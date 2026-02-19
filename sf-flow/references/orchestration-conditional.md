<!-- Parent: sf-flow/SKILL.md -->
   1 # Orchestration Pattern: Conditional
   2 
   3 ## Overview
   4 
   5 The **Conditional pattern** uses a parent flow to evaluate conditions and dynamically decide which child subflows to execute. Think of it as a smart router that directs automation down different paths based on business rules.
   6 
   7 ## When to Use This Pattern
   8 
   9 ✅ **Use Conditional when:**
  10 - Different scenarios require completely different logic
  11 - You want to avoid complex branching in a single flow
  12 - Child flows can be developed by different teams
  13 - Business rules determine which automation to run
  14 - You need to add new scenarios without modifying existing logic
  15 
  16 ❌ **Don't use when:**
  17 - All steps must execute regardless of conditions
  18 - Logic is simple (use inline decisions instead)
  19 - Conditions are trivial (no need for separate subflows)
  20 
  21 ## Real-World Example: Case Triage and Routing
  22 
  23 ### Business Requirement
  24 
  25 When a Case is created, route it to the appropriate team and apply appropriate automation based on priority and type:
  26 
  27 - **Priority = Critical** → Escalate immediately, page on-call engineer, create Slack alert
  28 - **Priority = High + Type = Technical** → Assign to senior support, create Jira ticket
  29 - **Priority = High + Type = Billing** → Assign to billing team, check payment status
  30 - **Priority = Medium/Low** → Standard assignment, send email notification
  31 
  32 Each scenario has completely different logic, so we route to specialized subflows.
  33 
  34 ## Architecture
  35 
  36 ```
  37 Parent: RTF_Case_TriageRouter (Decision Hub)
  38     ↓
  39     ├── [Critical] → Sub_EscalateCriticalCase
  40     │                 ├── Page on-call engineer
  41     │                 ├── Create Slack alert
  42     │                 └── Assign to escalation queue
  43     │
  44     ├── [High + Technical] → Sub_HandleTechnicalCase
  45     │                          ├── Assign to senior support
  46     │                          ├── Create Jira ticket
  47     │                          └── Set SLA timer
  48     │
  49     ├── [High + Billing] → Sub_HandleBillingCase
  50     │                        ├── Check payment status
  51     │                        ├── Assign to billing team
  52     │                        └── Generate payment report
  53     │
  54     └── [Medium/Low] → Sub_HandleStandardCase
  55                         ├── Auto-assign by round-robin
  56                         └── Send email notification
  57 ```
  58 
  59 ## Implementation
  60 
  61 ### Parent Flow: RTF_Case_TriageRouter
  62 
  63 ```xml
  64 <?xml version="1.0" encoding="UTF-8"?>
  65 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
  66     <apiVersion>65.0</apiVersion>
  67     <description>Conditional orchestrator that routes Cases to appropriate subflows based on priority and type.</description>
  68     <label>RTF_Case_TriageRouter</label>
  69     <processMetadataValues>
  70         <name>BuilderType</name>
  71         <value>
  72             <stringValue>LightningFlowBuilder</stringValue>
  73         </value>
  74     </processMetadataValues>
  75     <processType>AutoLaunchedFlow</processType>
  76 
  77     <!-- Routing Decision -->
  78     <decisions>
  79         <name>Route_By_Priority_And_Type</name>
  80         <label>Route By Priority And Type</label>
  81         <locationX>0</locationX>
  82         <locationY>0</locationY>
  83         <defaultConnector>
  84             <targetReference>Handle_Standard_Case</targetReference>
  85         </defaultConnector>
  86         <defaultConnectorLabel>Standard (Medium/Low)</defaultConnectorLabel>
  87 
  88         <!-- Rule 1: Critical Priority -->
  89         <rules>
  90             <name>Critical_Priority</name>
  91             <conditionLogic>and</conditionLogic>
  92             <conditions>
  93                 <leftValueReference>$Record.Priority</leftValueReference>
  94                 <operator>EqualTo</operator>
  95                 <rightValue>
  96                     <stringValue>Critical</stringValue>
  97                 </rightValue>
  98             </conditions>
  99             <connector>
 100                 <targetReference>Escalate_Critical_Case</targetReference>
 101             </connector>
 102             <label>Critical</label>
 103         </rules>
 104 
 105         <!-- Rule 2: High Priority + Technical -->
 106         <rules>
 107             <name>High_Priority_Technical</name>
 108             <conditionLogic>and</conditionLogic>
 109             <conditions>
 110                 <leftValueReference>$Record.Priority</leftValueReference>
 111                 <operator>EqualTo</operator>
 112                 <rightValue>
 113                     <stringValue>High</stringValue>
 114                 </rightValue>
 115             </conditions>
 116             <conditions>
 117                 <leftValueReference>$Record.Type</leftValueReference>
 118                 <operator>EqualTo</operator>
 119                 <rightValue>
 120                     <stringValue>Technical</stringValue>
 121                 </rightValue>
 122             </conditions>
 123             <connector>
 124                 <targetReference>Handle_Technical_Case</targetReference>
 125             </connector>
 126             <label>High + Technical</label>
 127         </rules>
 128 
 129         <!-- Rule 3: High Priority + Billing -->
 130         <rules>
 131             <name>High_Priority_Billing</name>
 132             <conditionLogic>and</conditionLogic>
 133             <conditions>
 134                 <leftValueReference>$Record.Priority</leftValueReference>
 135                 <operator>EqualTo</operator>
 136                 <rightValue>
 137                     <stringValue>High</stringValue>
 138                 </rightValue>
 139             </conditions>
 140             <conditions>
 141                 <leftValueReference>$Record.Type</leftValueReference>
 142                 <operator>EqualTo</operator>
 143                 <rightValue>
 144                     <stringValue>Billing</stringValue>
 145                 </rightValue>
 146             </conditions>
 147             <connector>
 148                 <targetReference>Handle_Billing_Case</targetReference>
 149             </connector>
 150             <label>High + Billing</label>
 151         </rules>
 152     </decisions>
 153 
 154     <!-- Subflow 1: Critical Case Escalation -->
 155     <subflows>
 156         <name>Escalate_Critical_Case</name>
 157         <label>Escalate Critical Case</label>
 158         <locationX>0</locationX>
 159         <locationY>0</locationY>
 160         <flowName>Sub_EscalateCriticalCase</flowName>
 161         <inputAssignments>
 162             <name>varCaseId</name>
 163             <value>
 164                 <elementReference>$Record.Id</elementReference>
 165             </value>
 166         </inputAssignments>
 167         <inputAssignments>
 168             <name>varCaseNumber</name>
 169             <value>
 170                 <elementReference>$Record.CaseNumber</elementReference>
 171             </value>
 172         </inputAssignments>
 173         <inputAssignments>
 174             <name>varSubject</name>
 175             <value>
 176                 <elementReference>$Record.Subject</elementReference>
 177             </value>
 178         </inputAssignments>
 179     </subflows>
 180 
 181     <!-- Subflow 2: Technical Case Handling -->
 182     <subflows>
 183         <name>Handle_Technical_Case</name>
 184         <label>Handle Technical Case</label>
 185         <locationX>0</locationX>
 186         <locationY>0</locationY>
 187         <flowName>Sub_HandleTechnicalCase</flowName>
 188         <inputAssignments>
 189             <name>varCaseId</name>
 190             <value>
 191                 <elementReference>$Record.Id</elementReference>
 192             </value>
 193         </inputAssignments>
 194         <inputAssignments>
 195             <name>varCaseNumber</name>
 196             <value>
 197                 <elementReference>$Record.CaseNumber</elementReference>
 198             </value>
 199         </inputAssignments>
 200         <inputAssignments>
 201             <name>varDescription</name>
 202             <value>
 203                 <elementReference>$Record.Description</elementReference>
 204             </value>
 205         </inputAssignments>
 206     </subflows>
 207 
 208     <!-- Subflow 3: Billing Case Handling -->
 209     <subflows>
 210         <name>Handle_Billing_Case</name>
 211         <label>Handle Billing Case</label>
 212         <locationX>0</locationX>
 213         <locationY>0</locationY>
 214         <flowName>Sub_HandleBillingCase</flowName>
 215         <inputAssignments>
 216             <name>varCaseId</name>
 217             <value>
 218                 <elementReference>$Record.Id</elementReference>
 219             </value>
 220         </inputAssignments>
 221         <inputAssignments>
 222             <name>varAccountId</name>
 223             <value>
 224                 <elementReference>$Record.AccountId</elementReference>
 225             </value>
 226         </inputAssignments>
 227     </subflows>
 228 
 229     <!-- Subflow 4: Standard Case Handling -->
 230     <subflows>
 231         <name>Handle_Standard_Case</name>
 232         <label>Handle Standard Case</label>
 233         <locationX>0</locationX>
 234         <locationY>0</locationY>
 235         <flowName>Sub_HandleStandardCase</flowName>
 236         <inputAssignments>
 237             <name>varCaseId</name>
 238             <value>
 239                 <elementReference>$Record.Id</elementReference>
 240             </value>
 241         </inputAssignments>
 242     </subflows>
 243 
 244     <start>
 245         <locationX>0</locationX>
 246         <locationY>0</locationY>
 247         <connector>
 248             <targetReference>Route_By_Priority_And_Type</targetReference>
 249         </connector>
 250         <object>Case</object>
 251         <recordTriggerType>Create</recordTriggerType>
 252         <triggerType>RecordAfterSave</triggerType>
 253     </start>
 254     <status>Draft</status>
 255 </Flow>
 256 ```
 257 
 258 ### Child Flow 1: Sub_EscalateCriticalCase
 259 
 260 ```xml
 261 <?xml version="1.0" encoding="UTF-8"?>
 262 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 263     <apiVersion>65.0</apiVersion>
 264     <description>Handles critical case escalation with immediate notifications and special routing.</description>
 265     <label>Sub_EscalateCriticalCase</label>
 266     <processType>AutoLaunchedFlow</processType>
 267 
 268     <!-- Step 1: Page On-Call Engineer -->
 269     <actionCalls>
 270         <name>Page_On_Call_Engineer</name>
 271         <label>Page On-Call Engineer</label>
 272         <locationX>0</locationX>
 273         <locationY>0</locationY>
 274         <actionName>PagerDuty_Trigger_Alert</actionName>
 275         <actionType>apex</actionType>
 276         <connector>
 277             <targetReference>Create_Slack_Alert</targetReference>
 278         </connector>
 279         <inputParameters>
 280             <name>caseId</name>
 281             <value>
 282                 <elementReference>varCaseId</elementReference>
 283             </value>
 284         </inputParameters>
 285         <inputParameters>
 286             <name>urgency</name>
 287             <value>
 288                 <stringValue>high</stringValue>
 289             </value>
 290         </inputParameters>
 291     </actionCalls>
 292 
 293     <!-- Step 2: Create Slack Alert -->
 294     <actionCalls>
 295         <name>Create_Slack_Alert</name>
 296         <label>Create Slack Alert</label>
 297         <locationX>0</locationX>
 298         <locationY>0</locationY>
 299         <actionName>Slack_Post_Message</actionName>
 300         <actionType>apex</actionType>
 301         <connector>
 302             <targetReference>Assign_To_Escalation_Queue</targetReference>
 303         </connector>
 304         <inputParameters>
 305             <name>channel</name>
 306             <value>
 307                 <stringValue>#critical-alerts</stringValue>
 308             </value>
 309         </inputParameters>
 310         <inputParameters>
 311             <name>message</name>
 312             <value>
 313                 <stringValue>🚨 CRITICAL CASE: {!varCaseNumber} - {!varSubject}</stringValue>
 314             </value>
 315         </inputParameters>
 316     </actionCalls>
 317 
 318     <!-- Step 3: Assign to Escalation Queue -->
 319     <recordUpdates>
 320         <name>Assign_To_Escalation_Queue</name>
 321         <label>Assign To Escalation Queue</label>
 322         <locationX>0</locationX>
 323         <locationY>0</locationY>
 324         <faultConnector>
 325             <targetReference>Log_Assignment_Error</targetReference>
 326         </faultConnector>
 327         <filterLogic>and</filterLogic>
 328         <filters>
 329             <field>Id</field>
 330             <operator>EqualTo</operator>
 331             <value>
 332                 <elementReference>varCaseId</elementReference>
 333             </value>
 334         </filters>
 335         <inputAssignments>
 336             <field>OwnerId</field>
 337             <value>
 338                 <stringValue>00G5e000001XYZ1</stringValue><!-- Escalation Queue ID -->
 339             </value>
 340         </inputAssignments>
 341         <inputAssignments>
 342             <field>Status</field>
 343             <value>
 344                 <stringValue>Escalated</stringValue>
 345             </value>
 346         </inputAssignments>
 347         <object>Case</object>
 348     </recordUpdates>
 349 
 350     <!-- Error Handler -->
 351     <subflows>
 352         <name>Log_Assignment_Error</name>
 353         <label>Log Assignment Error</label>
 354         <locationX>0</locationX>
 355         <locationY>0</locationY>
 356         <flowName>Sub_LogError</flowName>
 357         <inputAssignments>
 358             <name>varErrorMessage</name>
 359             <value>
 360                 <elementReference>$Flow.FaultMessage</elementReference>
 361             </value>
 362         </inputAssignments>
 363         <inputAssignments>
 364             <name>varFlowName</name>
 365             <value>
 366                 <stringValue>Sub_EscalateCriticalCase</stringValue>
 367             </value>
 368         </inputAssignments>
 369         <inputAssignments>
 370             <name>varRecordId</name>
 371             <value>
 372                 <elementReference>varCaseId</elementReference>
 373             </value>
 374         </inputAssignments>
 375     </subflows>
 376 
 377     <start>
 378         <locationX>0</locationX>
 379         <locationY>0</locationY>
 380         <connector>
 381             <targetReference>Page_On_Call_Engineer</targetReference>
 382         </connector>
 383     </start>
 384     <status>Draft</status>
 385 
 386     <!-- Input Variables -->
 387     <variables>
 388         <name>varCaseId</name>
 389         <dataType>String</dataType>
 390         <isInput>true</isInput>
 391         <isOutput>false</isOutput>
 392     </variables>
 393     <variables>
 394         <name>varCaseNumber</name>
 395         <dataType>String</dataType>
 396         <isInput>true</isInput>
 397         <isOutput>false</isOutput>
 398     </variables>
 399     <variables>
 400         <name>varSubject</name>
 401         <dataType>String</dataType>
 402         <isInput>true</isInput>
 403         <isOutput>false</isOutput>
 404     </variables>
 405 </Flow>
 406 ```
 407 
 408 ### Child Flow 2: Sub_HandleTechnicalCase
 409 
 410 ```xml
 411 <?xml version="1.0" encoding="UTF-8"?>
 412 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 413     <apiVersion>65.0</apiVersion>
 414     <description>Handles high-priority technical cases with Jira integration and senior support assignment.</description>
 415     <label>Sub_HandleTechnicalCase</label>
 416     <processType>AutoLaunchedFlow</processType>
 417 
 418     <!-- Step 1: Create Jira Ticket -->
 419     <actionCalls>
 420         <name>Create_Jira_Ticket</name>
 421         <label>Create Jira Ticket</label>
 422         <locationX>0</locationX>
 423         <locationY>0</locationY>
 424         <actionName>Jira_Create_Issue</actionName>
 425         <actionType>apex</actionType>
 426         <connector>
 427             <targetReference>Get_Senior_Support_Agent</targetReference>
 428         </connector>
 429         <inputParameters>
 430             <name>summary</name>
 431             <value>
 432                 <stringValue>SF Case {!varCaseNumber}</stringValue>
 433             </value>
 434         </inputParameters>
 435         <inputParameters>
 436             <name>description</name>
 437             <value>
 438                 <elementReference>varDescription</elementReference>
 439             </value>
 440         </inputParameters>
 441         <inputParameters>
 442             <name>priority</name>
 443             <value>
 444                 <stringValue>High</stringValue>
 445             </value>
 446         </inputParameters>
 447         <storeOutputAutomatically>true</storeOutputAutomatically>
 448     </actionCalls>
 449 
 450     <!-- Step 2: Get Available Senior Support Agent -->
 451     <recordLookups>
 452         <name>Get_Senior_Support_Agent</name>
 453         <label>Get Senior Support Agent</label>
 454         <locationX>0</locationX>
 455         <locationY>0</locationY>
 456         <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
 457         <connector>
 458             <targetReference>Assign_To_Senior_Support</targetReference>
 459         </connector>
 460         <filterLogic>and</filterLogic>
 461         <filters>
 462             <field>IsActive</field>
 463             <operator>EqualTo</operator>
 464             <value>
 465                 <booleanValue>true</booleanValue>
 466             </value>
 467         </filters>
 468         <filters>
 469             <field>UserRole.Name</field>
 470             <operator>EqualTo</operator>
 471             <value>
 472                 <stringValue>Senior Support Engineer</stringValue>
 473             </value>
 474         </filters>
 475         <getFirstRecordOnly>true</getFirstRecordOnly>
 476         <object>User</object>
 477         <sortField>NumberOfCasesAssigned__c</sortField>
 478         <sortOrder>Asc</sortOrder>
 479         <storeOutputAutomatically>true</storeOutputAutomatically>
 480     </recordLookups>
 481 
 482     <!-- Step 3: Assign Case -->
 483     <recordUpdates>
 484         <name>Assign_To_Senior_Support</name>
 485         <label>Assign To Senior Support</label>
 486         <locationX>0</locationX>
 487         <locationY>0</locationY>
 488         <filterLogic>and</filterLogic>
 489         <filters>
 490             <field>Id</field>
 491             <operator>EqualTo</operator>
 492             <value>
 493                 <elementReference>varCaseId</elementReference>
 494             </value>
 495         </filters>
 496         <inputAssignments>
 497             <field>OwnerId</field>
 498             <value>
 499                 <elementReference>Get_Senior_Support_Agent.Id</elementReference>
 500             </value>
 501         </inputAssignments>
 502         <inputAssignments>
 503             <field>Status</field>
 504             <value>
 505                 <stringValue>In Progress</stringValue>
 506             </value>
 507         </inputAssignments>
 508         <inputAssignments>
 509             <field>Jira_Ticket_Id__c</field>
 510             <value>
 511                 <elementReference>Create_Jira_Ticket.ticketId</elementReference>
 512             </value>
 513         </inputAssignments>
 514         <object>Case</object>
 515     </recordUpdates>
 516 
 517     <start>
 518         <locationX>0</locationX>
 519         <locationY>0</locationY>
 520         <connector>
 521             <targetReference>Create_Jira_Ticket</targetReference>
 522         </connector>
 523     </start>
 524     <status>Draft</status>
 525 
 526     <!-- Input Variables -->
 527     <variables>
 528         <name>varCaseId</name>
 529         <dataType>String</dataType>
 530         <isInput>true</isInput>
 531         <isOutput>false</isOutput>
 532     </variables>
 533     <variables>
 534         <name>varCaseNumber</name>
 535         <dataType>String</dataType>
 536         <isInput>true</isInput>
 537         <isOutput>false</isOutput>
 538     </variables>
 539     <variables>
 540         <name>varDescription</name>
 541         <dataType>String</dataType>
 542         <isInput>true</isInput>
 543         <isOutput>false</isOutput>
 544     </variables>
 545 </Flow>
 546 ```
 547 
 548 ## Key Characteristics
 549 
 550 ### 1. **Single Decision Point**
 551 All routing logic centralized in one decision element in the parent flow
 552 
 553 ### 2. **Mutually Exclusive Paths**
 554 Only ONE child subflow executes per scenario:
 555 ```
 556 If Critical → Sub_EscalateCriticalCase ONLY
 557 If High+Tech → Sub_HandleTechnicalCase ONLY
 558 If High+Billing → Sub_HandleBillingCase ONLY
 559 Else → Sub_HandleStandardCase ONLY
 560 ```
 561 
 562 ### 3. **Specialized Children**
 563 Each child flow is optimized for its specific scenario with unique logic
 564 
 565 ### 4. **Easy to Extend**
 566 Add new scenarios by adding new rules and new child subflows:
 567 ```xml
 568 <!-- Adding VIP customer handling -->
 569 <rules>
 570     <name>VIP_Customer</name>
 571     <conditions>
 572         <leftValueReference>$Record.Account.Type</leftValueReference>
 573         <operator>EqualTo</operator>
 574         <rightValue>
 575             <stringValue>VIP</stringValue>
 576         </rightValue>
 577     </conditions>
 578     <connector>
 579         <targetReference>Handle_VIP_Case</targetReference>
 580     </connector>
 581     <label>VIP Customer</label>
 582 </rules>
 583 ```
 584 
 585 ## Benefits of Conditional Pattern
 586 
 587 ### ✅ Separation of Concerns
 588 - Routing logic in parent
 589 - Business logic in children
 590 - No mixing of concerns
 591 
 592 ### ✅ Team Collaboration
 593 - Critical escalation team owns Sub_EscalateCriticalCase
 594 - Technical support team owns Sub_HandleTechnicalCase
 595 - Billing team owns Sub_HandleBillingCase
 596 - Teams work independently
 597 
 598 ### ✅ Simplified Testing
 599 - Test routing logic separately from business logic
 600 - Mock child subflows for parent testing
 601 - Test each child independently with representative data
 602 
 603 ### ✅ Performance Optimization
 604 - Only execute logic needed for the scenario
 605 - Avoid unnecessary queries and DML
 606 - Faster execution than "check everything" approach
 607 
 608 ### ✅ Maintainability
 609 - Add new scenarios without touching existing children
 610 - Modify specific scenario logic without affecting others
 611 - Clear separation makes debugging easier
 612 
 613 ## Common Use Cases
 614 
 615 1. **Case Routing**: Route by priority, type, product, geography
 616 2. **Lead Assignment**: Route by score, source, industry, region
 617 3. **Approval Routing**: Route by amount, requestor, department
 618 4. **Order Fulfillment**: Route by product type, shipping method, warehouse
 619 5. **Error Handling**: Route by error type, severity, system
 620 
 621 ## Best Practices
 622 
 623 ### ✅ DO:
 624 
 625 1. **Order Rules Carefully**: Most specific conditions first, default last
 626 2. **Document Decision Logic**: Clear labels and descriptions
 627 3. **Use Meaningful Names**: Sub_Handle{Scenario}Case, not Sub_Flow1
 628 4. **Keep Parent Lightweight**: Only routing logic, no business logic
 629 5. **Make Children Self-Contained**: Each child has everything it needs
 630 
 631 ### ❌ DON'T:
 632 
 633 1. **Duplicate Logic Across Children**: Extract common logic to shared subflows
 634 2. **Make Conditions Too Complex**: If routing is complex, simplify business rules
 635 3. **Forget the Default Path**: Always have a fallback scenario
 636 4. **Mix Routing and Business Logic**: Keep parent as pure router
 637 5. **Create Too Many Paths**: >10 paths suggests need for different pattern
 638 
 639 ## Advanced Pattern: Dynamic Routing
 640 
 641 For scenarios where routing rules are stored as metadata:
 642 
 643 ```xml
 644 <!-- Query routing rules from custom metadata -->
 645 <recordLookups>
 646     <name>Get_Routing_Rules</name>
 647     <label>Get Routing Rules</label>
 648     <object>Case_Routing_Rule__mdt</object>
 649     <filters>
 650         <field>IsActive__c</field>
 651         <operator>EqualTo</operator>
 652         <value>
 653             <booleanValue>true</booleanValue>
 654         </value>
 655     </filters>
 656     <sortField>Priority__c</sortField>
 657     <sortOrder>Asc</sortOrder>
 658     <storeOutputAutomatically>true</storeOutputAutomatically>
 659 </recordLookups>
 660 
 661 <!-- Loop through rules and evaluate -->
 662 <loops>
 663     <name>Evaluate_Routing_Rules</name>
 664     <collectionReference>Get_Routing_Rules</collectionReference>
 665     <iterationOrder>Asc</iterationOrder>
 666     <!-- Evaluate each rule until match found -->
 667 </loops>
 668 ```
 669 
 670 ## Performance Considerations
 671 
 672 ### Governor Limits
 673 - **DML Statements**: Only the executed child's DML counts (not all children)
 674 - **SOQL Queries**: Only the executed child's queries count
 675 - **Execution Time**: Faster than sequential (no unnecessary steps)
 676 
 677 ### Optimization Tips
 678 1. Order decision rules by frequency (most common first)
 679 2. Use indexed fields in routing conditions
 680 3. Keep routing decision fast (<100ms)
 681 4. Profile which paths execute most often
 682 
 683 ## Error Handling
 684 
 685 Each child should handle its own errors:
 686 
 687 ```xml
 688 <!-- In each child flow -->
 689 <recordUpdates>
 690     <name>Some_Operation</name>
 691     <faultConnector>
 692         <targetReference>Log_Child_Error</targetReference>
 693     </faultConnector>
 694     <!-- ... -->
 695 </recordUpdates>
 696 
 697 <subflows>
 698     <name>Log_Child_Error</name>
 699     <flowName>Sub_LogError</flowName>
 700     <inputAssignments>
 701         <name>varFlowName</name>
 702         <value>
 703             <stringValue>Sub_HandleTechnicalCase</stringValue>
 704         </value>
 705     </inputAssignments>
 706     <!-- ... -->
 707 </subflows>
 708 ```
 709 
 710 ## Related Patterns
 711 
 712 - [Parent-Child Orchestration](orchestration-parent-child.md) - Execute all children
 713 - [Sequential Orchestration](orchestration-sequential.md) - Chain flows in order
 714 - [Subflow Library](../references/subflow-library.md) - Reusable components
 715 
 716 ## Summary
 717 
 718 **Conditional orchestration** enables smart routing where a parent flow evaluates business rules and directs execution to specialized child subflows. This pattern creates maintainable, testable automation where teams can own their scenarios independently.
 719 
 720 **Key Takeaway**: If your flow has complex branching with statements like "If critical, do X, Y, Z; if high-priority technical, do A, B, C," use conditional orchestration. Each scenario becomes a focused, testable subflow. 🎯
