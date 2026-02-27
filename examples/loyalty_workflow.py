"""Example: Loyalty card lifecycle — generate, earn points, spend points, update tier.

Usage:
    export LIVEPASSES_API_KEY="your-api-key"
    python examples/loyalty_workflow.py
"""

from __future__ import annotations

import os
import sys

from livepasses import (
    BusinessData,
    BusinessContext,
    BusinessRuleError,
    CustomerInfo,
    GenerateAndWaitOptions,
    GeneratePassesParams,
    Livepasses,
    LivepassesError,
    LoyaltyContext,
    LoyaltyTransactionParams,
    PassRecipient,
    UpdatePassParams,
)


def main() -> None:
    api_key = os.environ.get("LIVEPASSES_API_KEY", "")
    if not api_key:
        print("Set LIVEPASSES_API_KEY environment variable first.")
        sys.exit(1)

    client = Livepasses(api_key)

    try:
        # 1. Generate a loyalty card
        print("Generating loyalty card...")
        result = client.passes.generate_and_wait(
            GeneratePassesParams(
                template_id=os.environ.get("LOYALTY_TEMPLATE_ID", "loyalty-template-id"),
                passes=[
                    PassRecipient(
                        customer=CustomerInfo(
                            first_name="Carlos",
                            last_name="Rivera",
                            email="carlos@example.com",
                            phone="+57300123456",
                        ),
                        business_data=BusinessData(
                            membership_number="MEM-2026-001",
                            current_points=0,
                            member_tier="Bronze",
                            account_balance=0,
                        ),
                    ),
                ],
            ),
            options=GenerateAndWaitOptions(
                on_progress=lambda s: print(f"  Progress: {s.progress_percentage}%"),
            ),
        )

        pass_id = result.passes[0].id
        print(f"  Pass ID: {pass_id}")
        print(f"  Membership: {result.passes[0].business_data.membership_number}\n")

        # 2. Earn points from a purchase
        print("Earning 500 points from purchase...")
        earn = client.passes.loyalty_transact(
            pass_id,
            LoyaltyTransactionParams(
                transaction_type="earn", points=500, description="Purchase at Store #42 - $50.00"
            ),
        )
        print(f"  Status: {earn.new_status}\n")

        # 3. Earn more points
        print("Earning 300 more points...")
        client.passes.loyalty_transact(
            pass_id,
            LoyaltyTransactionParams(
                transaction_type="earn", points=300, description="Purchase at Store #15 - $30.00"
            ),
        )

        # 4. Spend points for a reward
        print("Spending 200 points on a reward...")
        spend = client.passes.loyalty_transact(
            pass_id,
            LoyaltyTransactionParams(
                transaction_type="spend", points=200, description="Redeemed: Free coffee"
            ),
        )
        print(f"  Status: {spend.new_status}\n")

        # 5. Update tier based on accumulated points
        print("Upgrading to Gold tier...")
        client.passes.update(
            pass_id,
            UpdatePassParams(
                business_data=BusinessData(current_points=600, member_tier="Gold"),
                business_context=BusinessContext(
                    loyalty=LoyaltyContext(
                        program_update="Congratulations! You've been upgraded to Gold tier!",
                        seasonal_message="Enjoy double points this month!",
                    ),
                ),
            ),
        )
        print("  Tier updated to Gold\n")

        # 6. Validate the pass
        print("Validating pass...")
        validation = client.passes.validate(pass_id)
        print(f"  Valid: {validation.can_be_redeemed}")
        print(f"  Message: {validation.validation_message}\n")

        print("Done!")

    except BusinessRuleError as e:
        print(f"ERROR: Business rule violation: {e}")
    except LivepassesError as e:
        print(f"ERROR: API error [{e.code}]: {e}")


if __name__ == "__main__":
    main()
