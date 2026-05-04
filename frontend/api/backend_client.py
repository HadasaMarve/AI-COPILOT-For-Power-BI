"""
HTTP client for the FastAPI AI analysis backend.
"""

from typing import Any
import requests
from requests.exceptions import Timeout, RequestException

from config import BACKEND_URL

_TIMEOUT_SECONDS: int = 30


def request_ai_analysis(payload) -> dict[str, Any]:
    """
    POST payload to the backend and return the parsed JSON response.

    Retries once on any transient failure before raising.

    Args:
        payload: Request body built by payload_builder.

    Returns:
        Parsed JSON dict from the backend.

    Raises:
        RuntimeError: If both attempts fail.
    """
    last_error: Exception | None = None

    for attempt in range(2):
        try:
            response = requests.post(
                BACKEND_URL,
                json=payload,
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except Timeout as exc:
            last_error = exc
        except RequestException as exc:
            last_error = exc

    raise RuntimeError(
        f"Backend request failed after 2 attempts: {last_error}"
    ) from last_error
