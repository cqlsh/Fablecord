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

class PublicUserFlags(Flags):
    """
    The badges and account flags Discord shows publicly on a user.

    Bots cannot change these, they only come in with user payloads. The
    interesting ones for a bot are ``verified_bot``, which is about the
    bot itself, and ``spammer``, which explains why a user's direct
    messages land behind a warning.
    """

    __slots__ = []

    staff = Flag(1 << 0)
    """
    :class:`bool`: A Discord employee.
    """

    partner = Flag(1 << 1)
    """
    :class:`bool`: The owner of a partnered guild.
    """

    hypesquad = Flag(1 << 2)
    """
    :class:`bool`: A member of the HypeSquad events team, not one of the
    three houses.
    """

    bug_hunter = Flag(1 << 3)
    """
    :class:`bool`: A bug hunter of the first level.
    """

    hypesquad_bravery = Flag(1 << 6)
    """
    :class:`bool`: A member of the HypeSquad house Bravery.
    """

    hypesquad_brilliance = Flag(1 << 7)
    """
    :class:`bool`: A member of the HypeSquad house Brilliance.
    """

    hypesquad_balance = Flag(1 << 8)
    """
    :class:`bool`: A member of the HypeSquad house Balance.
    """

    early_supporter = Flag(1 << 9)
    """
    :class:`bool`: Bought Nitro before it was split into tiers.
    """

    team_user = Flag(1 << 10)
    """
    :class:`bool`: Not a person but the pseudo user that owns the
    applications of a team.
    """

    system = Flag(1 << 12)
    """
    :class:`bool`: The account Discord itself sends official messages from.
    """

    bug_hunter_level_2 = Flag(1 << 14)
    """
    :class:`bool`: A bug hunter of the second level.
    """

    verified_bot = Flag(1 << 16)
    """
    :class:`bool`: The bot passed verification, which is required to grow
    past a hundred guilds.
    """

    verified_bot_developer = Flag(1 << 17)
    """
    :class:`bool`: Owned a verified bot before the badge was retired in 2021.
    """

    discord_certified_moderator = Flag(1 << 18)
    """
    :class:`bool`: An alumni of the moderator programs.
    """

    bot_http_interactions = Flag(1 << 19)
    """
    :class:`bool`: The bot takes interactions over HTTP and never connects
    to the gateway, which is why it shows as online without a connection.
    """

    spammer = Flag(1 << 20)
    """
    :class:`bool`: Discord marked the user as a likely spammer, so clients
    hide their direct messages behind a warning.
    """

    active_developer = Flag(1 << 22)
    """
    :class:`bool`: Owns an application that ran a command in the last
    thirty days.
    """

class MemberFlags(Flags):
    """
    The flags of a guild member.

    Only ``bypasses_verification`` can be changed by a bot, and it needs
    the moderate members permission for that. Everything else is
    bookkeeping by Discord.
    """

    __slots__ = []

    did_rejoin = Flag(1 << 0)
    """
    :class:`bool`: The member left and came back, so join notifications
    and onboarding may have been skipped.
    """

    completed_onboarding = Flag(1 << 1)
    """
    :class:`bool`: The member finished the guild's onboarding.
    """

    bypasses_verification = Flag(1 << 2)
    """
    :class:`bool`: The member is exempt from the guild's membership
    screening and verification level.
    """

    started_onboarding = Flag(1 << 3)
    """
    :class:`bool`: The member started onboarding but has not finished it.
    """

    guest = Flag(1 << 4)
    """
    :class:`bool`: The member came in through a guest invite and only has
    access to a single voice channel for a limited time.
    """

    started_home_actions = Flag(1 << 5)
    """
    :class:`bool`: The member started the server guide's to do list.
    """

    completed_home_actions = Flag(1 << 6)
    """
    :class:`bool`: The member finished the server guide's to do list.
    """

    automod_quarantined_username = Flag(1 << 7)
    """
    :class:`bool`: Auto moderation quarantined the member because their
    username matched a rule.
    """

    dm_settings_upsell_acknowledged = Flag(1 << 9)
    """
    :class:`bool`: The member dismissed the prompt about direct message
    settings for this guild.
    """

    automod_quarantined_guild_tag = Flag(1 << 10)
    """
    :class:`bool`: Auto moderation quarantined the member because their
    guild tag matched a rule.
    """

__all__ = ["PublicUserFlags", "MemberFlags"]