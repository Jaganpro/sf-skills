---
name: sf-connected-apps
description: >
  Creates and manages Salesforce Connected Apps and External Client Apps with
  120-point scoring. Use when configuring OAuth flows, creating connected apps,
  setting up JWT bearer auth, or managing API access policies.
license: MIT
allowed-tools: Bash Read Write Edit Glob Grep WebFetch AskUserQuestion TodoWrite
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
---

# sf-connected-apps: Salesforce Connected Apps & External Client Apps

Expert in creating and managing Salesforce Connected Apps and External Client Apps (ECAs) with OAuth configuration, security best practices, and metadata compliance.

## Core Responsibilities

1. **Connected App Generation**: Create Connected Apps with OAuth 2.0 configuration, scopes, and callbacks
2. **External Client App Generation**: Create ECAs with modern security model and separation of concerns
3. **Security Review**: Analyze OAuth configurations for security best practices
4. **Validation & Scoring**: Score apps against 6 categories (0-120 points)
5. **Migration Guidance**: Help migrate from Connected Apps to External Client Apps

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:

| # | Question | Options |
|---|----------|---------|
| 1 | App Type | Connected App / External Client App |
| 2 | OAuth Flow | Web Server (Authorization Code), User-Agent, JWT Bearer, Device, Refresh Token |
| 3 | Primary Use Case | API Integration, SSO, Canvas App, Mobile App, CI/CD |
| 4 | Scopes Required | api, refresh_token, full, web, chatter_api, etc. |
| 5 | Distribution | Local (single org) / Packageable (multi-org) |

**Then**:
1. Check existing apps: `Glob: **/*.connectedApp-meta.xml`, `Glob: **/*.eca-meta.xml`
2. Check for existing OAuth configurations
3. Create TodoWrite tasks

### Phase 2: App Type Selection

**Decision Matrix**:

| Criteria | Connected App | External Client App (ECA) |
|----------|--------------|--------------------------|
| Single Org | ✓ Good | ✓ Good |
| Multi-Org Distribution | ⚠️ Manual recreation | ✓ Native packaging (2GP) |
| Secret Management | ⚠️ Visible in sandboxes | ✓ Hidden in sandboxes |
| Key Rotation | ⚠️ Manual | ✓ Automatable via API |
| Metadata Compliance | ⚠️ Partial | ✓ Full |
| Audit Trail | ⚠️ Limited | ✓ MFA + audit logging |
| Setup Complexity | Low | Medium |
| Minimum API Version | Any | 61.0+ |

**Recommendation Logic**:
- **Multi-org or ISV**: Always use External Client App
- **Regulated industry**: Use External Client App (audit requirements)
- **Simple single-org**: Connected App is sufficient
- **Automated DevOps**: Use External Client App (key rotation)

### Phase 3: Template Selection & Generation

**Select template based on app type**:

| App Type | Template File |
|----------|---------------|
| Connected App (Basic) | `templates/connected-app-basic.xml` |
| Connected App (Full OAuth) | `templates/connected-app-oauth.xml` |
| Connected App (JWT Bearer) | `templates/connected-app-jwt.xml` |
| Connected App (Canvas) | `templates/connected-app-canvas.xml` |
| External Client App | `templates/external-client-app.xml` |
| ECA Global OAuth | `templates/eca-global-oauth.xml` |
| ECA OAuth Settings | `templates/eca-oauth-settings.xml` |
| ECA Policies | `templates/eca-policies.xml` |

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-connected-apps/templates/[template]`
2. **Project folder**: `[project-root]/sf-connected-apps/templates/[template]`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-connected-apps/templates/connected-app-jwt.xml`

**File Locations**:
- Connected Apps: `force-app/main/default/connectedApps/`
- External Client Apps: `force-app/main/default/externalClientApps/`

### Phase 4: Security Validation & Scoring

**Run Validation**:
```
Score: XX/120 ⭐⭐⭐⭐ Rating
├─ Security: XX/30
├─ OAuth Configuration: XX/25
├─ Metadata Compliance: XX/20
├─ Best Practices: XX/20
├─ Scopes: XX/15
└─ Documentation: XX/10
```

**Scoring Criteria**:

#### Security (30 points)
- PKCE enabled for public clients (+10)
- Refresh token rotation enabled (+5)
- IP restrictions configured (+5)
- Certificate-based auth where applicable (+5)
- No wildcard callback URLs (+5)

#### OAuth Configuration (25 points)
- Valid callback URLs (+10)
- Appropriate OAuth flow for use case (+5)
- Token expiration configured (+5)
- ID token enabled for OpenID Connect (+5)

#### Metadata Compliance (20 points)
- All required fields present (+10)
- Valid API version (+5)
- Proper file naming convention (+5)

