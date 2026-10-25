"""Constants."""

from datetime import timedelta
from typing import Final

# SECURITY: The reverse-engineered vendor API is reached by bare IP over plaintext
# HTTP (see http/const.py) and unencrypted MQTT (port 10883). There is no TLS and no
# server-identity verification, so credentials, the bearer token, and device traffic
# are exposed to network observers. This is a known limitation imposed by the vendor
# service; switch to a TLS endpoint here if one becomes available.
SERVER: Final[str] = "8.209.119.184"
# A device counts as unavailable once no MQTT activity was received within this window. Not every
# device publishes telemetry unprompted (e.g. a lamp-only Ori on firmware 13 only answers a
# property.get), so the client sends a keepalive request every MQTT_KEEPALIVE_INTERVAL to keep
# fresh responses arriving within the window.
MQTT_AVAILABILITY_FRESHNESS_WINDOW: Final[timedelta] = timedelta(minutes=6)
# Well within the freshness window, so a single lost request or response doesn't flip availability.
MQTT_KEEPALIVE_INTERVAL: Final[timedelta] = timedelta(minutes=2)
