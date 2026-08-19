"""Passes resource for the Livepasses SDK."""

from __future__ import annotations

import dataclasses
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Generator, TypeVar

from livepasses._utils.pagination import auto_paginate
from livepasses._utils.polling import poll_until_complete
from livepasses.types.common import PagedResponse
from livepasses.types.passes import (
    BatchOperationInfo,
    BatchStatusResult,
    BatchStatistics,
    CheckInParams,
    GenerateAndWaitOptions,
    GeneratePassesParams,
    GeneratedPass,
    GeneratedPassSummary,
    GlobalPassDto,
    ListPassesParams,
    LookupPassParams,
    LoyaltyTransactionParams,
    MembershipCheckInParams,
    RedeemByScanParams,
    RedeemGiftCardParams,
    PassGenerationResult,
    PassLookupResult,
    PassPlatform,
    PassPlatforms,
    PassRedemptionResult,
    PassValidationResult,
    PushTemplatePassesParams,
    RedeemCouponParams,
    RedeemPassParams,
    UnifiedBusinessData,
    UpdatePassParams,
)

if TYPE_CHECKING:
    from livepasses._http import HttpClient


class PassesResource:
    """Resource for pass operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def generate(self, params: GeneratePassesParams) -> PassGenerationResult:
        """Generate one or more passes."""
        data = self._http.post("/api/passes/generate", params)
        return _parse_generation_result(data)

    def generate_and_wait(
        self,
        params: GeneratePassesParams,
        options: GenerateAndWaitOptions | None = None,
    ) -> PassGenerationResult:
        """Generate passes and poll until the batch completes.

        For single synchronous passes, returns immediately. For async batches,
        polls :meth:`get_batch_status` until the batch is completed, then merges
        the generated passes into the result.
        """
        opts = options or GenerateAndWaitOptions()
        result = self.generate(params)

        if not result.is_async_processing:
            return result

        batch_id = result.batch_operation.id if result.batch_operation else result.batch_id

        batch_status = poll_until_complete(
            fn=lambda: self.get_batch_status(batch_id),
            is_complete=lambda s: s.is_completed,
            interval=opts.poll_interval,
            max_attempts=opts.max_attempts,
            on_progress=opts.on_progress,
        )

        result.passes = [_summary_to_pass(s) for s in batch_status.generated_passes]
        return result

    def list(self, params: ListPassesParams | None = None) -> PagedResponse[GlobalPassDto]:
        """List passes with pagination."""
        query = _params_to_dict(params)
        paged = self._http.get_paged("/api/passes", query)
        return PagedResponse(
            items=[_dict_to_global_pass(item) for item in paged.items],
            pagination=paged.pagination,
        )

    def list_auto_paginate(
        self, params: ListPassesParams | None = None
    ) -> Generator[GlobalPassDto, None, None]:
        """Yield all passes across all pages."""
        base = _params_to_dict(params)

        def fetch_page(page: int) -> PagedResponse[GlobalPassDto]:
            base["page"] = page
            return self.list(ListPassesParams(**base))

        yield from auto_paginate(fetch_page)

    def lookup(self, params: LookupPassParams) -> PassLookupResult:
        """Look up a pass by ID, confirmation code, or holder email."""
        query = _params_to_dict(params)
        data = self._http.get("/api/passes/lookup", query)
        return _build_dataclass(PassLookupResult, data)

    def validate(self, pass_id: str) -> PassValidationResult:
        """Validate a pass."""
        data = self._http.get(f"/api/passes/{pass_id}/validate")
        return _build_dataclass(PassValidationResult, data)

    def update(self, pass_id: str, params: UpdatePassParams) -> None:
        """Update a pass."""
        self._http.put(f"/api/passes/{pass_id}", params)

    def push_template(self, template_id: str, params: PushTemplatePassesParams) -> None:
        """Push a scoped update to all eligible passes of a template."""
        self._http.post(f"/api/passes/template/{template_id}/push", params)

    def redeem(
        self, pass_id: str, params: RedeemPassParams | None = None
    ) -> PassRedemptionResult:
        """Redeem a single-use pass.

        Redeeming is terminal, so a pass the holder is meant to keep using must not go
        through here. Multi-use passes are refused with ``422`` / ``OPERATION_NOT_ALLOWED``
        instead of being consumed. Use the operation built for the type:

        - loyalty and stamp cards: ``stamp()`` (and ``unstamp()`` to undo)
        - memberships: ``membership_check_in()``, which does not consume the pass
        - coupons that allow multiple redemptions: ``redeem_coupon()``
        - gift cards: ``redeem_gift_card()``, which takes the amount to deduct
        """
        data = self._http.post(f"/api/passes/{pass_id}/redeem", params)
        return _build_dataclass(PassRedemptionResult, data)

    def check_in(
        self, pass_id: str, params: CheckInParams | None = None
    ) -> PassRedemptionResult:
        """Check in with a pass."""
        data = self._http.post(f"/api/passes/{pass_id}/check-in", params)
        return _build_dataclass(PassRedemptionResult, data)

    def redeem_coupon(
        self, pass_id: str, params: RedeemCouponParams | None = None
    ) -> PassRedemptionResult:
        """Redeem a coupon pass."""
        data = self._http.post(f"/api/passes/{pass_id}/redeem-coupon", params)
        return _build_dataclass(PassRedemptionResult, data)

    def loyalty_transact(
        self, pass_id: str, params: LoyaltyTransactionParams
    ) -> PassRedemptionResult:
        """Perform a loyalty transaction (earn or spend points)."""
        data = self._http.post(f"/api/passes/{pass_id}/loyalty/transact", params)
        return _build_dataclass(PassRedemptionResult, data)

    def redeem_gift_card(
        self, pass_id: str, params: RedeemGiftCardParams
    ) -> PassRedemptionResult:
        """Deduct an amount from a gift card's balance.

        Rejected when the amount exceeds the remaining balance; the balance is left
        untouched in that case.
        """
        data = self._http.post(f"/api/passes/{pass_id}/giftcard/redeem", params)
        return _build_dataclass(PassRedemptionResult, data)

    def membership_check_in(
        self, pass_id: str, params: MembershipCheckInParams | None = None
    ) -> PassRedemptionResult:
        """Check in a membership pass.

        Unlike an event check-in the pass is NOT consumed - it stays valid for the next
        visit. On a quota-limited membership the remaining uses decrement, and a check-in
        at zero is denied.
        """
        data = self._http.post(f"/api/passes/{pass_id}/membership/check-in", params)
        return _build_dataclass(PassRedemptionResult, data)

    def stamp(self, pass_id: str) -> PassRedemptionResult:
        """Add one stamp to the stamp card behind this pass.

        Repeat stamps on the same card are refused inside a short cooldown, so a double
        scan at the till does not award two stamps.
        """
        # Sends {} deliberately: the endpoint binds a request DTO, and a body of None
        # means no JSON and no Content-Type, which FastEndpoints answers with 415.
        data = self._http.post(f"/api/passes/{pass_id}/stamp", {})
        return _build_dataclass(PassRedemptionResult, data)

    def unstamp(self, pass_id: str) -> PassRedemptionResult:
        """Take back the most recent stamp, for correcting a mis-scan.

        Refused when there is nothing to undo, or when the last stamp was paid for by an
        external order.
        """
        # See stamp(): {} rather than None, or the request-DTO endpoint answers 415.
        data = self._http.post(f"/api/passes/{pass_id}/unstamp", {})
        return _build_dataclass(PassRedemptionResult, data)

    def redeem_by_scan(self, params: RedeemByScanParams) -> PassRedemptionResult:
        """Resolve a scanned barcode or NFC tap value and redeem it in one call."""
        data = self._http.post("/api/passes/redeem-by-scan", params)
        return _build_dataclass(PassRedemptionResult, data)

    def get_batch_status(self, batch_id: str) -> BatchStatusResult:
        """Get the status of a batch operation."""
        data = self._http.get(f"/api/passes/batch/{batch_id}/status")
        return _parse_batch_status(data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _params_to_dict(params: Any) -> dict[str, Any]:
    """Convert a dataclass params object to a dict, stripping None values."""
    if params is None:
        return {}
    if hasattr(params, "__dataclass_fields__"):
        return {k: v for k, v in asdict(params).items() if v is not None}
    return dict(params)


_T = TypeVar("_T")


def _build_dataclass(cls: type[_T], data: Any) -> _T:
    """Build a dataclass from a dict, passing only known fields."""
    if not isinstance(data, dict):
        return cls(**{})
    field_names = {f.name for f in dataclasses.fields(cls)}  # type: ignore[arg-type]
    filtered = {k: v for k, v in data.items() if k in field_names}
    return cls(**filtered)


def _parse_generation_result(data: Any) -> PassGenerationResult:
    """Parse a raw dict into a PassGenerationResult."""
    if not isinstance(data, dict):
        return _build_dataclass(PassGenerationResult, data)

    passes_raw = data.get("passes", [])
    passes = [_parse_generated_pass(p) for p in passes_raw] if passes_raw else []

    batch_op = None
    if data.get("batch_operation"):
        batch_op = _build_dataclass(BatchOperationInfo, data["batch_operation"])

    return PassGenerationResult(
        batch_id=data.get("batch_id", ""),
        template_id=data.get("template_id", ""),
        generated_at=data.get("generated_at", ""),
        total_passes=data.get("total_passes", 0),
        is_async_processing=data.get("is_async_processing", False),
        batch_operation=batch_op,
        passes=passes,
    )


def _parse_generated_pass(data: dict[str, Any]) -> GeneratedPass:
    """Parse a raw dict into a GeneratedPass."""
    platforms_data = data.get("platforms", {})
    platforms = PassPlatforms(
        apple=_build_dataclass(PassPlatform, platforms_data.get("apple", {})),
        google=_build_dataclass(PassPlatform, platforms_data.get("google", {})),
    )
    business_data = _build_dataclass(
        UnifiedBusinessData, data.get("business_data", {})
    )
    return GeneratedPass(
        id=data.get("id", ""),
        customer_email=data.get("customer_email"),
        confirmation_code=data.get("confirmation_code"),
        platforms=platforms,
        business_data=business_data,
        qr_code=data.get("qr_code"),
        status=data.get("status", ""),
        analytics=data.get("analytics"),
    )


def _parse_batch_status(data: Any) -> BatchStatusResult:
    """Parse a raw dict into a BatchStatusResult."""
    if not isinstance(data, dict):
        return _build_dataclass(BatchStatusResult, data)

    stats_raw = data.get("statistics", {})
    statistics = _build_dataclass(BatchStatistics, stats_raw)

    passes_raw = data.get("generated_passes", [])
    generated_passes = [
        _build_dataclass(GeneratedPassSummary, p) for p in passes_raw
    ]

    return BatchStatusResult(
        batch_id=data.get("batch_id", ""),
        status=data.get("status", ""),
        is_completed=data.get("is_completed", False),
        is_active=data.get("is_active", False),
        progress_percentage=data.get("progress_percentage", 0.0),
        statistics=statistics,
        generated_passes=generated_passes,
        estimated_completion=data.get("estimated_completion"),
        completed_at=data.get("completed_at"),
    )


def _summary_to_pass(summary: GeneratedPassSummary) -> GeneratedPass:
    """Convert a batch GeneratedPassSummary to a GeneratedPass."""
    return GeneratedPass(
        id=summary.pass_id,
        customer_email=summary.customer_email,
        confirmation_code=summary.confirmation_code,
        platforms=PassPlatforms(
            apple=PassPlatform(available=summary.has_apple_pass),
            google=PassPlatform(available=summary.has_google_pass),
        ),
        business_data=UnifiedBusinessData(),
        status=summary.status,
    )


def _dict_to_global_pass(data: Any) -> GlobalPassDto:
    """Convert a raw dict into a GlobalPassDto."""
    return _build_dataclass(GlobalPassDto, data)
