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

from .base import Flag, Flags
from .intents import Intents

class ApplicationFlags(Flags):
    """
    The flags of an application.

    The ``gateway_*`` ones say which privileged intents Discord approved
    for the application. The ``limited`` variants apply while it is in
    fewer than a hundred guilds, where no verification is needed for
    them. :meth:`missing_approvals` turns that into a check the client can
    run before it connects.
    """

    __slots__ = []

    auto_mod_badge = Flag(1 << 6)
    """
    :class:`bool`: The application has at least a hundred auto moderation
    rules active across its guilds.
    """

    gateway_presence = Flag(1 << 12)
    """
    :class:`bool`: Discord approved the presences intent after verification.
    """

    gateway_presence_limited = Flag(1 << 13)
    """
    :class:`bool`: The presences intent is switched on in the portal, which
    is enough below a hundred guilds.
    """

    gateway_guild_members = Flag(1 << 14)
    """
    :class:`bool`: Discord approved the members intent after verification.
    """

    gateway_guild_members_limited = Flag(1 << 15)
    """
    :class:`bool`: The members intent is switched on in the portal, which
    is enough below a hundred guilds.
    """

    verification_pending_guild_limit = Flag(1 << 16)
    """
    :class:`bool`: The application hit the hundred guild limit while its
    verification is still pending, so it cannot join more guilds.
    """

    embedded = Flag(1 << 17)
    """
    :class:`bool`: The application is an activity that runs inside Discord.
    """

    gateway_message_content = Flag(1 << 18)
    """
    :class:`bool`: Discord approved the message content intent after
    verification.
    """

    gateway_message_content_limited = Flag(1 << 19)
    """
    :class:`bool`: The message content intent is switched on in the portal,
    which is enough below a hundred guilds.
    """

    app_commands_badge = Flag(1 << 23)
    """
    :class:`bool`: The application has global application commands, which
    earns it the supports commands badge.
    """

    active = Flag(1 << 24)
    """
    :class:`bool`: One of its global commands was used in the last thirty
    days, which keeps the active developer badge.
    """

    def missing_approvals(self, intents: Intents, /) -> Intents:
        """
        The privileged intents in ``intents`` this application may not use.

        A full or limited approval counts as approved. An empty result
        means the application can identify with these intents.

        Parameters
        -----------
        intents: :class:`Intents`
            The intents the bot wants to identify with.

        Returns
        --------
        :class:`Intents`
            The requested privileged intents that lack approval.
        """
        missing = 0

        if intents.presences and not (self.gateway_presence or self.gateway_presence_limited):
            missing |= Intents.presences.bit

        if intents.members and not (self.gateway_guild_members or self.gateway_guild_members_limited):
            missing |= Intents.members.bit

        if intents.message_content and not (self.gateway_message_content or self.gateway_message_content_limited):
            missing |= Intents.message_content.bit

        return Intents.from_value(missing)

    def allows(self, intents: Intents, /) -> bool:
        """
        Whether Discord lets this application identify with ``intents``.

        The client runs this before connecting, so a missing approval fails
        with a clear message instead of close code 4014 from the gateway.

        Parameters
        -----------
        intents: :class:`Intents`
            The intents the bot wants to identify with.

        Returns
        --------
        :class:`bool`
            ``True`` when every requested privileged intent is approved.
        """
        return not self.missing_approvals(intents).value

class SKUFlags(Flags):
    """
    The flags of a SKU, a purchasable item of an application.
    """

    __slots__ = []

    available = Flag(1 << 2)
    """
    :class:`bool`: The SKU can be bought right now.
    """

    guild_subscription = Flag(1 << 7)
    """
    :class:`bool`: A recurring subscription that a guild buys and every
    member benefits from.
    """

    user_subscription = Flag(1 << 8)
    """
    :class:`bool`: A recurring subscription that a single user buys for
    themselves.
    """

__all__ = ["ApplicationFlags", "SKUFlags"]