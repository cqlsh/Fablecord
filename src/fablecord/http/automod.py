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
from collections.abc import Sequence
from ..utils.missing import MISSING
from .route import Route

if TYPE_CHECKING:
    from .client import RESTClient, Response

class AutoModeration:
    """
    The auto moderation endpoints: the rules of a guild that catch
    messages by keyword, spam, mention count or member profile and act
    on them.

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

    OF_GUILD: Final = Route("GET", "/guilds/{guild_id}/auto-moderation/rules")
    GET: Final = Route("GET", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}")
    CREATE: Final = Route("POST", "/guilds/{guild_id}/auto-moderation/rules")
    EDIT: Final = Route("PATCH", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}")
    DELETE: Final = Route("DELETE", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def of_guild(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the auto moderation rules of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.OF_GUILD.compile(guild_id))

    def get(self, guild_id: int, rule_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one auto moderation rule.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        rule_id: :class:`int`
            The rule.
        """
        return self.rest.request(self.GET.compile(guild_id, rule_id))

    def create(
            self,
            guild_id: int,
            /,
            *,
            name: str,
            event_type: int,
            trigger_type: int,
            actions: Sequence[dict[str, Any]],
            trigger_metadata: dict[str, Any] = MISSING,
            enabled: bool = MISSING,
            exempt_roles: Sequence[int] = MISSING,
            exempt_channels: Sequence[int] = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Creates an auto moderation rule. Discord keeps it disabled
        unless ``enabled`` says otherwise.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name.
        event_type: :class:`int`
            What the rule watches, ``1`` for messages being sent, ``2``
            for member profiles.
        trigger_type: :class:`int`
            What sets it off: keywords, spam, keyword presets, mention
            count or member profile.
        actions: Sequence[Dict[:class:`str`, Any]]
            What happens then, blocking the message, sending an alert or
            timing the member out.
        trigger_metadata: Dict[:class:`str`, Any]
            The keywords, presets, allow list or mention limit the
            trigger needs.
        enabled: :class:`bool`
            Whether the rule is active from the start.
        exempt_roles: Sequence[:class:`int`]
            Up to twenty roles the rule leaves alone.
        exempt_channels: Sequence[:class:`int`]
            Up to fifty channels the rule leaves alone.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {"name": name, "event_type": event_type, "trigger_type": trigger_type, "actions": actions}

        if trigger_metadata is not MISSING:
            payload["trigger_metadata"] = trigger_metadata

        if enabled is not MISSING:
            payload["enabled"] = enabled

        if exempt_roles is not MISSING:
            payload["exempt_roles"] = exempt_roles

        if exempt_channels is not MISSING:
            payload["exempt_channels"] = exempt_channels

        return self.rest.request(self.CREATE.compile(guild_id), json=payload, reason=reason)

    def edit(
            self,
            guild_id: int,
            rule_id: int,
            /,
            *,
            name: str = MISSING,
            event_type: int = MISSING,
            trigger_metadata: dict[str, Any] = MISSING,
            actions: Sequence[dict[str, Any]] = MISSING,
            enabled: bool = MISSING,
            exempt_roles: Sequence[int] = MISSING,
            exempt_channels: Sequence[int] = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits an auto moderation rule. The fields mean the same as in
        :meth:`create`, only what is given changes, and the trigger type
        cannot change.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        rule_id: :class:`int`
            The rule.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if event_type is not MISSING:
            payload["event_type"] = event_type

        if trigger_metadata is not MISSING:
            payload["trigger_metadata"] = trigger_metadata

        if actions is not MISSING:
            payload["actions"] = actions

        if enabled is not MISSING:
            payload["enabled"] = enabled

        if exempt_roles is not MISSING:
            payload["exempt_roles"] = exempt_roles

        if exempt_channels is not MISSING:
            payload["exempt_channels"] = exempt_channels

        return self.rest.request(self.EDIT.compile(guild_id, rule_id), json=payload, reason=reason)

    def delete(self, guild_id: int, rule_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes an auto moderation rule.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        rule_id: :class:`int`
            The rule.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(guild_id, rule_id), reason=reason)

__all__ = ["AutoModeration"]