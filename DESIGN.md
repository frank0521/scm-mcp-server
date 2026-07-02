# SCM MCP Server - Architecture Design

## Architecture Overview

```
┌─────────────────┐         stdio          ┌──────────────────┐        HTTPS         ┌─────────────────┐
│  Claude CLI     │    (JSON-RPC MCP)      │   MCP Server     │     (OAuth2)        │   SCM API       │
│  / Cursor       │ ◄────────────────────► │   (Python)       │ ◄─────────────────► │   (REST API)    │
│  / Claude Code  │                        │                  │                     │                 │
└─────────────────┘                        └──────────────────┘                     └─────────────────┘
                                                    │
                                                    │ reads
                                                    ▼
                                           ┌──────────────────┐
                                           │  OpenAPI Specs   │
                                           │  (YAML files)    │
                                           └──────────────────┘
```

## Component Design

### 1. MCP Server (`server.py`)
**Responsibility**: stdio-based MCP server that registers and dispatches tools.

**Initialization Flow**:
1. Load environment variables (credentials, base URL)
2. Parse OpenAPI specifications from `../pan.dev/openapi-specs/scm/`
3. Generate tool definitions dynamically
4. Register tools with MCP SDK
5. Start stdio transport

**Key Interfaces**:
```python
@server.call_tool()
async def handle_tool(name: str, arguments: dict) -> dict:
    # Route to appropriate handler based on tool name
    # Validate arguments against OpenAPI schema
    # Call SCMClient method
    # Return response or error
```

### 2. Authentication Module (`auth.py`)
**Responsibility**: OAuth2 client_credentials flow with automatic token refresh.

**Key Functions**:
```python
class OAuth2Manager:
    async def get_access_token() -> str:
        # Check if cached token is valid
        # If expired, fetch new token from /auth/v1/oauth2/access_token
        # Cache token and expiration time
        # Return valid access token
    
    async def refresh_token() -> str:
        # Force fetch new token
        # Update cache
```

**Token Storage**:
- In-memory cache (not persisted)
- Includes expiration timestamp
- Thread-safe for async operations

### 3. SCM REST Client (`client.py`)
**Responsibility**: Wrapper around httpx for SCM API calls.

**Key Methods**:
```python
class SCMClient:
    def __init__(self, base_url: str, oauth_manager: OAuth2Manager):
        self.client = httpx.AsyncClient(base_url=base_url)
        self.oauth = oauth_manager
    
    async def request(
        self, 
        method: str, 
        path: str, 
        params: dict = None, 
        json: dict = None
    ) -> dict:
        # Add Authorization header with Bearer token
        # Make HTTP request
        # Handle 401 (refresh token and retry once)
        # Handle other errors (4xx, 5xx)
        # Return parsed JSON response
    
    async def get(self, path: str, params: dict = None) -> dict:
        return await self.request("GET", path, params=params)
    
    async def post(self, path: str, json: dict) -> dict:
        return await self.request("POST", path, json=json)
    
    async def put(self, path: str, json: dict) -> dict:
        return await self.request("PUT", path, json=json)
    
    async def delete(self, path: str) -> dict:
        return await self.request("DELETE", path)
```

**Error Handling**:
- 401 Unauthorized → Refresh token and retry once
- 4xx Client Error → Return error details to MCP client
- 5xx Server Error → Return error details to MCP client
- Network errors → Return connection error message

### 4. OpenAPI Parser (`openapi_parser.py`)
**Responsibility**: Parse OpenAPI YAML files and generate MCP tool definitions.

**Parsing Strategy**:
```python
def parse_openapi_spec(yaml_path: str) -> List[ToolDefinition]:
    # Load YAML file
    # Extract base path and API version
    # For each endpoint (path + method):
    #   - Generate tool name from operationId or path
    #   - Extract description from summary/description
    #   - Convert OpenAPI parameters to JSON Schema (inputSchema)
    #   - Store HTTP method, path template, response schema
    # Return list of ToolDefinition objects

def parse_all_specs(base_dir: str) -> List[ToolDefinition]:
    # Recursively find all .yaml/.yml files in base_dir
    # Parse each file
    # Deduplicate by tool name
    # Return merged list
```

**Tool Definition Structure**:
```python
@dataclass
class ToolDefinition:
    name: str                    # e.g., "scm_iam_list_service_accounts"
    description: str             # From OpenAPI summary/description
    input_schema: dict           # JSON Schema for parameters
    http_method: str             # GET, POST, PUT, DELETE
    path_template: str           # e.g., "/iam/v1/service-accounts"
    response_schema: dict        # Expected response structure (optional)
```

