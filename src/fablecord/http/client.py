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

import logging
import asyncio
import ssl

from ..errors.http import HTTPException, BadRequest, Forbidden, NotFound, DiscordServerError, RateLimited, LoginFailure
from collections.abc import Sequence, Coroutine
from ..net.http import HTTPClient, HTTPResponse
from .scheduled_events import ScheduledEvents
from urllib.parse import quote, urlencode
from typing import Any, Final, Self, cast
from ..net.multipart import MultipartBody
from .route import CompiledRoute, Route
from .interactions import Interactions
from .applications import Applications
from .automod import AutoModeration
from .soundboard import Soundboard
from .ratelimit import RateLimiter
from .channels import Channels
from .messages import Messages
from .webhooks import Webhooks
from .stickers import Stickers
from json import dumps, loads
from sys import version_info
from .invites import Invites
from .guilds import Guilds
from .emojis import Emojis
from .. import __version__
from .users import Users
from ..file import File

type Response[T] = Coroutine[Any, Any, T]

_log: Final = logging.getLogger(__name__)

class RESTClient:
    """
    Talks to Discord's REST API.

    Every request goes out with the bot's token and user agent, waits
    for its rate limit bucket first and comes back as the JSON Discord
    answered. A 429 is waited out and the request sent again, a server
    error or a dropped connection is retried after a pause that grows
    with every attempt, and anything else Discord refuses becomes one of
    the exceptions in :mod:`fablecord.errors.http`. What a message or a
    guild is, this does not know: the endpoint modules build the routes
    and payloads, this one sends them.

    Parameters
    -----------
    base_url: :class:`str`
        Where the API lives, :attr:`Route.BASE` unless requests go
        through a proxy.
    global_limit: :class:`int`
        The requests per second Discord allows the bot across all
        routes, 50 unless it raised the limit.
    max_ratelimit_timeout: Optional[:class:`float`]
        A 429 that asks to wait longer than this many seconds raises
        :exc:`RateLimited` instead of waiting. ``None`` waits however
        long Discord asks.
    timeout: :class:`float`
        Seconds one attempt may take before it counts as a failed
        connection and is retried.
    connections: :class:`int`
        How many connections to Discord may be open at once. Requests
        beyond that wait for one to come back.
    ssl_context: Optional[:class:`ssl.SSLContext`]
        The TLS settings, the platform's trust store when not given.

    Attributes
    -----------
    token: Optional[:class:`str`]
        The bot token, set by :meth:`login`.
    base_url: :class:`str`
        Where the API lives.
    max_ratelimit_timeout: Optional[:class:`float`]
        The longest wait a 429 may ask for.
    transport: :class:`~fablecord.net.HTTPClient`
        The connection pool underneath.
    limiter: :class:`RateLimiter`
        The rate limit state, one bucket per route and major parameter.
    messages: :class:`Messages`
        The message endpoints.
    channels: :class:`Channels`
        The channel, thread and stage endpoints.
    guilds: :class:`Guilds`
        The guild, member, role and ban endpoints.
    webhooks: :class:`Webhooks`
        The webhook endpoints, follow-ups of interactions among them.
    interactions: :class:`Interactions`
        The interaction response and application command endpoints.
    users: :class:`Users`
        The user and DM endpoints.
    emojis: :class:`Emojis`
        The emoji endpoints.
    stickers: :class:`Stickers`
        The sticker endpoints.
    scheduled_events: :class:`ScheduledEvents`
        The scheduled event endpoints.
    automod: :class:`AutoModeration`
        The auto moderation endpoints.
    invites: :class:`Invites`
        The invite endpoints.
    soundboard: :class:`Soundboard`
        The soundboard endpoints.
    applications: :class:`Applications`
        The application, entitlement and SKU endpoints.
    USER_AGENT: :class:`str`
        The ``User-Agent`` Discord requires of bots, naming the library
        and its version.
    """

    __slots__ = [
        "token",
        "base_url",
        "max_ratelimit_timeout",
        "transport",
        "limiter",
        "messages",
        "channels",
        "guilds",
        "webhooks",
        "interactions",
        "users",
        "emojis",
        "stickers",
        "scheduled_events",
        "automod",
        "invites",
        "soundboard",
        "applications",
        "_headers"
    ]

    USER_AGENT: Final = f"DiscordBot (https://github.com/cqlsh/Fablecord, {__version__}) Python/{version_info[0]}.{version_info[1]}"
    ATTEMPTS: Final = 5
    RETRIED: Final = (500, 502, 503, 504, 524)
    ME: Final = Route("GET", "/users/@me")
    _CDN_HEADERS: Final = {"User-Agent": USER_AGENT}

    def __init__(
            self,
            *,
            base_url: str = Route.BASE,
            global_limit: int = 50,
            max_ratelimit_timeout: float | None = None,
            timeout: float = 30.0,
            connections: int = 100,
            ssl_context: ssl.SSLContext | None = None
    ) -> None:
        self.token: str | None = None
        self.base_url = base_url
        self.max_ratelimit_timeout = max_ratelimit_timeout
        self.transport = HTTPClient(limit=connections, timeout=timeout, ssl_context=ssl_context)
        self.limiter = RateLimiter(global_limit=global_limit)
        self.messages = Messages(self)
        self.channels = Channels(self)
        self.guilds = Guilds(self)
        self.webhooks = Webhooks(self)
        self.interactions = Interactions(self)
        self.users = Users(self)
        self.emojis = Emojis(self)
        self.stickers = Stickers(self)
        self.scheduled_events = ScheduledEvents(self)
        self.automod = AutoModeration(self)
        self.invites = Invites(self)
        self.soundboard = Soundboard(self)
        self.applications = Applications(self)
        self._headers = {"User-Agent": self.USER_AGENT}

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()

    async def login(self, token: str, /) -> dict[str, Any]:
        """
        |coro|

        Takes the token into use and fetches the bot's own user with it,
        which is how a bad token shows up before anything else is tried.

        Parameters
        -----------
        token: :class:`str`
            The bot token, without the ``Bot`` prefix.

        Raises
        -------
        LoginFailure
            Discord rejected the token. The client keeps the token it
            had before.
        HTTPException
            Discord refused the request for another reason.

        Returns
        --------
        Dict[:class:`str`, Any]
            The user payload of the bot.
        """
        previous = self.token, self._headers
        self.token = token
        self._headers = {"User-Agent": self.USER_AGENT, "Authorization": f"Bot {token}"}

        try:
            return await self.request(self.ME.compile())
        except HTTPException as error:
            self.token, self._headers = previous

            if error.status == 401:
                raise LoginFailure("Improper token has been passed.") from error

            raise

    async def request(
            self,
            route: CompiledRoute,
            /,
            *,
            json: Any = None,
            files: Sequence[File] | None = None,
            form: MultipartBody | None = None,
            params: dict[str, Any] | None = None,
            reason: str | None = None
    ) -> Any:
        """
        |coro|

        Sends one request and returns what Discord answered.

        Parameters
        -----------
        route: :class:`CompiledRoute`
            The endpoint with its parameters filled in.
        json: Any
            The payload, sent as JSON.
        files: Optional[Sequence[:class:`File`]]
            Files to upload with the payload. The request then goes out
            as multipart, the payload as its ``payload_json`` part and
            the files as ``files[0]``, ``files[1]`` and so on, which is
            how the payload's ``attachments`` entries refer to them.
        form: Optional[:class:`~fablecord.net.MultipartBody`]
            A multipart body put together by hand, instead of ``json``
            and ``files``.
        params: Optional[Dict[:class:`str`, Any]]
            The query string. ``None`` values are left out, booleans are
            written the way Discord reads them.
        reason: Optional[:class:`str`]
            The reason to show in the audit log.

        Raises
        -------
        BadRequest
            Discord rejected the payload.
        Forbidden
            The bot lacks the permission.
        NotFound
            The resource does not exist.
        DiscordServerError
            Discord kept failing through every attempt.
        HTTPException
            Discord refused the request for another reason, or something
            in front of Discord answered a 429.
        RateLimited
            A 429 asked for a longer wait than ``max_ratelimit_timeout``
            allows.
        TypeError
            ``form`` was given together with ``json`` or ``files``.
        ConnectionError
            The connection kept failing through every attempt.
        TimeoutError
            The response kept taking longer than ``timeout``.

        Returns
        --------
        Any
            The JSON Discord sent, ``None`` for a response without a
            body, the text for one that is not JSON.
        """
        method = route.method
        url = self.base_url + route.path
        if params:
            url = f"{url}?{self._query(params)}"

        headers = self._headers
        if reason is not None:
            headers = {**headers, "X-Audit-Log-Reason": quote(reason, safe="/ ")}

        if files:
            if form is not None:
                raise TypeError("files and form cannot be sent together")

            form = MultipartBody()
            form.add_field("payload_json", dumps(json, separators=(",", ":")), content_type="application/json")

            for index, file in enumerate(files):
                form.add_file(f"files[{index}]", file.data, filename=file.filename)

            body = form.encode()
            content_type = form.content_type
        elif form is not None:
            if json is not None:
                raise TypeError("json and form cannot be sent together")

            body = form.encode()
            content_type = form.content_type
        elif json is not None:
            body = dumps(json, separators=(",", ":")).encode()
            content_type = "application/json"
        else:
            body = None
            content_type = None

        transport = self.transport
        limiter = self.limiter
        attempt = 0

        while True:
            bucket = await limiter.acquire(route)

            try:
                response = await transport.request(method, url, headers=headers, body=body, content_type=content_type)
            except (OSError, TimeoutError) as error:
                limiter.release(bucket)
                attempt += 1

                if attempt == self.ATTEMPTS:
                    raise

                _log.warning("%s %s failed with %r, attempt %d of %d in %d seconds", method, route.path, error, attempt + 1, self.ATTEMPTS, 2 * attempt - 1)
                await asyncio.sleep(2 * attempt - 1)

                continue

            status = response.status
            data = self._parse(response)
            retry_after = self._retry_after(data) if status == 429 else None
            limiter.update(route, bucket, status, response.headers, retry_after=retry_after)

            if status < 300:
                return data

            if status == 429:
                if retry_after is None or "via" not in response.headers:
                    raise HTTPException(response, data)

                if self.max_ratelimit_timeout is not None and retry_after > self.max_ratelimit_timeout:
                    raise RateLimited(retry_after)

                attempt += 1

                if attempt == self.ATTEMPTS:
                    raise HTTPException(response, data)

                _log.warning("%s %s is rate limited, retrying in %.2f seconds", method, route.path, retry_after)

                continue

            if status in self.RETRIED:
                attempt += 1

                if attempt == self.ATTEMPTS:
                    raise DiscordServerError(response, data)

                _log.warning("%s %s returned %d, attempt %d of %d in %d seconds", method, route.path, status, attempt + 1, self.ATTEMPTS, 2 * attempt - 1)
                await asyncio.sleep(2 * attempt - 1)

                continue

            raise self._error(response, data)

    async def get_from_cdn(self, url: str, /) -> bytes:
        """
        |coro|

        Downloads an asset from Discord's CDN, an avatar or an
        attachment. The token stays out of it.

        Parameters
        -----------
        url: :class:`str`
            The absolute URL of the asset.

        Raises
        -------
        NotFound
            There is no asset at the URL.
        Forbidden
            The asset may not be read.
        HTTPException
            Fetching the asset failed for another reason.

        Returns
        --------
        :class:`bytes`
            The asset.
        """
        response = await self.transport.request("GET", url, headers=self._CDN_HEADERS)
        status = response.status

        if status == 200:
            return response.body

        if status == 404:
            raise NotFound(response, "asset not found")

        if status == 403:
            raise Forbidden(response, "cannot retrieve asset")

        raise HTTPException(response, "failed to get asset")

    async def close(self) -> None:
        """
        |coro|

        Closes the connections. Requests in flight finish first.
        """
        await self.transport.close()

    @staticmethod
    def _query(params: dict[str, Any], /) -> str:
        """
        Builds the query string, with booleans lowercased and ``None``
        left out, since Discord reads ``True`` as a string it does not
        know.
        """
        return urlencode({name: str(value).lower() if isinstance(value, bool) else value for name, value in params.items() if value is not None})

    @staticmethod
    def _parse(response: HTTPResponse, /) -> Any:
        """
        Reads the body as JSON when Discord says it is, as text otherwise,
        which is what an error page from Cloudflare comes as.
        """
        body = response.body
        if not body:
            return None

        if response.headers.get("content-type", "").startswith("application/json"):
            return loads(body)

        return body.decode("utf-8", "replace")

    @staticmethod
    def _retry_after(data: Any, /) -> float | None:
        """
        The seconds a 429 asks to wait, from the body Discord sends with
        it. ``None`` when the body is not Discord's, an error page from
        something in front of it for one.
        """
        if isinstance(data, dict):
            value = cast(dict[str, Any], data).get("retry_after")

            if isinstance(value, (int, float)):
                return float(value)

        return None

    @staticmethod
    def _error(response: HTTPResponse, data: Any, /) -> HTTPException:
        """
        Picks the exception for a status Discord refused with.
        """
        status = response.status

        if status == 400:
            return BadRequest(response, data)

        if status == 403:
            return Forbidden(response, data)

        if status == 404:
            return NotFound(response, data)

        if status >= 500:
            return DiscordServerError(response, data)

        return HTTPException(response, data)

__all__ = ["RESTClient", "Response"]