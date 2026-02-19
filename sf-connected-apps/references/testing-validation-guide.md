<!-- Parent: sf-connected-apps/SKILL.md -->
# Testing & Validation Guide

This guide documents tested External Client App (ECA) and Connected App patterns based on systematic validation testing (December 2025).

## Test Matrix

| Component Type | Template | Test Status |
|----------------|----------|-------------|
| Connected App (Basic) | `connected-app-basic.xml` | ✅ Verified |
| Connected App (Full OAuth) | `connected-app-oauth.xml` | ✅ Verified |
| Connected App (JWT Bearer) | `connected-app-jwt.xml` | ✅ Verified |
| Connected App (Canvas) | `connected-app-canvas.xml` | ⚠️ Location-dependent |
| External Client App | `external-client-app.xml` | ✅ Verified |
| ECA Global OAuth | `eca-global-oauth.xml` | ✅ Verified |
| ECA OAuth Settings | `eca-oauth-settings.xml` | ✅ Verified |

---

## Critical File Naming Conventions

### External Client App Files

| Metadata Type | File Suffix | Example |
|--------------|-------------|---------|
| ExternalClientApplication | `.eca-meta.xml` | `MyApp.eca-meta.xml` |
| ExtlClntAppOauthSettings | `.ecaOauth-meta.xml` | `MyApp.ecaOauth-meta.xml` |
| ExtlClntAppGlobalOauthSettings | `.ecaGlblOauth-meta.xml` | `MyApp.ecaGlblOauth-meta.xml` |
| ExtlClntAppOauthConfigurablePolicies | `.ecaOauthPlcy-meta.xml` | `MyApp.ecaOauthPlcy-meta.xml` |

⚠️ **CRITICAL**: Use `.ecaGlblOauth` (abbreviated), NOT `.ecaGlobalOauth`

### Connected App Files

| Metadata Type | File Suffix | Example |
|--------------|-------------|---------|
| ConnectedApp | `.connectedApp-meta.xml` | `MyApp.connectedApp-meta.xml` |

---

## Common Deployment Errors & Solutions

### Error: "Invalid or missing field" in ECA OAuth Settings

**Cause**: Using wrong schema with non-existent fields

**Wrong Schema (FAILS):**
```xml
<ExtlClntAppOauthSettings>
    <isAdminApproved>true</isAdminApproved>           <!-- DOES NOT EXIST -->
    <isCodeCredentialsEnabled>true</isCodeCredentialsEnabled>  <!-- DOES NOT EXIST -->
    <scopes>Api</scopes>                               <!-- WRONG FORMAT -->
</ExtlClntAppOauthSettings>
```

**Correct Schema:**
```xml
<ExtlClntAppOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <commaSeparatedOauthScopes>Api, RefreshToken</commaSeparatedOauthScopes>
    <externalClientApplication>MyApp</externalClientApplication>
    <label>MyApp OAuth Settings</label>
</ExtlClntAppOauthSettings>
```

### Error: "Missing required field" in ECA Global OAuth

**Cause**: Missing `externalClientApplication` or `label`

**Wrong (FAILS):**
```xml
<ExtlClntAppGlobalOauthSettings>
    <callbackUrl>https://example.com/callback</callbackUrl>
    <isPkceRequired>true</isPkceRequired>
</ExtlClntAppGlobalOauthSettings>
```

**Correct:**
```xml
<ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <callbackUrl>https://example.com/callback</callbackUrl>
    <externalClientApplication>MyApp</externalClientApplication>
    <isConsumerSecretOptional>true</isConsumerSecretOptional>
    <isIntrospectAllTokens>false</isIntrospectAllTokens>
    <isPkceRequired>true</isPkceRequired>
    <isSecretRequiredForRefreshToken>false</isSecretRequiredForRefreshToken>
    <label>MyApp Global OAuth</label>
    <shouldRotateConsumerKey>false</shouldRotateConsumerKey>
    <shouldRotateConsumerSecret>false</shouldRotateConsumerSecret>
</ExtlClntAppGlobalOauthSettings>
```

### Error: "Organization is not configured to support location"

**Cause**: Canvas app using location that requires org feature enablement

**Problematic Locations:**
- `AppLauncher` - Requires feature enablement
- Some other locations may have similar requirements

**Solution**: Use universally available locations:
```xml
<canvasApp>
    <locations>Visualforce</locations>
</canvasApp>
```

### Error: Certificate not found (JWT Bearer)

**Cause**: Referenced certificate doesn't exist in org

**Wrong:**
```xml
<certificate>NonExistent_Cert</certificate>
```

