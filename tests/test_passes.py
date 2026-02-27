"""Tests for the PassesResource."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from livepasses import (
    BusinessData,
    CheckInParams,
    CustomerInfo,
    GenerateAndWaitOptions,
    GeneratePassesParams,
    Livepasses,
    LookupPassParams,
    LoyaltyTransactionParams,
    PassRecipient,
)
from tests.mocks import (
    MOCK_BATCH_GENERATION_RESULT,
    MOCK_BATCH_STATUS_COMPLETED,
    MOCK_BATCH_STATUS_PROCESSING,
    MOCK_GLOBAL_PASS,
    MOCK_PASS_GENERATION_RESULT,
    MOCK_PASS_LOOKUP,
    MOCK_PASS_VALIDATION,
    MOCK_REDEMPTION_RESULT,
    mock_api_response,
    mock_paged_response,
)


@pytest.fixture()
def client() -> Livepasses:
    return Livepasses(
        "test-api-key",
        base_url="https://api.test.livepasses.com",
        max_retries=0,
    )


def _generate_params() -> GeneratePassesParams:
    return GeneratePassesParams(
        template_id="tmpl-001",
        passes=[
            PassRecipient(
                customer=CustomerInfo(first_name="John", last_name="Doe", email="john@example.com"),
                business_data=BusinessData(section_info="A", row_info="1", seat_number="10"),
            )
        ],
    )


def test_generate_single_pass(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response(MOCK_PASS_GENERATION_RESULT))
    result = client.passes.generate(_generate_params())
    assert result.is_async_processing is False
    assert len(result.passes) == 1
    assert result.passes[0].id == "pass-001"


def test_generate_and_wait_sync(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response(MOCK_PASS_GENERATION_RESULT))
    result = client.passes.generate_and_wait(_generate_params())
    assert result.is_async_processing is False
    assert len(result.passes) == 1


def test_generate_and_wait_async_polls(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    # 1st call: generate (async batch)
    httpx_mock.add_response(json=mock_api_response(MOCK_BATCH_GENERATION_RESULT))
    # 2nd call: batch status (processing)
    httpx_mock.add_response(json=mock_api_response(MOCK_BATCH_STATUS_PROCESSING))
    # 3rd call: batch status (completed)
    httpx_mock.add_response(json=mock_api_response(MOCK_BATCH_STATUS_COMPLETED))

    progress_calls: list[float] = []

    def on_progress(status: object) -> None:
        progress_calls.append(getattr(status, "progress_percentage", 0))

    result = client.passes.generate_and_wait(
        _generate_params(),
        options=GenerateAndWaitOptions(
            poll_interval=0.01,
            max_attempts=10,
            on_progress=on_progress,
        ),
    )
    assert len(httpx_mock.get_requests()) == 3
    assert len(result.passes) == 2
    assert progress_calls == [40.0, 100.0]


def test_list_passes(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(
        json=mock_paged_response([MOCK_GLOBAL_PASS], total_items=1)
    )
    result = client.passes.list()
    assert len(result.items) == 1
    assert result.pagination.total_items == 1
    assert result.items[0].id == "pass-001"


def test_lookup_pass(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response(MOCK_PASS_LOOKUP))
    result = client.passes.lookup(LookupPassParams(pass_id="pass-001"))
    assert result.is_valid is True
    assert result.pass_id == "pass-001"


def test_validate_pass(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response(MOCK_PASS_VALIDATION))
    result = client.passes.validate("pass-001")
    assert result.can_be_redeemed is True
    assert "qr" in result.verification_methods


def test_redeem_pass(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response(MOCK_REDEMPTION_RESULT))
    result = client.passes.redeem("pass-001")
    assert result.new_status == "Redeemed"
    assert result.already_redeemed is False


def test_check_in_with_location(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(
        json=mock_api_response(
            {**MOCK_REDEMPTION_RESULT, "newStatus": "CheckedIn", "location": {"name": "Gate A", "latitude": 4.6, "longitude": -74.1}}
        )
    )
    result = client.passes.check_in(
        "pass-001",
        CheckInParams(location="Gate A", latitude=4.6, longitude=-74.1),
    )
    assert result.new_status == "CheckedIn"


def test_loyalty_transact(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(
        json=mock_api_response(
            {**MOCK_REDEMPTION_RESULT, "pointsEarned": 100, "newBalance": 500, "transactionType": "earn"}
        )
    )
    result = client.passes.loyalty_transact(
        "pass-001",
        LoyaltyTransactionParams(transaction_type="earn", points=100),
    )
    assert result.points_earned == 100
    assert result.new_balance == 500


def test_get_batch_status(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response(MOCK_BATCH_STATUS_COMPLETED))
    result = client.passes.get_batch_status("batch-002")
    assert result.is_completed is True
    assert result.statistics.passes_generated == 5
