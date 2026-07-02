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

    if required_container:
        # At least one of folder/snippet/device must be provided
        schema["oneOf"] = [
            {"required": ["folder"]},
            {"required": ["snippet"]},
            {"required": ["device"]},
        ]

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

    if required_container:
        # ID + one of folder/snippet/device
        schema["oneOf"] = [
            {"required": [id_param_name, "folder"]},
            {"required": [id_param_name, "snippet"]},
            {"required": [id_param_name, "device"]},
        ]

    return schema
