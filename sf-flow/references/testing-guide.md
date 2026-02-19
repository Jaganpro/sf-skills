<!-- Parent: sf-flow/SKILL.md -->
   1 # Salesforce Flow Testing Guide
   2 
   3 > **Version**: 2.0.0
   4 > **Last Updated**: December 2025
   5 > **Purpose**: Comprehensive testing strategies for all Salesforce Flow types
   6 
   7 This guide provides structured testing approaches to ensure your flows work correctly under all conditions.
   8 
   9 ---
  10 
  11 ## Table of Contents
  12 
  13 1. [Test Path Coverage](#1-test-path-coverage)
  14 2. [Graduated Bulk Testing](#2-graduated-bulk-testing)
  15 3. [Edge Case Checklist](#3-edge-case-checklist)
  16 4. [User Context Testing](#4-user-context-testing)
  17 5. [Flow Type-Specific Testing](#5-flow-type-specific-testing)
  18 6. [Deployment Testing Sequence](#6-deployment-testing-sequence)
  19 7. [Regression Testing](#7-regression-testing)
  20 8. [Governor Limits Testing](#8-governor-limits-testing)
  21 9. [Post-Deployment Verification](#9-post-deployment-verification)
  22 
  23 ---
  24 
  25 ## 1. Test Path Coverage
  26 
  27 Before testing, map every possible route through your flow.
  28 
  29 ### Identify All Paths
  30 
  31 Document these for every flow:
  32 - **Decision element outcomes** (all branches, including default)
  33 - **Loop iterations** (0 items, 1 item, many items)
  34 - **Fault paths** (every DML element's error path)
  35 - **Conditional screens** (all visibility combinations)
  36 
  37 ### Test Matrix Template
  38 
  39 Create a test matrix for each flow:
  40 
  41 | Test Case ID | Path Description | Input Data | Expected Output | Actual Result | Pass/Fail |
  42 |--------------|------------------|------------|-----------------|---------------|-----------|
  43 | TC-001 | Happy path - all valid | Valid Account data | Record created | | |
  44 | TC-002 | Null input - missing required | AccountId = null | Error message shown | | |
  45 | TC-003 | Empty collection | 0 records from query | Loop skips, no DML | | |
  46 | TC-004 | Fault path - DML fails | Invalid record data | Error logged, user notified | | |
  47 | TC-005 | Decision branch A | Type = 'Customer' | Customer logic runs | | |
  48 | TC-006 | Decision branch B | Type = 'Partner' | Partner logic runs | | |
  49 
  50 ### Positive vs Negative Testing
  51 
  52 **Positive Testing**: Valid inputs → Expected successful outcomes
  53 - Correct data formats
  54 - Required fields populated
  55 - Valid record IDs
  56 
  57 **Negative Testing**: Invalid inputs → Graceful failure/error handling
  58 - Missing required values
  59 - Invalid formats
  60 - Non-existent record IDs
  61 - Null values where not expected
  62 
  63 ---
  64 
  65 ## 2. Graduated Bulk Testing
  66 
  67 Test in this progression to isolate issues:
  68 
  69 | Stage | Record Count | Purpose | What to Check |
  70 |-------|--------------|---------|---------------|
  71 | 1 | Single (1) | Logic correctness | Flow completes, correct output |
  72 | 2 | Small batch (10-20) | Basic bulkification | No obvious errors |
  73 | 3 | Medium batch (50-100) | Performance baseline | Execution time acceptable |
  74 | 4 | Large batch (200+) | Governor limit validation | No limit exceeded errors |
  75 | 5 | Stress test (10,000+) | Edge case (optional) | System stability |
  76 
  77 ### Why 200+ Records?
  78 
  79 - Record-triggered flows fire in **batches of 200**
  80 - Testing at this level ensures your flow survives real-world triggers
  81 - Data Loader operations commonly process 200 records per batch
  82 
  83 ### How to Bulk Test
  84 
  85 **Via Data Loader**:
  86 1. Create CSV with test data (200+ rows)
  87 2. Load via Data Loader or Workbench
  88 3. Monitor Debug Logs during execution
  89 
  90 **Via Apex**:
  91 ```apex
  92 @isTest
  93 static void testBulkTrigger() {
  94     List<Account> accounts = new List<Account>();
  95     for (Integer i = 0; i < 200; i++) {
  96         accounts.add(new Account(Name = 'Test ' + i));
  97     }
  98 
  99     Test.startTest();
 100     insert accounts;  // Triggers record-triggered flow
 101     Test.stopTest();
 102 
 103     // Assert expected outcomes
 104     System.assertEquals(200, [SELECT COUNT() FROM Account WHERE Name LIKE 'Test%']);
 105 }
 106 ```
 107 
 108 **Via Flow Simulator**:
 109 ```bash
 110 python3 validators/flow_simulator.py \
 111   force-app/main/default/flows/[FlowName].flow-meta.xml \
 112   --test-records 200
 113 ```
 114 
 115 ---
 116 
 117 ## 3. Edge Case Checklist
 118 
 119 Always test these scenarios:
 120 
 121 | Edge Case | Test Scenario | What to Verify |
 122 |-----------|---------------|----------------|
 123 | **Null values** | Required field is null | Error handling activates, no crash |
 124 | **Empty collections** | Get Records returns 0 | Loop skips gracefully, no null errors |
 125 | **Max field lengths** | 255-char text, max picklist | No truncation errors |
 126 | **Special characters** | `<>&"'` in text fields | No XML/formula breaks |
 127 | **Unicode/Emoji** | International characters, emojis | Proper encoding maintained |
 128 | **Date boundaries** | Year 2000, 2038, leap years | Date calculations work correctly |
 129 | **Negative numbers** | -1, MIN_INT values | Math operations handle correctly |
 130 | **Large numbers** | MAX_INT, currency limits | No overflow errors |
 131 | **Blank strings** | Empty string vs null | Handled differently if expected |
 132 | **Whitespace** | Leading/trailing spaces | Trimmed or preserved as designed |
 133 
 134 ### Creating Edge Case Test Data
 135 
 136 ```apex
 137 // Edge case test data
 138 Account edgeCaseAccount = new Account(
 139     Name = 'Test <Special> & "Characters"',           // Special chars
 140     Description = String.valueOf(Crypto.getRandomLong()),  // Max length test
 141     AnnualRevenue = -100                               // Negative number
 142 );
 143 ```
 144 
 145 ---
 146 
 147 ## 4. User Context Testing
 148 
 149 Test with multiple user profiles to verify security.
 150 
 151 ### Minimum Test Profiles
 152 
 153 | Profile | Purpose | What to Verify |
 154 |---------|---------|----------------|
 155 | **System Administrator** | Full access baseline | All features work |
 156 | **Standard User** | Limited permissions | FLS/CRUD enforced |
 157 | **Custom Profile** | Business-specific restrictions | Custom permissions work |
 158 | **Community User** (if applicable) | External access | Portal restrictions apply |
 159 
 160 ### What to Verify
 161 
 162 - **Field-Level Security (FLS)**: Restricted fields not visible
 163 - **Record sharing rules**: Access limited to owned/shared records
 164 - **Custom permissions**: `$Permission` global variable works
 165 - **System mode vs User mode**: Behaves as designed
 166 
 167 ### Testing with Different Users
 168 
 169 **CLI Approach**:
 170 ```bash
 171 # Authenticate as different user (sf org login user does not exist)
 172 sf org login web --alias standard-user-org
 173 # Note: To test as different users, authenticate separate orgs or use sf org login jwt with per-user credentials
 174 
 175 # Run tests/verify behavior
 176 ```
 177 
 178 **Apex Test Approach**:
 179 ```apex
 180 @isTest
 181 static void testAsStandardUser() {
 182     User standardUser = [SELECT Id FROM User WHERE Profile.Name = 'Standard User' LIMIT 1];
 183 
 184     System.runAs(standardUser) {
 185         // Test flow behavior as this user
 186         // Verify FLS/CRUD restrictions
 187     }
 188 }
 189 ```
 190 
 191 ### User Mode Flow Testing
 192 
 193 For flows running in User Mode, verify:
 194 - Users cannot access records they don't have permission to
 195 - Field-level security is enforced
 196 - Sharing rules are respected
 197 
 198 ### System Mode Flow Testing
 199 
 200 For flows running in System Mode:
 201 - Document justification for bypassing security
 202 - Verify flow doesn't expose sensitive data inappropriately
 203 - Test that security-sensitive operations are logged
 204 
 205 ---
 206 
 207 ## 5. Flow Type-Specific Testing
 208 
 209 ### Screen Flows
 210 
 211 **Launch Methods**:
 212 - Setup → Flows → Run
 213 - Direct URL: `https://[org].lightning.force.com/flow/[FlowApiName]`
 214 - Embedded in Lightning page
 215 
 216 **Test Checklist**:
 217 - [ ] All navigation paths (Next/Previous/Finish)
 218 - [ ] Input validation on each screen
 219 - [ ] Conditional field visibility
 220 - [ ] Multiple user profiles
 221 - [ ] Error messages display correctly
 222 - [ ] Progress indicator updates (if multi-step)
 223 - [ ] Back button behavior (data preserved or re-queried)
 224 
 225 ### Record-Triggered Flows
 226 
 227 **CRITICAL**: Always bulk test with 200+ records.
 228 
 229 **Test Checklist**:
 230 - [ ] Create single test record - verify trigger fires
 231 - [ ] Bulk test via Data Loader (200+ records)
 232 - [ ] Entry conditions work correctly
 233 - [ ] Before-save vs After-save timing correct
 234 - [ ] `$Record` and `$Record__Prior` values correct
 235 - [ ] Re-entry prevention working (if applicable)
 236 
 237 **Query Recent Executions**:
 238 ```bash
 239 sf data query --query "SELECT Id, Status, CreatedDate FROM FlowInterview WHERE FlowDeveloperName='[FlowName]' ORDER BY CreatedDate DESC LIMIT 10" --target-org [org]
 240 ```
 241 
 242 ### Autolaunched Flows
 243 
 244 **Test via Apex**:
 245 ```apex
 246 Map<String, Object> inputs = new Map<String, Object>{
 247     'inputRecordId' => testRecord.Id,
 248     'inputAmount' => 1000
 249 };
 250 
 251 Flow.Interview.My_Autolaunched_Flow flow = new Flow.Interview.My_Autolaunched_Flow(inputs);
 252 flow.start();
 253 
 254 // Get output variables
 255 String result = (String) flow.getVariableValue('outputResult');
 256 System.assertEquals('Success', result);
 257 ```
 258 
 259 **Test Checklist**:
 260 - [ ] Input variable mapping correct
 261 - [ ] Output variable values correct
 262 - [ ] Edge cases: nulls, empty collections, max values
 263 - [ ] Bulkification test (200+ records)
 264 - [ ] Governor limits not exceeded
 265 
 266 ### Scheduled Flows
 267 
 268 **Test Checklist**:
 269 - [ ] Verify schedule configuration in Setup → Scheduled Jobs
 270 - [ ] Manual "Run" test first (before enabling schedule)
 271 - [ ] Monitor Debug Logs during execution
 272 - [ ] Batch processing works correctly
 273 - [ ] Verify record selection criteria
 274 - [ ] Test with empty result set (no records match)
 275 - [ ] Cleanup/completion logic works
 276 
 277 **Verify Schedule**:
 278 ```bash
 279 sf data query --query "SELECT Id, CronJobDetail.Name, State, NextFireTime FROM CronTrigger WHERE CronJobDetail.Name LIKE '%[FlowName]%'" --target-org [org]
 280 ```
 281 
 282 ### Platform Event-Triggered Flows
 283 
 284 **Publish Test Event**:
 285 ```apex
 286 // Publish event
 287 My_Event__e event = new My_Event__e(
 288     Record_Id__c = testRecord.Id,
 289     Action__c = 'CREATE'
 290 );
 291 Database.SaveResult sr = EventBus.publish(event);
 292 System.assert(sr.isSuccess());
 293 ```
 294 
 295 **Test Checklist**:
 296 - [ ] Flow triggers on event publication
 297 - [ ] Event data accessible via `$Record`
 298 - [ ] High-volume scenarios work (multiple events)
 299 - [ ] Order of processing correct
 300 - [ ] Error handling works for failed events
 301 
 302 ---
 303 
 304 ## 6. Deployment Testing Sequence
 305 
 306 Follow this 5-step deployment validation:
 307 
 308 | Step | Action | Tool/Method | Success Criteria |
 309 |------|--------|-------------|------------------|
 310 | 1 | Validate XML structure | Flow validator scripts | No errors |
 311 | 2 | Deploy with checkOnly=true | `sf project deploy start --dry-run` | Deployment succeeds |
 312 | 3 | Verify package.xml | Manual review | API version matches flow |
 313 | 4 | Test with minimal data | 1-5 records in sandbox | Basic functionality works |
 314 | 5 | Test with bulk data | 200+ records in sandbox | Governor limits OK |
 315 
 316 ### Dry-Run Deployment
 317 
 318 ```bash
 319 # Validate without deploying
 320 sf project deploy start --source-dir force-app --dry-run --target-org sandbox
 321 
 322 # Check deployment status
 323 sf project deploy report --target-org sandbox
 324 ```
 325 
 326 ### Package.xml Verification
 327 
 328 Ensure API version matches:
 329 ```xml
 330 <?xml version="1.0" encoding="UTF-8"?>
 331 <Package xmlns="http://soap.sforce.com/2006/04/metadata">
 332     <types>
 333         <members>My_Flow</members>
 334         <name>Flow</name>
 335     </types>
 336     <version>65.0</version>  <!-- Must match flow's apiVersion -->
 337 </Package>
 338 ```
 339 
 340 ---
 341 
 342 ## 7. Regression Testing
 343 
 344 ### Document Test Cases
 345 
 346 Maintain a test case document for each flow:
 347 
 348 | Field | Description |
 349 |-------|-------------|
 350 | Test Case ID | Unique identifier (TC-001) |
 351 | Description | What this test verifies |
 352 | Pre-conditions | Required setup before test |
 353 | Steps | Numbered steps to execute |
 354 | Expected Result | What should happen |
 355 | Last Tested | Date and version |
 356 
 357 ### After Every Change
 358 
 359 Re-run **ALL** test cases, not just changed paths:
 360 - Logic changes can have cascading effects
 361 - Decision criteria changes affect multiple branches
 362 - Variable changes impact downstream elements
 363 
 364 ### Integration Testing
 365 
 366 Test interactions with:
 367 - **Other flows** on the same object (trigger order)
 368 - **Process Builders** (legacy - if still active)
 369 - **Apex triggers** (execution order matters)
 370 - **Validation rules** (may block flow DML)
 371 - **Workflow rules** (legacy - field updates)
 372 - **External integrations** (API calls, platform events)
 373 
 374 ### Automated Regression Testing
 375 
 376 Consider creating Apex test classes that:
 377 - Invoke flows programmatically
 378 - Assert expected outcomes
 379 - Run as part of CI/CD pipeline
 380 
 381 ```apex
 382 @isTest
 383 static void testFlowRegressionSuite() {
 384     // Setup test data
 385     Account testAccount = new Account(Name = 'Test');
 386     insert testAccount;
 387 
 388     // Invoke flow
 389     Map<String, Object> inputs = new Map<String, Object>{
 390         'recordId' => testAccount.Id
 391     };
 392     Flow.Interview.My_Flow flow = new Flow.Interview.My_Flow(inputs);
 393     flow.start();
 394 
 395     // Assert expected outcomes
 396     testAccount = [SELECT Status__c FROM Account WHERE Id = :testAccount.Id];
 397     System.assertEquals('Processed', testAccount.Status__c);
 398 }
 399 ```
 400 
 401 ---
 402 
 403 ## 8. Governor Limits Testing
 404 
 405 ### Limit Thresholds
 406 
 407 | Limit | Value | Warning Threshold |
 408 |-------|-------|-------------------|
 409 | SOQL Queries | 100 | 80 |
 410 | DML Statements | 150 | 120 |
 411 | Records Retrieved | 50,000 | 40,000 |
 412 | DML Rows | 10,000 | 8,000 |
 413 | CPU Time | 10,000 ms | 8,000 ms |
 414 | Heap Size | 6 MB | 5 MB |
 415 
 416 ### Monitoring During Tests
 417 
 418 **Debug Log Analysis**:
 419 1. Enable debug logs for running user
 420 2. Execute flow
 421 3. Review logs for `LIMIT_USAGE_FOR_NS`
 422 
 423 **Key Log Entries**:
 424 ```
 425 LIMIT_USAGE_FOR_NS|namespace||SOQL queries|15/100
 426 LIMIT_USAGE_FOR_NS|namespace||DML statements|5/150
 427 LIMIT_USAGE_FOR_NS|namespace||CPU time|1234/10000
 428 ```
 429 
 430 ### Governor Limit Prevention
 431 
 432 If approaching limits:
 433 - **SOQL**: Consolidate queries, add filters
 434 - **DML**: Batch operations, reduce elements
 435 - **CPU**: Simplify formulas, reduce loops
 436 - **Heap**: Process in smaller batches
 437 
 438 ---
 439 
 440 ## 9. Post-Deployment Verification
 441 
 442 ### Immediate Checks (Within 1 Hour)
 443 
 444 1. **Check Flow Status**: Setup → Process Automation → Flows
 445    - Verify flow is Active (if intended)
 446    - Verify correct version is active
 447 
 448 2. **Review Debug Logs**: Developer Console → Debug Logs
 449    - Check for unexpected errors
 450    - Verify expected execution paths
 451 
 452 3. **Monitor Flow Interviews**: Setup → Process Automation → Paused Flow Interviews
 453    - No unexpected paused interviews
 454 
 455 4. **Check Errors**: Setup → Process Automation → Flow Errors
 456    - No new errors from the deployed flow
 457 
 458 ### Short-Term Monitoring (First 24-48 Hours)
 459 
 460 - Monitor for user-reported issues
 461 - Check batch job completions (scheduled flows)
 462 - Review error email notifications
 463 - Verify integrations still working
 464 
 465 ### Query Flow Errors
 466 
 467 ```bash
 468 sf data query --query "SELECT Id, ElementApiName, ErrorMessage, FlowVersionId, InterviewGuid FROM FlowInterviewLogEntry WHERE CreatedDate = TODAY ORDER BY CreatedDate DESC LIMIT 20" --target-org [org]
 469 ```
 470 
 471 ---
 472 
 473 ## Quick Reference Commands
 474 
 475 ```bash
 476 # Deploy and test
 477 sf project deploy start --source-dir force-app --target-org sandbox
 478 
 479 # Query flow interviews
 480 sf data query --query "SELECT Id, Status FROM FlowInterview WHERE FlowDeveloperName='MyFlow' LIMIT 10" --target-org sandbox
 481 
 482 # Check scheduled jobs
 483 sf data query --query "SELECT Id, CronJobDetail.Name, State, NextFireTime FROM CronTrigger" --target-org sandbox
 484 
 485 # Authenticate as different user (sf org login user does not exist)
 486 sf org login web --alias test-user-org
 487 # Note: To test as different users, authenticate separate orgs or use sf org login jwt
 488 ```
 489 
 490 ---
 491 
 492 ## Flow Test CLI Commands
 493 
 494 ### Run Flow Tests
 495 
 496 > `sf flow run test` is a first-class CLI command for running Flow tests (available in sf CLI v2.122.6+).
 497 
 498 ```bash
 499 # Run all Flow tests
 500 sf flow run test -o TARGET_ORG --json
 501 
 502 # Run with code coverage
 503 sf flow run test -o TARGET_ORG --code-coverage --json
 504 
 505 # Run specific test classes
 506 sf flow run test --class-names MyFlowTest -o TARGET_ORG --json
 507 
 508 # Synchronous execution (waits for completion)
 509 sf flow run test -o TARGET_ORG --synchronous --json
 510 ```
 511 
 512 ### Combined Apex + Flow Test Runner
 513 
 514 > `sf logic run test` runs both Apex and Flow tests in a single command — useful for comprehensive CI/CD test suites.
 515 
 516 ```bash
 517 # Run combined Apex + Flow tests
 518 sf logic run test -o TARGET_ORG --json
 519 
 520 # Check results
 521 sf logic get test --test-run-id <id> -o TARGET_ORG --json
 522 ```
 523 
 524 ---
 525 
 526 ## Related Documentation
 527 
 528 - [Flow Best Practices](./flow-best-practices.md) - Design patterns and standards
 529 - [Testing Checklist](./testing-checklist.md) - Quick reference checklist
 530 - [Governance Checklist](./governance-checklist.md) - Security and compliance
