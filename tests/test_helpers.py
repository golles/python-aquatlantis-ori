"""Helpers tests."""

from datetime import UTC, datetime

import pytest

from aquatlantis_ori.helpers import (
    datetime_str_to_datetime,
    float_from_tenths,
    light_options_from_list,
    ms_timestamp_to_datetime,
    random_id,
    threshold_from_list,
    time_curves_from_list,
)
from aquatlantis_ori.models import LightOptions, Threshold, TimeCurve


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


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (250, 25.0),
        (0, 0.0),
        (-100, -10.0),
        (1000, 100.0),
        (500, 50.0),
    ],
)
def test_float_from_tenths(value: int, expected: float) -> None:
    """Test float_from_tenths."""
    assert float_from_tenths(value) == expected


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([200, 300], Threshold(min_value=20.0, max_value=30.0)),
        ([0, 1000], Threshold(min_value=0.0, max_value=100.0)),
        ([150, 450], Threshold(min_value=15.0, max_value=45.0)),
        ([100, 200], Threshold(min_value=10.0, max_value=20.0)),
    ],
)
def test_threshold_from_list(values: list[int], expected: Threshold) -> None:
    """Test threshold_from_list."""
    assert threshold_from_list(values) == expected


@pytest.mark.parametrize(
    ("values"),
    [
        ([]),
        ([1]),
        ([1, 2, 3]),
        ([1, 2, 3, 4]),
        ([1, 2, 3, 4, 5]),
    ],
)
def test_threshold_from_list_invalid_length(values: list[int]) -> None:
    """Test threshold_from_list with invalid data length."""
    with pytest.raises(ValueError, match="Threshold data must contain exactly 2 elements: \\[min_value, max_value\\]"):
        threshold_from_list(values)


def test_make_time_curves_empty() -> None:
    """Test _make_time_curves with empty data."""
    result = time_curves_from_list([])
    assert result == []


def test_make_time_curves_invalid_length() -> None:
    """Test _make_time_curves with invalid data length."""
    with pytest.raises(ValueError, match="Timecurve data length is not a multiple of 7"):
        time_curves_from_list([2, 1, 2, 3, 4, 5])


def test_make_time_curves_valid() -> None:
    """Test _make_time_curves with valid data."""
    data = [1, 12, 30, 75, 100, 80, 60, 40]
    result = time_curves_from_list(data)

    assert len(result) == 1
    assert isinstance(result[0], TimeCurve)
    assert result[0].hour == 12
    assert result[0].minute == 30
    assert result[0].intensity == 75
    assert result[0].red == 100
    assert result[0].green == 80
    assert result[0].blue == 60
    assert result[0].white == 40


def test_light_options_from_list() -> None:
    """Test light_options_from_list with valid data."""
    data = [75, 255, 128, 64, 200]
    result = light_options_from_list(data)

    assert isinstance(result, LightOptions)
    assert result.intensity == 75
    assert result.red == 255
    assert result.green == 128
    assert result.blue == 64
    assert result.white == 200


@pytest.mark.parametrize(
    ("value"),
    [
        ([]),
        ([1]),
        ([1, 2]),
        ([1, 2, 3, 4]),
        ([1, 2, 3, 4, 5, 6]),
        ([1, 2, 3, 4, 5, 6, 7]),
    ],
)
def test_light_options_from_list_invalid_lengths(value: list[int]) -> None:
    """Test light_options_from_list with invalid data length."""
    with pytest.raises(ValueError, match="Light options data must contain exactly 5 elements: \\[intensity, red, green, blue, white\\]"):
        light_options_from_list(value)
