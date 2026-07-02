"""MCP server for SCM API.

Uses official mcp SDK with stdio transport.
Current: Skeleton with empty tools list (Phase 1 TODO).
"""

import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import tools

# Initialize MCP server
app = Server("scm-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools.

    Returns:
        List of Tool objects generated from routing tables.
    """
    from .tools import _LIST_TOOLS, _GET_BY_ID_TOOLS
    from .tools.schemas import list_schema, get_by_id_schema

    tools_list: list[Tool] = []

    # Generate list tools
    for name, (path, param_keys) in _LIST_TOOLS.items():
        # Determine if this tool requires container param (folder/snippet/device)
        # For now, assume all config/security tools require it, ops/iam do not
        requires_container = path.startswith("/config/")

        tools_list.append(
            Tool(
                name=name,
                description=f"List resources at {path}",
                inputSchema=list_schema(required_container=requires_container),
            )
        )

    # Generate get-by-ID tools
    for name, (path_template, param_keys) in _GET_BY_ID_TOOLS.items():
        # Determine ID param name (first in param_keys)
        id_param_name = param_keys[0]
        requires_container = path_template.startswith("/config/")

        tools_list.append(
            Tool(
                name=name,
                description=f"Get resource by {id_param_name} at {path_template}",
                inputSchema=get_by_id_schema(
                    id_param_name=id_param_name, required_container=requires_container
                ),
            )
        )

    return tools_list


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute MCP tool by dispatching to tools module.

    Args:
        name: Tool name
        arguments: Tool input arguments

    Returns:
        List of TextContent with result or error message.
    """
    try:
        result = tools.call(name, arguments)
        # Format result as JSON string
        import json
        result_text = json.dumps(result, indent=2, ensure_ascii=False)
        return [TextContent(type="text", text=result_text)]

    except NotImplementedError as e:
        # Tool not implemented yet
        error_msg = f"Tool not implemented: {str(e)}"
        return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        # Unexpected error
        error_msg = f"Tool execution error: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def run_server() -> None:
    """Run MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def main() -> None:
    """CLI entry point for MCP server."""
    import asyncio

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
