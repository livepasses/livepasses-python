"""Internal HTTP client for the Livepasses SDK."""

from __future__ import annotations

import random
import time
from dataclasses import asdict, dataclass
from typing import Any

import httpx

from livepasses._utils.case import keys_to_camel, keys_to_snake
from livepasses.errors import LivepassesError, create_typed_error
from livepasses.types.common import PagedResponse, PaginationMetadata


@dataclass
class HttpClientConfig:
    """Configuration for the internal HTTP client."""

    api_key: str
    base_url: str
    timeout: float
    max_retries: int


class HttpClient:
    """Internal HTTP client that wraps httpx with retry, envelope
    unwrapping, and case conversion."""

    def __init__(self, config: HttpClientConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url.rstrip("/"),
            timeout=config.timeout,
            headers={
                "X-API-Key": config.api_key,
                "Accept": "application/json",
            },
        )

    # -- Public API ----------------------------------------------------------

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Send a GET request and return unwrapped data."""
        return self._request("GET", path, params=params)

    def post(self, path: str, body: Any | None = None) -> Any:
        """Send a POST request and return unwrapped data."""
        return self._request("POST", path, body=body)

    def put(self, path: str, body: Any | None = None) -> Any:
        """Send a PUT request and return unwrapped data."""
        return self._request("PUT", path, body=body)

    def delete(self, path: str) -> Any:
        """Send a DELETE request and return unwrapped data."""
        return self._request("DELETE", path)

    def get_paged(
        self, path: str, params: dict[str, Any] | None = None
    ) -> PagedResponse[Any]:
        """Send a GET request and return a full :class:`PagedResponse`."""
        return self._request_paged(path, params=params)

    # -- Private helpers -----------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: Any | None = None,
    ) -> Any:
        response = self._fetch_with_retry(method, path, params=params, body=body)
        json_data: dict[str, Any] = response.json()

        if not json_data.get("success", False):
            error = json_data.get("error", {})
            raise create_typed_error(
                message=error.get("message", json_data.get("message", "Unknown error")),
                status=response.status_code,
                code=error.get("code", "GENERAL_ERROR"),
                details=error.get("details"),
                retry_after=self._parse_retry_after(response),
            )

        return keys_to_snake(json_data.get("data"))

    def _request_paged(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> PagedResponse[Any]:
        response = self._fetch_with_retry("GET", path, params=params)
        json_data: dict[str, Any] = response.json()

        if not json_data.get("success", False):
            error = json_data.get("error", {})
            raise create_typed_error(
                message=error.get("message", json_data.get("message", "Unknown error")),
                status=response.status_code,
                code=error.get("code", "GENERAL_ERROR"),
                details=error.get("details"),
                retry_after=self._parse_retry_after(response),
            )

        raw_pagination = json_data.get("pagination", {})
        pagination = PaginationMetadata(
            current_page=raw_pagination.get("currentPage", 1),
            page_size=raw_pagination.get("pageSize", 20),
            total_pages=raw_pagination.get("totalPages", 1),
            total_items=raw_pagination.get("totalItems", 0),
        )
        items = [keys_to_snake(item) for item in json_data.get("items", [])]
        return PagedResponse(items=items, pagination=pagination)

    def _fetch_with_retry(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: Any | None = None,
    ) -> httpx.Response:
        url = path if path.startswith("/") else f"/{path}"
        query = self._build_query(params)
        json_body = keys_to_camel(self._serialize_body(body)) if body is not None else None

        last_exc: Exception | None = None
        max_attempts = self._config.max_retries + 1

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._client.request(
                    method,
                    url,
                    params=query,
                    json=json_body,
                )

                # 429 — retry with Retry-After or backoff
                if response.status_code == 429 and attempt < max_attempts:
                    retry_after = self._parse_retry_after(response)
                    delay = float(retry_after) if retry_after else self._backoff_delay(attempt)
                    time.sleep(delay)
                    continue

                # 5xx — retry with backoff (up to 2 extra retries)
                if response.status_code >= 500 and attempt < min(max_attempts, 3):
                    time.sleep(self._backoff_delay(attempt))
                    continue

                return response

            except httpx.TimeoutException as exc:
                raise LivepassesError(
                    message=f"Request timed out after {self._config.timeout}s",
                    status=0,
                    code="TIMEOUT",
                ) from exc

            except httpx.HTTPError as exc:
                last_exc = exc
                if attempt < max_attempts:
                    time.sleep(self._backoff_delay(attempt))
                    continue

        raise LivepassesError(
            message=f"Request failed after {max_attempts} attempts",
            status=0,
            code="NETWORK_ERROR",
        ) from last_exc

    # -- Utilities -----------------------------------------------------------

    @staticmethod
    def _build_query(params: dict[str, Any] | None) -> dict[str, str] | None:
        if not params:
            return None
        query: dict[str, str] = {}
        for key, value in params.items():
            if value is None:
                continue
            camel_key = keys_to_camel({key: None})
            actual_key = next(iter(camel_key))
            if isinstance(value, bool):
                query[actual_key] = str(value).lower()
            else:
                query[actual_key] = str(value)
        return query or None

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> int | None:
        header = response.headers.get("Retry-After")
        if header is None:
            return None
        try:
            return int(header)
        except ValueError:
            return None

    @staticmethod
    def _backoff_delay(attempt: int) -> float:
        """Exponential backoff: min(1.0 * 2^(attempt-1), 30.0) + jitter."""
        base: float = min(1.0 * (2 ** (attempt - 1)), 30.0)
        return base + random.random() * 0.5  # noqa: S311

    @staticmethod
    def _serialize_body(body: Any) -> Any:
        """Convert dataclass instances to dicts, stripping None values."""
        if hasattr(body, "__dataclass_fields__"):
            raw = asdict(body)
            return _strip_none(raw)
        if isinstance(body, dict):
            return _strip_none(body)
        return body


def _strip_none(d: dict[str, Any]) -> dict[str, Any]:
    """Recursively remove keys with None values from a dict."""
    result: dict[str, Any] = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, dict):
            result[k] = _strip_none(v)
        elif isinstance(v, list):
            result[k] = [
                _strip_none(item) if isinstance(item, dict) else item for item in v
            ]
        else:
            result[k] = v
    return result
