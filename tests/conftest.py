"""Shared pytest fixtures for Livepasses SDK tests."""

from __future__ import annotations

import pytest

from livepasses import Livepasses


@pytest.fixture()
def client() -> Livepasses:
    """Return a Livepasses client configured for testing."""
    return Livepasses(
        "test-api-key",
        base_url="https://api.test.livepasses.com",
        max_retries=0,
    )
