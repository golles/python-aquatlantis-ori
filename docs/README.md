# Aquatlantis Ori API

> [!CAUTION]
> This project is a personal, unofficial effort and is not affiliated with Aquatlantis. It was created to learn and experiment with controlling my own aquarium.
> The Ori API was reverse-engineered for this purpose, and functionality may break at any time if Aquatlantis changes their API.
> I'm not responsible for any damage or issues that may arise from using this client. Use at your own risk!

This documentation was created while reverse-engineering the Ori app (version 1.0.6) using tools like Wireshark to capture HTTP and MQTT traffic between the Ori app and the Ori server.
This documentation serves as a starting point for understanding how to interact with the Ori API. It is not exhaustive and may not cover all features or endpoints available in the API.
The documentation may be outdated or incomplete and should be used as a reference. For the most accurate and up-to-date information, refer to the source code in this repository, which is the most reliable source of information about the API.

The API is divided into two communication methods:

- [HTTP](HTTP.md) - authentication, device management, firmware information.
- [MQTT](MQTT.md) - real-time updates, device control.
