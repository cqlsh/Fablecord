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

from typing import Any, Literal, Self
from datetime import datetime

from .flags.message import EmbedFlags
from .utils.time import Time
from .colour import Colour

type EmbedType = Literal["rich", "image", "video", "gifv", "article", "link", "poll_result"]

class EmbedFooter:
    """
    The line at the bottom of an embed.

    Attributes
    -----------
    text: Optional[:class:`str`]
        The text of the footer.
    icon_url: Optional[:class:`str`]
        The small icon in front of the text.
    proxy_icon_url: Optional[:class:`str`]
        Discord's own copy of that icon, only on an embed that came
        from Discord.
    """

    __slots__ = ["text", "icon_url", "proxy_icon_url"]

    def __init__(self, data: dict[str, Any], /) -> None:
        get = data.get

        self.text = get("text")
        self.icon_url = get("icon_url")
        self.proxy_icon_url = get("proxy_icon_url")

    def __repr__(self) -> str:
        return f"<EmbedFooter text={self.text!r} icon_url={self.icon_url!r}>"

class EmbedMedia:
    """
    The image, thumbnail or video of an embed.

    Attributes
    -----------
    url: Optional[:class:`str`]
        Where the media comes from.
    proxy_url: Optional[:class:`str`]
        Discord's own copy, only on an embed that came from Discord.
    width: Optional[:class:`int`]
        The width in pixels, which only Discord fills in.
    height: Optional[:class:`int`]
        The height in pixels, which only Discord fills in.
    """

    __slots__ = ["url", "proxy_url", "width", "height", "_flags"]

    def __init__(self, data: dict[str, Any], /) -> None:
        get = data.get

        self.url = get("url")
        self.proxy_url = get("proxy_url")
        self.width = get("width")
        self.height = get("height")
        self._flags = get("flags", 0)

    @property
    def flags(self) -> EmbedFlags:
        """
        :class:`EmbedFlags`: What Discord marked about this media, such
        as explicit content.
        """
        flags = EmbedFlags.__new__(EmbedFlags)
        flags.value = self._flags

        return flags

    def __repr__(self) -> str:
        return f"<EmbedMedia url={self.url!r} width={self.width} height={self.height}>"

class EmbedProvider:
    """
    Who published what an embed links to, which only Discord fills in.

    Attributes
    -----------
    name: Optional[:class:`str`]
        The name of the site.
    url: Optional[:class:`str`]
        Its address.
    """

    __slots__ = ["name", "url"]

    def __init__(self, data: dict[str, Any], /) -> None:
        get = data.get

        self.name = get("name")
        self.url = get("url")

    def __repr__(self) -> str:
        return f"<EmbedProvider name={self.name!r} url={self.url!r}>"

class EmbedAuthor:
    """
    The line above the title of an embed.

    Attributes
    -----------
    name: Optional[:class:`str`]
        The name shown.
    url: Optional[:class:`str`]
        Where the name links to.
    icon_url: Optional[:class:`str`]
        The small icon in front of the name.
    proxy_icon_url: Optional[:class:`str`]
        Discord's own copy of that icon, only on an embed that came
        from Discord.
    """

    __slots__ = ["name", "url", "icon_url", "proxy_icon_url"]

    def __init__(self, data: dict[str, Any], /) -> None:
        get = data.get

        self.name = get("name")
        self.url = get("url")
        self.icon_url = get("icon_url")
        self.proxy_icon_url = get("proxy_icon_url")

    def __repr__(self) -> str:
        return f"<EmbedAuthor name={self.name!r} url={self.url!r}>"

class EmbedField:
    """
    One field of an embed.

    Attributes
    -----------
    name: :class:`str`
        The heading of the field.
    value: :class:`str`
        The text below it.
    inline: :class:`bool`
        Whether the field shares its row with the fields next to it,
        three of them at most.
    """

    __slots__ = ["name", "value", "inline"]

    def __init__(self, data: dict[str, Any], /) -> None:
        self.name = data["name"]
        self.value = data["value"]
        self.inline = data.get("inline", True)

    def __repr__(self) -> str:
        return f"<EmbedField name={self.name!r} inline={self.inline}>"

