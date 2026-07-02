"""Base class for custom MCP tools (optional extensibility layer)."""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base class for custom MCP tools.

    Use this if you need custom logic beyond simple REST API calls.
    Most tools are automatically generated from OpenAPI specs and don't need this.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (e.g., 'scm_custom_operation')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable tool description."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema for tool input parameters."""
        pass

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute the tool with given arguments.

        Args:
            arguments: Tool arguments (validated against input_schema)

        Returns:
            Tool result as dictionary

        Raises:
            Exception: If tool execution fails
        """
        pass
