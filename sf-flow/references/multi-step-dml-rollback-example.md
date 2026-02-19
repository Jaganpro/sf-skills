<!-- Parent: sf-flow/SKILL.md -->
   1 # Multi-Step DML Rollback Pattern Example
   2 
   3 > **Version**: 2.0.0
   4 > **Use Case**: Creating related records with rollback on failure
   5 > **Scenario**: Account → Contact → Opportunity creation with automatic cleanup
   6 
   7 ---
   8 
   9 ## Overview
  10 
  11 When a flow performs multiple DML operations (Create, Update, Delete), a failure in a later step can leave orphaned records from earlier successful operations. This example demonstrates the **rollback pattern** to maintain data integrity.
  12 
  13 ### Business Scenario
  14 
  15 A screen flow that:
  16 1. Creates an **Account** record
  17 2. Creates a **Primary Contact** for that Account
  18 3. Creates an initial **Opportunity** for the Account
  19 
  20 If step 3 fails, we must delete the Contact (step 2) and Account (step 1) to prevent orphaned data.
  21 
  22 ---
  23 
  24 ## Flow Architecture
  25 
  26 ```
  27 ┌─────────────────┐
  28 │  Screen_Input   │
  29 └────────┬────────┘
  30          │
  31          ▼
  32 ┌─────────────────┐     ┌─────────────────────┐
  33 │ Create_Account  │────▶│ Handle_Account_Error │
  34 └────────┬────────┘     └─────────────────────┘
  35          │ Success
  36          ▼
  37 ┌─────────────────┐     ┌─────────────────────────────┐
  38 │ Create_Contact  │────▶│ Rollback_Account_On_Error   │
  39 └────────┬────────┘     └─────────────────────────────┘
  40          │ Success
  41          ▼
  42 ┌─────────────────────┐     ┌─────────────────────────────────┐
  43 │ Create_Opportunity  │────▶│ Rollback_Contact_And_Account    │
  44 └────────┬────────────┘     └─────────────────────────────────┘
  45          │ Success
  46          ▼
  47 ┌─────────────────┐
  48 │ Screen_Success  │
  49 └─────────────────┘
  50 ```
  51 
  52 ---
  53 
  54 ## Variable Definitions (v2.0.0 Naming)
  55 
  56 ```xml
  57 <!-- Input Variables -->
  58 <variables>
  59     <name>inp_AccountName</name>
  60     <dataType>String</dataType>
  61     <isInput>true</isInput>
  62     <isOutput>false</isOutput>
  63 </variables>
  64 
  65 <variables>
  66     <name>inp_ContactFirstName</name>
  67     <dataType>String</dataType>
  68     <isInput>true</isInput>
  69     <isOutput>false</isOutput>
  70 </variables>
  71 
  72 <variables>
  73     <name>inp_ContactLastName</name>
  74     <dataType>String</dataType>
  75     <isInput>true</isInput>
  76     <isOutput>false</isOutput>
  77 </variables>
  78 
  79 <!-- Record ID Variables (for rollback) -->
  80 <variables>
  81     <name>var_CreatedAccountId</name>
  82     <dataType>String</dataType>
  83     <isInput>false</isInput>
  84     <isOutput>false</isOutput>
  85 </variables>
  86 
  87 <variables>
  88     <name>var_CreatedContactId</name>
  89     <dataType>String</dataType>
  90     <isInput>false</isInput>
  91     <isOutput>false</isOutput>
  92 </variables>
  93 
  94 <!-- Error Tracking -->
  95 <variables>
  96     <name>var_ErrorMessage</name>
  97     <dataType>String</dataType>
  98     <isInput>false</isInput>
  99     <isOutput>false</isOutput>
 100 </variables>
 101 
 102 <variables>
 103     <name>var_ErrorStep</name>
 104     <dataType>String</dataType>
 105     <isInput>false</isInput>
 106     <isOutput>false</isOutput>
 107 </variables>
 108 
 109 <!-- Output Variables -->
 110 <variables>
 111     <name>out_Success</name>
 112     <dataType>Boolean</dataType>
 113     <isInput>false</isInput>
 114     <isOutput>true</isOutput>
 115     <value>
 116         <booleanValue>false</booleanValue>
 117     </value>
 118 </variables>
 119 
 120 <variables>
 121     <name>out_ErrorDetails</name>
 122     <dataType>String</dataType>
 123     <isInput>false</isInput>
 124     <isOutput>true</isOutput>
 125 </variables>
 126 ```
 127 
 128 ---
 129 
 130 ## Step 1: Create Account
 131 
 132 ```xml
 133 <!-- Create Account Record -->
 134 <recordCreates>
 135     <name>Create_Account</name>
 136     <label>Create Account</label>
 137     <locationX>0</locationX>
 138     <locationY>0</locationY>
 139     <connector>
 140         <targetReference>Store_Account_Id</targetReference>
 141     </connector>
 142     <faultConnector>
 143         <targetReference>Handle_Account_Error</targetReference>
 144     </faultConnector>
 145     <inputAssignments>
 146         <field>Name</field>
 147         <value>
 148             <elementReference>inp_AccountName</elementReference>
 149         </value>
 150     </inputAssignments>
 151     <object>Account</object>
 152     <storeOutputAutomatically>true</storeOutputAutomatically>
 153 </recordCreates>
 154 
 155 <!-- Store Account ID for potential rollback -->
 156 <assignments>
 157     <name>Store_Account_Id</name>
 158     <label>Store Account Id</label>
 159     <locationX>0</locationX>
 160     <locationY>0</locationY>
 161     <assignmentItems>
 162         <assignToReference>var_CreatedAccountId</assignToReference>
 163         <operator>Assign</operator>
 164         <value>
 165             <elementReference>Create_Account</elementReference>
 166         </value>
 167     </assignmentItems>
 168     <connector>
 169         <targetReference>Create_Contact</targetReference>
 170     </connector>
 171 </assignments>
 172 
 173 <!-- Handle Account Creation Error -->
 174 <assignments>
 175     <name>Handle_Account_Error</name>
 176     <label>Handle Account Error</label>
 177     <locationX>0</locationX>
 178     <locationY>0</locationY>
 179     <assignmentItems>
 180         <assignToReference>var_ErrorMessage</assignToReference>
 181         <operator>Assign</operator>
 182         <value>
 183             <elementReference>$Flow.FaultMessage</elementReference>
 184         </value>
 185     </assignmentItems>
 186     <assignmentItems>
 187         <assignToReference>var_ErrorStep</assignToReference>
 188         <operator>Assign</operator>
 189         <value>
 190             <stringValue>Account Creation</stringValue>
 191         </value>
 192     </assignmentItems>
 193     <connector>
 194         <targetReference>Set_Error_Output</targetReference>
 195     </connector>
 196 </assignments>
 197 ```
 198 
 199 ---
 200 
 201 ## Step 2: Create Contact (with Rollback on Failure)
 202 
 203 ```xml
 204 <!-- Create Contact Record -->
 205 <recordCreates>
 206     <name>Create_Contact</name>
 207     <label>Create Contact</label>
 208     <locationX>0</locationX>
 209     <locationY>0</locationY>
 210     <connector>
 211         <targetReference>Store_Contact_Id</targetReference>
 212     </connector>
 213     <faultConnector>
 214         <targetReference>Capture_Contact_Error</targetReference>
 215     </faultConnector>
 216     <inputAssignments>
 217         <field>FirstName</field>
 218         <value>
 219             <elementReference>inp_ContactFirstName</elementReference>
 220         </value>
 221     </inputAssignments>
 222     <inputAssignments>
 223         <field>LastName</field>
 224         <value>
 225             <elementReference>inp_ContactLastName</elementReference>
 226         </value>
 227     </inputAssignments>
 228     <inputAssignments>
 229         <field>AccountId</field>
 230         <value>
 231             <elementReference>var_CreatedAccountId</elementReference>
 232         </value>
 233     </inputAssignments>
 234     <object>Contact</object>
 235     <storeOutputAutomatically>true</storeOutputAutomatically>
 236 </recordCreates>
 237 
 238 <!-- Store Contact ID for potential rollback -->
 239 <assignments>
 240     <name>Store_Contact_Id</name>
 241     <label>Store Contact Id</label>
 242     <locationX>0</locationX>
 243     <locationY>0</locationY>
 244     <assignmentItems>
 245         <assignToReference>var_CreatedContactId</assignToReference>
 246         <operator>Assign</operator>
 247         <value>
 248             <elementReference>Create_Contact</elementReference>
 249         </value>
 250     </assignmentItems>
 251     <connector>
 252         <targetReference>Create_Opportunity</targetReference>
 253     </connector>
 254 </assignments>
 255 
 256 <!-- Capture error message before rollback -->
 257 <assignments>
 258     <name>Capture_Contact_Error</name>
 259     <label>Capture Contact Error</label>
 260     <locationX>0</locationX>
 261     <locationY>0</locationY>
 262     <assignmentItems>
 263         <assignToReference>var_ErrorMessage</assignToReference>
 264         <operator>Assign</operator>
 265         <value>
 266             <elementReference>$Flow.FaultMessage</elementReference>
 267         </value>
 268     </assignmentItems>
 269     <assignmentItems>
 270         <assignToReference>var_ErrorStep</assignToReference>
 271         <operator>Assign</operator>
 272         <value>
 273             <stringValue>Contact Creation</stringValue>
 274         </value>
 275     </assignmentItems>
 276     <connector>
 277         <targetReference>Rollback_Account</targetReference>
 278     </connector>
 279 </assignments>
 280 
 281 <!-- ROLLBACK: Delete the Account we created -->
 282 <recordDeletes>
 283     <name>Rollback_Account</name>
 284     <label>Rollback Account</label>
 285     <locationX>0</locationX>
 286     <locationY>0</locationY>
 287     <connector>
 288         <targetReference>Set_Error_Output</targetReference>
 289     </connector>
 290     <faultConnector>
 291         <!-- If rollback fails, still proceed to error output -->
 292         <targetReference>Set_Error_Output</targetReference>
 293     </faultConnector>
 294     <filterLogic>and</filterLogic>
 295     <filters>
 296         <field>Id</field>
 297         <operator>EqualTo</operator>
 298         <value>
 299             <elementReference>var_CreatedAccountId</elementReference>
 300         </value>
 301     </filters>
 302     <object>Account</object>
 303 </recordDeletes>
 304 ```
 305 
 306 ---
 307 
 308 ## Step 3: Create Opportunity (with Full Rollback Chain)
 309 
 310 ```xml
 311 <!-- Create Opportunity Record -->
 312 <recordCreates>
 313     <name>Create_Opportunity</name>
 314     <label>Create Opportunity</label>
 315     <locationX>0</locationX>
 316     <locationY>0</locationY>
 317     <connector>
 318         <targetReference>Set_Success_Output</targetReference>
 319     </connector>
 320     <faultConnector>
 321         <targetReference>Capture_Opportunity_Error</targetReference>
 322     </faultConnector>
 323     <inputAssignments>
 324         <field>Name</field>
 325         <value>
 326             <stringValue>Initial Opportunity</stringValue>
 327         </value>
 328     </inputAssignments>
 329     <inputAssignments>
 330         <field>AccountId</field>
 331         <value>
 332             <elementReference>var_CreatedAccountId</elementReference>
 333         </value>
 334     </inputAssignments>
 335     <inputAssignments>
 336         <field>StageName</field>
 337         <value>
 338             <stringValue>Prospecting</stringValue>
 339         </value>
 340     </inputAssignments>
 341     <inputAssignments>
 342         <field>CloseDate</field>
 343         <value>
 344             <elementReference>$Flow.CurrentDate</elementReference>
 345         </value>
 346     </inputAssignments>
 347     <object>Opportunity</object>
 348     <storeOutputAutomatically>true</storeOutputAutomatically>
 349 </recordCreates>
 350 
 351 <!-- Capture error before starting rollback chain -->
 352 <assignments>
 353     <name>Capture_Opportunity_Error</name>
 354     <label>Capture Opportunity Error</label>
 355     <locationX>0</locationX>
 356     <locationY>0</locationY>
 357     <assignmentItems>
 358         <assignToReference>var_ErrorMessage</assignToReference>
 359         <operator>Assign</operator>
 360         <value>
 361             <elementReference>$Flow.FaultMessage</elementReference>
 362         </value>
 363     </assignmentItems>
 364     <assignmentItems>
 365         <assignToReference>var_ErrorStep</assignToReference>
 366         <operator>Assign</operator>
 367         <value>
 368             <stringValue>Opportunity Creation</stringValue>
 369         </value>
 370     </assignmentItems>
 371     <connector>
 372         <targetReference>Rollback_Contact</targetReference>
 373     </connector>
 374 </assignments>
 375 
 376 <!-- ROLLBACK CHAIN: Delete Contact first -->
 377 <recordDeletes>
 378     <name>Rollback_Contact</name>
 379     <label>Rollback Contact</label>
 380     <locationX>0</locationX>
 381     <locationY>0</locationY>
 382     <connector>
 383         <targetReference>Rollback_Account_After_Contact</targetReference>
 384     </connector>
 385     <faultConnector>
 386         <!-- Continue chain even if Contact delete fails -->
 387         <targetReference>Rollback_Account_After_Contact</targetReference>
 388     </faultConnector>
 389     <filterLogic>and</filterLogic>
 390     <filters>
 391         <field>Id</field>
 392         <operator>EqualTo</operator>
 393         <value>
 394             <elementReference>var_CreatedContactId</elementReference>
 395         </value>
 396     </filters>
 397     <object>Contact</object>
 398 </recordDeletes>
 399 
 400 <!-- ROLLBACK CHAIN: Then delete Account -->
 401 <recordDeletes>
 402     <name>Rollback_Account_After_Contact</name>
 403     <label>Rollback Account After Contact</label>
 404     <locationX>0</locationX>
 405     <locationY>0</locationY>
 406     <connector>
 407         <targetReference>Set_Error_Output</targetReference>
 408     </connector>
 409     <faultConnector>
 410         <targetReference>Set_Error_Output</targetReference>
 411     </faultConnector>
 412     <filterLogic>and</filterLogic>
 413     <filters>
 414         <field>Id</field>
 415         <operator>EqualTo</operator>
 416         <value>
 417             <elementReference>var_CreatedAccountId</elementReference>
 418         </value>
 419     </filters>
 420     <object>Account</object>
 421 </recordDeletes>
 422 ```
 423 
 424 ---
 425 
 426 ## Output Assignments
 427 
 428 ```xml
 429 <!-- Success Output -->
 430 <assignments>
 431     <name>Set_Success_Output</name>
 432     <label>Set Success Output</label>
 433     <locationX>0</locationX>
 434     <locationY>0</locationY>
 435     <assignmentItems>
 436         <assignToReference>out_Success</assignToReference>
 437         <operator>Assign</operator>
 438         <value>
 439             <booleanValue>true</booleanValue>
 440         </value>
 441     </assignmentItems>
 442     <connector>
 443         <targetReference>Screen_Success</targetReference>
 444     </connector>
 445 </assignments>
 446 
 447 <!-- Error Output with Context -->
 448 <assignments>
 449     <name>Set_Error_Output</name>
 450     <label>Set Error Output</label>
 451     <locationX>0</locationX>
 452     <locationY>0</locationY>
 453     <assignmentItems>
 454         <assignToReference>out_Success</assignToReference>
 455         <operator>Assign</operator>
 456         <value>
 457             <booleanValue>false</booleanValue>
 458         </value>
 459     </assignmentItems>
 460     <assignmentItems>
 461         <assignToReference>out_ErrorDetails</assignToReference>
 462         <operator>Assign</operator>
 463         <value>
 464             <!-- Concatenate step and error for context -->
 465             <stringValue>Failed at {!var_ErrorStep}: {!var_ErrorMessage}</stringValue>
 466         </value>
 467     </assignmentItems>
 468     <connector>
 469         <targetReference>Screen_Error</targetReference>
 470     </connector>
 471 </assignments>
 472 ```
 473 
 474 ---
 475 
 476 ## Key Patterns Demonstrated
 477 
 478 ### 1. Store IDs Immediately After Creation
 479 Always capture the Id of created records in a variable so you can delete them if needed later.
 480 
 481 ### 2. Rollback in Reverse Order
 482 Delete dependent records first (Contact), then parent records (Account). This respects referential integrity.
 483 
 484 ### 3. Continue Rollback Chain on Failure
 485 Even if a rollback delete fails, continue to the next delete. Use fault connectors that continue the chain.
 486 
 487 ### 4. Capture Error Context
 488 Store both the error message (`$Flow.FaultMessage`) and which step failed (`var_ErrorStep`) for debugging.
 489 
 490 ### 5. Use Output Variables
 491 Expose `out_Success` and `out_ErrorDetails` so calling flows/processes can handle the result.
 492 
 493 ---
 494 
 495 ## Alternative: Using the Rollback Subflow
 496 
 497 For reusable rollback logic, use the `Sub_RollbackRecords` subflow:
 498 
 499 ```xml
 500 <!-- Build collection of IDs to delete -->
 501 <assignments>
 502     <name>Build_Rollback_Collection</name>
 503     <label>Build Rollback Collection</label>
 504     <locationX>0</locationX>
 505     <locationY>0</locationY>
 506     <assignmentItems>
 507         <assignToReference>col_RecordsToRollback</assignToReference>
 508         <operator>Add</operator>
 509         <value>
 510             <elementReference>var_CreatedContactId</elementReference>
 511         </value>
 512     </assignmentItems>
 513     <assignmentItems>
 514         <assignToReference>col_RecordsToRollback</assignToReference>
 515         <operator>Add</operator>
 516         <value>
 517             <elementReference>var_CreatedAccountId</elementReference>
 518         </value>
 519     </assignmentItems>
 520 </assignments>
 521 ```
 522 
 523 Then call `Sub_RollbackRecords` with the collection. See `assets/subflows/subflow-dml-rollback.xml`.
 524 
 525 ---
 526 
 527 ## Testing Checklist
 528 
 529 - [ ] Successful creation of all 3 records
 530 - [ ] Account failure → no orphaned records
 531 - [ ] Contact failure → Account deleted, no Contact
 532 - [ ] Opportunity failure → Both Contact and Account deleted
 533 - [ ] Error messages include step context
 534 - [ ] Works with bulk operations (200+ records)
 535 
 536 ---
 537 
 538 ## Related Resources
 539 
 540 - [Flow Best Practices](../references/flow-best-practices.md) - Three-tier error handling
 541 - [Rollback Subflow Template](../assets/subflows/subflow-dml-rollback.xml) - Reusable rollback
 542 - [Testing Guide](../references/testing-guide.md) - Comprehensive testing strategies
