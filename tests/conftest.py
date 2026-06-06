"""Shared test fixtures."""

from uuid import UUID

import pytest

from aquatlantis_ori.http.models import ListAllDevicesResponseDevice
from aquatlantis_ori.models import StatusType
from aquatlantis_ori.mqtt.models import MQTTRetrievePayloadParam, StatusPayload


@pytest.fixture(name="sample_http_data")
def fixture_sample_http_data() -> ListAllDevicesResponseDevice:
    """Create sample HTTP device data."""
    return ListAllDevicesResponseDevice(
        id=UUID("5202cb6e-8d4f-406d-ad39-f49f82760b39"),
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
        groupId=UUID("222d614d-36d8-443a-988f-868ecf80e078"),
        creator=UUID("01e63611-fa7c-48fb-9c9a-332fae881057"),
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


@pytest.fixture(name="sample_offline_status_payload")
def fixture_sample_offline_status_payload() -> StatusPayload:
    """Create a sample OFFLINE status payload."""
    return StatusPayload(
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


@pytest.fixture(name="sample_online_status_payload")
def fixture_sample_online_status_payload() -> StatusPayload:
    """Create a sample ONLINE status payload."""
    return StatusPayload(
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
