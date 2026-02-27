"""Example: Generate and manage passes with the Livepasses SDK.

Usage:
    export LIVEPASSES_API_KEY="your-api-key"
    python examples/generate_passes.py
"""

from __future__ import annotations

import os
import sys

from livepasses import (
    AuthenticationError,
    BusinessData,
    BusinessContext,
    CheckInParams,
    CustomerInfo,
    EventContext,
    GenerateAndWaitOptions,
    GeneratePassesParams,
    Livepasses,
    LivepassesError,
    LookupPassParams,
    NotFoundError,
    PassRecipient,
    RateLimitError,
    ValidationError,
)


def main() -> None:
    api_key = os.environ.get("LIVEPASSES_API_KEY", "")
    if not api_key:
        print("Set LIVEPASSES_API_KEY environment variable first.")
        sys.exit(1)

    client = Livepasses(api_key)

    try:
        # 1. List templates
        print("Listing templates...")
        templates = client.templates.list()
        for tmpl in templates.items:
            print(f"  - {tmpl.name} ({tmpl.id}) [{tmpl.status}]")

        if not templates.items:
            print("No templates found. Create one in the dashboard first.")
            return

        template_id = templates.items[0].id

        # 2. Generate an event pass
        print(f"\nGenerating pass from template {template_id}...")
        result = client.passes.generate_and_wait(
            GeneratePassesParams(
                template_id=template_id,
                business_context=BusinessContext(
                    event=EventContext(
                        event_name="Tech Conference 2026",
                        event_date="2026-06-15T09:00:00Z",
                        doors_open="2026-06-15T08:00:00Z",
                    ),
                ),
                passes=[
                    PassRecipient(
                        customer=CustomerInfo(
                            first_name="Alice",
                            last_name="Smith",
                            email="alice@example.com",
                        ),
                        business_data=BusinessData(
                            section_info="VIP",
                            row_info="A",
                            seat_number="1",
                            ticket_type="VIP",
                            price=150.00,
                            currency="USD",
                        ),
                    ),
                ],
            ),
            options=GenerateAndWaitOptions(
                poll_interval=2.0,
                on_progress=lambda s: print(f"  Progress: {s.progress_percentage}%"),
            ),
        )

        print(f"Generated {result.total_passes} pass(es)")
        for p in result.passes:
            print(f"  Pass ID: {p.id}")
            print(f"  Apple Wallet: {p.platforms.apple.available}")
            print(f"  Google Wallet: {p.platforms.google.available}")

        if not result.passes:
            return

        pass_id = result.passes[0].id

        # 3. Look up the pass
        print(f"\nLooking up pass {pass_id}...")
        lookup = client.passes.lookup(LookupPassParams(pass_id=pass_id))
        print(f"  Status: {lookup.status}, Valid: {lookup.is_valid}")

        # 4. Validate
        print(f"\nValidating pass {pass_id}...")
        validation = client.passes.validate(pass_id)
        print(f"  Can redeem: {validation.can_be_redeemed}")
        print(f"  Methods: {validation.verification_methods}")

        # 5. Check in
        print(f"\nChecking in pass {pass_id}...")
        checkin = client.passes.check_in(
            pass_id,
            CheckInParams(location="Main Entrance", latitude=4.6097, longitude=-74.0817),
        )
        print(f"  New status: {checkin.new_status}")

    except AuthenticationError:
        print("ERROR: Invalid API key. Check your LIVEPASSES_API_KEY.")
    except ValidationError as e:
        print(f"ERROR: Validation failed: {e}")
    except NotFoundError as e:
        print(f"ERROR: Resource not found: {e}")
    except RateLimitError as e:
        print(f"ERROR: Rate limited. Retry after {e.retry_after}s")
    except LivepassesError as e:
        print(f"ERROR: API error [{e.code}]: {e}")


if __name__ == "__main__":
    main()
