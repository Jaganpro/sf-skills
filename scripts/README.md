# Credential Configuration Scripts

**Generic/reusable scripts** for configuring API credentials across sf-skills.

> 💡 **Pattern:** Each skill should have its own `scripts/setup-credentials.sh` that's tailored to that skill. These scripts in `/scripts/` are generic templates that can be copied and customized.
>
> **Example:** See `bland-ai-calls/scripts/setup-credentials.sh` for a skill-specific implementation.

---

## 🆕 What's New: Automatic Endpoint Security

**Problem Solved:** Named Credentials require **Remote Site Settings** or **CSP Trusted Sites** to allow outbound HTTP callouts. Previously, users had to configure these manually in the UI.

**Solution:** Setup scripts now **automatically deploy** endpoint security configurations!

### What Gets Configured Automatically

When you run `./scripts/setup-credentials.sh`:

1. ✅ **API Credentials** (Custom Setting or Named Credential)
2. ✅ **Endpoint Security** (CSP Trusted Sites or Remote Site Settings) ⭐ NEW!
3. ✅ **Org-specific configuration** (handles API version differences)

### How It Works

```bash
./bland-ai-calls/scripts/setup-credentials.sh AIZoom

# Script automatically:
# 1. Checks if org supports CSP Trusted Sites (API 48+)
# 2. If yes → deploys CSP Trusted Site
# 3. If no → falls back to Remote Site Setting
# 4. If already exists → skips deployment
```

**Result:** No manual UI configuration needed for endpoint security! 🎉

---

## 📋 Two Approaches

### Option 1: Named Credentials (Most Secure) ✅ Recommended
**Best for:** Production environments, OAuth flows, strict security requirements

**Pros:**
- ✅ Most secure (Salesforce-encrypted storage)
- ✅ Supports OAuth, JWT, Certificate auth
- ✅ Built-in token refresh
- ✅ Industry standard

**Cons:**
- ⚠️ Requires one-time UI configuration per org

**Script:** `configure-named-credential.sh`

---

### Option 2: Custom Settings (Fully Automated)
**Best for:** Dev environments, CI/CD pipelines, test automation

**Pros:**
- ✅ 100% scriptable (no UI required)
- ✅ Can version control structure
- ✅ Fast setup

**Cons:**
- ⚠️ Less secure than Named Credentials
- ⚠️ No built-in OAuth support
- ⚠️ Visible in metadata exports

**Script:** `set-api-credential.sh`

---

## 🚀 Quick Start

### For Named Credentials (Recommended)

```bash
# Step 1: Deploy the Named Credential structure
sf project deploy start \
  --metadata NamedCredential:Bland_AI_API \
  --target-org AIZoom

# Step 2: Configure credentials
./scripts/configure-named-credential.sh Bland_AI_API AIZoom

# Step 3: Follow on-screen instructions to complete setup in UI
```

### For Custom Settings (Fully Automated)

```bash
# One command - fully automated
./scripts/set-api-credential.sh BlandAI - AIZoom
# (Script will prompt for API key securely)
```

---

## 📖 Detailed Usage

### `configure-named-credential.sh`

**Purpose:** Helps configure Named Credentials with secure credential storage

**Usage:**
```bash
./scripts/configure-named-credential.sh <credential-name> <org-alias>
```

**Example:**
```bash
./scripts/configure-named-credential.sh Bland_AI_API AIZoom
```

**What it does:**
1. Validates org connection
2. Checks if Named Credential exists
3. Provides instructions for completing setup via UI
4. Optionally tests connection

**Prerequisites:**
- Named Credential must be deployed first
- Salesforce CLI (sf) must be installed
- Must be authenticated to target org

---

### `set-api-credential.sh`

**Purpose:** Programmatically sets API credentials using Custom Settings (fully automated)

**Usage:**
```bash
# Secure input (recommended)
./scripts/set-api-credential.sh <setting-name> - <org-alias>

# Direct input (less secure - visible in shell history)
./scripts/set-api-credential.sh <setting-name> <api-key> <org-alias>
```

**Examples:**
```bash
# Secure input (will prompt for key)
./scripts/set-api-credential.sh BlandAI - AIZoom

# Direct input
./scripts/set-api-credential.sh BlandAI sk_live_abc123xyz AIZoom
```

