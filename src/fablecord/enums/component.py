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

class ComponentType(Enum):
    """
    The type of a message or modal component.

    Discord sorts components into three groups. Layout components hold
    others, content components show something, and interactive ones
    carry a ``custom_id`` and come back as interactions. The categories
    below follow those groups, plus the two rules that decide whether a
    payload is accepted at all.
    """

    action_row = 1
    """
    A row of up to five buttons or a single select menu.
    """

    button = 2
    """
    A button. Up to five fit into one row.
    """

    string_select = 3
    """
    A select menu with options the bot defines.
    """

    text_input = 4
    """
    A text field. Only valid inside a modal.
    """

    user_select = 5
    """
    A select menu listing the members of the guild.
    """

    role_select = 6
    """
    A select menu listing the roles of the guild.
    """

    mentionable_select = 7
    """
    A select menu listing members and roles together.
    """

    channel_select = 8
    """
    A select menu listing channels, optionally limited to certain
    channel types.
    """

    section = 9
    """
    Up to three text displays with a button or a thumbnail as accessory
    on the right.
    """

    text_display = 10
    """
    Markdown text. It takes the place of ``content`` once a message uses
    the new components.
    """

    thumbnail = 11
    """
    A small image. Only valid as the accessory of a section.
    """

    media_gallery = 12
    """
    A grid of up to ten images or videos.
    """

    file = 13
    """
    An uploaded file shown as a block inside the message.
    """

    separator = 14
    """
    Vertical padding between components, with an optional divider line.
    """

    container = 17
    """
    A box around other components with an optional accent colour, the
    closest thing to an embed among the new components.
    """

    label = 18
    """
    A label and description around a single modal component. Modals use
    it where messages use action rows.
    """

    file_upload = 19
    """
    A file picker inside a modal.
    """

    radio_group = 21
    """
    A group of radio buttons inside a modal, exactly one can be picked.
    """

    checkbox_group = 22
    """
    A group of checkboxes inside a modal.
    """

    checkbox = 23
    """
    A single checkbox inside a modal.
    """

    is_layout = Category(action_row, section, separator, container, label)
    """
    :class:`bool`: Whether the component exists to hold or arrange other
    components. These never carry a ``custom_id`` and never produce an
    interaction on their own.
    """

    is_interactive = Category(
        button,
        string_select,
        text_input,
        user_select,
        role_select,
        mentionable_select,
        channel_select,
        file_upload,
        radio_group,
        checkbox_group,
        checkbox
    )
    """
    :class:`bool`: Whether the component takes a ``custom_id`` and comes
    back as a component interaction or as part of a modal submission.
    """

    is_select = Category(string_select, user_select, role_select, mentionable_select, channel_select)
    """
    :class:`bool`: Whether the component is a select menu. They share
    ``min_values``, ``max_values`` and ``placeholder``, and their
    interaction carries a list of chosen values.
    """

    needs_components_v2 = Category(section, text_display, thumbnail, media_gallery, file, separator, container)
    """
    :class:`bool`: Whether a message with this component has to set
    :attr:`MessageFlags.components_v2`, which in turn disables ``content``
    and ``embeds`` for that message.
    """

    is_modal_only = Category(text_input, label, file_upload, radio_group, checkbox_group, checkbox)
    """
    :class:`bool`: Whether the component is only valid inside a modal.
    A message that contains one is rejected.
    """

class ButtonStyle(Enum):
    """
    The look of a button, and with it the kind of button.

    The first four differ only in colour. ``link`` and ``premium`` are
    different beasts, they carry no ``custom_id`` and never send an
    interaction, Discord handles the click itself.
    """

    primary = 1
    """
    Blurple. Meant for the one main action of a message.
    """

    secondary = 2
    """
    Grey.
    """

    success = 3
    """
    Green.
    """

    danger = 4
    """
    Red, for actions that cannot be undone.
    """

    link = 5
    """
    Grey with an arrow, opens a URL. Takes ``url`` instead of
    ``custom_id``.
    """

    premium = 6
    """
    Opens the purchase sheet of a SKU. Takes ``sku_id``, and Discord
    fills in the label and the price itself.
    """

    is_interactive = Category.excluding(link, premium)
    """
    :class:`bool`: Whether a click reaches the bot as an interaction.
    Only such buttons need a ``custom_id``, the other two must not have
    one.
    """

class TextStyle(Enum):
    """
    The size of a text input in a modal.
    """

    short = 1
    """
    A single line field.
    """

    paragraph = 2
    """
    A multi line field that grows with its content.
    """

class SeparatorSpacing(Enum):
    """
    How much room a separator leaves between components.
    """

    small = 1
    """
    A small gap.
    """

    large = 2
    """
    A large gap.
    """

class SelectDefaultValueType(Enum):
    """
    What a preselected value of a select menu refers to.

    User, role, mentionable and channel selects can open with values
    already chosen. The type has to fit the menu, a mentionable select
    takes users and roles, the others only their own kind.
    """

    user = "user"
    """
    A user, for user and mentionable selects.
    """

    role = "role"
    """
    A role, for role and mentionable selects.
    """

    channel = "channel"
    """
    A channel, for channel selects.
    """

class MediaItemLoadingState(Enum):
    """
    Whether Discord has fetched the media behind a component yet.

    Thumbnails, media galleries and file components point at media by
    URL, and Discord loads it on its side. Until that is done the item
    has no size and no proxy URL.
    """

    unknown = 0
    """
    Discord did not say. Older payloads leave the field out.
    """

    loading = 1
    """
    Still being fetched, size and proxy URL are missing.
    """

    loaded = 2
    """
    Fetched, size and proxy URL are set.
    """

    not_found = 3
    """
    The URL gave nothing usable, the client shows a broken item.
    """

    is_settled = Category(loaded, not_found)
    """
    :class:`bool`: Whether Discord is done with the item, one way or
    the other. Only a settled item can be trusted not to change.
    """

__all__ = [
    "ComponentType",
    "ButtonStyle",
    "TextStyle",
    "SeparatorSpacing",
    "SelectDefaultValueType",
    "MediaItemLoadingState"
]