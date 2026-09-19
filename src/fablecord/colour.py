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

import random
import re

from colorsys import hsv_to_rgb
from typing import Final, Self

_RGB: Final = re.compile(r"rgb\s*\((?P<red>[0-9.]+%?)\s*,\s*(?P<green>[0-9.]+%?)\s*,\s*(?P<blue>[0-9.]+%?)\s*\)")

class Colour:
    """
    A 24-bit colour, the way Discord stores it for roles and embeds.

    The value is the integer Discord sends, ``0xRRGGBB``. Named colours
    are classmethods, ``Colour.blurple()``, so every call gives a fresh
    object that can be compared and hashed by its value. ``Color`` is
    the same class under the other spelling.

    Attributes
    -----------
    value: :class:`int`
        The colour as one integer from ``0`` to ``0xFFFFFF``.
    """

    __slots__ = ["value"]

    def __init__(self, value: int, /) -> None:
        self.value = value

    @property
    def r(self) -> int:
        """
        :class:`int`: The red part, ``0`` to ``255``.
        """
        return self.value >> 16 & 0xFF

    @property
    def g(self) -> int:
        """
        :class:`int`: The green part, ``0`` to ``255``.
        """
        return self.value >> 8 & 0xFF

    @property
    def b(self) -> int:
        """
        :class:`int`: The blue part, ``0`` to ``255``.
        """
        return self.value & 0xFF

    def to_rgb(self) -> tuple[int, int, int]:
        """
        The red, green and blue parts as a tuple.
        """
        value = self.value

        return value >> 16 & 0xFF, value >> 8 & 0xFF, value & 0xFF

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, /) -> Self:
        """
        A colour from its red, green and blue parts, ``0`` to ``255``
        each.
        """
        return cls(r << 16 | g << 8 | b)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, /) -> Self:
        """
        A colour from hue, saturation and value, ``0.0`` to ``1.0``
        each.
        """
        red, green, blue = hsv_to_rgb(h, s, v)

        return cls(int(red * 255) << 16 | int(green * 255) << 8 | int(blue * 255))

    @classmethod
    def from_str(cls, value: str, /) -> Self:
        """
        A colour from text.

        Parameters
        -----------
        value: :class:`str`
            ``#RRGGBB``, ``#RGB``, ``0xRRGGBB`` or ``rgb(r, g, b)`` with
            numbers from 0 to 255 or percentages.

        Raises
        -------
        ValueError
            The text is none of those, or a part is out of range.
        """
        if not value:
            raise ValueError("unknown colour format given")

        if value[0] == "#":
            return cls._from_hex(value[1:])

        if value[:2] == "0x":
            rest = value[2:]

            if rest.startswith("#"):
                return cls._from_hex(rest[1:])

            return cls._from_hex(rest)

        lowered = value.lower()

        if lowered[:3] == "rgb":
            return cls._from_rgb_text(lowered)

        raise ValueError("unknown colour format given")

    @classmethod
    def random(cls, *, seed: int | float | str | bytes | bytearray | None = None) -> Self:
        """
        A random colour with full saturation and value, the same one
        again for the same ``seed``.
        """
        generator = random if seed is None else random.Random(seed)

        return cls.from_hsv(generator.random(), 1, 1)

    @classmethod
    def default(cls) -> Self:
        """
        ``0``, which Discord shows as no colour at all.
        """
        return cls(0)

    @classmethod
    def teal(cls) -> Self:
        """
        ``0x1ABC9C``.
        """
        return cls(0x1ABC9C)

    @classmethod
    def dark_teal(cls) -> Self:
        """
        ``0x11806A``.
        """
        return cls(0x11806A)

    @classmethod
    def brand_green(cls) -> Self:
        """
        ``0x57F287``, Discord's own green.
        """
        return cls(0x57F287)

    @classmethod
    def green(cls) -> Self:
        """
        ``0x2ECC71``.
        """
        return cls(0x2ECC71)

    @classmethod
    def dark_green(cls) -> Self:
        """
        ``0x1F8B4C``.
        """
        return cls(0x1F8B4C)

    @classmethod
    def blue(cls) -> Self:
        """
        ``0x3498DB``.
        """
        return cls(0x3498DB)

    @classmethod
    def dark_blue(cls) -> Self:
        """
        ``0x206694``.
        """
        return cls(0x206694)

    @classmethod
    def purple(cls) -> Self:
        """
        ``0x9B59B6``.
        """
        return cls(0x9B59B6)

    @classmethod
    def dark_purple(cls) -> Self:
        """
        ``0x71368A``.
        """
        return cls(0x71368A)

    @classmethod
    def magenta(cls) -> Self:
        """
        ``0xE91E63``.
        """
        return cls(0xE91E63)

    @classmethod
    def dark_magenta(cls) -> Self:
        """
        ``0xAD1457``.
        """
        return cls(0xAD1457)

    @classmethod
    def gold(cls) -> Self:
        """
        ``0xF1C40F``.
        """
        return cls(0xF1C40F)

    @classmethod
    def dark_gold(cls) -> Self:
        """
        ``0xC27C0E``.
        """
        return cls(0xC27C0E)

    @classmethod
    def orange(cls) -> Self:
        """
        ``0xE67E22``.
        """
        return cls(0xE67E22)

    @classmethod
    def dark_orange(cls) -> Self:
        """
        ``0xA84300``.
        """
        return cls(0xA84300)

    @classmethod
    def brand_red(cls) -> Self:
        """
        ``0xED4245``, Discord's own red.
        """
        return cls(0xED4245)

    @classmethod
    def red(cls) -> Self:
        """
        ``0xE74C3C``.
        """
        return cls(0xE74C3C)

    @classmethod
    def dark_red(cls) -> Self:
        """
        ``0x992D22``.
        """
        return cls(0x992D22)

    @classmethod
    def lighter_grey(cls) -> Self:
        """
        ``0x95A5A6``.
        """
        return cls(0x95A5A6)

    @classmethod
    def dark_grey(cls) -> Self:
        """
        ``0x607D8B``.
        """
        return cls(0x607D8B)

    @classmethod
    def light_grey(cls) -> Self:
        """
        ``0x979C9F``.
        """
        return cls(0x979C9F)

    @classmethod
    def darker_grey(cls) -> Self:
        """
        ``0x546E7A``.
        """
        return cls(0x546E7A)

    @classmethod
    def og_blurple(cls) -> Self:
        """
        ``0x7289DA``, the blurple Discord had before 2021.
        """
        return cls(0x7289DA)

    @classmethod
    def blurple(cls) -> Self:
        """
        ``0x5865F2``, Discord's blurple.
        """
        return cls(0x5865F2)

    @classmethod
    def greyple(cls) -> Self:
        """
        ``0x99AAB5``.
        """
        return cls(0x99AAB5)

    @classmethod
    def ash_theme(cls) -> Self:
        """
        ``0x2E2E34``, the background of the ash theme.
        """
        return cls(0x2E2E34)

    @classmethod
    def dark_theme(cls) -> Self:
        """
        ``0x1A1A1E``, the background of the dark theme, so an embed in
        this colour has no visible edge there.
        """
        return cls(0x1A1A1E)

    @classmethod
    def onyx_theme(cls) -> Self:
        """
        ``0x070709``, the background of the onyx theme.
        """
        return cls(0x070709)

    @classmethod
    def light_theme(cls) -> Self:
        """
        ``0xFBFBFB``, the background of the light theme.
        """
        return cls(0xFBFBFB)

    @classmethod
    def fuchsia(cls) -> Self:
        """
        ``0xEB459E``.
        """
        return cls(0xEB459E)

    @classmethod
    def yellow(cls) -> Self:
        """
        ``0xFEE75C``.
        """
        return cls(0xFEE75C)

    @classmethod
    def ash_embed(cls) -> Self:
        """
        ``0x37373E``, the embed background of the ash theme.
        """
        return cls(0x37373E)

    @classmethod
    def dark_embed(cls) -> Self:
        """
        ``0x242429``, the embed background of the dark theme.
        """
        return cls(0x242429)

    @classmethod
    def onyx_embed(cls) -> Self:
        """
        ``0x131416``, the embed background of the onyx theme.
        """
        return cls(0x131416)

    @classmethod
    def light_embed(cls) -> Self:
        """
        ``0xFFFFFF``, the embed background of the light theme.
        """
        return cls(0xFFFFFF)

    @classmethod
    def pink(cls) -> Self:
        """
        ``0xEB459F``.
        """
        return cls(0xEB459F)

    @classmethod
    def _from_hex(cls, digits: str, /) -> Self:
        """
        Reads three or six hex digits, three meaning each one doubled.
        """
        if len(digits) == 3:
            digits = "".join(digit * 2 for digit in digits)

        try:
            value = int(digits, base=16)
        except ValueError:
            raise ValueError("hex number out of range for 24-bit colour") from None

        if not 0 <= value <= 0xFFFFFF:
            raise ValueError("hex number out of range for 24-bit colour")

        return cls(value)

    @classmethod
    def _from_rgb_text(cls, text: str, /) -> Self:
        """
        Reads ``rgb(r, g, b)`` with numbers or percentages.
        """
        match = _RGB.match(text)
        if match is None:
            raise ValueError("unknown colour format given")

        red, green, blue = match.groups()
        part = cls._part

        return cls(part(red) << 16 | part(green) << 8 | part(blue))

    @staticmethod
    def _part(number: str, /) -> int:
        """
        One part of ``rgb(...)``: ``0`` to ``255``, or a percentage.
        """
        if number[-1] == "%":
            percent = float(number[:-1])

            if not 0 <= percent <= 100:
                raise ValueError("rgb percentage can only be between 0 to 100")

            return round(255 * percent / 100)

        value = int(number)

        if not 0 <= value <= 255:
            raise ValueError("rgb number can only be between 0 to 255")

        return value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Colour) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return f"#{self.value:06x}"

    def __repr__(self) -> str:
        return f"<Colour value={self.value}>"

Color = Colour

__all__ = ["Colour", "Color"]