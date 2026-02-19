<!-- Parent: sf-integration/SKILL.md -->
   1 # Callout Patterns Reference
   2 
   3 This document provides detailed implementation patterns for REST and SOAP callouts in Salesforce integrations.
   4 
   5 > **Parent Document**: [sf-integration/SKILL.md](../SKILL.md)
   6 > **Related**: [event-patterns.md](./event-patterns.md)
   7 
   8 ---
   9 
  10 ## Table of Contents
  11 
  12 - [REST Callout Patterns](#rest-callout-patterns)
  13   - [Synchronous REST Callout](#synchronous-rest-callout)
  14   - [Asynchronous REST Callout (Queueable)](#asynchronous-rest-callout-queueable)
  15   - [Retry Handler with Exponential Backoff](#retry-handler-with-exponential-backoff)
  16 - [SOAP Callout Patterns](#soap-callout-patterns)
  17   - [WSDL2Apex Process](#wsdl2apex-process)
  18   - [SOAP Service Implementation](#soap-service-implementation)
  19 
  20 ---
  21 
  22 ## REST Callout Patterns
  23 
  24 ### Synchronous REST Callout
  25 
  26 **Use Case**: Need immediate response, NOT triggered from DML
  27 
  28 **Template**: `assets/callouts/rest-sync-callout.cls`
  29 
  30 **When to Use**:
  31 - User-initiated actions requiring immediate feedback
  32 - API calls from Lightning Web Components
  33 - Scheduled batch jobs needing sequential processing
  34 - Any non-trigger context where response is needed
  35 
  36 **When NOT to Use**:
  37 - Triggered from DML operations (triggers, Process Builder, flows)
  38 - Long-running operations (>10 seconds expected)
  39 - High-volume batch operations
  40 
  41 #### Implementation
  42 
  43 ```apex
  44 public with sharing class {{ServiceName}}Callout {
  45 
  46     private static final String NAMED_CREDENTIAL = 'callout:{{NamedCredentialName}}';
  47 
  48     public static HttpResponse makeRequest(String method, String endpoint, String body) {
  49         HttpRequest req = new HttpRequest();
  50         req.setEndpoint(NAMED_CREDENTIAL + endpoint);
  51         req.setMethod(method);
  52         req.setHeader('Content-Type', 'application/json');
  53         req.setTimeout(120000); // 120 seconds max
  54 
  55         if (String.isNotBlank(body)) {
  56             req.setBody(body);
  57         }
  58 
  59         Http http = new Http();
  60         return http.send(req);
  61     }
  62 
  63     public static Map<String, Object> get(String endpoint) {
  64         HttpResponse res = makeRequest('GET', endpoint, null);
  65         return handleResponse(res);
  66     }
  67 
  68     public static Map<String, Object> post(String endpoint, Map<String, Object> payload) {
  69         HttpResponse res = makeRequest('POST', endpoint, JSON.serialize(payload));
  70         return handleResponse(res);
  71     }
  72 
  73     public static Map<String, Object> put(String endpoint, Map<String, Object> payload) {
  74         HttpResponse res = makeRequest('PUT', endpoint, JSON.serialize(payload));
  75         return handleResponse(res);
  76     }
  77 
  78     public static Map<String, Object> patch(String endpoint, Map<String, Object> payload) {
  79         HttpResponse res = makeRequest('PATCH', endpoint, JSON.serialize(payload));
  80         return handleResponse(res);
  81     }
  82 
  83     public static void deleteRequest(String endpoint) {
  84         makeRequest('DELETE', endpoint, null);
  85     }
  86 
  87     private static Map<String, Object> handleResponse(HttpResponse res) {
  88         Integer statusCode = res.getStatusCode();
  89 
  90         if (statusCode >= 200 && statusCode < 300) {
  91             return (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
  92         } else if (statusCode >= 400 && statusCode < 500) {
  93             throw new CalloutException('Client Error: ' + statusCode + ' - ' + res.getBody());
  94         } else if (statusCode >= 500) {
  95             throw new CalloutException('Server Error: ' + statusCode + ' - ' + res.getBody());
  96         }
  97 
  98         return null;
  99     }
 100 }
 101 ```
 102 
 103 #### Key Features
 104 
 105 - **Named Credential Integration**: Uses `callout:` syntax for secure authentication
 106 - **Timeout Management**: 120-second max timeout (governor limit)
 107 - **HTTP Method Support**: GET, POST, PUT, PATCH, DELETE
 108 - **Status Code Handling**: Differentiates between client (4xx) and server (5xx) errors
 109 - **JSON Serialization**: Automatic JSON handling for request/response bodies
 110 
 111 #### Usage Example
 112 
 113 ```apex
 114 // GET request
 115 try {
 116     Map<String, Object> data = StripeCallout.get('/v1/customers/cus_123');
 117     String email = (String) data.get('email');
 118 } catch (CalloutException e) {
 119     // Handle error
 120     System.debug(LoggingLevel.ERROR, 'Callout failed: ' + e.getMessage());
 121 }
 122 
 123 // POST request
 124 Map<String, Object> payload = new Map<String, Object>{
 125     'email' => 'customer@example.com',
 126     'name' => 'John Doe'
 127 };
 128 Map<String, Object> response = StripeCallout.post('/v1/customers', payload);
 129 ```
 130 
 131 ---
 132 
 133 ### Asynchronous REST Callout (Queueable)
 134 
 135 **Use Case**: Callouts triggered from DML (triggers, Process Builder)
 136 
 137 **Template**: `assets/callouts/rest-queueable-callout.cls`
 138 
 139 **When to Use**:
 140 - Callouts from triggers (REQUIRED - sync callouts fail in triggers)
 141 - Fire-and-forget operations (no immediate response needed)
 142 - Bulk operations processing multiple records
 143 - Long-running API calls (>10 seconds)
 144 
 145 **Governor Limit Considerations**:
 146 - Max 50 queueable jobs per transaction
 147 - Queueable can chain to another queueable (max depth varies by org)
 148 - Callout timeout: 120 seconds
 149 
 150 #### Implementation
 151 
 152 ```apex
 153 public with sharing class {{ServiceName}}QueueableCallout implements Queueable, Database.AllowsCallouts {
 154 
 155     private List<Id> recordIds;
 156     private String operation;
 157 
 158     public {{ServiceName}}QueueableCallout(List<Id> recordIds, String operation) {
 159         this.recordIds = recordIds;
 160         this.operation = operation;
 161     }
 162 
 163     public void execute(QueueableContext context) {
 164         if (recordIds == null || recordIds.isEmpty()) {
 165             return;
 166         }
 167 
 168         try {
 169             // Query records
 170             List<{{ObjectName}}> records = [
 171                 SELECT Id, Name, {{FieldsToSend}}
 172                 FROM {{ObjectName}}
 173                 WHERE Id IN :recordIds
 174                 WITH USER_MODE
 175             ];
 176 
 177             // Make callout for each record (consider batching)
 178             for ({{ObjectName}} record : records) {
 179                 makeCallout(record);
 180             }
 181 
 182         } catch (CalloutException e) {
 183             // Log callout errors
 184             System.debug(LoggingLevel.ERROR, 'Callout failed: ' + e.getMessage());
 185             // Consider: Create error log record, retry logic, notification
 186         } catch (Exception e) {
 187             System.debug(LoggingLevel.ERROR, 'Error: ' + e.getMessage());
 188         }
 189     }
 190 
 191     private void makeCallout({{ObjectName}} record) {
 192         HttpRequest req = new HttpRequest();
 193         req.setEndpoint('callout:{{NamedCredentialName}}/{{Endpoint}}');
 194         req.setMethod('POST');
 195         req.setHeader('Content-Type', 'application/json');
 196         req.setTimeout(120000);
 197 
 198         Map<String, Object> payload = new Map<String, Object>{
 199             'id' => record.Id,
 200             'name' => record.Name
 201             // Add more fields
 202         };
 203         req.setBody(JSON.serialize(payload));
 204 
 205         Http http = new Http();
 206         HttpResponse res = http.send(req);
 207 
 208         if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
 209             // Success - update record status if needed
 210         } else {
 211             // Handle error
 212             throw new CalloutException('API Error: ' + res.getStatusCode());
 213         }
 214     }
 215 }
 216 ```
 217 
 218 #### Trigger Integration
 219 
 220 ```apex
 221 trigger OpportunityTrigger on Opportunity (after insert, after update) {
 222     List<Id> opportunityIds = new List<Id>();
 223 
 224     for (Opportunity opp : Trigger.new) {
 225         // Only sync closed-won opportunities
 226         if (opp.StageName == 'Closed Won') {
 227             opportunityIds.add(opp.Id);
 228         }
 229     }
 230 
 231     if (!opportunityIds.isEmpty()) {
 232         // Enqueue async callout
 233         System.enqueueJob(new SalesforceQueueableCallout(opportunityIds, 'SYNC'));
 234     }
 235 }
 236 ```
 237 
 238 #### Bulkification Pattern
 239 
 240 For high-volume scenarios, batch multiple callouts:
 241 
 242 ```apex
 243 private void makeCallouts(List<{{ObjectName}}> records) {
 244     // Batch up to 10 records per callout
 245     Integer BATCH_SIZE = 10;
 246     List<Map<String, Object>> batch = new List<Map<String, Object>>();
 247 
 248     for (Integer i = 0; i < records.size(); i++) {
 249         batch.add(buildPayload(records[i]));
 250 
 251         if (batch.size() == BATCH_SIZE || i == records.size() - 1) {
 252             // Make single callout with batch
 253             sendBatch(batch);
 254             batch.clear();
 255         }
 256     }
 257 }
 258 
 259 private void sendBatch(List<Map<String, Object>> batch) {
 260     HttpRequest req = new HttpRequest();
 261     req.setEndpoint('callout:{{NamedCredentialName}}/batch');
 262     req.setMethod('POST');
 263     req.setHeader('Content-Type', 'application/json');
 264     req.setTimeout(120000);
 265     req.setBody(JSON.serialize(new Map<String, Object>{'records' => batch}));
 266 
 267     Http http = new Http();
 268     HttpResponse res = http.send(req);
 269     // Handle response
 270 }
 271 ```
 272 
 273 ---
 274 
 275 ### Retry Handler with Exponential Backoff
 276 
 277 **Use Case**: Handle transient failures with intelligent retry logic
 278 
 279 **Template**: `assets/callouts/callout-retry-handler.cls`
 280 
 281 **Retry Strategy**:
 282 - **Max Retries**: 3 attempts
 283 - **Backoff**: Exponential (1s, 2s, 4s)
 284 - **Retry on**: 5xx server errors, network timeouts
 285 - **Don't Retry**: 4xx client errors (bad request, auth failure)
 286 
 287 #### Implementation
 288 
 289 ```apex
 290 public with sharing class CalloutRetryHandler {
 291 
 292     private static final Integer MAX_RETRIES = 3;
 293     private static final Integer BASE_DELAY_MS = 1000; // 1 second
 294 
 295     public static HttpResponse executeWithRetry(HttpRequest request) {
 296         Integer retryCount = 0;
 297         HttpResponse response;
 298 
 299         while (retryCount < MAX_RETRIES) {
 300             try {
 301                 Http http = new Http();
 302                 response = http.send(request);
 303 
 304                 // Success or client error (4xx) - don't retry
 305                 if (response.getStatusCode() < 500) {
 306                     return response;
 307                 }
 308 
 309                 // Server error (5xx) - retry with backoff
 310                 retryCount++;
 311                 if (retryCount < MAX_RETRIES) {
 312                     // Exponential backoff: 1s, 2s, 4s
 313                     Integer delayMs = BASE_DELAY_MS * (Integer) Math.pow(2, retryCount - 1);
 314                     // Note: Apex doesn't have sleep(), so we schedule retry via Queueable
 315                     throw new RetryableException('Server error, retry ' + retryCount);
 316                 }
 317 
 318             } catch (CalloutException e) {
 319                 retryCount++;
 320                 if (retryCount >= MAX_RETRIES) {
 321                     throw e;
 322                 }
 323             }
 324         }
 325 
 326         return response;
 327     }
 328 
 329     public class RetryableException extends Exception {}
 330 }
 331 ```
 332 
 333 #### Queueable Retry Pattern
 334 
 335 Since Apex doesn't support `Thread.sleep()`, implement retry delays using Queueable chaining:
 336 
 337 ```apex
 338 public with sharing class CalloutWithRetryQueueable implements Queueable, Database.AllowsCallouts {
 339 
 340     private HttpRequest request;
 341     private Integer retryCount;
 342     private static final Integer MAX_RETRIES = 3;
 343 
 344     public CalloutWithRetryQueueable(HttpRequest req) {
 345         this(req, 0);
 346     }
 347 
 348     private CalloutWithRetryQueueable(HttpRequest req, Integer retries) {
 349         this.request = req;
 350         this.retryCount = retries;
 351     }
 352 
 353     public void execute(QueueableContext context) {
 354         try {
 355             Http http = new Http();
 356             HttpResponse res = http.send(request);
 357 
 358             if (res.getStatusCode() >= 500 && retryCount < MAX_RETRIES) {
 359                 // Server error - retry
 360                 System.debug(LoggingLevel.WARN, 'Retry ' + (retryCount + 1) + ' for ' + request.getEndpoint());
 361                 System.enqueueJob(new CalloutWithRetryQueueable(request, retryCount + 1));
 362             } else if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
 363                 // Success
 364                 handleSuccess(res);
 365             } else {
 366                 // Client error - don't retry
 367                 handleError(res);
 368             }
 369 
 370         } catch (CalloutException e) {
 371             if (retryCount < MAX_RETRIES) {
 372                 System.enqueueJob(new CalloutWithRetryQueueable(request, retryCount + 1));
 373             } else {
 374                 throw e;
 375             }
 376         }
 377     }
 378 
 379     private void handleSuccess(HttpResponse res) {
 380         // Process successful response
 381         System.debug('Callout succeeded: ' + res.getBody());
 382     }
 383 
 384     private void handleError(HttpResponse res) {
 385         // Log error
 386         System.debug(LoggingLevel.ERROR, 'Callout error: ' + res.getStatusCode() + ' - ' + res.getBody());
 387     }
 388 }
 389 ```
 390 
 391 #### Idempotency Considerations
 392 
 393 When implementing retries, ensure API operations are idempotent:
 394 
 395 ```apex
 396 // BAD: Non-idempotent (creates new record on each retry)
 397 POST /api/orders { "item": "Widget", "quantity": 1 }
 398 
 399 // GOOD: Idempotent (uses idempotency key)
 400 POST /api/orders
 401 Headers: Idempotency-Key: {{recordId}}-{{timestamp}}
 402 { "item": "Widget", "quantity": 1 }
 403 ```
 404 
 405 ---
 406 
 407 ## SOAP Callout Patterns
 408 
 409 ### WSDL2Apex Process
 410 
 411 SOAP integrations in Salesforce use WSDL2Apex to auto-generate Apex classes from WSDL files.
 412 
 413 #### Step-by-Step Process
 414 
 415 **Step 1: Generate Apex from WSDL**
 416 
 417 1. Navigate to **Setup** → **Apex Classes** → **Generate from WSDL**
 418 2. Upload WSDL file or provide URL
 419 3. Salesforce parses WSDL and generates:
 420    - Stub class (contains service endpoint and operations)
 421    - Request/Response classes (for each operation)
 422    - Type classes (for complex data types)
 423 
 424 **Step 2: Configure Named Credential**
 425 
 426 Create a Named Credential for the SOAP endpoint:
 427 
 428 ```xml
 429 <?xml version="1.0" encoding="UTF-8"?>
 430 <NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
 431     <label>{{ServiceName}} SOAP</label>
 432     <endpoint>https://api.example.com/soap/v1</endpoint>
 433     <principalType>NamedUser</principalType>
 434     <protocol>Password</protocol>
 435     <username>{{Username}}</username>
 436     <password>{{Password}}</password>
 437 </NamedCredential>
 438 ```
 439 
 440 **Step 3: Use Generated Classes**
 441 
 442 Generated classes follow this naming pattern:
 443 - **Stub Class**: `{{WsdlNamespace}}.{{ServiceName}}`
 444 - **Port Type**: `{{WsdlNamespace}}.{{PortTypeName}}`
 445 - **Operations**: Methods on the port type class
 446 
 447 ---
 448 
 449 ### SOAP Service Implementation
 450 
 451 **Template**: `assets/soap/soap-callout-service.cls`
 452 
 453 #### Basic SOAP Callout
 454 
 455 ```apex
 456 public with sharing class {{ServiceName}}SoapService {
 457 
 458     public static {{ResponseType}} callService({{RequestType}} request) {
 459         try {
 460             // Generated stub class
 461             {{WsdlGeneratedClass}}.{{PortType}} stub = new {{WsdlGeneratedClass}}.{{PortType}}();
 462 
 463             // Set endpoint (use Named Credential if possible)
 464             stub.endpoint_x = 'callout:{{NamedCredentialName}}';
 465 
 466             // Set timeout
 467             stub.timeout_x = 120000;
 468 
 469             // Make the call
 470             return stub.{{OperationName}}(request);
 471 
 472         } catch (Exception e) {
 473             System.debug(LoggingLevel.ERROR, 'SOAP Callout Error: ' + e.getMessage());
 474             throw new CalloutException('SOAP service error: ' + e.getMessage());
 475         }
 476     }
 477 }
 478 ```
 479 
 480 #### Example: Weather Service SOAP Callout
 481 
 482 **WSDL**: `http://www.webservicex.net/globalweather.asmx?WSDL`
 483 
 484 **Generated Classes**:
 485 - `GlobalWeatherSoap`
 486 - `GetWeatherRequest`
 487 - `GetWeatherResponse`
 488 
 489 **Service Implementation**:
 490 
 491 ```apex
 492 public with sharing class WeatherService {
 493 
 494     public static String getWeather(String city, String country) {
 495         try {
 496             // Initialize SOAP stub
 497             GlobalWeatherSoap.GlobalWeatherSoap stub =
 498                 new GlobalWeatherSoap.GlobalWeatherSoap();
 499 
 500             // Configure endpoint and timeout
 501             stub.endpoint_x = 'callout:GlobalWeather_NC';
 502             stub.timeout_x = 120000;
 503 
 504             // Build request
 505             GlobalWeatherSoap.GetWeatherRequest req =
 506                 new GlobalWeatherSoap.GetWeatherRequest();
 507             req.CityName = city;
 508             req.CountryName = country;
 509 
 510             // Make callout
 511             GlobalWeatherSoap.GetWeatherResponse res = stub.GetWeather(req);
 512 
 513             return res.GetWeatherResult;
 514 
 515         } catch (System.CalloutException e) {
 516             System.debug(LoggingLevel.ERROR, 'Weather API callout failed: ' + e.getMessage());
 517             return null;
 518         }
 519     }
 520 }
 521 ```
 522 
 523 #### SOAP Headers and Authentication
 524 
 525 For SOAP services requiring custom headers (e.g., WS-Security):
 526 
 527 ```apex
 528 public with sharing class SecureSoapService {
 529 
 530     public static void callServiceWithAuth(String username, String password) {
 531         // Generated stub
 532         MyService.MyServiceSoap stub = new MyService.MyServiceSoap();
 533 
 534         // Set endpoint
 535         stub.endpoint_x = 'callout:MyService_NC';
 536         stub.timeout_x = 120000;
 537 
 538         // Set SOAP headers for authentication
 539         stub.inputHttpHeaders_x = new Map<String, String>{
 540             'SOAPAction' => 'http://tempuri.org/IMyService/MyOperation',
 541             'Authorization' => 'Basic ' + EncodingUtil.base64Encode(
 542                 Blob.valueOf(username + ':' + password)
 543             )
 544         };
 545 
 546         // Make request
 547         MyService.MyRequest req = new MyService.MyRequest();
 548         MyService.MyResponse res = stub.MyOperation(req);
 549     }
 550 }
 551 ```
 552 
 553 #### SOAP Fault Handling
 554 
 555 ```apex
 556 public with sharing class RobustSoapService {
 557 
 558     public static Object callWithFaultHandling() {
 559         try {
 560             MyService.MyServiceSoap stub = new MyService.MyServiceSoap();
 561             stub.endpoint_x = 'callout:MyService_NC';
 562             stub.timeout_x = 120000;
 563 
 564             MyService.MyRequest req = new MyService.MyRequest();
 565             return stub.MyOperation(req);
 566 
 567         } catch (System.CalloutException e) {
 568             // Parse SOAP fault
 569             String errorMessage = e.getMessage();
 570 
 571             if (errorMessage.contains('faultcode')) {
 572                 // SOAP Fault occurred
 573                 System.debug(LoggingLevel.ERROR, 'SOAP Fault: ' + errorMessage);
 574                 // Extract fault details using XML parsing if needed
 575             } else {
 576                 // Network/HTTP error
 577                 System.debug(LoggingLevel.ERROR, 'Callout error: ' + errorMessage);
 578             }
 579 
 580             throw e;
 581         }
 582     }
 583 }
 584 ```
 585 
 586 #### Async SOAP Callout (Queueable)
 587 
 588 For SOAP callouts triggered from DML:
 589 
 590 ```apex
 591 public with sharing class SoapQueueableCallout implements Queueable, Database.AllowsCallouts {
 592 
 593     private List<Id> recordIds;
 594 
 595     public SoapQueueableCallout(List<Id> recordIds) {
 596         this.recordIds = recordIds;
 597     }
 598 
 599     public void execute(QueueableContext context) {
 600         try {
 601             // Query records
 602             List<Account> accounts = [
 603                 SELECT Id, Name, BillingCity, BillingCountry
 604                 FROM Account
 605                 WHERE Id IN :recordIds
 606                 WITH USER_MODE
 607             ];
 608 
 609             // Initialize SOAP stub
 610             GlobalWeatherSoap.GlobalWeatherSoap stub =
 611                 new GlobalWeatherSoap.GlobalWeatherSoap();
 612             stub.endpoint_x = 'callout:GlobalWeather_NC';
 613             stub.timeout_x = 120000;
 614 
 615             // Process each record
 616             for (Account acc : accounts) {
 617                 GlobalWeatherSoap.GetWeatherRequest req =
 618                     new GlobalWeatherSoap.GetWeatherRequest();
 619                 req.CityName = acc.BillingCity;
 620                 req.CountryName = acc.BillingCountry;
 621 
 622                 GlobalWeatherSoap.GetWeatherResponse res = stub.GetWeather(req);
 623 
 624                 // Update account with weather data
 625                 acc.Weather_Data__c = res.GetWeatherResult;
 626             }
 627 
 628             // Update records
 629             update as user accounts;
 630 
 631         } catch (Exception e) {
 632             System.debug(LoggingLevel.ERROR, 'SOAP Queueable error: ' + e.getMessage());
 633         }
 634     }
 635 }
 636 ```
 637 
 638 ---
 639 
 640 ## Best Practices
 641 
 642 ### Callout Governor Limits
 643 
 644 | Limit | Value | Notes |
 645 |-------|-------|-------|
 646 | Max callouts per transaction | 100 | Batch multiple requests if possible |
 647 | Max timeout per callout | 120 seconds | Set explicitly with `setTimeout()` |
 648 | Max total timeout per transaction | 120 seconds | All callouts combined |
 649 | Max heap size | 6 MB (sync) / 12 MB (async) | Large responses consume heap |
 650 
 651 ### Security Checklist
 652 
 653 - Use Named Credentials for authentication (NEVER hardcode credentials)
 654 - Minimize OAuth scopes to least privilege
 655 - Use Certificate-based auth for high-security integrations
 656 - Validate SSL certificates (don't disable SSL verification)
 657 - Sanitize user input before including in callout payloads
 658 - Log callout errors without exposing sensitive data
 659 
 660 ### Error Handling Patterns
 661 
 662 ```apex
 663 try {
 664     HttpResponse res = makeCallout();
 665     handleResponse(res);
 666 } catch (System.CalloutException e) {
 667     // Network error, timeout, SSL error
 668     logError('Callout failed', e);
 669 } catch (JSONException e) {
 670     // Malformed JSON response
 671     logError('JSON parsing failed', e);
 672 } catch (Exception e) {
 673     // Unexpected error
 674     logError('Unexpected error', e);
 675 }
 676 ```
 677 
 678 ### Testing Callouts
 679 
 680 Use `Test.setMock()` to mock HTTP responses:
 681 
 682 ```apex
 683 @isTest
 684 private class MyCalloutTest {
 685 
 686     @isTest
 687     static void testSuccessfulCallout() {
 688         // Set mock response
 689         Test.setMock(HttpCalloutMock.class, new MockHttpResponseGenerator());
 690 
 691         Test.startTest();
 692         Map<String, Object> result = MyService.get('/customers/123');
 693         Test.stopTest();
 694 
 695         System.assertEquals('customer@example.com', result.get('email'));
 696     }
 697 
 698     // Mock class
 699     private class MockHttpResponseGenerator implements HttpCalloutMock {
 700         public HttpResponse respond(HttpRequest req) {
 701             HttpResponse res = new HttpResponse();
 702             res.setHeader('Content-Type', 'application/json');
 703             res.setBody('{"email":"customer@example.com"}');
 704             res.setStatusCode(200);
 705             return res;
 706         }
 707     }
 708 }
 709 ```
 710 
 711 ---
 712 
 713 ## Related Resources
 714 
 715 - [Event Patterns](./event-patterns.md) - Platform Events and Change Data Capture
 716 - [Main Skill Documentation](../SKILL.md) - sf-integration overview
 717 - [Named Credentials Templates](../assets/named-credentials/) - Authentication templates
 718 - [Callout Templates](../assets/callouts/) - Ready-to-use callout patterns
