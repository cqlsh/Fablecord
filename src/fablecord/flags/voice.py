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

from .base import Flag, Flags

class SpeakingFlags(Flags):
    """
    What a voice connection is transmitting.

    Sent to the voice gateway before audio starts and received for
    every other member who speaks. It is a bit field, a member can have
    the microphone open and priority at the same time, which is why
    this is not an enum.
    """

    microphone = Flag(1 << 0)
    """
    :class:`bool`: Plain voice audio. The client draws the green ring
    around the avatar while it is set.
    """

    soundshare = Flag(1 << 1)
    """
    :class:`bool`: Audio from a screen share or another application.
    The client shows no speaking indicator for it.
    """

    priority = Flag(1 << 2)
    """
    :class:`bool`: Priority speaker. Everyone else is turned down while
    this member speaks. Needs the priority speaker permission in the
    channel.
    """

__all__ = ["SpeakingFlags"]