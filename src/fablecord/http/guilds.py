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

class Guilds:
    """
    The guild endpoints: the guild itself, its members, bans, roles,
    voice states, prune, widget, welcome screen, onboarding, incident
    actions, the audit log and templates.

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

    GET: Final = Route("GET", "/guilds/{guild_id}")
    PREVIEW: Final = Route("GET", "/guilds/{guild_id}/preview")
    CREATE: Final = Route("POST", "/guilds")
    EDIT: Final = Route("PATCH", "/guilds/{guild_id}")
    DELETE: Final = Route("DELETE", "/guilds/{guild_id}")
    MFA: Final = Route("POST", "/guilds/{guild_id}/mfa")
    VANITY: Final = Route("GET", "/guilds/{guild_id}/vanity-url")
    WIDGET_SETTINGS: Final = Route("GET", "/guilds/{guild_id}/widget")
    EDIT_WIDGET: Final = Route("PATCH", "/guilds/{guild_id}/widget")
    WIDGET: Final = Route("GET", "/guilds/{guild_id}/widget.json")
    WELCOME_SCREEN: Final = Route("GET", "/guilds/{guild_id}/welcome-screen")
    EDIT_WELCOME_SCREEN: Final = Route("PATCH", "/guilds/{guild_id}/welcome-screen")
    ONBOARDING: Final = Route("GET", "/guilds/{guild_id}/onboarding")
    EDIT_ONBOARDING: Final = Route("PUT", "/guilds/{guild_id}/onboarding")
    INCIDENT_ACTIONS: Final = Route("PUT", "/guilds/{guild_id}/incident-actions")
    PRUNE_COUNT: Final = Route("GET", "/guilds/{guild_id}/prune")
    PRUNE: Final = Route("POST", "/guilds/{guild_id}/prune")
    VOICE_REGIONS: Final = Route("GET", "/guilds/{guild_id}/regions")
    INVITES: Final = Route("GET", "/guilds/{guild_id}/invites")
    INTEGRATIONS: Final = Route("GET", "/guilds/{guild_id}/integrations")
    DELETE_INTEGRATION: Final = Route("DELETE", "/guilds/{guild_id}/integrations/{integration_id}")
    AUDIT_LOGS: Final = Route("GET", "/guilds/{guild_id}/audit-logs")
    MEMBER: Final = Route("GET", "/guilds/{guild_id}/members/{user_id}")
    MEMBERS: Final = Route("GET", "/guilds/{guild_id}/members")
    SEARCH_MEMBERS: Final = Route("GET", "/guilds/{guild_id}/members/search")
    ADD_MEMBER: Final = Route("PUT", "/guilds/{guild_id}/members/{user_id}")
    EDIT_MEMBER: Final = Route("PATCH", "/guilds/{guild_id}/members/{user_id}")
    EDIT_ME: Final = Route("PATCH", "/guilds/{guild_id}/members/@me")
    KICK: Final = Route("DELETE", "/guilds/{guild_id}/members/{user_id}")
    ADD_ROLE: Final = Route("PUT", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}")
    REMOVE_ROLE: Final = Route("DELETE", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}")
    BANS: Final = Route("GET", "/guilds/{guild_id}/bans")
    BAN: Final = Route("GET", "/guilds/{guild_id}/bans/{user_id}")
    CREATE_BAN: Final = Route("PUT", "/guilds/{guild_id}/bans/{user_id}")
    UNBAN: Final = Route("DELETE", "/guilds/{guild_id}/bans/{user_id}")
    BULK_BAN: Final = Route("POST", "/guilds/{guild_id}/bulk-ban")
    ROLES: Final = Route("GET", "/guilds/{guild_id}/roles")
    ROLE: Final = Route("GET", "/guilds/{guild_id}/roles/{role_id}")
    CREATE_ROLE: Final = Route("POST", "/guilds/{guild_id}/roles")
    EDIT_ROLE: Final = Route("PATCH", "/guilds/{guild_id}/roles/{role_id}")
    REORDER_ROLES: Final = Route("PATCH", "/guilds/{guild_id}/roles")
    DELETE_ROLE: Final = Route("DELETE", "/guilds/{guild_id}/roles/{role_id}")
    VOICE_STATE: Final = Route("GET", "/guilds/{guild_id}/voice-states/{user_id}")
    MY_VOICE_STATE: Final = Route("GET", "/guilds/{guild_id}/voice-states/@me")
    EDIT_VOICE_STATE: Final = Route("PATCH", "/guilds/{guild_id}/voice-states/{user_id}")
    EDIT_MY_VOICE_STATE: Final = Route("PATCH", "/guilds/{guild_id}/voice-states/@me")
    TEMPLATE: Final = Route("GET", "/guilds/templates/{code}")
    CREATE_FROM_TEMPLATE: Final = Route("POST", "/guilds/templates/{code}")
    TEMPLATES: Final = Route("GET", "/guilds/{guild_id}/templates")
    CREATE_TEMPLATE: Final = Route("POST", "/guilds/{guild_id}/templates")
    SYNC_TEMPLATE: Final = Route("PUT", "/guilds/{guild_id}/templates/{code}")
    EDIT_TEMPLATE: Final = Route("PATCH", "/guilds/{guild_id}/templates/{code}")
    DELETE_TEMPLATE: Final = Route("DELETE", "/guilds/{guild_id}/templates/{code}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def get(self, guild_id: int, /, *, with_counts: bool = True) -> Response[dict[str, Any]]:
        """
        Fetches a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        with_counts: :class:`bool`
            Whether the member and presence counts come along.
        """
        return self.rest.request(self.GET.compile(guild_id), params={"with_counts": with_counts})

    def preview(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the preview of a discoverable guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.PREVIEW.compile(guild_id))

    def create(
            self,
            *,
            name: str,
            icon: str | None = MISSING,
            verification_level: int = MISSING,
            default_message_notifications: int = MISSING,
            explicit_content_filter: int = MISSING,
            roles: Sequence[dict[str, Any]] = MISSING,
            channels: Sequence[dict[str, Any]] = MISSING,
            afk_channel_id: int = MISSING,
            afk_timeout: int = MISSING,
            system_channel_id: int = MISSING,
            system_channel_flags: int = MISSING
    ) -> Response[dict[str, Any]]:
        """
        Creates a guild, which Discord allows a bot in fewer than ten
        guilds.

        Parameters
        -----------
        name: :class:`str`
            The name.
        icon: Optional[:class:`str`]
            The icon as a data URI.
        verification_level: :class:`int`
            The verification level.
        default_message_notifications: :class:`int`
            The default notification level.
        explicit_content_filter: :class:`int`
            The explicit content filter level.
        roles: Sequence[Dict[:class:`str`, Any]]
            The roles to create with the guild.
        channels: Sequence[Dict[:class:`str`, Any]]
            The channels to create with the guild.
        afk_channel_id: :class:`int`
            The AFK channel, by the ID given in ``channels``.
        afk_timeout: :class:`int`
            The AFK timeout in seconds.
        system_channel_id: :class:`int`
            The system channel, by the ID given in ``channels``.
        system_channel_flags: :class:`int`
            The system channel flags.
        """
        payload = self._present(
            name=name,
            icon=icon,
            verification_level=verification_level,
            default_message_notifications=default_message_notifications,
            explicit_content_filter=explicit_content_filter,
            roles=roles,
            channels=channels,
            afk_channel_id=afk_channel_id,
            afk_timeout=afk_timeout,
            system_channel_id=system_channel_id,
            system_channel_flags=system_channel_flags
        )

        return self.rest.request(self.CREATE.compile(), json=payload)

    def edit(
            self,
            guild_id: int,
            /,
            *,
            name: str = MISSING,
            verification_level: int | None = MISSING,
            default_message_notifications: int | None = MISSING,
            explicit_content_filter: int | None = MISSING,
            afk_channel_id: int | None = MISSING,
            afk_timeout: int = MISSING,
            icon: str | None = MISSING,
            owner_id: int = MISSING,
            splash: str | None = MISSING,
            discovery_splash: str | None = MISSING,
            banner: str | None = MISSING,
            system_channel_id: int | None = MISSING,
            system_channel_flags: int = MISSING,
            rules_channel_id: int | None = MISSING,
            public_updates_channel_id: int | None = MISSING,
            preferred_locale: str | None = MISSING,
            features: Sequence[str] = MISSING,
            description: str | None = MISSING,
            premium_progress_bar_enabled: bool = MISSING,
            safety_alerts_channel_id: int | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a guild. Only what is given changes, ``None`` clears a
        field where Discord allows it.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The new name.
        verification_level: Optional[:class:`int`]
            The verification level.
        default_message_notifications: Optional[:class:`int`]
            The default notification level.
        explicit_content_filter: Optional[:class:`int`]
            The explicit content filter level.
        afk_channel_id: Optional[:class:`int`]
            The AFK channel.
        afk_timeout: :class:`int`
            The AFK timeout in seconds.
        icon: Optional[:class:`str`]
            The icon as a data URI.
        owner_id: :class:`int`
            The member to hand the guild to, which only its owner can.
        splash: Optional[:class:`str`]
            The invite splash as a data URI.
        discovery_splash: Optional[:class:`str`]
            The discovery splash as a data URI.
        banner: Optional[:class:`str`]
            The banner as a data URI.
        system_channel_id: Optional[:class:`int`]
            The channel for system messages.
        system_channel_flags: :class:`int`
            Which system messages are suppressed.
        rules_channel_id: Optional[:class:`int`]
            The rules channel of a community guild.
        public_updates_channel_id: Optional[:class:`int`]
            The channel Discord posts community updates to.
        preferred_locale: Optional[:class:`str`]
            The locale of a community guild.
        features: Sequence[:class:`str`]
            The guild features that can be switched, ``COMMUNITY`` or
            ``DISCOVERABLE`` among them.
        description: Optional[:class:`str`]
            The description of a community guild.
        premium_progress_bar_enabled: :class:`bool`
            Whether the boost progress bar shows.
        safety_alerts_channel_id: Optional[:class:`int`]
            The channel Discord posts safety alerts to.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if verification_level is not MISSING:
            payload["verification_level"] = verification_level

        if default_message_notifications is not MISSING:
            payload["default_message_notifications"] = default_message_notifications

        if explicit_content_filter is not MISSING:
            payload["explicit_content_filter"] = explicit_content_filter

        if afk_channel_id is not MISSING:
            payload["afk_channel_id"] = afk_channel_id

        if afk_timeout is not MISSING:
            payload["afk_timeout"] = afk_timeout

        if icon is not MISSING:
            payload["icon"] = icon

        if owner_id is not MISSING:
            payload["owner_id"] = owner_id

        if splash is not MISSING:
            payload["splash"] = splash

        if discovery_splash is not MISSING:
            payload["discovery_splash"] = discovery_splash

        if banner is not MISSING:
            payload["banner"] = banner

        if system_channel_id is not MISSING:
            payload["system_channel_id"] = system_channel_id

        if system_channel_flags is not MISSING:
            payload["system_channel_flags"] = system_channel_flags

        if rules_channel_id is not MISSING:
            payload["rules_channel_id"] = rules_channel_id

        if public_updates_channel_id is not MISSING:
            payload["public_updates_channel_id"] = public_updates_channel_id

        if preferred_locale is not MISSING:
            payload["preferred_locale"] = preferred_locale

        if features is not MISSING:
            payload["features"] = features

        if description is not MISSING:
            payload["description"] = description

        if premium_progress_bar_enabled is not MISSING:
            payload["premium_progress_bar_enabled"] = premium_progress_bar_enabled

        if safety_alerts_channel_id is not MISSING:
            payload["safety_alerts_channel_id"] = safety_alerts_channel_id

        return self.rest.request(self.EDIT.compile(guild_id), json=payload, reason=reason)

    def delete(self, guild_id: int, /) -> Response[None]:
        """
        Deletes a guild the bot owns.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.DELETE.compile(guild_id))

    def set_mfa_level(self, guild_id: int, level: int, /, *, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Sets whether moderators need two-factor authentication, which
        only the owner of the guild can.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        level: :class:`int`
            ``0`` for none, ``1`` for required.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.MFA.compile(guild_id), json={"level": level}, reason=reason)

    def vanity_invite(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the vanity invite of a guild, its ``code`` and ``uses``.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.VANITY.compile(guild_id))

    def widget_settings(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches whether the widget is enabled and which channel it
        invites to.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.WIDGET_SETTINGS.compile(guild_id))

    def edit_widget(self, guild_id: int, /, *, enabled: bool = MISSING, channel_id: int | None = MISSING, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Edits the widget settings.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        enabled: :class:`bool`
            Whether the widget is enabled.
        channel_id: Optional[:class:`int`]
            The channel the widget invites to.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.EDIT_WIDGET.compile(guild_id), json=self._present(enabled=enabled, channel_id=channel_id), reason=reason)

    def widget(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the widget of a guild, the public view with its online
        members and channels.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.WIDGET.compile(guild_id))

    def welcome_screen(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the welcome screen of a community guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.WELCOME_SCREEN.compile(guild_id))

    def edit_welcome_screen(
            self,
            guild_id: int,
            /,
            *,
            enabled: bool | None = MISSING,
            welcome_channels: Sequence[dict[str, Any]] | None = MISSING,
            description: str | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits the welcome screen of a community guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        enabled: Optional[:class:`bool`]
            Whether the welcome screen shows.
        welcome_channels: Optional[Sequence[Dict[:class:`str`, Any]]]
            The channels it points to, with their descriptions and
            emoji.
        description: Optional[:class:`str`]
            The text of the welcome screen.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(enabled=enabled, welcome_channels=welcome_channels, description=description)

        return self.rest.request(self.EDIT_WELCOME_SCREEN.compile(guild_id), json=payload, reason=reason)

    def onboarding(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the onboarding of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.ONBOARDING.compile(guild_id))

    def edit_onboarding(
            self,
            guild_id: int,
            /,
            *,
            prompts: Sequence[dict[str, Any]] = MISSING,
            default_channel_ids: Sequence[int] = MISSING,
            enabled: bool = MISSING,
            mode: int = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits the onboarding of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        prompts: Sequence[Dict[:class:`str`, Any]]
            The prompts new members answer.
        default_channel_ids: Sequence[:class:`int`]
            The channels every new member gets.
        enabled: :class:`bool`
            Whether onboarding is enabled.
        mode: :class:`int`
            How the default channels and prompts must add up.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(prompts=prompts, default_channel_ids=default_channel_ids, enabled=enabled, mode=mode)

        return self.rest.request(self.EDIT_ONBOARDING.compile(guild_id), json=payload, reason=reason)

    def edit_incident_actions(
            self,
            guild_id: int,
            /,
            *,
            invites_disabled_until: str | None = MISSING,
            dms_disabled_until: str | None = MISSING
    ) -> Response[dict[str, Any]]:
        """
        Pauses invites or DMs for a guild, or lifts the pause.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        invites_disabled_until: Optional[:class:`str`]
            The ISO 8601 timestamp until which invites are paused, up to
            a day ahead, ``None`` to lift it.
        dms_disabled_until: Optional[:class:`str`]
            The ISO 8601 timestamp until which DMs between members are
            paused, up to a day ahead, ``None`` to lift it.
        """
        payload = self._present(invites_disabled_until=invites_disabled_until, dms_disabled_until=dms_disabled_until)

        return self.rest.request(self.INCIDENT_ACTIONS.compile(guild_id), json=payload)

    def prune_count(self, guild_id: int, /, *, days: int = MISSING, include_roles: Sequence[int] = MISSING) -> Response[dict[str, Any]]:
        """
        Counts the members a prune would remove, under ``pruned``.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        days: :class:`int`
            The days of inactivity that count, 1 to 30.
        include_roles: Sequence[:class:`int`]
            Roles whose members are counted although they have a role.
        """
        params = {"days": days or None, "include_roles": ",".join(map(str, include_roles)) if include_roles else None}

        return self.rest.request(self.PRUNE_COUNT.compile(guild_id), params=params)

    def prune(
            self,
            guild_id: int,
            /,
            *,
            days: int = MISSING,
            compute_prune_count: bool = MISSING,
            include_roles: Sequence[int] = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Kicks the members inactive for a number of days who have no
        role.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        days: :class:`int`
            The days of inactivity that count, 1 to 30.
        compute_prune_count: :class:`bool`
            Whether to report how many were removed, which takes long on
            a large guild.
        include_roles: Sequence[:class:`int`]
            Roles whose members are pruned although they have a role.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(days=days, compute_prune_count=compute_prune_count, include_roles=include_roles)

        return self.rest.request(self.PRUNE.compile(guild_id), json=payload, reason=reason)

    def voice_regions(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the voice regions a guild can use.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.VOICE_REGIONS.compile(guild_id))

    def invites(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the invites of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.INVITES.compile(guild_id))

    def integrations(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the integrations of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.INTEGRATIONS.compile(guild_id))

    def delete_integration(self, guild_id: int, integration_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Removes an integration from a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        integration_id: :class:`int`
            The integration.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE_INTEGRATION.compile(guild_id, integration_id), reason=reason)

    def audit_logs(
            self,
            guild_id: int,
            /,
            *,
            user_id: int | None = None,
            action_type: int | None = None,
            before: int | None = None,
            after: int | None = None,
            limit: int | None = None
    ) -> Response[dict[str, Any]]:
        """
        Fetches audit log entries, newest first unless ``after`` is
        given. The payload holds them under ``audit_log_entries`` with
        the users, webhooks and other objects they refer to.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: Optional[:class:`int`]
            Only entries of this user's actions.
        action_type: Optional[:class:`int`]
            Only entries of this action.
        before: Optional[:class:`int`]
            Only entries with an ID below this one.
        after: Optional[:class:`int`]
            Only entries with an ID above this one, oldest first.
        limit: Optional[:class:`int`]
            How many entries at most, 1 to 100.
        """
        return self.rest.request(self.AUDIT_LOGS.compile(guild_id), params={"user_id": user_id, "action_type": action_type, "before": before, "after": after, "limit": limit})

    def member(self, guild_id: int, user_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches a member.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The member.
        """
        return self.rest.request(self.MEMBER.compile(guild_id, user_id))

    def members(self, guild_id: int, /, *, limit: int | None = None, after: int | None = None) -> Response[list[dict[str, Any]]]:
        """
        Fetches members in order of their user ID, which takes the
        members intent.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        limit: Optional[:class:`int`]
            How many members at most, 1 to 1000.
        after: Optional[:class:`int`]
            Only members with a user ID above this one.
        """
        return self.rest.request(self.MEMBERS.compile(guild_id), params={"limit": limit, "after": after})

    def search_members(self, guild_id: int, /, *, query: str, limit: int | None = None) -> Response[list[dict[str, Any]]]:
        """
        Fetches the members whose username or nickname starts with a
        string.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        query: :class:`str`
            What the name starts with.
        limit: Optional[:class:`int`]
            How many members at most, 1 to 1000.
        """
        return self.rest.request(self.SEARCH_MEMBERS.compile(guild_id), params={"query": query, "limit": limit})

    def add_member(
            self,
            guild_id: int,
            user_id: int,
            /,
            *,
            access_token: str,
            nick: str = MISSING,
            roles: Sequence[int] = MISSING,
            mute: bool = MISSING,
            deaf: bool = MISSING
    ) -> Response[dict[str, Any] | None]:
        """
        Adds a user to a guild with an OAuth2 token that carries the
        ``guilds.join`` scope. ``None`` comes back when the user was a
        member already.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The user.
        access_token: :class:`str`
            The user's OAuth2 access token.
        nick: :class:`str`
            The nickname to start with.
        roles: Sequence[:class:`int`]
            The roles to start with.
        mute: :class:`bool`
            Whether the user starts muted in voice.
        deaf: :class:`bool`
            Whether the user starts deafened in voice.
        """
        payload = self._present(access_token=access_token, nick=nick, roles=roles, mute=mute, deaf=deaf)

        return self.rest.request(self.ADD_MEMBER.compile(guild_id, user_id), json=payload)

    def edit_member(
            self,
            guild_id: int,
            user_id: int,
            /,
            *,
            nick: str | None = MISSING,
            roles: Sequence[int] = MISSING,
            mute: bool = MISSING,
            deaf: bool = MISSING,
            channel_id: int | None = MISSING,
            communication_disabled_until: str | None = MISSING,
            flags: int = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a member. Only what is given changes.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The member.
        nick: Optional[:class:`str`]
            The nickname, ``None`` to remove it.
        roles: Sequence[:class:`int`]
            The whole set of roles.
        mute: :class:`bool`
            Whether the member is muted in voice.
        deaf: :class:`bool`
            Whether the member is deafened in voice.
        channel_id: Optional[:class:`int`]
            The voice channel to move the member to, ``None`` to
            disconnect them.
        communication_disabled_until: Optional[:class:`str`]
            The ISO 8601 timestamp until which the member is timed out,
            ``None`` to end the timeout.
        flags: :class:`int`
            The member flags.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if nick is not MISSING:
            payload["nick"] = nick

        if roles is not MISSING:
            payload["roles"] = roles

        if mute is not MISSING:
            payload["mute"] = mute

        if deaf is not MISSING:
            payload["deaf"] = deaf

        if channel_id is not MISSING:
            payload["channel_id"] = channel_id

        if communication_disabled_until is not MISSING:
            payload["communication_disabled_until"] = communication_disabled_until

        if flags is not MISSING:
            payload["flags"] = flags

        return self.rest.request(self.EDIT_MEMBER.compile(guild_id, user_id), json=payload, reason=reason)

    def edit_me(
            self,
            guild_id: int,
            /,
            *,
            nick: str | None = MISSING,
            avatar: str | None = MISSING,
            banner: str | None = MISSING,
            bio: str | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits the bot's own member in a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        nick: Optional[:class:`str`]
            The nickname, ``None`` to remove it.
        avatar: Optional[:class:`str`]
            The guild avatar as a data URI, ``None`` to remove it.
        banner: Optional[:class:`str`]
            The guild banner as a data URI, ``None`` to remove it.
        bio: Optional[:class:`str`]
            The guild bio, ``None`` to remove it.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(nick=nick, avatar=avatar, banner=banner, bio=bio)

        return self.rest.request(self.EDIT_ME.compile(guild_id), json=payload, reason=reason)

    def kick(self, guild_id: int, user_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Removes a member from a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The member.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.KICK.compile(guild_id, user_id), reason=reason)

    def add_role(self, guild_id: int, user_id: int, role_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Gives a member a role.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The member.
        role_id: :class:`int`
            The role.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.ADD_ROLE.compile(guild_id, user_id, role_id), reason=reason)

    def remove_role(self, guild_id: int, user_id: int, role_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Takes a role from a member.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The member.
        role_id: :class:`int`
            The role.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.REMOVE_ROLE.compile(guild_id, user_id, role_id), reason=reason)

    def bans(self, guild_id: int, /, *, limit: int | None = None, before: int | None = None, after: int | None = None) -> Response[list[dict[str, Any]]]:
        """
        Fetches bans in order of the banned user's ID.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        limit: Optional[:class:`int`]
            How many bans at most, 1 to 1000.
        before: Optional[:class:`int`]
            Only users with an ID below this one.
        after: Optional[:class:`int`]
            Only users with an ID above this one.
        """
        return self.rest.request(self.BANS.compile(guild_id), params={"limit": limit, "before": before, "after": after})

    def ban(self, guild_id: int, user_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the ban of a user, with its reason.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The banned user.
        """
        return self.rest.request(self.BAN.compile(guild_id, user_id))

    def create_ban(self, guild_id: int, user_id: int, /, *, delete_message_seconds: int = MISSING, reason: str | None = None) -> Response[None]:
        """
        Bans a user, who need not be a member.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The user.
        delete_message_seconds: :class:`int`
            How many seconds of the user's messages to delete, up to a
            week.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.CREATE_BAN.compile(guild_id, user_id), json=self._present(delete_message_seconds=delete_message_seconds), reason=reason)

    def unban(self, guild_id: int, user_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Lifts the ban of a user.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The user.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.UNBAN.compile(guild_id, user_id), reason=reason)

    def bulk_ban(self, guild_id: int, user_ids: Sequence[int], /, *, delete_message_seconds: int = MISSING, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Bans up to two hundred users at once. The payload tells which
        were ``banned_users`` and which ``failed_users``.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_ids: Sequence[:class:`int`]
            The users.
        delete_message_seconds: :class:`int`
            How many seconds of their messages to delete, up to a week.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(user_ids=user_ids, delete_message_seconds=delete_message_seconds)

        return self.rest.request(self.BULK_BAN.compile(guild_id), json=payload, reason=reason)

    def roles(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the roles of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.ROLES.compile(guild_id))

    def role(self, guild_id: int, role_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one role.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        role_id: :class:`int`
            The role.
        """
        return self.rest.request(self.ROLE.compile(guild_id, role_id))

    def create_role(
            self,
            guild_id: int,
            /,
            *,
            name: str = MISSING,
            permissions: str = MISSING,
            color: int = MISSING,
            colors: dict[str, Any] = MISSING,
            hoist: bool = MISSING,
            icon: str | None = MISSING,
            unicode_emoji: str | None = MISSING,
            mentionable: bool = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Creates a role. What is not given is up to Discord: a role named
        ``new role`` with the everyone permissions and no colour.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name.
        permissions: :class:`str`
            The permissions, as the bit set in a string.
        color: :class:`int`
            The colour as an RGB integer.
        colors: Dict[:class:`str`, Any]
            The colours of a gradient or holographic role.
        hoist: :class:`bool`
            Whether members with the role are listed separately.
        icon: Optional[:class:`str`]
            The icon as a data URI.
        unicode_emoji: Optional[:class:`str`]
            The emoji shown as the icon instead.
        mentionable: :class:`bool`
            Whether anyone can mention the role.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(name=name, permissions=permissions, color=color, colors=colors, hoist=hoist, icon=icon, unicode_emoji=unicode_emoji, mentionable=mentionable)

        return self.rest.request(self.CREATE_ROLE.compile(guild_id), json=payload, reason=reason)

    def edit_role(
            self,
            guild_id: int,
            role_id: int,
            /,
            *,
            name: str | None = MISSING,
            permissions: str | None = MISSING,
            color: int | None = MISSING,
            colors: dict[str, Any] | None = MISSING,
            hoist: bool | None = MISSING,
            icon: str | None = MISSING,
            unicode_emoji: str | None = MISSING,
            mentionable: bool | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a role. The fields mean the same as in
        :meth:`create_role`, only what is given changes.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        role_id: :class:`int`
            The role.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(name=name, permissions=permissions, color=color, colors=colors, hoist=hoist, icon=icon, unicode_emoji=unicode_emoji, mentionable=mentionable)

        return self.rest.request(self.EDIT_ROLE.compile(guild_id, role_id), json=payload, reason=reason)

    def reorder_roles(self, guild_id: int, positions: Sequence[dict[str, Any]], /, *, reason: str | None = None) -> Response[list[dict[str, Any]]]:
        """
        Moves roles in one go and returns all of them.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        positions: Sequence[Dict[:class:`str`, Any]]
            One entry per role with its ``id`` and the new ``position``.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.REORDER_ROLES.compile(guild_id), json=positions, reason=reason)

    def delete_role(self, guild_id: int, role_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes a role.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        role_id: :class:`int`
            The role.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE_ROLE.compile(guild_id, role_id), reason=reason)

    def voice_state(self, guild_id: int, user_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the voice state of a member.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The member.
        """
        return self.rest.request(self.VOICE_STATE.compile(guild_id, user_id))

    def my_voice_state(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the bot's own voice state in a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.MY_VOICE_STATE.compile(guild_id))

    def edit_voice_state(self, guild_id: int, user_id: int, /, *, channel_id: int = MISSING, suppress: bool = MISSING) -> Response[None]:
        """
        Edits the voice state of a member in a stage channel, which is
        how a speaker is invited or moved to the audience.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        user_id: :class:`int`
            The member.
        channel_id: :class:`int`
            The stage channel the member is in.
        suppress: :class:`bool`
            Whether the member is in the audience.
        """
        payload = self._present(channel_id=channel_id, suppress=suppress)

        return self.rest.request(self.EDIT_VOICE_STATE.compile(guild_id, user_id), json=payload)

    def edit_my_voice_state(
            self,
            guild_id: int,
            /,
            *,
            channel_id: int = MISSING,
            suppress: bool = MISSING,
            request_to_speak_timestamp: str | None = MISSING
    ) -> Response[None]:
        """
        Edits the bot's own voice state in a stage channel.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        channel_id: :class:`int`
            The stage channel the bot is in.
        suppress: :class:`bool`
            Whether the bot is in the audience.
        request_to_speak_timestamp: Optional[:class:`str`]
            The ISO 8601 timestamp of the request to speak, ``None`` to
            withdraw it.
        """
        payload = self._present(channel_id=channel_id, suppress=suppress, request_to_speak_timestamp=request_to_speak_timestamp)

        return self.rest.request(self.EDIT_MY_VOICE_STATE.compile(guild_id), json=payload)

    def template(self, code: str, /) -> Response[dict[str, Any]]:
        """
        Fetches a guild template.

        Parameters
        -----------
        code: :class:`str`
            The template code.
        """
        return self.rest.request(self.TEMPLATE.compile(code))

    def create_from_template(self, code: str, /, *, name: str, icon: str = MISSING) -> Response[dict[str, Any]]:
        """
        Creates a guild from a template, which Discord allows a bot in
        fewer than ten guilds.

        Parameters
        -----------
        code: :class:`str`
            The template code.
        name: :class:`str`
            The name of the new guild.
        icon: :class:`str`
            The icon as a data URI.
        """
        return self.rest.request(self.CREATE_FROM_TEMPLATE.compile(code), json=self._present(name=name, icon=icon))

    def templates(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the templates of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.TEMPLATES.compile(guild_id))

    def create_template(self, guild_id: int, /, *, name: str, description: str | None = MISSING) -> Response[dict[str, Any]]:
        """
        Creates a template from a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name of the template.
        description: Optional[:class:`str`]
            What the template is for.
        """
        return self.rest.request(self.CREATE_TEMPLATE.compile(guild_id), json=self._present(name=name, description=description))

    def sync_template(self, guild_id: int, code: str, /) -> Response[dict[str, Any]]:
        """
        Updates a template to the guild as it is now.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        code: :class:`str`
            The template code.
        """
        return self.rest.request(self.SYNC_TEMPLATE.compile(guild_id, code))

    def edit_template(self, guild_id: int, code: str, /, *, name: str = MISSING, description: str | None = MISSING) -> Response[dict[str, Any]]:
        """
        Renames or describes a template.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        code: :class:`str`
            The template code.
        name: :class:`str`
            The new name.
        description: Optional[:class:`str`]
            What the template is for, ``None`` to remove it.
        """
        return self.rest.request(self.EDIT_TEMPLATE.compile(guild_id, code), json=self._present(name=name, description=description))

    def delete_template(self, guild_id: int, code: str, /) -> Response[dict[str, Any]]:
        """
        Deletes a template.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        code: :class:`str`
            The template code.
        """
        return self.rest.request(self.DELETE_TEMPLATE.compile(guild_id, code))

    @staticmethod
    def _present(**fields: Any) -> dict[str, Any]:
        """
        The fields that were given, which keeps an edit from touching
        anything else.
        """
        return {name: value for name, value in fields.items() if value is not MISSING}

__all__ = ["Guilds"]