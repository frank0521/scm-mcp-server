# SCM MCP Server - Implementation Workflow

This document defines the implementation phases with clear acceptance criteria for each stage.

---

## Phase 1: Project Scaffolding (15 minutes)

### Objectives
- Create directory structure
- Initialize Python project
- Set up dependency management

### Tasks
- [x] Create project directories:
  - `src/scm_mcp/`
  - `src/scm_mcp/tools/`
  - `tests/`
- [ ] Create `pyproject.toml` with dependencies:
  - `mcp >= 0.9.0`
  - `httpx >= 0.27.0`
  - `pyyaml >= 6.0`
  - `pydantic >= 2.0`
  - `python-dotenv >= 1.0.0`
- [ ] Create empty `__init__.py` files:
  - `src/scm_mcp/__init__.py`
  - `src/scm_mcp/tools/__init__.py`
- [ ] Create `.env.example` template
- [ ] Create `.gitignore` (exclude `.env`, `__pycache__`, etc.)

### Acceptance Criteria
```bash
cd ~/vibe-coding/scm-mcp-server
pip install -e .
# Should complete without errors
```

---

## Phase 2: OAuth2 Authentication (30 minutes)

### Objectives
- Implement client_credentials flow
- Handle token caching and refresh
- Load credentials from environment variables

### Tasks
- [ ] Create `src/scm_mcp/auth.py`:
  - [ ] `OAuth2Manager` class
  - [ ] `get_access_token()` method with caching
  - [ ] `refresh_token()` method
  - [ ] Token expiration checking
- [ ] Load environment variables:
  - `SCM_CLIENT_ID`
  - `SCM_CLIENT_SECRET`
  - `SCM_TSG_ID`
  - `SCM_BASE_URL` (with default)
- [ ] Handle authentication errors gracefully

### Implementation Details
```python
# auth.py structure
class OAuth2Manager:
    def __init__(self, client_id: str, client_secret: str, tsg_id: str, base_url: str):
        self._token: Optional[str] = None
        self._expires_at: Optional[float] = None
        # ...
    
    async def get_access_token(self) -> str:
        # Check cache, fetch if expired
        pass
    
    async def _fetch_token(self) -> dict:
        # Call POST /auth/v1/oauth2/access_token
        # See auth/AuthService.yaml for request format
        pass
```

### Acceptance Criteria
```bash
# Set environment variables
export SCM_CLIENT_ID="test-client-id"
export SCM_CLIENT_SECRET="test-secret"
export SCM_TSG_ID="test-tsg"

# Test authentication
python -c "
import asyncio
from scm_mcp.auth import OAuth2Manager
manager = OAuth2Manager.from_env()
token = asyncio.run(manager.get_access_token())
print(f'Token obtained: {token[:20]}...')
"
# Should print token prefix or error message (if credentials are invalid)
```

---

## Phase 3: SCM REST Client (30 minutes)

### Objectives
- Wrap httpx for SCM API calls
- Automatic Bearer token injection
- Handle 401 errors with token refresh

### Tasks
- [ ] Create `src/scm_mcp/client.py`:
  - [ ] `SCMClient` class
  - [ ] `request(method, path, params, json)` method
  - [ ] Convenience methods: `get()`, `post()`, `put()`, `delete()`
  - [ ] Error handling:
    - 401 → refresh token, retry once
    - 4xx/5xx → return error details
    - Network errors → return connection error

### Implementation Details
```python
# client.py structure
class SCMClient:
    def __init__(self, base_url: str, oauth_manager: OAuth2Manager):
        self.base_url = base_url
        self.oauth = oauth_manager
        self.http = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def request(
        self, 
        method: str, 
        path: str, 
        params: Optional[dict] = None, 
        json: Optional[dict] = None
    ) -> dict:
        # Add Authorization header
        # Make request
        # Handle 401 with retry
        # Parse response
        pass
```

### Acceptance Criteria
```bash
# Test REST client (assuming valid credentials)
python -c "
import asyncio
from scm_mcp.client import SCMClient
from scm_mcp.auth import OAuth2Manager

async def test():
    oauth = OAuth2Manager.from_env()
    client = SCMClient(oauth=oauth)
    result = await client.get('/iam/v1/service-accounts', params={'limit': 1})
    print(f'Response: {result}')

asyncio.run(test())
"
# Should print service accounts response or error
```

