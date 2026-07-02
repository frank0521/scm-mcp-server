"""Unit tests for tool dispatch and execution.

Tests verify:
- Tool routing (list vs get-by-ID)
- Request construction (path, params)
- Response handling (success vs error)
"""

import pytest
from unittest.mock import Mock, patch

from scm_mcp_server.tools import call


@pytest.fixture
def mock_rest_client():
    """Mock rest_client.request for isolated testing."""
    with patch("scm_mcp_server.rest_client.request") as mock:
        yield mock


class TestToolScaffold:
    """Verify test infrastructure is working."""

    def test_pytest_working(self):
        """Sanity check: pytest can run."""
        assert True

    def test_mock_fixture_available(self, mock_rest_client):
        """Verify mock fixture is injectable."""
        assert mock_rest_client is not None


class TestToolDispatch:
    """Test tool routing and dispatch logic."""

    def test_unknown_tool_raises_not_implemented(self):
        """Unknown tool names should raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Tool 'unknown_tool' not implemented"):
            call("unknown_tool", {})


class TestObjectsCoreTools:
    """Test Objects Core read-only tools (14 tools)."""

    # ========================================================================
    # List operations (7 tools)
    # ========================================================================

    def test_list_addresses_success(self, mock_rest_client):
        """list_addresses: success case."""
        mock_rest_client.return_value = (200, {"data": [{"id": "addr-1", "name": "test"}], "total": 1})

        result = call("list_addresses", {"folder": "Shared", "limit": 10})

        mock_rest_client.assert_called_once_with("GET", "/config/objects/v1/addresses", params={"folder": "Shared", "limit": 10})
        assert result == {"data": [{"id": "addr-1", "name": "test"}], "total": 1}

    def test_list_addresses_error(self, mock_rest_client):
        """list_addresses: non-2xx response."""
        mock_rest_client.return_value = (404, {"message": "Not found"})

        result = call("list_addresses", {"folder": "Invalid"})

        assert result["error"] == "API request failed with HTTP 404"
        assert result["status"] == 404
        assert result["body"] == {"message": "Not found"}

    def test_list_address_groups(self, mock_rest_client):
        """list_address_groups: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_address_groups", {"folder": "Shared"})
        assert "data" in result

    def test_list_services(self, mock_rest_client):
        """list_services: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_services", {"folder": "Shared"})
        assert "data" in result

    def test_list_service_groups(self, mock_rest_client):
        """list_service_groups: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_service_groups", {"folder": "Shared"})
        assert "data" in result

    def test_list_tags(self, mock_rest_client):
        """list_tags: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_tags", {"folder": "Shared"})
        assert "data" in result

    def test_list_application_groups(self, mock_rest_client):
        """list_application_groups: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_application_groups", {"folder": "Shared"})
        assert "data" in result

    def test_list_external_dynamic_lists(self, mock_rest_client):
        """list_external_dynamic_lists: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_external_dynamic_lists", {"folder": "Shared"})
        assert "data" in result

    # ========================================================================
    # Get-by-ID operations (7 tools)
    # ========================================================================

    def test_get_address_success(self, mock_rest_client):
        """get_address: success case."""
        mock_rest_client.return_value = (200, {"id": "addr-123", "name": "test-addr"})

        result = call("get_address", {"id": "addr-123", "folder": "Shared"})

        mock_rest_client.assert_called_once_with("GET", "/config/objects/v1/addresses/addr-123", params={"folder": "Shared"})
        assert result == {"id": "addr-123", "name": "test-addr"}

    def test_get_address_missing_id(self, mock_rest_client):
        """get_address: missing required 'id' parameter."""
        result = call("get_address", {"folder": "Shared"})

        assert result["error"] == "Missing required parameter: id"
        assert result["status"] == 400
        mock_rest_client.assert_not_called()

    def test_get_address_error(self, mock_rest_client):
        """get_address: non-2xx response."""
        mock_rest_client.return_value = (404, {"message": "Address not found"})

        result = call("get_address", {"id": "invalid-id"})

        assert result["error"] == "API request failed with HTTP 404"
        assert result["status"] == 404

    def test_get_address_group(self, mock_rest_client):
        """get_address_group: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "ag-1"})
        result = call("get_address_group", {"id": "ag-1"})
        assert result["id"] == "ag-1"

    def test_get_service(self, mock_rest_client):
        """get_service: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "svc-1"})
        result = call("get_service", {"id": "svc-1"})
        assert result["id"] == "svc-1"

    def test_get_service_group(self, mock_rest_client):
        """get_service_group: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "sg-1"})
        result = call("get_service_group", {"id": "sg-1"})
        assert result["id"] == "sg-1"

    def test_get_tag(self, mock_rest_client):
        """get_tag: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "tag-1"})
        result = call("get_tag", {"id": "tag-1"})
        assert result["id"] == "tag-1"

    def test_get_application_group(self, mock_rest_client):
        """get_application_group: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "apg-1"})
        result = call("get_application_group", {"id": "apg-1"})
        assert result["id"] == "apg-1"

    def test_get_external_dynamic_list(self, mock_rest_client):
        """get_external_dynamic_list: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "edl-1"})
        result = call("get_external_dynamic_list", {"id": "edl-1"})
        assert result["id"] == "edl-1"


class TestSecurityRulesTools:
    """Test Security Rules read-only tools (8 tools)."""

    # ========================================================================
    # List operations (4 tools)
    # ========================================================================

    def test_list_security_rules_success(self, mock_rest_client):
        """list_security_rules: success case."""
        mock_rest_client.return_value = (200, {"data": [{"id": "rule-1", "name": "allow-web"}], "total": 1})

        result = call("list_security_rules", {"folder": "Shared", "limit": 50})

        mock_rest_client.assert_called_once_with("GET", "/config/security/v1/security-rules", params={"folder": "Shared", "limit": 50})
        assert result["total"] == 1

    def test_list_decryption_rules(self, mock_rest_client):
        """list_decryption_rules: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_decryption_rules", {"folder": "Shared"})
        assert "data" in result

    def test_list_app_override_rules(self, mock_rest_client):
        """list_app_override_rules: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_app_override_rules", {"folder": "Shared"})
        assert "data" in result

    def test_list_dos_protection_rules(self, mock_rest_client):
        """list_dos_protection_rules: basic smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_dos_protection_rules", {"folder": "Shared"})
        assert "data" in result

    # ========================================================================
    # Get-by-ID operations (4 tools)
    # ========================================================================

    def test_get_security_rule_success(self, mock_rest_client):
        """get_security_rule: success case."""
        mock_rest_client.return_value = (200, {"id": "rule-123", "name": "allow-ssh", "action": "allow"})

        result = call("get_security_rule", {"id": "rule-123", "folder": "Shared"})

        mock_rest_client.assert_called_once_with("GET", "/config/security/v1/security-rules/rule-123", params={"folder": "Shared"})
        assert result["action"] == "allow"

    def test_get_decryption_rule(self, mock_rest_client):
        """get_decryption_rule: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "dec-1"})
        result = call("get_decryption_rule", {"id": "dec-1"})
        assert result["id"] == "dec-1"

    def test_get_app_override_rule(self, mock_rest_client):
        """get_app_override_rule: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "ao-1"})
        result = call("get_app_override_rule", {"id": "ao-1"})
        assert result["id"] == "ao-1"

    def test_get_dos_protection_rule(self, mock_rest_client):
        """get_dos_protection_rule: basic smoke test."""
        mock_rest_client.return_value = (200, {"id": "dos-1"})
        result = call("get_dos_protection_rule", {"id": "dos-1"})
        assert result["id"] == "dos-1"
