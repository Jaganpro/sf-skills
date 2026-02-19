<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Bulkification Guide
   2 
   3 Comprehensive guide to writing bulk-safe Apex code, understanding governor limits, and optimizing collection handling.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Governor Limits Overview](#governor-limits-overview)
  10 2. [The Golden Rules](#the-golden-rules)
  11 3. [Common Bulkification Patterns](#common-bulkification-patterns)
  12 4. [Collection Handling Best Practices](#collection-handling-best-practices)
  13 5. [Monitoring and Debugging](#monitoring-and-debugging)
  14 6. [Bulk Testing](#bulk-testing)
  15 
  16 ---
  17 
  18 ## Governor Limits Overview
  19 
  20 Salesforce enforces per-transaction limits to ensure multi-tenant platform stability.
  21 
  22 ### Critical Limits (Synchronous Context)
  23 
  24 | Resource | Limit | Notes |
  25 |----------|-------|-------|
  26 | **SOQL Queries** | 100 | Includes parent-child queries |
  27 | **SOQL Query Rows** | 50,000 | Total rows retrieved |
  28 | **DML Statements** | 150 | insert, update, delete, undelete operations |
  29 | **DML Rows** | 10,000 | Total records per transaction |
  30 | **CPU Time** | 10,000ms | Actual CPU time (not wall clock) |
  31 | **Heap Size** | 6 MB | Memory used by variables |
  32 | **Callouts** | 100 | HTTP requests |
  33 | **Callout Time** | 120 seconds | Total time for all callouts |
  34 
  35 ### Asynchronous Limits (Future, Batch, Queueable)
  36 
  37 | Resource | Limit | Notes |
  38 |----------|-------|-------|
  39 | **SOQL Queries** | 200 | Double synchronous |
  40 | **SOQL Query Rows** | 50,000 | Same as sync |
  41 | **DML Statements** | 150 | Same as sync |
  42 | **DML Rows** | 10,000 | Same as sync |
  43 | **CPU Time** | 60,000ms | 6x synchronous |
  44 | **Heap Size** | 12 MB | 2x synchronous |
  45 
  46 **Key Insight**: Async has more SOQL queries and CPU time, but DML limits are the same.
  47 
  48 ---
  49 
  50 ## The Golden Rules
  51 
  52 ### Rule 1: Never Query Inside a Loop
  53 
  54 **❌ BAD - Hits SOQL limit at 100 accounts:**
  55 ```apex
  56 for (Account acc : accounts) {
  57     List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
  58     // Process contacts
  59 }
  60 ```
  61 
  62 **✅ GOOD - Single query handles unlimited accounts:**
  63 ```apex
  64 // Step 1: Collect all Account IDs
  65 Set<Id> accountIds = new Set<Id>();
  66 for (Account acc : accounts) {
  67     accountIds.add(acc.Id);
  68 }
  69 
  70 // Step 2: Query ONCE
  71 Map<Id, List<Contact>> contactsByAccountId = new Map<Id, List<Contact>>();
  72 for (Contact con : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
  73     if (!contactsByAccountId.containsKey(con.AccountId)) {
  74         contactsByAccountId.put(con.AccountId, new List<Contact>());
  75     }
  76     contactsByAccountId.get(con.AccountId).add(con);
  77 }
  78 
  79 // Step 3: Loop and process
  80 for (Account acc : accounts) {
  81     List<Contact> contacts = contactsByAccountId.get(acc.Id);
  82     if (contacts != null) {
  83         // Process contacts
  84     }
  85 }
  86 ```
  87 
  88 **Pattern**: Collect IDs → Query with `IN` clause → Build Map → Loop.
  89 
  90 ---
  91 
  92 ### Rule 2: Never DML Inside a Loop
  93 
  94 **❌ BAD - Hits DML limit at 150 accounts:**
  95 ```apex
  96 for (Account acc : accounts) {
  97     acc.Industry = 'Technology';
  98     update acc;  // DML inside loop!
  99 }
 100 ```
 101 
 102 **✅ GOOD - Single DML handles 10,000 accounts:**
 103 ```apex
 104 for (Account acc : accounts) {
 105     acc.Industry = 'Technology';
 106 }
 107 update accounts;  // DML after loop
 108 ```
 109 
 110 **Pattern**: Modify in loop → DML after loop.
 111 
 112 ---
 113 
 114 ### Rule 3: Use Collections Efficiently
 115 
 116 **❌ BAD - Multiple queries for related data:**
 117 ```apex
 118 for (Account acc : accounts) {
 119     List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
 120     List<Opportunity> opps = [SELECT Id FROM Opportunity WHERE AccountId = :acc.Id];
 121 }
 122 ```
 123 
 124 **✅ GOOD - Single query with subqueries:**
 125 ```apex
 126 Map<Id, Account> accountsWithRelated = new Map<Id, Account>([
 127     SELECT Id, Name,
 128            (SELECT Id FROM Contacts),
 129            (SELECT Id FROM Opportunities)
 130     FROM Account
 131     WHERE Id IN :accountIds
 132 ]);
 133 
 134 for (Account acc : accountsWithRelated.values()) {
 135     List<Contact> contacts = acc.Contacts;
 136     List<Opportunity> opps = acc.Opportunities;
 137 }
 138 ```
 139 
 140 **Pattern**: Use relationship queries to fetch related records in one SOQL.
 141 
 142 ---
 143 
 144 ## Common Bulkification Patterns
 145 
 146 ### Pattern 1: Map-Based Lookup
 147 
 148 **Use Case**: Need to lookup related records for each item in a loop.
 149 
 150 ```apex
 151 public static void updateAccountIndustry(List<Contact> contacts) {
 152     // Step 1: Collect Account IDs
 153     Set<Id> accountIds = new Set<Id>();
 154     for (Contact con : contacts) {
 155         if (con.AccountId != null) {
 156             accountIds.add(con.AccountId);
 157         }
 158     }
 159 
 160     // Step 2: Query Accounts into Map
 161     Map<Id, Account> accountMap = new Map<Id, Account>([
 162         SELECT Id, Industry
 163         FROM Account
 164         WHERE Id IN :accountIds
 165     ]);
 166 
 167     // Step 3: Loop and lookup
 168     for (Contact con : contacts) {
 169         Account acc = accountMap.get(con.AccountId);
 170         if (acc != null) {
 171             con.Description = 'Account Industry: ' + acc.Industry;
 172         }
 173     }
 174 
 175     update contacts;
 176 }
 177 ```
 178 
 179 **Key**: `Map<Id, SObject>` constructor automatically creates map from query results.
 180 
 181 ---
 182 
 183 ### Pattern 2: Grouping Related Records
 184 
 185 **Use Case**: Process child records grouped by parent.
 186 
 187 ```apex
 188 public static void processContactsByAccount(List<Contact> contacts) {
 189     // Group contacts by AccountId
 190     Map<Id, List<Contact>> contactsByAccount = new Map<Id, List<Contact>>();
 191 
 192     for (Contact con : contacts) {
 193         if (!contactsByAccount.containsKey(con.AccountId)) {
 194             contactsByAccount.put(con.AccountId, new List<Contact>());
 195         }
 196         contactsByAccount.get(con.AccountId).add(con);
 197     }
 198 
 199     // Process each group
 200     for (Id accountId : contactsByAccount.keySet()) {
 201         List<Contact> accountContacts = contactsByAccount.get(accountId);
 202         System.debug('Account ' + accountId + ' has ' + accountContacts.size() + ' contacts');
 203         // Process accountContacts
 204     }
 205 }
 206 ```
 207 
 208 **Alternative using Null Coalescing (API 59+):**
 209 ```apex
 210 for (Contact con : contacts) {
 211     List<Contact> existing = contactsByAccount.get(con.AccountId);
 212     if (existing == null) {
 213         existing = new List<Contact>();
 214         contactsByAccount.put(con.AccountId, existing);
 215     }
 216     existing.add(con);
 217 }
 218 ```
 219 
 220 ---
 221 
 222 ### Pattern 3: Aggregate Queries for Rollups
 223 
 224 **Use Case**: Calculate rollup values (count, sum, avg) on related records.
 225 
 226 ```apex
 227 public static void updateAccountContactCounts(Set<Id> accountIds) {
 228     // Query aggregate data
 229     Map<Id, Integer> contactCountsByAccount = new Map<Id, Integer>();
 230 
 231     for (AggregateResult ar : [
 232         SELECT AccountId, COUNT(Id) contactCount
 233         FROM Contact
 234         WHERE AccountId IN :accountIds
 235         GROUP BY AccountId
 236     ]) {
 237         Id accountId = (Id) ar.get('AccountId');
 238         Integer count = (Integer) ar.get('contactCount');
 239         contactCountsByAccount.put(accountId, count);
 240     }
 241 
 242     // Update accounts
 243     List<Account> accountsToUpdate = new List<Account>();
 244     for (Id accountId : accountIds) {
 245         Integer count = contactCountsByAccount.get(accountId) ?? 0;
 246         accountsToUpdate.add(new Account(
 247             Id = accountId,
 248             Number_of_Contacts__c = count
 249         ));
 250     }
 251 
 252     update accountsToUpdate;
 253 }
 254 ```
 255 
 256 **Why use aggregates**: More efficient than querying all records and counting in Apex.
 257 
 258 ---
 259 
 260 ### Pattern 4: Bulk Upsert with External ID
 261 
 262 **Use Case**: Upserting records from external system.
 263 
 264 ```apex
 265 public static void syncAccountsFromExternal(List<ExternalAccount> externalAccounts) {
 266     List<Account> accountsToUpsert = new List<Account>();
 267 
 268     for (ExternalAccount ext : externalAccounts) {
 269         accountsToUpsert.add(new Account(
 270             External_ID__c = ext.externalId,  // External ID field
 271             Name = ext.name,
 272             Industry = ext.industry
 273         ));
 274     }
 275 
 276     // Upsert by External ID field
 277     Database.upsert(accountsToUpsert, Account.External_ID__c, false);
 278 }
 279 ```
 280 
 281 **Key**: `Database.upsert()` with External ID field automatically matches and updates existing records.
 282 
 283 ---
 284 
 285 ### Pattern 5: Conditional DML (Only Update Changed Records)
 286 
 287 **Use Case**: Avoid unnecessary DML on unchanged records.
 288 
 289 ```apex
 290 public static void updateAccountsIfChanged(List<Account> accounts, Map<Id, Account> oldMap) {
 291     List<Account> accountsToUpdate = new List<Account>();
 292 
 293     for (Account newAcc : accounts) {
 294         Account oldAcc = oldMap.get(newAcc.Id);
 295 
 296         // Only update if specific fields changed
 297         if (newAcc.Industry != oldAcc.Industry || newAcc.Rating != oldAcc.Rating) {
 298             accountsToUpdate.add(newAcc);
 299         }
 300     }
 301 
 302     if (!accountsToUpdate.isEmpty()) {
 303         update accountsToUpdate;
 304     }
 305 }
 306 ```
 307 
 308 **Benefit**: Reduces DML statements and CPU time.
 309 
 310 ---
 311 
 312 ## Collection Handling Best Practices
 313 
 314 ### Use the Right Collection Type
 315 
 316 | Collection | When to Use | Key Features |
 317 |------------|-------------|--------------|
 318 | **List<T>** | Ordered data, duplicates allowed | Index access, iteration |
 319 | **Set<T>** | Unique values, fast lookups | No duplicates, O(1) contains() |
 320 | **Map<K,V>** | Key-value pairs, fast lookups | O(1) get(), unique keys |
 321 
 322 **Example: Deduplication**
 323 ```apex
 324 // ❌ BAD - O(n²) complexity
 325 List<Id> uniqueIds = new List<Id>();
 326 for (Id accountId : allAccountIds) {
 327     if (!uniqueIds.contains(accountId)) {  // Linear search!
 328         uniqueIds.add(accountId);
 329     }
 330 }
 331 
 332 // ✅ GOOD - O(n) complexity
 333 Set<Id> uniqueIdsSet = new Set<Id>(allAccountIds);  // Automatic deduplication
 334 ```
 335 
 336 ---
 337 
 338 ### List Operations
 339 
 340 **Creating Lists:**
 341 ```apex
 342 // Empty list
 343 List<Account> accounts = new List<Account>();
 344 
 345 // From SOQL
 346 List<Account> accounts = [SELECT Id FROM Account];
 347 
 348 // From Set
 349 Set<Id> idSet = new Set<Id>{acc1.Id, acc2.Id};
 350 List<Id> idList = new List<Id>(idSet);
 351 ```
 352 
 353 **Adding Elements:**
 354 ```apex
 355 accounts.add(newAccount);           // Add single
 356 accounts.addAll(moreAccounts);      // Add list
 357 ```
 358 
 359 **Checking Before DML (NOT NEEDED):**
 360 ```apex
 361 // ❌ UNNECESSARY - Salesforce handles empty lists
 362 if (!accounts.isEmpty()) {
 363     update accounts;
 364 }
 365 
 366 // ✅ SIMPLER - Just do it
 367 update accounts;  // No-op if empty, saves CPU cycles checking
 368 ```
 369 
 370 ---
 371 
 372 ### Set Operations
 373 
 374 **Union, Intersection, Difference:**
 375 ```apex
 376 Set<Id> set1 = new Set<Id>{id1, id2, id3};
 377 Set<Id> set2 = new Set<Id>{id2, id3, id4};
 378 
 379 // Union (all unique values)
 380 Set<Id> union = set1.clone();
 381 union.addAll(set2);  // {id1, id2, id3, id4}
 382 
 383 // Intersection (common values)
 384 Set<Id> intersection = set1.clone();
 385 intersection.retainAll(set2);  // {id2, id3}
 386 
 387 // Difference (in set1 but not set2)
 388 Set<Id> difference = set1.clone();
 389 difference.removeAll(set2);  // {id1}
 390 ```
 391 
 392 **Checking Membership:**
 393 ```apex
 394 if (accountIds.contains(acc.Id)) {
 395     // Fast O(1) lookup
 396 }
 397 ```
 398 
 399 **⚠️ API 62.0 Breaking Change:**
 400 Cannot modify Set while iterating - throws `System.FinalException`.
 401 
 402 ```apex
 403 // ❌ FAILS in API 62.0+
 404 Set<Id> ids = new Set<Id>{id1, id2, id3};
 405 for (Id currentId : ids) {
 406     ids.add(newId);  // FinalException!
 407 }
 408 
 409 // ✅ GOOD - Collect changes, apply after loop
 410 Set<Id> ids = new Set<Id>{id1, id2, id3};
 411 Set<Id> toAdd = new Set<Id>();
 412 
 413 for (Id currentId : ids) {
 414     toAdd.add(newId);
 415 }
 416 
 417 ids.addAll(toAdd);
 418 ```
 419 
 420 ---
 421 
 422 ### Map Operations
 423 
 424 **Creating Maps:**
 425 ```apex
 426 // Empty map
 427 Map<Id, Account> accountMap = new Map<Id, Account>();
 428 
 429 // From List (uses SObject Id as key)
 430 Map<Id, Account> accountMap = new Map<Id, Account>([SELECT Id, Name FROM Account]);
 431 
 432 // Manual insertion
 433 Map<String, Integer> scoreMap = new Map<String, Integer>();
 434 scoreMap.put('Alice', 95);
 435 scoreMap.put('Bob', 87);
 436 ```
 437 
 438 **Safe Access with Null Coalescing:**
 439 ```apex
 440 // Old way
 441 Integer score = scoreMap.get('Charlie');
 442 if (score == null) {
 443     score = 0;
 444 }
 445 
 446 // Modern way (API 59+)
 447 Integer score = scoreMap.get('Charlie') ?? 0;
 448 ```
 449 
 450 **Iterating Maps:**
 451 ```apex
 452 // Iterate keys
 453 for (Id accountId : accountMap.keySet()) {
 454     Account acc = accountMap.get(accountId);
 455 }
 456 
 457 // Iterate values
 458 for (Account acc : accountMap.values()) {
 459     System.debug(acc.Name);
 460 }
 461 
 462 // Iterate entries (best for both key + value)
 463 for (Id accountId : accountMap.keySet()) {
 464     Account acc = accountMap.get(accountId);
 465     System.debug('Account ' + accountId + ': ' + acc.Name);
 466 }
 467 ```
 468 
 469 ---
 470 
 471 ## Monitoring and Debugging
 472 
 473 ### Using Limits Class
 474 
 475 **Check current consumption:**
 476 ```apex
 477 System.debug('SOQL Queries: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
 478 System.debug('DML Statements: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
 479 System.debug('CPU Time: ' + Limits.getCpuTime() + '/' + Limits.getLimitCpuTime());
 480 System.debug('Heap Size: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize());
 481 ```
 482 
 483 **Strategic placement:**
 484 ```apex
 485 public static void expensiveOperation() {
 486     System.debug('=== BEFORE OPERATION ===');
 487     logLimits();
 488 
 489     // Expensive code
 490     List<Account> accounts = [SELECT Id FROM Account];
 491 
 492     System.debug('=== AFTER OPERATION ===');
 493     logLimits();
 494 }
 495 
 496 private static void logLimits() {
 497     System.debug('SOQL: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
 498     System.debug('DML: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
 499 }
 500 ```
 501 
 502 ---
 503 
 504 ### Debug Logs Best Practices
 505 
 506 **Use log levels strategically:**
 507 ```apex
 508 System.debug(LoggingLevel.ERROR, 'Critical failure: ' + errorMsg);
 509 System.debug(LoggingLevel.WARN, 'Warning: potential issue');
 510 System.debug(LoggingLevel.INFO, 'Processing ' + accounts.size() + ' accounts');
 511 System.debug(LoggingLevel.DEBUG, 'Variable value: ' + variable);
 512 System.debug(LoggingLevel.FINE, 'Detailed trace info');
 513 ```
 514 
 515 **Filter in Setup → Debug Logs:**
 516 - Apex Code: DEBUG
 517 - Database: INFO
 518 - Workflow: INFO
 519 - Validation: INFO
 520 
 521 **Avoid excessive debug statements** - they consume heap and CPU.
 522 
 523 ---
 524 
 525 ### Query Plan Analysis
 526 
 527 **Check query selectivity:**
 528 ```apex
 529 // Use EXPLAIN in Developer Console or Workbench
 530 // Or query plan API (requires REST call)
 531 ```
 532 
 533 **Indicators of bad queries:**
 534 - TableScan (full table scan)
 535 - Cardinality mismatch (estimated vs actual rows)
 536 - Missing indexes on WHERE clause fields
 537 
 538 **See Also**: [Live SOQL Query Plan Analyzer](../shared/code_analyzer/live_query_plan.py) for automated analysis.
 539 
 540 ---
 541 
 542 ## Bulk Testing
 543 
 544 ### The 251 Record Rule
 545 
 546 **Why 251?** Trigger bulkification often breaks between 200-250 records due to chunk processing.
 547 
 548 **Test Class Pattern:**
 549 ```apex
 550 @IsTest
 551 private class AccountTriggerTest {
 552 
 553     @TestSetup
 554     static void setup() {
 555         // Use Test Data Factory to create 251 records
 556         TestDataFactory.createAccounts(251);
 557     }
 558 
 559     @IsTest
 560     static void testBulkInsert() {
 561         Test.startTest();
 562 
 563         List<Account> accounts = new List<Account>();
 564         for (Integer i = 0; i < 251; i++) {
 565             accounts.add(new Account(Name = 'Bulk Test ' + i, Industry = 'Technology'));
 566         }
 567 
 568         insert accounts;
 569 
 570         Test.stopTest();
 571 
 572         // Verify all 251 were processed correctly
 573         List<Account> inserted = [SELECT Id, Industry FROM Account WHERE Name LIKE 'Bulk Test%'];
 574         Assert.areEqual(251, inserted.size(), 'All 251 accounts should be inserted');
 575 
 576         for (Account acc : inserted) {
 577             Assert.areEqual('Technology', acc.Industry, 'Industry should be set for all records');
 578         }
 579     }
 580 
 581     @IsTest
 582     static void testBulkUpdate() {
 583         Test.startTest();
 584 
 585         List<Account> accounts = [SELECT Id, Industry FROM Account];
 586         for (Account acc : accounts) {
 587             acc.Industry = 'Finance';
 588         }
 589 
 590         update accounts;
 591 
 592         Test.stopTest();
 593 
 594         // Verify
 595         List<Account> updated = [SELECT Id, Industry FROM Account];
 596         Assert.areEqual(251, updated.size());
 597 
 598         for (Account acc : updated) {
 599             Assert.areEqual('Finance', acc.Industry);
 600         }
 601     }
 602 }
 603 ```
 604 
 605 ---
 606 
 607 ### Test Data Factory Pattern
 608 
 609 **Centralized test data creation:**
 610 ```apex
 611 @IsTest
 612 public class TestDataFactory {
 613 
 614     public static List<Account> createAccounts(Integer count) {
 615         List<Account> accounts = new List<Account>();
 616 
 617         for (Integer i = 0; i < count; i++) {
 618             accounts.add(new Account(
 619                 Name = 'Test Account ' + i,
 620                 Industry = 'Technology',
 621                 AnnualRevenue = 1000000
 622             ));
 623         }
 624 
 625         insert accounts;
 626         return accounts;
 627     }
 628 
 629     public static List<Contact> createContacts(Integer count, Id accountId) {
 630         List<Contact> contacts = new List<Contact>();
 631 
 632         for (Integer i = 0; i < count; i++) {
 633             contacts.add(new Contact(
 634                 LastName = 'Test Contact ' + i,
 635                 AccountId = accountId,
 636                 Email = 'test' + i + '@example.com'
 637             ));
 638         }
 639 
 640         insert contacts;
 641         return contacts;
 642     }
 643 
 644     // Add more factory methods as needed
 645 }
 646 ```
 647 
 648 **Benefits**:
 649 - Centralized data creation
 650 - Consistent test data
 651 - Easy to create 251+ records
 652 - Reduces code duplication
 653 
 654 ---
 655 
 656 ### Performance Testing
 657 
 658 **Measure CPU time and SOQL:**
 659 ```apex
 660 @IsTest
 661 static void testPerformance() {
 662     TestDataFactory.createAccounts(251);
 663 
 664     Integer startQueries = Limits.getQueries();
 665     Integer startCpu = Limits.getCpuTime();
 666 
 667     Test.startTest();
 668 
 669     // Your code here
 670     AccountService.processAccounts([SELECT Id FROM Account]);
 671 
 672     Test.stopTest();
 673 
 674     Integer queriesUsed = Limits.getQueries() - startQueries;
 675     Integer cpuUsed = Limits.getCpuTime() - startCpu;
 676 
 677     System.debug('Queries used: ' + queriesUsed);
 678     System.debug('CPU time: ' + cpuUsed + 'ms');
 679 
 680     // Assert performance thresholds
 681     Assert.isTrue(queriesUsed <= 5, 'Should use no more than 5 SOQL queries');
 682     Assert.isTrue(cpuUsed <= 2000, 'Should complete in under 2 seconds CPU time');
 683 }
 684 ```
 685 
 686 ---
 687 
 688 ## Advanced Optimization Techniques
 689 
 690 ### Lazy Loading Pattern
 691 
 692 **Defer expensive operations until needed:**
 693 ```apex
 694 public class AccountProcessor {
 695 
 696     private Map<Id, List<Contact>> contactsCache;
 697 
 698     public List<Contact> getContactsForAccount(Id accountId) {
 699         // Lazy load - only query when first accessed
 700         if (contactsCache == null) {
 701             loadAllContacts();
 702         }
 703 
 704         return contactsCache.get(accountId) ?? new List<Contact>();
 705     }
 706 
 707     private void loadAllContacts() {
 708         contactsCache = new Map<Id, List<Contact>>();
 709 
 710         for (Contact con : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
 711             if (!contactsCache.containsKey(con.AccountId)) {
 712                 contactsCache.put(con.AccountId, new List<Contact>());
 713             }
 714             contactsCache.get(con.AccountId).add(con);
 715         }
 716     }
 717 }
 718 ```
 719 
 720 ---
 721 
 722 ### Platform Cache for Expensive Queries
 723 
 724 **Cache frequently accessed data:**
 725 ```apex
 726 public class CachedMetadataService {
 727 
 728     private static final String CACHE_PARTITION = 'local.MetadataCache';
 729 
 730     public static List<Config__c> getConfigurations() {
 731         // Try cache first
 732         List<Config__c> cached = (List<Config__c>) Cache.Org.get(CACHE_PARTITION + '.configs');
 733 
 734         if (cached != null) {
 735             return cached;
 736         }
 737 
 738         // Cache miss - query and store
 739         List<Config__c> configs = [SELECT Id, Name, Value__c FROM Config__c];
 740         Cache.Org.put(CACHE_PARTITION + '.configs', configs, 3600); // 1 hour TTL
 741 
 742         return configs;
 743     }
 744 }
 745 ```
 746 
 747 ---
 748 
 749 ## Reference
 750 
 751 **Full Documentation**: See `references/` folder for comprehensive guides:
 752 - `best-practices.md` - Bulkification patterns
 753 - `testing-guide.md` - Test Data Factory and bulk testing
 754 - `code-review-checklist.md` - Bulkification scoring criteria
 755 
 756 **Back to Main**: [SKILL.md](../SKILL.md)
