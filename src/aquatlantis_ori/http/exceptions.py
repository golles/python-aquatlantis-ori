"""HTTP exceptions."""

from aquatlantis_ori.exceptions import AquatlantisOriError


class AquatlantisOriConnectionError(AquatlantisOriError):
    """Exception raised for connection errors."""


class AquatlantisOriTimeoutError(AquatlantisOriError):
    """Exception raised for timeout errors."""


class AquatlantisOriDeserializeError(AquatlantisOriError):
    """Exception raised for deserialization errors."""


class AquatlantisOriLoginError(AquatlantisOriError):
    """Exception raised for login errors."""
