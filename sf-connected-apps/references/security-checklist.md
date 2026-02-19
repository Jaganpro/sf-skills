<!-- Parent: sf-connected-apps/SKILL.md -->
   1 # Security Checklist for Connected Apps & ECAs
   2 
   3 Use this checklist before deploying any OAuth application to production.
   4 
   5 ## Pre-Deployment Checklist
   6 
   7 ### OAuth Configuration
   8 
   9 - [ ] **Callback URLs are specific** (no wildcards)
  10 - [ ] **All URLs use HTTPS** (required for production)
  11 - [ ] **PKCE is enabled** for public clients (mobile, SPA)
  12 - [ ] **Consumer secret is protected** (not in source control)
  13 - [ ] **Minimal scopes selected** (principle of least privilege)
  14 - [ ] **No deprecated scopes** in use
  15 
  16 ### Token Policies
  17 
  18 - [ ] **Access token expiration** is configured appropriately
  19 - [ ] **Refresh token policy** matches use case
  20   - `infinite` only for trusted server applications
  21   - `specific_lifetime` for user-facing apps
  22   - `zero` for JWT Bearer flows
  23 - [ ] **Token rotation enabled** for ECAs in production
  24 - [ ] **IP restrictions configured** for server-to-server apps
  25 
  26 ### Access Control
  27 
  28 - [ ] **Admin pre-authorization** required for sensitive apps
  29 - [ ] **User assignment via Permission Set** or Profile
  30 - [ ] **Connected App policies** reviewed in Setup
  31 - [ ] **High Assurance session** required if needed
  32 
  33 ### External Client Apps (Additional)
  34 
  35 - [ ] **Distribution state** correctly set (Local vs Packageable)
  36 - [ ] **Consumer key rotation** enabled for production
  37 - [ ] **Consumer secret rotation** enabled for production
  38 - [ ] **Policies file** reviewed after first deployment
  39 
  40 ---
  41 
  42 ## Security Scoring Criteria
  43 
  44 ### Critical (Block Deployment)
  45 
  46 | Issue | Impact | Fix |
  47 |-------|--------|-----|
  48 | Wildcard callback URL | Token hijacking | Use specific URLs |
  49 | HTTP callback URL | Credential interception | Use HTTPS only |
  50 | Full scope without justification | Over-privileged access | Use minimal scopes |
  51 | Consumer secret in code | Credential leak | Use environment variables |
  52 
  53 ### High Priority
  54 
  55 | Issue | Impact | Fix |
  56 |-------|--------|-----|
  57 | PKCE disabled for mobile/SPA | Auth code interception | Enable PKCE |
  58 | No IP restrictions (server) | Unauthorized access | Configure IP ranges |
  59 | Infinite refresh tokens (user app) | Long-term compromise | Set expiration |
  60 | No token rotation (ECA) | Compromised credentials | Enable rotation |
  61 
  62 ### Medium Priority
  63 
  64 | Issue | Impact | Fix |
  65 |-------|--------|-----|
  66 | Missing description | Audit difficulty | Add clear description |
  67 | Generic contact email | Incident response delay | Use team email |
  68 | Introspection disabled | Token validation gaps | Enable if needed |
  69 | No logout URL | Session persistence | Configure logout |
  70 
  71 ---
  72 
  73 ## Scope Security Guide
  74 
  75 ### Recommended Scopes by Use Case
  76 
  77 | Use Case | Recommended Scopes |
  78 |----------|-------------------|
  79 | API Integration | `Api`, `RefreshToken` |
  80 | User Authentication | `OpenID`, `Profile`, `Email` |
  81 | Full API + Identity | `Api`, `RefreshToken`, `OpenID`, `Profile` |
  82 | Chatter Integration | `Api`, `ChatterApi` |
  83 | Server-to-Server | `Api` only |
  84 
  85 ### Scopes to Avoid
  86 
  87 | Scope | Risk | Alternative |
  88 |-------|------|-------------|
  89 | `Full` | Complete access to everything | Use specific scopes |
  90 | `Web` + `Api` together | Redundant, increases attack surface | Choose one |
  91 | `RefreshToken` for JWT | Unnecessary, JWT generates new tokens | Remove scope |
  92 
  93 ---
  94 
  95 ## IP Restriction Policies
  96 
  97 ### Policy Options
  98 
  99 | Policy | Description | Use Case |
 100 |--------|-------------|----------|
 101 | `ENFORCE` | Strict IP enforcement | Production server-to-server |
 102 | `BYPASS` | No IP restrictions | Development only |
 103 | `ENFORCE_ACTIVATED_USERS` | Enforce for active users | Mixed environments |
 104 
 105 ### Recommended Configuration
 106 
 107 ```xml
 108 <!-- Production: Server-to-Server -->
 109 <oauthPolicy>
 110     <ipRelaxation>ENFORCE</ipRelaxation>
 111 </oauthPolicy>
 112 
 113 <!-- Production: User-Facing -->
 114 <oauthPolicy>
 115     <ipRelaxation>ENFORCE_ACTIVATED_USERS</ipRelaxation>
 116 </oauthPolicy>
 117 
 118 <!-- Development Only -->
 119 <oauthPolicy>
 120     <ipRelaxation>BYPASS</ipRelaxation>
 121 </oauthPolicy>
 122 ```
 123 
 124 ---
 125 
 126 ## Certificate Management (JWT Bearer)
 127 
 128 ### Certificate Requirements
 129 
 130 - [ ] RSA 2048-bit or higher key size
 131 - [ ] Valid not-before and not-after dates
 132 - [ ] Uploaded to Salesforce Certificate and Key Management
 133 - [ ] Private key stored securely (HSM, Vault, secure storage)
 134 
 135 ### Certificate Rotation
 136 
 137 1. Generate new certificate before expiration
 138 2. Upload new certificate to Salesforce
 139 3. Update Connected App to use new certificate
 140 4. Update external system with new private key
 141 5. Test authentication
 142 6. Remove old certificate after transition period
 143 
 144 ---
 145 
 146 ## Monitoring & Audit
 147 
 148 ### What to Monitor
 149 
 150 - [ ] **Login History** for Connected App users
 151 - [ ] **OAuth Usage** in Setup
 152 - [ ] **Event Monitoring** for token events (Shield required)
 153 - [ ] **API Usage** limits and patterns
 154 
 155 ### Audit Checklist
 156 
 157 - [ ] Review Connected Apps quarterly
 158 - [ ] Remove unused applications
 159 - [ ] Rotate credentials annually
 160 - [ ] Verify scope appropriateness
 161 - [ ] Check for policy violations
 162 
 163 ---
 164 
 165 ## Incident Response
 166 
 167 ### If Credentials Are Compromised
 168 
 169 1. **Immediately** rotate Consumer Secret
 170 2. Revoke all active tokens
 171 3. Review login and access logs
 172 4. Update external systems with new credentials
 173 5. Investigate scope of compromise
 174 6. Document and report incident
 175 
 176 ### Commands for Response
 177 
 178 ```bash
 179 # List all Connected Apps
 180 sf org list metadata --metadata-type ConnectedApp --target-org <org>
 181 
 182 # Retrieve for review
 183 sf project retrieve start --metadata ConnectedApp:<AppName> --target-org <org>
 184 ```
 185 
 186 ---
 187 
 188 ## Compliance Considerations
 189 
 190 ### GDPR/Privacy
 191 
 192 - Ensure data access matches user consent
 193 - Document data flows through Connected Apps
 194 - Implement data retention policies
 195 
 196 ### SOC 2
 197 
 198 - Enable audit logging
 199 - Implement access reviews
 200 - Document security controls
 201 - Use certificate-based authentication
 202 
 203 ### HIPAA
 204 
 205 - Enable High Assurance sessions
 206 - Restrict data access scopes
 207 - Implement IP restrictions
 208 - Use encrypted connections only
