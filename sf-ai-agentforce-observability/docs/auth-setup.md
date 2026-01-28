# Authentication Setup

This skill uses JWT Bearer authentication to access the Data Cloud Query API. The setup process leverages the **sf-connected-apps** skill for External Client App (ECA) configuration.

## Prerequisites

1. **Salesforce CLI** installed and authenticated to your org
2. **sf-connected-apps** skill available (for ECA templates)
3. **OpenSSL** for certificate generation

---

## Quick Setup

### Step 1: Generate Certificate

```bash
# Create directory for JWT keys
mkdir -p ~/.sf/jwt

# Generate private key and self-signed certificate (valid 1 year)
openssl req -x509 -sha256 -nodes \
    -newkey rsa:2048 \
    -days 365 \
    -keyout ~/.sf/jwt/myorg.key \
    -out ~/.sf/jwt/myorg.crt \
    -subj "/CN=Data Cloud STDM Extractor/O=My Company"
```

### Step 2: Create External Client App

Use the **sf-connected-apps** skill to create an ECA with JWT Bearer flow:

```
/sf-connected-apps create-eca jwt-bearer --org myorg
```

Or manually create in Salesforce Setup:

1. **Setup** → **App Manager** → **New Connected App**
2. Enable OAuth Settings:
   - **Callback URL**: `https://login.salesforce.com/services/oauth2/callback`
   - **Use digital signatures**: ✅ Upload `~/.sf/jwt/myorg.crt`
   - **Selected OAuth Scopes**:
     - `cdp_query_api` (Data Cloud Query API)
     - `cdp_profile_api` (Data Cloud Profile API)
     - `refresh_token, offline_access`

### Step 3: Configure Policies

1. **Manage** → **Edit Policies**:
   - **Permitted Users**: Admin approved users are pre-authorized
   - **IP Relaxation**: Relax IP restrictions

2. **Manage Profiles** or **Manage Permission Sets**:
   - Add your user's profile or a permission set

### Step 4: Get Consumer Key

1. **View** the Connected App
2. Copy the **Consumer Key** (starts with `3MVG9...`)
3. Set environment variable:

```bash
export SF_CONSUMER_KEY="3MVG9..."
```

### Step 5: Test Authentication

```bash
stdm-extract test-auth --org myorg
```

Expected output:
```
✅ Authentication successful
   Instance URL: https://myorg.my.salesforce.com
   Token valid for: 3599 seconds
```

---

## File Locations

| File | Location | Description |
|------|----------|-------------|
| Private Key | `~/.sf/jwt/{org_alias}.key` | RSA private key for JWT signing |
| Certificate | `~/.sf/jwt/{org_alias}.crt` | X.509 certificate uploaded to Salesforce |
| Consumer Key | `$SF_CONSUMER_KEY` | Environment variable or CLI option |

---

## Required OAuth Scopes

| Scope | Purpose |
|-------|---------|
| `cdp_query_api` | Execute Data Cloud SQL queries |
| `cdp_profile_api` | Access profile and DMO metadata |
| `refresh_token` | Token refresh capability |
| `offline_access` | Server-to-server access |

---

## Troubleshooting

### invalid_grant Error

```
RuntimeError: Token exchange failed: invalid_grant
```

**Causes:**
1. Certificate mismatch - re-upload certificate to Salesforce
2. Expired certificate - regenerate with new validity period
3. User not authorized - assign to Connected App

**Verify certificate:**
```bash
openssl x509 -enddate -noout -in ~/.sf/jwt/myorg.crt
```

### 403 Forbidden

```
RuntimeError: Access denied: Ensure ECA has cdp_query_api scope
```

**Solution:** Add `cdp_query_api` and `cdp_profile_api` scopes to the Connected App.

### User Not Authorized

Ensure your user is either:
- Assigned to a Profile with access to the Connected App, OR
- Assigned to a Permission Set with Connected App access

---

## Sandbox vs Production

For **sandbox** orgs, use the sandbox login URL:

1. The skill automatically detects sandbox from `sf org display --json`
2. Token exchange uses `https://test.salesforce.com` for sandboxes

No additional configuration needed - the auth module handles this automatically.

---

## Security Best Practices

1. **Protect private keys**: Set `chmod 600 ~/.sf/jwt/*.key`
2. **Rotate certificates**: Regenerate annually before expiration
3. **Use separate ECAs**: One per org/environment
4. **Audit access**: Review Connected App usage in Setup → Security → Connected Apps OAuth Usage

---

## See Also

- [sf-connected-apps skill](../../sf-connected-apps/SKILL.md) - Detailed ECA setup
- [CLI Reference](cli-reference.md) - Command options
- [Troubleshooting](../resources/troubleshooting.md) - More error solutions
