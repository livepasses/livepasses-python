"""Tests for the Livepasses client class."""

from __future__ import annotations

import pytest

from livepasses import Livepasses
from livepasses.resources.passes import PassesResource
from livepasses.resources.templates import TemplatesResource
from livepasses.resources.webhooks import WebhooksResource


def test_raises_on_empty_api_key() -> None:
    with pytest.raises(ValueError, match="API key is required"):
        Livepasses("")


def test_raises_on_whitespace_api_key() -> None:
    with pytest.raises(ValueError, match="API key is required"):
        Livepasses("   ")


def test_resource_attributes_exist() -> None:
    client = Livepasses("test-key")
    assert isinstance(client.passes, PassesResource)
    assert isinstance(client.templates, TemplatesResource)
    assert isinstance(client.webhooks, WebhooksResource)


def test_accepts_custom_options() -> None:
    client = Livepasses(
        "test-key",
        base_url="https://custom.api.com",
        timeout=60.0,
        max_retries=5,
    )
    assert isinstance(client.passes, PassesResource)
