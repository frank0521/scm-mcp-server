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

**Ideal Format**: `scm_<module>_<action>_<resource>`
- Module: `auth`, `iam`, `sase`, `cloudngfw`, `subscription`, `tenancy`
- Action: `list`, `get`, `create`, `update`, `delete`
- Resource: singular/plural noun (e.g., `service_accounts`, `security_rule`)

**Ideal Examples**:
- `scm_iam_list_service_accounts` (GET /iam/v1/service-accounts)
- `scm_iam_create_access_policy` (POST /iam/v1/access-policies)
- `scm_sase_list_security_rules` (GET /config/security/v1/security-rules)
- `scm_sase_update_address_object` (PUT /config/objects/v1/addresses/{id})

**Actual Implementation Note** (as of 0.1.0):

Tool names are derived from OpenAPI `operationId` fields. When `operationId` is present, the tool name is `scm_{operationId}` (converted to lowercase with hyphens replaced by underscores). When `operationId` is absent, the name is derived from the HTTP method and path.

**Actual Naming Patterns Observed** (from E2E testing, 916 tools):

1. **operationId-based** (most common):
   - `scm_addurladminoverride` (operationId: `addUrlAdminOverride`)
   - `scm_listauthenticationrules` (operationId: `listAuthenticationRules`)
   - `scm_createaddress` (operationId: `createAddress`)
   - `scm_get-iam-v1-service_accounts` (operationId: `get-iam-v1-service_accounts`)

2. **Prefixed module names** (CIE DSS, posture management):
   - `scm_ciedss_create_cache_groups` (module prefix preserved)
   - `scm_batchdeleteposturechecks` (batch operations)
   - `scm_batchupsertposturechecks`

3. **Autocomplete utilities**:
   - `scm_autocompletehagateways`
   - `scm_autocompletehaipaddresses`
   - `scm_autocompletehanetmasks`

4. **Job/operation tools**:
   - `scm_bgppolicyexport` (async job initiation)
   - `scm_configaudit`

**Naming Inconsistencies**:
- Some tools lack module prefix (e.g., `scm_addurladminoverride` instead of `scm_url_add_admin_override`)
- CamelCase in operationId is flattened to lowercase (no underscores between words)
- Duplicate names across SASE/Cloud NGFW/NGFW specs (latest definition wins)

**Deduplication Strategy**:
When multiple OpenAPI files define the same operationId, the parser uses the **latest definition** encountered during filesystem traversal. This is logged as a warning but does not cause errors. Approximately 200+ duplicate tool names exist across the 41 OpenAPI files.

**Recommendation for Future Versions**:
- Normalize operationId-based names to follow `<module>_<action>_<resource>` pattern
- Add module prefix when missing
- Implement deterministic deduplication (e.g., prefer SASE > Cloud NGFW > NGFW)

## MCP Tools Mapping

**Total Tools**: 168 (Batch 1: 98, Batch 2: 70)

### Tool Naming Convention
- **Format**: `{action}_{resource}` (lowercase_underscore)
- **Actions**: `list`, `get`, `create`, `update`, `delete`, `move`
- **Write operations** marked with "⚠️ 写操作" in description

### Organization
- **Batch 1 (MVP)**: Core functionality - Objects, Security Rules, Security Profiles (read-only), Operations, IAM (98 tools)
- **Batch 2 (Extended)**: Extended objects and Security Profiles (write operations) (70 tools)

---

## Batch 1: MVP Tools (98 tools)

### 1.1 Objects Core (35 tools)

#### Addresses (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_addresses` | GET | `/config/objects/v1/addresses` | List address objects |
| `get_address` | GET | `/config/objects/v1/addresses/{id}` | Get address object by ID |
| `create_address` | POST | `/config/objects/v1/addresses` | ⚠️ 写操作 Create address object |
| `update_address` | PUT | `/config/objects/v1/addresses/{id}` | ⚠️ 写操作 Update address object |
| `delete_address` | DELETE | `/config/objects/v1/addresses/{id}` | ⚠️ 写操作 Delete address object |

