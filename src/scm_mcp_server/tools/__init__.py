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
}


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
    else:
        raise NotImplementedError(
            f"Tool '{name}' not implemented. "
            "Available tools: see _LIST_TOOLS and _GET_BY_ID_TOOLS in tools/__init__.py"
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

    # Build query params (filter out None values)
    params = {key: arguments[key] for key in param_keys if key in arguments and arguments[key] is not None}

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
    params = {key: arguments[key] for key in query_param_keys if key in arguments and arguments[key] is not None}

    status, body = rest_client.request("GET", path, params=params)

    if 200 <= status < 300:
        return body  # type: ignore
    else:
        return {"error": f"API request failed with HTTP {status}", "status": status, "body": body}
