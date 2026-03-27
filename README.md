# philiprehberger-batch-iter

[![Tests](https://github.com/philiprehberger/py-batch-iter/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-batch-iter/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-batch-iter.svg)](https://pypi.org/project/philiprehberger-batch-iter/)
[![License](https://img.shields.io/github/license/philiprehberger/py-batch-iter)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Batch processing with progress tracking and error handling.

## Installation

```bash
pip install philiprehberger-batch-iter
```

## Usage

```python
from philiprehberger_batch_iter import batch, collect_errors

# Split any iterable into fixed-size batches
for chunk in batch(range(10), size=3):
    print(chunk)
# [0, 1, 2]
# [3, 4, 5]
# [6, 7, 8]
# [9]

# Enable progress output to stderr
for chunk in batch(range(100), size=25, progress=True):
    process(chunk)
# batch 1: 25 items
# batch 2: 25 items
# ...
```

### Error collection

```python
from philiprehberger_batch_iter import collect_errors

def process_batch(items):
    for item in items:
        if item < 0:
            raise ValueError(f"negative value: {item}")

result = collect_errors([1, 2, -3, 4, 5, -6], size=2, fn=process_batch)
print(result.processed)     # 6
print(len(result.errors))   # 2
print(result.duration_ms)   # 0.12
```

### Async batching

```python
from philiprehberger_batch_iter import batch_async

async def process():
    async for chunk in batch_async(async_data_source(), size=50):
        await handle(chunk)
```

## API

| Function / Class | Description |
|------------------|-------------|
| `batch(iterable, size, progress=False)` | Yield fixed-size batches from an iterable |
| `batch_async(async_iterable, size)` | Async generator yielding fixed-size batches |
| `collect_errors(iterable, size, fn)` | Process batches and collect errors into a result |
| `BatchResult` | Dataclass with `processed`, `errors`, `duration_ms` |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
