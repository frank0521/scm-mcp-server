# Product Requirements Document (PRD)
# SCM MCP Server

**Version**: 0.1.0  
**Last Updated**: 2026-07-02  
**Status**: Draft  
**Owner**: Frank Fan

---

## 1. Target Users & Core Scenarios

### 1.1 User Personas

#### **Network Security Engineer**
**Role**: Day-to-day security policy management  
**Pain Points**:
- Manual SCM UI navigation is slow for repetitive tasks
- Need to cross-reference multiple objects (address, service, rule) across screens
- Want to query configurations using natural language instead of learning REST API

**Core Scenarios**:
- "Show me all security rules that reference address object '10.0.0.0/8'"
- "Create a new address object named 'corp-dmz' with IP 192.168.100.0/24"
- "List all security rules in folder 'Production' that have action 'allow'"

#### **Platform Operations Engineer**
**Role**: Monitor and maintain SCM infrastructure health  
**Pain Points**:
- Need to check license status, TSG resources, and device health across multiple tenants
- Manual API calls require writing scripts or using curl
- Want quick status checks without context switching

**Core Scenarios**:
- "List all licenses that expire within 30 days"
- "Show me all Tenant Service Groups I have access to"
- "Get the total count of security rules across all folders"

#### **Security Architect**
**Role**: Cross-environment consistency and compliance auditing  
**Pain Points**:
- Need to audit configurations across dev/staging/prod environments
- Manual comparison is error-prone and time-consuming
- Want to verify policy alignment without exporting/importing files

**Core Scenarios**:
- "Compare security rules between 'Development' and 'Production' folders"
- "Audit which address objects are not referenced by any security rule"
- "Show me all security rules that allow traffic from 'any' source"

#### **IAM Administrator**
**Role**: Manage service accounts, access policies, and permissions  
**Pain Points**:
- Need to track service account usage and permissions
- Want to quickly provision/deprovision access for automation scripts
- Audit who has write permissions to critical resources

**Core Scenarios**:
- "List all service accounts and their associated access policies"
- "Create a new service account for the CI/CD pipeline with read-only permissions"
- "Show me which service accounts have permission to delete security rules"

---

## 2. MVP Functional Scope

### 2.1 In Scope (MVP 0.1.0)

**Capability-Based Scope** (specific endpoints defined in `openapi-specs/scm/` YAML files):

#### **Read Operations (GET)**
- ✅ List resources with filtering (limit, offset, folder, etc.)
- ✅ Get specific resource by ID
- ✅ Query across all SCM modules:
  - Authentication tokens
  - IAM (service accounts, access policies, roles, permissions)
  - SASE configuration (security rules, address objects, services, applications)
  - Cloud NGFW configuration
  - NGFW device operations
  - Subscription (licenses, instances)
  - Tenancy (TSGs)

#### **Write Operations (POST/PUT/DELETE)**
- ✅ Create new resources (address objects, security rules, service accounts, etc.)
- ✅ Update existing resources by ID
- ✅ Delete resources by ID
- ⚠️ **No batch operations** (one tool call = one resource)

#### **Authentication & Authorization**
- ✅ OAuth2 client_credentials flow
- ✅ Automatic token refresh on expiration
- ✅ Token caching in memory (not persisted)
- ✅ Support for single TSG per session

#### **Tool Discovery & Execution**
- ✅ Dynamic tool generation from OpenAPI specifications
- ✅ JSON Schema validation for tool inputs
- ✅ Transparent error handling (SCM API errors passed through)

#### **User Experience**
- ✅ Natural language queries via Claude CLI / Cursor
- ✅ Structured JSON responses for programmatic use
- ✅ Clear error messages with actionable guidance

---

### 2.2 Out of Scope (Not in MVP 0.1.0)

#### **Performance & Caching**
- ❌ Local response caching (every request hits SCM API)
- ❌ Query result pagination automation (user must handle offset/limit)
- ❌ Connection pooling optimization (uses httpx defaults)

#### **Batch & Bulk Operations**
- ❌ Bulk create (e.g., create 100 address objects from CSV)
- ❌ Bulk delete (e.g., delete all unused objects)
- ❌ Transactional rollback (if create fails, no automatic cleanup)

#### **Advanced Workflows**
- ❌ Configuration backup/restore
- ❌ Version control integration (Git commit on changes)
- ❌ Change approval workflows
- ❌ Scheduled jobs / cron-based queries

#### **Real-Time Features**
- ❌ Webhook subscriptions for SCM events
- ❌ WebSocket streaming for live updates
- ❌ Push notifications

#### **Multi-Tenancy & Concurrency**
- ❌ Multi-TSG switching within single session
- ❌ Parallel requests to multiple SCM tenants
- ❌ Cross-TSG resource aggregation

