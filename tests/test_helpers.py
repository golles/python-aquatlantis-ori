"""Helpers tests."""

from datetime import UTC, datetime

import pytest

from aquatlantis_ori.helpers import (
    convert_tenths_to_celsius,
    convert_tenths_to_celsius_list,
    datetime_str_to_datetime,
    ms_timestamp_to_datetime,
    random_id,
)


def test_random_id_default_length() -> None:
    """Test id generation default lenght."""
    result = random_id()
    assert isinstance(result, int)
    assert len(str(result)) == 10
    assert 10**9 <= result < 10**10


@pytest.mark.parametrize("length", [1, 5, 8, 15])
def test_random_id_custom_length(length: int) -> None:
    """Test id generation with given lenght."""
    result = random_id(length)
    assert isinstance(result, int)
    assert len(str(result)) == length
    assert 10 ** (length - 1) <= result < 10**length


def test_ms_timestamp_to_datetime() -> None:
    """Test ms_timestamp_to_datetime."""
    timestamp_ms = "1719400000000"
    expected = datetime(2024, 6, 26, 11, 6, 40, tzinfo=UTC)
    assert ms_timestamp_to_datetime(timestamp_ms) == expected


def test_datetime_str_to_datetime() -> None:
    """Test datetime_str_to_datetime."""
    date_str = "2023-01-01 12:00:00"
    expected = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    result = datetime_str_to_datetime(date_str)
    assert result == expected
    assert result.tzinfo == UTC


def test_convert_tenths_to_celsius() -> None:
    """Test convert_tenths_to_celsius."""
    assert convert_tenths_to_celsius(250) == 25.0
    assert convert_tenths_to_celsius(0) == 0.0
    assert convert_tenths_to_celsius(-100) == -10.0
    assert convert_tenths_to_celsius(1000) == 100.0
    assert convert_tenths_to_celsius(500) == 50.0


def test_convert_tenths_to_celsius_list() -> None:
    """Test convert_tenths_to_celsius_list."""
    assert convert_tenths_to_celsius_list([250, 0, -100, 1000, 500]) == [25.0, 0.0, -10.0, 100.0, 50.0]
    assert convert_tenths_to_celsius_list([]) == []
    assert convert_tenths_to_celsius_list([100]) == [10.0]
    assert convert_tenths_to_celsius_list([-100]) == [-10.0]
