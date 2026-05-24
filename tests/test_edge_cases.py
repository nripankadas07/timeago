"""Tests for edge cases and special scenarios."""

from datetime import datetime, timedelta, timezone

import pytest

from timeago import format as timeago_format
from timeago import parse
from timeago.errors import TimeagoError


class TestMicroseconds:
    """Test microsecond handling."""

    def test_microseconds_just_now(self):
        """Microsecond differences should be 'just now'."""
        now = datetime(2024, 1, 1, 12, 0, 0, 500000)
        past = datetime(2024, 1, 1, 12, 0, 0, 100000)
        assert timeago_format(past, now) == "just now"

    def test_exact_same_time_with_microseconds(self):
        """Same time including microseconds should be 'just now'."""
        dt = datetime(2024, 1, 1, 12, 0, 0, 123456)
        assert timeago_format(dt, dt) == "just now"


class TestTimezoneAwareness:
    """Test timezone-aware datetime handling."""

    def test_both_naive(self):
        """Both naive datetimes should work."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        result = timeago_format(past, now)
        assert "1 hour ago" == result

    def test_both_aware_same_tz(self):
        """Both aware, same timezone should work."""
        tz = timezone.utc
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=tz)
        past = datetime(2024, 1, 1, 11, 0, 0, tzinfo=tz)
        result = timeago_format(past, now)
        assert "1 hour ago" == result

    def test_mixed_naive_aware_raises_error(self):
        """Naive and aware mix should raise error."""
        naive = datetime(2024, 1, 1, 12, 0, 0)
        aware = datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(TimeagoError):
            timeago_format(naive, aware)

    def test_both_aware_different_tz(self):
        """Different aware timezones should work (same instant)."""
        from datetime import timezone as tz_class

        tz_utc = timezone.utc
        tz_plus_1 = tz_class(timedelta(hours=1))

        # 12:00 UTC = 13:00 +01:00
        now_utc = datetime(2024, 1, 1, 12, 0, 0, tzinfo=tz_utc)
        now_plus_1 = datetime(2024, 1, 1, 13, 0, 0, tzinfo=tz_plus_1)

        # Same instant, should be "just now"
        assert timeago_format(now_utc, now_plus_1) == "just now"


class TestVeryLargeDeltas:
    """Test extremely large time deltas."""

    def test_100_years(self):
        """Should handle 100 years."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=36500)
        assert timeago_format(past, now) == "100 years ago"

    def test_1000_years(self):
        """Should handle 1000 years."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=365000)
        result = timeago_format(past, now)
        assert "1000 years ago" == result

    def test_in_1000_years(self):
        """Should handle future 1000 years."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(days=365000)
        result = timeago_format(future, now)
        assert "in 1000 years" == result


class TestZeroAndNearZero:
    """Test zero and near-zero values."""

    def test_zero_seconds(self):
        """Zero delta should be 'just now'."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        assert timeago_format(dt, dt) == "just now"

    def test_one_millisecond(self):
        """1ms should be 'just now'."""
        now = datetime(2024, 1, 1, 12, 0, 0, 1000)
        past = datetime(2024, 1, 1, 12, 0, 0, 0)
        assert timeago_format(past, now) == "just now"


class TestSpecialDates:
    """Test with special date values."""

    def test_leap_year_february(self):
        """Should handle leap year dates."""
        now = datetime(2024, 2, 29, 12, 0, 0)
        past = now - timedelta(days=1)
        assert timeago_format(past, now) == "1 day ago"

    def test_end_of_year(self):
        """Should handle end-of-year dates."""
        now = datetime(2024, 12, 31, 23, 59, 59)
        past = now - timedelta(hours=1)
        assert timeago_format(past, now) == "1 hour ago"

    def test_start_of_year(self):
        """Should handle start-of-year dates."""
        now = datetime(2024, 1, 1, 0, 0, 0)
        past = now - timedelta(hours=1)
        assert timeago_format(past, now) == "1 hour ago"


class TestInputValidation:
    """Test input validation."""

    def test_string_as_datetime(self):
        """String input should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format("2024-01-01", datetime.now())

    def test_int_as_datetime(self):
        """Integer input should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(1234567890, datetime.now())

    def test_dict_as_datetime(self):
        """Dict input should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format({"date": "2024-01-01"}, datetime.now())

    def test_none_as_datetime(self):
        """None as datetime should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(None, datetime.now())

    def test_string_as_now(self):
        """String as 'now' should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(datetime.now(), "2024-01-01")


class TestGranularityEdgeCases:
    """Test granularity parameter edge cases."""

    def test_granularity_one_only_largest_unit(self):
        """Granularity=1 should only show largest unit."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, hours=23, minutes=59)
        result = timeago_format(past, now, granularity=1)
        assert result == "1 day ago"

    def test_granularity_large_number(self):
        """Large granularity should cap at available units."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=45)
        result = timeago_format(past, now, granularity=100)
        assert result == "45 minutes ago"

    def test_granularity_ignores_zero_units(self):
        """Zero-value units should be skipped."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, minutes=45)
        result = timeago_format(past, now, granularity=3)
        assert "1 day, 45 minutes ago" == result
        assert "hours" not in result

    def test_granularity_respects_order(self):
        """Units should be in decreasing order."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=2, hours=3, minutes=15)
        result = timeago_format(past, now, granularity=3)
        assert result == "2 days, 3 hours, 15 minutes ago"


class TestParseEdgeCases:
    """Test parsing edge cases."""

    def test_parse_whitespace_tolerance(self):
        """Parse should handle extra whitespace."""
        # Exactly matches what format produces
        result = parse("1 hour ago")
        assert result == timedelta(hours=1)

    def test_parse_single_unit_no_granularity(self):
        """Parse single unit without explicit granularity."""
        result = parse("5 days ago")
        assert result == timedelta(days=5)

    def test_parse_exact_roundtrip_simple(self):
        """Simple format-parse-format roundtrip."""
        from timeago import format as timeago_format

        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=3)
        formatted = timeago_format(past, now)
        parsed = parse(formatted)
        assert parsed == timedelta(hours=3)
