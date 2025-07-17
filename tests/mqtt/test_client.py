"""MQTT Client tests."""
# pylint: disable=protected-access

from collections.abc import Generator
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
from _pytest.logging import LogCaptureFixture
from mashumaro.mixins.orjson import DataClassORJSONMixin
from paho.mqtt.client import MQTTMessage

from aquatlantis_ori.mqtt.client import AquatlantisOriMQTTClient
from aquatlantis_ori.mqtt.models import MQTTClientSettings


@dataclass
class DummyPayload(DataClassORJSONMixin):
    """Dummy payload for testing."""

    value: str


@pytest.fixture(name="client_settings")
def fixture_client_settings() -> MQTTClientSettings:
    """Fixture for MQTT client settings."""
    return MQTTClientSettings(client_id="cid", username="user", password="pass")  # noqa: S106


@pytest.fixture(name="mock_mqtt_client")
def fixture_mock_mqtt_client() -> Generator[MagicMock]:
    """Fixture for mocking the MQTT client."""
    with patch("paho.mqtt.client.Client", autospec=True) as mock:
        yield mock.return_value


@pytest.fixture(name="mqtt_client")
def fixture_mqtt_client(
    client_settings: MQTTClientSettings,
    mock_mqtt_client: MagicMock,  # noqa: ARG001, pylint: disable=unused-argument
) -> AquatlantisOriMQTTClient:
    """Fixture for the Aquatlantis Ori MQTT client using the mock client."""
    return AquatlantisOriMQTTClient(client_settings)


def test_init_sets_attributes(client_settings: MQTTClientSettings, mock_mqtt_client: MagicMock) -> None:
    """Test that the AquatlantisOriMQTTClient initializes correctly."""
    client = AquatlantisOriMQTTClient(client_settings)
    assert client._client_settings is client_settings
    assert client._client is mock_mqtt_client
    assert client._on_client_connect is None
    assert client._on_client_message is None
    mock_mqtt_client.reconnect_delay_set.assert_called_once()
    mock_mqtt_client.username_pw_set.assert_called_once_with(username="user", password="pass")  # noqa: S106


def test_is_connected(mqtt_client: AquatlantisOriMQTTClient, mock_mqtt_client: MagicMock) -> None:
    """Test the is_connected method of the MQTT client."""
    mock_mqtt_client.is_connected.return_value = True
    assert mqtt_client.is_connected() is True
    mock_mqtt_client.is_connected.return_value = False
    assert mqtt_client.is_connected() is False


def test_connect_calls_methods(mqtt_client: AquatlantisOriMQTTClient, mock_mqtt_client: MagicMock) -> None:
    """Test that connect method calls the expected methods."""
    mqtt_client.connect()
    mock_mqtt_client.connect.assert_called_once()
    mock_mqtt_client.loop_start.assert_called_once()


def test_disconnect_calls_methods(mqtt_client: AquatlantisOriMQTTClient, mock_mqtt_client: MagicMock) -> None:
    """Test that disconnect method calls the expected methods."""
    mqtt_client.disconnect()
    mock_mqtt_client.loop_stop.assert_called_once()
    mock_mqtt_client.disconnect.assert_called_once()


def test_subscribe_calls_methods(mqtt_client: AquatlantisOriMQTTClient, mock_mqtt_client: MagicMock) -> None:
    """Test that subscribe method calls the expected methods."""
    mqtt_client.subscribe("topic")
    mock_mqtt_client.subscribe.assert_called_once()


def test_publish_calls_publish(mqtt_client: AquatlantisOriMQTTClient, mock_mqtt_client: MagicMock) -> None:
    """Test that publish method calls the MQTT client's publish method."""
    payload = DummyPayload(value="dummy-json")
    mqtt_client.publish("topic", payload, qos=1)
    mock_mqtt_client.publish.assert_called_once_with("topic", '{"value":"dummy-json"}', qos=1)


@pytest.mark.usefixtures("mock_mqtt_client")
def test_on_connect_success(client_settings: MQTTClientSettings) -> None:
    """Test that on_connect method calls the callback on successful connect."""
    called = []

    def on_connect_cb() -> None:
        called.append(True)

    client = AquatlantisOriMQTTClient(client_settings, on_connect=on_connect_cb)
    # Simulate successful connect
    client._on_connect(client._client, {}, MagicMock(), 0, None)
    assert called


@pytest.mark.usefixtures("mock_mqtt_client")
def test_on_connect_failure(client_settings: MQTTClientSettings) -> None:
    """Test that on_connect method does not call the callback on failure."""
    called = []

    def on_connect_cb() -> None:
        called.append(True)

    client = AquatlantisOriMQTTClient(client_settings, on_connect=on_connect_cb)
    # Simulate failed connect
    client._on_connect(client._client, {}, MagicMock(), 1, None)
    assert not called


def test_on_disconnect_expected(mqtt_client: AquatlantisOriMQTTClient, mock_mqtt_client: MagicMock, caplog: LogCaptureFixture) -> None:
    """Test that on_disconnect method logs expected messages."""
    with caplog.at_level("INFO"):
        mqtt_client._on_disconnect(mock_mqtt_client, {}, 0, None)
    assert "Disconnected gracefully" in caplog.text


def test_on_disconnect_unexpected(mqtt_client: AquatlantisOriMQTTClient, mock_mqtt_client: MagicMock, caplog: LogCaptureFixture) -> None:
    """Test that on_disconnect method logs unexpected disconnections."""
    with caplog.at_level("WARNING"):
        mqtt_client._on_disconnect(mock_mqtt_client, {}, 1, None)
    assert "Unexpected disconnection" in caplog.text


def test_on_message_with_callback(client_settings: MQTTClientSettings, mock_mqtt_client: MagicMock) -> None:
    """Test that on_message method calls the callback with the message."""
    called = []

    def on_msg(msg: MQTTMessage) -> None:
        called.append(msg)

    client = AquatlantisOriMQTTClient(client_settings, on_message=on_msg)
    msg = MagicMock()
    msg.topic = "topic1"
    client._on_message(mock_mqtt_client, {}, msg)
    assert called[0] is msg


def test_on_message_without_callback(client_settings: MQTTClientSettings, mock_mqtt_client: MagicMock) -> None:
    """Test that on_message method does not raise when no callback is set."""
    client = AquatlantisOriMQTTClient(client_settings)
    msg = MagicMock()
    msg.topic = "topic1"
    # Should not raise
    client._on_message(mock_mqtt_client, {}, msg)