**What it does:**
1. Creates `API_Credentials__c` Custom Setting (if doesn't exist)
2. Inserts or updates credential record
3. Shows code example for using in Apex

**Apex Usage:**
```apex
// Retrieve API key in your Apex code
API_Credentials__c cred = API_Credentials__c.getInstance('BlandAI');
String apiKey = cred.API_Key__c;

HttpRequest req = new HttpRequest();
req.setHeader('Authorization', apiKey);
```

---

## 🔐 Security Best Practices

### ✅ DO:
- Use Named Credentials for production
- Use secure input mode (`-` for API key parameter)
- Store credentials in password manager
- Rotate API keys regularly
- Use different keys per environment

### ❌ DON'T:
- Commit API keys to source control
- Share API keys in chat/email
- Use production keys in dev/sandbox
- Store keys in shell history (use secure input)
- Hardcode credentials in Apex

---

## 🎯 Use Cases by Skill

| Skill | Credential Type | Script to Use | Example |
|-------|-----------------|---------------|---------|
| **bland-ai-calls** | API Key | `set-api-credential.sh` | `./scripts/set-api-credential.sh BlandAI - AIZoom` |
| **sf-integration** | OAuth 2.0 | `configure-named-credential.sh` | `./scripts/configure-named-credential.sh Stripe_API AIZoom` |
| **sf-connected-apps** | JWT Bearer | `configure-named-credential.sh` | `./scripts/configure-named-credential.sh JWT_Flow AIZoom` |
| Custom Integration | Depends | Both available | Choose based on requirements |

---

## 🔧 Troubleshooting

### "Named Credential not found"
**Cause:** Named Credential not deployed to org

**Fix:**
```bash
sf project deploy start \
  --metadata NamedCredential:Bland_AI_API \
  --target-org AIZoom
```

### "Cannot connect to org"
**Cause:** Not authenticated to target org

**Fix:**
```bash
sf org login web --alias AIZoom
```

### "sObject type 'API_Credentials__c' is not supported"
**Cause:** Custom Setting not yet created (first run)

**Fix:** Script will automatically create it - just rerun

### "API key visible in shell history"
**Cause:** Used direct input mode

**Fix:** Use secure input mode:
```bash
./scripts/set-api-credential.sh BlandAI - AIZoom
```

Or clear history:
```bash
history -c  # Clear current session
rm ~/.bash_history  # Clear all history (careful!)
```

---

## 🌍 Environment-Specific Credentials

### Multi-Org Setup

```bash
# Development
./scripts/set-api-credential.sh BlandAI - DevOrg
# Enter test API key

# Sandbox
./scripts/set-api-credential.sh BlandAI - SandboxOrg
# Enter sandbox API key

# Production
./scripts/configure-named-credential.sh Bland_AI_API ProdOrg
# Use Named Credentials for production (more secure)
```

---

## 📊 Comparison Matrix

| Feature | Named Credentials | Custom Settings |
|---------|-------------------|-----------------|
| **Security** | 🔒🔒🔒 Highest | 🔒🔒 Medium |
| **Automation** | ⚠️ Partial | ✅ Full |
| **OAuth Support** | ✅ Built-in | ❌ Manual |
| **Token Refresh** | ✅ Automatic | ❌ Manual |
| **Setup Time** | ~2 min (one-time) | ~10 sec |
| **Scriptable** | Partial | ✅ Full |
| **Production Ready** | ✅ Yes | ⚠️ Dev/Test only |
| **Visible in Exports** | ❌ No | ⚠️ Yes (structure) |

---

## 🔄 Migration Path

### From Custom Settings to Named Credentials

```bash
# Step 1: Deploy Named Credential
sf project deploy start --metadata NamedCredential:Bland_AI_API

# Step 2: Copy API key from Custom Setting
sf data query \
  --query "SELECT API_Key__c FROM API_Credentials__c WHERE Name='BlandAI'" \
  --target-org AIZoom

# Step 3: Manually configure Named Credential with same key

# Step 4: Update Apex to use Named Credential
# Before:
API_Credentials__c cred = API_Credentials__c.getInstance('BlandAI');
req.setHeader('Authorization', cred.API_Key__c);

# After:
req.setEndpoint('callout:Bland_AI_API/calls');
req.setHeader('Authorization', '{!$Credential.Password}');

# Step 5: Remove Custom Setting (optional)
```

---

## 🆘 Getting Help

**Script Issues:**
- Check script has execute permissions: `ls -la scripts/`
- Make executable: `chmod +x scripts/*.sh`

**Salesforce CLI Issues:**
- Update CLI: `npm install -g @salesforce/cli`
- Check version: `sf --version`

**API Key Issues:**
- Verify key in provider dashboard (Bland.ai, Stripe, etc.)
- Test key with curl: `curl -H "Authorization: YOUR_KEY" https://api.bland.ai/v1/calls`

---

## 💡 Pro Tips

1. **Use environment variables for CI/CD:**
   ```bash
   export BLAND_API_KEY="${{ secrets.BLAND_API_KEY }}"
   ./scripts/set-api-credential.sh BlandAI "$BLAND_API_KEY" ProdOrg
   ```

2. **Create wrapper scripts per skill:**
   ```bash
   # scripts/setup-bland-ai.sh
   #!/bin/bash
   ./scripts/set-api-credential.sh BlandAI - $1
   ```

3. **Document which credentials need setup:**
   ```markdown
   # .credentials-needed.md
   - Bland.ai API key: https://app.bland.ai/settings/api
   - Stripe API key: https://dashboard.stripe.com/apikeys
   ```

4. **Use password managers:**
   ```bash
   # macOS Keychain
   security find-generic-password -s "BlandAI" -w | \
     xargs -I {} ./scripts/set-api-credential.sh BlandAI {} AIZoom
   ```

---

**Happy integrating! 🚀**
