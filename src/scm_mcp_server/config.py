"""Configuration loader for SCM MCP Server.

Loading priority:
1. Environment variables (SCM_CLIENT_ID, SCM_CLIENT_SECRET, SCM_TSG_ID)
2. Encrypted credentials file (~/.scm-mcp/credentials.enc)

If env vars are set, they take precedence. Otherwise falls back to the
encrypted file (requires SCM_MASTER_KEY env or interactive passphrase).
"""

import os


class Config:
    """Configuration loaded from env vars or encrypted credentials."""

    # API URLs (with defaults)
    BASE_URL: str = os.getenv("SCM_BASE_URL", "https://api.strata.paloaltonetworks.com")
    AUTH_URL: str = os.getenv("SCM_AUTH_URL", "https://auth.apps.paloaltonetworks.com")

    # OAuth2 Credentials (required)
    CLIENT_ID: str | None = os.getenv("SCM_CLIENT_ID")
    CLIENT_SECRET: str | None = os.getenv("SCM_CLIENT_SECRET")
    TSG_ID: str | None = os.getenv("SCM_TSG_ID")

    _loaded_from_encrypted: bool = False

    @classmethod
    def validate(cls) -> None:
        """Validate credentials are available. Falls back to encrypted file.

        Raises:
            RuntimeError: If credentials are unavailable from all sources.
        """
        if cls.CLIENT_ID and cls.CLIENT_SECRET and cls.TSG_ID:
            return

        # Try encrypted credentials fallback
        try:
            from .secrets import load_credentials, CREDENTIALS_FILE
            if CREDENTIALS_FILE.exists():
                creds = load_credentials()
                cls.CLIENT_ID = cls.CLIENT_ID or creds.get("SCM_CLIENT_ID")
                cls.CLIENT_SECRET = cls.CLIENT_SECRET or creds.get("SCM_CLIENT_SECRET")
                cls.TSG_ID = cls.TSG_ID or creds.get("SCM_TSG_ID")
                cls._loaded_from_encrypted = True
        except Exception:
            pass

        missing = []
        if not cls.CLIENT_ID:
            missing.append("SCM_CLIENT_ID")
        if not cls.CLIENT_SECRET:
            missing.append("SCM_CLIENT_SECRET")
        if not cls.TSG_ID:
            missing.append("SCM_TSG_ID")

        if missing:
            raise RuntimeError(
                f"缺少必填环境变量: {', '.join(missing)}\n"
                "提示: 可通过 scm-mcp-secrets set 存储加密凭据，"
                "或设置 SCM_MASTER_KEY 环境变量自动解密"
            )
