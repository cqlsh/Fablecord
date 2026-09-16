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

class AuditLogActionCategory(Enum):
    """
    Whether an audit log entry created, updated or deleted its target.

    It decides which sides an entry carries: a create has only an
    ``after``, a delete only a ``before``, an update both. Actions such
    as kicks and bans have no category and no changes at all.
    """

    create = 1
    """
    Something new appeared, the entry carries only ``after``.
    """

    delete = 2
    """
    Something went away, the entry carries only ``before``.
    """

    update = 3
    """
    Something changed, the entry carries ``before`` and ``after``.
    """

class AuditLogTargetType(Enum):
    """
    What the ``target_id`` of an audit log entry points at.

    The action decides it, see :attr:`AuditLogAction.target_type`, and
    the entry uses it to turn the bare ID into the matching model.
    """

    guild = "guild"
    """
    The guild itself.
    """

    channel = "channel"
    """
    A channel, also for permission overwrites and bulk deletes.
    """

    user = "user"
    """
    A user or member, also for auto moderation actions against one.
    """

    role = "role"
    """
    A role.
    """

    invite = "invite"
    """
    An invite. The ID is the invite code's target, the code sits in the
    changes.
    """

    webhook = "webhook"
    """
    A webhook.
    """

    emoji = "emoji"
    """
    A custom emoji.
    """

    message = "message"
    """
    A message. The ID is the author, the options name the channel.
    """

    integration = "integration"
    """
    An integration.
    """

    stage_instance = "stage_instance"
    """
    A live stage.
    """

    sticker = "sticker"
    """
    A sticker.
    """

    scheduled_event = "scheduled_event"
    """
    A scheduled event.
    """

    thread = "thread"
    """
    A thread.
    """

    app_command = "app_command"
    """
    An application command, or the application itself when its default
    permissions changed.
    """

    soundboard_sound = "soundboard_sound"
    """
    A soundboard sound.
    """

    automod_rule = "automod_rule"
    """
    An auto moderation rule.
    """

    onboarding_prompt = "onboarding_prompt"
    """
    An onboarding question.
    """

    onboarding = "onboarding"
    """
    The onboarding settings of the guild.
    """

    home_settings = "home_settings"
    """
    The server guide of the guild.
    """

