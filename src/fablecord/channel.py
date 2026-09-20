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
from datetime import datetime

from .enums.channel import ChannelType, ForumLayoutType, ForumOrderType, VideoQualityMode
from .overwrite import PermissionOverwrite
from .flags.permissions import Permissions
from .partial_emoji import PartialEmoji
from .utils.snowflake import Snowflake
from .flags.guild import ChannelFlags
from .utils.time import Time

if TYPE_CHECKING:
    from .member import Member
    from .guild import Guild
    from .state import State

_VOICE: Final = Permissions.voice().value

_TIMEOUT: Final = Permissions.view_channel.bit | Permissions.read_message_history.bit

_ROLE: Final = 0

class Channel:
    """
    What every channel carries, whether members write in it, talk in
    it or open threads in it.

    The kinds of channel differ in what they add on top, so this is
    never built on its own.

    Attributes
    -----------
    id: :class:`int`
        The channel's ID.
    guild_id: :class:`int`
        The guild the channel belongs to.
    name: :class:`str`
        The channel's name.
    type: :class:`ChannelType`
        What kind of channel it is.
    """

    __slots__ = ["id", "guild_id", "name", "type", "_state", "_flags"]

    def __init__(self, state: State, guild_id: int, data: dict[str, Any], /) -> None:
        self._state = state
        self.id = int(data["id"])
        self.guild_id = guild_id

        self.update(data)

    def update(self, data: dict[str, Any], /) -> None:
        """
        Takes new data for the same channel, which the cache does on
        every channel update.
        """
        self.name = data["name"]
        self.type = ChannelType.try_value(data["type"])
        self._flags = data.get("flags", 0)

    @property
    def flags(self) -> ChannelFlags:
        """
        :class:`ChannelFlags`: What Discord marked about the channel,
        such as a post being pinned in its forum.
        """
        flags = ChannelFlags.__new__(ChannelFlags)
        flags.value = self._flags

        return flags

    @property
    def mention(self) -> str:
        """
        :class:`str`: The text that links to the channel in a message.
        """
        return f"<#{self.id}>"

    @property
    def jump_url(self) -> str:
        """
        :class:`str`: The link that opens the channel in a client.
        """
        return f"https://discord.com/channels/{self.guild_id}/{self.id}"

    @property
    def guild(self) -> Guild | None:
        """
        Optional[:class:`Guild`]: The guild the channel belongs to,
        ``None`` when it is not cached.
        """
        return self._state.get_guild(self.guild_id)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id} name={self.name!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Channel) and other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

