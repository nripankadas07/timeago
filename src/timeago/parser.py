"""Parse relative time strings back to timedeltas."""

import re
from datetime import timedelta

from timeago.errors import TimeagoError


def parse(text: str) -> timedelta:
    """Parse a relative time string to a timedelta.

    Supports: "just now", "1 hour ago", "2 hours, 30 minutes ago",
    "in 1 day", "in 2 days, 3 hours", etc.

    Args:
        text: A relative time string.

    Returns:
        A timedelta representing the duration.

    Raises:
        TimeagoError: If the format is invalid.
    """
    if not isinstance(text, str):
        raise TimeagoError(f"Expected string, got {type(text).__name__}")

    text = text.strip()
    if not text or text == "just now":
        return timedelta(0) if text == "just now" else _invalid_format(text)

    is_future, is_past = text.startswith("in "), text.endswith(" ago")
    if not (is_future or is_past):
        raise TimeagoError(f"String must start with 'in ' or end with ' ago': {text}")

    unit_text = text[3:] if is_future else text[:-4]
    return _parse_units(unit_text)


def _invalid_format(text: str) -> timedelta:
    """Raise invalid format error."""
    raise TimeagoError("Cannot parse empty string")


def _parse_units(text: str) -> timedelta:
    """Parse the unit portion of a relative time string."""
    unit_mapping = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
        "month": 2592000,
        "year": 31536000,
    }

    unit_pattern = r"second|minute|hour|day|week|month|year"
    pattern = rf"^(\d+)\s+({unit_pattern})s?(,\s*(\d+)\s+({unit_pattern})s?)*$"
    if not re.match(pattern, text.strip()):
        raise TimeagoError(f"Invalid format: {text}")

    pattern_units = rf"(\d+)\s+({unit_pattern})s?"
    matches = re.findall(pattern_units, text)

    if not matches:
        raise TimeagoError(f"No valid time units found in: {text}")

    total_seconds = 0
    for match in matches:
        count = int(match[0])
        unit = match[1]

        if unit not in unit_mapping:
            raise TimeagoError(f"Unknown unit: {unit}")

        total_seconds += count * unit_mapping[unit]

    return timedelta(seconds=total_seconds)
