"""SCM REST API client using httpx."""

import logging
from typing import Any, Optional

import httpx

from .auth import OAuth2Manager

logger = logging.getLogger(__name__)


class SCMClient:
    """HTTP client for SCM API with automatic OAuth2 token management.

    This client wraps httpx and provides:
    - Automatic Bearer token injection
    - Token refresh on 401 errors
    - Transparent error handling
    """

    def __init__(
        self,
        oauth: OAuth2Manager,
        timeout: float = 30.0,
    ) -> None:
        """Initialize SCM client.

        Args:
            oauth: OAuth2Manager instance for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.oauth = oauth
        self.http = httpx.AsyncClient(
            base_url=oauth.base_url,
            timeout=timeout,
            follow_redirects=True,
        )
        self._retry_count = 0

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute HTTP request with automatic token management.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., "/iam/v1/service-accounts")
            params: Query parameters (optional)
            json: Request body for POST/PUT (optional)

        Returns:
            Parsed JSON response as dictionary

        Raises:
            httpx.HTTPStatusError: For 4xx/5xx errors (after retry for 401)
            httpx.RequestError: For network errors
        """
        # Get access token
        token = await self.oauth.get_access_token()

        # Build headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Make request
        try:
            response = await self.http.request(
                method=method,
                url=path,
                params=params,
                json=json,
                headers=headers,
            )

            # Handle 401 with token refresh and retry
            if response.status_code == 401 and self._retry_count == 0:
                logger.info("Received 401, refreshing token and retrying")
                self._retry_count += 1
                try:
                    await self.oauth.refresh_token()
                    return await self.request(method, path, params, json)
                finally:
                    self._retry_count = 0

            # Raise for other error status codes
            response.raise_for_status()

            # Parse and return JSON response
            if response.status_code == 204:  # No Content
                return {"success": True}

            return response.json()

        except httpx.HTTPStatusError as e:
            # Extract error details from response
            error_detail = self._extract_error_detail(e.response)
            logger.error(
                f"SCM API error: {method} {path} -> HTTP {e.response.status_code}: {error_detail}"
            )
            raise

        except httpx.RequestError as e:
            logger.error(f"Network error: {method} {path} -> {e}")
            raise

        finally:
            # Reset retry count for next request
            if self._retry_count > 0:
                self._retry_count = 0

    async def get(
        self, path: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Execute GET request.

        Args:
            path: API path
            params: Query parameters (optional)

        Returns:
            Parsed JSON response
        """
        return await self.request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute POST request.

        Args:
            path: API path
            json: Request body
            params: Query parameters (optional)

        Returns:
            Parsed JSON response
        """
        return await self.request("POST", path, params=params, json=json)

    async def put(
        self,
        path: str,
        json: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute PUT request.

        Args:
            path: API path
            json: Request body
            params: Query parameters (optional)

        Returns:
            Parsed JSON response
        """
        return await self.request("PUT", path, params=params, json=json)

    async def delete(
        self, path: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Execute DELETE request.

        Args:
            path: API path
            params: Query parameters (optional)

        Returns:
            Parsed JSON response
        """
        return await self.request("DELETE", path, params=params)

    async def patch(
        self,
        path: str,
        json: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute PATCH request.

        Args:
            path: API path
            json: Request body
            params: Query parameters (optional)

        Returns:
            Parsed JSON response
        """
        return await self.request("PATCH", path, params=params, json=json)

    async def close(self) -> None:
        """Close HTTP client connection pool."""
        await self.http.aclose()

    def _extract_error_detail(self, response: httpx.Response) -> str:
        """Extract error message from SCM API error response.

        Args:
            response: HTTP response object

        Returns:
            Human-readable error message
        """
        try:
            error_data = response.json()
            # Common error fields in SCM API
            if isinstance(error_data, dict):
                return (
                    error_data.get("message")
                    or error_data.get("error")
                    or error_data.get("error_description")
                    or str(error_data)
                )
            return str(error_data)
        except Exception:
            # If JSON parsing fails, return raw text
            return response.text[:200]  # Truncate long error messages
