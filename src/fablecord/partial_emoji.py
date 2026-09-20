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

import re

from typing import TYPE_CHECKING, Any, Final, Self
from datetime import datetime

from .utils.snowflake import Snowflake
from .asset import Asset

if TYPE_CHECKING:
    from .state import State

_CUSTOM: Final = re.compile(r"<?(?:(?P<animated>a)?:)?(?P<name>\w+):(?P<id>\d{13,20})>?")

class EmojiTag:
    """
    What every emoji is, whether a guild uploaded it or a payload only
    named it.

    It carries nothing. Both kinds inherit it so that one check tells
    an emoji from anything else, which is what comparing them comes
    down to.
    """

    __slots__ = []

    id: Any

class EmojiFields:
    """
    The fields of an emoji and the two operations that run on every one
    of them, for when the C helper in :mod:`fablecord._speedups` could
    not be built.
    """

    __slots__ = ["name", "id", "animated", "_state", "_url"]

    name: str
    id: int | None
    animated: bool
    _state: State | None
    _url: Asset

    @classmethod
    def from_dict(cls, state: State | None, data: dict[str, Any], /) -> Self:
        """
        Builds one from the ``emoji`` of a payload, which carries a
        name, an ID and whether it moves.
        """
        self = cls.__new__(cls)
        get = data.get
        emoji_id = get("id")

        self.name = get("name") or ""
        self._state = state

        if emoji_id is None:
            self.id = None
            self.animated = False
        else:
            self.id = int(emoji_id)
            self.animated = get("animated", False)

        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EmojiFields):
            return NotImplemented

        emoji_id = self.id
        if emoji_id is None:
            return other.id is None and other.name == self.name

        return other.id == emoji_id

    def __hash__(self) -> int:
        emoji_id = self.id
        if emoji_id is None:
            return hash(self.name)

        return emoji_id >> 22

if TYPE_CHECKING:
    from ._speedups.emoji import EmojiBase
else:
    try:
        from ._speedups.emoji import EmojiBase
    except ImportError:
        EmojiBase = EmojiFields

class PartialEmoji(EmojiBase, EmojiTag):
    """
    An emoji as it turns up in a reaction, a button or an activity.

    Discord sends two kinds of emoji and this is both of them. A
    standard one carries only its character in :attr:`name` and has no
    ID; a custom one has an ID, a name and whether it moves. What a
    guild knows about its own emoji, who uploaded it and which roles
    may use it, belongs to :class:`Emoji` instead.

    The fields and the two things done to every emoji that arrives,
    building one from a payload and comparing two of them, come from
    the C helper in :mod:`fablecord._speedups` when it was compiled,
    and from :class:`EmojiFields` otherwise.

    Parameters
    -----------
    name: :class:`str`
        The character of a standard emoji, or the name of a custom one.
    id: Optional[:class:`int`]
        The ID of a custom emoji, ``None`` for a standard one.
    animated: :class:`bool`
        Whether a custom emoji moves, which decides the file extension
        of its image.

    Attributes
    -----------
    name: :class:`str`
        The character or the name.
    id: Optional[:class:`int`]
        The ID, ``None`` for a standard emoji.
    animated: :class:`bool`
        Whether the emoji moves.
    """

    __slots__ = []

    def __init__(self, *, name: str, id: int | None = None, animated: bool = False) -> None:
        self.name = name
        self.id = id
        self.animated = animated
        self._state = None

    @classmethod
    def from_str(cls, value: str, /) -> Self:
        """
        Reads an emoji out of the text a user typed.

        ``<a:name:id>`` and ``<:name:id>`` give a custom emoji, and so
        does the bare ``name:id``. Anything else is taken as a standard
        emoji, which is what a bot gets from a command argument or a
        message.

        Parameters
        -----------
        value: :class:`str`
            The text to read.
        """
        if ":" not in value:
            return cls(name=value)

        match = _CUSTOM.match(value)
        if match is None:
            return cls(name=value)

        animated, name, emoji_id = match.groups()

        return cls(name=name, id=int(emoji_id), animated=animated is not None)

    def to_dict(self) -> dict[str, Any]:
        """
        The payload for this emoji, as a button or a forum tag takes it.
        """
        data: dict[str, Any] = {"id": self.id, "name": self.name}

        if self.animated:
            data["animated"] = True

        return data

    def is_custom_emoji(self) -> bool:
        """
        Whether the emoji was uploaded to a guild, which is what having
        an ID means.
        """
        return self.id is not None

    def is_unicode_emoji(self) -> bool:
        """
        Whether the emoji is a standard one that every client already
        has.
        """
        return self.id is None

    @property
    def reaction(self) -> str:
        """
        :class:`str`: The emoji the way the reaction endpoints want it
        in a path, the character itself or ``name:id``.
        """
        emoji_id = self.id
        if emoji_id is None:
            return self.name

        return f"{self.name}:{emoji_id}"

    @property
    def url(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The image of a custom emoji, ``None``
        for a standard one, which has no file on the CDN. The asset is
        built once and kept.
        """
        try:
            return self._url
        except AttributeError:
            pass

        emoji_id = self.id
        if emoji_id is None:
            return None

        state = self._state
        asset = self._url = Asset.from_emoji(None if state is None else state.rest, emoji_id, self.animated)

        return asset

    @property
    def created_at(self) -> datetime | None:
        """
        Optional[:class:`datetime.datetime`]: When a custom emoji was
        uploaded, ``None`` for a standard one.
        """
        emoji_id = self.id
        if emoji_id is None:
            return None

        return Snowflake(emoji_id).created_at

    def __str__(self) -> str:
        emoji_id = self.id
        if emoji_id is None:
            return self.name

        if self.animated:
            return f"<a:{self.name}:{emoji_id}>"

        return f"<:{self.name}:{emoji_id}>"

    def __repr__(self) -> str:
        return f"<PartialEmoji id={self.id} name={self.name!r} animated={self.animated}>"

__all__ = ["PartialEmoji"]