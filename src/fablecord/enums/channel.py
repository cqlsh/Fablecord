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

from .base import Category, Enum

class ChannelType(Enum):
    """
    The type of a channel.

    The type decides which model the channel factory builds and which
    endpoints accept the channel. Threads share the message endpoints
    with text channels but have their own lifecycle, and the two direct
    message types never belong to a guild.
    """

    text = 0
    """
    A text channel in a guild.
    """

    private = 1
    """
    A direct message between the bot and one user.
    """

    voice = 2
    """
    A voice channel. Text can be sent into it as well.
    """

    group = 3
    """
    A group direct message. Bots cannot be part of one, it only shows up
    in invite payloads.
    """

    category = 4
    """
    A category that other channels sit under. It has no messages.
    """

    news = 5
    """
    An announcement channel. Messages in it can be published to every
    channel that follows it.
    """

    news_thread = 10
    """
    A thread inside an announcement channel.
    """

    public_thread = 11
    """
    A thread anyone who sees the parent channel can join.
    """

    private_thread = 12
    """
    A thread only invited members can see. Needs the parent's
    ``create_private_threads`` permission to create.
    """

    stage_voice = 13
    """
    A stage channel, where speakers are moderated and everyone else
    listens.
    """

    guild_directory = 14
    """
    The directory channel of a student hub. Bots never see one.
    """

    forum = 15
    """
    A forum. Every post is a thread, and the forum itself has no messages.
    """

    media = 16
    """
    A media channel. Like a forum, but every post has to carry media.
    """

    is_thread = Category(news_thread, public_thread, private_thread)
    """
    :class:`bool`: Whether channels of this type are threads, which means
    they use the thread endpoints and archive on their own.
    """

    is_voice = Category(voice, stage_voice)
    """
    :class:`bool`: Whether the bot can connect to channels of this type
    for audio.
    """

    is_direct = Category(private, group)
    """
    :class:`bool`: Whether channels of this type live outside a guild.
    """

    holds_threads_only = Category(forum, media)
    """
    :class:`bool`: Whether the channel has no messages of its own and
    every post is a thread, as forums and media channels do.
    """

class VideoQualityMode(Enum):
    """
    The video quality Discord enforces in a voice channel.
    """

    auto = 1
    """
    Discord picks the quality based on the connection.
    """

    full = 2
    """
    Always 720p. Needs at least boost level one.
    """

class ForumLayoutType(Enum):
    """
    How the client lays out the posts of a forum.
    """

    not_set = 0
    """
    Nothing chosen yet, the client uses its default.
    """

    list_view = 1
    """
    Posts as a list, one below the other.
    """

    gallery_view = 2
    """
    Posts as tiles with their first image as the preview.
    """

class ForumOrderType(Enum):
    """
    How the posts of a forum are sorted.
    """

    latest_activity = 0
    """
    The post with the newest message comes first.
    """

    creation_date = 1
    """
    The newest post comes first, regardless of activity.
    """

class PrivacyLevel(Enum):
    """
    Who can see a stage instance.

    Discord retired the public level, so the only value left is the one
    that keeps the stage inside the guild.
    """

    guild_only = 2
    """
    Only members of the guild can see the stage.
    """

class VoiceChannelEffectAnimationType(Enum):
    """
    The animation of a sound or emoji effect in a voice channel.
    """

    premium = 0
    """
    The fuller animation that Nitro subscribers get.
    """

    basic = 1
    """
    The plain animation everyone gets.
    """

__all__ = [
    "ChannelType",
    "VideoQualityMode",
    "ForumLayoutType",
    "ForumOrderType",
    "PrivacyLevel",
    "VoiceChannelEffectAnimationType"
]