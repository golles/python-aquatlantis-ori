"""Constants."""

from datetime import timedelta
from typing import Final

# SECURITY: The reverse-engineered vendor API is reached by bare IP over plaintext
# HTTP (see http/const.py) and unencrypted MQTT (port 10883). There is no TLS and no
# server-identity verification, so credentials, the bearer token, and device traffic
# are exposed to network observers. This is a known limitation imposed by the vendor
# service; switch to a TLS endpoint here if one becomes available.
SERVER: Final[str] = "8.209.119.184"
# Device telemetry arrives roughly every 5 minutes; 6 minutes adds a 1-minute buffer for jitter.
MQTT_AVAILABILITY_FRESHNESS_WINDOW: Final[timedelta] = timedelta(minutes=6)
