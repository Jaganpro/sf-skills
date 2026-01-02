# Connected App Setup for Live Preview

Guide for configuring OAuth to enable live preview mode with real Flow and Apex execution.

---

## Overview

Agent preview has two modes:

| Mode | Flag | Actions | Use Case |
|------|------|---------|----------|
| **Simulated** | (default) | LLM simulates action results | Logic testing, early development |
| **Live** | `--use-live-actions` | Real Flows/Apex execute | Integration testing, validation |

Live mode requires a **Connected App** for OAuth authentication.

---

## When You Need a Connected App

✅ **Required for:**
- `sf agent preview --use-live-actions`
- Testing real data queries
- Validating Flow execution
- Debugging Apex integration

❌ **Not required for:**
- `sf agent preview` (simulated mode)
- `sf agent test run` (automated tests)
- Agent validation and publishing

---

## Quick Setup

### Option 1: Use sf-connected-apps Skill (Recommended)

```
Skill(skill="sf-connected-apps", args="Create Connected App for Agentforce live preview with callback http://localhost:1717/OauthRedirect")
```

### Option 2: Manual Setup via UI

1. **Setup → App Manager → New Connected App**
2. Configure OAuth settings (see below)
3. Get Consumer Key and Secret

---

## Connected App Configuration

### Required Settings

| Field | Value |
|-------|-------|
| **Connected App Name** | Agentforce Preview App (or your choice) |
| **API Name** | Agentforce_Preview_App |
| **Contact Email** | Your email |
| **Enable OAuth Settings** | ✅ Checked |
| **Callback URL** | `http://localhost:1717/OauthRedirect` |
| **Selected OAuth Scopes** | See below |

### Required OAuth Scopes

| Scope | Purpose |
|-------|---------|
| `Full access (full)` | OR use specific scopes below |
| `Access and manage your data (api)` | Data operations |
| `Perform requests on your behalf (refresh_token, offline_access)` | Token refresh |
| `Access unique user identifiers (openid)` | User identification |

**Minimal Scopes (if not using `full`):**
- `api`
- `refresh_token`
- `offline_access`
- `openid`

### Security Settings (Optional)

| Setting | Recommendation |
|---------|----------------|
| **Require Secret for Refresh Token Flow** | ✅ Enable for production |
| **Require Proof Key for Code Exchange (PKCE)** | ✅ Enable for enhanced security |
| **IP Restrictions** | Configure if needed |

---

## Retrieve Credentials

After creating the Connected App:

1. **Click "Manage Consumer Details"**
2. **Verify identity** (email/SMS code)
3. **Copy:**
   - Consumer Key (Client ID)
   - Consumer Secret (Client Secret)

---

## Authentication

### Authenticate with the Connected App

```bash
# Web-based OAuth login
sf org login web --client-id YOUR_CONSUMER_KEY --set-default-dev-hub --alias preview-auth
```

### Or use existing org authentication

If already authenticated to the org:

```bash
# Check current auth
sf org display --target-org [alias]

# Re-authenticate if needed
sf org login web --alias [alias]
```

---

## Using Live Preview

### Basic Live Preview

```bash
sf agent preview \
  --api-name Customer_Support_Agent \
  --use-live-actions \
  --client-app Agentforce_Preview_App \
  --target-org dev
```

### With Debug Logs

```bash
sf agent preview \
  --api-name Customer_Support_Agent \
  --use-live-actions \
  --client-app Agentforce_Preview_App \
  --apex-debug \
  --output-dir ./logs \
  --target-org dev
```

### Save Transcripts

```bash
sf agent preview \
  --api-name Customer_Support_Agent \
  --use-live-actions \
  --client-app Agentforce_Preview_App \
  --output-dir ./preview-logs \
  --target-org dev
```

---

## Output Files

When using `--output-dir`, you get:

### transcript.json

Conversation record:

```json
{
  "conversationId": "0Af7X000000001",
  "messages": [
    {"role": "user", "content": "Where is my order?", "timestamp": "..."},
    {"role": "assistant", "content": "Let me check...", "timestamp": "..."}
  ],
  "status": "completed"
}
```

