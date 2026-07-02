# SCM MCP Server - Project Summary

## Overview
Model Context Protocol (MCP) server that enables Claude, Cursor, and other MCP clients to interact with Palo Alto Networks Strata Cloud Manager (SCM) API using natural language.

## Project Structure

```
scm-mcp-server/
├── Documentation (Context Stack Layers)
│   ├── CLAUDE.md                   # L1: Engineering contract (immutable rules)
│   ├── DESIGN.md                   # L2: Architecture design
│   ├── WORKFLOW.md                 # L3: Implementation workflow
│   └── README.md                   # L4: User documentation
│
├── Project Configuration
│   ├── pyproject.toml              # Python project config
│   ├── .env.example                # Environment variable template
│   ├── .gitignore                  # Git ignore rules
│   └── CHANGELOG.md                # Version history
│
├── Source Code
│   └── src/scm_mcp/
│       ├── __init__.py             # Package initialization
│       ├── server.py               # MCP server entry point
│       ├── auth.py                 # OAuth2 authentication
│       ├── client.py               # SCM REST client (httpx)
│       ├── openapi_parser.py       # OpenAPI spec parser
│       └── tools/
│           ├── __init__.py
│           └── base.py             # Tool base class (extensibility)
│
└── Testing
    ├── tests/integration_test.sh   # Integration test script
    └── verify_installation.sh      # Installation verification
```

## Key Features

### 1. Dynamic Tool Generation
- Tools automatically generated from OpenAPI YAML specifications
- No manual tool definition required
- Add new SCM endpoints → restart server → tools available

### 2. OAuth2 Authentication
- Client credentials flow
- Automatic token refresh
- Token caching with expiration handling

### 3. Full API Coverage
Supports all SCM API modules:
- **Auth**: Token management
- **IAM**: Service accounts, access policies, roles, permissions
- **SASE Config**: Security rules, address objects, services
- **Cloud NGFW**: Configuration management
- **NGFW**: Device operations
- **Subscription**: License management
- **Tenancy**: Tenant service groups

### 4. Zero Business Logic
- Pure proxy layer (no state management)
- Transparent error handling
- Direct API response passthrough

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.11+ | Modern async/await support |
| MCP SDK | `mcp >= 0.9.0` | Official protocol implementation |
| HTTP Client | `httpx >= 0.27.0` | Async HTTP requests |
| Schema Parser | `pyyaml >= 6.0` | OpenAPI YAML parsing |
| Data Validation | `pydantic >= 2.0` | Runtime type checking |
| Config Management | `python-dotenv >= 1.0.0` | Environment variables |

## Architecture Principles

### Single Source of Truth (SSOT)
- OpenAPI specs are the **only** source for API contracts
- No manual schema duplication
- No hardcoded endpoints or parameters

### Immutable Technology Stack
Defined in CLAUDE.md, cannot be changed:
- Python (not Node.js, Go, etc.)
- Official MCP SDK (not custom implementation)
- stdio transport (not HTTP/WebSocket)
- httpx (not requests/aiohttp)

### Configuration Sources
All configuration from environment variables:
- `SCM_CLIENT_ID`: OAuth2 client ID
- `SCM_CLIENT_SECRET`: OAuth2 client secret
- `SCM_TSG_ID`: Tenant Service Group ID
- `SCM_BASE_URL`: API base URL (optional, defaults to production)

## Installation & Usage

### Quick Start
```bash
# 1. Install
cd ~/vibe-coding/scm-mcp-server
pip install -e .

# 2. Configure environment
export SCM_CLIENT_ID="your-client-id"
export SCM_CLIENT_SECRET="your-secret"
export SCM_TSG_ID="your-tsg-id"

# 3. Verify installation
./verify_installation.sh

# 4. Run integration test (optional)
./tests/integration_test.sh

# 5. Configure Claude CLI
# Edit ~/.claude/claude_desktop_config.json (see README.md)

# 6. Start using with Claude
# Claude: "List all service accounts in SCM"
```

### Verification Steps
See [WORKFLOW.md](WORKFLOW.md) Phase 6 for complete acceptance criteria.

## File Roles

### Documentation (Context Stack)

#### CLAUDE.md (L1 - Engineering Contract)
- **Purpose**: Define immutable project constraints
- **Audience**: AI assistants, future developers
- **Content**: Technology stack rules, prohibitions, SSOT principles
- **When to read**: Before ANY code changes

#### DESIGN.md (L2 - Architecture Design)
- **Purpose**: Explain system architecture and design decisions
- **Audience**: Developers implementing features
- **Content**: Component design, data flow, API mappings, tool definitions
- **When to read**: Before implementing new features or debugging

#### WORKFLOW.md (L3 - Implementation Workflow)
- **Purpose**: Define implementation phases with acceptance criteria
- **Audience**: Developers building the project from scratch
- **Content**: 7 phases with tasks, verification steps, estimated time
- **When to read**: During initial implementation or major refactors

#### README.md (L4 - User Documentation)
- **Purpose**: Help end users install, configure, and use the server
- **Audience**: SCM users, Claude CLI users, DevOps engineers
- **Content**: Installation, configuration, usage examples, troubleshooting
- **When to read**: During setup or when encountering issues

### Source Code

#### server.py
- **Entry point** for MCP server
- Initializes OAuth2, parses OpenAPI specs
- Registers tools dynamically
- Dispatches tool calls to SCM API

#### auth.py
- **OAuth2 authentication** with client_credentials flow
- Token caching and automatic refresh
- Environment variable loading

