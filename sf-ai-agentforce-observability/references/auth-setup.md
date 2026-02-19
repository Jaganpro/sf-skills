<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
   1 # Authentication Setup
   2 
   3 This skill uses JWT Bearer authentication to access the Data Cloud Query API. Authentication is configured via an **External Client App (ECA)** in Salesforce.
   4 
   5 ## Prerequisites
   6 
   7 1. **Salesforce CLI** installed and authenticated to your org
   8 2. **OpenSSL** for certificate generation
   9 3. **Data Cloud** enabled in your org
  10 4. **System Administrator** profile (or appropriate permissions for ECA setup)
  11 
  12 ---
  13 
  14 ## Quick Setup (5 Steps)
  15 
  16 ### Step 1: Generate JWT Certificate
  17 
  18 ```bash
  19 # Create directory for JWT keys
  20 mkdir -p ~/.sf/jwt
  21 
  22 # Generate private key and self-signed certificate (valid 1 year)
  23 # Naming convention: {org_alias}-agentforce-observability.key
  24 openssl req -x509 -sha256 -nodes -days 365 \
  25     -newkey rsa:2048 \
  26     -keyout ~/.sf/jwt/Vivint-DevInt-agentforce-observability.key \
  27     -out ~/.sf/jwt/Vivint-DevInt-agentforce-observability.crt \
  28     -subj "/CN=AgentforceObservability/O=Vivint"
  29 
  30 # Secure the private key (required - Salesforce rejects world-readable keys)
  31 chmod 600 ~/.sf/jwt/Vivint-DevInt-agentforce-observability.key
  32 ```
  33 
  34 ### Step 2: Create External Client App
  35 
  36 In Salesforce Setup:
  37 
  38 1. **Setup** → **External Client App Manager** → **New External Client App**
  39 2. Fill in the basic details:
  40 
  41 | Field | Value |
  42 |-------|-------|
  43 | Name | `Agentforce Observability` |
  44 | API Name | `Agentforce_Observability` |
  45 | Description | `JWT Bearer auth for Agentforce STDM extraction via Claude Code` |
  46 | Distribution State | `Local` |
  47 
  48 3. Click **Save**
  49 
  50 ### Step 3: Configure OAuth Settings
  51 
  52 In the ECA → **OAuth Settings** tab:
  53 
  54 | Setting | Value |
  55 |---------|-------|
  56 | Enable OAuth | ✅ Checked |
  57 | Callback URL | `https://login.salesforce.com/services/oauth2/callback` |
  58 | Selected OAuth Scopes | `cdp_query_api`, `refresh_token, offline_access` |
  59 | Require PKCE | ❌ Unchecked (not needed for JWT Bearer) |
  60 | Enable Client Credentials Flow | ❌ Optional |
  61 
  62 **Upload Certificate:**
  63 1. Check **Use digital signatures**
  64 2. Click **Choose File**
  65 3. Upload `~/.sf/jwt/{org}-agentforce-observability.crt`
  66 4. Click **Save**
  67 
  68 ### Step 4: Configure App Policies
  69 
  70 In the ECA → **Policies** tab:
  71 
  72 | Setting | Value |
  73 |---------|-------|
  74 | Permitted Users | **Admin approved users are pre-authorized** |
  75 | IP Relaxation | Relax IP restrictions (for CLI usage) |
  76 
  77 **Add Your User:**
  78 1. Click **Manage** → **Manage Profiles** or **Manage Permission Sets**
  79 2. Add your user's profile or an appropriate permission set
  80 3. Click **Save**
  81 
  82 ### Step 5: Get Consumer Key & Test
  83 
  84 1. Go to ECA → **OAuth Settings** tab
  85 2. Copy the **Consumer Key** (starts with `3MVG9...`)
  86 3. Test authentication:
  87 
  88 ```bash
  89 # Option 1: Pass consumer key directly
  90 python3 scripts/cli.py test-auth \
  91     --org Vivint-DevInt \
  92     --consumer-key "3MVG9..."
  93 
  94 # Option 2: Use environment variable
  95 export SF_CONSUMER_KEY="3MVG9..."
  96 python3 scripts/cli.py test-auth --org Vivint-DevInt
  97 ```
  98 
  99 **Expected output:**
 100 ```
 101 Testing Authentication
 102 Org: Vivint-DevInt
 103 Key: /Users/you/.sf/jwt/Vivint-DevInt-agentforce-observability.key
 104 
 105 Getting org info...
 106 Instance: https://vivint--devint.sandbox.my.salesforce.com
 107 Username: your.user@vivint.com.devint
 108 Sandbox: True
 109 
 110 Testing token generation...
 111 ✓ Token generated
 112 
 113 Testing Data Cloud access...
 114 ✓ Data Cloud accessible
 115 
 116 Authentication successful!
 117 ```
 118 
 119 ---
 120 
 121 ## Key Path Resolution
 122 
 123 The CLI resolves the private key path in this order:
 124 
 125 1. **Explicit `--key-path`** argument (highest priority)
 126 2. **App-specific key**: `~/.sf/jwt/{org_alias}-agentforce-observability.key`
 127 3. **Generic org key**: `~/.sf/jwt/{org_alias}.key` (fallback)
 128 
 129 ### Examples
 130 
 131 ```bash
 132 # Uses app-specific key automatically
 133 python3 scripts/cli.py test-auth --org Vivint-DevInt --consumer-key "..."
 134 # → Resolves to: ~/.sf/jwt/Vivint-DevInt-agentforce-observability.key
 135 
 136 # Explicit key path (overrides all defaults)
 137 python3 scripts/cli.py test-auth --org Vivint-DevInt \
 138     --consumer-key "..." \
 139     --key-path ~/.sf/jwt/custom-key.key
 140 ```
 141 
 142 ---
 143 
 144 ## File Locations
 145 
 146 | File | Location | Description |
 147 |------|----------|-------------|
 148 | Private Key | `~/.sf/jwt/{org}-agentforce-observability.key` | RSA private key (chmod 600) |
 149 | Certificate | `~/.sf/jwt/{org}-agentforce-observability.crt` | X.509 cert uploaded to Salesforce |
 150 | Consumer Key | `$SF_CONSUMER_KEY` or `--consumer-key` | From ECA OAuth Settings |
 151 
 152 ---
 153 
 154 ## Required OAuth Scopes
 155 
 156 | Scope | Purpose | Required |
 157 |-------|---------|----------|
 158 | `cdp_query_api` | Execute Data Cloud SQL queries | ✅ Yes |
 159 | `refresh_token, offline_access` | Server-to-server access | ✅ Yes |
 160 | `cdp_profile_api` | Access profile and DMO metadata | Optional |
 161 
 162 ---
 163 
 164 ## Troubleshooting
 165 
 166 ### invalid_grant Error
 167 
 168 ```
 169 RuntimeError: Token exchange failed: invalid_grant
 170 ```
 171 
 172 **Causes & Fixes:**
 173 
 174 | Cause | Fix |
 175 |-------|-----|
 176 | Certificate mismatch | Re-upload `.crt` file to ECA |
 177 | Expired certificate | Regenerate with `openssl` (see Step 1) |
 178 | User not authorized | Add user to ECA policies (see Step 4) |
 179 | Wrong login URL | Verify sandbox detection is working |
 180 
 181 **Verify certificate expiry:**
 182 ```bash
 183 openssl x509 -enddate -noout -in ~/.sf/jwt/Vivint-DevInt-agentforce-observability.crt
 184 ```
 185 
 186 ### 403 Forbidden
 187 
 188 ```
 189 RuntimeError: Access denied: Ensure ECA has cdp_query_api scope
 190 ```
 191 
 192 **Fix:** Add `cdp_query_api` scope to the ECA OAuth Settings.
 193 
 194 ### Key Not Found
 195 
 196 ```
 197 FileNotFoundError: Private key not found at ~/.sf/jwt/myorg.key
 198 ```
 199 
 200 **Causes:**
 201 1. Key file doesn't exist → Generate with Step 1
 202 2. Wrong org alias → Check `sf org list` for correct alias
 203 3. Using old naming convention → Rename to `{org}-agentforce-observability.key`
 204 
 205 ### Permission Denied on Key
 206 
 207 ```
 208 PermissionError: [Errno 13] Permission denied: '~/.sf/jwt/...'
 209 ```
 210 
 211 **Fix:**
 212 ```bash
 213 chmod 600 ~/.sf/jwt/*.key
 214 ```
 215 
 216 ---
 217 
 218 ## Sandbox vs Production
 219 
 220 The skill automatically detects sandbox orgs:
 221 
 222 1. Reads `isSandbox` from `sf org display --json`
 223 2. Uses `https://test.salesforce.com` for token exchange (sandboxes)
 224 3. Uses `https://login.salesforce.com` for production
 225 
 226 No additional configuration needed.
 227 
 228 ---
 229 
 230 ## Security Best Practices
 231 
 232 1. **Protect private keys**: Always `chmod 600 ~/.sf/jwt/*.key`
 233 2. **Rotate certificates annually**: Regenerate before expiration
 234 3. **Use separate ECAs**: One per org/environment for isolation
 235 4. **Never commit keys**: Add `*.key` to `.gitignore`
 236 5. **Audit access**: Review ECA usage in Setup → Security → Connected Apps OAuth Usage
 237 
 238 ---
 239 
 240 ## Environment Variables
 241 
 242 For automation/CI, set these environment variables:
 243 
 244 ```bash
 245 # Consumer key (org-specific takes priority)
 246 export SF_VIVINT_DEVINT_CONSUMER_KEY="3MVG9..."
 247 # or generic fallback
 248 export SF_CONSUMER_KEY="3MVG9..."
 249 ```
 250 
 251 The CLI checks in this order:
 252 1. `--consumer-key` argument
 253 2. `SF_{ORG_ALIAS}_CONSUMER_KEY` (uppercase, hyphens to underscores)
 254 3. `SF_CONSUMER_KEY`
 255 
 256 ---
 257 
 258 ## See Also
 259 
 260 - [sf-connected-apps skill](../../sf-connected-apps/SKILL.md) - General ECA patterns
 261 - [CLI Reference](cli-reference.md) - All command options
 262 - [Troubleshooting](../references/troubleshooting.md) - More error solutions
