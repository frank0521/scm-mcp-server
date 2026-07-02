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
        Empty list (TODO: Phase 1 - populate from tool registry).
    """
    # TODO: Phase 1 - Generate tools list from OpenAPI specs
    # tools_list = []
    # for tool_def in tool_registry:
    #     tools_list.append(Tool(
    #         name=tool_def.name,
    #         description=tool_def.description,
    #         inputSchema=tool_def.input_schema,
    #     ))
    # return tools_list

    return []


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
