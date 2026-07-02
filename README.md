# SCM MCP Server

Model Context Protocol (MCP) server for **Palo Alto Networks Strata Cloud Manager (SCM)**.

This server enables Claude, Cursor, and other MCP clients to interact directly with the SCM API using natural language.

---

## Features

- 🔐 **OAuth2 Authentication**: Automatic token management with client_credentials flow
- 🛠️ **Dynamic Tool Generation**: Tools automatically generated from OpenAPI specifications
- 📦 **Full API Coverage**: Supports IAM, SASE Config, Cloud NGFW, Subscription, and Tenancy modules
- 🚀 **Zero Configuration**: Works out of the box with environment variables
- 🔄 **Auto Token Refresh**: Handles token expiration transparently

---

## Prerequisites

- **Python 3.11** or higher
- **SCM OAuth2 Credentials**:
  - Client ID
  - Client Secret
  - Tenant Service Group (TSG) ID
- **MCP Client**: Claude Desktop, Claude CLI, or Cursor

---

## Installation

### 1. Clone the Repository

```bash
cd ~/vibe-coding/
git clone <repository-url> scm-mcp-server
cd scm-mcp-server
```

### 2. Create Virtual Environment (Recommended)

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Why virtual environment?**  
On macOS with system Python (3.14+), PEP 668 requires virtual environments to prevent system package conflicts.

### 3. Install Dependencies

```bash
pip install -e .
```

This installs the package in editable mode with all required dependencies:
- `mcp` - Official MCP SDK
- `httpx` - Async HTTP client
- `pyyaml` - OpenAPI parsing
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

### 4. Configure Environment Variables

Create a `.env` file or export variables in your shell:

```bash
export SCM_CLIENT_ID="your-client-id"
export SCM_CLIENT_SECRET="your-client-secret"
export SCM_TSG_ID="your-tsg-id"
export SCM_BASE_URL="https://api.strata.paloaltonetworks.com"  # Optional, this is the default
```

Or copy `.env.example` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

---

## Configuration

### Claude Desktop / Claude CLI

Edit `~/.claude/claude_desktop_config.json`:

**Option 1: Using Virtual Environment (Recommended)**
```json
{
  "mcpServers": {
    "scm": {
      "command": "/Users/YOUR_USERNAME/vibe-coding/scm-mcp-server/venv/bin/python",
      "args": ["-m", "scm_mcp.server"],
      "env": {
        "SCM_CLIENT_ID": "your-client-id",
        "SCM_CLIENT_SECRET": "your-client-secret",
        "SCM_TSG_ID": "your-tsg-id"
      }
    }
  }
}
```

**Option 2: Using System Python (if no virtual environment)**
```json
{
  "mcpServers": {
    "scm": {
      "command": "python3",
      "args": ["-m", "scm_mcp.server"],
      "env": {
        "SCM_CLIENT_ID": "your-client-id",
        "SCM_CLIENT_SECRET": "your-client-secret",
        "SCM_TSG_ID": "your-tsg-id"
      }
    }
  }
}
```

**Note**: 
- Replace `YOUR_USERNAME` with your actual username
- Replace `your-client-id`, `your-client-secret`, and `your-tsg-id` with your actual credentials
- Use absolute path to venv Python for reliability

### Cursor

Add to Cursor's MCP configuration file (location varies by OS):

**macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`

```json
{
  "mcpServers": {
    "scm": {
      "command": "python",
      "args": ["-m", "scm_mcp.server"],
      "env": {
        "SCM_CLIENT_ID": "your-client-id",
        "SCM_CLIENT_SECRET": "your-client-secret",
        "SCM_TSG_ID": "your-tsg-id"
      }
    }
  }
}
```

### Manual Testing

You can run the server directly for testing:

```bash
python -m scm_mcp.server
```

The server uses stdio transport and expects JSON-RPC messages on stdin.

---

## Usage Examples

Once configured, you can use natural language with Claude to interact with SCM:

### List Resources

```
User: Show me all service accounts in SCM

Claude: [Calls scm_iam_list_service_accounts]
I found 12 service accounts:
1. backup-service (ID: sa-abc123)
2. monitoring-agent (ID: sa-def456)
...
```

### Create Resources

```
User: Create an address object named "corp-network" with IP range 10.0.0.0/8