#### Address Groups (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_address_groups` | GET | `/config/objects/v1/address-groups` | List address groups |
| `get_address_group` | GET | `/config/objects/v1/address-groups/{id}` | Get address group by ID |
| `create_address_group` | POST | `/config/objects/v1/address-groups` | ⚠️ 写操作 Create address group |
| `update_address_group` | PUT | `/config/objects/v1/address-groups/{id}` | ⚠️ 写操作 Update address group |
| `delete_address_group` | DELETE | `/config/objects/v1/address-groups/{id}` | ⚠️ 写操作 Delete address group |

#### Services (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_services` | GET | `/config/objects/v1/services` | List service objects |
| `get_service` | GET | `/config/objects/v1/services/{id}` | Get service object by ID |
| `create_service` | POST | `/config/objects/v1/services` | ⚠️ 写操作 Create service object |
| `update_service` | PUT | `/config/objects/v1/services/{id}` | ⚠️ 写操作 Update service object |
| `delete_service` | DELETE | `/config/objects/v1/services/{id}` | ⚠️ 写操作 Delete service object |

#### Service Groups (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_service_groups` | GET | `/config/objects/v1/service-groups` | List service groups |
| `get_service_group` | GET | `/config/objects/v1/service-groups/{id}` | Get service group by ID |
| `create_service_group` | POST | `/config/objects/v1/service-groups` | ⚠️ 写操作 Create service group |
| `update_service_group` | PUT | `/config/objects/v1/service-groups/{id}` | ⚠️ 写操作 Update service group |
| `delete_service_group` | DELETE | `/config/objects/v1/service-groups/{id}` | ⚠️ 写操作 Delete service group |

#### Tags (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_tags` | GET | `/config/objects/v1/tags` | List tag objects |
| `get_tag` | GET | `/config/objects/v1/tags/{id}` | Get tag object by ID |
| `create_tag` | POST | `/config/objects/v1/tags` | ⚠️ 写操作 Create tag object |
| `update_tag` | PUT | `/config/objects/v1/tags/{id}` | ⚠️ 写操作 Update tag object |
| `delete_tag` | DELETE | `/config/objects/v1/tags/{id}` | ⚠️ 写操作 Delete tag object |

#### Application Groups (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_application_groups` | GET | `/config/objects/v1/application-groups` | List application groups |
| `get_application_group` | GET | `/config/objects/v1/application-groups/{id}` | Get application group by ID |
| `create_application_group` | POST | `/config/objects/v1/application-groups` | ⚠️ 写操作 Create application group |
| `update_application_group` | PUT | `/config/objects/v1/application-groups/{id}` | ⚠️ 写操作 Update application group |
| `delete_application_group` | DELETE | `/config/objects/v1/application-groups/{id}` | ⚠️ 写操作 Delete application group |

#### External Dynamic Lists (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_external_dynamic_lists` | GET | `/config/objects/v1/external-dynamic-lists` | List external dynamic lists |
| `get_external_dynamic_list` | GET | `/config/objects/v1/external-dynamic-lists/{id}` | Get external dynamic list by ID |
| `create_external_dynamic_list` | POST | `/config/objects/v1/external-dynamic-lists` | ⚠️ 写操作 Create external dynamic list |
| `update_external_dynamic_list` | PUT | `/config/objects/v1/external-dynamic-lists/{id}` | ⚠️ 写操作 Update external dynamic list |
| `delete_external_dynamic_list` | DELETE | `/config/objects/v1/external-dynamic-lists/{id}` | ⚠️ 写操作 Delete external dynamic list |

---

### 1.2 Security Rules (23 tools)

