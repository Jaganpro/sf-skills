<!-- Parent: sf-flow/SKILL.md -->
   1 # Flow Orchestration Guide
   2 
   3 ## Introduction
   4 
   5 **Flow orchestration** is the practice of coordinating multiple flows to work together as a cohesive system. Instead of building large, monolithic flows, orchestration breaks complex automation into smaller, focused components that communicate through well-defined interfaces.
   6 
   7 ## Why Orchestrate?
   8 
   9 ### The Monolithic Flow Problem
  10 
  11 ```
  12 ❌ Single 800-Line Flow:
  13 RTF_Account_Update_Everything
  14 ├── Update 5 related objects (500 lines)
  15 ├── Send 3 different notifications (100 lines)
  16 ├── Complex validation logic (150 lines)
  17 └── Audit logging (50 lines)
  18 
  19 Problems:
  20 - Impossible to test individual pieces
  21 - Changes require full regression testing
  22 - Multiple teams can't work in parallel
  23 - Debugging is a nightmare
  24 - Can't reuse any logic elsewhere
  25 ```
  26 
  27 ### The Orchestrated Approach
  28 
  29 ```
  30 ✅ Parent + Children (200 lines total):
  31 RTF_Account_Update_Orchestrator (50 lines)
  32 ├── Sub_UpdateRelatedObjects (50 lines) ← Reusable!
  33 ├── Sub_SendNotifications (40 lines) ← Reusable!
  34 ├── Sub_ValidateChanges (30 lines) ← Reusable!
  35 └── Sub_AuditLog (30 lines) ← Reusable!
  36 
  37 Benefits:
  38 - Test each component independently
  39 - Change one without affecting others
  40 - Multiple teams own their components
  41 - Debug specific component easily
  42 - Reuse components across flows
  43 ```
  44 
  45 ## Three Core Orchestration Patterns
  46 
  47 ### 1. Parent-Child Pattern
  48 
  49 **Use when**: Complex task has multiple independent responsibilities
  50 
  51 **Structure**: Parent coordinates, children execute
  52 
  53 ```
  54 Parent (Orchestrator)
  55 ├── Child A (does one thing)
  56 ├── Child B (does another thing)
  57 └── Child C (does a third thing)
  58 ```
  59 
  60 **Example**: Account industry change
  61 - Parent: RTF_Account_IndustryChange_Orchestrator
  62 - Child 1: Update Contacts
  63 - Child 2: Update Opportunities
  64 - Child 3: Send Notifications
  65 
  66 **[Full Example →](../references/orchestration-parent-child.md)**
  67 
  68 ---
  69 
  70 ### 2. Sequential Pattern
  71 
  72 **Use when**: Each step depends on the previous step's output
  73 
  74 **Structure**: Linear pipeline with data flowing through stages
  75 
  76 ```
  77 Step 1 → Output → Step 2 → Output → Step 3 → Output → Step 4
  78 ```
  79 
  80 **Example**: Order processing
  81 - Step 1: Validate Order → (isValid, validationMessage)
  82 - Step 2: Calculate Tax → (taxAmount, totalAmount)
  83 - Step 3: Process Payment → (paymentId, status)
  84 - Step 4: Reserve Inventory → (reservationId)
  85 
  86 **[Full Example →](../references/orchestration-sequential.md)**
  87 
  88 ---
  89 
  90 ### 3. Conditional Pattern
  91 
  92 **Use when**: Different scenarios require completely different logic
  93 
  94 **Structure**: Router that directs to specialized handlers
  95 
  96 ```
  97 Parent (Router)
  98     ├── [Condition A] → Handler A
  99     ├── [Condition B] → Handler B
 100     ├── [Condition C] → Handler C
 101     └── [Default] → Handler D
 102 ```
 103 
 104 **Example**: Case triage
 105 - Critical → Escalate immediately
 106 - High + Technical → Create Jira ticket
 107 - High + Billing → Check payment status
 108 - Standard → Auto-assign
 109 
 110 **[Full Example →](../references/orchestration-conditional.md)**
 111 
 112 ---
 113 
 114 ## Choosing the Right Pattern
 115 
 116 ### Decision Tree
 117 
 118 ```
 119 Does each step depend on the previous step's output?
 120     ├── YES → Use Sequential Pattern
 121     │         (Order: Validate → Calculate → Charge → Fulfill)
 122     │
 123     └── NO → Are the steps completely independent?
 124             ├── YES → Use Parent-Child Pattern
 125             │         (Account: Update Contacts + Update Opps + Notify)
 126             │
 127             └── NO → Do different scenarios need different logic?
 128                     └── YES → Use Conditional Pattern
 129                               (Case: Route by priority and type)
 130 ```
 131 
 132 ### Pattern Comparison
 133 
 134 | Aspect | Parent-Child | Sequential | Conditional |
 135 |--------|-------------|-----------|------------|
 136 | **Execution** | All children run (parallel possible) | Steps run in order | One path runs |
 137 | **Dependencies** | Children independent | Each step needs previous output | Paths independent |
 138 | **Use Case** | Multi-responsibility task | Multi-stage pipeline | Scenario-based routing |
 139 | **Performance** | Fast (parallel possible) | Slower (sequential) | Fast (only one path) |
 140 | **Complexity** | Medium | Low | Medium |
 141 | **Testability** | Excellent (test each child) | Good (test each stage) | Excellent (test each path) |
 142 
 143 ## Best Practices
 144 
 145 ### 1. Design Principles
 146 
 147 #### Single Responsibility
 148 Each flow should do ONE thing well:
 149 ```xml
 150 ✅ GOOD:
 151 Sub_UpdateContactIndustry → Only updates Contact Industry field
 152 
 153 ❌ BAD:
 154 Sub_UpdateEverything → Updates Contacts, Opportunities, Cases, sends emails...
 155 ```
 156 
 157 #### Clear Interfaces
 158 Define explicit inputs and outputs:
 159 ```xml
 160 <!-- Good: Clear contract -->
 161 <variables>
 162     <name>varAccountId</name>
 163     <dataType>String</dataType>
 164     <isInput>true</isInput>
 165     <isOutput>false</isOutput>
 166 </variables>
 167 <variables>
 168     <name>varSuccessCount</name>
 169     <dataType>Number</dataType>
 170     <isInput>false</isInput>
 171     <isOutput>true</isOutput>
 172 </variables>
 173 ```
 174 
 175 #### Fail Fast
 176 Check prerequisites early, fail immediately if not met:
 177 ```xml
 178 <decisions>
 179     <name>Check_Prerequisites</name>
 180     <defaultConnector>
 181         <targetReference>Log_Error_And_Exit</targetReference>
 182     </defaultConnector>
 183     <rules>
 184         <name>Prerequisites_Met</name>
 185         <!-- Only proceed if everything is ready -->
 186         <connector>
 187             <targetReference>Begin_Processing</targetReference>
 188         </connector>
 189     </rules>
 190 </decisions>
 191 ```
 192 
 193 ---
 194 
 195 ### 2. Naming Conventions
 196 
 197 Use consistent prefixes to identify orchestration roles:
 198 
 199 | Prefix | Purpose | Example |
 200 |--------|---------|---------|
 201 | `RTF_` | Record-Triggered orchestrator | RTF_Account_UpdateOrchestrator |
 202 | `Auto_` | Autolaunched orchestrator | Auto_OrderProcessingPipeline |
 203 | `Sub_` | Reusable child/subflow | Sub_UpdateContactIndustry |
 204 | `Screen_` | Screen flow (UI) | Screen_OrderEntry |
 205 
 206 **Pattern**: `{Type}_{Object}_{Purpose}{Role}`
 207 
 208 Examples:
 209 - `RTF_Account_IndustryChange_Orchestrator` (parent)
 210 - `Sub_UpdateContactIndustry` (child)
 211 - `Auto_ValidateOrder` (sequential step)
 212 
 213 ---
 214 
 215 ### 3. Error Handling Strategy
 216 
 217 #### Each Child Handles Its Own Errors
 218 
 219 ```xml
 220 <!-- In child flow -->
 221 <recordUpdates>
 222     <name>Update_Records</name>
 223     <faultConnector>
 224         <targetReference>Log_Update_Error</targetReference>
 225     </faultConnector>
 226     <!-- ... -->
 227 </recordUpdates>
 228 
 229 <subflows>
 230     <name>Log_Update_Error</name>
 231     <flowName>Sub_LogError</flowName>
 232     <inputAssignments>
 233         <name>varFlowName</name>
 234         <value>
 235             <stringValue>Sub_UpdateContactIndustry</stringValue>
 236         </value>
 237     </inputAssignments>
 238     <inputAssignments>
 239         <name>varRecordId</name>
 240         <value>
 241             <elementReference>varAccountId</elementReference>
 242         </value>
 243     </inputAssignments>
 244     <inputAssignments>
 245         <name>varErrorMessage</name>
 246         <value>
 247             <elementReference>$Flow.FaultMessage</elementReference>
 248         </value>
 249     </inputAssignments>
 250 </subflows>
 251 ```
 252 
 253 #### Parent Monitors Overall Success
 254 
 255 ```xml
 256 <!-- In parent flow -->
 257 <decisions>
 258     <name>Check_Child_Success</name>
 259     <rules>
 260         <name>Child_Failed</name>
 261         <conditions>
 262             <leftValueReference>Update_Contacts.varSuccess</leftValueReference>
 263             <operator>EqualTo</operator>
 264             <rightValue>
 265                 <booleanValue>false</booleanValue>
 266             </rightValue>
 267         </conditions>
 268         <connector>
 269             <targetReference>Handle_Partial_Failure</targetReference>
 270         </connector>
 271     </rules>
 272     <defaultConnector>
 273         <targetReference>Continue_To_Next_Step</targetReference>
 274     </defaultConnector>
 275 </decisions>
 276 ```
 277 
 278 ---
 279 
 280 ### 4. Performance Optimization
 281 
 282 #### Minimize Subflow Calls in Loops
 283 
 284 ```xml
 285 ❌ BAD: Calling subflow 200 times
 286 <loops>
 287     <name>Loop_Through_Records</name>
 288     <collectionReference>Get_Records</collectionReference>
 289     <nextValueConnector>
 290         <targetReference>Call_Subflow_For_Each</targetReference><!-- BAD! -->
 291     </nextValueConnector>
 292 </loops>
 293 
 294 ✅ GOOD: Collect, then call subflow once
 295 <loops>
 296     <name>Loop_Through_Records</name>
 297     <collectionReference>Get_Records</collectionReference>
 298     <nextValueConnector>
 299         <targetReference>Add_To_Collection</targetReference>
 300     </nextValueConnector>
 301     <noMoreValuesConnector>
 302         <targetReference>Call_Subflow_Once_With_Collection</targetReference><!-- GOOD! -->
 303     </noMoreValuesConnector>
 304 </loops>
 305 ```
 306 
 307 #### Avoid Deep Nesting
 308 
 309 ```
 310 ✅ GOOD (3 levels):
 311 Parent → Child → Grandchild
 312 
 313 ⚠️ WARNING (5+ levels):
 314 Parent → Child → Grandchild → Great-grandchild → Great-great-grandchild
 315 
 316 Limit: Maximum 50 levels (governor limit)
 317 Recommended: Maximum 3-4 levels
 318 ```
 319 
 320 #### Use Bulkified Operations
 321 
 322 Each child should handle collections, not single records:
 323 
 324 ```xml
 325 <!-- Child accepts collection -->
 326 <variables>
 327     <name>colRecordsToProcess</name>
 328     <dataType>SObject</dataType>
 329     <isCollection>true</isCollection>
 330     <isInput>true</isInput>
 331 </variables>
 332 
 333 <!-- Bulk DML operation -->
 334 <recordUpdates>
 335     <name>Update_All_Records</name>
 336     <inputReference>colRecordsToProcess</inputReference>
 337     <!-- Processes entire collection in one DML -->
 338 </recordUpdates>
 339 ```
 340 
 341 ---
 342 
 343 ## Implementation Patterns
 344 
 345 ### Pattern 1: Fire-and-Forget
 346 
 347 Parent doesn't wait for children or check results:
 348 
 349 ```xml
 350 <subflows>
 351     <name>Send_Notification</name>
 352     <flowName>Sub_SendEmailAlert</flowName>
 353     <!-- No output checking, just fire it -->
 354     <connector>
 355         <targetReference>Next_Step</targetReference>
 356     </connector>
 357 </subflows>
 358 ```
 359 
 360 **Use when**: Child failure doesn't affect parent success (e.g., non-critical notifications)
 361 
 362 ---
 363 
 364 ### Pattern 2: Check-and-Continue
 365 
 366 Parent checks child result, then decides:
 367 
 368 ```xml
 369 <subflows>
 370     <name>Validate_Data</name>
 371     <flowName>Sub_ValidateRecord</flowName>
 372     <storeOutputAutomatically>true</storeOutputAutomatically>
 373     <connector>
 374         <targetReference>Check_Validation_Result</targetReference>
 375     </connector>
 376 </subflows>
 377 
 378 <decisions>
 379     <name>Check_Validation_Result</name>
 380     <rules>
 381         <name>Valid</name>
 382         <conditions>
 383             <leftValueReference>Validate_Data.varIsValid</leftValueReference>
 384             <operator>EqualTo</operator>
 385             <rightValue>
 386                 <booleanValue>true</booleanValue>
 387             </rightValue>
 388         </conditions>
 389         <connector>
 390             <targetReference>Continue_Processing</targetReference>
 391         </connector>
 392     </rules>
 393     <defaultConnector>
 394         <targetReference>Handle_Invalid_Data</targetReference>
 395     </defaultConnector>
 396 </decisions>
 397 ```
 398 
 399 **Use when**: Child result determines next step
 400 
 401 ---
 402 
 403 ### Pattern 3: Collect-and-Report
 404 
 405 Parent runs all children, collects results, reports summary:
 406 
 407 ```xml
 408 <!-- Run all children -->
 409 <subflows>
 410     <name>Update_Contacts</name>
 411     <flowName>Sub_UpdateContacts</flowName>
 412     <storeOutputAutomatically>true</storeOutputAutomatically>
 413     <connector>
 414         <targetReference>Update_Opportunities</targetReference>
 415     </connector>
 416 </subflows>
 417 
 418 <subflows>
 419     <name>Update_Opportunities</name>
 420     <flowName>Sub_UpdateOpportunities</flowName>
 421     <storeOutputAutomatically>true</storeOutputAutomatically>
 422     <connector>
 423         <targetReference>Generate_Summary</targetReference>
 424     </connector>
 425 </subflows>
 426 
 427 <!-- Collect results -->
 428 <assignments>
 429     <name>Generate_Summary</name>
 430     <assignmentItems>
 431         <assignToReference>varTotalRecordsUpdated</assignToReference>
 432         <operator>Add</operator>
 433         <value>
 434             <elementReference>Update_Contacts.varRecordCount</elementReference>
 435         </value>
 436     </assignmentItems>
 437     <assignmentItems>
 438         <assignToReference>varTotalRecordsUpdated</assignToReference>
 439         <operator>Add</operator>
 440         <value>
 441             <elementReference>Update_Opportunities.varRecordCount</elementReference>
 442         </value>
 443     </assignmentItems>
 444 </assignments>
 445 ```
 446 
 447 **Use when**: Parent needs to aggregate results from all children
 448 
 449 ---
 450 
 451 ## Testing Strategy
 452 
 453 ### Unit Testing Children
 454 
 455 Test each child flow independently:
 456 
 457 ```bash
 458 # Test Sub_UpdateContactIndustry
 459 1. Create 200 test Contacts linked to test Account
 460 2. Invoke Sub_UpdateContactIndustry via flow debug
 461 3. Verify all 200 Contacts updated
 462 4. Check no governor limit errors
 463 5. Verify error logging if fault injected
 464 ```
 465 
 466 ### Integration Testing Parents
 467 
 468 Test orchestration flow end-to-end:
 469 
 470 ```bash
 471 # Test RTF_Account_IndustryChange_Orchestrator
 472 1. Create test Account with related Contacts, Opportunities
 473 2. Update Account.Industry field
 474 3. Verify all children executed
 475 4. Check all related records updated
 476 5. Verify notifications sent
 477 6. Check audit logs created
 478 ```
 479 
 480 ### Bulk Testing
 481 
 482 Test with production-like volumes:
 483 
 484 ```bash
 485 # Bulk test orchestrated flows
 486 1. Use Data Loader to update 200 Accounts
 487 2. Monitor execution in Setup → Apex Jobs
 488 3. Check Flow_Error_Log__c for any failures
 489 4. Verify no governor limit errors
 490 5. Check debug logs for performance bottlenecks
 491 ```
 492 
 493 ---
 494 
 495 ## Common Anti-Patterns
 496 
 497 ### ❌ Anti-Pattern 1: God Flow
 498 
 499 One flow that does everything:
 500 
 501 ```
 502 RTF_Account_DoEverything
 503 ├── 500 lines of Contact updates
 504 ├── 400 lines of Opportunity updates
 505 ├── 300 lines of Case updates
 506 ├── 200 lines of notification logic
 507 └── 100 lines of audit logging
 508 
 509 Total: 1500 lines of unmaintainable spaghetti
 510 ```
 511 
 512 **Fix**: Break into orchestrator + specialized children
 513 
 514 ---
 515 
 516 ### ❌ Anti-Pattern 2: Circular Dependencies
 517 
 518 ```
 519 Flow A calls Flow B
 520 Flow B calls Flow C
 521 Flow C calls Flow A  ← INFINITE LOOP!
 522 ```
 523 
 524 **Fix**: Design clear flow hierarchy with no cycles
 525 
 526 ---
 527 
 528 ### ❌ Anti-Pattern 3: Chatty Orchestration
 529 
 530 ```
 531 Parent → Child A (1 record)
 532 Parent → Child A (1 record)
 533 Parent → Child A (1 record)
 534 ... 200 times
 535 
 536 Total: 200 subflow calls!
 537 ```
 538 
 539 **Fix**: Collect records, call child once with collection
 540 
 541 ---
 542 
 543 ### ❌ Anti-Pattern 4: Shared State
 544 
 545 ```
 546 Flow A sets global variable
 547 Flow B reads global variable
 548 Flow C modifies global variable
 549 
 550 Result: Unpredictable behavior based on execution order
 551 ```
 552 
 553 **Fix**: Pass data explicitly via input/output variables
 554 
 555 ---
 556 
 557 ## Troubleshooting
 558 
 559 ### "Subflow not found" Error
 560 
 561 ```
 562 ✅ Fix:
 563 1. Verify child flow is activated
 564 2. Check API name matches exactly (case-sensitive)
 565 3. Ensure child flow is deployed to target org
 566 ```
 567 
 568 ### "Too many subflow levels" Error
 569 
 570 ```
 571 ✅ Fix:
 572 1. Reduce nesting depth (max 50, recommend 3-4)
 573 2. Flatten hierarchy by combining some children
 574 3. Consider different orchestration pattern
 575 ```
 576 
 577 ### Performance Issues
 578 
 579 ```
 580 ✅ Fix:
 581 1. Profile flow execution in debug logs
 582 2. Check for DML/SOQL in loops
 583 3. Reduce number of subflow calls
 584 4. Use Transform element instead of loops
 585 5. Batch operations where possible
 586 ```
 587 
 588 ### Difficult Debugging
 589 
 590 ```
 591 ✅ Fix:
 592 1. Add descriptive element names
 593 2. Use Sub_LogError in all fault paths
 594 3. Add debug assignments to trace execution
 595 4. Test children independently first
 596 5. Use flow interview records to trace execution
 597 ```
 598 
 599 ---
 600 
 601 ## Governor Limits
 602 
 603 Orchestrated flows share governor limits across all components:
 604 
 605 | Limit | Value | Orchestration Impact |
 606 |-------|-------|---------------------|
 607 | SOQL Queries | 100 | Each child's queries count toward total |
 608 | DML Statements | 150 | Each child's DML counts toward total |
 609 | DML Rows | 10,000 | Shared across all children |
 610 | CPU Time | 10,000ms | Sum of all flow execution time |
 611 | Subflow Depth | 50 | Parent → Child → Grandchild... |
 612 
 613 **Tip**: Use `limits` method in debug logs to monitor consumption
 614 
 615 ---
 616 
 617 ## Version Control
 618 
 619 ### Organize by Pattern
 620 
 621 ```
 622 force-app/main/default/flows/
 623 ├── orchestrators/
 624 │   ├── RTF_Account_IndustryChange_Orchestrator.flow-meta.xml
 625 │   └── Auto_OrderProcessingPipeline.flow-meta.xml
 626 ├── subflows/
 627 │   ├── Sub_UpdateContactIndustry.flow-meta.xml
 628 │   ├── Sub_UpdateOpportunityStages.flow-meta.xml
 629 │   └── Sub_SendEmailAlert.flow-meta.xml
 630 └── standalone/
 631     └── Screen_SimpleForm.flow-meta.xml
 632 ```
 633 
 634 ### Dependency Documentation
 635 
 636 Create README documenting dependencies:
 637 
 638 ```markdown
 639 # Flow Dependencies
 640 
 641 ## RTF_Account_IndustryChange_Orchestrator
 642 - Calls: Sub_UpdateContactIndustry
 643 - Calls: Sub_UpdateOpportunityStages
 644 - Calls: Sub_SendEmailAlert
 645 
 646 ## Sub_UpdateContactIndustry
 647 - No dependencies
 648 
 649 ## Sub_UpdateOpportunityStages
 650 - Calls: Sub_LogError (error handling)
 651 ```
 652 
 653 ---
 654 
 655 ## Migration Strategy
 656 
 657 ### From Monolith to Orchestration
 658 
 659 #### Step 1: Identify Responsibilities
 660 Break down existing monolithic flow into distinct responsibilities
 661 
 662 #### Step 2: Extract Children
 663 Create child subflows for each responsibility
 664 
 665 #### Step 3: Create Orchestrator
 666 Build parent flow that calls children
 667 
 668 #### Step 4: Test Side-by-Side
 669 Run old and new flows in parallel (different trigger conditions)
 670 
 671 #### Step 5: Cutover
 672 Deactivate old flow, activate new orchestrated flows
 673 
 674 #### Step 6: Monitor
 675 Watch error logs and performance metrics
 676 
 677 ---
 678 
 679 ## Success Metrics
 680 
 681 ### Indicators of Good Orchestration
 682 
 683 ✅ **Modularity**: Average flow length < 200 lines
 684 ✅ **Reusability**: 40%+ of children used by multiple parents
 685 ✅ **Testability**: Can test each component independently
 686 ✅ **Maintainability**: Changes isolated to specific children
 687 ✅ **Performance**: No governor limit warnings
 688 ✅ **Observability**: Clear error logs showing which component failed
 689 
 690 ---
 691 
 692 ## Related Documentation
 693 
 694 - [Parent-Child Pattern Example](../references/orchestration-parent-child.md)
 695 - [Sequential Pattern Example](../references/orchestration-sequential.md)
 696 - [Conditional Pattern Example](../references/orchestration-conditional.md)
 697 - [Subflow Library](subflow-library.md)
 698 - [Error Logging Best Practices](../references/error-logging-example.md)
 699 
 700 ---
 701 
 702 ## Summary
 703 
 704 Flow orchestration transforms complex automations from unmaintainable monoliths into modular, testable systems. By applying the three core patterns—Parent-Child, Sequential, and Conditional—you can build robust, scalable automation that's easy to understand, test, and enhance.
 705 
 706 **Key Principles**:
 707 1. **Single Responsibility**: Each flow does one thing well
 708 2. **Clear Interfaces**: Explicit inputs and outputs
 709 3. **Error Handling**: Every component handles its own failures
 710 4. **Testability**: Independent testing of each component
 711 5. **Reusability**: Components used across multiple flows
 712 
 713 Start small: Identify one complex flow in your org and break it into an orchestrated architecture. The benefits become immediately apparent! 🚀