Claude: [Calls scm_sase_create_address_object with appropriate parameters]
Successfully created address object "corp-network" with IP 10.0.0.0/8.
```

### Get Specific Resources

```
User: Get details of security rule with ID "rule-12345"

Claude: [Calls scm_sase_get_security_rule]
Security Rule Details:
- Name: Block Suspicious Traffic
- Action: deny
- Source: any
- Destination: 192.168.1.0/24
...
```

### Filter and Pagination

```
User: Show me the first 10 security rules in the "Production" folder

Claude: [Calls scm_sase_list_security_rules with folder="Production" and limit=10]
Here are the first 10 security rules in Production:
1. Allow-Internal-Traffic
2. Block-External-Access
...
```

---

## Available Tools

The server dynamically generates tools from OpenAPI specifications. To see all available tools:

```bash
python -c "
from scm_mcp.openapi_parser import parse_all_specs
tools = parse_all_specs('../pan.dev/openapi-specs/scm/')
for tool in sorted([t.name for t in tools]):
    print(f'  {tool}')
"
```

### Tool Categories

#### Authentication
- `scm_auth_get_token` - Obtain OAuth2 access token (mostly for testing)

#### IAM (Identity and Access Management)
- `scm_iam_list_service_accounts` - List all service accounts
- `scm_iam_get_service_account` - Get service account details
- `scm_iam_create_service_account` - Create new service account
- `scm_iam_update_service_account` - Update existing service account
- `scm_iam_delete_service_account` - Delete service account
- `scm_iam_list_access_policies` - List access policies
- `scm_iam_create_access_policy` - Create access policy
- (Additional IAM tools for roles, permissions, user accounts...)

#### SASE Configuration
- `scm_sase_list_security_rules` - List security rules
- `scm_sase_get_security_rule` - Get security rule details
- `scm_sase_create_security_rule` - Create security rule
- `scm_sase_update_security_rule` - Update security rule
- `scm_sase_delete_security_rule` - Delete security rule
- `scm_sase_list_address_objects` - List address objects
- `scm_sase_create_address_object` - Create address object
- (Additional tools for address groups, services, applications...)

#### Cloud NGFW Configuration
- `scm_cloudngfw_list_security_rules` - List Cloud NGFW security rules
- `scm_cloudngfw_create_security_rule` - Create Cloud NGFW security rule
- (Similar structure to SASE tools)

#### Subscription Management
- `scm_subscription_list_licenses` - List licenses
- `scm_subscription_get_license` - Get license details

#### Tenancy Management
- `scm_tenancy_list_tsgs` - List Tenant Service Groups
- `scm_tenancy_get_tsg` - Get TSG details

---

## Troubleshooting

### Authentication Failed

**Error**: `Authentication failed: Invalid credentials`

**Solutions**:
1. Verify your credentials in the SCM UI:
   - Go to Settings → Identity & Access → Service Accounts
   - Confirm Client ID and Secret are correct
2. Check environment variables are set:
   ```bash
   echo $SCM_CLIENT_ID
   echo $SCM_CLIENT_SECRET
   echo $SCM_TSG_ID
   ```
3. Ensure TSG ID matches your tenant

### OpenAPI Specs Not Found

**Error**: `FileNotFoundError: ../pan.dev/openapi-specs/scm/`

**Solutions**:
1. Verify the `pan.dev` repository is cloned at `~/vibe-coding/pan.dev`
2. Check the relative path is correct from your project directory
3. If `pan.dev` is elsewhere, update the path in `server.py`

### Tool Not Found

**Error**: `Tool "scm_xxx_yyy" not found`

**Solutions**:
1. Restart the MCP server to reload OpenAPI specs
2. Check if the tool exists:
   ```bash
   python -c "from scm_mcp.openapi_parser import parse_all_specs; print([t.name for t in parse_all_specs('../pan.dev/openapi-specs/scm/')])"
   ```
3. Verify the corresponding OpenAPI file exists and is valid YAML

### Permission Denied / 403 Errors

**Error**: `403 Forbidden`

**Solutions**:
1. Check service account permissions in SCM
2. Ensure the service account has access to the requested resources
3. Verify TSG ID is correct

### Connection Timeout

**Error**: `Connection timeout`

**Solutions**:
1. Check network connectivity to `api.strata.paloaltonetworks.com`
2. Verify proxy settings if behind a corporate firewall
3. Increase timeout in `client.py` if needed (default: 30 seconds)

### Token Refresh Loop

**Error**: `401 Unauthorized` repeated multiple times

**Solutions**:
1. This indicates the token refresh is failing
2. Check credentials are still valid (not expired/revoked)
3. Restart the server to clear cached token
4. Check SCM logs for service account issues

---

## Development

### Project Structure

```
scm-mcp-server/
├── CLAUDE.md               # Engineering contract (L1)
├── DESIGN.md               # Architecture design (L2)
├── WORKFLOW.md             # Implementation phases (L3)
├── README.md               # User documentation (this file)
├── pyproject.toml          # Python project config
├── .env.example            # Environment variable template
├── src/
│   └── scm_mcp/
│       ├── __init__.py
│       ├── server.py       # MCP server entry point
│       ├── auth.py         # OAuth2 authentication
│       ├── client.py       # SCM REST client
│       ├── openapi_parser.py  # OpenAPI spec parser
│       └── tools/
│           ├── __init__.py
│           └── base.py     # Tool base class
└── tests/
    └── ...
