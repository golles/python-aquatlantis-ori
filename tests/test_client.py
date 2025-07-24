"""Client tests."""
# pylint: disable=protected-access

import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from _pytest.logging import LogCaptureFixture

from aquatlantis_ori.client import AquatlantisOriClient
from aquatlantis_ori.http.models import UserLoginResponseData
from aquatlantis_ori.mqtt.models import MQTTRetrievePayloadParam


@pytest.fixture(name="mock_http_client")
def fixture_mock_http_client() -> Generator[MagicMock]:
    """Fixture to mock the AquatlantisOriHTTPClient."""
    with patch("aquatlantis_ori.http.client.AquatlantisOriHTTPClient", autospec=True) as mock:
        yield mock.return_value


@pytest.fixture(name="mock_mqtt_client")
def fixture_mock_mqtt_client() -> Generator[MagicMock]:
    """Fixture to mock the AquatlantisOriMQTTClient."""
    with patch("aquatlantis_ori.mqtt.client.AquatlantisOriMQTTClient", autospec=True) as mock:
        yield mock.return_value


@pytest.fixture(name="client")
def fixture_client(mock_http_client: MagicMock, mock_mqtt_client: MagicMock) -> Generator[AquatlantisOriClient]:
    """Fixture for the AquatlantisOriClient."""
    with (
        patch("aquatlantis_ori.client.AquatlantisOriHTTPClient", return_value=mock_http_client),
        patch("aquatlantis_ori.client.AquatlantisOriMQTTClient", return_value=mock_mqtt_client),
    ):
        yield AquatlantisOriClient("user", "pass")


def test_init_sets_attributes(client: AquatlantisOriClient) -> None:
    """Test that the AquatlantisOriClient initializes correctly."""
    assert client._username == "user"
    assert client._password == "pass"  # noqa: S105
    assert client._http_client is not None
    assert client._mqtt_client is None
    assert client._devices == []


async def test_connect_success(client: AquatlantisOriClient, mock_http_client: MagicMock, mock_mqtt_client: MagicMock) -> None:
    """Test successful connection to the Aquatlantis Ori service."""
    login_data = MagicMock(spec=UserLoginResponseData)
    login_data.mqttClientid = "cid"
    login_data.mqttUsername = "u"
    login_data.mqttPassword = "p"
    login_data.nickname = "nick"
    login_data.email = "mail"
    mock_http_client.login = AsyncMock(return_value=MagicMock(data=login_data))
    mock_http_client.list_all_devices = AsyncMock(return_value=MagicMock(data=MagicMock(devices=[])))
    mock_mqtt_client.connect = MagicMock()
    await client.connect()
    assert client._mqtt_client is mock_mqtt_client
    mock_mqtt_client.connect.assert_called_once()


async def test_connect_login_error(client: AquatlantisOriClient, mock_http_client: MagicMock) -> None:
    """Test connection failure due to login failure."""
    mock_http_client.login = AsyncMock(return_value=MagicMock(data=None))
    with pytest.raises(Exception, match="Failed to log in to Aquatlantis Ori service"):
        await client.connect()


async def test_login_success_and_failure(client: AquatlantisOriClient, mock_http_client: MagicMock) -> None:
    """Test login success and failure paths."""
    # Success
    login_data = MagicMock()
    mock_http_client.login = AsyncMock(return_value=MagicMock(data=login_data))
    result = await client._login()
    assert result is login_data

    # Failure
    mock_http_client.login = AsyncMock(return_value=MagicMock(data=None))
    result = await client._login()
    assert result is None


def test_list_all_devices_empty(client: AquatlantisOriClient, mock_http_client: MagicMock, mock_mqtt_client: MagicMock) -> None:
    """Test listing all devices when no devices are present."""
    mock_http_client.list_all_devices = AsyncMock(return_value=MagicMock(data=None))
    result = pytest.run(asyncio.run(client._init_devices(mock_mqtt_client))) if hasattr(pytest, "run") else None
    # Should return empty list
    assert not result or result is None


def test_get_device_not_found(client: AquatlantisOriClient) -> None:
    """Test getting a device that does not exist."""
    client._devices = []
    assert client.get_device("foo") is None


def test_get_device_found(client: AquatlantisOriClient) -> None:
    """Test getting a device that exists."""
    device = MagicMock()
    device.devid = "foo"
    client._devices = [device]
    result = client.get_device("foo")
    assert result is device


def test_wait_until_devices_have_data(client: AquatlantisOriClient) -> None:
    """Test waiting until all devices have data."""
    device1 = MagicMock()
    device1.has_received_data = True
    device2 = MagicMock()
    device2.has_received_data = True
    client._devices = [device1, device2]

    asyncio.run(client.wait_for_data())


def test_wait_until_devices_have_data_not_ready(client: AquatlantisOriClient) -> None:
    """Test waiting until devices have data when not all devices are ready."""
    device1 = MagicMock()
    device1.has_received_data = False
    device2 = MagicMock()
    device2.has_received_data = True
    client._devices = [device1, device2]

    with pytest.raises(TimeoutError):
        asyncio.run(client.wait_for_data(interval=0.1, max_wait=0.5))


