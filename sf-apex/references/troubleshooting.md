<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Troubleshooting Guide
   2 
   3 Comprehensive guide to debugging Apex code, LSP validation, dependency management, and common deployment issues.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [LSP-Based Validation (Auto-Fix Loop)](#lsp-based-validation-auto-fix-loop)
  10 2. [Cross-Skill Dependency Checklist](#cross-skill-dependency-checklist)
  11 3. [Common Deployment Errors](#common-deployment-errors)
  12 4. [Debug Logs and Monitoring](#debug-logs-and-monitoring)
  13 5. [Governor Limit Debugging](#governor-limit-debugging)
  14 6. [Test Failures](#test-failures)
  15 
  16 ---
  17 
  18 ## LSP-Based Validation (Auto-Fix Loop)
  19 
  20 The sf-apex skill includes Language Server Protocol (LSP) integration for real-time syntax validation. This enables Claude to automatically detect and fix Apex syntax errors during code authoring.
  21 
  22 ### How It Works
  23 
  24 1. **PostToolUse Hook**: After every Write/Edit operation on `.cls` or `.trigger` files, the LSP hook validates syntax
  25 2. **Apex Language Server**: Uses Salesforce's official `apex-jorje-lsp.jar` (from VS Code extension)
  26 3. **Auto-Fix Loop**: If errors are found, Claude receives diagnostics and auto-fixes them (max 3 attempts)
  27 4. **Two-Layer Validation**:
  28    - **LSP Validation**: Fast syntax checking (~500ms)
  29    - **150-Point Validation**: Semantic analysis for best practices
  30 
  31 ---
  32 
  33 ### Prerequisites
  34 
  35 For LSP validation to work, users must have:
  36 
  37 | Requirement | How to Install |
  38 |-------------|----------------|
  39 | **VS Code Salesforce Extension Pack** | VS Code → Extensions → "Salesforce Extension Pack" |
  40 | **Java 11+ (Adoptium recommended)** | https://adoptium.net/temurin/releases/ |
  41 
  42 **Verify Installation:**
  43 ```bash
  44 # Check VS Code extensions
  45 code --list-extensions | grep salesforce
  46 
  47 # Check Java version
  48 java -version
  49 # Should output: openjdk version "11.x.x" or higher
  50 ```
  51 
  52 ---
  53 
  54 ### Validation Flow
  55 
  56 ```
  57 User writes Apex code → Write/Edit tool executes
  58                               ↓
  59                     ┌─────────────────────────┐
  60                     │   LSP Validation (fast) │
  61                     │   Syntax errors only    │
  62                     └─────────────────────────┘
  63                               ↓
  64                     ┌─────────────────────────┐
  65                     │  150-Point Validation   │
  66                     │  Semantic best practices│
  67                     └─────────────────────────┘
  68                               ↓
  69                     Claude sees any errors and auto-fixes
  70 ```
  71 
  72 ---
  73 
  74 ### Sample LSP Error Output
  75 
  76 ```
  77 ============================================================
  78 🔍 APEX LSP VALIDATION RESULTS
  79    File: force-app/main/default/classes/MyClass.cls
  80    Attempt: 1/3
  81 ============================================================
  82 
  83 Found 1 error(s), 0 warning(s)
  84 
  85 ISSUES TO FIX:
  86 ----------------------------------------
  87 ❌ [ERROR] line 4: Missing ';' at 'System.debug' (source: apex)
  88 
  89 ACTION REQUIRED:
  90 Please fix the Apex syntax errors above and try again.
  91 (Attempt 1/3)
  92 ============================================================
  93 ```
  94 
  95 ---
  96 
  97 ### Common LSP Errors
  98 
  99 | Error | Cause | Fix |
 100 |-------|-------|-----|
 101 | Missing ';' at ... | Statement not terminated | Add semicolon at end of line |
 102 | Unexpected token ... | Syntax error | Check brackets, quotes, keywords |
 103 | Unknown type ... | Class/type not found | Ensure class exists, check spelling |
 104 | Method does not exist ... | Method call on wrong type | Verify method name and signature |
 105 | Variable not found ... | Undeclared variable | Declare variable before use |
 106 
 107 **Example Auto-Fix Loop:**
 108 
 109 **Attempt 1 (ERROR):**
 110 ```apex
 111 public class MyClass {
 112     public void doSomething() {
 113         System.debug('Hello')  // Missing semicolon
 114     }
 115 }
 116 ```
 117 
 118 **LSP Output:**
 119 ```
 120 ❌ [ERROR] line 3: Missing ';' at '}'
 121 ```
 122 
 123 **Attempt 2 (SUCCESS):**
 124 ```apex
 125 public class MyClass {
 126     public void doSomething() {
 127         System.debug('Hello');  // Fixed!
 128     }
 129 }
 130 ```
 131 
 132 **LSP Output:**
 133 ```
 134 ✅ VALIDATION PASSED
 135 ```
 136 
 137 ---
 138 
 139 ### Graceful Degradation
 140 
 141 If LSP is unavailable (no VS Code extension or Java), validation silently skips - the skill continues to work with only 150-point semantic validation.
 142 
 143 **Detection Logic:**
 144 ```python
 145 # hooks/scripts/post-tool-validate.py
 146 try:
 147     result = run_lsp_validation(file_path)
 148     if result.has_errors:
 149         print_errors(result)
 150 except LSPNotAvailableException:
 151     # Silent fallback - continue without LSP
 152     pass
 153 ```
 154 
 155 ---
 156 
 157 ### Manual LSP Validation
 158 
 159 **Run LSP validation manually from VS Code:**
 160 
 161 1. Open Apex class in VS Code
 162 2. View → Problems panel (`Cmd+Shift+M` / `Ctrl+Shift+M`)
 163 3. See syntax errors highlighted in real-time
 164 
 165 **Run from CLI (if available):**
 166 ```bash
 167 # Apex compilation happens automatically during deploy (no standalone compile command)
 168 sf project deploy start --metadata ApexClass:MyClass --target-org <alias> --dry-run --json
 169 ```
 170 
 171 ---
 172 
 173 ## Cross-Skill Dependency Checklist
 174 
 175 **Before deploying Apex code, verify these prerequisites:**
 176 
 177 | Prerequisite | Check Command | Required For |
 178 |--------------|---------------|--------------|
 179 | **TAF Package** | `sf package installed list --target-org alias` | TAF trigger pattern |
 180 | **Custom Fields** | `sf sobject describe --sobject Lead --target-org alias` | Field references in code |
 181 | **Permission Sets** | `sf org list metadata --metadata-type PermissionSet` | FLS for custom fields |
 182 | **Trigger_Action__mdt** | Check Setup → Custom Metadata Types | TAF trigger execution |
 183 | **Named Credentials** | Check Setup → Named Credentials | External callouts |
 184 | **Custom Settings** | Check Setup → Custom Settings | Bypass flags, configuration |
 185 
 186 ---
 187 
 188 ### Common Deployment Order
 189 
 190 ```
 191 1. sf-metadata: Create custom fields
 192    └─> sf sobject create --sobject-name Lead --fields "Score__c:Number(3,0)"
 193 
 194 2. sf-metadata: Create Permission Sets
 195    └─> Grant FLS on custom fields
 196 
 197 3. sf-deploy: Deploy fields + Permission Sets
 198    └─> sf project deploy start --metadata-dir force-app/main/default/objects
 199 
 200 4. sf-apex: Deploy Apex classes/triggers
 201    └─> sf project deploy start --metadata-dir force-app/main/default/classes
 202 
 203 5. sf-data: Create test data
 204    └─> sf data create record --sobject Account --values "Name='Test'"
 205 ```
 206 
 207 ---
 208 
 209 ### Verifying Prerequisites
 210 
 211 **Check TAF Package:**
 212 ```bash
 213 sf package installed list --target-org myorg --json
 214 ```
 215 
 216 **Output:**
 217 ```json
 218 {
 219   "result": [
 220     {
 221       "Id": "04t...",
 222       "SubscriberPackageName": "Trigger Actions Framework",
 223       "SubscriberPackageVersionNumber": "1.2.0"
 224     }
 225   ]
 226 }
 227 ```
 228 
 229 **If not installed:**
 230 ```bash
 231 sf package install --package 04tKZ000000gUEFYA2 --target-org myorg --wait 10
 232 ```
 233 
 234 ---
 235 
 236 **Check Custom Metadata Records:**
 237 ```bash
 238 sf data query --query "SELECT DeveloperName, Object__c, Apex_Class_Name__c FROM Trigger_Action__mdt" --target-org myorg
 239 ```
 240 
 241 **Expected Output:**
 242 ```
 243 DeveloperName          Object__c  Apex_Class_Name__c
 244 ─────────────────────────────────────────────────────
 245 TA_Account_SetDefaults  Account    TA_Account_SetDefaults
 246 TA_Lead_CalculateScore  Lead       TA_Lead_CalculateScore
 247 ```
 248 
 249 **If missing, create via sf-metadata skill.**
 250 
 251 ---
 252 
 253 ## Common Deployment Errors
 254 
 255 ### Error: "Field does not exist"
 256 
 257 **Cause**: Apex references a custom field that doesn't exist in target org.
 258 
 259 **Example:**
 260 ```
 261 Error: Field Account.Custom_Field__c does not exist
 262 ```
 263 
 264 **Fix:**
 265 1. Verify field exists:
 266    ```bash
 267    sf sobject describe --sobject Account --target-org myorg | grep Custom_Field__c
 268    ```
 269 
 270 2. Deploy field first:
 271    ```bash
 272    sf project deploy start --metadata CustomField:Account.Custom_Field__c --target-org myorg
 273    ```
 274 
 275 3. Then deploy Apex
 276 
 277 ---
 278 
 279 ### Error: "Invalid type: TriggerAction"
 280 
 281 **Cause**: TAF package not installed in target org.
 282 
 283 **Example:**
 284 ```
 285 Error: Invalid type: TriggerAction.BeforeInsert
 286 ```
 287 
 288 **Fix:**
 289 ```bash
 290 # Install TAF package
 291 sf package install --package 04tKZ000000gUEFYA2 --target-org myorg --wait 10
 292 
 293 # Verify
 294 sf package installed list --target-org myorg
 295 ```
 296 
 297 ---
 298 
 299 ### Error: "Insufficient access rights"
 300 
 301 **Cause**: Deploy user lacks permissions.
 302 
 303 **Example:**
 304 ```
 305 Error: Insufficient access rights on object id
 306 ```
 307 
 308 **Fix:**
 309 1. Verify user has "Modify All Data" or is System Administrator
 310 2. Or add specific permissions to user's profile:
 311    ```bash
 312    sf org assign permset --name "Deploy_Permissions" --target-org myorg
 313    ```
 314 
 315 ---
 316 
 317 ### Error: "Test coverage less than 75%"
 318 
 319 **Cause**: Production deployment requires 75% test coverage.
 320 
 321 **Example:**
 322 ```
 323 Error: Average test coverage across all Apex Classes and Triggers is 68%, at least 75% required
 324 ```
 325 
 326 **Fix:**
 327 1. Identify uncovered classes:
 328    ```bash
 329    sf apex run test --code-coverage --result-format human --target-org myorg
 330    ```
 331 
 332 2. Add missing test classes
 333 
 334 3. Ensure tests have assertions:
 335    ```apex
 336    Assert.areEqual(expected, actual, 'Message');
 337    ```
 338 
 339 ---
 340 
 341 ### Error: "FIELD_CUSTOM_VALIDATION_EXCEPTION"
 342 
 343 **Cause**: Apex code violates validation rule.
 344 
 345 **Example:**
 346 ```
 347 Error: FIELD_CUSTOM_VALIDATION_EXCEPTION: Annual Revenue must be greater than 0
 348 ```
 349 
 350 **Fix:**
 351 1. Check validation rules:
 352    ```bash
 353    sf data query --query "SELECT ValidationName, ErrorDisplayField, ErrorMessage FROM ValidationRule WHERE EntityDefinition.QualifiedApiName = 'Account'" --target-org myorg
 354    ```
 355 
 356 2. Update Apex to satisfy validation logic:
 357    ```apex
 358    acc.AnnualRevenue = 1000000;  // Ensure > 0
 359    ```
 360 
 361 ---
 362 
 363 ## Debug Logs and Monitoring
 364 
 365 ### Enable Debug Logs
 366 
 367 **Via Setup:**
 368 1. Setup → Debug Logs
 369 2. Click "New"
 370 3. Select User
 371 4. Set expiration (max 24 hours)
 372 5. Set log levels:
 373    - Apex Code: `DEBUG`
 374    - Database: `INFO`
 375    - Workflow: `INFO`
 376 
 377 **Via CLI:**
 378 ```bash
 379 # Create trace flag
 380 sf data create record --sobject TraceFlag --values "StartDate=2025-01-01T00:00:00Z EndDate=2025-01-02T00:00:00Z LogType=USER_DEBUG TracedEntityId=<USER_ID> DebugLevelId=<DEBUG_LEVEL_ID>" --target-org myorg
 381 
 382 # Tail logs in real-time
 383 sf apex tail log --target-org myorg
 384 ```
 385 
 386 ---
 387 
 388 ### Reading Debug Logs
 389 
 390 **Structure:**
 391 ```
 392 HH:MM:SS.SSS|EXECUTION_STARTED
 393 HH:MM:SS.SSS|CODE_UNIT_STARTED|AccountService
 394 HH:MM:SS.SSS|USER_DEBUG|[3]|DEBUG|Processing account: Test
 395 HH:MM:SS.SSS|SOQL_EXECUTE_BEGIN|[5]|SELECT Id FROM Account
 396 HH:MM:SS.SSS|SOQL_EXECUTE_END|[5]|Rows:10
 397 HH:MM:SS.SSS|DML_BEGIN|[8]|Op:Update|Type:Account|Rows:10
 398 HH:MM:SS.SSS|DML_END|[8]
 399 HH:MM:SS.SSS|LIMIT_USAGE_FOR_NS|(default)|SOQL:1/100|DML:1/150
 400 HH:MM:SS.SSS|EXECUTION_FINISHED
 401 ```
 402 
 403 **Key Events:**
 404 - `USER_DEBUG`: Your `System.debug()` statements
 405 - `SOQL_EXECUTE_*`: SOQL queries
 406 - `DML_BEGIN/END`: DML operations
 407 - `LIMIT_USAGE_FOR_NS`: Governor limit consumption
 408 
 409 ---
 410 
 411 ### Strategic Debug Statements
 412 
 413 ```apex
 414 public static void processAccounts(List<Account> accounts) {
 415     System.debug(LoggingLevel.INFO, '=== START processAccounts ===');
 416     System.debug(LoggingLevel.INFO, 'Input size: ' + accounts.size());
 417 
 418     // Log limits BEFORE expensive operation
 419     System.debug('SOQL before: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
 420 
 421     List<Contact> contacts = [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds];
 422 
 423     // Log limits AFTER
 424     System.debug('SOQL after: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
 425     System.debug('Contacts retrieved: ' + contacts.size());
 426 
 427     System.debug(LoggingLevel.INFO, '=== END processAccounts ===');
 428 }
 429 ```
 430 
 431 ---
 432 
 433 ### Log Levels
 434 
 435 | Level | When to Use | Example |
 436 |-------|-------------|---------|
 437 | `ERROR` | Critical failures | `System.debug(LoggingLevel.ERROR, 'DML failed: ' + e.getMessage())` |
 438 | `WARN` | Potential issues | `System.debug(LoggingLevel.WARN, 'No contacts found for account')` |
 439 | `INFO` | Key milestones | `System.debug(LoggingLevel.INFO, 'Processing 251 accounts')` |
 440 | `DEBUG` | Detailed traces | `System.debug(LoggingLevel.DEBUG, 'Variable value: ' + var)` |
 441 | `FINE`/`FINER`/`FINEST` | Very detailed | Rarely used |
 442 
 443 ---
 444 
 445 ## Governor Limit Debugging
 446 
 447 ### Monitoring Limits in Code
 448 
 449 ```apex
 450 public static void expensiveOperation() {
 451     System.debug('=== LIMIT CHECK ===');
 452     System.debug('SOQL Queries: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
 453     System.debug('DML Statements: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
 454     System.debug('DML Rows: ' + Limits.getDmlRows() + '/' + Limits.getLimitDmlRows());
 455     System.debug('CPU Time: ' + Limits.getCpuTime() + '/' + Limits.getLimitCpuTime());
 456     System.debug('Heap Size: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize());
 457 }
 458 ```
 459 
 460 ---
 461 
 462 ### Common Limit Exceptions
 463 
 464 **SOQL Limit (100 queries):**
 465 ```
 466 System.LimitException: Too many SOQL queries: 101
 467 ```
 468 
 469 **Fix**: Query BEFORE loops, use Maps for lookups.
 470 
 471 **DML Limit (150 statements):**
 472 ```
 473 System.LimitException: Too many DML statements: 151
 474 ```
 475 
 476 **Fix**: Collect records in List, DML AFTER loop.
 477 
 478 **CPU Time Limit (10 seconds):**
 479 ```
 480 System.LimitException: Maximum CPU time exceeded
 481 ```
 482 
 483 **Fix**: Optimize loops, move expensive operations to async, reduce complexity.
 484 
 485 **Heap Size Limit (6 MB):**
 486 ```
 487 System.LimitException: Apex heap size too large
 488 ```
 489 
 490 **Fix**: Process in batches, clear collections when done, avoid storing large objects in memory.
 491 
 492 ---
 493 
 494 ### Using Limits Class for Alerts
 495 
 496 ```apex
 497 public static void monitoredOperation() {
 498     // Warn if approaching 80% of limit
 499     Integer queriesUsed = Limits.getQueries();
 500     Integer queriesLimit = Limits.getLimitQueries();
 501 
 502     if (queriesUsed > queriesLimit * 0.8) {
 503         System.debug(LoggingLevel.WARN, 'Approaching SOQL limit: ' + queriesUsed + '/' + queriesLimit);
 504     }
 505 
 506     // Expensive operation
 507     List<Account> accounts = [SELECT Id FROM Account];
 508 }
 509 ```
 510 
 511 ---
 512 
 513 ## Test Failures
 514 
 515 ### Common Test Failure Patterns
 516 
 517 **Pattern 1: No assertions**
 518 ```apex
 519 @IsTest
 520 static void testCreateAccount() {
 521     Account acc = new Account(Name = 'Test');
 522     insert acc;
 523     // PASSES even if logic is broken!
 524 }
 525 ```
 526 
 527 **Fix**: Add assertions
 528 ```apex
 529 @IsTest
 530 static void testCreateAccount() {
 531     Account acc = new Account(Name = 'Test', Industry = 'Tech');
 532     insert acc;
 533 
 534     Account inserted = [SELECT Id, Industry FROM Account WHERE Id = :acc.Id];
 535     Assert.areEqual('Tech', inserted.Industry, 'Industry should be set');
 536 }
 537 ```
 538 
 539 ---
 540 
 541 **Pattern 2: Order dependency**
 542 ```apex
 543 @IsTest
 544 static void test1() {
 545     insert new Account(Name = 'Shared');
 546 }
 547 
 548 @IsTest
 549 static void test2() {
 550     // Assumes test1 ran first - BRITTLE!
 551     Account acc = [SELECT Id FROM Account WHERE Name = 'Shared'];
 552 }
 553 ```
 554 
 555 **Fix**: Use @TestSetup or create data in each test
 556 ```apex
 557 @TestSetup
 558 static void setup() {
 559     insert new Account(Name = 'Shared');
 560 }
 561 
 562 @IsTest
 563 static void test2() {
 564     Account acc = [SELECT Id FROM Account WHERE Name = 'Shared'];  // Safe
 565 }
 566 ```
 567 
 568 ---
 569 
 570 **Pattern 3: Insufficient permissions**
 571 ```apex
 572 @IsTest
 573 static void testRestrictedUser() {
 574     User u = TestDataFactory.createStandardUser();
 575 
 576     System.runAs(u) {
 577         // Fails if user lacks permission
 578         insert new Account(Name = 'Test');
 579     }
 580 }
 581 ```
 582 
 583 **Fix**: Grant necessary permissions
 584 ```apex
 585 @TestSetup
 586 static void setup() {
 587     User u = TestDataFactory.createStandardUser();
 588     insert new PermissionSetAssignment(
 589         AssigneeId = u.Id,
 590         PermissionSetId = [SELECT Id FROM PermissionSet WHERE Name = 'Account_Create'].Id
 591     );
 592 }
 593 ```
 594 
 595 ---
 596 
 597 ### Running Tests
 598 
 599 **VS Code:**
 600 1. Open test class
 601 2. Click "Run Test" above `@IsTest` method
 602 3. View results in Output panel
 603 
 604 **CLI:**
 605 ```bash
 606 # Run specific test class
 607 sf apex run test --tests AccountServiceTest --result-format human --code-coverage --target-org myorg
 608 
 609 # Run all tests
 610 sf apex run test --test-level RunLocalTests --result-format human --code-coverage --target-org myorg
 611 
 612 # Run tests and generate coverage report
 613 sf apex run test --test-level RunLocalTests --code-coverage --result-format json --output-dir test-results --target-org myorg
 614 ```
 615 
 616 **Output:**
 617 ```
 618 Test Summary
 619 ════════════
 620 Outcome              Passed
 621 Tests Ran            12
 622 Pass Rate            100%
 623 Fail Rate            0%
 624 Skip Rate            0%
 625 Test Run Coverage    92%
 626 Org Wide Coverage    85%
 627 Test Execution Time  1234 ms
 628 
 629 Coverage Warnings
 630 ═════════════════
 631 AccountService.cls  Line 45 not covered by tests
 632 ```
 633 
 634 ---
 635 
 636 ## Debugging Strategies
 637 
 638 ### 1. Binary Search for Errors
 639 
 640 When unsure where error occurs, add debug statements at midpoints:
 641 
 642 ```apex
 643 public static void complexOperation() {
 644     System.debug('START');
 645 
 646     // Part 1
 647     List<Account> accounts = [SELECT Id FROM Account];
 648     System.debug('CHECKPOINT 1: Retrieved ' + accounts.size() + ' accounts');
 649 
 650     // Part 2
 651     for (Account acc : accounts) {
 652         acc.Industry = 'Tech';
 653     }
 654     System.debug('CHECKPOINT 2: Updated accounts');
 655 
 656     // Part 3
 657     update accounts;
 658     System.debug('CHECKPOINT 3: DML complete');
 659 
 660     System.debug('END');
 661 }
 662 ```
 663 
 664 Run and check logs to see which checkpoint fails.
 665 
 666 ---
 667 
 668 ### 2. Isolate in Anonymous Apex
 669 
 670 **Execute in Developer Console:**
 671 ```apex
 672 Account acc = new Account(Name = 'Debug Test', Industry = 'Tech');
 673 insert acc;
 674 
 675 System.debug('Account ID: ' + acc.Id);
 676 System.debug('Industry: ' + acc.Industry);
 677 ```
 678 
 679 Open Execute Anonymous Window (`Ctrl+E`), paste code, check logs.
 680 
 681 ---
 682 
 683 ### 3. Unit Test in Isolation
 684 
 685 **Create minimal test case:**
 686 ```apex
 687 @IsTest
 688 static void debugIssue() {
 689     Account acc = new Account(Name = 'Test', AnnualRevenue = null);
 690 
 691     Test.startTest();
 692     AccountService.calculateScore(acc);  // Isolated method
 693     Test.stopTest();
 694 
 695     System.debug('Score: ' + acc.Score__c);
 696 }
 697 ```
 698 
 699 Easier to debug than full integration test.
 700 
 701 ---
 702 
 703 ## Reference
 704 
 705 **Full Documentation**: See `references/` folder for comprehensive guides:
 706 - `best-practices.md` - Debugging best practices
 707 - `testing-guide.md` - Test troubleshooting
 708 - `code-review-checklist.md` - Quality checklist
 709 
 710 **Back to Main**: [SKILL.md](../SKILL.md)
