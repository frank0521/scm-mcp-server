"""OAuth2 authentication for SCM API using client_credentials flow."""

import asyncio
import os
import time
from typing import Optional

import httpx


class OAuth2Manager:
    """Manages OAuth2 token lifecycle for SCM API authentication.

    Implements client_credentials flow with automatic token refresh.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tsg_id: str,
        base_url: str = "https://api.strata.paloaltonetworks.com",
    ) -> None:
        """Initialize OAuth2 manager.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            tsg_id: Tenant Service Group ID
            base_url: SCM API base URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tsg_id = tsg_id
        self.base_url = base_url
        self.token_endpoint = f"{base_url}/auth/v1/oauth2/access_token"

        self._token: Optional[str] = None
        self._expires_at: Optional[float] = None
        self._lock = asyncio.Lock()

    @classmethod
    def from_env(cls) -> "OAuth2Manager":
        """Create OAuth2Manager from environment variables.

        Required environment variables:
        - SCM_CLIENT_ID
        - SCM_CLIENT_SECRET
        - SCM_TSG_ID

        Optional:
        - SCM_BASE_URL (defaults to production)

        Returns:
            OAuth2Manager instance

        Raises:
            ValueError: If required environment variables are missing
        """
        client_id = os.getenv("SCM_CLIENT_ID")
        client_secret = os.getenv("SCM_CLIENT_SECRET")
        tsg_id = os.getenv("SCM_TSG_ID")
        base_url = os.getenv("SCM_BASE_URL", "https://api.strata.paloaltonetworks.com")

        if not all([client_id, client_secret, tsg_id]):
            missing = []
            if not client_id:
                missing.append("SCM_CLIENT_ID")
            if not client_secret:
                missing.append("SCM_CLIENT_SECRET")
            if not tsg_id:
                missing.append("SCM_TSG_ID")
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            tsg_id=tsg_id,
            base_url=base_url,
        )

    async def get_access_token(self) -> str:
        """Get valid access token, fetching or refreshing as needed.

        Returns:
            Valid OAuth2 access token

        Raises:
            httpx.HTTPError: If token fetch fails
        """
        async with self._lock:
            # Check if cached token is still valid
            if self._token and self._expires_at:
                # Refresh if expiring within 60 seconds
                if time.time() < self._expires_at - 60:
                    return self._token

            # Fetch new token
            await self._fetch_token()

            if not self._token:
                raise RuntimeError("Failed to obtain access token")

            return self._token

    async def _fetch_token(self) -> None:
        """Fetch new access token from SCM API.

        Updates internal token cache and expiration time.

        Raises:
            httpx.HTTPError: If authentication fails
        """
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": f"tsg_id:{self.tsg_id}",
            }

            try:
                response = await client.post(
                    self.token_endpoint,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = f": {error_data.get('error_description', error_data.get('error', ''))}"
                except Exception:
                    pass
                raise RuntimeError(
                    f"Authentication failed (HTTP {e.response.status_code}){error_detail}"
                ) from e
            except httpx.RequestError as e:
                raise RuntimeError(f"Network error during authentication: {e}") from e

            token_data = response.json()
            self._token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            self._expires_at = time.time() + expires_in

    async def refresh_token(self) -> str:
        """Force refresh of access token.

        Returns:
            New access token

        Raises:
            httpx.HTTPError: If token refresh fails
        """
        async with self._lock:
            await self._fetch_token()
            if not self._token:
                raise RuntimeError("Failed to refresh access token")
            return self._token

    def clear_cache(self) -> None:
        """Clear cached token (useful for testing or manual invalidation)."""
        self._token = None
        self._expires_at = None
