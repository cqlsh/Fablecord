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

from .route import CompiledRoute, MajorParameter
from time import monotonic
from typing import Final
from math import inf

_FOREVER: Final = inf
_UNLIMITED: Final = 1 << 62
_IDLE: Final = 300.0

class Bucket:
    """
    A window of requests Discord allows, with the queue of requests
    waiting for the next one.

    :class:`RateLimiter` keeps one per bucket Discord reports and major
    parameter, and one more for the global limit. A bucket starts out
    unknown: it lets a single request through and queues the rest until
    the response to that request reveals the real limit.

    Attributes
    -----------
    hash: Optional[:class:`str`]
        The name Discord gave the bucket, ``None`` until the first
        response, an empty string for a route Discord does not limit.
    limit: :class:`int`
        The requests one window allows.
    remaining: :class:`int`
        The requests that may still start in the current window. Below
        zero while more requests are in flight than the window has left.
    reset_at: :class:`float`
        When the window ends, on the :func:`time.monotonic` clock.
    period: :class:`float`
        How long a window lasts, as far as the responses revealed it.
    pending: :class:`int`
        The requests sent whose response has not been counted yet.
    window: :class:`float`
        The reset time Discord reported for the current window, an epoch
        timestamp. It tells the responses of one window from those of
        the next, whatever order they arrive in.
    """

    __slots__ = ["hash", "limit", "remaining", "reset_at", "period", "pending", "window", "waiters", "timer"]

    def __init__(self, *, limit: int = 1, period: float = 0.0, reset_at: float = _FOREVER) -> None:
        self.hash: str | None = None
        self.limit = limit
        self.remaining = limit
        self.reset_at = reset_at
        self.period = period
        self.pending = 0
        self.window = 0.0
        self.waiters: list[asyncio.Future[bool]] = []
        self.timer: asyncio.TimerHandle | None = None

    def __repr__(self) -> str:
        return f"<Bucket hash={self.hash!r} limit={self.limit} remaining={self.remaining} pending={self.pending} waiting={len(self.waiters)}>"

    def reset(self) -> None:
        """
        Starts the next window, from the timer or from the request that
        finds the old one over. The requests still in flight belong to
        the new window as far as Discord is concerned, so they are taken
        off its allowance right away.
        """
        timer = self.timer
        if timer is not None:
            timer.cancel()
            self.timer = None

        now = monotonic()
        if now < self.reset_at:
            self.schedule(now)

            return

        self.remaining = self.limit - self.pending
        self.reset_at = now + self.period

        if self.waiters and self.remaining > 0:
            self.wake()

        if self.waiters:
            self.schedule(now)

    def schedule(self, now: float, /) -> None:
        """
        Sets the timer for the end of the window, unless it is set or
        the end is unknown.
        """
        if self.timer is None and now < self.reset_at < _FOREVER:
            self.timer = asyncio.get_running_loop().call_at(self.reset_at, self._tick)

    def _tick(self) -> None:
        """
        The timer firing: it has done its job, the window can start over.
        """
        self.timer = None
        self.reset()

    def wake(self) -> None:
        """
        Hands the free requests of the window to the waiters at the front
        of the queue. A waiter owns its request from here on, so nothing
        arriving later can slip past it.
        """
        woken = 0

        for future in self.waiters:
            if self.remaining <= 0:
                break

            woken += 1

            if not future.done():
                future.set_result(True)
                self.remaining -= 1

        del self.waiters[:woken]

    def disband(self) -> None:
        """
        Sends every waiter back to look its bucket up again, after the
        route moved to another one.
        """
        for future in self.waiters:
            if not future.done():
                future.set_result(False)

        self.waiters.clear()

        timer = self.timer
        if timer is not None:
            timer.cancel()
            self.timer = None

