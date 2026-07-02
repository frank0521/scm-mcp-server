"""Encrypted credential storage for SCM MCP Server.

Stores SCM_CLIENT_ID, SCM_CLIENT_SECRET, SCM_TSG_ID in an encrypted file
at ~/.scm-mcp/credentials.enc using Fernet (AES-128-CBC + HMAC-SHA256).

Master key derivation: PBKDF2-HMAC-SHA256 from a user-provided passphrase
with a random salt stored alongside the ciphertext.
"""

import base64
import getpass
import json
import sys
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

CREDENTIALS_DIR = Path.home() / ".scm-mcp"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.enc"
SALT_FILE = CREDENTIALS_DIR / "salt"

REQUIRED_KEYS = ("SCM_CLIENT_ID", "SCM_CLIENT_SECRET", "SCM_TSG_ID")


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive Fernet key from passphrase + salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


def _get_passphrase() -> str:
    """Get master passphrase from env or interactive prompt."""
    passphrase = __import__("os").getenv("SCM_MASTER_KEY")
    if passphrase:
        return passphrase
    return getpass.getpass("SCM master passphrase: ")


def store_credentials(credentials: dict[str, str], passphrase: str | None = None) -> Path:
    """Encrypt and store credentials to disk.

    Args:
        credentials: Dict with SCM_CLIENT_ID, SCM_CLIENT_SECRET, SCM_TSG_ID
        passphrase: Master passphrase. Prompts if None.

    Returns:
        Path to the encrypted credentials file.
    """
    CREDENTIALS_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)

    if passphrase is None:
        passphrase = getpass.getpass("Set master passphrase: ")
        confirm = getpass.getpass("Confirm passphrase: ")
        if passphrase != confirm:
            raise ValueError("Passphrases do not match")

    import os as _os
    salt = _os.urandom(16)
    key = _derive_key(passphrase, salt)
    fernet = Fernet(key)

    plaintext = json.dumps(credentials).encode()
    ciphertext = fernet.encrypt(plaintext)

    SALT_FILE.write_bytes(salt)
    SALT_FILE.chmod(0o600)
    CREDENTIALS_FILE.write_bytes(ciphertext)
    CREDENTIALS_FILE.chmod(0o600)

    return CREDENTIALS_FILE


def load_credentials(passphrase: str | None = None) -> dict[str, str]:
    """Decrypt and load credentials from disk.

    Args:
        passphrase: Master passphrase. Uses SCM_MASTER_KEY env or prompts if None.

    Returns:
        Dict with SCM_CLIENT_ID, SCM_CLIENT_SECRET, SCM_TSG_ID.

    Raises:
        FileNotFoundError: If credentials file doesn't exist.
        InvalidToken: If passphrase is wrong.
    """
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"加密凭据文件不存在: {CREDENTIALS_FILE}\n"
            "请先运行: scm-mcp-secrets set"
        )

    if passphrase is None:
        passphrase = _get_passphrase()

    salt = SALT_FILE.read_bytes()
    key = _derive_key(passphrase, salt)
    fernet = Fernet(key)

    ciphertext = CREDENTIALS_FILE.read_bytes()
    try:
        plaintext = fernet.decrypt(ciphertext)
    except InvalidToken:
        raise InvalidToken("解密失败：主密码错误或凭据文件已损坏")

    return json.loads(plaintext)


def delete_credentials() -> None:
    """Remove encrypted credentials from disk."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()
    if SALT_FILE.exists():
        SALT_FILE.unlink()


def main() -> None:
    """CLI entry point for scm-mcp-secrets."""
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: scm-mcp-secrets <command>")
        print("")
        print("Commands:")
        print("  set     Store encrypted credentials (interactive)")
        print("  show    Decrypt and display credentials")
        print("  delete  Remove encrypted credentials")
        print("")
        print("Environment:")
        print("  SCM_MASTER_KEY  Master passphrase (avoids interactive prompt)")
        sys.exit(0)

    command = sys.argv[1]

    if command == "set":
        print(f"Credentials will be stored at: {CREDENTIALS_FILE}")
        client_id = input("SCM_CLIENT_ID: ").strip()
        client_secret = getpass.getpass("SCM_CLIENT_SECRET: ").strip()
        tsg_id = input("SCM_TSG_ID: ").strip()

        if not all([client_id, client_secret, tsg_id]):
            print("Error: All fields are required", file=sys.stderr)
            sys.exit(1)

        credentials = {
            "SCM_CLIENT_ID": client_id,
            "SCM_CLIENT_SECRET": client_secret,
            "SCM_TSG_ID": tsg_id,
        }

        path = store_credentials(credentials)
        print(f"Credentials encrypted and saved to: {path}")

    elif command == "show":
        try:
            creds = load_credentials()
            print(f"SCM_CLIENT_ID:     {creds['SCM_CLIENT_ID']}")
            print(f"SCM_CLIENT_SECRET: {creds['SCM_CLIENT_SECRET'][:4]}{'*' * (len(creds['SCM_CLIENT_SECRET']) - 4)}")
            print(f"SCM_TSG_ID:        {creds['SCM_TSG_ID']}")
        except (FileNotFoundError, InvalidToken) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif command == "delete":
        delete_credentials()
        print("Credentials deleted.")

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
