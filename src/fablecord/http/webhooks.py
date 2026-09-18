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

class Webhooks:
    """
    The webhook endpoints: creating and managing webhooks, and sending,
    editing and deleting messages through one with its token.

    Discord limits the token routes per webhook and token, which is
    also how it treats interaction follow-ups, so those go through the
    same methods with the application ID and the interaction token.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered. Only the fields given end up in a payload.

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

    CREATE: Final = Route("POST", "/channels/{channel_id}/webhooks")
    OF_CHANNEL: Final = Route("GET", "/channels/{channel_id}/webhooks")
    OF_GUILD: Final = Route("GET", "/guilds/{guild_id}/webhooks")
    GET: Final = Route("GET", "/webhooks/{webhook_id}")
    GET_WITH_TOKEN: Final = Route("GET", "/webhooks/{webhook_id}/{webhook_token}")
    EDIT: Final = Route("PATCH", "/webhooks/{webhook_id}")
    EDIT_WITH_TOKEN: Final = Route("PATCH", "/webhooks/{webhook_id}/{webhook_token}")
    DELETE: Final = Route("DELETE", "/webhooks/{webhook_id}")
    DELETE_WITH_TOKEN: Final = Route("DELETE", "/webhooks/{webhook_id}/{webhook_token}")
    EXECUTE: Final = Route("POST", "/webhooks/{webhook_id}/{webhook_token}")
    MESSAGE: Final = Route("GET", "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
    EDIT_MESSAGE: Final = Route("PATCH", "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
    DELETE_MESSAGE: Final = Route("DELETE", "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def create(self, channel_id: int, /, *, name: str, avatar: str | None = MISSING, reason: str | None = None) -> Response[dict[str, Any]]:
        """
        Creates a webhook in a channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        name: :class:`str`
            The name, 1 to 80 characters and not ``clyde`` or ``discord``.
        avatar: Optional[:class:`str`]
            The avatar as a data URI.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {"name": name}

        if avatar is not MISSING:
            payload["avatar"] = avatar

        return self.rest.request(self.CREATE.compile(channel_id), json=payload, reason=reason)

    def of_channel(self, channel_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the webhooks of a channel.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        """
        return self.rest.request(self.OF_CHANNEL.compile(channel_id))

    def of_guild(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the webhooks of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.OF_GUILD.compile(guild_id))

    def get(self, webhook_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches a webhook, which takes the permission to manage webhooks
        in its guild.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook.
        """
        return self.rest.request(self.GET.compile(webhook_id))

    def get_with_token(self, webhook_id: int, token: str, /) -> Response[dict[str, Any]]:
        """
        Fetches a webhook by its token, which takes no permission and
        leaves the user who created it out of the payload.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook.
        token: :class:`str`
            Its token.
        """
        return self.rest.request(self.GET_WITH_TOKEN.compile(webhook_id, token))

    def edit(
            self,
            webhook_id: int,
            /,
            *,
            name: str = MISSING,
            avatar: str | None = MISSING,
            channel_id: int = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a webhook. Only what is given changes.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook.
        name: :class:`str`
            The new name.
        avatar: Optional[:class:`str`]
            The avatar as a data URI, ``None`` to remove it.
        channel_id: :class:`int`
            The channel to move the webhook to.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if avatar is not MISSING:
            payload["avatar"] = avatar

        if channel_id is not MISSING:
            payload["channel_id"] = channel_id

        return self.rest.request(self.EDIT.compile(webhook_id), json=payload, reason=reason)

    def edit_with_token(self, webhook_id: int, token: str, /, *, name: str = MISSING, avatar: str | None = MISSING) -> Response[dict[str, Any]]:
        """
        Edits a webhook by its token, which cannot move it.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook.
        token: :class:`str`
            Its token.
        name: :class:`str`
            The new name.
        avatar: Optional[:class:`str`]
            The avatar as a data URI, ``None`` to remove it.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if avatar is not MISSING:
            payload["avatar"] = avatar

        return self.rest.request(self.EDIT_WITH_TOKEN.compile(webhook_id, token), json=payload)

    def delete(self, webhook_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes a webhook.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(webhook_id), reason=reason)

    def delete_with_token(self, webhook_id: int, token: str, /) -> Response[None]:
        """
        Deletes a webhook by its token.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook.
        token: :class:`str`
            Its token.
        """
        return self.rest.request(self.DELETE_WITH_TOKEN.compile(webhook_id, token))

    def execute(
            self,
            webhook_id: int,
            token: str,
            /,
            *,
            content: str = MISSING,
            username: str = MISSING,
            avatar_url: str = MISSING,
            tts: bool = MISSING,
            embeds: Sequence[dict[str, Any]] = MISSING,
            allowed_mentions: dict[str, Any] = MISSING,
            components: Sequence[dict[str, Any]] = MISSING,
            attachments: Sequence[dict[str, Any]] = MISSING,
            files: Sequence[File] = MISSING,
            flags: int = MISSING,
            thread_name: str = MISSING,
            applied_tags: Sequence[int] = MISSING,
            poll: dict[str, Any] = MISSING,
            wait: bool = MISSING,
            thread_id: int | None = None,
            with_components: bool = MISSING
    ) -> Response[dict[str, Any] | None]:
        """
        Sends a message through a webhook. Discord answers with nothing
        unless ``wait`` is set, then with the message.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook, or the application for an interaction follow-up.
        token: :class:`str`
            The webhook token, or the interaction token.
        content: :class:`str`
            The text, up to 2000 characters.
        username: :class:`str`
            The name to show instead of the webhook's.
        avatar_url: :class:`str`
            The avatar to show instead of the webhook's.
        tts: :class:`bool`
            Whether the message is read out.
        embeds: Sequence[Dict[:class:`str`, Any]]
            Up to ten embeds as Discord expects them.
        allowed_mentions: Dict[:class:`str`, Any]
            Which mentions in the content may ping.
        components: Sequence[Dict[:class:`str`, Any]]
            The components under the message.
        attachments: Sequence[Dict[:class:`str`, Any]]
            Attachment entries that are not files of this request.
        files: Sequence[:class:`File`]
            The files to upload. Each gets its entry in ``attachments``
            after the given ones.
        flags: :class:`int`
            The message flags.
        thread_name: :class:`str`
            The name of the forum post to start with this message.
        applied_tags: Sequence[:class:`int`]
            The tags of that forum post.
        poll: Dict[:class:`str`, Any]
            The poll to attach.
        wait: :class:`bool`
            Whether to wait for the message and get it back, and to hear
            about an error instead of a silent drop.
        thread_id: Optional[:class:`int`]
            The thread of the webhook's channel to send to.
        with_components: :class:`bool`
            Whether the components are the new layout kind, which
            webhooks otherwise leave out.
        """
        payload = self._payload(content, embeds, allowed_mentions, components, attachments, files, flags, poll)

        if username is not MISSING:
            payload["username"] = username

        if avatar_url is not MISSING:
            payload["avatar_url"] = avatar_url

        if tts is not MISSING:
            payload["tts"] = tts

        if thread_name is not MISSING:
            payload["thread_name"] = thread_name

        if applied_tags is not MISSING:
            payload["applied_tags"] = applied_tags

        params = {"wait": wait or None, "thread_id": thread_id, "with_components": with_components or None}

        return self.rest.request(self.EXECUTE.compile(webhook_id, token), json=payload, files=files or None, params=params)

    def message(self, webhook_id: int, token: str, message_id: int, /, *, thread_id: int | None = None) -> Response[dict[str, Any]]:
        """
        Fetches a message the webhook sent.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook, or the application for an interaction.
        token: :class:`str`
            The webhook token, or the interaction token.
        message_id: :class:`int`
            The message.
        thread_id: Optional[:class:`int`]
            The thread the message is in.
        """
        return self.rest.request(self.MESSAGE.compile(webhook_id, token, message_id), params={"thread_id": thread_id})

    def edit_message(
            self,
            webhook_id: int,
            token: str,
            message_id: int,
            /,
            *,
            content: str | None = MISSING,
            embeds: Sequence[dict[str, Any]] | None = MISSING,
            allowed_mentions: dict[str, Any] | None = MISSING,
            components: Sequence[dict[str, Any]] | None = MISSING,
            attachments: Sequence[dict[str, Any]] = MISSING,
            files: Sequence[File] = MISSING,
            flags: int = MISSING,
            poll: dict[str, Any] = MISSING,
            thread_id: int | None = None,
            with_components: bool = MISSING
    ) -> Response[dict[str, Any]]:
        """
        Edits a message the webhook sent. Only what is given changes,
        ``None`` clears a field.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook, or the application for an interaction.
        token: :class:`str`
            The webhook token, or the interaction token.
        message_id: :class:`int`
            The message.
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
        thread_id: Optional[:class:`int`]
            The thread the message is in.
        with_components: :class:`bool`
            Whether the components are the new layout kind.
        """
        payload = self._payload(content, embeds, allowed_mentions, components, attachments, files, flags, poll)
        params = {"thread_id": thread_id, "with_components": with_components or None}

        return self.rest.request(self.EDIT_MESSAGE.compile(webhook_id, token, message_id), json=payload, files=files or None, params=params)

    def delete_message(self, webhook_id: int, token: str, message_id: int, /, *, thread_id: int | None = None) -> Response[None]:
        """
        Deletes a message the webhook sent.

        Parameters
        -----------
        webhook_id: :class:`int`
            The webhook, or the application for an interaction.
        token: :class:`str`
            The webhook token, or the interaction token.
        message_id: :class:`int`
            The message.
        thread_id: Optional[:class:`int`]
            The thread the message is in.
        """
        return self.rest.request(self.DELETE_MESSAGE.compile(webhook_id, token, message_id), params={"thread_id": thread_id})

    @staticmethod
    def _payload(
            content: str | None,
            embeds: Sequence[dict[str, Any]] | None,
            allowed_mentions: dict[str, Any] | None,
            components: Sequence[dict[str, Any]] | None,
            attachments: Sequence[dict[str, Any]],
            files: Sequence[File],
            flags: int,
            poll: dict[str, Any],
            /
    ) -> dict[str, Any]:
        """
        The part of a webhook message payload that sending and editing
        share. Files get their ``attachments`` entries here, numbered
        the way :meth:`RESTClient.request` names their multipart parts.
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

        return payload

__all__ = ["Webhooks"]