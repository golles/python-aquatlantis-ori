"""HTTP client."""

from __future__ import annotations

import asyncio
import logging
import socket
from json import JSONDecodeError
from types import TracebackType
from typing import Self

from aiohttp.client import ClientError, ClientResponse, ClientResponseError, ClientSession
from mashumaro.mixins.orjson import DataClassORJSONMixin
from yarl import URL

from aquatlantis_ori.const import SERVER
from aquatlantis_ori.http.const import PORT, PROTOCOL, HttpMethod
from aquatlantis_ori.http.exceptions import (
    AquatlantisOriConnectionError,
    AquatlantisOriDeserializeError,
    AquatlantisOriLoginError,
    AquatlantisOriTimeoutError,
)
from aquatlantis_ori.http.models import (
    DeviceInfoResponse,
    LatestFirmwareResponse,
    ListAllDevicesResponse,
    UserLoginPostData,
    UserLoginResponse,
    UserLogoutResponse,
)

logger = logging.getLogger(__name__)


class AquatlantisOriHTTPClient:
    """Aquatlantis Ori HTTP client."""

    request_timeout: int = 10
    _session: ClientSession
    _close_session: bool
    _token: str | None

    def __init__(self: Self, session: ClientSession | None = None) -> None:
        """Initialize the Aquatlantis Ori HTTP client."""
        if session is None:
            self._session = ClientSession()
            self._close_session = True
        else:
            self._session = session
            self._close_session = False

    async def login(self, credentials: UserLoginPostData) -> UserLoginResponse:
        """Login to the Aquatlantis Ori service."""
        response = await self._request(
            method=HttpMethod.POST,
            url=URL(f"{PROTOCOL}://{SERVER}:{PORT}/api/user/login?grant_type=app&brand=Aquatlantis"),
            data=credentials,
        )

        user_login_response = await self._deserialize(response, UserLoginResponse)
        if not user_login_response.is_success() or not user_login_response.data:
            msg = "Aquatlantis Ori login failed"
            raise AquatlantisOriLoginError(msg)

        self._token = user_login_response.data.token

        return user_login_response

    async def logout(self) -> UserLogoutResponse:
        """Logout from the Aquatlantis Ori service."""
        response = await self._request(
            method=HttpMethod.POST,
            url=URL(f"{PROTOCOL}://{SERVER}:{PORT}/api/user/logout"),
            headers={
                "Authorization": f"Bearer {self._token}",
            },
        )
        return await self._deserialize(response, UserLogoutResponse)

    async def list_all_devices(self: Self) -> ListAllDevicesResponse:
        """List devices connected to the Aquatlantis Ori service."""
        response = await self._request(
            method=HttpMethod.GET,
            url=URL(f"{PROTOCOL}://{SERVER}:{PORT}/api/device/list_all"),
            headers={
                "Authorization": f"Bearer {self._token}",
            },
        )
        return await self._deserialize(response, ListAllDevicesResponse)

    async def device_info(self: Self, device_id: str) -> DeviceInfoResponse:
        """Get information about a specific device connected to the Aquatlantis Ori service."""
        response = await self._request(
            method=HttpMethod.GET,
            url=URL(f"{PROTOCOL}://{SERVER}:{PORT}/api/device/info/{device_id}"),
            headers={
                "Authorization": f"Bearer {self._token}",
            },
        )
        return await self._deserialize(response, DeviceInfoResponse)

    async def lastest_firmware(self: Self, brand: str, pkey: str) -> LatestFirmwareResponse:
        """Get the latest firmware version for a given Aquatlantis Ori controller."""
        response = await self._request(
            method=HttpMethod.GET,
            url=URL(f"{PROTOCOL}://{SERVER}:{PORT}/api/firmware/latest?brand={brand}&pkey={pkey}"),
            headers={
                "Authorization": f"Bearer {self._token}",
            },
        )
        return await self._deserialize(response, LatestFirmwareResponse)

    async def _request(
        self: Self, method: HttpMethod, url: URL, headers: dict | None = None, data: DataClassORJSONMixin | None = None
    ) -> ClientResponse:
        """Make a request to the Aquatlantis Ori service."""
        headers = {
            "User-Agent": "Aquatlantis/89 CFNetwork/3826.500.131 Darwin/24.5.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(headers or {}),
        }

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    headers=headers,
                    json=data.to_dict() if data else None,
                )

                logger.info("%s request for url: %s responded with status %s", method, url, response.status)

                response.raise_for_status()

                return response
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the API"
            raise AquatlantisOriTimeoutError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with the API"
            raise AquatlantisOriConnectionError(msg) from exception

    async def _deserialize[T: DataClassORJSONMixin](self: Self, response: ClientResponse, model: type[T]) -> T:
        """Deserialize JSON response to a data class."""
        try:
            text = await response.text()
            return model.from_json(text)
        except JSONDecodeError as exception:
            msg = "Failed to deserialize response"
            raise AquatlantisOriDeserializeError(msg) from exception

    async def close(self: Self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self: Self) -> Self:
        """Async enter."""
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async exit."""
        await self.close()
