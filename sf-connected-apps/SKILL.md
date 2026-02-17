---
name: sf-connected-apps
description: >
  Creates and manages Salesforce Connected Apps and External Client Apps with
  120-point scoring. Use when configuring OAuth flows, creating connected apps,
  setting up JWT bearer auth, or managing API access policies.
license: MIT
allowed-tools: Bash Read Write Edit Glob Grep WebFetch AskUserQuestion TodoWrite
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
---

# sf-connected-apps: Salesforce Connected Apps & External Client Apps

Expert in creating and managing Salesforce Connected Apps and External Client Apps (ECAs) with OAuth configuration, security best practices, and metadata compliance.

## Core Responsibilities

1. **Connected App Generation**: Create Connected Apps with OAuth 2.0 configuration, scopes, and callbacks
2. **External Client App Generation**: Create ECAs with modern security model and separation of concerns
3. **Security Review**: Analyze OAuth configurations for security best practices
4. **Validation & Scoring**: Score apps against 6 categories (0-120 points)
5. **Migration Guidance**: Help migrate from Connected Apps to External Client Apps

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:

| # | Question | Key Options |
|---|----------|-------------|
| 1 | App Type | Connected App / External Client App |
| 2 | OAuth Flow | Authorization Code, JWT Bearer, Device, Client Credentials |
| 3 | Use Case | API Integration, SSO, Mobile, CI/CD |
| 4 | Scopes | api, refresh_token, full, web, etc. |
| 5 | Distribution | Local / Packageable (multi-org) |

**Then**:
1. Check existing: `Glob: **/*.connectedApp-meta.xml`, `Glob: **/*.eca-meta.xml`
2. Create TodoWrite tasks

### Phase 2: App Type Selection

| Criteria | Connected App | External Client App |
|----------|--------------|---------------------|
| Single Org | ✓ Good | ✓ Good |
| Multi-Org | ⚠️ Manual | ✓ 2GP Packaging |
| Secret Mgmt | ⚠️ Visible | ✓ Hidden in sandboxes |
| Key Rotation | ⚠️ Manual | ✓ API-driven |
| Audit Trail | ⚠️ Limited | ✓ MFA + audit |
| API Version | Any | 61.0+ required |

**Quick Decision**:
- **Multi-org or ISV** → External Client App
- **Regulated industry** → External Client App (audit requirements)
- **Simple single-org** → Connected App sufficient
- **Automated DevOps** → External Client App (key rotation)

### Phase 3: Template Selection & Generation

**Template Locations** (try in order):
1. `~/.claude/plugins/marketplaces/sf-skills/sf-connected-apps/templates/[template]`
2. `[project-root]/sf-connected-apps/templates/[template]`

**Template Selection**:

| App Type | Template File | Flow Type |
|----------|---------------|-----------|
| Connected App (Basic) | `connected-app-basic.xml` | Minimal OAuth |
| Connected App (Full) | `connected-app-oauth.xml` | Web Server Flow |
| Connected App (JWT) | `connected-app-jwt.xml` | Server-to-Server |
| Connected App (Canvas) | `connected-app-canvas.xml` | Canvas Apps |
| External Client App | `external-client-app.xml` | Base ECA |
| ECA OAuth (Global) | `eca-global-oauth.xml` | Global settings |
| ECA OAuth (Instance) | `eca-oauth-settings.xml` | Per-org settings |

**Output Locations**:
- Connected Apps: `force-app/main/default/connectedApps/`
- External Client Apps: `force-app/main/default/externalClientApps/`

### Phase 4: Security Validation & Scoring

**Scoring Categories**:
```
Score: XX/120 ⭐⭐⭐⭐
├─ Security: XX/30 (PKCE, token rotation, IP restrictions, certificates)
├─ OAuth Config: XX/25 (callbacks, flows, token expiration, OIDC)
├─ Metadata: XX/20 (required fields, API version, naming)
├─ Best Practices: XX/20 (minimal scopes, named principal, pre-auth)
├─ Scopes: XX/15 (least privilege, no deprecated)
└─ Documentation: XX/10 (description, contact email)
```

**Thresholds**:

| Score | Action | Meaning |
|-------|--------|---------|
| **80-120** | ✅ Deploy | Production-ready |
| **54-79** | ⚠️ Review | May need hardening |
| **<54** | ❌ Block | Security risk - fix first |

> 📋 **Detailed scoring**: See Phase 4 in previous version for point breakdown per criteria.

### Phase 5: Deployment & Documentation

