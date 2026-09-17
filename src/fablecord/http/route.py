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

from urllib.parse import quote
from typing import Final

type MajorParameter = int | str | tuple[int | str, ...] | None

class CompiledRoute:
    """
    A route with its parameters filled in, ready to be requested.

    Attributes
    -----------
    route: :class:`Route`
        The template this came from. It carries the method and the key
        under which the rate limiter remembers Discord's bucket.
    path: :class:`str`
        The path below :attr:`Route.BASE`, strings already percent-encoded.
    major: Union[:class:`int`, :class:`str`, Tuple[Union[:class:`int`, :class:`str`], ...], None]
        The channel, guild or webhook the request touches, a webhook
        together with its token. Discord counts every one of them on its
        own, so two requests only share a limit when both the route's
        bucket and this value match. ``None`` for a route without one.
    """

    __slots__ = ["route", "path", "major"]

    def __init__(self, route: Route, path: str, major: MajorParameter, /) -> None:
        self.route = route
        self.path = path
        self.major = major

    @property
    def method(self) -> str:
        """
        :class:`str`: The HTTP method of the route.
        """
        return self.route.method

    @property
    def url(self) -> str:
        """
        :class:`str`: The absolute URL to request.
        """
        return Route.BASE + self.path

    def __repr__(self) -> str:
        return f"<CompiledRoute {self.route.method} {self.path}>"

class Route:
    """
    One REST endpoint as a template, created once and compiled per request.

    A parameter whose name ends in ``_id`` is a snowflake. It is formatted
    as an integer, so nothing but digits can reach the path through it.
    Every other parameter, an emoji, a webhook token, an invite code,
    is a string and gets percent-encoded, slashes included.

    Parameters
    -----------
    method: :class:`str`
        The HTTP method, uppercase.
    path: :class:`str`
        The path below :attr:`BASE` with its parameters in braces, such
        as ``/channels/{channel_id}/messages/{message_id}``. Interaction
        routes name their parameters ``webhook_id`` and ``webhook_token``
        as well, Discord limits them per token like a webhook.
    variant: Optional[:class:`str`]
        Tells two uses of the same method and path apart where Discord
        limits them separately, deleting a message older than two weeks
        for one. It only ends up in :attr:`key`.

    Raises
    -------
    ValueError
        The path does not start with a slash.

    Attributes
    -----------
    method: :class:`str`
        The HTTP method.
    path: :class:`str`
        The path template as it was given.
    variant: Optional[:class:`str`]
        The variant as it was given.
    key: :class:`str`
        Method, path template and variant in one string. The rate limiter
        files the bucket Discord reports for this route under it.
    """

    __slots__ = ["method", "path", "variant", "key", "_count", "_template", "_strings", "_majors", "_bare"]

    BASE: Final = "https://discord.com/api/v10"
    MAJOR_PARAMETERS: Final = ["channel_id", "guild_id", "webhook_id", "webhook_token"]
    _PARAMETER: Final = re.compile(r"\{(?P<name>\w+)\}")
    _UNRESERVED: Final = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.~-"
    _QUOTED: Final[dict[str, str]] = {}

    def __init__(self, method: str, path: str, /, *, variant: str | None = None) -> None:
        if not path.startswith("/"):
            raise ValueError(f"the path {path!r} does not start with a slash")

        self.method = method
        self.path = path
        self.variant = variant
        self.key = f"{method} {path}" if variant is None else f"{method} {path} ({variant})"
        self._count = -1

    def compile(self, *values: int | str) -> CompiledRoute:
        """
        Fills in the parameters, in the order they appear in the path.

        Parameters
        -----------
        \\*values: Union[:class:`int`, :class:`str`]
            One value per parameter of the path.

        Raises
        -------
        TypeError
            The number of values does not fit the path, a snowflake
            parameter got something that is not a number, or a string
            parameter got something that is not a string.
        ValueError
            A string parameter is empty, ``.`` or ``..``, or it cannot be
            encoded as UTF-8.

        Returns
        --------
        :class:`CompiledRoute`
            The route for these values. A path without parameters always
            returns the same object.
        """
        if len(values) != self._count:
            if self._count >= 0:
                raise TypeError(f"{self.key} takes {self._count} values, not {len(values)}")

            self._prepare()

            return self.compile(*values)

        bare = self._bare
        if bare is not None:
            return bare

        majors = self._majors
        if not majors:
            major = None
        elif len(majors) == 1:
            major = values[majors[0]]
        else:
            major = tuple([values[index] for index in majors])

        strings = self._strings
        if strings:
            encoded = list(values)

            for index in strings:
                encoded[index] = self._quote(encoded[index])

            values = tuple(encoded)

        return CompiledRoute(self, self._template % values, major)

    def __repr__(self) -> str:
        return f"<Route {self.key}>"

    def _prepare(self) -> None:
        """
        Takes the path apart on first use. A library defines a few
        hundred routes and a bot touches a handful, so defining one costs
        next to nothing and only the used ones pay for this.

        A snowflake becomes ``%d`` in the template, which is what makes
        anything but an integer raise while formatting.
        """
        pieces = self._PARAMETER.split(self.path.replace("%", "%%"))
        names = pieces[1::2]
        pieces[1::2] = ["%d" if name.endswith("_id") else "%s" for name in names]

        self._template = "".join(pieces)
        self._strings = [index for index, name in enumerate(names) if not name.endswith("_id")]
        self._majors = [index for index, name in enumerate(names) if name in self.MAJOR_PARAMETERS]
        self._bare = None if names else CompiledRoute(self, self.path, None)
        self._count = len(names)

    @staticmethod
    def _quote(value: int | str, /) -> str:
        """
        Percent-encodes a string parameter.

        An emoji is looked up first, a bot reacts with the same few over
        and over and the encoded form is remembered for up to 1024 of
        them. Tokens and codes consist of unreserved characters: deleting
        those from the encoded bytes leaves nothing, and they pass as they
        are. An empty string or a dot segment would change which endpoint
        the path points at and is refused.
        """
        if not isinstance(value, str):
            raise TypeError(f"a string parameter got {value!r}")

        quoted = Route._QUOTED.get(value)
        if quoted is not None:
            return quoted

        if value in ("", ".", ".."):
            raise ValueError(f"a string parameter cannot be {value!r}")

        if not value.encode().translate(None, Route._UNRESERVED):
            return value

        quoted = quote(value, safe="")

        if len(Route._QUOTED) < 1024:
            Route._QUOTED[value] = quoted

        return quoted

__all__ = ["Route", "CompiledRoute", "MajorParameter"]