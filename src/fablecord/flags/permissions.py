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

class Permissions(Flags):
    """
    A set of Discord permissions.

    The names follow Discord's own, so ``view_channel`` is the permission
    Discord calls ``VIEW_CHANNEL``. ``administrator`` is not special here,
    the permission calculator in the guild models handles what it implies.
    What this class does know are the rules Discord applies after channel
    overwrites, see :meth:`apply_implicit_rules`.

    The category helpers such as :meth:`text` and :meth:`voice` return the
    permissions Discord groups under that heading in the client.
    """

    __slots__ = []

    create_instant_invite = Flag(1 << 0)
    """
    :class:`bool`: Create invites to the guild or a channel.
    """

    kick_members = Flag(1 << 1)
    """
    :class:`bool`: Kick members whose highest role is below the bot's own.
    """

    ban_members = Flag(1 << 2)
    """
    :class:`bool`: Ban and unban members, with the same role rule as kicking.
    """

    administrator = Flag(1 << 3)
    """
    :class:`bool`: Everything at once. Channel overwrites do not apply, and
    the guild's two factor requirement does.
    """

    manage_channels = Flag(1 << 4)
    """
    :class:`bool`: Create, edit, reorder and delete channels and threads.
    """

    manage_guild = Flag(1 << 5)
    """
    :class:`bool`: Change the guild's settings, and see its invites and
    integrations.
    """

    add_reactions = Flag(1 << 6)
    """
    :class:`bool`: Add a reaction nobody has added yet. Joining an existing
    reaction is always allowed.
    """

    view_audit_log = Flag(1 << 7)
    """
    :class:`bool`: Read the audit log. Also required for the audit log
    entry events to arrive.
    """

    priority_speaker = Flag(1 << 8)
    """
    :class:`bool`: Lower everyone else's volume while speaking.
    """

    stream = Flag(1 << 9)
    """
    :class:`bool`: Share the screen or go live in voice channels.
    """

    view_channel = Flag(1 << 10)
    """
    :class:`bool`: See the channel and read its messages. Without it no
    other permission in that channel applies.
    """

    send_messages = Flag(1 << 11)
    """
    :class:`bool`: Send messages and create forum posts. Without it
    ``embed_links``, ``attach_files``, ``mention_everyone`` and
    ``send_tts_messages`` are void.
    """

    send_tts_messages = Flag(1 << 12)
    """
    :class:`bool`: Send text to speech messages.
    """

    manage_messages = Flag(1 << 13)
    """
    :class:`bool`: Delete and pin messages of others, and remove reactions.
    """

    embed_links = Flag(1 << 14)
    """
    :class:`bool`: Let links unfurl into embeds. A bot also needs it to send
    embeds of its own.
    """

    attach_files = Flag(1 << 15)
    """
    :class:`bool`: Upload files.
    """

    read_message_history = Flag(1 << 16)
    """
    :class:`bool`: Read messages sent before joining, and fetch history
    over the API.
    """

    mention_everyone = Flag(1 << 17)
    """
    :class:`bool`: Ping everyone, here and every role, not only the ones
    marked as mentionable.
    """

    use_external_emojis = Flag(1 << 18)
    """
    :class:`bool`: Use emojis from other guilds, also in bot messages.
    """

    view_guild_insights = Flag(1 << 19)
    """
    :class:`bool`: See the guild's insights page.
    """

    connect = Flag(1 << 20)
    """
    :class:`bool`: Join voice channels. Without it the other voice
    permissions are void.
    """

    speak = Flag(1 << 21)
    """
    :class:`bool`: Speak in voice channels.
    """

    mute_members = Flag(1 << 22)
    """
    :class:`bool`: Server mute others in voice channels.
    """

    deafen_members = Flag(1 << 23)
    """
    :class:`bool`: Server deafen others in voice channels.
    """

    move_members = Flag(1 << 24)
    """
    :class:`bool`: Move others between voice channels, or disconnect them.
    """

    use_voice_activation = Flag(1 << 25)
    """
    :class:`bool`: Speak without push to talk.
    """

    change_nickname = Flag(1 << 26)
    """
    :class:`bool`: Change the own nickname.
    """

    manage_nicknames = Flag(1 << 27)
    """
    :class:`bool`: Change the nicknames of others.
    """

    manage_roles = Flag(1 << 28)
    """
    :class:`bool`: Create, edit and delete roles below the own highest one,
    and edit channel overwrites.
    """

    manage_webhooks = Flag(1 << 29)
    """
    :class:`bool`: Create, edit and delete webhooks.
    """

    manage_expressions = Flag(1 << 30)
    """
    :class:`bool`: Edit and delete emojis, stickers and soundboard sounds
    made by others.
    """

    use_application_commands = Flag(1 << 31)
    """
    :class:`bool`: Use slash commands, context menus and the other
    application commands.
    """

    request_to_speak = Flag(1 << 32)
    """
    :class:`bool`: Raise the hand in stage channels.
    """

    manage_events = Flag(1 << 33)
    """
    :class:`bool`: Edit and delete scheduled events made by others.
    """

    manage_threads = Flag(1 << 34)
    """
    :class:`bool`: Delete, archive and lock any thread, and see private ones.
    """

    create_public_threads = Flag(1 << 35)
    """
    :class:`bool`: Start public threads.
    """

    create_private_threads = Flag(1 << 36)
    """
    :class:`bool`: Start private threads.
    """

    use_external_stickers = Flag(1 << 37)
    """
    :class:`bool`: Use stickers from other guilds.
    """

    send_messages_in_threads = Flag(1 << 38)
    """
    :class:`bool`: Send messages in threads. Separate from ``send_messages``
    on purpose, one can be granted without the other.
    """

    use_embedded_activities = Flag(1 << 39)
    """
    :class:`bool`: Start activities in voice channels.
    """

    moderate_members = Flag(1 << 40)
    """
    :class:`bool`: Time members out.
    """

    view_creator_monetization_analytics = Flag(1 << 41)
    """
    :class:`bool`: See the analytics of role subscriptions.
    """

    use_soundboard = Flag(1 << 42)
    """
    :class:`bool`: Play soundboard sounds in voice channels.
    """

    create_expressions = Flag(1 << 43)
    """
    :class:`bool`: Add emojis, stickers and soundboard sounds, and edit and
    delete the own ones.
    """

    create_events = Flag(1 << 44)
    """
    :class:`bool`: Create scheduled events, and edit and delete the own ones.
    """

    use_external_sounds = Flag(1 << 45)
    """
    :class:`bool`: Play soundboard sounds from other guilds.
    """

    send_voice_messages = Flag(1 << 46)
    """
    :class:`bool`: Send voice messages.
    """

    set_voice_channel_status = Flag(1 << 48)
    """
    :class:`bool`: Set the status text of a voice channel.
    """

    send_polls = Flag(1 << 49)
    """
    :class:`bool`: Create polls.
    """

    use_external_apps = Flag(1 << 50)
    """
    :class:`bool`: Use user installed apps in the guild with responses that
    everyone can see.
    """

    pin_messages = Flag(1 << 51)
    """
    :class:`bool`: Pin and unpin messages without needing ``manage_messages``.
    """

    bypass_slowmode = Flag(1 << 52)
    """
    :class:`bool`: Ignore slowmode in channels that have one.
    """

    _general: ClassVar[int] = (
        manage_channels.bit
        | manage_guild.bit
        | view_audit_log.bit
        | view_channel.bit
        | view_guild_insights.bit
        | manage_roles.bit
        | manage_webhooks.bit
        | manage_expressions.bit
        | view_creator_monetization_analytics.bit
        | create_expressions.bit
    )

    _membership: ClassVar[int] = (
        create_instant_invite.bit
        | kick_members.bit
        | ban_members.bit
        | change_nickname.bit
        | manage_nicknames.bit
        | moderate_members.bit
    )

    _text: ClassVar[int] = (
        add_reactions.bit
        | send_messages.bit
        | send_tts_messages.bit
        | manage_messages.bit
        | embed_links.bit
        | attach_files.bit
        | read_message_history.bit
        | mention_everyone.bit
        | use_external_emojis.bit
        | use_application_commands.bit
        | manage_threads.bit
        | create_public_threads.bit
        | create_private_threads.bit
        | use_external_stickers.bit
        | send_messages_in_threads.bit
        | send_voice_messages.bit
        | send_polls.bit
        | use_external_apps.bit
        | pin_messages.bit
        | bypass_slowmode.bit
    )

    _voice: ClassVar[int] = (
        priority_speaker.bit
        | stream.bit
        | connect.bit
        | speak.bit
        | mute_members.bit
        | deafen_members.bit
        | move_members.bit
        | use_voice_activation.bit
        | use_embedded_activities.bit
        | use_soundboard.bit
        | use_external_sounds.bit
        | set_voice_channel_status.bit
    )

    _stage: ClassVar[int] = request_to_speak.bit

    _stage_moderator: ClassVar[int] = manage_channels.bit | mute_members.bit | move_members.bit

    _events: ClassVar[int] = manage_events.bit | create_events.bit

    _elevated: ClassVar[int] = (
        kick_members.bit
        | ban_members.bit
        | administrator.bit
        | manage_channels.bit
        | manage_guild.bit
        | manage_messages.bit
        | manage_roles.bit
        | manage_webhooks.bit
        | manage_expressions.bit
        | manage_threads.bit
        | moderate_members.bit
    )

    _guild_only: ClassVar[int] = (
        kick_members.bit
        | ban_members.bit
        | administrator.bit
        | manage_guild.bit
        | view_audit_log.bit
        | view_guild_insights.bit
        | change_nickname.bit
        | manage_nicknames.bit
        | manage_expressions.bit
        | manage_events.bit
        | moderate_members.bit
        | view_creator_monetization_analytics.bit
        | create_expressions.bit
        | create_events.bit
    )

    _needs_send_messages: ClassVar[int] = (
        send_tts_messages.bit
        | embed_links.bit
        | attach_files.bit
        | mention_everyone.bit
    )

    def handle_overwrite(self, allow: int, deny: int, /) -> None:
        """
        Applies a channel overwrite to these permissions.

        Denied bits are cleared first, then allowed bits are set, which is
        the order Discord itself uses.

        Parameters
        -----------
        allow: :class:`int`
            The raw value of the allowed permissions.
        deny: :class:`int`
            The raw value of the denied permissions.
        """
        self.value = (self.value & ~deny) | allow

    def apply_implicit_rules(self) -> None:
        """
        Applies the rules Discord applies after the overwrites.

        Without ``view_channel`` nothing else in the channel counts, only
        the guild wide permissions survive. Without ``send_messages`` the
        permissions that only matter for sending are void, and without
        ``connect`` the same goes for everything voice related. The
        permission calculator runs this as its last step, so a bot never
        believes it can embed links in a channel it cannot even see.
        """
        if not self.view_channel:
            self.value &= self._guild_only

            return

        if not self.send_messages:
            self.value &= ~self._needs_send_messages

        if not self.connect:
            self.value &= ~self._voice

    @classmethod
    def all_channel(cls) -> Self:
        """
        Every permission that can be set on a channel.

        Guild wide ones such as ``kick_members`` or ``manage_guild`` are
        left out.
        """
        return cls.from_value(cls._all & ~cls._guild_only)

    @classmethod
    def general(cls) -> Self:
        """
        The permissions Discord lists under general server permissions.
        """
        return cls.from_value(cls._general)

    @classmethod
    def membership(cls) -> Self:
        """
        The permissions Discord lists under membership permissions.
        """
        return cls.from_value(cls._membership)

    @classmethod
    def text(cls) -> Self:
        """
        The permissions Discord lists under text channel permissions.
        """
        return cls.from_value(cls._text)

    @classmethod
    def voice(cls) -> Self:
        """
        The permissions Discord lists under voice channel permissions.
        """
        return cls.from_value(cls._voice)

    @classmethod
    def stage(cls) -> Self:
        """
        The permissions Discord lists under stage channel permissions.
        """
        return cls.from_value(cls._stage)

    @classmethod
    def stage_moderator(cls) -> Self:
        """
        The permissions a stage moderator needs.
        """
        return cls.from_value(cls._stage_moderator)

    @classmethod
    def events(cls) -> Self:
        """
        The permissions Discord lists under events permissions.
        """
        return cls.from_value(cls._events)

    @classmethod
    def elevated(cls) -> Self:
        """
        The permissions Discord asks for two factor authentication for.
        """
        return cls.from_value(cls._elevated)

    @classmethod
    def advanced(cls) -> Self:
        """
        The permissions Discord lists under advanced permissions.

        That is only ``administrator``.
        """
        return cls.from_value(cls.administrator.bit)

__all__ = ["Permissions"]