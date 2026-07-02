# Changelog

All notable changes to SCM MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-02

### Added
- Initial release of SCM MCP Server
- OAuth2 client_credentials authentication with automatic token refresh
- Dynamic tool generation from OpenAPI specifications
- Support for all SCM API modules:
  - Authentication (auth/)
  - IAM (iam/)
  - SASE Configuration (config/sase/)
  - Cloud NGFW Configuration (config/cloudngfw/)
  - NGFW Configuration (config/ngfw/)
  - Subscription (subscription/)
  - Tenancy (tenancy/)
- MCP server with stdio transport
- Comprehensive documentation:
  - CLAUDE.md - Engineering contract
  - DESIGN.md - Architecture design
  - WORKFLOW.md - Implementation workflow
  - README.md - User documentation
- Integration test script
- Example environment configuration

### Technical Details
- Python 3.11+ support
- Dependencies: mcp, httpx, pyyaml, pydantic, python-dotenv
- Automatic OpenAPI schema parsing
- Error transparency (SCM API errors passed through)
- Async/await throughout for performance

[unreleased]: https://github.com/yourusername/scm-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/scm-mcp-server/releases/tag/v0.1.0
