"""Templates resource for the Livepasses SDK."""

from __future__ import annotations

import dataclasses
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from livepasses.types.common import PagedResponse
from livepasses.types.templates import (
    CreateTemplateParams,
    ListTemplatesParams,
    TemplateDetail,
    TemplateListItem,
    UpdateTemplateParams,
)

if TYPE_CHECKING:
    from livepasses._http import HttpClient


class TemplatesResource:
    """Resource for template operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, params: ListTemplatesParams | None = None) -> PagedResponse[TemplateListItem]:
        """List templates with pagination."""
        query = _params_to_dict(params)
        paged = self._http.get_paged("/api/templates", query)
        return PagedResponse(
            items=[_build_template_item(item) for item in paged.items],
            pagination=paged.pagination,
        )

    def get(self, template_id: str) -> TemplateDetail:
        """Get a template by ID."""
        data = self._http.get(f"/api/templates/{template_id}")
        return _build_template_detail(data)

    def create(self, params: CreateTemplateParams) -> TemplateDetail:
        """Create a new template."""
        data = self._http.post("/api/templates", params)
        return _build_template_detail(data)

    def update(self, template_id: str, params: UpdateTemplateParams) -> TemplateDetail:
        """Update a template."""
        data = self._http.put(f"/api/templates/{template_id}", params)
        return _build_template_detail(data)

    def activate(self, template_id: str) -> None:
        """Activate a template."""
        self._http.post(f"/api/templates/{template_id}/activate")

    def deactivate(self, template_id: str) -> None:
        """Deactivate a template."""
        self._http.post(f"/api/templates/{template_id}/deactivate")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _params_to_dict(params: Any) -> dict[str, Any]:
    if params is None:
        return {}
    if hasattr(params, "__dataclass_fields__"):
        return {k: v for k, v in asdict(params).items() if v is not None}
    return dict(params)


def _build_template_item(data: Any) -> TemplateListItem:
    if not isinstance(data, dict):
        return TemplateListItem(**{})
    field_names = {f.name for f in dataclasses.fields(TemplateListItem)}
    filtered = {k: v for k, v in data.items() if k in field_names}
    return TemplateListItem(**filtered)


def _build_template_detail(data: Any) -> TemplateDetail:
    if not isinstance(data, dict):
        return TemplateDetail(**{})
    field_names = {f.name for f in dataclasses.fields(TemplateDetail)}
    filtered = {k: v for k, v in data.items() if k in field_names}
    return TemplateDetail(**filtered)
