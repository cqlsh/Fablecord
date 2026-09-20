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

from .flags.user import MemberFlags, PublicUserFlags
from .utils.time import Time
from .colour import Colour
from .asset import Asset
from .user import User

if TYPE_CHECKING:
    from .state import State

class Member:
    """
    A user as one guild knows them.

    The account itself is shared: :attr:`user` is the same object every
    other guild and message points at, and everything a guild adds on
    top, the nickname, the roles, since when they are in, lives here.
    A member and the user behind them compare equal, so either can be
    looked up in the same set.

    Attributes
    -----------
    id: :class:`int`
        The member's ID, the same as the user's.
    guild_id: :class:`int`
        The guild they are in.
    user: :class:`User`
        The account behind the member.
    nick: Optional[:class:`str`]
        The name they carry in this guild, ``None`` when they use their
        own.
    role_ids: List[:class:`int`]
        The roles they have, without ``@everyone``, which every member
        has anyway.
    joined_at: Optional[:class:`datetime.datetime`]
        When they joined, ``None`` in the few payloads Discord leaves
        it out of.
    premium_since: Optional[:class:`datetime.datetime`]
        Since when they boost the guild, ``None`` when they do not.
    timed_out_until: Optional[:class:`datetime.datetime`]
        When a timeout runs out, ``None`` when there is none. A time in
        the past means it already ran out.
    deaf: :class:`bool`
        Whether the guild deafened them in voice.
    mute: :class:`bool`
        Whether the guild muted them in voice.
    pending: :class:`bool`
        Whether they still have to pass the membership screening.
    """

    __slots__ = [
        "id",
        "guild_id",
        "user",
        "nick",
        "role_ids",
        "joined_at",
        "premium_since",
        "timed_out_until",
        "deaf",
        "mute",
        "pending",
        "_state",
        "_avatar",
        "_banner",
        "_flags"
    ]

    def __init__(self, state: State, guild_id: int, data: dict[str, Any], /) -> None:
        user = state.store_user(data["user"])

        self._state = state
        self.guild_id = guild_id
        self.user = user
        self.id = user.id

        self.update(data)

    def update(self, data: dict[str, Any], /) -> None:
        """
        Takes new data for the same member, which the cache does on
        every member update and on every message they send.
        """
        get = data.get

        self.nick = get("nick")
        self.role_ids = [int(role) for role in data["roles"]]
        self.joined_at = Time.parse_optional(get("joined_at"))
        self.premium_since = Time.parse_optional(get("premium_since"))
        self.timed_out_until = Time.parse_optional(get("communication_disabled_until"))
        self.deaf = get("deaf", False)
        self.mute = get("mute", False)
        self.pending = get("pending", False)
        self._avatar = get("avatar")
        self._banner = get("banner")
        self._flags = get("flags", 0)

    @property
    def name(self) -> str:
        """
        :class:`str`: The username of the account behind the member.
        """
        return self.user.name

    @property
    def discriminator(self) -> str:
        """
        :class:`str`: The legacy four digits of the account.
        """
        return self.user.discriminator

    @property
    def global_name(self) -> str | None:
        """
        Optional[:class:`str`]: The display name the account chose,
        which the nickname of a guild wins over.
        """
        return self.user.global_name

    @property
    def bot(self) -> bool:
        """
        :class:`bool`: Whether the account belongs to an application.
        """
        return self.user.bot

    @property
    def system(self) -> bool:
        """
        :class:`bool`: Whether the account is Discord's own.
        """
        return self.user.system

    @property
    def display_name(self) -> str:
        """
        :class:`str`: The name this guild shows: the nickname, then the
        display name of the account, then the username.
        """
        nick = self.nick
        if nick is not None:
            return nick

        user = self.user

        return user.global_name or user.name

    @property
    def mention(self) -> str:
        """
        :class:`str`: The text that mentions the member in a message.
        """
        return f"<@{self.id}>"

    @property
    def avatar(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The avatar of the account, ``None``
        when it uses a default one. The one set for this guild is
        :attr:`guild_avatar`.
        """
        return self.user.avatar

    @property
    def guild_avatar(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The avatar the member set for this
        guild alone, ``None`` when they did not.
        """
        hash = self._avatar
        if hash is None:
            return None

        return Asset.from_guild_avatar(self._state.rest, self.guild_id, self.id, hash)

    @property
    def display_avatar(self) -> Asset:
        """
        :class:`Asset`: The avatar this guild shows: the one set for
        the guild, then the one of the account, then a default.
        """
        hash = self._avatar
        if hash is None:
            return self.user.display_avatar

        return Asset.from_guild_avatar(self._state.rest, self.guild_id, self.id, hash)

    @property
    def banner(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The profile banner of the account.
        """
        return self.user.banner

    @property
    def guild_banner(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The banner the member set for this
        guild alone, ``None`` when they did not.
        """
        hash = self._banner
        if hash is None:
            return None

        return Asset.from_guild_banner(self._state.rest, self.guild_id, self.id, hash)

    @property
    def display_banner(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The banner this guild shows, the one
        set for the guild or the one of the account.
        """
        hash = self._banner
        if hash is None:
            return self.user.banner

        return Asset.from_guild_banner(self._state.rest, self.guild_id, self.id, hash)

    @property
    def accent_colour(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: The colour behind the profile of the
        account.
        """
        return self.user.accent_colour

    @property
    def accent_color(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: :attr:`accent_colour` under the
        other spelling.
        """
        return self.user.accent_colour

    @property
    def public_flags(self) -> PublicUserFlags:
        """
        :class:`PublicUserFlags`: The badges on the account's profile.
        """
        return self.user.public_flags

    @property
    def flags(self) -> MemberFlags:
        """
        :class:`MemberFlags`: What this guild marked about the member,
        such as having passed the screening.
        """
        flags = MemberFlags.__new__(MemberFlags)
        flags.value = self._flags

        return flags

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the account was created.
        """
        return self.user.created_at

    def is_timed_out(self) -> bool:
        """
        Whether a timeout is running right now, which keeps the member
        from writing and from speaking.
        """
        if self.timed_out_until is None:
            return False

        return self.timed_out_until > Time.now()

    def __str__(self) -> str:
        return str(self.user)

    def __repr__(self) -> str:
        return f"<Member id={self.id} name={self.user.name!r} nick={self.nick!r} guild_id={self.guild_id}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (Member, User)) and other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

__all__ = ["Member"]