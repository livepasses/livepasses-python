"""Internal HTTP client for the Livepasses SDK."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, fields, is_dataclass
from typing import Any

import httpx

from livepasses._utils.case import keys_to_camel, keys_to_snake, to_camel_case
from livepasses.errors import LivepassesError, create_typed_error
from livepasses.types.common import PagedResponse, PaginationMetadata


_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE"})


def _read_envelope(response: httpx.Response) -> dict[str, Any] | None:
    """Parse the JSON envelope, or return None for an empty/non-JSON body
    (a challenge 401, a proxy 5xx, or a 204)."""
    try:
        data = response.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


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
        json_data = _read_envelope(response)

        if response.status_code >= 400 or (
            json_data is not None and not json_data.get("success", False)
        ):
            raise self._to_error(response, (json_data or {}).get("error") or {})

        return keys_to_snake((json_data or {}).get("data"))

    def _request_paged(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> PagedResponse[Any]:
        response = self._fetch_with_retry("GET", path, params=params)
        json_data = _read_envelope(response)

        if response.status_code >= 400 or (
            json_data is not None and not json_data.get("success", False)
        ):
            raise self._to_error(response, (json_data or {}).get("error") or {})

        json_data = json_data or {}
        raw_pagination = json_data.get("pagination", {})
        pagination = PaginationMetadata(
            current_page=raw_pagination.get("currentPage", 1),
            page_size=raw_pagination.get("pageSize", 20),
            total_pages=raw_pagination.get("totalPages", 1),
            total_items=raw_pagination.get("totalItems", 0),
        )
        items = [keys_to_snake(item) for item in json_data.get("items", [])]
        return PagedResponse(items=items, pagination=pagination)

    def _to_error(self, response: httpx.Response, error: dict[str, Any]) -> LivepassesError:
        message = error.get("message")
        code = error.get("code")
        return create_typed_error(
            message=message if message is not None else f"API request failed with status {response.status_code}",
            status=response.status_code,
            code=code if code is not None else "GENERAL_ERROR",
            details=error.get("details"),
            retry_after=self._parse_retry_after(response),
            fields=error.get("fields"),
        )

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
        json_body = _to_wire(body) if body is not None else None

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

                # 5xx — retry with backoff (up to 2 extra retries), only for idempotent
                # methods. No SDK sends an Idempotency-Key, so the gate is the HTTP
                # method alone.
                if (
                    response.status_code >= 500
                    and method.upper() in _IDEMPOTENT_METHODS
                    and attempt < min(max_attempts, 3)
                ):
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

def _to_wire(obj: Any) -> Any:
    """Convert a request body to its JSON wire shape.

    Dataclasses and dicts get camelCase keys and lose ``None`` values, recursively.
    A dataclass field marked ``verbatim`` in its metadata (``updated_fields``,
    ``metadata``) holds the caller's own data and is sent exactly as written.
    """
    if is_dataclass(obj) and not isinstance(obj, type):
        wire: dict[str, Any] = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            if value is None:
                continue
            wire[to_camel_case(f.name)] = value if f.metadata.get("verbatim") else _to_wire(value)
        return wire
    if isinstance(obj, dict):
        return {to_camel_case(k): _to_wire(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_to_wire(item) for item in obj]
    return obj
