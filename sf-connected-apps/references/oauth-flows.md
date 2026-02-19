<!-- Parent: sf-connected-apps/SKILL.md -->
   1 # OAuth 2.0 Flows Reference
   2 
   3 Complete guide to OAuth flows supported by Salesforce Connected Apps and External Client Apps.
   4 
   5 ## Flow Decision Matrix
   6 
   7 | Use Case | Recommended Flow | PKCE | Refresh Token | Secret Required |
   8 |----------|-----------------|------|---------------|-----------------|
   9 | Web Server (backend) | Authorization Code | Optional | Yes | Yes |
  10 | Single Page App (SPA) | Authorization Code | **Required** | Yes (rotate) | No |
  11 | Mobile Native App | Authorization Code | **Required** | Yes (rotate) | No |
  12 | Server-to-Server | JWT Bearer | N/A | No | Certificate |
  13 | CI/CD Pipeline | JWT Bearer | N/A | No | Certificate |
  14 | IoT/Device | Device Authorization | N/A | Yes | No |
  15 | CLI Tool | Device Authorization | N/A | Yes | No |
  16 | Legacy (avoid) | Username-Password | N/A | Yes | Yes |
  17 
  18 ---
  19 
  20 ## Authorization Code Flow
  21 
  22 **Best for**: Web applications, Mobile apps, SPAs
  23 
  24 ### Flow Diagram
  25 ```
  26 ┌──────────┐      ┌───────────────┐      ┌────────────────┐
  27 │  User    │      │  Application  │      │   Salesforce   │
  28 └────┬─────┘      └───────┬───────┘      └───────┬────────┘
  29      │                    │                      │
  30      │  1. Click Login    │                      │
  31      │───────────────────>│                      │
  32      │                    │                      │
  33      │                    │  2. Redirect to      │
  34      │                    │     /authorize       │
  35      │<───────────────────┼─────────────────────>│
  36      │                    │                      │
  37      │  3. Login & Consent│                      │
  38      │─────────────────────────────────────────>│
  39      │                    │                      │
  40      │                    │  4. Redirect with    │
  41      │<───────────────────┼──────code───────────│
  42      │                    │                      │
  43      │                    │  5. Exchange code    │
  44      │                    │     for tokens       │
  45      │                    │─────────────────────>│
  46      │                    │                      │
  47      │                    │  6. Access Token +   │
  48      │                    │     Refresh Token    │
  49      │                    │<─────────────────────│
  50      │                    │                      │
  51      │  7. Authenticated  │                      │
  52      │<───────────────────│                      │
  53 ```
  54 
  55 ### Authorization URL
  56 ```
  57 https://login.salesforce.com/services/oauth2/authorize
  58   ?response_type=code
  59   &client_id=<CONSUMER_KEY>
  60   &redirect_uri=<CALLBACK_URL>
  61   &scope=api refresh_token
  62   &state=<CSRF_TOKEN>
  63   &code_challenge=<PKCE_CHALLENGE>        # For PKCE
  64   &code_challenge_method=S256              # For PKCE
  65 ```
  66 
  67 ### Token Exchange
  68 ```bash
  69 curl -X POST https://login.salesforce.com/services/oauth2/token \
  70   -d "grant_type=authorization_code" \
  71   -d "code=<AUTH_CODE>" \
  72   -d "client_id=<CONSUMER_KEY>" \
  73   -d "client_secret=<CONSUMER_SECRET>" \
  74   -d "redirect_uri=<CALLBACK_URL>" \
  75   -d "code_verifier=<PKCE_VERIFIER>"      # For PKCE
  76 ```
  77 
  78 ---
  79 
  80 ## JWT Bearer Flow
  81 
  82 **Best for**: Server-to-server integrations, CI/CD, Headless automation
  83 
  84 ### Prerequisites
  85 1. X.509 Certificate uploaded to Salesforce
  86 2. Connected App with certificate configured
  87 3. Pre-authorized user via Permission Set
  88 
  89 ### Flow Diagram
  90 ```
  91 ┌─────────────────┐                 ┌────────────────┐
  92 │  Server/CI/CD   │                 │   Salesforce   │
  93 └────────┬────────┘                 └───────┬────────┘
  94          │                                  │
  95          │  1. Create JWT with claims       │
  96          │     - iss: consumer_key          │
  97          │     - sub: username              │
  98          │     - aud: login.salesforce.com  │
  99          │     - exp: expiration            │
 100          │                                  │
 101          │  2. Sign JWT with private key    │
 102          │                                  │
 103          │  3. POST to /token               │
 104          │─────────────────────────────────>│
 105          │                                  │
 106          │  4. Validate signature with      │
 107          │     uploaded certificate         │
 108          │                                  │
 109          │  5. Access Token                 │
 110          │<─────────────────────────────────│
 111 ```
 112 
 113 ### JWT Structure
 114 ```json
 115 // Header
 116 {
 117   "alg": "RS256"
 118 }
 119 
 120 // Payload
 121 {
 122   "iss": "<CONSUMER_KEY>",
 123   "sub": "user@company.com",
 124   "aud": "https://login.salesforce.com",
 125   "exp": 1234567890
 126 }
 127 ```
 128 
 129 ### Token Request
 130 ```bash
 131 curl -X POST https://login.salesforce.com/services/oauth2/token \
 132   -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
 133   -d "assertion=<SIGNED_JWT>"
 134 ```
 135 
 136 ---
 137 
 138 ## Client Credentials Flow
 139 
 140 **Best for**: Service accounts, Background processes
 141 
 142 ### Configuration
 143 - Enable `isClientCredentialsEnabled` in ECA OAuth Settings
 144 - Assign execution user via Permission Set
 145 
 146 ### Token Request
 147 ```bash
 148 curl -X POST https://login.salesforce.com/services/oauth2/token \
 149   -d "grant_type=client_credentials" \
 150   -d "client_id=<CONSUMER_KEY>" \
 151   -d "client_secret=<CONSUMER_SECRET>"
 152 ```
 153 
 154 ### Agent Runtime API — Required Scopes (Multi-Turn API Testing Only)
 155 
 156 When creating an ECA for Agentforce Agent Runtime API testing (`/einstein/ai-agent/v1`), the following OAuth scopes are **required**:
 157 
 158 > **Not needed for `sf agent preview`:** As of SF CLI v2.121.7, interactive preview (simulated and live) uses standard org auth. These scopes are only required for automated multi-turn testing via the Agent Runtime API.
 159 
 160 | Scope | Purpose |
 161 |-------|---------|
 162 | `api` | Base REST API access |
 163 | `chatbot_api` | Agent Runtime API conversation endpoints |
 164 | `sfap_api` | Einstein platform services |
 165 
 166 **ECA Configuration for Agent API Testing:**
 167 ```xml
 168 <!-- In ecaOauth-meta.xml -->
 169 <ExtlClntAppOauthSettings>
 170     <oauthScopes>Api</oauthScopes>
 171     <oauthScopes>ChatbotApi</oauthScopes>
 172     <oauthScopes>SfapApi</oauthScopes>
 173     <isClientCredentialsEnabled>true</isClientCredentialsEnabled>
 174     <!-- ... -->
 175 </ExtlClntAppOauthSettings>
 176 ```
 177 
 178 **Post-Deploy Steps:**
 179 1. In Setup, navigate to the ECA → **Manage** → **Edit Policies**
 180 2. Set **"Run As"** to an active Einstein Agent User
 181 3. Verify the agent's `GenAiPlannerBundle` has `plannerSurfaces` with `EinsteinAgentApiChannel`
 182 4. Verify the agent's `BotVersion` has `surfacesEnabled=true`
 183 
 184 > See `/sf-ai-agentforce-testing` and `/sf-ai-agentscript` for full Agent Runtime API testing workflow.
 185 
 186 ---
 187 
 188 ## Device Authorization Flow
 189 
 190 **Best for**: CLI tools, Smart TVs, IoT devices without browsers
 191 
 192 ### Flow Diagram
 193 ```
 194 ┌─────────────┐         ┌───────────────┐         ┌────────────────┐
 195 │   Device    │         │     User      │         │   Salesforce   │
 196 └──────┬──────┘         └───────┬───────┘         └───────┬────────┘
 197        │                        │                         │
 198        │  1. Request device code│                         │
 199        │─────────────────────────────────────────────────>│
 200        │                        │                         │
 201        │  2. device_code + user_code + verification_uri  │
 202        │<─────────────────────────────────────────────────│
 203        │                        │                         │
 204        │  3. Display code       │                         │
 205        │───────────────────────>│                         │
 206        │                        │                         │
 207        │                        │  4. Visit URL & enter   │
 208        │                        │     user_code           │
 209        │                        │────────────────────────>│
 210        │                        │                         │
 211        │  5. Poll for token     │                         │
 212        │─────────────────────────────────────────────────>│
 213        │                        │                         │
 214        │  6. Access Token (when authorized)               │
 215        │<─────────────────────────────────────────────────│
 216 ```
 217 
 218 ### Device Code Request
 219 ```bash
 220 curl -X POST https://login.salesforce.com/services/oauth2/device/code \
 221   -d "client_id=<CONSUMER_KEY>" \
 222   -d "scope=api refresh_token"
 223 ```
 224 
 225 ### Poll for Token
 226 ```bash
 227 curl -X POST https://login.salesforce.com/services/oauth2/token \
 228   -d "grant_type=device" \
 229   -d "client_id=<CONSUMER_KEY>" \
 230   -d "code=<DEVICE_CODE>"
 231 ```
 232 
 233 ---
 234 
 235 ## Refresh Token Flow
 236 
 237 **Use**: Exchange refresh token for new access token
 238 
 239 ```bash
 240 curl -X POST https://login.salesforce.com/services/oauth2/token \
 241   -d "grant_type=refresh_token" \
 242   -d "client_id=<CONSUMER_KEY>" \
 243   -d "client_secret=<CONSUMER_SECRET>" \
 244   -d "refresh_token=<REFRESH_TOKEN>"
 245 ```
 246 
 247 ---
 248 
 249 ## PKCE (Proof Key for Code Exchange)
 250 
 251 **Required for**: Mobile apps, SPAs, Public clients
 252 
 253 ### Generate Code Verifier & Challenge
 254 
 255 ```javascript
 256 // Generate random code verifier (43-128 chars)
 257 const codeVerifier = base64URLEncode(crypto.randomBytes(32));
 258 
 259 // Create code challenge
 260 const codeChallenge = base64URLEncode(
 261   crypto.createHash('sha256').update(codeVerifier).digest()
 262 );
 263 ```
 264 
 265 ### Use in Authorization
 266 ```
 267 /authorize?...&code_challenge=<CHALLENGE>&code_challenge_method=S256
 268 ```
 269 
 270 ### Use in Token Exchange
 271 ```
 272 grant_type=authorization_code&...&code_verifier=<VERIFIER>
 273 ```
 274 
 275 ---
 276 
 277 ## Token Introspection
 278 
 279 **Use**: Validate token status and metadata
 280 
 281 ```bash
 282 curl -X POST https://login.salesforce.com/services/oauth2/introspect \
 283   -d "token=<ACCESS_TOKEN>" \
 284   -d "client_id=<CONSUMER_KEY>" \
 285   -d "client_secret=<CONSUMER_SECRET>" \
 286   -d "token_type_hint=access_token"
 287 ```
 288 
 289 ---
 290 
 291 ## Token Revocation
 292 
 293 **Use**: Invalidate tokens on logout
 294 
 295 ```bash
 296 curl -X POST https://login.salesforce.com/services/oauth2/revoke \
 297   -d "token=<TOKEN>"
 298 ```
 299 
 300 ---
 301 
 302 ## Best Practices
 303 
 304 1. **Always use HTTPS** for callback URLs in production
 305 2. **Enable PKCE** for all public clients (mobile, SPA)
 306 3. **Use short-lived access tokens** with refresh token rotation
 307 4. **Store secrets securely** - never in client-side code
 308 5. **Implement state parameter** to prevent CSRF
 309 6. **Validate tokens** before trusting claims
 310 7. **Use JWT Bearer** for server-to-server instead of username-password
