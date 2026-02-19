<!-- Parent: sf-connected-apps/SKILL.md -->
   1 # Migration Guide: Connected App → External Client App
   2 
   3 Step-by-step guide for migrating from Connected Apps to External Client Apps (ECAs).
   4 
   5 ## Why Migrate?
   6 
   7 | Feature | Connected App | External Client App |
   8 |---------|--------------|---------------------|
   9 | Metadata Compliance | Partial | Full |
  10 | Secret in Sandboxes | Visible | Hidden |
  11 | Key Rotation | Manual | Automated via API |
  12 | Multi-Org Distribution | Manual recreation | Native 2GP packaging |
  13 | Audit Logging | Limited | MFA + full audit |
  14 | Security Model | Open by default | Closed by default |
  15 
  16 **Migrate when**:
  17 - Distributing to multiple orgs (ISV, enterprise)
  18 - Compliance requires audit trails
  19 - DevOps needs automated credential rotation
  20 - Moving to 2GP packaging
  21 
  22 ---
  23 
  24 ## Migration Process
  25 
  26 ### Phase 1: Assessment
  27 
  28 #### 1.1 Inventory Current Apps
  29 
  30 ```bash
  31 # List all Connected Apps
  32 sf org list metadata --metadata-type ConnectedApp --target-org <org>
  33 
  34 # Retrieve for analysis
  35 sf project retrieve start --metadata ConnectedApp --output-dir ./migration-review
  36 ```
  37 
  38 #### 1.2 Document Configuration
  39 
  40 For each Connected App, record:
  41 
  42 | Setting | Value |
  43 |---------|-------|
  44 | App Name | |
  45 | Consumer Key | |
  46 | OAuth Scopes | |
  47 | Callback URLs | |
  48 | IP Restrictions | |
  49 | Token Policy | |
  50 | Certificate (if JWT) | |
  51 
  52 #### 1.3 Identify Integrations
  53 
  54 List all systems using each Connected App:
  55 - External applications
  56 - CI/CD pipelines
  57 - Third-party tools
  58 - Mobile applications
  59 
  60 ---
  61 
  62 ### Phase 2: Planning
  63 
  64 #### 2.1 Choose Distribution Model
  65 
  66 | Scenario | Distribution State |
  67 |----------|-------------------|
  68 | Single org only | `Local` |
  69 | Multiple orgs, same company | `Local` per org or `Packageable` |
  70 | ISV/AppExchange | `Packageable` |
  71 
  72 #### 2.2 Plan Credential Rollover
  73 
  74 ```
  75 Timeline Example:
  76 Week 1: Create ECA, deploy to DevHub
  77 Week 2: Update integration systems with new credentials
  78 Week 3: Test in sandbox environments
  79 Week 4: Production cutover
  80 Week 5-8: Monitor, keep old app active as fallback
  81 Week 9: Deactivate Connected App
  82 Week 12: Delete Connected App
  83 ```
  84 
  85 ---
  86 
  87 ### Phase 3: Create External Client App
  88 
  89 #### 3.1 Prepare Scratch Org (if needed)
  90 
  91 ```json
  92 // config/project-scratch-def.json
  93 {
  94   "orgName": "ECA Migration Dev",
  95   "edition": "Developer",
  96   "features": [
  97     "ExternalClientApps",
  98     "ExtlClntAppSecretExposeCtl"
  99   ]
 100 }
 101 ```
 102 
 103 #### 3.2 Create ECA Metadata Files
 104 
 105 **File 1: Header** (`MyApp.eca-meta.xml`)
 106 ```xml
 107 <?xml version="1.0" encoding="UTF-8"?>
 108 <ExternalClientApplication xmlns="http://soap.sforce.com/2006/04/metadata">
 109     <contactEmail>team@company.com</contactEmail>
 110     <description>Migrated from Connected App: MyConnectedApp</description>
 111     <distributionState>Local</distributionState>
 112     <isProtected>false</isProtected>
 113     <label>MyApp</label>
 114 </ExternalClientApplication>
 115 ```
 116 
 117 **File 2: Global OAuth** (`MyApp.ecaGlobalOauth-meta.xml`)
 118 ```xml
 119 <?xml version="1.0" encoding="UTF-8"?>
 120 <ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
 121     <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
 122     <isConsumerSecretOptional>false</isConsumerSecretOptional>
 123     <isPkceRequired>true</isPkceRequired>
 124     <shouldRotateConsumerKey>true</shouldRotateConsumerKey>
 125     <shouldRotateConsumerSecret>true</shouldRotateConsumerSecret>
 126 </ExtlClntAppGlobalOauthSettings>
 127 ```
 128 
 129 **File 3: OAuth Settings** (`MyApp.ecaOauth-meta.xml`)
 130 ```xml
 131 <?xml version="1.0" encoding="UTF-8"?>
 132 <ExtlClntAppOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
 133     <isAdminApproved>true</isAdminApproved>
 134     <isCodeCredentialsEnabled>true</isCodeCredentialsEnabled>
 135     <isClientCredentialsEnabled>false</isClientCredentialsEnabled>
 136     <isRefreshTokenEnabled>true</isRefreshTokenEnabled>
 137     <scopes>Api</scopes>
 138     <scopes>RefreshToken</scopes>
 139 </ExtlClntAppOauthSettings>
 140 ```
 141 
 142 #### 3.3 Deploy to DevHub/Org
 143 
 144 ```bash
 145 sf project deploy start \
 146   --source-dir force-app/main/default/externalClientApps \
 147   --target-org <target-org>
 148 ```
 149 
 150 #### 3.4 Retrieve New Consumer Key
 151 
 152 After deployment:
 153 1. Go to Setup → External Client App Manager
 154 2. Select your ECA
 155 3. View Consumer Key (MFA required)
 156 4. Securely store credentials
 157 
 158 ---
 159 
 160 ### Phase 4: Update Integrations
 161 
 162 #### 4.1 Update External Systems
 163 
 164 For each integrated system:
 165 
 166 1. Update OAuth endpoint (if different environment)
 167 2. Replace Consumer Key
 168 3. Replace Consumer Secret
 169 4. Test authentication flow
 170 5. Verify API access
 171 
 172 #### 4.2 Configuration Mapping
 173 
 174 | Connected App Setting | ECA Equivalent |
 175 |----------------------|----------------|
 176 | Consumer Key | New Consumer Key (different) |
 177 | Consumer Secret | New Consumer Secret (different) |
 178 | Callback URL | Same (in ecaGlobalOauth) |
 179 | Scopes | Same (in ecaOauth) |
 180 | IP Relaxation | In ecaPolicy (admin-managed) |
 181 | Refresh Token Policy | In ecaPolicy (admin-managed) |
 182 
 183 ---
 184 
 185 ### Phase 5: Testing
 186 
 187 #### 5.1 Test Checklist
 188 
 189 - [ ] Authorization Code flow works
 190 - [ ] Token refresh works
 191 - [ ] API calls succeed
 192 - [ ] Scopes are correct
 193 - [ ] Error handling works
 194 - [ ] Logout/revocation works
 195 
 196 #### 5.2 Test Script
 197 
 198 ```bash
 199 # Test Authorization Code Flow
 200 curl "https://login.salesforce.com/services/oauth2/authorize?\
 201 response_type=code&\
 202 client_id=<NEW_CONSUMER_KEY>&\
 203 redirect_uri=<CALLBACK_URL>&\
 204 scope=api%20refresh_token"
 205 
 206 # Test Token Exchange
 207 curl -X POST https://login.salesforce.com/services/oauth2/token \
 208   -d "grant_type=authorization_code" \
 209   -d "code=<AUTH_CODE>" \
 210   -d "client_id=<NEW_CONSUMER_KEY>" \
 211   -d "client_secret=<NEW_CONSUMER_SECRET>" \
 212   -d "redirect_uri=<CALLBACK_URL>"
 213 ```
 214 
 215 ---
 216 
 217 ### Phase 6: Cutover
 218 
 219 #### 6.1 Production Deployment
 220 
 221 ```bash
 222 # Deploy ECA to production
 223 sf project deploy start \
 224   --source-dir force-app/main/default/externalClientApps \
 225   --target-org production
 226 ```
 227 
 228 #### 6.2 Cutover Steps
 229 
 230 1. Deploy ECA to production
 231 2. Configure policies in Setup
 232 3. Update production integrations
 233 4. Monitor for errors
 234 5. Keep Connected App active as fallback
 235 
 236 ---
 237 
 238 ### Phase 7: Decommission
 239 
 240 #### 7.1 Deactivate Connected App
 241 
 242 1. Go to Setup → Connected Apps → Manage Connected Apps
 243 2. Select the old Connected App
 244 3. Click "Edit Policies"
 245 4. Set "Permitted Users" to "Admin approved users are pre-authorized"
 246 5. Remove all user/profile assignments
 247 
 248 #### 7.2 Monitor Period
 249 
 250 - Monitor for 30 days minimum
 251 - Check for authentication failures
 252 - Investigate any traffic to old app
 253 
 254 #### 7.3 Delete Connected App
 255 
 256 After monitoring period:
 257 
 258 ```bash
 259 # Remove from source control
 260 rm force-app/main/default/connectedApps/OldApp.connectedApp-meta.xml
 261 
 262 # Or delete via Setup UI
 263 ```
 264 
 265 ---
 266 
 267 ## Rollback Plan
 268 
 269 If migration fails:
 270 
 271 1. **Immediate**: Revert external systems to old Consumer Key
 272 2. **Short-term**: Keep Connected App active during transition
 273 3. **Long-term**: Document issues and retry migration
 274 
 275 ---
 276 
 277 ## Common Issues
 278 
 279 | Issue | Cause | Solution |
 280 |-------|-------|----------|
 281 | "Invalid consumer key" | Using old key | Update to new ECA key |
 282 | "Callback URL mismatch" | URL not in ECA config | Add URL to ecaGlobalOauth |
 283 | "Scope not allowed" | Scope not in ecaOauth | Add required scope |
 284 | "User not authorized" | No policy assignment | Assign user via Permission Set |
 285 | "MFA required" | ECA security | Complete MFA challenge |
 286 
 287 ---
 288 
 289 ## Automation Script
 290 
 291 ```bash
 292 #!/bin/bash
 293 # migrate-connected-app.sh
 294 
 295 APP_NAME=$1
 296 TARGET_ORG=$2
 297 
 298 echo "📦 Migrating Connected App: $APP_NAME"
 299 
 300 # 1. Retrieve existing Connected App
 301 sf project retrieve start \
 302   --metadata "ConnectedApp:$APP_NAME" \
 303   --target-org $TARGET_ORG \
 304   --output-dir ./migration
 305 
 306 # 2. Create ECA directory
 307 mkdir -p force-app/main/default/externalClientApps
 308 
 309 # 3. Deploy ECA (assumes files are created)
 310 sf project deploy start \
 311   --source-dir force-app/main/default/externalClientApps \
 312   --target-org $TARGET_ORG
 313 
 314 echo "✅ ECA deployed. Retrieve new Consumer Key from Setup."
 315 ```