#### **Audit & Compliance**
- ❌ Local audit log storage (operations logged by SCM only)
- ❌ Change tracking / diff visualization
- ❌ Compliance report generation

#### **Alternative Protocols**
- ❌ GraphQL interface
- ❌ gRPC support
- ❌ WebSocket transport

---

## 3. Product-Level Data Flow

### 3.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  User Interaction Layer                                             │
│  - Natural language query in Claude CLI / Cursor                    │
│  - Example: "List all security rules in Production folder"          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Claude AI Layer                                                     │
│  - Intent understanding & parameter extraction                      │
│  - Tool selection: scm_sase_list_security_rules                     │
│  - Argument construction: {folder: "Production", limit: 100}        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  MCP Protocol Layer (stdio transport)                               │
│  - JSON-RPC tool call transmission                                  │
│  - Input schema validation (JSON Schema)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SCM MCP Server (This Product)                                      │
│  - OAuth2 token management (fetch/refresh)                          │
│  - HTTP request construction (method, path, params, body)           │
│  - Error handling & response parsing                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SCM REST API (Palo Alto Networks)                                  │
│  - Endpoint: GET /config/security/v1/security-rules                 │
│  - Authentication: Bearer <OAuth2 token>                            │
│  - Response: JSON array of security rule objects                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Response Flow (Reverse Path)                                       │
│  1. SCM API → MCP Server (JSON response)                            │
│  2. MCP Server → Claude (structured data)                           │
│  3. Claude → User (natural language summary + structured display)   │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Error Flow

```
SCM API Error (e.g., 404 Not Found)
    ↓
MCP Server extracts error details
    ↓
Returns error to Claude with status code + message
    ↓
Claude interprets error and informs user
    ↓
User sees actionable error message:
"Resource not found: security rule with ID 'abc-123' does not exist"
```

### 3.3 Authentication Flow

```
First Tool Call
    ↓
OAuth2Manager checks token cache
    ↓
No valid token → Fetch new token from /auth/v1/oauth2/access_token
    ↓
Cache token with expiration timestamp
    ↓
Use token for API request
    ↓
If 401 Unauthorized → Refresh token + Retry once
```

---

