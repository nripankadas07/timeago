"""Comprehensive tests for granularity parameter."""

import pytest
from datetime import datetime, timedelta
from timeago import format as timeago_format
from timeago.errors import TimeagoError


class TestGranularityOne:
    """Test with granularity=1 (single largest unit)."""

    def test_granularity_1_minutes(self):
        """Should show minutes as single unit."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=5)
        assert timeago_format(past, now, granularity=1) == "5 minutes ago"

    def test_granularity_1_hours(self):
        """Should show hours as single unit."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=2)
        assert timeago_format(past, now, granularity=1) == "2 hours ago"

    def test_granularity_1_ignores_smaller_units(self):
        """Should ignore smaller units with granularity=1."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=2, minutes=45)
        assert timeago_format(past, now, granularity=1) == "2 hours ago"

    def test_granularity_1_days(self):
        """Should show days as single unit."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=3)
        assert timeago_format(past, now, granularity=1) == "3 days ago"


class TestGranularityTwo:
    """Test with granularity=2 (two largest units)."""

    def test_granularity_2_hours_minutes(self):
        """Should show hours and minutes."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1, minutes=30)
        assert timeago_format(past, now, granularity=2) == "1 hour, 30 minutes ago"

    def test_granularity_2_days_hours(self):
        """Should show days and hours."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=2, hours=5)
        assert timeago_format(past, now, granularity=2) == "2 days, 5 hours ago"

    def test_granularity_2_skips_zeros(self):
        """Should skip zero intermediate units."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, minutes=30)
        # Should skip hours (0 hours) and show day and minutes
        result = timeago_format(past, now, granularity=2)
        assert result == "1 day, 30 minutes ago"

    def test_granularity_2_weeks_days(self):
        """Should show weeks and days."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=10)
        # 10 days = 1 week + 3 days
        result = timeago_format(past, now, granularity=2)
        assert result == "1 week, 3 days ago"


class TestGranularityThree:
    """Test with granularity=3 (three largest units)."""

    def test_granularity_3_days_hours_minutes(self):
        """Should show days, hours, and minutes."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, hours=2, minutes=30)
        result = timeago_format(past, now, granularity=3)
        assert result == "1 day, 2 hours, 30 minutes ago"

    def test_granularity_3_skips_zero_hour(self):
        """Should skip zero hour in middle."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, minutes=15)
        result = timeago_format(past, now, granularity=3)
        assert result == "1 day, 15 minutes ago"

    def test_granularity_3_weeks_days_hours(self):
        """Should show weeks, days, and hours."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=10, hours=5)
        # 10 days = 1 week + 3 days
        result = timeago_format(past, now, granularity=3)
        assert result == "1 week, 3 days, 5 hours ago"


class TestGranularityWithFuture:
    """Test granularity with future times."""

    def test_granularity_2_future_minutes_seconds(self):
        """Should show future minutes."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(hours=1, minutes=30)
        assert timeago_format(future, now, granularity=2) == "in 1 hour, 30 minutes"

    def test_granularity_3_future_days_hours_minutes(self):
        """Should show future days, hours, minutes."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(days=2, hours=3, minutes=45)
        result = timeago_format(future, now, granularity=3)
        assert result == "in 2 days, 3 hours, 45 minutes"


class TestGranularityErrors:
    """Test granularity error handling."""

    def test_granularity_negative(self):
        """Negative granularity should raise error."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(past, now, granularity=-1)

    def test_granularity_zero(self):
        """Zero granularity should raise error."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(past, now, granularity=0)

    def test_granularity_string(self):
        """String granularity should raise error."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises((TimeagoError, TypeError)):
            timeago_format(past, now, granularity="two")

    def test_granularity_float(self):
        """Float granularity should raise error or cast."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        # Should either raise or handle gracefully
        try:
            result = timeago_format(past, now, granularity=1.5)
            # If it doesn't raise, result should be valid
            assert "hour" in result
        except (TimeagoError, TypeError):
            pass


class TestGranularityLarge:
    """Test with large granularity values."""

    def test_granularity_10_caps_at_available(self):
        """Granularity > available units should use all."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=45)
        result = timeago_format(past, now, granularity=10)
        # Only 45 minutes, no hours/days
        assert result == "45 minutes ago"

    def test_granularity_5_all_units(self):
        """Granularity=5 with full delta."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=5, hours=4, minutes=30)
        result = timeago_format(past, now, granularity=5)
        # Should show all available: days, hours, minutes
        assert "5 days" in result
        assert "4 hours" in result
        assert "30 minutes" in result


class TestGranularityUnitBreakdown:
    """Test granularity shows correct unit breakdown."""

    def test_granularity_2_respects_max_units(self):
        """Granularity=2 should show exactly 2 units."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, hours=2, minutes=30)
        result = timeago_format(past, now, granularity=2)
        # Should show days and hours, drop minutes
        assert result == "1 day, 2 hours ago"
        assert "minutes" not in result

    def test_granularity_2_drops_smallest_unit(self):
        """Should drop smallest unit when granularity exceeded."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=2, hours=3, minutes=45)
        result = timeago_format(past, now, granularity=2)
        assert result == "2 days, 3 hours ago"
        assert "minutes" not in result


class TestGranularityWithAllUnits:
    """Test granularity with different combinations."""

    def test_months_weeks_days(self):
        """Granularity with months-weeks-days."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=45)
        # 45 days = 1 month (30 days) + 15 days = 1 month, 2 weeks, 1 day
        result = timeago_format(past, now, granularity=3)
        assert "month" in result or "weeks" in result

    def test_years_months_weeks(self):
        """Granularity with years-months-weeks."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=400)
        # 400 days = 1 year (365) + 35 days
        result = timeago_format(past, now, granularity=3)
        assert "1 year" in result
