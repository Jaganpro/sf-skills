<!-- Parent: sf-connected-apps/SKILL.md -->
   1 # sf-connected-apps Examples
   2 
   3 Real-world examples of using the sf-connected-apps skill.
   4 
   5 ## Example 1: Create a Basic API Integration Connected App
   6 
   7 **Request**:
   8 ```
   9 Use the sf-connected-apps skill to create a Connected App named "DataSyncIntegration"
  10 for syncing data with our external ERP system. It needs API access and refresh tokens.
  11 Contact email: admin@company.com
  12 ```
  13 
  14 **Generated Output**:
  15 - `force-app/main/default/connectedApps/DataSyncIntegration.connectedApp-meta.xml`
  16 
  17 ```xml
  18 <?xml version="1.0" encoding="UTF-8"?>
  19 <ConnectedApp xmlns="http://soap.sforce.com/2006/04/metadata">
  20     <label>DataSyncIntegration</label>
  21     <contactEmail>admin@company.com</contactEmail>
  22     <description>Data synchronization with external ERP system</description>
  23     <oauthConfig>
  24         <callbackUrl>https://erp.company.com/oauth/callback</callbackUrl>
  25         <isAdminApproved>true</isAdminApproved>
  26         <isConsumerSecretOptional>false</isConsumerSecretOptional>
  27         <scopes>Api</scopes>
  28         <scopes>RefreshToken</scopes>
  29     </oauthConfig>
  30     <oauthPolicy>
  31         <ipRelaxation>ENFORCE</ipRelaxation>
  32         <refreshTokenPolicy>infinite</refreshTokenPolicy>
  33     </oauthPolicy>
  34 </ConnectedApp>
  35 ```
  36 
  37 **Score**: 95/120 ⭐⭐⭐⭐
  38 
  39 ---
  40 
  41 ## Example 2: Create a JWT Bearer App for CI/CD
  42 
  43 **Request**:
  44 ```
  45 Create a Connected App for our CI/CD pipeline using JWT Bearer flow.
  46 Name it "GitHubActionsDeployment" and use certificate "GH_Actions_Cert".
  47 ```
  48 
  49 **Generated Output**:
  50 - `force-app/main/default/connectedApps/GitHubActionsDeployment.connectedApp-meta.xml`
  51 
  52 ```xml
  53 <?xml version="1.0" encoding="UTF-8"?>
  54 <ConnectedApp xmlns="http://soap.sforce.com/2006/04/metadata">
  55     <label>GitHubActionsDeployment</label>
  56     <contactEmail>devops@company.com</contactEmail>
  57     <description>CI/CD deployment via GitHub Actions - JWT Bearer flow</description>
  58     <oauthConfig>
  59         <callbackUrl>https://localhost/oauth/callback</callbackUrl>
  60         <certificate>GH_Actions_Cert</certificate>
  61         <isAdminApproved>true</isAdminApproved>
  62         <isConsumerSecretOptional>true</isConsumerSecretOptional>
  63         <scopes>Api</scopes>
  64     </oauthConfig>
  65     <oauthPolicy>
  66         <ipRelaxation>ENFORCE</ipRelaxation>
  67         <refreshTokenPolicy>zero</refreshTokenPolicy>
  68     </oauthPolicy>
  69 </ConnectedApp>
  70 ```
  71 
  72 **Score**: 108/120 ⭐⭐⭐⭐⭐
  73 
  74 ---
  75 
  76 ## Example 3: Create a Mobile App with External Client App
  77 
  78 **Request**:
  79 ```
  80 Create an External Client App for our mobile app "FieldServiceMobile".
  81 It needs PKCE enabled, refresh tokens, and should be packageable for distribution.
  82 ```
  83 
  84 **Generated Files**:
  85 
  86 ### 1. Header File: `FieldServiceMobile.eca-meta.xml`
  87 ```xml
  88 <?xml version="1.0" encoding="UTF-8"?>
  89 <ExternalClientApplication xmlns="http://soap.sforce.com/2006/04/metadata">
  90     <contactEmail>mobile-team@company.com</contactEmail>
  91     <description>Field Service mobile application for technicians</description>
  92     <distributionState>Packageable</distributionState>
  93     <isProtected>false</isProtected>
  94     <label>FieldServiceMobile</label>
  95 </ExternalClientApplication>
  96 ```
  97 
  98 ### 2. Global OAuth: `FieldServiceMobile.ecaGlobalOauth-meta.xml`
  99 ```xml
 100 <?xml version="1.0" encoding="UTF-8"?>
 101 <ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
 102     <callbackUrl>fieldservicemobile://oauth/callback</callbackUrl>
 103     <isConsumerSecretOptional>true</isConsumerSecretOptional>
 104     <isPkceRequired>true</isPkceRequired>
 105     <shouldRotateConsumerKey>true</shouldRotateConsumerKey>
 106     <shouldRotateConsumerSecret>true</shouldRotateConsumerSecret>
 107 </ExtlClntAppGlobalOauthSettings>
 108 ```
 109 
 110 ### 3. OAuth Settings: `FieldServiceMobile.ecaOauth-meta.xml`
 111 ```xml
 112 <?xml version="1.0" encoding="UTF-8"?>
 113 <ExtlClntAppOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
 114     <isAdminApproved>true</isAdminApproved>
 115     <isCodeCredentialsEnabled>true</isCodeCredentialsEnabled>
 116     <isClientCredentialsEnabled>false</isClientCredentialsEnabled>
 117     <isRefreshTokenEnabled>true</isRefreshTokenEnabled>
 118     <isIntrospectAllTokens>false</isIntrospectAllTokens>
 119     <scopes>Api</scopes>
 120     <scopes>RefreshToken</scopes>
 121     <scopes>OpenID</scopes>
 122 </ExtlClntAppOauthSettings>
 123 ```
 124 
 125 **Score**: 115/120 ⭐⭐⭐⭐⭐
 126 
 127 ---
 128 
 129 ## Example 4: Review Existing Connected Apps
 130 
 131 **Request**:
 132 ```
 133 Review and score my existing Connected Apps for security best practices.
 134 ```
 135 
 136 **Process**:
 137 1. Scan: `Glob: **/*.connectedApp-meta.xml`
 138 2. Read each file
 139 3. Validate against scoring criteria
 140 4. Generate report
 141 
 142 **Sample Report**:
 143 ```
 144 📊 CONNECTED APP SECURITY REVIEW
 145 ════════════════════════════════════════════════════════════════
 146 
 147 🔍 Apps Scanned: 3
 148 📅 Review Date: 2025-01-15
 149 
 150 ┌────────────────────────────┬────────┬────────┬──────────────────┐
 151 │ App Name                   │ Score  │ Rating │ Critical Issues  │
 152 ├────────────────────────────┼────────┼────────┼──────────────────┤
 153 │ LegacyERPConnector         │ 45/120 │ ⭐     │ 3                │
 154 │ MobileAppV2                │ 82/120 │ ⭐⭐⭐  │ 0                │
 155 │ DataSyncIntegration        │ 95/120 │ ⭐⭐⭐⭐│ 0                │
 156 └────────────────────────────┴────────┴────────┴──────────────────┘
 157 
 158 🚨 CRITICAL ISSUES
 159 
 160 LegacyERPConnector:
 161   ❌ Wildcard callback URL detected (https://*)
 162   ❌ Full scope granted (overly permissive)
 163   ❌ No IP restrictions configured
 164   ⚠️ Recommend: Migrate to External Client App
 165 
 166 ✅ RECOMMENDATIONS
 167 
 168 1. LegacyERPConnector: URGENT - Fix security issues or migrate to ECA
 169 2. MobileAppV2: Enable PKCE for mobile security
 170 3. DataSyncIntegration: Consider enabling token rotation
 171 ```
 172 
 173 ---
 174 
 175 ## Example 5: Migrate Connected App to External Client App
 176 
 177 **Request**:
 178 ```
 179 Migrate our "SalesPortal" Connected App to an External Client App for better security.
 180 ```
 181 
 182 **Process**:
 183 1. Read existing Connected App configuration
 184 2. Map OAuth settings to ECA structure
 185 3. Generate all required ECA files
 186 4. Provide migration checklist
 187 
 188 **Output**:
 189 ```
 190 📦 MIGRATION PLAN: SalesPortal → External Client App
 191 ════════════════════════════════════════════════════════════════
 192 
 193 📋 Source Configuration
 194    Type: Connected App
 195    OAuth Flow: Authorization Code
 196    Scopes: Api, RefreshToken, OpenID
 197    IP Policy: ENFORCE
 198 
 199 📄 Files to Generate:
 200    1. SalesPortalECA.eca-meta.xml
 201    2. SalesPortalECA.ecaGlobalOauth-meta.xml
 202    3. SalesPortalECA.ecaOauth-meta.xml
 203 
 204 🔄 Migration Steps:
 205    1. ✓ Generate ECA metadata files
 206    2. □ Deploy ECA to DevHub
 207    3. □ Generate new Consumer Key/Secret
 208    4. □ Update external application with new credentials
 209    5. □ Test OAuth flow
 210    6. □ Configure policies in subscriber orgs
 211    7. □ Deactivate old Connected App
 212    8. □ Monitor for 30 days before deletion
 213 
 214 ⚠️ Breaking Change: New Consumer Key/Secret required
 215 ```
 216 
 217 ---
 218 
 219 ## Deployment Commands
 220 
 221 ### Deploy Connected App
 222 ```bash
 223 sf project deploy start \
 224   --source-dir force-app/main/default/connectedApps \
 225   --target-org my-org
 226 ```
 227 
 228 ### Deploy External Client App
 229 ```bash
 230 sf project deploy start \
 231   --source-dir force-app/main/default/externalClientApps \
 232   --target-org my-devhub
 233 ```
 234 
 235 ### Retrieve Existing Apps
 236 ```bash
 237 # Connected Apps
 238 sf project retrieve start \
 239   --metadata ConnectedApp:MyAppName \
 240   --target-org my-org
 241 
 242 # External Client Apps
 243 sf project retrieve start \
 244   --metadata ExternalClientApplication:MyECAName \
 245   --target-org my-org
 246 ```
