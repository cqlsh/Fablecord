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

from typing import TYPE_CHECKING, Any, Final
from ..utils.missing import MISSING
from .route import Route

if TYPE_CHECKING:
    from .client import RESTClient, Response

class Users:
    """
    The user endpoints: users, the bot's own user and profile, the
    guilds it is in, and direct messages.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered. Only the fields given end up in a payload.

    Parameters
    -----------
    rest: :class:`RESTClient`
        The client that sends the requests.

    Attributes
    -----------
    rest: :class:`RESTClient`
        The client that sends the requests.
    """

    __slots__ = ["rest"]

    GET: Final = Route("GET", "/users/{user_id}")
    ME: Final = Route("GET", "/users/@me")
    EDIT_ME: Final = Route("PATCH", "/users/@me")
    MY_GUILDS: Final = Route("GET", "/users/@me/guilds")
    MY_MEMBER: Final = Route("GET", "/users/@me/guilds/{guild_id}/member")
    LEAVE_GUILD: Final = Route("DELETE", "/users/@me/guilds/{guild_id}")
    CREATE_DM: Final = Route("POST", "/users/@me/channels")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def get(self, user_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches a user.

        Parameters
        -----------
        user_id: :class:`int`
            The user.
        """
        return self.rest.request(self.GET.compile(user_id))

    def me(self) -> Response[dict[str, Any]]:
        """
        Fetches the bot's own user.
        """
        return self.rest.request(self.ME.compile())

    def edit_me(self, *, username: str = MISSING, avatar: str | None = MISSING, banner: str | None = MISSING) -> Response[dict[str, Any]]:
        """
        Edits the bot's own user. Only what is given changes.

        Parameters
        -----------
        username: :class:`str`
            The new username, which Discord lets a bot change only so
            often.
        avatar: Optional[:class:`str`]
            The avatar as a data URI, ``None`` to remove it.
        banner: Optional[:class:`str`]
            The banner as a data URI, ``None`` to remove it.
        """
        payload: dict[str, Any] = {}

        if username is not MISSING:
            payload["username"] = username

        if avatar is not MISSING:
            payload["avatar"] = avatar

        if banner is not MISSING:
            payload["banner"] = banner

        return self.rest.request(self.EDIT_ME.compile(), json=payload)

    def my_guilds(
            self,
            *,
            before: int | None = None,
            after: int | None = None,
            limit: int | None = None,
            with_counts: bool = MISSING
    ) -> Response[list[dict[str, Any]]]:
        """
        Fetches the guilds the bot is in, as partial guilds with the
        bot's permissions in each, up to two hundred at a time.

        Parameters
        -----------
        before: Optional[:class:`int`]
            Only guilds with an ID below this one.
        after: Optional[:class:`int`]
            Only guilds with an ID above this one.
        limit: Optional[:class:`int`]
            How many guilds at most, 1 to 200.
        with_counts: :class:`bool`
            Whether the member and presence counts come along.
        """
        return self.rest.request(self.MY_GUILDS.compile(), params={"before": before, "after": after, "limit": limit, "with_counts": with_counts or None})

    def my_member(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the bot's own member in a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.MY_MEMBER.compile(guild_id))

    def leave_guild(self, guild_id: int, /) -> Response[None]:
        """
        Leaves a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.LEAVE_GUILD.compile(guild_id))

    def create_dm(self, user_id: int, /) -> Response[dict[str, Any]]:
        """
        Opens the direct message channel with a user, or returns the
        one that exists. Discord frowns on opening DMs to users who never
        interacted with the bot.

        Parameters
        -----------
        user_id: :class:`int`
            The user.
        """
        return self.rest.request(self.CREATE_DM.compile(), json={"recipient_id": user_id})

__all__ = ["Users"]