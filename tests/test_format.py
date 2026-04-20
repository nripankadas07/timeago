"""Tests for timeago.format() function."""

import pytest
from datetime import datetime, timedelta, timezone
from timeago import format as timeago_format
from timeago.errors import TimeagoError


class TestFormatBasic:
    """Test basic formatting of datetime deltas."""

    def test_just_now(self):
        """Equal times should return 'just now'."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        assert timeago_format(now, now) == "just now"

    def test_seconds_ago(self):
        """Should format seconds ago."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(seconds=30)
        assert timeago_format(past, now) == "just now"

    def test_one_minute_ago(self):
        """Should format exactly 60 seconds as '1 minute ago'."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(seconds=60)
        assert timeago_format(past, now) == "1 minute ago"

    def test_two_minutes_ago(self):
        """Should format plural minutes."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=2)
        assert timeago_format(past, now) == "2 minutes ago"

    def test_one_hour_ago(self):
        """Should format singular hour."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        assert timeago_format(past, now) == "1 hour ago"

    def test_three_hours_ago(self):
        """Should format plural hours."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=3)
        assert timeago_format(past, now) == "3 hours ago"

    def test_one_day_ago(self):
        """Should format singular day."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1)
        assert timeago_format(past, now) == "1 day ago"

    def test_five_days_ago(self):
        """Should format plural days."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=5)
        assert timeago_format(past, now) == "5 days ago"

    def test_one_week_ago(self):
        """Should format singular week (7 days)."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=7)
        assert timeago_format(past, now) == "1 week ago"

    def test_two_weeks_ago(self):
        """Should format plural weeks."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=14)
        assert timeago_format(past, now) == "2 weeks ago"

    def test_one_month_ago(self):
        """Should format singular month (30 days)."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=30)
        assert timeago_format(past, now) == "1 month ago"

    def test_three_months_ago(self):
        """Should format plural months."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=90)
        assert timeago_format(past, now) == "3 months ago"

    def test_one_year_ago(self):
        """Should format singular year (365 days)."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=365)
        assert timeago_format(past, now) == "1 year ago"

    def test_two_years_ago(self):
        """Should format plural years."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=730)
        assert timeago_format(past, now) == "2 years ago"


class TestFormatFuture:
    """Test formatting of future datetimes."""

    def test_in_one_minute(self):
        """Should format future minute."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(minutes=1)
        assert timeago_format(future, now) == "in 1 minute"

    def test_in_five_minutes(self):
        """Should format future plural minutes."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(minutes=5)
        assert timeago_format(future, now) == "in 5 minutes"

    def test_in_one_hour(self):
        """Should format future singular hour."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(hours=1)
        assert timeago_format(future, now) == "in 1 hour"

    def test_in_two_days(self):
        """Should format future plural days."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(days=2)
        assert timeago_format(future, now) == "in 2 days"

    def test_in_one_year(self):
        """Should format future singular year."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        future = now + timedelta(days=365)
        assert timeago_format(future, now) == "in 1 year"


class TestFormatDefaultNow:
    """Test format with default now parameter."""

    def test_uses_current_time_when_now_is_none(self):
        """Should use current time if now is None."""
        past = datetime.now() - timedelta(hours=1)
        result = timeago_format(past, now=None)
        assert "hour" in result and "ago" in result

    def test_is_approximate_with_default_now(self):
        """Default now should produce reasonable relative time."""
        past = datetime.now() - timedelta(minutes=5)
        result = timeago_format(past)
        assert "minute" in result or "hour" in result


class TestFormatGranularity:
    """Test granularity parameter."""

    def test_granularity_one_default(self):
        """Default granularity should be 1."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=2, minutes=30)
        result = timeago_format(past, now, granularity=1)
        assert result == "2 hours ago"

    def test_granularity_two(self):
        """Granularity=2 should show two units."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=2, minutes=30)
        result = timeago_format(past, now, granularity=2)
        assert result == "2 hours, 30 minutes ago"

    def test_granularity_three(self):
        """Granularity=3 should show up to three units."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, hours=2, minutes=30)
        result = timeago_format(past, now, granularity=3)
        assert result == "1 day, 2 hours, 30 minutes ago"

    def test_granularity_with_zeros_skipped(self):
        """Should skip zero values even with higher granularity."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1, minutes=30)
        result = timeago_format(past, now, granularity=3)
        assert result == "1 day, 30 minutes ago"

    def test_granularity_caps_at_available_units(self):
        """Granularity higher than available units should use all units."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=30)
        result = timeago_format(past, now, granularity=5)
        assert result == "30 minutes ago"


