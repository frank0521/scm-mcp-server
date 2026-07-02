# IAM Policies and Permissions Guide
# SCM MCP Server

**Version**: 0.1.0  
**Last Updated**: 2026-07-02  
**Status**: Draft (requires validation with SCM product team)

---

## Overview

This document provides IAM policy examples for SCM MCP Server service accounts following the **principle of least privilege**. Each policy grants only the minimum permissions required for specific use cases.

**Important**: These policies are **examples** and should be validated against your organization's security requirements and SCM API documentation.

---

## Prerequisites

### Understanding SCM IAM Model

**Key Concepts**:
- **Service Account**: OAuth2 client credentials for API access
- **Access Policy**: Binds service account to roles within TSG scope
- **Role**: Collection of permissions (predefined or custom)
- **TSG (Tenant Service Group)**: Logical isolation boundary

**Policy Structure**:
```json
{
  "name": "policy-name",
  "principal": {
    "service_account_id": "sa-123456"
  },
  "resource": {
    "tsg_id": "1234567890"
  },
  "roles": ["role-id-1", "role-id-2"]
}
```

---

## Use Case 1: Read-Only Monitoring

**Scenario**: Platform operations team needs to monitor license status, TSG resources, and configuration compliance without making changes.

**Required Permissions**:
- ✅ Read service accounts, access policies, roles
- ✅ Read licenses, subscriptions
- ✅ Read security rules, address objects, services
- ✅ Read device configurations
- ❌ No create/update/delete permissions

**Example Access Policy**:
```json
{
  "name": "scm-mcp-readonly-policy",
  "description": "Read-only access for monitoring and compliance auditing",
  "principal": {
    "service_account_id": "sa-readonly-bot"
  },
  "resource": {
    "tsg_id": "1234567890",
    "folders": ["All"]
  },
  "roles": [
    "iam:read",
    "subscription:read",
    "config:read",
    "operations:read"
  ]
}
```

**Recommended SCM Roles** (may vary by SCM version):
- `iam:read` - View IAM resources
- `subscription:read` - View licenses and instances
- `config:read` - View SASE/NGFW configurations
- `operations:read` - View device status and jobs

**Testing**:
```bash
# Verify service account can list resources
python -m scm_mcp.server --list | grep -E "list|get"

# Test with Claude:
# "Show me all licenses that expire within 30 days"
# "List all security rules in Production folder"
```

---

## Use Case 2: Configuration Management (Read + Write)

**Scenario**: Security engineers need to create and modify security policies, address objects, and services but should not delete resources or access IAM management.

**Required Permissions**:
- ✅ Read/create/update security rules
- ✅ Read/create/update address objects and groups
- ✅ Read/create/update services and applications
- ✅ Read (but not modify) IAM resources
- ❌ No delete permissions
- ❌ No IAM write permissions

**Example Access Policy**:
```json
{
  "name": "scm-mcp-config-manager-policy",
  "description": "Configuration management for security policies",
  "principal": {
    "service_account_id": "sa-config-manager"
  },
  "resource": {
    "tsg_id": "1234567890",
    "folders": ["Development", "Staging", "Production"]
  },
  "roles": [
    "config:write",
    "config:read",
    "iam:read"
  ],
  "conditions": {
    "exclude_actions": ["delete"]
  }
}
```

**Recommended SCM Roles**:
- `config:write` - Create and update configurations
- `config:read` - View configurations
- `iam:read` - View IAM resources (for auditing)

**Conditional Exclusions**:
- Exclude `DELETE` method for all resources
- Limit scope to specific folders (not "All")

**Testing**:
```bash
# Test create operation
# Claude: "Create an address object named 'test-host' with IP 192.168.1.1"

# Test update operation
# Claude: "Update security rule 'allow-internal' to include source 10.0.0.0/8"

# Verify delete is blocked (should return 403)
# Claude: "Delete address object 'test-host'"
```

---

## Use Case 3: IAM Administration

**Scenario**: IAM administrators need to manage service accounts, access policies, and roles but should not access configuration or operational data.

**Required Permissions**:
- ✅ Read/create/update/delete service accounts
- ✅ Read/create/update/delete access policies
- ✅ Read/create/update custom roles
- ✅ Read permission sets
- ❌ No access to SASE/NGFW configurations
- ❌ No access to subscription/license data

