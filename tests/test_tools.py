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


class TestSecurityProfilesTools:
    """Test Security Profiles read-only tools (20 tools = 10 types × 2 operations)."""

    # Test one representative sample per profile type (smoke tests for brevity)

    def test_list_anti_spyware_profiles(self, mock_rest_client):
        """list_anti_spyware_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_anti_spyware_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_anti_spyware_profile(self, mock_rest_client):
        """get_anti_spyware_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "asp-1"})
        result = call("get_anti_spyware_profile", {"id": "asp-1"})
        assert result["id"] == "asp-1"

    def test_list_vulnerability_protection_profiles(self, mock_rest_client):
        """list_vulnerability_protection_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_vulnerability_protection_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_vulnerability_protection_profile(self, mock_rest_client):
        """get_vulnerability_protection_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "vpp-1"})
        result = call("get_vulnerability_protection_profile", {"id": "vpp-1"})
        assert result["id"] == "vpp-1"

    def test_list_url_filtering_profiles(self, mock_rest_client):
        """list_url_filtering_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_url_filtering_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_url_filtering_profile(self, mock_rest_client):
        """get_url_filtering_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "ufp-1"})
        result = call("get_url_filtering_profile", {"id": "ufp-1"})
        assert result["id"] == "ufp-1"

    def test_list_file_blocking_profiles(self, mock_rest_client):
        """list_file_blocking_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_file_blocking_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_file_blocking_profile(self, mock_rest_client):
        """get_file_blocking_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "fbp-1"})
        result = call("get_file_blocking_profile", {"id": "fbp-1"})
        assert result["id"] == "fbp-1"

    def test_list_wildfire_anti_virus_profiles(self, mock_rest_client):
        """list_wildfire_anti_virus_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_wildfire_anti_virus_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_wildfire_anti_virus_profile(self, mock_rest_client):
        """get_wildfire_anti_virus_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "wfav-1"})
        result = call("get_wildfire_anti_virus_profile", {"id": "wfav-1"})
        assert result["id"] == "wfav-1"

    def test_list_dns_security_profiles(self, mock_rest_client):
        """list_dns_security_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_dns_security_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_dns_security_profile(self, mock_rest_client):
        """get_dns_security_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "dsp-1"})
        result = call("get_dns_security_profile", {"id": "dsp-1"})
        assert result["id"] == "dsp-1"

    def test_list_dos_protection_profiles(self, mock_rest_client):
        """list_dos_protection_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_dos_protection_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_dos_protection_profile(self, mock_rest_client):
        """get_dos_protection_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "dpp-1"})
        result = call("get_dos_protection_profile", {"id": "dpp-1"})
        assert result["id"] == "dpp-1"

    def test_list_security_profile_groups(self, mock_rest_client):
        """list_security_profile_groups: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_security_profile_groups", {"folder": "Shared"})
        assert "data" in result

    def test_get_security_profile_group(self, mock_rest_client):
        """get_security_profile_group: smoke test."""
        mock_rest_client.return_value = (200, {"id": "spg-1"})
        result = call("get_security_profile_group", {"id": "spg-1"})
        assert result["id"] == "spg-1"

    def test_list_decryption_profiles(self, mock_rest_client):
        """list_decryption_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_decryption_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_decryption_profile(self, mock_rest_client):
        """get_decryption_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "dp-1"})
        result = call("get_decryption_profile", {"id": "dp-1"})
        assert result["id"] == "dp-1"

    def test_list_zone_protection_profiles(self, mock_rest_client):
        """list_zone_protection_profiles: smoke test."""
        mock_rest_client.return_value = (200, {"data": []})
        result = call("list_zone_protection_profiles", {"folder": "Shared"})
        assert "data" in result

    def test_get_zone_protection_profile(self, mock_rest_client):
        """get_zone_protection_profile: smoke test."""
        mock_rest_client.return_value = (200, {"id": "zpp-1"})
        result = call("get_zone_protection_profile", {"id": "zpp-1"})
        assert result["id"] == "zpp-1"


class TestOperationsTools:
    """Test Operations read-only tools (5 tools)."""

    def test_list_jobs_success(self, mock_rest_client):
        """list_jobs: success case."""
        mock_rest_client.return_value = (200, {"data": [{"id": "job-1", "status": "completed"}], "total": 1})

        result = call("list_jobs", {"limit": 20})

        mock_rest_client.assert_called_once_with("GET", "/config/operations/v1/jobs", params={"limit": 20})
        assert result["total"] == 1

    def test_get_job_success(self, mock_rest_client):
        """get_job: success case."""
        mock_rest_client.return_value = (200, {"id": "job-123", "status": "pending"})

        result = call("get_job", {"id": "job-123"})

        mock_rest_client.assert_called_once_with("GET", "/config/operations/v1/jobs/job-123", params={})
        assert result["status"] == "pending"

    def test_list_config_versions(self, mock_rest_client):
        """list_config_versions: smoke test."""
        mock_rest_client.return_value = (200, {"data": [{"version": "v1"}]})
        result = call("list_config_versions", {"limit": 10})
        assert "data" in result

    def test_get_config_version_success(self, mock_rest_client):
        """get_config_version: success with 'version' path param."""
        mock_rest_client.return_value = (200, {"version": "v42", "timestamp": "2026-07-02T00:00:00Z"})

        result = call("get_config_version", {"version": "v42"})

        mock_rest_client.assert_called_once_with("GET", "/config/operations/v1/config-versions/v42", params={})
        assert result["version"] == "v42"

    def test_get_running_config_success(self, mock_rest_client):
        """get_running_config: no path params, only query params."""
        mock_rest_client.return_value = (200, {"config": {...}})

        result = call("get_running_config", {})

        mock_rest_client.assert_called_once_with("GET", "/config/operations/v1/running-config", params={})
        assert "config" in result


class TestIAMTools:
    """Test IAM read-only tools (5 tools)."""

    def test_list_service_accounts_success(self, mock_rest_client):
        """list_service_accounts: success case."""
        mock_rest_client.return_value = (200, {"data": [{"id": "sa-1", "name": "test-sa"}], "total": 1})

        result = call("list_service_accounts", {"limit": 50, "offset": 0})

        mock_rest_client.assert_called_once_with("GET", "/iam/v1/service-accounts", params={"limit": 50, "offset": 0})
        assert result["total"] == 1

    def test_get_service_account_success(self, mock_rest_client):
        """get_service_account: success case."""
        mock_rest_client.return_value = (200, {"id": "sa-123", "name": "prod-sa"})

        result = call("get_service_account", {"id": "sa-123"})

        mock_rest_client.assert_called_once_with("GET", "/iam/v1/service-accounts/sa-123", params={})
        assert result["name"] == "prod-sa"

    def test_list_roles(self, mock_rest_client):
        """list_roles: smoke test."""
        mock_rest_client.return_value = (200, {"data": [{"id": "role-1"}]})
        result = call("list_roles", {})
        assert "data" in result

    def test_get_role(self, mock_rest_client):
        """get_role: smoke test."""
        mock_rest_client.return_value = (200, {"id": "role-42"})
        result = call("get_role", {"id": "role-42"})
        assert result["id"] == "role-42"

    def test_list_access_policies(self, mock_rest_client):
        """list_access_policies: smoke test (no get operation)."""
        mock_rest_client.return_value = (200, {"data": [{"id": "policy-1"}]})
        result = call("list_access_policies", {"limit": 100})
        assert "data" in result


class TestMCPServerIntegration:
    """Test MCP server integration with tool registry."""

    def test_list_tools_count(self):
        """list_tools() should return 52 tools."""
        from scm_mcp_server.server import list_tools
        import asyncio

        tools = asyncio.run(list_tools())
        assert len(tools) == 52, f"Expected 52 tools, got {len(tools)}"

    def test_list_tools_structure(self):
        """Verify Tool objects have correct structure."""
        from scm_mcp_server.server import list_tools
        import asyncio

        tools = asyncio.run(list_tools())
        sample_tool = tools[0]

        assert hasattr(sample_tool, "name")
        assert hasattr(sample_tool, "description")
        assert hasattr(sample_tool, "inputSchema")
        assert sample_tool.inputSchema["type"] == "object"
        assert "properties" in sample_tool.inputSchema

    def test_list_tools_coverage(self):
        """Verify all implemented tools appear in list_tools()."""
        from scm_mcp_server.server import list_tools
        from scm_mcp_server.tools import _LIST_TOOLS, _GET_BY_ID_TOOLS
        import asyncio

        tools = asyncio.run(list_tools())
        tool_names = {t.name for t in tools}

        # All list tools should be present
        for name in _LIST_TOOLS.keys():
            assert name in tool_names, f"Missing list tool: {name}"

        # All get-by-ID tools should be present
        for name in _GET_BY_ID_TOOLS.keys():
            assert name in tool_names, f"Missing get-by-ID tool: {name}"