#### Best Practices (20 points)
- Minimal scopes (least privilege) (+10)
- Named Principal for integrations (+5)
- Admin pre-authorization configured (+5)

#### Scopes (15 points)
- Only necessary scopes selected (+10)
- No deprecated scopes (+5)

#### Documentation (10 points)
- Description provided (+5)
- Contact email valid (+5)

### Scoring Thresholds

See `shared/docs/scoring-overview.md` (project root). Block deployment if score < 54.

### Phase 5: Deployment & Documentation

**Deployment via sf-devops-architect** (MANDATORY):
```
Task(subagent_type="sf-devops-architect", prompt="Deploy connected apps at force-app/main/default/connectedApps/ to [target-org] with --dry-run")
```

**Completion Summary**:
```
✓ App Created: [AppName]
  Type: [Connected App | External Client App]
  API: 62.0
  Location: force-app/main/default/[connectedApps|externalClientApps]/[AppName].*
  OAuth Flow: [flow type]
  Scopes: [scope list]
  Validation: PASSED (Score: XX/120)

Next Steps:
- For Connected App: Retrieve Consumer Key from Setup after deployment
- For ECA: Configure policies in subscriber org
- Test OAuth flow with Postman or curl
```

---

## Connected App Metadata Structure

### ConnectedApp XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ConnectedApp xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My Integration App</label>
    <contactEmail>admin@company.com</contactEmail>
    <description>Integration for external system</description>

    <!-- OAuth Configuration -->
    <oauthConfig>
        <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
        <certificate>MyCertificate</certificate>
        <consumerKey>AUTO_GENERATED</consumerKey>
        <isAdminApproved>true</isAdminApproved>
        <isConsumerSecretOptional>false</isConsumerSecretOptional>
        <isIntrospectAllTokens>false</isIntrospectAllTokens>
        <scopes>Api</scopes>
        <scopes>RefreshToken</scopes>
    </oauthConfig>

    <!-- OAuth Policy -->
    <oauthPolicy>
        <ipRelaxation>ENFORCE</ipRelaxation>
        <refreshTokenPolicy>infinite</refreshTokenPolicy>
    </oauthPolicy>
</ConnectedApp>
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `label` | Yes | Display name of the app |
| `contactEmail` | Yes | Admin contact email |
| `description` | No | App description |
| `oauthConfig` | No | OAuth settings (required for API access) |
| `oauthPolicy` | No | Token and IP policies |
| `samlConfig` | No | SAML SSO settings |
| `canvasConfig` | No | Canvas app settings |

### OAuth Scopes Reference

| Scope | API Name | Description |
|-------|----------|-------------|
| Access and manage your data | `Api` | REST/SOAP API access |
| Perform requests at any time | `RefreshToken` | Offline access via refresh token |
| Full access | `Full` | Complete access (use sparingly) |
| Access your basic information | `OpenID` | OpenID Connect |
| Web access | `Web` | Access via web browser |
| Access Chatter | `ChatterApi` | Chatter REST API |
| Access custom permissions | `CustomPermissions` | Custom permission access |
| Access Einstein Analytics | `Wave` | Analytics API access |
| Content access | `Content` | Content delivery |
| Access custom applications | `VisualForce` | Visualforce pages |

---

## External Client App Metadata Structure

### ExternalClientApplication (Header File)

**File**: `[AppName].eca-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalClientApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <contactEmail>admin@company.com</contactEmail>
    <description>External integration with modern security</description>
    <distributionState>Local</distributionState>
    <iconUrl>https://example.com/icon.png</iconUrl>
    <isProtected>false</isProtected>
    <label>My External Client App</label>
    <logoUrl>https://example.com/logo.png</logoUrl>
</ExternalClientApplication>
```

### ExtlClntAppGlobalOauthSettings (Global OAuth)

**File**: `[AppName].ecaGlblOauth-meta.xml`

> ⚠️ **IMPORTANT**: File suffix is `.ecaGlblOauth` (abbreviated), NOT `.ecaGlobalOauth`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
    <externalClientApplication>My_App_Name</externalClientApplication>
    <isConsumerSecretOptional>false</isConsumerSecretOptional>
    <isIntrospectAllTokens>false</isIntrospectAllTokens>
    <isPkceRequired>true</isPkceRequired>
    <isSecretRequiredForRefreshToken>true</isSecretRequiredForRefreshToken>
    <label>My App Global OAuth Settings</label>
    <shouldRotateConsumerKey>false</shouldRotateConsumerKey>
    <shouldRotateConsumerSecret>false</shouldRotateConsumerSecret>
