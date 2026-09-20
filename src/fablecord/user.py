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

from typing import TYPE_CHECKING, Any, Self
from datetime import datetime

from .flags.user import PublicUserFlags
from .utils.snowflake import Snowflake
from .enums.user import DefaultAvatar
from .utils.missing import MISSING
from .utils.image import Image
from .colour import Colour
from .asset import Asset

if TYPE_CHECKING:
    from .state import State

class User:
    """
    A Discord user, as seen from anywhere.

    Users are shared: the same object stands for one account wherever
    it turns up, in messages, members and reactions, and it is updated
    in place when Discord sends new data. Members carry a user plus
    what a guild adds, so a user and the member of the same account
    compare equal.

    Attributes
    -----------
    id: :class:`int`
        The user's ID.
    name: :class:`str`
        The username, unique since the move away from discriminators.
    discriminator: :class:`str`
        The legacy four digits, ``"0"`` for accounts on the new system,
        which is nearly all of them.
    global_name: Optional[:class:`str`]
        The display name the user chose, ``None`` when they show their
        username.
    bot: :class:`bool`
        Whether the account belongs to an application.
    system: :class:`bool`
        Whether the account is Discord's own, the one that sends
        official messages.
    """

    __slots__ = [
        "_state",
        "id",
        "name",
        "discriminator",
        "global_name",
        "bot",
        "system",
        "_avatar",
        "_banner",
        "_accent_colour",
        "_public_flags",
        "_avatar_decoration",
        "__weakref__"
    ]

    def __init__(self, state: State, data: dict[str, Any], /) -> None:
        self._state = state
        self.update(data)

    def update(self, data: dict[str, Any], /) -> None:
        """
        Takes new data for the same account, which the cache does
        whenever Discord sends the user again.
        """
        get = data.get

        self.id = int(data["id"])
        self.name = data["username"]
        self.discriminator = data["discriminator"]
        self.global_name = get("global_name")
        self.bot = get("bot", False)
        self.system = get("system", False)
        self._avatar = get("avatar")
        self._banner = get("banner")
        self._accent_colour = get("accent_color")
        self._public_flags = get("public_flags", 0)
        self._avatar_decoration = get("avatar_decoration_data")

    def changed(self, data: dict[str, Any], /) -> bool:
        """
        Whether a payload for this account differs in what a user
        changes about themselves: the username, the display name or
        the avatar. The cache checks this before it updates.
        """
        return self.name != data["username"] or self.global_name != data.get("global_name") or self._avatar != data.get("avatar")

    @property
    def display_name(self) -> str:
        """
        :class:`str`: The name to show: the global name, or the
        username when none was chosen.
        """
        return self.global_name or self.name

    @property
    def mention(self) -> str:
        """
        :class:`str`: The text that mentions the user in a message.
        """
        return f"<@{self.id}>"

    @property
    def avatar(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The avatar the user uploaded, ``None``
        when they use a default one.
        """
        hash = self._avatar
        if hash is None:
            return None

        return Asset.from_avatar(self._state.rest, self.id, hash)

    @property
    def default_avatar(self) -> Asset:
        """
        :class:`Asset`: The avatar Discord shows for the user without an
        upload, one of six by the ID or the legacy discriminator.
        """
        index = DefaultAvatar.for_user(self.id, int(self.discriminator)).value

        return Asset.from_default_avatar(self._state.rest, index)

    @property
    def display_avatar(self) -> Asset:
        """
        :class:`Asset`: The avatar to show: the uploaded one, or the
        default without it.
        """
        hash = self._avatar
        if hash is None:
            return self.default_avatar

        return Asset.from_avatar(self._state.rest, self.id, hash)

    @property
    def banner(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The profile banner, which only comes
        with a user fetched over HTTP, ``None`` otherwise.
        """
        hash = self._banner
        if hash is None:
            return None

        return Asset.from_user_banner(self._state.rest, self.id, hash)

    @property
    def accent_colour(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: The colour behind a profile without a
        banner, which only comes with a user fetched over HTTP.
        """
        value = self._accent_colour
        if value is None:
            return None

        return Colour(value)

    @property
    def accent_color(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: :attr:`accent_colour` under the other
        spelling.
        """
        return self.accent_colour

    @property
    def colour(self) -> Colour:
        """
        :class:`Colour`: The colour the user's name has outside a guild,
        which is always the default. Members carry their role colour.
        """
        return Colour(0)

    @property
    def color(self) -> Colour:
        """
        :class:`Colour`: :attr:`colour` under the other spelling.
        """
        return Colour(0)

    @property
    def public_flags(self) -> PublicUserFlags:
        """
        :class:`PublicUserFlags`: The badges on the profile.
        """
        flags = PublicUserFlags.__new__(PublicUserFlags)
        flags.value = self._public_flags

        return flags

    @property
    def avatar_decoration(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The decoration around the avatar,
        ``None`` without one.
        """
        data = self._avatar_decoration
        if data is None:
            return None

        return Asset.from_avatar_decoration(self._state.rest, data["asset"])

    @property
    def avatar_decoration_sku_id(self) -> int | None:
        """
        Optional[:class:`int`]: The SKU the avatar decoration was bought
        as, ``None`` without one.
        """
        data = self._avatar_decoration
        if data is None:
            return None

        return int(data["sku_id"])

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the account was created, taken
        from the ID.
        """
        return Snowflake(self.id).created_at

    def __str__(self) -> str:
        if self.discriminator == "0":
            return self.name

        return f"{self.name}#{self.discriminator}"

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} global_name={self.global_name!r} bot={self.bot}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented

        return other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

class ClientUser(User):
    """
    The bot's own user, with what only the account itself gets to see.

    Attributes
    -----------
    verified: :class:`bool`
        Whether the email of the account is verified.
    locale: Optional[:class:`str`]
        The language the account is set to, ``None`` when Discord did
        not send one.
    mfa_enabled: :class:`bool`
        Whether two-factor authentication is on.
    """

    __slots__ = ["verified", "locale", "mfa_enabled", "_flags"]

    def update(self, data: dict[str, Any], /) -> None:
        super().update(data)

        get = data.get
        self.verified = get("verified", False)
        self.locale = get("locale")
        self.mfa_enabled = get("mfa_enabled", False)
        self._flags = get("flags", 0)

    @property
    def flags(self) -> PublicUserFlags:
        """
        :class:`PublicUserFlags`: Every flag of the account, the public
        badges included.
        """
        flags = PublicUserFlags.__new__(PublicUserFlags)
        flags.value = self._flags

        return flags

    async def edit(self, *, username: str = MISSING, avatar: bytes | None = MISSING, banner: bytes | None = MISSING) -> Self:
        """
        |coro|

        Changes the bot's username, avatar or banner. Only what is
        given changes, ``None`` removes the avatar or banner.

        Parameters
        -----------
        username: :class:`str`
            The new username, which Discord lets a bot change only so
            often.
        avatar: Optional[:class:`bytes`]
            The new avatar as PNG, JPEG or GIF bytes.
        banner: Optional[:class:`bytes`]
            The new banner as PNG, JPEG or GIF bytes.

        Raises
        -------
        HTTPException
            Discord refused the change, for a username that is taken
            or changed too often.

        Returns
        --------
        :class:`ClientUser`
            This user, updated.
        """
        data = await self._state.rest.users.edit_me(username=username, avatar=self._uri(avatar), banner=self._uri(banner))
        self.update(data)

        return self

    @staticmethod
    def _uri(image: bytes | None, /) -> str | None:
        """
        Turns image bytes into the data URI the API takes, leaving
        ``None`` and a missing value as they are.
        """
        if image is MISSING:
            return MISSING

        if image is None:
            return None

        return Image.data_uri(image)

    def __repr__(self) -> str:
        return f"<ClientUser id={self.id} name={self.name!r} global_name={self.global_name!r} bot={self.bot} verified={self.verified} mfa_enabled={self.mfa_enabled}>"

__all__ = ["User", "ClientUser"]