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

class FablecordException(Exception):
    """
    Base class for every exception the library raises.

    Catch this to handle anything that comes out of Fablecord without
    caring what exactly went wrong.
    """

class ClientException(FablecordException):
    """
    Raised when an operation on the client fails because of how it was used.

    Usually the client is in the wrong state for the call, for example
    sending something before the connection is up.
    """

class InvalidData(ClientException):
    """
    Raised when Discord sends data the library cannot make sense of.

    This should not happen. If it does, it is either a bug here or an API
    change that has not been handled yet.
    """

__all__ = ["FablecordException", "ClientException", "InvalidData"]