```

### Running Tests

```bash
# Unit tests (if implemented)
pytest tests/

# Integration test
./tests/integration_test.sh
```

### Adding Custom Tools

If you need custom logic beyond simple REST calls:

1. Create a new file in `src/scm_mcp/tools/`
2. Inherit from `BaseTool`
3. Register in `server.py`

Example:
```python
# src/scm_mcp/tools/custom_tool.py
from .base import BaseTool

class CustomTool(BaseTool):
    name = "scm_custom_operation"
    description = "Performs a custom operation"
    
    async def execute(self, arguments: dict) -> dict:
        # Custom logic here
        pass
```

### Updating OpenAPI Specs

When SCM API changes:
1. Pull latest `pan.dev` repository
2. Restart the MCP server
3. New/updated tools will be available automatically

---

## Architecture

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

**High-level flow**:
1. Claude calls MCP tool (e.g., `scm_iam_list_service_accounts`)
2. MCP server validates arguments against OpenAPI schema
3. Server calls `SCMClient` with HTTP method and path
4. `SCMClient` adds OAuth2 Bearer token
5. HTTP request sent to SCM API
6. Response returned to Claude

**Key principles**:
- Zero business logic (pure proxy layer)
- Dynamic tool generation from OpenAPI specs
- Transparent error handling
- Automatic token management

---

## Security

### Credential Management
- **Never commit `.env` files** with real credentials
- Use environment variables or secure secret management
- Rotate credentials regularly

### API Permissions
- Service account inherits permissions from SCM IAM policies
- Follow principle of least privilege
- Monitor service account usage in SCM audit logs

### Network Security
- All communication over HTTPS (TLS 1.2+)
- Validate SCM API certificate (httpx default behavior)
- Consider IP allowlisting for production environments

---

## Contributing

See [WORKFLOW.md](WORKFLOW.md) for implementation phases and development guidelines.

### Coding Standards
- Type hints required (Python 3.11+ syntax)
- Follow PEP 8 style guide
- Use async/await for all I/O operations
- No hardcoded values (use environment variables)

### Before Submitting
- [ ] Read [CLAUDE.md](CLAUDE.md) for project constraints
- [ ] Run type checker: `mypy src/`
- [ ] Format code: `black src/`
- [ ] Test manually with Claude CLI

---

## Technology Stack

- **Python**: 3.11+
- **MCP SDK**: [mcp](https://pypi.org/project/mcp/) - Official Model Context Protocol SDK
- **HTTP Client**: [httpx](https://www.python-httpx.org/) - Async HTTP client
- **OpenAPI Parsing**: [PyYAML](https://pyyaml.org/) - YAML parser
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/) - Runtime type checking
- **Environment Variables**: [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## License

(To be determined)

---

## Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [DESIGN.md](DESIGN.md) for architecture details
3. Check SCM API documentation at [pan.dev](https://pan.dev/)
4. Open an issue in this repository

---

## Roadmap

### Planned Features
- [ ] Response caching (configurable)
- [ ] Rate limiting awareness
- [ ] Batch operations support
- [ ] Webhook integration (if SCM supports)
- [ ] Enhanced logging and metrics
- [ ] Docker containerization

### Out of Scope
- Local state management (e.g., database)
- Alternative authentication methods (only OAuth2)
- Non-REST protocols (only HTTP/HTTPS)

---

**Last Updated**: 2026-07-02  
**Version**: 0.1.0  
**Maintainer**: Frank Fan
