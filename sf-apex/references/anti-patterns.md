<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Anti-Patterns
   2 
   3 Comprehensive catalog of common Apex anti-patterns, code smells, and how to fix them.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Critical Anti-Patterns](#critical-anti-patterns)
  10 2. [Code Review Red Flags](#code-review-red-flags)
  11 3. [Performance Anti-Patterns](#performance-anti-patterns)
  12 4. [Security Anti-Patterns](#security-anti-patterns)
  13 5. [Testing Anti-Patterns](#testing-anti-patterns)
  14 6. [Code Smell Catalog](#code-smell-catalog)
  15 
  16 ---
  17 
  18 ## Critical Anti-Patterns
  19 
  20 These patterns will cause immediate failures or security vulnerabilities. **NEVER allow these in production code.**
  21 
  22 ### 1. SOQL in Loop
  23 
  24 **Problem**: Hits 100 SOQL query limit.
  25 
  26 **❌ BAD:**
  27 ```apex
  28 for (Account acc : accounts) {
  29     List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
  30     // Process contacts
  31 }
  32 // Fails after 100 accounts
  33 ```
  34 
  35 **✅ GOOD:**
  36 ```apex
  37 Set<Id> accountIds = new Set<Id>();
  38 for (Account acc : accounts) {
  39     accountIds.add(acc.Id);
  40 }
  41 
  42 Map<Id, List<Contact>> contactsByAccountId = new Map<Id, List<Contact>>();
  43 for (Contact con : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
  44     if (!contactsByAccountId.containsKey(con.AccountId)) {
  45         contactsByAccountId.put(con.AccountId, new List<Contact>());
  46     }
  47     contactsByAccountId.get(con.AccountId).add(con);
  48 }
  49 
  50 for (Account acc : accounts) {
  51     List<Contact> contacts = contactsByAccountId.get(acc.Id) ?? new List<Contact>();
  52     // Process contacts
  53 }
  54 ```
  55 
  56 **Detection**: Search for `[SELECT` inside `for` loops.
  57 
  58 ---
  59 
  60 ### 2. DML in Loop
  61 
  62 **Problem**: Hits 150 DML statement limit.
  63 
  64 **❌ BAD:**
  65 ```apex
  66 for (Account acc : accounts) {
  67     acc.Industry = 'Technology';
  68     update acc;  // DML in loop!
  69 }
  70 // Fails after 150 accounts
  71 ```
  72 
  73 **✅ GOOD:**
  74 ```apex
  75 for (Account acc : accounts) {
  76     acc.Industry = 'Technology';
  77 }
  78 update accounts;  // Single DML after loop
  79 ```
  80 
  81 **Detection**: Search for `insert`, `update`, `delete`, `upsert` inside `for` loops.
  82 
  83 ---
  84 
  85 ### 3. Missing Sharing Keyword
  86 
  87 **Problem**: Bypasses record-level security by default.
  88 
  89 **❌ BAD:**
  90 ```apex
  91 public class AccountService {
  92     // Implicitly "without sharing" - security risk!
  93 }
  94 ```
  95 
  96 **✅ GOOD:**
  97 ```apex
  98 public with sharing class AccountService {
  99     // Respects sharing rules
 100 }
 101 ```
 102 
 103 **Detection**: Classes without `with sharing`, `without sharing`, or `inherited sharing`.
 104 
 105 ---
 106 
 107 ### 4. Hardcoded Record IDs
 108 
 109 **Problem**: IDs differ between orgs, causing deployment failures.
 110 
 111 **❌ BAD:**
 112 ```apex
 113 Id recordTypeId = '012000000000000AAA';  // Hardcoded ID!
 114 ```
 115 
 116 **✅ GOOD:**
 117 ```apex
 118 // Option 1: Query at runtime
 119 Id recordTypeId = Schema.SObjectType.Account.getRecordTypeInfosByDeveloperName()
 120     .get('Enterprise').getRecordTypeId();
 121 
 122 // Option 2: Custom Metadata
 123 Account_Config__mdt config = Account_Config__mdt.getInstance('Default');
 124 Id recordTypeId = config.Record_Type_Id__c;
 125 ```
 126 
 127 **Detection**: 15 or 18-character ID literals in code.
 128 
 129 ---
 130 
 131 ### 5. Empty Catch Blocks
 132 
 133 **Problem**: Silently swallows errors, making debugging impossible.
 134 
 135 **❌ BAD:**
 136 ```apex
 137 try {
 138     insert accounts;
 139 } catch (DmlException e) {
 140     // Silent failure - no logging!
 141 }
 142 ```
 143 
 144 **✅ GOOD:**
 145 ```apex
 146 try {
 147     insert accounts;
 148 } catch (DmlException e) {
 149     System.debug(LoggingLevel.ERROR, 'Failed to insert accounts: ' + e.getMessage());
 150     throw e;  // Or handle gracefully with user feedback
 151 }
 152 ```
 153 
 154 **Detection**: `catch` blocks with no statements or only comments.
 155 
 156 ---
 157 
 158 ### 6. SOQL Injection
 159 
 160 **Problem**: User input concatenated into SOQL allows malicious queries.
 161 
 162 **❌ BAD:**
 163 ```apex
 164 String query = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';
 165 List<Account> accounts = Database.query(query);
 166 // userInput = "test' OR '1'='1" returns ALL accounts!
 167 ```
 168 
 169 **✅ GOOD:**
 170 ```apex
 171 // Use bind variables
 172 List<Account> accounts = [SELECT Id FROM Account WHERE Name = :userInput];
 173 ```
 174 
 175 **Detection**: String concatenation in SOQL with variables.
 176 
 177 ---
 178 
 179 ### 7. Test Without Assertions
 180 
 181 **Problem**: False positive tests that pass even when code fails.
 182 
 183 **❌ BAD:**
 184 ```apex
 185 @IsTest
 186 static void testAccountCreation() {
 187     Account acc = new Account(Name = 'Test');
 188     insert acc;
 189     // No assertions - test passes even if logic is broken!
 190 }
 191 ```
 192 
 193 **✅ GOOD:**
 194 ```apex
 195 @IsTest
 196 static void testAccountCreation() {
 197     Account acc = new Account(Name = 'Test', Industry = 'Tech');
 198     insert acc;
 199 
 200     Account inserted = [SELECT Id, Industry FROM Account WHERE Id = :acc.Id];
 201     Assert.areEqual('Tech', inserted.Industry, 'Industry should be set');
 202 }
 203 ```
 204 
 205 **Detection**: `@IsTest` methods with no `Assert.*` calls.
 206 
 207 ---
 208 
 209 ## Code Review Red Flags
 210 
 211 These patterns indicate poor code quality and should be refactored.
 212 
 213 | Anti-Pattern | Problem | Fix |
 214 |--------------|---------|-----|
 215 | **SOQL without WHERE or LIMIT** | Returns all records, slow | Always add `WHERE` clause or `LIMIT` |
 216 | **Multiple triggers on object** | Unpredictable execution order | Single trigger + Trigger Actions Framework |
 217 | **Generic `Exception` only** | Masks specific errors | Catch specific exceptions first |
 218 | **No trigger bypass flag** | Can't disable for data loads | Add Custom Setting bypass |
 219 | **`System.debug()` everywhere** | Performance impact, clutters logs | Use logging framework with levels |
 220 | **Unnecessary `isEmpty()` before DML** | Wastes CPU | Remove - DML handles empty lists |
 221 | **`!= false` comparisons** | Confusing double negative | Use `== true` or just the boolean |
 222 | **No Test Data Factory** | Duplicated test data setup | Centralize in factory class |
 223 | **God Class** | Single class does everything | Split into Service/Selector/Domain |
 224 | **Magic Numbers** | Hardcoded values like `if (score > 75)` | Use named constants |
 225 
 226 ---
 227 
 228 ### SOQL Without WHERE or LIMIT
 229 
 230 **❌ BAD:**
 231 ```apex
 232 List<Account> accounts = [SELECT Id FROM Account];
 233 // Returns ALL accounts - could be millions!
 234 ```
 235 
 236 **✅ GOOD:**
 237 ```apex
 238 // Option 1: Filter
 239 List<Account> accounts = [SELECT Id FROM Account WHERE Industry = 'Technology'];
 240 
 241 // Option 2: Limit
 242 List<Account> accounts = [SELECT Id FROM Account ORDER BY CreatedDate DESC LIMIT 200];
 243 
 244 // Option 3: Both
 245 List<Account> accounts = [SELECT Id FROM Account WHERE CreatedDate = THIS_YEAR LIMIT 1000];
 246 ```
 247 
 248 ---
 249 
 250 ### Multiple Triggers on Same Object
 251 
 252 **❌ BAD:**
 253 ```apex
 254 // AccountTrigger1.trigger
 255 trigger AccountTrigger1 on Account (before insert) {
 256     // Some logic
 257 }
 258 
 259 // AccountTrigger2.trigger
 260 trigger AccountTrigger2 on Account (before insert) {
 261     // More logic - which runs first?
 262 }
 263 ```
 264 
 265 **✅ GOOD:**
 266 ```apex
 267 // Single trigger + TAF
 268 trigger AccountTrigger on Account (before insert, after insert, before update, after update) {
 269     new MetadataTriggerHandler().run();
 270 }
 271 
 272 // Separate action classes
 273 public class TA_Account_SetDefaults implements TriggerAction.BeforeInsert { }
 274 public class TA_Account_Validate implements TriggerAction.BeforeInsert { }
 275 ```
 276 
 277 ---
 278 
 279 ### Generic Exception Only
 280 
 281 **❌ BAD:**
 282 ```apex
 283 try {
 284     insert accounts;
 285 } catch (Exception e) {
 286     // Catches EVERYTHING - too broad
 287 }
 288 ```
 289 
 290 **✅ GOOD:**
 291 ```apex
 292 try {
 293     insert accounts;
 294 } catch (DmlException e) {
 295     // Handle DML errors specifically
 296     System.debug('DML failed: ' + e.getDmlMessage(0));
 297 } catch (Exception e) {
 298     // Catch unexpected errors
 299     System.debug('Unexpected error: ' + e.getMessage());
 300     throw e;
 301 }
 302 ```
 303 
 304 ---
 305 
 306 ### Unnecessary isEmpty() Before DML
 307 
 308 **❌ BAD:**
 309 ```apex
 310 if (!accounts.isEmpty()) {
 311     update accounts;
 312 }
 313 // Wastes CPU checking - DML already handles empty lists
 314 ```
 315 
 316 **✅ GOOD:**
 317 ```apex
 318 update accounts;  // No-op if empty, no error thrown
 319 ```
 320 
 321 ---
 322 
 323 ### Double Negative Comparisons
 324 
 325 **❌ BAD:**
 326 ```apex
 327 if (acc.IsActive__c != false) {
 328     // Confusing logic
 329 }
 330 ```
 331 
 332 **✅ GOOD:**
 333 ```apex
 334 if (acc.IsActive__c == true) {
 335     // Clear intent
 336 }
 337 
 338 // Or even better
 339 if (acc.IsActive__c) {
 340     // Most concise
 341 }
 342 ```
 343 
 344 ---
 345 
 346 ## Performance Anti-Patterns
 347 
 348 ### 1. Nested Loops with SOQL
 349 
 350 **❌ BAD:**
 351 ```apex
 352 for (Account acc : accounts) {
 353     for (Contact con : [SELECT Id FROM Contact WHERE AccountId = :acc.Id]) {
 354         // Nested SOQL - quadratic complexity!
 355     }
 356 }
 357 ```
 358 
 359 **✅ GOOD:**
 360 ```apex
 361 Map<Id, Account> accountsWithContacts = new Map<Id, Account>([
 362     SELECT Id, (SELECT Id FROM Contacts)
 363     FROM Account
 364     WHERE Id IN :accountIds
 365 ]);
 366 
 367 for (Account acc : accountsWithContacts.values()) {
 368     for (Contact con : acc.Contacts) {
 369         // No SOQL in loop
 370     }
 371 }
 372 ```
 373 
 374 ---
 375 
 376 ### 2. Querying in Constructor
 377 
 378 **❌ BAD:**
 379 ```apex
 380 public class AccountService {
 381     private List<Account> accounts;
 382 
 383     public AccountService() {
 384         accounts = [SELECT Id FROM Account];  // Runs on EVERY instantiation
 385     }
 386 }
 387 ```
 388 
 389 **✅ GOOD:**
 390 ```apex
 391 public class AccountService {
 392     private List<Account> accounts;
 393 
 394     public AccountService(List<Account> accounts) {
 395         this.accounts = accounts;  // Inject dependencies
 396     }
 397 
 398     // Or lazy load only when needed
 399     private List<Account> getAccounts() {
 400         if (accounts == null) {
 401             accounts = [SELECT Id FROM Account LIMIT 200];
 402         }
 403         return accounts;
 404     }
 405 }
 406 ```
 407 
 408 ---
 409 
 410 ### 3. Excessive CPU Time
 411 
 412 **❌ BAD:**
 413 ```apex
 414 for (Account acc : accounts) {
 415     for (Integer i = 0; i < 10000; i++) {
 416         String hash = EncodingUtil.convertToHex(Crypto.generateDigest('SHA256', Blob.valueOf(acc.Name + i)));
 417         // Expensive crypto in nested loop
 418     }
 419 }
 420 ```
 421 
 422 **✅ GOOD:**
 423 ```apex
 424 // Move expensive operations outside loops
 425 String baseHash = EncodingUtil.convertToHex(Crypto.generateDigest('SHA256', Blob.valueOf('base')));
 426 
 427 for (Account acc : accounts) {
 428     acc.Hash__c = baseHash;  // Reuse computed value
 429 }
 430 ```
 431 
 432 ---
 433 
 434 ### 4. Inefficient Collections
 435 
 436 **❌ BAD:**
 437 ```apex
 438 List<Id> uniqueIds = new List<Id>();
 439 for (Id accountId : allIds) {
 440     if (!uniqueIds.contains(accountId)) {  // O(n) lookup in List
 441         uniqueIds.add(accountId);
 442     }
 443 }
 444 ```
 445 
 446 **✅ GOOD:**
 447 ```apex
 448 Set<Id> uniqueIds = new Set<Id>(allIds);  // O(1) deduplication
 449 ```
 450 
 451 ---
 452 
 453 ## Security Anti-Patterns
 454 
 455 ### 1. without sharing Everywhere
 456 
 457 **❌ BAD:**
 458 ```apex
 459 public without sharing class AccountController {
 460     @AuraEnabled
 461     public static List<Account> getAccounts() {
 462         // Bypasses sharing - user sees ALL accounts!
 463         return [SELECT Id FROM Account];
 464     }
 465 }
 466 ```
 467 
 468 **✅ GOOD:**
 469 ```apex
 470 public with sharing class AccountController {
 471     @AuraEnabled
 472     public static List<Account> getAccounts() {
 473         // Respects sharing rules
 474         return [SELECT Id FROM Account WITH USER_MODE];
 475     }
 476 }
 477 ```
 478 
 479 ---
 480 
 481 ### 2. No CRUD/FLS Checks
 482 
 483 **❌ BAD:**
 484 ```apex
 485 public static void updateAccounts(List<Account> accounts) {
 486     update accounts;  // No permission check!
 487 }
 488 ```
 489 
 490 **✅ GOOD:**
 491 ```apex
 492 public static void updateAccounts(List<Account> accounts) {
 493     if (!Schema.sObjectType.Account.isUpdateable()) {
 494         throw new SecurityException('User cannot update Accounts');
 495     }
 496 
 497     // Or use WITH USER_MODE in queries
 498     update accounts;
 499 }
 500 ```
 501 
 502 ---
 503 
 504 ### 3. Hardcoded Credentials
 505 
 506 **❌ BAD:**
 507 ```apex
 508 String apiKey = 'sk_live_abc123xyz';  // NEVER hardcode secrets!
 509 ```
 510 
 511 **✅ GOOD:**
 512 ```apex
 513 // Use Named Credentials
 514 HttpRequest req = new HttpRequest();
 515 req.setEndpoint('callout:MyNamedCredential/api');  // Auth handled by platform
 516 ```
 517 
 518 ---
 519 
 520 ## Testing Anti-Patterns
 521 
 522 ### 1. @SeeAllData=true
 523 
 524 **❌ BAD:**
 525 ```apex
 526 @IsTest(SeeAllData=true)
 527 private class AccountServiceTest {
 528     // Depends on org data - brittle, slow
 529 }
 530 ```
 531 
 532 **✅ GOOD:**
 533 ```apex
 534 @IsTest
 535 private class AccountServiceTest {
 536     @TestSetup
 537     static void setup() {
 538         TestDataFactory.createAccounts(10);  // Isolated test data
 539     }
 540 }
 541 ```
 542 
 543 ---
 544 
 545 ### 2. No Bulk Testing
 546 
 547 **❌ BAD:**
 548 ```apex
 549 @IsTest
 550 static void testAccountCreation() {
 551     Account acc = new Account(Name = 'Test');
 552     insert acc;
 553     // Only tests 1 record - misses bulkification bugs
 554 }
 555 ```
 556 
 557 **✅ GOOD:**
 558 ```apex
 559 @IsTest
 560 static void testBulkAccountCreation() {
 561     List<Account> accounts = new List<Account>();
 562     for (Integer i = 0; i < 251; i++) {
 563         accounts.add(new Account(Name = 'Bulk Test ' + i));
 564     }
 565 
 566     insert accounts;
 567     Assert.areEqual(251, [SELECT COUNT() FROM Account]);
 568 }
 569 ```
 570 
 571 ---
 572 
 573 ### 3. Testing Implementation, Not Behavior
 574 
 575 **❌ BAD:**
 576 ```apex
 577 @IsTest
 578 static void testGetAccountsCallsQuery() {
 579     // Tests internal implementation
 580     Assert.areEqual(1, Limits.getQueries(), 'Should call SOQL once');
 581 }
 582 ```
 583 
 584 **✅ GOOD:**
 585 ```apex
 586 @IsTest
 587 static void testGetAccountsReturnsCorrectRecords() {
 588     TestDataFactory.createAccounts(5);
 589 
 590     List<Account> results = AccountService.getAccounts();
 591 
 592     Assert.areEqual(5, results.size(), 'Should return all accounts');
 593 }
 594 ```
 595 
 596 ---
 597 
 598 ## Code Smell Catalog
 599 
 600 Based on "Clean Apex Code" by Pablo Gonzalez and clean code principles.
 601 
 602 ### Long Method
 603 
 604 **Smell**: Method exceeds 30 lines.
 605 
 606 **❌ BAD:**
 607 ```apex
 608 public static void processAccount(Account acc) {
 609     // 100 lines of mixed logic
 610     if (acc.Industry == 'Tech') {
 611         // Validation logic
 612         if (acc.AnnualRevenue == null) { ... }
 613         // Calculation logic
 614         Decimal score = ...;
 615         // DML logic
 616         update acc;
 617         // Notification logic
 618         EmailService.send(...);
 619     }
 620 }
 621 ```
 622 
 623 **✅ GOOD:**
 624 ```apex
 625 public static void processAccount(Account acc) {
 626     validateAccount(acc);
 627     calculateScore(acc);
 628     saveAccount(acc);
 629     notifyOwner(acc);
 630 }
 631 
 632 private static void validateAccount(Account acc) { ... }
 633 private static void calculateScore(Account acc) { ... }
 634 private static void saveAccount(Account acc) { ... }
 635 private static void notifyOwner(Account acc) { ... }
 636 ```
 637 
 638 **Refactoring**: Extract Method - split into smaller methods with single responsibilities.
 639 
 640 ---
 641 
 642 ### Large Class (God Class)
 643 
 644 **Smell**: Class exceeds 500 lines or has 20+ methods.
 645 
 646 **❌ BAD:**
 647 ```apex
 648 public class AccountService {
 649     // 50 methods mixing concerns:
 650     public static void createAccount() { }
 651     public static void updateAccount() { }
 652     public static void validateAccount() { }
 653     public static void calculateScore() { }
 654     public static void sendEmail() { }
 655     public static void generateReport() { }
 656     // ... 44 more methods
 657 }
 658 ```
 659 
 660 **✅ GOOD:**
 661 ```apex
 662 // Split by responsibility
 663 public class AccountService { }         // Business logic
 664 public class AccountValidator { }       // Validation
 665 public class AccountScoreCalculator { } // Scoring
 666 public class AccountEmailService { }    // Notifications
 667 public class AccountReportGenerator { } // Reporting
 668 ```
 669 
 670 **Refactoring**: Extract Class - split into multiple classes by concern.
 671 
 672 ---
 673 
 674 ### Magic Numbers
 675 
 676 **Smell**: Unexplained numeric literals.
 677 
 678 **❌ BAD:**
 679 ```apex
 680 if (acc.Score__c > 75) {
 681     acc.Rating = 'Hot';
 682 }
 683 ```
 684 
 685 **✅ GOOD:**
 686 ```apex
 687 private static final Integer HOT_LEAD_THRESHOLD = 75;
 688 
 689 if (acc.Score__c > HOT_LEAD_THRESHOLD) {
 690     acc.Rating = 'Hot';
 691 }
 692 ```
 693 
 694 ---
 695 
 696 ### Long Parameter List
 697 
 698 **Smell**: Method has 5+ parameters.
 699 
 700 **❌ BAD:**
 701 ```apex
 702 public static void createAccount(
 703     String name,
 704     String industry,
 705     Decimal revenue,
 706     String phone,
 707     String email,
 708     String website,
 709     Id ownerId
 710 ) { }
 711 ```
 712 
 713 **✅ GOOD:**
 714 ```apex
 715 public class AccountRequest {
 716     public String name;
 717     public String industry;
 718     public Decimal revenue;
 719     public String phone;
 720     public String email;
 721     public String website;
 722     public Id ownerId;
 723 }
 724 
 725 public static void createAccount(AccountRequest request) { }
 726 ```
 727 
 728 ---
 729 
 730 ### Feature Envy
 731 
 732 **Smell**: Method uses more methods/fields from another class than its own.
 733 
 734 **❌ BAD:**
 735 ```apex
 736 public class OrderService {
 737     public static Decimal calculateDiscount(Order__c order) {
 738         Account acc = [SELECT Id, Tier__c FROM Account WHERE Id = :order.Account__c];
 739         if (acc.Tier__c == 'Gold') {
 740             return order.Amount__c * 0.2;
 741         } else if (acc.Tier__c == 'Silver') {
 742             return order.Amount__c * 0.1;
 743         }
 744         return 0;
 745     }
 746 }
 747 ```
 748 
 749 **✅ GOOD:**
 750 ```apex
 751 public class Account extends SObject {
 752     public Decimal getDiscountRate() {
 753         if (this.Tier__c == 'Gold') return 0.2;
 754         if (this.Tier__c == 'Silver') return 0.1;
 755         return 0;
 756     }
 757 }
 758 
 759 public class OrderService {
 760     public static Decimal calculateDiscount(Order__c order) {
 761         Account acc = [SELECT Id, Tier__c FROM Account WHERE Id = :order.Account__c];
 762         return order.Amount__c * acc.getDiscountRate();
 763     }
 764 }
 765 ```
 766 
 767 **Refactoring**: Move Method - move logic to the class it uses most.
 768 
 769 ---
 770 
 771 ### Primitive Obsession
 772 
 773 **Smell**: Using primitives instead of small objects to represent concepts.
 774 
 775 **❌ BAD:**
 776 ```apex
 777 public static void sendEmail(String address, String subject, String body) {
 778     // Validates email format inline
 779     if (!address.contains('@')) throw new InvalidEmailException();
 780 }
 781 ```
 782 
 783 **✅ GOOD:**
 784 ```apex
 785 public class EmailAddress {
 786     private String value;
 787 
 788     public EmailAddress(String address) {
 789         if (!address.contains('@')) {
 790             throw new InvalidEmailException('Invalid email format');
 791         }
 792         this.value = address;
 793     }
 794 
 795     public String getValue() {
 796         return value;
 797     }
 798 }
 799 
 800 public static void sendEmail(EmailAddress address, String subject, String body) {
 801     // Email is already validated
 802 }
 803 ```
 804 
 805 ---
 806 
 807 ## Detection Tools
 808 
 809 **How to find anti-patterns:**
 810 
 811 | Tool | What It Finds |
 812 |------|---------------|
 813 | **Salesforce Code Analyzer** | SOQL/DML in loops, security issues |
 814 | **PMD (via VS Code)** | Code quality, complexity, unused code |
 815 | **Developer Console** | Test coverage, debug logs |
 816 | **Grep/Search** | Hardcoded IDs, empty catches, magic numbers |
 817 
 818 **VS Code Command:**
 819 ```bash
 820 sf code-analyzer run --workspace force-app/main/default/classes --output-format table
 821 ```
 822 
 823 **Example output:**
 824 ```
 825 Severity  File                    Line  Rule                     Message
 826 ────────────────────────────────────────────────────────────────────────────
 827 3         AccountService.cls      45    ApexSOQLInjection        SOQL injection risk
 828 2         AccountTrigger.trigger  12    ApexCRUDViolation        Missing FLS check
 829 1         ContactController.cls   28    ApexUnitTestClassShouldHaveAsserts  No assertions
 830 ```
 831 
 832 ---
 833 
 834 ## Refactoring Checklist
 835 
 836 When reviewing code, check for:
 837 
 838 **Bulkification:**
 839 - [ ] No SOQL in loops
 840 - [ ] No DML in loops
 841 - [ ] Collections used efficiently (Maps for lookups)
 842 - [ ] Tested with 251+ records
 843 
 844 **Security:**
 845 - [ ] All classes have sharing keyword
 846 - [ ] SOQL uses `WITH USER_MODE` or `Security.stripInaccessible()`
 847 - [ ] No hardcoded credentials
 848 - [ ] No SOQL injection vulnerabilities
 849 
 850 **Clean Code:**
 851 - [ ] Methods under 30 lines
 852 - [ ] Classes under 500 lines
 853 - [ ] No magic numbers (use constants)
 854 - [ ] Meaningful variable/method names
 855 
 856 **Testing:**
 857 - [ ] All methods covered by tests
 858 - [ ] Tests have assertions
 859 - [ ] Bulk tests exist (251+ records)
 860 - [ ] No `@SeeAllData=true`
 861 
 862 **Error Handling:**
 863 - [ ] No empty catch blocks
 864 - [ ] Specific exceptions before generic
 865 - [ ] Errors logged with context
 866 
 867 ---
 868 
 869 ## Reference
 870 
 871 **Full Documentation**: See `references/` folder for comprehensive guides:
 872 - `code-smells-guide.md` - Complete code smell catalog
 873 - `best-practices.md` - Correct patterns
 874 - `code-review-checklist.md` - 150-point scoring
 875 
 876 **Back to Main**: [SKILL.md](../SKILL.md)
