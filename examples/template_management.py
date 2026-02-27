"""Example: CRUD operations on pass templates.

Usage:
    export LIVEPASSES_API_KEY="your-api-key"
    python examples/template_management.py
"""

from __future__ import annotations

import os
import sys

from livepasses import (
    CreateTemplateParams,
    Livepasses,
    ListTemplatesParams,
    LivepassesError,
    UpdateTemplateParams,
    ValidationError,
)


def main() -> None:
    api_key = os.environ.get("LIVEPASSES_API_KEY", "")
    if not api_key:
        print("Set LIVEPASSES_API_KEY environment variable first.")
        sys.exit(1)

    client = Livepasses(api_key)

    try:
        # 1. Create a new event template
        print("Creating event template...")
        template = client.templates.create(
            CreateTemplateParams(
                name="VIP Concert Pass",
                description="Premium concert ticket with VIP access",
                business_features={
                    "passType": "event",
                    "hasSeating": True,
                    "hasGateInfo": True,
                    "supportedPlatforms": ["apple", "google"],
                },
            )
        )
        print(f"  Created: {template.id} — '{template.name}'")
        print(f"  Status: {template.status}\n")

        # 2. Update the template
        print("Updating template...")
        updated = client.templates.update(
            template.id,
            UpdateTemplateParams(
                name="VIP Concert Pass v2",
                description="Updated premium concert ticket with backstage access",
                business_features={
                    "passType": "event",
                    "hasSeating": True,
                    "hasGateInfo": True,
                    "hasBackstageAccess": True,
                    "supportedPlatforms": ["apple", "google"],
                },
            ),
        )
        print(f"  Updated: '{updated.name}'\n")

        # 3. Activate the template
        print("Activating template...")
        client.templates.activate(template.id)
        print("  Template is now active\n")

        # 4. List all active templates
        print("Listing active templates...")
        templates = client.templates.list(ListTemplatesParams(status="Active"))
        for t in templates.items:
            print(f"  - {t.name} ({t.type}) [{t.status}]")
        print(f"  Total: {templates.pagination.total_items}\n")

        # 5. Get template details
        print("Getting template details...")
        detail = client.templates.get(template.id)
        print(f"  Name: {detail.name}")
        print(f"  Type: {detail.type}")
        print(f"  Business features: {detail.business_features}\n")

        # 6. Deactivate when done
        print("Deactivating template...")
        client.templates.deactivate(template.id)
        print("  Template deactivated\n")

        print("Done!")

    except ValidationError as e:
        print(f"ERROR: Validation failed: {e.details}")
    except LivepassesError as e:
        print(f"ERROR: API error [{e.code}]: {e}")


if __name__ == "__main__":
    main()
