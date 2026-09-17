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

class TeamMembershipState(Enum):
    """
    Whether a team member has accepted their invitation.

    Invited members already show up in the team, but nothing they could
    do counts until they accept.
    """

    invited = 1
    """
    Invited, not yet accepted.
    """

    accepted = 2
    """
    A full member of the team.
    """

class TeamMemberRole(Enum):
    """
    What a team member may do with the team's applications.

    The owner of a team has no role, the team names them separately.
    """

    admin = "admin"
    """
    Manages the team and every application in it, short of deleting
    the team or removing the owner.
    """

    developer = "developer"
    """
    Changes application settings, tokens and commands, but cannot touch
    the team itself or payouts.
    """

    read_only = "read_only"
    """
    Sees the team and its applications without changing anything.
    """

    can_edit_applications = Category(admin, developer)
    """
    :class:`bool`: Whether the role can change an application's
    settings. Read-only members only look.
    """

__all__ = ["TeamMembershipState", "TeamMemberRole"]