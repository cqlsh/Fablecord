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
    from ..file import File

class Channels:
    """
    The channel endpoints: channels themselves and the channels of a
    guild, permission overwrites, invites, following announcement
    channels, threads with their members, and stage instances.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered. Only the fields given end up in a payload, which
    is what makes an edit change nothing but what was asked for.

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

    GET: Final = Route("GET", "/channels/{channel_id}")
    EDIT: Final = Route("PATCH", "/channels/{channel_id}")
    DELETE: Final = Route("DELETE", "/channels/{channel_id}")
    OF_GUILD: Final = Route("GET", "/guilds/{guild_id}/channels")
    CREATE: Final = Route("POST", "/guilds/{guild_id}/channels")
    REORDER: Final = Route("PATCH", "/guilds/{guild_id}/channels")
    SET_OVERWRITE: Final = Route("PUT", "/channels/{channel_id}/permissions/{overwrite_id}")
    DELETE_OVERWRITE: Final = Route("DELETE", "/channels/{channel_id}/permissions/{overwrite_id}")
    INVITES: Final = Route("GET", "/channels/{channel_id}/invites")
    CREATE_INVITE: Final = Route("POST", "/channels/{channel_id}/invites")
    FOLLOW: Final = Route("POST", "/channels/{channel_id}/followers")
    THREAD_FROM_MESSAGE: Final = Route("POST", "/channels/{channel_id}/messages/{message_id}/threads")
    THREAD: Final = Route("POST", "/channels/{channel_id}/threads")
    JOIN_THREAD: Final = Route("PUT", "/channels/{channel_id}/thread-members/@me")
    ADD_THREAD_MEMBER: Final = Route("PUT", "/channels/{channel_id}/thread-members/{user_id}")
    LEAVE_THREAD: Final = Route("DELETE", "/channels/{channel_id}/thread-members/@me")
    REMOVE_THREAD_MEMBER: Final = Route("DELETE", "/channels/{channel_id}/thread-members/{user_id}")
    THREAD_MEMBER: Final = Route("GET", "/channels/{channel_id}/thread-members/{user_id}")
    THREAD_MEMBERS: Final = Route("GET", "/channels/{channel_id}/thread-members")
    PUBLIC_ARCHIVED: Final = Route("GET", "/channels/{channel_id}/threads/archived/public")
    PRIVATE_ARCHIVED: Final = Route("GET", "/channels/{channel_id}/threads/archived/private")
    JOINED_PRIVATE_ARCHIVED: Final = Route("GET", "/channels/{channel_id}/users/@me/threads/archived/private")
    ACTIVE_THREADS: Final = Route("GET", "/guilds/{guild_id}/threads/active")
    CREATE_STAGE: Final = Route("POST", "/stage-instances")
    STAGE: Final = Route("GET", "/stage-instances/{channel_id}")
    EDIT_STAGE: Final = Route("PATCH", "/stage-instances/{channel_id}")
    DELETE_STAGE: Final = Route("DELETE", "/stage-instances/{channel_id}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def get(self, channel_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches a channel, a thread or a DM.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        """
        return self.rest.request(self.GET.compile(channel_id))

    def edit(
            self,
            channel_id: int,
            /,
            *,
            name: str = MISSING,
            type: int = MISSING,
            position: int | None = MISSING,
            topic: str | None = MISSING,
            nsfw: bool | None = MISSING,
            rate_limit_per_user: int | None = MISSING,
            bitrate: int | None = MISSING,
            user_limit: int | None = MISSING,
            permission_overwrites: Sequence[dict[str, Any]] | None = MISSING,
            parent_id: int | None = MISSING,
            rtc_region: str | None = MISSING,
            video_quality_mode: int | None = MISSING,
            default_auto_archive_duration: int | None = MISSING,
            flags: int | None = MISSING,
            available_tags: Sequence[dict[str, Any]] | None = MISSING,
            default_reaction_emoji: dict[str, Any] | None = MISSING,
            default_thread_rate_limit_per_user: int | None = MISSING,
            default_sort_order: int | None = MISSING,
            default_forum_layout: int | None = MISSING,
            archived: bool = MISSING,
            auto_archive_duration: int = MISSING,
            locked: bool = MISSING,
            invitable: bool = MISSING,
            applied_tags: Sequence[int] = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a channel or a thread. Only what is given changes, ``None``
        clears a field where Discord allows it.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        name: :class:`str`
            The new name.
        type: :class:`int`
            The new type, only between text and announcement channels.
        position: Optional[:class:`int`]
            The position in the channel list.
        topic: Optional[:class:`str`]
            The topic of a text or forum channel.
        nsfw: Optional[:class:`bool`]
            Whether the channel is age restricted.
        rate_limit_per_user: Optional[:class:`int`]
            The slowmode in seconds.
        bitrate: Optional[:class:`int`]
            The bitrate of a voice channel.
        user_limit: Optional[:class:`int`]
            How many members a voice channel takes.
        permission_overwrites: Optional[Sequence[Dict[:class:`str`, Any]]]
            The whole set of permission overwrites.
        parent_id: Optional[:class:`int`]
            The category to put the channel in.
        rtc_region: Optional[:class:`str`]
            The voice region, ``None`` for automatic.
        video_quality_mode: Optional[:class:`int`]
            The camera quality of a voice channel.
        default_auto_archive_duration: Optional[:class:`int`]
            The minutes of inactivity after which new threads archive.
        flags: Optional[:class:`int`]
            The channel flags.
        available_tags: Optional[Sequence[Dict[:class:`str`, Any]]]
            The tags a forum or media channel offers.
        default_reaction_emoji: Optional[Dict[:class:`str`, Any]]
            The emoji shown as the quick reaction on forum posts.
        default_thread_rate_limit_per_user: Optional[:class:`int`]
            The slowmode new threads start with.
        default_sort_order: Optional[:class:`int`]
            How posts of a forum or media channel are sorted.
        default_forum_layout: Optional[:class:`int`]
            How posts of a forum channel are laid out.
        archived: :class:`bool`
            Whether the thread is archived.
        auto_archive_duration: :class:`int`
            The minutes of inactivity after which the thread archives.
        locked: :class:`bool`
            Whether only moderators can unarchive the thread.
        invitable: :class:`bool`
            Whether anyone can add members to the private thread.
        applied_tags: Sequence[:class:`int`]
            The tags on the forum post.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._fields(
            name,
            type,
            position,
            topic,
            nsfw,
            rate_limit_per_user,
            bitrate,
            user_limit,
            permission_overwrites,
            parent_id,
            rtc_region,
            video_quality_mode,
            default_auto_archive_duration,
            available_tags,
            default_reaction_emoji,
            default_thread_rate_limit_per_user,
            default_sort_order,
            default_forum_layout
        )

        if flags is not MISSING:
            payload["flags"] = flags

        if archived is not MISSING:
            payload["archived"] = archived

        if auto_archive_duration is not MISSING:
            payload["auto_archive_duration"] = auto_archive_duration

        if locked is not MISSING:
            payload["locked"] = locked

        if invitable is not MISSING:
            payload["invitable"] = invitable

        if applied_tags is not MISSING:
            payload["applied_tags"] = applied_tags

        return self.rest.request(self.EDIT.compile(channel_id), json=payload, reason=reason)

    def delete(self, channel_id: int, /, *, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Deletes a channel, or closes a DM.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(channel_id), reason=reason)

    def of_guild(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the channels of a guild, threads not among them.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.OF_GUILD.compile(guild_id))

    def create(
            self,
            guild_id: int,
            /,
            *,
            name: str,
            type: int = MISSING,
            position: int = MISSING,
            topic: str = MISSING,
            nsfw: bool = MISSING,
            rate_limit_per_user: int = MISSING,
            bitrate: int = MISSING,
            user_limit: int = MISSING,
            permission_overwrites: Sequence[dict[str, Any]] = MISSING,
            parent_id: int = MISSING,
            rtc_region: str = MISSING,
            video_quality_mode: int = MISSING,
            default_auto_archive_duration: int = MISSING,
            available_tags: Sequence[dict[str, Any]] = MISSING,
            default_reaction_emoji: dict[str, Any] = MISSING,
            default_thread_rate_limit_per_user: int = MISSING,
            default_sort_order: int = MISSING,
            default_forum_layout: int = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Creates a channel in a guild. The fields mean the same as in
        :meth:`edit`, a text channel comes out when no type is given.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._fields(
            name,
            type,
            position,
            topic,
            nsfw,
            rate_limit_per_user,
            bitrate,
            user_limit,
            permission_overwrites,
            parent_id,
            rtc_region,
            video_quality_mode,
            default_auto_archive_duration,
            available_tags,
            default_reaction_emoji,
            default_thread_rate_limit_per_user,
            default_sort_order,
            default_forum_layout
        )

        return self.rest.request(self.CREATE.compile(guild_id), json=payload, reason=reason)

    def reorder(self, guild_id: int, positions: Sequence[dict[str, Any]], /, *, reason: str | None = None) -> Response[None]:
        """
        Moves channels of a guild in one go.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        positions: Sequence[Dict[:class:`str`, Any]]
            One entry per channel with its ``id`` and the new
            ``position``, ``parent_id`` or ``lock_permissions``.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.REORDER.compile(guild_id), json=positions, reason=reason)

    def set_overwrite(
            self,
            channel_id: int,
            overwrite_id: int,
            /,
            *,
            type: int,
            allow: str = MISSING,
            deny: str = MISSING,
            reason: str | None = None
    ) -> Response[None]:
        """
        Sets the permission overwrite of a role or member on a channel,
        replacing what was there.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        overwrite_id: :class:`int`
            The role or member.
        type: :class:`int`
            ``0`` for a role, ``1`` for a member.
        allow: :class:`str`
            The permissions to allow, as the bit set in a string.
        deny: :class:`str`
            The permissions to deny, as the bit set in a string.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(type=type, allow=allow, deny=deny)

        return self.rest.request(self.SET_OVERWRITE.compile(channel_id, overwrite_id), json=payload, reason=reason)

    def delete_overwrite(self, channel_id: int, overwrite_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Removes the permission overwrite of a role or member from a
        channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        overwrite_id: :class:`int`
            The role or member.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE_OVERWRITE.compile(channel_id, overwrite_id), reason=reason)

    def invites(self, channel_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the invites of a channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        """
        return self.rest.request(self.INVITES.compile(channel_id))

    def create_invite(
            self,
            channel_id: int,
            /,
            *,
            max_age: int = MISSING,
            max_uses: int = MISSING,
            temporary: bool = MISSING,
            unique: bool = MISSING,
            target_type: int = MISSING,
            target_user_id: int = MISSING,
            target_application_id: int = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Creates an invite to a channel. What is not given is up to
        Discord, which means a day of validity, unlimited uses and no
        temporary membership.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        max_age: :class:`int`
            Seconds until the invite expires, ``0`` for never.
        max_uses: :class:`int`
            How often the invite can be used, ``0`` for no limit.
        temporary: :class:`bool`
            Whether members who join through it are kicked once they
            leave voice without a role.
        unique: :class:`bool`
            Whether to create a new invite instead of reusing one that
            matches.
        target_type: :class:`int`
            What a voice channel invite opens, ``1`` a stream, ``2`` an
            activity.
        target_user_id: :class:`int`
            Whose stream.
        target_application_id: :class:`int`
            Which activity.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(
            max_age=max_age,
            max_uses=max_uses,
            temporary=temporary,
            unique=unique,
            target_type=target_type,
            target_user_id=target_user_id,
            target_application_id=target_application_id
        )

        return self.rest.request(self.CREATE_INVITE.compile(channel_id), json=payload, reason=reason)

    def follow(self, channel_id: int, target_channel_id: int, /, *, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Makes a channel follow an announcement channel, so the
        announcements are crossposted into it.

        Parameters
        -----------
        channel_id: :class:`int`
            The announcement channel.
        target_channel_id: :class:`int`
            The channel that receives the announcements.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.FOLLOW.compile(channel_id), json={"webhook_channel_id": target_channel_id}, reason=reason)

    def create_thread_from_message(
            self,
            channel_id: int,
            message_id: int,
            /,
            *,
            name: str,
            auto_archive_duration: int = MISSING,
            rate_limit_per_user: int | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Starts a public thread on a message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message the thread hangs off.
        name: :class:`str`
            The name of the thread.
        auto_archive_duration: :class:`int`
            The minutes of inactivity after which the thread archives.
        rate_limit_per_user: Optional[:class:`int`]
            The slowmode in seconds.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(name=name, auto_archive_duration=auto_archive_duration, rate_limit_per_user=rate_limit_per_user)

        return self.rest.request(self.THREAD_FROM_MESSAGE.compile(channel_id, message_id), json=payload, reason=reason)

    def create_thread(
            self,
            channel_id: int,
            /,
            *,
            name: str,
            type: int = MISSING,
            auto_archive_duration: int = MISSING,
            invitable: bool = MISSING,
            rate_limit_per_user: int | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Starts a thread that hangs off no message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        name: :class:`str`
            The name of the thread.
        type: :class:`int`
            The thread type, a private thread when not given.
        auto_archive_duration: :class:`int`
            The minutes of inactivity after which the thread archives.
        invitable: :class:`bool`
            Whether anyone can add members to a private thread.
        rate_limit_per_user: Optional[:class:`int`]
            The slowmode in seconds.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(name=name, type=type, auto_archive_duration=auto_archive_duration, invitable=invitable, rate_limit_per_user=rate_limit_per_user)

        return self.rest.request(self.THREAD.compile(channel_id), json=payload, reason=reason)

    def create_post(
            self,
            channel_id: int,
            /,
            *,
            name: str,
            message: dict[str, Any],
            auto_archive_duration: int = MISSING,
            rate_limit_per_user: int | None = MISSING,
            applied_tags: Sequence[int] = MISSING,
            files: Sequence[File] = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Starts a post in a forum or media channel, which is a thread
        with its first message.

        Parameters
        -----------
        channel_id: :class:`int`
            The forum or media channel.
        name: :class:`str`
            The title of the post.
        message: Dict[:class:`str`, Any]
            The first message, as :meth:`Messages.send` would build it.
        auto_archive_duration: :class:`int`
            The minutes of inactivity after which the post archives.
        rate_limit_per_user: Optional[:class:`int`]
            The slowmode in seconds.
        applied_tags: Sequence[:class:`int`]
            The tags of the post.
        files: Sequence[:class:`File`]
            The files of the first message. Each gets its entry in the
            message's ``attachments`` after the given ones.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        if files:
            entries = [file.to_dict(index) for index, file in enumerate(files)]
            message = {**message, "attachments": [*message.get("attachments", []), *entries]}

        payload = self._present(name=name, message=message, auto_archive_duration=auto_archive_duration, rate_limit_per_user=rate_limit_per_user, applied_tags=applied_tags)

        return self.rest.request(self.THREAD.compile(channel_id), json=payload, files=files or None, params={"use_nested_fields": 1}, reason=reason)

    def join_thread(self, channel_id: int, /) -> Response[None]:
        """
        Joins a thread as the bot.

        Parameters
        -----------
        channel_id: :class:`int`
            The thread.
        """
        return self.rest.request(self.JOIN_THREAD.compile(channel_id))

    def add_thread_member(self, channel_id: int, user_id: int, /) -> Response[None]:
        """
        Adds a member to a thread.

        Parameters
        -----------
        channel_id: :class:`int`
            The thread.
        user_id: :class:`int`
            The member.
        """
        return self.rest.request(self.ADD_THREAD_MEMBER.compile(channel_id, user_id))

    def leave_thread(self, channel_id: int, /) -> Response[None]:
        """
        Leaves a thread as the bot.

        Parameters
        -----------
        channel_id: :class:`int`
            The thread.
        """
        return self.rest.request(self.LEAVE_THREAD.compile(channel_id))

    def remove_thread_member(self, channel_id: int, user_id: int, /) -> Response[None]:
        """
        Removes a member from a thread.

        Parameters
        -----------
        channel_id: :class:`int`
            The thread.
        user_id: :class:`int`
            The member.
        """
        return self.rest.request(self.REMOVE_THREAD_MEMBER.compile(channel_id, user_id))

    def thread_member(self, channel_id: int, user_id: int, /, *, with_member: bool = MISSING) -> Response[dict[str, Any]]:
        """
        Fetches one member of a thread.

        Parameters
        -----------
        channel_id: :class:`int`
            The thread.
        user_id: :class:`int`
            The member.
        with_member: :class:`bool`
            Whether the guild member comes along in ``member``.
        """
        return self.rest.request(self.THREAD_MEMBER.compile(channel_id, user_id), params={"with_member": with_member or None})

    def thread_members(
            self,
            channel_id: int,
            /,
            *,
            with_member: bool = MISSING,
            after: int | None = None,
            limit: int | None = None
    ) -> Response[list[dict[str, Any]]]:
        """
        Fetches the members of a thread.

        Parameters
        -----------
        channel_id: :class:`int`
            The thread.
        with_member: :class:`bool`
            Whether each guild member comes along in ``member``, which
            is also what makes ``after`` and ``limit`` count.
        after: Optional[:class:`int`]
            Only members with an ID above this one.
        limit: Optional[:class:`int`]
            How many members at most, 1 to 100.
        """
        return self.rest.request(self.THREAD_MEMBERS.compile(channel_id), params={"with_member": with_member or None, "after": after, "limit": limit})

    def public_archived_threads(self, channel_id: int, /, *, before: str | None = None, limit: int | None = None) -> Response[dict[str, Any]]:
        """
        Fetches the archived public threads of a channel, most recently
        archived first. The payload holds them under ``threads`` with
        the bot's memberships under ``members`` and ``has_more``.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        before: Optional[:class:`str`]
            Only threads archived before this ISO 8601 timestamp.
        limit: Optional[:class:`int`]
            How many threads at most.
        """
        return self.rest.request(self.PUBLIC_ARCHIVED.compile(channel_id), params={"before": before, "limit": limit})

    def private_archived_threads(self, channel_id: int, /, *, before: str | None = None, limit: int | None = None) -> Response[dict[str, Any]]:
        """
        Fetches the archived private threads of a channel, which takes
        the permission to manage threads. The payload reads like
        :meth:`public_archived_threads`.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        before: Optional[:class:`str`]
            Only threads archived before this ISO 8601 timestamp.
        limit: Optional[:class:`int`]
            How many threads at most.
        """
        return self.rest.request(self.PRIVATE_ARCHIVED.compile(channel_id), params={"before": before, "limit": limit})

    def joined_private_archived_threads(self, channel_id: int, /, *, before: int | None = None, limit: int | None = None) -> Response[dict[str, Any]]:
        """
        Fetches the archived private threads of a channel the bot is a
        member of. The payload reads like :meth:`public_archived_threads`.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        before: Optional[:class:`int`]
            Only threads with an ID below this one.
        limit: Optional[:class:`int`]
            How many threads at most.
        """
        return self.rest.request(self.JOINED_PRIVATE_ARCHIVED.compile(channel_id), params={"before": before, "limit": limit})

    def active_threads(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches every active thread of a guild the bot can see. The
        payload holds them under ``threads`` with the bot's memberships
        under ``members``.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.ACTIVE_THREADS.compile(guild_id))

    def create_stage(
            self,
            channel_id: int,
            /,
            *,
            topic: str,
            privacy_level: int = MISSING,
            send_start_notification: bool = MISSING,
            guild_scheduled_event_id: int = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Starts a stage in a stage channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The stage channel.
        topic: :class:`str`
            What the stage is about.
        privacy_level: :class:`int`
            Who can see the stage.
        send_start_notification: :class:`bool`
            Whether everyone in the guild is notified.
        guild_scheduled_event_id: :class:`int`
            The scheduled event the stage belongs to.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(channel_id=channel_id, topic=topic, privacy_level=privacy_level, send_start_notification=send_start_notification, guild_scheduled_event_id=guild_scheduled_event_id)

        return self.rest.request(self.CREATE_STAGE.compile(), json=payload, reason=reason)

    def stage(self, channel_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the running stage of a stage channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The stage channel.
        """
        return self.rest.request(self.STAGE.compile(channel_id))

    def edit_stage(self, channel_id: int, /, *, topic: str = MISSING, privacy_level: int = MISSING, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Edits the running stage of a stage channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The stage channel.
        topic: :class:`str`
            What the stage is about.
        privacy_level: :class:`int`
            Who can see the stage.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload = self._present(topic=topic, privacy_level=privacy_level)

        return self.rest.request(self.EDIT_STAGE.compile(channel_id), json=payload, reason=reason)

    def delete_stage(self, channel_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Ends the running stage of a stage channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The stage channel.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE_STAGE.compile(channel_id), reason=reason)

    @staticmethod
    def _fields(
            name: str,
            type: int,
            position: int | None,
            topic: str | None,
            nsfw: bool | None,
            rate_limit_per_user: int | None,
            bitrate: int | None,
            user_limit: int | None,
            permission_overwrites: Sequence[dict[str, Any]] | None,
            parent_id: int | None,
            rtc_region: str | None,
            video_quality_mode: int | None,
            default_auto_archive_duration: int | None,
            available_tags: Sequence[dict[str, Any]] | None,
            default_reaction_emoji: dict[str, Any] | None,
            default_thread_rate_limit_per_user: int | None,
            default_sort_order: int | None,
            default_forum_layout: int | None,
            /
    ) -> dict[str, Any]:
        """
        The fields creating and editing a channel share, only those that
        were given.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if type is not MISSING:
            payload["type"] = type

        if position is not MISSING:
            payload["position"] = position

        if topic is not MISSING:
            payload["topic"] = topic

        if nsfw is not MISSING:
            payload["nsfw"] = nsfw

        if rate_limit_per_user is not MISSING:
            payload["rate_limit_per_user"] = rate_limit_per_user

        if bitrate is not MISSING:
            payload["bitrate"] = bitrate

        if user_limit is not MISSING:
            payload["user_limit"] = user_limit

        if permission_overwrites is not MISSING:
            payload["permission_overwrites"] = permission_overwrites

        if parent_id is not MISSING:
            payload["parent_id"] = parent_id

        if rtc_region is not MISSING:
            payload["rtc_region"] = rtc_region

        if video_quality_mode is not MISSING:
            payload["video_quality_mode"] = video_quality_mode

        if default_auto_archive_duration is not MISSING:
            payload["default_auto_archive_duration"] = default_auto_archive_duration

        if available_tags is not MISSING:
            payload["available_tags"] = available_tags

        if default_reaction_emoji is not MISSING:
            payload["default_reaction_emoji"] = default_reaction_emoji

        if default_thread_rate_limit_per_user is not MISSING:
            payload["default_thread_rate_limit_per_user"] = default_thread_rate_limit_per_user

        if default_sort_order is not MISSING:
            payload["default_sort_order"] = default_sort_order

        if default_forum_layout is not MISSING:
            payload["default_forum_layout"] = default_forum_layout

        return payload

    @staticmethod
    def _present(**fields: Any) -> dict[str, Any]:
        """
        The fields that were given, which keeps an edit from touching
        anything else.
        """
        return {name: value for name, value in fields.items() if value is not MISSING}

__all__ = ["Channels"]