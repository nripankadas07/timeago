"""Tests for timeago.parse() function."""

import pytest
from datetime import timedelta
from timeago import parse
from timeago.errors import TimeagoError


class TestParseBasic:
    """Test basic parsing of relative time strings."""

    def test_parse_just_now(self):
        """Parse 'just now'."""
        result = parse("just now")
        assert result == timedelta(0)

    def test_parse_one_minute_ago(self):
        """Parse '1 minute ago'."""
        result = parse("1 minute ago")
        assert result == timedelta(minutes=1)

    def test_parse_two_minutes_ago(self):
        """Parse '2 minutes ago'."""
        result = parse("2 minutes ago")
        assert result == timedelta(minutes=2)

    def test_parse_one_hour_ago(self):
        """Parse '1 hour ago'."""
        result = parse("1 hour ago")
        assert result == timedelta(hours=1)

    def test_parse_three_hours_ago(self):
        """Parse '3 hours ago'."""
        result = parse("3 hours ago")
        assert result == timedelta(hours=3)

    def test_parse_one_day_ago(self):
        """Parse '1 day ago'."""
        result = parse("1 day ago")
        assert result == timedelta(days=1)

    def test_parse_five_days_ago(self):
        """Parse '5 days ago'."""
        result = parse("5 days ago")
        assert result == timedelta(days=5)

    def test_parse_one_week_ago(self):
        """Parse '1 week ago'."""
        result = parse("1 week ago")
        assert result == timedelta(days=7)

    def test_parse_two_weeks_ago(self):
        """Parse '2 weeks ago'."""
        result = parse("2 weeks ago")
        assert result == timedelta(days=14)

    def test_parse_one_month_ago(self):
        """Parse '1 month ago'."""
        result = parse("1 month ago")
        assert result == timedelta(days=30)

    def test_parse_three_months_ago(self):
        """Parse '3 months ago'."""
        result = parse("3 months ago")
        assert result == timedelta(days=90)

    def test_parse_one_year_ago(self):
        """Parse '1 year ago'."""
        result = parse("1 year ago")
        assert result == timedelta(days=365)

    def test_parse_two_years_ago(self):
        """Parse '2 years ago'."""
        result = parse("2 years ago")
        assert result == timedelta(days=730)


class TestParseFuture:
    """Test parsing of future time strings."""

    def test_parse_in_one_minute(self):
        """Parse 'in 1 minute'."""
        result = parse("in 1 minute")
        assert result == timedelta(minutes=1)

    def test_parse_in_five_minutes(self):
        """Parse 'in 5 minutes'."""
        result = parse("in 5 minutes")
        assert result == timedelta(minutes=5)

    def test_parse_in_one_hour(self):
        """Parse 'in 1 hour'."""
        result = parse("in 1 hour")
        assert result == timedelta(hours=1)

    def test_parse_in_two_days(self):
        """Parse 'in 2 days'."""
        result = parse("in 2 days")
        assert result == timedelta(days=2)

    def test_parse_in_one_year(self):
        """Parse 'in 1 year'."""
        result = parse("in 1 year")
        assert result == timedelta(days=365)


class TestParseMultiGranularity:
    """Test parsing of multi-granularity strings."""

    def test_parse_two_units(self):
        """Parse multi-granularity string with 2 units."""
        result = parse("2 hours, 30 minutes ago")
        assert result == timedelta(hours=2, minutes=30)

    def test_parse_three_units(self):
        """Parse multi-granularity string with 3 units."""
        result = parse("1 day, 2 hours, 30 minutes ago")
        assert result == timedelta(days=1, hours=2, minutes=30)

    def test_parse_future_multiple_units(self):
        """Parse future multi-granularity string."""
        result = parse("in 1 day, 2 hours")
        assert result == timedelta(days=1, hours=2)


class TestParseErrors:
    """Test error handling."""

    def test_parse_invalid_format(self):
        """Should raise error for invalid format."""
        with pytest.raises(TimeagoError):
            parse("invalid string")

    def test_parse_empty_string(self):
        """Should raise error for empty string."""
        with pytest.raises(TimeagoError):
            parse("")

    def test_parse_none(self):
        """Should raise error for None."""
        with pytest.raises(TimeagoError):
            parse(None)

    def test_parse_malformed_number(self):
        """Should raise error for malformed number."""
        with pytest.raises(TimeagoError):
            parse("abc minutes ago")

    def test_parse_unknown_unit(self):
        """Should raise error for unknown unit."""
        with pytest.raises(TimeagoError):
            parse("5 fortnights ago")


class TestParseRoundTrip:
    """Test format -> parse -> format round trip."""

    def test_roundtrip_one_hour(self):
        """Format -> parse -> format should preserve value."""
        from timeago import format as timeago_format
        from datetime import datetime

        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        formatted = timeago_format(past, now)
        parsed = parse(formatted)
        reformatted = timeago_format(now - parsed, now)
        assert formatted == reformatted

    def test_roundtrip_multiple_units(self):
        """Round trip with granularity=2."""
        from timeago import format as timeago_format
        from datetime import datetime

        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=3, minutes=45)
        formatted = timeago_format(past, now, granularity=2)
        parsed = parse(formatted)
        reformatted = timeago_format(now - parsed, now, granularity=2)
        assert formatted == reformatted