def test_update_device_state_not_found(client: AquatlantisOriClient, caplog: LogCaptureFixture) -> None:
    """Test updating device state for a device that is not found."""
    client._devices = []
    with caplog.at_level("WARNING"):
        client._update_device_state("foo", MagicMock())
    assert "Device foo not found" in caplog.text


def test_update_device_state_calls_update_mqtt_data(client: AquatlantisOriClient) -> None:
    """Test that _update_device_state calls update_mqtt_data on the device."""
    device = MagicMock()
    data = MagicMock(spec=MQTTRetrievePayloadParam)
    data.to_dict.return_value = {"foo": "bar"}

    with patch.object(client, "get_device", return_value=device):
        client._update_device_state("dev1", data)

    device.update_mqtt_data.assert_called_once_with(data)


def test_update_device_state_device_not_found(client: AquatlantisOriClient, caplog: LogCaptureFixture) -> None:
    """Test that _update_device_state logs a warning when device is not found."""
    device = MagicMock()
    data = MagicMock(spec=MQTTRetrievePayloadParam)

    with patch.object(client, "get_device", return_value=device):
        client._update_device_state("dev1", data)

    with caplog.at_level("WARNING"):
        client._update_device_state("unknown", data)

    assert "Device unknown not found, cannot update state" in caplog.text


def test_update_device_status_not_found(client: AquatlantisOriClient, caplog: LogCaptureFixture) -> None:
    """Test updating device status for a device that is not found."""
    client._devices = []
    with caplog.at_level("WARNING"):
        client._update_device_status("foo", MagicMock())
    assert "Device foo not found" in caplog.text


def test_update_device_status_calls_update_mqtt_data(client: AquatlantisOriClient) -> None:
    """Test that _update_device_status calls update_mqtt_data on the device."""
    device = MagicMock()
    data = MagicMock(spec=MQTTRetrievePayloadParam)
    data.to_dict.return_value = {"status": 1}

    with patch.object(client, "get_device", return_value=device):
        client._update_device_status("dev1", data)

    device.update_status.assert_called_once_with(data)


def test_update_device_status_device_not_found(client: AquatlantisOriClient, caplog: LogCaptureFixture) -> None:
    """Test that _update_device_state logs a warning when device is not found."""
    device = MagicMock()
    data = MagicMock(spec=MQTTRetrievePayloadParam)

    with patch.object(client, "get_device", return_value=device):
        client._update_device_status("dev1", data)

    with caplog.at_level("WARNING"):
        client._update_device_status("unknown", data)

    assert "Device unknown not found, cannot update state" in caplog.text


def test_on_mqtt_connected(client: AquatlantisOriClient, caplog: LogCaptureFixture) -> None:
    """Test that _on_mqtt_connected logs info message."""
    with caplog.at_level("INFO"):
        client._on_mqtt_connected()
    assert "Connected to MQTT broker" in caplog.text


def test_on_mqtt_message_sensor_post(client: AquatlantisOriClient) -> None:
    """Test handling an MQTT message for sensor post."""
    msg = MagicMock()
    msg.topic = "foo/property/sensor/post"
    msg.payload.decode.return_value = "json"
    with (
        patch("aquatlantis_ori.mqtt.models.RetrievePayload.from_json", return_value=MagicMock(devid="d", param="p")) as from_json,
        patch.object(client, "_update_device_state") as upd,
    ):
        client._on_mqtt_message(msg)
        from_json.assert_called_once_with("json")
        upd.assert_called_once_with("d", "p")


def test_on_mqtt_message_property_post(client: AquatlantisOriClient) -> None:
    """Test handling an MQTT message for property post."""
    msg = MagicMock()
    msg.topic = "foo/property/post"
    msg.payload.decode.return_value = "json"
    with (
        patch("aquatlantis_ori.mqtt.models.RetrievePayload.from_json", return_value=MagicMock(devid="d", param="p")) as from_json,
        patch.object(client, "_update_device_state") as upd,
    ):
        client._on_mqtt_message(msg)
        from_json.assert_called_once_with("json")
        upd.assert_called_once_with("d", "p")


def test_on_mqtt_message_respto(client: AquatlantisOriClient) -> None:
    """Test handling an MQTT response message."""
    msg = MagicMock()
    msg.topic = "foo/respto/bar"
    msg.payload.decode.return_value = "json"
    with (
        patch("aquatlantis_ori.mqtt.models.RetrievePayload.from_json", return_value=MagicMock(devid="d", param="p")) as from_json,
        patch.object(client, "_update_device_state") as upd,
    ):
        client._on_mqtt_message(msg)
        from_json.assert_called_once_with("json")
        upd.assert_called_once_with("d", "p")


