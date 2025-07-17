"""HTTP Client tests."""
# pylint: disable=protected-access

from collections.abc import Generator
from json import JSONDecodeError
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp.client import ClientError, ClientResponse, ClientResponseError, ClientSession
from aiohttp.client_reqrep import RequestInfo
from yarl import URL

from aquatlantis_ori.http.client import AquatlantisOriHTTPClient
from aquatlantis_ori.http.const import HttpMethod
from aquatlantis_ori.http.exceptions import (
    AquatlantisOriConnectionError,
    AquatlantisOriDeserializeError,
    AquatlantisOriLoginError,
    AquatlantisOriTimeoutError,
)
from aquatlantis_ori.http.models import (
    DeviceInfoResponse,
    LatestFirmwareResponse,
    LatestFirmwareResponseData,
    ListAllDevicesResponse,
    ListAllDevicesResponseData,
    ListAllDevicesResponseDevice,
    UserLoginPostData,
    UserLoginResponse,
    UserLoginResponseData,
    UserLogoutResponse,
)


@pytest.fixture(name="mock_session")
def fixture_mock_session() -> Generator[ClientSession]:
    """Fixture for mock session."""
    with patch("aiohttp.client.ClientSession", autospec=True) as mock:
        yield mock.return_value


async def test_client_initialization() -> None:
    """Test client initialization."""
    client = AquatlantisOriHTTPClient()
    assert isinstance(client._session, ClientSession)
    assert client._close_session is True


