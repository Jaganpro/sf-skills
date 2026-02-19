<!-- Parent: sf-flow/SKILL.md -->
   1 # Orchestration Pattern: Parent-Child
   2 
   3 ## Overview
   4 
   5 The **Parent-Child pattern** is an orchestration approach where a parent flow coordinates multiple child subflows, each handling a specific responsibility. This creates modular, maintainable automation that's easier to test, debug, and enhance.
   6 
   7 ## When to Use This Pattern
   8 
   9 ✅ **Use Parent-Child when:**
  10 - Complex automation has multiple distinct steps
  11 - Different teams own different parts of the logic
  12 - You need to reuse steps across multiple parent flows
  13 - Testing and debugging large flows is difficult
  14 - Changes to one step shouldn't require retesting everything
  15 
  16 ❌ **Don't use when:**
  17 - Automation is simple with 1-2 steps
  18 - All logic is tightly coupled
  19 - Performance is critical (minimal subflow overhead acceptable)
  20 
  21 ## Real-World Example: Account Industry Change
  22 
  23 ### Business Requirement
  24 
  25 When an Account's Industry changes:
  26 1. Update all related Contacts with the new Industry
  27 2. Update all related Opportunities with Industry-specific Stage
  28 3. Send notification to Account Owner
  29 4. Log the change for audit purposes
  30 
  31 ### ❌ Monolithic Approach (Anti-Pattern)
  32 
  33 One large flow with everything inline:
  34 
  35 ```
  36 RTF_Account_IndustryChange
  37 ├── Get Related Contacts (150+ records)
  38 ├── Loop Through Contacts
  39 │   └── Update Each Contact (DML in loop! ❌)
  40 ├── Get Related Opportunities
  41 ├── Decision: Industry = "Technology"?
  42 │   ├── Yes → Update Stage to "Discovery"
  43 │   └── No → Update Stage to "Qualification"
  44 ├── Loop Through Opportunities
  45 │   └── Update Each Opportunity (DML in loop! ❌)
  46 ├── Send Email to Owner
  47 └── Create Audit Log
  48 
  49 Problems:
  50 - 400+ lines of XML
  51 - DML in loops causes bulk failures
  52 - Can't reuse Contact update logic elsewhere
  53 - Testing requires full end-to-end scenario
  54 - Debugging is painful
  55 ```
  56 
  57 ### ✅ Parent-Child Approach (Best Practice)
  58 
  59 Break into coordinated flows:
  60 
  61 ```
  62 Parent: RTF_Account_IndustryChange_Orchestrator
  63 ├── Child: Sub_UpdateContactIndustry (reusable)
  64 ├── Child: Sub_UpdateOpportunityStages (reusable)
  65 ├── Child: Sub_SendEmailAlert (from library)
  66 └── Child: Sub_CreateAuditLog (reusable)
  67 
  68 Benefits:
  69 - Each child is 50-100 lines
  70 - Each child can be tested independently
  71 - Children can be reused in other flows
  72 - Clear separation of concerns
  73 - Easy to add/remove steps
  74 ```
  75 
  76 ## Implementation
  77 
  78 ### Parent Flow: RTF_Account_IndustryChange_Orchestrator
  79 
  80 ```xml
  81 <?xml version="1.0" encoding="UTF-8"?>
  82 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
  83     <apiVersion>65.0</apiVersion>
  84     <description>Parent orchestrator that coordinates industry change automation. Calls child subflows for each responsibility.</description>
  85     <label>RTF_Account_IndustryChange_Orchestrator</label>
  86     <processMetadataValues>
  87         <name>BuilderType</name>
  88         <value>
  89             <stringValue>LightningFlowBuilder</stringValue>
  90         </value>
  91     </processMetadataValues>
  92     <processType>AutoLaunchedFlow</processType>
  93     <start>
  94         <locationX>0</locationX>
  95         <locationY>0</locationY>
  96         <connector>
  97             <targetReference>Update_Contacts</targetReference>
  98         </connector>
  99         <object>Account</object>
 100         <recordTriggerType>Update</recordTriggerType>
 101         <triggerType>RecordAfterSave</triggerType>
 102     </start>
 103     <status>Draft</status>
 104 
 105     <!-- Step 1: Update Related Contacts -->
 106     <subflows>
 107         <name>Update_Contacts</name>
 108         <label>Update Related Contacts</label>
 109         <locationX>0</locationX>
 110         <locationY>0</locationY>
 111         <connector>
 112             <targetReference>Update_Opportunities</targetReference>
 113         </connector>
 114         <flowName>Sub_UpdateContactIndustry</flowName>
 115         <inputAssignments>
 116             <name>varAccountId</name>
 117             <value>
 118                 <elementReference>$Record.Id</elementReference>
 119             </value>
 120         </inputAssignments>
 121         <inputAssignments>
 122             <name>varNewIndustry</name>
 123             <value>
 124                 <elementReference>$Record.Industry</elementReference>
 125             </value>
 126         </inputAssignments>
 127     </subflows>
 128 
 129     <!-- Step 2: Update Related Opportunities -->
 130     <subflows>
 131         <name>Update_Opportunities</name>
 132         <label>Update Related Opportunities</label>
 133         <locationX>0</locationX>
 134         <locationY>0</locationY>
 135         <connector>
 136             <targetReference>Notify_Owner</targetReference>
 137         </connector>
 138         <flowName>Sub_UpdateOpportunityStages</flowName>
 139         <inputAssignments>
 140             <name>varAccountId</name>
 141             <value>
 142                 <elementReference>$Record.Id</elementReference>
 143             </value>
 144         </inputAssignments>
 145         <inputAssignments>
 146             <name>varIndustry</name>
 147             <value>
 148                 <elementReference>$Record.Industry</elementReference>
 149             </value>
 150         </inputAssignments>
 151     </subflows>
 152 
 153     <!-- Step 3: Send Notification -->
 154     <subflows>
 155         <name>Notify_Owner</name>
 156         <label>Notify Account Owner</label>
 157         <locationX>0</locationX>
 158         <locationY>0</locationY>
 159         <connector>
 160             <targetReference>Create_Audit_Log</targetReference>
 161         </connector>
 162         <flowName>Sub_SendEmailAlert</flowName>
 163         <inputAssignments>
 164             <name>varEmailAddresses</name>
 165             <value>
 166                 <elementReference>$Record.Owner.Email</elementReference>
 167             </value>
 168         </inputAssignments>
 169         <inputAssignments>
 170             <name>varEmailSubject</name>
 171             <value>
 172                 <stringValue>Account Industry Updated</stringValue>
 173             </value>
 174         </inputAssignments>
 175         <inputAssignments>
 176             <name>varEmailBody</name>
 177             <value>
 178                 <stringValue>Account {!$Record.Name} industry changed to {!$Record.Industry}. Related records have been updated.</stringValue>
 179             </value>
 180         </inputAssignments>
 181     </subflows>
 182 
 183     <!-- Step 4: Audit Logging -->
 184     <subflows>
 185         <name>Create_Audit_Log</name>
 186         <label>Create Audit Log</label>
 187         <locationX>0</locationX>
 188         <locationY>0</locationY>
 189         <flowName>Sub_CreateAuditLog</flowName>
 190         <inputAssignments>
 191             <name>varObjectName</name>
 192             <value>
 193                 <stringValue>Account</stringValue>
 194             </value>
 195         </inputAssignments>
 196         <inputAssignments>
 197             <name>varRecordId</name>
 198             <value>
 199                 <elementReference>$Record.Id</elementReference>
 200             </value>
 201         </inputAssignments>
 202         <inputAssignments>
 203             <name>varFieldChanged</name>
 204             <value>
 205                 <stringValue>Industry</stringValue>
 206             </value>
 207         </inputAssignments>
 208         <inputAssignments>
 209             <name>varNewValue</name>
 210             <value>
 211                 <elementReference>$Record.Industry</elementReference>
 212             </value>
 213         </inputAssignments>
 214     </subflows>
 215 </Flow>
 216 ```
 217 
 218 ### Child Flow 1: Sub_UpdateContactIndustry
 219 
 220 ```xml
 221 <?xml version="1.0" encoding="UTF-8"?>
 222 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 223     <apiVersion>65.0</apiVersion>
 224     <description>Updates Industry field on all Contacts related to an Account. Bulkified and reusable.</description>
 225     <label>Sub_UpdateContactIndustry</label>
 226     <processType>AutoLaunchedFlow</processType>
 227 
 228     <!-- Get Related Contacts -->
 229     <recordLookups>
 230         <name>Get_Related_Contacts</name>
 231         <label>Get Related Contacts</label>
 232         <locationX>0</locationX>
 233         <locationY>0</locationY>
 234         <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
 235         <connector>
 236             <targetReference>Check_If_Contacts_Found</targetReference>
 237         </connector>
 238         <filterLogic>and</filterLogic>
 239         <filters>
 240             <field>AccountId</field>
 241             <operator>EqualTo</operator>
 242             <value>
 243                 <elementReference>varAccountId</elementReference>
 244             </value>
 245         </filters>
 246         <getFirstRecordOnly>false</getFirstRecordOnly>
 247         <object>Contact</object>
 248         <storeOutputAutomatically>true</storeOutputAutomatically>
 249     </recordLookups>
 250 
 251     <!-- Decision: Were contacts found? -->
 252     <decisions>
 253         <name>Check_If_Contacts_Found</name>
 254         <label>Contacts Found?</label>
 255         <locationX>0</locationX>
 256         <locationY>0</locationY>
 257         <defaultConnectorLabel>No Contacts</defaultConnectorLabel>
 258         <rules>
 259             <name>Contacts_Exist</name>
 260             <conditionLogic>and</conditionLogic>
 261             <conditions>
 262                 <leftValueReference>Get_Related_Contacts</leftValueReference>
 263                 <operator>IsNull</operator>
 264                 <rightValue>
 265                     <booleanValue>false</booleanValue>
 266                 </rightValue>
 267             </conditions>
 268             <connector>
 269                 <targetReference>Update_Contacts_Bulk</targetReference>
 270             </connector>
 271             <label>Contacts Exist</label>
 272         </rules>
 273     </decisions>
 274 
 275     <!-- Bulk Update (NO DML in loops!) -->
 276     <recordUpdates>
 277         <name>Update_Contacts_Bulk</name>
 278         <label>Update Contacts (Bulk)</label>
 279         <locationX>0</locationX>
 280         <locationY>0</locationY>
 281         <faultConnector>
 282             <targetReference>Log_Update_Error</targetReference>
 283         </faultConnector>
 284         <inputAssignments>
 285             <field>Industry</field>
 286             <value>
 287                 <elementReference>varNewIndustry</elementReference>
 288             </value>
 289         </inputAssignments>
 290         <inputReference>Get_Related_Contacts</inputReference>
 291     </recordUpdates>
 292 
 293     <!-- Error Handler -->
 294     <subflows>
 295         <name>Log_Update_Error</name>
 296         <label>Log Update Error</label>
 297         <locationX>0</locationX>
 298         <locationY>0</locationY>
 299         <flowName>Sub_LogError</flowName>
 300         <inputAssignments>
 301             <name>varErrorMessage</name>
 302             <value>
 303                 <elementReference>$Flow.FaultMessage</elementReference>
 304             </value>
 305         </inputAssignments>
 306         <inputAssignments>
 307             <name>varFlowName</name>
 308             <value>
 309                 <stringValue>Sub_UpdateContactIndustry</stringValue>
 310             </value>
 311         </inputAssignments>
 312         <inputAssignments>
 313             <name>varRecordId</name>
 314             <value>
 315                 <elementReference>varAccountId</elementReference>
 316             </value>
 317         </inputAssignments>
 318     </subflows>
 319 
 320     <start>
 321         <locationX>0</locationX>
 322         <locationY>0</locationY>
 323         <connector>
 324             <targetReference>Get_Related_Contacts</targetReference>
 325         </connector>
 326     </start>
 327     <status>Draft</status>
 328 
 329     <!-- Input Variables -->
 330     <variables>
 331         <name>varAccountId</name>
 332         <dataType>String</dataType>
 333         <isInput>true</isInput>
 334         <isOutput>false</isOutput>
 335     </variables>
 336     <variables>
 337         <name>varNewIndustry</name>
 338         <dataType>String</dataType>
 339         <isInput>true</isInput>
 340         <isOutput>false</isOutput>
 341     </variables>
 342 </Flow>
 343 ```
 344 
 345 ### Child Flow 2: Sub_UpdateOpportunityStages
 346 
 347 ```xml
 348 <?xml version="1.0" encoding="UTF-8"?>
 349 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 350     <apiVersion>65.0</apiVersion>
 351     <description>Updates Opportunity Stages based on Industry. Demonstrates conditional logic in child flows.</description>
 352     <label>Sub_UpdateOpportunityStages</label>
 353     <processType>AutoLaunchedFlow</processType>
 354 
 355     <!-- Get Related Opportunities -->
 356     <recordLookups>
 357         <name>Get_Related_Opportunities</name>
 358         <label>Get Related Opportunities</label>
 359         <locationX>0</locationX>
 360         <locationY>0</locationY>
 361         <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
 362         <connector>
 363             <targetReference>Check_If_Opportunities_Found</targetReference>
 364         </connector>
 365         <filterLogic>and</filterLogic>
 366         <filters>
 367             <field>AccountId</field>
 368             <operator>EqualTo</operator>
 369             <value>
 370                 <elementReference>varAccountId</elementReference>
 371             </value>
 372         </filters>
 373         <filters>
 374             <field>IsClosed</field>
 375             <operator>EqualTo</operator>
 376             <value>
 377                 <booleanValue>false</booleanValue>
 378             </value>
 379         </filters>
 380         <getFirstRecordOnly>false</getFirstRecordOnly>
 381         <object>Opportunity</object>
 382         <storeOutputAutomatically>true</storeOutputAutomatically>
 383     </recordLookups>
 384 
 385     <!-- Decision: Were opportunities found? -->
 386     <decisions>
 387         <name>Check_If_Opportunities_Found</name>
 388         <label>Opportunities Found?</label>
 389         <locationX>0</locationX>
 390         <locationY>0</locationY>
 391         <defaultConnectorLabel>No Opportunities</defaultConnectorLabel>
 392         <rules>
 393             <name>Opportunities_Exist</name>
 394             <conditionLogic>and</conditionLogic>
 395             <conditions>
 396                 <leftValueReference>Get_Related_Opportunities</leftValueReference>
 397                 <operator>IsNull</operator>
 398                 <rightValue>
 399                     <booleanValue>false</booleanValue>
 400                 </rightValue>
 401             </conditions>
 402             <connector>
 403                 <targetReference>Determine_Stage_By_Industry</targetReference>
 404             </connector>
 405             <label>Opportunities Exist</label>
 406         </rules>
 407     </decisions>
 408 
 409     <!-- Decision: Which stage based on Industry? -->
 410     <decisions>
 411         <name>Determine_Stage_By_Industry</name>
 412         <label>Determine Stage By Industry</label>
 413         <locationX>0</locationX>
 414         <locationY>0</locationY>
 415         <defaultConnector>
 416             <targetReference>Set_Default_Stage</targetReference>
 417         </defaultConnector>
 418         <defaultConnectorLabel>Other Industries</defaultConnectorLabel>
 419         <rules>
 420             <name>Technology_Industry</name>
 421             <conditionLogic>and</conditionLogic>
 422             <conditions>
 423                 <leftValueReference>varIndustry</leftValueReference>
 424                 <operator>EqualTo</operator>
 425                 <rightValue>
 426                     <stringValue>Technology</stringValue>
 427                 </rightValue>
 428             </conditions>
 429             <connector>
 430                 <targetReference>Set_Technology_Stage</targetReference>
 431             </connector>
 432             <label>Technology</label>
 433         </rules>
 434         <rules>
 435             <name>Healthcare_Industry</name>
 436             <conditionLogic>and</conditionLogic>
 437             <conditions>
 438                 <leftValueReference>varIndustry</leftValueReference>
 439                 <operator>EqualTo</operator>
 440                 <rightValue>
 441                     <stringValue>Healthcare</stringValue>
 442                 </rightValue>
 443             </conditions>
 444             <connector>
 445                 <targetReference>Set_Healthcare_Stage</targetReference>
 446             </connector>
 447             <label>Healthcare</label>
 448         </rules>
 449     </decisions>
 450 
 451     <!-- Assignment: Technology Stage -->
 452     <assignments>
 453         <name>Set_Technology_Stage</name>
 454         <label>Set Technology Stage</label>
 455         <locationX>0</locationX>
 456         <locationY>0</locationY>
 457         <assignmentItems>
 458             <assignToReference>varNewStage</assignToReference>
 459             <operator>Assign</operator>
 460             <value>
 461                 <stringValue>Discovery</stringValue>
 462             </value>
 463         </assignmentItems>
 464         <connector>
 465             <targetReference>Update_Opportunity_Stages</targetReference>
 466         </connector>
 467     </assignments>
 468 
 469     <!-- Assignment: Healthcare Stage -->
 470     <assignments>
 471         <name>Set_Healthcare_Stage</name>
 472         <label>Set Healthcare Stage</label>
 473         <locationX>0</locationX>
 474         <locationY>0</locationY>
 475         <assignmentItems>
 476             <assignToReference>varNewStage</assignToReference>
 477             <operator>Assign</operator>
 478             <value>
 479                 <stringValue>Needs Analysis</stringValue>
 480             </value>
 481         </assignmentItems>
 482         <connector>
 483             <targetReference>Update_Opportunity_Stages</targetReference>
 484         </connector>
 485     </assignments>
 486 
 487     <!-- Assignment: Default Stage -->
 488     <assignments>
 489         <name>Set_Default_Stage</name>
 490         <label>Set Default Stage</label>
 491         <locationX>0</locationX>
 492         <locationY>0</locationY>
 493         <assignmentItems>
 494             <assignToReference>varNewStage</assignToReference>
 495             <operator>Assign</operator>
 496             <value>
 497                 <stringValue>Qualification</stringValue>
 498             </value>
 499         </assignmentItems>
 500         <connector>
 501             <targetReference>Update_Opportunity_Stages</targetReference>
 502         </connector>
 503     </assignments>
 504 
 505     <!-- Bulk Update Opportunities -->
 506     <recordUpdates>
 507         <name>Update_Opportunity_Stages</name>
 508         <label>Update Opportunity Stages</label>
 509         <locationX>0</locationX>
 510         <locationY>0</locationY>
 511         <faultConnector>
 512             <targetReference>Log_Update_Error</targetReference>
 513         </faultConnector>
 514         <inputAssignments>
 515             <field>StageName</field>
 516             <value>
 517                 <elementReference>varNewStage</elementReference>
 518             </value>
 519         </inputAssignments>
 520         <inputReference>Get_Related_Opportunities</inputReference>
 521     </recordUpdates>
 522 
 523     <!-- Error Handler -->
 524     <subflows>
 525         <name>Log_Update_Error</name>
 526         <label>Log Update Error</label>
 527         <locationX>0</locationX>
 528         <locationY>0</locationY>
 529         <flowName>Sub_LogError</flowName>
 530         <inputAssignments>
 531             <name>varErrorMessage</name>
 532             <value>
 533                 <elementReference>$Flow.FaultMessage</elementReference>
 534             </value>
 535         </inputAssignments>
 536         <inputAssignments>
 537             <name>varFlowName</name>
 538             <value>
 539                 <stringValue>Sub_UpdateOpportunityStages</stringValue>
 540             </value>
 541         </inputAssignments>
 542         <inputAssignments>
 543             <name>varRecordId</name>
 544             <value>
 545                 <elementReference>varAccountId</elementReference>
 546             </value>
 547         </inputAssignments>
 548     </subflows>
 549 
 550     <start>
 551         <locationX>0</locationX>
 552         <locationY>0</locationY>
 553         <connector>
 554             <targetReference>Get_Related_Opportunities</targetReference>
 555         </connector>
 556     </start>
 557     <status>Draft</status>
 558 
 559     <!-- Variables -->
 560     <variables>
 561         <name>varAccountId</name>
 562         <dataType>String</dataType>
 563         <isInput>true</isInput>
 564         <isOutput>false</isOutput>
 565     </variables>
 566     <variables>
 567         <name>varIndustry</name>
 568         <dataType>String</dataType>
 569         <isInput>true</isInput>
 570         <isOutput>false</isOutput>
 571     </variables>
 572     <variables>
 573         <name>varNewStage</name>
 574         <dataType>String</dataType>
 575         <isInput>false</isInput>
 576         <isOutput>false</isOutput>
 577     </variables>
 578 </Flow>
 579 ```
 580 
 581 ## Benefits of This Pattern
 582 
 583 ### 1. **Modularity**
 584 Each child flow has one clear responsibility:
 585 - Sub_UpdateContactIndustry: Only handles Contact updates
 586 - Sub_UpdateOpportunityStages: Only handles Opportunity logic
 587 - Sub_SendEmailAlert: Only handles notifications
 588 
 589 ### 2. **Reusability**
 590 Child flows can be called from multiple parents:
 591 ```
 592 RTF_Account_IndustryChange → Sub_UpdateContactIndustry
 593 RTF_Account_Merge → Sub_UpdateContactIndustry
 594 Auto_BulkIndustryUpdate → Sub_UpdateContactIndustry
 595 ```
 596 
 597 ### 3. **Testability**
 598 Test each child independently:
 599 - Unit test: Sub_UpdateContactIndustry with 200 Contacts
 600 - Unit test: Sub_UpdateOpportunityStages with various Industries
 601 - Integration test: Parent flow with full scenario
 602 
 603 ### 4. **Maintainability**
 604 Update logic in one place:
 605 - Need to change Contact update logic? Edit Sub_UpdateContactIndustry
 606 - All parent flows automatically get the update
 607 - No need to find/replace across multiple flows
 608 
 609 ### 5. **Debugging**
 610 Clear error isolation:
 611 - Error in Contact update? Check Sub_UpdateContactIndustry logs
 612 - Parent flow shows which step failed
 613 - Error logs show exact subflow name
 614 
 615 ## Performance Considerations
 616 
 617 ### Governor Limits
 618 - **Subflow Depth**: Max 50 levels (parent → child → grandchild...)
 619 - **DML Statements**: Each child's DML counts toward 150 limit
 620 - **SOQL Queries**: Each child's query counts toward 100 limit
 621 
 622 ### Best Practices
 623 ✅ Keep parent flow lightweight (orchestration only)
 624 ✅ Put complex logic in children
 625 ✅ Use bulkified operations in each child
 626 ✅ Monitor total DML/SOQL across all children
 627 
 628 ## Testing Strategy
 629 
 630 ### 1. Unit Test Each Child
 631 ```bash
 632 # Test Sub_UpdateContactIndustry
 633 Create 200 test Contacts → Manually invoke flow → Verify all updated
 634 ```
 635 
 636 ### 2. Integration Test Parent
 637 ```bash
 638 # Test full orchestration
 639 Update Account Industry → Verify all children executed → Check audit logs
 640 ```
 641 
 642 ### 3. Bulk Test
 643 ```bash
 644 # Test with 200+ Accounts
 645 Data Loader update 200 Accounts → Verify no governor limit errors
 646 ```
 647 
 648 ## When to Add More Children
 649 
 650 Add a new child subflow when:
 651 - New requirement emerges (e.g., "Also update Cases")
 652 - Existing child gets too complex (>200 lines)
 653 - You need to reuse logic elsewhere
 654 
 655 ```xml
 656 <!-- Adding a new step is easy -->
 657 <subflows>
 658     <name>Update_Cases</name>
 659     <label>Update Related Cases</label>
 660     <locationX>0</locationX>
 661     <locationY>0</locationY>
 662     <connector>
 663         <targetReference>Notify_Owner</targetReference>
 664     </connector>
 665     <flowName>Sub_UpdateCaseIndustry</flowName>
 666     <inputAssignments>
 667         <name>varAccountId</name>
 668         <value>
 669             <elementReference>$Record.Id</elementReference>
 670         </value>
 671     </inputAssignments>
 672     <inputAssignments>
 673         <name>varIndustry</name>
 674         <value>
 675             <elementReference>$Record.Industry</elementReference>
 676         </value>
 677     </inputAssignments>
 678 </subflows>
 679 ```
 680 
 681 ## Related Patterns
 682 
 683 - [Sequential Orchestration](orchestration-sequential.md) - Chain flows A → B → C
 684 - [Conditional Orchestration](orchestration-conditional.md) - Parent decides which children to call
 685 - [Subflow Library](../references/subflow-library.md) - Reusable subflow templates
 686 
 687 ## Summary
 688 
 689 **Parent-Child orchestration** transforms complex automations from monolithic nightmares into modular, maintainable architectures. Each child flow is focused, testable, and reusable—making your entire automation ecosystem more robust.
 690 
 691 **Key Takeaway**: If your flow has more than 3 distinct responsibilities, consider breaking it into a parent orchestrator with child subflows. Your future self (and your team) will thank you! 🚀
