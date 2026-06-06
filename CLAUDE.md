# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
# Run all tests with coverage
uv run pytest

# Run a single test file
uv run pytest tests/test_device.py

# Run a single test by name
uv run pytest tests/test_device.py::test_set_power

# Type checking
uv run mypy .

# Lint
uv run ruff check .
uv run pylint src tests

# Format (auto-fix)
uv run ruff format .

# Check formatting without fixing
uv run ruff format --check .

# All CI checks (requires jq and yq)
./scripts/local_ci_checks.sh
```

All commands use `uv run` — the virtual environment is managed by `uv` at `.venv/`.

## Architecture

This is an async Python client library for the **Aquatlantis Ori Smart Controller** (aquarium lighting). The API was reverse-engineered; it is not officially supported.

The library uses **two protocols in parallel**:

- **HTTP** (`src/aquatlantis_ori/http/`) — Authentication (login/logout), device listing, device info, and firmware checks. Uses `aiohttp` + Bearer token. All responses deserialize via `mashumaro` (`DataClassORJSONMixin`).
- **MQTT** (`src/aquatlantis_ori/mqtt/`) — Real-time device state updates and device control. Uses `paho-mqtt` v5, non-default port `10883`. Topics are prefixed with the literal string `$username` (not a placeholder).

### Data flow

1. `AquatlantisOriClient` (the public entry point in `client.py`) logs in via HTTP, receives MQTT credentials, then connects the MQTT client.
2. Devices are fetched from HTTP and wrapped in `Device` objects; each `Device` immediately subscribes to its MQTT topic (`$username/<brand>&<pkey>&<devid>/#`) and issues a `force_update` to request current state.
3. Incoming MQTT messages update `Device` state via `update_mqtt_data()` or `update_status()`. HTTP data is updated via `update_http_data()`.
4. Control commands (e.g. `device.set_light()`) publish directly to MQTT; no HTTP call needed.

### Key encoding quirks (from the reversed API)

- **Temperatures** are integers in tenths of °C (e.g. `250` → `25.0°C`). `helpers.float_from_tenths()` handles this.
- **RGBA channels** in MQTT use `ch1brt`/`ch2brt`/`ch3brt`/`ch4brt` for red/green/blue/white. The `Device` class maps these to human-readable field names.
- **`timecurve`** is a flat `list[int]` where the first element is the count, followed by groups of 7 `[hour, minute, intensity, r, g, b, w]`. `helpers.time_curves_from_list()` / `list_from_time_curves()` handle parsing and encoding.
- **Custom presets** (`custom1`–`custom4`) are `list[int]` of 5 values: `[intensity, r, g, b, w]`.
- **`timeoffset`** is in minutes (not seconds), relative to UTC. Used by `Device.get_current_timecurve()` to find which scheduled light setting is currently active.

### Model serialization

All HTTP request/response models extend `mashumaro`'s `DataClassORJSONMixin`, giving `.from_json()` / `.to_json()` / `.to_dict()` for free. HTTP model field names mirror the camelCase API (e.g. `mqttClientid`, `appNotiEnable`); `Device.update_http_data()` maps these to snake_case attributes via explicit `field_source_map` dicts.

### Public API surface

Everything exported from `src/aquatlantis_ori/__init__.py` is the public interface: `AquatlantisOriClient`, `Device`, the exception classes, and all enums/dataclasses from `models.py`.

### Tests

Tests are in `tests/` and split by concern: `test_device.py`, `test_helpers.py`, `test_client.py`, with `http/` and `mqtt/` subdirectories for protocol-specific tests. Tests use `pytest-asyncio` (all async, `asyncio_mode = "auto"`). The MQTT client is typically mocked with `MagicMock(spec=AquatlantisOriMQTTClient)`.
