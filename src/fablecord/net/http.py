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

import asyncio
import json
import ssl

from typing import Any, Final, Self
from collections import deque

class HTTPResponse:
    """
    The answer to one request, read to the end.

    Attributes
    -----------
    status: :class:`int`
        The status code.
    reason: :class:`str`
        The reason phrase after the status code, ``OK`` or ``Not Found``.
    headers: Dict[:class:`str`, :class:`str`]
        The response headers with lowercased names. A header that came
        more than once is joined with commas.
    body: :class:`bytes`
        The raw body, empty when there was none.
    """

    __slots__ = ["status", "reason", "headers", "body"]

    def __init__(self, status: int, reason: str, headers: dict[str, str], body: bytes) -> None:
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body

    def text(self, encoding: str = "utf-8", /) -> str:
        """
        The body decoded as text.
        """
        return self.body.decode(encoding)

    def json(self) -> Any:
        """
        The body parsed as JSON.
        """
        return json.loads(self.body)

    def __repr__(self) -> str:
        return f"<HTTPResponse status={self.status} reason={self.reason!r} length={len(self.body)}>"

class HTTPProtocol(asyncio.Protocol):
    """
    One HTTP/1.1 connection that parses responses as the bytes arrive.

    It serves one request at a time. The response is assembled straight
    out of :meth:`data_received` without streams or intermediate reads.
    A response that arrives in one piece, which is the usual case for an
    API, is parsed in place on the bytes the loop handed over, the only
    copy being the body itself. Only a response split across several
    reads goes through a buffer.
    """

    __slots__ = (
        "transport",
        "closed",
        "keep_alive",
        "buffer",
        "waiter",
        "status",
        "reason",
        "headers",
        "head_only",
        "chunked",
        "remaining",
        "chunk_size",
        "parts",
        "in_body",
        "deadline",
        "timer"
    )

    _NAMES: Final[dict[str, str]] = {}

    def __init__(self) -> None:
        self.transport: asyncio.Transport | None = None
        self.closed = False
        self.keep_alive = True
        self.buffer: bytes | bytearray = b""
        self.waiter: asyncio.Future[HTTPResponse] | None = None
        self.head_only = False
        self.deadline = 0.0
        self.timer: asyncio.TimerHandle | None = None
        self._reset()

    def _reset(self) -> None:
        self.status = 0
        self.reason = ""
        self.headers: dict[str, str] = {}
        self.chunked = False
        self.remaining = -1
        self.chunk_size = -1
        self.parts: list[bytes] = []
        self.in_body = False

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        assert isinstance(transport, asyncio.Transport)

        self.transport = transport

    def connection_lost(self, exc: Exception | None) -> None:
        self.closed = True
        self.keep_alive = False

        timer = self.timer
        if timer is not None:
            timer.cancel()
            self.timer = None

        waiter = self.waiter
        if waiter is None or waiter.done():
            return

        if self.in_body and self.remaining < 0 and not self.chunked:
            self._complete()
            return

        waiter.set_exception(exc or ConnectionResetError("the connection was closed before the response was complete"))

    def data_received(self, data: bytes) -> None:
        buffer = self.buffer
        if buffer:
            buffer += data
        else:
            buffer = data

        try:
            offset = self._parse(buffer)
        except ValueError as error:
            self._fail(ConnectionError(f"malformed response: {error}"))
            return

        if offset == len(buffer):
            self.buffer = b""
        elif isinstance(buffer, bytearray):
            del buffer[:offset]
            self.buffer = buffer
        else:
            self.buffer = bytearray(buffer[offset:])

    def send(self, request: bytes, head_only: bool, timeout: float, /) -> asyncio.Future[HTTPResponse]:
        """
        Writes one request and returns the future for its response.

        The connection keeps one timer for its timeouts instead of one
        per request: it is set when none is pending and, when it fires
        with a response still outstanding, moves itself to that
        response's deadline. A request costs no timer of its own.

        Parameters
        -----------
        request: :class:`bytes`
            The full request, head and body.
        head_only: :class:`bool`
            Whether it was a ``HEAD`` request, whose response has no body
            no matter what the headers say.
        timeout: :class:`float`
            Seconds the response may take, after which the future fails
            with :class:`TimeoutError` and the connection is closed.
        """
        assert self.transport is not None

        loop = asyncio.get_running_loop()
        self.head_only = head_only
        self.waiter = loop.create_future()
        self.deadline = loop.time() + timeout

        if self.timer is None:
            self.timer = loop.call_at(self.deadline, self._expire)

        self.transport.write(request)

        return self.waiter

    def close(self) -> None:
        """
        Closes the connection, failing a response still in flight.
        """
        if self.transport is not None and not self.closed:
            self.transport.close()

        self.closed = True

        timer = self.timer
        if timer is not None:
            timer.cancel()
            self.timer = None

    def _expire(self) -> None:
        """
        The timer firing: with no response outstanding there is nothing
        to watch until the next request, with one past its deadline the
        request fails, with one still in time the timer moves on to its
        deadline.
        """
        self.timer = None

        waiter = self.waiter
        if waiter is None or waiter.done():
            return

        loop = asyncio.get_running_loop()
        if loop.time() >= self.deadline:
            self._fail(TimeoutError("the response did not arrive in time"))
        else:
            self.timer = loop.call_at(self.deadline, self._expire)

    def _parse(self, buffer: bytes | bytearray, /) -> int:
        offset = 0

        while True:
            if not self.in_body:
                offset, ready = self._parse_head(buffer, offset)
                if not ready:
                    return offset

                if not self.in_body:
                    continue

            if self.chunked:
                offset, done = self._parse_chunks(buffer, offset)
                if not done:
                    return offset
            elif self.remaining >= 0:
                end = offset + self.remaining
                if len(buffer) < end:
                    return offset

                self.parts.append(bytes(buffer[offset:end]))
                offset = end
            else:
                self.parts.append(bytes(buffer[offset:]))

                return len(buffer)

            self._complete()

            return offset

    def _parse_head(self, buffer: bytes | bytearray, offset: int, /) -> tuple[int, bool]:
        end = buffer.find(b"\r\n\r\n", offset)
        if end < 0:
            return offset, False

        head = bytes(buffer[offset:end]).decode("latin-1")
        status_line, _, block = head.partition("\r\n")
        version, _, rest = status_line.partition(" ")
        status, _, reason = rest.partition(" ")

        if version[:7] != "HTTP/1." or not status.isdigit():
            raise ValueError(f"bad status line {status_line!r}")

        self.status = int(status)
        self.reason = reason
        self.headers = self._parse_headers(block)

        if self.status < 200:
            self._reset()

            return end + 4, True

        self.in_body = True
        default = "keep-alive" if version == "HTTP/1.1" else "close"
        self.keep_alive = self.headers.get("connection", default).lower() != "close"

        if self.head_only or self.status in (204, 304):
            self.remaining = 0
        elif "chunked" in self.headers.get("transfer-encoding", ""):
            self.chunked = True
        elif "content-length" in self.headers:
            self.remaining = int(self.headers["content-length"])
        else:
            self.keep_alive = False

        return end + 4, True

    @staticmethod
    def _parse_headers(block: str, /) -> dict[str, str]:
        """
        Turns the header lines into a dict with lowercased names.

        Lowercased names are remembered across responses, a server sends
        the same handful of headers every time, so after the first
        response the lowering is a dict read.
        """
        headers: dict[str, str] = {}
        names = HTTPProtocol._NAMES

        for line in block.split("\r\n"):
            name, separator, value = line.partition(":")
            if not separator:
                if not line:
                    continue

                raise ValueError(f"bad header line {line!r}")

            lowered = names.get(name)
            if lowered is None:
                lowered = name.strip().lower()

                if len(names) < 256:
                    names[name] = lowered

            value = value.strip()
            previous = headers.get(lowered)
            headers[lowered] = value if previous is None else f"{previous}, {value}"

        return headers

    def _parse_chunks(self, buffer: bytes | bytearray, offset: int, /) -> tuple[int, bool]:
        while True:
            if self.chunk_size < 0:
                end = buffer.find(b"\r\n", offset)
                if end < 0:
                    return offset, False

                self.chunk_size = int(bytes(buffer[offset:end]).partition(b";")[0], 16)
                offset = end + 2

            if self.chunk_size == 0:
                if buffer[offset:offset + 2] == b"\r\n":
                    return offset + 2, True

                end = buffer.find(b"\r\n\r\n", offset)
                if end < 0:
                    return offset, False

                return end + 4, True

            end = offset + self.chunk_size
            if len(buffer) < end + 2:
                return offset, False

            self.parts.append(bytes(buffer[offset:end]))
            offset = end + 2
            self.chunk_size = -1

    def _complete(self) -> None:
        parts = self.parts
        body = parts[0] if len(parts) == 1 else b"".join(parts)
        response = HTTPResponse(self.status, self.reason, self.headers, body)
        waiter = self.waiter

        self._reset()
        self.waiter = None

        if waiter is not None and not waiter.done():
            waiter.set_result(response)

        if not self.keep_alive:
            self.close()

    def _fail(self, error: Exception, /) -> None:
        waiter = self.waiter
        self.waiter = None
        self.close()

        if waiter is not None and not waiter.done():
            waiter.set_exception(error)