**Deploy**:
```
Skill(skill="sf-deploy", args="Deploy connected apps to [target-org] with --dry-run")
```

**Completion Output**:
```
✓ App Created: [AppName]
  Type: [Connected App | External Client App]
  Location: force-app/main/default/[connectedApps|externalClientApps]/
  OAuth Flow: [flow]
  Scopes: [list]
  Score: XX/120

Next Steps:
- Retrieve Consumer Key from Setup > App Manager
- Test OAuth flow (Postman/curl)
- For ECA: Configure policies in subscriber org
```

---

## Quick Reference: OAuth Flow Selection

| Use Case | Flow | PKCE | Secret | Template |
|----------|------|------|--------|----------|
| Web Backend | Authorization Code | Optional | Yes | `connected-app-oauth.xml` |
| SPA/Mobile | Authorization Code | Required | No | `external-client-app.xml` |
| Server-to-Server | JWT Bearer | N/A | Certificate | `connected-app-jwt.xml` |
| CI/CD | JWT Bearer | N/A | Certificate | `connected-app-jwt.xml` |
| CLI/IoT | Device | N/A | No | `connected-app-basic.xml` |
| Service Account | Client Credentials | N/A | Yes | `eca-oauth-settings.xml` (ECA only) |

> 📘 **Detailed flows**: See [resources/oauth-flows-reference.md](resources/oauth-flows-reference.md) for implementation patterns, security checklists, and code examples.

---

## Metadata Structure Essentials

### Connected App XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ConnectedApp xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My Integration App</label>
    <contactEmail>admin@company.com</contactEmail>
    <description>Integration description</description>

    <!-- OAuth Configuration -->
    <oauthConfig>
        <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
        <certificate>MyCertificate</certificate> <!-- JWT Bearer only -->
        <scopes>Api</scopes>
        <scopes>RefreshToken</scopes>
        <isAdminApproved>true</isAdminApproved>
        <isConsumerSecretOptional>false</isConsumerSecretOptional>
        <isPkceRequired>true</isPkceRequired> <!-- Public clients -->
    </oauthConfig>

    <!-- OAuth Policy -->
    <oauthPolicy>
        <ipRelaxation>ENFORCE</ipRelaxation>
        <refreshTokenPolicy>infinite</refreshTokenPolicy>
        <isRefreshTokenRotationEnabled>true</isRefreshTokenRotationEnabled>
    </oauthPolicy>
</ConnectedApp>
```

### External Client App Files

**1. Header File** (`[AppName].eca-meta.xml`):
```xml
<ExternalClientApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My External Client App</label>
    <contactEmail>admin@company.com</contactEmail>
    <description>Modern integration</description>
    <distributionState>Local</distributionState> <!-- or Packageable -->
</ExternalClientApplication>
```

**2. Global OAuth** (`[AppName].ecaGlblOauth-meta.xml`):
```xml
<ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
    <externalClientApplication>My_App_Name</externalClientApplication>
    <label>Global OAuth Settings</label>
    <isPkceRequired>true</isPkceRequired>
    <isConsumerSecretOptional>true</isConsumerSecretOptional>
</ExtlClntAppGlobalOauthSettings>
```

> ⚠️ **Important**: File suffix is `.ecaGlblOauth` (abbreviated), NOT `.ecaGlobalOauth`

**3. Instance OAuth** (`[AppName].ecaOauth-meta.xml`):
```xml
<ExtlClntAppOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <externalClientApplication>My_App_Name</externalClientApplication>
    <commaSeparatedOauthScopes>api,refresh_token</commaSeparatedOauthScopes>
    <label>Instance OAuth Settings</label>
    <isClientCredentialsEnabled>false</isClientCredentialsEnabled>
