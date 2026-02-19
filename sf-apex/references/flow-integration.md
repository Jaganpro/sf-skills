<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Flow Integration Guide
   2 
   3 This guide covers creating Apex classes callable from Salesforce Flows using `@InvocableMethod` and `@InvocableVariable`.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────┐
  11 │                     FLOW → APEX INTEGRATION                         │
  12 ├─────────────────────────────────────────────────────────────────────┤
  13 │                                                                      │
  14 │   ┌─────────────┐     actionCalls      ┌─────────────────────┐     │
  15 │   │    Flow     │ ─────────────────────▶ │  @InvocableMethod   │     │
  16 │   │   Action    │                       │  Apex Class          │     │
  17 │   └─────────────┘ ◀───────────────────── └─────────────────────┘     │
  18 │                      Response                                        │
  19 │                                                                      │
  20 │   Input Variables ────▶ Request Wrapper ────▶ Business Logic        │
  21 │   Output Variables ◀──── Response Wrapper ◀──── Return Values       │
  22 │                                                                      │
  23 └─────────────────────────────────────────────────────────────────────┘
  24 ```
  25 
  26 ---
  27 
  28 ## Quick Reference
  29 
  30 | Annotation | Purpose | Required |
  31 |------------|---------|----------|
  32 | `@InvocableMethod` | Marks method as Flow-callable | Yes |
  33 | `@InvocableVariable` | Marks property as Flow parameter | Yes (for wrappers) |
  34 
  35 ---
  36 
  37 ## @InvocableMethod Decorator
  38 
  39 ### Syntax
  40 
  41 ```apex
  42 @InvocableMethod(
  43     label='Display Name in Flow'
  44     description='Explanation shown in Flow Builder'
  45     category='Category for grouping'
  46     callout=true  // If method makes HTTP callouts
  47 )
  48 public static List<Response> execute(List<Request> requests) {
  49     // Implementation
  50 }
  51 ```
  52 
  53 ### Parameters
  54 
  55 | Parameter | Description | Required |
  56 |-----------|-------------|----------|
  57 | `label` | Display name in Flow Builder action list | Yes |
  58 | `description` | Help text shown when configuring action | No |
  59 | `category` | Groups actions in Flow Builder | No |
  60 | `callout` | Set `true` if method makes HTTP callouts | No (default: false) |
  61 | `configurationEditor` | Custom LWC for configuration UI | No |
  62 
  63 ### Method Signature Rules
  64 
  65 ```apex
  66 // ✅ CORRECT: Static, List input, List output
  67 public static List<Response> execute(List<Request> requests)
  68 
  69 // ❌ WRONG: Non-static method
  70 public List<Response> execute(List<Request> requests)
  71 
  72 // ❌ WRONG: Single object (not List)
  73 public static Response execute(Request request)
  74 
  75 // ✅ CORRECT: Simple types also allowed
  76 public static List<String> execute(List<Id> recordIds)
  77 ```
  78 
  79 ---
  80 
  81 ## @InvocableVariable Decorator
  82 
  83 ### Syntax
  84 
  85 ```apex
  86 public class Request {
  87     @InvocableVariable(
  88         label='Record ID'
  89         description='The ID of the record to process'
  90         required=true
  91     )
  92     public Id recordId;
  93 }
  94 ```
  95 
  96 ### Parameters
  97 
  98 | Parameter | Description | Required |
  99 |-----------|-------------|----------|
 100 | `label` | Display name in Flow mapping UI | Yes |
 101 | `description` | Help text for the variable | No |
 102 | `required` | Whether Flow must provide a value | No (default: false) |
 103 
 104 ### Supported Data Types
 105 
 106 | Type | Flow Equivalent | Notes |
 107 |------|-----------------|-------|
 108 | `Boolean` | Boolean | |
 109 | `Date` | Date | |
 110 | `DateTime` | DateTime | |
 111 | `Decimal` | Number | |
 112 | `Double` | Number | |
 113 | `Integer` | Number | |
 114 | `Long` | Number | |
 115 | `String` | Text | |
 116 | `Time` | Time | |
 117 | `Id` | Text (Record ID) | Stores as 18-char ID |
 118 | `SObject` | Record | Any standard/custom object |
 119 | `List<T>` | Collection | Collection of any above type |
 120 
 121 ---
 122 
 123 ## Request/Response Pattern
 124 
 125 The recommended pattern uses wrapper classes for clean data exchange:
 126 
 127 ```apex
 128 public class AccountProcessorInvocable {
 129 
 130     @InvocableMethod(label='Process Account' category='Account')
 131     public static List<Response> execute(List<Request> requests) {
 132         List<Response> responses = new List<Response>();
 133 
 134         for (Request req : requests) {
 135             Response res = new Response();
 136             try {
 137                 // Process the request
 138                 res = processRequest(req);
 139             } catch (Exception e) {
 140                 res.isSuccess = false;
 141                 res.errorMessage = e.getMessage();
 142             }
 143             responses.add(res);
 144         }
 145 
 146         return responses;
 147     }
 148 
 149     private static Response processRequest(Request req) {
 150         // Business logic here
 151         Response res = new Response();
 152         res.isSuccess = true;
 153         res.outputMessage = 'Processed successfully';
 154         return res;
 155     }
 156 
 157     // ═══════════════════════════════════════════════════════════════
 158     // REQUEST WRAPPER
 159     // ═══════════════════════════════════════════════════════════════
 160     public class Request {
 161         @InvocableVariable(label='Account ID' required=true)
 162         public Id accountId;
 163 
 164         @InvocableVariable(label='Operation Type')
 165         public String operation;
 166     }
 167 
 168     // ═══════════════════════════════════════════════════════════════
 169     // RESPONSE WRAPPER
 170     // ═══════════════════════════════════════════════════════════════
 171     public class Response {
 172         @InvocableVariable(label='Is Success')
 173         public Boolean isSuccess;
 174 
 175         @InvocableVariable(label='Error Message')
 176         public String errorMessage;
 177 
 178         @InvocableVariable(label='Output Message')
 179         public String outputMessage;
 180 
 181         @InvocableVariable(label='Result Record ID')
 182         public Id outputRecordId;
 183     }
 184 }
 185 ```
 186 
 187 ---
 188 
 189 ## Bulkification Best Practices
 190 
 191 Flows can invoke your method with multiple records. Always bulkify:
 192 
 193 ```apex
 194 @InvocableMethod(label='Update Accounts' category='Account')
 195 public static List<Response> execute(List<Request> requests) {
 196     List<Response> responses = new List<Response>();
 197 
 198     // ─────────────────────────────────────────────────────────────
 199     // STEP 1: Collect all IDs first (avoid SOQL in loop)
 200     // ─────────────────────────────────────────────────────────────
 201     Set<Id> accountIds = new Set<Id>();
 202     for (Request req : requests) {
 203         if (req.accountId != null) {
 204             accountIds.add(req.accountId);
 205         }
 206     }
 207 
 208     // ─────────────────────────────────────────────────────────────
 209     // STEP 2: Single bulk query with USER_MODE
 210     // ─────────────────────────────────────────────────────────────
 211     Map<Id, Account> accountsById = new Map<Id, Account>(
 212         [SELECT Id, Name, Industry, AnnualRevenue
 213          FROM Account
 214          WHERE Id IN :accountIds
 215          WITH USER_MODE]
 216     );
 217 
 218     // ─────────────────────────────────────────────────────────────
 219     // STEP 3: Collect DML records
 220     // ─────────────────────────────────────────────────────────────
 221     List<Account> accountsToUpdate = new List<Account>();
 222 
 223     for (Request req : requests) {
 224         Response res = new Response();
 225         Account acc = accountsById.get(req.accountId);
 226 
 227         if (acc == null) {
 228             res.isSuccess = false;
 229             res.errorMessage = 'Account not found: ' + req.accountId;
 230         } else {
 231             // Process and collect for bulk DML
 232             acc.Description = 'Processed via Flow';
 233             accountsToUpdate.add(acc);
 234             res.isSuccess = true;
 235             res.outputRecordId = acc.Id;
 236         }
 237 
 238         responses.add(res);
 239     }
 240 
 241     // ─────────────────────────────────────────────────────────────
 242     // STEP 4: Single bulk DML operation
 243     // ─────────────────────────────────────────────────────────────
 244     if (!accountsToUpdate.isEmpty()) {
 245         update accountsToUpdate;
 246     }
 247 
 248     return responses;
 249 }
 250 ```
 251 
 252 ---
 253 
 254 ## Error Handling
 255 
 256 ### Return Errors to Flow (Recommended)
 257 
 258 ```apex
 259 public class Response {
 260     @InvocableVariable(label='Is Success')
 261     public Boolean isSuccess;
 262 
 263     @InvocableVariable(label='Error Message')
 264     public String errorMessage;
 265 
 266     @InvocableVariable(label='Error Type')
 267     public String errorType;
 268 }
 269 
 270 // In your method:
 271 try {
 272     // Business logic
 273     res.isSuccess = true;
 274 } catch (DmlException e) {
 275     res.isSuccess = false;
 276     res.errorMessage = e.getDmlMessage(0);
 277     res.errorType = 'DmlException';
 278 } catch (Exception e) {
 279     res.isSuccess = false;
 280     res.errorMessage = e.getMessage();
 281     res.errorType = e.getTypeName();
 282 }
 283 ```
 284 
 285 ### Throw Exception (Flow Fault Path)
 286 
 287 ```apex
 288 // Throwing an exception triggers the Flow's Fault path
 289 @InvocableMethod(label='Process Account')
 290 public static List<Response> execute(List<Request> requests) {
 291     if (requests.isEmpty()) {
 292         throw new InvocableException('No requests provided');
 293     }
 294     // ...
 295 }
 296 
 297 public class InvocableException extends Exception {}
 298 ```
 299 
 300 **Flow Fault Connector:**
 301 ```xml
 302 <actionCalls>
 303     <name>Call_Apex</name>
 304     <faultConnector>
 305         <targetReference>Handle_Error</targetReference>
 306     </faultConnector>
 307     <!-- ... -->
 308 </actionCalls>
 309 ```
 310 
 311 ---
 312 
 313 ## Working with Collections
 314 
 315 ### Accept Collection Input
 316 
 317 ```apex
 318 public class Request {
 319     @InvocableVariable(label='Account IDs' required=true)
 320     public List<Id> accountIds;  // Flow passes a collection
 321 }
 322 ```
 323 
 324 ### Return Collection Output
 325 
 326 ```apex
 327 public class Response {
 328     @InvocableVariable(label='Processed Accounts')
 329     public List<Account> accounts;  // Flow receives a collection
 330 }
 331 ```
 332 
 333 ### Collection Iteration in Flow
 334 
 335 When your invocable returns a List inside the Response, Flow can:
 336 1. Use it directly in data tables
 337 2. Loop over it with a Loop element
 338 3. Pass it to another invocable action
 339 
 340 ---
 341 
 342 ## Security Considerations
 343 
 344 ### FLS/CRUD Enforcement
 345 
 346 ```apex
 347 // Use USER_MODE for automatic FLS/CRUD checks
 348 Map<Id, Account> accounts = new Map<Id, Account>(
 349     [SELECT Id, Name FROM Account WHERE Id IN :ids WITH USER_MODE]
 350 );
 351 
 352 // Or use Security.stripInaccessible for DML
 353 SObjectAccessDecision decision = Security.stripInaccessible(
 354     AccessType.CREATABLE,
 355     accounts
 356 );
 357 insert decision.getRecords();
 358 ```
 359 
 360 ### with sharing
 361 
 362 ```apex
 363 // Always use 'with sharing' unless there's a specific reason not to
 364 public with sharing class AccountInvocable {
 365     // Respects org-wide defaults and sharing rules
 366 }
 367 ```
 368 
 369 ---
 370 
 371 ## Testing Invocable Methods
 372 
 373 ```apex
 374 @IsTest
 375 private class AccountInvocableTest {
 376 
 377     @IsTest
 378     static void testSuccessScenario() {
 379         // Setup test data
 380         Account testAccount = new Account(Name = 'Test Account');
 381         insert testAccount;
 382 
 383         // Create request
 384         AccountInvocable.Request req = new AccountInvocable.Request();
 385         req.accountId = testAccount.Id;
 386         req.operation = 'process';
 387 
 388         // Execute
 389         Test.startTest();
 390         List<AccountInvocable.Response> responses =
 391             AccountInvocable.execute(new List<AccountInvocable.Request>{ req });
 392         Test.stopTest();
 393 
 394         // Verify
 395         System.assertEquals(1, responses.size(), 'Should return one response');
 396         System.assertEquals(true, responses[0].isSuccess, 'Should succeed');
 397         System.assertNotEquals(null, responses[0].outputRecordId, 'Should return record ID');
 398     }
 399 
 400     @IsTest
 401     static void testBulkExecution() {
 402         // Test with multiple records to verify bulkification
 403         List<Account> accounts = new List<Account>();
 404         for (Integer i = 0; i < 200; i++) {
 405             accounts.add(new Account(Name = 'Test ' + i));
 406         }
 407         insert accounts;
 408 
 409         List<AccountInvocable.Request> requests = new List<AccountInvocable.Request>();
 410         for (Account acc : accounts) {
 411             AccountInvocable.Request req = new AccountInvocable.Request();
 412             req.accountId = acc.Id;
 413             requests.add(req);
 414         }
 415 
 416         Test.startTest();
 417         List<AccountInvocable.Response> responses = AccountInvocable.execute(requests);
 418         Test.stopTest();
 419 
 420         System.assertEquals(200, responses.size(), 'Should handle bulk records');
 421         for (AccountInvocable.Response res : responses) {
 422             System.assertEquals(true, res.isSuccess, 'All should succeed');
 423         }
 424     }
 425 
 426     @IsTest
 427     static void testErrorHandling() {
 428         // Test with invalid ID
 429         AccountInvocable.Request req = new AccountInvocable.Request();
 430         req.accountId = '001000000000000AAA';  // Non-existent ID
 431 
 432         Test.startTest();
 433         List<AccountInvocable.Response> responses =
 434             AccountInvocable.execute(new List<AccountInvocable.Request>{ req });
 435         Test.stopTest();
 436 
 437         System.assertEquals(false, responses[0].isSuccess, 'Should fail for invalid ID');
 438         System.assertNotEquals(null, responses[0].errorMessage, 'Should have error message');
 439     }
 440 }
 441 ```
 442 
 443 ---
 444 
 445 ## Flow XML Reference
 446 
 447 When your Invocable is deployed, Flows call it like this:
 448 
 449 ```xml
 450 <actionCalls>
 451     <name>Process_Account</name>
 452     <label>Process Account</label>
 453     <actionName>AccountProcessorInvocable</actionName>
 454     <actionType>apex</actionType>
 455     <connector>
 456         <targetReference>Next_Element</targetReference>
 457     </connector>
 458     <faultConnector>
 459         <targetReference>Error_Handler</targetReference>
 460     </faultConnector>
 461 
 462     <!-- Map Flow variable to Apex Request property -->
 463     <inputParameters>
 464         <name>accountId</name>
 465         <value>
 466             <elementReference>recordId</elementReference>
 467         </value>
 468     </inputParameters>
 469 
 470     <!-- Map Apex Response property to Flow variable -->
 471     <outputParameters>
 472         <assignToReference>isSuccess</assignToReference>
 473         <name>isSuccess</name>
 474     </outputParameters>
 475     <outputParameters>
 476         <assignToReference>errorMessage</assignToReference>
 477         <name>errorMessage</name>
 478     </outputParameters>
 479 </actionCalls>
 480 ```
 481 
 482 ---
 483 
 484 ## Cross-Skill Integration
 485 
 486 | Integration | See Also |
 487 |-------------|----------|
 488 | Flow → LWC → Apex | [triangle-pattern.md](triangle-pattern.md) |
 489 | Apex → LWC | [references/lwc-controller-patterns.md](./lwc-controller-patterns.md) (via @AuraEnabled) |
 490 | Agentforce Actions | sf-ai-agentscript skill (similar pattern for agent actions) |
 491 
 492 ---
 493 
 494 ## Template
 495 
 496 Use the template at `assets/invocable-method.cls` as a starting point.
