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
import ssl

from typing import ClassVar, Final, Self
from collections.abc import Callable
from collections import deque
from base64 import b64encode
from struct import Struct
from hashlib import sha1
from sys import maxsize
from os import urandom

try:
    from fablecord._speedups.websocket import parse as _parse_frames
    from fablecord._speedups.websocket import frame as _frame
except ImportError:
    _frame: Callable[[int, int, bytes], bytes] | None = None
    _parse_frames: Callable[[bytes, int, int, deque[str | bytes]], int] | None = None

_ACCEPT_GUID: Final = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
_WHOLE_TEXT: Final = 0x81
_WHOLE_TEXT_OR_BINARY: Final = (0x81, 0x82)
_RESERVED_CLOSE_CODES: Final = (1004, 1005, 1006)
_HEADER_64: Final = Struct("!BBQ").pack
_KEYS: Final = Struct("!256I").unpack
_IDENTITY: Final = int.from_bytes(bytes(range(256)))
_MASK_TABLES: Final[list[bytes]] = [
    (_IDENTITY ^ int.from_bytes(bytes([key]) * 256)).to_bytes(256) for key in range(256)
]

class WebSocketClosed(ConnectionError):
    """
    The connection is closed and nothing more will arrive.

    :meth:`WebSocket.receive` raises it once the queued messages are
    drained, so a read loop ends here.

    Attributes
    -----------
    code: :class:`int`
        The close code. Codes from 1000 to 1015 are defined by RFC 6455,
        Discord uses its own from 4000 upwards. ``1006`` means the
        connection dropped without a close frame.
    reason: :class:`str`
        The reason the closing side gave, often empty.
    """

    def __init__(self, code: int, reason: str) -> None:
        message = f"websocket closed with code {code}: {reason}" if reason else f"websocket closed with code {code}"
        super().__init__(message)

        self.code = code
        self.reason = reason

