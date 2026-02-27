"""Example: Coupon pass generation and redemption.

Usage:
    export LIVEPASSES_API_KEY="your-api-key"
    python examples/coupon_workflow.py
"""

from __future__ import annotations

import os
import sys

from livepasses import (
    BusinessContext,
    BusinessData,
    BusinessRuleError,
    CouponContext,
    CustomerInfo,
    GenerateAndWaitOptions,
    GeneratePassesParams,
    Livepasses,
    LivepassesError,
    LookupPassParams,
    PassRecipient,
    RedeemCouponParams,
    RedemptionLocation,
)


def main() -> None:
    api_key = os.environ.get("LIVEPASSES_API_KEY", "")
    if not api_key:
        print("Set LIVEPASSES_API_KEY environment variable first.")
        sys.exit(1)

    client = Livepasses(api_key)

    try:
        # 1. Generate coupon passes for a campaign
        print("Generating coupon passes...")
        result = client.passes.generate_and_wait(
            GeneratePassesParams(
                template_id=os.environ.get("COUPON_TEMPLATE_ID", "coupon-template-id"),
                business_context=BusinessContext(
                    coupon=CouponContext(
                        campaign_name="Summer Sale 2026",
                        special_message="Enjoy 20% off your next purchase!",
                        promotion_start_date="2026-06-01",
                        promotion_end_date="2026-08-31",
                    ),
                ),
                passes=[
                    PassRecipient(
                        customer=CustomerInfo(
                            first_name="Maria", last_name="Garcia", email="maria@example.com"
                        ),
                        business_data=BusinessData(promo_code="SUMMER20-001", max_usage_count=1),
                    ),
                    PassRecipient(
                        customer=CustomerInfo(
                            first_name="Pedro", last_name="Lopez", email="pedro@example.com"
                        ),
                        business_data=BusinessData(promo_code="SUMMER20-002", max_usage_count=1),
                    ),
                ],
            ),
            options=GenerateAndWaitOptions(
                on_progress=lambda s: print(f"  Progress: {s.progress_percentage}%"),
            ),
        )

        print(f"Generated {len(result.passes)} coupon(s)\n")

        # 2. Look up a coupon
        pass_id = result.passes[0].id
        print("Looking up coupon...")
        lookup = client.passes.lookup(LookupPassParams(pass_id=pass_id))
        print(f"  Holder: {lookup.holder_name}")
        print(f"  Status: {lookup.status}\n")

        # 3. Validate before redemption
        print("Validating coupon...")
        validation = client.passes.validate(pass_id)
        print(f"  Can redeem: {validation.can_be_redeemed}\n")

        # 4. Redeem the coupon at a store
        if validation.can_be_redeemed:
            print("Redeeming coupon...")
            try:
                redemption = client.passes.redeem_coupon(
                    pass_id,
                    RedeemCouponParams(
                        location=RedemptionLocation(
                            name="Store #42", latitude=4.6097, longitude=-74.0817
                        ),
                        notes="Applied to order #12345",
                    ),
                )
                print(f"  Previous status: {redemption.previous_status}")
                print(f"  New status: {redemption.new_status}")
                print(f"  Redeemed at: {redemption.redeemed_at}\n")
            except BusinessRuleError as e:
                print(f"  Cannot redeem: {e}\n")

        print("Done!")

    except LivepassesError as e:
        print(f"ERROR: API error [{e.code}]: {e}")


if __name__ == "__main__":
    main()
