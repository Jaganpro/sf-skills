<!-- Parent: sf-flow/SKILL.md -->
   1 # Orchestration Pattern: Sequential
   2 
   3 ## Overview
   4 
   5 The **Sequential pattern** chains multiple flows together where each flow's output becomes the next flow's input. This creates a pipeline of transformations, with each step building on the previous one.
   6 
   7 ## When to Use This Pattern
   8 
   9 ✅ **Use Sequential when:**
  10 - Each step depends on the previous step's output
  11 - You need a multi-stage validation/approval process
  12 - Data flows through a transformation pipeline
  13 - Steps must execute in a specific order
  14 - Each stage can be developed and tested independently
  15 
  16 ❌ **Don't use when:**
  17 - Steps are independent and can run in parallel
  18 - Order doesn't matter
  19 - You need conditional branching (use Conditional pattern instead)
  20 
  21 ## Real-World Example: Order Processing Pipeline
  22 
  23 ### Business Requirement
  24 
  25 Process customer orders through multiple stages:
  26 1. **Validate Order**: Check inventory, pricing, customer credit
  27 2. **Calculate Tax**: Determine tax based on shipping address and products
  28 3. **Process Payment**: Charge payment method
  29 4. **Reserve Inventory**: Allocate products from warehouse
  30 5. **Generate Invoice**: Create invoice record and send to customer
  31 
  32 Each step depends on the previous step's success. If any step fails, the pipeline stops.
  33 
  34 ## Architecture
  35 
  36 ```
  37 Screen Flow: Order_Entry
  38     ↓ (User submits order)
  39 Auto Flow: Auto_ValidateOrder
  40     ↓ (Outputs: varIsValid, varValidationMessage)
  41 Auto Flow: Auto_CalculateTax
  42     ↓ (Outputs: varTaxAmount, varTotalAmount)
  43 Auto Flow: Auto_ProcessPayment
  44     ↓ (Outputs: varPaymentId, varPaymentStatus)
  45 Auto Flow: Auto_ReserveInventory
  46     ↓ (Outputs: varReservationId)
  47 Auto Flow: Auto_GenerateInvoice
  48     ↓ (Outputs: varInvoiceId)
  49 Screen Flow: Order_Confirmation (displays final results)
  50 ```
  51 
  52 ## Implementation
  53 
  54 ### Flow 1: Screen_OrderEntry
  55 
  56 ```xml
  57 <?xml version="1.0" encoding="UTF-8"?>
  58 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
  59     <apiVersion>65.0</apiVersion>
  60     <description>Entry point for order processing. Collects order details and initiates sequential pipeline.</description>
  61     <label>Screen_OrderEntry</label>
  62     <processType>Flow</processType>
  63 
  64     <!-- Screen: Collect Order Information -->
  65     <screens>
  66         <name>Order_Details_Screen</name>
  67         <label>Enter Order Details</label>
  68         <locationX>0</locationX>
  69         <locationY>0</locationY>
  70         <allowBack>true</allowBack>
  71         <allowFinish>true</allowFinish>
  72         <allowPause>false</allowPause>
  73         <connector>
  74             <targetReference>Validate_Order</targetReference>
  75         </connector>
  76         <fields>
  77             <name>ProductId</name>
  78             <dataType>String</dataType>
  79             <fieldText>Product</fieldText>
  80             <fieldType>InputField</fieldType>
  81             <isRequired>true</isRequired>
  82         </fields>
  83         <fields>
  84             <name>Quantity</name>
  85             <dataType>Number</dataType>
  86             <fieldText>Quantity</fieldText>
  87             <fieldType>InputField</fieldType>
  88             <isRequired>true</isRequired>
  89             <scale>0</scale>
  90         </fields>
  91         <fields>
  92             <name>ShippingAddress</name>
  93             <dataType>String</dataType>
  94             <fieldText>Shipping Address</fieldText>
  95             <fieldType>LargeTextArea</fieldType>
  96             <isRequired>true</isRequired>
  97         </fields>
  98         <showFooter>true</showFooter>
  99         <showHeader>true</showHeader>
 100     </screens>
 101 
 102     <!-- Step 1: Validate Order -->
 103     <subflows>
 104         <name>Validate_Order</name>
 105         <label>Validate Order</label>
 106         <locationX>0</locationX>
 107         <locationY>0</locationY>
 108         <connector>
 109             <targetReference>Check_Validation_Result</targetReference>
 110         </connector>
 111         <flowName>Auto_ValidateOrder</flowName>
 112         <inputAssignments>
 113             <name>varProductId</name>
 114             <value>
 115                 <elementReference>ProductId</elementReference>
 116             </value>
 117         </inputAssignments>
 118         <inputAssignments>
 119             <name>varQuantity</name>
 120             <value>
 121                 <elementReference>Quantity</elementReference>
 122             </value>
 123         </inputAssignments>
 124         <storeOutputAutomatically>true</storeOutputAutomatically>
 125     </subflows>
 126 
 127     <!-- Decision: Did validation pass? -->
 128     <decisions>
 129         <name>Check_Validation_Result</name>
 130         <label>Validation Passed?</label>
 131         <locationX>0</locationX>
 132         <locationY>0</locationY>
 133         <defaultConnector>
 134             <targetReference>Show_Validation_Error</targetReference>
 135         </defaultConnector>
 136         <defaultConnectorLabel>Failed</defaultConnectorLabel>
 137         <rules>
 138             <name>Validation_Passed</name>
 139             <conditionLogic>and</conditionLogic>
 140             <conditions>
 141                 <leftValueReference>Validate_Order.varIsValid</leftValueReference>
 142                 <operator>EqualTo</operator>
 143                 <rightValue>
 144                     <booleanValue>true</booleanValue>
 145                 </rightValue>
 146             </conditions>
 147             <connector>
 148                 <targetReference>Calculate_Tax</targetReference>
 149             </connector>
 150             <label>Passed</label>
 151         </rules>
 152     </decisions>
 153 
 154     <!-- Step 2: Calculate Tax (only if validation passed) -->
 155     <subflows>
 156         <name>Calculate_Tax</name>
 157         <label>Calculate Tax</label>
 158         <locationX>0</locationX>
 159         <locationY>0</locationY>
 160         <connector>
 161             <targetReference>Process_Payment</targetReference>
 162         </connector>
 163         <flowName>Auto_CalculateTax</flowName>
 164         <inputAssignments>
 165             <name>varProductId</name>
 166             <value>
 167                 <elementReference>ProductId</elementReference>
 168             </value>
 169         </inputAssignments>
 170         <inputAssignments>
 171             <name>varQuantity</name>
 172             <value>
 173                 <elementReference>Quantity</elementReference>
 174             </value>
 175         </inputAssignments>
 176         <inputAssignments>
 177             <name>varShippingAddress</name>
 178             <value>
 179                 <elementReference>ShippingAddress</elementReference>
 180             </value>
 181         </inputAssignments>
 182         <storeOutputAutomatically>true</storeOutputAutomatically>
 183     </subflows>
 184 
 185     <!-- Step 3: Process Payment (uses tax calculation output) -->
 186     <subflows>
 187         <name>Process_Payment</name>
 188         <label>Process Payment</label>
 189         <locationX>0</locationX>
 190         <locationY>0</locationY>
 191         <connector>
 192             <targetReference>Check_Payment_Result</targetReference>
 193         </connector>
 194         <flowName>Auto_ProcessPayment</flowName>
 195         <inputAssignments>
 196             <name>varTotalAmount</name>
 197             <value>
 198                 <elementReference>Calculate_Tax.varTotalAmount</elementReference>
 199             </value>
 200         </inputAssignments>
 201         <storeOutputAutomatically>true</storeOutputAutomatically>
 202     </subflows>
 203 
 204     <!-- Decision: Did payment succeed? -->
 205     <decisions>
 206         <name>Check_Payment_Result</name>
 207         <label>Payment Successful?</label>
 208         <locationX>0</locationX>
 209         <locationY>0</locationY>
 210         <defaultConnector>
 211             <targetReference>Show_Payment_Error</targetReference>
 212         </defaultConnector>
 213         <defaultConnectorLabel>Failed</defaultConnectorLabel>
 214         <rules>
 215             <name>Payment_Successful</name>
 216             <conditionLogic>and</conditionLogic>
 217             <conditions>
 218                 <leftValueReference>Process_Payment.varPaymentStatus</leftValueReference>
 219                 <operator>EqualTo</operator>
 220                 <rightValue>
 221                     <stringValue>Success</stringValue>
 222                 </rightValue>
 223             </conditions>
 224             <connector>
 225                 <targetReference>Reserve_Inventory</targetReference>
 226             </connector>
 227             <label>Success</label>
 228         </rules>
 229     </decisions>
 230 
 231     <!-- Step 4: Reserve Inventory (only after successful payment) -->
 232     <subflows>
 233         <name>Reserve_Inventory</name>
 234         <label>Reserve Inventory</label>
 235         <locationX>0</locationX>
 236         <locationY>0</locationY>
 237         <connector>
 238             <targetReference>Generate_Invoice</targetReference>
 239         </connector>
 240         <flowName>Auto_ReserveInventory</flowName>
 241         <inputAssignments>
 242             <name>varProductId</name>
 243             <value>
 244                 <elementReference>ProductId</elementReference>
 245             </value>
 246         </inputAssignments>
 247         <inputAssignments>
 248             <name>varQuantity</name>
 249             <value>
 250                 <elementReference>Quantity</elementReference>
 251             </value>
 252         </inputAssignments>
 253         <storeOutputAutomatically>true</storeOutputAutomatically>
 254     </subflows>
 255 
 256     <!-- Step 5: Generate Invoice (final step) -->
 257     <subflows>
 258         <name>Generate_Invoice</name>
 259         <label>Generate Invoice</label>
 260         <locationX>0</locationX>
 261         <locationY>0</locationY>
 262         <connector>
 263             <targetReference>Show_Confirmation</targetReference>
 264         </connector>
 265         <flowName>Auto_GenerateInvoice</flowName>
 266         <inputAssignments>
 267             <name>varProductId</name>
 268             <value>
 269                 <elementReference>ProductId</elementReference>
 270             </value>
 271         </inputAssignments>
 272         <inputAssignments>
 273             <name>varQuantity</name>
 274             <value>
 275                 <elementReference>Quantity</elementReference>
 276             </value>
 277         </inputAssignments>
 278         <inputAssignments>
 279             <name>varTaxAmount</name>
 280             <value>
 281                 <elementReference>Calculate_Tax.varTaxAmount</elementReference>
 282             </value>
 283         </inputAssignments>
 284         <inputAssignments>
 285             <name>varTotalAmount</name>
 286             <value>
 287                 <elementReference>Calculate_Tax.varTotalAmount</elementReference>
 288             </value>
 289         </inputAssignments>
 290         <inputAssignments>
 291             <name>varPaymentId</name>
 292             <value>
 293                 <elementReference>Process_Payment.varPaymentId</elementReference>
 294             </value>
 295         </inputAssignments>
 296         <storeOutputAutomatically>true</storeOutputAutomatically>
 297     </subflows>
 298 
 299     <!-- Success Screen -->
 300     <screens>
 301         <name>Show_Confirmation</name>
 302         <label>Order Confirmation</label>
 303         <locationX>0</locationX>
 304         <locationY>0</locationY>
 305         <allowBack>false</allowBack>
 306         <allowFinish>true</allowFinish>
 307         <allowPause>false</allowPause>
 308         <fields>
 309             <name>ConfirmationMessage</name>
 310             <fieldText>Order Successful! Invoice #{!Generate_Invoice.varInvoiceNumber} has been created.</fieldText>
 311             <fieldType>DisplayText</fieldType>
 312         </fields>
 313         <showFooter>true</showFooter>
 314         <showHeader>true</showHeader>
 315     </screens>
 316 
 317     <!-- Error Screens -->
 318     <screens>
 319         <name>Show_Validation_Error</name>
 320         <label>Validation Error</label>
 321         <locationX>0</locationX>
 322         <locationY>0</locationY>
 323         <allowBack>true</allowBack>
 324         <allowFinish>true</allowFinish>
 325         <allowPause>false</allowPause>
 326         <fields>
 327             <name>ValidationErrorMessage</name>
 328             <fieldText>Order validation failed: {!Validate_Order.varValidationMessage}</fieldText>
 329             <fieldType>DisplayText</fieldType>
 330         </fields>
 331         <showFooter>true</showFooter>
 332         <showHeader>true</showHeader>
 333     </screens>
 334 
 335     <screens>
 336         <name>Show_Payment_Error</name>
 337         <label>Payment Error</label>
 338         <locationX>0</locationX>
 339         <locationY>0</locationY>
 340         <allowBack>false</allowBack>
 341         <allowFinish>true</allowFinish>
 342         <allowPause>false</allowPause>
 343         <fields>
 344             <name>PaymentErrorMessage</name>
 345             <fieldText>Payment failed. Your order has not been processed.</fieldText>
 346             <fieldType>DisplayText</fieldType>
 347         </fields>
 348         <showFooter>true</showFooter>
 349         <showHeader>true</showHeader>
 350     </screens>
 351 
 352     <start>
 353         <locationX>0</locationX>
 354         <locationY>0</locationY>
 355         <connector>
 356             <targetReference>Order_Details_Screen</targetReference>
 357         </connector>
 358     </start>
 359     <status>Draft</status>
 360 </Flow>
 361 ```
 362 
 363 ### Flow 2: Auto_ValidateOrder
 364 
 365 ```xml
 366 <?xml version="1.0" encoding="UTF-8"?>
 367 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 368     <apiVersion>65.0</apiVersion>
 369     <description>First step in sequential pipeline. Validates order details and returns validation status.</description>
 370     <label>Auto_ValidateOrder</label>
 371     <processType>AutoLaunchedFlow</processType>
 372 
 373     <!-- Query Product for Availability Check -->
 374     <recordLookups>
 375         <name>Get_Product_Details</name>
 376         <label>Get Product Details</label>
 377         <locationX>0</locationX>
 378         <locationY>0</locationY>
 379         <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
 380         <connector>
 381             <targetReference>Check_Product_Found</targetReference>
 382         </connector>
 383         <filterLogic>and</filterLogic>
 384         <filters>
 385             <field>Id</field>
 386             <operator>EqualTo</operator>
 387             <value>
 388                 <elementReference>varProductId</elementReference>
 389             </value>
 390         </filters>
 391         <getFirstRecordOnly>true</getFirstRecordOnly>
 392         <object>Product2</object>
 393         <storeOutputAutomatically>true</storeOutputAutomatically>
 394     </recordLookups>
 395 
 396     <!-- Validation Logic -->
 397     <decisions>
 398         <name>Check_Product_Found</name>
 399         <label>Product Exists?</label>
 400         <locationX>0</locationX>
 401         <locationY>0</locationY>
 402         <defaultConnector>
 403             <targetReference>Set_Invalid_Product</targetReference>
 404         </defaultConnector>
 405         <defaultConnectorLabel>Not Found</defaultConnectorLabel>
 406         <rules>
 407             <name>Product_Exists</name>
 408             <conditionLogic>and</conditionLogic>
 409             <conditions>
 410                 <leftValueReference>Get_Product_Details</leftValueReference>
 411                 <operator>IsNull</operator>
 412                 <rightValue>
 413                     <booleanValue>false</booleanValue>
 414                 </rightValue>
 415             </conditions>
 416             <connector>
 417                 <targetReference>Check_Quantity</targetReference>
 418             </connector>
 419             <label>Exists</label>
 420         </rules>
 421     </decisions>
 422 
 423     <decisions>
 424         <name>Check_Quantity</name>
 425         <label>Quantity Valid?</label>
 426         <locationX>0</locationX>
 427         <locationY>0</locationY>
 428         <defaultConnector>
 429             <targetReference>Set_Invalid_Quantity</targetReference>
 430         </defaultConnector>
 431         <defaultConnectorLabel>Invalid</defaultConnectorLabel>
 432         <rules>
 433             <name>Quantity_Valid</name>
 434             <conditionLogic>and</conditionLogic>
 435             <conditions>
 436                 <leftValueReference>varQuantity</leftValueReference>
 437                 <operator>GreaterThan</operator>
 438                 <rightValue>
 439                     <numberValue>0.0</numberValue>
 440                 </rightValue>
 441             </conditions>
 442             <connector>
 443                 <targetReference>Set_Valid</targetReference>
 444             </connector>
 445             <label>Valid</label>
 446         </rules>
 447     </decisions>
 448 
 449     <!-- Set Validation Results -->
 450     <assignments>
 451         <name>Set_Valid</name>
 452         <label>Set Valid</label>
 453         <locationX>0</locationX>
 454         <locationY>0</locationY>
 455         <assignmentItems>
 456             <assignToReference>varIsValid</assignToReference>
 457             <operator>Assign</operator>
 458             <value>
 459                 <booleanValue>true</booleanValue>
 460             </value>
 461         </assignmentItems>
 462         <assignmentItems>
 463             <assignToReference>varValidationMessage</assignToReference>
 464             <operator>Assign</operator>
 465             <value>
 466                 <stringValue>Validation passed</stringValue>
 467             </value>
 468         </assignmentItems>
 469     </assignments>
 470 
 471     <assignments>
 472         <name>Set_Invalid_Product</name>
 473         <label>Set Invalid Product</label>
 474         <locationX>0</locationX>
 475         <locationY>0</locationY>
 476         <assignmentItems>
 477             <assignToReference>varIsValid</assignToReference>
 478             <operator>Assign</operator>
 479             <value>
 480                 <booleanValue>false</booleanValue>
 481             </value>
 482         </assignmentItems>
 483         <assignmentItems>
 484             <assignToReference>varValidationMessage</assignToReference>
 485             <operator>Assign</operator>
 486             <value>
 487                 <stringValue>Product not found</stringValue>
 488             </value>
 489         </assignmentItems>
 490     </assignments>
 491 
 492     <assignments>
 493         <name>Set_Invalid_Quantity</name>
 494         <label>Set Invalid Quantity</label>
 495         <locationX>0</locationX>
 496         <locationY>0</locationY>
 497         <assignmentItems>
 498             <assignToReference>varIsValid</assignToReference>
 499             <operator>Assign</operator>
 500             <value>
 501                 <booleanValue>false</booleanValue>
 502             </value>
 503         </assignmentItems>
 504         <assignmentItems>
 505             <assignToReference>varValidationMessage</assignToReference>
 506             <operator>Assign</operator>
 507             <value>
 508                 <stringValue>Quantity must be greater than 0</stringValue>
 509             </value>
 510         </assignmentItems>
 511     </assignments>
 512 
 513     <start>
 514         <locationX>0</locationX>
 515         <locationY>0</locationY>
 516         <connector>
 517             <targetReference>Get_Product_Details</targetReference>
 518         </connector>
 519     </start>
 520     <status>Draft</status>
 521 
 522     <!-- Input Variables -->
 523     <variables>
 524         <name>varProductId</name>
 525         <dataType>String</dataType>
 526         <isInput>true</isInput>
 527         <isOutput>false</isOutput>
 528     </variables>
 529     <variables>
 530         <name>varQuantity</name>
 531         <dataType>Number</dataType>
 532         <isInput>true</isInput>
 533         <isOutput>false</isOutput>
 534         <scale>0</scale>
 535     </variables>
 536 
 537     <!-- Output Variables -->
 538     <variables>
 539         <name>varIsValid</name>
 540         <dataType>Boolean</dataType>
 541         <isInput>false</isInput>
 542         <isOutput>true</isOutput>
 543         <value>
 544             <booleanValue>false</booleanValue>
 545         </value>
 546     </variables>
 547     <variables>
 548         <name>varValidationMessage</name>
 549         <dataType>String</dataType>
 550         <isInput>false</isInput>
 551         <isOutput>true</isOutput>
 552     </variables>
 553 </Flow>
 554 ```
 555 
 556 ## Key Characteristics
 557 
 558 ### 1. **Linear Flow**
 559 Each step executes only after the previous step completes:
 560 ```
 561 Step 1 → Output → Step 2 → Output → Step 3 → Output → Step 4
 562 ```
 563 
 564 ### 2. **Data Propagation**
 565 Outputs from earlier steps are passed as inputs to later steps:
 566 ```
 567 Calculate_Tax.varTotalAmount → Process_Payment.varTotalAmount
 568 Process_Payment.varPaymentId → Generate_Invoice.varPaymentId
 569 ```
 570 
 571 ### 3. **Fail-Fast Behavior**
 572 If any step fails, the pipeline stops:
 573 ```
 574 Validation Failed → Show Error → End (no further processing)
 575 Payment Failed → Show Error → End (inventory not reserved)
 576 ```
 577 
 578 ### 4. **Clear Exit Points**
 579 Each validation point can terminate the flow early, preventing unnecessary work.
 580 
 581 ## Benefits of Sequential Pattern
 582 
 583 ### ✅ Staged Processing
 584 - Break complex workflows into digestible stages
 585 - Each stage has clear inputs and outputs
 586 - Easy to understand flow of data
 587 
 588 ### ✅ Error Isolation
 589 - Know exactly which stage failed
 590 - Can retry individual stages
 591 - Log shows precise failure point
 592 
 593 ### ✅ Flexibility
 594 - Add new stages easily
 595 - Remove stages without affecting others
 596 - Reorder stages if dependencies allow
 597 
 598 ### ✅ Testing
 599 - Test each stage independently
 600 - Mock outputs for downstream testing
 601 - Verify data transformation at each step
 602 
 603 ## Common Use Cases
 604 
 605 1. **Order Processing**: Validate → Calculate → Charge → Fulfill → Invoice
 606 2. **Approval Workflows**: Submit → Manager Approval → Director Approval → Execute
 607 3. **Data Transformation**: Extract → Transform → Validate → Load
 608 4. **Document Generation**: Gather Data → Apply Template → Generate PDF → Send
 609 5. **Multi-Step Validation**: Check A → Check B → Check C → Approve
 610 
 611 ## Best Practices
 612 
 613 ### ✅ DO:
 614 
 615 1. **Define Clear Contracts**: Each flow should have well-defined inputs and outputs
 616 2. **Use Output Variables**: Pass data between stages via output variables
 617 3. **Validate at Each Stage**: Check prerequisites before expensive operations
 618 4. **Log Stage Completion**: Track which stages completed successfully
 619 5. **Design for Rollback**: Consider how to undo if later stages fail
 620 
 621 ### ❌ DON'T:
 622 
 623 1. **Create Circular Dependencies**: A → B → C → A (infinite loop!)
 624 2. **Skip Error Handling**: Every stage should have fault paths
 625 3. **Make Steps Too Large**: Each stage should do ONE thing well
 626 4. **Ignore Performance**: Sequential = slower than parallel (by design)
 627 5. **Hardcode Values**: Use variables to pass data between stages
 628 
 629 ## Performance Considerations
 630 
 631 ### Sequential = Longer Execution Time
 632 
 633 ```
 634 Parallel (3 seconds total):
 635 Step A (1s) ───┐
 636 Step B (1s) ───┼──→ Complete
 637 Step C (1s) ───┘
 638 
 639 Sequential (3 seconds total):
 640 Step A (1s) → Step B (1s) → Step C (1s) → Complete
 641 ```
 642 
 643 **Trade-off**: Sequential is slower but provides:
 644 - Better error handling
 645 - Clear data flow
 646 - Easier debugging
 647 - Predictable execution order
 648 
 649 ## Error Handling in Pipelines
 650 
 651 ### Strategy 1: Fail Fast
 652 Stop on first error (shown in example above)
 653 
 654 ### Strategy 2: Collect and Report
 655 Continue through all steps, collect all errors, report at end:
 656 
 657 ```xml
 658 <!-- Track errors but don't stop -->
 659 <assignments>
 660     <name>Add_To_Error_List</name>
 661     <assignmentItems>
 662         <assignToReference>colErrors</assignToReference>
 663         <operator>Add</operator>
 664         <value>
 665             <elementReference>$Flow.FaultMessage</elementReference>
 666         </value>
 667     </assignmentItems>
 668     <connector>
 669         <targetReference>Next_Step</targetReference>
 670     </connector>
 671 </assignments>
 672 ```
 673 
 674 ### Strategy 3: Retry Logic
 675 Attempt failed step again before failing:
 676 
 677 ```xml
 678 <decisions>
 679     <name>Check_Retry_Count</name>
 680     <rules>
 681         <name>Can_Retry</name>
 682         <conditions>
 683             <leftValueReference>varRetryCount</leftValueReference>
 684             <operator>LessThan</operator>
 685             <rightValue>
 686                 <numberValue>3.0</numberValue>
 687             </rightValue>
 688         </conditions>
 689         <connector>
 690             <targetReference>Increment_Retry</targetReference>
 691         </connector>
 692     </rules>
 693     <defaultConnector>
 694         <targetReference>Report_Failure</targetReference>
 695     </defaultConnector>
 696 </decisions>
 697 ```
 698 
 699 ## Related Patterns
 700 
 701 - [Parent-Child Orchestration](orchestration-parent-child.md) - Coordinate parallel operations
 702 - [Conditional Orchestration](orchestration-conditional.md) - Branch based on conditions
 703 - [Subflow Library](../references/subflow-library.md) - Reusable building blocks
 704 
 705 ## Summary
 706 
 707 **Sequential orchestration** creates clear, predictable workflows where each step builds on the previous one. While slower than parallel execution, the benefits of clear data flow, error isolation, and maintainability make it ideal for multi-stage processes with dependencies.
 708 
 709 **Key Takeaway**: If your workflow is "Step A must complete before Step B can start," use sequential orchestration. Each stage becomes a tested, reusable component in your automation pipeline. 🔗