async def test_login_success(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test successful login."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    credentials = UserLoginPostData(credentials="pass", principal="user")
    token = "testtoken"  # noqa: S105
    user_data = UserLoginResponseData(
        brand="Aquatlantis", token=token, userId="1", avatar="", email="", nickname="", mqttClientid="", mqttUsername="", mqttPassword="", topic=""
    )
    login_response = UserLoginResponse(code=0, showMsg=True, message="ok", allDataCount=1, data=user_data)
    mock_response = MagicMock(spec=ClientResponse)
    monkeypatch.setattr(client, "_request", AsyncMock(return_value=mock_response))
    monkeypatch.setattr(client, "_deserialize", AsyncMock(return_value=login_response))
    result = await client.login(credentials)
    assert result.data
    assert result.data.token == token
    assert client._token == token


async def test_login_failure(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test login failure."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    credentials = UserLoginPostData(credentials="pass", principal="user")
    login_response = UserLoginResponse(code=1, showMsg=True, message="fail", allDataCount=0, data=None)
    mock_response = MagicMock(spec=ClientResponse)
    monkeypatch.setattr(client, "_request", AsyncMock(return_value=mock_response))
    monkeypatch.setattr(client, "_deserialize", AsyncMock(return_value=login_response))
    with pytest.raises(AquatlantisOriLoginError):
        await client.login(credentials)


async def test_logout(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test logout."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    client._token = "token"  # noqa: S105
    logout_response = UserLogoutResponse(code=0, showMsg=True, message="ok", allDataCount=1, data=None)
    mock_response = MagicMock(spec=ClientResponse)
    monkeypatch.setattr(client, "_request", AsyncMock(return_value=mock_response))
    monkeypatch.setattr(client, "_deserialize", AsyncMock(return_value=logout_response))
    result = await client.logout()
    assert isinstance(result, UserLogoutResponse)


async def test_list_all_devices(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test listing all devices."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    client._token = "token"  # noqa: S105,
    device = ListAllDevicesResponseDevice(
        id="1",
        brand="Aquatlantis",
        name="dev",
        status=1,
        picture=None,
        pkey="p",
        pid=1,
        subid=1,
        devid="d",
        mac="m",
        bluetoothMac="b",
        extend=None,
        param=None,
        version=None,
        enable=True,
        clientid="c",
        username="u",
        ip="i",
        port=1,
        onlineTime="",
        offlineTime="",
        offlineReason=None,
        userid=None,
        icon=None,
        groupName=None,
        groupId=None,
        creator="cr",
        createTime=None,
        updateTime=None,
        appNotiEnable=True,
        emailNotiEnable=True,
        notiEmail=None,
        isShow=None,
        bindDevices=[],
    )
    data = ListAllDevicesResponseData(devices=[device], filters=[], sharedDevices=[])
    response = ListAllDevicesResponse(code=0, showMsg=True, message="ok", allDataCount=1, data=data)
    mock_response = MagicMock(spec=ClientResponse)
    monkeypatch.setattr(client, "_request", AsyncMock(return_value=mock_response))
    monkeypatch.setattr(client, "_deserialize", AsyncMock(return_value=response))
    result = await client.list_all_devices()
    assert isinstance(result, ListAllDevicesResponse)
    assert result.data
    assert result.data.devices[0].id == "1"


async def test_device_info(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test device info retrieval."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    client._token = "token"  # noqa: S105
    device = ListAllDevicesResponseDevice(
        id="1",
        brand="Aquatlantis",
        name="dev",
        status=1,
        picture=None,
        pkey="p",
        pid=1,
        subid=1,
        devid="d",
        mac="m",
        bluetoothMac="b",
        extend=None,
        param=None,
        version=None,
        enable=True,
        clientid="c",
        username="u",
        ip="i",
        port=1,
        onlineTime="",
        offlineTime="",
        offlineReason=None,
        userid=None,
        icon=None,
        groupName=None,
        groupId=None,
        creator="cr",
        createTime=None,
        updateTime=None,
        appNotiEnable=True,
        emailNotiEnable=True,
        notiEmail=None,
        isShow=None,
        bindDevices=[],
    )
    response = DeviceInfoResponse(code=0, showMsg=True, message="ok", allDataCount=1, data=device)
    mock_response = MagicMock(spec=ClientResponse)
    monkeypatch.setattr(client, "_request", AsyncMock(return_value=mock_response))
    monkeypatch.setattr(client, "_deserialize", AsyncMock(return_value=response))
    result = await client.device_info("1")
    assert isinstance(result, DeviceInfoResponse)
    assert result.data.id == "1"


async def test_lastest_firmware(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test latest firmware retrieval."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    client._token = "token"  # noqa: S105
    fw_data = LatestFirmwareResponseData(
        id="fw", brand="Aquatlantis", pkey="p", subid=None, firmwareVersion=1, firmwareName="fw", firmwarePath="path"
    )
    response = LatestFirmwareResponse(code=0, showMsg=True, message="ok", allDataCount=1, data=fw_data)
    mock_response = MagicMock(spec=ClientResponse)
    monkeypatch.setattr(client, "_request", AsyncMock(return_value=mock_response))
    monkeypatch.setattr(client, "_deserialize", AsyncMock(return_value=response))
    result = await client.lastest_firmware("Aquatlantis", "p")
    assert isinstance(result, LatestFirmwareResponse)
    assert result.data
    assert result.data.id == "fw"


async def test_request_timeout(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test request timeout handling."""
    client = AquatlantisOriHTTPClient(session=mock_session)

    async def raise_timeout(*_args: int, **_kwargs: int) -> None:
        raise TimeoutError

    monkeypatch.setattr(client._session, "request", raise_timeout)
    with pytest.raises(AquatlantisOriTimeoutError):
        await client._request(HttpMethod.GET, URL("http://test"))


async def test_request_connection_error(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test request connection error handling."""
    client = AquatlantisOriHTTPClient(session=mock_session)

    async def raise_conn(*_args: int, **_kwargs: int) -> None:
        raise ClientError

    monkeypatch.setattr(client._session, "request", raise_conn)
    with pytest.raises(AquatlantisOriConnectionError):
        await client._request(HttpMethod.GET, URL("http://test"))


async def test_request_raises_for_status(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test _request handles non-2xx status via raise_for_status."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    mock_response = MagicMock(spec=ClientResponse)
    mock_request_info = MagicMock(spec=RequestInfo)
    mock_response.raise_for_status.side_effect = ClientResponseError(request_info=mock_request_info, history=())

    async def fake_request(*_args: int, **_kwargs: int) -> MagicMock:
        return mock_response

    monkeypatch.setattr(client._session, "request", fake_request)
    with pytest.raises(AquatlantisOriConnectionError):
        await client._request(HttpMethod.GET, URL("http://test"))


async def test_request_success(monkeypatch: pytest.MonkeyPatch, mock_session: ClientSession) -> None:
    """Test _request returns response on success (covers return statement)."""
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.raise_for_status.return_value = None

    async def fake_request(*_args: int, **_kwargs: int) -> MagicMock:
        return mock_response

    client = AquatlantisOriHTTPClient(session=mock_session)
    monkeypatch.setattr(client._session, "request", fake_request)
    response = await client._request(HttpMethod.GET, URL("http://test"))
    assert response is mock_response


async def test_close_closes_session() -> None:
    """Test close closes the session if needed."""
    mock_session = MagicMock(spec=ClientSession)
    client = AquatlantisOriHTTPClient(session=mock_session)
    client._close_session = True
    await client.close()
    mock_session.close.assert_awaited()


async def test_close_does_not_close_if_flag_false() -> None:
    """Test close does not close session if _close_session is False."""
    mock_session = MagicMock(spec=ClientSession)
    client = AquatlantisOriHTTPClient(session=mock_session)
    client._close_session = False
    await client.close()
    mock_session.close.assert_not_awaited()


async def test_async_context_manager() -> None:
    """Test async context manager methods __aenter__ and __aexit__."""
    mock_session = MagicMock(spec=ClientSession)
    client = AquatlantisOriHTTPClient(session=mock_session)
    client._close_session = True
    async with client as c:
        assert c is client
    mock_session.close.assert_awaited()


async def test_deserialize_json_error(mock_session: ClientSession) -> None:
    """Test deserialization error handling."""
    client = AquatlantisOriHTTPClient(session=mock_session)
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.text = AsyncMock(return_value="bad json")
    with (
        patch("aquatlantis_ori.http.models.UserLoginResponse.from_json", side_effect=JSONDecodeError("msg", "bad json", 0)),
        pytest.raises(AquatlantisOriDeserializeError),
    ):
        await client._deserialize(mock_response, UserLoginResponse)
