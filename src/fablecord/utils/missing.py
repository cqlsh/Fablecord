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

from typing import Any

class _MissingSentinel:
    """
    A sentinel that marks a value as not provided.

    This is used as the default for parameters where ``None`` is itself a
    meaningful value, for example when editing a message and clearing its
    content is different from leaving it untouched. Compare against the
    :data:`MISSING` instance with ``is``, never with ``==``.

    Copying, deep copying or unpickling the sentinel always yields the same
    instance, so identity checks stay reliable across those operations.
    """

    __slots__ = ()

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "..."

    def __copy__(self) -> _MissingSentinel:
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> _MissingSentinel:
        return self

    def __reduce__(self) -> str:
        return "MISSING"

MISSING: Any = _MissingSentinel()

__all__ = ["MISSING"]