class WebSocket(asyncio.Protocol):
    """
    One RFC 6455 client connection.

    Frames are parsed straight out of :meth:`data_received`. A message
    that fits in one read is sliced from the bytes the loop handed
    over; one spread over several reads is collected as pieces and
    joined once. Messages queue up for :meth:`receive`, pings are
    answered on the spot and a close frame is echoed before the
    transport goes down. No extension is negotiated, so a frame with
    RSV bits set is an error. Outgoing frames are built by the C helper
    in :mod:`fablecord._speedups` when it was compiled, otherwise in
    Python with the same result.

    Attributes
    -----------
    close_code: Optional[:class:`int`]
        The close code once the connection is closed, ``1006`` if it
        dropped without a close frame, ``None`` while it is open.
    close_reason: :class:`str`
        The close reason, empty until a close frame with one arrives.
    closing: :class:`bool`
        Whether a close frame went out already. Nothing but the peer's
        close frame is expected after that.
    closed: :class:`bool`
        Whether the transport is gone.
    paused: :class:`bool`
        Whether asyncio holds more than 64 KB of unsent data for this
        connection. Sends still go through, but a caller sending in
        bulk should await :meth:`drain` while this is set.
    """

    __slots__ = (
        "transport",
        "key",
        "max_size",
        "limit",
        "open",
        "closing",
        "closed",
        "close_code",
        "close_reason",
        "paused",
        "buffer",
        "frame_first",
        "parts",
        "needed",
        "messages",
        "waiter",
        "drain_waiter",
        "handshake",
        "disconnected",
        "fragments",
        "fragment_opcode",
        "fragment_length",
        "keys"
    )

    DEFAULT_PORTS: Final[dict[str, int]] = {"ws": 80, "wss": 443}
    CLOSE_TIMEOUT: Final = 5.0
    _ALIGNMENTS: Final[dict[int, tuple[int, int]]] = {}
    _ssl: ClassVar[ssl.SSLContext | None] = None

    def __init__(self, key: str, max_size: int | None, loop: asyncio.AbstractEventLoop) -> None:
        self.transport: asyncio.Transport | None = None
        self.key = key
        self.max_size = max_size
        self.limit = -1 if max_size is None else min(max_size, maxsize)
        self.open = False
        self.closing = False
        self.closed = False
        self.close_code: int | None = None
        self.close_reason = ""
        self.paused = False
        self.buffer = b""
        self.frame_first = 0
        self.parts: list[bytes] = []
        self.needed = 0
        self.messages: deque[str | bytes] = deque()
        self.waiter: asyncio.Future[None] | None = None
        self.drain_waiter: asyncio.Future[None] | None = None
        self.handshake = loop.create_future()
        self.disconnected = loop.create_future()
        self.fragments: list[bytes] = []
        self.fragment_opcode = 0
        self.fragment_length = 0
        self.keys: list[int] = []

    @classmethod
    async def connect(
        cls,
        url: str,
        /,
        *,
        headers: dict[str, str] | None = None,
        ssl_context: ssl.SSLContext | None = None,
        timeout: float = 30.0,
        max_size: int | None = None
    ) -> Self:
        """
        |coro|

        Opens a connection and completes the handshake.

        Parameters
        -----------
        url: :class:`str`
            The absolute ``ws://`` or ``wss://`` URL, query string included.
        headers: Optional[Dict[:class:`str`, :class:`str`]]
            Extra handshake headers. The ones the upgrade needs are set here.
        ssl_context: Optional[:class:`ssl.SSLContext`]
            The TLS context for ``wss``. Without one, a default context
            is built once in the executor and shared by every later
            connection.
        timeout: :class:`float`
            Seconds for connecting and the handshake together.
        max_size: Optional[:class:`int`]
            The largest message accepted in bytes. A bigger one closes
            the connection with code ``1009``. ``None`` accepts any size,
            which Discord's gateway needs since a ``GUILD_CREATE`` can run
            into megabytes.

        Raises
        -------
        ValueError
            The URL is not a ``ws`` or ``wss`` URL, or ``max_size`` is negative.
        ConnectionError
            The connection failed or the server did not accept the upgrade.
        TimeoutError
            Connecting and the handshake took longer than ``timeout``.

        Returns
        --------
        :class:`WebSocket`
            The open connection.
        """
        if max_size is not None and max_size < 0:
            raise ValueError("max_size cannot be negative")

        secure, host, port, path = cls._split(url)
        key = b64encode(urandom(16)).decode()
        request = cls._build(host, port, path, key, headers)
        loop = asyncio.get_running_loop()
        protocol = cls(key, max_size, loop)

        try:
            async with asyncio.timeout(timeout):
                if secure:
                    if ssl_context is None:
                        ssl_context = await cls._default_ssl()

                    transport, _ = await loop.create_connection(
                        lambda: protocol, host, port, ssl=ssl_context, server_hostname=host
                    )
                else:
                    transport, _ = await loop.create_connection(lambda: protocol, host, port)

                transport.write(request)
                await protocol.handshake
        except BaseException:
            protocol.handshake.cancel()

            if protocol.transport is not None:
                protocol.transport.close()

            raise

        return protocol

    async def receive(self) -> str | bytes:
        """
        |coro|

        Waits for the next message.

        Text frames come back as :class:`str`, binary frames as
        :class:`bytes`. Messages that arrived before the connection
        closed are still handed out, then the close is raised. Only one
        caller may wait at a time.

        Raises
        -------
        WebSocketClosed
            The connection is closed and no message is left.
        RuntimeError
            Another :meth:`receive` is already waiting.
        """
        messages = self.messages

        while not messages:
            if self.close_code is not None:
                raise WebSocketClosed(self.close_code, self.close_reason)

            if self.waiter is not None and not self.waiter.done():
                raise RuntimeError("another receive() is already waiting on this websocket")

            waiter = asyncio.get_running_loop().create_future()
            self.waiter = waiter

            try:
                await waiter
            finally:
                if self.waiter is waiter:
                    self.waiter = None

        return messages.popleft()

    def send_text(self, text: str, /) -> None:
        """
        Sends one text message.

        The frame goes to the transport at once, there is nothing to
        await; asyncio buffers it if the socket is not ready and sets
        :attr:`paused` once that buffer grows past 64 KB.

        Raises
        -------
        ConnectionError
            The connection is closing or closed.
        """
        if self.closing:
            raise ConnectionError("the websocket is closed")

        self._send_frame(1, text.encode())

    def send_bytes(self, data: bytes, /) -> None:
        """
        Sends one binary message.

        Raises
        -------
        ConnectionError
            The connection is closing or closed.
        """
        if self.closing:
            raise ConnectionError("the websocket is closed")

        self._send_frame(2, data)

    def ping(self, data: bytes = b"", /) -> None:
        """
        Sends a ping, which the peer must answer with a pong carrying
        the same payload. The pong is swallowed here, so this only
        keeps a quiet connection alive; Discord measures latency with
        its own heartbeat instead.

        Raises
        -------
        ConnectionError
            The connection is closing or closed.
        """
        if self.closing:
            raise ConnectionError("the websocket is closed")

        self._send_frame(9, data)

    async def drain(self) -> None:
        """
        |coro|

        Waits until asyncio has handed the buffered sends to the socket.

        Returns at once unless :attr:`paused` is set. Without this a
        caller that sends far more than the socket takes keeps every
        unsent frame in memory; checking :attr:`paused` after each send
        and awaiting this when it is set keeps that buffer near 64 KB.
        A connection that drops while waiting ends the wait, the next
        send then raises.

        Raises
        -------
        RuntimeError
            Another :meth:`drain` is already waiting.
        """
        if not self.paused or self.closed:
            return

        if self.drain_waiter is not None and not self.drain_waiter.done():
            raise RuntimeError("another drain() is already waiting on this websocket")

        waiter = asyncio.get_running_loop().create_future()
        self.drain_waiter = waiter

        try:
            await waiter
        finally:
            if self.drain_waiter is waiter:
                self.drain_waiter = None

    async def close(self, code: int = 1000, reason: str = "") -> None:
        """
        |coro|

        Starts the closing handshake and waits for the connection to go
        down.

        The close frame goes out right away, the peer answers with its
        own and drops the TCP connection. If that does not happen within
        :attr:`CLOSE_TIMEOUT` seconds the transport is aborted. On a
        connection that is already closed this returns at once.

        Parameters
        -----------
        code: :class:`int`
            The close code to send, ``1000`` for a normal end. RFC 6455
            allows ``1000`` to ``1014`` without the reserved ``1004``,
            ``1005`` and ``1006``, and ``3000`` to ``4999`` for libraries
            and applications, where Discord's own codes live.
        reason: :class:`str`
            A short reason for the peer, at most 123 bytes of UTF-8.

        Raises
        -------
        ValueError
            The code may not be sent or the reason is too long for a
            control frame.
        """
        if not self._is_close_code(code):
            raise ValueError(f"{code} is not a close code that may be sent")

        payload = code.to_bytes(2) + reason.encode()
        if len(payload) > 125:
            raise ValueError("the close reason is longer than 123 bytes of UTF-8")

        transport = self.transport
        if transport is None or self.closed:
            return

        if not self.closing:
            self.closing = True
            self._send_frame(8, payload)

        _, pending = await asyncio.wait([self.disconnected], timeout=self.CLOSE_TIMEOUT)

        if pending:
            transport.abort()
            await asyncio.wait([self.disconnected])

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        assert isinstance(transport, asyncio.Transport)

        self.transport = transport

    def connection_lost(self, exc: Exception | None) -> None:
        self.closing = True
        self.closed = True
        self.buffer = b""
        self.parts = []
        self.needed = 0

        if self.close_code is None:
            self.close_code = 1006

        if not self.handshake.done():
            self.handshake.set_exception(exc or ConnectionResetError("the connection was closed during the handshake"))

        self._wake_closed()
        self.resume_writing()

        if not self.disconnected.done():
            self.disconnected.set_result(None)

    def pause_writing(self) -> None:
        self.paused = True

    def resume_writing(self) -> None:
        self.paused = False

        waiter = self.drain_waiter
        if waiter is not None:
            self.drain_waiter = None

            if not waiter.done():
                waiter.set_result(None)

    def data_received(self, data: bytes) -> None:
        """
        Parses what arrived.

        A frame whose payload did not fit in the read that brought its
        header is collected read by read in :attr:`parts` and joined
        once it is complete, so a large message costs one copy no
        matter how many reads it took. Only an unfinished frame header,
        at most thirteen bytes, is carried over into the next read. A
        read that asyncio still hands over after the connection was
        failed or refused is dropped; the proactor loop on Windows does
        that with a read that had completed before the close.
        """
        if self.close_code is not None:
            return

        offset = 0
        needed = self.needed

        if needed:
            if len(data) < needed:
                self.parts.append(data)
                self.needed = needed - len(data)
                return

            self.parts.append(data if len(data) == needed else data[:needed])
            payload = b"".join(self.parts)
            self.parts = []
            self.needed = 0
            self._handle_frame(self.frame_first, payload)

            if self.close_code is not None or len(data) == needed:
                return

            buffer = data
            offset = needed
        elif self.buffer:
            buffer = self.buffer + data
        else:
            buffer = data

        if self.open:
            offset = self._parse(buffer, offset)
        else:
            if self.handshake.done():
                return

            offset = self._parse_handshake(buffer)

            if self.open and offset < len(buffer):
                offset = self._parse(buffer, offset)

        if offset == len(buffer) or self.close_code is not None:
            self.buffer = b""
        else:
            self.buffer = buffer[offset:]

    def _parse_handshake(self, buffer: bytes, /) -> int:
        """
        Checks the server's upgrade response once it is complete and
        returns where the first frame starts, ``0`` while the response
        is still incomplete.
        """
        end = buffer.find(b"\r\n\r\n")
        if end < 0:
            return 0

        head = buffer[:end].decode("latin-1")
        status_line, _, block = head.partition("\r\n")
        _, _, status = status_line.partition(" ")

        if not status.startswith("101"):
            self._refuse(f"the server answered {status_line!r} instead of switching protocols")
            return end + 4

        accept = ""
        for line in block.split("\r\n"):
            name, separator, value = line.partition(":")
            if separator and name.strip().lower() == "sec-websocket-accept":
                accept = value.strip()
                break

        expected = b64encode(sha1((self.key + _ACCEPT_GUID).encode()).digest()).decode()
        if accept != expected:
            self._refuse("the server sent a wrong Sec-WebSocket-Accept")
            return end + 4

        self.open = True
        self.handshake.set_result(None)

        return end + 4

    def _parse(self, buffer: bytes, offset: int, /) -> int:
        """
        Handles every complete frame in the buffer and returns the
        offset of the first incomplete one.

        A whole data frame outside a fragmented message, which is every
        frame Discord sends, is delivered right here, by the C helper
        when it is there. Fragments and control frames go through the
        helpers. A frame whose payload runs past the buffer switches
        the connection to collecting the rest in :attr:`parts`.
        """
        total = len(buffer)
        max_size = self.max_size
        limit = self.limit
        messages = self.messages

        while total - offset >= 2:
            if _parse_frames is not None and not self.fragment_opcode:
                offset = _parse_frames(buffer, offset, limit, messages)

                if messages and self.waiter is not None:
                    self._wake_receiver()

                if total - offset < 2:
                    break

            first = buffer[offset]
            second = buffer[offset + 1]
            length = second & 0x7F
            start = offset + 2

            if length == 126:
                if total - start < 2:
                    break

                length = buffer[start] << 8 | buffer[start + 1]
                start += 2

                if length < 126:
                    self._fail(1002, "the server sent a 16-bit length for a payload that fits in 7 bits")
                    break
            elif length == 127:
                if total - start < 8:
                    break

                length = int.from_bytes(buffer[start:start + 8])
                start += 8

                if length < 65536 or length >> 63:
                    self._fail(1002, "the server sent a 64-bit length that is not minimal or has its top bit set")
                    break

            if second & 0x80 or first & 0x70:
                self._fail(1002, "the server sent a masked frame or set RSV bits without an extension")
                break

            if first & 0x08:
                if length > 125 or not first & 0x80:
                    self._fail(1002, "the server sent a fragmented or oversized control frame")
                    break
            elif max_size is not None and self.fragment_length + length > max_size:
                self._fail(1009, f"a message above {max_size} bytes")
                break

            end = start + length
            if end > total:
                self.frame_first = first
                self.parts = [buffer[start:]]
                self.needed = end - total

                return total

            payload = buffer[start:end]
            offset = end

            if first in _WHOLE_TEXT_OR_BINARY and not self.fragment_opcode:
                if first == _WHOLE_TEXT:
                    try:
                        message: str | bytes = payload.decode()
                    except UnicodeDecodeError:
                        self._fail(1007, "the server sent text that is not valid UTF-8")
                        break
                else:
                    message = payload

                messages.append(message)
                waiter = self.waiter

                if waiter is not None:
                    self.waiter = None

                    if not waiter.done():
                        waiter.set_result(None)

                continue

            self._handle_frame(first, payload)

            if self.close_code is not None:
                break

        return offset

    def _handle_frame(self, first: int, payload: bytes, /) -> None:
        """
        Handles a frame off the fast path: a fragment, a continuation,
        a control frame or a data frame that was collected over several
        reads.
        """
        opcode = first & 0x0F

        if opcode < 3:
            self._handle_data(first, opcode, payload)
        elif opcode == 8:
            self._handle_close(payload)
        elif opcode == 9:
            if not self.closing:
                self._send_frame(10, payload)
        elif opcode != 10:
            self._fail(1002, f"the server sent an unknown opcode {opcode}")

    def _handle_data(self, first: int, opcode: int, payload: bytes, /) -> None:
        """
        Delivers a whole message or collects one more fragment of it.
        """
        if opcode:
            if self.fragment_opcode:
                self._fail(1002, "the server started a new message inside a fragmented one")
                return

            if first & 0x80:
                self._deliver(opcode, payload)
                return

            self.fragment_opcode = opcode
            self.fragments = [payload]
            self.fragment_length = len(payload)
            return

        if not self.fragment_opcode:
            self._fail(1002, "the server sent a continuation frame without a message")
            return

        self.fragments.append(payload)
        self.fragment_length += len(payload)

        if not first & 0x80:
            return

        opcode = self.fragment_opcode
        message = b"".join(self.fragments)
        self.fragment_opcode = 0
        self.fragments = []
        self.fragment_length = 0
        self._deliver(opcode, message)

    def _handle_close(self, payload: bytes, /) -> None:
        """
        Takes the peer's close frame apart the way RFC 6455 section 7.4
        demands. An empty payload means no code was given, ``1005``. A
        single byte, a code that must not appear on the wire or a reason
        that is not UTF-8 is a violation of its own and ends the
        connection with ``1002`` or ``1007`` instead of the peer's code.
        """
        if not payload:
            self._fail(1005, "")
            return

        if len(payload) == 1:
            self._fail(1002, "the server sent a close frame with half a close code")
            return

        code = int.from_bytes(payload[:2])
        if not self._is_close_code(code):
            self._fail(1002, f"the server sent the invalid close code {code}")
            return

        try:
            reason = payload[2:].decode()
        except UnicodeDecodeError:
            self._fail(1007, "the server sent a close reason that is not valid UTF-8")
            return

        self._fail(code, reason)

    def _deliver(self, opcode: int, payload: bytes, /) -> None:
        if opcode == 1:
            try:
                message: str | bytes = payload.decode()
            except UnicodeDecodeError:
                self._fail(1007, "the server sent text that is not valid UTF-8")
                return
        else:
            message = payload

        self.messages.append(message)
        self._wake_receiver()

    def _wake_receiver(self) -> None:
        waiter = self.waiter
        if waiter is not None:
            self.waiter = None

            if not waiter.done():
                waiter.set_result(None)

    def _fail(self, code: int, reason: str, /) -> None:
        """
        Ends the connection with a close code, whether the peer sent it
        or we found a violation. Our close frame goes out first unless
        one is on the wire already, then the transport closes and a
        waiting :meth:`receive` gets the close.
        """
        self.close_code = code
        self.close_reason = reason

        if not self.closing:
            self.closing = True
            self._send_frame(8, b"" if code == 1005 else code.to_bytes(2) + reason.encode())

        if self.transport is not None:
            self.transport.close()

        self._wake_closed()

    def _refuse(self, reason: str, /) -> None:
        if not self.handshake.done():
            self.handshake.set_exception(ConnectionError(reason))

        if self.transport is not None:
            self.transport.close()

    def _wake_closed(self) -> None:
        waiter = self.waiter
        if waiter is None:
            return

        self.waiter = None
        code = 1006 if self.close_code is None else self.close_code

        if not waiter.done():
            waiter.set_exception(WebSocketClosed(code, self.close_reason))

    def _send_frame(self, opcode: int, payload: bytes, /) -> None:
        """
        Writes one masked frame.

        RFC 6455 demands that a client masks every frame with a fresh
        key from a strong entropy source. Keys are taken from a pool of
        256 that one :func:`os.urandom` call refills, as integers, so
        neither the mask nor the header needs a conversion. With the C
        helper the whole frame is one call. Without it a payload up to
        400 bytes, which covers every frame a Discord client sends, is
        XORed as one big integer against the key repeated to its
        length; the repetition is a multiplication with a constant
        cached per payload size. Bigger payloads go through
        :meth:`_mask_large`. Header and key become bytes as one integer,
        cheaper than packing and joining them.
        """
        assert self.transport is not None

        keys = self.keys
        if not keys:
            keys.extend(_KEYS(urandom(1024)))

        key = keys.pop()

        if _frame is not None:
            self.transport.write(_frame(opcode, key, payload))
            return

        size = len(payload)

        if size <= 400:
            alignment = self._ALIGNMENTS.get(size)

            if alignment is None:
                words = (size + 3) // 4
                alignment = (((1 << (32 * words)) - 1) // 0xFFFFFFFF, 32 * words - 8 * size)
                self._ALIGNMENTS[size] = alignment

            repeat, shift = alignment
            masked = (int.from_bytes(payload) ^ (key * repeat >> shift)).to_bytes(size)
        else:
            masked = self._mask_large(payload, key.to_bytes(4))

        if size < 126:
            header = ((0x8080 | opcode << 8 | size) << 32 | key).to_bytes(6)
        elif size < 65536:
            header = ((0x80FE | opcode << 8) << 48 | size << 32 | key).to_bytes(8)
        else:
            header = _HEADER_64(0x80 | opcode, 255, size) + key.to_bytes(4)

        self.transport.write(header + masked)

    @staticmethod
    def _is_close_code(code: int, /) -> bool:
        """
        Whether RFC 6455 allows the code inside a close frame. ``1005``,
        ``1006`` and ``1015`` only ever describe a close locally, the rest
        below ``3000`` is either reserved or not assigned.
        """
        if 3000 <= code <= 4999:
            return True

        return 1000 <= code <= 1014 and code not in _RESERVED_CLOSE_CODES

    @staticmethod
    def _mask_large(payload: bytes, key: bytes, /) -> bytearray:
        """
        Masks a payload above 400 bytes with four strided translates,
        one per key byte, which beat the big-integer conversions from
        there on.
        """
        tables = _MASK_TABLES
        masked = bytearray(payload)
        masked[0::4] = masked[0::4].translate(tables[key[0]])
        masked[1::4] = masked[1::4].translate(tables[key[1]])
        masked[2::4] = masked[2::4].translate(tables[key[2]])
        masked[3::4] = masked[3::4].translate(tables[key[3]])

        return masked

    @classmethod
    async def _default_ssl(cls) -> ssl.SSLContext:
        """
        Builds the shared TLS context on first use. It reads the
        certificate store from disk, so that one blocking call goes to
        the executor instead of the loop.
        """
        context = WebSocket._ssl

        if context is None:
            context = await asyncio.get_running_loop().run_in_executor(None, ssl.create_default_context)
            WebSocket._ssl = context

        return context

    @staticmethod
    def _split(url: str, /) -> tuple[bool, str, int, str]:
        scheme, separator, rest = url.partition("://")
        default_port = WebSocket.DEFAULT_PORTS.get(scheme)

        if not separator or default_port is None:
            raise ValueError(f"{url!r} is not a ws or wss URL")

        end = len(rest)
        for stop in ("/", "?"):
            index = rest.find(stop)

            if 0 <= index < end:
                end = index

        authority = rest[:end]
        resource = rest[end:]
        host, colon, port = authority.partition(":")

        if not resource:
            resource = "/"
        elif resource[0] == "?":
            resource = "/" + resource

        return scheme == "wss", host, int(port) if colon else default_port, resource

    @staticmethod
    def _build(host: str, port: int, path: str, key: str, headers: dict[str, str] | None, /) -> bytes:
        lines = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}" if port in (80, 443) else f"Host: {host}:{port}",
            "Upgrade: websocket",
            "Connection: Upgrade",
            f"Sec-WebSocket-Key: {key}",
            "Sec-WebSocket-Version: 13"
        ]

        if headers:
            lines.extend(f"{name}: {value}" for name, value in headers.items())

        lines.append("\r\n")

        return "\r\n".join(lines).encode("latin-1")

__all__ = ["WebSocket", "WebSocketClosed"]