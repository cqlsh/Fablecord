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

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Final, Self

from .flags.permissions import Permissions
from .flags.base import Flag

_PERMISSIONS: Final[dict[str, int]] = {name: flag.bit for name, flag in vars(Permissions).items() if isinstance(flag, Flag)}
_NAMED_BITS: Final[list[tuple[str, int]]] = list(_PERMISSIONS.items())

class Overwrites:
    """
    Gives a subclass one property per permission, so the list of
    permissions lives in :class:`Permissions` alone and cannot drift
    apart from it.
    """

    __slots__ = []

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        for name, bit in _PERMISSIONS.items():
            setattr(cls, name, Overwrites._permission(bit))

    @staticmethod
    def _permission(bit: int, /) -> property:
        """
        One permission as a property, which reads ``True``, ``False``
        or ``None`` and writes by moving the bit between the allowed
        and the denied side. The mask that clears the bit is worked
        out once here instead of on every write.
        """
        clear = ~bit

        def read(self: PermissionOverwrite) -> bool | None:
            if self.allow & bit:
                return True

            if self.deny & bit:
                return False

            return None

        def write(self: PermissionOverwrite, value: bool | None) -> None:
            if value:
                self.allow |= bit

                if self.deny & bit:
                    self.deny &= clear
            elif value is None:
                self.allow &= clear
                self.deny &= clear
            else:
                self.deny |= bit

                if self.allow & bit:
                    self.allow &= clear

        return property(read, write)

class PermissionOverwrite(Overwrites):
    """
    What one role or member may and may not do in a channel.

    A channel keeps an overwrite per role and per member, and each
    permission in it is allowed, denied, or left alone so the roles
    decide. Setting one to ``None`` is what takes it back out of the
    overwrite.

    Every permission of :class:`Permissions` is here as an attribute
    that reads and writes ``True``, ``False`` or ``None``:

    .. code-block:: python

        overwrite = PermissionOverwrite(send_messages=False)
        overwrite.view_channel = True
        overwrite.send_messages = None

    Parameters
    -----------
    **permissions: Optional[:class:`bool`]
        The permissions to set right away.

    Raises
    -------
    TypeError
        One of the names is not a permission.

    Attributes
    -----------
    allow: :class:`int`
        The bits Discord sends as ``allow``, the permissions this turns
        on.
    deny: :class:`int`
        The bits Discord sends as ``deny``, the ones it turns off.
    """

    __slots__ = ["allow", "deny"]

    if TYPE_CHECKING:
        create_instant_invite: bool | None
        kick_members: bool | None
        ban_members: bool | None
        administrator: bool | None
        manage_channels: bool | None
        manage_guild: bool | None
        add_reactions: bool | None
        view_audit_log: bool | None
        priority_speaker: bool | None
        stream: bool | None
        view_channel: bool | None
        send_messages: bool | None
        send_tts_messages: bool | None
        manage_messages: bool | None
        embed_links: bool | None
        attach_files: bool | None
        read_message_history: bool | None
        mention_everyone: bool | None
        use_external_emojis: bool | None
        view_guild_insights: bool | None
        connect: bool | None
        speak: bool | None
        mute_members: bool | None
        deafen_members: bool | None
        move_members: bool | None
        use_voice_activation: bool | None
        change_nickname: bool | None
        manage_nicknames: bool | None
        manage_roles: bool | None
        manage_webhooks: bool | None
        manage_expressions: bool | None
        use_application_commands: bool | None
        request_to_speak: bool | None
        manage_events: bool | None
        manage_threads: bool | None
        create_public_threads: bool | None
        create_private_threads: bool | None
        use_external_stickers: bool | None
        send_messages_in_threads: bool | None
        use_embedded_activities: bool | None
        moderate_members: bool | None
        view_creator_monetization_analytics: bool | None
        use_soundboard: bool | None
        create_expressions: bool | None
        create_events: bool | None
        use_external_sounds: bool | None
        send_voice_messages: bool | None
        set_voice_channel_status: bool | None
        send_polls: bool | None
        use_external_apps: bool | None
        pin_messages: bool | None
        bypass_slowmode: bool | None

    def __init__(self, **permissions: bool | None) -> None:
        self.allow = 0
        self.deny = 0

        if permissions:
            self.update(**permissions)

    @classmethod
    def from_pair(cls, allow: Permissions, deny: Permissions, /) -> Self:
        """
        The overwrite a channel's ``allow`` and ``deny`` describe,
        which is how Discord sends one.
        """
        self = cls.__new__(cls)
        self.allow = allow.value
        self.deny = deny.value

        return self

    def pair(self) -> tuple[Permissions, Permissions]:
        """
        The overwrite as the pair Discord takes back, what it allows
        and what it denies.
        """
        allowed = Permissions.__new__(Permissions)
        allowed.value = self.allow

        denied = Permissions.__new__(Permissions)
        denied.value = self.deny

        return allowed, denied

    def update(self, **permissions: bool | None) -> None:
        """
        Sets several permissions at once, leaving the rest as they are.

        Raises
        -------
        TypeError
            One of the names is not a permission.
        """
        allow = self.allow
        deny = self.deny

        for name, value in permissions.items():
            bit = _PERMISSIONS.get(name)

            if bit is None:
                raise TypeError(f"{name!r} is not a permission")

            if value is None:
                allow &= ~bit
                deny &= ~bit
            elif value:
                allow |= bit
                deny &= ~bit
            else:
                deny |= bit
                allow &= ~bit

        self.allow = allow
        self.deny = deny

    def is_empty(self) -> bool:
        """
        Whether the overwrite says nothing at all, which is what lets a
        channel drop it.
        """
        return not (self.allow or self.deny)

    def __iter__(self) -> Iterator[tuple[str, bool | None]]:
        allow = self.allow
        either = allow | self.deny

        return iter([(name, bool(allow & bit) if either & bit else None) for name, bit in _NAMED_BITS])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PermissionOverwrite) and other.allow == self.allow and other.deny == self.deny

    def __repr__(self) -> str:
        return f"<PermissionOverwrite allow={self.allow} deny={self.deny}>"

__all__ = ["PermissionOverwrite", "Overwrites"]