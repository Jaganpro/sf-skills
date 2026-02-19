<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
   1 # External Client App (ECA) Setup for Agent API Testing
   2 
   3 Guide for creating an External Client App with Client Credentials flow to authenticate with the Agent Runtime API.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 The Agent Runtime API requires **OAuth 2.0 Client Credentials flow**, which is different from the Web Server OAuth flow used by `sf agent preview`. This requires an **External Client App (ECA)**, not a standard Connected App.
  10 
  11 ### OAuth Flow Comparison
  12 
  13 | Flow | Used By | App Type | User Interaction |
  14 |------|---------|----------|-----------------|
  15 | **Standard Org Auth** | `sf agent preview --use-live-actions` | None (standard `sf org login web`) | Browser login required |
  16 | **Client Credentials** | Agent Runtime API (multi-turn testing) | External Client App (ECA) | None (machine-to-machine) |
  17 
  18 > **Key Difference:** Client Credentials flow is machine-to-machine — no browser login needed. Perfect for automated testing.
  19 
  20 ---
  21 
  22 ## Prerequisites
  23 
  24 | Requirement | Details |
  25 |-------------|---------|
  26 | Salesforce org with Agentforce | Agent must be published and activated |
  27 | System Administrator profile | Required to create ECAs |
  28 | My Domain enabled | Required for OAuth endpoints |
  29 | Agent Runtime API access | Included with Agentforce license |
  30 
  31 ---
  32 
  33 ## Quick Setup
  34 
  35 ### Option 1: Use sf-connected-apps Skill (Recommended)
  36 
  37 ```
  38 Skill(skill="sf-connected-apps", args="Create External Client App with Client Credentials flow for Agent Runtime API testing. Scopes: api, chatbot_api, sfap_api, refresh_token, offline_access")
  39 ```
  40 
  41 ### Option 2: Manual Setup via UI
  42 
  43 Follow the steps below.
  44 
  45 ---
  46 
  47 ## Step-by-Step Manual Creation
  48 
  49 ### Step 1: Navigate to External Client App Setup
  50 
  51 1. **Setup** → Quick Find → **App Manager**
  52 2. Click **New Connected App** → Select **External Client App**
  53 3. Or: **Setup** → Quick Find → **External Client Apps**
  54 
  55 ### Step 2: Basic Information
  56 
  57 | Field | Value |
  58 |-------|-------|
  59 | **Name** | Agent API Testing |
  60 | **API Name** | Agent_API_Testing |
  61 | **Contact Email** | Your admin email |
  62 | **Description** | ECA for Agent Runtime API multi-turn testing |
  63 
  64 ### Step 3: Configure Client Credentials
  65 
  66 1. Under **OAuth Settings**:
  67    - **Enable Client Credentials Flow**: ✅ Checked
  68    - **Grant Type**: Client Credentials
  69 2. **Callback URL**: Not required for Client Credentials (use `https://login.salesforce.com/services/oauth2/callback` if field is mandatory)
  70 
  71 ### Step 4: OAuth Scopes
  72 
  73 | Scope | Purpose | Required |
  74 |-------|---------|----------|
  75 | `api` | Manage user data via APIs | ✅ Yes |
  76 | `chatbot_api` | Access chatbot/agent services | ✅ Yes |
  77 | `sfap_api` | Access the Salesforce API Platform | ✅ Yes |
  78 | `refresh_token, offline_access` | Perform requests at any time | Recommended |
  79 
  80 > **Minimum Required:** `api`, `chatbot_api`, and `sfap_api` together enable Agent Runtime API access.
  81 
  82 ### Additional OAuth Settings
  83 
  84 | Setting | Value |
  85 |---------|-------|
  86 | **Enable Client Credentials Flow** | ✅ Checked |
  87 | **Issue JWT-based access tokens for named users** | ✅ Checked |
  88 | Require secret for Web Server Flow | ❌ Deselected |
  89 | Require secret for Refresh Token Flow | ❌ Deselected |
  90 | Require PKCE for Supported Authorization Flows | ❌ Deselected |
  91 
  92 ### Step 5: Execution User (Run As)
  93 
  94 For Client Credentials flow, you must assign an **execution user**:
  95 
  96 1. From your app settings, click the **Policy** tab
  97 2. Click **Edit**
  98 3. Under **OAuth Flows and External Client App Enhancements**:
  99    - Check **Enable Client Credentials Flow**
 100    - Set **Run As (Username)** to a user with at least API Only access
 101 4. Save the changes
 102 
 103 The execution user's permissions determine what the API can access:
 104 - Must have at least API access
 105 - Must have access to the agents being tested
 106 - System Administrator profile works but use least-privilege when possible
 107 
 108 ### Step 6: Save and Retrieve Credentials
 109 
 110 1. **Save** the External Client App
 111 2. Click **Manage Consumer Details**
 112 3. Verify identity (email/SMS code)
 113 4. Copy:
 114    - **Consumer Key** (Client ID)
 115    - **Consumer Secret** (Client Secret)
 116 
 117 > ⚠️ **Security:** Store credentials securely. Never commit them to source control or write them to files during testing. Keep them in shell variables within the conversation context only.
 118 
 119 ---
 120 
 121 ## Verify ECA Configuration
 122 
 123 ### Test Token Request
 124 
 125 > **NEVER use `curl` for OAuth token validation.** Domains containing `--` (e.g., `my-org--devint.sandbox.my.salesforce.com`) cause shell expansion failures with curl's `--` argument parsing. Use the credential manager script instead.
 126 
 127 ```bash
 128 # Validate credentials via credential_manager.py (handles OAuth internally)
 129 python3 ~/.claude/skills/sf-ai-agentforce-testing/hooks/scripts/credential_manager.py \
 130   validate --org-alias {org} --eca-name {eca}
 131 ```
 132 
 133 The script outputs JSON with the validation result including token metadata (scopes, instance URL, token type).
 134 
 135 ### Expected Success Response
 136 
 137 ```json
 138 {
 139   "access_token": "eyJ0bmsiOiJjb3JlL3Byb2QvM...(JWT token)",
 140   "signature": "HBb7Zf4aaOUlI1V...",
 141   "token_format": "jwt",
 142   "scope": "sfap_api chatbot_api api",
 143   "instance_url": "https://your-domain.my.salesforce.com",
 144   "id": "https://login.salesforce.com/id/00D.../005...",
 145   "token_type": "Bearer",
 146   "issued_at": "1700000000000",
 147   "api_instance_url": "https://api.salesforce.com"
 148 }
 149 ```
 150 
 151 ### Common Errors
 152 
 153 | Error | Cause | Fix |
 154 |-------|-------|-----|
 155 | `invalid_client_id` | Wrong Consumer Key | Re-copy from ECA settings |
 156 | `invalid_client` | Client Credentials not enabled | Enable in ECA OAuth settings |
 157 | `invalid_grant` | No execution user assigned | Assign Run As user in ECA |
 158 | `unsupported_grant_type` | Not an ECA (standard Connected App) | Create an External Client App, not Connected App |
 159 | `INVALID_SESSION_ID` | Token expired or revoked | Re-authenticate |
 160 
 161 ---
 162 
 163 ## ECA vs Connected App: When to Use Which
 164 
 165 | Scenario | Use | Why |
 166 |----------|-----|-----|
 167 | `sf agent preview --use-live-actions` | Standard org auth | No app setup needed (v2.121.7+) |
 168 | Multi-turn API testing | External Client App (Client Credentials) | Machine-to-machine, no browser needed |
 169 | CI/CD automated testing | External Client App (Client Credentials) | Non-interactive, scriptable |
 170 | Manual ad-hoc testing | Either | Depends on test approach |
 171 
 172 ---
 173 
 174 ## Security Best Practices
 175 
 176 | Practice | Description |
 177 |----------|-------------|
 178 | **Never write secrets to files** | Keep Consumer Key/Secret in shell variables only |
 179 | **Use least-privilege execution user** | Don't use full admin if not needed |
 180 | **Rotate secrets periodically** | Regenerate Consumer Secret quarterly |
 181 | **Limit OAuth scopes** | Only include scopes needed for testing |
 182 | **Monitor usage** | Review ECA login history in Setup |
 183 | **Separate test and production ECAs** | Never reuse production credentials for testing |
 184 
 185 ---
 186 
 187 ## Integration with Testing Workflow
 188 
 189 Once ECA is configured, the testing skill uses it as follows:
 190 
 191 ```
 192 1. AskUserQuestion: "Do you have an ECA with Client Credentials?"
 193    │
 194    ├─ YES → Collect Consumer Key, Secret, My Domain URL
 195    │        (stored in conversation context only)
 196    │
 197    └─ NO → Delegate:
 198            Skill(skill="sf-connected-apps",
 199              args="Create ECA with Client Credentials for Agent API testing")
 200            Then collect credentials from user
 201    │
 202    ▼
 203 2. Authenticate and retrieve access token
 204 3. Query BotDefinition for agent ID
 205 4. Begin multi-turn test execution
 206 ```
 207 
 208 ---
 209 
 210 ## Related Documentation
 211 
 212 | Resource | Link |
 213 |----------|------|
 214 | Agent Runtime API | [agent-api-reference.md](agent-api-reference.md) |
 215 | Connected App Setup (Web OAuth) | [connected-app-setup.md](connected-app-setup.md) |
 216 | Multi-Turn Testing Guide | [multi-turn-testing-guide.md](multi-turn-testing-guide.md) |