#### client.py
- **SCM REST client** wrapper around httpx
- Automatic Bearer token injection
- 401 error handling with token refresh
- Error detail extraction

#### openapi_parser.py
- **OpenAPI spec parser**
- Recursively finds YAML files
- Generates ToolDefinition objects
- Resolves JSON Schema $ref pointers

#### tools/base.py
- **Extensibility layer** (optional)
- Abstract base class for custom tools
- Use only if custom logic is needed beyond REST calls

## Dependencies on External Projects

### pan.dev Repository
- **Location**: `../pan.dev/openapi-specs/scm/`
- **Purpose**: OpenAPI specifications for SCM API
- **Maintenance**: Maintained by Palo Alto Networks
- **Update strategy**: Pull latest pan.dev → restart server → new tools available

### SCM API
- **Base URL**: `https://api.strata.paloaltonetworks.com`
- **Authentication**: OAuth2 client credentials
- **Rate limits**: (Check SCM documentation)
- **API versioning**: Handled per endpoint (e.g., `/iam/v1/...`)

## Development Workflow

### Adding New Tools
1. Update OpenAPI spec in pan.dev repository (if needed)
2. Restart MCP server
3. Tools automatically available (no code changes required)

### Debugging
```bash
# Check tool definitions
python -m scm_mcp.server --list

# Test authentication
python -c "
import asyncio
from scm_mcp.auth import OAuth2Manager
asyncio.run(OAuth2Manager.from_env().get_access_token())
"

# Test OpenAPI parsing
python -c "
from scm_mcp.openapi_parser import parse_all_specs
tools = parse_all_specs()
print(f'{len(tools)} tools parsed')
"

# View server logs
# (stderr output when running server)
```

### Testing Strategy
1. **Unit tests**: (Not yet implemented) Test individual components
2. **Integration tests**: `./tests/integration_test.sh` - End-to-end verification
3. **Manual tests**: Use Claude CLI to call tools

## Security Considerations

### Credential Management
- ✅ Environment variables only (never commit .env)
- ✅ Token stored in memory only (not persisted)
- ✅ HTTPS for all API calls
- ⚠️  Rotate credentials regularly

### API Permissions
- Server inherits service account permissions
- Use principle of least privilege
- Monitor usage in SCM audit logs

### Input Validation
- MCP SDK validates against JSON Schema
- OpenAPI schemas define allowed inputs
- No SQL injection risk (REST API only)
- No command injection risk (no shell execution)

## Known Limitations

### Current Version (0.1.0)
- No response caching (every call hits SCM API)
- No batch operations (one tool call = one API request)
- No webhook support (polling only)
- Sequential tool execution (MCP protocol limitation)

### By Design (Won't Fix)
- No local state management (stateless proxy only)
- No alternative auth methods (OAuth2 only)
- No non-REST protocols (HTTP/HTTPS only)
- No custom business logic (passthrough only)

## Future Roadmap

### Planned (Not Yet Implemented)
- [ ] Response caching (configurable TTL)
- [ ] Rate limiting awareness
- [ ] Batch operations (if SCM API supports)
- [ ] Enhanced logging and metrics
- [ ] Docker containerization
- [ ] Unit test suite
- [ ] CI/CD pipeline

### Out of Scope
- ❌ Local database persistence
- ❌ API key authentication
- ❌ WebSocket transport
- ❌ Alternative HTTP libraries

## Troubleshooting Quick Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing required environment variables` | Credentials not set | Export `SCM_CLIENT_ID`, `SCM_CLIENT_SECRET`, `SCM_TSG_ID` |
| `FileNotFoundError: ../pan.dev` | OpenAPI specs not found | Clone pan.dev repository to `~/vibe-coding/pan.dev` |
| `401 Unauthorized` | Invalid credentials or expired token | Verify credentials in SCM UI, check TSG ID |
| `Tool not found` | Server using old OpenAPI specs | Restart MCP server to reload tools |
| `403 Forbidden` | Service account lacks permissions | Check access policies in SCM IAM |
| `Connection timeout` | Network issues | Check connectivity to `api.strata.paloaltonetworks.com` |

## Maintenance Checklist

### Regular (Weekly)
- [ ] Check for OpenAPI spec updates in pan.dev
- [ ] Review server logs for errors
- [ ] Verify all tools still function

### Periodic (Monthly)
- [ ] Rotate OAuth2 credentials
- [ ] Update Python dependencies
- [ ] Review and update documentation

### As Needed
- [ ] Add custom tools (rare, most should be auto-generated)
- [ ] Update error handling logic
- [ ] Performance optimization (if needed)

## Support & Resources

### Documentation
- [README.md](README.md) - User guide
- [DESIGN.md](DESIGN.md) - Architecture
- [WORKFLOW.md](WORKFLOW.md) - Implementation guide
- [CLAUDE.md](CLAUDE.md) - Engineering contract

### External Resources
- SCM API Documentation: https://pan.dev/scm/api/
- MCP Protocol: https://modelcontextprotocol.io/
- pan.dev Repository: https://github.com/PaloAltoNetworks/pan.dev

### Getting Help
1. Check troubleshooting section in README.md
2. Review DESIGN.md for architecture questions
3. Consult pan.dev for SCM API documentation
4. Open issue in project repository

---

**Version**: 0.1.0  
**Last Updated**: 2026-07-02  
**Maintainer**: Frank Fan  
**License**: MIT (to be confirmed)
