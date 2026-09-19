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

from inspect import iscoroutinefunction
from collections.abc import Callable
from typing import Any, Final

from ..gateway.decoder import Decoder
from ..gateway.shard import Shard

type Listener = Callable[..., Any]
type Check = Callable[..., bool]
type Parser = Callable[[Shard, dict[str, Any]], object]
type Raw = Callable[[Shard, str, bytes], object]

_log: Final = logging.getLogger(__name__)
_load: Final = Decoder.load

class Dispatcher:
    """
    Turns what the shards receive into the events a bot listens to.

    A parser is registered for every gateway event that matters, with
    the names of the events it can emit. :meth:`dispatch`, which the
    shards call with the raw payload, parses the JSON only when that
    parser is active: because a listener or a :meth:`wait_for` exists
    for one of its events, or because it was registered as always
    needed, which the cache uses for ``GUILD_CREATE`` and the like.
    Everything else is dropped after one dictionary lookup on the
    interned event name.

    Listeners take the emitted event's arguments. A coroutine function
    runs as its own task, a plain function runs right there in the
    dispatch. An exception in either goes to the ``error`` listeners
    with the event name and the exception, or into the log when there
    are none.

    Attributes
    -----------
    raw: Optional[Callable[[:class:`Shard`, :class:`str`, :class:`bytes`], Any]]
        Called with every dispatch before anything else, parsed or not.
        Handy for logging the traffic, ``None`` by default.
    """

    __slots__ = ["raw", "_parsers", "_active", "_listeners", "_waiters", "_loop"]

    def __init__(self) -> None:
        self.raw: Raw | None = None
        self._parsers: dict[str, tuple[list[str], bool, Parser]] = {}
        self._active: dict[str, Parser] = {}
        self._listeners: dict[str, list[tuple[Listener, bool]]] = {}
        self._waiters: dict[str, list[tuple[asyncio.Future[Any], Check | None]]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def register(self, *, name: str, events: list[str], parser: Parser, always: bool = False) -> None:
        """
        Sets the parser for one gateway event.

        Parameters
        -----------
        name: :class:`str`
            The gateway event, such as ``MESSAGE_CREATE``.
        events: List[:class:`str`]
            The events the parser can emit, such as ``message``. The
            parser runs while any of them has a listener or a waiter.
        parser: Callable[[:class:`Shard`, Dict[:class:`str`, Any]], Any]
            Takes the shard and the ``d`` of the payload.
        always: :class:`bool`
            Run the parser even when nobody listens, because the cache
            depends on it.
        """
        self._parsers[name] = (events, always, parser)
        self._refresh()

    def unregister(self, *, name: str) -> None:
        """
        Drops the parser of one gateway event, which is dropped from
        then on.
        """
        self._parsers.pop(name, None)
        self._refresh()

    def wants(self, name: str, /) -> bool:
        """
        Whether a gateway event is parsed right now.
        """
        return name in self._active

    def add_listener(self, event: str, callback: Listener, /) -> None:
        """
        Adds a listener for an event.

        Parameters
        -----------
        event: :class:`str`
            The event, such as ``message``.
        callback: Callable[..., Any]
            Takes the event's arguments. A coroutine function is
            scheduled as a task, a plain function is called directly.
        """
        entry = (callback, iscoroutinefunction(callback))
        listeners = self._listeners.get(event)

        if listeners is None:
            self._listeners[event] = [entry]
            self._refresh()
        else:
            listeners.append(entry)

    def remove_listener(self, event: str, callback: Listener, /) -> None:
        """
        Removes a listener again. Nothing happens when it was not added.
        """
        listeners = self._listeners.get(event)
        if listeners is None:
            return

        remaining = [entry for entry in listeners if entry[0] != callback]

        if remaining:
            listeners[:] = remaining
        else:
            del self._listeners[event]
            self._refresh()

    async def wait_for(self, event: str, *, check: Check | None = None, timeout: float | None = None) -> Any:
        """
        |coro|

        Waits for the next emit of an event that ``check`` accepts.

        Parameters
        -----------
        event: :class:`str`
            The event to wait for.
        check: Optional[Callable[..., :class:`bool`]]
            Takes the event's arguments and says whether this is the
            one. Without a check the next emit counts.
        timeout: Optional[:class:`float`]
            Seconds to wait before giving up.

        Raises
        -------
        TimeoutError
            The event did not come in time.

        Returns
        --------
        Any
            The event's argument, ``None`` when it has none and a tuple
            when it has several.
        """
        loop = self._loop
        if loop is None:
            loop = self._loop = asyncio.get_running_loop()

        future: asyncio.Future[Any] = loop.create_future()
        entry = (future, check)
        waiters = self._waiters.get(event)

        if waiters is None:
            self._waiters[event] = [entry]
            self._refresh()
        else:
            waiters.append(entry)

        try:
            async with asyncio.timeout(timeout):
                return await future
        finally:
            waiters = self._waiters.get(event)

            if waiters is not None and entry in waiters:
                waiters.remove(entry)

                if not waiters:
                    del self._waiters[event]
                    self._refresh()

    def emit(self, event: str, /, *args: Any) -> None:
        """
        Calls the listeners of an event and resolves its waiters.

        Parameters
        -----------
        event: :class:`str`
            The event.
        *args: Any
            What the listeners and checks receive.
        """
        listeners = self._listeners.get(event)

        if listeners is not None:
            for callback, is_coroutine in listeners:
                if is_coroutine:
                    self._schedule(callback=callback, event=event, args=args)

                    continue

                try:
                    callback(*args)
                except Exception as error:
                    self._failed(event=event, error=error)

        waiters = self._waiters.get(event)

        if waiters:
            self._resolve(event=event, waiters=waiters, args=args)

    def dispatch(self, shard: Shard, name: str, payload: bytes, /) -> None:
        """
        Takes one gateway dispatch from a shard, which is what the
        shards are given as their ``dispatch``.
        """
        raw = self.raw
        if raw is not None:
            raw(shard, name, payload)

        parser = self._active.get(name)
        if parser is None:
            return

        parser(shard, _load(payload)["d"])

    def _refresh(self) -> None:
        """
        Recomputes which parsers run, after listeners, waiters or
        parsers changed.
        """
        listeners = self._listeners
        waiters = self._waiters
        active: dict[str, Parser] = {}

        for name, (events, always, parser) in self._parsers.items():
            if always or any(event in listeners or event in waiters for event in events):
                active[name] = parser

        self._active = active

    def _schedule(self, *, callback: Listener, event: str, args: tuple[Any, ...]) -> None:
        loop = self._loop
        if loop is None:
            loop = self._loop = asyncio.get_running_loop()

        loop.create_task(self._run(callback, event, args), name=f"fablecord: {event}")

    async def _run(self, callback: Listener, event: str, args: tuple[Any, ...], /) -> None:
        try:
            await callback(*args)
        except asyncio.CancelledError:
            pass
        except Exception as error:
            self._failed(event=event, error=error)

    def _failed(self, *, event: str, error: Exception) -> None:
        """
        Hands a listener's exception to the ``error`` listeners, or logs
        it when there are none or the failing listener was one of them.
        """
        if event != "error" and "error" in self._listeners:
            self.emit("error", event, error)

            return

        _log.error("Ignoring the exception raised by a listener of %s", event, exc_info=error)

    def _resolve(self, *, event: str, waiters: list[tuple[asyncio.Future[Any], Check | None]], args: tuple[Any, ...]) -> None:
        """
        Gives the waiters whose check passes the event's arguments.
        """
        if not args:
            result = None
        elif len(args) == 1:
            result = args[0]
        else:
            result = args

        remaining: list[tuple[asyncio.Future[Any], Check | None]] = []

        for entry in waiters:
            future, check = entry

            if future.done():
                continue

            if check is not None:
                try:
                    passed = check(*args)
                except Exception as error:
                    future.set_exception(error)

                    continue

                if not passed:
                    remaining.append(entry)

                    continue

            future.set_result(result)

        if remaining:
            waiters[:] = remaining
        else:
            del self._waiters[event]
            self._refresh()

__all__ = ["Dispatcher"]