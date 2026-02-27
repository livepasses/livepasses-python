"""Template-related types for the Livepasses SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TemplateListItem:
    """A template as returned by the list endpoint."""

    id: str
    name: str
    type: str
    status: str
    pass_count: int
    created_at: str
    description: str | None = None
    updated_at: str | None = None


@dataclass
class TemplateDetail(TemplateListItem):
    """Full template details."""

    business_features: dict[str, Any] | None = None
    platform_support: dict[str, Any] | None = None
    media_configuration: dict[str, Any] | None = None


@dataclass
class ListTemplatesParams:
    """Parameters for listing templates."""

    page: int | None = None
    page_size: int | None = None
    search_term: str | None = None
    sort_by: str | None = None
    sort_descending: bool | None = None
    type: str | None = None
    status: str | None = None


@dataclass
class CreateTemplateParams:
    """Parameters for creating a template."""

    name: str
    business_features: dict[str, Any]
    description: str | None = None
    required_media: list[str] | None = None


@dataclass
class UpdateTemplateParams:
    """Parameters for updating a template."""

    name: str | None = None
    description: str | None = None
    business_features: dict[str, Any] | None = None
