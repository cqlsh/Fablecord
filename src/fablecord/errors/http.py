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

from .base import FablecordException, ClientException
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from ..net.http import HTTPResponse

class HTTPException(FablecordException):
    """
    Raised when Discord answers a request with an error.

    Printed, it reads like ``404 Not Found (error code: 10008): Unknown
    Message``, and for a rejected payload every field Discord objected
    to follows on its own line. That text is only put together when
    something asks for it, so an error caught and dropped costs little.

    Attributes
    -----------
    response: :class:`~fablecord.net.HTTPResponse`
        The response that failed.
    status: :class:`int`
        The status code of the response.
    code: :class:`int`
        The error code Discord lists in its documentation, ``0`` when
        the response did not carry one.
    message: :class:`str`
        Discord's message alone, ``Unknown Message`` or ``Invalid Form
        Body``, or the body as text when it was not JSON.
    errors: Optional[Dict[:class:`str`, Any]]
        The ``errors`` object as Discord sent it, nested by field, when
        the response had one.
    """

    def __init__(self, response: HTTPResponse, data: dict[str, Any] | str | None = None, /) -> None:
        self.response = response
        self.status = response.status

        if isinstance(data, dict):
            self.code: int = data.get("code", 0)
            self.errors: dict[str, Any] | None = data.get("errors")
            self.message: str = str(data.get("message", ""))
        else:
            self.code = 0
            self.errors = None
            self.message = data or ""

        super().__init__()

    @property
    def text(self) -> str:
        """
        :class:`str`: Discord's message, followed by the field errors,
        one per line as ``In embeds.0.title: Must be 256 or fewer in
        length.``
        """
        errors = self.errors
        if not errors:
            return self.message

        lines = [self.message]
        self._flatten(errors, "", lines)

        return "\n".join(lines)

    def __str__(self) -> str:
        args = self.args
        if args:
            return args[0]

        text = self.text
        if text:
            message = f"{self.status} {self.response.reason} (error code: {self.code}): {text}"
        else:
            message = f"{self.status} {self.response.reason} (error code: {self.code})"

        self.args = (message,)

        return message

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)!r})"

    @staticmethod
    def _flatten(errors: dict[str, Any], prefix: str, lines: list[str], /) -> None:
        """
        Walks Discord's nested ``errors`` object and writes one line per
        field that was rejected, with the path to it in dots.
        """
        for name, value in errors.items():
            path = f"{prefix}.{name}" if prefix else name

            if isinstance(value, dict):
                nested = cast(dict[str, Any], value)

                if "_errors" in nested:
                    lines.append(f"In {path}: {HTTPException._messages(nested['_errors'])}")
                else:
                    HTTPException._flatten(nested, path, lines)
            else:
                lines.append(f"In {path}: {value}")

    @staticmethod
    def _messages(leaves: Any, /) -> str:
        """
        Joins the messages of one field's ``_errors`` list, and shrugs at
        anything that is not the list Discord documents.
        """
        if not isinstance(leaves, list):
            return str(leaves)

        messages: list[str] = []
        for entry in cast(list[Any], leaves):
            if isinstance(entry, dict):
                messages.append(str(cast(dict[str, Any], entry).get("message", "")))
            else:
                messages.append(str(entry))

        return " ".join(messages)

class BadRequest(HTTPException):
    """
    Raised when Discord rejects what was sent, status 400.

    Usually a field was too long, missing or of the wrong kind, and
    :attr:`~HTTPException.text` names every one Discord complained about.
    """

class Forbidden(HTTPException):
    """
    Raised when the bot lacks the permission, status 403.
    """

class NotFound(HTTPException):
    """
    Raised when the resource does not exist, status 404, a deleted
    message or a channel the bot cannot see among them.
    """

class DiscordServerError(HTTPException):
    """
    Raised when Discord itself failed, status 500 and above, after the
    request was retried.
    """

class RateLimited(FablecordException):
    """
    Raised when a request would have to wait longer for a rate limit than
    the client allows.

    It can be raised before the request goes out, so it does not subclass
    :exc:`HTTPException`.

    Attributes
    -----------
    retry_after: :class:`float`
        The seconds to wait before the request has a chance.
    """

    def __init__(self, retry_after: float, /) -> None:
        self.retry_after = retry_after

        super().__init__(f"Too many requests. Retry in {retry_after:.2f} seconds.")

class LoginFailure(ClientException):
    """
    Raised when Discord rejects the token at login.
    """

__all__ = ["HTTPException", "BadRequest", "Forbidden", "NotFound", "DiscordServerError", "RateLimited", "LoginFailure"]