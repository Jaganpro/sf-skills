<!-- Parent: sf-connected-apps/SKILL.md -->
   1 # OAuth Flows Reference for Connected Apps
   2 
   3 Detailed OAuth flow patterns, configuration examples, and implementation guidance for the sf-connected-apps skill.
   4 
   5 > **Related**: For flow diagrams and curl examples, see [references/oauth-flows.md](../references/oauth-flows.md)
   6 
   7 ---
   8 
   9 ## Flow Selection Decision Tree
  10 
  11 ```
  12 START
  13 │
  14 ├─ Do you have a backend server?
  15 │  ├─ YES: Can it securely store secrets?
  16 │  │  ├─ YES: Authorization Code Flow (Web Server)
  17 │  │  └─ NO: Authorization Code + PKCE (SPA/Mobile)
  18 │  │
  19 │  └─ NO: Is this server-to-server?
  20 │     ├─ YES: JWT Bearer Flow
  21 │     └─ NO: Device Authorization Flow (CLI/IoT)
  22 │
  23 └─ Is this for a specific integration user?
  24    ├─ YES: JWT Bearer Flow
  25    └─ NO: Authorization Code Flow
  26 ```
  27 
  28 ---
  29 
  30 ## Authorization Code Flow (Web Server)
  31 
  32 ### When to Use
  33 - Web applications with backend server
  34 - Can securely store consumer secret
  35 - User-interactive flow needed
  36 - Examples: Portal, Integration Hub, Admin Console
  37 
  38 ### Connected App Configuration
  39 
  40 **Minimal scopes for API access**:
  41 ```xml
  42 <oauthConfig>
  43     <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
  44     <scopes>Api</scopes>
  45     <scopes>RefreshToken</scopes>
  46     <isConsumerSecretOptional>false</isConsumerSecretOptional>
  47 </oauthConfig>
  48 ```
  49 
  50 **With OpenID Connect**:
  51 ```xml
  52 <oauthConfig>
  53     <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
  54     <scopes>Api</scopes>
  55     <scopes>RefreshToken</scopes>
  56     <scopes>OpenID</scopes>
  57     <isIdTokenEnabled>true</isIdTokenEnabled>
  58     <isConsumerSecretOptional>false</isConsumerSecretOptional>
  59 </oauthConfig>
  60 ```
  61 
  62 ### Security Checklist
  63 - [ ] HTTPS callback URL (no localhost in production)
  64 - [ ] Consumer secret stored in environment variables (never in code)
  65 - [ ] State parameter validated (CSRF protection)
  66 - [ ] Authorization code used only once
  67 - [ ] Refresh token rotation enabled
  68 - [ ] IP restrictions configured (optional)
  69 
  70 ### Common Issues
  71 
  72 **Problem**: "redirect_uri_mismatch" error
  73 - **Cause**: Callback URL doesn't match exactly
  74 - **Fix**: Ensure exact match including protocol, domain, path, and query parameters
  75 
  76 **Problem**: "invalid_client_id" error
  77 - **Cause**: Consumer key incorrect or app not deployed
  78 - **Fix**: Verify consumer key from Setup > App Manager
  79 
  80 ---
  81 
  82 ## Authorization Code + PKCE (Public Clients)
  83 
  84 ### When to Use
  85 - Single Page Applications (React, Vue, Angular)
  86 - Mobile apps (iOS, Android)
  87 - Desktop apps
  88 - Any client that cannot securely store secrets
  89 
  90 ### Connected App Configuration
  91 
  92 ```xml
  93 <oauthConfig>
  94     <callbackUrl>myapp://oauth/callback</callbackUrl>
  95     <scopes>Api</scopes>
  96     <scopes>RefreshToken</scopes>
  97     <isConsumerSecretOptional>true</isConsumerSecretOptional>
  98     <isPkceRequired>true</isPkceRequired>
  99 </oauthConfig>
 100 
 101 <oauthPolicy>
 102     <refreshTokenPolicy>infinite</refreshTokenPolicy>
 103     <isRefreshTokenRotationEnabled>true</isRefreshTokenRotationEnabled>
 104 </oauthPolicy>
 105 ```
 106 
 107 ### External Client App Configuration
 108 
 109 ```xml
 110 <!-- ecaGlblOauth-meta.xml -->
 111 <ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
 112     <callbackUrl>myapp://oauth/callback</callbackUrl>
 113     <externalClientApplication>MyMobileApp</externalClientApplication>
 114     <isConsumerSecretOptional>true</isConsumerSecretOptional>
 115     <isPkceRequired>true</isPkceRequired>
 116     <isSecretRequiredForRefreshToken>false</isSecretRequiredForRefreshToken>
 117     <label>Mobile App OAuth Settings</label>
 118 </ExtlClntAppGlobalOauthSettings>
 119 ```
 120 
 121 ### Implementation Pattern (JavaScript)
 122 
 123 ```javascript
 124 // Generate PKCE verifier and challenge
 125 function generatePKCE() {
 126   const array = new Uint8Array(32);
 127   crypto.getRandomValues(array);
 128   const codeVerifier = base64URLEncode(array);
 129 
 130   return crypto.subtle.digest('SHA-256', new TextEncoder().encode(codeVerifier))
 131     .then(buffer => ({
 132       codeVerifier,
 133       codeChallenge: base64URLEncode(new Uint8Array(buffer))
 134     }));
 135 }
 136 
 137 // Store verifier in sessionStorage (cleared on close)
 138 const { codeVerifier, codeChallenge } = await generatePKCE();
 139 sessionStorage.setItem('pkce_verifier', codeVerifier);
 140 
 141 // Authorization URL
 142 const authUrl = `https://login.salesforce.com/services/oauth2/authorize?` +
 143   `response_type=code` +
 144   `&client_id=${CLIENT_ID}` +
 145   `&redirect_uri=${REDIRECT_URI}` +
 146   `&scope=api%20refresh_token` +
 147   `&state=${STATE}` +
 148   `&code_challenge=${codeChallenge}` +
 149   `&code_challenge_method=S256`;
 150 ```
 151 
 152 ### Security Checklist
 153 - [ ] PKCE required in Connected App config
 154 - [ ] Consumer secret optional
 155 - [ ] Refresh token rotation enabled
 156 - [ ] Code verifier stored securely (sessionStorage, keychain)
 157 - [ ] State parameter validated
 158 - [ ] Deep link callback handled securely (mobile)
 159 
 160 ---
 161 
 162 ## JWT Bearer Flow (Server-to-Server)
 163 
 164 ### When to Use
 165 - CI/CD pipelines (GitHub Actions, Jenkins)
 166 - Backend integrations without user interaction
 167 - Service accounts
 168 - Scheduled jobs
 169 
 170 ### Prerequisites
 171 
 172 **1. Generate X.509 Certificate**:
 173 ```bash
 174 # Generate private key
 175 openssl genrsa -out server.key 2048
 176 
 177 # Generate certificate signing request
 178 openssl req -new -key server.key -out server.csr
 179 
 180 # Self-sign certificate (valid 1 year)
 181 openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
 182 ```
 183 
 184 **2. Upload to Salesforce**:
 185 - Setup > Certificate and Key Management > Create Self-Signed Certificate
 186 - Or use the certificate from step 1
 187 
 188 ### Connected App Configuration
 189 
 190 ```xml
 191 <oauthConfig>
 192     <certificate>JWTAuthCertificate</certificate>
 193     <consumerKey>AUTO_GENERATED</consumerKey>
 194     <scopes>Api</scopes>
 195     <scopes>Web</scopes>
 196     <isAdminApproved>true</isAdminApproved>
 197 </oauthConfig>
 198 
 199 <oauthPolicy>
 200     <ipRelaxation>ENFORCE</ipRelaxation>
 201 </oauthPolicy>
 202 ```
 203 
 204 **Important**: No `callbackUrl` needed for JWT Bearer flow.
 205 
 206 ### Pre-Authorization
 207 
 208 **Option 1: Permission Set**
 209 ```xml
 210 <!-- permissionsets/IntegrationUser.permissionset-meta.xml -->
 211 <PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
 212     <label>API Integration User</label>
 213     <connectedAppSettings>
 214         <connectedApp>MyJWTApp</connectedApp>
 215         <enabled>true</enabled>
 216     </connectedAppSettings>
 217     <hasActivationRequired>false</hasActivationRequired>
 218 </PermissionSet>
 219 ```
 220 
 221 Assign to integration user: Setup > Users > [User] > Permission Set Assignments
 222 
 223 **Option 2: Profile**
 224 Setup > Manage Connected Apps > [App] > Edit Policies > Permitted Users = "Admin approved users are pre-authorized"
 225 
 226 ### Implementation Pattern (Node.js)
 227 
 228 ```javascript
 229 const jwt = require('jsonwebtoken');
 230 const axios = require('axios');
 231 const fs = require('fs');
 232 
 233 async function getAccessToken() {
 234   const privateKey = fs.readFileSync('server.key', 'utf8');
 235 
 236   const claims = {
 237     iss: process.env.CONSUMER_KEY,
 238     sub: 'integration@company.com', // Pre-authorized user
 239     aud: 'https://login.salesforce.com',
 240     exp: Math.floor(Date.now() / 1000) + 300 // 5 min
 241   };
 242 
 243   const assertion = jwt.sign(claims, privateKey, { algorithm: 'RS256' });
 244 
 245   const response = await axios.post('https://login.salesforce.com/services/oauth2/token',
 246     new URLSearchParams({
 247       grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
 248       assertion: assertion
 249     })
 250   );
 251 
 252   return response.data.access_token;
 253 }
 254 ```
 255 
 256 ### Security Checklist
 257 - [ ] Private key stored securely (secrets manager, not in repo)
 258 - [ ] Certificate uploaded to Salesforce
 259 - [ ] User pre-authorized via Permission Set
 260 - [ ] IP restrictions configured
 261 - [ ] Token expiration set (exp claim)
 262 - [ ] Audience (aud) set correctly (login vs test.salesforce.com)
 263 
 264 ### Common Issues
 265 
 266 **Problem**: "user hasn't approved this consumer" error
 267 - **Cause**: User not pre-authorized
 268 - **Fix**: Assign Permission Set or configure admin pre-approval
 269 
 270 **Problem**: "invalid_grant" error
 271 - **Cause**: Certificate mismatch or expired token
 272 - **Fix**: Verify certificate name matches `<certificate>` tag, check exp claim
 273 
 274 ---
 275 
 276 ## Device Authorization Flow
 277 
 278 ### When to Use
 279 - CLI tools (sf CLI, custom CLIs)
 280 - Smart TVs, Set-top boxes
 281 - IoT devices without keyboard
 282 - Any device with limited input capability
 283 
 284 ### Connected App Configuration
 285 
 286 ```xml
 287 <oauthConfig>
 288     <callbackUrl>http://localhost:8080</callbackUrl>
 289     <scopes>Api</scopes>
 290     <scopes>RefreshToken</scopes>
 291     <isConsumerSecretOptional>true</isConsumerSecretOptional>
 292 </oauthConfig>
 293 ```
 294 
 295 ### Implementation Pattern (Python)
 296 
 297 ```python
 298 import requests
 299 import time
 300 
 301 CLIENT_ID = 'your_consumer_key'
 302 DEVICE_CODE_URL = 'https://login.salesforce.com/services/oauth2/device/code'
 303 TOKEN_URL = 'https://login.salesforce.com/services/oauth2/token'
 304 
 305 # Step 1: Request device code
 306 response = requests.post(DEVICE_CODE_URL, data={
 307     'client_id': CLIENT_ID,
 308     'scope': 'api refresh_token'
 309 })
 310 data = response.json()
 311 
 312 # Step 2: Display user code
 313 print(f"Visit: {data['verification_uri']}")
 314 print(f"Enter code: {data['user_code']}")
 315 
 316 # Step 3: Poll for token
 317 device_code = data['device_code']
 318 interval = data['interval']  # Polling interval in seconds
 319 
 320 while True:
 321     time.sleep(interval)
 322 
 323     token_response = requests.post(TOKEN_URL, data={
 324         'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
 325         'client_id': CLIENT_ID,
 326         'code': device_code
 327     })
 328 
 329     if token_response.status_code == 200:
 330         tokens = token_response.json()
 331         print(f"Access Token: {tokens['access_token']}")
 332         break
 333     elif token_response.json().get('error') == 'authorization_pending':
 334         continue  # User hasn't authorized yet
 335     else:
 336         print(f"Error: {token_response.json()}")
 337         break
 338 ```
 339 
 340 ### Security Checklist
 341 - [ ] Consumer secret optional
 342 - [ ] Polling interval respected (don't spam)
 343 - [ ] Device code expires after timeout
 344 - [ ] Refresh token stored securely
 345 
 346 ---
 347 
 348 ## Client Credentials Flow (ECA Only)
 349 
 350 ### When to Use
 351 - Service accounts (not tied to specific user)
 352 - Background processes
 353 - Microservices
 354 - Requires External Client App (not available in Connected Apps)
 355 
 356 ### External Client App Configuration
 357 
 358 ```xml
 359 <!-- ecaOauth-meta.xml -->
 360 <ExtlClntAppOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
 361     <commaSeparatedOauthScopes>api,refresh_token</commaSeparatedOauthScopes>
 362     <externalClientApplication>MyServiceApp</externalClientApplication>
 363     <isClientCredentialsEnabled>true</isClientCredentialsEnabled>
 364     <label>Service OAuth Settings</label>
 365     <executionUser>service@company.com</executionUser>
 366 </ExtlClntAppOauthSettings>
 367 ```
 368 
 369 ### Implementation Pattern
 370 
 371 ```bash
 372 curl -X POST https://login.salesforce.com/services/oauth2/token \
 373   -d "grant_type=client_credentials" \
 374   -d "client_id=<CONSUMER_KEY>" \
 375   -d "client_secret=<CONSUMER_SECRET>"
 376 ```
 377 
 378 ### Security Checklist
 379 - [ ] Execution user configured
 380 - [ ] Consumer secret rotated regularly
 381 - [ ] Scopes minimal (least privilege)
 382 - [ ] IP restrictions enabled
 383 
 384 ---
 385 
 386 ## Refresh Token Patterns
 387 
 388 ### Standard Refresh
 389 
 390 ```javascript
 391 async function refreshAccessToken(refreshToken) {
 392   const response = await axios.post('https://login.salesforce.com/services/oauth2/token',
 393     new URLSearchParams({
 394       grant_type: 'refresh_token',
 395       client_id: CLIENT_ID,
 396       client_secret: CLIENT_SECRET,
 397       refresh_token: refreshToken
 398     })
 399   );
 400 
 401   return response.data;
 402 }
 403 ```
 404 
 405 ### With Token Rotation (Recommended)
 406 
 407 When `isRefreshTokenRotationEnabled=true`, each refresh returns a NEW refresh token:
 408 
 409 ```javascript
 410 async function refreshWithRotation(refreshToken) {
 411   const response = await refreshAccessToken(refreshToken);
 412 
 413   // Store NEW refresh token (old one is now invalid)
 414   await secureStorage.set('refresh_token', response.refresh_token);
 415   await secureStorage.set('access_token', response.access_token);
 416 
 417   return response;
 418 }
 419 ```
 420 
 421 ### Refresh Token Policies
 422 
 423 | Policy | Description | Use Case |
 424 |--------|-------------|----------|
 425 | `infinite` | Never expires | Trusted integrations |
 426 | `immediately` | Expires on use | Maximum security |
 427 | `zero` | Not issued | Access token only |
 428 
 429 **Configuration**:
 430 ```xml
 431 <oauthPolicy>
 432     <refreshTokenPolicy>infinite</refreshTokenPolicy>
 433     <isRefreshTokenRotationEnabled>true</isRefreshTokenRotationEnabled>
 434 </oauthPolicy>
 435 ```
 436 
 437 ---
 438 
 439 ## Named Credentials Integration
 440 
 441 ### Why Use Named Credentials
 442 - Secrets managed by Salesforce (not in code)
 443 - Automatic token refresh
 444 - Per-user or per-org authentication
 445 - Audit trail in Setup Audit Trail
 446 
 447 ### Create Named Credential for JWT Flow
 448 
 449 ```xml
 450 <!-- namedCredentials/SalesforceAPI.namedCredential-meta.xml -->
 451 <NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
 452     <label>Salesforce API</label>
 453     <endpoint>https://yourinstance.salesforce.com</endpoint>
 454     <protocol>NoAuthentication</protocol>
 455     <principalType>NamedUser</principalType>
 456     <oauthConfig>
 457         <certificate>JWTAuthCertificate</certificate>
 458         <consumerKey>YOUR_CONSUMER_KEY</consumerKey>
 459         <oauthFlows>JwtBearer</oauthFlows>
 460         <username>integration@company.com</username>
 461     </oauthConfig>
 462 </NamedCredential>
 463 ```
 464 
 465 ### Use in Apex
 466 
 467 ```apex
 468 HttpRequest req = new HttpRequest();
 469 req.setEndpoint('callout:SalesforceAPI/services/data/v62.0/query?q=SELECT+Id+FROM+Account');
 470 req.setMethod('GET');
 471 
 472 Http http = new Http();
 473 HttpResponse res = http.send(req);
 474 ```
 475 
 476 ---
 477 
 478 ## Error Handling Patterns
 479 
 480 ### OAuth Error Response Structure
 481 
 482 ```json
 483 {
 484   "error": "invalid_grant",
 485   "error_description": "authentication failure"
 486 }
 487 ```
 488 
 489 ### Common Errors
 490 
 491 | Error Code | Meaning | Resolution |
 492 |------------|---------|------------|
 493 | `invalid_client_id` | Consumer key invalid | Verify key from Setup |
 494 | `invalid_client` | Secret incorrect | Check consumer secret |
 495 | `redirect_uri_mismatch` | Callback URL mismatch | Match exactly with config |
 496 | `invalid_grant` | Auth code expired/used | Request new authorization |
 497 | `unsupported_grant_type` | Flow not enabled | Enable in Connected App |
 498 | `invalid_scope` | Scope not allowed | Check available scopes |
 499 | `access_denied` | User declined | User must approve |
 500 
 501 ### Retry Logic Example
 502 
 503 ```javascript
 504 async function callSalesforceAPI(accessToken, retries = 1) {
 505   try {
 506     return await axios.get('https://instance.salesforce.com/services/data/v62.0/query', {
 507       headers: { 'Authorization': `Bearer ${accessToken}` }
 508     });
 509   } catch (error) {
 510     if (error.response?.status === 401 && retries > 0) {
 511       // Token expired, refresh and retry
 512       const newToken = await refreshAccessToken();
 513       return callSalesforceAPI(newToken, retries - 1);
 514     }
 515     throw error;
 516   }
 517 }
 518 ```
 519 
 520 ---
 521 
 522 ## Scoring Impact by Flow
 523 
 524 | Flow | Security Score Impact | Best Practices Score |
 525 |------|----------------------|---------------------|
 526 | Authorization Code + PKCE | +10 (PKCE enabled) | +10 (modern flow) |
 527 | JWT Bearer | +5 (certificate) | +15 (server-to-server best practice) |
 528 | Device Authorization | +5 (secret optional) | +10 (appropriate for CLI) |
 529 | Username-Password | -10 (deprecated) | -10 (anti-pattern) |
 530 
 531 **Recommendation**: JWT Bearer or Authorization Code + PKCE score highest (90-100/120).
 532 
 533 ---
 534 
 535 ## Testing OAuth Flows
 536 
 537 ### Postman Collection Variables
 538 
 539 ```json
 540 {
 541   "login_url": "https://login.salesforce.com",
 542   "client_id": "{{CONSUMER_KEY}}",
 543   "client_secret": "{{CONSUMER_SECRET}}",
 544   "redirect_uri": "https://oauth.pstmn.io/v1/callback",
 545   "username": "test@company.com",
 546   "password": "password123"
 547 }
 548 ```
 549 
 550 ### Quick Test: JWT Bearer
 551 
 552 ```bash
 553 # Generate JWT (requires jq)
 554 JWT=$(python3 -c "
 555 import jwt, time, os
 556 claims = {
 557     'iss': os.getenv('CONSUMER_KEY'),
 558     'sub': 'integration@company.com',
 559     'aud': 'https://login.salesforce.com',
 560     'exp': int(time.time()) + 300
 561 }
 562 with open('server.key') as f:
 563     print(jwt.encode(claims, f.read(), algorithm='RS256'))
 564 ")
 565 
 566 # Get token
 567 curl -X POST https://login.salesforce.com/services/oauth2/token \
 568   -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
 569   -d "assertion=$JWT" | jq
 570 ```
 571 
 572 ---
 573 
 574 ## Migration Strategies
 575 
 576 ### Connected App → External Client App
 577 
 578 **Step 1**: Create equivalent ECA
 579 ```bash
 580 # Read existing Connected App
 581 Grep: pattern="<oauthConfig>" path="force-app/main/default/connectedApps/"
 582 
 583 # Create new ECA with same scopes
 584 # Use templates: external-client-app.xml, eca-global-oauth.xml
 585 ```
 586 
 587 **Step 2**: Parallel operation
 588 - Deploy ECA alongside Connected App
 589 - Update one integration at a time
 590 - Monitor both apps
 591 
 592 **Step 3**: Cutover
 593 - Update all integrations to use new Consumer Key
 594 - Disable old Connected App
 595 - Archive after 30 days
 596 
 597 **Scoring benefit**: ECA typically scores 15-20 points higher due to modern security model.
 598 
 599 ---
 600 
 601 ## Quick Reference
 602 
 603 ### Template Selection by Flow
 604 
 605 | Flow | Template File |
 606 |------|---------------|
 607 | Authorization Code (basic) | `connected-app-oauth.xml` |
 608 | JWT Bearer | `connected-app-jwt.xml` |
 609 | Mobile/SPA (PKCE) | `external-client-app.xml` + `eca-global-oauth.xml` |
 610 | Device Authorization | `connected-app-basic.xml` (secret optional) |
 611 | Client Credentials | `eca-oauth-settings.xml` (ECA only) |
 612 
 613 ### Salesforce OAuth Endpoints
 614 
 615 | Environment | Base URL |
 616 |-------------|----------|
 617 | Production | `https://login.salesforce.com` |
 618 | Sandbox | `https://test.salesforce.com` |
 619 | Custom Domain | `https://yourdomain.my.salesforce.com` |
 620 
 621 ### Key Endpoints
 622 - Authorize: `/services/oauth2/authorize`
 623 - Token: `/services/oauth2/token`
 624 - Revoke: `/services/oauth2/revoke`
 625 - Introspect: `/services/oauth2/introspect`
 626 - Device Code: `/services/oauth2/device/code`
 627 - UserInfo (OpenID): `/services/oauth2/userinfo`
 628 
 629 ---
 630 
 631 ## Related Resources
 632 
 633 - **Flow Diagrams**: [references/oauth-flows.md](../references/oauth-flows.md)
 634 - **Security Checklist**: [references/security-checklist.md](../references/security-checklist.md)
 635 - **Migration Guide**: [references/migration-guide.md](../references/migration-guide.md)
 636 - **Main Skill**: [SKILL.md](../SKILL.md)
