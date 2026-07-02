# SCM MCP Server

Model Context Protocol (MCP) server for **Palo Alto Networks Strata Cloud Manager (SCM)**.

Enables Claude, Cursor, and other MCP clients to interact with the SCM API using natural language. 168 tools covering Objects, Security Rules, Security Profiles, Operations, and IAM.

---

## Prerequisites

- **Python 3.11+**
- **SCM OAuth2 Credentials**: Client ID, Client Secret, TSG ID
- **MCP Client**: Claude CLI, Claude Desktop, or Cursor

---

## Installation

```bash
cd ~/vibe-coding/scm-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## Configuration

### Environment Variables

```bash
export SCM_CLIENT_ID="your-client-id"
export SCM_CLIENT_SECRET="your-client-secret"
export SCM_TSG_ID="your-tsg-id"
export SCM_BASE_URL="https://api.strata.paloaltonetworks.com"  # optional, this is the default
```

### Claude CLI / Claude Desktop

Add to `~/.claude.json` or `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scm": {
      "command": "/path/to/scm-mcp-server/venv/bin/python",
      "args": ["-m", "scm_mcp_server.server"],
      "env": {
        "SCM_CLIENT_ID": "your-client-id",
        "SCM_CLIENT_SECRET": "your-client-secret",
        "SCM_TSG_ID": "your-tsg-id"
      }
    }
  }
}
```

### Cursor

Add to Cursor MCP settings (`~/Library/Application Support/Cursor/User/globalStorage/mcp.json` on macOS):

```json
{
  "mcpServers": {
    "scm": {
      "command": "/path/to/scm-mcp-server/venv/bin/python",
      "args": ["-m", "scm_mcp_server.server"],
      "env": {
        "SCM_CLIENT_ID": "your-client-id",
        "SCM_CLIENT_SECRET": "your-client-secret",
        "SCM_TSG_ID": "your-tsg-id"
      }
    }
  }
}
```

---

## Available Tools (168)

### Objects Core (35 tools)

| Resource | list | get | create | update | delete |
|----------|------|-----|--------|--------|--------|
| Addresses | `list_addresses` | `get_address` | `create_address` | `update_address` | `delete_address` |
| Address Groups | `list_address_groups` | `get_address_group` | `create_address_group` | `update_address_group` | `delete_address_group` |
| Services | `list_services` | `get_service` | `create_service` | `update_service` | `delete_service` |
| Service Groups | `list_service_groups` | `get_service_group` | `create_service_group` | `update_service_group` | `delete_service_group` |
| Tags | `list_tags` | `get_tag` | `create_tag` | `update_tag` | `delete_tag` |
| Application Groups | `list_application_groups` | `get_application_group` | `create_application_group` | `update_application_group` | `delete_application_group` |
| External Dynamic Lists | `list_external_dynamic_lists` | `get_external_dynamic_list` | `create_external_dynamic_list` | `update_external_dynamic_list` | `delete_external_dynamic_list` |

### Objects Extended (40 tools)

| Resource | list | get | create | update | delete |
|----------|------|-----|--------|--------|--------|
| Applications | `list_applications` | `get_application` | - | - | - |
| Application Filters | `list_application_filters` | `get_application_filter` | `create_application_filter` | `update_application_filter` | `delete_application_filter` |
| Schedules | `list_schedules` | `get_schedule` | `create_schedule` | `update_schedule` | `delete_schedule` |
| Regions | `list_regions` | `get_region` | `create_region` | `update_region` | `delete_region` |
| HIP Objects | `list_hip_objects` | `get_hip_object` | `create_hip_object` | `update_hip_object` | `delete_hip_object` |
| HIP Profiles | `list_hip_profiles` | `get_hip_profile` | `create_hip_profile` | `update_hip_profile` | `delete_hip_profile` |
| Log Forwarding Profiles | `list_log_forwarding_profiles` | `get_log_forwarding_profile` | `create_log_forwarding_profile` | `update_log_forwarding_profile` | `delete_log_forwarding_profile` |
| HTTP Server Profiles | `list_http_server_profiles` | `get_http_server_profile` | `create_http_server_profile` | - | `delete_http_server_profile` |
| Syslog Server Profiles | `list_syslog_server_profiles` | `get_syslog_server_profile` | `create_syslog_server_profile` | - | `delete_syslog_server_profile` |

### Security Rules (23 tools)

| Resource | list | get | create | update | delete | move |
|----------|------|-----|--------|--------|--------|------|
| Security Rules | `list_security_rules` | `get_security_rule` | `create_security_rule` | `update_security_rule` | `delete_security_rule` | `move_security_rule` |
| Decryption Rules | `list_decryption_rules` | `get_decryption_rule` | `create_decryption_rule` | `update_decryption_rule` | `delete_decryption_rule` | `move_decryption_rule` |
| App Override Rules | `list_app_override_rules` | `get_app_override_rule` | `create_app_override_rule` | `update_app_override_rule` | `delete_app_override_rule` | `move_app_override_rule` |
| DoS Protection Rules | `list_dos_protection_rules` | `get_dos_protection_rule` | `create_dos_protection_rule` | `update_dos_protection_rule` | `delete_dos_protection_rule` | - |

### Security Profiles (50 tools: 20 read + 30 write)

| Profile Type | list | get | create | update | delete |
|-------------|------|-----|--------|--------|--------|
| Anti-Spyware | `list_anti_spyware_profiles` | `get_anti_spyware_profile` | `create_anti_spyware_profile` | `update_anti_spyware_profile` | `delete_anti_spyware_profile` |
| Vulnerability Protection | `list_vulnerability_protection_profiles` | `get_vulnerability_protection_profile` | `create_vulnerability_protection_profile` | `update_vulnerability_protection_profile` | `delete_vulnerability_protection_profile` |
| URL Filtering | `list_url_filtering_profiles` | `get_url_filtering_profile` | `create_url_filtering_profile` | `update_url_filtering_profile` | `delete_url_filtering_profile` |
| File Blocking | `list_file_blocking_profiles` | `get_file_blocking_profile` | `create_file_blocking_profile` | `update_file_blocking_profile` | `delete_file_blocking_profile` |
| Wildfire Anti-Virus | `list_wildfire_anti_virus_profiles` | `get_wildfire_anti_virus_profile` | `create_wildfire_anti_virus_profile` | `update_wildfire_anti_virus_profile` | `delete_wildfire_anti_virus_profile` |
| DNS Security | `list_dns_security_profiles` | `get_dns_security_profile` | `create_dns_security_profile` | `update_dns_security_profile` | `delete_dns_security_profile` |
| DoS Protection | `list_dos_protection_profiles` | `get_dos_protection_profile` | `create_dos_protection_profile` | `update_dos_protection_profile` | `delete_dos_protection_profile` |
| Security Profile Groups | `list_security_profile_groups` | `get_security_profile_group` | `create_security_profile_group` | `update_security_profile_group` | `delete_security_profile_group` |
| Decryption Profiles | `list_decryption_profiles` | `get_decryption_profile` | `create_decryption_profile` | `update_decryption_profile` | `delete_decryption_profile` |
| Zone Protection | `list_zone_protection_profiles` | `get_zone_protection_profile` | `create_zone_protection_profile` | `update_zone_protection_profile` | `delete_zone_protection_profile` |

### Operations (8 tools)

| Tool | Description |
|------|-------------|
| `list_jobs` | List configuration jobs |
| `get_job` | Get job status by ID |
| `list_config_versions` | List configuration versions |
| `get_config_version` | Get specific config version |
| `get_running_config` | Get current running config |
| `push_candidate_config` | **High-risk**: Push candidate config to devices |
| `load_candidate_config` | Load config version as candidate |
| `commit_config` | Commit candidate to running config |

### IAM (12 tools)

| Resource | list | get | create | update | delete |
|----------|------|-----|--------|--------|--------|
| Service Accounts | `list_service_accounts` | `get_service_account` | `create_service_account` | `update_service_account` | `delete_service_account` |
| Roles | `list_roles` | `get_role` | `create_role` | - | `delete_role` |
| Access Policies | `list_access_policies` | - | `create_access_policy` | - | `delete_access_policy` |

---

## Usage Examples

```
User: Show me all security rules in the Production folder

