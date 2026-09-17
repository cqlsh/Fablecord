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

class ScheduledEventEntityType(Enum):
    """
    Where a scheduled event takes place.

    The type decides which fields Discord demands. Events in a channel
    need the channel, external events need a location and an end time
    instead.
    """

    stage_instance = 1
    """
    In a stage channel. Discord opens the stage when the event starts.
    """

    voice = 2
    """
    In a voice channel.
    """

    external = 3
    """
    Somewhere outside Discord, described by a location text.
    """

    needs_channel = Category(stage_instance, voice)
    """
    :class:`bool`: Whether the event takes a channel. The external kind
    rejects one and wants a location and an end time instead.
    """

class ScheduledEventStatus(Enum):
    """
    Where a scheduled event stands.

    Status only moves forward, from scheduled to active to completed,
    or from scheduled to canceled. Discord removes finished events
    shortly after.
    """

    scheduled = 1
    """
    Announced and waiting for its start time.
    """

    active = 2
    """
    Running right now.
    """

    completed = 3
    """
    Over. It cannot be started again.
    """

    canceled = 4
    """
    Called off before it started.
    """

    is_over = Category(completed, canceled)
    """
    :class:`bool`: Whether the event is finished for good. Discord
    rejects every status change on such an event.
    """

class ScheduledEventRecurrenceFrequency(Enum):
    """
    How often a recurring scheduled event repeats.

    Discord only allows a few combinations, a yearly or monthly rule
    needs the month and day, a weekly rule the weekday, and the
    interval may only be raised for weekly rules.
    """

    yearly = 0
    """
    Once a year on a given month and day.
    """

    monthly = 1
    """
    Once a month on a given weekday of a given week.
    """

    weekly = 2
    """
    Once a week on given weekdays, every week or every other week.
    """

    daily = 3
    """
    Every day, or on a run of consecutive weekdays.
    """

__all__ = ["ScheduledEventEntityType", "ScheduledEventStatus", "ScheduledEventRecurrenceFrequency"]