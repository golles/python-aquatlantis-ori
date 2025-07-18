# MQTT API

The MQTT server is used to control the devices and receive direct updates from them.

## General Notes

- The MQTT server is listening on port `10883` and not the default port `1883`.
- Topics are prefixed with `$username`; note that this isn't a placeholder.
- Temperatures are provided in tenths of degrees Celsius, e.g., `250` is `25.0°C`.
- Humidity might be provided in the same format as well.
- Channels are numbered from 1 to 4, such as `ch1brt` being the brightness of channel 1, `ch2brt` for channel 2, and so on:
  - Channel 1 is the red channel
  - Channel 2 is the green channel
  - Channel 3 is the blue channel
  - Channel 4 is the white channel
- The user presets `custom1`, `custom2`, `custom3`, and `custom4` contain 5 values:
  - The first value is the intensity (0-100)
  - The second value is the channel 1 brightness (0-100)
  - The third value is the channel 2 brightness (0-100)
  - The fourth value is the channel 3 brightness (0-100)
  - The fifth value is the channel 4 brightness (0-100)
- `timecurve` is the user-defined schedule for the light:
  - The first element in the list indicates the number of curve entries.
  - Each subsequent 7 elements represent a single timecurve entry, in the following order:
    1. Hour (0-23)
    2. Minute (0-59)
    3. Intensity (0-100)
    4. Channel 1 brightness (0-100)
    5. Channel 2 brightness (0-100)
    6. Channel 3 brightness (0-100)
    7. Channel 4 brightness (0-100)
- Unlike the HTTP API, `version` is provided in the MQTT API, which is the firmware version of the device.
- `dynamic_mode` is the lighting mode.
- On/off can be defined as 1/0, but also as 0/-1.
- Please refer to the code for the exact values, as they are not documented.

## Topics

The following MQTT topics have been discovered:

```txt
$username/Aquatlantis&Aquatlantis527&ESP-XXX/event/post
$username/Aquatlantis&Aquatlantis527&ESP-XXX/ntp/response
$username/Aquatlantis&Aquatlantis527&ESP-XXX/ntp/request
$username/Aquatlantis&Aquatlantis527&ESP-XXX/property/post
$username/Aquatlantis&Aquatlantis527&ESP-XXX/property/sensor/post
$username/Aquatlantis&Aquatlantis527&ESP-XXX/respto/user_uuid
$username/Aquatlantis&Aquatlantis527&ESP-XXX/reqfrom/user_uuid
$username/Aquatlantis&Aquatlantis527&ESP-XXX/status
$username/Aquatlantis&Aquatlantis527&ESP-XXX/ota/version
```

This can be simplified/combined by listening to:

```txt
$username/Aquatlantis&Aquatlantis527&ESP-XXX/#
```

- `ESP-XXX` is the `devid` of the device, which is a unique identifier for each device.
- `user_uuid` is the `creator` of the device, which is a unique identifier for the user.

## Initial message / data update

There is a message that can be sent to request data back. This can be used as an initial message to get the current state of the device. One or more properties can be requested.

### Request

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/reqfrom/user_uuid`

Payload:

```json
{
  "param": {
    "props": [
      "air_humi",
      "air_humi_thrd",
      "air_temp",
      "air_temp_thrd",
      "ch1brt",
      "ch2brt",
      "ch3brt",
      "ch4brt",
      "custom1",
      "custom2",
      "custom3",
      "custom4",
      "device_time",
      "dynamic_mode",
      "intensity",
      "ip",
      "light_type",
      "mode",
      "power",
      "preview",
      "rssi",
      "sensor_type",
      "sensor_valid",
      "ssid",
      "timecurve",
      "timeoffset",
      "version",
      "water_temp",
      "water_temp_thrd"
    ]
  },
  "id": 1234567890,
  "brand": "Aquatlantis",
  "devid": "ESP-XXX",
  "method": "property.get",
  "version": "1",
  "pkey": "Aquatlantis527"
}
```

Notes:

- The `id` is a random number that is used to identify the request and response.
- The `props` list contains the properties that should be returned in the response; there might be more.

### Response

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/respto/user_uuid`

Payload:

