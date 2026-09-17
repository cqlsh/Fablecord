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

from .base import Enum

class CollectibleType(Enum):
    """
    The kinds of cosmetic items a user can equip.

    Discord has exactly one so far. The collectibles object of a user
    is keyed by this, so new kinds arrive without breaking the parser.
    """

    nameplate = "nameplate"
    """
    A nameplate, the animated backdrop behind a name in the member list.
    """

class NameplatePalette(Enum):
    """
    The colour palette of a nameplate.

    Discord sends it next to the asset path so a client can tint the
    name and the background to match the animation.
    """

    crimson = "crimson"
    """
    A deep red.
    """

    berry = "berry"
    """
    A purplish red.
    """

    sky = "sky"
    """
    A light blue.
    """

    teal = "teal"
    """
    A blue green.
    """

    forest = "forest"
    """
    A dark green.
    """

    bubble_gum = "bubble_gum"
    """
    A pink.
    """

    violet = "violet"
    """
    A purple.
    """

    cobalt = "cobalt"
    """
    A strong blue.
    """

    clover = "clover"
    """
    A bright green.
    """

    lemon = "lemon"
    """
    A yellow.
    """

    white = "white"
    """
    White, for nameplates that are mostly light.
    """

__all__ = ["CollectibleType", "NameplatePalette"]