### responses.json

Full API details including action invocations:

```json
{
  "messages": [
    {
      "role": "function",
      "name": "get_order_status",
      "content": {
        "orderId": "a1J7X00000001",
        "status": "Shipped",
        "trackingNumber": "1Z999..."
      },
      "executionTimeMs": 450
    }
  ],
  "metrics": {
    "flowInvocations": 1,
    "apexInvocations": 0,
    "totalDuration": 3050
  }
}
```

### apex-debug.log

When using `--apex-debug`:

```
13:45:22.123 (123456789)|USER_DEBUG|[15]|DEBUG|Processing order lookup
13:45:22.234 (234567890)|SOQL_EXECUTE_BEGIN|[20]|Aggregations:0|SELECT Id, Status...
13:45:22.345 (345678901)|SOQL_EXECUTE_END|[20]|Rows:1
```

---

## Troubleshooting

### 401 Unauthorized

**Cause:** Connected App not properly configured or not authorized.

**Solution:**
1. Verify Connected App callback URL matches `http://localhost:1717/OauthRedirect`
2. Re-authenticate: `sf org login web --alias [alias]`
3. Check Connected App is enabled for the user's profile

### "Connected App not found"

**Cause:** Wrong API name in `--client-app` flag.

**Solution:**
1. Check the API Name (not Display Name) in Setup → App Manager
2. Use exact API name: `--client-app Agentforce_Preview_App`

### Actions not executing

**Cause:** Actions require deployed Flows/Apex.

**Solution:**
1. Verify Flow is active: `sf flow resume --name [FlowName]`
2. Verify Apex is deployed: `sf project deploy start --metadata ApexClass:[ClassName]`
3. Check agent is activated: `sf agent activate --api-name [Agent]`

### Timeout errors

**Cause:** Flow or Apex taking too long.

**Solution:**
1. Add debug logs: `--apex-debug`
2. Check Flow for long-running operations
3. Verify external callouts are responsive

---

## Security Best Practices

| Practice | Description |
|----------|-------------|
| **Use dedicated app** | Create separate Connected App for preview vs production |
| **Limit scopes** | Use minimum necessary OAuth scopes |
| **Enable PKCE** | Require Proof Key for Code Exchange |
| **IP restrictions** | Limit access by IP range if possible |
| **Rotate secrets** | Periodically rotate Consumer Secret |
| **Audit logs** | Monitor Connected App usage |

---

## Connected App Metadata

If using metadata-based deployment:

```xml
<!-- connectedApps/Agentforce_Preview.connectedApp-meta.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<ConnectedApp xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Agentforce Preview</label>
    <contactEmail>admin@example.com</contactEmail>
    <oauthConfig>
        <callbackUrl>http://localhost:1717/OauthRedirect</callbackUrl>
        <certificate>YOUR_CERT_IF_NEEDED</certificate>
        <consumerKey>AUTO_GENERATED</consumerKey>
        <isAdminApproved>true</isAdminApproved>
        <isConsumerSecretOptional>false</isConsumerSecretOptional>
        <isIntrospectAllTokens>false</isIntrospectAllTokens>
        <scopes>Full</scopes>
        <scopes>Api</scopes>
        <scopes>RefreshToken</scopes>
    </oauthConfig>
    <oauthPolicy>
        <ipRelaxation>ENFORCE</ipRelaxation>
        <refreshTokenPolicy>infinite</refreshTokenPolicy>
    </oauthPolicy>
</ConnectedApp>
```

Deploy with:
```bash
sf project deploy start --metadata ConnectedApp:Agentforce_Preview --target-org [alias]
```

---

## Related Skills

| Skill | Use For |
|-------|---------|
| sf-connected-apps | Create and manage Connected Apps |
| sf-flow | Debug failing Flow actions |
| sf-apex | Debug failing Apex actions |
| sf-debug | Analyze debug logs |
