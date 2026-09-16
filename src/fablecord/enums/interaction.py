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

class InteractionType(Enum):
    """
    What kind of interaction Discord sent.

    Everything but ``ping`` has to be answered within three seconds,
    :class:`InteractionResponseType` lists the ways to do that.
    """

    ping = 1
    """
    Discord checking that an interaction endpoint is alive. Only arrives
    over HTTP, the gateway never delivers it.
    """

    application_command = 2
    """
    A slash command or a context menu command was used.
    """

    component = 3
    """
    A button was pressed or a select menu was used.
    """

    autocomplete = 4
    """
    The user is typing into an option with autocomplete. Only choices
    can go back, the user sees nothing else.
    """

    modal_submit = 5
    """
    A modal was submitted.
    """

    can_be_deferred = Category.excluding(ping, autocomplete)
    """
    :class:`bool`: Whether the interaction may be answered with a loading
    state first. Pings and autocomplete want their real answer right away.
    """

class InteractionResponseType(Enum):
    """
    How an interaction gets answered.

    Not every response fits every interaction, a ping only takes
    ``pong`` and an autocomplete only takes ``autocomplete_result``.
    The rest go with commands, components and modals within the limits
    noted on each member.
    """

    pong = 1
    """
    The only answer to a ping.
    """

    channel_message = 4
    """
    Send a message right away.
    """

    deferred_channel_message = 5
    """
    Show a loading state now and send the message later through a
    follow-up.
    """

    deferred_message_update = 6
    """
    Acknowledge a component interaction without any visible change.
    The message can still be edited later through a follow-up.
    """

    message_update = 7
    """
    Edit the message the component sits on.
    """

    autocomplete_result = 8
    """
    Offer up to 25 choices for the option being typed.
    """

    modal = 9
    """
    Open a modal. Not available as the answer to a modal submission.
    """

    launch_activity = 12
    """
    Launch the activity of the application. Only applications with an
    activity enabled can use it.
    """

    is_deferred = Category(deferred_channel_message, deferred_message_update)
    """
    :class:`bool`: Whether the response only buys time. The real answer
    has to follow within fifteen minutes through a follow-up.
    """

    edits_message = Category(deferred_message_update, message_update)
    """
    :class:`bool`: Whether the response acts on the message a component
    sits on. Commands have no such message, so only component
    interactions and modals opened from one can use it.
    """

class InteractionContextType(Enum):
    """
    Where an interaction can be used.

    A command lists the contexts it allows, and every interaction
    carries the one it came from.
    """

    guild = 0
    """
    In a guild.
    """

    bot_dm = 1
    """
    In the direct message with the bot.
    """

    private_channel = 2
    """
    In direct messages and group chats the bot is not part of. Only
    user installed applications get here.
    """

class AppInstallationType(Enum):
    """
    Where an application is installed.

    An application can support both, and a command can be limited to
    one of them.
    """

    guild = 0
    """
    Installed to a guild. The bot joins the guild and receives its
    events.
    """

    user = 1
    """
    Installed to a user account. The commands follow the user into
    every guild and direct message, nothing else does.
    """

class AppCommandType(Enum):
    """
    How an application command is invoked.

    Only ``chat_input`` commands take options and a description, the
    context menu ones show up on a right click.
    """

    chat_input = 1
    """
    A slash command.
    """

    user = 2
    """
    An entry in the context menu of a user.
    """

    message = 3
    """
    An entry in the context menu of a message.
    """

    primary_entry_point = 4
    """
    The command that launches the activity of the application. There
    is at most one, Discord creates it once activities are enabled.
    """

    is_context_menu = Category(user, message)
    """
    :class:`bool`: Whether the command sits in a right click menu. Those
    take neither options nor a description, and their name may contain
    spaces and capitals.
    """

class AppCommandOptionType(Enum):
    """
    The type of an application command option.

    The type decides what the user can enter and in which form the
    value arrives, the categories cover the differences that matter
    when reading an interaction.
    """

    subcommand = 1
    """
    A subcommand. It carries options of its own instead of a value.
    """

    subcommand_group = 2
    """
    A group of subcommands. Groups cannot nest any further.
    """

    string = 3
    """
    Text, up to 6000 characters.
    """

    integer = 4
    """
    A whole number between -2^53 and 2^53.
    """

    boolean = 5
    """
    ``True`` or ``False``.
    """

    user = 6
    """
    A user, resolved to a member when used in a guild.
    """

    channel = 7
    """
    A channel of the guild, optionally limited to certain channel types.
    """

    role = 8
    """
    A role of the guild.
    """

    mentionable = 9
    """
    A user or a role.
    """

    number = 10
    """
    A floating point number between -2^53 and 2^53.
    """

    attachment = 11
    """
    An uploaded file.
    """

    is_nested = Category(subcommand, subcommand_group)
    """
    :class:`bool`: Whether the option holds further options instead of a
    value.
    """

    allows_choices = Category(string, integer, number)
    """
    :class:`bool`: Whether the option can offer fixed choices or
    autocomplete. Only text and numbers can.
    """

    is_resolved = Category(user, channel, role, mentionable, attachment)
    """
    :class:`bool`: Whether the value arrives as an ID that has to be
    looked up in the resolved data of the interaction.
    """

class AppCommandPermissionType(Enum):
    """
    What a command permission override applies to.

    Overrides are set by guild admins in the client, a bot can only
    read them.
    """

    role = 1
    """
    A role. The ID of the guild itself stands for the everyone role.
    """

    user = 2
    """
    A single user.
    """

    channel = 3
    """
    A channel. The ID of the guild minus one stands for all channels.
    """

class EntryPointHandlerType(Enum):
    """
    Who handles the primary entry point command.
    """

    app_handler = 1
    """
    The application receives the interaction and answers it itself.
    """

    discord_launch_activity = 2
    """
    Discord launches the activity and posts a message on its own, the
    application never sees the interaction.
    """

__all__ = [
    "InteractionType",
    "InteractionResponseType",
    "InteractionContextType",
    "AppInstallationType",
    "AppCommandType",
    "AppCommandOptionType",
    "AppCommandPermissionType",
    "EntryPointHandlerType"
]