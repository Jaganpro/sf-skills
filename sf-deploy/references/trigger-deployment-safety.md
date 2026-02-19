<!-- Parent: sf-deploy/SKILL.md -->
   1 # Trigger Deployment Safety Guide
   2 
   3 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
   4 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
   5 
   6 ## Overview
   7 
   8 This guide covers deployment considerations for triggers, focusing on cascade failures, atomicity patterns, and async decoupling strategies.
   9 
  10 ---
  11 
  12 ## 1. Understanding Cascade Failures
  13 
  14 ### What Are Cascade Failures?
  15 
  16 When an exception in one trigger causes rollback of operations from preceding triggers in the chain.
  17 
  18 ```
  19 Account Insert → AccountTrigger → ContactTrigger → OpportunityTrigger
  20                      ✓               ✓                 ✗ (Exception)
  21 
  22                  All three operations ROLL BACK
  23 ```
  24 
  25 ### Default Behavior
  26 
  27 - Uncaught exceptions in triggers cause rollback of **all** operations in the transaction
  28 - This includes operations from other triggers that fired successfully
  29 - This behavior may or may not be desired depending on business requirements
  30 
  31 ### When Cascade Failure is DESIRED
  32 
  33 - All operations represent ONE atomic business process
  34 - Example: Order with line items must be complete or not exist
  35 - Same business unit/persona owns all the data
  36 
  37 ```apex
  38 // DESIRED cascade: Order and OrderItems must both succeed
  39 trigger OrderTrigger on Order__c (after insert) {
  40     // If this fails, we WANT the Order insert to roll back
  41     List<OrderItem__c> items = createDefaultLineItems(Trigger.new);
  42     insert items;  // Exception here rolls back Order insert - GOOD
  43 }
  44 ```
  45 
  46 ### When Cascade Failure is PROBLEMATIC
  47 
  48 - Operations represent INDEPENDENT business processes
  49 - Example: Creating account + syncing to external CRM
  50 - Different business units own different parts of the process
  51 
  52 ```apex
  53 // PROBLEMATIC cascade: CRM sync failure shouldn't prevent Account creation
  54 trigger AccountTrigger on Account (after insert) {
  55     // If CRM sync fails, Account creation also fails - BAD
  56     CRMService.syncNewAccounts(Trigger.new);  // Exception here rolls back Account
  57 }
  58 ```
  59 
  60 ---
  61 
  62 ## 2. Atomicity Patterns
  63 
  64 ### Explicit Savepoints
  65 
  66 Use `Database.setSavepoint()` for explicit transaction control within a single process.
  67 
  68 ```apex
  69 /**
  70  * Demonstrates explicit atomicity control for cross-object operations
  71  */
  72 public class AccountOwnership {
  73 
  74     /**
  75      * Reassigns all related records when account owner changes.
  76      * This is an ATOMIC operation - all changes succeed or all roll back.
  77      */
  78     public static void reassignRelatedRecords(
  79         List<Account> accountsWithNewOwner,
  80         Map<Id, Account> oldAccountsById
  81     ) {
  82         // Create savepoint for atomic operation
  83         Savepoint sp = Database.setSavepoint();
  84 
  85         try {
  86             Map<Id, Id> newOwnerByAccountId = buildOwnerMap(accountsWithNewOwner);
  87 
  88             // Step 1: Reassign opportunities
  89             reassignOpportunities(newOwnerByAccountId);
  90 
  91             // Step 2: Reassign cases
  92             reassignCases(newOwnerByAccountId);
  93 
  94             // Step 3: Create transition tasks
  95             createOwnerTransitionTasks(accountsWithNewOwner, oldAccountsById);
  96 
  97         } catch (Exception e) {
  98             // Rollback ALL changes if ANY step fails
  99             Database.rollback(sp);
 100 
 101             // Log the failure for investigation
 102             ErrorLogger.log('AccountOwnership.reassignRelatedRecords', e);
 103 
 104             // Re-throw to inform the caller
 105             throw new AccountOwnershipException(
 106                 'Failed to reassign related records: ' + e.getMessage()
 107             );
 108         }
 109     }
 110 }
 111 ```
 112 
 113 ### When to Use Savepoints
 114 
 115 | Scenario | Use Savepoint? | Reason |
 116 |----------|---------------|--------|
 117 | Multi-object update in same trigger | Yes | Ensures consistency |
 118 | Order + OrderItems creation | Yes | Business atomicity required |
 119 | Account + CRM sync | No | Use async decoupling instead |
 120 | Validation that spans objects | Yes | All-or-nothing validation |
 121 
 122 ---
 123 
 124 ## 3. Async Decoupling Patterns
 125 
 126 ### The Problem
 127 
 128 After-trigger logic that represents an independent business process can cause cascade failures.
 129 
 130 ### Solution: Queueable Jobs
 131 
 132 ```apex
 133 /**
 134  * Queueable job for processing that should not block the main transaction
 135  */
 136 public class AccountSyncQueueable implements Queueable, Database.AllowsCallouts {
 137 
 138     private Set<Id> accountIds;
 139     private TriggerOperation operationType;
 140 
 141     public AccountSyncQueueable(Set<Id> accountIds, TriggerOperation operationType) {
 142         this.accountIds = accountIds;
 143         this.operationType = operationType;
 144     }
 145 
 146     public void execute(QueueableContext context) {
 147         try {
 148             List<Account> accounts = [
 149                 SELECT Id, Name, Website, Industry, BillingAddress
 150                 FROM Account
 151                 WHERE Id IN :accountIds
 152             ];
 153 
 154             switch on operationType {
 155                 when AFTER_INSERT {
 156                     ExternalCRM.createAccounts(accounts);
 157                 }
 158                 when AFTER_UPDATE {
 159                     ExternalCRM.updateAccounts(accounts);
 160                 }
 161                 when AFTER_DELETE {
 162                     ExternalCRM.deleteAccounts(accountIds);
 163                 }
 164             }
 165 
 166         } catch (Exception e) {
 167             // Log error but don't fail - this is independent of main transaction
 168             ErrorLogger.log('AccountSyncQueueable', e, accountIds);
 169         }
 170     }
 171 }
 172 ```
 173 
 174 ### Usage in Trigger Handler
 175 
 176 ```apex
 177 public void afterInsert(List<Account> newAccounts, Map<Id, Account> newAccountsById) {
 178     // Synchronous operations that SHOULD block
 179     AccountNotifications.notifySalesTeam(newAccounts);
 180 
 181     // Async operations that should NOT block main transaction
 182     if (canEnqueueJob()) {
 183         System.enqueueJob(new AccountSyncQueueable(
 184             newAccountsById.keySet(),
 185             TriggerOperation.AFTER_INSERT
 186         ));
 187     }
 188 }
 189 
 190 private Boolean canEnqueueJob() {
 191     return !System.isBatch() &&
 192            !System.isFuture() &&
 193            Limits.getQueueableJobs() < Limits.getLimitQueueableJobs();
 194 }
 195 ```
 196 
 197 ### Platform Events for Maximum Decoupling
 198 
 199 ```apex
 200 // Publisher (in trigger)
 201 EventBus.publish(new Account_Changed__e(
 202     Account_Id__c = account.Id,
 203     Change_Type__c = 'INSERT'
 204 ));
 205 
 206 // Subscriber (separate trigger on platform event)
 207 trigger AccountChangedSubscriber on Account_Changed__e (after insert) {
 208     // Process events - failures here don't affect original transaction
 209     List<Id> accountIds = new List<Id>();
 210     for (Account_Changed__e event : Trigger.new) {
 211         accountIds.add(event.Account_Id__c);
 212     }
 213     // Sync to external system
 214 }
 215 ```
 216 
 217 ### Decoupling Decision Matrix
 218 
 219 | Business Process | Same User Persona? | Failure Impact | Recommendation |
 220 |-----------------|-------------------|----------------|----------------|
 221 | Order + Line Items | Yes | Must be atomic | Synchronous + Savepoint |
 222 | Account + Audit Log | Yes | Can retry | Queueable |
 223 | Account + External CRM | No | Independent | Platform Event |
 224 | Contact + Marketing Cloud | No | Independent | Platform Event |
 225 | Record + Email Notification | Yes | Non-critical | @future |
 226 
 227 ---
 228 
 229 ## 4. Pre-Deployment Checklist
 230 
 231 ### Trigger Cascade Analysis
 232 
 233 Before deploying triggers, analyze the cascade impact:
 234 
 235 ```
 236 CHECKLIST:
 237 □ List all triggers that fire on the same transaction
 238 □ Identify which operations are atomic (same business process)
 239 □ Identify which operations are independent (different processes)
 240 □ Verify exception handling in each trigger
 241 □ Check for recursive trigger prevention
 242 □ Review async job usage and limits
 243 ```
 244 
 245 ### Questions to Answer
 246 
 247 1. **What triggers will fire together?**
 248    - Map the full trigger chain for each DML operation
 249    - Include triggers on related objects (parent-child)
 250 
 251 2. **What happens if each trigger fails?**
 252    - Which operations will roll back?
 253    - Is that the desired behavior?
 254 
 255 3. **Are there external system calls?**
 256    - Should they be async?
 257    - What happens if they fail?
 258 
 259 4. **What about governor limits?**
 260    - How many DML statements in the chain?
 261    - How many SOQL queries?
 262    - Can bulk operations stay within limits?
 263 
 264 ---
 265 
 266 ## 5. Testing Cascade Scenarios
 267 
 268 ### Test Cascade Success
 269 
 270 ```apex
 271 @IsTest
 272 static void testTriggerChain_AllSucceed() {
 273     Test.startTest();
 274     Account acc = new Account(Name = 'Test');
 275     insert acc;  // Should fire AccountTrigger, create child records, etc.
 276     Test.stopTest();
 277 
 278     // Verify all expected records were created
 279     Assert.areEqual(1, [SELECT COUNT() FROM Contact WHERE AccountId = :acc.Id]);
 280     Assert.areEqual(1, [SELECT COUNT() FROM Task WHERE WhatId = :acc.Id]);
 281 }
 282 ```
 283 
 284 ### Test Cascade Failure (Expected Rollback)
 285 
 286 ```apex
 287 @IsTest
 288 static void testTriggerChain_ChildFailure_RollsBack() {
 289     // Configure scenario that will cause child trigger to fail
 290     Test.startTest();
 291     try {
 292         Account acc = new Account(Name = 'Trigger Failure Test');
 293         insert acc;
 294         Assert.fail('Expected DmlException');
 295     } catch (DmlException e) {
 296         // Expected - verify Account was NOT created
 297         Assert.areEqual(0, [SELECT COUNT() FROM Account WHERE Name = 'Trigger Failure Test']);
 298     }
 299     Test.stopTest();
 300 }
 301 ```
 302 
 303 ### Test Async Decoupling
 304 
 305 ```apex
 306 @IsTest
 307 static void testAccountInsert_CRMSyncAsync_DoesNotBlock() {
 308     // Even if CRM sync would fail, Account should be created
 309     Test.startTest();
 310     Account acc = new Account(Name = 'Async Test');
 311     insert acc;
 312     Test.stopTest();
 313 
 314     // Account should exist regardless of async job outcome
 315     Assert.areEqual(1, [SELECT COUNT() FROM Account WHERE Name = 'Async Test']);
 316 
 317     // Verify async job was enqueued
 318     Assert.areEqual(1, [SELECT COUNT() FROM AsyncApexJob WHERE JobType = 'Queueable']);
 319 }
 320 ```
 321 
 322 ---
 323 
 324 ## 6. Deployment Commands for Trigger Safety
 325 
 326 ### Validate Before Deploying
 327 
 328 ```bash
 329 # Always validate triggers before deploying
 330 sf project deploy start --dry-run \
 331     --source-dir force-app/main/default/triggers \
 332     --source-dir force-app/main/default/classes \
 333     --test-level RunLocalTests \
 334     --target-org alias
 335 ```
 336 
 337 ### Deploy with Test Coverage
 338 
 339 ```bash
 340 # Deploy triggers with their test classes
 341 sf project deploy start \
 342     --source-dir force-app/main/default/triggers \
 343     --source-dir force-app/main/default/classes \
 344     --test-level RunSpecifiedTests \
 345     --tests AccountTriggerTest,ContactTriggerTest \
 346     --target-org alias
 347 ```
 348 
 349 ### Verify Trigger Order
 350 
 351 After deployment, verify trigger execution order if you have multiple triggers on the same object:
 352 
 353 ```bash
 354 # Query trigger execution order (via Debug Logs)
 355 sf apex log tail --target-org alias
 356 
 357 # Or check in Setup: Object Manager → [Object] → Triggers
 358 ```
 359 
 360 ---
 361 
 362 ## Summary
 363 
 364 | Pattern | Use Case | Trade-off |
 365 |---------|----------|-----------|
 366 | **Default (Cascade)** | Atomic business processes | Simple but all-or-nothing |
 367 | **Savepoint** | Controlled rollback within handler | More code, explicit control |
 368 | **Queueable** | Independent async processes | Decoupled but async limits |
 369 | **Platform Event** | Maximum decoupling | More infrastructure |
 370 | **@future** | Simple fire-and-forget | Limited parameters |
 371 
 372 ### Key Principles
 373 
 374 1. **Make atomicity decisions explicit** - Don't rely on default behavior accidentally
 375 2. **Decouple independent processes** - Use async for cross-domain operations
 376 3. **Test cascade scenarios** - Verify both success and failure paths
 377 4. **Document trigger chains** - Future maintainers need to understand dependencies
 378 5. **Validate before deploying** - Use `--dry-run` to catch issues early
