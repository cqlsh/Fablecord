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
from typing import Final, Self

_fromtimestamp: Final = datetime.fromtimestamp

class Snowflake(int):
    """
    A Discord snowflake ID.

    Behaves like a normal :class:`int` and can be used as one everywhere.
    The extra properties pull the creation time and the generator bits
    out of the ID.

    Attributes
    -----------
    EPOCH: :class:`int`
        Discord's epoch in milliseconds, the start of 2015.
    """

    __slots__ = ()

    EPOCH: Final = 1420070400000

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the ID was generated, in UTC.
        The zone goes in positionally, as a keyword it costs a quarter of
        the whole call.
        """
        return _fromtimestamp(((self >> 22) + self.EPOCH) / 1000, UTC)

    @property
    def timestamp(self) -> float:
        """
        :class:`float`: When the ID was generated, as a Unix timestamp.
        """
        return ((self >> 22) + self.EPOCH) / 1000

    @property
    def worker_id(self) -> int:
        """
        :class:`int`: The worker that generated the ID.
        """
        return (self >> 17) & 0x1F

    @property
    def process_id(self) -> int:
        """
        :class:`int`: The process that generated the ID.
        """
        return (self >> 12) & 0x1F

    @property
    def increment(self) -> int:
        """
        :class:`int`: The counter of the process that generated the ID.
        """
        return self & 0xFFF

    @classmethod
    def from_datetime(cls, when: datetime, *, high: bool = False) -> Self:
        """
        Builds a snowflake for a point in time.

        Handy for ``before`` and ``after`` style queries. Pass ``high=True``
        for an upper bound so the whole millisecond is covered. Naive
        datetimes count as local time, like :meth:`datetime.datetime.timestamp`.

        Parameters
        -----------
        when: :class:`datetime.datetime`
            The point in time.
        high: :class:`bool`
            Fill the lower 22 bits with ones instead of zeros.

        Returns
        --------
        :class:`Snowflake`
            The snowflake for that time.
        """
        millis = int(when.timestamp() * 1000) - cls.EPOCH
        if high:
            return cls((millis << 22) | 0x3FFFFF)
        return cls(millis << 22)

__all__ = ["Snowflake"]