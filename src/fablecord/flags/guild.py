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

from .base import Flag, Flags

class SystemChannelFlags(Flags):
    """
    What a guild's system channel keeps quiet about.

    Discord stores these as suppressions, a set bit means the message is
    not sent, and the names here say exactly that. discord.py flips them
    around, so its ``join_notifications`` is our
    ``suppress_join_notifications`` negated. A value of ``0`` means the
    system channel posts everything, which is what a new guild starts with.
    """

    __slots__ = []

    suppress_join_notifications = Flag(1 << 0)
    """
    :class:`bool`: No message when a member joins. With this set, the
    reply suppression below has nothing left to suppress.
    """

    suppress_premium_subscriptions = Flag(1 << 1)
    """
    :class:`bool`: No message when someone boosts the guild or it reaches
    a new boost level.
    """

    suppress_guild_reminder_notifications = Flag(1 << 2)
    """
    :class:`bool`: No setup tips from Discord in the system channel.
    """

    suppress_join_notification_replies = Flag(1 << 3)
    """
    :class:`bool`: Join messages come without the sticker reply buttons.
    """

    suppress_role_subscription_purchase_notifications = Flag(1 << 4)
    """
    :class:`bool`: No message when someone buys or renews a role subscription.
    """

    suppress_role_subscription_purchase_notification_replies = Flag(1 << 5)
    """
    :class:`bool`: Role subscription messages come without the sticker
    reply buttons.
    """

    suppress_emoji_added_notifications = Flag(1 << 8)
    """
    :class:`bool`: No message when an emoji is added to the guild.
    """

class ChannelFlags(Flags):
    """
    The flags of a channel or thread.

    ``pinned`` only ever appears on threads inside forum and media
    channels, the other two only on the forum or media channel itself.
    """

    __slots__ = []

    pinned = Flag(1 << 1)
    """
    :class:`bool`: The post sits at the top of its forum. A forum can pin
    only one post at a time.
    """

    require_tag = Flag(1 << 4)
    """
    :class:`bool`: Every new post needs at least one tag, creating one
    without fails with a 400.
    """

    hide_media_download_options = Flag(1 << 15)
    """
    :class:`bool`: The download button on embedded media is hidden. Media
    channels only.
    """

class RoleFlags(Flags):
    """
    The flags of a role.
    """

    __slots__ = []

    in_prompt = Flag(1 << 0)
    """
    :class:`bool`: The role is offered in an onboarding prompt, so it
    cannot be deleted while that prompt exists.
    """

__all__ = ["SystemChannelFlags", "ChannelFlags", "RoleFlags"]