"""Webhook-related types for the Livepasses SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Events the API accepts on a webhook subscription. Mirrors the server's allow-list exactly:
# subscribing to anything outside it is rejected with a 400, so a value that is not here is not
# a "not yet supported" event - it is a request that always fails.
WebhookEventType = Literal[
    "pass.generated",
    "pass.redeemed",
    "pass.updated",
    "loyalty.transacted",
    "coupon.applied",
    "transfer.initiated",
    "transfer.accepted",
    "transfer.declined",
    "transfer.revoked",
    "transfer.expired",
    "*",  # every event above
]


@dataclass
class Webhook:
    """A registered webhook."""

    id: str
    url: str
    events: list[WebhookEventType]
    is_active: bool
    created_at: str
    secret: str | None = None


@dataclass
class CreateWebhookParams:
    """Parameters for creating a webhook."""

    url: str
    events: list[WebhookEventType]
