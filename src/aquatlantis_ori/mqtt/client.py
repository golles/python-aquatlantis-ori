"""MQTT client."""

import logging
from collections.abc import Callable
from typing import Any, Self

import paho.mqtt.client as mqtt
from mashumaro.mixins.orjson import DataClassORJSONMixin

from aquatlantis_ori.const import SERVER
from aquatlantis_ori.mqtt.const import PORT
from aquatlantis_ori.mqtt.models import MQTTClientSettings

logger = logging.getLogger(__name__)


class AquatlantisOriMQTTClient:
    """Aquatlantis Ori MQTT Client."""

    _client: mqtt.Client
    _client_settings: MQTTClientSettings
    _on_client_connect: Callable[[], None] | None
    _on_client_message: Callable[[mqtt.MQTTMessage], None] | None

    def __init__(
        self: Self,
        client_settings: MQTTClientSettings,
        on_connect: Callable[[], None] | None = None,
        on_message: Callable[[mqtt.MQTTMessage], None] | None = None,
    ) -> None:
        """Initialize the MQTT client."""
        self._client = mqtt.Client(client_id=client_settings.client_id, protocol=mqtt.MQTTProtocolVersion.MQTTv5)
        self._client_settings = client_settings
        self._on_client_connect = on_connect
        self._on_client_message = on_message

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.reconnect_delay_set(min_delay=1, max_delay=120)
        self._client.username_pw_set(username=client_settings.username, password=client_settings.password)

    def is_connected(self: Self) -> bool:
        """Check if the client is connected to the MQTT broker."""
        return self._client.is_connected()

    def connect(self: Self) -> None:
        """Connect to the MQTT broker."""
        logger.info("Connecting to MQTT broker at %s:%s", SERVER, PORT)
        self._client.connect(SERVER, PORT, keepalive=60)
        self._client.loop_start()

    def disconnect(self: Self) -> None:
        """Gracefully disconnect from the MQTT broker."""
        logger.info("Disconnecting from MQTT broker...")
        self._client.loop_stop()
        self._client.disconnect()

    def subscribe(self: Self, topic: str) -> None:
        """Subscribe to a specific topic."""
        logger.info("Subscribing to topic %s", topic)
        self._client.subscribe(topic)

    def publish(self: Self, topic: str, payload: DataClassORJSONMixin, qos: int = 0) -> None:
        """Publish a message to the specified topic."""
        logger.info("Publishing message to topic %s", topic)
        payload_string = payload.to_json()
        self._client.publish(topic, payload_string, qos=qos)

    def _on_connect(
        self: Self,
        _client: mqtt.Client,
        _userdata: dict[str, Any],
        _flags: mqtt.ConnectFlags,
        rc: mqtt.ReasonCode | int,
        _properties: mqtt.Properties | None,
    ) -> None:
        """Callback for when the MQTT client connects to the broker."""
        if rc == 0:
            logger.info("Connected successfully to MQTT broker.")

            if self._on_client_connect is not None:
                self._on_client_connect()
        else:
            logger.warning("Failed to connect, return code %s", rc)

    def _on_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: dict[str, Any],
        rc: mqtt.ReasonCode | int | None,
        _properties: mqtt.Properties | None,
    ) -> None:
        """Callback for when the client disconnects."""
        if rc != 0:
            logger.warning("Unexpected disconnection. Will attempt to reconnect. RC=%s", rc)
        else:
            logger.info("Disconnected gracefully from MQTT broker.")

    def _on_message(self, _client: mqtt.Client, _userdata: dict[str, Any], message: mqtt.MQTTMessage) -> None:
        """Callback for when the MQTT client receives a message."""
        logger.info("Message on topic %s", message.topic)
        if self._on_client_message is not None:
            self._on_client_message(message)
