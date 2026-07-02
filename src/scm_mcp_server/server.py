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
    from .tools import (
        _LIST_TOOLS, _GET_BY_ID_TOOLS, _CREATE_TOOLS, _UPDATE_TOOLS,
        _DELETE_TOOLS, _MOVE_TOOLS, _PUSH_TOOLS, _LOAD_TOOLS, _COMMIT_TOOLS,
    )
    from .tools.schemas import (
        list_schema, get_by_id_schema, move_schema, push_schema,
        load_schema, commit_schema, create_schema, update_schema, delete_schema,
    )

    tools_list: list[Tool] = []

    # Generate list tools
    for name, (path, param_keys) in _LIST_TOOLS.items():
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

    # Generate create tools
    for name, (path, body_param_keys, query_param_keys) in _CREATE_TOOLS.items():
        tools_list.append(
            Tool(
                name=name,
                description=f"⚠️ 写操作 Create resource at {path}",
                inputSchema=create_schema(has_container="folder" in query_param_keys),
            )
        )

    # Generate update tools
    for name, (path_template, path_param_keys, query_param_keys) in _UPDATE_TOOLS.items():
        tools_list.append(
            Tool(
                name=name,
                description=f"⚠️ 写操作 Update resource at {path_template}",
                inputSchema=update_schema(has_container="folder" in query_param_keys),
            )
        )

    # Generate delete tools
    for name, (path_template, path_param_keys, query_param_keys) in _DELETE_TOOLS.items():
        tools_list.append(
            Tool(
                name=name,
                description=f"⚠️ 写操作 Delete resource at {path_template}",
                inputSchema=delete_schema(has_container="folder" in query_param_keys),
            )
        )

    # Generate move tools
    for name, (path_template, body_keys) in _MOVE_TOOLS.items():
        tools_list.append(
            Tool(
                name=name,
                description=f"⚠️ 写操作，会改变规则顺序 Move rule at {path_template}",
                inputSchema=move_schema(),
            )
        )

    # Generate push tools
    for name, (path, body_keys) in _PUSH_TOOLS.items():
        tools_list.append(
            Tool(
                name=name,
                description="⚠️ 高风险写操作：会将候选配置下发到真实设备 Push candidate configuration",
                inputSchema=push_schema(),
            )
        )

    # Generate load tools
    for name, (path, body_keys) in _LOAD_TOOLS.items():
        tools_list.append(
            Tool(
                name=name,
                description=f"⚠️ 写操作 Load config version as candidate at {path}",
                inputSchema=load_schema(),
            )
        )

    # Generate commit tools
    for name, (path, body_keys) in _COMMIT_TOOLS.items():
        tools_list.append(
            Tool(
                name=name,
                description=f"⚠️ 写操作 Commit candidate to running config at {path}",
                inputSchema=commit_schema(),
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
