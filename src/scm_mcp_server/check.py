"""Connectivity check for SCM API.

Validates:
1. OAuth2 token can be obtained
2. SCM API is reachable (GET /config/operations/v1/jobs)

Exit codes:
- 0: Success
- 1: Failure
"""

import sys

from . import auth, rest_client


def main() -> None:
    """Run connectivity check.

    Exit codes:
        0: All checks passed
        1: One or more checks failed
    """
    print("SCM MCP Server - Connectivity Check")
    print("=" * 50)

    # Check 1: OAuth2 token
    print("\n[1/2] Testing OAuth2 authentication...")
    try:
        token = auth.get_token()
        print(f"    ✓ Token obtained (length: {len(token)} chars)")
    except Exception as e:
        print(f"    ✗ Authentication failed: {e}")
        sys.exit(1)

    # Check 2: API connectivity
    print("\n[2/2] Testing SCM API connectivity...")
    try:
        status, body = rest_client.request("GET", "/config/operations/v1/jobs", params={"limit": 1})

        if 200 <= status < 300:
            print(f"    ✓ API reachable (HTTP {status})")
        else:
            print(f"    ✗ API returned HTTP {status}")
            print(f"    Response: {body}")
            sys.exit(1)

    except Exception as e:
        print(f"    ✗ API request failed: {e}")
        sys.exit(1)

    # Success
    print("\n" + "=" * 50)
    print("✓ All checks passed")
    print("=" * 50)
    sys.exit(0)


if __name__ == "__main__":
    main()
