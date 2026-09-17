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

class WebhookType(Enum):
    """
    What kind of webhook a payload describes.

    Only incoming webhooks carry a token and can be executed by URL.
    The other two show up when listing a channel's webhooks, but
    nothing can be sent through them directly.
    """

    incoming = 1
    """
    A webhook that posts messages into a channel. It has a token, and
    the token alone is enough to execute it.
    """

    channel_follower = 2
    """
    The webhook Discord creates when a channel follows an announcement
    channel. It has no token, Discord executes it itself.
    """

    application = 3
    """
    The webhook behind an application's interaction responses. Only
    reachable through an interaction token.
    """

__all__ = ["WebhookType"]