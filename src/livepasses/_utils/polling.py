"""Polling utility for batch operations."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def poll_until_complete(
    fn: Callable[[], T],
    is_complete: Callable[[T], bool],
    *,
    interval: float = 2.0,
    max_attempts: int = 150,
    on_progress: Callable[[T], None] | None = None,
) -> T:
    """Poll a function until a completion condition is met.

    Args:
        fn: Callable that returns the current status.
        is_complete: Predicate that returns True when polling should stop.
        interval: Seconds between polls (default 2.0).
        max_attempts: Maximum number of poll attempts (default 150).
        on_progress: Optional callback invoked with each poll result.

    Returns:
        The final result from *fn*.
    """
    for attempt in range(max_attempts):
        result = fn()
        if on_progress is not None:
            on_progress(result)
        if is_complete(result):
            return result
        if attempt < max_attempts - 1:
            time.sleep(interval)

    # Final attempt after exhausting max_attempts
    final_result = fn()
    if on_progress is not None:
        on_progress(final_result)
    return final_result