</ExtlClntAppGlobalOauthSettings>
```

**ECA Required Fields** (both GlobalOauth and OauthSettings):
- `externalClientApplication` - Reference to parent ECA (must match .eca file name)
- `label` - Display label
- Global: `callbackUrl` | Instance: `commaSeparatedOauthScopes` (NOT individual `<scopes>` tags)

### ExtlClntAppOauthSettings (Instance OAuth)

**File**: `[AppName].ecaOauth-meta.xml`

> **Note**: OAuth flows are configured via Admin UI or `ExtlClntAppConfigurablePolicies`.

### ExtlClntAppConfigurablePolicies (Admin Policies)

**File**: `[AppName].ecaPolicy-meta.xml` (auto-generated, admin-configurable)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtlClntAppConfigurablePolicies xmlns="http://soap.sforce.com/2006/04/metadata">
    <ipRelaxation>ENFORCE</ipRelaxation>
    <refreshTokenPolicy>infinite</refreshTokenPolicy>
    <sessionTimeout>120</sessionTimeout>
</ExtlClntAppConfigurablePolicies>
```

### ECA Distribution States

| State | Description | Use Case |
|-------|-------------|----------|
| `Local` | Available only in creating org | Development, single-org integrations |
| `Packageable` | Can be included in 2GP packages | ISV apps, multi-org distribution |

---

## Security Best Practices

> 📋 **Scoring details**: See Phase 4 Scoring Criteria above for point breakdown.

### Anti-Patterns

| Anti-Pattern | Risk | Fix |
|--------------|------|-----|
| Wildcard callback URL | Token hijacking | Use specific URLs |
| `Full` scope everywhere | Over-privileged | Use minimal scopes |
| No token expiration | Long-term compromise | Set expiration policy |
| Consumer secret in code | Credential leak | Use Named Credentials |
| PKCE disabled for mobile | Authorization code interception | Enable PKCE |
| No IP restrictions | Unauthorized access | Configure IP ranges |

---

## OAuth Flow Decision Matrix

| Use Case | Recommended Flow | PKCE | Refresh Token |
|----------|-----------------|------|---------------|
| Web Server Application | Authorization Code | Optional | Yes |
| Single Page Application | Authorization Code | Required | Yes (rotate) |
| Mobile Application | Authorization Code | Required | Yes (rotate) |
| Server-to-Server | JWT Bearer | N/A | No |
| CI/CD Pipeline | JWT Bearer | N/A | No |
| Device (TV, CLI) | Device Authorization | N/A | Yes |
| Legacy (avoid) | Username-Password | N/A | Yes |

---

## Scratch Org Configuration

For **External Client Apps**, add these features to your scratch org definition:

```json
{
  "orgName": "ECA Development Org",
  "edition": "Developer",
  "features": [
    "ExternalClientApps",
    "ExtlClntAppSecretExposeCtl"
  ],
  "settings": {
    "securitySettings": {
      "enableAdminLoginAsAnyUser": true
    }
  }
}
```

---

## Cross-Skill Integration

| Skill/Agent | When to Use | Example |
|-------------|-------------|---------|
| sf-metadata | Create Named Credentials for secure callouts | `Skill(skill="sf-metadata")` → "Create Named Credential for Stripe API" |
| **sf-devops-architect** | ⚠️ MANDATORY for deployment | `Task(subagent_type="sf-devops-architect", ...)` |
| sf-apex | Create Apex for OAuth token handling | `Skill(skill="sf-apex")` → "Create OAuth token refresh service" |

---

## Migration: Connected App → External Client App

**Step 1: Assess Current State**
```
Glob: **/*.connectedApp-meta.xml
```
Review existing Connected Apps and their configurations.

**Step 2: Create ECA Equivalent**
- Map OAuth settings to ECA structure
- Create all required ECA metadata files
- Set `distributionState` based on needs

**Step 3: Update Integrations**
- Generate new Consumer Key/Secret
- Update external systems with new credentials
- Test OAuth flows

**Step 4: Deprecate Old App**
- Remove from Connected App policies
- Archive or delete Connected App metadata

---

## Common Commands

**List Connected Apps in Org**:
```bash
sf org list metadata --metadata-type ConnectedApp --target-org [alias]
```

**Retrieve Connected App**:
```bash
sf project retrieve start --metadata ConnectedApp:[AppName] --target-org [alias]
```

**Deploy Connected App**:
```bash
sf project deploy start --source-dir force-app/main/default/connectedApps --target-org [alias]
```

---

## Notes

- **API Version**: 62.0+ recommended, 61.0+ required for External Client Apps
- **Scoring**: Block deployment if score < 54
- **External Client Apps**: Preferred for new development (modern security model)
- **Consumer Secret**: Never commit to version control

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
