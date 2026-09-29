"""Tests for the internal HTTP client."""

from __future__ import annotations

import httpx
import pytest
from pytest_httpx import HTTPXMock

from livepasses import Livepasses
from livepasses._http import HttpClient, HttpClientConfig
from livepasses.errors import (
    AuthenticationError,
    ForbiddenError,
    LivepassesError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ValidationError,
)
from tests.mocks import mock_api_error, mock_api_response, mock_paged_response


@pytest.fixture()
def client() -> Livepasses:
    return Livepasses(
        "test-api-key",
        base_url="https://api.test.livepasses.com",
        max_retries=0,
    )


@pytest.fixture()
def http_client() -> HttpClient:
    return HttpClient(
        HttpClientConfig(
            api_key="test-api-key",
            base_url="https://api.test.livepasses.com",
            timeout=30.0,
            max_retries=0,
        )
    )


def test_get_sends_api_key_header(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response({"isValid": True, "canBeRedeemed": True, "status": "Active", "verificationMethods": []}))
    client.passes.validate("pass-1")
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["X-API-Key"] == "test-api-key"
    assert request.method == "GET"


def test_post_sends_json_body(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    from livepasses import (
        BusinessData,
        CustomerInfo,
        GeneratePassesParams,
        PassRecipient,
    )

    httpx_mock.add_response(
        json=mock_api_response(
            {
                "batchId": "b1",
                "templateId": "t1",
                "generatedAt": "2026-01-01",
                "totalPasses": 1,
                "isAsyncProcessing": False,
                "passes": [],
            }
        )
    )
    client.passes.generate(
        GeneratePassesParams(
            template_id="t1",
            passes=[
                PassRecipient(
                    customer=CustomerInfo(first_name="John", last_name="Doe"),
                    business_data=BusinessData(section_info="A"),
                )
            ],
        )
    )
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["content-type"] == "application/json"
    body = request.read()
    assert b"templateId" in body  # camelCase conversion


def test_query_params_skip_none(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(json=mock_api_response({"pass_id": "p1", "template_id": "t1", "status": "Active", "is_valid": True}))
    from livepasses import LookupPassParams

    client.passes.lookup(LookupPassParams(pass_id="p1"))
    request = httpx_mock.get_request()
    assert request is not None
    url = str(request.url)
    assert "passId=p1" in url
    assert "confirmationCode" not in url
    assert "holderEmail" not in url


def test_envelope_unwrapping(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(
        json=mock_api_response(
            {"isValid": True, "canBeRedeemed": True, "status": "Active", "verificationMethods": ["qr"]}
        )
    )
    result = client.passes.validate("pass-1")
    assert result.is_valid is True
    assert result.can_be_redeemed is True


def test_authentication_error(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(status_code=401, json=mock_api_error("UNAUTHORIZED", "Invalid API key"))
    with pytest.raises(AuthenticationError) as exc_info:
        client.passes.validate("pass-1")
    assert exc_info.value.status == 401
    assert exc_info.value.code == "UNAUTHORIZED"


def test_not_found_error(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(status_code=404, json=mock_api_error("NOT_FOUND", "Pass not found"))
    with pytest.raises(NotFoundError) as exc_info:
        client.passes.validate("pass-999")
    assert exc_info.value.status == 404


def test_validation_error(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(status_code=400, json=mock_api_error("VALIDATION_ERROR", "Bad input"))
    with pytest.raises(ValidationError) as exc_info:
        client.passes.validate("pass-1")
    assert exc_info.value.code == "VALIDATION_ERROR"


def test_rate_limit_error_with_retry_after(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    httpx_mock.add_response(
        status_code=429,
        json=mock_api_error("RATE_LIMIT_EXCEEDED", "Too many requests"),
        headers={"Retry-After": "30"},
    )
    with pytest.raises(RateLimitError) as exc_info:
        client.passes.validate("pass-1")
    assert exc_info.value.retry_after == 30


def test_5xx_retry_then_success(httpx_mock: HTTPXMock) -> None:
    retry_client = Livepasses(
        "test-key",
        base_url="https://api.test.livepasses.com",
        max_retries=2,
    )
    httpx_mock.add_response(status_code=500, json={"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": "err"}})
    httpx_mock.add_response(
        json=mock_api_response(
            {"isValid": True, "canBeRedeemed": True, "status": "Active", "verificationMethods": []}
        )
    )
    result = retry_client.passes.validate("pass-1")
    assert result.is_valid is True
    assert len(httpx_mock.get_requests()) == 2


def test_timeout_raises_livepasses_error(httpx_mock: HTTPXMock) -> None:
    timeout_client = Livepasses(
        "test-key",
        base_url="https://api.test.livepasses.com",
        timeout=0.001,
        max_retries=0,
    )
    httpx_mock.add_exception(httpx.ReadTimeout("timed out"))
    with pytest.raises(LivepassesError) as exc_info:
        timeout_client.passes.validate("pass-1")
    assert exc_info.value.code == "TIMEOUT"


def test_paged_response_parsing(httpx_mock: HTTPXMock, client: Livepasses) -> None:
    from tests.mocks import MOCK_GLOBAL_PASS

    httpx_mock.add_response(
        json=mock_paged_response([MOCK_GLOBAL_PASS], total_items=50, page=1, page_size=20)
    )
    result = client.passes.list()
    assert len(result.items) == 1
    assert result.pagination.total_items == 50
    assert result.pagination.current_page == 1
    assert result.items[0].id == "pass-001"


def test_refusal_with_status_raises_typed_error_from_envelope(
    http_client: HttpClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        status_code=404,
        json={
            "success": False,
            "data": None,
            "error": {"code": "TEMPLATE_NOT_FOUND", "message": "gone"},
        },
    )
    with pytest.raises(NotFoundError) as exc:
        http_client.get("/api/templates/x")
    assert exc.value.code == "TEMPLATE_NOT_FOUND"
    assert exc.value.status == 404


def test_validation_error_carries_fields(http_client: HttpClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        status_code=400,
        json={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "bad",
                "fields": {"name": ["required"]},
            },
        },
    )
    with pytest.raises(ValidationError) as exc:
        http_client.post("/api/x", body={})
    assert exc.value.fields == {"name": ["required"]}


def test_empty_body_error_raises_typed_error(http_client: HttpClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=404, content=b"")
    with pytest.raises(NotFoundError):
        http_client.delete("/api/webhooks/x")


def test_forbidden_status_wins_over_an_unauthorized_code(
    http_client: HttpClient, httpx_mock: HTTPXMock
) -> None:
    # A handler-level UNAUTHORIZED refusal answers 403: a permission problem, not a bad key.
    httpx_mock.add_response(
        status_code=403,
        json={"success": False, "data": None, "error": {"code": "UNAUTHORIZED", "message": "no"}},
    )
    with pytest.raises(ForbiddenError) as exc:
        http_client.get("/api/x")
    assert exc.value.status == 403
    assert exc.value.code == "UNAUTHORIZED"


def test_quota_exceeded_carries_the_real_status(
    http_client: HttpClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        status_code=422,
        json={"success": False, "data": None, "error": {"code": "QUOTA_EXCEEDED", "message": "limit"}},
    )
    with pytest.raises(QuotaExceededError) as exc:
        http_client.post("/api/templates", body={})
    assert exc.value.status == 422


def test_empty_body_401_is_authentication_error(
    http_client: HttpClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(status_code=401, content=b"")
    with pytest.raises(AuthenticationError) as exc:
        http_client.get("/api/x")
    assert exc.value.status == 401


def test_paged_refusal_raises_typed_error(http_client: HttpClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        status_code=403,
        json={
            "success": False,
            "error": {"code": "FORBIDDEN", "message": "nope"},
        },
    )
    with pytest.raises(LivepassesError) as exc:
        http_client.get_paged("/api/passes")
    assert exc.value.status == 403
    assert exc.value.code == "FORBIDDEN"


def test_retries_server_error_only_for_idempotent_methods(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("time.sleep", lambda _s: None)
    retrying = HttpClient(
        HttpClientConfig(
            api_key="k",
            base_url="https://api.test.livepasses.com",
            timeout=30.0,
            max_retries=3,
        )
    )
    body = {"success": False, "error": {"code": "EXTERNAL_SERVICE_ERROR", "message": "upstream"}}
    httpx_mock.add_response(status_code=502, json=body, is_reusable=True)

    with pytest.raises(LivepassesError):
        retrying.post("/api/passes/generate", body={})
    assert len(httpx_mock.get_requests()) == 1

    with pytest.raises(LivepassesError):
        retrying.get("/api/passes/x")
    assert len(httpx_mock.get_requests()) == 4
