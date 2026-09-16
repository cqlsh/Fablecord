"""
The MIT License (MIT)

Copyright (c) 2026-present cqlsh

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import enum

from typing import TYPE_CHECKING, Any, Self
from collections.abc import Callable

class _LookupTable(dict[Any, Any]):
    """
    Maps raw values to members and fills itself on a miss.

    A missing key does not raise. The table asks ``create`` for an unknown
    member, keeps it, and from then on that value is a plain dict read like
    any other.
    """

    __slots__ = ["create"]

    def __init__(self, members: dict[Any, Any], create: Callable[[object], Any]) -> None:
        super().__init__(members)

        self.create = create

    def __missing__(self, value: object) -> Any:
        member = self.create(value)
        self[value] = member

        return member

class Category:
    """
    Groups members of an enum under a boolean attribute.

    It is declared in the class body next to the members, with the raw
    values of the members that belong to the group::

        class ChannelType(Enum):
            text = 0
            voice = 2
            stage_voice = 13

            is_voice = Category(voice, stage_voice)

    :meth:`excluding` declares the opposite group, every member but the
    listed ones. Unknown members belong to it as well, which is the right
    default for whatever Discord adds later.

    When the class is created every member gets the answer stored as a
    plain ``True`` or ``False``, and an unknown member gets its answers the
    moment it is made. Reading ``channel.type.is_voice`` is therefore one
    attribute read that the interpreter serves from its fast path, cheaper
    than a property and cheaper than a tuple of raw values by hand.

    The category does not stay on the class. A class attribute of the
    same name would cost every member read that fast path, so the
    metaclass moves the categories into ``_categories_`` and only the
    members carry the answers, ``ChannelType.is_voice`` itself raises.
    The descriptor protocol below exists only for the type checker, it is
    how the checker knows that members answer with a :class:`bool`.
    """

    __slots__ = ["values", "name", "excludes"]

    def __init__(self, *values: object) -> None:
        self.values = frozenset(values)
        self.name = ""
        self.excludes = False

    @classmethod
    def excluding(cls, *values: object) -> Self:
        """
        The group of every member except the given ones.

        Parameters
        -----------
        \\*values
            The raw values of the members that do not belong to the group.
        """
        category = cls(*values)
        category.excludes = True

        return category

    def holds(self, value: object, /) -> bool:
        """
        Whether the member with this raw value belongs to the group.
        """
        if self.excludes:
            return value not in self.values

        return value in self.values

    def __repr__(self) -> str:
        if self.excludes:
            return f"<Category {self.name!r} excluding={set(self.values)!r}>"

        return f"<Category {self.name!r} values={set(self.values)!r}>"

    if TYPE_CHECKING:
        def __get__(self, instance: Enum, owner: type[Any]) -> bool:
            ...

class EnumMeta(enum.EnumType):
    """
    Builds enum classes without the standard library's member machinery.

    It still derives from :class:`enum.EnumType`, so type checkers treat
    the classes as enums and iteration, ``__getitem__`` and ``__members__``
    keep working on the usual tables. Creating the class and looking up a
    value are done here, because that is where the time goes.
    """

    _members_by_value_: dict[Any, Any]
    _lookuptable_: _LookupTable
    _categories_: tuple[Category, ...]

    @classmethod
    def __prepare__(metacls, name: str, bases: tuple[type, ...], **kwargs: Any) -> Any:
        """
        Gives the class body a plain dict.

        The standard one does bookkeeping on every assignment that we do
        not need.
        """
        return {}

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any) -> EnumMeta:
        categories = metacls._take_categories(namespace=namespace)
        definitions = metacls._take_member_definitions(namespace=namespace)

        cls = type.__new__(metacls, name, bases, namespace, **kwargs)
        cls._categories_ = categories

        by_value = cls._create_members(definitions=definitions)
        cls._install_lookup(by_value=by_value)

        return cls

    @staticmethod
    def _take_categories(namespace: dict[str, Any]) -> tuple[Category, ...]:
        """
        Pulls the categories out of the class body and names them.

        They must not become class attributes. The interpreter only serves
        an instance attribute from its fast path when the class has no
        attribute of the same name, and that fast path is the point of a
        category, measured as half the cost of every read.
        """
        categories = {name: value for name, value in namespace.items() if isinstance(value, Category)}

        for name, category in categories.items():
            category.name = name
            del namespace[name]

        return tuple(categories.values())

    @staticmethod
    def _take_member_definitions(namespace: dict[str, Any]) -> dict[str, object]:
        """
        Pulls the member definitions out of the class body.

        Everything that is neither private nor a descriptor is a member.
        Methods, properties and classmethods stay in the namespace.
        """
        definitions = {
            name: value
            for name, value in namespace.items()
            if not name.startswith("_") and not hasattr(value, "__get__")
        }

        for name in definitions:
            del namespace[name]

        return definitions

    def _create_members(cls, definitions: dict[str, object]) -> dict[Any, Any]:
        """
        Creates the members, hangs them onto the class and returns them by value.

        A value that appears twice gives an alias. Aliases are attributes
        and show up in ``__members__``, but not when iterating. Attributes
        go through ``type.__setattr__`` to skip the reassignment guard of
        :class:`enum.EnumType`, which has nothing to guard yet.
        """
        by_name: dict[str, Any] = {}
        by_value: dict[Any, Any] = {}

        for name, value in definitions.items():
            if value in by_value:
                member = by_value[value]
            else:
                member = cls._new_member(name=name, value=value)
                by_value[value] = member

            by_name[name] = member
            type.__setattr__(cls, name, member)

        cls._member_map_ = by_name
        cls._member_names_ = [member.name for member in by_value.values()]

        return by_value

    def _install_lookup(cls, by_value: dict[Any, Any]) -> None:
        """
        Sets up the two ways from a value to a member.

        The plain dict serves ``Cls(value)``, because the interpreter has a
        fast path for exact dicts. The lookup table fills itself with
        unknown members on a miss, and its ``__getitem__`` becomes
        :meth:`try_value`, so that lookup never enters Python at all.
        """
        cls._members_by_value_ = by_value
        cls._lookuptable_ = _LookupTable(members=by_value, create=cls._new_unknown)

        type.__setattr__(cls, "try_value", staticmethod(cls._lookuptable_.__getitem__))

    def _new_member(cls, name: str, value: object) -> Any:
        """
        Builds one member and writes every category answer onto it.

        Unknown members come through here as well, so they answer exactly
        like the defined ones. The attributes are always set in the same
        order, which lets the interpreter share one key table between all
        members and serve their attributes from its fast path.
        """
        member: Any = object.__new__(cls)
        member.name = name
        member.value = value

        for category in cls._categories_:
            setattr(member, category.name, category.holds(value))

        return member

    def _new_unknown(cls, value: object) -> Any:
        return cls._new_member(name=f"unknown_{value}", value=value)

    if not TYPE_CHECKING:
        def __call__(cls: Any, value: object) -> Any:
            """
            Looks up a member by value, the same way :meth:`try_value` does.

            The stub for :class:`enum.EnumType` already describes this call
            exactly, so the implementation stays out of the type checker's
            sight. Mirroring the stub's overloads here would only make the
            call slower.
            """
            try:
                return cls._members_by_value_[value]
            except KeyError:
                member = cls.try_value(value)
                cls._members_by_value_[value] = member

                return member

    def __contains__(cls, value: object) -> bool:
        if isinstance(value, cls):
            return True

        try:
            return value in cls._lookuptable_
        except TypeError:
            return False

    def __len__(cls) -> int:
        return len(cls._member_names_)

    def __dir__(cls) -> list[str]:
        return list(type.__dir__(cls))

    def __repr__(cls) -> str:
        return f"<enum {cls.__name__!r}>"

class Enum(metaclass=EnumMeta):
    """
    Base for enums whose values Discord may extend at any time.

    Members are objects of their own, not their values. Two members are
    equal only when they are the same object, and a raw value from a
    payload never equals a member. :meth:`try_value` turns the raw value
    into a member and ``value`` gets it back out for a payload. Keeping the
    members off ``int`` and ``str`` is what lets the interpreter serve
    ``value``, ``name`` and every :class:`Category` from its fast path.

    Looking up a value that is not defined does not raise. You get a member
    named ``unknown_<value>`` that still carries the value, so a new API
    addition never breaks parsing. Such members are cached, so the same
    value always gives the same object and ``is`` comparisons keep working.

    :meth:`try_value` is the lookup table's own ``__getitem__``, so a
    known value costs a single dict read and nothing else runs in Python.

    Attributes
    -----------
    name: :class:`str`
        The member's name, ``unknown_<value>`` for unknown values.
    value: Any
        The member's raw value as Discord sends it.
    try_value: Callable[[:class:`object`], :class:`Enum`]
        Returns the member for a raw value, creating an unknown one if needed.
    """

    name: str
    value: Any
    try_value: Callable[[object], Self]

    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}: {self.value!r}>"

    def __str__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __format__(self, spec: str) -> str:
        return format(str(self), spec)

    def __reduce__(self) -> tuple[type[Self], tuple[Any]]:
        return type(self), (self.value,)

class OrderedEnum(Enum):
    """
    An :class:`Enum` whose members rank by their value.

    Meant for levels that build on each other, so that a check like
    ``level >= VerificationLevel.medium`` reads the way it is meant.
    Only members of the same enum compare, a raw value has to go through
    :meth:`try_value` first.

    Equality stays identity. It is spelled out here on purpose, once a
    class defines any comparison the interpreter routes ``==`` and ``!=``
    through its generic path, and the explicit identity check below is
    twice as fast as the fallback that would run otherwise.
    """

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

    def __le__(self, other: Self) -> bool:
        return self.value <= other.value

    def __gt__(self, other: Self) -> bool:
        return self.value > other.value

    def __ge__(self, other: Self) -> bool:
        return self.value >= other.value

    def __eq__(self, other: object) -> bool:
        return self is other

    def __ne__(self, other: object) -> bool:
        return self is not other

    __hash__ = object.__hash__

__all__ = ["Enum", "OrderedEnum", "Category"]