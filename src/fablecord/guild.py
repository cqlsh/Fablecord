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
from operator import attrgetter
from datetime import datetime

from .channel import CategoryChannel, ForumChannel, GuildChannel, StageChannel, TextChannel, Thread, VoiceChannel
from .enums.guild import ContentFilter, MFALevel, NSFWLevel, NotificationLevel, VerificationLevel
from .flags.guild import SystemChannelFlags
from .utils.snowflake import Snowflake
from .enums.locale import Locale
from .utils.time import Time
from .member import Member
from .asset import Asset
from .role import Role

if TYPE_CHECKING:
    from .state import State

_POSITION: Final = attrgetter("position", "id")

_CHANNELS: Final[dict[int, type[GuildChannel]]] = {
    0: TextChannel,
    2: VoiceChannel,
    4: CategoryChannel,
    5: TextChannel,
    13: StageChannel,
    15: ForumChannel,
    16: ForumChannel
}

class Guild:
    """
    A guild, which is what Discord calls a server.

    A guild holds the roles, channels, threads and members the bot can
    see, and is what every one of them is looked up through. The
    payload of ``GUILD_CREATE`` brings all of that at once, while a
    later guild update carries nothing but the guild's own settings and
    leaves the caches alone.

    Attributes
    -----------
    id: :class:`int`
        The guild's ID.
    name: :class:`str`
        The guild's name.
    owner_id: Optional[:class:`int`]
        Who owns the guild, ``None`` while it is unavailable.
    afk_timeout: :class:`int`
        After how many seconds without speaking a member is moved to
        the AFK channel.
    widget_enabled: :class:`bool`
        Whether the guild hands its widget out to anyone.
    verification_level: :class:`VerificationLevel`
        What a member has to have done before they may write.
    default_notifications: :class:`NotificationLevel`
        What a member is notified about unless they say otherwise.
    explicit_content_filter: :class:`ContentFilter`
        Whose attachments Discord scans for explicit content.
    mfa_level: :class:`MFALevel`
        Whether moderators need two factor authentication to act.
    nsfw_level: :class:`NSFWLevel`
        What Discord's own review made of the guild.
    features: List[:class:`str`]
        What the guild is unlocked for, such as ``COMMUNITY`` or
        ``BANNER``.
    application_id: Optional[:class:`int`]
        The bot that made the guild, ``None`` for an ordinary one.
    description: Optional[:class:`str`]
        The line shown in discovery, ``None`` when it has none.
    vanity_url_code: Optional[:class:`str`]
        The short invite code, ``None`` when the guild has none.
    premium_tier: :class:`int`
        The boost level, from ``0`` to ``3``.
    premium_subscription_count: :class:`int`
        How many boosts the guild has.
    premium_progress_bar_enabled: :class:`bool`
        Whether the boost bar is shown to members.
    preferred_locale: :class:`Locale`
        The language discovery and Discord's own messages use.
    max_presences: Optional[:class:`int`]
        How many members may be online at once, ``None`` on all but the
        largest guilds.
    max_members: Optional[:class:`int`]
        How many members the guild may hold, ``None`` when Discord did
        not say.
    max_video_channel_users: Optional[:class:`int`]
        How many members may have their camera on in a voice channel.
    max_stage_video_channel_users: Optional[:class:`int`]
        How many may have it on in a stage channel.
    approximate_member_count: Optional[:class:`int`]
        Roughly how many members the guild has, only in a payload that
        was asked for counts.
    approximate_presence_count: Optional[:class:`int`]
        Roughly how many of them are online, under the same condition.
    member_count: Optional[:class:`int`]
        How many members the guild has, as ``GUILD_CREATE`` counted
        them, ``None`` when it never arrived.
    large: :class:`bool`
        Whether Discord held the member list back because the guild is
        over the threshold.
    unavailable: :class:`bool`
        Whether Discord is having trouble with the guild, which means
        nothing but the ID can be trusted.
    joined_at: Optional[:class:`datetime.datetime`]
        When the bot joined, ``None`` when Discord did not say.
    """

    __slots__ = [
        "id",
        "name",
        "owner_id",
        "afk_timeout",
        "widget_enabled",
        "verification_level",
        "default_notifications",
        "explicit_content_filter",
        "mfa_level",
        "nsfw_level",
        "features",
        "application_id",
        "description",
        "vanity_url_code",
        "premium_tier",
        "premium_subscription_count",
        "premium_progress_bar_enabled",
        "preferred_locale",
        "max_presences",
        "max_members",
        "max_video_channel_users",
        "max_stage_video_channel_users",
        "approximate_member_count",
        "approximate_presence_count",
        "member_count",
        "large",
        "unavailable",
        "joined_at",
        "_state",
        "_icon",
        "_splash",
        "_discovery_splash",
        "_banner",
        "_system_channel_flags",
        "_afk_channel_id",
        "_widget_channel_id",
        "_system_channel_id",
        "_rules_channel_id",
        "_public_updates_channel_id",
        "_safety_alerts_channel_id",
        "_roles",
        "_channels",
        "_threads",
        "_members"
    ]

    def __init__(self, state: State, data: dict[str, Any], /) -> None:
        self._state = state
        self.id = int(data["id"])
        self.member_count: int | None = None
        self.joined_at: datetime | None = None
        self.large = False
        self._roles: dict[int, Role] = {}
        self._channels: dict[int, Any] = {}
        self._threads: dict[int, Thread] = {}
        self._members: dict[int, Member] = {}

        self.update(data)

    def update(self, data: dict[str, Any], /) -> None:
        """
        Takes new data for the same guild, which the cache does on
        every guild update.

        The roles, channels, threads and members are only rebuilt when
        Discord sends them, so an update that carries nothing but the
        guild's own settings leaves the caches as they are.
        """
        get = data.get
        state = self._state
        guild_id = self.id

        owner_id = get("owner_id")
        application_id = get("application_id")
        afk_channel = get("afk_channel_id")
        widget_channel = get("widget_channel_id")
        system_channel = get("system_channel_id")
        rules_channel = get("rules_channel_id")
        updates_channel = get("public_updates_channel_id")
        alerts_channel = get("safety_alerts_channel_id")
        member_count = get("member_count")
        large = get("large")
        joined_at = get("joined_at")
        roles = get("roles")
        channels = get("channels")
        threads = get("threads")
        members = get("members")

        self.name = get("name", "")
        self.owner_id = None if owner_id is None else int(owner_id)
        self.afk_timeout = get("afk_timeout", 0)
        self.widget_enabled = get("widget_enabled", False)
        self.verification_level = VerificationLevel.try_value(get("verification_level", 0))
        self.default_notifications = NotificationLevel.try_value(get("default_message_notifications", 0))
        self.explicit_content_filter = ContentFilter.try_value(get("explicit_content_filter", 0))
        self.mfa_level = MFALevel.try_value(get("mfa_level", 0))
        self.nsfw_level = NSFWLevel.try_value(get("nsfw_level", 0))
        self.features: list[str] = get("features") or []
        self.application_id = None if application_id is None else int(application_id)
        self.description = get("description")
        self.vanity_url_code = get("vanity_url_code")
        self.premium_tier = get("premium_tier", 0)
        self.premium_subscription_count = get("premium_subscription_count", 0)
        self.premium_progress_bar_enabled = get("premium_progress_bar_enabled", False)
        self.preferred_locale = Locale.try_value(get("preferred_locale", "en-US"))
        self.max_presences: int | None = get("max_presences")
        self.max_members: int | None = get("max_members")
        self.max_video_channel_users: int | None = get("max_video_channel_users")
        self.max_stage_video_channel_users: int | None = get("max_stage_video_channel_users")
        self.approximate_member_count: int | None = get("approximate_member_count")
        self.approximate_presence_count: int | None = get("approximate_presence_count")
        self.unavailable = get("unavailable", False)
        self._icon = get("icon")
        self._splash = get("splash")
        self._discovery_splash = get("discovery_splash")
        self._banner = get("banner")
        self._system_channel_flags = get("system_channel_flags", 0)
        self._afk_channel_id = None if afk_channel is None else int(afk_channel)
        self._widget_channel_id = None if widget_channel is None else int(widget_channel)
        self._system_channel_id = None if system_channel is None else int(system_channel)
        self._rules_channel_id = None if rules_channel is None else int(rules_channel)
        self._public_updates_channel_id = None if updates_channel is None else int(updates_channel)
        self._safety_alerts_channel_id = None if alerts_channel is None else int(alerts_channel)

        if member_count is not None:
            self.member_count = member_count

        if large is not None:
            self.large = large

        if joined_at is not None:
            self.joined_at = Time.parse(joined_at)

        if roles is not None:
            built_roles: dict[int, Role] = {}

            for entry in roles:
                role = Role(state, guild_id, entry)
                built_roles[role.id] = role

            self._roles = built_roles

        if channels is not None:
            built_channels: dict[int, Any] = {}

            for entry in channels:
                channel = _CHANNELS.get(entry["type"], GuildChannel)(state, guild_id, entry)
                built_channels[channel.id] = channel

            self._channels = built_channels

        if threads is not None:
            built_threads: dict[int, Thread] = {}

            for entry in threads:
                thread = Thread(state, guild_id, entry)
                built_threads[thread.id] = thread

            self._threads = built_threads

        if members is not None:
            built_members: dict[int, Member] = {}

            for entry in members:
                member = Member(state, guild_id, entry)
                built_members[member.id] = member

            self._members = built_members

    def get_role(self, role_id: int, /) -> Role | None:
        """
        The role with an ID, ``None`` when the guild has none.
        """
        return self._roles.get(role_id)

    def get_channel(self, channel_id: int, /) -> GuildChannel | None:
        """
        The channel with an ID, ``None`` when the guild has none. A
        thread is not one of these, :meth:`get_thread` finds those.
        """
        return self._channels.get(channel_id)

    def get_thread(self, thread_id: int, /) -> Thread | None:
        """
        The thread with an ID, ``None`` when the guild has none.
        """
        return self._threads.get(thread_id)

    def get_channel_or_thread(self, channel_id: int, /) -> GuildChannel | Thread | None:
        """
        The channel or the thread with an ID, ``None`` when the guild
        has neither. This is what a message is looked up through, since
        the channel it names may be either one.
        """
        channel = self._channels.get(channel_id)
        if channel is not None:
            return channel

        return self._threads.get(channel_id)

    def get_member(self, member_id: int, /) -> Member | None:
        """
        The member with an ID, ``None`` when none is cached.
        """
        return self._members.get(member_id)

    def add_role(self, data: dict[str, Any], /) -> Role:
        """
        Builds a role from a payload and puts it into the cache.
        """
        role = Role(self._state, self.id, data)
        self._roles[role.id] = role

        return role

    def remove_role(self, role_id: int, /) -> Role | None:
        """
        Drops a role from the cache and hands it back, ``None`` when
        the guild had none with that ID.
        """
        return self._roles.pop(role_id, None)

    def add_channel(self, data: dict[str, Any], /) -> GuildChannel:
        """
        Builds a channel from a payload and puts it into the cache.
        """
        channel = _CHANNELS.get(data["type"], GuildChannel)(self._state, self.id, data)
        self._channels[channel.id] = channel

        return channel

    def remove_channel(self, channel_id: int, /) -> GuildChannel | None:
        """
        Drops a channel from the cache and hands it back, ``None`` when
        the guild had none with that ID.
        """
        return self._channels.pop(channel_id, None)

    def add_thread(self, data: dict[str, Any], /) -> Thread:
        """
        Builds a thread from a payload and puts it into the cache.
        """
        thread = Thread(self._state, self.id, data)
        self._threads[thread.id] = thread

        return thread

    def remove_thread(self, thread_id: int, /) -> Thread | None:
        """
        Drops a thread from the cache and hands it back, ``None`` when
        the guild had none with that ID.
        """
        return self._threads.pop(thread_id, None)

    def add_member(self, data: dict[str, Any], /) -> Member:
        """
        Builds a member from a payload and puts it into the cache.
        """
        member = Member(self._state, self.id, data)
        self._members[member.id] = member

        return member

    def remove_member(self, member_id: int, /) -> Member | None:
        """
        Drops a member from the cache and hands it back, ``None`` when
        the guild had none with that ID.
        """
        return self._members.pop(member_id, None)

    def is_chunked(self) -> bool:
        """
        Whether the member list is complete, which it is once the bot
        has asked for the members of a large guild.
        """
        count = self.member_count

        return count is not None and len(self._members) >= count

    @property
    def roles(self) -> list[Role]:
        """
        List[:class:`Role`]: The guild's roles from the lowest to the
        highest, which is the order Discord checks them in.
        """
        guild_id = self.id
        roles = list(self._roles.values())
        roles.sort(key=lambda role: (role.id != guild_id, role.position, -role.id))

        return roles

    @property
    def channels(self) -> list[GuildChannel]:
        """
        List[:class:`GuildChannel`]: Every channel of the guild, in the
        order the cache holds them.
        """
        return list(self._channels.values())

    @property
    def threads(self) -> list[Thread]:
        """
        List[:class:`Thread`]: Every thread the bot can see.
        """
        return list(self._threads.values())

    @property
    def members(self) -> list[Member]:
        """
        List[:class:`Member`]: Every member in the cache.
        """
        return list(self._members.values())

    @property
    def text_channels(self) -> list[TextChannel]:
        """
        List[:class:`TextChannel`]: The text and announcement channels,
        in the order clients show them.
        """
        channels = [channel for channel in self._channels.values() if isinstance(channel, TextChannel)]
        channels.sort(key=_POSITION)

        return channels

    @property
    def voice_channels(self) -> list[VoiceChannel]:
        """
        List[:class:`VoiceChannel`]: The voice channels, in the order
        clients show them.
        """
        channels = [channel for channel in self._channels.values() if isinstance(channel, VoiceChannel)]
        channels.sort(key=_POSITION)

        return channels

    @property
    def stage_channels(self) -> list[StageChannel]:
        """
        List[:class:`StageChannel`]: The stage channels, in the order
        clients show them.
        """
        channels = [channel for channel in self._channels.values() if isinstance(channel, StageChannel)]
        channels.sort(key=_POSITION)

        return channels

    @property
    def categories(self) -> list[CategoryChannel]:
        """
        List[:class:`CategoryChannel`]: The categories, in the order
        clients show them.
        """
        channels = [channel for channel in self._channels.values() if isinstance(channel, CategoryChannel)]
        channels.sort(key=_POSITION)

        return channels

    @property
    def forums(self) -> list[ForumChannel]:
        """
        List[:class:`ForumChannel`]: The forum and media channels, in
        the order clients show them.
        """
        channels = [channel for channel in self._channels.values() if isinstance(channel, ForumChannel)]
        channels.sort(key=_POSITION)

        return channels

    @property
    def default_role(self) -> Role | None:
        """
        Optional[:class:`Role`]: ``@everyone``, the role every member
        has, ``None`` while the guild is unavailable.
        """
        return self._roles.get(self.id)

    @property
    def owner(self) -> Member | None:
        """
        Optional[:class:`Member`]: Who owns the guild, ``None`` when
        they are not in the cache.
        """
        owner_id = self.owner_id
        if owner_id is None:
            return None

        return self._members.get(owner_id)

    @property
    def me(self) -> Member | None:
        """
        Optional[:class:`Member`]: The bot as a member of this guild,
        ``None`` before ``READY`` arrived.
        """
        user = self._state.user
        if user is None:
            return None

        return self._members.get(user.id)

    @property
    def afk_channel(self) -> VoiceChannel | None:
        """
        Optional[:class:`VoiceChannel`]: Where members are moved after
        being quiet, ``None`` when the guild has no AFK channel.
        """
        channel_id = self._afk_channel_id
        if channel_id is None:
            return None

        return self._channels.get(channel_id)

    @property
    def system_channel(self) -> TextChannel | None:
        """
        Optional[:class:`TextChannel`]: Where Discord posts its join
        and boost messages, ``None`` when the guild turned them off.
        """
        channel_id = self._system_channel_id
        if channel_id is None:
            return None

        return self._channels.get(channel_id)

    @property
    def rules_channel(self) -> TextChannel | None:
        """
        Optional[:class:`TextChannel`]: Where a community guild keeps
        its rules, ``None`` when it has none.
        """
        channel_id = self._rules_channel_id
        if channel_id is None:
            return None

        return self._channels.get(channel_id)

    @property
    def public_updates_channel(self) -> TextChannel | None:
        """
        Optional[:class:`TextChannel`]: Where Discord writes to the
        moderators of a community guild, ``None`` when it has none.
        """
        channel_id = self._public_updates_channel_id
        if channel_id is None:
            return None

        return self._channels.get(channel_id)

    @property
    def safety_alerts_channel(self) -> TextChannel | None:
        """
        Optional[:class:`TextChannel`]: Where Discord sends its safety
        alerts, ``None`` when the guild picked none.
        """
        channel_id = self._safety_alerts_channel_id
        if channel_id is None:
            return None

        return self._channels.get(channel_id)

    @property
    def widget_channel(self) -> GuildChannel | None:
        """
        Optional[:class:`GuildChannel`]: The channel the widget invites
        into, ``None`` when it invites into none.
        """
        channel_id = self._widget_channel_id
        if channel_id is None:
            return None

        return self._channels.get(channel_id)

    @property
    def system_channel_flags(self) -> SystemChannelFlags:
        """
        :class:`SystemChannelFlags`: What the system channel keeps
        quiet about.
        """
        flags = SystemChannelFlags.__new__(SystemChannelFlags)
        flags.value = self._system_channel_flags

        return flags

    @property
    def icon(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The guild's icon, ``None`` when it
        has none.
        """
        hash = self._icon
        if hash is None:
            return None

        return Asset.from_guild_image(self._state.rest, self.id, hash, "icons")

    @property
    def banner(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The image above the channel list,
        ``None`` when the guild has none.
        """
        hash = self._banner
        if hash is None:
            return None

        return Asset.from_guild_image(self._state.rest, self.id, hash, "banners")

    @property
    def splash(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The image behind an invite, ``None``
        when the guild has none.
        """
        hash = self._splash
        if hash is None:
            return None

        return Asset.from_guild_image(self._state.rest, self.id, hash, "splashes")

    @property
    def discovery_splash(self) -> Asset | None:
        """
        Optional[:class:`Asset`]: The image shown in discovery,
        ``None`` when the guild has none.
        """
        hash = self._discovery_splash
        if hash is None:
            return None

        return Asset.from_guild_image(self._state.rest, self.id, hash, "discovery-splashes")

    @property
    def vanity_url(self) -> str | None:
        """
        Optional[:class:`str`]: The guild's short invite, ``None`` when
        it has none.
        """
        code = self.vanity_url_code
        if code is None:
            return None

        return f"https://discord.gg/{code}"

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the guild was made, taken from
        the ID.
        """
        return Snowflake(self.id).created_at

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Guild id={self.id} name={self.name!r} member_count={self.member_count}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Guild) and other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

__all__ = ["Guild"]