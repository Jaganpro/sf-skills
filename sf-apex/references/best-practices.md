<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Best Practices Reference
   2 
   3 ## 1. Bulkification
   4 
   5 ### The Problem
   6 Apex triggers can process up to 200 records at once. Code that works for single records often fails at scale.
   7 
   8 ### Anti-Pattern
   9 ```apex
  10 // BAD: SOQL in loop - will hit 100 query limit
  11 for (Account acc : Trigger.new) {
  12     Contact c = [SELECT Id FROM Contact WHERE AccountId = :acc.Id LIMIT 1];
  13 }
  14 ```
  15 
  16 ### Best Practice
  17 ```apex
  18 // GOOD: Query once, use Map for lookup
  19 Set<Id> accountIds = new Map<Id, Account>(Trigger.new).keySet();
  20 Map<Id, Contact> contactsByAccountId = new Map<Id, Contact>();
  21 for (Contact c : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
  22     contactsByAccountId.put(c.AccountId, c);
  23 }
  24 
  25 for (Account acc : Trigger.new) {
  26     Contact c = contactsByAccountId.get(acc.Id);
  27 }
  28 ```
  29 
  30 ### DML Bulkification
  31 ```apex
  32 // BAD: DML in loop
  33 for (Account acc : accounts) {
  34     acc.Status__c = 'Active';
  35     update acc;
  36 }
  37 
  38 // GOOD: Collect and update once
  39 List<Account> toUpdate = new List<Account>();
  40 for (Account acc : accounts) {
  41     acc.Status__c = 'Active';
  42     toUpdate.add(acc);
  43 }
  44 update toUpdate;
  45 ```
  46 
  47 ### Test with Bulk Data
  48 ```apex
  49 @isTest
  50 static void testBulkOperation() {
  51     List<Account> accounts = new List<Account>();
  52     for (Integer i = 0; i < 251; i++) {  // 251 to span two trigger batches
  53         accounts.add(new Account(Name = 'Test ' + i));
  54     }
  55 
  56     Test.startTest();
  57     insert accounts;
  58     Test.stopTest();
  59 
  60     Assert.areEqual(251, [SELECT COUNT() FROM Account]);
  61 }
  62 ```
  63 
  64 ---
  65 
  66 ## 2. Collections Best Practices
  67 
  68 ### Use Map Constructor for ID Extraction
  69 ```apex
  70 // BAD: Loop to get IDs
  71 Set<Id> accountIds = new Set<Id>();
  72 for (Account acc : accounts) {
  73     accountIds.add(acc.Id);
  74 }
  75 
  76 // GOOD: Map constructor
  77 Set<Id> accountIds = new Map<Id, Account>(accounts).keySet();
  78 ```
  79 
  80 ### Use Maps for Lookups
  81 ```apex
  82 // Build lookup map
  83 Map<Id, Account> accountsById = new Map<Id, Account>(accounts);
  84 
  85 // O(1) lookup instead of O(n) loop
  86 Account acc = accountsById.get(someId);
  87 ```
  88 
  89 ### Collection Naming Convention
  90 ```apex
  91 List<Account> accounts;              // Plural noun
  92 Set<Id> accountIds;                  // Type suffix
  93 Map<Id, Account> accountsById;       // Key description
  94 Map<String, List<Contact>> contactsByEmail;  // Nested collection
  95 ```
  96 
  97 ---
  98 
  99 ## 3. SOQL Best Practices
 100 
 101 ### Always Use Selective Queries
 102 ```apex
 103 // GOOD: Filter on indexed fields
 104 [SELECT Id FROM Account WHERE Id = :recordId]
 105 [SELECT Id FROM Account WHERE Name = :name]
 106 [SELECT Id FROM Account WHERE CreatedDate > :startDate]
 107 [SELECT Id FROM Contact WHERE Email = :email]  // If External ID
 108 
 109 // BAD: Non-selective patterns
 110 [SELECT Id FROM Account WHERE Custom_Field__c != null]  // != null
 111 [SELECT Id FROM Account WHERE Name LIKE '%test%']       // Leading wildcard
 112 [SELECT Id FROM Account WHERE CALENDAR_YEAR(CreatedDate) = 2025]  // Function
 113 ```
 114 
 115 ### Use Bind Variables (Prevent SOQL Injection)
 116 ```apex
 117 // BAD: String concatenation (SOQL injection risk)
 118 String query = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';
 119 
 120 // GOOD: Bind variable
 121 String query = 'SELECT Id FROM Account WHERE Name = :userInput';
 122 List<Account> accounts = Database.query(query);
 123 ```
 124 
 125 ### Use USER_MODE for Security
 126 ```apex
 127 // Enforces CRUD/FLS automatically
 128 List<Account> accounts = [SELECT Id, Name FROM Account WITH USER_MODE];
 129 
 130 // For Database methods
 131 Database.query(query, AccessLevel.USER_MODE);
 132 Database.insert(records, AccessLevel.USER_MODE);
 133 ```
 134 
 135 ### SOQL For Loops for Large Data
 136 ```apex
 137 // Memory efficient - processes 200 records at a time
 138 for (Account acc : [SELECT Id, Name FROM Account]) {
 139     // Process each account
 140 }
 141 
 142 // Or batch processing
 143 for (List<Account> batch : [SELECT Id, Name FROM Account]) {
 144     // Process batch of 200
 145 }
 146 ```
 147 
 148 ---
 149 
 150 ## 4. Governor Limits Awareness
 151 
 152 ### Key Limits
 153 | Limit | Synchronous | Asynchronous |
 154 |-------|-------------|--------------|
 155 | SOQL Queries | 100 | 200 |
 156 | DML Statements | 150 | 150 |
 157 | CPU Time | 10,000 ms | 60,000 ms |
 158 | Heap Size | 6 MB | 12 MB |
 159 | Callouts | 100 | 100 |
 160 
 161 ### Monitor Limits
 162 ```apex
 163 System.debug('SOQL: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
 164 System.debug('DML: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
 165 System.debug('CPU: ' + Limits.getCpuTime() + '/' + Limits.getLimitCpuTime());
 166 System.debug('Heap: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize());
 167 ```
 168 
 169 ### Heap Optimization
 170 ```apex
 171 // BAD: Class-level variable holds large data
 172 public class BadExample {
 173     private List<Account> allAccounts;  // Stays in memory
 174 }
 175 
 176 // GOOD: Let variables go out of scope
 177 public class GoodExample {
 178     public void process() {
 179         List<Account> accounts = [SELECT Id FROM Account];
 180         // Process...
 181     }  // accounts released here
 182 }
 183 ```
 184 
 185 ---
 186 
 187 ## 5. Null Safety
 188 
 189 ### Null Coalescing Operator (??)
 190 ```apex
 191 // Old way
 192 String value = input != null ? input : 'default';
 193 
 194 // New way (API 60+)
 195 String value = input ?? 'default';
 196 
 197 // Chaining
 198 String value = firstChoice ?? secondChoice ?? 'default';
 199 ```
 200 
 201 ### Safe Navigation Operator (?.)
 202 ```apex
 203 // Old way
 204 String accountName = null;
 205 if (contact != null && contact.Account != null) {
 206     accountName = contact.Account.Name;
 207 }
 208 
 209 // New way
 210 String accountName = contact?.Account?.Name;
 211 
 212 // With null coalescing
 213 String accountName = contact?.Account?.Name ?? 'Unknown';
 214 ```
 215 
 216 ### Null-Safe Collection Access
 217 ```apex
 218 // Check before accessing
 219 if (myMap != null && myMap.containsKey(key)) {
 220     return myMap.get(key);
 221 }
 222 
 223 // Or use getOrDefault pattern
 224 public static Object getOrDefault(Map<Id, Object> m, Id key, Object defaultVal) {
 225     return m?.containsKey(key) == true ? m.get(key) : defaultVal;
 226 }
 227 ```
 228 
 229 ---
 230 
 231 ## 6. Error Handling
 232 
 233 ### Catch Specific Exceptions
 234 ```apex
 235 try {
 236     insert accounts;
 237 } catch (DmlException e) {
 238     // Handle DML-specific errors
 239     for (Integer i = 0; i < e.getNumDml(); i++) {
 240         System.debug('Field: ' + e.getDmlFieldNames(i));
 241         System.debug('Message: ' + e.getDmlMessage(i));
 242     }
 243 } catch (QueryException e) {
 244     // Handle query errors
 245 } catch (Exception e) {
 246     // Generic fallback - log and rethrow
 247     System.debug(LoggingLevel.ERROR, e.getMessage());
 248     throw e;
 249 }
 250 ```
 251 
 252 ### Custom Exceptions
 253 ```apex
 254 public class InsufficientInventoryException extends Exception {}
 255 
 256 public void processOrder(Order ord) {
 257     if (ord.Quantity__c > availableStock) {
 258         throw new InsufficientInventoryException(
 259             'Requested: ' + ord.Quantity__c + ', Available: ' + availableStock
 260         );
 261     }
 262 }
 263 ```
 264 
 265 ### AuraHandledException for LWC
 266 ```apex
 267 @AuraEnabled
 268 public static void processRecord(Id recordId) {
 269     try {
 270         // Business logic
 271     } catch (Exception e) {
 272         throw new AuraHandledException(e.getMessage());
 273     }
 274 }
 275 ```
 276 
 277 ---
 278 
 279 ## 7. Async Apex Selection
 280 
 281 ### @future
 282 ```apex
 283 // Simple, fire-and-forget
 284 @future(callout=true)
 285 public static void makeCallout(Set<Id> recordIds) {
 286     // Cannot return value, cannot chain
 287 }
 288 ```
 289 
 290 ### Queueable
 291 ```apex
 292 // Complex logic, can chain, can pass complex types
 293 public class ProcessRecordsQueueable implements Queueable {
 294     private List<Account> accounts;
 295 
 296     public ProcessRecordsQueueable(List<Account> accounts) {
 297         this.accounts = accounts;
 298     }
 299 
 300     public void execute(QueueableContext context) {
 301         // Process accounts
 302 
 303         // Chain next job if needed
 304         if (moreWork) {
 305             System.enqueueJob(new ProcessRecordsQueueable(nextBatch));
 306         }
 307     }
 308 }
 309 ```
 310 
 311 ### Batch Apex
 312 ```apex
 313 // Large data volumes (millions of records)
 314 public class ProcessAccountsBatch implements Database.Batchable<SObject> {
 315     public Database.QueryLocator start(Database.BatchableContext bc) {
 316         return Database.getQueryLocator('SELECT Id FROM Account');
 317     }
 318 
 319     public void execute(Database.BatchableContext bc, List<Account> scope) {
 320         // Process batch (default 200 records)
 321     }
 322 
 323     public void finish(Database.BatchableContext bc) {
 324         // Cleanup, notifications, chain next batch
 325     }
 326 }
 327 ```
 328 
 329 ---
 330 
 331 ## 8. Platform Cache
 332 
 333 ### When to Use
 334 - Frequently accessed, rarely changed data
 335 - Expensive calculations
 336 - Cross-transaction data sharing
 337 
 338 ### Implementation
 339 ```apex
 340 // Check cache first
 341 Account acc = (Account)Cache.Org.get('local.AccountCache.' + accountId);
 342 if (acc == null) {
 343     acc = [SELECT Id, Name FROM Account WHERE Id = :accountId];
 344     Cache.Org.put('local.AccountCache.' + accountId, acc, 3600);  // 1 hour TTL
 345 }
 346 return acc;
 347 ```
 348 
 349 ### Always Handle Cache Misses
 350 ```apex
 351 // Cache can be evicted at any time
 352 Object cachedValue = Cache.Org.get(key);
 353 if (cachedValue == null) {
 354     // Rebuild from source
 355 }
 356 ```
 357 
 358 ---
 359 
 360 ## 9. Static Variables for Transaction Caching
 361 
 362 ### Prevent Duplicate Queries
 363 ```apex
 364 public class AccountService {
 365     private static Map<Id, Account> accountCache;
 366 
 367     public static Account getAccount(Id accountId) {
 368         if (accountCache == null) {
 369             accountCache = new Map<Id, Account>();
 370         }
 371 
 372         if (!accountCache.containsKey(accountId)) {
 373             accountCache.put(accountId, [SELECT Id, Name FROM Account WHERE Id = :accountId]);
 374         }
 375 
 376         return accountCache.get(accountId);
 377     }
 378 }
 379 ```
 380 
 381 ### Recursion Prevention
 382 ```apex
 383 public class TriggerHelper {
 384     private static Set<Id> processedIds = new Set<Id>();
 385 
 386     public static Boolean hasProcessed(Id recordId) {
 387         if (processedIds.contains(recordId)) {
 388             return true;
 389         }
 390         processedIds.add(recordId);
 391         return false;
 392     }
 393 }
 394 ```
 395 
 396 ---
 397 
 398 ## 10. Guard Clauses & Fail-Fast
 399 
 400 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
 401 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
 402 
 403 ### The Problem
 404 
 405 Deeply nested validation leads to hard-to-read code where business logic is buried.
 406 
 407 ### Anti-Pattern
 408 ```apex
 409 // BAD: Deep nesting obscures business logic
 410 public void processAccountUpdate(Account oldAccount, Account newAccount) {
 411     if (newAccount != null) {
 412         if (oldAccount != null) {
 413             if (newAccount.Id != null) {
 414                 if (hasFieldChanged(oldAccount, newAccount)) {
 415                     if (UserInfo.getUserType() == 'Standard') {
 416                         // Actual business logic buried 5 levels deep
 417                         performSync(newAccount);
 418                         sendNotification(newAccount);
 419                     }
 420                 }
 421             }
 422         }
 423     }
 424 }
 425 ```
 426 
 427 ### Best Practice: Guard Clauses
 428 ```apex
 429 // GOOD: Guard clauses at the top, exit early
 430 public void processAccountUpdate(Account oldAccount, Account newAccount) {
 431     // Guard clauses - validate preconditions and exit fast
 432     if (newAccount == null) return;
 433     if (oldAccount == null) return;
 434     if (newAccount.Id == null) return;
 435     if (!hasFieldChanged(oldAccount, newAccount)) return;
 436     if (UserInfo.getUserType() != 'Standard') return;
 437 
 438     // Main logic is now at the top level, clearly visible
 439     performSync(newAccount);
 440     sendNotification(newAccount);
 441 }
 442 ```
 443 
 444 ### Parameter Validation with Exceptions
 445 
 446 For public APIs, throw exceptions for invalid input:
 447 
 448 ```apex
 449 public Database.LeadConvertResult convertLead(Id leadId, Id accountId) {
 450     // Guard clauses with exceptions for public API
 451     if (leadId == null) {
 452         throw new IllegalArgumentException('Lead ID cannot be null');
 453     }
 454 
 455     if (leadId.getSObjectType() != Lead.SObjectType) {
 456         throw new IllegalArgumentException('Expected Lead ID, received: ' + leadId.getSObjectType());
 457     }
 458 
 459     Lead leadRecord = queryLead(leadId);
 460 
 461     if (leadRecord == null) {
 462         throw new IllegalArgumentException('Lead not found: ' + leadId);
 463     }
 464 
 465     if (leadRecord.IsConverted) {
 466         throw new IllegalArgumentException('Lead is already converted: ' + leadId);
 467     }
 468 
 469     // Main conversion logic
 470     return performConversion(leadRecord, accountId);
 471 }
 472 ```
 473 
 474 ### When to Use Each Pattern
 475 
 476 | Scenario | Pattern | Example |
 477 |----------|---------|---------|
 478 | Private/internal methods | `return` early | `if (list == null) return;` |
 479 | Public API | `throw Exception` | `throw new IllegalArgumentException(...)` |
 480 | Trigger handlers | `return` for skip | `if (records.isEmpty()) return;` |
 481 | Validation service | `addError()` | `record.addError('...')` |
 482 
 483 ---
 484 
 485 ## 11. Comment Best Practices
 486 
 487 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
 488 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
 489 
 490 ### Core Principle
 491 
 492 Comments should explain **"why"**, not **"what"**. The code itself should communicate the "what".
 493 
 494 ### When Comments Add Value
 495 
 496 ```apex
 497 // GOOD: Explains business decision
 498 // Salesforce processes triggers in batches of 200. We use 201 to ensure
 499 // our code handles batch boundaries correctly during testing.
 500 private static final Integer BULK_TEST_SIZE = 201;
 501 
 502 // GOOD: Documents platform limitation
 503 // Safe navigation (?.) doesn't work in formulas - must use IF(ISBLANK())
 504 // See Known Issue W-12345678
 505 
 506 // GOOD: References external documentation
 507 // Algorithm based on RFC 7519 (JSON Web Token specification)
 508 // See: https://tools.ietf.org/html/rfc7519#section-4.1
 509 
 510 // GOOD: Explains non-obvious optimization
 511 // DML on empty list still consumes ~10x CPU. Always check isEmpty().
 512 if (!accountsToUpdate.isEmpty()) {
 513     update accountsToUpdate;
 514 }
 515 ```
 516 
 517 ### Comment Anti-Patterns
 518 
 519 ```apex
 520 // BAD: Restates what code clearly shows
 521 Integer count = 0;  // Initialize count to zero
 522 
 523 // BAD: Version history belongs in Git
 524 // Modified by John on 2024-01-15 to add validation
 525 // Modified by Jane on 2024-02-20 to fix bug
 526 
 527 // BAD: Commented-out code (delete it!)
 528 // if (account.Type == 'Partner') {
 529 //     processPartner(account);
 530 // }
 531 
 532 // BAD: TODO without owner or ticket
 533 // TODO: fix this later
 534 
 535 // GOOD: TODO with context
 536 // TODO(JIRA-1234): Refactor to use Platform Events after Spring '26 release
 537 ```
 538 
 539 ### Self-Documenting Code
 540 
 541 Instead of comments, make code self-explanatory:
 542 
 543 ```apex
 544 // BAD: Needs comment to explain
 545 if (acc.AnnualRevenue > 1000000 && acc.Type == 'Enterprise' && acc.Industry == 'Technology') {
 546     // Process strategic tech accounts
 547 }
 548 
 549 // GOOD: Code explains itself
 550 Boolean isStrategicTechAccount =
 551     acc.AnnualRevenue > 1000000 &&
 552     acc.Type == 'Enterprise' &&
 553     acc.Industry == 'Technology';
 554 
 555 if (isStrategicTechAccount) {
 556     processStrategicAccount(acc);
 557 }
 558 ```
 559 
 560 ---
 561 
 562 ## 12. DML Performance Pattern
 563 
 564 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
 565 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
 566 
 567 ### The Problem
 568 
 569 DML operations on empty collections still consume significant CPU time (~10x more than checking isEmpty first).
 570 
 571 ### Anti-Pattern
 572 ```apex
 573 // BAD: DML on potentially empty list
 574 List<Account> accountsToUpdate = new List<Account>();
 575 // ... conditional logic that might not add anything ...
 576 update accountsToUpdate;  // Wastes CPU even if empty
 577 ```
 578 
 579 ### Best Practice
 580 ```apex
 581 // GOOD: Always check isEmpty() before DML
 582 if (!accountsToUpdate.isEmpty()) {
 583     update accountsToUpdate;
 584 }
 585 ```
 586 
 587 ### SafeDML Wrapper
 588 
 589 Create a utility class to enforce this pattern:
 590 
 591 ```apex
 592 public class SafeDML {
 593 
 594     public static Database.SaveResult[] safeInsert(List<SObject> records) {
 595         if (records == null || records.isEmpty()) {
 596             return new List<Database.SaveResult>();
 597         }
 598         return Database.insert(records, false);
 599     }
 600 
 601     public static Database.SaveResult[] safeUpdate(List<SObject> records) {
 602         if (records == null || records.isEmpty()) {
 603             return new List<Database.SaveResult>();
 604         }
 605         return Database.update(records, false);
 606     }
 607 
 608     public static Database.DeleteResult[] safeDelete(List<SObject> records) {
 609         if (records == null || records.isEmpty()) {
 610             return new List<Database.DeleteResult>();
 611         }
 612         return Database.delete(records, false);
 613     }
 614 
 615     public static Database.UpsertResult[] safeUpsert(
 616         List<SObject> records,
 617         Schema.SObjectField externalIdField
 618     ) {
 619         if (records == null || records.isEmpty()) {
 620             return new List<Database.UpsertResult>();
 621         }
 622         return Database.upsert(records, externalIdField, false);
 623     }
 624 }
 625 ```
 626 
 627 ### Usage
 628 ```apex
 629 // Clean, safe DML operations
 630 SafeDML.safeInsert(newAccounts);
 631 SafeDML.safeUpdate(modifiedContacts);
 632 SafeDML.safeDelete(obsoleteRecords);
 633 ```
 634 
 635 ### Performance Impact
 636 
 637 | Scenario | CPU Time |
 638 |----------|----------|
 639 | `update emptyList` | ~100-200 CPU ms |
 640 | `if (!empty) update` | ~10-20 CPU ms |
 641 | **Savings** | **~10x improvement** |
 642 
 643 In triggers processing many records, this optimization compounds significantly.
