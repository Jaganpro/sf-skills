<!-- Parent: sf-flow/SKILL.md -->
   1 # Transform vs Loop: A Decision Guide
   2 
   3 When processing collections in Salesforce Flow, choosing between **Transform** and **Loop** elements can significantly impact both performance and maintainability. This guide provides clear decision criteria and best practices.
   4 
   5 ---
   6 
   7 ## Quick Decision Matrix
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────────┐
  11 │ TRANSFORM vs LOOP DECISION MATRIX                                       │
  12 ├───────────────────────────────┬─────────────────────────────────────────┤
  13 │ USE TRANSFORM                 │ USE LOOP                                │
  14 ├───────────────────────────────┼─────────────────────────────────────────┤
  15 │ Mapping one collection to     │ IF/ELSE logic per record                │
  16 │   another                     │ Different records need different paths  │
  17 │ Bulk field assignments        │ Counters, flags, multi-step calcs       │
  18 │ Simple formula calculations   │ Business rules vary per record          │
  19 │ Preparing records for DML     │ Need to track state across iterations   │
  20 │ Fewer elements, cleaner flows │ Complex conditional transformations     │
  21 └───────────────────────────────┴─────────────────────────────────────────┘
  22 ```
  23 
  24 **Simple Rule to Remember:**
  25 - **Shaping data** → Use **Transform** (30-50% faster)
  26 - **Making decisions per record** → Use **Loop**
  27 
  28 ---
  29 
  30 ## When Transform is the Right Choice
  31 
  32 Transform is ideal when you need to:
  33 
  34 ### 1. Map One Collection to Another
  35 Converting a collection of one record type to another (e.g., Contacts → Opportunity Contact Roles).
  36 
  37 ```
  38 ✅ GOOD: Get Contacts → Transform → Create Opportunity Contact Roles
  39 ❌ BAD:  Get Contacts → Loop → Assignment → Create Records (per iteration)
  40 ```
  41 
  42 ### 2. Bulk Field Assignments
  43 Assigning the same field values across all records in a collection.
  44 
  45 ```
  46 Example: Set Status = "Processed" for all records
  47 Transform handles this in a single server-side operation.
  48 ```
  49 
  50 ### 3. Simple Calculations Using Formulas
  51 Transform supports formulas for generating dynamic values during mapping.
  52 
  53 ```
  54 Example: Calculate FullName from FirstName + ' ' + LastName
  55 ```
  56 
  57 ### 4. Prepare Records for Create/Update Operations
  58 Building a collection of records to insert or update.
  59 
  60 ```
  61 Example: Map Account fields to new Case records before bulk insert
  62 ```
  63 
  64 ### 5. Reduce Flow Elements
  65 Transform consolidates what would be Loop + Assignment into a single element, making flows cleaner and easier to maintain.
  66 
  67 ---
  68 
  69 ## When You Still Need a Loop
  70 
  71 Loop is required when:
  72 
  73 ### 1. IF/ELSE Logic Per Record
  74 Different records need different processing paths.
  75 
  76 ```
  77 Example:
  78 - If Amount > 10000 → High priority
  79 - If Amount > 5000 → Medium priority
  80 - Else → Low priority
  81 ```
  82 
  83 ### 2. Counters, Flags, or Multi-Step Calculations
  84 You need to maintain state across iterations.
  85 
  86 ```
  87 Example: Count how many records meet certain criteria
  88          Track running totals
  89          Build comma-separated lists
  90 ```
  91 
  92 ### 3. Business Rules Vary Per Record
  93 Each record may follow a different logic path based on its values.
  94 
  95 ```
  96 Example: Route leads to different queues based on State + Industry
  97 ```
  98 
  99 ### 4. Complex Conditional Transformations
 100 When the transformation logic itself is conditional and complex.
 101 
 102 ```
 103 Example: If record has parent → use parent's values
 104          If orphan → use defaults
 105          If flagged → skip entirely
 106 ```
 107 
 108 ---
 109 
 110 ## Performance Comparison
 111 
 112 | Metric | Transform | Loop + Assignment |
 113 |--------|-----------|-------------------|
 114 | **Processing Model** | Server-side bulk | Client-side iteration |
 115 | **Speed** | 30-50% faster | Baseline |
 116 | **CPU Time** | Lower | Higher |
 117 | **DML Statements** | No change | No change |
 118 | **Flow Elements** | 1 element | 2+ elements |
 119 | **Maintainability** | Simpler | More complex |
 120 
 121 ### Why Transform is Faster
 122 
 123 Transform processes the entire collection as a single server-side operation, while Loop iterates through each record individually. For large collections (100+ records), this difference becomes significant.
 124 
 125 ---
 126 
 127 ## Visual Comparison: Before and After
 128 
 129 ### BAD Pattern: Loop for Simple Mapping
 130 
 131 ```
 132 ┌─────────────────────────────────────────────────────────────────────────┐
 133 │ ❌ ANTI-PATTERN: Using Loop for Simple Field Mapping                   │
 134 └─────────────────────────────────────────────────────────────────────────┘
 135 
 136     ┌──────────────────┐
 137     │ Get Records      │  Query Contacts
 138     │ (All Contacts)   │
 139     └────────┬─────────┘
 140              │
 141              ▼
 142     ┌──────────────────┐
 143     │ Loop             │  Iterate through each Contact
 144     │ (Contact Loop)   │◄──────────────────────────────┐
 145     └────────┬─────────┘                               │
 146              │ For Each                                │
 147              ▼                                         │
 148     ┌──────────────────┐                               │
 149     │ Assignment       │  Map Contact fields to        │
 150     │ (Map Fields)     │  OpportunityContactRole       │
 151     └────────┬─────────┘                               │
 152              │                                         │
 153              ▼                                         │
 154     ┌──────────────────┐                               │
 155     │ Add to Collection│  Build output collection      │
 156     └────────┬─────────┘                               │
 157              │ After Last ─────────────────────────────┘
 158              ▼
 159     ┌──────────────────┐
 160     │ Create Records   │  Insert all OCRs
 161     └──────────────────┘
 162 
 163     Problem: 4 elements, client-side iteration, slower
 164 ```
 165 
 166 ### GOOD Pattern: Transform for Simple Mapping
 167 
 168 ```
 169 ┌─────────────────────────────────────────────────────────────────────────┐
 170 │ ✅ BEST PRACTICE: Using Transform for Field Mapping                    │
 171 └─────────────────────────────────────────────────────────────────────────┘
 172 
 173     ┌──────────────────┐
 174     │ Get Records      │  Query Contacts
 175     │ (All Contacts)   │
 176     └────────┬─────────┘
 177              │
 178              ▼
 179     ┌──────────────────┐
 180     │ Transform        │  Map Contact → OpportunityContactRole
 181     │ (Map to OCR)     │  (Server-side bulk operation)
 182     └────────┬─────────┘
 183              │
 184              ▼
 185     ┌──────────────────┐
 186     │ Create Records   │  Insert all OCRs
 187     └──────────────────┘
 188 
 189     Benefits: 3 elements, server-side processing, 30-50% faster
 190 ```
 191 
 192 ---
 193 
 194 ## Transform XML Structure Reference
 195 
 196 > **Important:** Create Transform elements in Flow Builder UI, then deploy. The XML structure is complex and error-prone to hand-write.
 197 
 198 ### Basic Structure
 199 
 200 ```xml
 201 <transforms>
 202     <name>Transform_Contacts_To_OCR</name>
 203     <label>Transform Contacts to Opportunity Contact Roles</label>
 204     <locationX>0</locationX>
 205     <locationY>0</locationY>
 206     <connector>
 207         <targetReference>Create_OCR_Records</targetReference>
 208     </connector>
 209     <!-- Input: collection of source records -->
 210     <inputVariable>col_Contacts</inputVariable>
 211     <!-- Output: collection of target records -->
 212     <outputVariable>col_OpportunityContactRoles</outputVariable>
 213     <!-- Field mappings with optional formulas -->
 214     <transformValueActions>
 215         <transformValueActionType>Map</transformValueActionType>
 216         <inputReference>col_Contacts.ContactId</inputReference>
 217         <outputReference>col_OpportunityContactRoles.ContactId</outputReference>
 218     </transformValueActions>
 219     <transformValueActions>
 220         <transformValueActionType>Map</transformValueActionType>
 221         <inputReference>var_OpportunityId</inputReference>
 222         <outputReference>col_OpportunityContactRoles.OpportunityId</outputReference>
 223     </transformValueActions>
 224     <transformValueActions>
 225         <transformValueActionType>Formula</transformValueActionType>
 226         <formula>"Primary"</formula>
 227         <outputReference>col_OpportunityContactRoles.Role</outputReference>
 228     </transformValueActions>
 229 </transforms>
 230 ```
 231 
 232 ### Key Elements
 233 
 234 | Element | Purpose |
 235 |---------|---------|
 236 | `inputVariable` | Source collection to transform |
 237 | `outputVariable` | Target collection (output) |
 238 | `transformValueActions` | Individual field mappings |
 239 | `transformValueActionType` | `Map` (direct copy) or `Formula` (calculated) |
 240 | `inputReference` | Source field path |
 241 | `outputReference` | Target field path |
 242 | `formula` | Formula expression (when type is Formula) |
 243 
 244 ---
 245 
 246 ## Testing Transform Elements
 247 
 248 ### 1. Flow Builder Debug Mode
 249 
 250 ```
 251 Step-by-Step:
 252 1. Open your flow in Flow Builder
 253 2. Click the "Debug" button in the toolbar
 254 3. Configure debug inputs:
 255    - Provide a sample collection (or create test records)
 256    - Set any required input variables
 257 4. Run the debug
 258 5. Inspect the Transform element output:
 259    - Verify field mappings are correct
 260    - Check formula calculations
 261    - Confirm collection size matches input
 262 ```
 263 
 264 ### 2. Apex Test Class Approach
 265 
 266 ```apex
 267 @isTest
 268 private class TransformFlowTest {
 269 
 270     @isTest
 271     static void testTransformMapsFieldsCorrectly() {
 272         // Setup: Create source records
 273         List<Contact> contacts = new List<Contact>();
 274         for (Integer i = 0; i < 200; i++) {
 275             contacts.add(new Contact(
 276                 FirstName = 'Test' + i,
 277                 LastName = 'Contact' + i,
 278                 Email = 'test' + i + '@example.com'
 279             ));
 280         }
 281         insert contacts;
 282 
 283         // Create parent Opportunity
 284         Opportunity opp = new Opportunity(
 285             Name = 'Test Opp',
 286             StageName = 'Prospecting',
 287             CloseDate = Date.today().addDays(30)
 288         );
 289         insert opp;
 290 
 291         // Execute: Run the Transform flow
 292         Test.startTest();
 293         Map<String, Object> inputs = new Map<String, Object>{
 294             'inp_Contacts' => contacts,
 295             'inp_OpportunityId' => opp.Id
 296         };
 297         Flow.Interview.Transform_Contact_To_OCR flow =
 298             new Flow.Interview.Transform_Contact_To_OCR(inputs);
 299         flow.start();
 300         Test.stopTest();
 301 
 302         // Verify: Check transformed records were created
 303         List<OpportunityContactRole> ocrs = [
 304             SELECT Id, ContactId, OpportunityId, Role
 305             FROM OpportunityContactRole
 306             WHERE OpportunityId = :opp.Id
 307         ];
 308 
 309         System.assertEquals(200, ocrs.size(), 'All contacts should be mapped');
 310         for (OpportunityContactRole ocr : ocrs) {
 311             System.assertNotEquals(null, ocr.ContactId, 'ContactId should be mapped');
 312             System.assertEquals(opp.Id, ocr.OpportunityId, 'OpportunityId should be set');
 313         }
 314     }
 315 
 316     @isTest
 317     static void testTransformPerformance() {
 318         // Setup: Create 250 records (exceeds batch boundary)
 319         List<Contact> contacts = new List<Contact>();
 320         for (Integer i = 0; i < 250; i++) {
 321             contacts.add(new Contact(
 322                 FirstName = 'Perf' + i,
 323                 LastName = 'Test' + i
 324             ));
 325         }
 326         insert contacts;
 327 
 328         Opportunity opp = new Opportunity(
 329             Name = 'Perf Test',
 330             StageName = 'Prospecting',
 331             CloseDate = Date.today().addDays(30)
 332         );
 333         insert opp;
 334 
 335         // Execute and measure
 336         Test.startTest();
 337         Integer cpuBefore = Limits.getCpuTime();
 338 
 339         Map<String, Object> inputs = new Map<String, Object>{
 340             'inp_Contacts' => contacts,
 341             'inp_OpportunityId' => opp.Id
 342         };
 343         Flow.Interview.Transform_Contact_To_OCR flow =
 344             new Flow.Interview.Transform_Contact_To_OCR(inputs);
 345         flow.start();
 346 
 347         Integer cpuAfter = Limits.getCpuTime();
 348         Test.stopTest();
 349 
 350         // Assert: Transform should be efficient
 351         Integer cpuUsed = cpuAfter - cpuBefore;
 352         System.assert(cpuUsed < 5000,
 353             'Transform should use minimal CPU. Used: ' + cpuUsed + 'ms');
 354     }
 355 }
 356 ```
 357 
 358 ### 3. CLI Performance Comparison
 359 
 360 ```bash
 361 # Enable debug logging
 362 sf apex log tail --color
 363 
 364 # Run Transform flow via anonymous Apex
 365 sf apex run -f scripts/run-transform-flow.apex
 366 
 367 # Run equivalent Loop flow for comparison
 368 sf apex run -f scripts/run-loop-flow.apex
 369 
 370 # Compare CPU_TIME in debug logs
 371 # Transform should show ~30-50% lower CPU_TIME
 372 ```
 373 
 374 ### Sample Anonymous Apex (`scripts/run-transform-flow.apex`)
 375 
 376 ```apex
 377 // Query source records
 378 List<Contact> contacts = [SELECT Id, FirstName, LastName, Email FROM Contact LIMIT 200];
 379 
 380 // Get target Opportunity
 381 Opportunity opp = [SELECT Id FROM Opportunity LIMIT 1];
 382 
 383 // Run Transform flow
 384 Map<String, Object> inputs = new Map<String, Object>{
 385     'inp_Contacts' => contacts,
 386     'inp_OpportunityId' => opp.Id
 387 };
 388 
 389 Flow.Interview flow = Flow.Interview.createInterview('Transform_Contact_To_OCR', inputs);
 390 flow.start();
 391 
 392 System.debug('Transform completed. CPU Time: ' + Limits.getCpuTime() + 'ms');
 393 ```
 394 
 395 ---
 396 
 397 ## Migration Checklist: Loop to Transform
 398 
 399 If you have existing flows using Loop for simple field mapping, consider migrating:
 400 
 401 - [ ] Identify Loop elements that only do field assignment (no decisions)
 402 - [ ] Verify no counters, flags, or state tracking is needed
 403 - [ ] Create equivalent Transform element in Flow Builder UI
 404 - [ ] Test with same data set
 405 - [ ] Compare debug output for correctness
 406 - [ ] Compare CPU time for performance gain
 407 - [ ] Replace Loop + Assignment with single Transform
 408 - [ ] Validate and deploy
 409 
 410 ---
 411 
 412 ## Common Mistakes to Avoid
 413 
 414 ### 1. Using Transform for Conditional Logic
 415 
 416 ```
 417 ❌ WRONG: Trying to add IF/ELSE inside Transform
 418    Transform doesn't support per-record branching.
 419 
 420 ✅ RIGHT: Use Loop + Decision for conditional processing.
 421 ```
 422 
 423 ### 2. Ignoring the UI Recommendation
 424 
 425 ```
 426 ❌ WRONG: Hand-writing Transform XML
 427    The XML structure is complex with strict ordering requirements.
 428 
 429 ✅ RIGHT: Always create Transform in Flow Builder, then deploy.
 430 ```
 431 
 432 ### 3. Over-Optimizing Simple Flows
 433 
 434 ```
 435 ❌ WRONG: Converting every Loop to Transform
 436    Some flows process very small collections where optimization doesn't matter.
 437 
 438 ✅ RIGHT: Focus on loops processing 50+ records regularly.
 439 ```
 440 
 441 ---
 442 
 443 ## Related Documentation
 444 
 445 - [Loop Pattern Template](../assets/elements/loop-pattern.xml) - When Loop is the right choice
 446 - [Transform Pattern Template](../assets/elements/transform-pattern.xml) - Reference XML structure
 447 - [Flow Best Practices](./flow-best-practices.md) - General optimization guidelines
 448 - [Governance Checklist](./governance-checklist.md) - Pre-deployment validation
 449 
 450 ---
 451 
 452 ## Attribution
 453 
 454 This guide was inspired by content shared by:
 455 - **Jalumchi Akpoke** - Transform vs Loop decision pattern visualization
 456 - **Shubham Bhardwaj** - Original YouTube video on Transform efficiency
 457 
 458 See [CREDITS.md](../CREDITS.md) for full attribution.
