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

class SKUType(Enum):
    """
    What a SKU sells.

    Only three kinds end up in entitlements. ``subscription_group`` is
    the parent of subscription SKUs and never sold on its own.
    """

    durable = 2
    """
    A one time purchase that stays with the user.
    """

    consumable = 3
    """
    A one time purchase the application uses up. It marks the
    entitlement consumed once the user has received what they bought.
    """

    subscription = 5
    """
    A recurring subscription with a billing period.
    """

    subscription_group = 6
    """
    The group a subscription SKU belongs to. It only structures the
    store listing.
    """

    is_purchasable = Category(durable, consumable, subscription)
    """
    :class:`bool`: Whether users can buy the SKU and entitlements can
    point at it. The group is a container, not a product.
    """

class EntitlementType(Enum):
    """
    How a user or guild came to own a SKU.

    Most bots only care that an entitlement exists. The type matters
    for accounting, and for telling test entitlements from real ones.
    """

    purchase = 1
    """
    Bought in the store of the application.
    """

    premium_subscription = 2
    """
    Part of a Nitro subscription.
    """

    developer_gift = 3
    """
    Given away by the developer.
    """

    test_mode_purchase = 4
    """
    Created through the API for testing. No money changed hands.
    """

    free_purchase = 5
    """
    Claimed while the SKU was free.
    """

    user_gift = 6
    """
    Gifted by another user.
    """

    premium_purchase = 7
    """
    Claimed for free as a Nitro subscriber.
    """

    application_subscription = 8
    """
    A running application subscription, the usual type for recurring
    SKUs.
    """

    is_paid = Category(purchase, application_subscription)
    """
    :class:`bool`: Whether the owner paid the application for it. Gifts,
    Nitro perks, free claims and test entitlements are not revenue.
    """

class EntitlementOwnerType(Enum):
    """
    Who an entitlement belongs to.

    Needed when creating a test entitlement, otherwise the entitlement
    itself says whether it carries a user or a guild ID.
    """

    guild = 1
    """
    A guild, every member gets the benefit.
    """

    user = 2
    """
    A single user, in every guild they share with the application.
    """

class SubscriptionStatus(Enum):
    """
    Where a subscription stands in its billing cycle.

    ``ending`` still grants access until the current period runs out,
    only ``inactive`` means the benefit is gone.
    """

    active = 0
    """
    Renews at the end of the current period.
    """

    ending = 1
    """
    Cancelled, but paid for until the current period ends.
    """

    inactive = 2
    """
    Ended, the user no longer has the benefit.
    """

    grants_access = Category(active, ending)
    """
    :class:`bool`: Whether the user still has what they subscribed to.
    A cancelled subscription keeps its benefit until the period ends.
    """

__all__ = ["SKUType", "EntitlementType", "EntitlementOwnerType", "SubscriptionStatus"]