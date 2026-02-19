<!-- Parent: sf-flow/SKILL.md -->
   1 # Salesforce Flow XML Metadata Gotchas
   2 
   3 Critical XML metadata constraints and known issues when deploying flows via Metadata API.
   4 
   5 ## storeOutputAutomatically Data Leak Risk (v2.0.0)
   6 
   7 **⚠️ SECURITY WARNING**: When `storeOutputAutomatically="true"` in recordLookups, **ALL fields** are retrieved and stored.
   8 
   9 ### Risks
  10 
  11 1. **Data Leak**: Sensitive fields (SSN, salary, etc.) may be exposed unintentionally
  12 2. **Performance**: Large objects with many fields impact query performance
  13 3. **Screen Flow Exposure**: In screen flows, external users could access all data
  14 
  15 ### Recommended Pattern
  16 
  17 **Always specify only the fields you need:**
  18 
  19 ```xml
  20 <recordLookups>
  21     <name>Get_Account</name>
  22     <!-- Specify exact fields needed -->
  23     <queriedFields>Id</queriedFields>
  24     <queriedFields>Name</queriedFields>
  25     <queriedFields>Industry</queriedFields>
  26     <!-- Store in explicit variable -->
  27     <outputReference>rec_Account</outputReference>
  28 </recordLookups>
  29 ```
  30 
  31 **Avoid:**
  32 ```xml
  33 <recordLookups>
  34     <name>Get_Account</name>
  35     <!-- Retrieves ALL fields - security risk! -->
  36     <storeOutputAutomatically>true</storeOutputAutomatically>
  37 </recordLookups>
  38 ```
  39 
  40 ---
  41 
  42 ## Relationship Fields Not Supported in recordLookups (CRITICAL)
  43 
  44 **⚠️ DEPLOYMENT BLOCKER**: Flow's Get Records (recordLookups) CANNOT query parent relationship fields.
  45 
  46 ### What Doesn't Work
  47 
  48 ```xml
  49 <!-- ❌ THIS WILL FAIL DEPLOYMENT -->
  50 <recordLookups>
  51     <name>Get_User</name>
  52     <object>User</object>
  53     <queriedFields>Id</queriedFields>
  54     <queriedFields>Name</queriedFields>
  55     <queriedFields>Manager.Name</queriedFields>  <!-- FAILS! -->
  56 </recordLookups>
  57 ```
  58 
  59 **Error**: `field integrity exception: unknown (The field "Manager.Name" for the object "User" doesn't exist.)`
  60 
  61 ### Why It Fails
  62 
  63 - Flow's recordLookups only supports direct fields on the queried object
  64 - Parent relationship traversal (dot notation like `Parent.Field`) is NOT supported
  65 - This is different from SOQL in Apex which supports relationship queries
  66 
  67 ### Fields That WON'T Work
  68 
  69 | Object | Invalid Field | Error |
  70 |--------|---------------|-------|
  71 | User | `Manager.Name` | Manager.Name doesn't exist |
  72 | Contact | `Account.Name` | Account.Name doesn't exist |
  73 | Case | `Account.Owner.Email` | Account.Owner.Email doesn't exist |
  74 | Opportunity | `Account.Industry` | Account.Industry doesn't exist |
  75 
  76 ### Correct Solution: Two-Step Query
  77 
  78 ```xml
  79 <!-- Step 1: Get the child record with lookup ID -->
  80 <recordLookups>
  81     <name>Get_User</name>
  82     <object>User</object>
  83     <queriedFields>Id</queriedFields>
  84     <queriedFields>Name</queriedFields>
  85     <queriedFields>ManagerId</queriedFields>  <!-- ✅ Get the ID only -->
  86     <outputReference>rec_User</outputReference>
  87 </recordLookups>
  88 
  89 <!-- Step 2: Query parent record using the lookup ID -->
  90 <recordLookups>
  91     <name>Get_Manager</name>
  92     <object>User</object>
  93     <filters>
  94         <field>Id</field>
  95         <operator>EqualTo</operator>
  96         <value>
  97             <elementReference>rec_User.ManagerId</elementReference>
  98         </value>
  99     </filters>
 100     <queriedFields>Id</queriedFields>
 101     <queriedFields>Name</queriedFields>
 102     <outputReference>rec_Manager</outputReference>
 103 </recordLookups>
 104 ```
 105 
 106 ### Flow Routing
 107 
 108 Ensure your flow checks for null before using the parent record:
 109 ```xml
 110 <decisions>
 111     <name>Check_Manager_Exists</name>
 112     <rules>
 113         <conditions>
 114             <leftValueReference>rec_Manager</leftValueReference>
 115             <operator>IsNull</operator>
 116             <rightValue><booleanValue>false</booleanValue></rightValue>
 117         </conditions>
 118     </rules>
 119 </decisions>
 120 ```
 121 
 122 ---
 123 
 124 ## $Record vs $Record__c Confusion (Record-Triggered Flows)
 125 
 126 **⚠️ COMMON MISTAKE**: Confusing Flow's `$Record` with Process Builder's `$Record__c`.
 127 
 128 ### What's the Difference?
 129 
 130 | Variable | Context | Usage |
 131 |----------|---------|-------|
 132 | `$Record` | Flow (Record-Triggered) | Single record that triggered the flow |
 133 | `$Record__c` | Process Builder | Collection of records in trigger batch |
 134 
 135 ### The Mistake
 136 
 137 Trying to create a loop over `$Record__c` in a Flow:
 138 
 139 ```xml
 140 <!-- ❌ THIS DOES NOT EXIST IN FLOWS -->
 141 <loops>
 142     <collectionReference>$Record__c</collectionReference>  <!-- INVALID! -->
 143 </loops>
 144 ```
 145 
 146 ### Why This Happens
 147 
 148 - Process Builder used `$Record__c` to represent the batch of triggering records
 149 - Developers migrating from Process Builder assume Flows work the same way
 150 - In Flows, `$Record` is always a **single record**, not a collection
 151 - The platform handles bulk batching automatically
 152 
 153 ### Correct Approach in Record-Triggered Flows
 154 
 155 **Use `$Record` directly without loops:**
 156 
 157 ```xml
 158 <!-- ✅ CORRECT: Direct access to triggered record -->
 159 <decisions>
 160     <conditions>
 161         <leftValueReference>$Record.StageName</leftValueReference>
 162         <operator>EqualTo</operator>
 163         <rightValue><stringValue>Closed Won</stringValue></rightValue>
 164     </conditions>
 165 </decisions>
 166 
 167 <!-- ✅ Build task using $Record fields -->
 168 <assignments>
 169     <assignmentItems>
 170         <assignToReference>rec_Task.WhatId</assignToReference>
 171         <value><elementReference>$Record.Id</elementReference></value>
 172     </assignmentItems>
 173 </assignments>
 174 ```
 175 
 176 ### When You DO Need Loops
 177 
 178 Only when processing **related records**, not the triggered record:
 179 
 180 ```xml
 181 <!-- ✅ CORRECT: Loop over RELATED records -->
 182 <recordLookups>
 183     <filters>
 184         <field>AccountId</field>
 185         <value><elementReference>$Record.AccountId</elementReference></value>
 186     </filters>
 187     <outputReference>col_RelatedContacts</outputReference>
 188 </recordLookups>
 189 
 190 <loops>
 191     <collectionReference>col_RelatedContacts</collectionReference>  <!-- ✅ Valid -->
 192 </loops>
 193 ```
 194 
 195 ---
 196 
 197 ## recordLookups Conflicts
 198 
 199 **NEVER use both** `<storeOutputAutomatically>` AND `<outputReference>` together.
 200 
 201 **Choose ONE approach:**
 202 ```xml
 203 <!-- Option 1: Auto-store (creates variable automatically) - NOT RECOMMENDED -->
 204 <storeOutputAutomatically>true</storeOutputAutomatically>
 205 
 206 <!-- Option 2: Explicit variable - RECOMMENDED -->
 207 <outputReference>rec_AccountRecord</outputReference>
 208 ```
 209 
 210 ## Element Ordering in recordLookups
 211 
 212 Elements must follow this order:
 213 1. `<name>` 2. `<label>` 3. `<locationX>` 4. `<locationY>` 5. `<assignNullValuesIfNoRecordsFound>` 6. `<connector>` 7. `<filterLogic>` 8. `<filters>` 9. `<getFirstRecordOnly>` 10. `<object>` 11. `<outputReference>` OR `<storeOutputAutomatically>` 12. `<queriedFields>`
 214 
 215 ## Transform Element
 216 
 217 **Recommendation**: Create Transform elements in Flow Builder UI, then deploy - do NOT hand-write.
 218 
 219 Issues with hand-written Transform:
 220 - Complex nested XML structure with strict ordering
 221 - `inputReference` placement varies by context
 222 - Multiple conflicting rules in Metadata API
 223 
 224 ## Subflow Calling Limitation (Metadata API Constraint)
 225 
 226 **Record-triggered flows (`processType="AutoLaunchedFlow"`) CANNOT call subflows via XML deployment.**
 227 
 228 **Root Cause**: Salesforce Metadata API does not support the "flow" action type for AutoLaunchedFlow process types.
 229 
 230 **Valid action types for AutoLaunchedFlow**: apex, chatterPost, emailAlert, emailSimple, and platform-specific actions - but NOT "flow".
 231 
 232 **Error message**: "You can't use the Flows action type in flows with the Autolaunched Flow process type"
 233 
 234 **Screen Flows (`processType="Flow"`) CAN call subflows** successfully via XML deployment.
 235 
 236 **UI vs XML**: Flow Builder UI may use different internal mechanisms - UI capabilities may differ from direct XML deployment.
 237 
 238 ### Recommended Solution for Record-Triggered Flows
 239 
 240 Use **inline orchestration** instead of subflows:
 241 
 242 1. Organize logic into clear sections with descriptive element naming
 243 2. Pattern: `Decision_CheckCriteria` → `Assignment_SetFields` → `Create_Record`
 244 3. Add XML comments to delineate sections: `<!-- Section 1: Contact Creation -->`
 245 
 246 **Benefits**: Single atomic flow, no deployment dependencies, full execution control.
 247 
 248 **Reference**: [Salesforce Help Article 000396957](https://help.salesforce.com/s/articleView?id=000396957&type=1)
 249 
 250 ## Fault Connectors Cannot Self-Reference (CRITICAL)
 251 
 252 **⚠️ DEPLOYMENT BLOCKER**: An element CANNOT have a fault connector pointing to itself.
 253 
 254 ### What Doesn't Work
 255 
 256 ```xml
 257 <!-- ❌ THIS WILL FAIL DEPLOYMENT -->
 258 <recordUpdates>
 259     <name>Update_Account</name>
 260     <label>Update Account</label>
 261     <connector>
 262         <targetReference>Next_Element</targetReference>
 263     </connector>
 264     <faultConnector>
 265         <targetReference>Update_Account</targetReference>  <!-- FAILS! Self-reference -->
 266     </faultConnector>
 267     <!-- ... -->
 268 </recordUpdates>
 269 ```
 270 
 271 **Error**: `The element "Update_Account" cannot be connected to itself.`
 272 
 273 ### Why This Matters
 274 
 275 - Self-referencing fault connectors would create infinite loops on failure
 276 - Salesforce validates this during deployment and blocks it
 277 - This applies to ALL connector types (faultConnector, connector, nextValueConnector, etc.)
 278 
 279 ### Correct Fault Handling Patterns
 280 
 281 **Option 1: Route to dedicated error handler:**
 282 ```xml
 283 <recordUpdates>
 284     <name>Update_Account</name>
 285     <faultConnector>
 286         <targetReference>Handle_Update_Error</targetReference>  <!-- ✅ Different element -->
 287     </faultConnector>
 288 </recordUpdates>
 289 
 290 <assignments>
 291     <name>Handle_Update_Error</name>
 292     <!-- Log error, set flag, etc. -->
 293 </assignments>
 294 ```
 295 
 296 **Option 2: Route to error logging assignment:**
 297 ```xml
 298 <recordUpdates>
 299     <name>Update_Account</name>
 300     <faultConnector>
 301         <targetReference>Log_Error_And_Continue</targetReference>  <!-- ✅ -->
 302     </faultConnector>
 303 </recordUpdates>
 304 ```
 305 
 306 **Option 3: Omit fault connector (flow will terminate on error):**
 307 ```xml
 308 <recordUpdates>
 309     <name>Update_Account</name>
 310     <connector>
 311         <targetReference>Next_Element</targetReference>
 312     </connector>
 313     <!-- No faultConnector - flow terminates on failure -->
 314 </recordUpdates>
 315 ```
 316 
 317 ### Best Practice
 318 
 319 - Always route fault connectors to a dedicated error handling element
 320 - Use an assignment to capture `{!$Flow.FaultMessage}` before logging
 321 - Consider whether the flow should continue or terminate on failure
 322 
 323 ---
 324 
 325 ## Root-Level Element Ordering (CRITICAL)
 326 
 327 Salesforce Metadata API requires **strict alphabetical ordering** at root level.
 328 
 329 ### Complete Element Type List (Alphabetical Order)
 330 
 331 All elements of the same type MUST be grouped together. You CANNOT have elements of one type scattered across the file.
 332 
 333 ```
 334 1.  <apiVersion>
 335 2.  <assignments>         ← ALL assignments together
 336 3.  <constants>
 337 4.  <decisions>           ← ALL decisions together
 338 5.  <description>
 339 6.  <environments>
 340 7.  <formulas>
 341 8.  <interviewLabel>
 342 9.  <label>
 343 10. <loops>               ← ALL loops together
 344 11. <processMetadataValues>
 345 12. <processType>
 346 13. <recordCreates>       ← ALL recordCreates together
 347 14. <recordDeletes>       ← ALL recordDeletes together
 348 15. <recordLookups>       ← ALL recordLookups together
 349 16. <recordUpdates>       ← ALL recordUpdates together
 350 17. <runInMode>
 351 18. <screens>             ← ALL screens together
 352 19. <start>
 353 20. <status>
 354 21. <subflows>            ← ALL subflows together
 355 22. <textTemplates>
 356 23. <variables>           ← ALL variables together
 357 24. <waits>
 358 ```
 359 
 360 ### The Grouping Rule (CRITICAL)
 361 
 362 **Wrong** - Assignment after loops section:
 363 ```xml
 364 <assignments>
 365     <name>Set_Initial_Values</name>
 366     <!-- ... -->
 367 </assignments>
 368 <loops>
 369     <name>Loop_Contacts</name>
 370     <!-- ... -->
 371 </loops>
 372 <assignments>  <!-- ❌ FAILS: Can't have assignments after loops! -->
 373     <name>Increment_Counter</name>
 374     <!-- ... -->
 375 </assignments>
 376 ```
 377 
 378 **Error**: `Element assignments is duplicated at this location in type Flow`
 379 
 380 **Correct** - All assignments together:
 381 ```xml
 382 <assignments>  <!-- ✅ All assignments grouped -->
 383     <name>Increment_Counter</name>
 384     <!-- ... -->
 385 </assignments>
 386 <assignments>
 387     <name>Set_Initial_Values</name>
 388     <!-- ... -->
 389 </assignments>
 390 <loops>
 391     <name>Loop_Contacts</name>
 392     <!-- ... -->
 393 </loops>
 394 ```
 395 
 396 ### Why This Happens
 397 
 398 When generating flows programmatically or manually editing XML:
 399 - Easy to add a new element near related logic
 400 - Salesforce requires ALL elements of same type to appear consecutively
 401 - The "duplicate" error is misleading - it means elements aren't grouped
 402 
 403 **Note**: API 60.0+ does NOT use `<bulkSupport>` - bulk processing is automatic.
 404 
 405 ## Common Deployment Errors
 406 
 407 | Error | Cause | Solution |
 408 |-------|-------|----------|
 409 | "Element X is duplicated" | Elements not alphabetically ordered | Reorder elements |
 410 | "Element bulkSupport invalid" | Using deprecated element (API 60.0+) | Remove `<bulkSupport>` |
 411 | "Error parsing file" | Malformed XML | Validate XML syntax |
 412 | "field 'X.Y' doesn't exist" | Relationship field in queriedFields | Use two-step query pattern |
 413 | "$Record__Prior can only be used..." | Using $Record__Prior with Create trigger | Change to Update or CreateAndUpdate |
 414 | "You can't use the Flows action type..." | Subflow in AutoLaunchedFlow | Use inline logic instead |
 415 | "nothing is connected to the Start element" | Empty flow with no elements | Add at least one assignment connected to start |
 416 
 417 ---
 418 
 419 ## Start Element Must Have Connector (For Agentforce Flow Actions)
 420 
 421 **⚠️ DEPLOYMENT BLOCKER**: Flows used as Agent Script actions MUST have at least one element connected to the Start element.
 422 
 423 ### What Doesn't Work
 424 
 425 ```xml
 426 <!-- ❌ THIS WILL FAIL DEPLOYMENT -->
 427 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 428     <apiVersion>65.0</apiVersion>
 429     <label>My Agent Flow</label>
 430     <processType>AutoLaunchedFlow</processType>
 431     <status>Active</status>
 432 
 433     <variables>
 434         <name>inp_SearchQuery</name>
 435         <dataType>String</dataType>
 436         <isInput>true</isInput>
 437         <isOutput>false</isOutput>
 438     </variables>
 439 
 440     <start>
 441         <locationX>50</locationX>
 442         <locationY>50</locationY>
 443         <!-- No connector! -->
 444     </start>
 445 </Flow>
 446 ```
 447 
 448 **Error**: `field integrity exception: unknown (The flow can't run because nothing is connected to the Start element.)`
 449 
 450 ### Why This Happens
 451 
 452 - Minimal flows with only inputs/outputs and no logic still need at least one element
 453 - Salesforce validates that the flow has something to execute
 454 - This is especially common when creating stub/mock flows for testing
 455 
 456 ### Correct Pattern: Add Assignment Element
 457 
 458 Even for simple pass-through flows, add at least one assignment:
 459 
 460 ```xml
 461 <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
 462     <apiVersion>65.0</apiVersion>
 463     <label>My Agent Flow</label>
 464     <processType>AutoLaunchedFlow</processType>
 465     <status>Active</status>
 466 
 467     <variables>
 468         <name>inp_SearchQuery</name>
 469         <dataType>String</dataType>
 470         <isInput>true</isInput>
 471         <isOutput>false</isOutput>
 472     </variables>
 473     <variables>
 474         <name>out_Result</name>
 475         <dataType>String</dataType>
 476         <isInput>false</isInput>
 477         <isOutput>true</isOutput>
 478     </variables>
 479 
 480     <!-- ✅ Start connected to assignment -->
 481     <start>
 482         <locationX>50</locationX>
 483         <locationY>50</locationY>
 484         <connector>
 485             <targetReference>Set_Result</targetReference>
 486         </connector>
 487     </start>
 488 
 489     <!-- ✅ At least one element required -->
 490     <assignments>
 491         <name>Set_Result</name>
 492         <label>Set Result</label>
 493         <locationX>176</locationX>
 494         <locationY>158</locationY>
 495         <assignmentItems>
 496             <assignToReference>out_Result</assignToReference>
 497             <operator>Assign</operator>
 498             <value>
 499                 <stringValue>Success</stringValue>
 500             </value>
 501         </assignmentItems>
 502     </assignments>
 503 </Flow>
 504 ```
 505 
 506 ### When Creating Agentforce Flow Actions
 507 
 508 1. **Define inputs** matching Agent Script action `inputs:`
 509 2. **Define outputs** matching Agent Script action `outputs:`
 510 3. **Add at least one assignment** to set output values
 511 4. **Connect start to assignment** via `<connector>`
 512 5. **Set status to Active** for agent to invoke
 513 
 514 ---
 515 
 516 ## Summary: Lessons Learned
 517 
 518 ### Fault Connector Self-Reference
 519 - **Problem**: Fault connector pointing to the same element
 520 - **Error**: "The element cannot be connected to itself"
 521 - **Solution**: Route fault connectors to a dedicated error handler element
 522 
 523 ### XML Element Grouping
 524 - **Problem**: Elements of same type scattered across the file
 525 - **Error**: "Element X is duplicated at this location"
 526 - **Solution**: Group ALL elements of same type together, in alphabetical order by type
 527 
 528 ### Relationship Fields
 529 - **Problem**: Querying `Parent.Field` in Get Records
 530 - **Solution**: Two separate queries - child first, then parent by ID
 531 
 532 ### Record-Triggered Flow Architecture
 533 - **Problem**: Creating loops over triggered records
 534 - **Solution**: Use `$Record` directly - platform handles batching
 535 
 536 ### Deployment
 537 - **Problem**: Using direct CLI commands
 538 - **Solution**: Always use sf-deploy skill
 539 
 540 ### $Record Context
 541 - **Problem**: Confusing Flow's `$Record` with Process Builder's `$Record__c`
 542 - **Solution**: `$Record` is single record, use without loops
 543 
 544 ### Standard Objects for Testing
 545 - **Problem**: Custom objects may not exist in target org
 546 - **Solution**: When testing flow generation/deployment, prefer standard objects (Account, Contact, Opportunity, Task) for guaranteed deployability
