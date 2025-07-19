"""Helpers."""

import random
from datetime import UTC, datetime

from .models import LightOptions, Threshold, TimeCurve


def random_id(length: int = 10) -> int:
    """Generate a random ID of specified length."""
    return random.randint(10 ** (length - 1), 10**length - 1)  # noqa: S311


def ms_timestamp_to_datetime(value: str) -> datetime:
    """Convert a timestamp in milliseconds to a datetime object."""
    return datetime.fromtimestamp(int(value) / 1000, tz=UTC)


def datetime_str_to_datetime(value: str) -> datetime:
    """Convert a datetime string to a datetime object."""
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").astimezone(UTC)


def float_from_tenths(value: int) -> float:
    """Convert an integer value representing tenths to a float."""
    return value / 10.0


def threshold_from_list(data: list[int]) -> Threshold:
    """Convert a list of threshold values to a Threshold object."""
    no_of_fields = 2
    if len(data) != no_of_fields:
        msg = f"Threshold data must contain exactly {no_of_fields} elements: [min_value, max_value]."
        raise ValueError(msg)

    return Threshold(
        min_value=float_from_tenths(data[0]),
        max_value=float_from_tenths(data[1]),
    )


def time_curves_from_list(data: list[int]) -> list[TimeCurve]:
    """Parse a flat list of timecurve data into a list of TimeCurve objects.

    The first element in the list indicates the number of curve entries and is ignored.
    Each subsequent 7 elements represent a single timecurve entry, in the following order:
        [hour, minute, intensity, ch1brt, ch2brt, ch3brt, ch4brt]

    Args:
        data (list): Raw timecurve data from the device.

    Returns:
        list[TimeCurve]: List of parsed TimeCurve instances.
    """
    if not data:
        return []

    # Skip the first item which is the length.
    entries = data[1:]

    if len(entries) % 7 != 0:
        msg = "Timecurve data length is not a multiple of 7 after skipping the count."
        raise ValueError(msg)

    return [TimeCurve(*entries[i : i + 7]) for i in range(0, len(entries), 7)]


def light_options_from_list(data: list[int]) -> LightOptions:
    """Parse a flat list of light options data into a LightOptions object."""
    no_of_fields = 5
    if len(data) != no_of_fields:
        msg = f"Light options data must contain exactly {no_of_fields} elements: [intensity, red, green, blue, white]."
        raise ValueError(msg)

    options = LightOptions()
    if data[0]:
        options.intensity = data[0]
    if data[1]:
        options.red = data[1]
    if data[2]:
        options.green = data[2]
    if data[3]:
        options.blue = data[3]
    if data[4]:
        options.white = data[4]
    return options
