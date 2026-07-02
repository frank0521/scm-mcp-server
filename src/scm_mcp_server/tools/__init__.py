"""Tool dispatcher for MCP tools.

TODO: Phase 1 - Implement tool registry and dispatch logic.
Current: Placeholder that raises NotImplementedError.
"""


def call(name: str, arguments: dict) -> dict:
    """Dispatch tool call to appropriate handler.

    Args:
        name: Tool name (e.g., "scm_iam_list_service_accounts")
        arguments: Tool input arguments (validated by MCP SDK)

    Returns:
        Tool execution result as dictionary.

    Raises:
        NotImplementedError: No tools implemented yet (Phase 1 TODO).
    """
    # TODO: Phase 1 - Implement tool registry
    # tool_registry = {
    #     "scm_iam_list_service_accounts": iam_tools.list_service_accounts,
    #     ...
    # }
    # if name not in tool_registry:
    #     raise ValueError(f"Unknown tool: {name}")
    # return tool_registry[name](**arguments)

    raise NotImplementedError(
        f"Tool '{name}' not implemented. "
        "Tool registry is TBD (see WORKFLOW.md Phase 1)."
    )