**Solution**: Create certificate first, then reference it:
```bash
# 1. Create certificate in org (Setup > Certificate and Key Management)
# 2. Reference in Connected App
<certificate>My_JWT_Cert</certificate>
```

---

## Field Reference

### ExtlClntAppOauthSettings (ECA OAuth)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `commaSeparatedOauthScopes` | String | Yes | Comma-separated scopes (e.g., "Api, RefreshToken") |
| `externalClientApplication` | String | Yes | Reference to parent ECA API name |
| `label` | String | Yes | Display label |

**Available Scopes:**
- `Api` - REST/SOAP API access
- `RefreshToken` - Offline access
- `OpenID` - OpenID Connect
- `Profile` - User profile info
- `Email` - User email
- `Web` - Web browser access
- `ChatterApi` - Chatter REST API

### ExtlClntAppGlobalOauthSettings (ECA Global OAuth)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `callbackUrl` | URL | Yes | OAuth redirect URI |
| `externalClientApplication` | String | Yes | Reference to parent ECA |
| `isConsumerSecretOptional` | Boolean | No | True for public clients with PKCE |
| `isIntrospectAllTokens` | Boolean | No | Enable token introspection |
| `isPkceRequired` | Boolean | No | Require PKCE (recommended for public clients) |
| `isSecretRequiredForRefreshToken` | Boolean | No | Require secret for refresh |
| `label` | String | Yes | Display label |
| `shouldRotateConsumerKey` | Boolean | No | Enable key rotation |
| `shouldRotateConsumerSecret` | Boolean | No | Enable secret rotation |

---

## Deployment Order

For External Client Apps, deploy in this order:

```bash
# 1. Deploy base ECA first
sf project deploy start --metadata ExternalClientApplication:MyApp --target-org [alias]

# 2. Deploy OAuth settings
sf project deploy start --metadata ExtlClntAppOauthSettings:MyApp --target-org [alias]

# 3. Deploy Global OAuth (if needed)
sf project deploy start --metadata ExtlClntAppGlobalOauthSettings:MyApp --target-org [alias]

# Or deploy all together (recommended)
sf project deploy start --source-dir force-app/main/default/externalClientApps --target-org [alias]
```

---

## Post-Deployment Steps

### Client Credentials Flow (ECA)

Client Credentials flow requires additional configuration **not available via metadata**:

1. **Create Permission Set** with "Salesforce API Integration" permission
2. **Assign Permission Set** to the External Client App
3. **Configure Execution User** in Setup

### JWT Bearer Flow (Connected App)

1. **Upload Certificate** to org before deployment
2. **Pre-authorize Users** after deployment (Setup > Manage Connected Apps)

---

## Deployment Checklist

### External Client App

- [ ] `.eca-meta.xml` file exists
- [ ] `.ecaOauth-meta.xml` file exists (not ecaOAuth)
- [ ] `.ecaGlblOauth-meta.xml` uses abbreviated suffix (not ecaGlobalOauth)
- [ ] All files reference same `externalClientApplication` name
- [ ] All files have `label` field
- [ ] `commaSeparatedOauthScopes` uses string format, not individual `<scopes>` tags
- [ ] Callback URL is HTTPS (or custom scheme for mobile)
- [ ] PKCE enabled for public clients

### Connected App

- [ ] `.connectedApp-meta.xml` file exists
- [ ] `contactEmail` is valid
- [ ] Callback URL matches OAuth flow requirements
- [ ] Certificate exists in org (for JWT Bearer)
- [ ] Canvas locations are supported by org (if using Canvas)

---

## Tested Configurations

### Minimal ECA (API Integration)

```
Files:
├── MyApp.eca-meta.xml
├── MyApp.ecaOauth-meta.xml
└── MyApp.ecaGlblOauth-meta.xml

Scopes: Api, RefreshToken
PKCE: false (confidential client)
```

### Mobile App ECA (PKCE)

```
Files:
├── MobileApp.eca-meta.xml
├── MobileApp.ecaOauth-meta.xml
└── MobileApp.ecaGlblOauth-meta.xml

Scopes: Api, RefreshToken, OpenID
PKCE: true (public client)
Callback: com.example.app://oauth/callback
```

### Server-to-Server ECA

```
Files:
├── ServiceApp.eca-meta.xml
└── ServiceApp.ecaOauth-meta.xml

Scopes: Api
Note: Client Credentials requires post-deployment Permission Set assignment
```

---

*Last Updated: December 2025*
*Based on testing with SF CLI and API v65.0*
