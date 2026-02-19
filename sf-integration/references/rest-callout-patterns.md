<!-- Parent: sf-integration/SKILL.md -->
   1 # REST Callout Patterns
   2 
   3 ## Overview
   4 
   5 This guide covers patterns for making HTTP callouts from Salesforce Apex to external REST APIs.
   6 
   7 ## Synchronous vs Asynchronous
   8 
   9 ### When to Use Synchronous
  10 
  11 - User needs immediate response
  12 - Called from Visualforce, LWC, or Aura
  13 - NOT triggered by DML operations
  14 - Response required before next action
  15 
  16 ### When to Use Asynchronous
  17 
  18 - Called from triggers (REQUIRED)
  19 - Fire-and-forget operations
  20 - Background processing
  21 - Long-running operations
  22 
  23 ```
  24 ┌─────────────────────────────────────────────────────────────────┐
  25 │  CALLOUT CONTEXT DECISION                                       │
  26 ├─────────────────────────────────────────────────────────────────┤
  27 │                                                                 │
  28 │  Is this called from a trigger or after DML?                    │
  29 │  ├── YES → Use Queueable with Database.AllowsCallouts          │
  30 │  └── NO  → Synchronous OK                                       │
  31 │                                                                 │
  32 │  Does user need immediate response?                             │
  33 │  ├── YES → Synchronous (if allowed)                            │
  34 │  └── NO  → Consider async for better UX                         │
  35 │                                                                 │
  36 └─────────────────────────────────────────────────────────────────┘
  37 ```
  38 
  39 ## Basic Request Pattern
  40 
  41 ```apex
  42 public class RestCallout {
  43 
  44     public static HttpResponse makeRequest(String method, String endpoint, String body) {
  45         HttpRequest req = new HttpRequest();
  46         req.setEndpoint('callout:MyCredential' + endpoint);
  47         req.setMethod(method);
  48         req.setHeader('Content-Type', 'application/json');
  49         req.setHeader('Accept', 'application/json');
  50         req.setTimeout(120000); // 120 seconds max
  51 
  52         if (String.isNotBlank(body)) {
  53             req.setBody(body);
  54         }
  55 
  56         return new Http().send(req);
  57     }
  58 }
  59 ```
  60 
  61 ## HTTP Methods
  62 
  63 | Method | Use Case | Body |
  64 |--------|----------|------|
  65 | GET | Retrieve resource | No |
  66 | POST | Create resource | Yes |
  67 | PUT | Full update | Yes |
  68 | PATCH | Partial update | Yes |
  69 | DELETE | Remove resource | Usually No |
  70 
  71 ## Response Handling
  72 
  73 ### Status Code Categories
  74 
  75 ```apex
  76 Integer statusCode = response.getStatusCode();
  77 
  78 if (statusCode >= 200 && statusCode < 300) {
  79     // Success (2xx)
  80 } else if (statusCode >= 400 && statusCode < 500) {
  81     // Client error (4xx) - don't retry
  82 } else if (statusCode >= 500) {
  83     // Server error (5xx) - may retry
  84 }
  85 ```
  86 
  87 ### Common Status Codes
  88 
  89 | Code | Meaning | Action |
  90 |------|---------|--------|
  91 | 200 | OK | Process response |
  92 | 201 | Created | Resource created |
  93 | 204 | No Content | Success, no body |
  94 | 400 | Bad Request | Fix request |
  95 | 401 | Unauthorized | Check credentials |
  96 | 403 | Forbidden | Check permissions |
  97 | 404 | Not Found | Resource doesn't exist |
  98 | 429 | Too Many Requests | Rate limited, retry later |
  99 | 500 | Server Error | Retry with backoff |
 100 | 503 | Service Unavailable | Retry later |
 101 
 102 ## Error Handling Pattern
 103 
 104 ```apex
 105 public class ApiClient {
 106 
 107     public static Map<String, Object> callApi(String endpoint) {
 108         try {
 109             HttpResponse res = makeRequest('GET', endpoint, null);
 110 
 111             if (res.getStatusCode() == 200) {
 112                 return (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
 113             }
 114 
 115             // Handle specific errors
 116             if (res.getStatusCode() == 404) {
 117                 throw new NotFoundException('Resource not found: ' + endpoint);
 118             }
 119 
 120             if (res.getStatusCode() == 429) {
 121                 String retryAfter = res.getHeader('Retry-After');
 122                 throw new RateLimitedException('Rate limited. Retry after: ' + retryAfter);
 123             }
 124 
 125             throw new ApiException('API Error: ' + res.getStatusCode() + ' - ' + res.getBody());
 126 
 127         } catch (CalloutException e) {
 128             // Network error, timeout, SSL error
 129             throw new ApiException('Connection failed: ' + e.getMessage(), e);
 130         }
 131     }
 132 
 133     public class ApiException extends Exception {}
 134     public class NotFoundException extends Exception {}
 135     public class RateLimitedException extends Exception {}
 136 }
 137 ```
 138 
 139 ## Retry Pattern
 140 
 141 ```apex
 142 public class RetryableCallout {
 143 
 144     private static final Integer MAX_RETRIES = 3;
 145     private static final Set<Integer> RETRYABLE_CODES = new Set<Integer>{
 146         408, 429, 500, 502, 503, 504
 147     };
 148 
 149     public static HttpResponse callWithRetry(HttpRequest request) {
 150         Integer attempts = 0;
 151 
 152         while (attempts < MAX_RETRIES) {
 153             HttpResponse res = new Http().send(request);
 154 
 155             if (!RETRYABLE_CODES.contains(res.getStatusCode())) {
 156                 return res;
 157             }
 158 
 159             attempts++;
 160             System.debug('Retry ' + attempts + ' for ' + res.getStatusCode());
 161         }
 162 
 163         throw new CalloutException('Max retries exceeded');
 164     }
 165 }
 166 ```
 167 
 168 ## Queueable Pattern (Async)
 169 
 170 ```apex
 171 public class AsyncCallout implements Queueable, Database.AllowsCallouts {
 172 
 173     private Id recordId;
 174 
 175     public AsyncCallout(Id recordId) {
 176         this.recordId = recordId;
 177     }
 178 
 179     public void execute(QueueableContext context) {
 180         // Query record
 181         Account acc = [SELECT Id, Name FROM Account WHERE Id = :recordId];
 182 
 183         // Make callout
 184         HttpRequest req = new HttpRequest();
 185         req.setEndpoint('callout:MyAPI/accounts');
 186         req.setMethod('POST');
 187         req.setBody(JSON.serialize(new Map<String, Object>{
 188             'name' => acc.Name,
 189             'sfId' => acc.Id
 190         }));
 191 
 192         HttpResponse res = new Http().send(req);
 193 
 194         // Update record with result
 195         if (res.getStatusCode() == 201) {
 196             acc.External_Id__c = extractId(res.getBody());
 197             update acc;
 198         }
 199     }
 200 
 201     private String extractId(String body) {
 202         Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(body);
 203         return (String) result.get('id');
 204     }
 205 }
 206 
 207 // Usage from trigger:
 208 // System.enqueueJob(new AsyncCallout(accountId));
 209 ```
 210 
 211 ## Pagination Pattern
 212 
 213 ```apex
 214 public class PaginatedApiClient {
 215 
 216     public static List<Map<String, Object>> getAllRecords(String endpoint) {
 217         List<Map<String, Object>> allRecords = new List<Map<String, Object>>();
 218         String nextPageUrl = endpoint;
 219 
 220         while (String.isNotBlank(nextPageUrl)) {
 221             HttpResponse res = makeRequest('GET', nextPageUrl, null);
 222             Map<String, Object> response = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
 223 
 224             // Add records from this page
 225             List<Object> records = (List<Object>) response.get('data');
 226             for (Object rec : records) {
 227                 allRecords.add((Map<String, Object>) rec);
 228             }
 229 
 230             // Get next page URL
 231             nextPageUrl = (String) response.get('nextPage');
 232         }
 233 
 234         return allRecords;
 235     }
 236 }
 237 ```
 238 
 239 ## Governor Limits
 240 
 241 | Limit | Value |
 242 |-------|-------|
 243 | Callouts per transaction | 100 |
 244 | Maximum timeout | 120,000 ms (120 seconds) |
 245 | Maximum request size | 6 MB |
 246 | Maximum response size | 6 MB |
 247 | Concurrent long-running requests | 10 |
 248 
 249 ## Testing Callouts
 250 
 251 ```apex
 252 @isTest
 253 private class ApiClientTest {
 254 
 255     @isTest
 256     static void testSuccessfulCallout() {
 257         // Set mock
 258         Test.setMock(HttpCalloutMock.class, new MockSuccess());
 259 
 260         Test.startTest();
 261         Map<String, Object> result = ApiClient.callApi('/endpoint');
 262         Test.stopTest();
 263 
 264         System.assertEquals('value', result.get('key'));
 265     }
 266 
 267     private class MockSuccess implements HttpCalloutMock {
 268         public HttpResponse respond(HttpRequest req) {
 269             HttpResponse res = new HttpResponse();
 270             res.setStatusCode(200);
 271             res.setBody('{"key": "value"}');
 272             return res;
 273         }
 274     }
 275 }
 276 ```
 277 
 278 ## Best Practices
 279 
 280 1. **Always use Named Credentials** - Never hardcode endpoints or credentials
 281 2. **Set appropriate timeouts** - Default may be too short for slow APIs
 282 3. **Handle all error cases** - Don't assume success
 283 4. **Log requests and responses** - Essential for debugging
 284 5. **Use async for trigger contexts** - Queueable with AllowsCallouts
 285 6. **Implement retry logic** - For transient failures
 286 7. **Monitor governor limits** - Especially callout count
 287 8. **Parse errors gracefully** - APIs return errors in various formats
