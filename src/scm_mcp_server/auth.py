"""OAuth2 client_credentials authentication for SCM API.

Token lifecycle:
- Valid for 15 minutes (900 seconds)
- Refreshed automatically 60 seconds before expiration
- Thread-safe with threading.Lock
"""

import threading
import time
from typing import Any

import httpx

from .config import Config


class OAuth2Manager:
    """Manages OAuth2 token lifecycle with automatic refresh."""

    # Token validity: 15 minutes, refresh 60s early
    TOKEN_LIFETIME = 900  # seconds
    REFRESH_BUFFER = 60  # seconds

    def __init__(self) -> None:
        """Initialize OAuth2 manager."""
        self._token: str | None = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def get_token(self) -> str:
        """Get valid access token, refreshing if necessary.

        Returns:
            Valid OAuth2 access token.

        Raises:
            RuntimeError: If token fetch fails.
        """
        with self._lock:
            now = time.time()
            # Refresh if token is missing or will expire within 60 seconds
            if not self._token or now >= (self._expires_at - self.REFRESH_BUFFER):
                self._fetch_token()

            if not self._token:
                raise RuntimeError("Failed to obtain access token")

            return self._token

    def bearer_headers(self) -> dict[str, str]:
        """Get HTTP headers with Bearer token.

        Returns:
            Headers dictionary with Authorization and Content-Type.
        """
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _fetch_token(self) -> None:
        """Fetch new access token from SCM auth service.

        Updates internal token cache and expiration time.

        Raises:
            RuntimeError: If authentication fails.
        """
        # Validate config before attempting auth
        Config.validate()

        url = f"{Config.AUTH_URL}/auth/v1/oauth2/access_token"
        data = {
            "grant_type": "client_credentials",
            "client_id": Config.CLIENT_ID,
            "client_secret": Config.CLIENT_SECRET,
            "scope": f"tsg_id:{Config.TSG_ID}",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                token_data = response.json()

            self._token = token_data["access_token"]
            # Use server-provided expires_in or fallback to default 15 minutes
            expires_in = token_data.get("expires_in", self.TOKEN_LIFETIME)
            self._expires_at = time.time() + expires_in

        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error_description") or error_data.get("error", "")
            except Exception:
                error_detail = e.response.text[:200]

            raise RuntimeError(
                f"OAuth2 authentication failed (HTTP {e.response.status_code}): {error_detail}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error during authentication: {e}") from e


# Singleton instance
_oauth_manager = OAuth2Manager()


def get_token() -> str:
    """Get valid OAuth2 access token (singleton interface).

    Returns:
        Valid access token string.
    """
    return _oauth_manager.get_token()


def bearer_headers() -> dict[str, str]:
    """Get HTTP headers with Bearer token (singleton interface).

    Returns:
        Headers dictionary.
    """
    return _oauth_manager.bearer_headers()
