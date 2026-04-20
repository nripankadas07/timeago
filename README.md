# timeago

Format datetime deltas as human-readable relative time strings ("3 hours ago", "in 2 days").

## Installation

```bash
pip install timeago
```

## Quick Start

```python
from datetime import datetime, timedelta
from timeago import format

# Basic usage
now = datetime.now()
past = now - timedelta(hours=3)
print(format(past, now))  # "3 hours ago"

# Future times
future = now + timedelta(days=2)
print(format(future, now))  # "in 2 days"

# With granularity (show multiple units)
past = now - timedelta(hours=2, minutes=30)
print(format(past, now, granularity=2))  # "2 hours, 30 minutes ago"

# Parse strings back to timedeltas
from timeago import parse
delta = parse("3 hours ago")
print(delta)  # timedelta(seconds=10800)
```

## API Reference

### `format(dt: datetime, now: datetime | None = None, granularity: int = 1) -> str`

Format a datetime as a relative time string.

**Parameters:**
- `dt` (datetime): The datetime to format
- `now` (datetime | None): Reference time (defaults to current time if None)
- `granularity` (int): Number of units to display (must be positive, default=1)

**Returns:** Human-readable relative time string

**Raises:** `TimeagoError` for invalid inputs

**Examples:**
```python
from datetime import datetime, timedelta
from timeago import format

now = datetime(2024, 1, 1, 12, 0, 0)

# Past
past = now - timedelta(hours=1)
format(past, now)  # "1 hour ago"

# Future
future = now + timedelta(minutes=30)
format(future, now)  # "in 30 minutes"

# Multiple granularity
past = now - timedelta(days=1, hours=2, minutes=15)
format(past, now, granularity=3)  # "1 day, 2 hours, 15 minutes ago"

# Timezone-aware datetimes
from datetime import timezone
utc = timezone.utc
dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=utc)
format(dt - timedelta(hours=1), dt)  # "1 hour ago"
```

### `parse(text: str) -> timedelta`

Parse a relative time string back to a timedelta.

**Parameters:**
- `text` (str): Relative time string to parse

**Returns:** timedelta representing the duration

**Raises:** `TimeagoError` for invalid formats

**Supported Formats:**
- "just now"
- "1 minute ago" / "2 minutes ago"
- "in 1 hour" / "in 3 hours"
- "1 day, 2 hours, 30 minutes ago" (multiple units)

**Examples:**
```python
from timeago import parse

parse("just now")  # timedelta(0)
parse("1 hour ago")  # timedelta(hours=1)
parse("in 2 days")  # timedelta(days=2)
parse("1 day, 2 hours ago")  # timedelta(days=1, hours=2)
```

### `TimeagoError`

Exception raised by timeago functions for validation errors.

```python
from timeago import format, TimeagoError

try:
    format("invalid", None)
except TimeagoError as e:
    print(f"Error: {e}")
```

## Supported Time Units

- seconds (< 60s becomes "just now")
- minutes (60s - 3599s)
- hours (3600s - 86399s)
- days (1 - 6 days)
- weeks (7+ days)
- months (30+ days, 30-day months)
- years (365+ days, 365-day years)

## Edge Cases Handled

- **Sub-second deltas:** Return "just now"
- **Timezone-aware datetimes:** Fully supported
- **Mixed naive/aware:** Raises `TimeagoError`
- **Future times:** Returns "in X" format
- **Singular vs plural:** "1 hour ago" vs "2 hours ago"
- **Multiple granularity:** "2 hours, 30 minutes ago"
- **Boundary values:** 60 seconds = "1 minute ago" (not "60 seconds ago")

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src/timeago tests/

# Run specific test file
pytest tests/test_format.py
```

## Design Principles

- **Simple API:** Two functions, one exception type
- **Type-safe:** Full type hints, mypy compatible
- **Well-tested:** 60+ tests covering happy paths and edge cases
- **Production-ready:** Input validation, clear error messages
- **No external dependencies:** Uses only Python stdlib
- **Clean code:** Functions ≤30 lines, max nesting 3 levels

## License

MIT License - see LICENSE file for details

## Author

nripankadas07
