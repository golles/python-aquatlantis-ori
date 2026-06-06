"""Constants."""

from datetime import timedelta
from typing import Final

SERVER: Final[str] = "8.209.119.184"
# Device telemetry arrives roughly every 5 minutes; 6 minutes adds a 1-minute buffer for jitter.
MQTT_AVAILABILITY_FRESHNESS_WINDOW: Final[timedelta] = timedelta(minutes=6)
