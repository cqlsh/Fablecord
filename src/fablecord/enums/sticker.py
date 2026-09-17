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

class StickerType(Enum):
    """
    Where a sticker comes from.
    """

    standard = 1
    """
    One of Discord's own packs. Usable everywhere without a permission.
    """

    guild = 2
    """
    Uploaded to a guild. Usable there by everyone, elsewhere only by Nitro subscribers.
    """

class StickerFormatType(Enum):
    """
    The file format of a sticker.

    The format decides the file extension on the CDN and whether the
    sticker moves. Guilds can upload three of the four, Lottie is
    reserved for Discord's own packs.
    """

    png = 1
    """
    A still image.
    """

    apng = 2
    """
    An animated PNG.
    """

    lottie = 3
    """
    A Lottie vector animation, served as JSON. Only in Discord's own
    packs, and only rendered by Discord's own clients.
    """

    gif = 4
    """
    An animated GIF.
    """

    is_animated = Category(apng, lottie, gif)
    """
    :class:`bool`: Whether the sticker moves.
    """

    __extensions: dict[int, str] = {png: "png", apng: "png", lottie: "json", gif: "gif"}

    @property
    def file_extension(self) -> str:
        """
        :class:`str`: The extension of the sticker's file on the CDN.
        Both PNG formats use ``png``, Lottie uses ``json``. Unknown
        formats fall back to ``png``.
        """
        value: int = self.value

        return self.__extensions.get(value, "png")

__all__ = ["StickerType", "StickerFormatType"]