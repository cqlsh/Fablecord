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
from ..net.multipart import MultipartBody
from ..utils.missing import MISSING
from .route import Route

if TYPE_CHECKING:
    from .client import RESTClient, Response
    from ..file import File

class Stickers:
    """
    The sticker endpoints: stickers by ID, the packs Discord offers, and
    the custom stickers of a guild.

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

    GET: Final = Route("GET", "/stickers/{sticker_id}")
    PACKS: Final = Route("GET", "/sticker-packs")
    PACK: Final = Route("GET", "/sticker-packs/{pack_id}")
    OF_GUILD: Final = Route("GET", "/guilds/{guild_id}/stickers")
    GET_GUILD: Final = Route("GET", "/guilds/{guild_id}/stickers/{sticker_id}")
    CREATE: Final = Route("POST", "/guilds/{guild_id}/stickers")
    EDIT: Final = Route("PATCH", "/guilds/{guild_id}/stickers/{sticker_id}")
    DELETE: Final = Route("DELETE", "/guilds/{guild_id}/stickers/{sticker_id}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def get(self, sticker_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches a sticker, standard or custom.

        Parameters
        -----------
        sticker_id: :class:`int`
            The sticker.
        """
        return self.rest.request(self.GET.compile(sticker_id))

    def packs(self) -> Response[dict[str, Any]]:
        """
        Fetches the sticker packs Discord offers. The payload holds them
        under ``sticker_packs``.
        """
        return self.rest.request(self.PACKS.compile())

    def pack(self, pack_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one sticker pack Discord offers.

        Parameters
        -----------
        pack_id: :class:`int`
            The pack.
        """
        return self.rest.request(self.PACK.compile(pack_id))

    def of_guild(self, guild_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the custom stickers of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        """
        return self.rest.request(self.OF_GUILD.compile(guild_id))

    def get_guild(self, guild_id: int, sticker_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one custom sticker of a guild, with the user who made
        it when the bot may manage expressions.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        sticker_id: :class:`int`
            The sticker.
        """
        return self.rest.request(self.GET_GUILD.compile(guild_id, sticker_id))

    def create(
            self,
            guild_id: int,
            /,
            *,
            name: str,
            description: str,
            tags: str,
            file: File,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Creates a custom sticker in a guild. Discord takes this as a
        form with the file next to the fields rather than as JSON, and
        wants to be told what kind of file it is.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        name: :class:`str`
            The name, 2 to 30 characters.
        description: :class:`str`
            The description, empty or 2 to 100 characters.
        tags: :class:`str`
            The autocomplete tags, up to 200 characters.
        file: :class:`File`
            The image: PNG, APNG, GIF or Lottie JSON, up to 512 KB.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        form = MultipartBody()
        form.add_field("name", name)
        form.add_field("description", description)
        form.add_field("tags", tags)
        form.add_file("file", file.data, filename=file.filename, content_type=self._mime(file.data))

        return self.rest.request(self.CREATE.compile(guild_id), form=form, reason=reason)

    def edit(
            self,
            guild_id: int,
            sticker_id: int,
            /,
            *,
            name: str = MISSING,
            description: str | None = MISSING,
            tags: str = MISSING,
            reason: str | None = None
    ) -> Response[dict[str, Any]]:
        """
        Edits a custom sticker of a guild. Only what is given changes.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        sticker_id: :class:`int`
            The sticker.
        name: :class:`str`
            The new name.
        description: Optional[:class:`str`]
            The new description, ``None`` to remove it.
        tags: :class:`str`
            The new autocomplete tags.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if description is not MISSING:
            payload["description"] = description

        if tags is not MISSING:
            payload["tags"] = tags

        return self.rest.request(self.EDIT.compile(guild_id, sticker_id), json=payload, reason=reason)

    def delete(self, guild_id: int, sticker_id: int, /, *, reason: str | None = None) -> Response[None]:
        """
        Deletes a custom sticker of a guild.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild.
        sticker_id: :class:`int`
            The sticker.
        reason: Optional[:class:`str`]
            The reason for the audit log.
        """
        return self.rest.request(self.DELETE.compile(guild_id, sticker_id), reason=reason)

    @staticmethod
    def _mime(data: bytes, /) -> str:
        """
        Tells Discord what kind of file a sticker is from its first
        bytes, since the form carries no other hint.
        """
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"

        if data.startswith((b"GIF87a", b"GIF89a")):
            return "image/gif"

        if data.lstrip().startswith(b"{"):
            return "application/json"

        return "application/octet-stream"

__all__ = ["Stickers"]