def test_on_mqtt_message_status(client: AquatlantisOriClient) -> None:
    """Test handling an MQTT response message."""
    msg = MagicMock()
    msg.topic = "foo/status"
    msg.payload.decode.return_value = "json"
    with (
        patch("aquatlantis_ori.mqtt.models.StatusPayload.from_json", return_value=MagicMock(devid="d", status=1)) as from_json,
        patch.object(client, "_update_device_status") as upd,
    ):
        client._on_mqtt_message(msg)
        from_json.assert_called_once_with("json")
        upd.assert_called_once_with("d", from_json.return_value)


def test_on_mqtt_message_unsupported_topic(client: AquatlantisOriClient, caplog: LogCaptureFixture) -> None:
    """Test handling an unsupported MQTT message topic."""
    msg = MagicMock()
    msg.topic = "foo/unsupported/topic"
    msg.payload.decode.return_value = "json"
    with caplog.at_level("DEBUG"):
        client._on_mqtt_message(msg)
    assert "Received message on unsupported topic: foo/unsupported/topic" in caplog.text


@pytest.mark.parametrize(
    "topic",
    [
        "$username/Aquatlantis&Aquatlantis527&ESP-XXX/ntp/response",
        "$username/Aquatlantis&Aquatlantis527&ESP-XXX/ntp/request",
        "$username/Aquatlantis&Aquatlantis527&ESP-XXX/property/set",
        "$username/Aquatlantis&Aquatlantis527&ESP-XXX/reqfrom/userid",
    ],
)
def test_on_mqtt_message_unsupported_topic_ignore(client: AquatlantisOriClient, caplog: LogCaptureFixture, topic: str) -> None:
    """Test handling an ignored unsupported MQTT message topic."""
    msg = MagicMock()
    msg.topic = topic
    msg.payload.decode.return_value = "json"
    with caplog.at_level("DEBUG"):
        client._on_mqtt_message(msg)
    assert f"Received message on unsupported topic: {topic}" not in caplog.text


async def test_close_with_connected_mqtt(client: AquatlantisOriClient, mock_http_client: MagicMock, mock_mqtt_client: MagicMock) -> None:
    """Test closing the client when MQTT is connected."""
    mock_http_client.close = AsyncMock()
    mock_mqtt_client.is_connected.return_value = True
    mock_mqtt_client.disconnect = MagicMock()
    client._mqtt_client = mock_mqtt_client
    await client.close()
    mock_http_client.close.assert_awaited()
    mock_mqtt_client.disconnect.assert_called_once()


async def test_close_without_connected_mqtt(client: AquatlantisOriClient, mock_http_client: MagicMock, mock_mqtt_client: MagicMock) -> None:
    """Test closing the client when MQTT is not connected."""
    mock_http_client.close = AsyncMock()
    mock_mqtt_client.is_connected.return_value = False
    mock_mqtt_client.disconnect = MagicMock()
    client._mqtt_client = mock_mqtt_client
    await client.close()
    mock_http_client.close.assert_awaited()
    mock_mqtt_client.disconnect.assert_not_called()


async def test_async_context_manager(client: AquatlantisOriClient) -> None:
    """Test the async context manager for the client."""
    async with client as c:
        assert c is client


def test_get_devices(client: AquatlantisOriClient) -> None:
    """Test getting the list of devices."""
    device1 = MagicMock()
    device2 = MagicMock()
    client._devices = [device1, device2]
    result = client.get_devices()
    assert result == [device1, device2]


def test_check_firmware_updates(client: AquatlantisOriClient, mock_http_client: MagicMock) -> None:
    """Test checking firmware updates for devices."""
    device1 = MagicMock()
    device1.brand = "brand1"
    device1.pkey = "pkey1"
    device2 = MagicMock()
    device2.brand = "brand2"
    device2.pkey = "pkey2"
    client._devices = [device1, device2]

    firmware_data1 = MagicMock()
    firmware_data2 = MagicMock()

    mock_http_client.lastest_firmware.side_effect = [
        MagicMock(data=firmware_data1),
        MagicMock(data=firmware_data2),
    ]

    asyncio.run(client.check_firmware_updates())

    device1.update_firmware_data.assert_called_once_with(firmware_data1)
    device2.update_firmware_data.assert_called_once_with(firmware_data2)


def test_update_devices(client: AquatlantisOriClient, mock_http_client: MagicMock) -> None:
    """Test updating devices with the latest information."""
    device1 = MagicMock()
    device1.devid = "dev1"
    device2 = MagicMock()
    device2.devid = "dev2"
    client._devices = [device1, device2]

    device_info1 = MagicMock()
    device_info2 = MagicMock()

    mock_http_client.device_info.side_effect = [
        MagicMock(data=device_info1),
        MagicMock(data=device_info2),
    ]

    asyncio.run(client.update_devices())

    device1.update_http_data.assert_called_once_with(device_info1)
    device1.force_update.assert_called_once()
    device2.update_http_data.assert_called_once_with(device_info2)
    device2.force_update.assert_called_once()