**Example Access Policy**:
```json
{
  "name": "scm-mcp-iam-admin-policy",
  "description": "IAM administration for service account management",
  "principal": {
    "service_account_id": "sa-iam-admin"
  },
  "resource": {
    "tsg_id": "1234567890"
  },
  "roles": [
    "iam:admin"
  ]
}
```

**Recommended SCM Roles**:
- `iam:admin` - Full IAM management permissions

**Security Considerations**:
- ⚠️ This is a **high-privilege** role
- Use separate service account (not shared with config management)
- Enable audit logging for all IAM changes
- Rotate credentials frequently (e.g., every 30 days)

**Testing**:
```bash
# Test service account creation
# Claude: "Create a new service account for CI/CD pipeline"

# Test access policy assignment
# Claude: "Assign read-only role to service account sa-123"

# Verify config access is blocked (should return 403)
# Claude: "List security rules"
```

---

## Use Case 4: Full Admin (Emergency Access)

**Scenario**: Break-glass account for emergency operations requiring full access to all resources.

**Required Permissions**:
- ✅ All IAM permissions
- ✅ All configuration permissions
- ✅ All subscription/license permissions
- ✅ All operational permissions
- ✅ Delete permissions

**Example Access Policy**:
```json
{
  "name": "scm-mcp-emergency-admin-policy",
  "description": "Emergency break-glass account - full access",
  "principal": {
    "service_account_id": "sa-emergency-admin"
  },
  "resource": {
    "tsg_id": "1234567890",
    "folders": ["All"]
  },
  "roles": [
    "superadmin"
  ]
}
```

**Recommended SCM Roles**:
- `superadmin` or equivalent highest-privilege role

**Security Requirements**:
- 🔒 Store credentials in secure vault (e.g., AWS Secrets Manager)
- 🔒 Require multi-factor authentication for vault access
- 🔒 Enable detailed audit logging
- 🔒 Set credential expiration (e.g., 7 days)
- 🔒 Alert on credential usage
- 🔒 Require incident ticket number for access

**Usage Guidelines**:
- Only use during incidents or critical operations
- Document reason for access in change management system
- Rotate credentials immediately after use
- Review audit logs within 24 hours

---

## Permission Matrix

| Operation | Read-Only | Config Manager | IAM Admin | Full Admin |
|-----------|-----------|----------------|-----------|------------|
| **IAM: List Service Accounts** | ✅ | ✅ | ✅ | ✅ |
| **IAM: Create Service Account** | ❌ | ❌ | ✅ | ✅ |
| **IAM: Delete Service Account** | ❌ | ❌ | ✅ | ✅ |
| **Config: List Security Rules** | ✅ | ✅ | ❌ | ✅ |
| **Config: Create Security Rule** | ❌ | ✅ | ❌ | ✅ |
| **Config: Update Security Rule** | ❌ | ✅ | ❌ | ✅ |
| **Config: Delete Security Rule** | ❌ | ❌ | ❌ | ✅ |
| **Config: List Address Objects** | ✅ | ✅ | ❌ | ✅ |
| **Config: Create Address Object** | ❌ | ✅ | ❌ | ✅ |
| **Subscription: List Licenses** | ✅ | ✅ | ❌ | ✅ |
| **Operations: List Devices** | ✅ | ✅ | ❌ | ✅ |

---

## Creating Service Accounts and Policies

### Step 1: Create Service Account via SCM UI

1. Navigate to **Settings → Identity & Access → Service Accounts**
2. Click **Create Service Account**
3. Enter name (e.g., `scm-mcp-readonly-bot`)
4. Enter contact email
5. Add description (e.g., "Read-only monitoring for SCM MCP Server")
6. Click **Create**
7. **Save credentials** (Client ID and Secret) securely

### Step 2: Create Access Policy via SCM UI

1. Navigate to **Settings → Identity & Access → Access Policies**
2. Click **Create Access Policy**
3. Enter policy name (e.g., `scm-mcp-readonly-policy`)
4. Select **Service Account** as principal (choose the one created above)
5. Select **TSG** as resource scope
6. Assign roles (e.g., `iam:read`, `config:read`, `subscription:read`)
7. Click **Create**

### Step 3: Configure SCM MCP Server

```bash
export SCM_CLIENT_ID="<client-id-from-step-1>"
export SCM_CLIENT_SECRET="<client-secret-from-step-1>"
export SCM_TSG_ID="<your-tsg-id>"
```

### Step 4: Verify Permissions