Claude: [calls list_security_rules with folder="Production"]
Found 15 security rules...

User: Create an address object named "corp-dmz" with IP 192.168.100.0/24

Claude: [calls create_address with name="corp-dmz", ip_netmask="192.168.100.0/24", folder="Shared"]
Created address object "corp-dmz" (id: addr-xxx)

User: Move security rule abc-123 to the top of the pre rulebase

Claude: [calls move_security_rule with id="abc-123", destination="top", rulebase="pre"]
Rule moved to top position.
```

---

## Connectivity Self-Check

Run the stdio smoke test to verify the server starts, registers tools, and responds to calls:

```bash
source venv/bin/activate
python scripts/smoke_stdio.py
```

Expected output (without SCM credentials configured):

```
[OK] initialize: server=scm-mcp-server
[OK] tools/list: 168 tools registered
[OK] tool name set matches routing tables exactly
[OK] call_tool(list_roles): response received (76 chars)
```

To verify syntax of all source files:

```bash
python -c "
import ast, pathlib, sys
for f in pathlib.Path('src/scm_mcp_server').rglob('*.py'):
    ast.parse(f.read_text())
print('OK')
"
```

To run unit tests:

```bash
pytest tests/ -q
```

---

## Troubleshooting

### Missing Environment Variables

```
Tool execution error: 缺少必填环境变量: SCM_CLIENT_ID, SCM_CLIENT_SECRET, SCM_TSG_ID
```

Set the required variables (see Configuration above).

### Authentication Failed

Verify credentials in SCM UI: Settings > Identity & Access > Service Accounts.

### Permission Denied (403)

Check the service account's IAM access policies in SCM.

### Connection Timeout

Verify network connectivity to `api.strata.paloaltonetworks.com`.

---

## Project Structure

```
scm-mcp-server/
├── src/scm_mcp_server/
│   ├── server.py         # MCP server (stdio transport)
│   ├── rest_client.py    # SCM REST client (httpx + OAuth2)
│   ├── auth.py           # OAuth2 token management
│   ├── config.py         # Environment variable loading
│   └── tools/
│       ├── __init__.py   # Routing tables + dispatcher
│       └── schemas.py    # JSON Schema definitions
├── tests/test_tools.py   # 124 unit tests
├── scripts/smoke_stdio.py # stdio transport smoke test
├── CLAUDE.md             # Engineering contract
├── DESIGN.md             # Architecture + API mapping
└── WORKFLOW.md           # Implementation phases
```

---

**Version**: 0.1.0 | **Tools**: 168 | **Python**: 3.11+ | **Transport**: stdio
