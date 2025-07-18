# HTTP API

The HTTP API is used for initial authentication, device discovery, and firmware information. It provides a RESTful interface to interact with the data from the Ori controller.

## General Notes

- Communication is done over HTTP, and there doesn't appear to be a DNS name for the web server.
- JSON is used as the data format for requests and responses. Specific headers for this aren't listed in the documentation, but it is safe to assume that `Content-Type: application/json` and `Accept: application/json` are used for requests.
- The iOS app (version 1.0.6) uses `Aquatlantis/89 CFNetwork/3826.500.131 Darwin/24.5.0` as the user agent, but this doesn't appear to be required for the HTTP API.

## User - login

To authenticate with the Ori controller, you need to provide your email and password. The authentication endpoint will return a session token that is used for subsequent requests.

| Property | Value                                                                       |
| -------- | --------------------------------------------------------------------------- |
| Endpoint | `http://8.209.119.184:8888/api/user/login?grant_type=app&brand=Aquatlantis` |
| Method   | `POST`                                                                      |
| Headers  | None                                                                        |

Body:

```json
{
  "credentials": "user_password",
  "principal": "password@user@email.com"
}
```

Response:

```json
{
  "code": 0,
  "showMsg": false,
  "data": {
    "brand": "Aquatlantis",
    "token": "token",
    "avatar": null,
    "email": "user@email.com",
    "nickname": "username",
    "mqttClientid": "mqtt_client_id",
    "mqttUsername": "mqtt_username",
    "mqttPassword": "mqtt_password",
    "topic": "app/radians/uuid"
  },
  "message": "Successfully!",
  "allDataCount": 0
}
```

Notes:

- The user email is prefixed with `password@` in the request.
- MQTT credentials are provided in the response.
- The `topic` doesn't appear to be a topic where data is published.
- The `token` is used for subsequent HTTP requests to authenticate the user.

## User - info

Get information about the authenticated user.

| Property | Value                                     |
| -------- | ----------------------------------------- |
| Endpoint | `http://8.209.119.184:8888/api/user/info` |
| Method   | `PUT`                                     |
| Headers  | None                                      |

Body:

```json
{
  "iosToken": "token"
}
```

Response:

```json
{
  "code": 0,
  "showMsg": false,
  "data": {
    "brand": "Aquatlantis",
    "token": "token",
    "avatar": null,
    "email": "user@email.com",
    "nickname": "username",
    "mqttClientid": "mqtt_client_id",
    "mqttUsername": "mqtt_username",
    "mqttPassword": "mqtt_password",
    "topic": "app/radians/uuid"
  },
  "message": "Successfully!",
  "allDataCount": 0
}
```

Notes:

- The `iosToken` is not used in the response, but it is required in the request.

## User - logout

To log out from the Ori controller, you can use the logout endpoint.

| Property | Value                                       |
| -------- | ------------------------------------------- |
| Endpoint | `http://8.209.119.184:8888/api/user/logout` |
| Method   | `POST`                                      |
| Headers  | `Authentication: Bearer token`              |
| Body     | None                                        |

Response:

```json
{
  "code": 0,
  "showMsg": false,
  "data": null,
  "message": "Successfully!",
  "allDataCount": 0
}
```

Notes:

- The authentication token isn't destroyed immediately on the server, so you can keep using it. This looks like a bug.

## Device - all devices

To discover all devices associated with the authenticated user, you can use the following endpoint.

| Property | Value                                           |
| -------- | ----------------------------------------------- |
| Endpoint | `http://8.209.119.184:8888/api/device/list_all` |
| Method   | `GET`                                           |
| Headers  | `Authentication: Bearer token`                  |
| Body     | None                                            |

Response:

```json
{
  "code": 0,
  "showMsg": false,
  "data": {
    "devices": [
      {
        "id": "uuid",
        "brand": "Aquatlantis",
        "name": "user defined name",
        "status": 0,
        "picture": null,
        "pkey": "Aquatlantis527",
        "pid": 0,
        "subid": 0,
        "devid": "ESP-XXX",
        "mac": "XXX",
        "bluetoothMac": "xxx",
        "extend": null,
        "param": null,
        "version": null,
        "enable": true,
        "clientid": "client_id",
        "username": "username",
        "ip": "ip_address",
        "port": 53037,
        "onlineTime": timestamp,
        "offlineTime": timestamp,
        "offlineReason": null,
        "userid": null,
        "icon": null,
        "groupName": null,
        "groupId": null,
        "creator": "uuid",
        "createTime": "datetime",
        "updateTime": null,
        "appNotiEnable": true,
        "emailNotiEnable": false,
        "notiEmail": "",
        "isShow": true,
        "bindDevices": []
      }
    ],
    "filters": [],
    "sharedDevices": []
  },
  "message": "Successfully!",
  "allDataCount": 0
}
```