class TestFormatLargeDeltas:
    """Test very large time deltas."""

    def test_one_decade(self):
        """Should format 10 years."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=3650)
        assert timeago_format(past, now) == "10 years ago"

    def test_one_century(self):
        """Should format 100 years."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=36500)
        assert timeago_format(past, now) == "100 years ago"


class TestFormatErrors:
    """Test error handling."""

    def test_naive_and_aware_datetime_mix(self):
        """Should raise error when mixing naive and aware datetimes."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        aware_dt = datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(TimeagoError):
            timeago_format(aware_dt, now)

    def test_non_datetime_input(self):
        """Should raise error for non-datetime input."""
        with pytest.raises(TimeagoError):
            timeago_format("2024-01-01", datetime.now())

    def test_none_as_datetime(self):
        """Should raise error for None as datetime."""
        with pytest.raises(TimeagoError):
            timeago_format(None, datetime.now())

    def test_negative_granularity(self):
        """Should raise error for negative granularity."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(past, now, granularity=-1)

    def test_zero_granularity(self):
        """Should raise error for zero granularity."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(past, now, granularity=0)

    def test_aware_to_aware_mixing(self):
        """Two aware datetimes with different timezones should work (same instant)."""
        utc_tz = timezone.utc
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=utc_tz)
        past = now - timedelta(hours=1)
        result = timeago_format(past, now)
        assert "1 hour ago" == result

    def test_both_aware_same_timezone(self):
        """Both aware, same timezone should work."""
        utc_tz = timezone.utc
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=utc_tz)
        past = datetime(2024, 1, 1, 11, 0, 0, tzinfo=utc_tz)
        result = timeago_format(past, now)
        assert result == "1 hour ago"


class TestFormatBoundaryValues:
    """Test boundary conditions."""

    def test_59_seconds_returns_just_now(self):
        """59 seconds should still be 'just now'."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(seconds=59)
        assert timeago_format(past, now) == "just now"

    def test_60_seconds_returns_one_minute(self):
        """60 seconds should be '1 minute ago'."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(seconds=60)
        assert timeago_format(past, now) == "1 minute ago"

    def test_1_second_returns_just_now(self):
        """1 second should return 'just now'."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(seconds=1)
        assert timeago_format(past, now) == "just now"

    def test_days_to_weeks_boundary(self):
        """6 days should still be days, 7 should be week."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        six_days = now - timedelta(days=6)
        seven_days = now - timedelta(days=7)
        assert "6 days ago" == timeago_format(six_days, now)
        assert "1 week ago" == timeago_format(seven_days, now)

    def test_weeks_to_months_boundary(self):
        """29 days should be weeks, 30 should be month."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        twenty_nine = now - timedelta(days=29)
        thirty = now - timedelta(days=30)
        result_29 = timeago_format(twenty_nine, now)
        assert "4 weeks ago" == result_29
        assert "1 month ago" == timeago_format(thirty, now)

    def test_months_to_years_boundary(self):
        """364 days should be months, 365 should be year."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        three_64 = now - timedelta(days=364)
        three_65 = now - timedelta(days=365)
        result_364 = timeago_format(three_64, now)
        assert "12 months ago" == result_364
        assert "1 year ago" == timeago_format(three_65, now)

    def test_sub_second_is_just_now(self):
        """Sub-second deltas should be 'just now'."""
        now = datetime(2024, 1, 1, 12, 0, 0, 500000)
        past = datetime(2024, 1, 1, 12, 0, 0, 100000)
        assert timeago_format(past, now) == "just now"


class TestFormatSingularPlural:
    """Test singular vs plural forms."""

    def test_1_minute_singular(self):
        """1 minute should be singular."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=1)
        assert timeago_format(past, now) == "1 minute ago"

    def test_2_minutes_plural(self):
        """2 minutes should be plural."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=2)
        assert timeago_format(past, now) == "2 minutes ago"

    def test_1_hour_singular(self):
        """1 hour should be singular."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        assert timeago_format(past, now) == "1 hour ago"

    def test_2_hours_plural(self):
        """2 hours should be plural."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=2)
        assert timeago_format(past, now) == "2 hours ago"

    def test_1_day_singular(self):
        """1 day should be singular."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=1)
        assert timeago_format(past, now) == "1 day ago"

    def test_2_days_plural(self):
        """2 days should be plural."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(days=2)
        assert timeago_format(past, now) == "2 days ago"
