<!-- Parent: sf-flow/SKILL.md -->
   1 # Salesforce Flow Best Practices Guide
   2 
   3 > **Version**: 2.0.0
   4 > **Last Updated**: December 2025
   5 > **Applies to**: All flow types (Screen, Record-Triggered, Scheduled, Platform Event, Autolaunched)
   6 
   7 This guide consolidates best practices for building maintainable, performant, and secure Salesforce Flows.
   8 
   9 ---
  10 
  11 ## Table of Contents
  12 
  13 **Strategy & Planning**
  14 1. [When NOT to Use Flow](#1-when-not-to-use-flow) ⚠️ NEW
  15 2. [Pre-Development Planning](#2-pre-development-planning) ⚠️ NEW
  16 3. [When to Escalate to Apex](#3-when-to-escalate-to-apex) ⚠️ NEW
  17 
  18 **Flow Element Design**
  19 4. [Flow Element Organization](#4-flow-element-organization)
  20 5. [Using $Record in Record-Triggered Flows](#5-using-record-in-record-triggered-flows)
  21 6. [Querying Relationship Data](#6-querying-relationship-data)
  22 7. [Query Optimization](#7-query-optimization)
  23 8. [Transform vs Loop Elements](#8-transform-vs-loop-elements)
  24 9. [Collection Filter Optimization](#9-collection-filter-optimization)
  25 
  26 **Architecture & Integration**
  27 10. [When to Use Subflows](#10-when-to-use-subflows)
  28 11. [Custom Metadata for Business Logic](#11-custom-metadata-for-business-logic) ⚠️ NEW
  29 
  30 **Error Handling & Transactions**
  31 12. [Three-Tier Error Handling](#12-three-tier-error-handling)
  32 13. [Multi-Step DML Rollback Strategy](#13-multi-step-dml-rollback-strategy)
  33 14. [Transaction Management](#14-transaction-management)
  34 
  35 **User Experience & Maintenance**
  36 15. [Screen Flow UX Best Practices](#15-screen-flow-ux-best-practices)
  37 16. [Bypass Mechanism for Data Loads](#16-bypass-mechanism-for-data-loads)
  38 17. [Flow Activation Guidelines](#17-flow-activation-guidelines)
  39 18. [Variable Naming Conventions](#18-variable-naming-conventions)
  40 19. [Flow & Element Descriptions](#19-flow--element-descriptions) ⚠️ NEW
  41 
  42 ---
  43 
  44 ## 1. When NOT to Use Flow
  45 
  46 Before building a Flow, evaluate whether simpler declarative tools might better serve your needs. Flows add maintenance overhead and consume runtime resources—use them when their power is needed.
  47 
  48 ### Prefer Declarative Configuration Over Flow
  49 
  50 | Requirement | Better Alternative | Why |
  51 |-------------|-------------------|-----|
  52 | Same-record field calculation | **Formula Field** | No runtime cost, always current, no maintenance |
  53 | Data validation with error message | **Validation Rule** | Built-in UI, simpler to debug, better performance |
  54 | Parent aggregate from children | **Roll-Up Summary Field** | Automatic, real-time, zero maintenance |
  55 | Field defaulting on create | **Field Default Value** | Native platform feature, cleaner |
  56 | Simple required field logic | **Page Layout / Field-Level Security** | Declarative, no code |
  57 | Conditional field visibility | **Dynamic Forms** | UI-native, better UX |
  58 | Simple field updates on related records | **Workflow Rule** (if already in use) | Simpler for basic use cases |
  59 
  60 ### When Flow IS the Right Choice
  61 
  62 | Scenario | Why Flow |
  63 |----------|----------|
  64 | Complex multi-object updates | Orchestrate related changes in transaction |
  65 | Conditional branching (3+ paths) | Decision logic beyond validation rules |
  66 | User interaction required | Screen Flows for guided processes |
  67 | Scheduled automation | Time-based execution |
  68 | Platform Event handling | Real-time event processing |
  69 | Integration callouts | HTTP callouts with error handling |
  70 | Complex approval routing | Dynamic approval matrix |
  71 
  72 ### Decision Checklist
  73 
  74 Before creating a Flow, ask:
  75 
  76 - [ ] Can a Formula Field calculate this value?
  77 - [ ] Can a Validation Rule enforce this business requirement?
  78 - [ ] Is this a simple "if changed, update field" scenario? (Consider Process Builder migration later)
  79 - [ ] Does this require user interaction? (If no, consider automation alternatives)
  80 - [ ] Will this run on every record save? (High-frequency = high scrutiny needed)
  81 
  82 > **Rule of Thumb**: If you can solve it with clicks (formula, validation, roll-up), do that first. Flows are powerful but add complexity.
  83 
  84 ---
  85 
  86 ## 2. Pre-Development Planning
  87 
  88 Define business requirements and map logic **before** opening Flow Builder. Planning prevents rework and ensures stakeholder alignment.
  89 
  90 ### Step 1: Document Requirements
  91 
  92 Before building, answer these questions:
  93 
  94 | Question | Purpose |
  95 |----------|---------|
  96 | What triggers this automation? | Defines Flow type (Record-Triggered, Scheduled, Screen) |
  97 | What are ALL outcomes? | Identifies branches (happy path + edge cases) |
  98 | Who are the affected users? | Determines User vs System Mode |
  99 | What objects/fields are involved? | Identifies dependencies |
 100 | Are there existing automations? | Prevents conflicts/duplicates |
 101 
 102 ### Step 2: Visual Mapping
 103 
 104 Sketch your Flow logic before building. Recommended tools:
 105 
 106 | Tool | Cost | Best For |
 107 |------|------|----------|
 108 | **draw.io / diagrams.net** | Free | Quick flowcharts, team sharing |
 109 | **Lucidchart** | Paid | Professional diagrams, Salesforce shapes |
 110 | **Miro / FigJam** | Freemium | Collaborative whiteboarding |
 111 | **Paper/Whiteboard** | Free | Initial brainstorming |
 112 
 113 ### Step 3: Identify Dependencies
 114 
 115 | Dependency Type | Check Before Building |
 116 |-----------------|----------------------|
 117 | Custom Objects/Fields | Do they exist? Create with sf-metadata first |
 118 | Custom Metadata Types | Bypass settings, thresholds, config values |
 119 | Permission Sets | Required for System Mode considerations |
 120 | External Systems | Callout endpoints, credentials |
 121 | Other Automations | Triggers, Process Builders, other Flows on same object |
 122 
 123 ### Step 4: Define Test Scenarios
 124 
 125 Before building, list your test cases:
 126 
 127 ```
 128 Test Scenarios for: Auto_Lead_Assignment
 129 ├── Happy Path: New Lead with valid data → Assigns correctly
 130 ├── Edge Case: Lead missing required field → Handles gracefully
 131 ├── Bulk Test: 200+ Leads created → No governor limits
 132 ├── Permission Test: User without edit access → Appropriate error
 133 └── Conflict Test: Existing trigger on Lead → No infinite loop
 134 ```
 135 
 136 ### Planning Deliverable Template
 137 
 138 ```
 139 FLOW PLANNING DOCUMENT
 140 ═══════════════════════════════════════════════════
 141 
 142 Flow Name: [Auto_Lead_Assignment]
 143 Type: Record-Triggered (After Save)
 144 Object: Lead
 145 Trigger: On Create, On Update (when Status changes)
 146 
 147 BUSINESS REQUIREMENTS:
 148 1. Assign leads to reps based on territory
 149 2. Send notification email to assigned rep
 150 3. Update Lead Status to "Assigned"
 151 
 152 ENTRY CONDITIONS:
 153 - Status changed to 'New' OR Record is new
 154 - NOT assigned to a rep yet
 155 
 156 DECISION LOGIC:
 157 - If Region = 'West' → Assign to User A
 158 - If Region = 'East' → Assign to User B
 159 - Else → Assign to Queue
 160 
 161 ERROR HANDLING:
 162 - If assignment fails → Log error, don't block save
 163 
 164 DEPENDENCIES:
 165 - Custom field: Region__c (exists ✓)
 166 - Queue: Unassigned_Leads (exists ✓)
 167 ═══════════════════════════════════════════════════
 168 ```
 169 
 170 ---
 171 
 172 ## 3. When to Escalate to Apex
 173 
 174 Flow is powerful, but Apex is sometimes the better tool. Know when to escalate to Invocable Apex.
 175 
 176 ### Escalation Decision Matrix
 177 
 178 | Scenario | Why Apex is Better |
 179 |----------|-------------------|
 180 | **>5 nested decision branches** | Flow becomes unreadable; Apex switch/if is cleaner |
 181 | **Complex math/string manipulation** | Apex is more expressive (regex, math libraries) |
 182 | **External HTTP callouts** | Better error handling, retry logic, timeout control |
 183 | **Database transactions with partial commit** | Apex Savepoints for precise rollback control |
 184 | **Complex data transformations** | Apex collections (Maps, Sets) are more powerful |
 185 | **Performance-critical bulk operations** | Apex is faster for large datasets (10K+ records) |
 186 | **Unit testing requirements** | Apex test classes provide better coverage metrics |
 187 | **Governor limit gymnastics** | Apex gives finer control over limits |
 188 
 189 ### Red Flags: When Flow is Fighting You
 190 
 191 If you encounter these patterns, consider Apex:
 192 
 193 ```
 194 🚩 RED FLAGS (Consider Apex Instead)
 195 ═══════════════════════════════════════════════════
 196 
 197 ❌ Building workarounds for Flow limitations
 198    → "I need to loop twice because Flow can't..."
 199 
 200 ❌ Flow canvas is unreadably complex
 201    → More than 20 elements, crossing connectors
 202 
 203 ❌ Performance issues at scale
 204    → Flow times out with realistic data volumes
 205 
 206 ❌ Need precise error messages
 207    → $Flow.FaultMessage isn't granular enough
 208 
 209 ❌ Complex JSON/XML parsing
 210    → Flow formulas are awkward for nested structures
 211 
 212 ❌ Multi-object transactions with partial rollback
 213    → Flow's all-or-nothing isn't sufficient
 214 ═══════════════════════════════════════════════════
 215 ```
 216 
 217 ### The Hybrid Approach: Flow + Invocable Apex
 218 
 219 Best practice: Use Flow for orchestration, Apex for complexity.
 220 
 221 ```
 222 ┌─────────────────────────────────────────────────────────────┐
 223 │ HYBRID PATTERN: Flow orchestrates, Apex handles complexity │
 224 └─────────────────────────────────────────────────────────────┘
 225 
 226 Flow (Auto_Process_Order):
 227 ├── Start: Record-Triggered (Order)
 228 ├── Decision: Is Complex Processing Needed?
 229 │   ├── Yes → Apex Action: ProcessComplexOrder (Invocable)
 230 │   └── No  → Simple Assignment Elements
 231 ├── Get Records: Related Line Items
 232 ├── Apex Action: CalculateTaxAndDiscount (Invocable)
 233 └── Update Records: Order with calculated values
 234 
 235 Benefits:
 236 ✓ Flow handles simple orchestration (readable)
 237 ✓ Apex handles complex math (maintainable)
 238 ✓ Apex is unit-testable (reliable)
 239 ✓ Admins can modify flow logic (accessible)
 240 ```
 241 
 242 ### Invocable Apex Template
 243 
 244 When escalating to Apex, use this pattern:
 245 
 246 ```apex
 247 /**
 248  * Invocable Apex for Flow: Complex Order Processing
 249  * Called from: Auto_Process_Order Flow
 250  */
 251 public class OrderProcessor {
 252 
 253     @InvocableMethod(
 254         label='Process Complex Order'
 255         description='Calculates tax, discounts, and validates inventory'
 256         category='Order Management'
 257     )
 258     public static List<OutputWrapper> processOrders(List<InputWrapper> inputs) {
 259         List<OutputWrapper> results = new List<OutputWrapper>();
 260 
 261         for (InputWrapper input : inputs) {
 262             OutputWrapper output = new OutputWrapper();
 263             try {
 264                 // Complex logic here
 265                 output.isSuccess = true;
 266                 output.message = 'Processed successfully';
 267             } catch (Exception e) {
 268                 output.isSuccess = false;
 269                 output.message = e.getMessage();
 270             }
 271             results.add(output);
 272         }
 273         return results;
 274     }
 275 
 276     public class InputWrapper {
 277         @InvocableVariable(required=true label='Order ID')
 278         public Id orderId;
 279     }
 280 
 281     public class OutputWrapper {
 282         @InvocableVariable(label='Success')
 283         public Boolean isSuccess;
 284         @InvocableVariable(label='Message')
 285         public String message;
 286     }
 287 }
 288 ```
 289 
 290 > **Rule of Thumb**: If you're building workarounds for Flow limitations, use Apex. Flow should feel natural—if it doesn't, escalate.
 291 
 292 ---
 293 
 294 ## 4. Flow Element Organization
 295 
 296 Structure your flow elements in this sequence for maintainability:
 297 
 298 | Order | Element Type | Purpose |
 299 |-------|--------------|---------|
 300 | 1 | Variables & Constants | Define all data containers first |
 301 | 2 | Start Element | Entry conditions, triggers, schedules |
 302 | 3 | Initial Record Lookups | Retrieve needed data early |
 303 | 4 | Formula Definitions | Define calculations before use |
 304 | 5 | Decision Elements | Branching logic |
 305 | 6 | Assignment Elements | Data preparation/manipulation |
 306 | 7 | Screens (if Screen Flow) | User interaction |
 307 | 8 | DML Operations | Create/Update/Delete records |
 308 | 9 | Error Handling | Fault paths and rollback |
 309 | 10 | Ending Elements | Complete flow, return outputs |
 310 
 311 ### Why This Order Matters
 312 
 313 - **Readability**: Reviewers can follow the logical flow
 314 - **Maintainability**: Easy to locate elements by function
 315 - **Debugging**: Errors trace back to predictable locations
 316 
 317 ---
 318 
 319 ## 5. Using $Record in Record-Triggered Flows
 320 
 321 When your flow is triggered by a record change, use `$Record` to access field values instead of querying the same object again.
 322 
 323 ### ⚠️ CRITICAL: $Record vs $Record__c
 324 
 325 **Do NOT confuse Flow's `$Record` with Process Builder's `$Record__c`.**
 326 
 327 | Variable | Platform | Meaning |
 328 |----------|----------|---------|
 329 | `$Record` | **Flow** | Single record that triggered the flow |
 330 | `$Record__c` | Process Builder (legacy) | Collection of records in trigger batch |
 331 
 332 **Common Mistake**: Developers migrating from Process Builder try to loop over `$Record__c` in Flows. This doesn't work because:
 333 - `$Record__c` does not exist in Flows
 334 - `$Record` in Flows is a single record, not a collection
 335 - The platform handles bulk batching automatically - you don't need to loop
 336 
 337 **Correct Approach**: Use `$Record` directly without loops:
 338 ```
 339 Decision: {!$Record.StageName} equals "Closed Won"
 340 Assignment: Set rec_Task.WhatId = {!$Record.Id}
 341 Create Records: rec_Task
 342 ```
 343 
 344 ### Anti-Pattern (Avoid)
 345 
 346 ```
 347 Trigger: Account record updated
 348 Step 1: Get Records → Query Account where Id = {!$Record.Id}
 349 Step 2: Use queried Account fields
 350 ```
 351 
 352 **Problems**:
 353 - Wastes a SOQL query (you already have the record!)
 354 - Adds unnecessary complexity
 355 - Can cause timing issues with stale data
 356 
 357 ### Best Practice
 358 
 359 ```
 360 Trigger: Account record updated
 361 Step 1: Use {!$Record.Name}, {!$Record.Industry} directly
 362 ```
 363 
 364 **Benefits**:
 365 - Zero additional SOQL queries
 366 - Always has current field values
 367 - Simpler, more readable flow
 368 
 369 ### When You DO Need to Query
 370 
 371 Query the trigger object only when you need:
 372 - Related records (e.g., Account's Contacts)
 373 - Fields not included in the trigger context
 374 - Historical comparison (`$Record__Prior`)
 375 
 376 ---
 377 
 378 ## 6. Querying Relationship Data
 379 
 380 ### ⚠️ Get Records Does NOT Support Parent Traversal
 381 
 382 **Critical Limitation**: You CANNOT query parent relationship fields in Flow's Get Records.
 383 
 384 #### What Doesn't Work
 385 
 386 ```
 387 Get Records: User
 388 Fields: Id, Name, Manager.Name  ← FAILS!
 389 ```
 390 
 391 **Error**: "The field 'Manager.Name' for the object 'User' doesn't exist."
 392 
 393 #### The Solution: Two-Step Pattern
 394 
 395 Query the child object first, then query the parent using the lookup ID:
 396 
 397 ```
 398 Step 1: Get Records → User
 399         Fields: Id, Name, ManagerId
 400         Store in: rec_User
 401 
 402 Step 2: Get Records → User
 403         Filter: Id equals {!rec_User.ManagerId}
 404         Fields: Id, Name
 405         Store in: rec_Manager
 406 
 407 Step 3: Use {!rec_Manager.Name} in your flow
 408 ```
 409 
 410 #### Common Relationship Queries That Need This Pattern
 411 
 412 | Child Object | Parent Field | Two-Step Approach |
 413 |--------------|--------------|-------------------|
 414 | Contact | Account.Name | Get Contact → Get Account by AccountId |
 415 | Case | Account.Owner.Email | Get Case → Get Account → Get User |
 416 | Opportunity | Account.Industry | Get Opportunity → Get Account by AccountId |
 417 | User | Manager.Name | Get User → Get User by ManagerId |
 418 
 419 #### Why This Matters
 420 
 421 - Flow's Get Records uses simple field retrieval, not SOQL relationship queries
 422 - This is different from Apex where you can write `SELECT Account.Name FROM Contact`
 423 - Always check for null on the parent record before using its fields
 424 
 425 ---
 426 
 427 ## 7. Query Optimization
 428 
 429 ### Use 'In' and 'Not In' Operators
 430 
 431 When filtering against a collection of values, use `In` or `Not In` operators instead of multiple OR conditions.
 432 
 433 **Best Practice**:
 434 ```
 435 Get Records where Status IN {!col_StatusValues}
 436 ```
 437 
 438 **Avoid**:
 439 ```
 440 Get Records where Status = 'Open' OR Status = 'Pending' OR Status = 'Review'
 441 ```
 442 
 443 ### Always Add Filter Conditions
 444 
 445 Every Get Records element should have filter conditions to:
 446 - Limit the result set
 447 - Improve query performance
 448 - Avoid hitting governor limits
 449 
 450 ### Use Indexed Fields for Large Data Volumes
 451 
 452 For orgs with **100K+ records** on an object, filter on indexed fields to ensure fast query performance.
 453 
 454 #### Always Indexed Fields
 455 
 456 | Field Type | Examples | Notes |
 457 |------------|----------|-------|
 458 | **Id** | Record ID | Primary key, fastest |
 459 | **Name** | Account Name, Contact Name | Standard name field |
 460 | **CreatedDate** | - | Useful for recent records |
 461 | **SystemModstamp** | - | Last modified timestamp |
 462 | **RecordTypeId** | - | If using Record Types |
 463 | **OwnerId** | - | User lookup |
 464 
 465 #### Custom Indexed Fields
 466 
 467 | Field Type | Notes |
 468 |------------|-------|
 469 | **External ID fields** | Automatically indexed |
 470 | **Lookup/Master-Detail fields** | Relationship fields are indexed |
 471 | **Custom fields with indexing** | Request via Salesforce Support |
 472 | **Unique fields** | Automatically indexed |
 473 
 474 #### Performance Impact
 475 
 476 ```
 477 ┌─────────────────────────────────────────────────────────────────┐
 478 │ QUERY PERFORMANCE: Indexed vs Non-Indexed                       │
 479 └─────────────────────────────────────────────────────────────────┘
 480 
 481 ❌ NON-INDEXED FILTER (Slow on large objects):
 482    Get Records: Account
 483    Filter: Custom_Text__c = "ValueABC"
 484    → Full table scan = slow + timeout risk
 485 
 486 ✅ INDEXED FILTER (Fast at any scale):
 487    Get Records: Account
 488    Filter: External_Id__c = "ValueABC"
 489    → Index lookup = milliseconds
 490 ```
 491 
 492 #### When to Request Custom Indexing
 493 
 494 Contact Salesforce Support to request indexing when:
 495 - Object has 100K+ records
 496 - Query frequently filters on a specific field
 497 - Flow timeouts occur with non-indexed filters
 498 
 499 > **Tip**: Use `SELECT Id FROM Object WHERE Field = 'value'` in Developer Console to test query performance before building the Flow.
 500 
 501 ### Use getFirstRecordOnly
 502 
 503 When you expect a single record (e.g., looking up by unique ID), enable `getFirstRecordOnly`:
 504 - Improves performance
 505 - Clearer intent
 506 - Simpler variable handling
 507 
 508 ### Avoid storeOutputAutomatically
 509 
 510 When `storeOutputAutomatically="true"`, ALL fields are retrieved and stored:
 511 
 512 **Risks**:
 513 - Exposes sensitive data unintentionally
 514 - Impacts performance with large objects
 515 - Security issue in screen flows (external users see all data)
 516 
 517 **Fix**: Explicitly specify only the fields you need in the Get Records element.
 518 
 519 ---
 520 
 521 ## 8. Transform vs Loop Elements
 522 
 523 When processing collections, choosing between **Transform** and **Loop** elements significantly impacts performance and maintainability.
 524 
 525 ### Quick Decision Rule
 526 
 527 > **Shaping data** → Use **Transform** (30-50% faster)
 528 > **Making decisions per record** → Use **Loop**
 529 
 530 ### When to Use Transform
 531 
 532 Transform is the right choice for:
 533 
 534 | Use Case | Example |
 535 |----------|---------|
 536 | **Mapping collections** | Contact[] → OpportunityContactRole[] |
 537 | **Bulk field assignments** | Set Status = "Processed" for all records |
 538 | **Simple formulas** | Calculate FullName from FirstName + LastName |
 539 | **Preparing records for DML** | Build collection for Create Records |
 540 
 541 ### When to Use Loop
 542 
 543 Loop is required when:
 544 
 545 | Use Case | Example |
 546 |----------|---------|
 547 | **Per-record IF/ELSE** | Different processing based on Amount threshold |
 548 | **Counters/flags** | Count records meeting criteria |
 549 | **State tracking** | Running totals, comma-separated lists |
 550 | **Varying business rules** | Different logic paths per record type |
 551 
 552 ### Visual Comparison
 553 
 554 ```
 555 ❌ ANTI-PATTERN: Loop for simple field mapping
 556    Get Records → Loop → Assignment → Add to Collection → Create Records
 557    (5 elements, client-side iteration)
 558 
 559 ✅ BEST PRACTICE: Transform for field mapping
 560    Get Records → Transform → Create Records
 561    (3 elements, server-side bulk operation, 30-50% faster)
 562 ```
 563 
 564 ### Performance Impact
 565 
 566 Transform processes the entire collection server-side as a single bulk operation, while Loop iterates client-side. For collections of 100+ records, Transform can be **30-50% faster**.
 567 
 568 ### XML Recommendation
 569 
 570 > ⚠️ **Create Transform elements in Flow Builder UI, then deploy.**
 571 > Transform XML is complex with strict ordering—do not hand-write.
 572 
 573 See [Transform vs Loop Guide](./transform-vs-loop-guide.md) for detailed decision criteria, examples, and testing strategies.
 574 
 575 ---
 576 
 577 ## 9. Collection Filter Optimization
 578 
 579 Collection Filter is a powerful tool for reducing governor limit usage by filtering in memory instead of making additional SOQL queries.
 580 
 581 ### The Pattern
 582 
 583 Instead of multiple Get Records calls, query once and filter in memory:
 584 
 585 ```
 586 ┌─────────────────────────────────────────────────────────────────────────┐
 587 │ ❌ ANTI-PATTERN: Multiple Get Records calls                            │
 588 └─────────────────────────────────────────────────────────────────────────┘
 589 
 590 For each Account in loop:
 591   → Get Records: Contacts WHERE AccountId = {!current_Account.Id}
 592   → Process contacts...
 593 
 594 Problem: N SOQL queries (one per Account) = Governor limit risk!
 595 
 596 ┌─────────────────────────────────────────────────────────────────────────┐
 597 │ ✅ BEST PRACTICE: Query once + Collection Filter                       │
 598 └─────────────────────────────────────────────────────────────────────────┘
 599 
 600 1. Get Records: ALL Contacts WHERE AccountId IN {!col_AccountIds}
 601    → 1 SOQL query total
 602 
 603 2. Loop through Accounts:
 604    → Collection Filter: Contacts WHERE AccountId = {!current_Account.Id}
 605    → Process filtered contacts (in-memory, no SOQL!)
 606 ```
 607 
 608 ### Benefits
 609 
 610 | Metric | Multiple Queries | Query Once + Filter |
 611 |--------|------------------|---------------------|
 612 | SOQL Queries | N (one per parent) | 1 |
 613 | Performance | Slow | Fast |
 614 | Governor Risk | High | Low |
 615 | Scalability | Poor | Excellent |
 616 
 617 ### Implementation Steps
 618 
 619 1. **Collect parent IDs** into a collection variable
 620 2. **Single Get Records** using `IN` operator with ID collection
 621 3. **Loop through parents**, using Collection Filter to get related records
 622 4. **Process filtered subset** in each iteration
 623 
 624 ### When to Use
 625 
 626 - Parent-child processing (Account → Contacts, Opportunity → Line Items)
 627 - Batch operations where you need related records
 628 - Any scenario requiring records from the same object for multiple parents
 629 
 630 ### Governor Limit Savings
 631 
 632 With Collection Filter, you can process thousands of related records with a **single SOQL query** instead of hitting the 100-query limit.
 633 
 634 ---
 635 
 636 ## 10. When to Use Subflows
 637 
 638 Use subflows for:
 639 
 640 ### 1. Reusability
 641 Same logic needed in multiple flows? Extract it to a subflow.
 642 - Error logging
 643 - Email notifications
 644 - Common validations
 645 
 646 ### 2. Complex Orchestration
 647 Break large flows into manageable pieces:
 648 - Main flow orchestrates
 649 - Subflows handle specific responsibilities
 650 - Easier to test individually
 651 
 652 ### 3. Permission Elevation
 653 When a flow running in user context needs elevated permissions:
 654 - Main flow runs in user context
 655 - Subflow runs in system context for specific operations
 656 - Maintains security while enabling functionality
 657 
 658 ### 4. Organizational Clarity
 659 If your flow diagram is unwieldy:
 660 - Extract logical sections into subflows
 661 - Name subflows descriptively
 662 - Document the orchestration pattern
 663 
 664 ### Subflow Naming Convention
 665 
 666 Use the `Sub_` prefix:
 667 - `Sub_LogError`
 668 - `Sub_SendEmailAlert`
 669 - `Sub_ValidateRecord`
 670 - `Sub_BulkUpdater`
 671 
 672 ---
 673 
 674 ## 11. Custom Metadata for Business Logic
 675 
 676 Store frequently changing business logic values in **Custom Metadata Types (CMDT)** rather than hard-coding them in Flow. This enables admins to change thresholds, settings, and routing logic without modifying the Flow.
 677 
 678 ### Why Use CMDT for Business Logic
 679 
 680 | Benefit | Description |
 681 |---------|-------------|
 682 | **No deployment needed** | Change values in Setup, no Flow modification |
 683 | **Environment-specific** | Different values per sandbox/production |
 684 | **Audit trail** | Changes tracked in Setup Audit Trail |
 685 | **Admin-friendly** | Non-developers can update business rules |
 686 | **Testable** | CMDT records are accessible in test context |
 687 
 688 ### Two Access Patterns
 689 
 690 | Pattern | Syntax | SOQL Count | Use When |
 691 |---------|--------|------------|----------|
 692 | **Formula Reference** | `$CustomMetadata.Type__mdt.Record.Field__c` | 0 | Single known record, simple value |
 693 | **Get Records Query** | Get Records → CMDT object | 1 | Multiple records, dynamic filtering |
 694 
 695 #### Formula Pattern (Preferred for Single Values)
 696 
 697 - **No SOQL consumed** - platform resolves at runtime
 698 - Direct reference in conditions/assignments
 699 - Syntax: `{!$CustomMetadata.Flow_Settings__mdt.Discount_Threshold.Numeric_Value__c}`
 700 
 701 ```
 702 Decision: Check_Threshold
 703 ├── Condition: {!$Record.Amount} >= {!$CustomMetadata.Flow_Settings__mdt.Discount_Threshold.Numeric_Value__c}
 704 └── Outcome: Apply_Discount
 705 ```
 706 
 707 #### Get Records Pattern (For Dynamic Queries)
 708 
 709 - **Consumes 1 SOQL** per query
 710 - Enables filtering, multiple record retrieval
 711 - Visible in Flow debug logs for troubleshooting
 712 - Useful when CMDT record name is dynamic or you need to iterate
 713 
 714 ```
 715 Get Records: Flow_Settings__mdt
 716 ├── Filter: Category__c = "Discount"
 717 ├── Store All Records: col_DiscountSettings
 718 └── Use in Loop or Transform
 719 ```
 720 
 721 > **Rule of Thumb**: Use Formula Reference when you know the exact CMDT record at design time. Use Get Records when the record selection is dynamic or you need multiple records.
 722 
 723 ### What to Store in CMDT
 724 
 725 | Value Type | Example CMDT Field | ⚠️ Key Guidance |
 726 |------------|-------------------|-----------------|
 727 | **Business Thresholds** | `Discount_Threshold__c`, `Max_Approval_Amount__c` | Ideal for values that change quarterly or less |
 728 | **Feature Toggles** | `Enable_Auto_Assignment__c` | Boolean flags for gradual rollouts |
 729 | **Record Type Names** | `RecordType_DeveloperName__c` | Store DeveloperName, NOT 15/18-char IDs |
 730 | **Queue/User Names** | `Assignment_Queue_Name__c` | Store DeveloperName, resolve ID at runtime |
 731 | **Email Recipients** | `Notification_Email__c`, `Template_Name__c` | Store template API names, not IDs |
 732 | **URLs/Endpoints** | `External_API_Endpoint__c` | Enables sandbox vs production differences |
 733 | **Picklist Mappings** | `Source_Value__c` → `Target_Value__c` | Great for value translations |
 734 
 735 > ⚠️ **CRITICAL: Never Store Salesforce IDs in CMDT**
 736 >
 737 > Salesforce 15/18-character IDs (RecordTypeId, QueueId, UserId, ProfileId) are **org-specific**.
 738 > The same Queue has different IDs in sandbox vs production. Storing IDs in CMDT causes deployment failures.
 739 >
 740 > **❌ Wrong**: `Queue_Id__c = '00G5f000004XXXX'`
 741 > **✅ Right**: `Queue_Name__c = 'Support_Queue'` → Resolve ID at runtime with Get Records
 742 
 743 #### Runtime ID Resolution Pattern
 744 
 745 When you need to route to a Queue, User, or RecordType stored in CMDT:
 746 
 747 ```
 748 1. Get CMDT Value:
 749    Formula: {!$CustomMetadata.Flow_Settings__mdt.Support_Queue.Queue_Name__c}
 750    → Returns: "Support_Queue" (DeveloperName)
 751 
 752 2. Get Records: Group (Queue)
 753    Filter: DeveloperName = {!var_QueueName} AND Type = 'Queue'
 754    Store: rec_Queue
 755 
 756 3. Assignment:
 757    Set {!$Record.OwnerId} = {!rec_Queue.Id}
 758 ```
 759 
 760 ### Common Use Cases
 761 
 762 | Use Case | CMDT Field Example | Flow Usage |
 763 |----------|-------------------|------------|
 764 | Discount thresholds | `Discount_Threshold__c = 10000` | Decision: Amount > {!$CustomMetadata...} |
 765 | Feature toggles | `Enable_Auto_Assignment__c = true` | Decision: Feature enabled? |
 766 | Approval limits | `Max_Approval_Amount__c = 50000` | Route based on amount threshold |
 767 | Email recipients | `Notification_Email__c` | Send email to CMDT value |
 768 | SLA thresholds | `SLA_Warning_Hours__c = 24` | Decision: Hours > threshold |
 769 | API endpoints | `External_API_Endpoint__c` | HTTP Callout URL |
 770 
 771 ### Implementation Pattern
 772 
 773 #### Step 1: Create Custom Metadata Type
 774 
 775 ```
 776 Object: Flow_Settings__mdt
 777 Fields:
 778 ├── Setting_Name__c (Text, Unique)
 779 ├── Numeric_Value__c (Number)
 780 ├── Text_Value__c (Text)
 781 ├── Boolean_Value__c (Checkbox)
 782 └── Description__c (Text Area)
 783 ```
 784 
 785 #### Step 2: Create Records
 786 
 787 ```
 788 Record: Discount_Threshold
 789 ├── Setting_Name__c = "Discount_Threshold"
 790 ├── Numeric_Value__c = 10000
 791 ├── Text_Value__c = null
 792 ├── Boolean_Value__c = false
 793 └── Description__c = "Minimum order amount for automatic discount"
 794 ```
 795 
 796 #### Step 3: Reference in Flow
 797 
 798 ```
 799 Decision Element: Check_Discount_Eligibility
 800 ├── Condition: {!$Record.Amount} >= {!$CustomMetadata.Flow_Settings__mdt.Discount_Threshold.Numeric_Value__c}
 801 │   └── Outcome: Apply_Discount
 802 └── Default: No_Discount
 803 ```
 804 
 805 ### Best Practices
 806 
 807 | Practice | Reason |
 808 |----------|--------|
 809 | **Use descriptive DeveloperNames** | `Discount_Threshold` not `Setting_1` |
 810 | **Document in Description field** | Future maintainers understand purpose |
 811 | **Group related settings** | One CMDT type per domain (Sales, Service, etc.) |
 812 | **Include in deployment packages** | CMDT records are metadata, deploy with code |
 813 | **Test with realistic values** | Verify Flow behavior with production thresholds |
 814 
 815 ### Identifying Hard-Coded Candidates (Migration Checklist)
 816 
 817 Review existing flows for these hard-coded patterns that should migrate to CMDT:
 818 
 819 ```
 820 HARD-CODED PATTERN AUDIT
 821 ═══════════════════════════════════════════════════════════
 822 
 823 📋 CHECK YOUR FLOWS FOR:
 824 
 825 □ 15/18-character Salesforce IDs
 826   └─ RecordTypeIds, QueueIds, UserIds, ProfileIds
 827   └─ Example: OwnerId = '005...' → Store Queue DeveloperName
 828 
 829 □ Hardcoded URLs or endpoints
 830   └─ HTTP callout URLs, redirect paths
 831   └─ Example: endpoint = 'https://api.prod...' → Store in CMDT
 832 
 833 □ Magic numbers (thresholds, limits, percentages)
 834   └─ Discount rates, approval limits, SLA hours
 835   └─ Example: Amount > 10000 → Use CMDT threshold
 836 
 837 □ Email addresses in Send Email actions
 838   └─ Notification recipients, CC lists
 839   └─ Example: To = 'admin@company.com' → Store in CMDT
 840 
 841 □ Profile/Permission Set names
 842   └─ Used in Decision conditions
 843   └─ Store as text, query Profile/PermissionSet at runtime
 844 
 845 □ Object API names used in dynamic references
 846   └─ Hard-coded object strings for generic patterns
 847 
 848 □ Picklist values used in conditions
 849   └─ Values that might change across regions/deployments
 850 
 851 ═══════════════════════════════════════════════════════════
 852 ```
 853 
 854 > **Validator Note**: The sf-flow validator automatically flags `HardcodedId` and `HardcodedUrl` patterns during analysis.
 855 
 856 ### When NOT to Use CMDT
 857 
 858 | Scenario | Better Alternative |
 859 |----------|-------------------|
 860 | User-specific preferences | Custom Settings (Hierarchy) |
 861 | Frequently changing data | Custom Object with query |
 862 | Large datasets (1000+ records) | Custom Object |
 863 | Binary file storage | Static Resource or Files |
 864 
 865 > **Tip**: CMDT is ideal for business rules that change quarterly or less. For daily-changing values, use Custom Objects or Custom Settings.
 866 
 867 #### Deployment vs Data Load Distinction
 868 
 869 CMDT records are **metadata**, not data. This has important implications:
 870 
 871 | Aspect | Custom Metadata Type | Custom Object / Custom Setting |
 872 |--------|---------------------|-------------------------------|
 873 | **Move between orgs** | Change Sets, Metadata API, sf deploy | Data Loader, sf data import |
 874 | **Update in production** | Setup → Custom Metadata Types | Data operations (update records) |
 875 | **Included in packages** | ✅ Yes (managed/unmanaged) | ❌ No (data must be seeded separately) |
 876 | **Test context access** | ✅ Accessible without `@TestSetup` | Requires test data creation |
 877 
 878 > **Common Mistake**: Trying to use Data Loader to update CMDT values. CMDT records are deployed as metadata—use Change Sets, Metadata API (`sf project deploy`), or Setup UI to modify values between environments.
 879 
 880 ---
 881 
 882 ## 12. Three-Tier Error Handling
 883 
 884 Implement comprehensive error handling at three levels:
 885 
 886 ### Tier 1: Input Validation (Pre-Execution)
 887 
 888 **When**: Before any DML operations
 889 **What to Check**:
 890 - Null/empty required values
 891 - Business rule prerequisites
 892 - Data format validation
 893 
 894 **Action**: Show validation error screen or set error output variable
 895 
 896 ### Tier 2: DML Error Handling (During Execution)
 897 
 898 **When**: On every DML element (Create, Update, Delete)
 899 **What to Do**:
 900 - Add fault paths to ALL DML elements
 901 - Capture `{!$Flow.FaultMessage}` for context
 902 - Include record IDs and operation type in error messages
 903 
 904 **Action**: Route to error handler, prepare for rollback
 905 
 906 ### Tier 3: Rollback Handling (Post-Failure)
 907 
 908 **When**: After a DML failure when prior operations succeeded
 909 **What to Do**:
 910 - Delete records created earlier in the transaction
 911 - Restore original values if updates failed
 912 - Log the failure for debugging
 913 
 914 **Action**: Execute rollback, notify user/admin
 915 
 916 ### Error Message Best Practice
 917 
 918 Include context in every error message:
 919 ```
 920 "Failed to create Contact for Account {!rec_Account.Id}: {!$Flow.FaultMessage}"
 921 "Update failed on Opportunity {!rec_Opportunity.Id} during {!var_CurrentOperation}"
 922 ```
 923 
 924 ---
 925 
 926 ## 13. Multi-Step DML Rollback Strategy
 927 
 928 When a flow performs multiple DML operations, implement rollback paths.
 929 
 930 ### Pattern: Primary → Dependent → Rollback Chain
 931 
 932 #### Step 1: Create Primary Record (e.g., Account)
 933 - On success → Continue to step 2
 934 - On failure → Show error, stop flow
 935 
 936 #### Step 2: Create Dependent Records (e.g., Contacts, Opportunities)
 937 - On success → Continue to step 3
 938 - On failure → **DELETE primary record**, show error
 939 
 940 #### Step 3: Update Related Records
 941 - On success → Complete flow
 942 - On failure → **DELETE dependents, DELETE primary**, show error
 943 
 944 ### Implementation Pattern
 945 
 946 ```
 947 1. Create Account → Store ID in var_AccountId
 948 2. Create Contacts → On fault: Delete Account using var_AccountId
 949 3. Create Opportunities → On fault: Delete Contacts, Delete Account
 950 4. Success → Return output variables
 951 ```
 952 
 953 ### Error Message Pattern
 954 
 955 Use `errorMessage` output variable to surface failures:
 956 ```
 957 "Failed to create Account: {!$Flow.FaultMessage}"
 958 "Failed to create Contact: {!$Flow.FaultMessage}. Account rolled back."
 959 ```
 960 
 961 ---
 962 
 963 ## 14. Transaction Management
 964 
 965 ### Understanding Flow Transactions
 966 
 967 - All DML in a flow runs in a **single transaction** (unless using async)
 968 - If any DML fails, **all changes roll back automatically**
 969 - Use this to your advantage for data integrity
 970 
 971 ### Save Point Pattern
 972 
 973 For complex multi-step flows where you need manual rollback control:
 974 
 975 1. Create primary records
 976 2. Store IDs of created records in a collection
 977 3. Create dependent records
 978 4. On failure → Use stored IDs for manual rollback
 979 
 980 ### Transaction Limits to Consider
 981 
 982 | Limit | Value |
 983 |-------|-------|
 984 | DML statements per transaction | 150 |
 985 | SOQL queries per transaction | 100 |
 986 | Records retrieved by SOQL | 50,000 |
 987 | DML rows per transaction | 10,000 |
 988 
 989 ### Document Transaction Boundaries
 990 
 991 Add comments in flow description:
 992 ```
 993 TRANSACTION: Creates Account → Creates Contact → Updates related Opportunities
 994 ```
 995 
 996 ---
 997 
 998 ## 15. Screen Flow UX Best Practices
 999 
1000 ### Progress Indicators
1001 
1002 For multi-step flows (3+ screens):
1003 - Use Screen component headers to show "Step X of Y"
1004 - Consider visual progress bars for long wizards
1005 - Update progress on each screen transition
1006 
1007 ### Stage Resource for Multi-Screen Flows
1008 
1009 The **Stage** resource provides visual progress tracking across multiple screens, showing users where they are in a multi-step process.
1010 
1011 #### When to Use Stage
1012 
1013 - Flows with 3+ screens that represent distinct phases
1014 - Onboarding wizards (Identity → Configuration → Confirmation)
1015 - Order processes (Cart → Shipping → Payment → Review)
1016 - Application workflows with logical sections
1017 
1018 #### How Stages Work
1019 
1020 1. **Define stages** in your flow resources (Stage elements)
1021 2. **Assign current stage** using Assignment element at each phase transition
1022 3. **Display progress** using the Stage component in screens
1023 
1024 #### Stage Example
1025 
1026 ```
1027 Flow: New Customer Onboarding
1028 
1029 Stages:
1030 1. Identity (collect customer info)
1031 2. Configuration (set preferences)
1032 3. Payment (billing details)
1033 4. Confirmation (review and submit)
1034 
1035 Each screen shows visual indicator: ● ○ ○ ○ → ● ● ○ ○ → ● ● ● ○ → ● ● ● ●
1036 ```
1037 
1038 #### Benefits
1039 
1040 | Feature | Benefit |
1041 |---------|---------|
1042 | Visual progress | Users know how far along they are |
1043 | Reduced abandonment | Clear expectation of remaining steps |
1044 | Better UX | Professional wizard-like experience |
1045 | Navigation context | Users understand their position |
1046 
1047 #### Implementation Tips
1048 
1049 - Keep stage names short (1-3 words)
1050 - Use consistent naming pattern (nouns: "Identity", "Payment" vs verbs: "Collect Info", "Enter Payment")
1051 - Consider allowing users to click back to previous stages (if safe)
1052 
1053 ### Button Design
1054 
1055 #### Naming Pattern
1056 Use: `Action_[Verb]_[Object]`
1057 - `Action_Save_Contact`
1058 - `Action_Submit_Application`
1059 - `Action_Cancel_Request`
1060 
1061 #### Button Ordering
1062 1. **Primary action** first (Submit, Save, Confirm)
1063 2. **Secondary actions** next (Save Draft, Back)
1064 3. **Tertiary/Cancel** last (Cancel, Exit)
1065 
1066 ### Navigation Controls
1067 
1068 #### Standard Navigation Pattern
1069 
1070 | Button | Position | When to Show |
1071 |--------|----------|--------------|
1072 | Previous | Left | After first screen (if safe) |
1073 | Cancel | Left | Always |
1074 | Next | Right | Before final screen |
1075 | Finish/Submit | Right | Final screen only |
1076 
1077 #### When to Disable Back Button
1078 
1079 Disable "Previous" when returning would:
1080 - Cause duplicate record creation
1081 - Lose unsaved complex data
1082 - Break transaction integrity
1083 - Confuse business process state
1084 
1085 ### Screen Instructions
1086 
1087 For complex screens, add instruction text at the top:
1088 - Use Display Text component
1089 - Keep instructions concise (1-2 sentences)
1090 - Highlight required fields or important notes
1091 
1092 Example: "Complete all required fields (*) before proceeding."
1093 
1094 ### Performance Tips
1095 
1096 - **Lazy Loading**: Don't load all data upfront; query as needed per screen
1097 - **Minimize Screens**: Each screen = user wait time; combine where logical
1098 - **Avoid Complex Formulas**: In screen components (impacts render time)
1099 - **LWC for Complex UI**: Consider Lightning Web Components for rich interactions
1100 
1101 ---
1102 
1103 ## 16. Bypass Mechanism for Data Loads
1104 
1105 When loading large amounts of data, flows can cause performance issues. Implement a bypass mechanism using Custom Metadata.
1106 
1107 ### Setup Pattern
1108 
1109 #### Step 1: Create Custom Metadata Type
1110 
1111 Create `Flow_Bypass_Settings__mdt` with fields:
1112 - `Bypass_Flows__c` (Checkbox)
1113 - `Flow_API_Name__c` (Text) - optional, for granular control
1114 
1115 #### Step 2: Add Decision at Flow Start
1116 
1117 Add a Decision element as the first step after Start:
1118 
1119 **Condition**: `{!$CustomMetadata.Flow_Bypass_Settings__mdt.Default.Bypass_Flows__c} = true`
1120 - **If true** → End flow early (no processing)
1121 - **If false** → Continue normal processing
1122 
1123 ### Use Cases
1124 
1125 - Data migrations
1126 - Bulk data loads via Data Loader
1127 - Integration batch processing
1128 - Initial org setup/seeding
1129 
1130 ### Best Practice
1131 
1132 - Document which flows support bypass
1133 - Ensure bypass is disabled after data load completes
1134 - Consider logging when bypass is active
1135 
1136 ---
1137 
1138 ## 17. Flow Activation Guidelines
1139 
1140 ### When to Keep Flows in Draft
1141 
1142 - During development and testing
1143 - Before user acceptance testing (UAT) is complete
1144 - When dependent configurations aren't deployed yet
1145 
1146 ### Deployment Recommendation
1147 
1148 1. Deploy flows as **Draft** initially
1149 2. Validate in target environment
1150 3. Test with representative data
1151 4. Activate only after verification
1152 5. Keep previous version as backup before activating new version
1153 
1154 ### Scheduled Flow Considerations
1155 
1156 Scheduled flows run automatically without user interaction:
1157 - Test thoroughly before activation
1158 - Verify schedule frequency is correct
1159 - Ensure error notifications are configured
1160 - Monitor first few executions
1161 
1162 ---
1163 
1164 ## 18. Variable Naming Conventions
1165 
1166 Use consistent prefixes for all variables:
1167 
1168 | Prefix | Purpose | Example |
1169 |--------|---------|---------|
1170 | `var_` | Regular variables | `var_AccountName` |
1171 | `col_` | Collections | `col_ContactIds` |
1172 | `rec_` | Record variables | `rec_Account` |
1173 | `inp_` | Input variables | `inp_RecordId` |
1174 | `out_` | Output variables | `out_IsSuccess` |
1175 
1176 ### Why Prefixes Matter
1177 
1178 - **Clarity**: Immediately understand variable type
1179 - **Debugging**: Easier to trace values in debug logs
1180 - **Maintenance**: New developers understand intent quickly
1181 - **Consistency**: Team-wide standards reduce confusion
1182 
1183 ### Element Naming
1184 
1185 For flow elements (decisions, assignments, etc.):
1186 - Use `PascalCase_With_Underscores`
1187 - Be descriptive: `Check_Account_Type` not `Decision_1`
1188 - Include context: `Get_Related_Contacts` not `Get_Records`
1189 
1190 ---
1191 
1192 ## 19. Flow & Element Descriptions
1193 
1194 Clear descriptions are essential for maintenance, collaboration, and **Agentforce integration**. AI agents use Flow descriptions to understand and select appropriate automations.
1195 
1196 ### Flow Description (Critical for Agentforce)
1197 
1198 #### Why This Matters
1199 
1200 | Consumer | How They Use Descriptions |
1201 |----------|--------------------------|
1202 | **Agentforce Agents** | AI uses descriptions to understand what automation does and when to invoke it |
1203 | **Future Developers** | Quick understanding without reading the entire flow |
1204 | **Flow Orchestrator** | Discovery of available subflows |
1205 | **Governance Tools** | Auditing and documentation generation |
1206 | **Setup Search** | Finding flows by purpose |
1207 
1208 #### What to Include in Flow Description
1209 
1210 Every Flow description should contain:
1211 
1212 1. **Purpose**: One sentence explaining what the flow does
1213 2. **Trigger**: When/how the flow is invoked
1214 3. **Objects**: Which objects are read/written
1215 4. **Outcome**: What changes when the flow completes
1216 5. **Dependencies**: Any required configurations or prerequisites
1217 
1218 #### Examples
1219 
1220 ```
1221 ✅ GOOD DESCRIPTION:
1222 ───────────────────────────────────────────────────────────────
1223 "Automatically assigns new Leads to the appropriate sales rep
1224 based on territory and product interest. Updates Lead Owner,
1225 sets Assignment_Date__c, and sends notification email to the
1226 assigned rep. Triggered on Lead creation when Status = 'New'.
1227 Requires Territory__c field and Lead_Assignment_Queue__c queue."
1228 ───────────────────────────────────────────────────────────────
1229 
1230 ❌ BAD DESCRIPTION:
1231 "Lead flow"
1232 "Auto assignment"
1233 "Created by Admin"
1234 ```
1235 
1236 #### Description Template
1237 
1238 ```
1239 [ACTION] [OBJECT(S)] [CONDITION].
1240 [WHAT CHANGES]. [TRIGGER/SCHEDULE].
1241 [DEPENDENCIES if any].
1242 ```
1243 
1244 Examples using template:
1245 - "Creates Task and sends email when Opportunity Stage changes to Closed Won. Updates Account Last_Deal_Date__c. Runs after Opportunity update."
1246 - "Validates Contact email format and enriches with external data. Blocks save if validation fails. Runs before Contact insert/update."
1247 
1248 ### Element Descriptions
1249 
1250 Add descriptions to complex elements (Decisions, Assignments, Get Records, Loops) to explain **why** the element exists, not just what it does.
1251 
1252 #### When to Add Element Descriptions
1253 
1254 | Element Type | Add Description When... |
1255 |--------------|------------------------|
1256 | **Decision** | Logic has business meaning beyond obvious field comparison |
1257 | **Get Records** | Query has specific filter reasoning |
1258 | **Assignment** | Calculation or transformation isn't self-evident |
1259 | **Loop** | Processing order or exit conditions matter |
1260 | **Subflow** | Purpose of delegation isn't obvious |
1261 
1262 #### Element Description Format
1263 
1264 ```
1265 WHY: [Business reason this element exists]
1266 WHAT: [Technical summary if complex]
1267 EDGE CASE: [Special handling if applicable]
1268 ```
1269 
1270 #### Examples
1271 
1272 ```
1273 Decision: Check_Discount_Eligibility
1274 Description: "Customers with >$100K annual revenue OR
1275 Premium tier get automatic 15% discount. Edge case:
1276 New customers without revenue history default to no discount."
1277 
1278 Get Records: Get_Active_Contracts
1279 Description: "Retrieves only contracts expiring in next 90 days
1280 to avoid processing historical data. Filtered by Status=Active
1281 to reduce collection size for bulk safety."
1282 
1283 Assignment: Calculate_Renewal_Date
1284 Description: "Adds 365 days to current contract end date.
1285 Uses formula to handle leap years. Returns null if
1286 original end date is null (new contracts)."
1287 ```
1288 
1289 ### Benefits of Good Descriptions
1290 
1291 | Benefit | Impact |
1292 |---------|--------|
1293 | **6-month test** | Can you understand the flow in 6 months? |
1294 | **Handoff ready** | New team member can maintain without meetings |
1295 | **Agentforce-ready** | AI can discover and use your flows correctly |
1296 | **Audit-friendly** | Compliance reviews understand business logic |
1297 | **Debug faster** | Element descriptions explain expected behavior |
1298 
1299 > **Rule of Thumb**: If you had to explain this Flow or element to a colleague, put that explanation in the description.
1300 
1301 ---
1302 
1303 ## Quick Reference Checklist
1304 
1305 ### Record-Triggered Flow Essentials
1306 - [ ] Use `$Record` directly - do NOT create loops over triggered records
1307 - [ ] Never use `$Record__c` (Process Builder pattern, doesn't exist in Flows)
1308 - [ ] Platform handles bulk batching - you don't need manual loops
1309 
1310 ### Get Records Best Practices
1311 - [ ] Use `$Record` instead of querying trigger object
1312 - [ ] Add filters to all Get Records elements
1313 - [ ] Enable `getFirstRecordOnly` when expecting single record
1314 - [ ] Disable `storeOutputAutomatically` (specify fields explicitly)
1315 - [ ] **For relationship data**: Use two-step query pattern (child → parent by ID)
1316 - [ ] Never query `Parent.Field` in queriedFields (not supported)
1317 
1318 ### Error Handling & DML
1319 - [ ] Add fault paths to all DML operations
1320 - [ ] Implement rollback for multi-step DML
1321 - [ ] Capture `$Flow.FaultMessage` in error handlers
1322 
1323 ### Naming & Organization
1324 - [ ] Use variable naming prefixes (`var_`, `col_`, `rec_`, etc.)
1325 - [ ] Add progress indicators to multi-screen flows
1326 
1327 ### Testing & Deployment
1328 - [ ] Test with bulk data (200+ records)
1329 - [ ] Keep flows in Draft until fully tested
1330 - [ ] **Always use sf-deploy skill** - never direct CLI commands
1331 
1332 ---
1333 
1334 ## Related Documentation
1335 
1336 - [Transform vs Loop Guide](./transform-vs-loop-guide.md) - When to use each element
1337 - [Flow Quick Reference](./flow-quick-reference.md) - Comprehensive cheat sheet
1338 - [Orchestration Guide](./orchestration-guide.md) - Parent-child and sequential patterns
1339 - [Subflow Library](./subflow-library.md) - Reusable subflow templates
1340 - [Testing Guide](./testing-guide.md) - Comprehensive testing strategies
1341 - [Governance Checklist](./governance-checklist.md) - Security and compliance
1342 - [XML Gotchas](./xml-gotchas.md) - Common XML pitfalls
