"""Models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class StatusType(IntEnum):
    """Status types."""

    OFFLINE = 0
    ONLINE = 1


class DynamicModeType(IntEnum):
    """Dynamic mode types, also known as lightning effect."""

    OFF = 0
    ON = 1


class ModeType(IntEnum):
    """Light mode types."""

    MANUAL = 0
    AUTOMATIC = 1


class PowerType(IntEnum):
    """Power state types."""

    OFF = 0
    ON = 1


class SensorType(IntEnum):
    """Sensor types."""

    TEMPERATURE = 1
    TEMPERATURE_HUMIDITY = 2


class SensorValidType(IntEnum):
    """Sensor valid state types."""

    INVALID = 0
    VALID = 1


class LightType(IntEnum):
    """Light types."""

    RGBW_ULTRA = 0
    UV_ULTRA = 1
    EASY_LED = 2


@dataclass
class TimeCurve:
    """Time curve model."""

    hour: int
    minute: int
    intensity: int
    red: int
    green: int
    blue: int
    white: int


@dataclass
class LightOptions:
    """Light options model."""

    intensity: int | None = None
    red: int | None = None
    green: int | None = None
    blue: int | None = None
    white: int | None = None


@dataclass
class Threshold:
    """Threshold model."""

    min_value: float
    max_value: float
