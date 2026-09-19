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

from binascii import b2a_base64

class Image:
    """
    What the API needs to know about an image it is handed as bytes.

    Avatars, icons, banners and emojis go to Discord as data URIs, and
    Discord decides from the declared type whether it takes the
    image, so the type is read from the first bytes rather than from
    a file name.
    """

    __slots__ = []

    @staticmethod
    def mime(data: bytes, /) -> str:
        """
        The MIME type of an image from its first bytes.

        Parameters
        -----------
        data: :class:`bytes`
            The whole image, or at least its first twelve bytes.

        Raises
        -------
        ValueError
            The bytes are not a PNG, JPEG, GIF or WebP image, which are
            the formats Discord takes.

        Returns
        --------
        :class:`str`
            ``image/png``, ``image/jpeg``, ``image/gif`` or
            ``image/webp``.
        """
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"

        if data.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"

        if data.startswith((b"GIF87a", b"GIF89a")):
            return "image/gif"

        if data.startswith(b"RIFF") and data.startswith(b"WEBP", 8):
            return "image/webp"

        raise ValueError("the image is not a PNG, JPEG, GIF or WebP")

    @staticmethod
    def data_uri(data: bytes, /) -> str:
        """
        The image as the ``data:`` URI the API takes for avatars,
        icons, banners and emojis.

        Raises
        -------
        ValueError
            The bytes are not an image Discord takes.
        """
        return f"data:{Image.mime(data)};base64,{b2a_base64(data, newline=False).decode()}"

__all__ = ["Image"]