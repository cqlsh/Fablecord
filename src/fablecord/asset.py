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

from typing import Final, Self
from os import PathLike
from io import BufferedIOBase

from .errors.base import ClientException
from .http.client import RESTClient
from .utils.missing import MISSING

_CDN: Final = "https://cdn.discordapp.com"
_STATIC_FORMATS: Final = frozenset(["png", "jpg", "jpeg", "webp"])
_ANIMATED_FORMATS: Final = frozenset(["png", "jpg", "jpeg", "webp", "gif"])
_STICKER_APPLICATION: Final = 710982414301790216

class Asset:
    """
    An image on Discord's CDN: an avatar, an icon, a banner, an emoji.

    The URL is built once from the object the asset belongs to and the
    hash Discord sent. :meth:`with_size` and :meth:`with_format` give a
    new asset with a different query, :meth:`read` downloads the bytes.
    Two assets are equal when their URLs are.

    Attributes
    -----------
    url: :class:`str`
        The full URL, with the format and the size.
    key: :class:`str`
        The hash the URL was built from, or the ID or index of what it
        shows when there is no hash.
    animated: :class:`bool`
        Whether the image is a GIF, which only avatars, banners,
        icons and emojis can be.
    """

    __slots__ = ["url", "key", "animated", "_rest"]

    BASE: Final = _CDN

    def __init__(self, rest: RESTClient | None, url: str, key: str, animated: bool, /) -> None:
        self._rest = rest
        self.url = url
        self.key = key
        self.animated = animated

    @classmethod
    def from_avatar(cls, rest: RESTClient | None, user_id: int, hash: str, /) -> Self:
        """
        A user's avatar at 1024 pixels.
        """
        animated = hash.startswith("a_")

        return cls(rest, f"{_CDN}/avatars/{user_id}/{hash}.{'gif' if animated else 'png'}?size=1024", hash, animated)

    @classmethod
    def from_default_avatar(cls, rest: RESTClient | None, index: int, /) -> Self:
        """
        One of the default avatars, by its index from ``0`` to ``5``.
        """
        return cls(rest, f"{_CDN}/embed/avatars/{index}.png", str(index), False)

    @classmethod
    def from_guild_avatar(cls, rest: RESTClient | None, guild_id: int, user_id: int, hash: str, /) -> Self:
        """
        The avatar a member set for one guild, at 1024 pixels.
        """
        animated = hash.startswith("a_")

        return cls(rest, f"{_CDN}/guilds/{guild_id}/users/{user_id}/avatars/{hash}.{'gif' if animated else 'png'}?size=1024", hash, animated)

    @classmethod
    def from_guild_banner(cls, rest: RESTClient | None, guild_id: int, user_id: int, hash: str, /) -> Self:
        """
        The banner a member set for one guild, at 1024 pixels.
        """
        animated = hash.startswith("a_")

        return cls(rest, f"{_CDN}/guilds/{guild_id}/users/{user_id}/banners/{hash}.{'gif' if animated else 'png'}?size=1024", hash, animated)

    @classmethod
    def from_user_banner(cls, rest: RESTClient | None, user_id: int, hash: str, /) -> Self:
        """
        A user's profile banner at 512 pixels.
        """
        animated = hash.startswith("a_")

        return cls(rest, f"{_CDN}/banners/{user_id}/{hash}.{'gif' if animated else 'png'}?size=512", hash, animated)

    @classmethod
    def from_avatar_decoration(cls, rest: RESTClient | None, hash: str, /) -> Self:
        """
        An avatar decoration at 96 pixels. They are animated PNGs, so
        the asset counts as animated even though the format is PNG.
        """
        return cls(rest, f"{_CDN}/avatar-decoration-presets/{hash}.png?size=96", hash, True)

    @classmethod
    def from_guild_image(cls, rest: RESTClient | None, guild_id: int, hash: str, path: str, /) -> Self:
        """
        A guild's icon, splash, discovery splash or banner at 1024
        pixels, ``path`` being ``icons``, ``splashes``,
        ``discovery-splashes`` or ``banners``.
        """
        animated = hash.startswith("a_")

        return cls(rest, f"{_CDN}/{path}/{guild_id}/{hash}.{'gif' if animated else 'png'}?size=1024", hash, animated)

    @classmethod
    def from_icon(cls, rest: RESTClient | None, object_id: int, hash: str, path: str, /) -> Self:
        """
        The icon of an application, team or role at 1024 pixels,
        ``path`` being ``app``, ``team`` or ``role``.
        """
        return cls(rest, f"{_CDN}/{path}-icons/{object_id}/{hash}.png?size=1024", hash, False)

    @classmethod
    def from_cover_image(cls, rest: RESTClient | None, application_id: int, hash: str, /) -> Self:
        """
        An application's store cover image at 1024 pixels.
        """
        return cls(rest, f"{_CDN}/app-assets/{application_id}/store/{hash}.png?size=1024", hash, False)

    @classmethod
    def from_scheduled_event_cover(cls, rest: RESTClient | None, event_id: int, hash: str, /) -> Self:
        """
        The cover image of a scheduled event at 1024 pixels.
        """
        return cls(rest, f"{_CDN}/guild-events/{event_id}/{hash}.png?size=1024", hash, False)

    @classmethod
    def from_sticker_banner(cls, rest: RESTClient | None, banner_id: int, /) -> Self:
        """
        The banner of a sticker pack in its own size.
        """
        return cls(rest, f"{_CDN}/app-assets/{_STICKER_APPLICATION}/store/{banner_id}.png", str(banner_id), False)

    @classmethod
    def from_emoji(cls, rest: RESTClient | None, emoji_id: int, animated: bool, /) -> Self:
        """
        A custom emoji in its own size.
        """
        return cls(rest, f"{_CDN}/emojis/{emoji_id}.{'gif' if animated else 'png'}", str(emoji_id), animated)

    @classmethod
    def from_sticker(cls, rest: RESTClient | None, sticker_id: int, extension: str, animated: bool, /) -> Self:
        """
        A sticker in its own size, ``extension`` being ``png`` for PNG
        and APNG stickers, ``json`` for Lottie and ``gif`` for GIF.
        """
        return cls(rest, f"{_CDN}/stickers/{sticker_id}.{extension}", str(sticker_id), animated)

    def is_animated(self) -> bool:
        """
        Whether the image is a GIF, the same as :attr:`animated`.
        """
        return self.animated

    def with_size(self, size: int, /) -> Self:
        """
        The same image at another size.

        Parameters
        -----------
        size: :class:`int`
            A power of two from 16 to 4096.

        Raises
        -------
        ValueError
            The size is not one the CDN serves.
        """
        if size < 16 or size > 4096 or size & (size - 1):
            raise ValueError("size must be a power of two from 16 to 4096")

        base, format, _ = self._parts()

        return type(self)(self._rest, f"{base}.{format}?size={size}", self.key, self.animated)

    def with_format(self, format: str, /) -> Self:
        """
        The same image in another format.

        Parameters
        -----------
        format: :class:`str`
            ``png``, ``jpg``, ``jpeg`` or ``webp``, and ``gif`` for an
            animated asset.

        Raises
        -------
        ValueError
            The format is not one the CDN serves for this asset.
        """
        allowed = _ANIMATED_FORMATS if self.animated else _STATIC_FORMATS

        if format not in allowed:
            raise ValueError(f"format must be one of {sorted(allowed)}")

        base, _, size = self._parts()
        url = f"{base}.{format}?size={size}" if size else f"{base}.{format}"

        return type(self)(self._rest, url, self.key, self.animated)

    def with_static_format(self, format: str, /) -> Self:
        """
        The same image in another format unless it is animated, which
        keeps its GIF.
        """
        if self.animated:
            return self

        return self.with_format(format)

    def replace(self, *, size: int = MISSING, format: str = MISSING, static_format: str = MISSING) -> Self:
        """
        The same image with a new size, format or both.

        Parameters
        -----------
        size: :class:`int`
            A power of two from 16 to 4096.
        format: :class:`str`
            The format for every asset, ``gif`` only for animated ones.
        static_format: :class:`str`
            The format for an asset that is not animated, which wins
            over ``format`` for those.

        Raises
        -------
        ValueError
            The size or a format is not one the CDN serves.
        """
        asset = self

        if static_format is not MISSING and not self.animated:
            asset = asset.with_format(static_format)
        elif format is not MISSING:
            asset = asset.with_format(format)

        if size is not MISSING:
            asset = asset.with_size(size)

        return asset

    async def read(self) -> bytes:
        """
        |coro|

        Downloads the image.

        Raises
        -------
        ClientException
            The asset was built without a client to download with.
        NotFound
            The image is gone from the CDN.
        HTTPException
            The download failed.
        """
        rest = self._rest
        if rest is None:
            raise ClientException("this asset has no client to download with")

        return await rest.get_from_cdn(self.url)

    async def save(self, fp: str | PathLike[str] | BufferedIOBase, /, *, seek_begin: bool = True) -> int:
        """
        |coro|

        Downloads the image into a file.

        Parameters
        -----------
        fp: Union[:class:`str`, :class:`os.PathLike`, :class:`io.BufferedIOBase`]
            A path to write, or an open binary file to write into.
        seek_begin: :class:`bool`
            Whether to seek an open file back to the start afterwards.

        Returns
        --------
        :class:`int`
            The number of bytes written.
        """
        data = await self.read()

        if isinstance(fp, BufferedIOBase):
            written = fp.write(data)

            if seek_begin:
                fp.seek(0)

            return written

        with open(fp, "wb") as file:
            return file.write(data)

    def _parts(self) -> tuple[str, str, int]:
        """
        Takes the URL apart into everything before the extension, the
        extension and the size, ``0`` without one. Only the extension
        and the query hold a dot or a question mark past the host.
        """
        url = self.url
        dot = url.rindex(".")
        question = url.find("?", dot)

        if question < 0:
            return url[:dot], url[dot + 1:], 0

        return url[:dot], url[dot + 1:question], int(url[question + 6:])

    def __str__(self) -> str:
        return self.url

    def __len__(self) -> int:
        return len(self.url)

    def __repr__(self) -> str:
        return f"<Asset url={self.url!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Asset) and other.url == self.url

    def __hash__(self) -> int:
        return hash(self.url)

__all__ = ["Asset"]