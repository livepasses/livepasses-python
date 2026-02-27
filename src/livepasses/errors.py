"""Typed error hierarchy for the Livepasses SDK."""

from __future__ import annotations


class LivepassesError(Exception):
    """Base error for all Livepasses API errors."""

    def __init__(
        self,
        message: str,
        status: int,
        code: str,
        details: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details


class AuthenticationError(LivepassesError):
    """Raised for 401 authentication failures."""


class ValidationError(LivepassesError):
    """Raised for 400 validation errors."""


class ForbiddenError(LivepassesError):
    """Raised for 403 forbidden errors."""


class NotFoundError(LivepassesError):
    """Raised for 404 not found errors."""


class RateLimitError(LivepassesError):
    """Raised for 429 rate limit exceeded errors."""

    def __init__(
        self,
        message: str,
        status: int,
        code: str,
        details: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status, code, details)
        self.retry_after = retry_after


class QuotaExceededError(LivepassesError):
    """Raised when API quota is exceeded."""


class BusinessRuleError(LivepassesError):
    """Raised for 422 business rule violations."""


# ---------------------------------------------------------------------------
# Error code sets (mirrors Node SDK exactly)
# ---------------------------------------------------------------------------

_AUTH_CODES = {"UNAUTHORIZED", "INVALID_API_KEY", "API_KEY_EXPIRED", "API_KEY_REVOKED"}

_FORBIDDEN_CODES = {"FORBIDDEN", "INSUFFICIENT_PERMISSIONS"}

_VALIDATION_CODES = {
    "VALIDATION_ERROR",
    "REQUIRED_FIELD_MISSING",
    "INVALID_FIELD_FORMAT",
    "FIELD_TOO_LONG",
    "FIELD_TOO_SHORT",
    "INVALID_FIELD_VALUE",
}

_NOT_FOUND_CODES = {
    "NOT_FOUND",
    "PASS_NOT_FOUND",
    "TEMPLATE_NOT_FOUND",
    "TENANT_NOT_FOUND",
    "PARTNERSHIP_NOT_FOUND",
}

_RATE_LIMIT_CODES = {"RATE_LIMIT_EXCEEDED", "TOO_MANY_REQUESTS"}

_QUOTA_CODES = {
    "QUOTA_EXCEEDED",
    "API_QUOTA_EXCEEDED",
    "SUBSCRIPTION_REQUIRED",
    "FEATURE_NOT_AVAILABLE",
}

_BUSINESS_RULE_CODES = {
    "BUSINESS_RULE_VIOLATION",
    "OPERATION_NOT_ALLOWED",
    "PASS_EXPIRED",
    "PASS_ALREADY_USED",
    "TEMPLATE_INACTIVE",
    "RESOURCE_LOCKED",
    "RESOURCE_EXPIRED",
}


def create_typed_error(
    message: str,
    status: int,
    code: str,
    details: str | None = None,
    retry_after: int | None = None,
) -> LivepassesError:
    """Create a typed error based on the error code or HTTP status."""
    if code in _AUTH_CODES:
        return AuthenticationError(message, status, code, details)
    if code in _FORBIDDEN_CODES:
        return ForbiddenError(message, status, code, details)
    if code in _VALIDATION_CODES:
        return ValidationError(message, status, code, details)
    if code in _NOT_FOUND_CODES:
        return NotFoundError(message, status, code, details)
    if code in _RATE_LIMIT_CODES:
        return RateLimitError(message, status, code, details, retry_after)
    if code in _QUOTA_CODES:
        return QuotaExceededError(message, status, code, details)
    if code in _BUSINESS_RULE_CODES:
        return BusinessRuleError(message, status, code, details)

    # Fallback: map by HTTP status
    if status == 401:
        return AuthenticationError(message, status, code, details)
    if status == 403:
        return ForbiddenError(message, status, code, details)
    if status == 404:
        return NotFoundError(message, status, code, details)
    if status == 429:
        return RateLimitError(message, status, code, details, retry_after)

    return LivepassesError(message, status, code, details)
