"""Tool dispatcher for MCP tools.

Implements table-driven routing for list and get-by-ID operations.
"""

from typing import Any

from .. import rest_client


# ============================================================================
# Routing Tables
# ============================================================================

# List operations: tool_name -> (path, tuple_of_query_param_keys)
_LIST_TOOLS: dict[str, tuple[str, tuple[str, ...]]] = {
    # Objects Core
    "list_addresses": ("/config/objects/v1/addresses", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_address_groups": ("/config/objects/v1/address-groups", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_services": ("/config/objects/v1/services", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_service_groups": ("/config/objects/v1/service-groups", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_tags": ("/config/objects/v1/tags", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_application_groups": ("/config/objects/v1/application-groups", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_external_dynamic_lists": ("/config/objects/v1/external-dynamic-lists", ("folder", "snippet", "device", "name", "limit", "offset")),
    # Security Rules
    "list_security_rules": ("/config/security/v1/security-rules", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_decryption_rules": ("/config/security/v1/decryption-rules", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_app_override_rules": ("/config/security/v1/app-override-rules", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_dos_protection_rules": ("/config/security/v1/dos-protection-rules", ("folder", "snippet", "device", "name", "limit", "offset")),
    # Security Profiles (Read-Only)
    "list_anti_spyware_profiles": ("/config/security/v1/anti-spyware-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_vulnerability_protection_profiles": ("/config/security/v1/vulnerability-protection-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_url_filtering_profiles": ("/config/security/v1/url-filtering-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_file_blocking_profiles": ("/config/security/v1/file-blocking-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_wildfire_anti_virus_profiles": ("/config/security/v1/wildfire-anti-virus-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_dns_security_profiles": ("/config/security/v1/dns-security-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_dos_protection_profiles": ("/config/security/v1/dos-protection-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_security_profile_groups": ("/config/security/v1/profile-groups", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_decryption_profiles": ("/config/security/v1/decryption-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    "list_zone_protection_profiles": ("/config/security/v1/zone-protection-profiles", ("folder", "snippet", "device", "name", "limit", "offset")),
    # Operations
    "list_jobs": ("/config/operations/v1/jobs", ("limit", "offset")),
    "list_config_versions": ("/config/operations/v1/config-versions", ("limit", "offset")),
    "get_running_config": ("/config/operations/v1/running-config", ()),
    # IAM
    "list_service_accounts": ("/iam/v1/service-accounts", ("limit", "offset")),
    "list_roles": ("/iam/v1/roles", ("limit", "offset")),
    "list_access_policies": ("/iam/v1/access-policies", ("limit", "offset")),
}

# Get-by-ID operations: tool_name -> (path_template, tuple_of_param_keys)
# path_template uses {id} or {version} as placeholder
# param_keys include the path param (id/version) + optional query params (folder/snippet/device)
_GET_BY_ID_TOOLS: dict[str, tuple[str, tuple[str, ...]]] = {
    # Objects Core
    "get_address": ("/config/objects/v1/addresses/{id}", ("id", "folder", "snippet", "device")),
    "get_address_group": ("/config/objects/v1/address-groups/{id}", ("id", "folder", "snippet", "device")),
    "get_service": ("/config/objects/v1/services/{id}", ("id", "folder", "snippet", "device")),
    "get_service_group": ("/config/objects/v1/service-groups/{id}", ("id", "folder", "snippet", "device")),
    "get_tag": ("/config/objects/v1/tags/{id}", ("id", "folder", "snippet", "device")),
    "get_application_group": ("/config/objects/v1/application-groups/{id}", ("id", "folder", "snippet", "device")),
    "get_external_dynamic_list": ("/config/objects/v1/external-dynamic-lists/{id}", ("id", "folder", "snippet", "device")),
    # Security Rules
    "get_security_rule": ("/config/security/v1/security-rules/{id}", ("id", "folder", "snippet", "device")),
    "get_decryption_rule": ("/config/security/v1/decryption-rules/{id}", ("id", "folder", "snippet", "device")),
    "get_app_override_rule": ("/config/security/v1/app-override-rules/{id}", ("id", "folder", "snippet", "device")),
    "get_dos_protection_rule": ("/config/security/v1/dos-protection-rules/{id}", ("id", "folder", "snippet", "device")),
    # Security Profiles (Read-Only)
    "get_anti_spyware_profile": ("/config/security/v1/anti-spyware-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_vulnerability_protection_profile": ("/config/security/v1/vulnerability-protection-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_url_filtering_profile": ("/config/security/v1/url-filtering-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_file_blocking_profile": ("/config/security/v1/file-blocking-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_wildfire_anti_virus_profile": ("/config/security/v1/wildfire-anti-virus-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_dns_security_profile": ("/config/security/v1/dns-security-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_dos_protection_profile": ("/config/security/v1/dos-protection-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_security_profile_group": ("/config/security/v1/profile-groups/{id}", ("id", "folder", "snippet", "device")),
    "get_decryption_profile": ("/config/security/v1/decryption-profiles/{id}", ("id", "folder", "snippet", "device")),
    "get_zone_protection_profile": ("/config/security/v1/zone-protection-profiles/{id}", ("id", "folder", "snippet", "device")),
    # Operations
    "get_job": ("/config/operations/v1/jobs/{id}", ("id",)),
    "get_config_version": ("/config/operations/v1/config-versions/{version}", ("version",)),
    # IAM
    "get_service_account": ("/iam/v1/service-accounts/{id}", ("id",)),
    "get_role": ("/iam/v1/roles/{id}", ("id",)),
}

# Create operations: tool_name -> (path, tuple_of_body_param_keys, tuple_of_query_param_keys)
_CREATE_TOOLS: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    # Objects Core
    "create_address": ("/config/objects/v1/addresses", (), ("folder", "snippet", "device")),
    "create_address_group": ("/config/objects/v1/address-groups", (), ("folder", "snippet", "device")),
    "create_service": ("/config/objects/v1/services", (), ("folder", "snippet", "device")),
    "create_service_group": ("/config/objects/v1/service-groups", (), ("folder", "snippet", "device")),
    "create_tag": ("/config/objects/v1/tags", (), ("folder", "snippet", "device")),
    "create_application_group": ("/config/objects/v1/application-groups", (), ("folder", "snippet", "device")),
    "create_external_dynamic_list": ("/config/objects/v1/external-dynamic-lists", (), ("folder", "snippet", "device")),
    # Security Rules
    "create_security_rule": ("/config/security/v1/security-rules", (), ("folder", "snippet", "device")),
    "create_decryption_rule": ("/config/security/v1/decryption-rules", (), ("folder", "snippet", "device")),
    "create_app_override_rule": ("/config/security/v1/app-override-rules", (), ("folder", "snippet", "device")),
    "create_dos_protection_rule": ("/config/security/v1/dos-protection-rules", (), ("folder", "snippet", "device")),
    # IAM
    "create_service_account": ("/iam/v1/service-accounts", (), ()),
    "create_role": ("/iam/v1/roles", (), ()),
    "create_access_policy": ("/iam/v1/access-policies", (), ()),
}

# Update operations: tool_name -> (path_template, tuple_of_body_param_keys, tuple_of_query_param_keys)
_UPDATE_TOOLS: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    # Objects Core
    "update_address": ("/config/objects/v1/addresses/{id}", ("id",), ("folder", "snippet", "device")),
    "update_address_group": ("/config/objects/v1/address-groups/{id}", ("id",), ("folder", "snippet", "device")),
    "update_service": ("/config/objects/v1/services/{id}", ("id",), ("folder", "snippet", "device")),
    "update_service_group": ("/config/objects/v1/service-groups/{id}", ("id",), ("folder", "snippet", "device")),
    "update_tag": ("/config/objects/v1/tags/{id}", ("id",), ("folder", "snippet", "device")),
    "update_application_group": ("/config/objects/v1/application-groups/{id}", ("id",), ("folder", "snippet", "device")),
    "update_external_dynamic_list": ("/config/objects/v1/external-dynamic-lists/{id}", ("id",), ("folder", "snippet", "device")),
    # Security Rules
    "update_security_rule": ("/config/security/v1/security-rules/{id}", ("id",), ("folder", "snippet", "device")),
    "update_decryption_rule": ("/config/security/v1/decryption-rules/{id}", ("id",), ("folder", "snippet", "device")),
    "update_app_override_rule": ("/config/security/v1/app-override-rules/{id}", ("id",), ("folder", "snippet", "device")),
    "update_dos_protection_rule": ("/config/security/v1/dos-protection-rules/{id}", ("id",), ("folder", "snippet", "device")),
    # IAM
    "update_service_account": ("/iam/v1/service-accounts/{id}", ("id",), ()),
}

# Delete operations: tool_name -> (path_template, tuple_of_path_param_keys, tuple_of_query_param_keys)
_DELETE_TOOLS: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    # Objects Core
    "delete_address": ("/config/objects/v1/addresses/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_address_group": ("/config/objects/v1/address-groups/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_service": ("/config/objects/v1/services/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_service_group": ("/config/objects/v1/service-groups/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_tag": ("/config/objects/v1/tags/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_application_group": ("/config/objects/v1/application-groups/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_external_dynamic_list": ("/config/objects/v1/external-dynamic-lists/{id}", ("id",), ("folder", "snippet", "device")),
    # Security Rules
    "delete_security_rule": ("/config/security/v1/security-rules/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_decryption_rule": ("/config/security/v1/decryption-rules/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_app_override_rule": ("/config/security/v1/app-override-rules/{id}", ("id",), ("folder", "snippet", "device")),
    "delete_dos_protection_rule": ("/config/security/v1/dos-protection-rules/{id}", ("id",), ("folder", "snippet", "device")),
    # IAM
    "delete_service_account": ("/iam/v1/service-accounts/{id}", ("id",), ()),
    "delete_role": ("/iam/v1/roles/{id}", ("id",), ()),
    "delete_access_policy": ("/iam/v1/access-policies/{id}", ("id",), ()),
}

# Move operations (special case for rules): tool_name -> (path_template, tuple_of_path_param_keys)
_MOVE_TOOLS: dict[str, tuple[str, tuple[str, ...]]] = {
    "move_security_rule": ("/config/security/v1/security-rules/{id}:move", ("id",)),
    "move_decryption_rule": ("/config/security/v1/decryption-rules/{id}:move", ("id",)),
    "move_app_override_rule": ("/config/security/v1/app-override-rules/{id}:move", ("id",)),
}


# ============================================================================
# Helper Functions
# ============================================================================

def _pick(data: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    """Extract subset of keys from data, filtering out None values.

    Args:
        data: Source dictionary
        keys: Keys to extract

    Returns:
        Dictionary with only specified keys (non-None values).
    """
    return {key: data[key] for key in keys if key in data and data[key] is not None}


# ============================================================================
# Dispatcher
# ============================================================================

def call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Dispatch tool call to appropriate handler.

    Args:
        name: Tool name (e.g., "list_addresses", "get_address")
        arguments: Tool input arguments

    Returns:
        Tool execution result as dictionary.
        On success: API response body (dict or list)
        On error: {"error": str, "status": int, "body": Any}

    Raises:
        NotImplementedError: If tool name is not in routing tables.
    """
    if name in _LIST_TOOLS:
        return _handle_list(name, arguments)
    elif name in _GET_BY_ID_TOOLS:
        return _handle_get_by_id(name, arguments)
    elif name in _CREATE_TOOLS:
        return _handle_create(name, arguments)
    elif name in _UPDATE_TOOLS:
        return _handle_update(name, arguments)
    elif name in _DELETE_TOOLS:
        return _handle_delete(name, arguments)
    elif name in _MOVE_TOOLS:
        return _handle_move(name, arguments)
    else:
        raise NotImplementedError(
            f"Tool '{name}' not implemented. "
            "Available tools: see routing tables in tools/__init__.py"
        )


def _handle_list(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle list operations.

    Args:
        name: Tool name from _LIST_TOOLS
        arguments: Query parameters (folder, limit, offset, etc.)

    Returns:
        API response or error dict.
    """
    path, param_keys = _LIST_TOOLS[name]

    # Build query params
    params = _pick(arguments, param_keys)

    status, body = rest_client.request("GET", path, params=params)

    if 200 <= status < 300:
        return body  # type: ignore
    else:
        return {"error": f"API request failed with HTTP {status}", "status": status, "body": body}


def _handle_get_by_id(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle get-by-ID operations.

    Args:
        name: Tool name from _GET_BY_ID_TOOLS
        arguments: Must include 'id' or 'version', optional folder/snippet/device

    Returns:
        API response or error dict.
    """
    path_template, param_keys = _GET_BY_ID_TOOLS[name]

    # Extract path parameter (first in param_keys, e.g., "id" or "version")
    path_param_name = param_keys[0]
    if path_param_name not in arguments:
        return {
            "error": f"Missing required parameter: {path_param_name}",
            "status": 400,
            "body": None,
        }

    path_param_value = arguments[path_param_name]
    # Replace {id} or {version} in template
    path = path_template.replace(f"{{{path_param_name}}}", str(path_param_value))

    # Build query params (remaining keys after path param)
    query_param_keys = param_keys[1:]
    params = _pick(arguments, query_param_keys)

    status, body = rest_client.request("GET", path, params=params)

    if 200 <= status < 300:
        return body  # type: ignore
    else:
        return {"error": f"API request failed with HTTP {status}", "status": status, "body": body}


def _handle_create(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle create operations (POST).

    Args:
        name: Tool name from _CREATE_TOOLS
        arguments: Request body data + optional query params (folder/snippet/device)

    Returns:
        API response or error dict.
    """
    path, body_param_keys, query_param_keys = _CREATE_TOOLS[name]

    # Build query params
    params = _pick(arguments, query_param_keys)

    # Build request body (everything except query params)
    reserved_keys = set(query_param_keys)
    body = {key: value for key, value in arguments.items() if key not in reserved_keys and value is not None}

    status, response = rest_client.request("POST", path, params=params, json=body)

    if 200 <= status < 300:
        return response  # type: ignore
    else:
        return {"error": f"API request failed with HTTP {status}", "status": status, "body": response}


def _handle_update(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle update operations (PUT).

    Args:
        name: Tool name from _UPDATE_TOOLS
        arguments: Must include path param (e.g., 'id') + body data + optional query params

    Returns:
        API response or error dict.
    """
    path_template, path_param_keys, query_param_keys = _UPDATE_TOOLS[name]

    # Extract path parameter (first in path_param_keys)
    path_param_name = path_param_keys[0]
    if path_param_name not in arguments:
        return {
            "error": f"Missing required parameter: {path_param_name}",
            "status": 400,
            "body": None,
        }

    path_param_value = arguments[path_param_name]
    path = path_template.replace(f"{{{path_param_name}}}", str(path_param_value))

    # Build query params
    params = _pick(arguments, query_param_keys)

    # Build request body (everything except path param and query params)
    reserved_keys = set(path_param_keys) | set(query_param_keys)
    body = {key: value for key, value in arguments.items() if key not in reserved_keys and value is not None}

    status, response = rest_client.request("PUT", path, params=params, json=body)

    if 200 <= status < 300:
        return response  # type: ignore
    else:
        return {"error": f"API request failed with HTTP {status}", "status": status, "body": response}


def _handle_delete(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle delete operations (DELETE).

    Args:
        name: Tool name from _DELETE_TOOLS
        arguments: Must include path param (e.g., 'id') + optional query params

    Returns:
        API response or error dict.
    """
    path_template, path_param_keys, query_param_keys = _DELETE_TOOLS[name]

    # Extract path parameter (first in path_param_keys)
    path_param_name = path_param_keys[0]
    if path_param_name not in arguments:
        return {
            "error": f"Missing required parameter: {path_param_name}",
            "status": 400,
            "body": None,
        }

    path_param_value = arguments[path_param_name]
    path = path_template.replace(f"{{{path_param_name}}}", str(path_param_value))

    # Build query params
    params = _pick(arguments, query_param_keys)

    status, response = rest_client.request("DELETE", path, params=params)

    if 200 <= status < 300:
        return response  # type: ignore
    else:
        return {"error": f"API request failed with HTTP {status}", "status": status, "body": response}


def _handle_move(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle move operations (POST with :move action).

    Args:
        name: Tool name from _MOVE_TOOLS
        arguments: Must include 'id' + move directive (e.g., 'destination', 'where')

    Returns:
        API response or error dict.
    """
    path_template, path_param_keys = _MOVE_TOOLS[name]

    # Extract path parameter
    path_param_name = path_param_keys[0]
    if path_param_name not in arguments:
        return {
            "error": f"Missing required parameter: {path_param_name}",
            "status": 400,
            "body": None,
        }

    path_param_value = arguments[path_param_name]
    path = path_template.replace(f"{{{path_param_name}}}", str(path_param_value))

    # Build request body (everything except path param)
    reserved_keys = set(path_param_keys)
    body = {key: value for key, value in arguments.items() if key not in reserved_keys and value is not None}

    status, response = rest_client.request("POST", path, params={}, json=body)

    if 200 <= status < 300:
        return response  # type: ignore
    else:
        return {"error": f"API request failed with HTTP {status}", "status": status, "body": response}
