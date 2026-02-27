"""Webhook-related types for the Livepasses SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

WebhookEventType = Literal[
    "pass.generated",
    "pass.redeemed",
    "pass.updated",
    "pass.expired",
    "pass.checked_in",
    "batch.completed",
    "batch.failed",
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
