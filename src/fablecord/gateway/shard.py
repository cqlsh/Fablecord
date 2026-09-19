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
import logging
import random
import zlib
import ssl
import sys

from collections.abc import Awaitable, Callable
from time import perf_counter, monotonic
from typing import Any, Final, Literal
from json import dumps

from ..errors.gateway import GatewayClosed, PrivilegedIntentsRequired, ShardingRequired
from ..net.websocket import WebSocket, WebSocketClosed
from ..errors.base import ClientException
from ..errors.http import LoginFailure
from ..flags.intents import Intents
from .decoder import Decoder

type Dispatch = Callable[[Shard, str, bytes], object]
type IdentifyGate = Callable[[int], Awaitable[None]]

_log: Final = logging.getLogger(__name__)
_QUERY: Final = "?v=10&encoding=json&compress=zlib-stream"
_PROPERTIES: Final = {"os": sys.platform, "browser": "fablecord", "device": "fablecord"}
_IDENTIFY_AGAIN: Final = frozenset([4003, 4005, 4007, 4009])
_BROKEN: Final = frozenset([4010, 4012, 4013])
_WINDOW: Final = 60.0
_LIMIT: Final = 115
_IDENTIFY_DELAY: Final = 5.0
_BACKOFF_CAP: Final = 60.0
_SHORT_SESSION: Final = 5.0
_LATE_HEARTBEAT: Final = 10.0

