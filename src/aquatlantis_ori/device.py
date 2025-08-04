"""Device."""

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Self

from aquatlantis_ori.helpers import (
    datetime_str_to_datetime,
    float_from_tenths,
    light_options_from_list,
    ms_timestamp_to_datetime,
    random_id,
    threshold_from_list,
    time_curves_from_list,
)
from aquatlantis_ori.http.models import LatestFirmwareResponseData, ListAllDevicesResponseDevice
from aquatlantis_ori.models import (
    DynamicModeType,
    LightOptions,
    LightType,
    ModeType,
    PowerType,
    SensorType,
    SensorValidType,
    StatusType,
    Threshold,
    TimeCurve,
)
from aquatlantis_ori.mqtt.client import AquatlantisOriMQTTClient
from aquatlantis_ori.mqtt.models import MethodType, MQTTRetrievePayloadParam, MQTTSendPayload, MQTTSendPayloadParam, PropsType, StatusPayload

logger = logging.getLogger(__name__)


class Device:
    """Aquatlantis Ori Device."""

    _mqtt_client: AquatlantisOriMQTTClient
    has_received_data: bool = False  # Indicates if the device has received

    # Variables from HTTP and MQTT response
    status: StatusType  # Device status

    # Variables from HTTP response
    id: str  # Unique identifier for the device
    brand: str  # Device brand, Aquatlantis
    name: str  # Device name
    pkey: str  # Device product key
    devid: str  # Device ID
    mac: str  # Device MAC address
    bluetooth_mac: str  # Device Bluetooth MAC address
    enable: bool  # Whether the device is enabled or not
    ip: str  # Device IP address
    port: int  # Device port
    online_time: datetime | None = None  # Time when the device was last online
    offline_time: datetime | None = None  # Time when the device was last offline
    offline_reason: str | None = None  # Reason for the device being offline, if applicable
    group_name: str | None = None  # Name of the group the device belongs to
    group_id: int | None = None  # Group ID the device belongs to
    creator: str  # Creator of the device, uuid
    create_time: datetime | None = None  # Time when the device was created
    update_time: datetime | None = None  # Time when the device was last updated
    app_notifications: bool  # Whether app notifications are enabled
    email_notifications: bool  # Whether email notifications are enabled
    notification_email: str | None = None  # Email address for notifications, if enabled

    # Variables from MQTT response
    timeoffset: int | None = None  # Time offset in seconds
    rssi: int | None = None  # Signal strength in dBm
    device_time: datetime | None = None  # Device time in UTC
    version: str | None = None  # Firmware version of the device
    ssid: str | None = None  # Wi-Fi SSID
    intensity: int | None = None  # Light intensity (0-100)
    custom1: LightOptions | None = None  # User defined preset 1
    custom2: LightOptions | None = None  # User defined preset 2
    custom3: LightOptions | None = None  # User defined preset 3
    custom4: LightOptions | None = None  # User defined preset 4
    timecurve: list[TimeCurve] | None = None  # The user defined automatic mode schedule for light intensity and colors
    preview: int | None = None  # This is the minute of the day in preview, -1 is off, range is 0-1439.
    light_type: LightType | None = None  # Type of light used by the device
    dynamic_mode: DynamicModeType | None = None  # Lightning effect
    mode: ModeType | None = None  # Current mode of the device
    power: PowerType | None = None  # Power state of the device
    sensor_type: SensorType | None = None  # Type of sensor used by the device
    water_temperature: float | None = None  # Water temperature in degrees Celsius
    sensor_valid: SensorValidType | None = None  # Valid has temperature sensor data
    water_temperature_thresholds: Threshold | None = None  # Water temperature thresholds
    air_temperature_thresholds: Threshold | None = None  # Air temperature thresholds
    air_humidity_thresholds: Threshold | None = None  # Air humidity thresholds
    red: int | None = None  # Red color channel (0-100)
    green: int | None = None  # Green color channel (0-100)
    blue: int | None = None  # Blue color channel (0-100)
    white: int | None = None  # White color channel (0-100)

    # Variables from http firmware reponse
    latest_firmware_version: str | None = None  # Latest firmware version available for the device
    firmware_name: str | None = None  # Name of the firmware file
    firmware_path: str | None = None  # Path to the firmware file

    def __init__(self: Self, mqtt_client: AquatlantisOriMQTTClient, data: ListAllDevicesResponseDevice) -> None:
        """Initialize the device."""
        self._mqtt_client = mqtt_client
        self.devid = data.devid  # Set this as soon as possible for debug logging purposes.
        self.update_http_data(data)

        self._mqtt_client.subscribe(f"$username/{self.brand}&{self.pkey}&{self.devid}/#")
        self.force_update()

    def update_http_data(self: Self, data: ListAllDevicesResponseDevice) -> None:
        """Update the device data from HTTP response."""
        field_map: dict[str, Callable[[Any], Any]] = {
            "id": lambda v: v,
            "brand": lambda v: v,
            "name": lambda v: v,
            "status": StatusType,
            "pkey": lambda v: v,
            "devid": lambda v: v,
            "mac": lambda v: v,
            "bluetooth_mac": lambda v: v,
            "enable": lambda v: v,
            "ip": lambda v: v,
            "port": lambda v: v,
            "online_time": ms_timestamp_to_datetime,
            "offline_time": ms_timestamp_to_datetime,
            "offline_reason": lambda v: v,
            "group_name": lambda v: v,
            "group_id": lambda v: v,
            "creator": lambda v: v,
            "create_time": datetime_str_to_datetime,
            "update_time": datetime_str_to_datetime,
            "app_notifications": lambda v: v,
            "email_notifications": lambda v: v,
            "notification_email": lambda v: v,
        }

        # Field rename map
        field_source_map = {
            "bluetooth_mac": "bluetoothMac",
            "offline_reason": "offlineReason",
            "group_name": "groupName",
            "group_id": "groupId",
            "online_time": "onlineTime",
            "offline_time": "offlineTime",
            "create_time": "createTime",
            "update_time": "updateTime",
            "app_notifications": "appNotiEnable",
            "email_notifications": "emailNotiEnable",
            "notification_email": "notiEmail",
        }

        # Build reverse map to default to field name if not specially mapped
        for field, transform in field_map.items():
            source_attr = field_source_map.get(field, field)
            value = getattr(data, source_attr, None)
            if value is not None:
                transformed_value = transform(value)
                logger.debug("%s setting %s to %s", self.devid, field, transformed_value)
                setattr(self, field, transformed_value)

    def update_mqtt_data(self: Self, data: MQTTRetrievePayloadParam) -> None:
        """Update the device state from MQTT data."""
        field_map: dict[str, Callable[[Any], Any]] = {
            "timeoffset": lambda v: v,
            "rssi": lambda v: v,
            "device_time": ms_timestamp_to_datetime,
            "version": lambda v: v,
            "ssid": lambda v: v,
            "intensity": lambda v: v,
            "ip": lambda v: v,
            "custom1": light_options_from_list,
            "custom2": light_options_from_list,
            "custom3": light_options_from_list,
            "custom4": light_options_from_list,
            "timecurve": time_curves_from_list,
            "preview": int,
            "light_type": LightType,
            "dynamic_mode": DynamicModeType,
            "mode": ModeType,
            "power": PowerType,
            "sensor_type": SensorType,
            "water_temperature": float_from_tenths,
            "sensor_valid": SensorValidType,
            "water_temperature_thresholds": threshold_from_list,
            "air_temperature_thresholds": threshold_from_list,
            "air_humidity_thresholds": threshold_from_list,
            "red": lambda v: v,
            "green": lambda v: v,
            "blue": lambda v: v,
            "white": lambda v: v,
        }

        # Field rename map
        field_source_map = {
            "water_temperature": "water_temp",
            "water_temperature_thresholds": "water_temp_thrd",
            "air_temperature_thresholds": "air_temp_thrd",
            "air_humidity_thresholds": "air_humi_thrd",
            "red": "ch1brt",
            "green": "ch2brt",
            "blue": "ch3brt",
            "white": "ch4brt",
        }

        # Build reverse map to default to field name if not specially mapped
        for field, transform in field_map.items():
            source_attr = field_source_map.get(field, field)
            value = getattr(data, source_attr, None)
            if value is not None:
                transformed_value = transform(value)
                logger.debug("%s setting %s to %s", self.devid, field, transformed_value)
                setattr(self, field, transformed_value)

        self.has_received_data = True

    def update_status(self: Self, data: StatusPayload) -> None:
        """Update the status of the device."""
        logger.debug("%s setting status to %s", self.devid, data.status)
        restored = self.status == StatusType.OFFLINE and data.status == StatusType.ONLINE
        self.status = StatusType(data.status)

        if restored:
            logger.info("%s restored came back online", self.devid)
            self.force_update()

    def update_firmware_data(self: Self, data: LatestFirmwareResponseData) -> None:
        """Update the device firmware data from HTTP response."""
        logger.debug("%s setting latest_firmware_version to %s", self.devid, data.firmwareVersion)
        self.latest_firmware_version = str(data.firmwareVersion)
        logger.debug("%s setting firmware_name to %s", self.devid, data.firmwareName)
        self.firmware_name = data.firmwareName
        logger.debug("%s setting firmware_path to %s", self.devid, data.firmwarePath)
        self.firmware_path = data.firmwarePath

    def force_update(self: Self) -> None:
        """Force an update of the device state."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/reqfrom/{self.creator}",
            MethodType.PROPERTY_GET,
            MQTTSendPayloadParam(props=list(PropsType)),
        )

    def _publish(self: Self, topic: str, method: MethodType, params: MQTTSendPayloadParam) -> None:
        """Publish the device state to MQTT."""
        payload = MQTTSendPayload(
            id=random_id(10),
            brand=self.brand,
            devid=self.devid,
            method=method,
            version="1",
            pkey=self.pkey,
            param=params,
        )

        if self._mqtt_client.is_connected():
            self._mqtt_client.publish(topic, payload)

    def get_current_timecurve(self: Self) -> TimeCurve | None:
        """Get the current active timecurve based on the current time."""
        if not self.timecurve:
            return None

        current_time = datetime.now(tz=UTC)
        current_hour = current_time.hour
        current_minute = current_time.minute

        # Sort timecurves by hour and minute
        sorted_timecurves = sorted(self.timecurve, key=lambda tc: (tc.hour, tc.minute))

        # Find the most recent timecurve that has passed
        active_timecurve = None
        for timecurve in sorted_timecurves:
            if timecurve.hour < current_hour or (timecurve.hour == current_hour and timecurve.minute <= current_minute):
                active_timecurve = timecurve
            else:
                break  # All remaining timecurves are in the future

        # If no timecurve has passed today, use the last one from yesterday
        if active_timecurve is None and sorted_timecurves:
            active_timecurve = sorted_timecurves[-1]

        return active_timecurve

    @property
    def is_light_on(self: Self) -> bool:
        """Check if the light is on."""
        if self.power == PowerType.ON:
            return True

        if self.mode == ModeType.AUTOMATIC and self.timecurve:
            current_timecurve = self.get_current_timecurve()
            if current_timecurve and current_timecurve.intensity > 0:
                return True

        return False

    def set_power(self: Self, power: PowerType) -> None:
        """Set the power state of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(power=power.value),
        )

    def set_mode(self: Self, mode: ModeType) -> None:
        """Set the power state of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(mode=mode.value),
        )

    def set_dynamic_mode(self: Self, dynamic_mode: DynamicModeType) -> None:
        """Set the dynamic mode of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(dynamic_mode=dynamic_mode.value),
        )

    def set_intensity(self: Self, intensity: int) -> None:
        """Set the light intensity of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(intensity=intensity),
        )

    def set_red(self: Self, red: int) -> None:
        """Set the red color intensity of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(ch1brt=red),
        )

    def set_green(self: Self, green: int) -> None:
        """Set the green color intensity of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(ch2brt=green),
        )

    def set_blue(self: Self, blue: int) -> None:
        """Set the blue color intensity of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(ch3brt=blue),
        )

    def set_white(self: Self, white: int) -> None:
        """Set the white color intensity of the device."""
        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(ch4brt=white),
        )

    def set_light(
        self: Self,
        power: PowerType | None = None,
        options: LightOptions | None = None,
    ) -> None:
        """Set the light properties of the device."""
        params: dict[str, Any] = {}

        if power is not None:
            params["power"] = power.value

        if options is not None:
            if options.intensity is not None:
                params["intensity"] = options.intensity
            if options.red is not None:
                params["ch1brt"] = options.red
            if options.green is not None:
                params["ch2brt"] = options.green
            if options.blue is not None:
                params["ch3brt"] = options.blue
            if options.white is not None:
                params["ch4brt"] = options.white

        self._publish(
            f"$username/{self.brand}&{self.pkey}&{self.devid}/property/set",
            MethodType.PROPERTY_SET,
            MQTTSendPayloadParam(**params),
        )