**Tool Naming Convention**:
- Format: `scm_<module>_<action>_<resource>`
- Module: `auth`, `iam`, `sase`, `cloudngfw`, `subscription`, `tenancy`
- Action: `list`, `get`, `create`, `update`, `delete`
- Resource: singular/plural noun (e.g., `service_accounts`, `security_rule`)

Examples:
- `scm_iam_list_service_accounts` (GET /iam/v1/service-accounts)
- `scm_iam_create_access_policy` (POST /iam/v1/access-policies)
- `scm_sase_list_security_rules` (GET /config/security/v1/security-rules)
- `scm_sase_update_address_object` (PUT /config/objects/v1/addresses/{id})

## MCP Tools Mapping

### Auth Tools

#### `scm_auth_get_token`
- **OpenAPI**: `auth/AuthService.yaml` → POST `/auth/v1/oauth2/access_token`
- **Input**: None (uses environment variables)
- **Output**: `{access_token: string, expires_in: number, token_type: string}`
- **Note**: Primarily for testing; automatic token management is built-in

### IAM Tools

#### `scm_iam_list_service_accounts`
- **OpenAPI**: `iam/ServiceAccounts.yaml` → GET `/iam/v1/service-accounts`
- **Input**: `{limit?: number, offset?: number, filter?: string}`
- **Output**: `{data: ServiceAccount[], total: number, offset: number, limit: number}`

#### `scm_iam_get_service_account`
- **OpenAPI**: `iam/ServiceAccounts.yaml` → GET `/iam/v1/service-accounts/{id}`
- **Input**: `{id: string}`
- **Output**: `ServiceAccount`

#### `scm_iam_create_service_account`
- **OpenAPI**: `iam/ServiceAccounts.yaml` → POST `/iam/v1/service-accounts`
- **Input**: Schema from OpenAPI `requestBody` (name, description, etc.)
- **Output**: Created `ServiceAccount`

#### `scm_iam_list_access_policies`
- **OpenAPI**: `iam/AccessPolicies.yaml` → GET `/iam/v1/access-policies`
- **Input**: `{limit?: number, offset?: number}`
- **Output**: `{data: AccessPolicy[]}`

#### `scm_iam_create_access_policy`
- **OpenAPI**: `iam/AccessPolicies.yaml` → POST `/iam/v1/access-policies`
- **Input**: Schema from OpenAPI (principal, resource, actions, etc.)
- **Output**: Created `AccessPolicy`

### SASE Config Tools

#### `scm_sase_list_security_rules`
- **OpenAPI**: `config/sase/security/security-services-R2-2026.yaml` → GET `/config/security/v1/security-rules`
- **Input**: `{folder?: string, limit?: number, offset?: number}`
- **Output**: `{data: SecurityRule[], total: number}`

#### `scm_sase_get_security_rule`
- **OpenAPI**: Same file → GET `/config/security/v1/security-rules/{id}`
- **Input**: `{id: string, folder?: string}`
- **Output**: `SecurityRule`

#### `scm_sase_create_security_rule`
- **OpenAPI**: Same file → POST `/config/security/v1/security-rules`
- **Input**: Schema from OpenAPI (name, source, destination, action, etc.)
- **Output**: Created `SecurityRule`

#### `scm_sase_update_security_rule`
- **OpenAPI**: Same file → PUT `/config/security/v1/security-rules/{id}`
- **Input**: `{id: string, ...updates}`
- **Output**: Updated `SecurityRule`

#### `scm_sase_delete_security_rule`
- **OpenAPI**: Same file → DELETE `/config/security/v1/security-rules/{id}`
- **Input**: `{id: string}`
- **Output**: `{success: boolean}`

#### `scm_sase_list_address_objects`
- **OpenAPI**: `config/sase/objects/objects-june.yaml` → GET `/config/objects/v1/addresses`
- **Input**: `{folder?: string, limit?: number, offset?: number}`
- **Output**: `{data: AddressObject[]}`

#### `scm_sase_create_address_object`
- **OpenAPI**: Same file → POST `/config/objects/v1/addresses`
- **Input**: Schema from OpenAPI (name, ip_netmask?, fqdn?, description?, etc.)
- **Output**: Created `AddressObject`

### Cloud NGFW Config Tools

