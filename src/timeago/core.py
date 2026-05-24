"""Core timeago formatting logic."""

from datetime import datetime, timedelta

from timeago.errors import TimeagoError


def format(dt: datetime, now: datetime | None = None, granularity: int = 1) -> str:
    """Format a datetime as a relative time string.

    Args:
        dt: The datetime to format.
        now: The reference time (defaults to current time if None).
        granularity: Number of units to show (1-based). Must be positive.

    Returns:
        A human-readable relative time string like "3 hours ago" or "in 2 days".

    Raises:
        TimeagoError: If inputs are invalid or incompatible.
    """
    _validate_inputs(dt, now, granularity)
    now = now or datetime.now()
    delta = now - dt
    return (
        _format_future(-delta, granularity)
        if delta.total_seconds() < 0
        else _format_past(delta, granularity)
    )


def _validate_inputs(dt: object, now: object, granularity: int) -> None:
    """Validate all inputs."""
    if not isinstance(dt, datetime):
        raise TimeagoError(f"Expected datetime for dt, got {type(dt).__name__}")
    if now is not None:
        if not isinstance(now, datetime):
            raise TimeagoError(f"Expected datetime for now, got {type(now).__name__}")
        _validate_timezone_compatibility(dt, now)
    _validate_granularity(granularity)


def _validate_datetime(dt: object, name: str) -> None:
    """Validate that an object is a datetime instance."""
    if not isinstance(dt, datetime):
        raise TimeagoError(f"Expected datetime for {name}, got {type(dt).__name__}")


def _validate_granularity(granularity: int) -> None:
    """Validate that granularity is a positive integer."""
    if not isinstance(granularity, int):
        raise TimeagoError(f"granularity must be int, got {type(granularity).__name__}")
    if granularity <= 0:
        raise TimeagoError(f"granularity must be positive, got {granularity}")


def _validate_timezone_compatibility(dt: datetime, now: datetime) -> None:
    """Check that both datetimes have compatible timezone info."""
    dt_aware = dt.tzinfo is not None
    now_aware = now.tzinfo is not None

    if dt_aware != now_aware:
        raise TimeagoError("Cannot mix naive and aware datetimes")


def _format_past(delta: timedelta, granularity: int) -> str:
    """Format a past timedelta as 'X ago'."""
    total_seconds = delta.total_seconds()

    if total_seconds < 60:
        return "just now"

    units = _break_down_delta(delta)
    parts = _format_units(units, granularity)

    if not parts:
        return "just now"

    return ", ".join(parts) + " ago"


def _format_future(delta: timedelta, granularity: int) -> str:
    """Format a future timedelta as 'in X'."""
    units = _break_down_delta(delta)
    parts = _format_units(units, granularity)

    if not parts:
        return "just now"

    return "in " + ", ".join(parts)


def _break_down_delta(delta: timedelta) -> dict[str, int]:
    """Break a timedelta into time units.

    Returns a dict with keys: years, months, weeks, days, hours, minutes, seconds
    """
    total_seconds = int(delta.total_seconds())

    if total_seconds < 0:
        total_seconds = -total_seconds

    years = total_seconds // (365 * 86400)
    remainder = total_seconds % (365 * 86400)

    months = remainder // (30 * 86400)
    remainder %= 30 * 86400

    weeks = remainder // (7 * 86400)
    remainder %= 7 * 86400

    days = remainder // 86400
    remainder %= 86400

    hours = remainder // 3600
    remainder %= 3600

    minutes = remainder // 60
    seconds = remainder % 60

    return {
        "years": years,
        "months": months,
        "weeks": weeks,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }


def _format_units(units: dict[str, int], granularity: int) -> list[str]:
    """Convert units dict to formatted strings, respecting granularity.

    Only includes non-zero units, up to granularity limit.
    """
    unit_names = ["years", "months", "weeks", "days", "hours", "minutes", "seconds"]
    parts: list[str] = []

    for unit in unit_names:
        if len(parts) >= granularity:
            break

        count = units[unit]
        if count == 0:
            continue

        parts.append(_format_unit(count, unit))

    return parts


def _format_unit(count: int, unit: str) -> str:
    """Format a single unit as a string (e.g., '2 hours')."""
    if count == 1:
        singular = unit.rstrip("s")
        return f"{count} {singular}"
    else:
        return f"{count} {unit}"
