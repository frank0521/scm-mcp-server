"""OpenAPI specification parser for generating MCP tool definitions."""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """MCP tool definition generated from OpenAPI specification.

    Attributes:
        name: Tool name (e.g., "scm_iam_list_service_accounts")
        description: Human-readable description
        input_schema: JSON Schema for tool input parameters
        http_method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        path_template: API path template (e.g., "/iam/v1/service-accounts/{id}")
        response_schema: Expected response schema (optional)
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    http_method: str
    path_template: str
    response_schema: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class OpenAPIParser:
    """Parser for OpenAPI YAML specifications."""

    def __init__(self, base_dir: str = "../pan.dev/openapi-specs/scm") -> None:
        """Initialize parser.

        Args:
            base_dir: Base directory containing OpenAPI YAML files
        """
        self.base_dir = Path(base_dir).expanduser().resolve()
        if not self.base_dir.exists():
            raise FileNotFoundError(f"OpenAPI spec directory not found: {self.base_dir}")

    def parse_all_specs(self) -> list[ToolDefinition]:
        """Parse all OpenAPI specifications in base directory.

        Returns:
            List of tool definitions

        Raises:
            FileNotFoundError: If base directory doesn't exist
        """
        tools: list[ToolDefinition] = []
        yaml_files = list(self.base_dir.rglob("*.yaml")) + list(
            self.base_dir.rglob("*.yml")
        )

        logger.info(f"Found {len(yaml_files)} OpenAPI spec files")

        for yaml_file in yaml_files:
            try:
                file_tools = self.parse_spec_file(yaml_file)
                tools.extend(file_tools)
                logger.debug(f"Parsed {len(file_tools)} tools from {yaml_file.name}")
            except Exception as e:
                logger.error(f"Failed to parse {yaml_file}: {e}")
                # Continue parsing other files

        # Deduplicate by name (latest definition wins)
        unique_tools: dict[str, ToolDefinition] = {}
        for tool in tools:
            if tool.name in unique_tools:
                logger.warning(f"Duplicate tool name: {tool.name}, using latest definition")
            unique_tools[tool.name] = tool

        logger.info(f"Parsed {len(unique_tools)} unique tools from {len(yaml_files)} files")
        return list(unique_tools.values())

    def parse_spec_file(self, file_path: Path) -> list[ToolDefinition]:
        """Parse a single OpenAPI YAML file.

        Args:
            file_path: Path to OpenAPI YAML file

        Returns:
            List of tool definitions from this file
        """
        with open(file_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        if not isinstance(spec, dict) or "paths" not in spec:
            logger.warning(f"Invalid OpenAPI spec (missing 'paths'): {file_path}")
            return []

        tools: list[ToolDefinition] = []
        paths = spec.get("paths", {})

        # Determine module name from file path
        module_name = self._extract_module_name(file_path)

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    continue  # Skip non-HTTP method keys like "parameters"

                if not isinstance(operation, dict):
                    continue

                try:
                    tool = self._parse_operation(
                        path=path,
                        method=method.upper(),
                        operation=operation,
                        module_name=module_name,
                        spec=spec,
                    )
                    if tool:
                        tools.append(tool)
                except Exception as e:
                    logger.error(f"Failed to parse operation {method} {path}: {e}")

        return tools

    def _parse_operation(
        self,
        path: str,
        method: str,
        operation: dict[str, Any],
        module_name: str,
        spec: dict[str, Any],
    ) -> Optional[ToolDefinition]:
        """Parse a single operation into a tool definition.

        Args:
            path: API path (e.g., "/iam/v1/service-accounts")
            method: HTTP method (GET, POST, etc.)
            operation: OpenAPI operation object
            module_name: Module name (e.g., "iam", "sase")
            spec: Full OpenAPI specification (for resolving refs)

        Returns:
            ToolDefinition or None if parsing fails
        """
        # Generate tool name
        operation_id = operation.get("operationId")
        tool_name = self._generate_tool_name(path, method, operation_id, module_name)

        # Extract description
        description = operation.get("summary") or operation.get("description") or f"{method} {path}"

        # Build input schema from parameters and requestBody
        input_schema = self._build_input_schema(operation, spec)

        # Extract response schema (optional)
        response_schema = self._extract_response_schema(operation, spec)

        return ToolDefinition(
            name=tool_name,
            description=description,
            input_schema=input_schema,
            http_method=method,
            path_template=path,
            response_schema=response_schema,
            metadata={
                "operation_id": operation_id,
                "module": module_name,
            },
        )

    def _generate_tool_name(
        self, path: str, method: str, operation_id: Optional[str], module_name: str
    ) -> str:
        """Generate MCP tool name from operation.

        Format: scm_<module>_<action>_<resource>

        Args:
            path: API path
            method: HTTP method
            operation_id: OpenAPI operationId (if present)
            module_name: Module name (e.g., "iam")

        Returns:
            Tool name (e.g., "scm_iam_list_service_accounts")
        """
        if operation_id:
            # Clean operationId: convert hyphens to underscores, make lowercase
            clean_id = operation_id.lower().replace("-", "_")
            return f"scm_{clean_id}"

        # Derive from path and method
        # Example: GET /iam/v1/service-accounts -> scm_iam_list_service_accounts
        # Example: POST /config/security/v1/security-rules -> scm_sase_create_security_rule

        # Extract resource name from path (last segment)
        path_parts = [p for p in path.split("/") if p and not p.startswith("v")]
        if not path_parts:
            return f"scm_{module_name}_{method.lower()}"

        # Get resource name (last part, after version)
        resource = path_parts[-1]
        resource = resource.replace("-", "_")

        # Determine action from method
        action_map = {
            "GET": "list" if "{" not in path else "get",
            "POST": "create",
            "PUT": "update",
            "PATCH": "patch",
            "DELETE": "delete",
        }
        action = action_map.get(method, method.lower())

        return f"scm_{module_name}_{action}_{resource}"

    def _build_input_schema(
        self, operation: dict[str, Any], spec: dict[str, Any]
    ) -> dict[str, Any]:
        """Build JSON Schema for tool input from OpenAPI parameters and requestBody.

        Args:
            operation: OpenAPI operation object
            spec: Full OpenAPI specification (for resolving refs)

        Returns:
            JSON Schema dictionary
        """
        properties: dict[str, Any] = {}
        required: list[str] = []

        # Parse parameters (path, query, header)
        parameters = operation.get("parameters", [])
        for param in parameters:
            param_name = param.get("name")
            param_in = param.get("in")  # path, query, header
            param_schema = param.get("schema", {"type": "string"})
            param_required = param.get("required", False)
            param_desc = param.get("description", "")

            if param_name:
                properties[param_name] = {
                    **param_schema,
                    "description": param_desc,
                }
                if param_required:
                    required.append(param_name)

        # Parse requestBody
        request_body = operation.get("requestBody")
        if request_body:
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            body_schema = json_content.get("schema")

            if body_schema:
                # Resolve $ref if present
                resolved_schema = self._resolve_ref(body_schema, spec)

                # If schema has properties, merge them into input schema
                if "properties" in resolved_schema:
                    for prop_name, prop_schema in resolved_schema["properties"].items():
                        properties[prop_name] = prop_schema

                    # Add required fields from body schema
                    body_required = resolved_schema.get("required", [])
                    required.extend(body_required)
                else:
                    # Treat entire body as a single "body" parameter
                    properties["body"] = resolved_schema
                    if request_body.get("required", False):
                        required.append("body")

        # Build final schema
        schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema

    def _extract_response_schema(
        self, operation: dict[str, Any], spec: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Extract response schema from operation (optional).

        Args:
            operation: OpenAPI operation object
            spec: Full OpenAPI specification

        Returns:
            Response schema or None
        """
        responses = operation.get("responses", {})
        # Look for successful response (200, 201, etc.)
        for status_code in ["200", "201", "202"]:
            if status_code in responses:
                response = responses[status_code]
                content = response.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema")
                if schema:
                    return self._resolve_ref(schema, spec)

        return None

    def _resolve_ref(self, schema: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
        """Resolve JSON Schema $ref pointers.

        Args:
            schema: Schema object (may contain $ref)
            spec: Full OpenAPI specification

        Returns:
            Resolved schema
        """
        if not isinstance(schema, dict):
            return schema

        if "$ref" in schema:
            ref_path = schema["$ref"]
            # Example: "#/components/schemas/service_account"
            if ref_path.startswith("#/"):
                parts = ref_path[2:].split("/")
                resolved = spec
                for part in parts:
                    resolved = resolved.get(part, {})
                return self._resolve_ref(resolved, spec)  # Recursively resolve

        # Recursively resolve nested schemas
        resolved = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                resolved[key] = self._resolve_ref(value, spec)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_ref(item, spec) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                resolved[key] = value

        return resolved

    def _extract_module_name(self, file_path: Path) -> str:
        """Extract module name from file path.

        Args:
            file_path: Path to OpenAPI file

        Returns:
            Module name (e.g., "iam", "sase", "cloudngfw")
        """
        # Example: .../openapi-specs/scm/iam/ServiceAccounts.yaml -> "iam"
        # Example: .../openapi-specs/scm/config/sase/security/... -> "sase"

        relative_path = file_path.relative_to(self.base_dir)
        parts = relative_path.parts

        if not parts:
            return "unknown"

        # First level: auth, config, iam, subscription, tenancy
        first_level = parts[0]

        if first_level == "config" and len(parts) > 1:
            # Use second level: sase, cloudngfw, ngfw, etc.
            return parts[1]

        return first_level


def parse_all_specs(base_dir: str = "../pan.dev/openapi-specs/scm") -> list[ToolDefinition]:
    """Convenience function to parse all OpenAPI specs.

    Args:
        base_dir: Base directory containing OpenAPI YAML files

    Returns:
        List of tool definitions
    """
    parser = OpenAPIParser(base_dir)
    return parser.parse_all_specs()
