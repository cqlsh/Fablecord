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

class Invites:
    """
    The invite endpoints: looking an invite up by its code and revoking
    it. Creating one belongs to its channel, see
    :meth:`Channels.create_invite`.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered.

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

    GET: Final = Route("GET", "/invites/{code}")
    DELETE: Final = Route("DELETE", "/invites/{code}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def get(
            self,
            code: str,
            /,
            *,
            with_counts: bool = MISSING,
            with_expiration: bool = MISSING,
            guild_scheduled_event_id: int | None = None
    ) -> Response[dict[str, Any]]:
        """
        Fetches an invite by its code, with its guild and channel.

        Parameters
        -----------
        code: :class:`str`
            The invite code, the part after ``discord.gg/``.
        with_counts: :class:`bool`
            Whether the guild's member and presence counts come along.
        with_expiration: :class:`bool`
            Whether the expiry date comes along.
        guild_scheduled_event_id: Optional[:class:`int`]
            A scheduled event of the guild to include in the payload.
        """
        params = {"with_counts": with_counts or None, "with_expiration": with_expiration or None, "guild_scheduled_event_id": guild_scheduled_event_id}

        return self.rest.request(self.GET.compile(code), params=params)

    def delete(self, code: str, /, *, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Revokes an invite, which takes the permission to manage the
        channel or the guild.

        Parameters
        -----------
        code: :class:`str`
            The invite code.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(code), reason=reason)

__all__ = ["Invites"]