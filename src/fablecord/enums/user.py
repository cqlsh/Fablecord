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

from .base import Category, Enum
from typing import Self

class Status(Enum):
    """
    The presence status of a user.

    ``invisible`` only ever goes out, a bot can set it for itself but
    never sees it on anyone else, others simply appear offline.
    """

    online = "online"
    """
    Online, the green dot.
    """

    idle = "idle"
    """
    Away, the yellow moon.
    """

    dnd = "dnd"
    """
    Do not disturb, the red dot. Notifications are muted for the user.
    """

    offline = "offline"
    """
    Offline or invisible from the outside.
    """

    invisible = "invisible"
    """
    Online but shown as offline. Only valid when setting the own presence.
    """

    is_online = Category.excluding(offline, invisible)
    """
    :class:`bool`: Whether the user is connected in some way, meaning
    anything but ``offline`` and ``invisible``.
    """

class DefaultAvatar(Enum):
    """
    The colour of the default avatar a user without one gets.

    Discord picks it from the user ID, or from the discriminator for the
    few accounts that still have one. :meth:`for_user` does that math.
    """

    blurple = 0
    """
    Blurple.
    """

    grey = 1
    """
    Grey.
    """

    green = 2
    """
    Green.
    """

    orange = 3
    """
    Orange.
    """

    red = 4
    """
    Red.
    """

    pink = 5
    """
    Pink. Only users without a discriminator can get this one.
    """

    @classmethod
    def for_user(cls, user_id: int, discriminator: int = 0, /) -> Self:
        """
        The default avatar Discord shows for a user.

        Parameters
        -----------
        user_id: :class:`int`
            The ID of the user.
        discriminator: :class:`int`
            The legacy discriminator, ``0`` for accounts that moved to the
            new username system.

        Returns
        --------
        :class:`DefaultAvatar`
            The colour Discord assigns to that user.
        """
        if discriminator:
            return cls.try_value(discriminator % 5)

        return cls.try_value((user_id >> 22) % 6)

class ActivityType(Enum):
    """
    What kind of activity a presence shows.

    Bots can only set ``playing``, ``streaming``, ``listening``,
    ``watching``, ``competing`` and a ``custom`` status for themselves.
    """

    playing = 0
    """
    Playing something.
    """

    streaming = 1
    """
    Streaming on Twitch or YouTube. The only type with a clickable link.
    """

    listening = 2
    """
    Listening to something, Spotify uses this.
    """

    watching = 3
    """
    Watching something.
    """

    custom = 4
    """
    A custom status, free text with an optional emoji.
    """

    competing = 5
    """
    Competing in something.
    """

class StatusDisplayType(Enum):
    """
    Which line of an activity the member list shows next to the name.

    By default that is the activity's name. An activity can ask for its
    state or details line instead, so a music bot can show the song
    rather than the name of the player. The members carry a prefix
    because ``name`` is already what every enum member calls itself.
    """

    activity_name = 0
    """
    The activity's name, as in "Playing Chess".
    """

    activity_state = 1
    """
    The state line, usually what the user is doing right now.
    """

    activity_details = 2
    """
    The details line, usually where or in what they are doing it.
    """

__all__ = ["Status", "DefaultAvatar", "ActivityType", "StatusDisplayType"]