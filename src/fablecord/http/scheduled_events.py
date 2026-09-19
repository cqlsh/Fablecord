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

from typing import TYPE_CHECKING, Any, Final
from ..utils.missing import MISSING
from .route import Route

if TYPE_CHECKING:
    from .client import RESTClient, Response

class ScheduledEvents:
    """
    The scheduled event endpoints of a guild: the events, their
    lifecycle and who is interested in them.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered. Only the fields given end up in a payload.

    Parameters
    -----------
    rest: :class:`RESTClient`
        The client that sends the requests.

    Attributes
    -----------
    rest: :class:`RESTClient`
        The client that sends the requests.
    """

    __slots__ = ["rest"]

    OF_GUILD: Final = Route("GET", "/guilds/{guild_id}/scheduled-events")
    CREATE: Final = Route("POST", "/guilds/{guild_id}/scheduled-events")
    GET: Final = Route("GET", "/guilds/{guild_id}/scheduled-events/{event_id}")
    EDIT: Final = Route("PATCH", "/guilds/{guild_id}/scheduled-events/{event_id}")
    DELETE: Final = Route("DELETE", "/guilds/{guild_id}/scheduled-events/{event_id}")
    USERS: Final = Route("GET", "/guilds/{guild_id}/scheduled-events/{event_id}/users")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def of_guild(self, guild_id: int, /, *, with_user_count: bool = MISSING) -> Response[list[dict[str, Any]]]:
        """
        Fetches the scheduled events of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        with_user_count: :class:`bool`
            Whether the number of interested users comes along.
        """
        return self.rest.request(self.OF_GUILD.compile(guild_id), params={"with_user_count": with_user_count or None})

    def create(
            self,
            guild_id: int,
            /,
            *,
            name: str,
            privacy_level: int,
            scheduled_start_time: str,
            entity_type: int,
            channel_id: int = MISSING,
            entity_metadata: dict[str, Any] = MISSING,
            scheduled_end_time: str = MISSING,
            description: str = MISSING,
            image: str = MISSING,
            recurrence_rule: dict[str, Any] = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Creates a scheduled event. A stage or voice event needs its
        ``channel_id``, an external one its ``entity_metadata`` with the
        location and a ``scheduled_end_time``.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name, 1 to 100 characters.
        privacy_level: :class:`int`
            Who can see the event, ``2`` for the guild's members.
        scheduled_start_time: :class:`str`
            The ISO 8601 timestamp the event starts at.
        entity_type: :class:`int`
            Where the event happens: ``1`` a stage channel, ``2`` a voice
            channel, ``3`` elsewhere.
        channel_id: :class:`int`
            The stage or voice channel.
        entity_metadata: Dict[:class:`str`, Any]
            The ``location`` of an external event.
        scheduled_end_time: :class:`str`
            The ISO 8601 timestamp the event ends at.
        description: :class:`str`
            The description, up to 1000 characters.
        image: :class:`str`
            The cover image as a data URI.
        recurrence_rule: Dict[:class:`str`, Any]
            How the event repeats.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {"name": name, "privacy_level": privacy_level, "scheduled_start_time": scheduled_start_time, "entity_type": entity_type}

        if channel_id is not MISSING:
            payload["channel_id"] = channel_id

        if entity_metadata is not MISSING:
            payload["entity_metadata"] = entity_metadata

        if scheduled_end_time is not MISSING:
            payload["scheduled_end_time"] = scheduled_end_time

        if description is not MISSING:
            payload["description"] = description

        if image is not MISSING:
            payload["image"] = image

        if recurrence_rule is not MISSING:
            payload["recurrence_rule"] = recurrence_rule

        return self.rest.request(self.CREATE.compile(guild_id), json=payload, reason=reason)

    def get(self, guild_id: int, event_id: int, /, *, with_user_count: bool = MISSING) -> Response[dict[str, Any]]:
        """
        Fetches one scheduled event.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        event_id: :class:`int`
            The event.
        with_user_count: :class:`bool`
            Whether the number of interested users comes along.
        """
        return self.rest.request(self.GET.compile(guild_id, event_id), params={"with_user_count": with_user_count or None})

    def edit(
            self,
            guild_id: int,
            event_id: int,
            /,
            *,
            name: str = MISSING,
            privacy_level: int = MISSING,
            scheduled_start_time: str = MISSING,
            scheduled_end_time: str = MISSING,
            entity_type: int = MISSING,
            channel_id: int | None = MISSING,
            entity_metadata: dict[str, Any] | None = MISSING,
            description: str | None = MISSING,
            image: str = MISSING,
            status: int = MISSING,
            recurrence_rule: dict[str, Any] | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a scheduled event. The fields mean the same as in
        :meth:`create`, only what is given changes, and ``status`` is
        how an event is started, completed or cancelled.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        event_id: :class:`int`
            The event.
        status: :class:`int`
            ``2`` to start the event, ``3`` to complete it, ``4`` to
            cancel it.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if privacy_level is not MISSING:
            payload["privacy_level"] = privacy_level

        if scheduled_start_time is not MISSING:
            payload["scheduled_start_time"] = scheduled_start_time

        if scheduled_end_time is not MISSING:
            payload["scheduled_end_time"] = scheduled_end_time

        if entity_type is not MISSING:
            payload["entity_type"] = entity_type

        if channel_id is not MISSING:
            payload["channel_id"] = channel_id

        if entity_metadata is not MISSING:
            payload["entity_metadata"] = entity_metadata

        if description is not MISSING:
            payload["description"] = description

        if image is not MISSING:
            payload["image"] = image

        if status is not MISSING:
            payload["status"] = status

        if recurrence_rule is not MISSING:
            payload["recurrence_rule"] = recurrence_rule

        return self.rest.request(self.EDIT.compile(guild_id, event_id), json=payload, reason=reason)

    def delete(self, guild_id: int, event_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes a scheduled event.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        event_id: :class:`int`
            The event.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(guild_id, event_id), reason=reason)

    def users(
            self,
            guild_id: int,
            event_id: int,
            /,
            *,
            limit: int | None = None,
            with_member: bool = MISSING,
            before: int | None = None,
            after: int | None = None
    ) -> Response[list[dict[str, Any]]]:
        """
        Fetches the users interested in a scheduled event.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        event_id: :class:`int`
            The event.
        limit: Optional[:class:`int`]
            How many users at most, 1 to 100.
        with_member: :class:`bool`
            Whether each guild member comes along in ``member``.
        before: Optional[:class:`int`]
            Only users with an ID below this one.
        after: Optional[:class:`int`]
            Only users with an ID above this one.
        """
        return self.rest.request(self.USERS.compile(guild_id, event_id), params={"limit": limit, "with_member": with_member or None, "before": before, "after": after})

__all__ = ["ScheduledEvents"]