---

## Phase 4: OpenAPI Parser (1 hour)

### Objectives
- Parse OpenAPI YAML files
- Extract endpoint metadata
- Generate MCP tool definitions

### Tasks
- [ ] Create `src/scm_mcp/openapi_parser.py`:
  - [ ] `ToolDefinition` dataclass
  - [ ] `parse_openapi_file(yaml_path)` function
  - [ ] `parse_all_specs(base_dir)` function
  - [ ] Convert OpenAPI parameters to JSON Schema
  - [ ] Generate tool names from operationId or path
- [ ] Handle OpenAPI features:
  - Path parameters (`/resource/{id}`)
  - Query parameters
  - Request body schemas
  - Response schemas (optional)

### Implementation Details
```python
# openapi_parser.py structure
@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict  # JSON Schema
    http_method: str
    path_template: str
    response_schema: Optional[dict] = None

def parse_openapi_file(yaml_path: str) -> List[ToolDefinition]:
    # Load YAML
    # Extract paths
    # For each path + method:
    #   - Generate tool name
    #   - Extract parameters
    #   - Convert to JSON Schema
    pass

def parse_all_specs(base_dir: str) -> List[ToolDefinition]:
    # Find all .yaml/.yml files recursively
    # Parse each
    # Deduplicate by name (latest file wins)
    pass
```

### Tool Naming Logic
```python
def generate_tool_name(path: str, method: str, operation_id: Optional[str]) -> str:
    # Prefer operationId if present
    if operation_id:
        return f"scm_{operation_id}"
    
    # Otherwise derive from path and method
    # Example: GET /iam/v1/service-accounts → scm_iam_list_service_accounts
    # Example: POST /iam/v1/access-policies → scm_iam_create_access_policy
    pass
```

### Acceptance Criteria
```bash
# Test OpenAPI parsing
python -c "
from scm_mcp.openapi_parser import parse_all_specs
tools = parse_all_specs('../pan.dev/openapi-specs/scm/')
print(f'Parsed {len(tools)} tools')
for tool in tools[:5]:
    print(f'  - {tool.name}: {tool.http_method} {tool.path_template}')
"
# Should print list of tools like:
#   Parsed 47 tools
#   - scm_auth_get_token: POST /auth/v1/oauth2/access_token
#   - scm_iam_list_service_accounts: GET /iam/v1/service-accounts
#   ...
```

---

## Phase 5: MCP Server Implementation (1 hour)

### Objectives
- Create MCP server with stdio transport
- Register tools dynamically from OpenAPI specs
- Implement tool handlers

### Tasks
- [ ] Create `src/scm_mcp/server.py`:
  - [ ] Initialize MCP server
  - [ ] Load OpenAPI specs at startup
  - [ ] Register each tool with `@server.call_tool()`
  - [ ] Implement generic tool handler
  - [ ] Map tool names to HTTP requests
- [ ] Create `src/scm_mcp/tools/base.py`:
  - [ ] `BaseTool` abstract class (optional, for extensibility)
- [ ] Implement tool execution logic:
  - Validate input against schema
  - Call SCMClient with appropriate method/path
  - Return response or error

### Implementation Details
```python
# server.py structure
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from scm_mcp.auth import OAuth2Manager
from scm_mcp.client import SCMClient
from scm_mcp.openapi_parser import parse_all_specs

# Initialize
app = Server("scm-mcp-server")
oauth_manager = OAuth2Manager.from_env()
scm_client = SCMClient(oauth=oauth_manager)
tools = parse_all_specs("../pan.dev/openapi-specs/scm/")

# Register tools dynamically
for tool_def in tools:
    @app.call_tool()
    async def handle_tool(name: str, arguments: dict):
        # Find tool definition by name
        # Validate arguments
        # Execute HTTP request via scm_client
        # Return response
        pass

# Main entry point
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Acceptance Criteria
```bash
# Start server (will block)
python -m scm_mcp.server

# In another terminal, test with mcp CLI (if available)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python -m scm_mcp.server

