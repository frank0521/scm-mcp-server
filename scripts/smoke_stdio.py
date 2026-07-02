#!/usr/bin/env python3
"""stdio smoke test: prove the MCP server works over real stdio transport.

Runs: initialize → tools/list → call_tool(list_jobs) via official mcp SDK client.
Exit 0 on success, 1 on failure.
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = str(PROJECT_ROOT / "venv" / "bin" / "python")

EXPECTED_TOOL_COUNT = 168


async def main() -> int:
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.session import ClientSession

    server_params = StdioServerParameters(
        command=VENV_PYTHON,
        args=["-m", "scm_mcp_server.server"],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. Initialize
            result = await session.initialize()
            print(f"[OK] initialize: server={result.serverInfo.name}")

            # 2. tools/list
            tools_result = await session.list_tools()
            tool_names = {t.name for t in tools_result.tools}
            count = len(tool_names)

            if count != EXPECTED_TOOL_COUNT:
                print(f"[FAIL] tools/list: expected {EXPECTED_TOOL_COUNT}, got {count}")
                return 1
            print(f"[OK] tools/list: {count} tools registered")

            # Verify against routing tables
            sys.path.insert(0, str(PROJECT_ROOT / "src"))
            from scm_mcp_server.tools import (
                _LIST_TOOLS, _GET_BY_ID_TOOLS, _CREATE_TOOLS, _UPDATE_TOOLS,
                _DELETE_TOOLS, _MOVE_TOOLS, _PUSH_TOOLS, _LOAD_TOOLS, _COMMIT_TOOLS,
            )
            expected_names = set()
            for table in [_LIST_TOOLS, _GET_BY_ID_TOOLS, _CREATE_TOOLS, _UPDATE_TOOLS,
                          _DELETE_TOOLS, _MOVE_TOOLS, _PUSH_TOOLS, _LOAD_TOOLS, _COMMIT_TOOLS]:
                expected_names |= table.keys()

            if tool_names != expected_names:
                missing = expected_names - tool_names
                extra = tool_names - expected_names
                if missing:
                    print(f"[FAIL] Missing tools: {sorted(missing)}")
                if extra:
                    print(f"[FAIL] Extra tools: {sorted(extra)}")
                return 1
            print("[OK] tool name set matches routing tables exactly")

            # 3. call_tool: proves dispatch works end-to-end over stdio
            # list_roles has no container requirement, avoids schema validation issues
            call_result = await session.call_tool("list_roles", {})
            text = call_result.content[0].text
            print(f"[OK] call_tool(list_roles): response received ({len(text)} chars)")
            print(f"     Preview: {text[:200]}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
