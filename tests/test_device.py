"""Device tests."""
# pylint: disable=protected-access

from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from aquatlantis_ori.device import Device
from aquatlantis_ori.http.models import LatestFirmwareResponseData, ListAllDevicesResponseDevice
from aquatlantis_ori.models import DynamicModeType, LightOptions, ModeType, PowerType, StatusType, Threshold, TimeCurve
from aquatlantis_ori.mqtt.client import AquatlantisOriMQTTClient
from aquatlantis_ori.mqtt.models import MethodType, MQTTRetrievePayloadParam, PropsType, StatusPayload


@pytest.fixture(name="mock_mqtt_client")
def fixture_mock_mqtt_client() -> MagicMock:
    """Create a mock MQTT client."""
    client = MagicMock(spec=AquatlantisOriMQTTClient)
    client.subscribe = MagicMock()
    client.publish = MagicMock()
    client.is_connected = MagicMock(return_value=True)
    return client


@pytest.fixture(name="sample_http_data")
def fixture_sample_http_data() -> ListAllDevicesResponseDevice:
    """Create sample HTTP device data."""
    return ListAllDevicesResponseDevice(
        id="device123",
        brand="Aquatlantis",
        name="Test Device",
        status=1,
        picture=None,
        pkey="testpkey",
        pid=0,
        subid=0,
        devid="testdevid",
        mac="00:11:22:33:44:55",
        bluetoothMac="00:11:22:33:44:66",
        extend=None,
        param=None,
        version=None,
        enable=True,
        clientid="client123",
        username="testuser",
        ip="192.168.1.100",
        port=8080,
        onlineTime="1719400000000",
        offlineTime="1719500000000",
        offlineReason=None,
        userid=None,
        icon=None,
        groupName="Test Group",
        groupId=1,
        creator="creator123",
        createTime="2023-01-01 12:00:00",
        updateTime="2023-01-02 12:00:00",
        appNotiEnable=False,
        emailNotiEnable=False,
        notiEmail=None,
        isShow=None,
        bindDevices=[],
    )


@pytest.fixture(name="sample_mqtt_data")
def fixture_sample_mqtt_data() -> MQTTRetrievePayloadParam:
    """Create sample MQTT device data."""
    return MQTTRetrievePayloadParam(
        timeoffset=3600,
        rssi=-45,
        device_time="1719400000000",
        version="1.0.0",
        ssid="TestWiFi",
        ip="192.168.1.100",
        intensity=80,
        custom1=[75, 255, 128, 64, 200],
        custom2=[50, 200, 100, 50, 150],
        custom3=None,
        custom4=None,
        timecurve=[2, 8, 0, 50, 10, 20, 30, 40, 18, 30, 80, 60, 70, 80, 90],
        preview=0,
        light_type=1,
        dynamic_mode=0,
        mode=1,
        power=1,
        sensor_type=1,
        water_temp=250,  # 25.0°C
        sensor_valid=1,
        water_temp_thrd=[200, 300],
        air_temp_thrd=[150, 250],
        air_humi_thrd=None,
        ch1brt=10,
        ch2brt=20,
        ch3brt=30,
        ch4brt=40,
    )


@pytest.fixture(name="mock_random_id")
def fixture_mock_random_id() -> Generator[MagicMock]:
    """Mock the random_id function."""
    with patch("aquatlantis_ori.device.random_id", return_value="randomid123") as mock:
        yield mock


