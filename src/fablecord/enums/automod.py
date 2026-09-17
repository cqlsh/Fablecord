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

class AutoModRuleTriggerType(Enum):
    """
    What an auto moderation rule looks for.

    The trigger decides which metadata a rule takes and how many rules
    of that kind a guild may have: six keyword rules, one of each other
    kind.
    """

    keyword = 1
    """
    Words, phrases or regular expressions the rule lists itself.
    """

    spam = 3
    """
    Discord's own spam detection, without settings of its own.
    """

    keyword_preset = 4
    """
    One or more of Discord's word lists, see
    :class:`AutoModKeywordPresetType`.
    """

    mention_spam = 5
    """
    More unique mentions in one message than the rule allows.
    """

    member_profile = 6
    """
    Words in a member's name, nickname or bio instead of in messages.
    """

    takes_keywords = Category(keyword, member_profile)
    """
    :class:`bool`: Whether the rule carries its own word lists and
    regular expressions. The other triggers reject that metadata.
    """

class AutoModRuleEventType(Enum):
    """
    When Discord checks a rule.
    """

    message_send = 1
    """
    A member sends or edits a message.
    """

    member_update = 2
    """
    A member changes their profile.
    """

class AutoModRuleActionType(Enum):
    """
    What happens when a rule triggers.

    A rule can combine several actions. Which ones fit depends on the
    trigger, a message can only be blocked where there is a message and
    only keyword and mention spam rules may time members out.
    """

    block_message = 1
    """
    The message is not sent. An optional explanation is shown to the
    author.
    """

    send_alert_message = 2
    """
    A report is posted to a channel the rule names.
    """

    timeout = 3
    """
    The member is timed out for a duration the rule names. Needs
    ``moderate_members`` from whoever creates the rule.
    """

    block_member_interactions = 4
    """
    The member cannot interact in the guild until their profile passes.
    Only for member profile rules.
    """

    needs_metadata = Category(send_alert_message, timeout)
    """
    :class:`bool`: Whether the action is incomplete without its
    settings, the alert channel or the timeout duration.
    """

class AutoModKeywordPresetType(Enum):
    """
    The word lists Discord maintains for keyword preset rules.
    """

    profanity = 1
    """
    Swearing and cursing.
    """

    sexual_content = 2
    """
    Sexual references.
    """

    slurs = 3
    """
    Personal insults and hate speech.
    """

__all__ = ["AutoModRuleTriggerType", "AutoModRuleEventType", "AutoModRuleActionType", "AutoModKeywordPresetType"]