"""Tests for error handling and TimeagoError."""

from datetime import datetime, timedelta, timezone

import pytest

from timeago import format as timeago_format
from timeago import parse
from timeago.errors import TimeagoError


class TestFormatInputValidation:
    """Test format() input validation."""

    def test_datetime_is_none(self):
        """None as datetime should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(None, datetime.now())

    def test_datetime_is_string(self):
        """String as datetime should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format("2024-01-01", datetime.now())

    def test_datetime_is_int(self):
        """Integer as datetime should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(1234567890, datetime.now())

    def test_datetime_is_float(self):
        """Float as datetime should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(123.456, datetime.now())

    def test_datetime_is_dict(self):
        """Dict as datetime should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format({"year": 2024}, datetime.now())

    def test_datetime_is_list(self):
        """List as datetime should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format([2024, 1, 1], datetime.now())

    def test_now_is_none_is_valid(self):
        """None as 'now' should be valid (uses current time)."""
        past = datetime.now() - timedelta(hours=1)
        result = timeago_format(past, now=None)
        assert "hour" in result

    def test_now_is_string(self):
        """String as 'now' should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(datetime.now(), "2024-01-01")

    def test_now_is_int(self):
        """Integer as 'now' should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            timeago_format(datetime.now(), 1234567890)


class TestTimezoneValidation:
    """Test timezone mismatch detection."""

    def test_naive_datetime_aware_now(self):
        """Naive datetime with aware 'now' should raise error."""
        naive = datetime(2024, 1, 1, 12, 0, 0)
        aware = datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(TimeagoError):
            timeago_format(naive, aware)

    def test_aware_datetime_naive_now(self):
        """Aware datetime with naive 'now' should raise error."""
        aware = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        naive = datetime(2024, 1, 1, 13, 0, 0)
        with pytest.raises(TimeagoError):
            timeago_format(aware, naive)

    def test_both_aware_same_timezone(self):
        """Both aware, same timezone should work."""
        tz = timezone.utc
        dt1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=tz)
        dt2 = datetime(2024, 1, 1, 13, 0, 0, tzinfo=tz)
        result = timeago_format(dt1, dt2)
        assert "1 hour ago" == result

    def test_both_aware_different_timezones(self):
        """Both aware, different timezones should work (same instant)."""
        utc = timezone.utc
        utc_plus_1 = timezone(timedelta(hours=1))
        # 12:00 UTC == 13:00 +01:00
        dt_utc = datetime(2024, 1, 1, 12, 0, 0, tzinfo=utc)
        dt_plus_1 = datetime(2024, 1, 1, 13, 0, 0, tzinfo=utc_plus_1)
        result = timeago_format(dt_utc, dt_plus_1)
        assert "just now" == result

    def test_both_naive(self):
        """Both naive should work."""
        dt1 = datetime(2024, 1, 1, 12, 0, 0)
        dt2 = datetime(2024, 1, 1, 13, 0, 0)
        result = timeago_format(dt1, dt2)
        assert "1 hour ago" == result


class TestGranularityValidation:
    """Test granularity parameter validation."""

    def test_granularity_negative_one(self):
        """Granularity of -1 should raise error."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(past, now, granularity=-1)

    def test_granularity_zero(self):
        """Granularity of 0 should raise error."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(past, now, granularity=0)

    def test_granularity_large_negative(self):
        """Large negative granularity should raise error."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(past, now, granularity=-100)

    def test_granularity_positive_works(self):
        """Positive granularity should work."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        result = timeago_format(past, now, granularity=1)
        assert "1 hour ago" == result


class TestParseInputValidation:
    """Test parse() input validation."""

    def test_parse_none(self):
        """None input should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            parse(None)

    def test_parse_empty_string(self):
        """Empty string should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            parse("")

    def test_parse_whitespace_only(self):
        """Whitespace-only string should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            parse("   ")

    def test_parse_invalid_format(self):
        """Invalid format should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            parse("blah blah blah")

    def test_parse_unknown_unit(self):
        """Unknown unit should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            parse("5 fortnights ago")

    def test_parse_malformed_number(self):
        """Non-numeric value should raise TimeagoError."""
        with pytest.raises(TimeagoError):
            parse("abc minutes ago")

    def test_parse_float_number(self):
        """Float number in parse should raise error or handle."""
        try:
            result = parse("2.5 hours ago")
            # If it doesn't raise, verify result is reasonable
            assert result.total_seconds() > 0
        except TimeagoError:
            pass

    def test_parse_integer_as_input(self):
        """Integer as input should raise error."""
        with pytest.raises(TimeagoError):
            parse(12345)

    def test_parse_dict_as_input(self):
        """Dict as input should raise error."""
        with pytest.raises(TimeagoError):
            parse({"time": "1 hour"})


class TestParseFormats:
    """Test parse() format validation."""

    def test_parse_valid_singular(self):
        """Valid singular format should work."""
        result = parse("1 hour ago")
        assert result == timedelta(hours=1)

    def test_parse_valid_plural(self):
        """Valid plural format should work."""
        result = parse("2 hours ago")
        assert result == timedelta(hours=2)

    def test_parse_valid_future(self):
        """Valid future format should work."""
        result = parse("in 1 hour")
        assert result == timedelta(hours=1)

    def test_parse_missing_ago(self):
        """Missing 'ago' in past format should raise error."""
        with pytest.raises(TimeagoError):
            parse("1 hour")

    def test_parse_missing_in(self):
        """Missing 'in' in future format should raise error."""
        with pytest.raises(TimeagoError):
            parse("1 hour from now")

    def test_parse_wrong_order(self):
        """Wrong order of words should raise error."""
        with pytest.raises(TimeagoError):
            parse("ago 1 hour")

    def test_parse_extra_words(self):
        """Extra words should raise error."""
        with pytest.raises(TimeagoError):
            parse("just 1 hour ago")


class TestErrorMessages:
    """Test that errors are informative."""

    def test_error_is_timeago_error(self):
        """Errors should be TimeagoError type."""
        with pytest.raises(TimeagoError):
            timeago_format("invalid", datetime.now())

    def test_error_has_message(self):
        """TimeagoError should have message."""
        try:
            timeago_format("invalid", datetime.now())
        except TimeagoError as e:
            assert str(e)
            assert len(str(e)) > 0

    def test_parse_error_is_timeago_error(self):
        """Parse errors should be TimeagoError type."""
        with pytest.raises(TimeagoError):
            parse("invalid format")


class TestTypeErrors:
    """Test handling of type errors."""

    def test_format_with_timedelta(self):
        """Passing timedelta as datetime should raise error."""
        td = timedelta(hours=1)
        with pytest.raises(TimeagoError):
            timeago_format(td, datetime.now())

    def test_format_with_date(self):
        """Passing date (not datetime) may raise error."""
        from datetime import date

        d = date(2024, 1, 1)
        try:
            timeago_format(d, datetime.now())
        except (TimeagoError, TypeError, AttributeError):
            pass
