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

class MessageType(Enum):
    """
    The type of a message.

    Only a handful of types carry content a user wrote. Everything else
    is a system message that Discord renders from the type alone, and
    some of those cannot be deleted at all. :attr:`is_system` and
    :attr:`is_deletable` answer both questions without a table lookup in
    user code.
    """

    default = 0
    """
    A regular message.
    """

    recipient_add = 1
    """
    Someone was added to a group direct message or a thread.
    """

    recipient_remove = 2
    """
    Someone was removed from a group direct message or a thread.
    """

    call = 3
    """
    A call was started in a direct message.
    """

    channel_name_change = 4
    """
    The name of a group direct message or a thread changed.
    """

    channel_icon_change = 5
    """
    The icon of a group direct message changed.
    """

    pins_add = 6
    """
    A message was pinned.
    """

    new_member = 7
    """
    A member joined the guild. The system channel shows a random greeting.
    """

    premium_guild_subscription = 8
    """
    Someone boosted the guild.
    """

    premium_guild_tier_1 = 9
    """
    A boost pushed the guild to level one.
    """

    premium_guild_tier_2 = 10
    """
    A boost pushed the guild to level two.
    """

    premium_guild_tier_3 = 11
    """
    A boost pushed the guild to level three.
    """

    channel_follow_add = 12
    """
    An announcement channel was followed into this channel.
    """

    guild_stream = 13
    """
    A stream started in a guild. Discord no longer sends this one.
    """

    guild_discovery_disqualified = 14
    """
    The guild lost its server discovery listing.
    """

    guild_discovery_requalified = 15
    """
    The guild qualifies for server discovery again.
    """

    guild_discovery_grace_period_initial_warning = 16
    """
    First warning that the guild is about to lose its discovery listing.
    """

    guild_discovery_grace_period_final_warning = 17
    """
    Last warning that the guild is about to lose its discovery listing.
    """

    thread_created = 18
    """
    A thread was created from a message in this channel.
    """

    reply = 19
    """
    A reply to another message. ``message_reference`` points at it.
    """

    chat_input_command = 20
    """
    The response to a slash command.
    """

    thread_starter_message = 21
    """
    The first message of a thread, a copy of the message it was started
    from.
    """

    guild_invite_reminder = 22
    """
    Discord nudging a new guild's owner to invite people.
    """

    context_menu_command = 23
    """
    The response to a user or message context menu command.
    """

    auto_moderation_action = 24
    """
    Auto moderation blocked or flagged something. Only visible with
    ``view_audit_log`` or ``manage_guild``.
    """

    role_subscription_purchase = 25
    """
    Someone bought or renewed a role subscription.
    """

    interaction_premium_upsell = 26
    """
    An application asking the user to subscribe to it.
    """

    stage_start = 27
    """
    A stage went live.
    """

    stage_end = 28
    """
    A stage ended.
    """

    stage_speaker = 29
    """
    Someone became a speaker on the stage.
    """

    stage_raise_hand = 30
    """
    Someone raised their hand on the stage.
    """

    stage_topic = 31
    """
    The topic of the stage changed.
    """

    guild_application_premium_subscription = 32
    """
    The guild subscribed to an application.
    """

    guild_incident_alert_mode_enabled = 36
    """
    A moderator paused invites or direct messages to deal with an incident.
    """

    guild_incident_alert_mode_disabled = 37
    """
    The incident measures were lifted.
    """

    guild_incident_report_raid = 38
    """
    A moderator reported a raid to Discord.
    """

    guild_incident_report_false_alarm = 39
    """
    A moderator reported that the raid alert was a false alarm.
    """

    purchase_notification = 44
    """
    Someone bought a product from the guild's shop.
    """

    poll_result = 46
    """
    A poll ended and this message shows its result.
    """

    emoji_added = 63
    """
    An emoji was added to the guild.
    """

    is_system = Category.excluding(
        default,
        reply,
        chat_input_command,
        context_menu_command,
        thread_starter_message
    )
    """
    :class:`bool`: Whether Discord writes the content of such messages
    itself. For these the content field is empty and the client renders
    a fixed text from the type.
    """

    is_deletable = Category.excluding(
        recipient_add,
        recipient_remove,
        call,
        channel_name_change,
        channel_icon_change,
        guild_discovery_disqualified,
        guild_discovery_requalified,
        guild_discovery_grace_period_initial_warning,
        guild_discovery_grace_period_final_warning,
        thread_starter_message,
        guild_application_premium_subscription
    )
    """
    :class:`bool`: Whether Discord lets anyone delete such messages.
    Trying it on the others fails with a 400.
    """

class MessageReferenceType(Enum):
    """
    What a message reference points at.
    """

    default = 0
    """
    A reply. The referenced message is quoted above the reply.
    """

    forward = 1
    """
    A forward. The message carries a snapshot of the referenced one.
    """

class ReactionType(Enum):
    """
    The kind of a reaction.
    """

    normal = 0
    """
    A regular reaction.
    """

    burst = 1
    """
    A super reaction with an animation, which costs Nitro users a burst.
    """

class PollLayoutType(Enum):
    """
    The layout of a poll.

    Discord has exactly one so far, the field exists for later.
    """

    default = 1
    """
    The standard layout with the answers listed below the question.
    """

__all__ = ["MessageType", "MessageReferenceType", "ReactionType", "PollLayoutType"]