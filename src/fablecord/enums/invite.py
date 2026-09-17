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

from .base import Enum

class InviteTarget(Enum):
    """
    What an invite into a voice channel opens on join.

    A plain invite has no target. Each target wants its matching field
    when the invite is created, the streaming user or the application,
    and Discord rejects an invite that names the wrong one.
    """

    stream = 1
    """
    A member's stream. The invite carries the streaming user.
    """

    embedded_application = 2
    """
    An activity in the channel. The invite carries the application.
    """

class InviteType(Enum):
    """
    What an invite leads into.

    Bots only ever create and resolve guild invites, the other two
    show up when a user's invite is looked up by code.
    """

    guild = 0
    """
    A guild channel, the usual invite.
    """

    group_dm = 1
    """
    A group direct message. Bots cannot join those.
    """

    friend = 2
    """
    A friend request link.
    """

__all__ = ["InviteTarget", "InviteType"]