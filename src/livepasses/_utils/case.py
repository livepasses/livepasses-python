"""Snake_case <-> camelCase conversion utilities."""

from __future__ import annotations

import re
from typing import Any

_CAMEL_RE = re.compile(r"([A-Z])")
_SNAKE_RE = re.compile(r"_([a-z])")


def to_camel_case(s: str) -> str:
    """Convert a snake_case string to camelCase."""
    return _SNAKE_RE.sub(lambda m: m.group(1).upper(), s)


def to_snake_case(s: str) -> str:
    """Convert a camelCase string to snake_case."""
    return _CAMEL_RE.sub(r"_\1", s).lower().lstrip("_")


def keys_to_camel(obj: Any) -> Any:
    """Recursively convert all dict keys from snake_case to camelCase."""
    if isinstance(obj, dict):
        return {to_camel_case(k): keys_to_camel(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [keys_to_camel(item) for item in obj]
    return obj


def keys_to_snake(obj: Any) -> Any:
    """Recursively convert all dict keys from camelCase to snake_case."""
    if isinstance(obj, dict):
        return {to_snake_case(k): keys_to_snake(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [keys_to_snake(item) for item in obj]
    return obj