class HTTPClient:
    """
    An HTTP/1.1 client with a keep-alive pool and nothing Discord in it.

    Connections are kept per host and handed out again for the next
    request, up to ``limit`` of them per host at once. Requests beyond
    that wait for a connection to come back. TLS uses the platform's
    trust store through :mod:`ssl`.

    Attributes
    -----------
    limit: :class:`int`
        How many connections one host may have open at the same time.
    timeout: :class:`float`
        Seconds a request may take from first byte sent to last byte
        received, after which :class:`TimeoutError` is raised.
    """

    __slots__ = ["limit", "timeout", "_ssl", "_idle", "_open", "_waiters", "_closed"]

    DEFAULT_PORTS: Final = {"http": 80, "https": 443}

    def __init__(self, *, limit: int = 100, timeout: float = 30.0, ssl_context: ssl.SSLContext | None = None) -> None:
        self.limit = limit
        self.timeout = timeout
        self._ssl = ssl_context
        self._idle: dict[tuple[str, str, int], deque[HTTPProtocol]] = {}
        self._open: dict[tuple[str, str, int], int] = {}
        self._waiters: dict[tuple[str, str, int], deque[asyncio.Future[None]]] = {}
        self._closed = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()

    async def request(
            self,
            method: str,
            url: str,
            /,
            *,
            headers: dict[str, str] | None = None,
            body: bytes | None = None,
            content_type: str | None = None
    ) -> HTTPResponse:
        """
        |coro|

        Sends one request and reads the whole response.

        Parameters
        -----------
        method: :class:`str`
            The HTTP method, uppercase.
        url: :class:`str`
            The absolute URL, ``https://host/path?query``.
        headers: Optional[Dict[:class:`str`, :class:`str`]]
            Extra request headers. ``Host`` and ``Content-Length`` are
            added here, everything else is up to the caller.
        body: Optional[:class:`bytes`]
            The request body, already encoded.
        content_type: Optional[:class:`str`]
            The ``Content-Type`` of the body.

        Raises
        -------
        ConnectionError
            The connection failed or the server sent something that is
            not HTTP.
        TimeoutError
            The response did not arrive within :attr:`timeout`.

        Returns
        --------
        :class:`HTTPResponse`
            The response with its full body.
        """
        scheme, host, port, path = self._split(url)
        key = (scheme, host, port)
        request = self._build(method, host, port, path, headers, body, content_type)

        idle = self._idle.get(key)
        if idle and not idle[-1].closed:
            protocol = idle.pop()
        else:
            protocol = await self._acquire(key)

        try:
            response = await protocol.send(request, method == "HEAD", self.timeout)
        except BaseException:
            protocol.close()
            self._release(key, protocol)

            raise

        self._release(key, protocol)

        return response

    async def close(self) -> None:
        """
        |coro|

        Closes every idle connection. Requests in flight finish on their
        own connections, which are dropped afterwards.
        """
        self._closed = True

        for idle in self._idle.values():
            while idle:
                idle.pop().close()

        for waiters in self._waiters.values():
            while waiters:
                waiter = waiters.popleft()
                if not waiter.done():
                    waiter.set_exception(ConnectionError("the client is closed"))

    @staticmethod
    def _split(url: str, /) -> tuple[str, str, int, str]:
        scheme, separator, rest = url.partition("://")
        if not separator:
            raise ValueError(f"{url!r} is not an absolute URL")

        authority, slash, path = rest.partition("/")
        host, colon, port = authority.partition(":")
        default_port = HTTPClient.DEFAULT_PORTS.get(scheme)

        if default_port is None:
            raise ValueError(f"{scheme!r} is not a scheme this client speaks")

        return scheme, host, int(port) if colon else default_port, slash + path if slash else "/"

    @staticmethod
    def _build(
        method: str,
        host: str,
        port: int,
        path: str,
        headers: dict[str, str] | None,
        body: bytes | None,
        content_type: str | None
    ) -> bytes:
        lines = [f"{method} {path} HTTP/1.1", f"Host: {host}" if port in (80, 443) else f"Host: {host}:{port}"]

        if headers:
            lines.extend(f"{name}: {value}" for name, value in headers.items())

        if body is not None:
            lines.append(f"Content-Length: {len(body)}")

            if content_type is not None:
                lines.append(f"Content-Type: {content_type}")
        elif method in ("POST", "PUT", "PATCH"):
            lines.append("Content-Length: 0")

        lines.append("\r\n")
        head = "\r\n".join(lines).encode("latin-1")

        return head if body is None else head + body

    async def _acquire(self, key: tuple[str, str, int], /) -> HTTPProtocol:
        if self._closed:
            raise ConnectionError("the client is closed")

        while True:
            idle = self._idle.get(key)
            while idle:
                protocol = idle.pop()
                if not protocol.closed:
                    return protocol

                self._open[key] -= 1

            if self._open.get(key, 0) < self.limit:
                break

            waiter = asyncio.get_running_loop().create_future()
            self._waiters.setdefault(key, deque()).append(waiter)
            await waiter

        self._open[key] = self._open.get(key, 0) + 1

        try:
            return await self._connect(key)
        except BaseException:
            self._open[key] -= 1
            self._wake(key)

            raise

    async def _connect(self, key: tuple[str, str, int], /) -> HTTPProtocol:
        """
        Opens a connection for the key.

        The TLS context is built on the first secure connection and kept.
        Building it reads the certificate store from disk, so that one
        blocking call goes to the executor instead of the loop.
        """
        scheme, host, port = key
        loop = asyncio.get_running_loop()

        if scheme == "https":
            if self._ssl is None:
                self._ssl = await loop.run_in_executor(None, ssl.create_default_context)

            _, protocol = await loop.create_connection(HTTPProtocol, host, port, ssl=self._ssl, server_hostname=host)
        else:
            _, protocol = await loop.create_connection(HTTPProtocol, host, port)

        return protocol

    def _release(self, key: tuple[str, str, int], protocol: HTTPProtocol, /) -> None:
        if protocol.closed or not protocol.keep_alive or self._closed:
            protocol.close()
            self._open[key] -= 1
        else:
            self._idle.setdefault(key, deque()).append(protocol)

        self._wake(key)

    def _wake(self, key: tuple[str, str, int], /) -> None:
        waiters = self._waiters.get(key)

        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)

                return

__all__ = ["HTTPResponse", "HTTPProtocol", "HTTPClient"]