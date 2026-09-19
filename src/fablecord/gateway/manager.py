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
import ssl

from typing import Any, Final
from time import monotonic

from ..errors.base import ClientException
from ..http.client import RESTClient
from ..flags.intents import Intents
from ..http.route import Route
from .shard import Dispatch, Shard

_log: Final = logging.getLogger(__name__)
_GATEWAY_BOT: Final = Route("GET", "/gateway/bot")
_SPACING: Final = 5.0
_DAY: Final = 86400.0

class ShardManager:
    """
    Runs every shard of the bot.

    :meth:`start` asks Discord how many shards the bot needs and how
    many may identify at once, brings the shards up in that order and
    returns once each of them is ready. Identifies are spaced five
    seconds apart per bucket, so a bot with a ``max_concurrency`` of
    16 brings 16 shards up together and the next 16 five seconds
    later. Reconnects go through the same gate, and the daily budget
    of session starts is watched so the shards wait for its reset
    instead of running into ``4004``.

    Attributes
    -----------
    shards: Dict[:class:`int`, :class:`Shard`]
        The shards this process runs, by shard ID.
    shard_count: :class:`int`
        How many shards the bot has in total, ``0`` before :meth:`start`.
    max_concurrency: :class:`int`
        How many shards may identify within the same five seconds.
    """

    __slots__ = [
        "token",
        "intents",
        "dispatch",
        "rest",
        "shard_ids",
        "shard_count",
        "large_threshold",
        "presence",
        "ssl_context",
        "timeout",
        "shards",
        "max_concurrency",
        "_tasks",
        "_buckets",
        "_total",
        "_remaining",
        "_reset_at"
    ]

    def __init__(
        self,
        token: str,
        *,
        intents: Intents,
        dispatch: Dispatch,
        rest: RESTClient,
        shard_ids: list[int] | None = None,
        shard_count: int | None = None,
        large_threshold: int = 250,
        presence: dict[str, Any] | None = None,
        ssl_context: ssl.SSLContext | None = None,
        timeout: float = 30.0
    ) -> None:
        if shard_ids is not None and shard_count is None:
            raise ValueError("shard_ids needs shard_count, the total the bot runs across every process")

        self.token = token
        self.intents = intents
        self.dispatch = dispatch
        self.rest = rest
        self.shard_ids = shard_ids
        self.shard_count = shard_count or 0
        self.large_threshold = large_threshold
        self.presence = presence
        self.ssl_context = ssl_context
        self.timeout = timeout
        self.shards: dict[int, Shard] = {}
        self.max_concurrency = 1
        self._tasks: dict[int, asyncio.Task[None]] = {}
        self._buckets: list[float] = []
        self._total = 0
        self._remaining = 0
        self._reset_at = 0.0

    @property
    def is_ready(self) -> bool:
        """
        :class:`bool`: Whether every shard has its session up.
        """
        shards = self.shards

        return bool(shards) and all(shard.is_ready for shard in shards.values())

    @property
    def latency(self) -> float:
        """
        :class:`float`: The heartbeat latency in seconds averaged over
        the shards, ``nan`` until every shard has one.
        """
        shards = self.shards
        if not shards:
            return float("nan")

        return sum(shard.latency for shard in shards.values()) / len(shards)

    async def start(self) -> None:
        """
        |coro|

        Fetches the gateway details, connects every shard and returns
        once all of them are ready.

        Raises
        -------
        HTTPException
            ``GET /gateway/bot`` failed, which with a ``401`` means the
            token is wrong.
        LoginFailure
            The gateway rejected the token.
        GatewayClosed
            A shard was closed for something a reconnect cannot fix.
        ValueError
            A shard ID in ``shard_ids`` is not below ``shard_count``.
        """
        info = await self.rest.request(_GATEWAY_BOT.compile())
        limit = info["session_start_limit"]

        self.max_concurrency = limit["max_concurrency"]
        self._buckets = [0.0] * self.max_concurrency
        self._total = limit["total"]
        self._remaining = limit["remaining"]
        self._reset_at = monotonic() + limit["reset_after"] / 1000

        count = self.shard_count or info["shards"]
        self.shard_count = count
        ids = self.shard_ids if self.shard_ids is not None else list(range(count))

        for shard_id in ids:
            if not 0 <= shard_id < count:
                raise ValueError(f"shard {shard_id} does not exist with a shard count of {count}")

        if self._remaining < len(ids):
            _log.warning("Only %d session starts are left today for %d shards, the rest wait for the reset", self._remaining, len(ids))

        _log.info("Starting %d of %d shards, %d at a time", len(ids), count, self.max_concurrency)

        for shard_id in ids:
            shard = Shard(
                self.token,
                intents=self.intents,
                dispatch=self.dispatch,
                url=info["url"],
                shard_id=shard_id,
                shard_count=count,
                large_threshold=self.large_threshold,
                presence=self.presence,
                identify_gate=self._gate,
                ssl_context=self.ssl_context,
                timeout=self.timeout
            )
            self.shards[shard_id] = shard
            self._tasks[shard_id] = asyncio.create_task(shard.run(), name=f"fablecord-shard-{shard_id}")

        for shard_id, shard in self.shards.items():
            await self._ready_or_failed(shard=shard, task=self._tasks[shard_id])

    async def join(self) -> None:
        """
        |coro|

        Waits until every shard has stopped, which happens through
        :meth:`close` or through an error no reconnect can fix. That
        error closes the other shards and is raised here.
        """
        tasks = list(self._tasks.values())
        if not tasks:
            return

        try:
            await asyncio.gather(*tasks)
        except BaseException:
            await self.close()

            raise

    async def close(self) -> None:
        """
        |coro|

        Ends every session and waits for the shards to stop. A shard
        that is between connections is cancelled once ``timeout``
        seconds have passed.
        """
        shards = list(self.shards.values())
        if shards:
            await asyncio.gather(*(shard.close() for shard in shards))

        tasks = list(self._tasks.values())
        if not tasks:
            return

        _, pending = await asyncio.wait(tasks, timeout=self.timeout)

        for task in pending:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def wait_until_ready(self) -> None:
        """
        |coro|

        Waits until every shard has its session up.
        """
        for shard in list(self.shards.values()):
            await shard.wait_until_ready()

    def shard_for(self, guild_id: int, /) -> Shard:
        """
        The shard a guild lives on, which Discord derives from the
        guild's ID and the shard count.

        Raises
        -------
        ClientException
            The shard runs in another process, or nothing was started.
        """
        count = self.shard_count
        if not count:
            raise ClientException("the shards are not started")

        shard_id = (guild_id >> 22) % count
        shard = self.shards.get(shard_id)

        if shard is None:
            raise ClientException(f"guild {guild_id} is on shard {shard_id}, which this process does not run")

        return shard

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

        Changes the bot's status and activities on every shard, and
        keeps them for the identifies to come.
        """
        presence = {"since": since, "activities": activities or [], "status": status, "afk": afk}
        self.presence = presence

        for shard in self.shards.values():
            shard.presence = presence

        await asyncio.gather(*(shard.send(op=3, data=presence) for shard in self.shards.values()))

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

        Asks the guild's shard for its members, see
        :meth:`Shard.request_members`.
        """
        shard = self.shard_for(guild_id)
        await shard.request_members(guild_id=guild_id, query=query, limit=limit, presences=presences, user_ids=user_ids, nonce=nonce)

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

        Joins, moves or leaves a voice channel through the guild's
        shard, see :meth:`Shard.update_voice_state`.
        """
        shard = self.shard_for(guild_id)
        await shard.update_voice_state(guild_id=guild_id, channel_id=channel_id, self_mute=self_mute, self_deaf=self_deaf)

    async def _gate(self, shard_id: int, /) -> None:
        """
        Holds a shard back until its bucket may identify and a session
        start is left for today.
        """
        if self._remaining <= 0:
            wait = self._reset_at - monotonic()

            if wait > 0:
                _log.warning("No session starts are left today, shard %d waits %.0f seconds for the reset", shard_id, wait)
                await asyncio.sleep(wait)

            self._remaining = self._total
            self._reset_at = monotonic() + _DAY

        buckets = self._buckets
        bucket = shard_id % self.max_concurrency

        while True:
            wait = buckets[bucket] - monotonic()

            if wait <= 0:
                break

            await asyncio.sleep(wait)

        buckets[bucket] = monotonic() + _SPACING
        self._remaining -= 1

    async def _ready_or_failed(self, *, shard: Shard, task: asyncio.Task[None]) -> None:
        """
        Waits for one shard to become ready, and if its run ends first,
        closes the others and raises what ended it.
        """
        waiter = asyncio.ensure_future(shard.wait_until_ready())
        done, _ = await asyncio.wait([waiter, task], return_when=asyncio.FIRST_COMPLETED)

        if waiter in done:
            return

        waiter.cancel()
        await self.close()
        task.result()

__all__ = ["ShardManager"]