#### Security Rules (6 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_security_rules` | GET | `/config/security/v1/security-rules` | List security rules |
| `get_security_rule` | GET | `/config/security/v1/security-rules/{id}` | Get security rule by ID |
| `create_security_rule` | POST | `/config/security/v1/security-rules` | ⚠️ 写操作 Create security rule |
| `update_security_rule` | PUT | `/config/security/v1/security-rules/{id}` | ⚠️ 写操作 Update security rule |
| `delete_security_rule` | DELETE | `/config/security/v1/security-rules/{id}` | ⚠️ 写操作 Delete security rule |
| `move_security_rule` | POST | `/config/security/v1/security-rules/{id}:move` | ⚠️ 写操作 Move security rule position |

#### Decryption Rules (6 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_decryption_rules` | GET | `/config/security/v1/decryption-rules` | List decryption rules |
| `get_decryption_rule` | GET | `/config/security/v1/decryption-rules/{id}` | Get decryption rule by ID |
| `create_decryption_rule` | POST | `/config/security/v1/decryption-rules` | ⚠️ 写操作 Create decryption rule |
| `update_decryption_rule` | PUT | `/config/security/v1/decryption-rules/{id}` | ⚠️ 写操作 Update decryption rule |
| `delete_decryption_rule` | DELETE | `/config/security/v1/decryption-rules/{id}` | ⚠️ 写操作 Delete decryption rule |
| `move_decryption_rule` | POST | `/config/security/v1/decryption-rules/{id}:move` | ⚠️ 写操作 Move decryption rule position |

#### App Override Rules (6 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_app_override_rules` | GET | `/config/security/v1/app-override-rules` | List app override rules |
| `get_app_override_rule` | GET | `/config/security/v1/app-override-rules/{id}` | Get app override rule by ID |
| `create_app_override_rule` | POST | `/config/security/v1/app-override-rules` | ⚠️ 写操作 Create app override rule |
| `update_app_override_rule` | PUT | `/config/security/v1/app-override-rules/{id}` | ⚠️ 写操作 Update app override rule |
| `delete_app_override_rule` | DELETE | `/config/security/v1/app-override-rules/{id}` | ⚠️ 写操作 Delete app override rule |
| `move_app_override_rule` | POST | `/config/security/v1/app-override-rules/{id}:move` | ⚠️ 写操作 Move app override rule position |

#### DoS Protection Rules (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_dos_protection_rules` | GET | `/config/security/v1/dos-protection-rules` | List DoS protection rules |
| `get_dos_protection_rule` | GET | `/config/security/v1/dos-protection-rules/{id}` | Get DoS protection rule by ID |
| `create_dos_protection_rule` | POST | `/config/security/v1/dos-protection-rules` | ⚠️ 写操作 Create DoS protection rule |
| `update_dos_protection_rule` | PUT | `/config/security/v1/dos-protection-rules/{id}` | ⚠️ 写操作 Update DoS protection rule |
| `delete_dos_protection_rule` | DELETE | `/config/security/v1/dos-protection-rules/{id}` | ⚠️ 写操作 Delete DoS protection rule |

---

### 1.3 Security Profiles (Read-Only) (20 tools)

#### Anti-Spyware Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_anti_spyware_profiles` | GET | `/config/security/v1/anti-spyware-profiles` | List anti-spyware profiles |
| `get_anti_spyware_profile` | GET | `/config/security/v1/anti-spyware-profiles/{id}` | Get anti-spyware profile by ID |

#### Vulnerability Protection Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_vulnerability_protection_profiles` | GET | `/config/security/v1/vulnerability-protection-profiles` | List vulnerability protection profiles |
| `get_vulnerability_protection_profile` | GET | `/config/security/v1/vulnerability-protection-profiles/{id}` | Get vulnerability protection profile by ID |

#### URL Filtering Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_url_filtering_profiles` | GET | `/config/security/v1/url-filtering-profiles` | List URL filtering profiles |
| `get_url_filtering_profile` | GET | `/config/security/v1/url-filtering-profiles/{id}` | Get URL filtering profile by ID |