Similar structure to SASE tools, but using `config/cloudngfw/` OpenAPI specs:
- `scm_cloudngfw_list_security_rules`
- `scm_cloudngfw_create_security_rule`
- `scm_cloudngfw_list_address_objects`
- etc.

### Subscription Tools

#### `scm_subscription_list_licenses`
- **OpenAPI**: `subscription/Licenses.yaml` → GET `/subscription/v1/licenses`
- **Input**: `{limit?: number, offset?: number}`
- **Output**: `{data: License[]}`

### Tenancy Tools

#### `scm_tenancy_list_tsgs`
- **OpenAPI**: `tenancy/TenantServiceGroup.yaml` → GET `/tenancy/v1/tenant-service-groups`
- **Input**: `{limit?: number, offset?: number}`
- **Output**: `{data: TenantServiceGroup[]}`

## Data Flow Example

### Scenario: List Service Accounts

```
1. User (Claude): "Show me all service accounts"

2. Claude calls MCP tool: scm_iam_list_service_accounts
   Arguments: {limit: 100}

3. MCP Server (server.py):
   - Validates arguments against inputSchema
   - Routes to handler

4. Handler:
   - Calls SCMClient.get("/iam/v1/service-accounts", params={"limit": 100})

5. SCMClient (client.py):
   - Gets access token from OAuth2Manager
   - Makes HTTP GET request:
     GET https://api.strata.paloaltonetworks.com/iam/v1/service-accounts?limit=100
     Authorization: Bearer <token>

6. SCM API responds:
   {
     "data": [
       {"id": "sa-123", "name": "example-sa", ...},
       ...
     ],
     "total": 42,
     "offset": 0,
     "limit": 100
   }

7. SCMClient returns parsed JSON to handler

8. Handler returns to MCP Server

9. MCP Server sends response to Claude via stdio

10. Claude processes and presents to user: "Found 42 service accounts: ..."
```

## Implementation Principles

### 1. Zero Business Logic
- Each tool is a **thin wrapper** around a REST API call
- No data transformation beyond what's required for MCP protocol
- No caching, aggregation, or derived computations

### 2. Dynamic Tool Generation
- Tools are generated at startup from OpenAPI specs
- No hardcoded tool definitions in source code
- Adding new SCM API endpoints requires no code changes (only OpenAPI updates)

### 3. Error Transparency
- SCM API errors are passed through to Claude verbatim
- HTTP status codes and error messages preserved
- No custom error wrapping (except for connection issues)

### 4. Pagination Handling
- Pagination parameters (limit, offset) are exposed in tool input schemas
- No automatic pagination (fetching all pages)
- Rationale: Claude can decide whether to paginate or request specific pages

### 5. Authentication Abstraction
- Tools do not handle authentication
- OAuth2Manager maintains token lifecycle
- Automatic retry on 401 (one retry only to avoid loops)

## Security Considerations

### 1. Credential Storage
- All credentials in environment variables
- No plaintext credentials in logs
- Token stored in memory only (not persisted to disk)

### 2. API Scope
- Server inherits permissions from OAuth2 client credentials
- No privilege escalation or bypass mechanisms
- Respect SCM API rate limits (no built-in retry logic beyond auth)

### 3. Input Validation
- All tool inputs validated against OpenAPI schemas
- No SQL injection risk (REST API only)
- No command injection risk (no shell execution)

## Extensibility

### Adding New Tools
1. Update OpenAPI specs in `../pan.dev/openapi-specs/scm/`
2. Restart MCP server
3. New tools automatically available

### Custom Tool Logic (if needed)
- Override specific tools in `tools/` directory
- Inherit from `BaseTool` class
- Register custom handler in `server.py`

### Testing New Endpoints
- Use `scm_auth_get_token` to verify authentication
- Test individual tools via Claude CLI or `mcp` CLI
- Check MCP server logs (stderr) for debugging

## Performance Considerations

### Startup Time
- OpenAPI parsing happens once at startup
- Expected: < 2 seconds for ~50 API endpoints

### Request Latency
- Dominated by SCM API response time
- No additional overhead from MCP layer (simple passthrough)

### Concurrent Requests
- httpx.AsyncClient supports concurrent requests
- MCP stdio transport is sequential (one request at a time from Claude)

## Future Enhancements (Out of Scope)

- ❌ Local caching of API responses
- ❌ Webhook support for real-time updates
- ❌ Batch operations (must be added to SCM API first)
- ❌ GraphQL interface (SCM uses REST only)

---

**Last Updated**: 2026-07-02  
**Architecture Reviewer**: Claude Sonnet 4.5