class AuditLogAction(Enum):
    """
    The kind of change an audit log entry records.

    Discord numbers the actions in blocks per object type, which is why
    the values have gaps. :attr:`is_create`, :attr:`is_update` and
    :attr:`is_delete` say which of ``before`` and ``after`` an entry
    carries, :attr:`target_type` says what its ID points at.
    """

    guild_update = 1
    """
    The guild's settings changed.
    """

    channel_create = 10
    """
    A channel was created.
    """

    channel_update = 11
    """
    A channel's settings changed.
    """

    channel_delete = 12
    """
    A channel was deleted.
    """

    overwrite_create = 13
    """
    A permission overwrite was added to a channel. The target is the
    channel, the options name the role or member.
    """

    overwrite_update = 14
    """
    A permission overwrite of a channel changed.
    """

    overwrite_delete = 15
    """
    A permission overwrite was removed from a channel.
    """

    kick = 20
    """
    A member was kicked.
    """

    member_prune = 21
    """
    Inactive members were pruned. The options carry the day count and how
    many left, there is no single target.
    """

    ban = 22
    """
    A user was banned.
    """

    unban = 23
    """
    A user was unbanned.
    """

    member_update = 24
    """
    A member's nickname, timeout or voice mute state changed.
    """

    member_role_update = 25
    """
    Roles were added to or removed from a member.
    """

    member_move = 26
    """
    Members were moved to another voice channel.
    """

    member_disconnect = 27
    """
    Members were disconnected from voice.
    """

    bot_add = 28
    """
    A bot was added to the guild.
    """

    role_create = 30
    """
    A role was created.
    """

    role_update = 31
    """
    A role's settings or permissions changed.
    """

    role_delete = 32
    """
    A role was deleted.
    """

    invite_create = 40
    """
    An invite was created.
    """

    invite_update = 41
    """
    An invite was changed.
    """

    invite_delete = 42
    """
    An invite was revoked.
    """

    webhook_create = 50
    """
    A webhook was created.
    """

    webhook_update = 51
    """
    A webhook's name, avatar or channel changed.
    """

    webhook_delete = 52
    """
    A webhook was deleted.
    """

    emoji_create = 60
    """
    An emoji was uploaded.
    """

    emoji_update = 61
    """
    An emoji was renamed.
    """

    emoji_delete = 62
    """
    An emoji was deleted.
    """

    message_delete = 72
    """
    Someone deleted another user's message. The target is the author,
    the options name the channel and the count.
    """

    message_bulk_delete = 73
    """
    Messages were deleted in bulk. The target is the channel.
    """

    message_pin = 74
    """
    A message was pinned. The options name the channel and the message.
    """

    message_unpin = 75
    """
    A message was unpinned.
    """

    integration_create = 80
    """
    An integration was added.
    """

    integration_update = 81
    """
    An integration's settings changed.
    """

    integration_delete = 82
    """
    An integration was removed.
    """

    stage_instance_create = 83
    """
    A stage went live.
    """

    stage_instance_update = 84
    """
    A stage's topic or privacy changed.
    """

    stage_instance_delete = 85
    """
    A stage ended.
    """

    sticker_create = 90
    """
    A sticker was uploaded.
    """

    sticker_update = 91
    """
    A sticker's details changed.
    """

    sticker_delete = 92
    """
    A sticker was deleted.
    """

    scheduled_event_create = 100
    """
    A scheduled event was created.
    """

    scheduled_event_update = 101
    """
    A scheduled event changed.
    """

    scheduled_event_delete = 102
    """
    A scheduled event was cancelled.
    """

    thread_create = 110
    """
    A thread was created.
    """

    thread_update = 111
    """
    A thread's settings changed.
    """

    thread_delete = 112
    """
    A thread was deleted.
    """

    app_command_permission_update = 121
    """
    The permissions of an application command changed. The target is the
    command, or the application when its defaults changed.
    """

    soundboard_sound_create = 130
    """
    A soundboard sound was uploaded.
    """

    soundboard_sound_update = 131
    """
    A soundboard sound changed.
    """

    soundboard_sound_delete = 132
    """
    A soundboard sound was deleted.
    """

    automod_rule_create = 140
    """
    An auto moderation rule was created.
    """

    automod_rule_update = 141
    """
    An auto moderation rule changed.
    """

    automod_rule_delete = 142
    """
    An auto moderation rule was deleted.
    """

    automod_block_message = 143
    """
    Auto moderation blocked a message. The target is the author.
    """

    automod_flag_message = 144
    """
    Auto moderation flagged a message to a channel.
    """

    automod_timeout_member = 145
    """
    Auto moderation timed a member out.
    """

    automod_quarantine_user = 146
    """
    Auto moderation quarantined a user.
    """

    creator_monetization_request_created = 150
    """
    The guild applied for creator monetization. There is no target.
    """

    creator_monetization_terms_accepted = 151
    """
    The monetization terms were accepted. There is no target.
    """

    onboarding_prompt_create = 163
    """
    An onboarding question was added.
    """

    onboarding_prompt_update = 164
    """
    An onboarding question changed.
    """

    onboarding_prompt_delete = 165
    """
    An onboarding question was removed.
    """

    onboarding_create = 166
    """
    Onboarding was set up.
    """

    onboarding_update = 167
    """
    The onboarding settings changed.
    """

    home_settings_create = 190
    """
    The server guide was set up.
    """

    home_settings_update = 191
    """
    The server guide changed.
    """

    is_create = Category(
        channel_create,
        overwrite_create,
        role_create,
        invite_create,
        webhook_create,
        emoji_create,
        integration_create,
        stage_instance_create,
        sticker_create,
        scheduled_event_create,
        thread_create,
        soundboard_sound_create,
        automod_rule_create,
        onboarding_prompt_create,
        onboarding_create,
        home_settings_create
    )
    """
    :class:`bool`: Whether the entry records something new. Such entries
    carry only ``after``.
    """

    is_update = Category(
        guild_update,
        channel_update,
        overwrite_update,
        member_update,
        member_role_update,
        role_update,
        invite_update,
        webhook_update,
        emoji_update,
        integration_update,
        stage_instance_update,
        sticker_update,
        scheduled_event_update,
        thread_update,
        app_command_permission_update,
        soundboard_sound_update,
        automod_rule_update,
        onboarding_prompt_update,
        onboarding_update,
        home_settings_update
    )
    """
    :class:`bool`: Whether the entry records a change. Such entries carry
    ``before`` and ``after``.
    """

    is_delete = Category(
        channel_delete,
        overwrite_delete,
        role_delete,
        invite_delete,
        webhook_delete,
        emoji_delete,
        message_delete,
        message_bulk_delete,
        integration_delete,
        stage_instance_delete,
        sticker_delete,
        scheduled_event_delete,
        thread_delete,
        soundboard_sound_delete,
        automod_rule_delete,
        onboarding_prompt_delete
    )
    """
    :class:`bool`: Whether the entry records a removal. Such entries carry
    only ``before``.
    """

    __targets: dict[AuditLogTargetType, list[int]] = {
        AuditLogTargetType.guild: [guild_update],
        AuditLogTargetType.channel: [channel_create, channel_update, channel_delete, overwrite_create, overwrite_update, overwrite_delete, message_bulk_delete],
        AuditLogTargetType.user: [
            kick, member_prune, ban, unban, member_update, 
            member_role_update, member_move, member_disconnect, 
            bot_add, automod_block_message, automod_flag_message, 
            automod_timeout_member, automod_quarantine_user
        ],
        AuditLogTargetType.role: [role_create, role_update, role_delete],
        AuditLogTargetType.invite: [invite_create, invite_update, invite_delete],
        AuditLogTargetType.webhook: [webhook_create, webhook_update, webhook_delete],
        AuditLogTargetType.emoji: [emoji_create, emoji_update, emoji_delete],
        AuditLogTargetType.message: [message_delete, message_pin, message_unpin],
        AuditLogTargetType.integration: [integration_create, integration_update, integration_delete],
        AuditLogTargetType.stage_instance: [stage_instance_create, stage_instance_update, stage_instance_delete],
        AuditLogTargetType.sticker: [sticker_create, sticker_update, sticker_delete],
        AuditLogTargetType.scheduled_event: [scheduled_event_create, scheduled_event_update, scheduled_event_delete],
        AuditLogTargetType.thread: [thread_create, thread_update, thread_delete],
        AuditLogTargetType.app_command: [app_command_permission_update],
        AuditLogTargetType.soundboard_sound: [soundboard_sound_create, soundboard_sound_update, soundboard_sound_delete],
        AuditLogTargetType.automod_rule: [automod_rule_create, automod_rule_update, automod_rule_delete],
        AuditLogTargetType.onboarding_prompt: [onboarding_prompt_create, onboarding_prompt_update, onboarding_prompt_delete],
        AuditLogTargetType.onboarding: [onboarding_create, onboarding_update],
        AuditLogTargetType.home_settings: [home_settings_create, home_settings_update]
    }
    __target_by_value: dict[int, AuditLogTargetType] = {value: target for target, values in __targets.items() for value in values}

    @property
    def category(self) -> AuditLogActionCategory | None:
        """
        Optional[:class:`AuditLogActionCategory`]: The category as a
        member, for code that wants one value instead of three checks.
        ``None`` for actions without changes, such as kicks and bans.
        """
        if self.is_create:
            return AuditLogActionCategory.create

        if self.is_update:
            return AuditLogActionCategory.update

        if self.is_delete:
            return AuditLogActionCategory.delete

        return None

    @property
    def target_type(self) -> AuditLogTargetType | None:
        """
        Optional[:class:`AuditLogTargetType`]: What the ``target_id`` of
        an entry with this action points at. ``None`` for the two
        monetization actions and for actions Discord added since.
        """
        return self.__target_by_value.get(self.value)

__all__ = ["AuditLogActionCategory", "AuditLogTargetType", "AuditLogAction"]