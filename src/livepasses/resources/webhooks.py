"""Webhooks resource for the Livepasses SDK."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any

from livepasses.types.webhooks import CreateWebhookParams, Webhook

if TYPE_CHECKING:
    from livepasses._http import HttpClient


class WebhooksResource:
    """Resource for webhook operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: CreateWebhookParams) -> Webhook:
        """Create a new webhook."""
        data = self._http.post("/api/webhooks", params)
        return _build_webhook(data)

    def list(self) -> list[Webhook]:
        """List all webhooks."""
        data = self._http.get("/api/webhooks")
        if isinstance(data, list):
            return [_build_webhook(item) for item in data]
        return []

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook."""
        self._http.delete(f"/api/webhooks/{webhook_id}")


def _build_webhook(data: Any) -> Webhook:
    if not isinstance(data, dict):
        return Webhook(**{})
    field_names = {f.name for f in dataclasses.fields(Webhook)}
    filtered = {k: v for k, v in data.items() if k in field_names}
    return Webhook(**filtered)
