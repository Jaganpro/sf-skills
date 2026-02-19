<!-- Parent: sf-integration/SKILL.md -->
   1 # Named Credentials Guide
   2 
   3 ## Overview
   4 
   5 Named Credentials provide secure storage of authentication credentials and endpoint URLs for external system integrations. They eliminate the need to hardcode credentials in Apex code.
   6 
   7 ## Architecture Evolution
   8 
   9 ### Legacy Named Credentials (Pre-API 61)
  10 
  11 - Single principal per credential
  12 - Authentication configured directly on Named Credential
  13 - Simpler setup but less flexible
  14 
  15 ### External Credentials (API 61+)
  16 
  17 - Separate External Credential and Named Credential
  18 - Named Principal and Per-User Principal support
  19 - Permission Set-based access control
  20 - More secure and flexible
  21 
  22 ```
  23 ┌─────────────────────────────────────────────────────────────────┐
  24 │  CREDENTIAL ARCHITECTURE (API 61+)                              │
  25 ├─────────────────────────────────────────────────────────────────┤
  26 │                                                                 │
  27 │  External Credential                                            │
  28 │  ├── Authentication Protocol (OAuth, JWT, Custom)               │
  29 │  ├── OAuth/JWT Parameters                                       │
  30 │  └── Principals                                                 │
  31 │      ├── Named Principal (shared service account)               │
  32 │      └── Per-User Principal (individual auth)                   │
  33 │                                                                 │
  34 │  Named Credential                                               │
  35 │  ├── Endpoint URL                                               │
  36 │  └── References External Credential                             │
  37 │                                                                 │
  38 │  Permission Set                                                 │
  39 │  └── External Credential Principal Access                       │
  40 │                                                                 │
  41 └─────────────────────────────────────────────────────────────────┘
  42 ```
  43 
  44 ## Authentication Types
  45 
  46 ### 1. OAuth 2.0 Client Credentials
  47 
  48 **Use Case**: Server-to-server integration without user context
  49 
  50 ```apex
  51 // Apex usage - Named Credential handles auth automatically
  52 HttpRequest req = new HttpRequest();
  53 req.setEndpoint('callout:MyOAuthCredential/api/resource');
  54 req.setMethod('GET');
  55 // Authorization header added automatically
  56 ```
  57 
  58 **Setup**:
  59 1. Create Auth Provider (optional, for complex OAuth)
  60 2. Create Named Credential with OAuth protocol
  61 3. Enter Client ID and Client Secret via UI
  62 
  63 ### 2. OAuth 2.0 JWT Bearer
  64 
  65 **Use Case**: Certificate-based server-to-server auth
  66 
  67 **Prerequisites**:
  68 - Certificate in Setup → Certificate and Key Management
  69 - Connected App configured for JWT Bearer
  70 - External system configured to trust certificate
  71 
  72 **Flow**:
  73 1. Salesforce creates JWT with claims (iss, sub, aud, exp)
  74 2. JWT signed with certificate private key
  75 3. JWT exchanged for access token
  76 4. Access token used for API calls
  77 
  78 ### 3. Certificate-Based (Mutual TLS)
  79 
  80 **Use Case**: High-security integrations requiring client certificate
  81 
  82 **Setup**:
  83 1. Obtain client certificate from CA or external system
  84 2. Import to Setup → Certificate and Key Management
  85 3. Configure Named Credential with certificate
  86 4. External system must trust Salesforce's certificate
  87 
  88 ### 4. Basic Auth / API Key
  89 
  90 **Use Case**: Simple APIs, internal systems
  91 
  92 **Pattern for API Key**:
  93 ```apex
  94 HttpRequest req = new HttpRequest();
  95 req.setEndpoint('callout:MyCredential/api/resource');
  96 req.setHeader('X-API-Key', '{!$Credential.Password}');
  97 ```
  98 
  99 ## Best Practices
 100 
 101 ### DO
 102 
 103 - **Use Named Credentials** for ALL external callouts
 104 - **Rotate credentials** regularly using Named Credential update
 105 - **Use External Credentials** (API 61+) for new development
 106 - **Limit OAuth scopes** to minimum required
 107 - **Use Per-User Principal** when user context matters
 108 - **Test credentials** before deployment
 109 
 110 ### DON'T
 111 
 112 - **Never hardcode** credentials in Apex
 113 - **Never commit** credentials to source control
 114 - **Don't share** service account credentials across environments
 115 - **Don't use** overly broad OAuth scopes
 116 
 117 ## Common Patterns
 118 
 119 ### Pattern 1: Service Integration
 120 
 121 ```apex
 122 public class ExternalServiceCallout {
 123     public static HttpResponse callService(String endpoint, String body) {
 124         HttpRequest req = new HttpRequest();
 125         req.setEndpoint('callout:ServiceCredential' + endpoint);
 126         req.setMethod('POST');
 127         req.setHeader('Content-Type', 'application/json');
 128         req.setBody(body);
 129         return new Http().send(req);
 130     }
 131 }
 132 ```
 133 
 134 ### Pattern 2: Multiple Environments
 135 
 136 ```
 137 Named Credentials:
 138 ├── MyAPI_Dev     → https://api-dev.example.com
 139 ├── MyAPI_UAT     → https://api-uat.example.com
 140 └── MyAPI_Prod    → https://api.example.com
 141 ```
 142 
 143 Use Custom Metadata or Custom Settings to select credential by environment.
 144 
 145 ### Pattern 3: Per-User OAuth (API 61+)
 146 
 147 For APIs requiring user-specific authentication:
 148 
 149 1. Create External Credential with Per-User Principal
 150 2. Create Named Credential referencing External Credential
 151 3. Users authenticate individually via OAuth flow
 152 4. Each user's callouts use their own token
 153 
 154 ## Troubleshooting
 155 
 156 | Error | Cause | Solution |
 157 |-------|-------|----------|
 158 | `Named credential not found` | Credential doesn't exist or wrong name | Verify credential name in Setup |
 159 | `Authentication failed` | Invalid credentials | Update credentials via Setup UI |
 160 | `Insufficient privileges` | User lacks permission | Assign Permission Set with External Credential Principal Access |
 161 | `Connection refused` | Network/firewall issue | Check Remote Site Settings, firewall rules |
 162 | `Certificate error` | SSL/TLS issue | Verify certificate chain, expiration |
 163 
 164 ## Migration: Legacy to External Credentials
 165 
 166 1. **Create External Credential** with same auth parameters
 167 2. **Create new Named Credential** referencing External Credential
 168 3. **Create Permission Set** with External Credential Principal Access
 169 4. **Assign Permission Set** to integration users
 170 5. **Update Apex code** to use new Named Credential
 171 6. **Test thoroughly** before decommissioning legacy credential
 172 7. **Delete legacy** Named Credential after validation
