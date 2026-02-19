<!-- Parent: sf-integration/SKILL.md -->
   1 # Integration Security Best Practices
   2 
   3 ## Overview
   4 
   5 Security is critical for integrations. This guide covers best practices for securing Salesforce integrations with external systems.
   6 
   7 ## Credential Management
   8 
   9 ### DO: Use Named Credentials
  10 
  11 ```apex
  12 // ✅ CORRECT - Named Credential handles auth
  13 HttpRequest req = new HttpRequest();
  14 req.setEndpoint('callout:MySecureAPI/resource');
  15 ```
  16 
  17 ### DON'T: Hardcode Credentials
  18 
  19 ```apex
  20 // ❌ WRONG - Never hardcode credentials
  21 req.setHeader('Authorization', 'Bearer sk_live_abc123...');
  22 req.setEndpoint('https://api.example.com');
  23 ```
  24 
  25 ### Credential Storage Rules
  26 
  27 | Item | Storage Location | Never Store In |
  28 |------|------------------|----------------|
  29 | API Keys | Named Credential | Apex code, Custom Settings |
  30 | Client Secrets | Named Credential / External Credential | Source control |
  31 | Certificates | Certificate & Key Management | Static Resources |
  32 | Passwords | Named Credential | Custom Metadata |
  33 
  34 ## OAuth Best Practices
  35 
  36 ### Scope Minimization
  37 
  38 Request only necessary scopes:
  39 
  40 ```
  41 ✅ read:orders write:orders
  42 ❌ admin:* read:* write:*
  43 ```
  44 
  45 ### Token Handling
  46 
  47 - Never log access tokens
  48 - Don't expose tokens in error messages
  49 - Use short-lived tokens when possible
  50 - Implement token refresh handling
  51 
  52 ### PKCE for Public Clients
  53 
  54 For mobile or SPA clients:
  55 
  56 ```
  57 Use Authorization Code with PKCE, not Implicit flow
  58 ```
  59 
  60 ## Network Security
  61 
  62 ### Remote Site Settings
  63 
  64 - Only allow necessary domains
  65 - Don't use wildcard domains
  66 - Review and audit regularly
  67 
  68 ### Certificate Validation
  69 
  70 - Use trusted CA certificates
  71 - Don't disable SSL/TLS verification
  72 - Monitor certificate expiration
  73 
  74 ### IP Restrictions
  75 
  76 For Connected Apps:
  77 - Configure IP relaxation carefully
  78 - Use "Enforce IP restrictions" when possible
  79 
  80 ## Input Validation
  81 
  82 ### Validate External Data
  83 
  84 ```apex
  85 // Validate before processing
  86 public static void processExternalData(String externalId) {
  87     // Validate format
  88     if (!Pattern.matches('[A-Za-z0-9]{10,20}', externalId)) {
  89         throw new ValidationException('Invalid external ID format');
  90     }
  91 
  92     // Sanitize for SOQL
  93     String safeId = String.escapeSingleQuotes(externalId);
  94 }
  95 ```
  96 
  97 ### Output Encoding
  98 
  99 ```apex
 100 // Encode data sent to external systems
 101 String encodedData = EncodingUtil.urlEncode(userData, 'UTF-8');
 102 ```
 103 
 104 ## Error Handling Security
 105 
 106 ### Don't Expose Internal Details
 107 
 108 ```apex
 109 // ❌ WRONG - Exposes internal structure
 110 throw new CalloutException('Failed: ' + response.getBody());
 111 
 112 // ✅ CORRECT - User-friendly, log details separately
 113 System.debug(LoggingLevel.ERROR, 'API Error: ' + response.getBody());
 114 throw new CalloutException('Unable to complete request. Contact support.');
 115 ```
 116 
 117 ### Log Securely
 118 
 119 ```apex
 120 // ❌ WRONG - Logs sensitive data
 121 System.debug('Request: ' + JSON.serialize(request)); // May contain PII
 122 
 123 // ✅ CORRECT - Redact sensitive fields
 124 System.debug('Request to: ' + endpoint + ', Status: ' + statusCode);
 125 ```
 126 
 127 ## API Security Patterns
 128 
 129 ### Rate Limiting Awareness
 130 
 131 ```apex
 132 if (response.getStatusCode() == 429) {
 133     String retryAfter = response.getHeader('Retry-After');
 134     // Implement backoff, don't hammer the API
 135 }
 136 ```
 137 
 138 ### Idempotency Keys
 139 
 140 For POST requests that shouldn't duplicate:
 141 
 142 ```apex
 143 req.setHeader('Idempotency-Key', generateUniqueKey());
 144 ```
 145 
 146 ### Request Signing
 147 
 148 For APIs requiring signature:
 149 
 150 ```apex
 151 String signature = generateHmacSignature(payload, secretKey);
 152 req.setHeader('X-Signature', signature);
 153 ```
 154 
 155 ## User Context Security
 156 
 157 ### Per-User vs Named Principal
 158 
 159 | Scenario | Use |
 160 |----------|-----|
 161 | User-specific data access | Per-User Principal |
 162 | Background/batch jobs | Named Principal |
 163 | Service integrations | Named Principal |
 164 | User-initiated with audit | Per-User Principal |
 165 
 166 ### Audit Logging
 167 
 168 ```apex
 169 public static void logIntegrationActivity(String operation, Id userId, String externalSystem) {
 170     Integration_Log__c log = new Integration_Log__c(
 171         Operation__c = operation,
 172         User__c = userId,
 173         External_System__c = externalSystem,
 174         Timestamp__c = Datetime.now()
 175     );
 176     insert log;
 177 }
 178 ```
 179 
 180 ## Platform Event Security
 181 
 182 ### Sensitive Data in Events
 183 
 184 - Don't include PII in event payloads when avoidable
 185 - Use record IDs and query for details
 186 - Consider encryption for sensitive fields
 187 
 188 ### Event Consumer Validation
 189 
 190 ```apex
 191 trigger SecureEventHandler on My_Event__e (after insert) {
 192     for (My_Event__e event : Trigger.new) {
 193         // Validate event source/origin if possible
 194         if (!isValidEventSource(event)) {
 195             System.debug(LoggingLevel.WARN, 'Suspicious event: ' + event.ReplayId);
 196             continue;
 197         }
 198         processEvent(event);
 199     }
 200 }
 201 ```
 202 
 203 ## Security Checklist
 204 
 205 ### Before Deployment
 206 
 207 - [ ] Named Credentials used for all external calls
 208 - [ ] No hardcoded credentials in code
 209 - [ ] OAuth scopes minimized
 210 - [ ] Remote Site Settings restricted
 211 - [ ] Error messages don't expose internals
 212 - [ ] Sensitive data not logged
 213 - [ ] Input validation implemented
 214 - [ ] Rate limiting handled
 215 - [ ] Certificate expiration monitored
 216 
 217 ### Regular Review
 218 
 219 - [ ] Audit Named Credential usage
 220 - [ ] Review integration user permissions
 221 - [ ] Check for unused credentials
 222 - [ ] Monitor integration error logs
 223 - [ ] Validate certificate validity
 224 - [ ] Review OAuth app authorizations
 225 
 226 ## Compliance Considerations
 227 
 228 ### GDPR / Data Privacy
 229 
 230 - Minimize data transferred
 231 - Document data flows
 232 - Implement data deletion for integrated records
 233 - Encrypt PII in transit and at rest
 234 
 235 ### SOC 2 / Security Audits
 236 
 237 - Maintain integration documentation
 238 - Log all external access
 239 - Implement change management
 240 - Regular security assessments
 241 
 242 ### HIPAA (Healthcare)
 243 
 244 - Business Associate Agreements
 245 - Encryption requirements
 246 - Access logging
 247 - Minimum necessary standard
