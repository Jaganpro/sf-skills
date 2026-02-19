<!-- Parent: sf-flow/SKILL.md -->
   1 # Reusable Subflow Library
   2 
   3 ## Overview
   4 
   5 The Subflow Library provides pre-built, production-ready subflows that accelerate flow development and enforce best practices. Instead of recreating common patterns, use these standardized components to build flows faster while maintaining consistency.
   6 
   7 **Benefits:**
   8 - ⚡ **Faster Development**: Pre-built patterns save 30-50% development time
   9 - 🔒 **Built-in Error Handling**: Fault paths and logging included
  10 - ✅ **Best Practices**: Bulkified, tested, and validated
  11 - 🔄 **Reusable**: One subflow, many parent flows
  12 - 📊 **Maintainable**: Update once, improve everywhere
  13 
  14 ---
  15 
  16 ## Available Subflows
  17 
  18 ### 1. Sub_LogError
  19 **Purpose**: Structured error logging for fault paths
  20 **File**: `assets/subflows/subflow-error-logger.xml`
  21 
  22 **When to Use**:
  23 - In fault paths of DML operations
  24 - When you need to capture and track flow failures
  25 - For production observability and debugging
  26 
  27 **Input Variables**:
  28 - `varFlowName` (String): Name of the calling flow
  29 - `varRecordId` (String): ID of the record being processed
  30 - `varErrorMessage` (String): Error message (typically `$Flow.FaultMessage`)
  31 
  32 **Output Variables**: None
  33 
  34 **Example**:
  35 ```xml
  36 <subflows>
  37     <name>Log_Update_Error</name>
  38     <flowName>Sub_LogError</flowName>
  39     <inputAssignments>
  40         <name>varFlowName</name>
  41         <value>
  42             <stringValue>RTF_Account_UpdateIndustry</stringValue>
  43         </value>
  44     </inputAssignments>
  45     <inputAssignments>
  46         <name>varRecordId</name>
  47         <value>
  48             <elementReference>$Record.Id</elementReference>
  49         </value>
  50     </inputAssignments>
  51     <inputAssignments>
  52         <name>varErrorMessage</name>
  53         <value>
  54             <elementReference>$Flow.FaultMessage</elementReference>
  55         </value>
  56     </inputAssignments>
  57 </subflows>
  58 ```
  59 
  60 **Prerequisites**:
  61 Create Flow_Error_Log__c custom object with fields:
  62 - `Flow_Name__c` (Text, 255)
  63 - `Record_Id__c` (Text, 18)
  64 - `Error_Message__c` (Long Text Area, 32,768)
  65 
  66 **Related**: [Error Logging Example](../references/error-logging-example.md)
  67 
  68 ---
  69 
  70 ### 2. Sub_SendEmailAlert
  71 **Purpose**: Standard email notifications
  72 **File**: `assets/subflows/subflow-email-alert.xml`
  73 
  74 **When to Use**:
  75 - Send notifications when certain conditions are met
  76 - Alert users about flow completion or errors
  77 - Standardize email formatting across flows
  78 
  79 **Input Variables**:
  80 - `varEmailAddresses` (String): Comma-separated email addresses
  81 - `varEmailSubject` (String): Email subject line
  82 - `varEmailBody` (String): Email body content
  83 
  84 **Output Variables**: None
  85 
  86 **Example**:
  87 ```xml
  88 <subflows>
  89     <name>Notify_Manager</name>
  90     <flowName>Sub_SendEmailAlert</flowName>
  91     <inputAssignments>
  92         <name>varEmailAddresses</name>
  93         <value>
  94             <elementReference>$Record.Manager.Email</elementReference>
  95         </value>
  96     </inputAssignments>
  97     <inputAssignments>
  98         <name>varEmailSubject</name>
  99         <value>
 100             <stringValue>High-Value Opportunity Created</stringValue>
 101         </value>
 102     </inputAssignments>
 103     <inputAssignments>
 104         <name>varEmailBody</name>
 105         <value>
 106             <stringValue>A new opportunity worth {!$Record.Amount} has been created.</stringValue>
 107         </value>
 108     </inputAssignments>
 109 </subflows>
 110 ```
 111 
 112 **Best Practices**:
 113 - Use formula fields or text templates to build dynamic email bodies
 114 - Consider using email templates instead for complex HTML emails
 115 - Validate email addresses before passing to subflow
 116 
 117 ---
 118 
 119 ### 3. Sub_ValidateRecord
 120 **Purpose**: Common validation patterns
 121 **File**: `assets/subflows/subflow-record-validator.xml`
 122 
 123 **When to Use**:
 124 - Validate required fields before DML operations
 125 - Check business rules before proceeding
 126 - Return validation status to parent flow
 127 
 128 **Input Variables**:
 129 - `varFieldValue` (String): Field value to validate
 130 
 131 **Output Variables**:
 132 - `varIsValid` (Boolean): `true` if validation passed, `false` otherwise
 133 - `varValidationMessage` (String): Validation result message
 134 
 135 **Example**:
 136 ```xml
 137 <subflows>
 138     <name>Validate_Industry</name>
 139     <flowName>Sub_ValidateRecord</flowName>
 140     <inputAssignments>
 141         <name>varFieldValue</name>
 142         <value>
 143             <elementReference>$Record.Industry</elementReference>
 144         </value>
 145     </inputAssignments>
 146     <storeOutputAutomatically>true</storeOutputAutomatically>
 147 </subflows>
 148 
 149 <!-- Decision based on validation result -->
 150 <decisions>
 151     <name>Check_Validation</name>
 152     <rules>
 153         <name>Valid</name>
 154         <conditions>
 155             <leftValueReference>Validate_Industry.varIsValid</leftValueReference>
 156             <operator>EqualTo</operator>
 157             <rightValue>
 158                 <booleanValue>true</booleanValue>
 159             </rightValue>
 160         </conditions>
 161         <connector>
 162             <targetReference>Proceed_With_Update</targetReference>
 163         </connector>
 164     </rules>
 165     <defaultConnector>
 166         <targetReference>Show_Error_Screen</targetReference>
 167     </defaultConnector>
 168 </decisions>
 169 ```
 170 
 171 **Extension**:
 172 Customize the validation logic in the subflow for your specific needs:
 173 - Add more complex rules (regex, format checks)
 174 - Validate multiple fields
 175 - Check against external systems
 176 
 177 ---
 178 
 179 ### 4. Sub_UpdateRelatedRecords
 180 **Purpose**: Bulk update pattern with error handling
 181 **File**: `assets/subflows/subflow-bulk-updater.xml`
 182 
 183 **When to Use**:
 184 - Update collections of related records
 185 - Maintain bulkification best practices
 186 - Centralize common update logic
 187 
 188 **Input Variables**:
 189 - `colRecordsToUpdate` (SObject Collection): Collection of records to update
 190 - `varNewValue` (String): New value to assign (customize for your field type)
 191 
 192 **Output Variables**: None
 193 
 194 **Example**:
 195 ```xml
 196 <!-- First, collect records in a loop -->
 197 <loops>
 198     <name>Loop_Through_Contacts</name>
 199     <collectionReference>Get_Related_Contacts</collectionReference>
 200     <iterationOrder>Asc</iterationOrder>
 201     <nextValueConnector>
 202         <targetReference>Add_To_Collection</targetReference>
 203     </nextValueConnector>
 204     <noMoreValuesConnector>
 205         <targetReference>Call_Bulk_Updater</targetReference>
 206     </noMoreValuesConnector>
 207 </loops>
 208 
 209 <assignments>
 210     <name>Add_To_Collection</name>
 211     <assignmentItems>
 212         <assignToReference>colContactsToUpdate</assignToReference>
 213         <operator>Add</operator>
 214         <value>
 215             <elementReference>Loop_Through_Contacts</elementReference>
 216         </value>
 217     </assignmentItems>
 218     <connector>
 219         <targetReference>Loop_Through_Contacts</targetReference>
 220     </connector>
 221 </assignments>
 222 
 223 <!-- Then, call subflow OUTSIDE the loop -->
 224 <subflows>
 225     <name>Call_Bulk_Updater</name>
 226     <flowName>Sub_UpdateRelatedRecords</flowName>
 227     <inputAssignments>
 228         <name>colRecordsToUpdate</name>
 229         <value>
 230             <elementReference>colContactsToUpdate</elementReference>
 231         </value>
 232     </inputAssignments>
 233     <inputAssignments>
 234         <name>varNewValue</name>
 235         <value>
 236             <elementReference>$Record.Industry</elementReference>
 237         </value>
 238     </inputAssignments>
 239 </subflows>
 240 ```
 241 
 242 **Key Pattern**:
 243 ✅ **Correct**: Loop → Add to Collection → (Outside Loop) → Call Subflow with Collection
 244 ❌ **Incorrect**: Loop → Call Subflow → (DML in loop!)
 245 
 246 ---
 247 
 248 ### 5. Sub_QueryRecordsWithRetry
 249 **Purpose**: Query with built-in error handling
 250 **File**: `assets/subflows/subflow-query-with-retry.xml`
 251 
 252 **When to Use**:
 253 - Query related records with fault handling
 254 - Standardize query patterns
 255 - Log query failures for troubleshooting
 256 
 257 **Input Variables**:
 258 - `varAccountId` (String): Filter criteria (customize for your query)
 259 
 260 **Output Variables**:
 261 - Automatically stores query results (use `storeOutputAutomatically="true"`)
 262 
 263 **Example**:
 264 ```xml
 265 <subflows>
 266     <name>Get_Related_Contacts</name>
 267     <flowName>Sub_QueryRecordsWithRetry</flowName>
 268     <inputAssignments>
 269         <name>varAccountId</name>
 270         <value>
 271             <elementReference>$Record.Id</elementReference>
 272         </value>
 273     </inputAssignments>
 274     <storeOutputAutomatically>true</storeOutputAutomatically>
 275 </subflows>
 276 
 277 <!-- Access query results -->
 278 <decisions>
 279     <name>Check_Results</name>
 280     <rules>
 281         <name>Contacts_Found</name>
 282         <conditions>
 283             <leftValueReference>Get_Related_Contacts</leftValueReference>
 284             <operator>IsNull</operator>
 285             <rightValue>
 286                 <booleanValue>false</booleanValue>
 287             </rightValue>
 288         </conditions>
 289         <connector>
 290             <targetReference>Process_Contacts</targetReference>
 291         </connector>
 292     </rules>
 293     <defaultConnector>
 294         <targetReference>No_Contacts_Path</targetReference>
 295     </defaultConnector>
 296 </decisions>
 297 ```
 298 
 299 **Customization**:
 300 Modify the query filters in the template for your specific object and criteria.
 301 
 302 ---
 303 
 304 ## Deployment Guide
 305 
 306 ### Step 1: Deploy Subflows to Your Org
 307 
 308 ```bash
 309 # Deploy all subflows at once
 310 sf project deploy start \
 311   --source-dir assets/subflows/ \
 312   --target-org myorg
 313 
 314 # Or deploy individually
 315 sf project deploy start \
 316   --source-dir assets/subflows/subflow-error-logger.xml \
 317   --target-org myorg
 318 ```
 319 
 320 ### Step 2: Activate Subflows
 321 
 322 1. Navigate to **Setup → Flows**
 323 2. Find each subflow (Sub_LogError, Sub_SendEmailAlert, etc.)
 324 3. Click **Activate**
 325 
 326 **⚠️ Important**: Deploy Sub_LogError first if other subflows use it for error handling.
 327 
 328 ### Step 3: Create Required Custom Objects
 329 
 330 For **Sub_LogError**, create the Flow_Error_Log__c object:
 331 
 332 ```bash
 333 # Using Salesforce CLI
 334 sf data create record \
 335   --sobject CustomObject \
 336   --values "FullName=Flow_Error_Log__c Label='Flow Error Log' PluralLabel='Flow Error Logs'"
 337 ```
 338 
 339 Or manually in Setup → Object Manager → Create → Custom Object.
 340 
 341 ---
 342 
 343 ## Usage Patterns
 344 
 345 ### Pattern 1: Orchestrated Error Handling
 346 
 347 Use Sub_LogError consistently across all flows:
 348 
 349 ```
 350 Parent Flow
 351 ├── DML Operation 1 → [Fault] → Sub_LogError
 352 ├── DML Operation 2 → [Fault] → Sub_LogError
 353 └── Subflow Call → [Fault] → Sub_LogError
 354 ```
 355 
 356 ### Pattern 2: Modular Notifications
 357 
 358 Centralize all email logic in Sub_SendEmailAlert:
 359 
 360 ```
 361 Record-Triggered Flow
 362 ├── Decision: High Value?
 363 │   ├── Yes → Sub_SendEmailAlert(Manager)
 364 │   └── No → End
 365 └── Decision: Overdue?
 366     ├── Yes → Sub_SendEmailAlert(Owner)
 367     └── No → End
 368 ```
 369 
 370 ### Pattern 3: Validation Pipeline
 371 
 372 Chain validation subflows before DML:
 373 
 374 ```
 375 Screen Flow
 376 ├── Sub_ValidateRecord(Required Fields)
 377 │   └── Invalid? → Show Error
 378 ├── Sub_ValidateRecord(Business Rules)
 379 │   └── Invalid? → Show Error
 380 └── All Valid → Create Record
 381 ```
 382 
 383 ---
 384 
 385 ## Best Practices
 386 
 387 ### ✅ DO:
 388 
 389 1. **Deploy Once, Reference Everywhere**: Activate subflows in your org, then reference them in multiple parent flows
 390 2. **Use Naming Conventions**: Start subflow names with `Sub_` for easy identification
 391 3. **Add Fault Paths**: Connect all DML operations in subflows to error handlers
 392 4. **Document Inputs/Outputs**: Use clear variable names (varFieldName, colRecordCollection)
 393 5. **Version Control**: Track subflow changes and test before updating active versions
 394 
 395 ### ❌ DON'T:
 396 
 397 1. **Don't Copy-Paste Subflows**: Reference the deployed subflow instead of duplicating logic
 398 2. **Don't Skip Error Handling**: All subflows should handle their own errors gracefully
 399 3. **Don't Hardcode Values**: Use input variables for flexibility
 400 4. **Don't Create DML in Loops**: Use Sub_UpdateRelatedRecords pattern for bulk operations
 401 5. **Don't Forget Testing**: Test subflows independently before using in parent flows
 402 
 403 ---
 404 
 405 ## Testing Your Subflows
 406 
 407 ### Unit Testing Individual Subflows
 408 
 409 1. Create a test flow that calls the subflow
 410 2. Pass various input combinations (valid, invalid, null)
 411 3. Verify output variables and behavior
 412 4. Check error logs if using Sub_LogError
 413 
 414 ```bash
 415 # Example: Test Sub_LogError
 416 sf data query \
 417   --query "SELECT Flow_Name__c, Error_Message__c FROM Flow_Error_Log__c ORDER BY CreatedDate DESC LIMIT 5" \
 418   --target-org myorg
 419 ```
 420 
 421 ### Integration Testing in Parent Flows
 422 
 423 1. Use subflows in record-triggered flows
 424 2. Test with bulk data (200+ records)
 425 3. Verify subflow doesn't cause governor limit errors
 426 4. Check execution time in debug logs
 427 
 428 ---
 429 
 430 ## Customization Guide
 431 
 432 ### Extending Subflows
 433 
 434 All subflows are templates—customize for your needs:
 435 
 436 1. **Clone the subflow**: Create a copy (e.g., `Sub_LogError_WithEmail`)
 437 2. **Add custom logic**: Extend functionality while keeping core pattern
 438 3. **Maintain naming convention**: Keep `Sub_` prefix for discoverability
 439 
 440 ### Example: Enhanced Error Logger
 441 
 442 Extend Sub_LogError to send Platform Events:
 443 
 444 ```xml
 445 <!-- Add to subflow after Create_Error_Log -->
 446 <recordCreates>
 447     <name>Publish_Error_Event</name>
 448     <object>Flow_Error__e</object>
 449     <inputAssignments>
 450         <field>Flow_Name__c</field>
 451         <value>
 452             <elementReference>varFlowName</elementReference>
 453         </value>
 454     </inputAssignments>
 455     <!-- Real-time error monitoring -->
 456 </recordCreates>
 457 ```
 458 
 459 ---
 460 
 461 ## Performance Considerations
 462 
 463 ### Governor Limits
 464 
 465 - **Subflow Depth**: Maximum 50 levels of nested subflows (avoid deep nesting)
 466 - **DML Statements**: Each subflow DML counts toward 150 limit
 467 - **SOQL Queries**: Each subflow query counts toward 100 limit
 468 
 469 ### Optimization Tips
 470 
 471 1. **Batch Operations**: Use Sub_UpdateRelatedRecords for bulk updates
 472 2. **Minimize Subflow Calls**: Call once with collections vs. multiple times with single records
 473 3. **Cache Results**: Store subflow outputs in variables to avoid repeated calls
 474 
 475 ---
 476 
 477 ## Troubleshooting
 478 
 479 ### "Subflow not found" Error
 480 - ✅ Verify subflow is activated in target org
 481 - ✅ Check API name matches exactly (`Sub_LogError`, not `Sub_Log_Error`)
 482 - ✅ Deploy subflow before deploying parent flow
 483 
 484 ### "Input variable not found" Error
 485 - ✅ Verify variable names match subflow definition
 486 - ✅ Check variable data types (String vs. SObject Collection)
 487 - ✅ Ensure required inputs are provided
 488 
 489 ### Performance Issues
 490 - ✅ Check debug logs for subflow execution time
 491 - ✅ Avoid calling subflows inside loops
 492 - ✅ Use bulk operations with collections
 493 
 494 ---
 495 
 496 ## Version History
 497 
 498 | Version | Date | Changes |
 499 |---------|------|---------|
 500 | 1.0 | 2024-11-30 | Initial library: 5 subflows (LogError, EmailAlert, Validator, BulkUpdater, QueryWithRetry) |
 501 
 502 ---
 503 
 504 ## Related Documentation
 505 
 506 - [Error Logging Example](../references/error-logging-example.md) - Detailed Sub_LogError usage
 507 - [Orchestration Guide](orchestration-guide.md) - Parent-child flow patterns
 508 - [Flow Best Practices](flow-best-practices.md) - Flow guidelines and security
 509 
 510 ---
 511 
 512 ## Support
 513 
 514 For issues or questions:
 515 1. Check subflow XML for correct variable names and types
 516 2. Test subflow independently before using in parent flow
 517 3. Review error logs in Flow_Error_Log__c (if using Sub_LogError)
 518 4. Check debug logs for detailed execution information
 519 
 520 **Happy flow building! 🚀**
