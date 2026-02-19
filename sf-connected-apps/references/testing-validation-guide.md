<!-- Parent: sf-connected-apps/SKILL.md -->
   1 # Testing & Validation Guide
   2 
   3 This guide documents tested External Client App (ECA) and Connected App patterns based on systematic validation testing (December 2025).
   4 
   5 ## Test Matrix
   6 
   7 | Component Type | Template | Test Status |
   8 |----------------|----------|-------------|
   9 | Connected App (Basic) | `connected-app-basic.xml` | ✅ Verified |
  10 | Connected App (Full OAuth) | `connected-app-oauth.xml` | ✅ Verified |
  11 | Connected App (JWT Bearer) | `connected-app-jwt.xml` | ✅ Verified |
  12 | Connected App (Canvas) | `connected-app-canvas.xml` | ⚠️ Location-dependent |
  13 | External Client App | `external-client-app.xml` | ✅ Verified |
  14 | ECA Global OAuth | `eca-global-oauth.xml` | ✅ Verified |
  15 | ECA OAuth Settings | `eca-oauth-settings.xml` | ✅ Verified |
  16 
  17 ---
  18 
  19 ## Critical File Naming Conventions
  20 
  21 ### External Client App Files
  22 
  23 | Metadata Type | File Suffix | Example |
  24 |--------------|-------------|---------|
  25 | ExternalClientApplication | `.eca-meta.xml` | `MyApp.eca-meta.xml` |
  26 | ExtlClntAppOauthSettings | `.ecaOauth-meta.xml` | `MyApp.ecaOauth-meta.xml` |
  27 | ExtlClntAppGlobalOauthSettings | `.ecaGlblOauth-meta.xml` | `MyApp.ecaGlblOauth-meta.xml` |
  28 | ExtlClntAppOauthConfigurablePolicies | `.ecaOauthPlcy-meta.xml` | `MyApp.ecaOauthPlcy-meta.xml` |
  29 
  30 ⚠️ **CRITICAL**: Use `.ecaGlblOauth` (abbreviated), NOT `.ecaGlobalOauth`
  31 
  32 ### Connected App Files
  33 
  34 | Metadata Type | File Suffix | Example |
  35 |--------------|-------------|---------|
  36 | ConnectedApp | `.connectedApp-meta.xml` | `MyApp.connectedApp-meta.xml` |
  37 
  38 ---
  39 
  40 ## Common Deployment Errors & Solutions
  41 
  42 ### Error: "Invalid or missing field" in ECA OAuth Settings
  43 
  44 **Cause**: Using wrong schema with non-existent fields
  45 
  46 **Wrong Schema (FAILS):**
  47 ```xml
  48 <ExtlClntAppOauthSettings>
  49     <isAdminApproved>true</isAdminApproved>           <!-- DOES NOT EXIST -->
  50     <isCodeCredentialsEnabled>true</isCodeCredentialsEnabled>  <!-- DOES NOT EXIST -->
  51     <scopes>Api</scopes>                               <!-- WRONG FORMAT -->
  52 </ExtlClntAppOauthSettings>
  53 ```
  54 
  55 **Correct Schema:**
  56 ```xml
  57 <ExtlClntAppOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
  58     <commaSeparatedOauthScopes>Api, RefreshToken</commaSeparatedOauthScopes>
  59     <externalClientApplication>MyApp</externalClientApplication>
  60     <label>MyApp OAuth Settings</label>
  61 </ExtlClntAppOauthSettings>
  62 ```
  63 
  64 ### Error: "Missing required field" in ECA Global OAuth
  65 
  66 **Cause**: Missing `externalClientApplication` or `label`
  67 
  68 **Wrong (FAILS):**
  69 ```xml
  70 <ExtlClntAppGlobalOauthSettings>
  71     <callbackUrl>https://example.com/callback</callbackUrl>
  72     <isPkceRequired>true</isPkceRequired>
  73 </ExtlClntAppGlobalOauthSettings>
  74 ```
  75 
  76 **Correct:**
  77 ```xml
  78 <ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
  79     <callbackUrl>https://example.com/callback</callbackUrl>
  80     <externalClientApplication>MyApp</externalClientApplication>
  81     <isConsumerSecretOptional>true</isConsumerSecretOptional>
  82     <isIntrospectAllTokens>false</isIntrospectAllTokens>
  83     <isPkceRequired>true</isPkceRequired>
  84     <isSecretRequiredForRefreshToken>false</isSecretRequiredForRefreshToken>
  85     <label>MyApp Global OAuth</label>
  86     <shouldRotateConsumerKey>false</shouldRotateConsumerKey>
  87     <shouldRotateConsumerSecret>false</shouldRotateConsumerSecret>
  88 </ExtlClntAppGlobalOauthSettings>
  89 ```
  90 
  91 ### Error: "Organization is not configured to support location"
  92 
  93 **Cause**: Canvas app using location that requires org feature enablement
  94 
  95 **Problematic Locations:**
  96 - `AppLauncher` - Requires feature enablement
  97 - Some other locations may have similar requirements
  98 
  99 **Solution**: Use universally available locations:
 100 ```xml
 101 <canvasApp>
 102     <locations>Visualforce</locations>
 103 </canvasApp>
 104 ```
 105 
 106 ### Error: Certificate not found (JWT Bearer)
 107 
 108 **Cause**: Referenced certificate doesn't exist in org
 109 
 110 **Wrong:**
 111 ```xml
 112 <certificate>NonExistent_Cert</certificate>
 113 ```
 114 
 115 **Solution**: Create certificate first, then reference it:
 116 ```bash
 117 # 1. Create certificate in org (Setup > Certificate and Key Management)
 118 # 2. Reference in Connected App
 119 <certificate>My_JWT_Cert</certificate>
 120 ```
 121 
 122 ---
 123 
 124 ## Field Reference
 125 
 126 ### ExtlClntAppOauthSettings (ECA OAuth)
 127 
 128 | Field | Type | Required | Description |
 129 |-------|------|----------|-------------|
 130 | `commaSeparatedOauthScopes` | String | Yes | Comma-separated scopes (e.g., "Api, RefreshToken") |
 131 | `externalClientApplication` | String | Yes | Reference to parent ECA API name |
 132 | `label` | String | Yes | Display label |
 133 
 134 **Available Scopes:**
 135 - `Api` - REST/SOAP API access
 136 - `RefreshToken` - Offline access
 137 - `OpenID` - OpenID Connect
 138 - `Profile` - User profile info
 139 - `Email` - User email
 140 - `Web` - Web browser access
 141 - `ChatterApi` - Chatter REST API
 142 
 143 ### ExtlClntAppGlobalOauthSettings (ECA Global OAuth)
 144 
 145 | Field | Type | Required | Description |
 146 |-------|------|----------|-------------|
 147 | `callbackUrl` | URL | Yes | OAuth redirect URI |
 148 | `externalClientApplication` | String | Yes | Reference to parent ECA |
 149 | `isConsumerSecretOptional` | Boolean | No | True for public clients with PKCE |
 150 | `isIntrospectAllTokens` | Boolean | No | Enable token introspection |
 151 | `isPkceRequired` | Boolean | No | Require PKCE (recommended for public clients) |
 152 | `isSecretRequiredForRefreshToken` | Boolean | No | Require secret for refresh |
 153 | `label` | String | Yes | Display label |
 154 | `shouldRotateConsumerKey` | Boolean | No | Enable key rotation |
 155 | `shouldRotateConsumerSecret` | Boolean | No | Enable secret rotation |
 156 
 157 ---
 158 
 159 ## Deployment Order
 160 
 161 For External Client Apps, deploy in this order:
 162 
 163 ```bash
 164 # 1. Deploy base ECA first
 165 sf project deploy start --metadata ExternalClientApplication:MyApp --target-org [alias]
 166 
 167 # 2. Deploy OAuth settings
 168 sf project deploy start --metadata ExtlClntAppOauthSettings:MyApp --target-org [alias]
 169 
 170 # 3. Deploy Global OAuth (if needed)
 171 sf project deploy start --metadata ExtlClntAppGlobalOauthSettings:MyApp --target-org [alias]
 172 
 173 # Or deploy all together (recommended)
 174 sf project deploy start --source-dir force-app/main/default/externalClientApps --target-org [alias]
 175 ```
 176 
 177 ---
 178 
 179 ## Post-Deployment Steps
 180 
 181 ### Client Credentials Flow (ECA)
 182 
 183 Client Credentials flow requires additional configuration **not available via metadata**:
 184 
 185 1. **Create Permission Set** with "Salesforce API Integration" permission
 186 2. **Assign Permission Set** to the External Client App
 187 3. **Configure Execution User** in Setup
 188 
 189 ### JWT Bearer Flow (Connected App)
 190 
 191 1. **Upload Certificate** to org before deployment
 192 2. **Pre-authorize Users** after deployment (Setup > Manage Connected Apps)
 193 
 194 ---
 195 
 196 ## Deployment Checklist
 197 
 198 ### External Client App
 199 
 200 - [ ] `.eca-meta.xml` file exists
 201 - [ ] `.ecaOauth-meta.xml` file exists (not ecaOAuth)
 202 - [ ] `.ecaGlblOauth-meta.xml` uses abbreviated suffix (not ecaGlobalOauth)
 203 - [ ] All files reference same `externalClientApplication` name
 204 - [ ] All files have `label` field
 205 - [ ] `commaSeparatedOauthScopes` uses string format, not individual `<scopes>` tags
 206 - [ ] Callback URL is HTTPS (or custom scheme for mobile)
 207 - [ ] PKCE enabled for public clients
 208 
 209 ### Connected App
 210 
 211 - [ ] `.connectedApp-meta.xml` file exists
 212 - [ ] `contactEmail` is valid
 213 - [ ] Callback URL matches OAuth flow requirements
 214 - [ ] Certificate exists in org (for JWT Bearer)
 215 - [ ] Canvas locations are supported by org (if using Canvas)
 216 
 217 ---
 218 
 219 ## Tested Configurations
 220 
 221 ### Minimal ECA (API Integration)
 222 
 223 ```
 224 Files:
 225 ├── MyApp.eca-meta.xml
 226 ├── MyApp.ecaOauth-meta.xml
 227 └── MyApp.ecaGlblOauth-meta.xml
 228 
 229 Scopes: Api, RefreshToken
 230 PKCE: false (confidential client)
 231 ```
 232 
 233 ### Mobile App ECA (PKCE)
 234 
 235 ```
 236 Files:
 237 ├── MobileApp.eca-meta.xml
 238 ├── MobileApp.ecaOauth-meta.xml
 239 └── MobileApp.ecaGlblOauth-meta.xml
 240 
 241 Scopes: Api, RefreshToken, OpenID
 242 PKCE: true (public client)
 243 Callback: com.example.app://oauth/callback
 244 ```
 245 
 246 ### Server-to-Server ECA
 247 
 248 ```
 249 Files:
 250 ├── ServiceApp.eca-meta.xml
 251 └── ServiceApp.ecaOauth-meta.xml
 252 
 253 Scopes: Api
 254 Note: Client Credentials requires post-deployment Permission Set assignment
 255 ```
 256 
 257 ---
 258 
 259 *Last Updated: December 2025*
 260 *Based on testing with SF CLI and API v65.0*
