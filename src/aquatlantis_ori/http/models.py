"""HTTP models."""
# pylint: disable=invalid-name, too-many-instance-attributes

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class AquatlantisOriReponse(DataClassORJSONMixin):
    """Base response model."""

    code: int
    showMsg: bool
    message: str
    allDataCount: int

    def is_success(self) -> bool:
        """Check if the response is successful."""
        return self.code == 0


@dataclass
class DeviceInfoResponse(AquatlantisOriReponse):
    """Device info response model."""

    data: ListAllDevicesResponseDevice


@dataclass
class LatestFirmwareResponse(AquatlantisOriReponse):
    """Latest firmware response model."""

    data: LatestFirmwareResponseData | None


@dataclass
class LatestFirmwareResponseData(DataClassORJSONMixin):
    """Latest firmware response data model."""

    id: str
    brand: str
    pkey: str
    subid: str | None
    firmwareVersion: int
    firmwareName: str
    firmwarePath: str


@dataclass
class ListAllDevicesResponse(AquatlantisOriReponse):
    """List all devices response model."""

    data: ListAllDevicesResponseData | None


@dataclass
class ListAllDevicesResponseData(DataClassORJSONMixin):
    """List all devices response data model."""

    devices: list[ListAllDevicesResponseDevice]
    filters: list
    sharedDevices: list


@dataclass
class ListAllDevicesResponseDevice(DataClassORJSONMixin):
    """List all devices response device model."""

    id: str
    brand: str
    name: str
    status: int
    picture: str | None
    pkey: str
    pid: int
    subid: int
    devid: str
    mac: str
    bluetoothMac: str
    extend: str | None
    param: str | None
    version: str | None
    enable: bool
    clientid: str
    username: str
    ip: str
    port: int
    onlineTime: str
    offlineTime: str
    offlineReason: str | None
    userid: str | None
    icon: str | None
    groupName: str | None
    groupId: int | None
    creator: str
    createTime: str | None
    updateTime: str | None
    appNotiEnable: bool
    emailNotiEnable: bool
    notiEmail: str | None
    isShow: bool | None
    bindDevices: list[Any]


@dataclass
class UserLoginPostData(DataClassORJSONMixin):
    """User login data model."""

    credentials: str
    principal: str


@dataclass
class UserLoginResponse(AquatlantisOriReponse):
    """User login response model."""

    data: UserLoginResponseData | None


@dataclass
class UserLoginResponseData(DataClassORJSONMixin):
    """User login response data model."""

    brand: str
    token: str
    userId: str
    avatar: str
    email: str
    nickname: str
    mqttClientid: str
    mqttUsername: str
    mqttPassword: str
    topic: str


@dataclass
class UserLogoutResponse(AquatlantisOriReponse):
    """User logout response model."""

    data: None