Notes:

- `devid` is made up of the "ESP-" prefix and WiFi MAC address.
- `appNotiEnable` is true when temperature high/low warnings are enabled in the app.
- `version` seems to always be `null`.

## Device - single device

To get detailed information about a specific device, you can use the following endpoint. You need to replace `uuid` with the actual id of the device.

| Property | Value                                            |
| -------- | ------------------------------------------------ |
| Endpoint | `http://8.209.119.184:8888/api/device/info/uuid` |
| Method   | `GET`                                            |
| Headers  | `Authentication: Bearer token`                   |
| Body     | None                                             |

Response:

```json
{
    "code": 0,
    "showMsg": false,
    "data": {
        "id": "uuid",
        "brand": "Aquatlantis",
        "name": "user defined name",
        "status": 0,
        "picture": null,
        "pkey": "Aquatlantis527",
        "pid": 0,
        "subid": 0,
        "devid": "ESP-XXX",
        "mac": "XXX",
        "bluetoothMac": "xxx",
        "extend": null,
        "param": null,
        "version": null,
        "enable": true,
        "clientid": "client_id",
        "username": "username",
        "ip": "ip_address",
        "port": 53037,
        "onlineTime": timestamp,
        "offlineTime": timestamp,
        "offlineReason": null,
        "userid": null,
        "icon": null,
        "groupName": null,
        "groupId": null,
        "creator": "uuid",
        "createTime": "datetime",
        "updateTime": null,
        "appNotiEnable": true,
        "emailNotiEnable": false,
        "notiEmail": "",
        "isShow": true,
        "bindDevices": []
    },
    "message": "Successfully!",
    "allDataCount": 0
}
```

## Device - notifications

To get the latest firmware information for a specific device, you can use the following endpoint. You need to replace `Aquatlantis527` with the actual pkey of the device.

| Property | Value                                                                     |
| -------- | ------------------------------------------------------------------------- |
| Endpoint | `http://8.209.119.184/api/device/configure_sensor_noti_email/device_uuid` |
| Method   | `PUT`                                                                     |
| Headers  | `Authentication: Bearer token`                                            |

Body:

```json
{
  "appNotiEnable": true,
  "emailNotiEnable": false,
  "email": ""
}
```

Response:

```json
{
  "code": 0,
  "showMsg": false,
  "data": {
    "id": "uuid",
    "brand": "Aquatlantis",
    "name": "user defined name",
    "status": 0,
    "picture": null,
    "pkey": "Aquatlantis527",
    "pid": 0,
    "subid": 0,
    "devid": "ESP-XXX",
    "mac": "XXX",
    "bluetoothMac": "xxx",
    "extend": null,
    "param": null,
    "version": null,
    "enable": true,
    "clientid": "client_id",
    "username": "username",
    "ip": "ip_address",
    "port": 53037,
    "onlineTime": timestamp,
    "offlineTime": timestamp,
    "offlineReason": null,
    "userid": null,
    "icon": null,
    "groupName": null,
    "groupId": null,
    "creator": "uuid",
    "createTime": "datetime",
    "updateTime": null,
    "appNotiEnable": true,
    "emailNotiEnable": false,
    "notiEmail": "",
    "isShow": true,
    "bindDevices": []
  },
  "message": "Successfully!",
  "allDataCount": 0
}
```

Notes:

-

## Firmware info

To get firmware information for the Ori controller, you can use the firmware endpoint.

| Property | Value                                                                                 |
| -------- | ------------------------------------------------------------------------------------- |
| Endpoint | `http://8.209.119.184:8888/api/firmware/latest?brand=Aquatlantis&pkey=Aquatlantis527` |
| Method   | `POST`                                                                                |
| Headers  | `Authentication: Bearer token`                                                        |
| Body     | None                                                                                  |

Response:

```json
{
  "code": 0,
  "showMsg": false,
  "data": {
    "id": "uuid",
    "brand": "Aquatlantis",
    "pkey": "Aquatlantis527",
    "subid": null,
    "firmwareVersion": 12,
    "firmwareName": "Aquatlantis527_V12.bin",
    "firmwarePath": "http://8.209.119.184:9001/aquatlantis/file/firmware/bd7ccc62-3a3a-4328-a5df-9ec8a9760048/Aquatlantis527_V12.bin?params"
  },
  "message": "Successfully!",
  "allDataCount": 0
}
```

Notes:

- `firmwarePath` has several `X-Amz-XXX` parameters.
- `firmwarePath` is a direct link to the firmware file, which can be downloaded.
- It's unclear how to trigger a firmware update. This needs to be investigated further; it may be done via MQTT.
