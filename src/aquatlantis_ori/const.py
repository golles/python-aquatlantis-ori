"""Constants."""

from datetime import timedelta
from typing import Final

SERVER: Final[str] = "8.209.119.184"
MQTT_AVAILABILITY_FRESHNESS_WINDOW: Final[timedelta] = timedelta(minutes=6)
