"""Shared JSON Schema definitions for tool input parameters.

Provides reusable schema components for common SCM API query parameters.
"""

from typing import Any

# Common query parameters for list operations
FOLDER_PARAM: dict[str, Any] = {
    "type": "string",
    "description": "Folder name (e.g., 'Shared', 'Mobile Users'). Required for most config operations.",
}

SNIPPET_PARAM: dict[str, Any] = {
    "type": "string",
    "description": "Snippet name. Alternative to folder for template-based configs.",
}

DEVICE_PARAM: dict[str, Any] = {
    "type": "string",
    "description": "Device name. Alternative to folder for device-specific configs.",
}

NAME_PARAM: dict[str, Any] = {
    "type": "string",
    "description": "Object name for filtering by exact match.",
}

LIMIT_PARAM: dict[str, Any] = {
    "type": "integer",
    "description": "Maximum number of results to return (default: 200, max: 10000).",
    "minimum": 1,
    "maximum": 10000,
}

OFFSET_PARAM: dict[str, Any] = {
    "type": "integer",
    "description": "Number of results to skip for pagination (default: 0).",
    "minimum": 0,
}

# Path parameters for get-by-ID operations
ID_PARAM: dict[str, Any] = {
    "type": "string",
    "description": "Unique identifier (UUID) of the resource.",
}

VERSION_PARAM: dict[str, Any] = {
    "type": "string",
    "description": "Configuration version identifier.",
}


def list_schema(
    *,
    required_container: bool = False,
    additional_params: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate input schema for list operations.

    Args:
        required_container: If True, at least one of folder/snippet/device is required.
            Validation is delegated to the SCM API.
        additional_params: Extra parameters to merge into properties.

    Returns:
        JSON Schema object with type="object".
    """
    properties: dict[str, Any] = {
        "folder": FOLDER_PARAM,
        "snippet": SNIPPET_PARAM,
        "device": DEVICE_PARAM,
        "name": NAME_PARAM,
        "limit": LIMIT_PARAM,
        "offset": OFFSET_PARAM,
    }

    if additional_params:
        properties.update(additional_params)

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }

    return schema


def get_by_id_schema(
    *,
    id_param_name: str = "id",
    required_container: bool = False,
    additional_params: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate input schema for get-by-ID operations.

    Args:
        id_param_name: Name of the ID parameter (default: "id", alternative: "version").
        required_container: If True, folder/snippet/device is required alongside ID.
            Validation is delegated to the SCM API.
        additional_params: Extra parameters to merge into properties.

    Returns:
        JSON Schema object with type="object".
    """
    id_schema = ID_PARAM if id_param_name == "id" else VERSION_PARAM

    properties: dict[str, Any] = {
        id_param_name: id_schema,
        "folder": FOLDER_PARAM,
        "snippet": SNIPPET_PARAM,
        "device": DEVICE_PARAM,
    }

    if additional_params:
        properties.update(additional_params)

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "required": [id_param_name],
    }

    return schema


def create_schema(*, has_container: bool = True) -> dict[str, Any]:
    """Generate input schema for create operations (POST)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "folder": FOLDER_PARAM,
            "snippet": SNIPPET_PARAM,
            "device": DEVICE_PARAM,
        },
        "additionalProperties": True,
    }
    return schema


def update_schema(*, has_container: bool = True) -> dict[str, Any]:
    """Generate input schema for update operations (PUT)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "id": ID_PARAM,
            "folder": FOLDER_PARAM,
            "snippet": SNIPPET_PARAM,
            "device": DEVICE_PARAM,
        },
        "required": ["id"],
        "additionalProperties": True,
    }
    return schema


def delete_schema(*, has_container: bool = True) -> dict[str, Any]:
    """Generate input schema for delete operations (DELETE)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "id": ID_PARAM,
            "folder": FOLDER_PARAM,
            "snippet": SNIPPET_PARAM,
            "device": DEVICE_PARAM,
        },
        "required": ["id"],
    }
    return schema


def move_schema() -> dict[str, Any]:
    """Generate input schema for move operations (rule reordering)."""
    return {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "UUID of the rule to move.",
            },
            "destination": {
                "type": "string",
                "enum": ["top", "bottom", "before", "after"],
                "description": "Where to move the rule.",
            },
            "rulebase": {
                "type": "string",
                "enum": ["pre", "post"],
                "description": "Which rulebase the rule belongs to.",
            },
            "destination_rule": {
                "type": "string",
                "description": "UUID of the pivot rule (required when destination is 'before' or 'after').",
            },
        },
        "required": ["id", "destination", "rulebase"],
    }


def push_schema() -> dict[str, Any]:
    """Generate input schema for push candidate config."""
    return {
        "type": "object",
        "properties": {
            "admin": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of administrators and/or service accounts.",
            },
            "description": {
                "type": "string",
                "description": "A description of the changes being pushed.",
            },
            "folder": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Target folders for the configuration push.",
            },
            "devices": {
                "type": "array",
                "items": {"type": "number"},
                "description": "Target device serial numbers for the configuration push.",
            },
        },
    }


def load_schema() -> dict[str, Any]:
    """Generate input schema for load config version."""
    return {
        "type": "object",
        "properties": {
            "version": {
                "type": "integer",
                "description": "Configuration version number to load as candidate.",
            },
        },
        "required": ["version"],
    }


def commit_schema() -> dict[str, Any]:
    """Generate input schema for commit config."""
    return {
        "type": "object",
        "properties": {},
    }
