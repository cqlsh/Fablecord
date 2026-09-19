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
from ..utils.missing import MISSING
from .route import Route

if TYPE_CHECKING:
    from .client import RESTClient, Response

class Soundboard:
    """
    The soundboard endpoints: the sounds Discord ships, the sounds of a
    guild, and playing one in a voice channel.

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

    SEND: Final = Route("POST", "/channels/{channel_id}/send-soundboard-sound")
    DEFAULTS: Final = Route("GET", "/soundboard-default-sounds")
    OF_GUILD: Final = Route("GET", "/guilds/{guild_id}/soundboard-sounds")
    GET: Final = Route("GET", "/guilds/{guild_id}/soundboard-sounds/{sound_id}")
    CREATE: Final = Route("POST", "/guilds/{guild_id}/soundboard-sounds")
    EDIT: Final = Route("PATCH", "/guilds/{guild_id}/soundboard-sounds/{sound_id}")
    DELETE: Final = Route("DELETE", "/guilds/{guild_id}/soundboard-sounds/{sound_id}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def send(self, channel_id: int, /, *, sound_id: int, source_guild_id: int = MISSING) -> Response[None]:
        """
        Plays a sound in a voice channel the bot is connected to, and
        not muted or deafened in.

        Parameters
        -----------
        channel_id: :class:`int`
            The voice channel.
        sound_id: :class:`int`
            The sound.
        source_guild_id: :class:`int`
            The guild the sound belongs to, when it is not this one.
        """
        payload: dict[str, Any] = {"sound_id": sound_id}

        if source_guild_id is not MISSING:
            payload["source_guild_id"] = source_guild_id

        return self.rest.request(self.SEND.compile(channel_id), json=payload)

    def defaults(self) -> Response[list[dict[str, Any]]]:
        """
        Fetches the sounds Discord ships with every soundboard.
        """
        return self.rest.request(self.DEFAULTS.compile())

    def of_guild(self, guild_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches the sounds of a guild. The payload holds them under
        ``items``.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.OF_GUILD.compile(guild_id))

    def get(self, guild_id: int, sound_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one sound of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        sound_id: :class:`int`
            The sound.
        """
        return self.rest.request(self.GET.compile(guild_id, sound_id))

    def create(
            self,
            guild_id: int,
            /,
            *,
            name: str,
            sound: str,
            volume: float = MISSING,
            emoji_id: int | None = MISSING,
            emoji_name: str | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Adds a sound to a guild's soundboard.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name, 2 to 32 characters.
        sound: :class:`str`
            The audio as a data URI, MP3 or Ogg, up to 512 KB and five
            seconds.
        volume: :class:`float`
            The volume from 0 to 1, full when not given.
        emoji_id: Optional[:class:`int`]
            The custom emoji shown with the sound.
        emoji_name: Optional[:class:`str`]
            The standard emoji shown with the sound.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {"name": name, "sound": sound}

        if volume is not MISSING:
            payload["volume"] = volume

        if emoji_id is not MISSING:
            payload["emoji_id"] = emoji_id

        if emoji_name is not MISSING:
            payload["emoji_name"] = emoji_name

        return self.rest.request(self.CREATE.compile(guild_id), json=payload, reason=reason)

    def edit(
            self,
            guild_id: int,
            sound_id: int,
            /,
            *,
            name: str = MISSING,
            volume: float | None = MISSING,
            emoji_id: int | None = MISSING,
            emoji_name: str | None = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a sound of a guild. Only what is given changes, ``None``
        clears a field.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        sound_id: :class:`int`
            The sound.
        name: :class:`str`
            The new name.
        volume: Optional[:class:`float`]
            The volume from 0 to 1.
        emoji_id: Optional[:class:`int`]
            The custom emoji shown with the sound.
        emoji_name: Optional[:class:`str`]
            The standard emoji shown with the sound.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if volume is not MISSING:
            payload["volume"] = volume

        if emoji_id is not MISSING:
            payload["emoji_id"] = emoji_id

        if emoji_name is not MISSING:
            payload["emoji_name"] = emoji_name

        return self.rest.request(self.EDIT.compile(guild_id, sound_id), json=payload, reason=reason)

    def delete(self, guild_id: int, sound_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Removes a sound from a guild's soundboard.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        sound_id: :class:`int`
            The sound.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(guild_id, sound_id), reason=reason)

__all__ = ["Soundboard"]