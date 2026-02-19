<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Patterns Deep Dive
   2 
   3 Comprehensive guide to advanced Apex patterns including Trigger Actions Framework, Flow Integration, and architectural patterns.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Trigger Actions Framework (TAF)](#trigger-actions-framework-taf)
  10 2. [Flow Integration (@InvocableMethod)](#flow-integration-invocablemethod)
  11 3. [Async Patterns](#async-patterns)
  12 4. [Service Layer Patterns](#service-layer-patterns)
  13 
  14 ---
  15 
  16 ## Trigger Actions Framework (TAF)
  17 
  18 ### ⚠️ CRITICAL PREREQUISITES
  19 
  20 **Before using TAF patterns, the target org MUST have:**
  21 
  22 1. **Trigger Actions Framework Package Installed**
  23    - GitHub: https://github.com/mitchspano/apex-trigger-actions-framework
  24    - Install via: `sf package install --package 04tKZ000000gUEFYA2 --target-org [alias] --wait 10`
  25    - Or use unlocked package from repository
  26 
  27 2. **Custom Metadata Type Records Created**
  28    - TAF triggers do NOTHING without `Trigger_Action__mdt` records!
  29    - Each trigger action class needs a corresponding CMT record
  30 
  31 **If TAF is NOT installed, use the Standard Trigger Pattern instead.**
  32 
  33 ---
  34 
  35 ### TAF Pattern (Requires Package)
  36 
  37 All triggers MUST use the Trigger Actions Framework pattern when the package is installed:
  38 
  39 **Trigger** (one per object):
  40 ```apex
  41 trigger AccountTrigger on Account (
  42     before insert, after insert,
  43     before update, after update,
  44     before delete, after delete, after undelete
  45 ) {
  46     new MetadataTriggerHandler().run();
  47 }
  48 ```
  49 
  50 **Single-Context Action Class** (one interface):
  51 ```apex
  52 public class TA_Account_SetDefaults implements TriggerAction.BeforeInsert {
  53     public void beforeInsert(List<Account> newList) {
  54         for (Account acc : newList) {
  55             if (acc.Industry == null) {
  56                 acc.Industry = 'Other';
  57             }
  58         }
  59     }
  60 }
  61 ```
  62 
  63 **Multi-Context Action Class** (multiple interfaces):
  64 ```apex
  65 public class TA_Lead_CalculateScore implements TriggerAction.BeforeInsert, TriggerAction.BeforeUpdate {
  66 
  67     // Called on new record creation
  68     public void beforeInsert(List<Lead> newList) {
  69         calculateScores(newList);
  70     }
  71 
  72     // Called on record updates
  73     public void beforeUpdate(List<Lead> newList, List<Lead> oldList) {
  74         // Only recalculate if scoring fields changed
  75         List<Lead> leadsToScore = new List<Lead>();
  76         Map<Id, Lead> oldMap = new Map<Id, Lead>(oldList);
  77 
  78         for (Lead newLead : newList) {
  79             Lead oldLead = oldMap.get(newLead.Id);
  80             if (scoringFieldsChanged(newLead, oldLead)) {
  81                 leadsToScore.add(newLead);
  82             }
  83         }
  84 
  85         if (!leadsToScore.isEmpty()) {
  86             calculateScores(leadsToScore);
  87         }
  88     }
  89 
  90     private void calculateScores(List<Lead> leads) {
  91         // Scoring logic here
  92         for (Lead l : leads) {
  93             Integer score = 0;
  94             if (l.Industry == 'Technology') score += 10;
  95             if (l.NumberOfEmployees != null && l.NumberOfEmployees > 100) score += 20;
  96             l.Score__c = score;
  97         }
  98     }
  99 
 100     private Boolean scoringFieldsChanged(Lead newLead, Lead oldLead) {
 101         return newLead.Industry != oldLead.Industry ||
 102                newLead.NumberOfEmployees != oldLead.NumberOfEmployees;
 103     }
 104 }
 105 ```
 106 
 107 ---
 108 
 109 ### ⚠️ REQUIRED: Custom Metadata Type Records
 110 
 111 **TAF triggers will NOT execute without `Trigger_Action__mdt` records!**
 112 
 113 For each trigger action class, create a Custom Metadata record:
 114 
 115 | Field | Value | Description |
 116 |-------|-------|-------------|
 117 | Label | TA Lead Calculate Score | Human-readable name |
 118 | Trigger_Action_Name__c | TA_Lead_CalculateScore | Apex class name |
 119 | Object__c | Lead | sObject API name |
 120 | Context__c | Before Insert | Trigger context |
 121 | Order__c | 1 | Execution order (lower = first) |
 122 | Active__c | true | Enable/disable without deploy |
 123 
 124 **Example Custom Metadata XML** (`Trigger_Action.TA_Lead_CalculateScore_BI.md-meta.xml`):
 125 ```xml
 126 <?xml version="1.0" encoding="UTF-8"?>
 127 <CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata">
 128     <label>TA Lead Calculate Score - Before Insert</label>
 129     <protected>false</protected>
 130     <values>
 131         <field>Apex_Class_Name__c</field>
 132         <value xsi:type="xsd:string">TA_Lead_CalculateScore</value>
 133     </values>
 134     <values>
 135         <field>Object__c</field>
 136         <value xsi:type="xsd:string">Lead</value>
 137     </values>
 138     <values>
 139         <field>Order__c</field>
 140         <value xsi:type="xsd:double">1.0</value>
 141     </values>
 142     <values>
 143         <field>Bypass_Execution__c</field>
 144         <value xsi:type="xsd:boolean">false</value>
 145     </values>
 146 </CustomMetadata>
 147 ```
 148 
 149 **NOTE**: Create separate CMT records for each context (Before Insert, Before Update, etc.)
 150 
 151 **Deploy Custom Metadata:**
 152 ```bash
 153 sf project deploy start --metadata CustomMetadata:Trigger_Action.TA_Lead_CalculateScore_BI --target-org myorg
 154 ```
 155 
 156 ---
 157 
 158 ### Standard Trigger Pattern (No Package Required)
 159 
 160 **Use this when TAF package is NOT installed in the target org:**
 161 
 162 ```apex
 163 trigger LeadTrigger on Lead (before insert, before update) {
 164 
 165     LeadScoringService scoringService = new LeadScoringService();
 166 
 167     if (Trigger.isBefore) {
 168         if (Trigger.isInsert) {
 169             scoringService.calculateScores(Trigger.new);
 170         }
 171         else if (Trigger.isUpdate) {
 172             scoringService.recalculateIfChanged(Trigger.new, Trigger.oldMap);
 173         }
 174     }
 175 }
 176 ```
 177 
 178 **Service Class:**
 179 ```apex
 180 public with sharing class LeadScoringService {
 181 
 182     public void calculateScores(List<Lead> leads) {
 183         for (Lead l : leads) {
 184             Integer score = 0;
 185             if (l.Industry == 'Technology') score += 10;
 186             if (l.NumberOfEmployees != null && l.NumberOfEmployees > 100) score += 20;
 187             l.Score__c = score;
 188         }
 189     }
 190 
 191     public void recalculateIfChanged(List<Lead> newLeads, Map<Id, Lead> oldMap) {
 192         List<Lead> leadsToScore = new List<Lead>();
 193 
 194         for (Lead newLead : newLeads) {
 195             Lead oldLead = oldMap.get(newLead.Id);
 196             if (scoringFieldsChanged(newLead, oldLead)) {
 197                 leadsToScore.add(newLead);
 198             }
 199         }
 200 
 201         if (!leadsToScore.isEmpty()) {
 202             calculateScores(leadsToScore);
 203         }
 204     }
 205 
 206     private Boolean scoringFieldsChanged(Lead newLead, Lead oldLead) {
 207         return newLead.Industry != oldLead.Industry ||
 208                newLead.NumberOfEmployees != oldLead.NumberOfEmployees;
 209     }
 210 }
 211 ```
 212 
 213 **Pros**: No external dependencies, works in any org
 214 **Cons**: Less maintainable for complex triggers, no declarative control
 215 
 216 ---
 217 
 218 ### TAF vs Standard Pattern Comparison
 219 
 220 | Feature | TAF Pattern | Standard Pattern |
 221 |---------|-------------|------------------|
 222 | **Package Required** | Yes | No |
 223 | **Complexity** | Lower (single-purpose classes) | Higher (monolithic trigger) |
 224 | **Maintainability** | High (separate files) | Medium (one trigger file) |
 225 | **Declarative Control** | Yes (CMT records) | No |
 226 | **Order Control** | Yes (Order__c field) | Manual in code |
 227 | **Bypass Mechanism** | Built-in (Active__c) | Manual Custom Setting |
 228 | **Testing** | Easy (test action classes) | Medium (test trigger + service) |
 229 
 230 **Recommendation**: Use TAF when available, fall back to Standard Pattern when TAF is not installed.
 231 
 232 ---
 233 
 234 ## Flow Integration (@InvocableMethod)
 235 
 236 Apex classes can be called from Flow using `@InvocableMethod`. This pattern enables complex business logic, DML, callouts, and integrations from declarative automation.
 237 
 238 ### Quick Reference
 239 
 240 | Annotation | Purpose |
 241 |------------|---------|
 242 | `@InvocableMethod` | Makes method callable from Flow |
 243 | `@InvocableVariable` | Exposes properties in Request/Response wrappers |
 244 
 245 ### Template
 246 
 247 Use `assets/invocable-method.cls` for the complete pattern with Request/Response wrappers.
 248 
 249 ### Basic Example
 250 
 251 ```apex
 252 public with sharing class RecordProcessor {
 253 
 254     @InvocableMethod(label='Process Record' category='Custom')
 255     public static List<Response> execute(List<Request> requests) {
 256         List<Response> responses = new List<Response>();
 257 
 258         for (Request req : requests) {
 259             Response res = new Response();
 260             res.isSuccess = true;
 261             res.processedId = req.recordId;
 262             responses.add(res);
 263         }
 264 
 265         return responses;
 266     }
 267 
 268     public class Request {
 269         @InvocableVariable(label='Record ID' required=true)
 270         public Id recordId;
 271     }
 272 
 273     public class Response {
 274         @InvocableVariable(label='Is Success')
 275         public Boolean isSuccess;
 276 
 277         @InvocableVariable(label='Processed ID')
 278         public Id processedId;
 279     }
 280 }
 281 ```
 282 
 283 ### Advanced Example with Error Handling
 284 
 285 ```apex
 286 public with sharing class AccountValidator {
 287 
 288     @InvocableMethod(
 289         label='Validate Account Data'
 290         description='Validates account data and returns validation results'
 291         category='Account Management'
 292     )
 293     public static List<ValidationResponse> validateAccounts(List<ValidationRequest> requests) {
 294         List<ValidationResponse> responses = new List<ValidationResponse>();
 295 
 296         // Collect all Account IDs for bulk query
 297         Set<Id> accountIds = new Set<Id>();
 298         for (ValidationRequest req : requests) {
 299             accountIds.add(req.accountId);
 300         }
 301 
 302         // Bulk query
 303         Map<Id, Account> accountMap = new Map<Id, Account>(
 304             [SELECT Id, Name, Industry, AnnualRevenue, Phone
 305              FROM Account
 306              WHERE Id IN :accountIds
 307              WITH USER_MODE]
 308         );
 309 
 310         // Process each request
 311         for (ValidationRequest req : requests) {
 312             ValidationResponse res = new ValidationResponse();
 313 
 314             Account acc = accountMap.get(req.accountId);
 315             if (acc == null) {
 316                 res.isValid = false;
 317                 res.errorMessage = 'Account not found';
 318                 responses.add(res);
 319                 continue;
 320             }
 321 
 322             // Validation logic
 323             List<String> errors = new List<String>();
 324 
 325             if (String.isBlank(acc.Name)) {
 326                 errors.add('Name is required');
 327             }
 328             if (String.isBlank(acc.Industry)) {
 329                 errors.add('Industry is required');
 330             }
 331             if (acc.AnnualRevenue == null || acc.AnnualRevenue <= 0) {
 332                 errors.add('Annual Revenue must be greater than 0');
 333             }
 334 
 335             res.isValid = errors.isEmpty();
 336             res.errorMessage = errors.isEmpty() ? null : String.join(errors, '; ');
 337             res.validatedAccountId = acc.Id;
 338 
 339             responses.add(res);
 340         }
 341 
 342         return responses;
 343     }
 344 
 345     public class ValidationRequest {
 346         @InvocableVariable(label='Account ID' description='ID of account to validate' required=true)
 347         public Id accountId;
 348     }
 349 
 350     public class ValidationResponse {
 351         @InvocableVariable(label='Is Valid' description='Whether account passed validation')
 352         public Boolean isValid;
 353 
 354         @InvocableVariable(label='Error Message' description='Validation error details')
 355         public String errorMessage;
 356 
 357         @InvocableVariable(label='Validated Account ID')
 358         public Id validatedAccountId;
 359     }
 360 }
 361 ```
 362 
 363 ### Best Practices
 364 
 365 1. **Always use Request/Response wrappers** - Never use primitive types directly
 366 2. **Bulkify** - Process `List<Request>` even if Flow passes single record
 367 3. **Use USER_MODE** - Respect user permissions in SOQL
 368 4. **Error handling** - Return structured errors in Response, don't throw exceptions
 369 5. **Label & Category** - Make methods discoverable in Flow Builder
 370 6. **Description** - Add descriptions to variables for clarity
 371 
 372 ### Common Patterns
 373 
 374 **Pattern 1: DML Operations**
 375 ```apex
 376 @InvocableMethod(label='Create Related Contacts')
 377 public static List<Response> createContacts(List<Request> requests) {
 378     List<Contact> contactsToInsert = new List<Contact>();
 379 
 380     for (Request req : requests) {
 381         Contact con = new Contact(
 382             AccountId = req.accountId,
 383             LastName = req.lastName,
 384             Email = req.email
 385         );
 386         contactsToInsert.add(con);
 387     }
 388 
 389     insert contactsToInsert;
 390 
 391     // Return results
 392     List<Response> responses = new List<Response>();
 393     for (Contact con : contactsToInsert) {
 394         Response res = new Response();
 395         res.contactId = con.Id;
 396         responses.add(res);
 397     }
 398     return responses;
 399 }
 400 ```
 401 
 402 **Pattern 2: External Callouts**
 403 ```apex
 404 @InvocableMethod(label='Send to External System')
 405 public static List<Response> sendData(List<Request> requests) {
 406     // Note: Callouts in Flow require @future or Queueable
 407     // This is a sync example - for async, enqueue from here
 408 
 409     List<Response> responses = new List<Response>();
 410     for (Request req : requests) {
 411         HttpRequest request = new HttpRequest();
 412         request.setEndpoint('callout:MyNamedCredential/api');
 413         request.setMethod('POST');
 414         request.setBody(JSON.serialize(req));
 415 
 416         Http http = new Http();
 417         HttpResponse response = http.send(request);
 418 
 419         Response res = new Response();
 420         res.statusCode = response.getStatusCode();
 421         res.success = response.getStatusCode() == 200;
 422         responses.add(res);
 423     }
 424     return responses;
 425 }
 426 ```
 427 
 428 **See Also**:
 429 - [references/flow-integration.md](../references/flow-integration.md) - Complete @InvocableMethod guide
 430 - [references/triangle-pattern.md](../references/triangle-pattern.md) - Flow-LWC-Apex triangle (Apex perspective)
 431 
 432 ---
 433 
 434 ## Async Patterns
 435 
 436 ### Decision Matrix
 437 
 438 | Scenario | Use | Pros | Cons |
 439 |----------|-----|------|------|
 440 | Simple callout, fire-and-forget | `@future(callout=true)` | Simple, built-in | No return value, no chaining |
 441 | Complex logic, needs chaining | `Queueable` | Return ID, chain jobs, complex types | More code |
 442 | Process millions of records | `Batch Apex` | Handles huge volumes | Complex, overhead |
 443 | Scheduled/recurring job | `Schedulable` | Cron-like scheduling | Requires separate Queueable/Batch |
 444 | Post-queueable cleanup | `Queueable Finalizer` | Guaranteed execution | Only for Queueable |
 445 
 446 ### @future Pattern
 447 
 448 ```apex
 449 public class CalloutService {
 450 
 451     @future(callout=true)
 452     public static void sendDataToExternalSystem(Set<Id> recordIds) {
 453         // Cannot pass complex objects, only primitives
 454         List<Account> accounts = [SELECT Id, Name FROM Account WHERE Id IN :recordIds];
 455 
 456         HttpRequest req = new HttpRequest();
 457         req.setEndpoint('callout:MyNamedCredential/api');
 458         req.setMethod('POST');
 459         req.setBody(JSON.serialize(accounts));
 460 
 461         Http http = new Http();
 462         HttpResponse res = http.send(req);
 463 
 464         // Process response (no return to caller)
 465         System.debug('Response: ' + res.getBody());
 466     }
 467 }
 468 ```
 469 
 470 ### Queueable Pattern
 471 
 472 ```apex
 473 public class AccountProcessor implements Queueable {
 474 
 475     private List<Id> accountIds;
 476 
 477     public AccountProcessor(List<Id> accountIds) {
 478         this.accountIds = accountIds;
 479     }
 480 
 481     public void execute(QueueableContext context) {
 482         List<Account> accounts = [SELECT Id, Name, Industry FROM Account WHERE Id IN :accountIds];
 483 
 484         for (Account acc : accounts) {
 485             acc.Description = 'Processed on ' + System.now();
 486         }
 487 
 488         update accounts;
 489 
 490         // Chain another job if needed
 491         if (!Test.isRunningTest() && accountIds.size() > 200) {
 492             // Process next batch
 493             List<Id> nextBatch = getNextBatch();
 494             if (!nextBatch.isEmpty()) {
 495                 System.enqueueJob(new AccountProcessor(nextBatch));
 496             }
 497         }
 498     }
 499 
 500     private List<Id> getNextBatch() {
 501         // Logic to get next batch
 502         return new List<Id>();
 503     }
 504 }
 505 
 506 // Usage:
 507 System.enqueueJob(new AccountProcessor(accountIds));
 508 ```
 509 
 510 ### Queueable with Finalizer
 511 
 512 ```apex
 513 public class DataSyncQueueable implements Queueable {
 514 
 515     public void execute(QueueableContext context) {
 516         // Attach finalizer for cleanup
 517         System.attachFinalizer(new DataSyncFinalizer(context.getJobId()));
 518 
 519         // Main logic
 520         try {
 521             // Process data
 522             Http http = new Http();
 523             HttpRequest req = new HttpRequest();
 524             req.setEndpoint('callout:ExternalSystem/sync');
 525             req.setMethod('POST');
 526 
 527             HttpResponse res = http.send(req);
 528 
 529             if (res.getStatusCode() != 200) {
 530                 throw new CalloutException('Sync failed: ' + res.getBody());
 531             }
 532         } catch (Exception e) {
 533             // Log error
 534             System.debug(LoggingLevel.ERROR, 'Sync failed: ' + e.getMessage());
 535             throw e; // Finalizer will still run
 536         }
 537     }
 538 }
 539 
 540 public class DataSyncFinalizer implements Finalizer {
 541 
 542     private Id jobId;
 543 
 544     public DataSyncFinalizer(Id jobId) {
 545         this.jobId = jobId;
 546     }
 547 
 548     public void execute(FinalizerContext context) {
 549         // This ALWAYS runs, even if job fails
 550 
 551         // Log status
 552         insert new Sync_Log__c(
 553             Job_Id__c = String.valueOf(jobId),
 554             Status__c = context.getResult() == ParentJobResult.SUCCESS ? 'Success' : 'Failed',
 555             Error__c = context.getException()?.getMessage()
 556         );
 557     }
 558 }
 559 ```
 560 
 561 ### Batch Apex Pattern
 562 
 563 ```apex
 564 public class AccountBatchProcessor implements Database.Batchable<SObject> {
 565 
 566     // Start: Define query
 567     public Database.QueryLocator start(Database.BatchableContext context) {
 568         return Database.getQueryLocator([
 569             SELECT Id, Name, Industry, AnnualRevenue
 570             FROM Account
 571             WHERE Industry = 'Technology'
 572         ]);
 573     }
 574 
 575     // Execute: Process each batch (default 200 records)
 576     public void execute(Database.BatchableContext context, List<Account> scope) {
 577         for (Account acc : scope) {
 578             acc.Description = 'Processed by batch on ' + System.now();
 579         }
 580 
 581         update scope;
 582     }
 583 
 584     // Finish: Post-processing
 585     public void finish(Database.BatchableContext context) {
 586         // Send email, log results, chain another batch
 587         AsyncApexJob job = [
 588             SELECT Id, Status, NumberOfErrors, JobItemsProcessed, TotalJobItems
 589             FROM AsyncApexJob
 590             WHERE Id = :context.getJobId()
 591         ];
 592 
 593         System.debug('Batch completed: ' + job.TotalJobItems + ' items processed');
 594     }
 595 }
 596 
 597 // Usage:
 598 Database.executeBatch(new AccountBatchProcessor(), 200); // Batch size
 599 ```
 600 
 601 ---
 602 
 603 ## Service Layer Patterns
 604 
 605 ### Service Class Structure
 606 
 607 ```apex
 608 public with sharing class AccountService {
 609 
 610     // Public interface methods
 611     public static List<Account> createAccounts(List<AccountRequest> requests) {
 612         validateRequests(requests);
 613 
 614         List<Account> accounts = buildAccounts(requests);
 615         insert accounts;
 616 
 617         // Post-processing
 618         handlePostCreation(accounts);
 619 
 620         return accounts;
 621     }
 622 
 623     // Private helper methods
 624     private static void validateRequests(List<AccountRequest> requests) {
 625         for (AccountRequest req : requests) {
 626             if (String.isBlank(req.name)) {
 627                 throw new IllegalArgumentException('Account name is required');
 628             }
 629         }
 630     }
 631 
 632     private static List<Account> buildAccounts(List<AccountRequest> requests) {
 633         List<Account> accounts = new List<Account>();
 634         for (AccountRequest req : requests) {
 635             accounts.add(new Account(
 636                 Name = req.name,
 637                 Industry = req.industry
 638             ));
 639         }
 640         return accounts;
 641     }
 642 
 643     private static void handlePostCreation(List<Account> accounts) {
 644         // Create related records, send notifications, etc.
 645     }
 646 
 647     // Inner class for structured requests
 648     public class AccountRequest {
 649         public String name;
 650         public String industry;
 651     }
 652 }
 653 ```
 654 
 655 ### Selector Pattern (Data Access Layer)
 656 
 657 ```apex
 658 public inherited sharing class AccountSelector {
 659 
 660     public static List<Account> selectById(Set<Id> accountIds) {
 661         return [
 662             SELECT Id, Name, Industry, AnnualRevenue, Type
 663             FROM Account
 664             WHERE Id IN :accountIds
 665             WITH USER_MODE
 666         ];
 667     }
 668 
 669     public static List<Account> selectByIndustry(String industry) {
 670         return [
 671             SELECT Id, Name, Industry, AnnualRevenue
 672             FROM Account
 673             WHERE Industry = :industry
 674             WITH USER_MODE
 675             LIMIT 200
 676         ];
 677     }
 678 
 679     public static Map<Id, Account> selectByIdWithContacts(Set<Id> accountIds) {
 680         return new Map<Id, Account>([
 681             SELECT Id, Name,
 682                    (SELECT Id, Name, Email FROM Contacts)
 683             FROM Account
 684             WHERE Id IN :accountIds
 685             WITH USER_MODE
 686         ]);
 687     }
 688 }
 689 ```
 690 
 691 **Benefits**:
 692 - Centralized SOQL queries
 693 - Reusable across multiple classes
 694 - Easier to test (mock Selector)
 695 - Consistent field selection
 696 
 697 ---
 698 
 699 ## Reference
 700 
 701 **Full Documentation**: See `references/` folder for comprehensive guides:
 702 - `trigger-actions-framework.md` - TAF setup and advanced patterns
 703 - `design-patterns.md` - 12 Apex design patterns
 704 - `flow-integration.md` - Complete @InvocableMethod guide
 705 - `triangle-pattern.md` - Flow-LWC-Apex integration
 706 
 707 **Back to Main**: [SKILL.md](../SKILL.md)