#### File Blocking Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_file_blocking_profiles` | GET | `/config/security/v1/file-blocking-profiles` | List file blocking profiles |
| `get_file_blocking_profile` | GET | `/config/security/v1/file-blocking-profiles/{id}` | Get file blocking profile by ID |

#### Wildfire Anti-Virus Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_wildfire_anti_virus_profiles` | GET | `/config/security/v1/wildfire-anti-virus-profiles` | List Wildfire anti-virus profiles |
| `get_wildfire_anti_virus_profile` | GET | `/config/security/v1/wildfire-anti-virus-profiles/{id}` | Get Wildfire anti-virus profile by ID |

#### DNS Security Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_dns_security_profiles` | GET | `/config/security/v1/dns-security-profiles` | List DNS security profiles |
| `get_dns_security_profile` | GET | `/config/security/v1/dns-security-profiles/{id}` | Get DNS security profile by ID |

#### DoS Protection Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_dos_protection_profiles` | GET | `/config/security/v1/dos-protection-profiles` | List DoS protection profiles |
| `get_dos_protection_profile` | GET | `/config/security/v1/dos-protection-profiles/{id}` | Get DoS protection profile by ID |

#### Security Profile Groups (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_security_profile_groups` | GET | `/config/security/v1/profile-groups` | List security profile groups |
| `get_security_profile_group` | GET | `/config/security/v1/profile-groups/{id}` | Get security profile group by ID |

#### Decryption Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_decryption_profiles` | GET | `/config/security/v1/decryption-profiles` | List decryption profiles |
| `get_decryption_profile` | GET | `/config/security/v1/decryption-profiles/{id}` | Get decryption profile by ID |

#### Zone Protection Profiles (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_zone_protection_profiles` | GET | `/config/security/v1/zone-protection-profiles` | List zone protection profiles |
| `get_zone_protection_profile` | GET | `/config/security/v1/zone-protection-profiles/{id}` | Get zone protection profile by ID |

---

### 1.4 Operations (8 tools)

#### Jobs (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_jobs` | GET | `/config/operations/v1/jobs` | List configuration jobs |
| `get_job` | GET | `/config/operations/v1/jobs/{id}` | Get job status by ID |

#### Config Versions (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_config_versions` | GET | `/config/operations/v1/config-versions` | List configuration versions |
| `get_config_version` | GET | `/config/operations/v1/config-versions/{version}` | Get specific config version |

#### Candidate Config (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `push_candidate_config` | POST | `/config/operations/v1/config-versions:push` | ⚠️ 写操作 Push candidate config |
| `load_candidate_config` | POST | `/config/operations/v1/config-versions/{version}:load` | ⚠️ 写操作 Load config version as candidate |

#### Running Config (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `commit_config` | POST | `/config/operations/v1/jobs:commit` | ⚠️ 写操作 Commit candidate to running config |
| `get_running_config` | GET | `/config/operations/v1/running-config` | Get current running config |

---

### 1.5 IAM (12 tools)

#### Service Accounts (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_service_accounts` | GET | `/iam/v1/service-accounts` | List service accounts |
| `get_service_account` | GET | `/iam/v1/service-accounts/{id}` | Get service account by ID |
| `create_service_account` | POST | `/iam/v1/service-accounts` | ⚠️ 写操作 Create service account |
| `update_service_account` | PUT | `/iam/v1/service-accounts/{id}` | ⚠️ 写操作 Update service account |
| `delete_service_account` | DELETE | `/iam/v1/service-accounts/{id}` | ⚠️ 写操作 Delete service account |

#### Roles (4 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_roles` | GET | `/iam/v1/roles` | List IAM roles |
| `get_role` | GET | `/iam/v1/roles/{id}` | Get role by ID |
| `create_role` | POST | `/iam/v1/roles` | ⚠️ 写操作 Create custom role |
| `delete_role` | DELETE | `/iam/v1/roles/{id}` | ⚠️ 写操作 Delete custom role |

