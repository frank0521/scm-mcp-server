# SCM MCP Server - Engineering Contract

## Project Identity
- **Name**: SCM MCP Server
- **Purpose**: Provide Model Context Protocol interface for Palo Alto Networks Strata Cloud Manager (SCM)
- **Technology Stack** (IMMUTABLE): Python 3.11+, official `mcp` SDK, `httpx`, stdio transport

## Technology Stack Rules (MUST NOT CHANGE)

### Core Technologies
1. **Python** as the sole implementation language
2. **Official `mcp` SDK** (not custom protocol implementation)
3. **stdio transport** (not HTTP/WebSocket)
4. **httpx** as HTTP client (not requests/aiohttp)

### Additional Dependencies
- **PyYAML**: OpenAPI specification parsing
- **Pydantic**: Data validation
- **python-dotenv**: Environment variable management

## Directory Structure

```
scm-mcp-server/
├── CLAUDE.md           # This file - L1 engineering contract
├── DESIGN.md           # L2 architecture and API mapping
├── WORKFLOW.md         # L3 implementation phases
├── README.md           # User documentation
├── pyproject.toml      # Python project configuration
├── .env.example        # Environment variable template
├── src/
│   └── scm_mcp/
│       ├── __init__.py
│       ├── server.py           # MCP server entry point
│       ├── auth.py             # OAuth2 client_credentials
│       ├── client.py           # SCM REST client (httpx)
│       ├── openapi_parser.py   # OpenAPI YAML parser
│       └── tools/
│           ├── __init__.py
│           └── base.py         # Tool base class
└── tests/
    └── ...
```

## Single Source of Truth (SSOT)

### OpenAPI as Schema Authority
- **Tool schemas MUST be parsed from OpenAPI YAML files**, not hand-written
- OpenAPI specification location: `../pan.dev/openapi-specs/scm/`
- No manual duplication of API contracts in code
- No fabrication of endpoints or parameters

### No Business Logic Reimplementation
- This server is a **proxy layer only**
- Do NOT reimplement SCM business logic
- Do NOT add local state management (caching, database)
- Each tool maps 1:1 to a REST API call

## Authentication and Configuration

### OAuth2 Requirements
- **Flow**: client_credentials grant type
- **Credential Sources** (environment variables):
  - `SCM_CLIENT_ID`: OAuth2 client ID
  - `SCM_CLIENT_SECRET`: OAuth2 client secret
  - `SCM_TSG_ID`: Tenant Service Group ID

### API Configuration
- **Base URL**: Environment variable `SCM_BASE_URL`
  - Default: `https://api.strata.paloaltonetworks.com`
  - MUST NOT be hardcoded in source code
- **Token endpoint**: `/auth/v1/oauth2/access_token`

## Prohibitions

### Security
- ❌ Do NOT bypass OAuth2 with API keys
- ❌ Do NOT hardcode credentials anywhere
- ❌ Do NOT commit `.env` files with real credentials

### Schema Management
- ❌ Do NOT modify OpenAPI specification files
- ❌ Do NOT manually write tool input schemas
- ❌ Do NOT invent API endpoints not present in OpenAPI specs

### Architecture
- ❌ Do NOT implement local caching
- ❌ Do NOT add database persistence
- ❌ Do NOT change transport from stdio to HTTP/WebSocket
- ❌ Do NOT replace httpx with other HTTP libraries

## Mandatory Behaviors

### Error Handling
- MUST transparently pass SCM API errors to the MCP client
- MUST auto-refresh OAuth2 token on 401 responses
- MUST log authentication failures with actionable messages

### Tool Registration
- MUST dynamically generate tools from OpenAPI specs
- MUST validate input parameters against OpenAPI schemas
- MUST use descriptive tool names: `scm_<module>_<action>_<resource>`
  - Example: `scm_iam_list_service_accounts`

### Code Quality
- MUST use type hints (Python 3.11+ syntax)
- MUST handle async/await properly (httpx is async)
- MUST use structured logging (not print statements)

## OpenAPI Specification Structure

Reference structure (as of 2026-07-02):
```
../pan.dev/openapi-specs/scm/
├── auth/
│   └── AuthService.yaml
├── config/
│   ├── sase/
│   │   ├── security/security-services-R2-2026.yaml
│   │   ├── objects/objects-june.yaml
│   │   ├── operations/config-operations-march.yaml
│   │   └── ...
│   ├── cloudngfw/
│   │   ├── security/security-services.yaml
│   │   ├── objects/objects-june.yaml
│   │   └── ...
│   └── ngfw/...
├── iam/
│   ├── ServiceAccounts.yaml
│   ├── AccessPolicies.yaml
│   └── ...
├── subscription/
│   └── Licenses.yaml
└── tenancy/
    └── TenantServiceGroup.yaml
```

## Version Control
- Main branch: `main`
- OpenAPI specs are maintained in separate repository: `../pan.dev`
- Do NOT vendor OpenAPI specs into this repository

## Testing Requirements
- MUST provide example `.env.example`
- MUST document manual verification steps
- SHOULD include integration test scripts (optional)

## AI Assistant Instructions
When modifying this project:
1. Read this file FIRST before any changes
2. Verify OpenAPI specs exist before parsing
3. Do NOT suggest technology stack changes
4. Do NOT hardcode values that should be environment variables
5. Reject requests to "simplify" by removing OpenAPI parsing

---

**Last Updated**: 2026-07-02  
**Maintainer**: Frank Fan  
**License**: (To be determined)
