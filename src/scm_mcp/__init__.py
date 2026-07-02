"""SCM MCP Server - Model Context Protocol server for Palo Alto Networks Strata Cloud Manager."""

__version__ = "0.1.0"
__author__ = "Frank Fan"
__license__ = "MIT"

from .auth import OAuth2Manager
from .client import SCMClient
from .openapi_parser import ToolDefinition, parse_all_specs

__all__ = [
    "OAuth2Manager",
    "SCMClient",
    "ToolDefinition",
    "parse_all_specs",
]
