"""Shared mock response factories and fixtures for tests."""

from __future__ import annotations

from typing import Any


def mock_api_response(data: Any, message: str = "Success") -> dict[str, Any]:
    """Wrap *data* in a standard API success envelope."""
    return {
        "success": True,
        "data": data,
        "message": message,
        "meta": {
            "traceId": "test-trace-id",
            "timestamp": "2026-02-25T00:00:00Z",
        },
    }


def mock_api_error(code: str, message: str = "Error") -> dict[str, Any]:
    """Return a standard API error envelope."""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }


def mock_paged_response(
    items: list[Any],
    total_items: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Return a standard paginated API response envelope."""
    total = total_items if total_items is not None else len(items)
    total_pages = max(1, -(-total // page_size))  # ceil division
    return {
        "success": True,
        "items": items,
        "pagination": {
            "currentPage": page,
            "pageSize": page_size,
            "totalPages": total_pages,
            "totalItems": total,
        },
    }


# ---------------------------------------------------------------------------
# Fixed mock objects (camelCase — as the API returns them)
# ---------------------------------------------------------------------------

MOCK_PASS_GENERATION_RESULT: dict[str, Any] = {
    "batchId": "batch-001",
    "templateId": "tmpl-001",
    "generatedAt": "2026-02-25T12:00:00Z",
    "totalPasses": 1,
    "isAsyncProcessing": False,
    "passes": [
        {
            "id": "pass-001",
            "customerEmail": "john@example.com",
            "confirmationCode": "CONF-001",
            "platforms": {
                "apple": {"available": True, "addToWalletUrl": "https://example.com/apple", "features": []},
                "google": {"available": True, "addToWalletUrl": "https://example.com/google", "features": []},
            },
            "businessData": {"sectionInfo": "A", "rowInfo": "1", "seatNumber": "10"},
            "status": "Active",
        }
    ],
}

MOCK_BATCH_GENERATION_RESULT: dict[str, Any] = {
    "batchId": "batch-002",
    "templateId": "tmpl-001",
    "generatedAt": "2026-02-25T12:00:00Z",
    "totalPasses": 5,
    "isAsyncProcessing": True,
    "batchOperation": {
        "id": "batch-002",
        "status": "Processing",
        "totalRecipients": 5,
        "passesGenerated": 0,
        "generationFailures": 0,
        "progressPercentage": 0,
        "statusPollUrl": "/api/passes/batch/batch-002/status",
    },
    "passes": [],
}

MOCK_BATCH_STATUS_PROCESSING: dict[str, Any] = {
    "batchId": "batch-002",
    "status": "Processing",
    "isCompleted": False,
    "isActive": True,
    "progressPercentage": 40,
    "statistics": {
        "totalRecipients": 5,
        "passesGenerated": 2,
        "generationFailures": 0,
        "deliverySent": 0,
        "deliveryFailed": 0,
    },
    "generatedPasses": [],
}

MOCK_BATCH_STATUS_COMPLETED: dict[str, Any] = {
    "batchId": "batch-002",
    "status": "Completed",
    "isCompleted": True,
    "isActive": False,
    "progressPercentage": 100,
    "statistics": {
        "totalRecipients": 5,
        "passesGenerated": 5,
        "generationFailures": 0,
        "deliverySent": 5,
        "deliveryFailed": 0,
    },
    "generatedPasses": [
        {
            "passId": "pass-101",
            "customerEmail": "a@example.com",
            "confirmationCode": "CONF-A",
            "status": "Active",
            "hasApplePass": True,
            "hasGooglePass": True,
        },
        {
            "passId": "pass-102",
            "customerEmail": "b@example.com",
            "confirmationCode": "CONF-B",
            "status": "Active",
            "hasApplePass": True,
            "hasGooglePass": False,
        },
    ],
}

MOCK_PASS_LOOKUP: dict[str, Any] = {
    "passId": "pass-001",
    "templateId": "tmpl-001",
    "status": "Active",
    "isValid": True,
    "holderName": "John Doe",
    "holderEmail": "john@example.com",
    "confirmationCode": "CONF-001",
}

MOCK_PASS_VALIDATION: dict[str, Any] = {
    "isValid": True,
    "canBeRedeemed": True,
    "status": "Active",
    "verificationMethods": ["qr", "confirmation_code"],
}

MOCK_REDEMPTION_RESULT: dict[str, Any] = {
    "passId": "pass-001",
    "newStatus": "Redeemed",
    "redeemedAt": "2026-02-25T14:00:00Z",
    "alreadyRedeemed": False,
}

MOCK_GLOBAL_PASS: dict[str, Any] = {
    "id": "pass-001",
    "templateId": "tmpl-001",
    "templateName": "VIP Event Ticket",
    "status": "Active",
    "holderName": "John Doe",
    "holderEmail": "john@example.com",
    "confirmationCode": "CONF-001",
    "passType": "EventTicket",
    "hasApplePass": True,
    "hasGooglePass": True,
    "createdAt": "2026-02-25T12:00:00Z",
}
