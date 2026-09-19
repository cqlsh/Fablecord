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

import zlib
import re

from json.decoder import JSONDecoder
from collections.abc import Callable
from typing import Any, Final
from sys import intern

try:
    from fablecord._speedups.gateway import peek as _peek
except ImportError:
    _peek: Callable[[bytes], tuple[int, int | None, str | None] | None] | None = None

_DECODE: Final = JSONDecoder().raw_decode
_SUFFIX: Final = b"\x00\x00\xff\xff"
_HEAD: Final = re.compile(rb'\{"t":(?:null|"(?P<name>[A-Z_0-9]+)"),"s":(?:null|(?P<sequence>\d+)),"op":(?P<op>\d+)')
_SMALL: Final = 256
_BLOCK: Final = 8192

class Decoder:
    """
    Turns what the gateway sends into payloads, and reads the envelope
    of a payload without parsing it.

    Discord compresses the connection as one zlib stream: every payload
    ends in a sync flush, and a payload may arrive in more than one
    WebSocket message. :meth:`feed` collects and inflates them. A small
    message inflates into a small buffer, which is cheaper than the
    32 KB block zlib starts with, and the rare payload that outgrows it
    is finished in a second step. :meth:`peek` then reads the opcode,
    sequence number and event name from the first bytes of the JSON,
    in C when :mod:`fablecord._speedups` was compiled and with a
    regular expression otherwise, which is enough to tell whether
    anyone wants the event before it is parsed at all. Event names are
    interned, so the tables an event is looked up in compare by
    identity. A payload that does not start the way Discord writes
    them is parsed instead, so nothing depends on the order of its
    keys.
    """

    __slots__ = ["_inflator", "_inflate", "_parts"]

    def __init__(self) -> None:
        self._inflator = zlib.decompressobj()
        self._inflate = self._inflator.decompress
        self._parts: list[bytes] = []

    def feed(self, message: bytes, /) -> bytes | None:
        """
        Takes one WebSocket message of the stream.

        Parameters
        -----------
        message: :class:`bytes`
            The binary message as it came off the connection.

        Raises
        -------
        zlib.error
            The stream is corrupt, which means the connection has to be
            replaced.

        Returns
        --------
        Optional[:class:`bytes`]
            The JSON of the payload the message completed, ``None`` when
            more messages have to come first.
        """
        parts = self._parts
        if parts:
            parts.append(message)

            if len(message) < 4:
                message = b"".join(parts)

            if not message.endswith(_SUFFIX):
                return None

            message = b"".join(parts)
            parts.clear()
        elif not message.endswith(_SUFFIX):
            parts.append(message)

            return None

        if len(message) >= _SMALL:
            return self._inflate(message)

        payload = self._inflate(message, _BLOCK)
        if len(payload) < _BLOCK:
            return payload

        return self._drain(payload=payload)

    def peek(self, payload: bytes, /) -> tuple[int, int | None, str | None]:
        """
        Reads the envelope of a payload from its first bytes.

        Parameters
        -----------
        payload: :class:`bytes`
            The JSON of one payload.

        Returns
        --------
        Tuple[:class:`int`, Optional[:class:`int`], Optional[:class:`str`]]
            The opcode, the sequence number and the event name. The
            latter two are ``None`` on anything but a dispatch, and the
            name is the same object for every payload of an event.
        """
        if _peek is not None:
            envelope = _peek(payload)
        else:
            envelope = self._scan(payload)

        if envelope is None:
            parsed = _DECODE(payload.decode())[0]

            return parsed["op"], parsed.get("s"), parsed.get("t")

        return envelope

    def reset(self) -> None:
        """
        Starts a fresh stream, which every new connection needs since
        Discord compresses each one from scratch.
        """
        self._inflator = zlib.decompressobj()
        self._inflate = self._inflator.decompress
        self._parts.clear()

    @staticmethod
    def load(payload: bytes, /) -> dict[str, Any]:
        """
        Parses a whole payload.

        Parameters
        -----------
        payload: :class:`bytes`
            The JSON of one payload.
        """
        return _DECODE(payload.decode())[0]

    @staticmethod
    def _scan(payload: bytes, /) -> tuple[int, int | None, str | None] | None:
        """
        Reads the envelope with a regular expression when the C helper
        was not compiled, with the same result.
        """
        match = _HEAD.match(payload)
        if match is None:
            return None

        raw_name, raw_sequence, raw_op = match.groups()

        name = None if raw_name is None else intern(raw_name.decode())
        sequence = None if raw_sequence is None else int(raw_sequence)

        return int(raw_op), sequence, name

    def _drain(self, *, payload: bytes) -> bytes:
        """
        Finishes a payload that outgrew the small buffer, which takes a
        very repetitive one from a tiny message.
        """
        parts = [payload]
        inflator = self._inflator

        while True:
            more = inflator.decompress(inflator.unconsumed_tail)

            if not more:
                return b"".join(parts)

            parts.append(more)

__all__ = ["Decoder"]