"""Read-only diagnostic example for the Aquatlantis Ori client.

Connects to the live service and prints the parsed state of every device. It
NEVER sends control actions (no ``set_*`` / power / light calls); the only
outbound MQTT is the ``property.get`` request the client issues on connect to
fetch current state.

Credentials are read from the environment so they are never committed:

    export AQUATLANTIS_USERNAME="you@example.com"
    export AQUATLANTIS_PASSWORD="your-password"
    uv run python examples/validate.py
"""

import asyncio
import logging
import os
import warnings

from aquatlantis_ori import AquatlantisOriClient

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("validate")

CHANNEL_MIN = 0
CHANNEL_MAX = 100
MINUTES_PER_HOUR = 60
MAX_PLAUSIBLE_OFFSET_HOURS = 14


def _check_channel(name: str, value: int | None) -> None:
    """Print a colour channel value and whether it falls within the documented range."""
    if value is None:
        print(f"  {name:7}: None (not reported)")
        return
    in_range = CHANNEL_MIN <= value <= CHANNEL_MAX
    print(f"  {name:7}: {value}  range {CHANNEL_MIN}-{CHANNEL_MAX} {'OK' if in_range else 'OUT OF RANGE'}")


async def main() -> None:
    """Connect read-only and print parsed device state."""
    username = os.environ.get("AQUATLANTIS_USERNAME")
    password = os.environ.get("AQUATLANTIS_PASSWORD")
    if not username or not password:
        msg = "Set AQUATLANTIS_USERNAME and AQUATLANTIS_PASSWORD environment variables."
        raise SystemExit(msg)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")

        async with AquatlantisOriClient(username, password) as client:
            await client.connect()  # logs in (HTTP), connects MQTT, force_update (property.get)

            # force_update-on-connect: data should arrive without waiting for periodic telemetry.
            try:
                await client.wait_for_data(max_wait=10.0)
                print("[force_update-on-connect] data received within timeout: OK")
            except TimeoutError:
                print("[force_update-on-connect] TIMEOUT waiting for first MQTT payload")

            # Read-only HTTP refresh; exercises device_info deserialization.
            await client.update_devices()
            print("[update_devices] HTTP refresh + deserialize: OK")

            devices = client.get_devices()
            print(f"[devices] found {len(devices)}")

            for device in devices:
                print(f"\n=== {device.name} ({device.devid}) ===")
                print(f"[availability] status={device.status} availability_state={device.availability_state}")

                print(f"[timeoffset] {device.timeoffset} (minutes)")
                if device.timeoffset is not None:
                    hours = device.timeoffset / MINUTES_PER_HOUR
                    plausible = -MAX_PLAUSIBLE_OFFSET_HOURS <= hours <= MAX_PLAUSIBLE_OFFSET_HOURS
                    print(f"  => {hours:+.1f}h  {'plausible as minutes' if plausible else 'IMPLAUSIBLE'}")

                print(f"[get_current_timecurve] {device.get_current_timecurve()}")
                print(f"[is_light_on] power={device.power} mode={device.mode} -> {device.is_light_on}")

                print("[channels]")
                _check_channel("red", device.red)
                _check_channel("green", device.green)
                _check_channel("blue", device.blue)
                _check_channel("white", device.white)
                print(f"  intensity: {device.intensity}")

                print("[custom presets]")
                for idx in (1, 2, 3, 4):
                    print(f"  custom{idx}: {getattr(device, f'custom{idx}')}")

                print(f"[firmware] installed={device.version} latest={device.latest_firmware_version} name={device.firmware_name}")

    paho_v1 = [str(w.message) for w in caught if "Callback API version 1" in str(w.message)]
    print(f"\n[paho callback api] deprecated-v1 warnings: {paho_v1 or 'none (VERSION2 OK)'}")


if __name__ == "__main__":
    asyncio.run(main())
