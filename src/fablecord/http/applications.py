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

from typing import TYPE_CHECKING, Any, Final
from collections.abc import Sequence
from ..utils.missing import MISSING
from .route import Route

if TYPE_CHECKING:
    from .client import RESTClient, Response

class Applications:
    """
    The application endpoints: the bot's own application, its role
    connection metadata, and what it sells, SKUs, entitlements and
    subscriptions.

    Every method builds the route and the payload and hands them to
    :meth:`RESTClient.request`, so what comes back is the raw payload
    Discord answered. Only the fields given end up in a payload.

    Parameters
    -----------
    rest: :class:`RESTClient`
        The client that sends the requests.

    Attributes
    -----------
    rest: :class:`RESTClient`
        The client that sends the requests.
    """

    __slots__ = ["rest"]

    ME: Final = Route("GET", "/applications/@me")
    EDIT_ME: Final = Route("PATCH", "/applications/@me")
    ROLE_CONNECTION_METADATA: Final = Route("GET", "/applications/{application_id}/role-connections/metadata")
    SET_ROLE_CONNECTION_METADATA: Final = Route("PUT", "/applications/{application_id}/role-connections/metadata")
    ENTITLEMENTS: Final = Route("GET", "/applications/{application_id}/entitlements")
    ENTITLEMENT: Final = Route("GET", "/applications/{application_id}/entitlements/{entitlement_id}")
    CONSUME_ENTITLEMENT: Final = Route("POST", "/applications/{application_id}/entitlements/{entitlement_id}/consume")
    CREATE_TEST_ENTITLEMENT: Final = Route("POST", "/applications/{application_id}/entitlements")
    DELETE_TEST_ENTITLEMENT: Final = Route("DELETE", "/applications/{application_id}/entitlements/{entitlement_id}")
    SKUS: Final = Route("GET", "/applications/{application_id}/skus")
    SUBSCRIPTIONS: Final = Route("GET", "/skus/{sku_id}/subscriptions")
    SUBSCRIPTION: Final = Route("GET", "/skus/{sku_id}/subscriptions/{subscription_id}")
    ACTIVITY_INSTANCE: Final = Route("GET", "/applications/{application_id}/activity-instances/{instance}")

    def __init__(self, rest: RESTClient, /) -> None:
        self.rest = rest

    def me(self) -> Response[dict[str, Any]]:
        """
        Fetches the bot's own application.
        """
        return self.rest.request(self.ME.compile())

    def edit_me(
            self,
            *,
            description: str = MISSING,
            icon: str | None = MISSING,
            cover_image: str | None = MISSING,
            tags: Sequence[str] = MISSING,
            flags: int = MISSING,
            install_params: dict[str, Any] = MISSING,
            integration_types_config: dict[str, Any] = MISSING,
            custom_install_url: str = MISSING,
            role_connections_verification_url: str = MISSING,
            interactions_endpoint_url: str = MISSING,
            event_webhooks_url: str = MISSING,
            event_webhooks_status: int = MISSING,
            event_webhooks_types: Sequence[str] = MISSING
    ) -> Response[dict[str, Any]]:
        """
        Edits the bot's own application. Only what is given changes.

        Parameters
        -----------
        description: :class:`str`
            The description.
        icon: Optional[:class:`str`]
            The icon as a data URI, ``None`` to remove it.
        cover_image: Optional[:class:`str`]
            The cover image as a data URI, ``None`` to remove it.
        tags: Sequence[:class:`str`]
            Up to five tags describing the application.
        flags: :class:`int`
            The application flags, only the gateway intent flags can be
            set here.
        install_params: Dict[:class:`str`, Any]
            The scopes and permissions of the in-app install link.
        integration_types_config: Dict[:class:`str`, Any]
            The install settings per context, guild and user.
        custom_install_url: :class:`str`
            The install link to use instead of Discord's.
        role_connections_verification_url: :class:`str`
            The URL for linked roles.
        interactions_endpoint_url: :class:`str`
            The URL interactions are posted to instead of the gateway.
        event_webhooks_url: :class:`str`
            The URL events are posted to.
        event_webhooks_status: :class:`int`
            Whether event webhooks are enabled.
        event_webhooks_types: Sequence[:class:`str`]
            The events posted to the webhook URL.
        """
        payload: dict[str, Any] = {}

        if description is not MISSING:
            payload["description"] = description

        if icon is not MISSING:
            payload["icon"] = icon

        if cover_image is not MISSING:
            payload["cover_image"] = cover_image

        if tags is not MISSING:
            payload["tags"] = tags

        if flags is not MISSING:
            payload["flags"] = flags

        if install_params is not MISSING:
            payload["install_params"] = install_params

        if integration_types_config is not MISSING:
            payload["integration_types_config"] = integration_types_config

        if custom_install_url is not MISSING:
            payload["custom_install_url"] = custom_install_url

        if role_connections_verification_url is not MISSING:
            payload["role_connections_verification_url"] = role_connections_verification_url

        if interactions_endpoint_url is not MISSING:
            payload["interactions_endpoint_url"] = interactions_endpoint_url

        if event_webhooks_url is not MISSING:
            payload["event_webhooks_url"] = event_webhooks_url

        if event_webhooks_status is not MISSING:
            payload["event_webhooks_status"] = event_webhooks_status

        if event_webhooks_types is not MISSING:
            payload["event_webhooks_types"] = event_webhooks_types

        return self.rest.request(self.EDIT_ME.compile(), json=payload)

    def role_connection_metadata(self, application_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the metadata fields a linked role can be gated on.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        """
        return self.rest.request(self.ROLE_CONNECTION_METADATA.compile(application_id))

    def set_role_connection_metadata(self, application_id: int, records: Sequence[dict[str, Any]], /) -> Response[list[dict[str, Any]]]:
        """
        Replaces the metadata fields a linked role can be gated on, up
        to five.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        records: Sequence[Dict[:class:`str`, Any]]
            The fields, each with its ``type``, ``key``, ``name`` and
            ``description``.
        """
        return self.rest.request(self.SET_ROLE_CONNECTION_METADATA.compile(application_id), json=records)

    def entitlements(
            self,
            application_id: int,
            /,
            *,
            user_id: int | None = None,
            sku_ids: Sequence[int] = MISSING,
            before: int | None = None,
            after: int | None = None,
            limit: int | None = None,
            guild_id: int | None = None,
            exclude_ended: bool = MISSING,
            exclude_deleted: bool = MISSING
    ) -> Response[list[dict[str, Any]]]:
        """
        Fetches the entitlements of an application, the SKUs users and
        guilds have access to.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        user_id: Optional[:class:`int`]
            Only entitlements of this user.
        sku_ids: Sequence[:class:`int`]
            Only entitlements to these SKUs.
        before: Optional[:class:`int`]
            Only entitlements with an ID below this one.
        after: Optional[:class:`int`]
            Only entitlements with an ID above this one.
        limit: Optional[:class:`int`]
            How many entitlements at most, 1 to 100.
        guild_id: Optional[:class:`int`]
            Only entitlements of this guild.
        exclude_ended: :class:`bool`
            Whether to leave out entitlements that have ended.
        exclude_deleted: :class:`bool`
            Whether to leave out entitlements that were deleted.
        """
        params = {
            "user_id": user_id,
            "sku_ids": ",".join(map(str, sku_ids)) if sku_ids else None,
            "before": before,
            "after": after,
            "limit": limit,
            "guild_id": guild_id,
            "exclude_ended": exclude_ended or None,
            "exclude_deleted": exclude_deleted or None
        }

        return self.rest.request(self.ENTITLEMENTS.compile(application_id), params=params)

    def entitlement(self, application_id: int, entitlement_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one entitlement.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        entitlement_id: :class:`int`
            The entitlement.
        """
        return self.rest.request(self.ENTITLEMENT.compile(application_id, entitlement_id))

    def consume_entitlement(self, application_id: int, entitlement_id: int, /) -> Response[None]:
        """
        Marks a one-time purchase as consumed, after which it no longer
        shows as active.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        entitlement_id: :class:`int`
            The entitlement.
        """
        return self.rest.request(self.CONSUME_ENTITLEMENT.compile(application_id, entitlement_id))

    def create_test_entitlement(self, application_id: int, /, *, sku_id: int, owner_id: int, owner_type: int) -> Response[dict[str, Any]]:
        """
        Grants a test entitlement to a user or guild, for trying a SKU
        without a purchase.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        sku_id: :class:`int`
            The SKU.
        owner_id: :class:`int`
            The user or guild to grant it to.
        owner_type: :class:`int`
            ``1`` for a guild, ``2`` for a user.
        """
        return self.rest.request(self.CREATE_TEST_ENTITLEMENT.compile(application_id), json={"sku_id": sku_id, "owner_id": owner_id, "owner_type": owner_type})

    def delete_test_entitlement(self, application_id: int, entitlement_id: int, /) -> Response[None]:
        """
        Removes a test entitlement.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        entitlement_id: :class:`int`
            The entitlement.
        """
        return self.rest.request(self.DELETE_TEST_ENTITLEMENT.compile(application_id, entitlement_id))

    def skus(self, application_id: int, /) -> Response[list[dict[str, Any]]]:
        """
        Fetches the SKUs of an application, what it sells.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        """
        return self.rest.request(self.SKUS.compile(application_id))

    def subscriptions(
            self,
            sku_id: int,
            /,
            *,
            before: int | None = None,
            after: int | None = None,
            limit: int | None = None,
            user_id: int | None = None
    ) -> Response[list[dict[str, Any]]]:
        """
        Fetches the subscriptions to a SKU, which for an application
        means the ones of a user, so ``user_id`` is expected.

        Parameters
        -----------
        sku_id: :class:`int`
            The SKU.
        before: Optional[:class:`int`]
            Only subscriptions with an ID below this one.
        after: Optional[:class:`int`]
            Only subscriptions with an ID above this one.
        limit: Optional[:class:`int`]
            How many subscriptions at most, 1 to 100.
        user_id: Optional[:class:`int`]
            Whose subscriptions.
        """
        return self.rest.request(self.SUBSCRIPTIONS.compile(sku_id), params={"before": before, "after": after, "limit": limit, "user_id": user_id})

    def subscription(self, sku_id: int, subscription_id: int, /) -> Response[dict[str, Any]]:
        """
        Fetches one subscription to a SKU.

        Parameters
        -----------
        sku_id: :class:`int`
            The SKU.
        subscription_id: :class:`int`
            The subscription.
        """
        return self.rest.request(self.SUBSCRIPTION.compile(sku_id, subscription_id))

    def activity_instance(self, application_id: int, instance_id: str, /) -> Response[dict[str, Any]]:
        """
        Fetches a running instance of the application's activity.

        Parameters
        -----------
        application_id: :class:`int`
            The application.
        instance_id: :class:`str`
            The instance.
        """
        return self.rest.request(self.ACTIVITY_INSTANCE.compile(application_id, instance_id))

__all__ = ["Applications"]