```bash
# Test authentication
python -c "
import asyncio
from scm_mcp.auth import OAuth2Manager

async def test():
    oauth = OAuth2Manager.from_env()
    token = await oauth.get_access_token()
    print('Authentication successful')

asyncio.run(test())
"

# Test permissions with Claude
# Claude: "List all service accounts"
# Expected: Success for read-only, config manager, IAM admin, full admin
# Expected: 403 Forbidden for service accounts with no IAM read permission
```

---

## Troubleshooting

### Error: 403 Forbidden

**Symptoms**:
```
HTTPStatusError: 403 Forbidden
```

**Possible Causes**:
1. Service account lacks required role for the operation
2. TSG scope is incorrect
3. Folder access is restricted

**Resolution**:
1. Check access policy in SCM UI
2. Verify role assignments include required permissions
3. Confirm TSG ID matches the one in access policy
4. Check folder restrictions (if using folder-scoped policies)

---

### Error: 401 Unauthorized

**Symptoms**:
```
Authentication failed (HTTP 401)
```

**Possible Causes**:
1. Invalid Client ID or Secret
2. Service account disabled or deleted
3. Credentials expired (if short-lived)

**Resolution**:
1. Verify credentials in SCM UI (Settings → Service Accounts)
2. Check if service account is active
3. Regenerate credentials if needed

---

### Error: Token has insufficient permissions

**Symptoms**:
Tool call succeeds but returns empty results or partial data.

**Possible Causes**:
- Token has read permission but not for the specific resource type
- Folder-level restrictions limiting visibility

**Resolution**:
1. Review access policy roles
2. Test with broader permissions temporarily to isolate issue
3. Check SCM audit logs for permission denials

---

## Security Best Practices

### 1. Credential Management
- ✅ Store credentials in secret management system (AWS Secrets Manager, HashiCorp Vault)
- ✅ Use short-lived credentials when possible (e.g., 1-7 days)
- ✅ Rotate credentials regularly (every 30-90 days)
- ✅ Never commit credentials to git repositories
- ✅ Use separate service accounts per use case (read-only, config, IAM)

### 2. Audit and Monitoring
- ✅ Enable SCM audit logging for all API calls
- ✅ Monitor for unexpected tool usage (e.g., delete operations from read-only account)
- ✅ Set up alerts for authentication failures
- ✅ Review audit logs weekly
- ✅ Track service account usage metrics

### 3. Least Privilege Enforcement
- ✅ Start with read-only permissions
- ✅ Add write permissions only when required
- ✅ Avoid "superadmin" or "full admin" roles except for break-glass accounts
- ✅ Use folder-scoped policies instead of TSG-wide when possible
- ✅ Exclude delete permissions by default

### 4. Testing and Validation
- ✅ Test new policies in non-production TSG first
- ✅ Verify both positive (allowed) and negative (denied) test cases
- ✅ Document expected permissions in policy description
- ✅ Maintain test scripts for permission validation

---

## Open Questions (Pending SCM Product Team Clarification)

1. **Q1**: What are the exact predefined role names in SCM IAM?
   - Status: Awaiting SCM documentation
   - Examples above use assumed role names (`iam:read`, `config:write`, etc.)

2. **Q2**: Can conditional access policies exclude specific HTTP methods (e.g., DELETE)?
   - Status: Feature capability unknown
   - Alternative: Use custom roles without delete permissions

3. **Q3**: What is the minimum permission set for "read-only monitoring"?
   - Status: Needs testing with real SCM environment
   - May vary by SCM version

4. **Q4**: Are folder-scoped policies available for all resource types?
   - Status: Unknown
   - May be limited to configuration resources only

5. **Q5**: Can service accounts access multiple TSGs with different policies?
   - Status: Awaiting product team confirmation
   - Current implementation assumes single TSG per server instance

---

## References

- **SCM API Documentation**: https://pan.dev/scm/api/iam/
- **PRD Risk Assessment**: [../docs/PRD.md](PRD.md) § 5.1 Risk 3: Token Scope Too Broad
- **Security Guide**: [SECURITY-GUIDE.md](SECURITY-GUIDE.md) (to be created)
- **OpenAPI Specs**: `../pan.dev/openapi-specs/scm/iam/`

---

**Document Status**: Draft - Requires validation with real SCM environment  
**Next Review**: After MVP 0.1.0 release with real credential testing  
**Approval Required**: Security Team, SCM Product Team
