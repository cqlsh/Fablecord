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
from collections.abc import Sequence
from ..utils.missing import MISSING
from .route import Route

if TYPE_CHECKING:
    from .client import RESTClient, Response

class Emojis:
    """
    The emoji endpoints: the custom emoji of a guild, and the emoji an
    application owns and can use anywhere.

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

    OF_GUILD: Final = Route("GET", "/guilds/{guild_id}/emojis")
    GET: Final = Route("GET", "/guilds/{guild_id}/emojis/{emoji_id}")
    CREATE: Final = Route("POST", "/guilds/{guild_id}/emojis")
    EDIT: Final = Route("PATCH", "/guilds/{guild_id}/emojis/{emoji_id}")
    DELETE: Final = Route("DELETE", "/guilds/{guild_id}/emojis/{emoji_id}")
    OF_APPLICATION: Final = Route("GET", "/applications/{application_id}/emojis")
    GET_APPLICATION: Final = Route("GET", "/applications/{application_id}/emojis/{emoji_id}")
    CREATE_APPLICATION: Final = Route("POST", "/applications/{application_id}/emojis")
    EDIT_APPLICATION: Final = Route("PATCH", "/applications/{application_id}/emojis/{emoji_id}")
    DELETE_APPLICATION: Final = Route("DELETE", "/applications/{application_id}/emojis/{emoji_id}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def of_guild(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the custom emoji of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.OF_GUILD.compile(guild_id))

    def get(self, guild_id: int, emoji_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one custom emoji of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        emoji_id: :class:`int`
            The emoji.
        """
        return self.rest.request(self.GET.compile(guild_id, emoji_id))

    def create(self, guild_id: int, /, *, name: str, image: str, roles: Sequence[int] = MISSING, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Creates a custom emoji in a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name, 2 to 32 characters of letters, digits and
            underscores.
        image: :class:`str`
            The image as a data URI, up to 256 KB.
        roles: Sequence[:class:`int`]
            The roles allowed to use the emoji, everyone when not given.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {"name": name, "image": image}

        if roles is not MISSING:
            payload["roles"] = roles

        return self.rest.request(self.CREATE.compile(guild_id), json=payload, reason=reason)

    def edit(self, guild_id: int, emoji_id: int, /, *, name: str = MISSING, roles: Sequence[int] | None = MISSING, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Edits a custom emoji of a guild. Only what is given changes.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        emoji_id: :class:`int`
            The emoji.
        name: :class:`str`
            The new name.
        roles: Optional[Sequence[:class:`int`]]
            The roles allowed to use the emoji, ``None`` for everyone.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if roles is not MISSING:
            payload["roles"] = roles

        return self.rest.request(self.EDIT.compile(guild_id, emoji_id), json=payload, reason=reason)

    def delete(self, guild_id: int, emoji_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes a custom emoji of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        emoji_id: :class:`int`
            The emoji.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(guild_id, emoji_id), reason=reason)

    def of_application(self, application_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the emoji of an application. The payload holds them
        under ``items``.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        """
        return self.rest.request(self.OF_APPLICATION.compile(application_id))

    def get_application(self, application_id: int, emoji_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one emoji of an application.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        emoji_id: :class:`int`
            The emoji.
        """
        return self.rest.request(self.GET_APPLICATION.compile(application_id, emoji_id))

    def create_application(self, application_id: int, /, *, name: str, image: str) -> Response[dict[str, Any]]:
        """
        Creates an emoji for an application, usable by the bot in every
        guild. An application holds up to two thousand.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        name: :class:`str`
            The name, 2 to 32 characters of letters, digits and
            underscores.
        image: :class:`str`
            The image as a data URI, up to 256 KB.
        """
        return self.rest.request(self.CREATE_APPLICATION.compile(application_id), json={"name": name, "image": image})

    def edit_application(self, application_id: int, emoji_id: int, /, *, name: str) -> Response[dict[str, Any]]:
        """
        Renames an emoji of an application.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        emoji_id: :class:`int`
            The emoji.
        name: :class:`str`
            The new name.
        """
        return self.rest.request(self.EDIT_APPLICATION.compile(application_id, emoji_id), json={"name": name})

    def delete_application(self, application_id: int, emoji_id: int, /) -> Response[None]:
        """
        Deletes an emoji of an application.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        emoji_id: :class:`int`
            The emoji.
        """
        return self.rest.request(self.DELETE_APPLICATION.compile(application_id, emoji_id))

__all__ = ["Emojis"]