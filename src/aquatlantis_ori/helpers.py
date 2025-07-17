"""Helpers."""

import random
from datetime import UTC, datetime


def random_id(length: int = 10) -> int:
    """Generate a random ID of specified length."""
    return random.randint(10 ** (length - 1), 10**length - 1)  # noqa: S311


def ms_timestamp_to_datetime(value: str) -> datetime:
    """Convert a timestamp in milliseconds to a datetime object."""
    return datetime.fromtimestamp(int(value) / 1000, tz=UTC)


def datetime_str_to_datetime(value: str) -> datetime:
    """Convert a datetime string to a datetime object."""
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").astimezone(UTC)


def convert_tenths_to_celsius(value: int) -> float:
    """Convert water temperature from tenths of degrees Celsius to degrees Celsius."""
    return value / 10.0


def convert_tenths_to_celsius_list(value: list[int]) -> list[float]:
    """Convert a list of water temperatures from tenths of degrees Celsius to degrees Celsius."""
    return [convert_tenths_to_celsius(v) for v in value]
