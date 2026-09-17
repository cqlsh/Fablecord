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

import re

from typing import Final

class Markdown:
    """
    Escaping and stripping of Discord's markdown in user supplied text.

    Every pattern is compiled once at import, and wherever the result
    can be described as a template the regex engine expands it itself,
    so most calls run without a Python callback per match. discord.py
    compiles on every call and calls back into Python for each hit.
    """

    __slots__ = ()

    _URL: Final = r"(?P<url><[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;\"\'\]\s])"
    _COMMON: Final = r"^>(?:>>)?\s|\[.+\]\(.+\)|^#{1,3}|^\s*-"
    _STOCK: Final = re.compile(rf"(?P<markdown>[_\\~|\*`]|{_COMMON})", re.MULTILINE)
    _STOCK_AROUND_LINKS: Final = re.compile(rf"{_URL}|(?P<markdown>[_\\~|\*`]|{_COMMON})", re.MULTILINE)
    _AS_NEEDED: Final = re.compile(
        "|".join(r"\{0}(?=([\s\S]*((?<!\{0})\{0})))".format(char) for char in "*`_~|") + f"|{_COMMON}",
        re.MULTILINE
    )
    _MENTION: Final = re.compile(r"@(everyone|here|[!&]?[0-9]{17,20})")

    @staticmethod
    def escape(text: str, /, *, as_needed: bool = False, ignore_links: bool = True) -> str:
        """
        Escapes the markdown in a text so Discord shows it as written.

        Parameters
        -----------
        text: :class:`str`
            The text, usually something a user typed.
        as_needed: :class:`bool`
            Escape only what would render, so ``**hello**`` turns into
            ``\\*\\*hello**``. Cheaper on clean text, but a determined
            user can still sneak formatting through, and links are not
            spared in this mode.
        ignore_links: :class:`bool`
            Leave URLs alone, so an underscore inside a link keeps the
            link working.

        Returns
        --------
        :class:`str`
            The escaped text.
        """
        if as_needed:
            return Markdown._AS_NEEDED.sub(r"\\\g<0>", text.replace("\\", "\\\\"))

        if ignore_links:
            return Markdown._STOCK_AROUND_LINKS.sub(Markdown._keep_link_or_escape, text)

        return Markdown._STOCK.sub(r"\\\g<markdown>", text)

    @staticmethod
    def remove(text: str, /, *, ignore_links: bool = True) -> str:
        """
        Strips the markdown characters out of a text.

        This is not markdown aware, ``10 * 5`` loses its star as well.

        Parameters
        -----------
        text: :class:`str`
            The text to strip.
        ignore_links: :class:`bool`
            Leave URLs alone, so the underscores in a link survive.

        Returns
        --------
        :class:`str`
            The text without markdown characters.
        """
        if ignore_links:
            return Markdown._STOCK_AROUND_LINKS.sub(r"\g<url>", text)

        return Markdown._STOCK.sub("", text)

    @staticmethod
    def escape_mentions(text: str, /) -> str:
        """
        Defuses ``@everyone``, ``@here`` and user and role mentions.

        A zero width space goes in after the ``@``, so the text still
        reads the same but pings nobody. Allowed mentions on the message
        are the better tool, this is for text that has to be shown
        verbatim, such as a quoted message.

        Parameters
        -----------
        text: :class:`str`
            The text to defuse.

        Returns
        --------
        :class:`str`
            The text with every mention broken up.
        """
        return Markdown._MENTION.sub("@\u200b\\1", text)

    @staticmethod
    def _keep_link_or_escape(match: re.Match[str], /) -> str:
        """
        Hands a link back untouched and puts a backslash before anything
        else, for the one case a template cannot express.
        """
        return match[1] or "\\" + match[2]

__all__ = ["Markdown"]