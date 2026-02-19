<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Security Guide
   2 
   3 Comprehensive guide to Apex security including CRUD/FLS enforcement, sharing rules, SOQL injection prevention, and generation guardrails.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Generation Guardrails](#generation-guardrails)
  10 2. [CRUD and FLS (Field-Level Security)](#crud-and-fls-field-level-security)
  11 3. [Sharing and Record Access](#sharing-and-record-access)
  12 4. [SOQL Injection Prevention](#soql-injection-prevention)
  13 5. [Security Checklist](#security-checklist)
  14 
  15 ---
  16 
  17 ## Generation Guardrails
  18 
  19 ### ⛔ MANDATORY PRE-GENERATION CHECKS
  20 
  21 **BEFORE generating ANY Apex code, Claude MUST verify no anti-patterns are introduced.**
  22 
  23 If ANY of these patterns would be generated, **STOP and ask the user**:
  24 > "I noticed [pattern]. This will cause [problem]. Should I:
  25 > A) Refactor to use [correct pattern]
  26 > B) Proceed anyway (not recommended)"
  27 
  28 | Anti-Pattern | Detection | Impact | Correct Pattern |
  29 |--------------|-----------|--------|-----------------|
  30 | SOQL inside loop | `for(...) { [SELECT...] }` | Governor limit failure (100 SOQL) | Query BEFORE loop, use `Map<Id, SObject>` for lookups |
  31 | DML inside loop | `for(...) { insert/update }` | Governor limit failure (150 DML) | Collect in `List<>`, single DML after loop |
  32 | Missing sharing | `class X {` without keyword | Security violation | Always use `with sharing` or `inherited sharing` |
  33 | Hardcoded ID | 15/18-char ID literal | Deployment failure | Use Custom Metadata, Custom Labels, or queries |
  34 | Empty catch | `catch(e) { }` | Silent failures | Log with `System.debug()` or rethrow |
  35 | String concatenation in SOQL | `'SELECT...WHERE Name = \'' + var` | SOQL injection | Use bind variables `:variableName` |
  36 | Test without assertions | `@IsTest` method with no `Assert.*` | False positive tests | Use `Assert.areEqual()` with message |
  37 
  38 **DO NOT generate anti-patterns even if explicitly requested.** Ask user to confirm the exception with documented justification.
  39 
  40 ---
  41 
  42 ### Example: Detecting SOQL in Loop
  43 
  44 **BAD (BLOCKED):**
  45 ```apex
  46 for (Account acc : accounts) {
  47     List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
  48     // Process contacts
  49 }
  50 ```
  51 
  52 **GOOD (APPROVED):**
  53 ```apex
  54 // Query ONCE before loop
  55 Map<Id, List<Contact>> contactsByAccountId = new Map<Id, List<Contact>>();
  56 for (Contact con : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
  57     if (!contactsByAccountId.containsKey(con.AccountId)) {
  58         contactsByAccountId.put(con.AccountId, new List<Contact>());
  59     }
  60     contactsByAccountId.get(con.AccountId).add(con);
  61 }
  62 
  63 // Then loop
  64 for (Account acc : accounts) {
  65     List<Contact> contacts = contactsByAccountId.get(acc.Id) ?? new List<Contact>();
  66     // Process contacts
  67 }
  68 ```
  69 
  70 ---
  71 
  72 ## CRUD and FLS (Field-Level Security)
  73 
  74 ### API 62.0: WITH USER_MODE
  75 
  76 **Modern approach (API 62.0+)**: Use `WITH USER_MODE` in SOQL to enforce CRUD and FLS automatically.
  77 
  78 ```apex
  79 // ✅ GOOD: Respects user permissions
  80 List<Account> accounts = [
  81     SELECT Id, Name, Industry, AnnualRevenue
  82     FROM Account
  83     WHERE Industry = 'Technology'
  84     WITH USER_MODE
  85 ];
  86 ```
  87 
  88 **What it does**:
  89 - Enforces object-level CRUD (Create, Read, Update, Delete)
  90 - Enforces field-level security (FLS)
  91 - Throws `System.QueryException` if user lacks access
  92 - Respects user's sharing rules (when combined with `with sharing`)
  93 
  94 **When to use SYSTEM_MODE**:
  95 ```apex
  96 // Only use SYSTEM_MODE when you explicitly NEED to bypass security
  97 List<Account> accounts = [
  98     SELECT Id, Name, Sensitive_Field__c
  99     FROM Account
 100     WITH SYSTEM_MODE  // ⚠️ Use with caution!
 101 ];
 102 ```
 103 
 104 **Use cases for SYSTEM_MODE**:
 105 - Background jobs that must process all records regardless of user
 106 - System integrations
 107 - Administrative cleanup scripts
 108 
 109 **ALWAYS document why SYSTEM_MODE is needed:**
 110 ```apex
 111 // JUSTIFICATION: This batch job processes all accounts for regulatory reporting,
 112 // regardless of user's access level. Approved by Security Team on 2025-01-01.
 113 ```
 114 
 115 ---
 116 
 117 ### Legacy Approach: Security.stripInaccessible()
 118 
 119 **For pre-62.0 compatibility** or when you need to filter fields dynamically:
 120 
 121 ```apex
 122 // Query all fields
 123 List<Account> accounts = [SELECT Id, Name, Industry, AnnualRevenue FROM Account];
 124 
 125 // Strip inaccessible fields
 126 SObjectAccessDecision decision = Security.stripInaccessible(
 127     AccessType.READABLE,
 128     accounts
 129 );
 130 
 131 // Use stripped records
 132 List<Account> accessibleAccounts = decision.getRecords();
 133 
 134 // Check which fields were removed
 135 Set<String> removedFields = decision.getRemovedFields().get('Account');
 136 if (removedFields != null && !removedFields.isEmpty()) {
 137     System.debug('User lacks access to fields: ' + removedFields);
 138 }
 139 ```
 140 
 141 **Access Types**:
 142 - `READABLE` - Read access (for queries)
 143 - `CREATABLE` - Create access (before insert)
 144 - `UPDATABLE` - Update access (before update)
 145 - `UPSERTABLE` - Upsert access
 146 
 147 **Example: Pre-DML Check**
 148 ```apex
 149 public static void createAccounts(List<Account> accounts) {
 150     // Check if user can create these fields
 151     SObjectAccessDecision decision = Security.stripInaccessible(
 152         AccessType.CREATABLE,
 153         accounts
 154     );
 155 
 156     if (!decision.getRemovedFields().isEmpty()) {
 157         throw new SecurityException('User lacks permission to create some fields');
 158     }
 159 
 160     insert decision.getRecords();
 161 }
 162 ```
 163 
 164 ---
 165 
 166 ### Manual CRUD/FLS Checks (Verbose but Explicit)
 167 
 168 ```apex
 169 // Check object-level CRUD
 170 if (!Schema.sObjectType.Account.isAccessible()) {
 171     throw new SecurityException('User cannot read Accounts');
 172 }
 173 
 174 if (!Schema.sObjectType.Account.isCreateable()) {
 175     throw new SecurityException('User cannot create Accounts');
 176 }
 177 
 178 // Check field-level security
 179 if (!Schema.sObjectType.Account.fields.Industry.isAccessible()) {
 180     throw new SecurityException('User cannot read Industry field');
 181 }
 182 
 183 if (!Schema.sObjectType.Account.fields.Industry.isUpdateable()) {
 184     throw new SecurityException('User cannot update Industry field');
 185 }
 186 ```
 187 
 188 **When to use**: Legacy codebases, specific error messaging, or when you need fine-grained control.
 189 
 190 ---
 191 
 192 ## Sharing and Record Access
 193 
 194 ### Sharing Keywords
 195 
 196 | Keyword | Behavior | When to Use |
 197 |---------|----------|-------------|
 198 | `with sharing` | Enforces record-level sharing | Default for user-facing code |
 199 | `without sharing` | Bypasses record-level sharing | System operations, integrations |
 200 | `inherited sharing` | Inherits from calling class | Utility classes, shared libraries |
 201 
 202 **Default Rule**: If no keyword specified, class runs in `without sharing` mode (pre-API 40 behavior).
 203 
 204 **ALWAYS specify a sharing keyword** - implicit behavior is confusing.
 205 
 206 ---
 207 
 208 ### with sharing (Recommended Default)
 209 
 210 ```apex
 211 public with sharing class AccountService {
 212 
 213     public static List<Account> getAccountsForUser() {
 214         // User only sees Accounts they have access to via sharing rules
 215         return [SELECT Id, Name FROM Account WITH USER_MODE];
 216     }
 217 
 218     public static void updateAccount(Account acc) {
 219         // Throws exception if user lacks access
 220         update acc;
 221     }
 222 }
 223 ```
 224 
 225 **Use cases**:
 226 - User-facing controllers (LWC, Aura, Visualforce)
 227 - Service classes handling user requests
 228 - Trigger actions that respect user context
 229 
 230 ---
 231 
 232 ### without sharing (Use Sparingly)
 233 
 234 ```apex
 235 public without sharing class AdminService {
 236 
 237     // JUSTIFICATION: This method is only called by system administrators
 238     // to perform global updates. Access controlled by Custom Permission.
 239     public static void globalAccountUpdate() {
 240         List<Account> allAccounts = [SELECT Id, Name FROM Account];
 241         // Process ALL accounts, ignoring sharing
 242     }
 243 }
 244 ```
 245 
 246 **Use cases**:
 247 - Background jobs
 248 - System integrations
 249 - Administrative operations
 250 
 251 **Security Note**: Always add access control checks when using `without sharing`:
 252 ```apex
 253 public without sharing class AdminService {
 254 
 255     public static void globalUpdate() {
 256         // Check permission before executing
 257         if (!FeatureManagement.checkPermission('Admin_Global_Update')) {
 258             throw new SecurityException('Requires Admin_Global_Update permission');
 259         }
 260 
 261         // Now safe to proceed with without sharing logic
 262     }
 263 }
 264 ```
 265 
 266 ---
 267 
 268 ### inherited sharing (Best for Utilities)
 269 
 270 ```apex
 271 public inherited sharing class StringUtils {
 272 
 273     // Inherits sharing from calling class
 274     public static String sanitize(String input) {
 275         return String.escapeSingleQuotes(input);
 276     }
 277 }
 278 
 279 // Called from "with sharing" class → runs with sharing
 280 // Called from "without sharing" class → runs without sharing
 281 ```
 282 
 283 **Use cases**:
 284 - Utility classes
 285 - Helper methods
 286 - Shared libraries that don't directly query records
 287 
 288 ---
 289 
 290 ### Mixing Sharing Contexts
 291 
 292 ```apex
 293 public with sharing class UserFacingService {
 294 
 295     public static void processAccount(Id accountId) {
 296         // This runs WITH sharing
 297         Account acc = [SELECT Id, Name FROM Account WHERE Id = :accountId];
 298 
 299         // Call a without sharing method for specific operation
 300         SystemOperations.performGlobalCheck(acc);
 301     }
 302 }
 303 
 304 public without sharing class SystemOperations {
 305 
 306     public static void performGlobalCheck(Account acc) {
 307         // This runs WITHOUT sharing
 308         // Can access records the original user couldn't see
 309     }
 310 }
 311 ```
 312 
 313 **Pattern**: Start with `with sharing`, only escalate to `without sharing` when needed.
 314 
 315 ---
 316 
 317 ## SOQL Injection Prevention
 318 
 319 ### The Problem
 320 
 321 **NEVER concatenate user input into SOQL strings:**
 322 
 323 ```apex
 324 // ❌ VULNERABLE to SOQL injection
 325 public static List<Account> searchAccounts(String userInput) {
 326     String query = 'SELECT Id, Name FROM Account WHERE Name = \'' + userInput + '\'';
 327     return Database.query(query);
 328 }
 329 
 330 // Attack: userInput = "test' OR '1'='1"
 331 // Results in: SELECT Id, Name FROM Account WHERE Name = 'test' OR '1'='1'
 332 // Returns ALL accounts!
 333 ```
 334 
 335 ---
 336 
 337 ### Solution 1: Bind Variables (Recommended)
 338 
 339 ```apex
 340 // ✅ SAFE: Use bind variables
 341 public static List<Account> searchAccounts(String userInput) {
 342     return [SELECT Id, Name FROM Account WHERE Name = :userInput WITH USER_MODE];
 343 }
 344 
 345 // Even with malicious input, it's treated as a literal string
 346 ```
 347 
 348 **Why it works**: Salesforce treats `:userInput` as a value, not executable SOQL.
 349 
 350 ---
 351 
 352 ### Solution 2: String.escapeSingleQuotes()
 353 
 354 **When dynamic SOQL is unavoidable** (rare cases):
 355 
 356 ```apex
 357 // ✅ SAFE: Escape user input
 358 public static List<Account> dynamicSearch(String userInput) {
 359     String sanitized = String.escapeSingleQuotes(userInput);
 360     String query = 'SELECT Id, Name FROM Account WHERE Name = \'' + sanitized + '\'';
 361     return Database.query(query);
 362 }
 363 ```
 364 
 365 **What it does**: Escapes single quotes (`'` → `\'`) to prevent breaking out of string literals.
 366 
 367 **Still prefer bind variables** - escapeSingleQuotes is a backup.
 368 
 369 ---
 370 
 371 ### Solution 3: Allowlist Validation
 372 
 373 **For field names, operators, or other dynamic query parts:**
 374 
 375 ```apex
 376 public static List<Account> sortedAccounts(String sortField) {
 377     // ✅ SAFE: Validate against allowlist
 378     Set<String> allowedFields = new Set<String>{'Name', 'Industry', 'AnnualRevenue'};
 379 
 380     if (!allowedFields.contains(sortField)) {
 381         throw new IllegalArgumentException('Invalid sort field');
 382     }
 383 
 384     String query = 'SELECT Id, Name, Industry FROM Account ORDER BY ' + sortField;
 385     return Database.query(query);
 386 }
 387 ```
 388 
 389 **Use case**: Dynamic ORDER BY, dynamic field selection (but NOT WHERE clause values).
 390 
 391 ---
 392 
 393 ### Dynamic SOQL Best Practices
 394 
 395 **Pattern: Safe Dynamic Query Builder**
 396 ```apex
 397 public class SafeQueryBuilder {
 398 
 399     private static final Set<String> ALLOWED_FIELDS = new Set<String>{
 400         'Id', 'Name', 'Industry', 'AnnualRevenue'
 401     };
 402 
 403     private static final Set<String> ALLOWED_OPERATORS = new Set<String>{
 404         '=', '!=', '<', '>', '<=', '>=', 'LIKE', 'IN'
 405     };
 406 
 407     public static List<Account> query(
 408         String field,
 409         String operator,
 410         String value
 411     ) {
 412         // Validate field
 413         if (!ALLOWED_FIELDS.contains(field)) {
 414             throw new IllegalArgumentException('Invalid field: ' + field);
 415         }
 416 
 417         // Validate operator
 418         if (!ALLOWED_OPERATORS.contains(operator)) {
 419             throw new IllegalArgumentException('Invalid operator: ' + operator);
 420         }
 421 
 422         // Use bind variable for value
 423         String query = 'SELECT Id, Name FROM Account WHERE ' + field + ' ' + operator + ' :value WITH USER_MODE';
 424         return Database.query(query);
 425     }
 426 }
 427 ```
 428 
 429 ---
 430 
 431 ## Security Checklist
 432 
 433 Use this checklist when generating or reviewing Apex code:
 434 
 435 ### CRUD/FLS
 436 
 437 - [ ] All SOQL queries use `WITH USER_MODE` (or `Security.stripInaccessible()` for pre-62.0)
 438 - [ ] DML operations check `isCreateable()`, `isUpdateable()`, `isDeletable()` OR use `WITH USER_MODE`
 439 - [ ] Custom fields have Permission Sets/Profiles granting FLS
 440 - [ ] System operations using `WITH SYSTEM_MODE` are documented with justification
 441 
 442 ### Sharing
 443 
 444 - [ ] All classes have explicit sharing keyword (`with sharing`, `without sharing`, or `inherited sharing`)
 445 - [ ] User-facing classes use `with sharing`
 446 - [ ] `without sharing` classes have documented justification
 447 - [ ] `without sharing` classes include Custom Permission checks
 448 
 449 ### SOQL Injection
 450 
 451 - [ ] No string concatenation in WHERE clauses with user input
 452 - [ ] All user input uses bind variables (`:variableName`)
 453 - [ ] Dynamic SOQL uses allowlist validation for field names/operators
 454 - [ ] `String.escapeSingleQuotes()` used if concatenation is unavoidable
 455 
 456 ### General Security
 457 
 458 - [ ] No hardcoded credentials or API keys (use Named Credentials)
 459 - [ ] No hardcoded Record IDs (use Custom Metadata or queries)
 460 - [ ] Sensitive data (SSN, PII) is encrypted at rest (Platform Encryption)
 461 - [ ] External callouts use Named Credentials, not plain URLs
 462 - [ ] Error messages don't leak sensitive information
 463 
 464 ---
 465 
 466 ## Advanced Security Patterns
 467 
 468 ### Custom Permissions
 469 
 470 **Check user has specific permission before dangerous operations:**
 471 
 472 ```apex
 473 public without sharing class DataDeletionService {
 474 
 475     public static void deleteAllTestData() {
 476         // Check Custom Permission
 477         if (!FeatureManagement.checkPermission('Delete_Test_Data')) {
 478             throw new SecurityException('Requires Delete_Test_Data permission');
 479         }
 480 
 481         // Safe to proceed
 482         delete [SELECT Id FROM Account WHERE Name LIKE 'TEST%'];
 483     }
 484 }
 485 ```
 486 
 487 **Create Custom Permission**: Setup → Custom Permissions → New
 488 
 489 ---
 490 
 491 ### Secure Remote Actions (@AuraEnabled)
 492 
 493 ```apex
 494 public with sharing class AccountController {
 495 
 496     @AuraEnabled(cacheable=true)
 497     public static List<Account> getAccounts() {
 498         // Runs with sharing + user mode = secure
 499         return [SELECT Id, Name FROM Account WITH USER_MODE LIMIT 50];
 500     }
 501 
 502     @AuraEnabled
 503     public static void updateAccount(Account acc) {
 504         // Verify user can update
 505         if (!Schema.sObjectType.Account.isUpdateable()) {
 506             throw new AuraHandledException('No update permission');
 507         }
 508 
 509         update acc;
 510     }
 511 }
 512 ```
 513 
 514 **Security Notes**:
 515 - Always use `with sharing` for `@AuraEnabled` methods
 516 - Use `WITH USER_MODE` in SOQL
 517 - Validate DML permissions before operations
 518 - Use `AuraHandledException` for friendly error messages
 519 
 520 ---
 521 
 522 ### Platform Events Security
 523 
 524 ```apex
 525 public with sharing class EventPublisher {
 526 
 527     public static void publishEvent(String message) {
 528         // Check if user can create Platform Events
 529         if (!Schema.sObjectType.MyEvent__e.isCreateable()) {
 530             throw new SecurityException('Cannot publish events');
 531         }
 532 
 533         MyEvent__e event = new MyEvent__e(
 534             Message__c = message
 535         );
 536 
 537         EventBus.publish(event);
 538     }
 539 }
 540 ```
 541 
 542 ---
 543 
 544 ## Common Security Vulnerabilities
 545 
 546 | Vulnerability | Example | Fix |
 547 |---------------|---------|-----|
 548 | **SOQL Injection** | `'WHERE Name = \'' + input + '\''` | Use bind variable `:input` |
 549 | **XSS (Cross-Site Scripting)** | Returning unsanitized HTML | Use `HTMLENCODE()` in VF or LWC escaping |
 550 | **Insecure Direct Object Reference** | Accepting record ID from user without checking access | Query with `WITH USER_MODE`, verify in `with sharing` |
 551 | **Hardcoded Credentials** | `String apiKey = 'abc123';` | Use Named Credentials |
 552 | **Missing FLS** | Directly querying fields without checking | Use `WITH USER_MODE` |
 553 | **Overly Permissive Sharing** | `without sharing` everywhere | Use `with sharing` by default |
 554 
 555 ---
 556 
 557 ## Testing Security
 558 
 559 ### Test User Mode
 560 
 561 ```apex
 562 @IsTest
 563 static void testUserModeEnforcesPermissions() {
 564     // Create user without Account read access
 565     User restrictedUser = createRestrictedUser();
 566 
 567     System.runAs(restrictedUser) {
 568         try {
 569             List<Account> accounts = [SELECT Id FROM Account WITH USER_MODE];
 570             Assert.fail('Expected QueryException for user without access');
 571         } catch (System.QueryException e) {
 572             Assert.isTrue(e.getMessage().contains('Insufficient privileges'));
 573         }
 574     }
 575 }
 576 ```
 577 
 578 ### Test Sharing Rules
 579 
 580 ```apex
 581 @IsTest
 582 static void testSharingEnforcement() {
 583     Account acc = new Account(Name = 'Test Account', OwnerId = UserInfo.getUserId());
 584     insert acc;
 585 
 586     // Create user who is NOT the owner
 587     User otherUser = createStandardUser();
 588 
 589     System.runAs(otherUser) {
 590         // Should NOT see account owned by different user
 591         List<Account> visible = [SELECT Id FROM Account WHERE Id = :acc.Id];
 592         Assert.areEqual(0, visible.size(), 'User should not see account due to sharing rules');
 593     }
 594 }
 595 ```
 596 
 597 ---
 598 
 599 ## Reference
 600 
 601 **Full Documentation**: See `references/` folder for comprehensive guides:
 602 - `security-guide.md` - Complete security reference (this is an extract)
 603 - `best-practices.md` - Includes security best practices
 604 - `code-review-checklist.md` - Security scoring criteria
 605 
 606 **Back to Main**: [SKILL.md](../SKILL.md)