class GuildChannel(Channel):
    """
    A channel that sits in the channel list of a guild.

    On top of what every channel has, this knows where it sits, which
    category holds it and which roles and members it changes the
    permissions of. A thread has none of that, so it is not one of
    these.

    Attributes
    -----------
    position: :class:`int`
        Where the channel sits among its siblings, counting from ``0``.
    category_id: Optional[:class:`int`]
        The category holding the channel, ``None`` when it sits at the
        top level.
    nsfw: :class:`bool`
        Whether the channel is marked as age restricted.
    overwrites: Dict[:class:`int`, :class:`PermissionOverwrite`]
        What the channel changes for single roles and members, by their
        ID. The one under the guild's own ID belongs to ``@everyone``.
    """

    __slots__ = ["position", "category_id", "nsfw", "overwrites", "_members"]

    _denied = 0

    def update(self, data: dict[str, Any], /) -> None:
        get = data.get
        category = get("parent_id")

        self.name = data["name"]
        self.type = ChannelType.try_value(data["type"])
        self.position = get("position", 0)
        self.category_id = None if category is None else int(category)
        self.nsfw = get("nsfw", False)
        self._flags = get("flags", 0)

        overwrites: dict[int, PermissionOverwrite] = {}
        members: set[int] = set()

        for entry in get("permission_overwrites") or ():
            target = int(entry["id"])
            overwrite = PermissionOverwrite.__new__(PermissionOverwrite)
            overwrite.allow = int(entry["allow"])
            overwrite.deny = int(entry["deny"])
            overwrites[target] = overwrite

            if entry["type"] != _ROLE:
                members.add(target)

        self.overwrites = overwrites
        self._members = members

    def overwrite_for(self, target_id: int, /) -> PermissionOverwrite | None:
        """
        What the channel changes for one role or member, ``None`` when
        it changes nothing for them.

        Parameters
        -----------
        target_id: :class:`int`
            The ID of the role or the member.
        """
        return self.overwrites.get(target_id)

    def permissions_for(self, member: Member, /) -> Permissions:
        """
        What a member may do in this channel.

        What their roles allow across the guild is the starting point,
        the channel's own overwrites are applied on top, and the rules
        Discord applies without saying so finish it: a member who
        cannot see the channel can do nothing in it, one who cannot
        write cannot pin or attach either, and one who cannot join
        cannot speak. Whatever the kind of channel has no use for is
        dropped last, so a text channel never answers with a voice
        permission, not even for the owner.

        Parameters
        -----------
        member: :class:`Member`
            The member to answer for.
        """
        if self._state.get_guild(self.guild_id) is None:
            return Permissions.none()

        base = member.guild_permissions

        if not base.administrator:
            overwrites = self.overwrites
            everyone = overwrites.get(self.guild_id)

            if everyone is not None:
                base.handle_overwrite(everyone.allow, everyone.deny)

            allow = 0
            deny = 0

            for role_id in member.role_ids:
                overwrite = overwrites.get(role_id)

                if overwrite is not None:
                    allow |= overwrite.allow
                    deny |= overwrite.deny

            base.handle_overwrite(allow, deny)

            own = overwrites.get(member.id)
            if own is not None:
                base.handle_overwrite(own.allow, own.deny)

            if member.is_timed_out():
                base.value &= _TIMEOUT

            base.apply_implicit_rules()

        base.value &= ~self._denied

        return base

    def is_role_overwrite(self, target_id: int, /) -> bool:
        """
        Whether an overwrite belongs to a role rather than to a single
        member, which Discord sends alongside it and an edit has to
        send back.
        """
        return target_id not in self._members

    def is_nsfw(self) -> bool:
        """
        Whether the channel is marked as age restricted, which is what
        makes a client ask before it shows anything.
        """
        return self.nsfw

    @property
    def category(self) -> CategoryChannel | None:
        """
        Optional[:class:`CategoryChannel`]: The category holding the
        channel, ``None`` when it sits at the top level or the guild is
        not cached.
        """
        category_id = self.category_id
        if category_id is None:
            return None

        guild = self._state.get_guild(self.guild_id)
        if guild is None:
            return None

        channel = guild.get_channel(category_id)

        return channel if isinstance(channel, CategoryChannel) else None

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the channel was made, taken
        from the ID.
        """
        return Snowflake(self.id).created_at

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id} name={self.name!r} position={self.position}>"

class TextChannel(GuildChannel):
    """
    A channel of a guild that messages are written in.

    This covers both an ordinary text channel and an announcement
    channel, which differ only in that the second one can be followed
    from other guilds, and :meth:`is_news` tells them apart.

    Attributes
    -----------
    topic: Optional[:class:`str`]
        The line under the channel's name, ``None`` when it has none.
    slowmode_delay: :class:`int`
        How many seconds a member has to wait between two messages,
        ``0`` when they do not have to wait.
    last_message_id: Optional[:class:`int`]
        The last message Discord saw in the channel, which may already
        be deleted, ``None`` when there was none.
    default_auto_archive_duration: :class:`int`
        After how many minutes without a message a new thread here
        archives itself.
    default_thread_slowmode_delay: :class:`int`
        The slowmode a new thread here starts with, in seconds.
    """

    __slots__ = [
        "topic",
        "slowmode_delay",
        "last_message_id",
        "default_auto_archive_duration",
        "default_thread_slowmode_delay"
    ]

    _denied = _VOICE

    def update(self, data: dict[str, Any], /) -> None:
        super().update(data)

        get = data.get
        last_message = get("last_message_id")

        self.topic = get("topic")
        self.slowmode_delay = get("rate_limit_per_user", 0)
        self.last_message_id = None if last_message is None else int(last_message)
        self.default_auto_archive_duration = get("default_auto_archive_duration", 1440)
        self.default_thread_slowmode_delay = get("default_thread_rate_limit_per_user", 0)

    def is_news(self) -> bool:
        """
        Whether the channel is an announcement channel, which other
        guilds can follow to get its messages.
        """
        return self.type is ChannelType.news

    @property
    def last_message_jump_url(self) -> str | None:
        """
        Optional[:class:`str`]: The link to the last message Discord
        saw here, ``None`` when there was none. The message may be
        gone, since Discord does not take the ID back when one is
        deleted.
        """
        message_id = self.last_message_id
        if message_id is None:
            return None

        return f"https://discord.com/channels/{self.guild_id}/{self.id}/{message_id}"

class VocalChannel(GuildChannel):
    """
    What a voice and a stage channel share.

    Both carry a voice connection and a text chat next to it, so they
    have the fields of a text channel as well as the ones that decide
    how the audio sounds.

    Attributes
    -----------
    bitrate: :class:`int`
        How many bits per second the audio uses. What a guild may set
        depends on its boost level.
    user_limit: :class:`int`
        How many members may be in at once, ``0`` when there is no
        limit.
    rtc_region: Optional[:class:`str`]
        The voice region the channel is pinned to, ``None`` when
        Discord picks one itself.
    video_quality_mode: :class:`VideoQualityMode`
        Whether Discord scales camera and screen share by itself.
    slowmode_delay: :class:`int`
        How many seconds a member has to wait between two messages in
        the text chat, ``0`` when they do not have to wait.
    last_message_id: Optional[:class:`int`]
        The last message Discord saw in the text chat, ``None`` when
        there was none.
    """

    __slots__ = [
        "bitrate",
        "user_limit",
        "rtc_region",
        "video_quality_mode",
        "slowmode_delay",
        "last_message_id"
    ]

    def update(self, data: dict[str, Any], /) -> None:
        super().update(data)

        get = data.get
        last_message = get("last_message_id")

        self.bitrate = get("bitrate", 64000)
        self.user_limit = get("user_limit", 0)
        self.rtc_region = get("rtc_region")
        self.video_quality_mode = VideoQualityMode.try_value(get("video_quality_mode", 1))
        self.slowmode_delay = get("rate_limit_per_user", 0)
        self.last_message_id = None if last_message is None else int(last_message)

class VoiceChannel(VocalChannel):
    """
    A voice channel of a guild, which members talk in and write in.
    """

    __slots__ = []

class StageChannel(VocalChannel):
    """
    A stage channel of a guild, where a few speak and the rest listen.

    Attributes
    -----------
    topic: Optional[:class:`str`]
        The subject of the stage, which Discord shows while one is
        running, ``None`` when there is none.
    """

    __slots__ = ["topic"]

    def update(self, data: dict[str, Any], /) -> None:
        super().update(data)

        self.topic = data.get("topic")

class CategoryChannel(GuildChannel):
    """
    A category of a guild, which holds other channels.

    A category has no messages and no voice of its own. What it is for
    is order and permissions: a channel inside it starts from what the
    category allows unless it says otherwise, and a channel made in an
    age restricted category starts out age restricted as well.
    """

    __slots__ = []

class ForumTag:
    """
    One of the labels a forum hands out, which a post carries to say
    what it is about.

    Attributes
    -----------
    id: :class:`int`
        The tag's ID.
    name: :class:`str`
        The tag's name.
    moderated: :class:`bool`
        Whether only members who may manage threads can put this tag on
        a post or take it off.
    emoji: Optional[:class:`PartialEmoji`]
        The emoji shown in front of the name, ``None`` when it has
        none.
    """

    __slots__ = ["id", "name", "moderated", "emoji"]

    def __init__(self, state: State | None, data: dict[str, Any], /) -> None:
        get = data.get
        emoji_id = get("emoji_id")
        emoji_name = get("emoji_name")

        self.id = int(data["id"])
        self.name = data["name"]
        self.moderated = get("moderated", False)

        if emoji_id is None and emoji_name is None:
            self.emoji = None
        else:
            self.emoji = PartialEmoji.from_dict(state, {"id": emoji_id, "name": emoji_name})

    def to_dict(self) -> dict[str, Any]:
        """
        The payload for this tag, which an edit of the forum sends back
        to keep it.
        """
        emoji = self.emoji

        return {
            "id": self.id,
            "name": self.name,
            "moderated": self.moderated,
            "emoji_id": None if emoji is None else emoji.id,
            "emoji_name": None if emoji is None else emoji.name or None
        }

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<ForumTag id={self.id} name={self.name!r} moderated={self.moderated}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ForumTag) and other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

class ForumChannel(GuildChannel):
    """
    A forum or media channel of a guild, which holds posts instead of
    messages.

    Nobody writes in the channel itself. Every message lives in a post,
    which is a thread of its own, and the channel decides what a new
    post starts out with and which tags it may carry. A media channel
    is the same thing with a gallery in front, and :meth:`is_media`
    tells the two apart.

    Attributes
    -----------
    topic: Optional[:class:`str`]
        The guidelines shown above the posts, ``None`` when there are
        none.
    slowmode_delay: :class:`int`
        How many seconds a member has to wait between two posts.
    last_message_id: Optional[:class:`int`]
        The last post Discord saw here, ``None`` when there was none.
    default_auto_archive_duration: :class:`int`
        After how many minutes without a message a new post archives
        itself.
    default_thread_slowmode_delay: :class:`int`
        The slowmode a new post starts with, in seconds.
    default_layout: :class:`ForumLayoutType`
        How clients lay the posts out.
    default_sort_order: Optional[:class:`ForumOrderType`]
        How clients sort the posts, ``None`` when the forum leaves it
        to them.
    available_tags: Dict[:class:`int`, :class:`ForumTag`]
        The tags a post may carry, by their ID.
    default_reaction_emoji: Optional[:class:`PartialEmoji`]
        The emoji clients offer under a new post, ``None`` when there
        is none.
    """

    __slots__ = [
        "topic",
        "slowmode_delay",
        "last_message_id",
        "default_auto_archive_duration",
        "default_thread_slowmode_delay",
        "default_layout",
        "default_sort_order",
        "available_tags",
        "default_reaction_emoji"
    ]

    _denied = _VOICE

    def update(self, data: dict[str, Any], /) -> None:
        super().update(data)

        get = data.get
        state = self._state
        last_message = get("last_message_id")
        sort_order = get("default_sort_order")
        reaction = get("default_reaction_emoji")

        self.topic = get("topic")
        self.slowmode_delay = get("rate_limit_per_user", 0)
        self.last_message_id = None if last_message is None else int(last_message)
        self.default_auto_archive_duration = get("default_auto_archive_duration", 1440)
        self.default_thread_slowmode_delay = get("default_thread_rate_limit_per_user", 0)
        self.default_layout = ForumLayoutType.try_value(get("default_forum_layout", 0))
        self.default_sort_order = None if sort_order is None else ForumOrderType.try_value(sort_order)
        self.available_tags = {tag.id: tag for tag in (ForumTag(state, entry) for entry in get("available_tags") or ())}

        if reaction is None:
            self.default_reaction_emoji = None
        else:
            self.default_reaction_emoji = PartialEmoji.from_dict(state, {"id": reaction.get("emoji_id"), "name": reaction.get("emoji_name")})

    def tag_for(self, tag_id: int, /) -> ForumTag | None:
        """
        One of the tags the forum hands out, ``None`` when it has no
        tag with that ID.
        """
        return self.available_tags.get(tag_id)

    def is_media(self) -> bool:
        """
        Whether the channel is a media channel, which shows its posts
        as a gallery and hides their text.
        """
        return self.type is ChannelType.media

class Thread(Channel):
    """
    A thread, which hangs under a channel and holds its own messages.

    A thread has no permissions of its own: what a member may do in it
    comes from the channel it hangs under. A post in a forum is a
    thread as well, and carries the tags of that forum.

    Attributes
    -----------
    parent_id: :class:`int`
        The channel the thread hangs under, a forum for a post.
    owner_id: :class:`int`
        Who opened the thread.
    archived: :class:`bool`
        Whether the thread is closed, which hides it from the channel
        list until someone writes in it again.
    auto_archive_duration: :class:`int`
        After how many minutes without a message the thread archives
        itself.
    archive_timestamp: Optional[:class:`datetime.datetime`]
        When the thread was last opened or closed, which is what the
        archiving counts from.
    locked: :class:`bool`
        Whether only members who may manage threads can open it again.
    invitable: :class:`bool`
        Whether anyone in a private thread may add others to it.
    message_count: :class:`int`
        How many messages the thread holds, not counting the ones that
        were deleted. It stops counting at 50 on an old thread.
    member_count: :class:`int`
        How many members are in the thread, which Discord stops
        counting at 50.
    total_message_sent: :class:`int`
        How many messages were ever sent here, the deleted ones
        included.
    slowmode_delay: :class:`int`
        How many seconds a member has to wait between two messages.
    last_message_id: Optional[:class:`int`]
        The last message Discord saw here, ``None`` when there was
        none.
    applied_tag_ids: List[:class:`int`]
        The tags a post carries, by their ID, empty for a thread that
        is not a post.
    """

    __slots__ = [
        "parent_id",
        "owner_id",
        "archived",
        "auto_archive_duration",
        "archive_timestamp",
        "locked",
        "invitable",
        "message_count",
        "member_count",
        "total_message_sent",
        "slowmode_delay",
        "last_message_id",
        "applied_tag_ids",
        "_created_at"
    ]

    def update(self, data: dict[str, Any], /) -> None:
        get = data.get
        metadata: dict[str, Any] = get("thread_metadata") or {}
        last_message = get("last_message_id")

        self.name = data["name"]
        self.type = ChannelType.try_value(data["type"])
        self._flags = get("flags", 0)
        self.parent_id = int(data["parent_id"])
        self.owner_id = int(data["owner_id"])
        self.message_count = get("message_count", 0)
        self.member_count = get("member_count", 0)
        self.total_message_sent = get("total_message_sent", 0)
        self.slowmode_delay = get("rate_limit_per_user", 0)
        self.last_message_id = None if last_message is None else int(last_message)
        self.applied_tag_ids = [int(tag) for tag in get("applied_tags") or ()]
        self.archived = metadata.get("archived", False)
        self.auto_archive_duration = metadata.get("auto_archive_duration", 1440)
        self.archive_timestamp = Time.parse_optional(metadata.get("archive_timestamp"))
        self.locked = metadata.get("locked", False)
        self.invitable = metadata.get("invitable", True)
        self._created_at = Time.parse_optional(metadata.get("create_timestamp"))

    def is_private(self) -> bool:
        """
        Whether only members who were added can see the thread.
        """
        return self.type is ChannelType.private_thread

    def is_news(self) -> bool:
        """
        Whether the thread hangs under an announcement channel.
        """
        return self.type is ChannelType.news_thread

    def is_post(self) -> bool:
        """
        Whether the thread is a post in a forum, which is what carrying
        tags means.
        """
        return bool(self.applied_tag_ids)

    def permissions_for(self, member: Member, /) -> Permissions:
        """
        What a member may do in the thread, which is whatever they may
        do in the channel it hangs under.

        Parameters
        -----------
        member: :class:`Member`
            The member to answer for.
        """
        guild = self._state.get_guild(self.guild_id)
        if guild is None:
            return Permissions.none()

        parent = guild.get_channel(self.parent_id)
        if parent is None:
            return Permissions.none()

        return parent.permissions_for(member)

    @property
    def parent(self) -> GuildChannel | None:
        """
        Optional[:class:`GuildChannel`]: The channel the thread hangs
        under, ``None`` when it or the guild is not cached.
        """
        guild = self._state.get_guild(self.guild_id)
        if guild is None:
            return None

        return guild.get_channel(self.parent_id)

    @property
    def created_at(self) -> datetime | None:
        """
        Optional[:class:`datetime.datetime`]: When the thread was
        opened, ``None`` for one opened before 2022. The ID cannot
        answer instead, because a thread started on an old message
        carries that message's ID.
        """
        return self._created_at

    @property
    def parent_jump_url(self) -> str:
        """
        :class:`str`: The link that opens the channel the thread hangs
        under.
        """
        return f"https://discord.com/channels/{self.guild_id}/{self.parent_id}"

    def __repr__(self) -> str:
        return f"<Thread id={self.id} name={self.name!r} parent_id={self.parent_id} archived={self.archived}>"

__all__ = ["Channel", "GuildChannel", "TextChannel", "VocalChannel", "VoiceChannel", "StageChannel", "CategoryChannel", "ForumChannel", "ForumTag", "Thread"]