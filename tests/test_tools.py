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


class TestMoveOperations:
    """Test move operations with body_keys-based routing."""

    def test_move_security_rule_success(self, mock_rest_client):
        """move_security_rule: POST with correct path and body fields."""
        mock_rest_client.return_value = (200, {"id": "rule-1"})

        result = call("move_security_rule", {
            "id": "rule-1",
            "destination": "before",
            "rulebase": "pre",
            "destination_rule": "rule-2",
        })

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/security/v1/security-rules/rule-1:move",
            params={},
            json={"destination": "before", "rulebase": "pre", "destination_rule": "rule-2"},
        )
        assert result["id"] == "rule-1"

    def test_move_security_rule_top(self, mock_rest_client):
        """move_security_rule: destination=top, no destination_rule needed."""
        mock_rest_client.return_value = (200, {"id": "rule-1"})

        result = call("move_security_rule", {
            "id": "rule-1",
            "destination": "top",
            "rulebase": "pre",
        })

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/security/v1/security-rules/rule-1:move",
            params={},
            json={"destination": "top", "rulebase": "pre"},
        )

    def test_move_security_rule_missing_id(self, mock_rest_client):
        """move_security_rule: missing id returns 400."""
        result = call("move_security_rule", {"destination": "top", "rulebase": "pre"})

        assert result["error"] == "Missing required parameter: id"
        assert result["status"] == 400
        mock_rest_client.assert_not_called()

    def test_move_decryption_rule_success(self, mock_rest_client):
        """move_decryption_rule: correct path."""
        mock_rest_client.return_value = (200, {"id": "dec-1"})

        result = call("move_decryption_rule", {
            "id": "dec-1",
            "destination": "after",
            "rulebase": "post",
            "destination_rule": "dec-2",
        })

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/security/v1/decryption-rules/dec-1:move",
            params={},
            json={"destination": "after", "rulebase": "post", "destination_rule": "dec-2"},
        )

    def test_move_app_override_rule_success(self, mock_rest_client):
        """move_app_override_rule: correct path."""
        mock_rest_client.return_value = (200, {"id": "ao-1"})

        result = call("move_app_override_rule", {
            "id": "ao-1",
            "destination": "bottom",
            "rulebase": "pre",
        })

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/security/v1/app-override-rules/ao-1:move",
            params={},
            json={"destination": "bottom", "rulebase": "pre"},
        )

    def test_move_error_response(self, mock_rest_client):
        """move operation: non-2xx response."""
        mock_rest_client.return_value = (409, {"message": "Conflict"})

        result = call("move_security_rule", {
            "id": "rule-1",
            "destination": "top",
            "rulebase": "pre",
        })

        assert result["error"] == "API request failed with HTTP 409"
        assert result["status"] == 409


class TestPushOperation:
    """Test push_candidate_config."""

    def test_push_candidate_config_success(self, mock_rest_client):
        """push_candidate_config: POST with body fields from YAML schema."""
        mock_rest_client.return_value = (201, {"job_id": "job-999"})

        result = call("push_candidate_config", {
            "folder": ["Shared", "Mobile Users"],
            "description": "Deploy new rules",
            "admin": ["admin@example.com"],
        })

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/operations/v1/config-versions:push",
            params={},
            json={
                "folder": ["Shared", "Mobile Users"],
                "description": "Deploy new rules",
                "admin": ["admin@example.com"],
            },
        )
        assert result["job_id"] == "job-999"

    def test_push_candidate_config_devices(self, mock_rest_client):
        """push_candidate_config: push to specific devices."""
        mock_rest_client.return_value = (201, {"job_id": "job-100"})

        result = call("push_candidate_config", {
            "devices": [7951000388704, 7951000388707],
            "description": "Push to devices",
        })

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/operations/v1/config-versions:push",
            params={},
            json={
                "devices": [7951000388704, 7951000388707],
                "description": "Push to devices",
            },
        )

    def test_push_candidate_config_error(self, mock_rest_client):
        """push_candidate_config: non-2xx response."""
        mock_rest_client.return_value = (400, {"message": "No folders specified"})

        result = call("push_candidate_config", {})

        assert result["error"] == "API request failed with HTTP 400"
        assert result["status"] == 400


