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

from .flags.permissions import Permissions
from .utils.snowflake import Snowflake
from .flags.guild import RoleFlags
from .colour import Colour
from .asset import Asset

if TYPE_CHECKING:
    from .state import State

class RoleTags:
    """
    Why a role is managed, which Discord attaches to the ones it keeps
    in its own hands.

    A managed role cannot be given out or taken away by hand, and this
    says who holds it: a bot, an integration, the server's boosters, a
    shop item or a linked account.

    Attributes
    -----------
    bot_id: Optional[:class:`int`]
        The bot the role belongs to, ``None`` when no bot does.
    integration_id: Optional[:class:`int`]
        The integration the role belongs to, ``None`` when none does.
    subscription_listing_id: Optional[:class:`int`]
        The shop listing the role is sold with, ``None`` when it is not
        for sale.
    """

    __slots__ = [
        "bot_id",
        "integration_id",
        "subscription_listing_id",
        "_premium_subscriber",
        "_available_for_purchase",
        "_guild_connections"
    ]

    def __init__(self, data: dict[str, Any], /) -> None:
        get = data.get

        bot_id = get("bot_id")
        integration_id = get("integration_id")
        listing_id = get("subscription_listing_id")

        self.bot_id = None if bot_id is None else int(bot_id)
        self.integration_id = None if integration_id is None else int(integration_id)
        self.subscription_listing_id = None if listing_id is None else int(listing_id)
        self._premium_subscriber = "premium_subscriber" in data
        self._available_for_purchase = "available_for_purchase" in data
        self._guild_connections = "guild_connections" in data

    def is_bot_managed(self) -> bool:
        """
        Whether the role is the one a bot got when it was invited.
        """
        return self.bot_id is not None

    def is_premium_subscriber(self) -> bool:
        """
        Whether the role is the one everyone boosting the server has.
        """
        return self._premium_subscriber

    def is_integration(self) -> bool:
        """
        Whether an integration such as Twitch or YouTube hands the role
        out.
        """
        return self.integration_id is not None

    def is_available_for_purchase(self) -> bool:
        """
        Whether the role is on sale in the server's shop.
        """
        return self._available_for_purchase

    def is_guild_connection(self) -> bool:
        """
        Whether members get the role by meeting a linked account
        requirement.
        """
        return self._guild_connections

    def __repr__(self) -> str:
        return f"<RoleTags bot_id={self.bot_id} integration_id={self.integration_id} premium_subscriber={self._premium_subscriber}>"