#### Access Policies (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_access_policies` | GET | `/iam/v1/access-policies` | List access policies |
| `create_access_policy` | POST | `/iam/v1/access-policies` | ⚠️ 写操作 Create access policy |
| `delete_access_policy` | DELETE | `/iam/v1/access-policies/{id}` | ⚠️ 写操作 Delete access policy |

---

## Batch 2: Extended Tools (70 tools)

### 2.1 Objects Extended (40 tools)

#### Applications (2 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_applications` | GET | `/config/objects/v1/applications` | List application objects |
| `get_application` | GET | `/config/objects/v1/applications/{id}` | Get application object by ID |

#### Application Filters (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_application_filters` | GET | `/config/objects/v1/application-filters` | List application filters |
| `get_application_filter` | GET | `/config/objects/v1/application-filters/{id}` | Get application filter by ID |
| `create_application_filter` | POST | `/config/objects/v1/application-filters` | ⚠️ 写操作 Create application filter |
| `update_application_filter` | PUT | `/config/objects/v1/application-filters/{id}` | ⚠️ 写操作 Update application filter |
| `delete_application_filter` | DELETE | `/config/objects/v1/application-filters/{id}` | ⚠️ 写操作 Delete application filter |

#### Schedules (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_schedules` | GET | `/config/objects/v1/schedules` | List schedule objects |
| `get_schedule` | GET | `/config/objects/v1/schedules/{id}` | Get schedule object by ID |
| `create_schedule` | POST | `/config/objects/v1/schedules` | ⚠️ 写操作 Create schedule object |
| `update_schedule` | PUT | `/config/objects/v1/schedules/{id}` | ⚠️ 写操作 Update schedule object |
| `delete_schedule` | DELETE | `/config/objects/v1/schedules/{id}` | ⚠️ 写操作 Delete schedule object |

#### Regions (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_regions` | GET | `/config/objects/v1/regions` | List region objects |
| `get_region` | GET | `/config/objects/v1/regions/{id}` | Get region object by ID |
| `create_region` | POST | `/config/objects/v1/regions` | ⚠️ 写操作 Create region object |
| `update_region` | PUT | `/config/objects/v1/regions/{id}` | ⚠️ 写操作 Update region object |
| `delete_region` | DELETE | `/config/objects/v1/regions/{id}` | ⚠️ 写操作 Delete region object |

#### HIP Objects (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_hip_objects` | GET | `/config/objects/v1/hip-objects` | List HIP objects |
| `get_hip_object` | GET | `/config/objects/v1/hip-objects/{id}` | Get HIP object by ID |
| `create_hip_object` | POST | `/config/objects/v1/hip-objects` | ⚠️ 写操作 Create HIP object |
| `update_hip_object` | PUT | `/config/objects/v1/hip-objects/{id}` | ⚠️ 写操作 Update HIP object |
| `delete_hip_object` | DELETE | `/config/objects/v1/hip-objects/{id}` | ⚠️ 写操作 Delete HIP object |

#### HIP Profiles (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_hip_profiles` | GET | `/config/objects/v1/hip-profiles` | List HIP profiles |
| `get_hip_profile` | GET | `/config/objects/v1/hip-profiles/{id}` | Get HIP profile by ID |
| `create_hip_profile` | POST | `/config/objects/v1/hip-profiles` | ⚠️ 写操作 Create HIP profile |
| `update_hip_profile` | PUT | `/config/objects/v1/hip-profiles/{id}` | ⚠️ 写操作 Update HIP profile |
| `delete_hip_profile` | DELETE | `/config/objects/v1/hip-profiles/{id}` | ⚠️ 写操作 Delete HIP profile |

