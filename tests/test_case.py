"""Tests for case conversion utilities."""

from __future__ import annotations

from livepasses._utils.case import keys_to_camel, keys_to_snake, to_camel_case, to_snake_case


def test_to_camel_case() -> None:
    assert to_camel_case("template_id") == "templateId"
    assert to_camel_case("is_async_processing") == "isAsyncProcessing"
    assert to_camel_case("id") == "id"
    assert to_camel_case("") == ""


def test_to_snake_case() -> None:
    assert to_snake_case("templateId") == "template_id"
    assert to_snake_case("isAsyncProcessing") == "is_async_processing"
    assert to_snake_case("id") == "id"
    assert to_snake_case("") == ""


def test_keys_to_camel_nested() -> None:
    result = keys_to_camel({
        "template_id": "t1",
        "business_context": {
            "event_name": "Concert",
            "doors_open": "18:00",
        },
        "passes": [
            {"first_name": "John", "last_name": "Doe"},
        ],
    })
    assert result == {
        "templateId": "t1",
        "businessContext": {
            "eventName": "Concert",
            "doorsOpen": "18:00",
        },
        "passes": [
            {"firstName": "John", "lastName": "Doe"},
        ],
    }


def test_keys_to_snake_nested() -> None:
    result = keys_to_snake({
        "templateId": "t1",
        "businessContext": {
            "eventName": "Concert",
            "doorsOpen": "18:00",
        },
        "passes": [
            {"firstName": "John", "lastName": "Doe"},
        ],
    })
    assert result == {
        "template_id": "t1",
        "business_context": {
            "event_name": "Concert",
            "doors_open": "18:00",
        },
        "passes": [
            {"first_name": "John", "last_name": "Doe"},
        ],
    }


def test_keys_to_camel_preserves_non_dict_values() -> None:
    assert keys_to_camel("hello") == "hello"
    assert keys_to_camel(42) == 42
    assert keys_to_camel(None) is None
