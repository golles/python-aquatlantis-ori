"""MQTT models."""
# pylint: disable=too-many-instance-attributes, disable=duplicate-code

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class MQTTClientSettings:
    """MQQT client settings."""

    client_id: str
    username: str
    password: str


class MethodType(StrEnum):
    """Supported method types."""

    PROPERTY_GET = "property.get"
    PROPERTY_POST = "property.post"
    PROPERTY_SET = "property.set"
    OTA_VERSION = "ota.version"
    OTA_CHECK = "ota.check"


class PropsType(StrEnum):
    """Supported property types."""

    AIR_HUMI = "air_humi"
    AIR_HUMI_THRD = "air_humi_thrd"
    AIR_TEMP = "air_temp"
    AIR_TEMP_THRD = "air_temp_thrd"
    CH1_BRT = "ch1brt"
    CH2_BRT = "ch2brt"
    CH3_BRT = "ch3brt"
    CH4_BRT = "ch4brt"
    CUSTOM1 = "custom1"
    CUSTOM2 = "custom2"
    CUSTOM3 = "custom3"
    CUSTOM4 = "custom4"
    DEVICE_TIME = "device_time"
    DYNAMIC_MODE = "dynamic_mode"
    INTENSITY = "intensity"
    IP = "ip"
    LIGHT_TYPE = "light_type"
    MODE = "mode"
    POWER = "power"
    PREVIEW = "preview"
    RSSI = "rssi"
    SENSOR_TYPE = "sensor_type"
    SENSOR_VALID = "sensor_valid"
    SSID = "ssid"
    TIMECURVE = "timecurve"
    TIMEOFFSET = "timeoffset"
    VERSION = "version"
    WATER_TEMP = "water_temp"
    WATER_TEMP_THRD = "water_temp_thrd"


@dataclass
class MQTTPayload(DataClassORJSONMixin):
    """Aquatlantis Ori MQTT Payload."""

    id: int
    brand: str
    devid: str
    method: MethodType
    version: str
    pkey: str


@dataclass
class MQTTSendPayload(MQTTPayload):
    """Aquatlantis Ori MQTT Payload for sending."""

    param: MQTTSendPayloadParam


@dataclass
class MQTTSendPayloadParam(DataClassORJSONMixin):
    """Aquatlantis Ori MQTT Payload Parameter for sending."""

    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        """Configuration for Device."""

        omit_none = True

    props: list[PropsType] | None = None
    mode: int | None = None
    power: int | None = None
    intensity: int | None = None
    dynamic_mode: int | None = None
    ch1brt: int | None = None
    ch2brt: int | None = None
    ch3brt: int | None = None
    ch4brt: int | None = None


@dataclass
class RetrievePayload(MQTTPayload):
    """Aquatlantis Ori MQTT Payload for retrieving."""

    param: MQTTRetrievePayloadParam


@dataclass
class MQTTRetrievePayloadParam(DataClassORJSONMixin):
    """Aquatlantis Ori MQTT Payload Parameter for retrieving."""

    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        """Configuration for Device."""

        omit_none = True

    timeoffset: int | None = None
    rssi: int | None = None
    device_time: str | None = None
    version: str | None = None
    ssid: str | None = None
    ip: str | None = None
    intensity: int | None = None
    custom1: list[int] | None = None
    custom2: list[int] | None = None
    custom3: list[int] | None = None
    custom4: list[int] | None = None
    timecurve: list[int] | None = None
    preview: int | None = None
    light_type: int | None = None
    dynamic_mode: int | None = None
    mode: int | None = None
    power: int | None = None
    sensor_type: int | None = None
    water_temp: int | None = None
    sensor_valid: int | None = None
    water_temp_thrd: list[int] | None = None
    air_temp_thrd: list[int] | None = None
    air_humi_thrd: list[int] | None = None
    ch1brt: int | None = None
    ch2brt: int | None = None
    ch3brt: int | None = None
    ch4brt: int | None = None


@dataclass
class StatusPayload(DataClassORJSONMixin):
    """Aquatlantis Ori MQTT Status Payload."""

    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        """Configuration for Device."""

        omit_none = True

    username: str
    timestamp: int
    status: int
    port: int
    pkey: str
    ip: str
    devid: str
    clientid: str
    brand: str
    app: int
    reason: str | None = None
