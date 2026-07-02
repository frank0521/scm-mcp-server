"""MCP server for SCM API."""

import asyncio
import logging
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .auth import OAuth2Manager
from .client import SCMClient
from .openapi_parser import ToolDefinition, parse_all_specs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,  # MCP uses stdout for protocol, stderr for logs
)
logger = logging.getLogger(__name__)

# Global state
app = Server("scm-mcp-server")
oauth_manager: OAuth2Manager
scm_client: SCMClient
tool_definitions: dict[str, ToolDefinition] = {}


async def initialize() -> None:
    """Initialize server: load credentials, parse OpenAPI specs."""
    global oauth_manager, scm_client, tool_definitions

    logger.info("Initializing SCM MCP Server")

    # Load OAuth2 credentials from environment
    try:
        oauth_manager = OAuth2Manager.from_env()
        logger.info("OAuth2 credentials loaded from environment")
    except ValueError as e:
        logger.error(f"Failed to load credentials: {e}")
        raise

    # Initialize SCM client
    scm_client = SCMClient(oauth=oauth_manager)

    # Parse OpenAPI specifications
    openapi_base = os.getenv(
        "OPENAPI_SPEC_PATH", "../pan.dev/openapi-specs/scm"
    )
    try:
        tools = parse_all_specs(openapi_base)
        logger.info(f"Parsed {len(tools)} tools from OpenAPI specs")

        # Build tool lookup dictionary
        for tool in tools:
            tool_definitions[tool.name] = tool

    except FileNotFoundError as e:
        logger.error(f"OpenAPI specs not found: {e}")
        logger.error("Make sure pan.dev repository is cloned at ../pan.dev")
        raise

    logger.info("Initialization complete")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools.

    Returns:
        List of Tool objects for MCP protocol
    """
    tools = []
    for tool_def in tool_definitions.values():
        tools.append(
            Tool(
                name=tool_def.name,
                description=tool_def.description,
                inputSchema=tool_def.input_schema,
            )
        )

    logger.debug(f"Returning {len(tools)} tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute MCP tool by calling SCM API.

    Args:
        name: Tool name (e.g., "scm_iam_list_service_accounts")
        arguments: Tool arguments (validated by MCP SDK)

    Returns:
        List of TextContent with JSON response or error

    Raises:
        ValueError: If tool not found
    """
    logger.info(f"Tool called: {name} with args: {arguments}")

    # Look up tool definition
    tool_def = tool_definitions.get(name)
    if not tool_def:
        error_msg = f"Tool not found: {name}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    try:
        # Execute HTTP request
        result = await execute_tool(tool_def, arguments)

        # Format response as JSON string
        import json
        response_text = json.dumps(result, indent=2)

        logger.info(f"Tool {name} completed successfully")
        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]


async def execute_tool(tool_def: ToolDefinition, arguments: dict[str, Any]) -> Any:
    """Execute a tool by calling SCM API.

    Args:
        tool_def: Tool definition with HTTP method and path
        arguments: Tool arguments (path params, query params, body)

    Returns:
        API response as dictionary

    Raises:
        httpx.HTTPError: If API call fails
    """
    method = tool_def.http_method
    path_template = tool_def.path_template

    # Separate path parameters from other arguments
    path_params = {}
    query_params = {}
    body_data = {}

    # Identify path parameters (in curly braces)
    import re
    path_param_names = re.findall(r"\{(\w+)\}", path_template)

    for key, value in arguments.items():
        if key in path_param_names:
            path_params[key] = value
        elif method in ["POST", "PUT", "PATCH"]:
            # For write methods, non-path params go to body
            body_data[key] = value
        else:
            # For read methods, non-path params are query params
            query_params[key] = value

    # Substitute path parameters
    path = path_template
    for param_name, param_value in path_params.items():
        path = path.replace(f"{{{param_name}}}", str(param_value))

    # Execute request
    if method == "GET":
        return await scm_client.get(path, params=query_params or None)
    elif method == "POST":
        return await scm_client.post(path, json=body_data, params=query_params or None)
    elif method == "PUT":
        return await scm_client.put(path, json=body_data, params=query_params or None)
    elif method == "PATCH":
        return await scm_client.patch(path, json=body_data, params=query_params or None)
    elif method == "DELETE":
        return await scm_client.delete(path, params=query_params or None)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


async def main() -> None:
    """Main entry point: initialize and run MCP server."""
    try:
        # Initialize (load credentials, parse OpenAPI)
        await initialize()

        # Run MCP server with stdio transport
        logger.info("Starting MCP server with stdio transport")
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        await scm_client.close()
        logger.info("Server shutdown complete")


def cli() -> None:
    """CLI entry point for testing.

    Usage:
        python -m scm_mcp.server          # Run server
        python -m scm_mcp.server --list   # List tools
    """
    if len(sys.argv) > 1 and sys.argv[1] in ["--list", "--list-tools"]:
        # List tools and exit (for debugging)
        async def list_and_exit() -> None:
            await initialize()
            tools = await list_tools()
            print(f"\n{len(tools)} tools available:\n")
            for tool in sorted(tools, key=lambda t: t.name):
                print(f"  - {tool.name}")
                print(f"    {tool.description}")
            await scm_client.close()

        asyncio.run(list_and_exit())
    else:
        # Run server
        asyncio.run(main())


if __name__ == "__main__":
    cli()
