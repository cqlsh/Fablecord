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

import os
import io

from typing import Any, BinaryIO, Final
from .utils.missing import MISSING

_SPOILER: Final = "SPOILER_"

class File:
    """
    A file to send with a message.

    The contents are read right here, from a path, a stream or bytes,
    so the same :class:`File` can be sent as often as wanted and the
    request can be retried without touching the source again.

    Parameters
    -----------
    fp: Union[:class:`str`, :class:`os.PathLike`, :class:`bytes`, :class:`io.BufferedIOBase`]
        The file: a path to open and read, bytes to send as they are,
        or a stream open in binary mode, read to the end from where it
        stands.
    filename: Optional[:class:`str`]
        The name Discord shows. Taken from the path or the stream when
        not given, ``untitled`` for bytes.
    spoiler: :class:`bool`
        Whether Discord hides the file behind a spoiler. When not given,
        a name starting with ``SPOILER_`` makes it one.
    description: Optional[:class:`str`]
        The alt text of an image.

    Attributes
    -----------
    data: :class:`bytes`
        The contents.
    spoiler: :class:`bool`
        Whether Discord hides the file behind a spoiler.
    description: Optional[:class:`str`]
        The alt text, ``None`` when there is none.
    """

    __slots__ = ["data", "spoiler", "description", "_filename"]

    def __init__(
            self,
            fp: str | os.PathLike[str] | bytes | io.BufferedIOBase | BinaryIO,
            filename: str | None = None,
            *,
            spoiler: bool = MISSING,
            description: str | None = None
    ) -> None:
        if isinstance(fp, bytes):
            self.data = fp

            if filename is None:
                filename = "untitled"
        elif isinstance(fp, (str, os.PathLike)):
            path = os.fspath(fp)

            with open(path, "rb") as stream:
                self.data = stream.read()

            if filename is None:
                filename = os.path.basename(path)
        else:
            self.data = fp.read()

            if filename is None:
                name: Any = getattr(fp, "name", None)
                filename = "untitled" if name is None else os.path.basename(str(name))

        stripped = filename
        while stripped.startswith(_SPOILER):
            stripped = stripped[8:]

        self._filename = stripped
        self.spoiler: bool = (stripped != filename) if spoiler is MISSING else spoiler
        self.description = description

    @property
    def filename(self) -> str:
        """
        :class:`str`: The name Discord shows, with ``SPOILER_`` in front
        of it for a spoiler.
        """
        return _SPOILER + self._filename if self.spoiler else self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        stripped = value
        while stripped.startswith(_SPOILER):
            stripped = stripped[8:]

        self._filename = stripped
        self.spoiler = stripped != value

    @property
    def uri(self) -> str:
        """
        :class:`str`: The ``attachment://`` URL that an embed or a
        component uses to show this file once it is uploaded with the
        message.
        """
        return f"attachment://{self.filename}"

    def to_dict(self, index: int, /) -> dict[str, Any]:
        """
        The entry for the ``attachments`` list of a message payload,
        which is how the description reaches Discord.

        Parameters
        -----------
        index: :class:`int`
            The position of the file among the files of the message.
        """
        filename = self._filename
        if self.spoiler:
            filename = _SPOILER + filename

        description = self.description
        if description is None:
            return {"id": index, "filename": filename}

        return {"id": index, "filename": filename, "description": description}

    def __repr__(self) -> str:
        return f"<File filename={self.filename!r} size={len(self.data)} spoiler={self.spoiler}>"

__all__ = ["File"]