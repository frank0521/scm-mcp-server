"""Configuration loader for SCM MCP Server.

Reads 5 environment variables required for SCM API access:
- SCM_BASE_URL: SCM API base URL (optional, has default)
- SCM_AUTH_URL: OAuth2 authentication URL (optional, has default)
- SCM_CLIENT_ID: OAuth2 client ID (required)
- SCM_CLIENT_SECRET: OAuth2 client secret (required)
- SCM_TSG_ID: Tenant Service Group ID (required)
"""

import os


class Config:
    """Configuration singleton loaded from environment variables."""

    # API URLs (with defaults)
    BASE_URL: str = os.getenv("SCM_BASE_URL", "https://api.strata.paloaltonetworks.com")
    AUTH_URL: str = os.getenv("SCM_AUTH_URL", "https://auth.apps.paloaltonetworks.com")

    # OAuth2 Credentials (required)
    CLIENT_ID: str | None = os.getenv("SCM_CLIENT_ID")
    CLIENT_SECRET: str | None = os.getenv("SCM_CLIENT_SECRET")
    TSG_ID: str | None = os.getenv("SCM_TSG_ID")

    @classmethod
    def validate(cls) -> None:
        """Validate that all required environment variables are set.

        Raises:
            RuntimeError: If any required variable is missing.
        """
        missing = []
        if not cls.CLIENT_ID:
            missing.append("SCM_CLIENT_ID")
        if not cls.CLIENT_SECRET:
            missing.append("SCM_CLIENT_SECRET")
        if not cls.TSG_ID:
            missing.append("SCM_TSG_ID")

        if missing:
            raise RuntimeError(f"缺少必填环境变量: {', '.join(missing)}")


# Validate on module import
Config.validate()
