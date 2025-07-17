"""HTTP Constants."""

from enum import StrEnum
from typing import Final

PORT: Final[int] = 8888
PROTOCOL: Final[str] = "http"


class HttpMethod(StrEnum):
    """HTTP methods."""

    DELETE = "DELETE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