class Role:
    """
    A role in a guild.

    Roles decide what a member may do and which colour their name has.
    They are ordered, and comparing two of them with ``<`` and ``>``
    answers which one sits higher, which is what Discord checks before
    it lets one member act on another. The ``@everyone`` role carries
    the guild's own ID and sits below every other one.

    Attributes
    -----------
    id: :class:`int`
        The role's ID.
    guild_id: :class:`int`
        The guild the role belongs to.
    name: :class:`str`
        The role's name.
    position: :class:`int`
        Where the role sits, counting up from ``0`` for ``@everyone``.
        Several roles can share a position, and the older one wins.
    hoist: :class:`bool`
        Whether members with this role are listed on their own in the
        member list.
    managed: :class:`bool`
        Whether a bot, an integration or a subscription hands the role
        out, which means nobody can give it away by hand.
    mentionable: :class:`bool`
        Whether anyone may ping the role.
    unicode_emoji: Optional[:class:`str`]
        The standard emoji shown next to the role, ``None`` when it has
        none or carries an uploaded icon instead.
    tags: Optional[:class:`RoleTags`]
        Why the role is managed, ``None`` when it is an ordinary one.
    """

    __slots__ = [
        "id",
        "guild_id",
        "name",
        "position",
        "hoist",
        "managed",
        "mentionable",
        "unicode_emoji",
        "tags",
        "_state",
        "_permissions",
        "_colour",
        "_secondary_colour",
        "_tertiary_colour",
        "_icon",
        "_flags"
    ]

    def __init__(self, state: State, guild_id: int, data: dict[str, Any], /) -> None:
        self._state = state
        self.id = int(data["id"])
        self.guild_id = guild_id

        self.update(data)

    def update(self, data: dict[str, Any], /) -> None:
        """
        Takes new data for the same role, which the cache does whenever
        Discord sends it again.
        """
        get = data.get
        colours: dict[str, int | None] = get("colors") or {}
        tags: dict[str, Any] | None = get("tags")

        self.name = data["name"]
        self.position = get("position", 0)
        self.hoist = get("hoist", False)
        self.managed = get("managed", False)
        self.mentionable = get("mentionable", False)
        self.unicode_emoji = get("unicode_emoji")
        self.tags = None if tags is None else RoleTags(tags)
        self._permissions = int(get("permissions", 0))
        self._colour = colours.get("primary_color") or get("color", 0)
        self._secondary_colour: int | None = colours.get("secondary_color")
        self._tertiary_colour: int | None = colours.get("tertiary_color")
        self._icon = get("icon")
        self._flags = get("flags", 0)

    @property
    def permissions(self) -> Permissions:
        """
        :class:`Permissions`: What the role allows on its own, before
        any channel changes them.
        """
        permissions = Permissions.__new__(Permissions)
        permissions.value = self._permissions

        return permissions

    @property
    def colour(self) -> Colour:
        """
        :class:`Colour`: The colour members get from this role, black
        when the role has none, which means it does not colour a name
        at all.
        """
        return Colour(self._colour)

    @property
    def color(self) -> Colour:
        """
        :class:`Colour`: :attr:`colour` under the other spelling.
        """
        return Colour(self._colour)

    @property
    def secondary_colour(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: The second colour of a role that
        fades from one to another, ``None`` on a plain one.
        """
        value = self._secondary_colour
        if value is None:
            return None

        return Colour(value)

    @property
    def secondary_color(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: :attr:`secondary_colour` under the
        other spelling.
        """
        return self.secondary_colour

    @property
    def tertiary_colour(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: The third colour, which only a role
        with the holographic style carries.
        """
        value = self._tertiary_colour
        if value is None:
            return None

        return Colour(value)

    @property
    def tertiary_color(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: :attr:`tertiary_colour` under the
        other spelling.
        """
        return self.tertiary_colour

    @property
    def icon(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The image next to the role's name,
        ``None`` when it has none. A role shows either this or
        :attr:`unicode_emoji`.
        """
        hash = self._icon
        if hash is None:
            return None

        return Asset.from_icon(self._state.rest, self.id, hash, "role")

    @property
    def display_icon(self) -> Asset | str | None:
        """
        Optional[Union[:class:`Asset`, :class:`str`]]: What is shown
        next to the role's name, the uploaded image or the standard
        emoji, ``None`` when the role has neither.
        """
        hash = self._icon
        if hash is None:
            return self.unicode_emoji

        return Asset.from_icon(self._state.rest, self.id, hash, "role")

    @property
    def flags(self) -> RoleFlags:
        """
        :class:`RoleFlags`: What Discord marked about the role, such as
        members being able to pick it themselves.
        """
        flags = RoleFlags.__new__(RoleFlags)
        flags.value = self._flags

        return flags

    @property
    def mention(self) -> str:
        """
        :class:`str`: The text that pings the role in a message.
        """
        return f"<@&{self.id}>"

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the role was made, taken from
        the ID.
        """
        return Snowflake(self.id).created_at

    def is_default(self) -> bool:
        """
        Whether this is ``@everyone``, the role every member has, which
        carries the guild's own ID.
        """
        return self.id == self.guild_id

    def is_bot_managed(self) -> bool:
        """
        Whether the role is the one a bot got when it was invited.
        """
        tags = self.tags

        return tags is not None and tags.bot_id is not None

    def is_premium_subscriber(self) -> bool:
        """
        Whether the role is the one everyone boosting the guild has.
        """
        tags = self.tags

        return tags is not None and tags.is_premium_subscriber()

    def is_integration(self) -> bool:
        """
        Whether an integration such as Twitch or YouTube hands the role
        out.
        """
        tags = self.tags

        return tags is not None and tags.integration_id is not None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r} position={self.position}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Role) and other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented

        if self.guild_id != other.guild_id:
            raise RuntimeError("cannot compare roles from two different guilds")

        if self.id == self.guild_id:
            return other.id != other.guild_id

        if other.id == other.guild_id:
            return False

        if self.position != other.position:
            return self.position < other.position

        return self.id > other.id

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented

        return other.__lt__(self)

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented

        return not other.__lt__(self)

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented

        return not self.__lt__(other)

__all__ = ["Role", "RoleTags"]