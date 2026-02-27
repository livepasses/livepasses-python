"""Pass-related types for the Livepasses SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal


# ---------------------------------------------------------------------------
# Request types
# ---------------------------------------------------------------------------


@dataclass
class CustomerInfo:
    """Customer information for pass generation."""

    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    preferred_language: str | None = None


@dataclass
class BusinessData:
    """Business-specific data for pass generation.

    Contains fields for event, loyalty, and coupon pass types.
    """

    # Event fields
    section_info: str | None = None
    row_info: str | None = None
    seat_number: str | None = None
    gate_info: str | None = None
    confirmation_code: str | None = None
    ticket_type: str | None = None
    price: float | None = None
    currency: str | None = None

    # Loyalty fields
    membership_number: str | None = None
    current_points: int | None = None
    member_tier: str | None = None
    lifetime_points: int | None = None
    account_balance: float | None = None
    member_since: str | None = None
    favorite_store: str | None = None

    # Coupon fields
    promo_code: str | None = None
    campaign_id: str | None = None
    customer_segment: str | None = None
    max_usage_count: int | None = None
    source_channel: str | None = None


@dataclass
class PersonalizationData:
    """Optional personalization data for a pass."""

    dietary_restrictions: str | None = None
    accessibility_needs: str | None = None
    custom_fields: dict[str, str] | None = None


@dataclass
class PassRecipient:
    """A single pass recipient with customer and business data."""

    customer: CustomerInfo
    business_data: BusinessData
    personalizations: PersonalizationData | None = None


@dataclass
class EventContext:
    """Contextual information for event passes."""

    event_name: str | None = None
    event_date: str | None = None
    doors_open: str | None = None
    special_announcement: str | None = None


@dataclass
class LoyaltyContext:
    """Contextual information for loyalty passes."""

    program_update: str | None = None
    seasonal_message: str | None = None


@dataclass
class CouponContext:
    """Contextual information for coupon passes."""

    campaign_name: str | None = None
    special_message: str | None = None
    promotion_start_date: str | None = None
    promotion_end_date: str | None = None


@dataclass
class BusinessContext:
    """Business context containing type-specific information."""

    event: EventContext | None = None
    loyalty: LoyaltyContext | None = None
    coupon: CouponContext | None = None


@dataclass
class PassGenerationOptions:
    """Options for pass generation."""

    delivery_method: str | None = None  # auto | email | sms | whatsapp | webhook | return_urls
    generate_for_all_platforms: bool | None = None


@dataclass
class GeneratePassesParams:
    """Parameters for generating passes."""

    template_id: str
    passes: list[PassRecipient]
    business_context: BusinessContext | None = None
    options: PassGenerationOptions | None = None


@dataclass
class LookupPassParams:
    """Parameters for looking up a pass."""

    pass_id: str | None = None
    confirmation_code: str | None = None
    holder_email: str | None = None


@dataclass
class RedeemPassParams:
    """Parameters for redeeming a pass."""

    location: str | None = None
    notes: str | None = None


@dataclass
class CheckInParams:
    """Parameters for checking in with a pass."""

    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None


@dataclass
class RedeemCouponParams:
    """Parameters for redeeming a coupon pass."""

    location: str | None = None
    notes: str | None = None


@dataclass
class LoyaltyTransactionParams:
    """Parameters for a loyalty transaction."""

    transaction_type: Literal["earn", "spend"]
    points: int
    description: str | None = None


@dataclass
class UpdatePassParams:
    """Parameters for updating a pass."""

    business_data: dict[str, object] | None = None
    status: str | None = None


@dataclass
class BulkUpdatePassesParams:
    """Parameters for bulk-updating passes."""

    pass_ids: list[str]
    updates: UpdatePassParams


@dataclass
class ListPassesParams:
    """Parameters for listing passes."""

    page: int | None = None
    page_size: int | None = None
    search_term: str | None = None
    sort_by: str | None = None
    sort_descending: bool | None = None
    template_id: str | None = None
    status: str | None = None


@dataclass
class GenerateAndWaitOptions:
    """Options for generate_and_wait polling behavior."""

    poll_interval: float = 2.0
    max_attempts: int = 150
    on_progress: Callable[[BatchStatusResult], None] | None = None


# ---------------------------------------------------------------------------
# Response types
# ---------------------------------------------------------------------------


@dataclass
class PassPlatform:
    """Platform-specific pass information."""

    available: bool
    add_to_wallet_url: str | None = None
    pass_url: str | None = None
    jwt_token: str | None = None
    features: list[str] = field(default_factory=list)


@dataclass
class PassPlatforms:
    """Pass platforms (Apple and Google)."""

    apple: PassPlatform
    google: PassPlatform


@dataclass
class UnifiedBusinessData:
    """Unified business data across all pass types."""

    # Event
    section_info: str | None = None
    row_info: str | None = None
    seat_number: str | None = None
    gate_info: str | None = None
    confirmation_code: str | None = None
    ticket_type: str | None = None
    price: float | None = None
    currency: str | None = None

    # Loyalty
    membership_number: str | None = None
    current_points: int | None = None
    member_tier: str | None = None
    lifetime_points: int | None = None
    account_balance: float | None = None
    member_since: str | None = None
    favorite_store: str | None = None

    # Coupon
    promo_code: str | None = None
    campaign_id: str | None = None
    customer_segment: str | None = None
    max_usage_count: int | None = None
    source_channel: str | None = None


@dataclass
class AnalyticsInfo:
    """Analytics tracking information for a pass."""

    tracking_id: str
    engagement_url: str


@dataclass
class GeneratedPass:
    """A single generated pass."""

    id: str
    platforms: PassPlatforms
    business_data: UnifiedBusinessData
    customer_email: str | None = None
    confirmation_code: str | None = None
    qr_code: str | None = None
    status: str = ""
    analytics: AnalyticsInfo | None = None


@dataclass
class BatchOperationInfo:
    """Information about a batch operation."""

    id: str
    status: str
    total_recipients: int
    passes_generated: int
    generation_failures: int
    progress_percentage: float
    estimated_completion: str | None = None
    status_poll_url: str = ""


@dataclass
class DeliveryDetail:
    """Detail about a single delivery attempt."""

    recipient: str | None = None
    status: str = ""


@dataclass
class PassDeliveryResult:
    """Result of pass delivery."""

    method: str
    status: str
    sent_at: str
    details: list[DeliveryDetail] = field(default_factory=list)


@dataclass
class BusinessMetrics:
    """Business metrics for a pass generation batch."""

    total_revenue: float | None = None
    revenue_by_type: dict[str, float] | None = None
    distribution_by_type: dict[str, int] | None = None


@dataclass
class PassGenerationResult:
    """Result of a pass generation request."""

    batch_id: str
    template_id: str
    generated_at: str
    total_passes: int
    is_async_processing: bool
    batch_operation: BatchOperationInfo | None = None
    passes: list[GeneratedPass] = field(default_factory=list)
    delivery: PassDeliveryResult | None = None
    business_metrics: BusinessMetrics | None = None


# ---------------------------------------------------------------------------
# Lookup / Validation
# ---------------------------------------------------------------------------


@dataclass
class PassLookupResult:
    """Result of a pass lookup."""

    pass_id: str
    template_id: str
    status: str
    is_valid: bool
    holder_name: str | None = None
    holder_email: str | None = None
    confirmation_code: str | None = None
    created_at: str | None = None


@dataclass
class PassValidationResult:
    """Result of a pass validation."""

    is_valid: bool
    can_be_redeemed: bool
    status: str
    verification_methods: list[str] = field(default_factory=list)
    message: str | None = None


# ---------------------------------------------------------------------------
# Redemption
# ---------------------------------------------------------------------------


@dataclass
class RedemptionLocation:
    """Location where a redemption occurred."""

    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class PassRedemptionResult:
    """Result of a pass redemption/check-in."""

    pass_id: str
    new_status: str
    redeemed_at: str
    already_redeemed: bool = False
    location: RedemptionLocation | None = None
    points_earned: int | None = None
    new_balance: int | None = None
    transaction_type: str | None = None


# ---------------------------------------------------------------------------
# Batch Status
# ---------------------------------------------------------------------------


@dataclass
class GeneratedPassSummary:
    """Summary of a generated pass from a batch status response."""

    pass_id: str
    customer_email: str | None = None
    confirmation_code: str | None = None
    status: str = ""
    has_apple_pass: bool = False
    has_google_pass: bool = False


@dataclass
class BatchStatistics:
    """Statistics for a batch operation."""

    total_recipients: int = 0
    passes_generated: int = 0
    generation_failures: int = 0
    delivery_sent: int = 0
    delivery_failed: int = 0


@dataclass
class BatchStatusResult:
    """Result of a batch status check."""

    batch_id: str
    status: str
    is_completed: bool
    is_active: bool
    progress_percentage: float
    statistics: BatchStatistics
    generated_passes: list[GeneratedPassSummary] = field(default_factory=list)
    estimated_completion: str | None = None
    completed_at: str | None = None


# ---------------------------------------------------------------------------
# List Passes
# ---------------------------------------------------------------------------


@dataclass
class GlobalPassDto:
    """A pass as returned by the list endpoint."""

    id: str
    template_id: str
    template_name: str | None = None
    status: str = ""
    holder_name: str | None = None
    holder_email: str | None = None
    confirmation_code: str | None = None
    pass_type: str | None = None
    has_apple_pass: bool = False
    has_google_pass: bool = False
    created_at: str | None = None
    updated_at: str | None = None
