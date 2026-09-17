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

from datetime import UTC, datetime
from typing import Final, Literal
from functools import partial
from time import time

from .snowflake import Snowflake

type TimestampStyle = Literal["t", "T", "d", "D", "f", "F", "s", "S", "R"]

_UNIX_EPOCH: Final = datetime(1970, 1, 1, tzinfo=UTC)

class Time:
    """
    The time helpers the parsers and the HTTP layer share.

    Discord sends timestamps as ISO 8601 strings with an offset and takes
    them back the same way. Everything here works in UTC, and a naive
    datetime handed in is taken as UTC rather than as local time, which
    is the mistake that otherwise shifts every timeout by a timezone.

    :attr:`parse` and :attr:`now` are the C functions of :mod:`datetime`
    bound directly, so the most common call in the library pays no
    Python frame at all.

    Attributes
    -----------
    parse: Callable[[:class:`str`], :class:`datetime.datetime`]
        Turns an ISO 8601 string from a payload into an aware datetime.
    now: Callable[[], :class:`datetime.datetime`]
        The current time in UTC, timezone aware.
    """

    __slots__ = ()

    parse = staticmethod(datetime.fromisoformat)
    now = staticmethod(partial(datetime.now, UTC))

    @staticmethod
    def parse_optional(value: str | None, /) -> datetime | None:
        """
        Like :attr:`parse`, for fields Discord leaves at ``null``.

        Parameters
        -----------
        value: Optional[:class:`str`]
            The ISO 8601 string, or ``None``.

        Returns
        --------
        Optional[:class:`datetime.datetime`]
            The moment it names, or ``None`` when there was none.
        """
        if value is None:
            return None

        return datetime.fromisoformat(value)

    @staticmethod
    def serialize(when: datetime, /) -> str:
        """
        Turns a datetime into the string Discord accepts.

        The result is always in UTC. ``isoformat`` spends a third of its
        time asking the zone for its offset, so the zone is stripped
        first and the ``+00:00`` appended by hand, which gives the same
        string for less.

        Parameters
        -----------
        when: :class:`datetime.datetime`
            The moment to send. A naive one is taken as UTC, one in
            another zone is converted.

        Returns
        --------
        :class:`str`
            An ISO 8601 string with the UTC offset.
        """
        if when.tzinfo is None:
            return when.isoformat() + "+00:00"

        if when.tzinfo is not UTC:
            when = when.astimezone(UTC)

        return when.replace(tzinfo=None).isoformat() + "+00:00"

class Timestamp:
    """
    Discord's timestamp markup, ``<t:seconds:style>``.

    The client renders it in the reader's own timezone and language. The
    style picks the form, without one Discord shows the short date and
    time:

    ==========  ===============================  ========================
    Style       Example                          Meaning
    ==========  ===============================  ========================
    ``t``       22:57                            Short time
    ``T``       22:57:58                         Long time
    ``d``       17/05/2016                       Short date
    ``D``       17 May 2016                      Long date
    ``f``       17 May 2016 22:57                Short date and time
    ``F``       Tuesday, 17 May 2016 22:57       Long date and time
    ``s``       17/05/2016, 22:57                Compact date and time
    ``S``       17/05/2016, 22:57:58             Compact with seconds
    ``R``       5 years ago                      Relative
    ==========  ===============================  ========================

    The style is checked by the type checker, not at runtime. The
    snowflake form never touches :class:`datetime.datetime`, so the
    creation time of a message or member costs a few integer operations.
    """

    __slots__ = ()

    @staticmethod
    def for_datetime(when: datetime, style: TimestampStyle | None = None, /) -> str:
        """
        The markup for a moment given as a datetime.

        Parameters
        -----------
        when: :class:`datetime.datetime`
            The moment to show. A naive one is taken as UTC.
        style: Optional[:class:`str`]
            One of the style letters, or ``None`` for Discord's default.

        Returns
        --------
        :class:`str`
            The markup to put into a message.
        """
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)

        elapsed = when - _UNIX_EPOCH
        seconds = elapsed.days * 86400 + elapsed.seconds

        if style is None:
            return f"<t:{seconds}>"

        return f"<t:{seconds}:{style}>"

    @staticmethod
    def for_snowflake(id: int, style: TimestampStyle | None = None, /) -> str:
        """
        The markup for the moment an ID was generated.

        Parameters
        -----------
        id: :class:`int`
            Any Discord ID, a message, a member, a channel.
        style: Optional[:class:`str`]
            One of the style letters, or ``None`` for Discord's default.

        Returns
        --------
        :class:`str`
            The markup to put into a message.
        """
        seconds = ((id >> 22) + Snowflake.EPOCH) // 1000

        if style is None:
            return f"<t:{seconds}>"

        return f"<t:{seconds}:{style}>"

    @staticmethod
    def now(style: TimestampStyle | None = None, /) -> str:
        """
        The markup for the current moment.

        Parameters
        -----------
        style: Optional[:class:`str`]
            One of the style letters, or ``None`` for Discord's default.

        Returns
        --------
        :class:`str`
            The markup to put into a message.
        """
        seconds = int(time())

        if style is None:
            return f"<t:{seconds}>"

        return f"<t:{seconds}:{style}>"

__all__ = ["TimestampStyle", "Time", "Timestamp"]