class Shard:
    """
    One connection to the gateway.

    :meth:`run` keeps the shard connected: it identifies, answers the
    heartbeat, resumes after a drop and identifies again when Discord
    ends the session, with a growing pause between attempts that fail
    right away. Every dispatch reaches ``dispatch`` as the interned
    event name and the raw JSON, so whoever is on the other end decides
    whether the payload is worth parsing. Only the codes that mean the
    bot is misconfigured end the shard, they come out of :meth:`run` as
    :exc:`LoginFailure` or :exc:`GatewayClosed`.

    Attributes
    -----------
    shard_id: :class:`int`
        The shard's number, ``0`` for a bot that runs on one connection.
    shard_count: :class:`int`
        How many shards the bot runs.
    session_id: Optional[:class:`str`]
        The session Discord gave at ``READY``, ``None`` before the first
        one and after Discord invalidated it.
    sequence: Optional[:class:`int`]
        The last sequence number seen, which a resume and every
        heartbeat send back.
    latency: :class:`float`
        Seconds between the last heartbeat and its acknowledgement,
        ``nan`` until the first one was answered.
    heartbeat_interval: :class:`float`
        Seconds between heartbeats, as Discord asked for in ``HELLO``.
    websocket: Optional[:class:`WebSocket`]
        The open connection, ``None`` between two of them.
    """

    __slots__ = [
        "token",
        "intents",
        "dispatch",
        "url",
        "shard_id",
        "shard_count",
        "large_threshold",
        "presence",
        "identify_gate",
        "ssl_context",
        "timeout",
        "decoder",
        "websocket",
        "session_id",
        "sequence",
        "resume_url",
        "latency",
        "heartbeat_interval",
        "_heartbeat",
        "_beat_sent",
        "_acked",
        "_sent",
        "_window",
        "_ready",
        "_stopping",
        "_last_identify",
        "_failures"
    ]

    def __init__(
        self,
        token: str,
        *,
        intents: Intents,
        dispatch: Dispatch,
        url: str = "wss://gateway.discord.gg",
        shard_id: int = 0,
        shard_count: int = 1,
        large_threshold: int = 250,
        presence: dict[str, Any] | None = None,
        identify_gate: IdentifyGate | None = None,
        ssl_context: ssl.SSLContext | None = None,
        timeout: float = 30.0
    ) -> None:
        self.token = token
        self.intents = intents
        self.dispatch = dispatch
        self.url = url
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.large_threshold = large_threshold
        self.presence = presence
        self.identify_gate = identify_gate
        self.ssl_context = ssl_context
        self.timeout = timeout
        self.decoder = Decoder()
        self.websocket: WebSocket | None = None
        self.session_id: str | None = None
        self.sequence: int | None = None
        self.resume_url: str | None = None
        self.latency = float("nan")
        self.heartbeat_interval = 0.0
        self._heartbeat: asyncio.Task[None] | None = None
        self._beat_sent = 0.0
        self._acked = True
        self._sent = 0
        self._window = 0.0
        self._ready = asyncio.Event()
        self._stopping = False
        self._last_identify = 0.0
        self._failures = 0

    @property
    def is_ready(self) -> bool:
        """
        :class:`bool`: Whether the session is up, which it is from
        ``READY`` or ``RESUMED`` until the connection drops.
        """
        return self._ready.is_set()

    async def run(self) -> None:
        """
        |coro|

        Connects and stays connected until :meth:`close` is called.

        A connection that cannot be made is retried after a pause that
        doubles up to a minute, with some jitter so shards do not all
        return at once. A session that ends is resumed when Discord
        allows it and replaced by a fresh identify otherwise.

        Raises
        -------
        LoginFailure
            Discord rejected the token.
        GatewayClosed
            The shard, intents or API version are wrong, which no
            reconnect can fix. :exc:`PrivilegedIntentsRequired` and
            :exc:`ShardingRequired` say which.
        """
        resume = False

        while not self._stopping:
            started = monotonic()

            try:
                action = await self._session(resume=resume)
            except (OSError, TimeoutError) as error:
                delay = self._backoff()
                _log.warning("Shard %d could not connect (%s), trying again in %.1f seconds", self.shard_id, error, delay)
                await asyncio.sleep(delay)

                continue

            if action is None:
                return

            resume = action == "resume"

            if monotonic() - started < _SHORT_SESSION:
                delay = self._backoff()
                _log.warning("Shard %d lost its connection right away, trying again in %.1f seconds", self.shard_id, delay)
                await asyncio.sleep(delay)

    async def close(self) -> None:
        """
        |coro|

        Ends the session and lets :meth:`run` return.

        The connection is closed with code ``1000``, which tells Discord
        the session is over, so the bot goes offline at once instead of
        lingering until the session times out.
        """
        self._stopping = True
        websocket = self.websocket

        if websocket is not None and not websocket.closed:
            await websocket.close(1000)

    async def wait_until_ready(self) -> None:
        """
        |coro|

        Waits until the session is up. Returns at once while it is.
        """
        await self._ready.wait()

    async def send(self, op: int, data: Any) -> None:
        """
        |coro|

        Sends one payload, waiting when the connection's budget of 120
        sends per minute is spent. A few of those are kept back for
        heartbeats, which never wait.

        Parameters
        -----------
        op: :class:`int`
            The opcode.
        data: Any
            What goes under ``d``.

        Raises
        -------
        ClientException
            The shard is not connected right now.
        """
        websocket = self.websocket
        if websocket is None or websocket.closing:
            raise ClientException(f"shard {self.shard_id} is not connected")

        while True:
            now = monotonic()

            if now - self._window >= _WINDOW:
                self._window = now
                self._sent = 0

            if self._sent < _LIMIT:
                break

            delay = self._window + _WINDOW - now
            _log.warning("Shard %d is sending too fast, waiting %.1f seconds", self.shard_id, delay)
            await asyncio.sleep(delay)

        self._sent += 1
        websocket.send_text(dumps({"op": op, "d": data}, separators=(",", ":")))

    async def update_presence(
        self,
        *,
        status: str = "online",
        activities: list[dict[str, Any]] | None = None,
        afk: bool = False,
        since: int | None = None
    ) -> None:
        """
        |coro|

        Changes what the bot shows as its status and activities on this
        shard. ``since`` is the Unix time in milliseconds the bot went
        idle, which only matters together with ``afk``.
        """
        await self.send(op=3, data={"since": since, "activities": activities or [], "status": status, "afk": afk})

    async def request_members(
        self,
        *,
        guild_id: int,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: list[int] | None = None,
        nonce: str | None = None
    ) -> None:
        """
        |coro|

        Asks for the members of a guild, which arrive in one or more
        ``GUILD_MEMBERS_CHUNK`` dispatches. An empty ``query`` with
        ``limit`` ``0`` requests everyone, which needs the server
        members intent; ``user_ids`` picks members instead of a name
        prefix and ``nonce`` comes back in every chunk so the answer
        can be told apart from other requests.
        """
        data: dict[str, Any] = {"guild_id": guild_id, "limit": limit, "presences": presences}

        if user_ids is None:
            data["query"] = query
        else:
            data["user_ids"] = user_ids

        if nonce is not None:
            data["nonce"] = nonce

        await self.send(op=8, data=data)

    async def update_voice_state(
        self,
        *,
        guild_id: int,
        channel_id: int | None,
        self_mute: bool = False,
        self_deaf: bool = False
    ) -> None:
        """
        |coro|

        Joins, moves within or, with ``channel_id`` ``None``, leaves a
        voice channel. Discord answers with ``VOICE_STATE_UPDATE`` and,
        when joining, ``VOICE_SERVER_UPDATE`` with the voice endpoint.
        """
        await self.send(op=4, data={"guild_id": guild_id, "channel_id": channel_id, "self_mute": self_mute, "self_deaf": self_deaf})

    async def _session(self, *, resume: bool) -> Literal["resume", "identify"] | None:
        """
        Runs one connection from the handshake to its close and says
        what to do next, ``None`` when the shard is done.
        """
        url = self.resume_url if resume and self.resume_url else self.url
        websocket = await WebSocket.connect(url + _QUERY, ssl_context=self.ssl_context, timeout=self.timeout)
        self.websocket = websocket
        self.decoder.reset()
        self._acked = True

        try:
            interval = await self._hello(websocket=websocket)
            self.heartbeat_interval = interval
            self._heartbeat = asyncio.create_task(self._beat(websocket=websocket, interval=interval), name=f"fablecord-heartbeat-{self.shard_id}")

            if resume and self.session_id is not None:
                await self._resume()
            else:
                await self._identify()

            return await self._read(websocket=websocket)
        finally:
            heartbeat = self._heartbeat
            if heartbeat is not None:
                self._heartbeat = None
                heartbeat.cancel()

            self.websocket = None
            self._ready.clear()

            if not websocket.closed:
                await websocket.close(1000 if self._stopping else 4000)

    async def _hello(self, *, websocket: WebSocket) -> float:
        """
        Waits for ``HELLO`` and returns the heartbeat interval in
        seconds. Anything else first is a protocol error worth a fresh
        connection.
        """
        decoder = self.decoder

        try:
            async with asyncio.timeout(self.timeout):
                while True:
                    message = await websocket.receive()
                    payload = decoder.feed(message if isinstance(message, bytes) else message.encode())

                    if payload is not None:
                        break
        except WebSocketClosed as closed:
            raise ConnectionError(f"the gateway closed with code {closed.code} before HELLO") from None

        op, _, _ = decoder.peek(payload)
        if op != 10:
            await websocket.close(1002, "expected HELLO")
            raise ConnectionError(f"the gateway sent opcode {op} instead of HELLO")

        return decoder.load(payload)["d"]["heartbeat_interval"] / 1000

    async def _identify(self) -> None:
        """
        Sends ``IDENTIFY``, at most once every five seconds for this
        shard when no gate spaces the shards out.
        """
        gate = self.identify_gate

        if gate is not None:
            await gate(self.shard_id)
        else:
            wait = self._last_identify + _IDENTIFY_DELAY - monotonic()

            if wait > 0:
                await asyncio.sleep(wait)

        self._last_identify = monotonic()
        data: dict[str, Any] = {
            "token": self.token,
            "properties": _PROPERTIES,
            "large_threshold": self.large_threshold,
            "shard": [self.shard_id, self.shard_count],
            "intents": self.intents.value
        }

        if self.presence is not None:
            data["presence"] = self.presence

        await self.send(op=2, data=data)
        _log.info("Shard %d of %d sent IDENTIFY", self.shard_id, self.shard_count)

    async def _resume(self) -> None:
        """
        Sends ``RESUME`` for the session that was lost.
        """
        await self.send(op=6, data={"token": self.token, "session_id": self.session_id, "seq": self.sequence})
        _log.info("Shard %d sent RESUME for session %s", self.shard_id, self.session_id)

    async def _read(self, *, websocket: WebSocket) -> Literal["resume", "identify"] | None:
        """
        Handles everything after the identify until the connection
        closes.
        """
        decoder = self.decoder
        receive = websocket.receive
        feed = decoder.feed
        peek = decoder.peek
        dispatch = self.dispatch

        try:
            while True:
                message = await receive()
                payload = feed(message if isinstance(message, bytes) else message.encode())

                if payload is None:
                    continue

                op, sequence, name = peek(payload)

                if op == 0:
                    self.sequence = sequence

                    if name is None:
                        continue

                    if name == "READY":
                        self._on_ready(payload=payload)
                    elif name == "RESUMED":
                        self._on_resumed()

                    try:
                        dispatch(self, name, payload)
                    except Exception:
                        _log.exception("Ignoring the exception raised while dispatching %s on shard %d", name, self.shard_id)

                    continue

                if op == 11:
                    self._acked = True
                    self.latency = perf_counter() - self._beat_sent
                elif op == 1:
                    self._send_heartbeat(websocket=websocket)
                elif op == 7:
                    _log.info("Shard %d was asked to reconnect", self.shard_id)
                    await websocket.close(4000, "reconnecting")

                    return "resume"
                elif op == 9:
                    if decoder.load(payload)["d"]:
                        _log.info("Shard %d has an invalid session that can be resumed", self.shard_id)
                        await websocket.close(4000, "resuming")

                        return "resume"

                    _log.info("Shard %d has an invalid session, identifying again", self.shard_id)
                    self.session_id = None
                    self.sequence = None
                    await asyncio.sleep(random.uniform(1.0, 5.0))
                    await self._identify()
                elif op != 10:
                    _log.debug("Shard %d received the unknown opcode %d", self.shard_id, op)
        except WebSocketClosed as closed:
            return self._closed(code=closed.code, reason=closed.reason)
        except zlib.error as error:
            _log.warning("Shard %d received a corrupt stream (%s), reconnecting", self.shard_id, error)
            await websocket.close(4000, "corrupt stream")

            return "resume"

    def _on_ready(self, *, payload: bytes) -> None:
        data = self.decoder.load(payload)["d"]
        self.session_id = data["session_id"]
        self.resume_url = data["resume_gateway_url"]
        self._failures = 0
        self._ready.set()
        _log.info("Shard %d is connected with session %s", self.shard_id, self.session_id)

    def _on_resumed(self) -> None:
        self._failures = 0
        self._ready.set()
        _log.info("Shard %d resumed session %s", self.shard_id, self.session_id)

    def _closed(self, *, code: int, reason: str) -> Literal["resume", "identify"] | None:
        """
        Turns a close code into the next step, or into the error the
        code stands for.
        """
        if self._stopping:
            return None

        if code == 4004:
            raise LoginFailure("Discord rejected the token at IDENTIFY")

        if code == 4014:
            raise PrivilegedIntentsRequired(self.shard_id)

        if code == 4011:
            raise ShardingRequired(self.shard_id)

        if code in _BROKEN:
            raise GatewayClosed(code, reason, self.shard_id)

        if code in _IDENTIFY_AGAIN:
            _log.info("Shard %d was closed with code %d, identifying again", self.shard_id, code)
            self.session_id = None
            self.sequence = None

            return "identify"

        _log.info("Shard %d was closed with code %d, resuming", self.shard_id, code)

        return "resume"

    async def _beat(self, *, websocket: WebSocket, interval: float) -> None:
        """
        Heartbeats for the life of one connection, and ends it when an
        acknowledgement stays out, since a connection that does not
        answer has died on Discord's side.
        """
        await asyncio.sleep(interval * random.random())

        while True:
            if not self._acked:
                _log.warning("Shard %d got no heartbeat acknowledgement, reconnecting", self.shard_id)
                await websocket.close(4000, "no heartbeat acknowledgement")

                return

            self._acked = False
            self._beat_sent = perf_counter()
            self._send_heartbeat(websocket=websocket)
            due = monotonic() + interval
            await asyncio.sleep(interval)

            late = monotonic() - due
            if late > _LATE_HEARTBEAT:
                _log.warning("Shard %d sent its heartbeat %.1f seconds late, something is blocking the event loop", self.shard_id, late)

    def _send_heartbeat(self, *, websocket: WebSocket) -> None:
        sequence = self.sequence
        text = '{"op":1,"d":null}' if sequence is None else f'{{"op":1,"d":{sequence}}}'

        try:
            websocket.send_text(text)
        except ConnectionError:
            pass

    def _backoff(self) -> float:
        """
        The pause before the next attempt, doubling from a second up to
        a minute with jitter.
        """
        self._failures += 1

        return min(_BACKOFF_CAP, 2.0 ** self._failures) * random.uniform(0.5, 1.0)

__all__ = ["Shard"]