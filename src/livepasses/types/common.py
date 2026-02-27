"""Common types shared across the Livepasses SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ApiError:
    """API error details returned in error responses."""

    message: str
    code: str
    details: str | None = None
    timestamp: str | None = None
    trace_id: str | None = None


@dataclass
class PaginationMetadata:
    """Pagination metadata for paged API responses."""

    current_page: int
    page_size: int
    total_pages: int
    total_items: int


@dataclass
class PagedResponse(Generic[T]):
    """Paginated API response containing items and pagination metadata."""

    items: list[T]
    pagination: PaginationMetadata


@dataclass
class ResponseMetadata:
    """Optional metadata included in API responses."""

    trace_id: str | None = None
    processing_time_ms: float | None = None
    timestamp: str | None = None


@dataclass
class PagedParams:
    """Base parameters for paginated list requests."""

    page: int | None = None
    page_size: int | None = None
    search_term: str | None = None
    sort_by: str | None = None
    sort_descending: bool | None = None


class ApiErrorCodes:
    """All API error code string constants."""

    # General
    GENERAL_ERROR = "GENERAL_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

    # Auth / Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_API_KEY = "INVALID_API_KEY"
    API_KEY_EXPIRED = "API_KEY_EXPIRED"
    API_KEY_REVOKED = "API_KEY_REVOKED"
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FIELD_FORMAT = "INVALID_FIELD_FORMAT"
    FIELD_TOO_LONG = "FIELD_TOO_LONG"
    FIELD_TOO_SHORT = "FIELD_TOO_SHORT"
    INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"

    # Resource
    NOT_FOUND = "NOT_FOUND"
    PASS_NOT_FOUND = "PASS_NOT_FOUND"
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    TENANT_NOT_FOUND = "TENANT_NOT_FOUND"
    PARTNERSHIP_NOT_FOUND = "PARTNERSHIP_NOT_FOUND"

    # Business Rules
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    PASS_EXPIRED = "PASS_EXPIRED"
    PASS_ALREADY_USED = "PASS_ALREADY_USED"
    TEMPLATE_INACTIVE = "TEMPLATE_INACTIVE"
    RESOURCE_LOCKED = "RESOURCE_LOCKED"
    RESOURCE_EXPIRED = "RESOURCE_EXPIRED"

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"

    # Quota
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    API_QUOTA_EXCEEDED = "API_QUOTA_EXCEEDED"
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"
    FEATURE_NOT_AVAILABLE = "FEATURE_NOT_AVAILABLE"

    # External Services
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    APPLE_WALLET_ERROR = "APPLE_WALLET_ERROR"
    GOOGLE_WALLET_ERROR = "GOOGLE_WALLET_ERROR"
