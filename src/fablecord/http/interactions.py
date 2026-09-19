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

class Interactions:
    """
    The interaction endpoints: answering an interaction, the original
    response, and the application commands, global and per guild.

    Follow-up messages are webhook messages to Discord, so they go
    through :class:`Webhooks` with the application ID as the webhook and
    the interaction token as its token. Discord limits the interaction
    routes the same way, which is why their parameters carry the
    webhook names.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered.

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

    RESPOND: Final = Route("POST", "/interactions/{webhook_id}/{webhook_token}/callback")
    ORIGINAL: Final = Route("GET", "/webhooks/{webhook_id}/{webhook_token}/messages/@original")
    EDIT_ORIGINAL: Final = Route("PATCH", "/webhooks/{webhook_id}/{webhook_token}/messages/@original")
    DELETE_ORIGINAL: Final = Route("DELETE", "/webhooks/{webhook_id}/{webhook_token}/messages/@original")
    GLOBAL_COMMANDS: Final = Route("GET", "/applications/{application_id}/commands")
    CREATE_GLOBAL_COMMAND: Final = Route("POST", "/applications/{application_id}/commands")
    SET_GLOBAL_COMMANDS: Final = Route("PUT", "/applications/{application_id}/commands")
    GLOBAL_COMMAND: Final = Route("GET", "/applications/{application_id}/commands/{command_id}")
    EDIT_GLOBAL_COMMAND: Final = Route("PATCH", "/applications/{application_id}/commands/{command_id}")
    DELETE_GLOBAL_COMMAND: Final = Route("DELETE", "/applications/{application_id}/commands/{command_id}")
    GUILD_COMMANDS: Final = Route("GET", "/applications/{application_id}/guilds/{guild_id}/commands")
    CREATE_GUILD_COMMAND: Final = Route("POST", "/applications/{application_id}/guilds/{guild_id}/commands")
    SET_GUILD_COMMANDS: Final = Route("PUT", "/applications/{application_id}/guilds/{guild_id}/commands")
    GUILD_COMMAND: Final = Route("GET", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}")
    EDIT_GUILD_COMMAND: Final = Route("PATCH", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}")
    DELETE_GUILD_COMMAND: Final = Route("DELETE", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}")
    GUILD_COMMAND_PERMISSIONS: Final = Route("GET", "/applications/{application_id}/guilds/{guild_id}/commands/permissions")
    COMMAND_PERMISSIONS: Final = Route("GET", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions")
    SET_COMMAND_PERMISSIONS: Final = Route("PUT", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def respond(
            self,
            interaction_id: int,
            token: str,
            /,
            *,
            type: int,
            data: dict[str, Any] = MISSING,
            files: Sequence[File] = MISSING,
            with_response: bool = MISSING
    ) -> Response[dict[str, Any] | None]:
        """
        Answers an interaction, which has to happen within three seconds
        of receiving it.

        Parameters
        -----------
        interaction_id: :class:`int`
            The interaction.
        token: :class:`str`
            Its token.
        type: :class:`int`
            The kind of answer: a message, a deferral, a modal, an
            autocomplete result or an update of the message.
        data: Dict[:class:`str`, Any]
            What the answer carries, a message payload for one.
        files: Sequence[:class:`File`]
            The files of a message answer. Each gets its entry in the
            ``attachments`` of ``data`` after the given ones.
        with_response: :class:`bool`
            Whether Discord answers with what the interaction resulted
            in, the message it created for one, instead of nothing.
        """
        if files:
            entries = [file.to_dict(index) for index, file in enumerate(files)]
            given: dict[str, Any] = {} if data is MISSING else data
            data = {**given, "attachments": [*given.get("attachments", []), *entries]}

        payload: dict[str, Any] = {"type": type}

        if data is not MISSING:
            payload["data"] = data

        return self.rest.request(self.RESPOND.compile(interaction_id, token), json=payload, files=files or None, params={"with_response": with_response or None})

    def original(self, application_id: int, token: str, /) -> Response[dict[str, Any]]:
        """
        Fetches the message an interaction was answered with.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        token: :class:`str`
            The interaction token.
        """
        return self.rest.request(self.ORIGINAL.compile(application_id, token))

    def edit_original(
            self,
            application_id: int,
            token: str,
            /,
            *,
            content: str | None = MISSING,
            embeds: Sequence[dict[str, Any]] | None = MISSING,
            allowed_mentions: dict[str, Any] | None = MISSING,
            components: Sequence[dict[str, Any]] | None = MISSING,
            attachments: Sequence[dict[str, Any]] = MISSING,
            files: Sequence[File] = MISSING,
            flags: int = MISSING,
            poll: dict[str, Any] = MISSING
    ) -> Response[dict[str, Any]]:
        """
        Edits the message an interaction was answered with, which is
        also how a deferred answer gets its content. Only what is given
        changes, ``None`` clears a field.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        token: :class:`str`
            The interaction token.
        content: Optional[:class:`str`]
            The new text.
        embeds: Optional[Sequence[Dict[:class:`str`, Any]]]
            The new embeds, all of them.
        allowed_mentions: Optional[Dict[:class:`str`, Any]]
            Which mentions in the content may ping.
        components: Optional[Sequence[Dict[:class:`str`, Any]]]
            The new components.
        attachments: Sequence[Dict[:class:`str`, Any]]
            The attachments to keep. Any not listed here is removed once
            this or ``files`` is given.
        files: Sequence[:class:`File`]
            The files to add.
        flags: :class:`int`
            The new message flags.
        poll: Dict[:class:`str`, Any]
            The poll to attach, which only works on a message that has
            none yet.
        """
        payload: dict[str, Any] = {}

        if content is not MISSING:
            payload["content"] = content

        if embeds is not MISSING:
            payload["embeds"] = embeds

        if allowed_mentions is not MISSING:
            payload["allowed_mentions"] = allowed_mentions

        if components is not MISSING:
            payload["components"] = components

        if flags is not MISSING:
            payload["flags"] = flags

        if poll is not MISSING:
            payload["poll"] = poll

        if files is not MISSING:
            entries = [file.to_dict(index) for index, file in enumerate(files)]
            payload["attachments"] = entries if attachments is MISSING else [*attachments, *entries]
        elif attachments is not MISSING:
            payload["attachments"] = attachments

        return self.rest.request(self.EDIT_ORIGINAL.compile(application_id, token), json=payload, files=files or None)

    def delete_original(self, application_id: int, token: str, /) -> Response[None]:
        """
        Deletes the message an interaction was answered with.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        token: :class:`str`
            The interaction token.
        """
        return self.rest.request(self.DELETE_ORIGINAL.compile(application_id, token))

    def global_commands(self, application_id: int, /, *, with_localizations: bool = MISSING) -> Response[list[dict[str, Any]]]:
        """
        Fetches the global commands of an application.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        with_localizations: :class:`bool`
            Whether every translation comes along instead of the one for
            the requesting locale.
        """
        return self.rest.request(self.GLOBAL_COMMANDS.compile(application_id), params={"with_localizations": with_localizations or None})

    def create_global_command(self, application_id: int, command: dict[str, Any], /) -> Response[dict[str, Any]]:
        """
        Creates a global command, or replaces the one with the same
        name and type.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        command: Dict[:class:`str`, Any]
            The command as Discord expects it.
        """
        return self.rest.request(self.CREATE_GLOBAL_COMMAND.compile(application_id), json=command)

    def set_global_commands(self, application_id: int, commands: Sequence[dict[str, Any]], /) -> Response[list[dict[str, Any]]]:
        """
        Replaces every global command of an application in one go.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        commands: Sequence[Dict[:class:`str`, Any]]
            The commands as Discord expects them, all of them.
        """
        return self.rest.request(self.SET_GLOBAL_COMMANDS.compile(application_id), json=commands)

    def global_command(self, application_id: int, command_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one global command.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        command_id: :class:`int`
            The command.
        """
        return self.rest.request(self.GLOBAL_COMMAND.compile(application_id, command_id))

    def edit_global_command(self, application_id: int, command_id: int, command: dict[str, Any], /) -> Response[dict[str, Any]]:
        """
        Edits a global command. Only the fields in the payload change.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        command_id: :class:`int`
            The command.
        command: Dict[:class:`str`, Any]
            The fields to change, as Discord expects them.
        """
        return self.rest.request(self.EDIT_GLOBAL_COMMAND.compile(application_id, command_id), json=command)

    def delete_global_command(self, application_id: int, command_id: int, /) -> Response[None]:
        """
        Deletes a global command.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        command_id: :class:`int`
            The command.
        """
        return self.rest.request(self.DELETE_GLOBAL_COMMAND.compile(application_id, command_id))

    def guild_commands(self, application_id: int, guild_id: int, /, *, with_localizations: bool = MISSING) -> Response[list[dict[str, Any]]]:
        """
        Fetches the commands of an application in a guild.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        with_localizations: :class:`bool`
            Whether every translation comes along instead of the one for
            the requesting locale.
        """
        return self.rest.request(self.GUILD_COMMANDS.compile(application_id, guild_id), params={"with_localizations": with_localizations or None})

    def create_guild_command(self, application_id: int, guild_id: int, command: dict[str, Any], /) -> Response[dict[str, Any]]:
        """
        Creates a command in a guild, or replaces the one with the same
        name and type.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        command: Dict[:class:`str`, Any]
            The command as Discord expects it.
        """
        return self.rest.request(self.CREATE_GUILD_COMMAND.compile(application_id, guild_id), json=command)

    def set_guild_commands(self, application_id: int, guild_id: int, commands: Sequence[dict[str, Any]], /) -> Response[list[dict[str, Any]]]:
        """
        Replaces every command of an application in a guild in one go.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        commands: Sequence[Dict[:class:`str`, Any]]
            The commands as Discord expects them, all of them.
        """
        return self.rest.request(self.SET_GUILD_COMMANDS.compile(application_id, guild_id), json=commands)

    def guild_command(self, application_id: int, guild_id: int, command_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one command of a guild.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        command_id: :class:`int`
            The command.
        """
        return self.rest.request(self.GUILD_COMMAND.compile(application_id, guild_id, command_id))

    def edit_guild_command(self, application_id: int, guild_id: int, command_id: int, command: dict[str, Any], /) -> Response[dict[str, Any]]:
        """
        Edits a command of a guild. Only the fields in the payload
        change.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        command_id: :class:`int`
            The command.
        command: Dict[:class:`str`, Any]
            The fields to change, as Discord expects them.
        """
        return self.rest.request(self.EDIT_GUILD_COMMAND.compile(application_id, guild_id, command_id), json=command)

    def delete_guild_command(self, application_id: int, guild_id: int, command_id: int, /) -> Response[None]:
        """
        Deletes a command of a guild.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        command_id: :class:`int`
            The command.
        """
        return self.rest.request(self.DELETE_GUILD_COMMAND.compile(application_id, guild_id, command_id))

    def guild_command_permissions(self, application_id: int, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the permission overwrites of every command in a guild.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.GUILD_COMMAND_PERMISSIONS.compile(application_id, guild_id))

    def command_permissions(self, application_id: int, guild_id: int, command_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the permission overwrites of one command in a guild.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        command_id: :class:`int`
            The command.
        """
        return self.rest.request(self.COMMAND_PERMISSIONS.compile(application_id, guild_id, command_id))

    def set_command_permissions(self, application_id: int, guild_id: int, command_id: int, permissions: Sequence[dict[str, Any]], /) -> Response[dict[str, Any]]:
        """
        Replaces the permission overwrites of a command in a guild.
        Discord only accepts this from a user's OAuth2 token with the
        ``applications.commands.permissions.update`` scope, not from the
        bot token.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        guild_id: :class:`int`
            The guild.
        command_id: :class:`int`
            The command.
        permissions: Sequence[Dict[:class:`str`, Any]]
            The overwrites, up to a hundred, each with ``id``, ``type``
            and ``permission``.
        """
        return self.rest.request(self.SET_COMMAND_PERMISSIONS.compile(application_id, guild_id, command_id), json={"permissions": permissions})

__all__ = ["Interactions"]