class RateLimiter:
    """
    Keeps requests within Discord's rate limits.

    Discord limits requests per bucket, a bucket being a group of routes
    it names in the ``X-RateLimit-Bucket`` header, counted separately for
    each channel, guild or webhook. On top there is a limit across all
    routes per second. The limiter waits before a request that would
    exceed either, learns the buckets from the responses and backs off as
    long as a 429 asks.

    The request path is :meth:`acquire`, the request, then :meth:`update`
    with the response, or :meth:`release` when none came.

    Parameters
    -----------
    global_limit: :class:`int`
        The requests Discord allows per second across all routes, 50
        unless it raised the limit for the bot.
    """

    __slots__ = ["_buckets", "_hashes", "_global", "_sweep_at"]

    def __init__(self, *, global_limit: int = 50) -> None:
        self._buckets: dict[tuple[str, MajorParameter], Bucket] = {}
        self._hashes: dict[str, str] = {}
        self._global = Bucket(limit=global_limit, period=1.0, reset_at=0.0)
        self._sweep_at = 256

    async def acquire(self, route: CompiledRoute, /) -> Bucket:
        """
        Waits until a request for the route may be sent.

        Parameters
        -----------
        route: :class:`CompiledRoute`
            The route about to be requested.

        Returns
        --------
        :class:`Bucket`
            The bucket the request counts against. Hand it to
            :meth:`update` with the response, or to :meth:`release` when
            the request never got one.
        """
        key = (route.route.key, route.major)
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = self._create(key, route)

        now = monotonic()
        if now >= bucket.reset_at:
            bucket.reset()

        if bucket.remaining > 0:
            bucket.remaining -= 1
        else:
            while not await self._turn(bucket):
                bucket = self._buckets.get(key)
                if bucket is None:
                    bucket = self._create(key, route)

                now = monotonic()
                if now >= bucket.reset_at:
                    bucket.reset()

                if bucket.remaining > 0:
                    bucket.remaining -= 1

                    break

            now = monotonic()

        bucket.pending += 1

        window = self._global
        if now >= window.reset_at:
            window.reset()

        if window.remaining > 0:
            window.remaining -= 1
        else:
            try:
                await self._turn(window)
            except asyncio.CancelledError:
                bucket.pending -= 1
                bucket.remaining += 1

                if bucket.waiters:
                    bucket.wake()

                raise

        return bucket

    def update(self, route: CompiledRoute, bucket: Bucket, status: int, headers: dict[str, str], /, *, retry_after: float | None = None) -> None:
        """
        Counts a response against its bucket and takes in what the
        headers say about the limit.

        A response with rate limit headers sets the bucket's size and
        window. One without them, from a proxy or a Cloudflare error page,
        gives the request back to the bucket. A 429 empties the bucket, or
        the global window, for as long as Discord asks.

        Parameters
        -----------
        route: :class:`CompiledRoute`
            The route that was requested.
        bucket: :class:`Bucket`
            What :meth:`acquire` returned for it.
        status: :class:`int`
            The status code of the response.
        headers: Dict[:class:`str`, :class:`str`]
            The response headers with lowercased names.
        retry_after: Optional[:class:`float`]
            The ``retry_after`` from the body of a 429. It has
            milliseconds where the ``Retry-After`` header is rounded up
            to whole seconds, which is used when this is not given.
        """
        bucket.pending -= 1
        now = monotonic()
        hash = headers.get("x-ratelimit-bucket") or None

        if hash is not None:
            pending = bucket.pending

            if hash != bucket.hash:
                bucket, pending = self._learn(route, bucket, hash)

            reset = float(headers.get("x-ratelimit-reset", "0"))
            if reset >= bucket.window:
                limit = int(headers.get("x-ratelimit-limit", "1"))
                reported = int(headers.get("x-ratelimit-remaining", "0"))
                reset_after = float(headers.get("x-ratelimit-reset-after", "0"))

                if reset > bucket.window:
                    bucket.window = reset
                    bucket.remaining = reported - pending

                    if reported == limit - 1 or reset_after > bucket.period:
                        bucket.period = reset_after
                else:
                    bucket.remaining = min(bucket.remaining, reported - pending)

                bucket.limit = limit
                bucket.reset_at = now + reset_after

        if status == 429:
            if retry_after is None:
                retry_after = float(headers.get("retry-after", "0"))

            if headers.get("x-ratelimit-scope") == "global" or "x-ratelimit-global" in headers:
                window = self._global
                window.remaining = 0
                window.reset_at = now + retry_after

                if hash is None:
                    bucket.remaining += 1
            else:
                bucket.remaining = 0
                bucket.reset_at = now + retry_after
        elif hash is None:
            if status >= 500 or bucket.hash is not None:
                bucket.remaining += 1
            else:
                bucket.hash = ""
                bucket.limit = bucket.remaining = _UNLIMITED
                bucket.reset_at = _FOREVER
                self._hashes[route.route.key] = ""

        if bucket.waiters:
            if bucket.remaining > 0:
                bucket.wake()

            if bucket.waiters:
                bucket.schedule(now)

    def release(self, bucket: Bucket, /) -> None:
        """
        Gives a request back to its bucket after the connection failed
        before a response came.

        Parameters
        -----------
        bucket: :class:`Bucket`
            What :meth:`acquire` returned for the request.
        """
        bucket.pending -= 1
        bucket.remaining += 1

        if bucket.waiters:
            bucket.wake()

    @staticmethod
    async def _turn(bucket: Bucket, /) -> bool:
        """
        Queues for the next free request of the bucket.

        Returns ``True`` once a request was handed over and ``False`` when
        the route moved to another bucket meanwhile, so the caller has to
        look it up again. A waiter cancelled after it was handed a request
        passes the request on.
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        bucket.waiters.append(future)
        bucket.schedule(monotonic())

        try:
            return await future
        except asyncio.CancelledError:
            if future.done() and not future.cancelled() and future.result():
                bucket.remaining += 1

                if bucket.waiters:
                    bucket.wake()

            raise

    def _create(self, key: tuple[str, MajorParameter], route: CompiledRoute, /) -> Bucket:
        """
        Sets up the bucket for a route and major parameter seen for the
        first time. Once Discord has named the bucket of the route, a new
        major parameter shares the bucket of that name if another route
        already has it, otherwise it gets a bucket under that name that
        still has to find out its size.
        """
        if len(self._buckets) >= self._sweep_at:
            self._sweep()

        hash = self._hashes.get(key[0])

        if hash is None:
            bucket = Bucket()
        elif not hash:
            bucket = Bucket(limit=_UNLIMITED)
            bucket.hash = hash
        else:
            bucket = self._buckets.get((hash, route.major))

            if bucket is None:
                bucket = Bucket()
                bucket.hash = hash
                self._buckets[(hash, route.major)] = bucket

        self._buckets[key] = bucket

        return bucket

    def _learn(self, route: CompiledRoute, bucket: Bucket, hash: str, /) -> tuple[Bucket, int]:
        """
        Files the route under the bucket a response named.

        The usual case is the first response of a route: the bucket keeps
        its state and gets its name. When a bucket of that name exists
        already, because another route turned out to share it or Discord
        moved the route, the route moves over and its waiters queue up
        there. The requests still in flight on the old bucket are counted
        against the shared one until each of them reports, which is why
        the number of requests to hold back is returned along with it.
        """
        key = route.route.key
        major = route.major
        self._hashes[key] = hash
        shared = self._buckets.get((hash, major))

        if shared is None:
            if bucket.hash is None:
                bucket.hash = hash
                self._buckets[(hash, major)] = bucket

                return bucket, bucket.pending

            shared = Bucket()
            shared.hash = hash
            self._buckets[(hash, major)] = shared

        self._buckets[(key, major)] = shared
        bucket.disband()

        return shared, shared.pending + bucket.pending

    def _sweep(self) -> None:
        """
        Drops the buckets nothing has used for five minutes, and the
        unknown ones nothing is waiting for. The next sweep comes once the
        buckets have doubled, so a bot with thousands of busy channels is
        not scanning them on every new one.
        """
        now = monotonic()
        buckets = self._buckets
        stale = [key for key, bucket in buckets.items() if bucket.pending == 0 and not bucket.waiters and (bucket.reset_at == _FOREVER or now > bucket.reset_at + _IDLE)]

        for key in stale:
            del buckets[key]

        self._sweep_at = max(256, 2 * len(buckets))

__all__ = ["RateLimiter", "Bucket"]