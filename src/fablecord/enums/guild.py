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

from .base import Enum, OrderedEnum

class VerificationLevel(OrderedEnum):
    """
    What a member needs before they can talk in the guild.

    The levels build on each other, so ``level >= VerificationLevel.medium``
    is a valid check, the members rank by their value.
    """

    none = 0
    """
    No requirement.
    """

    low = 1
    """
    A verified email on the Discord account.
    """

    medium = 2
    """
    On top of that, the account has to be older than five minutes.
    """

    high = 3
    """
    On top of that, ten minutes as a member of the guild.
    """

    highest = 4
    """
    On top of that, a verified phone number.
    """

class ContentFilter(OrderedEnum):
    """
    Whose messages Discord scans for explicit media.

    Higher values cover more members, so the members rank by their value.
    """

    disabled = 0
    """
    Nothing is scanned.
    """

    no_role = 1
    """
    Only messages from members without a role are scanned.
    """

    all_members = 2
    """
    Every message is scanned.
    """

class NotificationLevel(Enum):
    """
    The default notification setting members get when they join.
    """

    all_messages = 0
    """
    Every message notifies.
    """

    only_mentions = 1
    """
    Only mentions notify.
    """

class MFALevel(Enum):
    """
    Whether moderators need two factor authentication.

    With it required, a bot whose owner has no two factor authentication
    loses the elevated permissions, see :meth:`Permissions.elevated`.
    """

    disabled = 0
    """
    Not required.
    """

    require_2fa = 1
    """
    Moderation actions need two factor authentication on the account.
    """

class NSFWLevel(Enum):
    """
    How Discord rates the guild as a whole.

    This is set by Discord, not by the guild, and decides whether the
    guild is reachable from platforms with age restrictions.
    """

    default = 0
    """
    Not rated yet.
    """

    explicit = 1
    """
    Rated as explicit.
    """

    safe = 2
    """
    Rated as safe.
    """

    age_restricted = 3
    """
    Age restricted, hidden on platforms that enforce that.
    """

class ExpireBehaviour(Enum):
    """
    What happens to a subscriber's role when their integration subscription
    runs out.
    """

    remove_role = 0
    """
    The role is taken away, the member stays.
    """

    kick = 1
    """
    The member is kicked from the guild.
    """

class OnboardingMode(Enum):
    """
    Which channels count towards the onboarding requirement.

    Discord demands that onboarding leaves a new member with at least
    seven channels to see, and the mode decides which ones count.
    """

    default = 0
    """
    Only the default channels count.
    """

    advanced = 1
    """
    Default channels and the channels of onboarding questions count.
    """

class OnboardingPromptType(Enum):
    """
    How an onboarding question is presented.
    """

    multiple_choice = 0
    """
    The options are shown as cards to pick from.
    """

    dropdown = 1
    """
    The options are shown in a dropdown.
    """

__all__ = [
    "VerificationLevel",
    "ContentFilter",
    "NotificationLevel",
    "MFALevel",
    "NSFWLevel",
    "ExpireBehaviour",
    "OnboardingMode",
    "OnboardingPromptType"
]