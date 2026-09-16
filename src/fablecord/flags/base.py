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

from typing import Any, ClassVar, Self, overload
from collections.abc import Iterator

class Flag:
    """
    A single bit of a :class:`Flags` value.

    Reads as a :class:`bool` on an instance and as itself on the class, so
    the bit stays available for building masks by hand.

    Attributes
    -----------
    bit: :class:`int`
        The bit this flag stands for.
    name: :class:`str`
        The attribute name the flag was defined under.
    """

    __slots__ = ["bit", "name"]

    def __init__(self, bit: int) -> None:
        self.bit = bit
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: Flags, owner: type) -> bool:
        ...

    def __get__(self, instance: Flags | None, owner: type) -> Self | bool:
        if instance is None:
            return self

        return (instance.value & self.bit) == self.bit

    def __set__(self, instance: Flags, enabled: bool) -> None:
        if enabled:
            instance.value |= self.bit
        else:
            instance.value &= ~self.bit

    def __repr__(self) -> str:
        return f"<Flag {self.name} bit={self.bit}>"

class Flags:
    """
    Base for bit fields such as intents and permissions.

    Subclasses define their bits as :class:`Flag` attributes. Every flag can
    be read and set as a plain :class:`bool`, the raw value is always at
    hand as :attr:`value`, and instances combine with ``|``, ``&``, ``^``
    and ``~`` like sets. An instance with no bit set is false, so a bare
    ``if permissions:`` asks whether anything is granted at all.

    An instance is built from keywords, ``Intents(guilds=True)``, from a
    raw value with :meth:`from_value`, or from both at once by passing the
    raw value first, ``Permissions(value, send_messages=False)``.

    Attributes
    -----------
    value: :class:`int`
        The raw bit field as Discord sends and expects it.
    """

    __slots__ = ["value"]

    _flags: ClassVar[dict[str, int]] = {}
    _all: ClassVar[int] = 0

    value: int

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        flags = dict(cls._flags)
        for name, attribute in vars(cls).items():
            if isinstance(attribute, Flag):
                flags[name] = attribute.bit

        combined = 0
        for bit in flags.values():
            combined |= bit

        cls._flags = flags
        cls._all = combined

    def __init__(self, value: int = 0, /, **flags: bool) -> None:
        if flags:
            table = self._flags

            try:
                for name, enabled in flags.items():
                    if enabled:
                        value |= table[name]
                    else:
                        value &= ~table[name]
            except KeyError as error:
                raise TypeError(f"{error.args[0]!r} is not a flag of {type(self).__name__}") from None

        self.value = value

    def update(self, **flags: bool) -> None:
        """
        Sets several flags at once, ``False`` clears a flag.

        Parameters
        -----------
        flags: :class:`bool`
            Flag names mapped to whether they should be enabled.

        Raises
        -------
        TypeError
            A name is not a flag of this class.
        """
        self.value = type(self)(self.value, **flags).value

    @classmethod
    def from_value(cls, value: int, /) -> Self:
        """
        Wraps a raw bit field without touching it.

        Parameters
        -----------
        value: :class:`int`
            The bit field as received from Discord.

        Returns
        --------
        :class:`Flags`
            The wrapped value.
        """
        self = cls.__new__(cls)
        self.value = value

        return self

    @classmethod
    def all(cls) -> Self:
        """
        Returns an instance with every flag enabled.
        """
        return cls.from_value(cls._all)

    @classmethod
    def none(cls) -> Self:
        """
        Returns an instance with every flag disabled.
        """
        return cls.from_value(0)

    def is_subset(self, other: Self, /) -> bool:
        """
        Whether every flag enabled here is also enabled in ``other``.
        """
        return (self.value & other.value) == self.value

    def is_superset(self, other: Self, /) -> bool:
        """
        Whether every flag enabled in ``other`` is also enabled here.
        """
        return (self.value & other.value) == other.value

    def is_strict_subset(self, other: Self, /) -> bool:
        """
        Whether this is a subset of ``other`` and not equal to it.
        """
        return self.value != other.value and self.is_subset(other)

    def is_strict_superset(self, other: Self, /) -> bool:
        """
        Whether this is a superset of ``other`` and not equal to it.
        """
        return self.value != other.value and self.is_superset(other)

    def _with_value(self, value: int, /) -> Self:
        """
        The instance side twin of :meth:`from_value`.

        Calling a classmethod through an instance binds it first, which
        costs the operators below a noticeable share of their time.
        """
        cls = type(self)
        new = cls.__new__(cls)
        new.value = value

        return new

    def __or__(self, other: Self) -> Self:
        return self._with_value(self.value | other.value)

    def __and__(self, other: Self) -> Self:
        return self._with_value(self.value & other.value)

    def __xor__(self, other: Self) -> Self:
        return self._with_value(self.value ^ other.value)

    def __invert__(self) -> Self:
        return self._with_value(self._all & ~self.value)

    def __le__(self, other: Self) -> bool:
        return self.is_subset(other)

    def __ge__(self, other: Self) -> bool:
        return self.is_superset(other)

    def __lt__(self, other: Self) -> bool:
        return self.is_strict_subset(other)

    def __gt__(self, other: Self) -> bool:
        return self.is_strict_superset(other)

    def __eq__(self, other: Any) -> bool:
        return other.__class__ is self.__class__ and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __bool__(self) -> bool:
        return self.value != 0

    def __int__(self) -> int:
        return self.value

    def __iter__(self) -> Iterator[tuple[str, bool]]:
        for name, bit in self._flags.items():
            yield name, (self.value & bit) == bit

    def __repr__(self) -> str:
        return f"<{type(self).__name__} value={self.value}>"

__all__ = ["Flag", "Flags"]