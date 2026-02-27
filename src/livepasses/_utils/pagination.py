"""Auto-pagination utility."""

from __future__ import annotations

from typing import Callable, Generator, TypeVar

from livepasses.types.common import PagedResponse

T = TypeVar("T")


def auto_paginate(
    fn: Callable[[int], PagedResponse[T]],
) -> Generator[T, None, None]:
    """Yield all items across all pages.

    Args:
        fn: Callable that takes a page number (1-indexed) and returns a
            :class:`PagedResponse`.

    Yields:
        Each item from every page.
    """
    page = 1
    while True:
        response = fn(page)
        yield from response.items
        if page >= response.pagination.total_pages or len(response.items) == 0:
            break
        page += 1
