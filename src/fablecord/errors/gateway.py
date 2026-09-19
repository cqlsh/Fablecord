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

from .base import ClientException

class GatewayClosed(ClientException):
    """
    Raised when the gateway closed a shard with a code it cannot come
    back from.

    A shard reconnects on its own after every close that allows a
    resume or a fresh identify, so this only surfaces for the codes
    that mean the bot itself is misconfigured: ``4010`` for a shard
    that does not exist, ``4012`` for an API version Discord no longer
    serves, ``4013`` for an intent value Discord does not know, and
    the two with their own subclasses below. A rejected token raises
    :exc:`LoginFailure` instead, like a rejected login over HTTP.

    Attributes
    -----------
    code: :class:`int`
        The close code Discord sent.
    reason: :class:`str`
        The reason that came with it, often empty.
    shard_id: :class:`int`
        The shard that was closed.
    """

    def __init__(self, code: int, reason: str, shard_id: int, /) -> None:
        self.code = code
        self.reason = reason
        self.shard_id = shard_id

    def __str__(self) -> str:
        if self.reason:
            return f"Shard {self.shard_id} was closed by the gateway with code {self.code}: {self.reason}"

        return f"Shard {self.shard_id} was closed by the gateway with code {self.code}"

class PrivilegedIntentsRequired(GatewayClosed):
    """
    Raised when the identify asked for a privileged intent the bot is
    not allowed to use, which the gateway answers with code ``4014``.

    Presences, server members and message content each have to be
    switched on for the bot in the developer portal, and a bot in more
    than 100 guilds has to be verified for them. Until then the intent
    has to be left out of :class:`Intents`, or the connection is closed
    again right after every identify.
    """

    def __init__(self, shard_id: int, /) -> None:
        self.code = 4014
        self.reason = "Disallowed intent(s)"
        self.shard_id = shard_id

class ShardingRequired(GatewayClosed):
    """
    Raised when the bot is in too many guilds for the shards it
    identified with, which the gateway answers with code ``4011``.

    Discord requires at least one shard per 2500 guilds. The count
    Discord recommends comes from ``GET /gateway/bot`` and is what the
    automatic sharding uses, so this appears when a fixed count was
    passed that is too small.
    """

    def __init__(self, shard_id: int, /) -> None:
        self.code = 4011
        self.reason = "Sharding required"
        self.shard_id = shard_id

__all__ = ["GatewayClosed", "PrivilegedIntentsRequired", "ShardingRequired"]