class TestLoadOperation:
    """Test load_candidate_config."""

    def test_load_candidate_config_success(self, mock_rest_client):
        """load_candidate_config: POST with version in body."""
        mock_rest_client.return_value = (201, {"success": True})

        result = call("load_candidate_config", {"version": 42})

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/operations/v1/config-versions:load",
            params={},
            json={"version": 42},
        )
        assert result["success"] is True

    def test_load_candidate_config_error(self, mock_rest_client):
        """load_candidate_config: non-2xx response."""
        mock_rest_client.return_value = (404, {"message": "Version not found"})

        result = call("load_candidate_config", {"version": 999})

        assert result["error"] == "API request failed with HTTP 404"


class TestCommitOperation:
    """Test commit_config."""

    def test_commit_config_success(self, mock_rest_client):
        """commit_config: POST with empty body."""
        mock_rest_client.return_value = (201, {"job_id": "job-500"})

        result = call("commit_config", {})

        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/operations/v1/jobs:commit",
            params={},
            json={},
        )
        assert result["job_id"] == "job-500"

    def test_commit_config_error(self, mock_rest_client):
        """commit_config: non-2xx response."""
        mock_rest_client.return_value = (409, {"message": "Pending changes conflict"})

        result = call("commit_config", {})

        assert result["error"] == "API request failed with HTTP 409"


class TestMCPServerIntegration:
    """Test MCP server integration with tool registry."""

    def test_list_tools_count(self):
        """list_tools() should return 98 tools (Batch 1)."""
        from scm_mcp_server.server import list_tools
        import asyncio

        tools = asyncio.run(list_tools())
        assert len(tools) == 98, f"Expected 98 tools, got {len(tools)}"

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
        """Verify all routing-table tools appear in list_tools()."""
        from scm_mcp_server.server import list_tools
        from scm_mcp_server.tools import (
            _LIST_TOOLS, _GET_BY_ID_TOOLS, _CREATE_TOOLS,
            _UPDATE_TOOLS, _DELETE_TOOLS, _MOVE_TOOLS,
            _PUSH_TOOLS, _LOAD_TOOLS, _COMMIT_TOOLS,
        )
        import asyncio

        tools = asyncio.run(list_tools())
        tool_names = {t.name for t in tools}

        all_tables = [
            _LIST_TOOLS, _GET_BY_ID_TOOLS, _CREATE_TOOLS,
            _UPDATE_TOOLS, _DELETE_TOOLS, _MOVE_TOOLS,
            _PUSH_TOOLS, _LOAD_TOOLS, _COMMIT_TOOLS,
        ]
        for table in all_tables:
            for name in table.keys():
                assert name in tool_names, f"Missing tool: {name}"

    def test_move_tool_descriptions(self):
        """Move tools must warn about rule order change."""
        from scm_mcp_server.server import list_tools
        import asyncio

        tools = asyncio.run(list_tools())
        move_tools = [t for t in tools if t.name.startswith("move_")]

        for tool in move_tools:
            assert "会改变规则顺序" in tool.description, f"{tool.name} missing warning"

    def test_push_tool_description(self):
        """push_candidate_config must warn about high-risk operation."""
        from scm_mcp_server.server import list_tools
        import asyncio

        tools = asyncio.run(list_tools())
        push_tools = [t for t in tools if t.name == "push_candidate_config"]

        assert len(push_tools) == 1
        assert "高风险写操作" in push_tools[0].description
        assert "会将候选配置下发到真实设备" in push_tools[0].description