#### Log Forwarding Profiles (5 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_log_forwarding_profiles` | GET | `/config/objects/v1/log-forwarding-profiles` | List log forwarding profiles |
| `get_log_forwarding_profile` | GET | `/config/objects/v1/log-forwarding-profiles/{id}` | Get log forwarding profile by ID |
| `create_log_forwarding_profile` | POST | `/config/objects/v1/log-forwarding-profiles` | ⚠️ 写操作 Create log forwarding profile |
| `update_log_forwarding_profile` | PUT | `/config/objects/v1/log-forwarding-profiles/{id}` | ⚠️ 写操作 Update log forwarding profile |
| `delete_log_forwarding_profile` | DELETE | `/config/objects/v1/log-forwarding-profiles/{id}` | ⚠️ 写操作 Delete log forwarding profile |

#### HTTP Server Profiles (4 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_http_server_profiles` | GET | `/config/objects/v1/http-server-profiles` | List HTTP server profiles |
| `get_http_server_profile` | GET | `/config/objects/v1/http-server-profiles/{id}` | Get HTTP server profile by ID |
| `create_http_server_profile` | POST | `/config/objects/v1/http-server-profiles` | ⚠️ 写操作 Create HTTP server profile |
| `delete_http_server_profile` | DELETE | `/config/objects/v1/http-server-profiles/{id}` | ⚠️ 写操作 Delete HTTP server profile |

#### Syslog Server Profiles (4 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `list_syslog_server_profiles` | GET | `/config/objects/v1/syslog-server-profiles` | List syslog server profiles |
| `get_syslog_server_profile` | GET | `/config/objects/v1/syslog-server-profiles/{id}` | Get syslog server profile by ID |
| `create_syslog_server_profile` | POST | `/config/objects/v1/syslog-server-profiles` | ⚠️ 写操作 Create syslog server profile |
| `delete_syslog_server_profile` | DELETE | `/config/objects/v1/syslog-server-profiles/{id}` | ⚠️ 写操作 Delete syslog server profile |

---

### 2.2 Security Profiles (Write Operations) (30 tools)

#### Anti-Spyware Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_anti_spyware_profile` | POST | `/config/security/v1/anti-spyware-profiles` | ⚠️ 写操作 Create anti-spyware profile |
| `update_anti_spyware_profile` | PUT | `/config/security/v1/anti-spyware-profiles/{id}` | ⚠️ 写操作 Update anti-spyware profile |
| `delete_anti_spyware_profile` | DELETE | `/config/security/v1/anti-spyware-profiles/{id}` | ⚠️ 写操作 Delete anti-spyware profile |

#### Vulnerability Protection Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_vulnerability_protection_profile` | POST | `/config/security/v1/vulnerability-protection-profiles` | ⚠️ 写操作 Create vulnerability protection profile |
| `update_vulnerability_protection_profile` | PUT | `/config/security/v1/vulnerability-protection-profiles/{id}` | ⚠️ 写操作 Update vulnerability protection profile |
| `delete_vulnerability_protection_profile` | DELETE | `/config/security/v1/vulnerability-protection-profiles/{id}` | ⚠️ 写操作 Delete vulnerability protection profile |

#### URL Filtering Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_url_filtering_profile` | POST | `/config/security/v1/url-filtering-profiles` | ⚠️ 写操作 Create URL filtering profile |
| `update_url_filtering_profile` | PUT | `/config/security/v1/url-filtering-profiles/{id}` | ⚠️ 写操作 Update URL filtering profile |
| `delete_url_filtering_profile` | DELETE | `/config/security/v1/url-filtering-profiles/{id}` | ⚠️ 写操作 Delete URL filtering profile |

#### File Blocking Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_file_blocking_profile` | POST | `/config/security/v1/file-blocking-profiles` | ⚠️ 写操作 Create file blocking profile |
| `update_file_blocking_profile` | PUT | `/config/security/v1/file-blocking-profiles/{id}` | ⚠️ 写操作 Update file blocking profile |
| `delete_file_blocking_profile` | DELETE | `/config/security/v1/file-blocking-profiles/{id}` | ⚠️ 写操作 Delete file blocking profile |

