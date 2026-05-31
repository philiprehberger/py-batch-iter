import asyncio

import pytest

from philiprehberger_batch_iter import (
    batch,
    batch_async,
    batch_async_map,
    batch_filter,
    batch_map,
    batch_reduce,
    collect_errors,
    BatchResult,
)


def test_batch_splits_list():
    result = list(batch([1, 2, 3, 4], size=2))
    assert result == [[1, 2], [3, 4]]


def test_batch_with_remainder():
    result = list(batch([1, 2, 3, 4, 5], size=2))
    assert result == [[1, 2], [3, 4], [5]]


def test_batch_with_generator():
    gen = (x for x in range(7))
    result = list(batch(gen, size=3))
    assert result == [[0, 1, 2], [3, 4, 5], [6]]


def test_collect_errors_captures_errors():
    call_count = 0

    def fail_on_second(chunk):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise ValueError("boom")

    result = collect_errors([1, 2, 3, 4, 5, 6], size=2, fn=fail_on_second)

    assert result.processed == 6
    assert len(result.errors) == 1
    assert str(result.errors[0]) == "boom"


def test_batch_result_fields():
    result = BatchResult(processed=10, errors=[], duration_ms=42.5)
    assert result.processed == 10
    assert result.errors == []
    assert result.duration_ms == 42.5


def test_batch_map_doubles():
    result = batch_map([1, 2, 3, 4, 5], size=2, fn=lambda chunk: [x * 2 for x in chunk])
    assert result == [2, 4, 6, 8, 10]


def test_batch_map_with_remainder():
    result = batch_map([1, 2, 3, 4, 5], size=3, fn=lambda chunk: [x + 10 for x in chunk])
    assert result == [11, 12, 13, 14, 15]


def test_batch_map_empty_iterable():
    result = batch_map([], size=2, fn=lambda chunk: chunk)
    assert result == []


def test_batch_map_preserves_order():
    calls: list[list[int]] = []

    def track(chunk: list[int]) -> list[int]:
        calls.append(chunk)
        return chunk

    result = batch_map(range(7), size=3, fn=track)
    assert result == [0, 1, 2, 3, 4, 5, 6]
    assert calls == [[0, 1, 2], [3, 4, 5], [6]]


def test_batch_map_transform_type():
    result = batch_map(["a", "bb", "ccc"], size=2, fn=lambda chunk: [len(s) for s in chunk])
    assert result == [1, 2, 3]


def test_batch_async_map_doubles():
    async def src():
        for x in range(5):
            yield x

    async def double(chunk):
        return [x * 2 for x in chunk]

    result = asyncio.run(batch_async_map(src(), size=2, fn=double))
    assert result == [0, 2, 4, 6, 8]


def test_batch_async_map_empty():
    async def src():
        if False:
            yield 0

    async def fn(chunk):
        return chunk

    result = asyncio.run(batch_async_map(src(), size=3, fn=fn))
    assert result == []


def test_batch_async_yields_chunks():
    async def src():
        for x in range(7):
            yield x

    async def collect():
        return [c async for c in batch_async(src(), size=3)]

    assert asyncio.run(collect()) == [[0, 1, 2], [3, 4, 5], [6]]


def test_batch_filter_evens():
    result = list(batch_filter(range(10), 3, lambda x: x % 2 == 0))
    assert result == [[0, 2, 4], [6, 8]]


def test_batch_filter_empty_iterable():
    result = list(batch_filter([], 5, lambda x: True))
    assert result == []


def test_batch_filter_no_matches():
    result = list(batch_filter([1, 3, 5], 2, lambda x: x % 2 == 0))
    assert result == []


def test_batch_filter_invalid_size():
    with pytest.raises(ValueError):
        list(batch_filter([1], 0, lambda x: True))


def test_batch_reduce_sums():
    result = batch_reduce(range(10), 3, lambda acc, chunk: acc + sum(chunk), 0)
    assert result == 45


def test_batch_reduce_empty():
    result = batch_reduce([], 5, lambda acc, _: acc + 1, 0)
    assert result == 0


def test_batch_reduce_invalid_size():
    with pytest.raises(ValueError):
        batch_reduce([1], 0, lambda a, b: a, 0)