class TestBatch1Completeness:
    """Verify DESIGN.md Batch 1 tool names == registered tool names (no missing, no extra)."""

    BATCH1_TOOLS = {
        # 1.1 Objects Core (35 tools)
        "list_addresses", "get_address", "create_address", "update_address", "delete_address",
        "list_address_groups", "get_address_group", "create_address_group", "update_address_group", "delete_address_group",
        "list_services", "get_service", "create_service", "update_service", "delete_service",
        "list_service_groups", "get_service_group", "create_service_group", "update_service_group", "delete_service_group",
        "list_tags", "get_tag", "create_tag", "update_tag", "delete_tag",
        "list_application_groups", "get_application_group", "create_application_group", "update_application_group", "delete_application_group",
        "list_external_dynamic_lists", "get_external_dynamic_list", "create_external_dynamic_list", "update_external_dynamic_list", "delete_external_dynamic_list",
        # 1.2 Security Rules (23 tools)
        "list_security_rules", "get_security_rule", "create_security_rule", "update_security_rule", "delete_security_rule", "move_security_rule",
        "list_decryption_rules", "get_decryption_rule", "create_decryption_rule", "update_decryption_rule", "delete_decryption_rule", "move_decryption_rule",
        "list_app_override_rules", "get_app_override_rule", "create_app_override_rule", "update_app_override_rule", "delete_app_override_rule", "move_app_override_rule",
        "list_dos_protection_rules", "get_dos_protection_rule", "create_dos_protection_rule", "update_dos_protection_rule", "delete_dos_protection_rule",
        # 1.3 Security Profiles Read-Only (20 tools)
        "list_anti_spyware_profiles", "get_anti_spyware_profile",
        "list_vulnerability_protection_profiles", "get_vulnerability_protection_profile",
        "list_url_filtering_profiles", "get_url_filtering_profile",
        "list_file_blocking_profiles", "get_file_blocking_profile",
        "list_wildfire_anti_virus_profiles", "get_wildfire_anti_virus_profile",
        "list_dns_security_profiles", "get_dns_security_profile",
        "list_dos_protection_profiles", "get_dos_protection_profile",
        "list_security_profile_groups", "get_security_profile_group",
        "list_decryption_profiles", "get_decryption_profile",
        "list_zone_protection_profiles", "get_zone_protection_profile",
        # 1.4 Operations (8 tools)
        "list_jobs", "get_job",
        "list_config_versions", "get_config_version",
        "push_candidate_config", "load_candidate_config",
        "commit_config", "get_running_config",
        # 1.5 IAM (12 tools)
        "list_service_accounts", "get_service_account", "create_service_account", "update_service_account", "delete_service_account",
        "list_roles", "get_role", "create_role", "delete_role",
        "list_access_policies", "create_access_policy", "delete_access_policy",
    }

    def test_batch1_count(self):
        """Batch 1 should have exactly 98 tools."""
        assert len(self.BATCH1_TOOLS) == 98, f"Expected 98, got {len(self.BATCH1_TOOLS)}"

    def test_no_missing_tools(self):
        """All DESIGN.md Batch 1 tools must be registered."""
        from scm_mcp_server.server import list_tools
        import asyncio

        tools = asyncio.run(list_tools())
        registered = {t.name for t in tools}

        missing = self.BATCH1_TOOLS - registered
        assert not missing, f"Missing from registry: {sorted(missing)}"

    def test_no_extra_tools(self):
        """No extra tools beyond DESIGN.md Batch 1 should be registered."""
        from scm_mcp_server.server import list_tools
        import asyncio

        tools = asyncio.run(list_tools())
        registered = {t.name for t in tools}

        extra = registered - self.BATCH1_TOOLS
        assert not extra, f"Extra tools not in Batch 1: {sorted(extra)}"