#### Wildfire Anti-Virus Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_wildfire_anti_virus_profile` | POST | `/config/security/v1/wildfire-anti-virus-profiles` | ⚠️ 写操作 Create Wildfire anti-virus profile |
| `update_wildfire_anti_virus_profile` | PUT | `/config/security/v1/wildfire-anti-virus-profiles/{id}` | ⚠️ 写操作 Update Wildfire anti-virus profile |
| `delete_wildfire_anti_virus_profile` | DELETE | `/config/security/v1/wildfire-anti-virus-profiles/{id}` | ⚠️ 写操作 Delete Wildfire anti-virus profile |

#### DNS Security Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_dns_security_profile` | POST | `/config/security/v1/dns-security-profiles` | ⚠️ 写操作 Create DNS security profile |
| `update_dns_security_profile` | PUT | `/config/security/v1/dns-security-profiles/{id}` | ⚠️ 写操作 Update DNS security profile |
| `delete_dns_security_profile` | DELETE | `/config/security/v1/dns-security-profiles/{id}` | ⚠️ 写操作 Delete DNS security profile |

#### DoS Protection Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_dos_protection_profile` | POST | `/config/security/v1/dos-protection-profiles` | ⚠️ 写操作 Create DoS protection profile |
| `update_dos_protection_profile` | PUT | `/config/security/v1/dos-protection-profiles/{id}` | ⚠️ 写操作 Update DoS protection profile |
| `delete_dos_protection_profile` | DELETE | `/config/security/v1/dos-protection-profiles/{id}` | ⚠️ 写操作 Delete DoS protection profile |

#### Security Profile Groups (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_security_profile_group` | POST | `/config/security/v1/profile-groups` | ⚠️ 写操作 Create security profile group |
| `update_security_profile_group` | PUT | `/config/security/v1/profile-groups/{id}` | ⚠️ 写操作 Update security profile group |
| `delete_security_profile_group` | DELETE | `/config/security/v1/profile-groups/{id}` | ⚠️ 写操作 Delete security profile group |

#### Decryption Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_decryption_profile` | POST | `/config/security/v1/decryption-profiles` | ⚠️ 写操作 Create decryption profile |
| `update_decryption_profile` | PUT | `/config/security/v1/decryption-profiles/{id}` | ⚠️ 写操作 Update decryption profile |
| `delete_decryption_profile` | DELETE | `/config/security/v1/decryption-profiles/{id}` | ⚠️ 写操作 Delete decryption profile |

#### Zone Protection Profiles (3 tools)
| Tool Name | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `create_zone_protection_profile` | POST | `/config/security/v1/zone-protection-profiles` | ⚠️ 写操作 Create zone protection profile |
| `update_zone_protection_profile` | PUT | `/config/security/v1/zone-protection-profiles/{id}` | ⚠️ 写操作 Update zone protection profile |
| `delete_zone_protection_profile` | DELETE | `/config/security/v1/zone-protection-profiles/{id}` | ⚠️ 写操作 Delete zone protection profile |

---

## OpenAPI Source Files

All tools are extracted from the following OpenAPI specifications:

| Domain | Source File | Tools Count |
|--------|-------------|-------------|
| **Objects** | `config/sase/objects/objects-june.yaml` | 75 tools |
| **Security** | `config/sase/security/security-services-R2-2026.yaml` | 53 tools |
| **Operations** | `config/sase/operations/config-operations-march.yaml` | 8 tools |
| **IAM** | `iam/ServiceAccounts.yaml`, `iam/Roles.yaml`, `iam/AccessPolicies.yaml` | 12 tools |
| **Total** | 4 OpenAPI files | **168 tools** |

**Note**: Auth endpoints (`auth/AuthService.yaml`) are NOT exposed as tools. OAuth2 token management is handled internally by `auth.py`.

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
