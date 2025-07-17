# Python Aquatlantis Ori

[![PyPI version][pypi_badge]][pypi_link]
[![License][license_badge]][license_link]
[![Codecov][codecov_badge]][codecov_link]
[![Sonar quality gate][sonar_badge]][sonar_link]
[![GitHub repo stars][stars_badge]][stars_link]
[![Buy me a coffee][buymecoffee_badge]][buymecoffee_link]

An asynchronous Python client for the Aquatlantis Ori Smart Controller

> [!CAUTION]
> This project is a personal, unofficial effort and is not affiliated with Aquatlantis. It was created to learn and experiment with controlling my own aquarium.
> The Ori API was reverse-engineered for this purpose, and functionality may break at any time if Aquatlantis changes their API.
> I'm not responsible for any damage or issues that may arise from using this client. Use at your own risk!

## Installation

You can install this package using your preferred package manager. For example, using pip:

```sh
pip install aquatlantis-ori
```

## Usage

To use the Aquatlantis Ori client, you can import it in your Python scripts and start interacting with your Ori controller. Here is a simple example:

```python
import asyncio
import logging

from aquatlantis_ori import AquatlantisOriClient, LightOptions, PowerType

logging.basicConfig(level=logging.WARNING)
logging.getLogger("aquatlantis_ori").setLevel(logging.INFO)


async def main() -> None:
    async with AquatlantisOriClient("email", "password") as client:
        await client.connect()
        device = client.get_devices()[0]

        scenarios: list[dict] = [
            {"power": PowerType.ON, "options": LightOptions(intensity=100, red=100, green=0, blue=0, white=0)},
            {"power": PowerType.ON, "options": LightOptions(intensity=100, red=0, green=100, blue=0, white=0)},
            {"power": PowerType.ON, "options": LightOptions(intensity=100, red=0, green=0, blue=100, white=0)},
            {"power": PowerType.ON, "options": LightOptions(intensity=100, red=0, green=0, blue=0, white=100)},
            {"power": PowerType.ON, "options": LightOptions(intensity=100, red=100, green=100, blue=100, white=100)},
            {"power": PowerType.OFF},
            {"power": PowerType.ON, "options": LightOptions(intensity=80, red=0, green=0, blue=0, white=100)},
            {"power": PowerType.ON, "options": LightOptions(intensity=60, red=0, green=0, blue=0, white=100)},
            {"power": PowerType.ON, "options": LightOptions(intensity=40, red=0, green=0, blue=0, white=100)},
            {"power": PowerType.ON, "options": LightOptions(intensity=20, red=0, green=0, blue=0, white=100)},
            {"power": PowerType.ON, "options": LightOptions(intensity=1, red=0, green=0, blue=0, white=100)},
            {"power": PowerType.OFF},
        ]

        for scenario in scenarios:
            device.set_light(
                power=scenario.get("power"),
                options=scenario.get("options"),
            )
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

Contributions are welcome! Please familiarize yourself with the [contribution guidelines](CONTRIBUTING.md). This document will also help you set up your development environment.

---

Thank you for your interest in the Python Aquatlantis Ori client! If you have any questions or need further assistance, feel free to open an issue or submit a pull request.

[pypi_link]: https://pypi.org/project/aquatlantis-ori/
[pypi_badge]: https://img.shields.io/pypi/v/aquatlantis-ori?style=for-the-badge
[license_link]: https://github.com/golles/python-aquatlantis-ori/blob/main/LICENSE
[license_badge]: https://img.shields.io/github/license/golles/python-aquatlantis-ori.svg?style=for-the-badge
[codecov_link]: https://app.codecov.io/gh/golles/python-aquatlantis-ori
[codecov_badge]: https://img.shields.io/codecov/c/github/golles/python-aquatlantis-ori?style=for-the-badge
[sonar_link]: https://sonarcloud.io/project/overview?id=golles_python-aquatlantis-ori
[sonar_badge]: https://img.shields.io/sonar/quality_gate/golles_python-aquatlantis-ori?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge
[stars_link]: https://github.com/golles/python-aquatlantis-ori/stargazers
[stars_badge]: https://img.shields.io/github/stars/golles/python-aquatlantis-ori?style=for-the-badge
[buymecoffee_link]: https://www.buymeacoffee.com/golles
[buymecoffee_badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
