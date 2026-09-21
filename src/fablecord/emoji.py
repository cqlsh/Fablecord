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

from typing import TYPE_CHECKING, Any
from datetime import datetime

from .utils.snowflake import Snowflake
from .partial_emoji import EmojiTag
from .asset import Asset

if TYPE_CHECKING:
    from .guild import Guild
    from .state import State
    from .role import Role

class Emoji(EmojiTag):
    """
    An emoji that was uploaded, either to a guild or to an
    application.

    This is the one the bot owns and can edit or delete. The emoji
    that turns up in a reaction, a button or an activity carries
    nothing but a name and an ID, and is a :class:`PartialEmoji`
    instead. The two compare equal when they stand for the same
    emoji, either way round.

    Attributes
    -----------
    id: :class:`int`
        The emoji's ID.
    name: :class:`str`
        The emoji's name, without the colons.
    animated: :class:`bool`
        Whether the emoji moves, which decides the file extension of
        its image.
    guild_id: Optional[:class:`int`]
        The guild the emoji belongs to, ``None`` for one an
        application owns.
    require_colons: :class:`bool`
        Whether the emoji has to be typed between colons.
    managed: :class:`bool`
        Whether an integration such as Twitch put the emoji here,
        which means nobody can edit or delete it by hand.
    available: :class:`bool`
        Whether the emoji can be used at all. A guild that loses
        boosts keeps its emojis but turns the ones over its limit off.
    role_ids: List[:class:`int`]
        The roles that may use the emoji, by their ID, empty when
        every member may.
    user: Optional[:class:`User`]
        Who uploaded the emoji, ``None`` unless the payload came from
        a request made with the permission to manage emojis.
    """

    __slots__ = [
        "id",
        "name",
        "animated",
        "guild_id",
        "require_colons",
        "managed",
        "available",
        "role_ids",
        "user",
        "_state",
        "_url"
    ]

    def __init__(self, state: State, guild_id: int | None, data: dict[str, Any], /) -> None:
        self._state = state
        self.id = int(data["id"])
        self.guild_id = guild_id

        self.update(data)

    def update(self, data: dict[str, Any], /) -> None:
        """
        Takes new data for the same emoji, which the cache does on
        every emoji update.
        """
        get = data.get
        user = get("user")

        self.name = data["name"]
        self.animated = get("animated", False)
        self.require_colons = get("require_colons", True)
        self.managed = get("managed", False)
        self.available = get("available", True)
        self.role_ids = [int(role) for role in get("roles") or ()]
        self.user = None if user is None else self._state.store_user(user)

    def to_dict(self) -> dict[str, Any]:
        """
        The payload for this emoji, as a button or a forum tag takes
        it.
        """
        data: dict[str, Any] = {"id": self.id, "name": self.name}

        if self.animated:
            data["animated"] = True

        return data

    def is_usable(self) -> bool:
        """
        Whether the bot may put this emoji into a message right now,
        which it may when the emoji is available and either open to
        everyone or tied to a role the bot holds.
        """
        if not self.available:
            return False

        role_ids = self.role_ids
        guild_id = self.guild_id

        if not role_ids or guild_id is None:
            return True

        guild = self._state.get_guild(guild_id)
        if guild is None:
            return False

        me = guild.me
        if me is None:
            return False

        mine = me.role_ids

        return any(role_id in mine for role_id in role_ids)

    def is_application_owned(self) -> bool:
        """
        Whether an application owns the emoji rather than a guild,
        which means it works everywhere the bot is.
        """
        return self.guild_id is None

    @property
    def guild(self) -> Guild | None:
        """
        Optional[:class:`Guild`]: The guild the emoji belongs to,
        ``None`` for an application emoji or while the guild is not
        cached.
        """
        guild_id = self.guild_id
        if guild_id is None:
            return None

        return self._state.get_guild(guild_id)

    @property
    def roles(self) -> list[Role]:
        """
        List[:class:`Role`]: The roles that may use the emoji from the
        lowest to the highest, empty when every member may.
        """
        role_ids = self.role_ids
        guild_id = self.guild_id

        if not role_ids or guild_id is None:
            return []

        guild = self._state.get_guild(guild_id)
        if guild is None:
            return []

        roles = [role for role in map(guild.get_role, role_ids) if role is not None]
        roles.sort(key=lambda role: (role.id != role.guild_id, role.position, -role.id))

        return roles

    @property
    def url(self) -> Asset:
        """
        :class:`Asset`: The emoji's image, built once and kept.
        """
        try:
            return self._url
        except AttributeError:
            pass

        asset = self._url = Asset.from_emoji(self._state.rest, self.id, self.animated)

        return asset

    @property
    def reaction(self) -> str:
        """
        :class:`str`: The emoji the way the reaction endpoints want it
        in a path, ``name:id``.
        """
        return f"{self.name}:{self.id}"

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the emoji was uploaded, taken
        from the ID.
        """
        return Snowflake(self.id).created_at

    def __str__(self) -> str:
        if self.animated:
            return f"<a:{self.name}:{self.id}>"

        return f"<:{self.name}:{self.id}>"

    def __repr__(self) -> str:
        return f"<Emoji id={self.id} name={self.name!r} animated={self.animated}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EmojiTag):
            return other.id == self.id

        return NotImplemented

    def __hash__(self) -> int:
        return self.id >> 22

__all__ = ["Emoji"]