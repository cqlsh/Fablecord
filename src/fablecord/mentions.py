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

from collections.abc import Sequence
from typing import Any, Protocol, Self, cast

from .utils.missing import MISSING

class Mentionable(Protocol):
    """
    Anything with an ID that a message can be told to mention: a user,
    a member or a role.
    """

    id: int

class AllowedMentions:
    """
    Which mentions in a message actually ping.

    Discord pings whatever the content names unless a message says
    otherwise, so this is what keeps a bot from ringing a whole server
    because someone put ``@everyone`` in a quote. The client takes one
    for every message it sends and :meth:`Messageable.send` takes one
    for a single message, where what is given wins over what the
    client set.

    A field left out stays :data:`MISSING` and is sent as allowed,
    which is what Discord does without the field as well.

    Attributes
    -----------
    everyone: :class:`bool`
        Whether ``@everyone`` and ``@here`` ping.
    users: Union[:class:`bool`, Sequence[Union[:class:`int`, :class:`Mentionable`]]]
        ``True`` to ping every user the content names, ``False`` for
        none of them, or the users that may be pinged, given as IDs or
        as anything with one.
    roles: Union[:class:`bool`, Sequence[Union[:class:`int`, :class:`Mentionable`]]]
        The same for roles.
    replied_user: :class:`bool`
        Whether a reply pings the author of the message it answers.
    """

    __slots__ = ["everyone", "users", "roles", "replied_user"]

    def __init__(
        self,
        *,
        everyone: bool = MISSING,
        users: bool | Sequence[int | Mentionable] = MISSING,
        roles: bool | Sequence[int | Mentionable] = MISSING,
        replied_user: bool = MISSING
    ) -> None:
        self.everyone = everyone
        self.users = users
        self.roles = roles
        self.replied_user = replied_user

    @classmethod
    def all(cls) -> Self:
        """
        Lets every mention through, which is what Discord does on its
        own.
        """
        return cls(everyone=True, users=True, roles=True, replied_user=True)

    @classmethod
    def none(cls) -> Self:
        """
        Stops every mention, so the message shows the names without
        ringing anyone.
        """
        return cls(everyone=False, users=False, roles=False, replied_user=False)

    def to_dict(self) -> dict[str, Any]:
        """
        The payload for this, as ``allowed_mentions`` of a message.
        """
        parse: list[str] = []
        data: dict[str, Any] = {"parse": parse}

        if self.everyone is not False:
            parse.append("everyone")

        users = self.users
        if users is MISSING or users is True:
            parse.append("users")
        elif users is not False:
            if users and not isinstance(users[0], int):
                data["users"] = [user.id for user in cast(Sequence[Mentionable], users)]
            else:
                data["users"] = list(users)

        roles = self.roles
        if roles is MISSING or roles is True:
            parse.append("roles")
        elif roles is not False:
            if roles and not isinstance(roles[0], int):
                data["roles"] = [role.id for role in cast(Sequence[Mentionable], roles)]
            else:
                data["roles"] = list(roles)

        if self.replied_user is not False:
            data["replied_user"] = True

        return data

    def merge(self, other: AllowedMentions, /) -> AllowedMentions:
        """
        The two of them together, where every field ``other`` sets wins
        and the rest stays as it is here. This is how the mentions of
        one message override the ones the client was built with.
        """
        merged = AllowedMentions.__new__(AllowedMentions)

        everyone = other.everyone
        merged.everyone = self.everyone if everyone is MISSING else everyone

        users = other.users
        merged.users = self.users if users is MISSING else users

        roles = other.roles
        merged.roles = self.roles if roles is MISSING else roles

        replied_user = other.replied_user
        merged.replied_user = self.replied_user if replied_user is MISSING else replied_user

        return merged

    def __repr__(self) -> str:
        return f"<AllowedMentions everyone={self.everyone} users={self.users} roles={self.roles} replied_user={self.replied_user}>"

__all__ = ["AllowedMentions", "Mentionable"]