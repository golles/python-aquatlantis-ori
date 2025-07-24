"""Client."""

import asyncio
import logging
from types import TracebackType
from typing import Self

import paho.mqtt.client as mqtt
from aiohttp import ClientSession

from aquatlantis_ori.device import Device
from aquatlantis_ori.exceptions import AquatlantisOriError
from aquatlantis_ori.http.client import AquatlantisOriHTTPClient
from aquatlantis_ori.http.models import UserLoginPostData, UserLoginResponseData
from aquatlantis_ori.mqtt.client import AquatlantisOriMQTTClient
from aquatlantis_ori.mqtt.models import MQTTClientSettings, MQTTRetrievePayloadParam, RetrievePayload, StatusPayload

logger = logging.getLogger(__name__)


class AquatlantisOriClient:
    """Aquatlantis Ori Client."""

    _username: str
    _password: str
    _http_client: AquatlantisOriHTTPClient
    _mqtt_client: AquatlantisOriMQTTClient | None
    _devices: list[Device]

    def __init__(self, username: str, password: str, session: ClientSession | None = None) -> None:
        """Initialize the client."""
        self._username = username
        self._password = password
        self._http_client = AquatlantisOriHTTPClient(session=session)
        self._mqtt_client: AquatlantisOriMQTTClient | None = None
        self._devices = []

    async def connect(self: Self) -> None:
        """Connect to the Aquatlantis Ori service."""
        login_data = await self._login()
        if not login_data:
            msg = "Failed to log in to Aquatlantis Ori service"
            raise AquatlantisOriError(msg)

        logger.info("Logged in as %s (%s)", login_data.nickname, login_data.email)

        self._mqtt_client = AquatlantisOriMQTTClient(
            client_settings=MQTTClientSettings(
                client_id=login_data.mqttClientid,
                username=login_data.mqttUsername,
                password=login_data.mqttPassword,
            ),
            on_connect=self._on_mqtt_connected,
            on_message=self._on_mqtt_message,
        )

        self._mqtt_client.connect()

        await self._init_devices(self._mqtt_client)
        await self.check_firmware_updates()

    async def _login(self: Self) -> UserLoginResponseData | None:
        """Login to the Aquatlantis Ori service."""
        login_data = await self._http_client.login(UserLoginPostData(self._password, f"password@{self._username}"))
        if login_data.data:
            logger.info("Aquatlantis Ori login successful")
            return login_data.data

        logger.error("Aquatlantis Ori login failed")
        return None

    async def _init_devices(self: Self, mqtt_client: AquatlantisOriMQTTClient) -> None:
        """Initialize devices."""
        list_all_devices = await self._http_client.list_all_devices()
        all_devices = list_all_devices.data.devices if list_all_devices.data else []
        logger.info("Found %s Aquatlantis Ori devices", len(all_devices))
        device_list: list[Device] = [Device(mqtt_client, device) for device in all_devices]
        self._devices = device_list

    async def check_firmware_updates(self: Self) -> None:
        """Check for firmware updates for all devices."""
        for device in self._devices:
            firmware_info = await self._http_client.lastest_firmware(device.brand, device.pkey)
            if firmware_info.data:
                device.update_firmware_data(firmware_info.data)

    async def update_devices(self: Self) -> None:
        """Update devices with the latest information."""
        for device in self._devices:
            device_info = await self._http_client.device_info(device.devid)
            if device_info.data:
                device.update_http_data(device_info.data)
                device.force_update()

    def get_devices(self: Self) -> list[Device]:
        """Get the list of devices."""
        return self._devices

    def get_device(self: Self, devid: str) -> Device | None:
        """Get a device by its device id."""
        device = next((d for d in self._devices if d.devid == devid), None)
        if not device:
            return None

        return device

    async def wait_for_data(self: Self, interval: float = 0.2, max_wait: float = 5.0) -> None:
        """Wait for all devices to have data within a specified time frame.

        This function will check every `interval` seconds until all devices have data or until `max_wait` seconds have passed.

        Args:
            interval (float): The interval in seconds to check for data.
            max_wait (float): The maximum time in seconds to wait for all devices to have data.

        Raises:
            TimeoutError: If the maximum wait time is exceeded.
        """

        async def _check() -> None:
            while True:
                devices = self.get_devices()
                if all(device.has_received_data for device in devices):
                    return
                await asyncio.sleep(interval)

        await asyncio.wait_for(_check(), timeout=max_wait)

    def _update_device_state(self: Self, devid: str, data: MQTTRetrievePayloadParam) -> None:
        """Update the state of a device."""
        logger.info("Updating state for device %s", devid)

        device = self.get_device(devid)
        if not device:
            logger.warning("Device %s not found, cannot update state", devid)
            return

        logger.debug("Updated values for %s: %s", devid, data.to_dict())
        device.update_mqtt_data(data)

    def _update_device_status(self: Self, devid: str, data: StatusPayload) -> None:
        """Update the status of a device."""
        logger.info("Updating status for device %s", devid)

        device = self.get_device(devid)
        if not device:
            logger.warning("Device %s not found, cannot update state", devid)
            return

        logger.debug("Updated values for %s: %s", devid, data.to_dict())
        device.update_status(data)

    def _on_mqtt_connected(self: Self) -> None:
        logger.info("Connected to MQTT broker")

    def _on_mqtt_message(self, message: mqtt.MQTTMessage) -> None:
        """Callback for when a message is received from the MQTT broker."""
        logger.info("Received message on topic %s", message.topic)

        if (
            message.topic.endswith("/property/sensor/post")
            or message.topic.endswith("/property/post")
            or message.topic.endswith("/ota/version")
            or "/respto/" in message.topic
        ):
            # The above topics are used for device state updates and share the same payload structure
            payload = RetrievePayload.from_json(message.payload.decode("utf-8"))
            self._update_device_state(payload.devid, payload.param)
        elif message.topic.endswith("/status"):
            status_payload = StatusPayload.from_json(message.payload.decode("utf-8"))
            self._update_device_status(status_payload.devid, status_payload)
        elif not ("/reqfrom/" in message.topic or "/ntp/" in message.topic or message.topic.endswith("/property/set")):
            # Log unsupported topics
            logger.debug("Received message on unsupported topic: %s with payload: %s", message.topic, message.payload.decode("utf-8"))

    async def close(self: Self) -> None:
        """Close client."""
        await self._http_client.close()

        if self._mqtt_client and self._mqtt_client.is_connected():
            self._mqtt_client.disconnect()

    async def __aenter__(self: Self) -> Self:
        """Async enter."""
        return self

    async def __aexit__(self: Self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """Async exit."""
        await self.close()
