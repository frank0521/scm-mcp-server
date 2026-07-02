# Changelog

All notable changes to SCM MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated DESIGN.md with actual tool naming patterns observed in testing
- Updated README.md with virtual environment setup instructions (macOS PEP 668 compliance)

### Added
- docs/PRD.md - Product Requirements Document (4 user personas, MVP scope, 45 acceptance criteria)
- docs/E2E-TEST-REPORT.md - Phase 6 end-to-end test report
- docs/IAM-POLICIES.md - IAM policy examples for least privilege access control
- docs/SECURITY-GUIDE.md - Security best practices and threat mitigation

### Fixed
- Claude CLI configuration examples now include virtual environment Python path
- Installation steps now include virtual environment creation

---

## [0.1.0] - 2026-07-02

### Added

#### Core Features
- **OAuth2 Authentication**: client_credentials flow with automatic token refresh
- **Dynamic Tool Generation**: 916 tools generated from 41 OpenAPI specification files
- **MCP Server**: stdio transport-based server for Claude CLI and Cursor integration
- **Full API Coverage**: Support for all SCM API modules:
  - Authentication (`auth/`)
  - IAM (`iam/`) - Service accounts, access policies, roles, permissions
  - SASE Configuration (`config/sase/`) - Security rules, objects, services
  - Cloud NGFW Configuration (`config/cloudngfw/`)
  - NGFW Configuration (`config/ngfw/`)
  - Subscription (`subscription/`) - Licenses, instances
  - Tenancy (`tenancy/`) - Tenant Service Groups

#### Documentation (Context Stack)
- **L1: CLAUDE.md** - Engineering contract (immutable technology stack rules, SSOT principles)
- **L2: DESIGN.md** - Architecture design (component structure, API mappings, data flow)
- **L3: WORKFLOW.md** - Implementation workflow (7 phases with acceptance criteria)
- **L4: README.md** - User documentation (installation, configuration, usage)
- **Product: docs/PRD.md** - Product requirements (user personas, MVP scope, risks)
- **docs/PROJECT_SUMMARY.md** - Project overview and quick reference
- **docs/E2E-TEST-REPORT.md** - End-to-end testing results and findings
- **docs/IAM-POLICIES.md** - IAM policy examples and security guidance
- **docs/SECURITY-GUIDE.md** - Security best practices and compliance guidelines

#### Testing & Verification
- `tests/integration_test.sh` - Integration test script (auth, parsing, client)
- `verify_installation.sh` - Installation verification script
- End-to-end testing completed (916 tools, 5.09s startup time)

#### Configuration Examples
- `.env.example` - Environment variable template
- `.gitignore` - Secure defaults (excludes credentials, venv, caches)
- Claude CLI configuration examples (with virtual environment support)

### Technical Details

#### Implementation
- **Language**: Python 3.11+ (3.14 tested)
- **Dependencies**:
  - `mcp>=0.9.0` - Official MCP SDK
  - `httpx>=0.27.0` - Async HTTP client
  - `pyyaml>=6.0` - OpenAPI YAML parsing
  - `pydantic>=2.0` - Runtime data validation
  - `python-dotenv>=1.0.0` - Environment configuration
- **Architecture**: Async/await throughout for non-blocking I/O
- **Transport**: stdio (JSON-RPC over stdin/stdout)
- **Authentication**: In-memory token caching with automatic refresh
- **Error Handling**: Transparent SCM API error passthrough

#### Performance (Verified in E2E Testing)
- OpenAPI parsing: **5.09 seconds** for 41 files (< 5s target ✅)
- Tool generation: **916 tools** with 100% success rate
- Server startup: < 6 seconds total (including OpenAPI parsing)
- Memory usage: Stable (no leaks observed in testing)

#### Security
- Credentials from environment variables only (no hardcoding)
- Token stored in memory only (not persisted to disk)
- Secrets not logged to stderr
- HTTPS for all SCM API calls
- JSON Schema input validation (derived from OpenAPI)

### Known Limitations

#### By Design
- No local caching (stateless proxy)
- No batch operations (one tool call = one API request)
- No webhook/real-time event support
- Sequential tool execution (MCP protocol limitation)
- Single TSG per server instance

#### Identified in Testing
- ~200 duplicate tool names across SASE/Cloud NGFW/NGFW specs (latest definition wins)
- Some tool names don't follow ideal `<module>_<action>_<resource>` pattern (based on OpenAPI operationId)
- Virtual environment required on macOS Python 3.14+ (PEP 668)

### Testing Status

#### Completed ✅
- Installation and setup (with virtual environment)
- Module imports and dependency resolution
- OpenAPI parsing (41 files, 916 tools)
- Server initialization and error handling
- Environment variable validation
- Tool listing and discovery

#### Pending (Requires Real SCM Credentials) ⏸️
- OAuth2 authentication with live SCM API
- Token refresh on expiration
- Actual CRUD operations (GET/POST/PUT/DELETE)
- Error scenarios (404, 403, 500, timeout)
- Claude CLI integration testing
- Security validation (credentials not leaked, token not persisted)

[unreleased]: https://github.com/yourusername/scm-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/scm-mcp-server/releases/tag/v0.1.0