def test_device_initialization(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test device initialization."""
    device = Device(mock_mqtt_client, sample_http_data)

    # Check HTTP data mapping
    assert device.id == "device123"
    assert device.brand == "Aquatlantis"
    assert device.name == "Test Device"
    assert device.status == 1
    assert device.pkey == "testpkey"
    assert device.devid == "testdevid"
    assert device.mac == "00:11:22:33:44:55"
    assert device.bluetooth_mac == "00:11:22:33:44:66"
    assert device.enable is True
    assert device.ip == "192.168.1.100"
    assert device.port == 8080
    assert device.group_name == "Test Group"
    assert device.group_id == 1
    assert device.creator == "creator123"

    # Check datetime conversions
    assert device.online_time is not None
    assert device.online_time.year == 2024
    assert device.offline_time is not None
    assert device.offline_time.year == 2024
    assert device.create_time is not None
    assert device.create_time.year == 2023
    assert device.update_time is not None
    assert device.update_time.year == 2023

    # Check MQTT subscription
    mock_mqtt_client.subscribe.assert_called_once_with("$username/Aquatlantis&testpkey&testdevid/#")

    # Check force update was called
    mock_mqtt_client.publish.assert_called_once()


def test_update_http_data(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test updating device with HTTP data."""
    device = Device(mock_mqtt_client, sample_http_data)

    # Update with new data
    new_data = ListAllDevicesResponseDevice(
        id="device456",
        brand="NewBrand",
        name="New Device",
        status=0,
        picture=None,
        pkey="newpkey",
        pid=0,
        subid=0,
        devid="newdevid",
        mac="11:22:33:44:55:66",
        bluetoothMac="11:22:33:44:55:77",
        extend=None,
        param=None,
        version=None,
        enable=False,
        clientid="newclient",
        username="newuser",
        ip="192.168.1.200",
        port=9090,
        onlineTime="1719600000000",
        offlineTime="1719700000000",
        offlineReason="Network error",
        userid=None,
        icon=None,
        groupName="New Group",
        groupId=2,
        creator="newcreator",
        createTime="2023-02-01 12:00:00",
        updateTime="2023-02-02 12:00:00",
        appNotiEnable=True,
        emailNotiEnable=True,
        notiEmail="test@example.com",
        isShow=True,
        bindDevices=[],
    )

    device.update_http_data(new_data)

    assert device.id == "device456"
    assert device.brand == "NewBrand"
    assert device.name == "New Device"
    assert device.status == StatusType.OFFLINE
    assert device.enable is False
    assert device.offline_reason == "Network error"
    assert device.group_name == "New Group"


def test_update_mqtt_data(
    mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice, sample_mqtt_data: MQTTRetrievePayloadParam
) -> None:
    """Test updating device with MQTT data."""
    device = Device(mock_mqtt_client, sample_http_data)
    device.update_mqtt_data(sample_mqtt_data)

    assert device.timeoffset == 3600
    assert device.rssi == -45
    assert device.version == "1.0.0"
    assert device.ssid == "TestWiFi"
    assert device.ip == "192.168.1.100"
    assert device.intensity == 80
    assert device.custom1 == LightOptions(intensity=75, red=255, green=128, blue=64, white=200)
    assert device.custom2 == LightOptions(intensity=50, red=200, green=100, blue=50, white=150)
    assert device.custom3 is None
    assert device.custom4 is None
    assert device.preview == 0
    assert device.light_type == 1
    assert device.dynamic_mode == DynamicModeType.OFF
    assert device.mode == ModeType.AUTOMATIC
    assert device.power == PowerType.ON
    assert device.sensor_type == 1
    assert device.water_temperature == 25.0  # Converted from 250
    assert device.water_temperature_thresholds == Threshold(20.0, 30.0)  # Converted from [200, 300]
    assert device.air_temperature_thresholds == Threshold(15.0, 25.0)  # Converted from [150, 250]
    assert device.sensor_valid == 1

    # Check datetime conversion
    assert device.device_time is not None
    assert device.device_time.year == 2024

    # Check timecurve parsing
    assert device.timecurve is not None
    assert len(device.timecurve) == 2
    if device.timecurve is not None:
        assert isinstance(device.timecurve[0], TimeCurve)
        assert device.timecurve[0].hour == 8
        assert device.timecurve[0].minute == 0
        assert device.timecurve[0].intensity == 50
        assert device.timecurve[1].hour == 18
        assert device.timecurve[1].minute == 30
        assert device.timecurve[1].intensity == 80


@pytest.mark.usefixtures("mock_random_id")
def test_force_update(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test force_update method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.force_update()

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/reqfrom/creator123"
    assert payload.id == "randomid123"
    assert payload.brand == "Aquatlantis"
    assert payload.devid == "testdevid"
    assert payload.method == MethodType.PROPERTY_GET
    assert payload.pkey == "testpkey"
    assert payload.param.props == list(PropsType)


def test_set_power(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_power method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_power(PowerType.ON)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.power == PowerType.ON.value


def test_set_mode(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_mode method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_mode(ModeType.MANUAL)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.mode == ModeType.MANUAL.value


def test_set_dynamic_mode(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_dynamic_mode method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_dynamic_mode(DynamicModeType.ON)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.dynamic_mode == DynamicModeType.ON.value


def test_set_intensity(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_intensity method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_intensity(75)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.intensity == 75


def test_set_red(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_red method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_red(10)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.ch1brt == 10


def test_set_green(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_green method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_green(50)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.ch2brt == 50


def test_set_blue(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_blue method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_blue(80)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.ch3brt == 80


def test_set_white(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_white method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_white(100)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.ch4brt == 100


def test_set_light(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_light method."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    options = LightOptions(intensity=100, red=50, green=75, blue=25, white=10)
    device.set_light(power=PowerType.ON, options=options)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.power == PowerType.ON.value
    assert payload.param.intensity == 100
    assert payload.param.ch1brt == 50
    assert payload.param.ch2brt == 75
    assert payload.param.ch3brt == 25
    assert payload.param.ch4brt == 10


def test_set_light_without_power(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_light method without power."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    options = LightOptions(intensity=100, red=50, green=75, blue=25, white=10)
    device.set_light(options=options)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.power is None
    assert payload.param.intensity == 100
    assert payload.param.ch1brt == 50
    assert payload.param.ch2brt == 75
    assert payload.param.ch3brt == 25
    assert payload.param.ch4brt == 10


def test_set_light_without_options(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test set_light method without options."""
    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_light(power=PowerType.ON)

    mock_mqtt_client.publish.assert_called_once()
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/property/set"
    assert payload.method == MethodType.PROPERTY_SET
    assert payload.param.power == PowerType.ON.value
    assert payload.param.intensity is None
    assert payload.param.ch1brt is None
    assert payload.param.ch2brt is None
    assert payload.param.ch3brt is None
    assert payload.param.ch4brt is None


def test_publish_when_disconnected(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test _publish method when MQTT client is disconnected."""
    mock_mqtt_client.is_connected.return_value = False

    device = Device(mock_mqtt_client, sample_http_data)
    mock_mqtt_client.reset_mock()

    device.set_power(PowerType.OFF)

    # Should not publish when disconnected
    mock_mqtt_client.publish.assert_not_called()


def test_update_mqtt_data_with_none_values(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test update_mqtt_data with None values."""
    device = Device(mock_mqtt_client, sample_http_data)

    mqtt_data = MQTTRetrievePayloadParam(
        timeoffset=None,
        rssi=None,
        device_time=None,
        version=None,
        ssid=None,
        ip=None,
        intensity=50,  # Only this one is not None
        custom1=None,
        custom2=None,
        custom3=None,
        custom4=None,
        timecurve=None,
        preview=None,
        light_type=None,
        dynamic_mode=None,
        mode=None,
        power=None,
        sensor_type=None,
        water_temp=None,
        sensor_valid=None,
        water_temp_thrd=None,
        air_temp_thrd=None,
        air_humi_thrd=None,
        ch1brt=None,
        ch2brt=None,
        ch3brt=None,
        ch4brt=None,
    )

    device.update_mqtt_data(mqtt_data)

    # Only intensity should be updated
    assert device.intensity == 50
    # Other values should remain None or unchanged
    assert device.timeoffset is None
    assert device.rssi is None
    assert device.version is None


def test_update_http_data_with_none_timestamps(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test update_http_data with None timestamp values."""
    sample_http_data.createTime = None
    sample_http_data.updateTime = None

    device = Device(mock_mqtt_client, sample_http_data)

    # Timestamp fields should remain None when source is None
    assert device.create_time is None
    assert device.update_time is None


def test_update_status(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test updating device status."""
    device = Device(mock_mqtt_client, sample_http_data)
    assert device.status == StatusType.ONLINE

    status_data = StatusPayload(
        username="testuser",
        timestamp=1752702401491,
        status=StatusType.OFFLINE,
        reason="keepalive_timeout",
        port=8080,
        pkey="testpkey",
        ip="192.168.1.100",
        devid="testdevid",
        clientid="client123",
        brand="Aquatlantis",
        app=0,
    )

    device.update_status(status_data)
    assert device.status == StatusType.OFFLINE


@pytest.mark.usefixtures("mock_random_id")
def test_update_status_restored(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test updating device status from offline to online, force update should be called."""
    device = Device(mock_mqtt_client, sample_http_data)
    device.status = StatusType.OFFLINE

    status_data = StatusPayload(
        username="testuser",
        timestamp=1752702401491,
        status=StatusType.ONLINE,
        reason=None,
        port=8080,
        pkey="testpkey",
        ip="192.168.1.100",
        devid="testdevid",
        clientid="client123",
        brand="Aquatlantis",
        app=0,
    )

    device.update_status(status_data)
    assert device.status == StatusType.ONLINE

    # verify that force_update was called
    assert mock_mqtt_client.publish.call_count == 2
    call_args = mock_mqtt_client.publish.call_args
    topic, payload = call_args[0]

    assert topic == "$username/Aquatlantis&testpkey&testdevid/reqfrom/creator123"
    assert payload.id == "randomid123"
    assert payload.brand == "Aquatlantis"
    assert payload.devid == "testdevid"
    assert payload.method == MethodType.PROPERTY_GET
    assert payload.pkey == "testpkey"
    assert payload.param.props == list(PropsType)


def test_update_firmware_data(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test updating firmware data."""
    device = Device(mock_mqtt_client, sample_http_data)

    firmware_data = LatestFirmwareResponseData(
        id="firmware123",
        brand="Aquatlantis",
        pkey="testpkey",
        subid=None,
        firmwareVersion=2,
        firmwareName="firmware_v2.bin",
        firmwarePath="http://example.com/firmware_v2.bin",
    )

    device.update_firmware_data(firmware_data)
    assert device.latest_firmware_version == "2"
    assert device.firmware_name == "firmware_v2.bin"
    assert device.firmware_path == "http://example.com/firmware_v2.bin"


def test_get_current_timecurve_no_timecurves(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test get_current_timecurve when no timecurves are set."""
    device = Device(mock_mqtt_client, sample_http_data)
    device.timecurve = None

    result = device.get_current_timecurve()
    assert result is None

    device.timecurve = []
    result = device.get_current_timecurve()
    assert result is None


@patch("aquatlantis_ori.device.datetime")
def test_get_current_timecurve_normal_case(
    mock_datetime: MagicMock, mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice
) -> None:
    """Test get_current_timecurve with normal operation."""
    # Mock current time to 14:30 (2:30 PM)
    mock_now = datetime(2023, 8, 4, 14, 30, 0, tzinfo=UTC)
    mock_datetime.now.return_value = mock_now

    device = Device(mock_mqtt_client, sample_http_data)

    device.timecurve = [
        TimeCurve(hour=7, minute=59, intensity=0, red=0, green=0, blue=0, white=0),
        TimeCurve(hour=8, minute=0, intensity=5, red=5, green=5, blue=5, white=5),
        TimeCurve(hour=10, minute=0, intensity=70, red=30, green=60, blue=80, white=60),
        TimeCurve(hour=12, minute=0, intensity=80, red=30, green=60, blue=80, white=70),
        TimeCurve(hour=16, minute=0, intensity=70, red=30, green=60, blue=80, white=60),
        TimeCurve(hour=18, minute=0, intensity=40, red=10, green=20, blue=30, white=20),
        TimeCurve(hour=20, minute=0, intensity=5, red=5, green=5, blue=10, white=5),
        TimeCurve(hour=21, minute=0, intensity=0, red=0, green=0, blue=0, white=0),
    ]

    # At 14:30, the active timecurve should be the 12:00 one
    result = device.get_current_timecurve()
    assert result is not None
    assert result.hour == 12
    assert result.minute == 0
    assert result.intensity == 80


@patch("aquatlantis_ori.device.datetime")
def test_get_current_timecurve_exact_time(
    mock_datetime: MagicMock, mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice
) -> None:
    """Test get_current_timecurve when current time exactly matches a timecurve."""
    # Mock current time to exactly 16:00
    mock_now = datetime(2023, 8, 4, 16, 0, 0, tzinfo=UTC)
    mock_datetime.now.return_value = mock_now

    device = Device(mock_mqtt_client, sample_http_data)
    device.timecurve = [
        TimeCurve(hour=8, minute=0, intensity=5, red=5, green=5, blue=5, white=5),
        TimeCurve(hour=16, minute=0, intensity=70, red=30, green=60, blue=80, white=60),
        TimeCurve(hour=20, minute=0, intensity=5, red=5, green=5, blue=10, white=5),
    ]

    # At exactly 16:00, should return the 16:00 timecurve
    result = device.get_current_timecurve()
    assert result is not None
    assert result.hour == 16
    assert result.minute == 0
    assert result.intensity == 70


@patch("aquatlantis_ori.device.datetime")
def test_get_current_timecurve_early_morning(
    mock_datetime: MagicMock, mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice
) -> None:
    """Test get_current_timecurve early in the morning before any timecurve."""
    # Mock current time to 06:00 (before any timecurve)
    mock_now = datetime(2023, 8, 4, 6, 0, 0, tzinfo=UTC)
    mock_datetime.now.return_value = mock_now

    device = Device(mock_mqtt_client, sample_http_data)
    device.timecurve = [
        TimeCurve(hour=8, minute=0, intensity=5, red=5, green=5, blue=5, white=5),
        TimeCurve(hour=16, minute=0, intensity=70, red=30, green=60, blue=80, white=60),
        TimeCurve(hour=21, minute=0, intensity=0, red=0, green=0, blue=0, white=0),
    ]

    # At 06:00, should return the last timecurve from "yesterday" (21:00)
    result = device.get_current_timecurve()
    assert result is not None
    assert result.hour == 21
    assert result.minute == 0
    assert result.intensity == 0


@patch("aquatlantis_ori.device.datetime")
def test_get_current_timecurve_unordered_list(
    mock_datetime: MagicMock, mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice
) -> None:
    """Test get_current_timecurve with unordered timecurves to ensure sorting works."""
    # Mock current time to 15:30
    mock_now = datetime(2023, 8, 4, 15, 30, 0, tzinfo=UTC)
    mock_datetime.now.return_value = mock_now

    device = Device(mock_mqtt_client, sample_http_data)

    # Deliberately unordered timecurves
    device.timecurve = [
        TimeCurve(hour=20, minute=0, intensity=5, red=5, green=5, blue=10, white=5),
        TimeCurve(hour=8, minute=0, intensity=5, red=5, green=5, blue=5, white=5),
        TimeCurve(hour=16, minute=0, intensity=70, red=30, green=60, blue=80, white=60),
        TimeCurve(hour=12, minute=0, intensity=80, red=30, green=60, blue=80, white=70),
    ]

    # At 15:30, should return the 12:00 timecurve (not the 16:00 one)
    result = device.get_current_timecurve()
    assert result is not None
    assert result.hour == 12
    assert result.minute == 0
    assert result.intensity == 80


def test_is_light_on_with_automatic_mode_and_timecurve(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test is_light_on property with automatic mode and timecurve."""
    device = Device(mock_mqtt_client, sample_http_data)
    device.power = PowerType.OFF
    device.mode = ModeType.AUTOMATIC
    device.timecurve = [TimeCurve(hour=12, minute=0, intensity=80, red=30, green=60, blue=80, white=70)]  # Need to set timecurve

    # Mock get_current_timecurve to return a timecurve with intensity > 0
    with patch.object(device, "get_current_timecurve") as mock_get_timecurve:
        mock_get_timecurve.return_value = TimeCurve(hour=12, minute=0, intensity=80, red=30, green=60, blue=80, white=70)
        assert device.is_light_on is True

        # Test with intensity = 0
        mock_get_timecurve.return_value = TimeCurve(hour=21, minute=0, intensity=0, red=0, green=0, blue=0, white=0)
        assert device.is_light_on is False

        # Test with no timecurve
        mock_get_timecurve.return_value = None
        assert device.is_light_on is False


def test_is_light_on_with_power_on(mock_mqtt_client: MagicMock, sample_http_data: ListAllDevicesResponseDevice) -> None:
    """Test is_light_on property when power is ON."""
    device = Device(mock_mqtt_client, sample_http_data)
    device.power = PowerType.ON

    # Should return True regardless of mode or timecurve
    assert device.is_light_on is True
