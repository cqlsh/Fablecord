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

from weakref import ref
from typing import Any

from .events.dispatcher import Dispatcher
from .http.client import RESTClient
from .user import ClientUser, User
from .guild import Guild

class UserRef(ref[User]):
    """
    A weak reference to a cached user that knows its key, so the
    cache entry can go when the user does.
    """

    __slots__ = ["key"]

    key: int

class State:
    """
    Everything the models share: the REST client, the dispatcher and
    the cache.

    Guilds are held for as long as the bot is in them, and everything
    inside one hangs off it, so a role, a channel or a member is found
    through its guild rather than through a cache of its own.

    Users are held weakly: one stays cached while a member, a message
    or a reaction refers to it and leaves on its own afterwards, so
    the cache never outgrows what the bot is looking at.

    Attributes
    -----------
    rest: :class:`RESTClient`
        The HTTP side, for every action a model takes.
    dispatcher: :class:`Dispatcher`
        Where the parsers send their events.
    user: Optional[:class:`ClientUser`]
        The bot's own user once ``READY`` arrived.
    """

    __slots__ = ["rest", "dispatcher", "user", "_guilds", "_users"]

    def __init__(self, *, rest: RESTClient, dispatcher: Dispatcher) -> None:
        self.rest = rest
        self.dispatcher = dispatcher
        self.user: ClientUser | None = None
        self._guilds: dict[int, Guild] = {}
        self._users: dict[int, UserRef] = {}

    @property
    def guilds(self) -> list[Guild]:
        """
        List[:class:`Guild`]: Every guild the bot is in.
        """
        return list(self._guilds.values())

    def get_guild(self, guild_id: int, /) -> Guild | None:
        """
        The cached guild with an ID, ``None`` when the bot is in none
        with that ID.
        """
        return self._guilds.get(guild_id)

    def store_guild(self, data: dict[str, Any], /) -> Guild:
        """
        The guild for a payload: the cached one brought up to date, or
        a new one that goes into the cache.

        ``GUILD_CREATE`` arrives again after every reconnect, and
        updating the object rather than replacing it means the guilds,
        roles and channels a bot is holding on to stay the ones the
        cache hands out.
        """
        guild_id = int(data["id"])
        guild = self._guilds.get(guild_id)

        if guild is None:
            guild = Guild(self, data)
            self._guilds[guild_id] = guild
        else:
            guild.update(data)

        return guild

    def remove_guild(self, guild_id: int, /) -> Guild | None:
        """
        Drops a guild from the cache and hands it back, ``None`` when
        none was cached.
        """
        return self._guilds.pop(guild_id, None)

    @property
    def users(self) -> list[User]:
        """
        List[:class:`User`]: Every user in the cache right now.
        """
        users: list[User] = []

        for reference in self._users.values():
            user = reference()

            if user is not None:
                users.append(user)

        return users

    def get_user(self, user_id: int, /) -> User | None:
        """
        The cached user with an ID, ``None`` when nothing holds one.
        """
        reference = self._users.get(user_id)
        if reference is None:
            return None

        return reference()

    def store_user(self, data: dict[str, Any], /) -> User:
        """
        The user for a payload: the cached one as it is, or a new one
        that goes into the cache. The parsers of the events that carry
        newer data, a user or member update and a presence, bring a
        cached user up to date themselves.
        """
        user_id = int(data["id"])
        reference = self._users.get(user_id)

        if reference is not None:
            user = reference()

            if user is not None:
                return user

        user = User(self, data)
        reference = UserRef(user, self._forget_user)
        reference.key = user_id
        self._users[user_id] = reference

        return user

    def _forget_user(self, reference: UserRef, /) -> None:
        """
        Drops the cache entry of a user that was collected, unless a
        newer object took its key in the meantime.
        """
        users = self._users
        key = reference.key

        if users.get(key) is reference:
            del users[key]

__all__ = ["State"]