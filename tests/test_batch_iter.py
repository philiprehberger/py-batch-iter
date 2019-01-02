from philiprehberger_batch_iter import batch, collect_errors, BatchResult


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
