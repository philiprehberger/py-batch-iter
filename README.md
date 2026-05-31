# philiprehberger-batch-iter

[![Tests](https://github.com/philiprehberger/py-batch-iter/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-batch-iter/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-batch-iter.svg)](https://pypi.org/project/philiprehberger-batch-iter/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-batch-iter)](https://github.com/philiprehberger/py-batch-iter/commits/main)

Batch processing with progress tracking and error handling.

## Installation

```bash
pip install philiprehberger-batch-iter
```

## Usage

```python
from philiprehberger_batch_iter import batch, batch_map, collect_errors

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

### Batch map

```python
from philiprehberger_batch_iter import batch_map

# Process items in batches and collect flattened results
results = batch_map(range(10), size=3, fn=lambda chunk: [x * 2 for x in chunk])
print(results)
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
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

### Filtering and reducing in batches

```python
from philiprehberger_batch_iter import batch_filter, batch_reduce

# Stream items through a predicate, yielding batches of matches
for chunk in batch_filter(range(10), size=3, predicate=lambda x: x % 2 == 0):
    print(chunk)
# [0, 2, 4]
# [6, 8]

# Reduce over batches without holding the full sequence in memory
total = batch_reduce(
    range(10),
    size=3,
    fn=lambda acc, chunk: acc + sum(chunk),
    initial=0,
)
print(total)  # 45
```

### Async batching

```python
from philiprehberger_batch_iter import batch_async

async def process():
    async for chunk in batch_async(async_data_source(), size=50):
        await handle(chunk)
```

### Async batch map

```python
from philiprehberger_batch_iter import batch_async_map

async def upload(chunk):
    return await api.upload_many(chunk)

results = await batch_async_map(items_aiter, size=100, fn=upload)
```

## API

| Function / Class | Description |
|------------------|-------------|
| `batch(iterable, size, progress=False)` | Yield fixed-size batches from an iterable |
| `batch_map(iterable, size, fn)` | Process batches with `fn` and return a flat result list |
| `batch_filter(iterable, size, predicate)` | Yield batches of items matching `predicate` |
| `batch_reduce(iterable, size, fn, initial)` | Reduce over batches, calling `fn(acc, batch)` per batch |
| `batch_async(async_iterable, size)` | Async generator yielding fixed-size batches |
| `batch_async_map(async_iterable, size, fn)` | Async counterpart to `batch_map`, awaits each batch |
| `collect_errors(iterable, size, fn)` | Process batches and collect errors into a result |
| `BatchResult` | Dataclass with `processed`, `errors`, `duration_ms` |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-batch-iter)

🐛 [Report issues](https://github.com/philiprehberger/py-batch-iter/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-batch-iter/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