# Expected: JSON response listing all tools
```

---

## Phase 6: End-to-End Testing (30 minutes)

### Objectives
- Configure Claude CLI / Cursor
- Test representative tools
- Verify error handling

### Tasks
- [ ] Configure MCP client (Claude CLI example):
  ```json
  {
    "mcpServers": {
      "scm": {
        "command": "python",
        "args": ["-m", "scm_mcp.server"],
        "env": {
          "SCM_CLIENT_ID": "your-client-id",
          "SCM_CLIENT_SECRET": "your-secret",
          "SCM_TSG_ID": "your-tsg-id"
        }
      }
    }
  }
  ```
- [ ] Test cases:
  1. **List service accounts**: "Show me all service accounts"
  2. **Get specific resource**: "Get details of service account with ID abc-123"
  3. **Create resource**: "Create an address object named 'test-host' with IP 192.168.1.1"
  4. **List with pagination**: "Show me the first 10 security rules"
  5. **Error handling**: "Get service account with ID 'invalid-id'" (should return 404)

### Test Script
```bash
#!/bin/bash
# tests/integration_test.sh

echo "Testing SCM MCP Server..."

# Test 1: Authentication
echo "1. Testing authentication..."
python -c "
import asyncio
from scm_mcp.auth import OAuth2Manager
asyncio.run(OAuth2Manager.from_env().get_access_token())
print('✓ Authentication successful')
"

# Test 2: List service accounts
echo "2. Testing list service accounts..."
# (Use mcp CLI or Claude CLI)

# Test 3: Error handling
echo "3. Testing error handling..."
# (Try invalid credentials)
```

### Acceptance Criteria
- [ ] Claude can successfully call at least 3 different tools
- [ ] Error messages are informative (not generic "API failed")
- [ ] Token refresh works (test by forcing token expiration)

---

## Phase 7: Documentation and Delivery (30 minutes)

### Objectives
- Complete user-facing documentation
- Provide setup examples
- Document troubleshooting steps

### Tasks
- [ ] Complete `README.md`:
  - [ ] Installation instructions
  - [ ] Configuration examples (Claude CLI, Cursor)
  - [ ] Usage examples
  - [ ] Available tools list
  - [ ] Troubleshooting section
- [ ] Create `.env.example`:
  ```bash
  SCM_CLIENT_ID=your-client-id-here
  SCM_CLIENT_SECRET=your-client-secret-here
  SCM_TSG_ID=your-tsg-id-here
  SCM_BASE_URL=https://api.strata.paloaltonetworks.com
  ```
- [ ] Document common errors:
  - "Authentication failed" → Check credentials
  - "OpenAPI specs not found" → Verify `../pan.dev` path
  - "Tool not found" → Restart MCP server to reload specs

### Acceptance Criteria
- [ ] A new user can follow README to set up and run the server
- [ ] `.env.example` provides clear template
- [ ] Troubleshooting section addresses top 3 likely errors

---

## Verification Checklist

### Pre-Deployment
- [ ] All environment variables documented
- [ ] No hardcoded credentials in source code
- [ ] OpenAPI specs path is configurable
- [ ] Error messages include actionable guidance

### Functional Testing
- [ ] Can list resources (GET endpoints)
- [ ] Can create resources (POST endpoints)
- [ ] Can update resources (PUT endpoints)
- [ ] Can delete resources (DELETE endpoints)
- [ ] Pagination parameters work correctly
- [ ] Authentication token refreshes automatically

### Integration Testing
- [ ] Works with Claude CLI
- [ ] Works with Cursor (if applicable)
- [ ] Tools appear in MCP client tool list
- [ ] Tool descriptions are clear and accurate

### Error Scenarios
- [ ] Invalid credentials → Clear error message
- [ ] Expired token → Automatic refresh
- [ ] Invalid tool arguments → Schema validation error
- [ ] SCM API error (404, 500) → Transparent error passthrough
- [ ] Network timeout → Connection error message

---

## Post-Implementation Tasks

### Optional Enhancements
- [ ] Add logging configuration (levels: DEBUG, INFO, ERROR)
- [ ] Add metrics (tool call counts, latency)
- [ ] Add unit tests for OpenAPI parser
- [ ] Add integration tests with mock SCM API
- [ ] Add CI/CD pipeline (GitHub Actions)

### Maintenance
- [ ] Monitor OpenAPI spec updates in `pan.dev` repository
- [ ] Update tool definitions when SCM API changes
- [ ] Document breaking changes in CHANGELOG.md

---

**Last Updated**: 2026-07-02  
**Estimated Total Time**: 4 hours  
**Dependencies**: Python 3.11+, valid SCM credentials, access to `pan.dev` repository
