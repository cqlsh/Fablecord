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

from os import urandom

class MultipartBody:
    """
    A ``multipart/form-data`` request body assembled in memory.

    Discord takes uploads as one ``payload_json`` field holding the JSON
    that would otherwise be the body, followed by a ``files[n]`` field per
    attachment. Parts are collected as they come and joined once in
    :meth:`encode`, so a file's bytes are copied a single time no matter
    how many parts surround it.

    Attributes
    -----------
    boundary: :class:`str`
        The random boundary between the parts, 32 hex characters from
        :func:`os.urandom`. It travels in :attr:`content_type` so the
        server knows where each part starts.
    """

    __slots__ = ["boundary", "_parts"]

    def __init__(self) -> None:
        self.boundary = urandom(16).hex()
        self._parts: list[bytes] = []

    @property
    def content_type(self) -> str:
        """
        :class:`str`: The ``Content-Type`` value to send along with the encoded body.
        """
        return f"multipart/form-data; boundary={self.boundary}"

    def add_field(self, name: str, value: str | bytes, /, *, content_type: str | None = None) -> None:
        """
        Adds a plain field.

        A :class:`str` value is sent as UTF-8. Without ``content_type`` the
        part carries no ``Content-Type`` header and servers read it as
        ``text/plain``; Discord's ``payload_json`` belongs here with
        ``application/json``.

        Parameters
        -----------
        name: :class:`str`
            The field name, for example ``payload_json``.
        value: Union[:class:`str`, :class:`bytes`]
            The field content.
        content_type: Optional[:class:`str`]
            The media type of the content, if it is not plain text.

        Raises
        -------
        ValueError
            The name contains a line break, which no header can carry.
        """
        head = f'--{self.boundary}\r\nContent-Disposition: form-data; name="{self._quote(name)}"'

        if content_type is not None:
            head = f"{head}\r\nContent-Type: {content_type}"

        if isinstance(value, str):
            value = value.encode()

        self._parts.extend([f"{head}\r\n\r\n".encode(), value, b"\r\n"])

    def add_file(
            self,
            name: str,
            data: bytes,
            /,
            *,
            filename: str,
            content_type: str = "application/octet-stream"
    ) -> None:
        """
        Adds a file.

        The filename is what Discord shows and stores as the attachment
        name, so it should carry the extension. The bytes are not copied
        until :meth:`encode` runs.

        Parameters
        -----------
        name: :class:`str`
            The field name, ``files[0]`` for the first attachment.
        data: :class:`bytes`
            The whole file.
        filename: :class:`str`
            The name the server receives for the file.
        content_type: :class:`str`
            The media type of the file. Discord does not need the real one
            and sniffs the content itself, so the default is fine.

        Raises
        -------
        ValueError
            The name or filename contains a line break, which no header can carry.
        """
        head = (
            f'--{self.boundary}\r\nContent-Disposition: form-data; name="{self._quote(name)}"; '
            f'filename="{self._quote(filename)}"\r\nContent-Type: {content_type}\r\n\r\n'
        )

        self._parts.extend([head.encode(), data, b"\r\n"])

    def encode(self) -> bytes:
        """
        Joins every part and the closing boundary into the final body.

        Returns
        --------
        :class:`bytes`
            The body to send with :attr:`content_type`.
        """
        closing = f"--{self.boundary}--\r\n".encode()

        return b"".join(self._parts + [closing])

    @staticmethod
    def _quote(value: str, /) -> str:
        """
        Escapes a name or filename for a quoted header parameter the way
        aiohttp does with ``quote_fields=False``, so Discord receives the
        same bytes discord.py has been sending for years.
        """
        if "\r" in value or "\n" in value:
            raise ValueError("a field name or filename cannot contain line breaks")

        return value.replace("\\", "\\\\").replace('"', '\\"')

__all__ = ["MultipartBody"]