```json
{
  "version": "1",
  "id": 1234567890,
  "brand": "Aquatlantis",
  "pkey": "Aquatlantis527",
  "devid": "ESP-XXX",
  "method": "property.get",
  "param": {
    "air_humi_thrd": [0, 0],
    "air_temp_thrd": [0, 0],
    "ch1brt": 100,
    "ch2brt": 100,
    "ch3brt": 100,
    "ch4brt": 100,
    "custom1": [100, 100, 100, 100, 100],
    "custom2": [100, 100, 100, 100, 100],
    "custom3": [100, 100, 100, 100, 100],
    "custom4": [100, 100, 100, 100, 100],
    "device_time": "timestamp",
    "dynamic_mode": 0,
    "intensity": 40,
    "ip": "ip",
    "light_type": 0,
    "mode": 0,
    "power": 1,
    "preview": -1,
    "rssi": -61,
    "sensor_type": 1,
    "sensor_valid": 1,
    "ssid": "WiFi SSID",
    "timecurve": [
      7, 0, 0, 100, 0, 0, 0, 0, 8, 0, 100, 0, 0, 0, 0, 10, 0, 100, 100, 100, 100, 100,
      18, 0, 100, 100, 100, 100, 100, 19, 0, 100, 10, 10, 10, 10, 20, 0, 100, 5, 5, 5,
      5, 21, 0, 100, 0, 0, 2, 0
    ],
    "timeoffset": 120,
    "version": 12,
    "water_temp": 250,
    "water_temp_thrd": [0, 0]
  }
}
```

## Device updates

Device updates are provided when they change.

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/property/set`

Payload:

```json
{
  "method": "property.set",
  "brand": "Aquatlantis",
  "param": {
    "intensity": 75
  },
  "id": 1234567890,
  "version": "1",
  "pkey": "Aquatlantis527",
  "devid": "ESP-XXX"
}
```

Notes:

- `param` contains one or more properties (listed above) that are updated. In this case, the `intensity` is set to `75`.

## Sensor updates

Sensor updates appear to be provided on a time-based interval. This appears to be every 5 minutes.

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/property/sensor/post`

Payload:

```json
{
  "version": "1",
  "id": 1234567890,
  "brand": "Aquatlantis",
  "pkey": "Aquatlantis527",
  "devid": "ESP-XXX",
  "method": "property.post",
  "param": {
    "water_temp": 243
  }
}
```

Notes:

- `param` contains one or more properties (listed above) that are updated. In this case, the `water_temp` is set to `243`.

## Device status

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/status`
Payload:

```json
{
  "username": "username",
  "timestamp": 1234567890,
  "status": 0,
  "reason": "keepalive_timeout",
  "port": 62906,
  "pkey": "Aquatlantis527",
  "ip": "ip",
  "devid": "ESP-XXX",
  "clientid": "client_id",
  "brand": "Aquatlantis",
  "app": 0
}
```

Notes:

- `status` can be `0` (offline) or `1` (online).
- `reason` can be `keepalive_timeout`, but can also be missing, which indicates that the device is online.
- `port` has another value

## Firmware/OTA

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/ota/version`

Payload:

```json
{
  "version": "1",
  "id": 1,
  "brand": "Aquatlantis",
  "pkey": "Aquatlantis527",
  "devid": "ESP-XXX",
  "method": "ota.version",
  "param": {
    "version": 12
  }
}
```

## Device control

Some values of the device can be controlled via MQTT, such as `power`, `dynamic_mode`, `intensity`, and more.

### Power control

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/property/set`

Payload:

```json
{
  "method": "property.set",
  "brand": "Aquatlantis",
  "param": {
    "power": 0
  },
  "id": 1234567890,
  "version": "1",
  "pkey": "Aquatlantis527",
  "devid": "ESP-XXX"
}
```

Notes:

- In this example, `power` is set to `0`, which turns the device off, whereas `1` would turn it on.

### Light control - setting several properties

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/property/set`

Payload:

```json
{
  "method": "property.set",
  "brand": "Aquatlantis",
  "param": {
    "power": 1,
    "intensity": 100,
    "ch1brt": 100,
    "ch2brt": 100,
    "ch3brt": 100,
    "ch4brt": 100
  },
  "id": 1234567890,
  "version": "1",
  "pkey": "Aquatlantis527",
  "devid": "ESP-XXX"
}
```

## NTP requests

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/ntp/request`

Payload:

```json
{
  "deviceSendTime": 4540
}
```

Topic: `$username/Aquatlantis&Aquatlantis527&ESP-XXX/ntp/response`

Payload:

```json
{
  "serverRecvTime": 1752704115809,
  "deviceSendTime": 4540
}
```