</ExtlClntAppOauthSettings>
```

---

## OAuth Scopes Reference

| Scope Display Name | API Name | Use Case |
|-------------------|----------|----------|
| Access and manage your data | `Api` | REST/SOAP API access |
| Perform requests at any time | `RefreshToken` | Offline access |
| Full access | `Full` | Complete access (use sparingly) |
| Access your basic information | `OpenID` | OpenID Connect |
| Web access | `Web` | Web browser access |
| Access Chatter | `ChatterApi` | Chatter REST API |
| Access custom permissions | `CustomPermissions` | Custom permissions |
| Access Einstein Analytics | `Wave` | Analytics API |

---

## Security Best Practices

| Anti-Pattern | Risk | Fix | Score Impact |
|--------------|------|-----|--------------|
| Wildcard callback | Token hijacking | Specific URLs | -10 points |
| `Full` scope everywhere | Over-privileged | Minimal scopes | -15 points |
| No token expiration | Long-term compromise | Set expiration | -5 points |
| Secret in code | Credential leak | Named Credentials | -15 points |
| PKCE disabled (mobile) | Code interception | Enable PKCE | -10 points |
| No IP restrictions | Unauthorized access | Configure IP ranges | -5 points |

> 🔒 **Security details**: See [docs/security-checklist.md](docs/security-checklist.md) for comprehensive security review.

---

## Scratch Org Setup (External Client Apps)

```json
{
  "orgName": "ECA Development Org",
  "edition": "Developer",
  "features": [
    "ExternalClientApps",
    "ExtlClntAppSecretExposeCtl"
  ]
}
```

---

## Common CLI Commands

```bash
# List Connected Apps in org
sf org list metadata --metadata-type ConnectedApp --target-org [alias]

# Retrieve Connected App
sf project retrieve start --metadata ConnectedApp:[AppName] --target-org [alias]

# Deploy
sf project deploy start --source-dir force-app/main/default/connectedApps --target-org [alias]

# Retrieve Consumer Key (after deployment)
# Go to Setup > App Manager > [App] > View
```

---

## Migration: Connected App → External Client App

**Quick Steps**:
1. **Assess**: `Glob: **/*.connectedApp-meta.xml`
2. **Create**: Map OAuth settings to ECA structure
3. **Parallel**: Deploy ECA alongside old app
4. **Test**: Verify flows with new Consumer Key
5. **Cutover**: Update integrations, disable old app
6. **Archive**: Remove after 30-day grace period

**Scoring Benefit**: ECAs typically score 15-20 points higher.

> 📘 **Detailed migration**: See [docs/migration-guide.md](docs/migration-guide.md) for step-by-step process.

---

## Cross-Skill Integration

| Skill | Use Case | Example |
|-------|----------|---------|
| sf-metadata | Named Credentials for callouts | `Skill(skill="sf-metadata")` → "Create Named Credential" |
| sf-deploy | Deploy to org | `Skill(skill="sf-deploy", args="Deploy to [org]")` |
| sf-apex | OAuth token handling | `Skill(skill="sf-apex")` → "Create token refresh service" |

---

## Key Insights

| Insight | Description | Reference |
|---------|-------------|-----------|
| **ECA vs Connected App** | ECAs provide better secret management and 2GP packaging | Phase 2 Decision Matrix |
| **PKCE for Public Clients** | Always required for mobile/SPA apps | [resources/oauth-flows-reference.md](resources/oauth-flows-reference.md) |
| **JWT Bearer for CI/CD** | Server-to-server auth without user interaction | [resources/oauth-flows-reference.md](resources/oauth-flows-reference.md) |
| **Token Rotation** | Enable for SPAs to prevent token reuse | [resources/oauth-flows-reference.md](resources/oauth-flows-reference.md) |
| **Named Credentials** | Store secrets securely, automatic refresh | [resources/oauth-flows-reference.md](resources/oauth-flows-reference.md) |
| **Minimal Scopes** | Use least privilege (api instead of full) | Phase 4 Scoring |
| **IP Restrictions** | Add when integration has known IP ranges | Phase 4 Scoring |
| **Certificate Auth** | Stronger than username/password for JWT | [resources/oauth-flows-reference.md](resources/oauth-flows-reference.md) |

---

## Notes

- **API Version**: 62.0+ recommended, 61.0+ required for External Client Apps
- **Scoring**: Block deployment if score < 54 (54% threshold)
- **Consumer Secret**: Never commit to version control - use environment variables
- **External Client Apps**: Preferred for new development (modern security model)
- **Testing**: Use Postman for OAuth flow testing before production

---

## Additional Resources

### Detailed References
- **OAuth Flow Patterns**: [resources/oauth-flows-reference.md](resources/oauth-flows-reference.md)
  - Implementation examples (Node.js, Python, JavaScript)
  - Security checklists per flow
  - Error handling patterns
  - Named Credentials integration

### Documentation
- **OAuth Flow Diagrams**: [docs/oauth-flows.md](docs/oauth-flows.md)
- **Security Review**: [docs/security-checklist.md](docs/security-checklist.md)
- **Migration Guide**: [docs/migration-guide.md](docs/migration-guide.md)
- **Testing & Validation**: [docs/testing-validation-guide.md](docs/testing-validation-guide.md)

### Examples
- **Usage Examples**: [examples/example-usage.md](examples/example-usage.md)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
