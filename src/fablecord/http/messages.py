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
from ..utils.snowflake import Snowflake
from collections.abc import Sequence
from ..utils.missing import MISSING
from .route import Route
from time import time

if TYPE_CHECKING:
    from .client import RESTClient, Response
    from ..file import File

_TWO_WEEKS: Final = 14 * 86400

class Messages:
    """
    The endpoints under a channel's messages: sending, editing and
    deleting them, reactions, pins, polls and the typing indicator.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered, not a model. Snowflakes go in as integers, an
    emoji as the string Discord wants in a URL, the character itself
    or ``name:id`` for a custom one.

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

    GET: Final = Route("GET", "/channels/{channel_id}/messages/{message_id}")
    HISTORY: Final = Route("GET", "/channels/{channel_id}/messages")
    SEND: Final = Route("POST", "/channels/{channel_id}/messages")
    EDIT: Final = Route("PATCH", "/channels/{channel_id}/messages/{message_id}")
    DELETE: Final = Route("DELETE", "/channels/{channel_id}/messages/{message_id}")
    DELETE_FRESH: Final = Route("DELETE", "/channels/{channel_id}/messages/{message_id}", variant="under ten seconds")
    DELETE_OLD: Final = Route("DELETE", "/channels/{channel_id}/messages/{message_id}", variant="older than two weeks")
    BULK_DELETE: Final = Route("POST", "/channels/{channel_id}/messages/bulk-delete")
    CROSSPOST: Final = Route("POST", "/channels/{channel_id}/messages/{message_id}/crosspost")
    REACT: Final = Route("PUT", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
    UNREACT: Final = Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
    REMOVE_REACTION: Final = Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}")
    REACTIONS: Final = Route("GET", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")
    CLEAR_REACTIONS: Final = Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions")
    CLEAR_REACTION: Final = Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")
    PINS: Final = Route("GET", "/channels/{channel_id}/messages/pins")
    PIN: Final = Route("PUT", "/channels/{channel_id}/messages/pins/{message_id}")
    UNPIN: Final = Route("DELETE", "/channels/{channel_id}/messages/pins/{message_id}")
    TYPING: Final = Route("POST", "/channels/{channel_id}/typing")
    POLL_VOTERS: Final = Route("GET", "/channels/{channel_id}/polls/{message_id}/answers/{answer_id}")
    END_POLL: Final = Route("POST", "/channels/{channel_id}/polls/{message_id}/expire")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def get(self, channel_id: int, message_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        """
        return self.rest.request(self.GET.compile(channel_id, message_id))

    def history(
            self,
            channel_id: int,
            /,
            *,
            limit: int = 50,
            before: int | None = None,
            after: int | None = None,
            around: int | None = None
    ) -> Response[list[dict[str, Any]]]:
        """
        Fetches up to a hundred messages of a channel, newest first.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        limit: :class:`int`
            How many messages at most, 1 to 100.
        before: Optional[:class:`int`]
            Only messages older than this message.
        after: Optional[:class:`int`]
            Only messages newer than this message.
        around: Optional[:class:`int`]
            Messages on both sides of this message.
        """
        return self.rest.request(self.HISTORY.compile(channel_id), params={"limit": limit, "before": before, "after": after, "around": around})

    def send(
            self,
            channel_id: int,
            /,
            *,
            content: str | None = MISSING,
            tts: bool = MISSING,
            embeds: Sequence[dict[str, Any]] = MISSING,
            allowed_mentions: dict[str, Any] = MISSING,
            message_reference: dict[str, Any] = MISSING,
            components: Sequence[dict[str, Any]] = MISSING,
            sticker_ids: Sequence[int] = MISSING,
            attachments: Sequence[dict[str, Any]] = MISSING,
            files: Sequence[File] = MISSING,
            flags: int = MISSING,
            nonce: int | str = MISSING,
            enforce_nonce: bool = MISSING,
            poll: dict[str, Any] = MISSING
    ) -> Response[dict[str, Any]]:
        """
        Sends a message. Only what is given ends up in the payload.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel to send to.
        content: Optional[:class:`str`]
            The text, up to 2000 characters.
        tts: :class:`bool`
            Whether the message is read out.
        embeds: Sequence[Dict[:class:`str`, Any]]
            Up to ten embeds as Discord expects them.
        allowed_mentions: Dict[:class:`str`, Any]
            Which mentions in the content may ping.
        message_reference: Dict[:class:`str`, Any]
            The message this one replies to or forwards.
        components: Sequence[Dict[:class:`str`, Any]]
            The components under the message.
        sticker_ids: Sequence[:class:`int`]
            Up to three stickers.
        attachments: Sequence[Dict[:class:`str`, Any]]
            Attachment entries that are not files of this request, kept
            attachments when a message is forwarded for one.
        files: Sequence[:class:`File`]
            The files to upload. Each gets its entry in ``attachments``
            after the given ones.
        flags: :class:`int`
            The message flags, ``SUPPRESS_EMBEDS`` or ``SUPPRESS_NOTIFICATIONS``
            among them.
        nonce: Union[:class:`int`, :class:`str`]
            A value Discord echoes in the message create event, to match
            the event to this request.
        enforce_nonce: :class:`bool`
            Whether Discord returns the existing message instead of
            creating another when the nonce was used recently.
        poll: Dict[:class:`str`, Any]
            The poll to attach.
        """
        payload = self._payload(content, embeds, allowed_mentions, components, attachments, files, flags)

        if tts is not MISSING:
            payload["tts"] = tts

        if message_reference is not MISSING:
            payload["message_reference"] = message_reference

        if sticker_ids is not MISSING:
            payload["sticker_ids"] = sticker_ids

        if nonce is not MISSING:
            payload["nonce"] = nonce

        if enforce_nonce is not MISSING:
            payload["enforce_nonce"] = enforce_nonce

        if poll is not MISSING:
            payload["poll"] = poll

        return self.rest.request(self.SEND.compile(channel_id), json=payload, files=files or None)

    def edit(
            self,
            channel_id: int,
            message_id: int,
            /,
            *,
            content: str | None = MISSING,
            embeds: Sequence[dict[str, Any]] | None = MISSING,
            allowed_mentions: dict[str, Any] | None = MISSING,
            components: Sequence[dict[str, Any]] | None = MISSING,
            attachments: Sequence[dict[str, Any]] = MISSING,
            files: Sequence[File] = MISSING,
            flags: int = MISSING
    ) -> Response[dict[str, Any]]:
        """
        Edits a message. Only what is given changes, ``None`` clears a
        field.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
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
        """
        payload = self._payload(content, embeds, allowed_mentions, components, attachments, files, flags)

        return self.rest.request(self.EDIT.compile(channel_id, message_id), json=payload, files=files or None)

    def delete(self, channel_id: int, message_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes a message.

        Discord limits deleting a message under ten seconds old and one
        older than two weeks apart from the rest, so the route carries a
        variant for each and the rate limiter keeps three buckets.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        age = time() - ((message_id >> 22) + Snowflake.EPOCH) / 1000

        if age < 10:
            route = self.DELETE_FRESH
        elif age < _TWO_WEEKS:
            route = self.DELETE
        else:
            route = self.DELETE_OLD

        return self.rest.request(route.compile(channel_id, message_id), reason=reason)

    def bulk_delete(self, channel_id: int, message_ids: Sequence[int], /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes two to a hundred messages at once, none of them older
        than two weeks.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the messages are in.
        message_ids: Sequence[:class:`int`]
            The messages.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.BULK_DELETE.compile(channel_id), json={"messages": message_ids}, reason=reason)

    def crosspost(self, channel_id: int, message_id: int, /) -> Response[dict[str, Any]]:
        """
        Publishes a message of an announcement channel to the channels
        following it.

        Parameters
        -----------
        channel_id: :class:`int`
            The announcement channel.
        message_id: :class:`int`
            The message.
        """
        return self.rest.request(self.CROSSPOST.compile(channel_id, message_id))

    def add_reaction(self, channel_id: int, message_id: int, emoji: str, /) -> Response[None]:
        """
        Reacts to a message as the bot.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        emoji: :class:`str`
            The emoji, the character itself or ``name:id`` for a custom
            one.
        """
        return self.rest.request(self.REACT.compile(channel_id, message_id, emoji))

    def remove_own_reaction(self, channel_id: int, message_id: int, emoji: str, /) -> Response[None]:
        """
        Takes the bot's reaction off a message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        emoji: :class:`str`
            The emoji, the character itself or ``name:id`` for a custom
            one.
        """
        return self.rest.request(self.UNREACT.compile(channel_id, message_id, emoji))

    def remove_reaction(self, channel_id: int, message_id: int, emoji: str, user_id: int, /) -> Response[None]:
        """
        Takes someone's reaction off a message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        emoji: :class:`str`
            The emoji, the character itself or ``name:id`` for a custom
            one.
        user_id: :class:`int`
            Whose reaction.
        """
        return self.rest.request(self.REMOVE_REACTION.compile(channel_id, message_id, emoji, user_id))

    def reactions(
            self,
            channel_id: int,
            message_id: int,
            emoji: str,
            /,
            *,
            limit: int = 25,
            after: int | None = None,
            type: int | None = None
    ) -> Response[list[dict[str, Any]]]:
        """
        Fetches the users who reacted with an emoji.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        emoji: :class:`str`
            The emoji, the character itself or ``name:id`` for a custom
            one.
        limit: :class:`int`
            How many users at most, 1 to 100.
        after: Optional[:class:`int`]
            Only users with an ID above this one.
        type: Optional[:class:`int`]
            ``0`` for normal reactions, ``1`` for super reactions.
        """
        return self.rest.request(self.REACTIONS.compile(channel_id, message_id, emoji), params={"limit": limit, "after": after, "type": type})

    def clear_reactions(self, channel_id: int, message_id: int, /) -> Response[None]:
        """
        Takes every reaction off a message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        """
        return self.rest.request(self.CLEAR_REACTIONS.compile(channel_id, message_id))

    def clear_reaction(self, channel_id: int, message_id: int, emoji: str, /) -> Response[None]:
        """
        Takes every reaction with one emoji off a message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        emoji: :class:`str`
            The emoji, the character itself or ``name:id`` for a custom
            one.
        """
        return self.rest.request(self.CLEAR_REACTION.compile(channel_id, message_id, emoji))

    def pins(self, channel_id: int, /, *, limit: int | None = None, before: str | None = None) -> Response[dict[str, Any]]:
        """
        Fetches the pinned messages of a channel, most recently pinned
        first. The payload holds them under ``items`` with the time each
        was pinned, and ``has_more`` tells whether another page follows.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        limit: Optional[:class:`int`]
            How many pins at most, 1 to 50.
        before: Optional[:class:`str`]
            Only pins made before this ISO 8601 timestamp.
        """
        return self.rest.request(self.PINS.compile(channel_id), params={"limit": limit, "before": before})

    def pin(self, channel_id: int, message_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Pins a message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.PIN.compile(channel_id, message_id), reason=reason)

    def unpin(self, channel_id: int, message_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Unpins a message.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the message is in.
        message_id: :class:`int`
            The message.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.UNPIN.compile(channel_id, message_id), reason=reason)

    def typing(self, channel_id: int, /) -> Response[None]:
        """
        Shows the bot as typing in a channel for about ten seconds.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel.
        """
        return self.rest.request(self.TYPING.compile(channel_id))

    def poll_voters(
            self,
            channel_id: int,
            message_id: int,
            answer_id: int,
            /,
            *,
            after: int | None = None,
            limit: int | None = None
    ) -> Response[dict[str, Any]]:
        """
        Fetches the users who voted for an answer of a poll. The payload
        holds them under ``users``.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the poll is in.
        message_id: :class:`int`
            The message carrying the poll.
        answer_id: :class:`int`
            The answer.
        after: Optional[:class:`int`]
            Only users with an ID above this one.
        limit: Optional[:class:`int`]
            How many users at most, 1 to 100.
        """
        return self.rest.request(self.POLL_VOTERS.compile(channel_id, message_id, answer_id), params={"after": after, "limit": limit})

    def end_poll(self, channel_id: int, message_id: int, /) -> Response[dict[str, Any]]:
        """
        Ends a poll early.

        Parameters
        -----------
        channel_id: :class:`int`
            The channel the poll is in.
        message_id: :class:`int`
            The message carrying the poll.
        """
        return self.rest.request(self.END_POLL.compile(channel_id, message_id))

    @staticmethod
    def _payload(
            content: str | None,
            embeds: Sequence[dict[str, Any]] | None,
            allowed_mentions: dict[str, Any] | None,
            components: Sequence[dict[str, Any]] | None,
            attachments: Sequence[dict[str, Any]],
            files: Sequence[File],
            flags: int,
            /
    ) -> dict[str, Any]:
        """
        The part of a message payload that sending and editing share.
        Files get their ``attachments`` entries here, numbered the way
        :meth:`RESTClient.request` names their multipart parts.
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

        if files is not MISSING:
            entries = [file.to_dict(index) for index, file in enumerate(files)]
            payload["attachments"] = entries if attachments is MISSING else [*attachments, *entries]
        elif attachments is not MISSING:
            payload["attachments"] = attachments

        return payload

__all__ = ["Messages"]