class Embed:
    """
    The rich block a message can carry, built piece by piece.

    A message takes up to ten of them, together at most 6000
    characters, which :func:`len` counts. Every method that adds
    something returns the embed, so calls chain. The parts Discord
    fills in on a link, the provider and the video, are read-only
    here.

    Unlike discord.py, a part that is not set is ``None`` rather than
    an empty stand-in, so ``embed.footer.text`` needs a footer to
    exist and the type checker sees the difference.

    Every part stays as Discord sent it until it is read, and the
    object built for it is kept, so an embed nobody looks into costs
    nothing beyond the parsing and one that is read pays for each
    part once.

    Parameters
    -----------
    colour: Optional[Union[:class:`Colour`, :class:`int`]]
        The stripe down the left side.
    color: Optional[Union[:class:`Colour`, :class:`int`]]
        The same under the other spelling.
    title: Optional[:class:`str`]
        The heading, at most 256 characters.
    type: :class:`str`
        What kind of embed this is, ``rich`` for one a bot builds.
    url: Optional[:class:`str`]
        Where the title links to.
    description: Optional[:class:`str`]
        The text below the title, at most 4096 characters.
    timestamp: Optional[:class:`datetime.datetime`]
        The time shown in the footer. A naive one is taken as UTC.

    Attributes
    -----------
    title: Optional[:class:`str`]
        The heading.
    type: :class:`str`
        What kind of embed this is.
    url: Optional[:class:`str`]
        Where the title links to.
    description: Optional[:class:`str`]
        The text below the title.
    """

    __slots__ = [
        "title",
        "type",
        "url",
        "description",
        "_colour",
        "_timestamp",
        "_footer",
        "_image",
        "_thumbnail",
        "_video",
        "_provider",
        "_author",
        "_fields",
        "_flags",
        "_built_footer",
        "_built_image",
        "_built_thumbnail",
        "_built_video",
        "_built_provider",
        "_built_author",
        "_built_fields"
    ]

    def __init__(
        self,
        *,
        colour: Colour | int | None = None,
        color: Colour | int | None = None,
        title: str | None = None,
        type: EmbedType = "rich",
        url: str | None = None,
        description: str | None = None,
        timestamp: datetime | None = None
    ) -> None:
        value = colour if colour is not None else color

        self.title = title
        self.type = type
        self.url = url
        self.description = description
        self._colour = Colour(value) if isinstance(value, int) else value
        self._timestamp = timestamp
        self._footer: dict[str, Any] | None = None
        self._image: dict[str, Any] | None = None
        self._thumbnail: dict[str, Any] | None = None
        self._video: dict[str, Any] | None = None
        self._provider: dict[str, Any] | None = None
        self._author: dict[str, Any] | None = None
        self._fields: list[dict[str, Any]] | None = None
        self._flags = 0

        self._built_footer: EmbedFooter | None = None
        self._built_image: EmbedMedia | None = None
        self._built_thumbnail: EmbedMedia | None = None
        self._built_video: EmbedMedia | None = None
        self._built_provider: EmbedProvider | None = None
        self._built_author: EmbedAuthor | None = None
        self._built_fields: list[EmbedField] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], /) -> Self:
        """
        Builds an embed from the payload Discord sends or takes.

        Parameters
        -----------
        data: Dict[:class:`str`, Any]
            The payload. What it holds is taken as it is, the parts
            Discord fills in included.
        """
        self = cls.__new__(cls)
        get = data.get

        self.title = get("title")
        self.type = get("type", "rich")
        self.url = get("url")
        self.description = get("description")

        colour = get("color", get("colour"))
        self._colour = None if colour is None else Colour(colour)

        stamp = get("timestamp")
        self._timestamp = None if stamp is None else Time.parse(stamp)

        self._footer = get("footer")
        self._image = get("image")
        self._thumbnail = get("thumbnail")
        self._video = get("video")
        self._provider = get("provider")
        self._author = get("author")
        self._fields = get("fields")
        self._flags = get("flags", 0)

        self._built_footer = None
        self._built_image = None
        self._built_thumbnail = None
        self._built_video = None
        self._built_provider = None
        self._built_author = None
        self._built_fields = None

        return self

    def to_dict(self) -> dict[str, Any]:
        """
        The payload for this embed, ready to send. Only what is set
        goes in.
        """
        data: dict[str, Any] = {}

        if self.title is not None:
            data["title"] = self.title

        if self.type:
            data["type"] = self.type

        if self.description is not None:
            data["description"] = self.description

        if self.url is not None:
            data["url"] = self.url

        colour = self._colour
        if colour is not None:
            data["color"] = colour.value

        timestamp = self._timestamp
        if timestamp is not None:
            data["timestamp"] = Time.serialize(timestamp)

        if self._footer is not None:
            data["footer"] = self._footer

        if self._image is not None:
            data["image"] = self._image

        if self._thumbnail is not None:
            data["thumbnail"] = self._thumbnail

        if self._video is not None:
            data["video"] = self._video

        if self._provider is not None:
            data["provider"] = self._provider

        if self._author is not None:
            data["author"] = self._author

        if self._fields is not None:
            data["fields"] = self._fields

        return data

    def copy(self) -> Self:
        """
        A copy of the embed that can be changed on its own. The parts
        that hold nothing but strings are shared, so setting one on
        either embed does not touch the other.
        """
        other = self.__class__.__new__(self.__class__)

        other.title = self.title
        other.type = self.type
        other.url = self.url
        other.description = self.description
        other._colour = self._colour
        other._timestamp = self._timestamp
        other._footer = self._footer
        other._image = self._image
        other._thumbnail = self._thumbnail
        other._video = self._video
        other._provider = self._provider
        other._author = self._author
        other._fields = None if self._fields is None else self._fields.copy()
        other._flags = self._flags

        other._built_footer = None
        other._built_image = None
        other._built_thumbnail = None
        other._built_video = None
        other._built_provider = None
        other._built_author = None
        other._built_fields = None

        return other

    @property
    def colour(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: The stripe down the left side.
        """
        return self._colour

    @colour.setter
    def colour(self, value: Colour | int | None) -> None:
        self._colour = Colour(value) if isinstance(value, int) else value

    @property
    def color(self) -> Colour | None:
        """
        Optional[:class:`Colour`]: :attr:`colour` under the other
        spelling.
        """
        return self._colour

    @color.setter
    def color(self, value: Colour | int | None) -> None:
        self._colour = Colour(value) if isinstance(value, int) else value

    @property
    def timestamp(self) -> datetime | None:
        """
        Optional[:class:`datetime.datetime`]: The time shown in the
        footer.
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime | None) -> None:
        self._timestamp = value

    @property
    def flags(self) -> EmbedFlags:
        """
        :class:`EmbedFlags`: What Discord marked about this embed.
        """
        flags = EmbedFlags.__new__(EmbedFlags)
        flags.value = self._flags

        return flags

    @property
    def footer(self) -> EmbedFooter | None:
        """
        Optional[:class:`EmbedFooter`]: The line at the bottom,
        ``None`` when there is none.
        """
        built = self._built_footer
        if built is not None:
            return built

        data = self._footer
        if data is None:
            return None

        built = self._built_footer = EmbedFooter(data)

        return built

    @property
    def image(self) -> EmbedMedia | None:
        """
        Optional[:class:`EmbedMedia`]: The large image below the
        fields, ``None`` when there is none.
        """
        built = self._built_image
        if built is not None:
            return built

        data = self._image
        if data is None:
            return None

        built = self._built_image = EmbedMedia(data)

        return built

    @property
    def thumbnail(self) -> EmbedMedia | None:
        """
        Optional[:class:`EmbedMedia`]: The small image in the top right
        corner, ``None`` when there is none.
        """
        built = self._built_thumbnail
        if built is not None:
            return built

        data = self._thumbnail
        if data is None:
            return None

        built = self._built_thumbnail = EmbedMedia(data)

        return built

    @property
    def video(self) -> EmbedMedia | None:
        """
        Optional[:class:`EmbedMedia`]: The video of a link embed, which
        only Discord sets.
        """
        built = self._built_video
        if built is not None:
            return built

        data = self._video
        if data is None:
            return None

        built = self._built_video = EmbedMedia(data)

        return built

    @property
    def provider(self) -> EmbedProvider | None:
        """
        Optional[:class:`EmbedProvider`]: Who published what a link
        embed points at, which only Discord sets.
        """
        built = self._built_provider
        if built is not None:
            return built

        data = self._provider
        if data is None:
            return None

        built = self._built_provider = EmbedProvider(data)

        return built

    @property
    def author(self) -> EmbedAuthor | None:
        """
        Optional[:class:`EmbedAuthor`]: The line above the title,
        ``None`` when there is none.
        """
        built = self._built_author
        if built is not None:
            return built

        data = self._author
        if data is None:
            return None

        built = self._built_author = EmbedAuthor(data)

        return built

    @property
    def fields(self) -> list[EmbedField]:
        """
        List[:class:`EmbedField`]: The fields in the order they show,
        empty when there are none. The list belongs to the embed, so
        add and remove fields through the methods below.
        """
        built = self._built_fields
        if built is not None:
            return built

        fields = self._fields
        if fields is None:
            return []

        built = self._built_fields = [EmbedField(field) for field in fields]

        return built

    def set_footer(self, *, text: str | None = None, icon_url: str | None = None) -> Self:
        """
        Sets the line at the bottom, replacing what was there.

        Parameters
        -----------
        text: Optional[:class:`str`]
            The text, at most 2048 characters.
        icon_url: Optional[:class:`str`]
            The small icon in front of it.
        """
        footer: dict[str, Any] = {}

        if text is not None:
            footer["text"] = text

        if icon_url is not None:
            footer["icon_url"] = icon_url

        self._footer = footer
        self._built_footer = None

        return self

    def remove_footer(self) -> Self:
        """
        Takes the footer away again.
        """
        self._footer = None
        self._built_footer = None

        return self

    def set_author(self, *, name: str, url: str | None = None, icon_url: str | None = None) -> Self:
        """
        Sets the line above the title, replacing what was there.

        Parameters
        -----------
        name: :class:`str`
            The name, at most 256 characters.
        url: Optional[:class:`str`]
            Where the name links to.
        icon_url: Optional[:class:`str`]
            The small icon in front of it.
        """
        author: dict[str, Any] = {"name": name}

        if url is not None:
            author["url"] = url

        if icon_url is not None:
            author["icon_url"] = icon_url

        self._author = author
        self._built_author = None

        return self

    def remove_author(self) -> Self:
        """
        Takes the author line away again.
        """
        self._author = None
        self._built_author = None

        return self

    def set_image(self, *, url: str | None) -> Self:
        """
        Sets the large image below the fields, ``None`` to remove it.
        A file sent with the message goes in as
        ``attachment://filename``.
        """
        self._image = None if url is None else {"url": url}
        self._built_image = None

        return self

    def set_thumbnail(self, *, url: str | None) -> Self:
        """
        Sets the small image in the top right corner, ``None`` to
        remove it. A file sent with the message goes in as
        ``attachment://filename``.
        """
        self._thumbnail = None if url is None else {"url": url}
        self._built_thumbnail = None

        return self

    def add_field(self, *, name: str, value: str, inline: bool = True) -> Self:
        """
        Adds a field at the end, of which an embed takes 25.

        Parameters
        -----------
        name: :class:`str`
            The heading, at most 256 characters.
        value: :class:`str`
            The text below it, at most 1024 characters.
        inline: :class:`bool`
            Whether the field shares its row with the ones next to it.
        """
        field = {"name": name, "value": value, "inline": inline}
        fields = self._fields

        if fields is None:
            self._fields = [field]
        else:
            fields.append(field)

        self._built_fields = None

        return self

    def insert_field_at(self, index: int, /, *, name: str, value: str, inline: bool = True) -> Self:
        """
        Adds a field in front of the one at ``index``, or at the end
        when the index is past them.
        """
        field = {"name": name, "value": value, "inline": inline}
        fields = self._fields

        if fields is None:
            self._fields = [field]
        else:
            fields.insert(index, field)

        self._built_fields = None

        return self

    def set_field_at(self, index: int, /, *, name: str, value: str, inline: bool = True) -> Self:
        """
        Replaces the field at ``index``.

        Raises
        -------
        IndexError
            There is no field at that index.
        """
        fields = self._fields
        if fields is None:
            raise IndexError("this embed has no fields")

        fields[index] = {"name": name, "value": value, "inline": inline}
        self._built_fields = None

        return self

    def remove_field(self, index: int, /) -> Self:
        """
        Takes the field at ``index`` away, and does nothing when there
        is none there.
        """
        fields = self._fields

        if fields is not None:
            try:
                del fields[index]
            except IndexError:
                pass

            self._built_fields = None

        return self

    def clear_fields(self) -> Self:
        """
        Takes every field away.
        """
        self._fields = None
        self._built_fields = None

        return self

    def __len__(self) -> int:
        total = len(self.title or "") + len(self.description or "")
        fields = self._fields

        if fields is not None:
            for field in fields:
                total += len(field["name"]) + len(field["value"])

        footer = self._footer
        if footer is not None:
            try:
                total += len(footer["text"])
            except KeyError:
                pass

        author = self._author
        if author is not None:
            try:
                total += len(author["name"])
            except KeyError:
                pass

        return total

    def __bool__(self) -> bool:
        return any((
            self.title,
            self.url,
            self.description,
            self._colour,
            self._fields,
            self._timestamp,
            self._author,
            self._thumbnail,
            self._footer,
            self._image,
            self._provider,
            self._video
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Embed):
            return NotImplemented

        return (
            self.type == other.type
            and self.title == other.title
            and self.url == other.url
            and self.description == other.description
            and self._colour == other._colour
            and self._timestamp == other._timestamp
            and self._fields == other._fields
            and self._author == other._author
            and self._footer == other._footer
            and self._image == other._image
            and self._thumbnail == other._thumbnail
            and self._provider == other._provider
            and self._video == other._video
            and self._flags == other._flags
        )

    def __repr__(self) -> str:
        return f"<Embed type={self.type!r} title={self.title!r} url={self.url!r}>"

__all__ = ["Embed", "EmbedFooter", "EmbedMedia", "EmbedProvider", "EmbedAuthor", "EmbedField"]