"""Example: Register, list, and manage webhooks.

Usage:
    export LIVEPASSES_API_KEY="your-api-key"
    python examples/webhook_setup.py
"""

from __future__ import annotations

import os
import sys

from livepasses import (
    CreateWebhookParams,
    Livepasses,
    LivepassesError,
)


def main() -> None:
    api_key = os.environ.get("LIVEPASSES_API_KEY", "")
    if not api_key:
        print("Set LIVEPASSES_API_KEY environment variable first.")
        sys.exit(1)

    client = Livepasses(api_key)

    try:
        # 1. Create a webhook for pass events
        print("Registering webhook...")
        webhook = client.webhooks.create(
            CreateWebhookParams(
                url="https://your-app.com/webhooks/livepasses",
                events=["pass.generated", "pass.redeemed", "pass.checked_in", "batch.completed"],
            )
        )
        print(f"  Webhook ID: {webhook.id}")
        print(f"  URL: {webhook.url}")
        print(f"  Events: {', '.join(webhook.events)}")
        print(f"  Secret: {webhook.secret}")
        print("  (Store this secret to verify incoming webhook signatures)\n")

        # 2. List all registered webhooks
        print("Listing all webhooks...")
        webhooks = client.webhooks.list()
        for wh in webhooks:
            print(f"  - {wh.id}: {wh.url} (active: {wh.is_active})")
            print(f"    Events: {', '.join(wh.events)}")
        print()

        # 3. Clean up — delete the webhook
        print("Deleting webhook...")
        client.webhooks.delete(webhook.id)
        print("  Webhook deleted\n")

        print("Done!")

    except LivepassesError as e:
        print(f"ERROR: API error [{e.code}]: {e}")


if __name__ == "__main__":
    main()
