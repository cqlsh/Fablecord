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

from typing import ClassVar, Self

from .base import Flag, Flags

class MessageFlags(Flags):
    """
    The flags of a message.

    Most of these are set by Discord. The ones a bot may set itself when
    sending are listed by :meth:`sendable`, anything else in a send request
    is rejected with a 400.
    """

    __slots__ = []

    crossposted = Flag(1 << 0)
    """
    :class:`bool`: The message was published to the channels that follow
    this announcement channel.
    """

    is_crossposted = Flag(1 << 1)
    """
    :class:`bool`: The message is a copy that arrived from a followed
    announcement channel.
    """

    suppress_embeds = Flag(1 << 2)
    """
    :class:`bool`: Links in the message do not unfurl. Toggling it on an
    existing message is the only edit a bot can make to someone else's
    message, given ``manage_messages``.
    """

    source_message_deleted = Flag(1 << 3)
    """
    :class:`bool`: The original of this crosspost was deleted, so the copy
    can no longer be updated.
    """

    urgent = Flag(1 << 4)
    """
    :class:`bool`: An urgent message from Discord's system, shown until the
    user acknowledges it.
    """

    has_thread = Flag(1 << 5)
    """
    :class:`bool`: A thread was started from this message. Its ID equals
    the message ID.
    """

    ephemeral = Flag(1 << 6)
    """
    :class:`bool`: Only the user who triggered the interaction sees the
    message. It cannot be fetched later, reacted to or pinned.
    """

    loading = Flag(1 << 7)
    """
    :class:`bool`: A deferred interaction response that is still showing
    the thinking state.
    """

    failed_to_mention_some_roles_in_thread = Flag(1 << 8)
    """
    :class:`bool`: Adding a mentioned role to the thread failed, usually
    because the role has too many members.
    """

    suppress_notifications = Flag(1 << 12)
    """
    :class:`bool`: The message pings nobody, not even people it mentions.
    This is what ``@silent`` does in the client.
    """

    voice = Flag(1 << 13)
    """
    :class:`bool`: A voice message. Discord requires exactly one audio
    attachment with a waveform and a duration and nothing else.
    """

    forwarded = Flag(1 << 14)
    """
    :class:`bool`: The message carries a snapshot of a forwarded message
    instead of content of its own.
    """

    components_v2 = Flag(1 << 15)
    """
    :class:`bool`: The message is built from layout components. Content,
    embeds, stickers and polls are not allowed on such a message, and it
    cannot be turned back into a normal one.
    """

    _sendable: ClassVar[int] = (
        suppress_embeds.bit
        | suppress_notifications.bit
        | ephemeral.bit
        | voice.bit
        | components_v2.bit
    )

    @classmethod
    def sendable(cls) -> Self:
        """
        The flags a bot may set itself when sending a message.

        Everything else is decided by Discord, and a send request that
        carries one of those flags fails with a 400.
        """
        return cls.from_value(cls._sendable)

class AttachmentFlags(Flags):
    """
    The flags of an attachment.
    """

    __slots__ = []

    clip = Flag(1 << 0)
    """
    :class:`bool`: A clip recorded from a stream or activity.
    """

    thumbnail = Flag(1 << 1)
    """
    :class:`bool`: The thumbnail of a media channel post, not a regular
    attachment.
    """

    remix = Flag(1 << 2)
    """
    :class:`bool`: The image was edited with the client's remix feature.
    """

    spoiler = Flag(1 << 3)
    """
    :class:`bool`: The attachment is blurred until clicked. Uploading a
    file named ``SPOILER_something`` sets this.
    """

    contains_explicit_media = Flag(1 << 4)
    """
    :class:`bool`: Discord's scan flagged the attachment as explicit.
    """

    animated = Flag(1 << 5)
    """
    :class:`bool`: An animated image, so a preview will not show the motion.
    """

class EmbedFlags(Flags):
    """
    The flags of an embed.
    """

    __slots__ = []

    contains_explicit_media = Flag(1 << 4)
    """
    :class:`bool`: Discord's scan flagged the embedded media as explicit.
    """

    content_inventory_entry = Flag(1 << 5)
    """
    :class:`bool`: The embed shows an activity from a user's content inventory.
    """

__all__ = ["MessageFlags", "AttachmentFlags", "EmbedFlags"]