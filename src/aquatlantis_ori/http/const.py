"""HTTP Constants."""

from enum import StrEnum
from typing import Final

PORT: Final[int] = 8888
# SECURITY: plaintext HTTP — login credentials and the bearer token are sent
# unencrypted. Imposed by the vendor service; see const.SERVER for details.
PROTOCOL: Final[str] = "http"


class HttpMethod(StrEnum):
    """HTTP methods."""

    DELETE = "DELETE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