class TestWriteOperations:
    """Test write operations (create/update/delete/move)."""

    # ========================================================================
    # Create operations
    # ========================================================================

    def test_create_address_success(self, mock_rest_client):
        """create_address: success case."""
        mock_rest_client.return_value = (201, {"id": "new-addr", "name": "test-address"})

        result = call("create_address", {
            "name": "test-address",
            "ip_netmask": "10.0.0.1/32",
            "folder": "Shared",
        })

        # Verify POST request with correct path, params, and body
        mock_rest_client.assert_called_once_with(
            "POST",
            "/config/objects/v1/addresses",
            params={"folder": "Shared"},
            json={"name": "test-address", "ip_netmask": "10.0.0.1/32"},
        )
        assert result["id"] == "new-addr"

    def test_create_security_rule(self, mock_rest_client):
        """create_security_rule: smoke test."""
        mock_rest_client.return_value = (201, {"id": "rule-new"})
        result = call("create_security_rule", {
            "name": "allow-ssh",
            "action": "allow",
            "folder": "Shared",
        })
        assert result["id"] == "rule-new"

    def test_create_service_account(self, mock_rest_client):
        """create_service_account: IAM create (no folder param)."""
        mock_rest_client.return_value = (201, {"id": "sa-new"})
        result = call("create_service_account", {"name": "test-sa"})

        mock_rest_client.assert_called_once_with(
            "POST",
            "/iam/v1/service-accounts",
            params={},
            json={"name": "test-sa"},
        )
        assert result["id"] == "sa-new"

    # ========================================================================
    # Update operations
    # ========================================================================

    def test_update_address_success(self, mock_rest_client):
        """update_address: success case."""
        mock_rest_client.return_value = (200, {"id": "addr-123", "name": "updated-addr"})

        result = call("update_address", {
            "id": "addr-123",
            "name": "updated-addr",
            "ip_netmask": "10.0.0.2/32",
            "folder": "Shared",
        })

        mock_rest_client.assert_called_once_with(
            "PUT",
            "/config/objects/v1/addresses/addr-123",
            params={"folder": "Shared"},
            json={"name": "updated-addr", "ip_netmask": "10.0.0.2/32"},
        )
        assert result["name"] == "updated-addr"

    def test_update_address_missing_id(self, mock_rest_client):
        """update_address: missing required 'id' parameter."""
        result = call("update_address", {"name": "test", "folder": "Shared"})

        assert result["error"] == "Missing required parameter: id"
        assert result["status"] == 400
        mock_rest_client.assert_not_called()

    def test_update_service_account(self, mock_rest_client):
        """update_service_account: IAM update (no folder param)."""
        mock_rest_client.return_value = (200, {"id": "sa-123", "name": "updated-sa"})
        result = call("update_service_account", {"id": "sa-123", "name": "updated-sa"})

        mock_rest_client.assert_called_once_with(
            "PUT",
            "/iam/v1/service-accounts/sa-123",
            params={},
            json={"name": "updated-sa"},
        )

    # ========================================================================
    # Delete operations
    # ========================================================================

    def test_delete_address_success(self, mock_rest_client):
        """delete_address: success case."""
        mock_rest_client.return_value = (204, {})

        result = call("delete_address", {"id": "addr-123", "folder": "Shared"})

        mock_rest_client.assert_called_once_with(
            "DELETE",
            "/config/objects/v1/addresses/addr-123",
            params={"folder": "Shared"},
        )
        assert result == {}

    def test_delete_security_rule(self, mock_rest_client):
        """delete_security_rule: smoke test."""
        mock_rest_client.return_value = (204, {})
        result = call("delete_security_rule", {"id": "rule-123", "folder": "Shared"})
        assert result == {}

    def test_delete_service_account(self, mock_rest_client):
        """delete_service_account: IAM delete (no folder param)."""
        mock_rest_client.return_value = (204, {})
        result = call("delete_service_account", {"id": "sa-123"})

        mock_rest_client.assert_called_once_with(
            "DELETE",
            "/iam/v1/service-accounts/sa-123",
            params={},
        )

    # ========================================================================
    # Error handling
    # ========================================================================

    def test_create_error_response(self, mock_rest_client):
        """create operation: non-2xx response."""
        mock_rest_client.return_value = (400, {"message": "Invalid request"})

        result = call("create_address", {"name": "test", "folder": "Shared"})

        assert result["error"] == "API request failed with HTTP 400"
        assert result["status"] == 400
        assert result["body"]["message"] == "Invalid request"
