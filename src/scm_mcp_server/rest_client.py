"""HTTP REST client for SCM API.

Design:
- request(method, full_path, *, params, json) → (status: int, body: dict | str)
- Injects Bearer token automatically via auth.bearer_headers()
- Does NOT raise on non-2xx status codes (caller handles status)
- Returns tuple of (status_code, parsed_body)
"""

from typing import Any

import httpx

from . import auth
from .config import Config


def request(
    method: str,
    full_path: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any] | str]:
    """Execute HTTP request to SCM API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        full_path: Full API path (e.g., "/config/operations/v1/jobs")
        params: Query parameters (optional)
        json: Request body for POST/PUT/PATCH (optional)

    Returns:
        Tuple of (status_code, response_body)
        - response_body is dict if JSON, str if plain text

    Raises:
        httpx.RequestError: For network errors (timeout, connection refused)
    """
    url = f"{Config.BASE_URL}{full_path}"
    headers = auth.bearer_headers()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                headers=headers,
            )

        # Parse response body
        try:
            body = response.json()
        except Exception:
            # Not JSON, return raw text
            body = response.text

        return response.status_code, body

    except httpx.RequestError as e:
        # Network error: timeout, connection refused, etc.
        raise RuntimeError(f"Network error: {e}") from e
