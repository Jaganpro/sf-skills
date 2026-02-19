<!-- Parent: sf-flow/SKILL.md -->
   1 # Record-Triggered Flow Example: Opportunity Stage Update
   2 
   3 This example demonstrates creating a Record-Triggered Flow with proper bulkification that updates related contacts when an Opportunity reaches "Closed Won".
   4 
   5 ## Scenario
   6 
   7 When an Opportunity is marked as "Closed Won":
   8 - Find all related Contacts
   9 - Update their Status__c field to "Customer"
  10 - Send notification to account owner
  11 - **Handle bulk updates** (200+ opportunities at once)
  12 
  13 ## User Request
  14 
  15 ```
  16 User: "Create a record-triggered flow on Opportunity.
  17 When the Stage changes to 'Closed Won', update all related contacts
  18 to have Status__c = 'Customer'."
  19 ```
  20 
  21 ## Skill Workflow
  22 
  23 ### Phase 1: Requirements Gathering
  24 
  25 The skill asks:
  26 
  27 **Q1: What type of flow?**
  28 → Record-Triggered Flow (After-Save)
  29 
  30 **Q2: What is the purpose?**
  31 → "Update related contacts when opportunity reaches Closed Won"
  32 
  33 **Q3: Which object triggers this flow?**
  34 → "Opportunity"
  35 
  36 **Q4: When should it run?**
  37 → After records are created OR updated
  38 
  39 **Q5: Target org?**
  40 → "production" (careful - always test in sandbox first!)
  41 
  42 ### Phase 2: Flow Design
  43 
  44 The skill designs a **bulkified** flow:
  45 - **Trigger**: Opportunity, After Save, Create and Update
  46 - **bulkSupport**: true (CRITICAL for bulk processing)
  47 - **Decision**: Check if Stage = 'Closed Won'
  48 - **Get Records**: Related Contacts (collection)
  49 - **Update Records**: Contact collection (single DML, outside any loops)
  50 - **Fault Path**: Error handling for DML failure
  51 
  52 ### Phase 3: Validation
  53 
  54 ```
  55 Flow Validation Report: Opportunity_Closed_Won_Update_Contacts (API 65.0)
  56 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  57 
  58 ✓ XML Structure: Valid
  59 ✓ API Version: 65.0 (current - Winter '26)
  60 ✓ Required Elements: Present
  61 ✓ Element References: All valid
  62 ✓ Naming Conventions: Compliant
  63 ✓ Bulkification: <bulkSupport>true</bulkSupport> present
  64 ✓ Bulkification: No DML in loops
  65 
  66 ⚠ Warnings: None
  67 ✗ Errors: None
  68 
  69 Best Practices Score: 100/100 (Excellent ✨)
  70 
  71 Recommendations:
  72   1. ✓ Bulkified design - handles collections properly
  73   2. ✓ Fault path configured for error handling
  74   3. ✓ No governor limit issues expected
  75 
  76 ✓ VALIDATION PASSED - Flow ready for deployment
  77 ```
  78 
  79 ### Phase 4: Deployment
  80 
  81 **Important**: Even though user said "production", skill deploys to sandbox FIRST for testing.
  82 
  83 ```
  84 ⚠️  IMPORTANT: You specified 'production' but testing in sandbox is
  85 strongly recommended for record-triggered flows.
  86 
  87 Deploying to sandbox-test first...
  88 
  89 Step 1: Validation (Check-Only)
  90 ✓ Metadata structure valid
  91 ✓ Opportunity object accessible
  92 ✓ Contact object accessible
  93 ✓ Status__c field exists on Contact
  94 ✓ No deployment conflicts
  95 
  96 Step 2: Actual Deployment
  97 ✓ Deployed to sandbox-test
  98 ✓ Flow status: Draft
  99 ✓ Ready for bulk testing
 100 ```
 101 
 102 ### Phase 5: Testing Checklist (CRITICAL for Record-Triggered)
 103 
 104 ```
 105 ✓ Testing Checklist: Opportunity_Closed_Won_Update_Contacts
 106 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 107 
 108 SINGLE RECORD TESTING:
 109 □ Create test Opportunity with Stage = 'Prospecting'
 110 □ Add 2-3 related Contacts
 111 □ Update Opportunity Stage to 'Closed Won'
 112 □ Check Debug Logs - verify flow executed
 113 □ Verify Contacts updated to Status__c = 'Customer'
 114 □ Check no errors in Debug Logs
 115 
 116 BULK TESTING (CRITICAL):
 117 □ Prepare 200+ test Opportunities with related Contacts
 118 □ Use Data Loader to bulk update Stage to 'Closed Won'
 119 □ Monitor Debug Logs during bulk update
 120 □ Verify NO governor limit errors
 121 □ Confirm all Contacts updated correctly
 122 □ Check execution time stays within limits
 123 
 124 ERROR TESTING:
 125 □ Test with Opportunity that has no related Contacts
 126 □ Test with invalid Contact field values
 127 □ Verify fault path triggers on errors
 128 □ Check error messages are helpful
 129 
 130 Debug Logs Query:
 131 sf data query --query "SELECT Id, Status, NumElements FROM FlowInterview
 132 WHERE FlowDefinitionName='Opportunity_Closed_Won_Update_Contacts'
 133 AND CreatedDate=TODAY ORDER BY CreatedDate DESC LIMIT 50"
 134 --target-org sandbox-test
 135 ```
 136 
 137 ## Generated Flow Structure (Key Parts)
 138 
 139 ### Start Element with Bulkification
 140 
 141 ```xml
 142 <start>
 143     <locationX>50</locationX>
 144     <locationY>50</locationY>
 145     <object>Opportunity</object>
 146     <recordTriggerType>CreateAndUpdate</recordTriggerType>
 147     <triggerType>RecordAfterSave</triggerType>
 148     <bulkSupport>true</bulkSupport>  <!-- CRITICAL for bulk processing -->
 149     <connector>
 150         <targetReference>Decision_Check_Stage</targetReference>
 151     </connector>
 152 </start>
 153 ```
 154 
 155 ### Decision: Check if Closed Won
 156 
 157 ```xml
 158 <decisions>
 159     <name>Decision_Check_Stage</name>
 160     <label>Check if Closed Won</label>
 161     <rules>
 162         <name>Is_Closed_Won</name>
 163         <conditionLogic>and</conditionLogic>
 164         <conditions>
 165             <leftValueReference>$Record.StageName</leftValueReference>
 166             <operator>EqualTo</operator>
 167             <rightValue>
 168                 <stringValue>Closed Won</stringValue>
 169             </rightValue>
 170         </conditions>
 171         <connector>
 172             <targetReference>Get_Related_Contacts</targetReference>
 173         </connector>
 174         <label>Is Closed Won</label>
 175     </rules>
 176 </decisions>
 177 ```
 178 
 179 ### Get Records: Related Contacts (Collection)
 180 
 181 ```xml
 182 <recordLookups>
 183     <name>Get_Related_Contacts</name>
 184     <label>Get Related Contacts</label>
 185     <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
 186     <connector>
 187         <targetReference>Update_Contact_Status</targetReference>
 188     </connector>
 189     <filterLogic>and</filterLogic>
 190     <filters>
 191         <field>AccountId</field>
 192         <operator>EqualTo</operator>
 193         <value>
 194             <elementReference>$Record.AccountId</elementReference>
 195         </value>
 196     </filters>
 197     <object>Contact</object>
 198     <outputReference>colContacts</outputReference>  <!-- Collection variable -->
 199     <queriedFields>Id</queriedFields>
 200     <queriedFields>Status__c</queriedFields>
 201 </recordLookups>
 202 ```
 203 
 204 ### Update Records: Bulk Update (NOT in a loop!)
 205 
 206 ```xml
 207 <recordUpdates>
 208     <name>Update_Contact_Status</name>
 209     <label>Update Contact Status</label>
 210     <faultConnector>
 211         <targetReference>Handle_Error</targetReference>  <!-- Fault path -->
 212     </faultConnector>
 213     <inputAssignments>
 214         <field>Status__c</field>
 215         <value>
 216             <stringValue>Customer</stringValue>
 217         </value>
 218     </inputAssignments>
 219     <inputReference>colContacts</inputReference>  <!-- Updates entire collection -->
 220 </recordUpdates>
 221 ```
 222 
 223 ## Testing Results
 224 
 225 ### Single Record Test
 226 ✓ Flow triggered correctly
 227 ✓ Stage change detected
 228 ✓ Related contacts retrieved (3 contacts)
 229 ✓ All 3 contacts updated to Status__c = 'Customer'
 230 ✓ Execution time: 142ms
 231 ✓ No errors
 232 
 233 ### Bulk Test (200 Opportunities, ~800 Contacts)
 234 ✓ Data Loader bulk update completed
 235 ✓ Flow executed for all 200 opportunities
 236 ✓ All ~800 contacts updated correctly
 237 ✓ **NO governor limit errors**
 238 ✓ Average execution time: 287ms per opportunity
 239 ✓ Total DML statements: Within limits (150 max)
 240 ✓ SOQL queries: Within limits (100 max)
 241 
 242 **Why it worked:**
 243 - `<bulkSupport>true</bulkSupport>` enabled collection processing
 244 - DML operation on collection (not individual records in a loop)
 245 - Single SOQL query per opportunity
 246 - Fault paths handled errors gracefully
 247 
 248 ## Common Mistakes (Avoided by This Flow)
 249 
 250 ### ❌ WRONG: DML in Loop
 251 ```xml
 252 <!-- THIS WOULD FAIL WITH BULK DATA -->
 253 <loops>
 254     <name>Loop_Contacts</name>
 255     <collectionReference>colContacts</collectionReference>
 256     <nextValueConnector>
 257         <targetReference>Update_Single_Contact</targetReference>  <!-- DML HERE -->
 258     </nextValueConnector>
 259 </loops>
 260 
 261 <recordUpdates>
 262     <name>Update_Single_Contact</name>
 263     <!-- This executes INSIDE the loop - CRITICAL ERROR -->
 264     <!-- Hits governor limit with 200+ records -->
 265 </recordUpdates>
 266 ```
 267 
 268 **Why it fails:**
 269 - DML inside loop = one DML per record
 270 - Governor limit: 150 DML statements per transaction
 271 - 200 contacts = 200 DML statements = FAILURE
 272 
 273 ### ✓ CORRECT: Bulk DML
 274 ```xml
 275 <!-- Our flow does this correctly -->
 276 <recordLookups>
 277     <name>Get_Related_Contacts</name>
 278     <outputReference>colContacts</outputReference>  <!-- Get collection -->
 279 </recordLookups>
 280 
 281 <recordUpdates>
 282     <name>Update_Contact_Status</name>
 283     <inputReference>colContacts</inputReference>  <!-- Update entire collection -->
 284     <!-- Single DML operation, regardless of collection size -->
 285 </recordUpdates>
 286 ```
 287 
 288 **Why it works:**
 289 - One DML operation for entire collection
 290 - Handles 200, 2000, or 20,000 records equally well
 291 - Stays within governor limits
 292 
 293 ## Production Deployment
 294 
 295 After successful bulk testing in sandbox:
 296 
 297 1. **Deploy to production:**
 298    ```
 299    "Deploy Opportunity_Closed_Won_Update_Contacts to production"
 300    ```
 301 
 302 2. **Activate carefully:**
 303    - Skill prompts: "Keep as Draft or Activate Now?"
 304    - Select: "Keep as Draft"
 305    - Manually activate after final verification
 306 
 307 3. **Monitor in production:**
 308    - Check Debug Logs daily for first week
 309    - Review flow interviews for errors
 310    - Monitor performance metrics
 311 
 312 4. **Set up monitoring:**
 313    ```
 314    sf data query --query "SELECT Id, Status, NumElements
 315    FROM FlowInterview
 316    WHERE FlowDefinitionName='Opportunity_Closed_Won_Update_Contacts'
 317    AND Status='Error'
 318    AND CreatedDate=LAST_N_DAYS:1"
 319    --target-org production
 320    ```
 321 
 322 ## Performance Metrics
 323 
 324 **Single Execution:**
 325 - SOQL Queries: 1 (Get Contacts)
 326 - DML Statements: 1 (Update Contacts)
 327 - Execution Time: ~150ms
 328 
 329 **Bulk Execution (200 Opportunities):**
 330 - SOQL Queries: 200 (1 per opportunity)
 331 - DML Statements: 200 (1 per opportunity)
 332 - Total Time: ~58 seconds
 333 - **NO governor limit errors**
 334 
 335 ## Key Takeaways
 336 
 337 ✓ **ALWAYS set <bulkSupport>true</bulkSupport>** for record-triggered flows
 338 ✓ **NEVER put DML inside loops** - causes bulk failures
 339 ✓ **Use collections** - get all records, update all at once
 340 ✓ **Add fault paths** - handle errors gracefully
 341 ✓ **Test with bulk data** - 200+ records minimum
 342 ✓ **Monitor in production** - check Debug Logs regularly
 343 
 344 This is production-grade, bulkified Flow design!
