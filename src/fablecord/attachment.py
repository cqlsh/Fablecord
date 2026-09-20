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
from datetime import datetime
from base64 import b64decode
from os import PathLike
from io import BufferedIOBase

from .flags.message import AttachmentFlags
from .utils.snowflake import Snowflake
from .utils.missing import MISSING
from .file import File

if TYPE_CHECKING:
    from .state import State

_SPOILER: Final = AttachmentFlags.spoiler.bit

class Attachment:
    """
    A file someone sent with a message.

    Discord keeps the file itself on its CDN and sends this alongside
    the message. :meth:`read` downloads it, :meth:`save` writes it to
    disk and :meth:`to_file` turns it into a :class:`File` that can go
    out with another message.

    Attributes
    -----------
    id: :class:`int`
        The attachment's ID.
    filename: :class:`str`
        The name of the file as it was uploaded.
    title: Optional[:class:`str`]
        The name Discord shows instead of the file name, which it sets
        for a file whose name it had to clean up.
    description: Optional[:class:`str`]
        The alt text, which screen readers announce.
    size: :class:`int`
        The size in bytes.
    url: :class:`str`
        Where the file lives. The link stops working once the message
        is deleted, and it carries a signature that runs out after a
        day.
    proxy_url: :class:`str`
        Discord's own copy, which it may still serve for a while after
        the message is gone.
    height: Optional[:class:`int`]
        The height in pixels, only for an image or a video.
    width: Optional[:class:`int`]
        The width in pixels, only for an image or a video.
    content_type: Optional[:class:`str`]
        The media type Discord determined, such as ``image/png``.
    ephemeral: :class:`bool`
        Whether the file belongs to a message only its receiver sees,
        which Discord removes after a few days.
    duration: Optional[:class:`float`]
        How long a voice message runs, in seconds.
    waveform: Optional[:class:`bytes`]
        The bars a voice message draws, one byte per sample.
    """

    __slots__ = [
        "id",
        "filename",
        "title",
        "description",
        "size",
        "url",
        "proxy_url",
        "height",
        "width",
        "content_type",
        "ephemeral",
        "duration",
        "waveform",
        "_state",
        "_flags"
    ]

    def __init__(self, state: State, data: dict[str, Any], /) -> None:
        get = data.get

        self.id = int(data["id"])
        self.filename = data["filename"]
        self.title = get("title")
        self.description = get("description")
        self.size = data["size"]
        self.url = data["url"]
        self.proxy_url = data["proxy_url"]
        self.height = get("height")
        self.width = get("width")
        self.content_type = get("content_type")
        self.ephemeral = get("ephemeral", False)
        self.duration = get("duration_secs")
        self._state = state
        self._flags = get("flags", 0)

        waveform = get("waveform")
        self.waveform = None if waveform is None else b64decode(waveform)

    @property
    def flags(self) -> AttachmentFlags:
        """
        :class:`AttachmentFlags`: What Discord marked about the file,
        such as it being a spoiler or a clip.
        """
        flags = AttachmentFlags.__new__(AttachmentFlags)
        flags.value = self._flags

        return flags

    @property
    def created_at(self) -> datetime:
        """
        :class:`datetime.datetime`: When the file was uploaded, taken
        from the ID.
        """
        return Snowflake(self.id).created_at

    def is_spoiler(self) -> bool:
        """
        Whether the file is hidden until it is clicked, which Discord
        marks with a flag and with the name it was uploaded under.
        """
        return self.filename.startswith("SPOILER_") or bool(self._flags & _SPOILER)

    def is_voice_message(self) -> bool:
        """
        Whether the file is a voice message, which is what carrying a
        length and a waveform means.
        """
        return self.duration is not None and self.waveform is not None

    async def read(self, *, use_cached: bool = False) -> bytes:
        """
        |coro|

        Downloads the file.

        Parameters
        -----------
        use_cached: :class:`bool`
            Download :attr:`proxy_url` instead of :attr:`url`, which is
            the only one that still works for a while once the message
            is deleted.

        Raises
        -------
        NotFound
            The file is gone, which happens once the message was
            deleted or the link ran out.
        HTTPException
            The download failed.

        Returns
        --------
        :class:`bytes`
            The file.
        """
        return await self._state.rest.get_from_cdn(self.proxy_url if use_cached else self.url)

    async def save(
        self,
        fp: str | PathLike[str] | BufferedIOBase,
        /,
        *,
        seek_begin: bool = True,
        use_cached: bool = False
    ) -> int:
        """
        |coro|

        Downloads the file and writes it.

        Parameters
        -----------
        fp: Union[:class:`str`, :class:`os.PathLike`, :class:`io.BufferedIOBase`]
            A path to write, or an open binary file to write into.
        seek_begin: :class:`bool`
            Whether to seek an open file back to the start afterwards.
        use_cached: :class:`bool`
            Download Discord's own copy, see :meth:`read`.

        Returns
        --------
        :class:`int`
            The number of bytes written.
        """
        data = await self.read(use_cached=use_cached)

        if isinstance(fp, BufferedIOBase):
            written = fp.write(data)

            if seek_begin:
                fp.seek(0)

            return written

        with open(fp, "wb") as file:
            return file.write(data)

    async def to_file(
        self,
        *,
        filename: str | None = MISSING,
        description: str | None = MISSING,
        spoiler: bool = MISSING,
        use_cached: bool = False
    ) -> File:
        """
        |coro|

        Downloads the file and wraps it so it can go out with another
        message.

        Parameters
        -----------
        filename: Optional[:class:`str`]
            The name to send it under, the one it arrived with by
            default.
        description: Optional[:class:`str`]
            The alt text to send, the one it arrived with by default.
        spoiler: :class:`bool`
            Whether to hide it until it is clicked, the way it arrived
            by default.
        use_cached: :class:`bool`
            Download Discord's own copy, see :meth:`read`.

        Returns
        --------
        :class:`File`
            The file, ready to send.
        """
        data = await self.read(use_cached=use_cached)

        return File(
            data,
            self.filename if filename is MISSING else filename,
            spoiler=self.is_spoiler() if spoiler is MISSING else spoiler,
            description=self.description if description is MISSING else description
        )

    def to_dict(self) -> dict[str, Any]:
        """
        The payload for this attachment, which an edit sends back to
        keep the file on the message.
        """
        data: dict[str, Any] = {
            "id": self.id,
            "filename": self.filename,
            "size": self.size,
            "url": self.url,
            "proxy_url": self.proxy_url,
            "spoiler": self.is_spoiler()
        }

        if self.title is not None:
            data["title"] = self.title

        if self.description is not None:
            data["description"] = self.description

        if self.height is not None:
            data["height"] = self.height

        if self.width is not None:
            data["width"] = self.width

        if self.content_type is not None:
            data["content_type"] = self.content_type

        return data

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"<Attachment id={self.id} filename={self.filename!r} size={self.size} url={self.url!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Attachment) and other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

__all__ = ["Attachment"]