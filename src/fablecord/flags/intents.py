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

class Intents(Flags):
    """
    The gateway intents a bot subscribes to.

    Discord only sends the events an intent covers, so this is the first
    knob for keeping traffic down. ``members``, ``presences`` and
    ``message_content`` are privileged: they have to be switched on in the
    developer portal as well, and if they are not, the gateway closes the
    connection with code 4014 right after identifying.

    Combined flags such as ``messages`` stand for the guild and the direct
    message variant at once. They read as ``True`` only when both are set.
    """

    __slots__ = []

    guilds = Flag(1 << 0)
    """
    :class:`bool`: Guild, channel, thread, role and stage instance events.
    Without it the guild cache stays empty and most of the library has
    nothing to work with, so leave it on unless the bot only answers
    interactions.
    """

    members = Flag(1 << 1)
    """
    :class:`bool`: Member join, update and leave events, and the member
    lists that arrive with a guild on startup. Privileged.
    """

    moderation = Flag(1 << 2)
    """
    :class:`bool`: Ban and unban events and new audit log entries.
    """

    expressions = Flag(1 << 3)
    """
    :class:`bool`: Changes to a guild's emojis, stickers and soundboard.
    """

    integrations = Flag(1 << 4)
    """
    :class:`bool`: Integration changes and the guild wide integrations update.
    """

    webhooks = Flag(1 << 5)
    """
    :class:`bool`: The webhooks update event. It only says that a channel's
    webhooks changed, not how, so a fetch has to follow.
    """

    invites = Flag(1 << 6)
    """
    :class:`bool`: Invite creation and deletion. Discord only sends these
    when the bot may manage the guild or the channel in question.
    """

    voice_states = Flag(1 << 7)
    """
    :class:`bool`: Voice state updates. Required to know who sits in a voice
    channel and to connect to one yourself.
    """

    presences = Flag(1 << 8)
    """
    :class:`bool`: Status and activity changes of members. Privileged, and
    by far the noisiest intent on large guilds.
    """

    guild_messages = Flag(1 << 9)
    """
    :class:`bool`: Message create, update, delete and bulk delete in guilds.
    The content stays empty unless ``message_content`` is on or the bot is
    mentioned in the message.
    """

    guild_reactions = Flag(1 << 10)
    """
    :class:`bool`: Reactions being added, removed or cleared in guilds.
    """

    guild_typing = Flag(1 << 11)
    """
    :class:`bool`: Typing indicators in guilds. Rarely worth the traffic.
    """

    dm_messages = Flag(1 << 12)
    """
    :class:`bool`: Message events in direct messages. The content is always
    included there, direct messages do not need ``message_content``.
    """

    dm_reactions = Flag(1 << 13)
    """
    :class:`bool`: Reactions being added, removed or cleared in direct messages.
    """

    dm_typing = Flag(1 << 14)
    """
    :class:`bool`: Typing indicators in direct messages.
    """

    message_content = Flag(1 << 15)
    """
    :class:`bool`: The content, embeds, attachments and components of guild
    messages that do not mention the bot. Privileged. Without it a prefix
    command bot only ever sees empty strings.
    """

    guild_scheduled_events = Flag(1 << 16)
    """
    :class:`bool`: Scheduled events being created, changed or deleted, and
    users subscribing to them.
    """

    auto_moderation_configuration = Flag(1 << 20)
    """
    :class:`bool`: Auto moderation rules being created, changed or deleted.
    """

    auto_moderation_execution = Flag(1 << 21)
    """
    :class:`bool`: Auto moderation taking action on a message or member.
    """

    guild_polls = Flag(1 << 24)
    """
    :class:`bool`: Votes being added or removed on polls in guilds.
    """

    dm_polls = Flag(1 << 25)
    """
    :class:`bool`: Votes being added or removed on polls in direct messages.
    """

    messages = Flag(guild_messages.bit | dm_messages.bit)
    """
    :class:`bool`: Message events in guilds and direct messages.
    """

    reactions = Flag(guild_reactions.bit | dm_reactions.bit)
    """
    :class:`bool`: Reaction events in guilds and direct messages.
    """

    typing = Flag(guild_typing.bit | dm_typing.bit)
    """
    :class:`bool`: Typing indicators in guilds and direct messages.
    """

    auto_moderation = Flag(auto_moderation_configuration.bit | auto_moderation_execution.bit)
    """
    :class:`bool`: Auto moderation rule changes and actions.
    """

    polls = Flag(guild_polls.bit | dm_polls.bit)
    """
    :class:`bool`: Poll votes in guilds and direct messages.
    """

    _privileged: ClassVar[int] = members.bit | presences.bit | message_content.bit

    @property
    def has_privileged(self) -> bool:
        """
        :class:`bool`: Whether any privileged intent is enabled.

        The client checks this on startup, because a privileged intent
        without approval in the developer portal makes the gateway close
        the connection with code 4014.
        """
        return bool(self.value & self._privileged)

    @classmethod
    def default(cls) -> Self:
        """
        Everything except the privileged intents.

        This is what a bot can use without touching the developer portal.
        """
        return cls.from_value(cls._all & ~cls._privileged)

    @classmethod
    def privileged(cls) -> Self:
        """
        The intents Discord gates behind the developer portal.
        """
        return cls.from_value(cls._privileged)

__all__ = ["Intents"]