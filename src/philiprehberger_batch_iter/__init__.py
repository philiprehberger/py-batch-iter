"""Batch processing with progress tracking and error handling."""

from __future__ import annotations

import sys
import time
from collections.abc import AsyncIterable, AsyncIterator, Callable, Iterable, Iterator
from dataclasses import dataclass, field
from itertools import islice
from typing import TypeVar

__all__ = [
    "batch",
    "batch_async",
    "batch_map",
    "collect_errors",
    "BatchResult",
]

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class BatchResult:
    """Result of processing batches with error collection.

    Attributes:
        processed: Total number of items processed.
        errors: List of exceptions caught during processing.
        duration_ms: Total processing time in milliseconds.
    """

    processed: int = 0
    errors: list[Exception] = field(default_factory=list)
    duration_ms: float = 0.0


def batch(
    iterable: Iterable[T],
    size: int,
    *,
    progress: bool = False,
) -> Iterator[list[T]]:
    """Yield successive batches of *size* items from *iterable*.

    Uses ``itertools.islice`` internally so it works efficiently with
    generators and other lazy iterables without consuming the entire
    sequence into memory.

    Args:
        iterable: The iterable to split into batches.
        size: Maximum number of items per batch.
        progress: If ``True``, print a progress line to stderr after
            each batch is yielded.

    Yields:
        Lists of up to *size* items.
    """
    if size < 1:
        msg = "Batch size must be at least 1"
        raise ValueError(msg)

    it = iter(iterable)
    batch_num = 0

    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        batch_num += 1
        if progress:
            print(
                f"batch {batch_num}: {len(chunk)} items",
                file=sys.stderr,
            )
        yield chunk


async def batch_async(
    async_iterable: AsyncIterable[T],
    size: int,
) -> AsyncIterator[list[T]]:
    """Async generator that yields batches of *size* items.

    Args:
        async_iterable: The async iterable to split into batches.
        size: Maximum number of items per batch.

    Yields:
        Lists of up to *size* items.
    """
    if size < 1:
        msg = "Batch size must be at least 1"
        raise ValueError(msg)

    current: list[T] = []
    async for item in async_iterable:
        current.append(item)
        if len(current) == size:
            yield current
            current = []

    if current:
        yield current


def batch_map(
    iterable: Iterable[T],
    size: int,
    fn: Callable[[list[T]], list[R]],
) -> list[R]:
    """Process an iterable in batches, applying *fn* to each batch, returning flattened results.

    Each batch is passed to *fn*, which must return a list. The
    returned lists are concatenated into a single flat result list.

    Args:
        iterable: The iterable to split into batches.
        size: Maximum number of items per batch.
        fn: Callable that receives a batch and returns a list of results.

    Returns:
        A flat list of all results from every batch.
    """
    results: list[R] = []
    for chunk in batch(iterable, size):
        results.extend(fn(chunk))
    return results


def collect_errors(
    iterable: Iterable[T],
    size: int,
    fn: Callable[[list[T]], None],
) -> BatchResult:
    """Process batches and collect errors instead of raising.

    Calls *fn* with each batch. If *fn* raises an exception the error
    is recorded and processing continues with the next batch.

    Args:
        iterable: The iterable to split into batches.
        size: Maximum number of items per batch.
        fn: Callable invoked with each batch.

    Returns:
        A :class:`BatchResult` with counts and any captured errors.
    """
    result = BatchResult()
    start = time.monotonic()

    for chunk in batch(iterable, size):
        try:
            fn(chunk)
        except Exception as exc:  # noqa: BLE001
            result.errors.append(exc)
        result.processed += len(chunk)

    elapsed = time.monotonic() - start
    result.duration_ms = round(elapsed * 1000, 2)
    return result