**Technical Details**: For tool-to-REST endpoint mapping, see [DESIGN.md § MCP Tools Mapping](../DESIGN.md#mcp-tools-mapping).

**Implementation Details**: For code-level data flow, see [DESIGN.md § Data Flow Example](../DESIGN.md#data-flow-example).

---

## 4. Acceptance Criteria

All criteria are **observable** and **verifiable** through testing.

### 4.1 Functional Acceptance

#### **Read Operations**
- [ ] **AC-F1**: User can execute "List all service accounts" via Claude CLI and receive at least 1 service account in response (if any exist)
- [ ] **AC-F2**: User can execute "Get service account with ID X" and receive the correct service account object
- [ ] **AC-F3**: User can filter resources using query parameters (e.g., "Show security rules in folder 'Production'") and results match the folder parameter
- [ ] **AC-F4**: User can paginate results by specifying limit/offset and receive the expected number of items

#### **Write Operations**
- [ ] **AC-F5**: User can create a new address object via Claude and verify its existence in SCM UI
- [ ] **AC-F6**: User can update an existing resource and verify changes in SCM UI
- [ ] **AC-F7**: User can delete a test resource and verify its removal via subsequent GET request returning 404
- [ ] **AC-F8**: Write operations return the created/updated resource ID in the response

#### **Authentication**
- [ ] **AC-F9**: When `SCM_CLIENT_ID` is invalid, the error message contains "Authentication failed" and mentions credentials
- [ ] **AC-F10**: When token expires mid-session, the next tool call automatically refreshes the token and succeeds (no user intervention required)
- [ ] **AC-F11**: After token refresh, subsequent tool calls use the new token without re-authentication

#### **Error Handling**
- [ ] **AC-F12**: When requesting a non-existent resource (404), the error message contains "not found" and the resource ID
- [ ] **AC-F13**: When API returns 403 Forbidden, the error message indicates permission issues and suggests checking IAM policies
- [ ] **AC-F14**: When network timeout occurs, the error message states "Connection timeout" with the SCM API URL
- [ ] **AC-F15**: When API returns 5xx errors, the error message includes the status code and raw error response

---

### 4.2 Performance Acceptance

- [ ] **AC-P1**: Server startup (including OpenAPI parsing) completes within **5 seconds**
- [ ] **AC-P2**: Tool call latency overhead is **≤ 50ms** beyond SCM API response time (measured via logs)
- [ ] **AC-P3**: OpenAPI parser successfully generates tool definitions from **100% of valid YAML files** in `openapi-specs/scm/`
- [ ] **AC-P4**: Server handles **10 sequential tool calls** without memory leaks (memory usage increases ≤ 10MB)

---

### 4.3 Security Acceptance

- [ ] **AC-S1**: `SCM_CLIENT_SECRET` does **not appear** in any log output (check stderr logs)
- [ ] **AC-S2**: OAuth2 token is **not persisted** to disk (verify no token files created in filesystem)
- [ ] **AC-S3**: Token is **cleared from memory** when server shuts down (no plaintext token in core dumps)
- [ ] **AC-S4**: For destructive operations (DELETE), Claude explicitly asks user for confirmation before execution (MCP protocol behavior, not server-enforced)
- [ ] **AC-S5**: Requests to SCM API use **HTTPS only** (verify via network logs)

---

### 4.4 Usability Acceptance

- [ ] **AC-U1**: User can configure the server by following README.md without external documentation (measure: ≤ 10 minutes from clone to first tool call)
- [ ] **AC-U2**: When OpenAPI specs are missing, error message provides the exact command to clone `pan.dev` repository
- [ ] **AC-U3**: When environment variables are missing, error message lists all missing variable names (e.g., "Missing: SCM_CLIENT_ID, SCM_TSG_ID")
- [ ] **AC-U4**: Tool names are human-readable and follow the pattern `scm_<module>_<action>_<resource>` (e.g., `scm_iam_list_service_accounts`)

---

### 4.5 Integration Acceptance

- [ ] **AC-I1**: Server works with **Claude CLI** on macOS (verified via manual test)
- [ ] **AC-I2**: Server works with **Cursor** editor (verified via manual test)
- [ ] **AC-I3**: Tools appear in Claude's tool list when server is configured in `claude_desktop_config.json`
- [ ] **AC-I4**: Tool descriptions are visible and accurate in MCP client's tool discovery interface

---

## 5. Risks & Open Questions

### 5.1 Critical Risks

#### **Risk 1: Credential Leakage**
**Impact**: High - Compromised OAuth2 credentials grant full API access  
**Probability**: Medium - User error or logging misconfiguration  
**Mitigation**:
- ✅ Implemented: `.env` in `.gitignore`
- ✅ Implemented: Secrets not logged to stderr
- ✅ Implemented: Token stored in memory only
- 🔄 Recommended: Document short-lived credential rotation policy
- 🔄 Recommended: Use secret management service (e.g., AWS Secrets Manager) for production

**Status**: Partially mitigated, requires user discipline

---

#### **Risk 2: Accidental Write Operations**
**Impact**: High - Unintended deletion/modification of production resources  
**Probability**: Medium - User misunderstands Claude's intent or gives ambiguous instructions  
**Mitigation**:
- ✅ Implemented: No batch delete operations
- ⚠️ Partial: Claude typically confirms destructive actions (not guaranteed by protocol)
- 🔄 Recommended: Document read-only testing workflow with separate service account
- 🔄 Recommended: Require explicit "confirm: true" parameter for DELETE operations (not in MVP)

**Status**: Requires user caution + IAM best practices

---

#### **Risk 3: Token Scope Too Broad**
**Impact**: Medium - Service account has more permissions than necessary (violates least privilege)  
**Probability**: High - Users may reuse existing admin-level service accounts  
**Mitigation**:
- 🔄 Needed: Document minimal IAM policy examples per use case
- 🔄 Needed: Provide sample access policies for read-only, config-only, IAM-only workflows
- 🔄 Needed: Tool usage guidance for "least privilege by scenario"

**Status**: Documentation gap, needs user guidance

---

#### **Risk 4: API Version Drift**
**Impact**: Medium - Tools break when SCM API deprecates endpoints or changes schemas  
**Probability**: Medium - SCM API evolves over time  
**Mitigation**:
- ✅ Implemented: OpenAPI specs as single source of truth
- 🔄 Needed: Monitor `pan.dev` repository for changes
- 🔄 Needed: Automated CI/CD to detect schema changes
- 🔄 Needed: Deprecation warning handling (if SCM API provides it)

**Status**: Requires ongoing maintenance process

---

### 5.2 Medium Risks

#### **Risk 5: Rate Limiting**
**Impact**: Low - Excessive API calls blocked by SCM rate limits  
**Probability**: Low - Claude's sequential tool calls unlikely to hit limits  
**Mitigation**:
- ✅ Implemented: Transparent 429 error passthrough
- ✅ Implemented: No automatic retry loops (avoids amplifying rate limit issues)
- 🔄 Recommended: Document expected rate limits (if known)

**Status**: Handled by design

---

#### **Risk 6: Network Reliability**
**Impact**: Low - Timeouts or connection failures interrupt user workflows  
**Probability**: Medium - Corporate proxies, VPNs, or SCM API outages  
**Mitigation**:
- ✅ Implemented: 30-second timeout (configurable)
- ✅ Implemented: Clear error messages for network issues
- 🔄 Recommended: Document proxy configuration steps

**Status**: Acceptable for MVP

---

### 5.3 Open Questions (Require Clarification)

| # | Question | Impact | Owner | Deadline |
|---|----------|--------|-------|----------|
| **Q1** | What are SCM API's global rate limits (requests per minute/hour)? | Medium | SCM Product Team | Before GA |
| **Q2** | What is the minimal IAM policy for read-only operations? | High | Security Team | Before MVP release |
| **Q3** | Do write operations require approval workflows in enterprise deployments? | High | Customer Success | Before MVP release |
| **Q4** | Can a single service account access multiple TSGs simultaneously? | Low | SCM Product Team | Nice-to-have |
| **Q5** | How often does `pan.dev` OpenAPI repository update? | Medium | pan.dev Maintainers | Before CI/CD setup |
| **Q6** | Are there SCM API deprecation notices or sunset timelines? | Medium | SCM Product Team | Before GA |
| **Q7** | What is the maximum page size (limit parameter) for list operations? | Low | SCM Product Team | Before docs finalize |
| **Q8** | Do tokens have IP address restrictions or other conditional access policies? | Medium | Security Team | Before production use |

---

### 5.4 Assumptions (Requiring Validation)

1. **Assumption**: SCM API is stable and backwards-compatible within major versions  
   **Risk if wrong**: Frequent tool breakage  
   **Validation**: Review SCM API changelog and versioning policy

2. **Assumption**: OAuth2 token expiration is communicated via `expires_in` field  
   **Risk if wrong**: Token refresh logic fails  
   **Validation**: Test with real SCM credentials

3. **Assumption**: All SCM modules use consistent error response formats  
   **Risk if wrong**: Error parsing fails for some endpoints  
   **Validation**: Test error scenarios across all modules

4. **Assumption**: OpenAPI specs in `pan.dev` accurately reflect production API  
   **Risk if wrong**: Generated tools have incorrect schemas  
   **Validation**: Cross-check sample requests against live API

5. **Assumption**: Claude respects user intent for destructive operations (asks for confirmation)  
   **Risk if wrong**: Accidental deletes occur  
   **Validation**: Test with multiple destructive scenarios

---

### 5.5 Dependencies & External Risks

| Dependency | Risk | Mitigation |
|------------|------|------------|
| **pan.dev repository** | Specs become outdated or unmaintained | Fork repository if needed; establish update cadence |
| **SCM API availability** | Downtime blocks all operations | Document offline mode limitations (none in MVP) |
| **MCP protocol stability** | Breaking changes in MCP SDK | Pin `mcp` version; test upgrades in dev first |
| **Claude API behavior** | Changes in tool calling semantics | Monitor Anthropic updates; regression test |

---

## 6. Success Metrics (Post-MVP)

Not required for MVP validation, but tracked for future iterations:

- **Adoption**: Number of active Claude CLI users with SCM server configured
- **Usage**: Average tool calls per user per week
- **Reliability**: Tool call success rate (target: > 95%)
- **Performance**: P95 latency for tool calls (target: < 2 seconds end-to-end)
- **Support**: Reduction in manual API scripting requests to platform team

---

## 7. Compliance & Security Notes

### 7.1 Data Handling
- No SCM data is stored locally (stateless proxy)
- All data flows through memory only
- Logs contain request metadata but not response payloads

### 7.2 Credential Management
- Credentials sourced from environment variables or secure vaults
- No plaintext credentials in configuration files
- Token lifetime follows SCM API defaults (typically 1 hour)

### 7.3 Audit Trail
- Tool executions logged to stderr (timestamp, tool name, user)
- SCM API maintains authoritative audit logs
- Recommend enabling SCM audit logging for compliance

---

## 8. References

- **Technical Architecture**: [DESIGN.md](../DESIGN.md)
- **Implementation Workflow**: [WORKFLOW.md](../WORKFLOW.md)
- **Engineering Contract**: [CLAUDE.md](../CLAUDE.md)
- **User Documentation**: [README.md](../README.md)
- **SCM API Documentation**: https://pan.dev/scm/api/
- **OpenAPI Specifications**: `../pan.dev/openapi-specs/scm/`

---

**Document Status**: Draft - Pending stakeholder review  
**Next Review**: Before MVP 0.1.0 release  
**Approval Required**: Product Owner, Security Team, Platform Engineering
