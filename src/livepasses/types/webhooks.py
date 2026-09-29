"""Webhook-related types for the Livepasses SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Events the API accepts on a webhook subscription. Mirrors the server's allow-list exactly:
# subscribing to anything outside it is rejected with a 400, so a value that is not here is not
# a "not yet supported" event - it is a request that always fails.
WebhookEventType = Literal[
    "pass.generated",
    # The holder saved the pass to a wallet: it went from no device to one. A second device does
    # not fire it again; a re-add after "pass.removed" does.
    "pass.installed",
    # The holder removed the pass from their wallet and it is on no device. Holder-initiated only:
    # cancellation, transfer and operator ejection never fire it.
    "pass.removed",
    "pass.redeemed",
    "pass.updated",
    "pass.cancelled",
    "pass.expired",
    "loyalty.transacted",
    "coupon.applied",
    # A membership pass was scanned at a door. Distinct from "pass.redeemed", which for a
    # single-use pass means the entitlement is now spent.
    "membership.checked_in",
    "transfer.initiated",
    "transfer.accepted",
    "transfer.declined",
    "transfer.revoked",
    "transfer.expired",
    # Advisory: raised when membership sharing detection flags a pass, e.g. the same card
    # checking in at too many distinct venues within a window. The triggering check-in still
    # succeeded; this event never blocks or denies anything.
    "pass.sharing_suspected",
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
