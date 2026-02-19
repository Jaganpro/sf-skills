<!-- Parent: sf-flow/SKILL.md -->
   1 # Flow Quick Reference
   2 
   3 A comprehensive cheat sheet for Salesforce Flow development. Use this guide for quick decisions on flow types, elements, and variables.
   4 
   5 ---
   6 
   7 ## Flow Type Selection Decision Tree
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────────┐
  11 │ WHICH FLOW TYPE SHOULD I USE?                                           │
  12 └─────────────────────────────────────────────────────────────────────────┘
  13 
  14 Need to gather user input?
  15 ├─ YES ──────────────────────────────────────────► SCREEN FLOW
  16 │                                                   └─ Foreground execution
  17 │                                                   └─ Users see and interact
  18 │
  19 └─ NO ─► Need multi-step, multi-user workflow?
  20          ├─ YES ─────────────────────────────────► FLOW ORCHESTRATION
  21          │                                          └─ Multi-stage approvals
  22          │                                          └─ Sequential user tasks
  23          │
  24          └─ NO ─► Record created, updated, or deleted?
  25                   ├─ YES ────────────────────────► RECORD-TRIGGERED FLOW
  26                   │    │
  27                   │    ├─ Modify same record? ──► Before-Save Trigger
  28                   │    │    └─ No DML required
  29                   │    │    └─ Field updates, validation
  30                   │    │
  31                   │    └─ Modify related records? ► After-Save Trigger
  32                   │         └─ DML on other objects
  33                   │         └─ Callouts, emails
  34                   │
  35                   └─ NO ─► Run on a schedule?
  36                            ├─ YES ──────────────► SCHEDULE-TRIGGERED FLOW
  37                            │                       └─ Runs once/daily/weekly
  38                            │                       └─ Batch processing
  39                            │
  40                            └─ NO ─► Platform Event received?
  41                                     ├─ YES ─────► PLATFORM EVENT-TRIGGERED
  42                                     │              └─ Event-driven automation
  43                                     │              └─ Async processing
  44                                     │
  45                                     └─ NO ──────► AUTOLAUNCHED FLOW
  46                                                    └─ Called from Apex/REST
  47                                                    └─ Called from other flows
  48                                                    └─ Agent actions
  49 ```
  50 
  51 ---
  52 
  53 ## Flow Type Quick Reference
  54 
  55 | Flow Type | Trigger | Use Case | Execution |
  56 |-----------|---------|----------|-----------|
  57 | **Screen Flow** | User clicks button/link | Forms, wizards, guided processes | Foreground |
  58 | **Record-Triggered (Before)** | Record DML (before commit) | Same-record validation, field defaults | Background |
  59 | **Record-Triggered (After)** | Record DML (after commit) | Related records, callouts, emails | Background |
  60 | **Schedule-Triggered** | Time-based (cron) | Batch updates, cleanup, notifications | Background |
  61 | **Platform Event-Triggered** | Platform Event published | Event-driven processing, async work | Background |
  62 | **Autolaunched** | Code/Flow invocation | Subflows, Apex-called, REST API | Background |
  63 | **Flow Orchestration** | Multi-step workflow | Approvals, multi-user processes | Background |
  64 
  65 ---
  66 
  67 ## Flow Elements Reference
  68 
  69 ### Logic Elements (Flow Control)
  70 
  71 ```
  72 ┌─────────────────────────────────────────────────────────────────────────┐
  73 │ LOGIC ELEMENTS                                                          │
  74 ├──────────────────┬──────────────────────────────────────────────────────┤
  75 │ Assignment       │ Set variable values; update data as flow progresses │
  76 │                  │ Example: var_Total = var_Subtotal * 1.08             │
  77 ├──────────────────┼──────────────────────────────────────────────────────┤
  78 │ Decision         │ IF/THEN/ELSE routing; branch flow paths             │
  79 │                  │ Example: If Amount > 10000 → High Priority path     │
  80 ├──────────────────┼──────────────────────────────────────────────────────┤
  81 │ Loop             │ Iterate through collections; per-record processing  │
  82 │                  │ Example: For each Contact in collection...          │
  83 │                  │ USE WHEN: Per-record decisions, counters, flags     │
  84 ├──────────────────┼──────────────────────────────────────────────────────┤
  85 │ Collection Sort  │ Organize collection by specified field              │
  86 │                  │ Example: Sort Accounts by AnnualRevenue DESC        │
  87 ├──────────────────┼──────────────────────────────────────────────────────┤
  88 │ Collection Filter│ Create filtered subset without new SOQL query       │
  89 │                  │ Example: Filter Opps where Amount > 5000            │
  90 │                  │ TIP: Use after Get Records to reduce governor use   │
  91 ├──────────────────┼──────────────────────────────────────────────────────┤
  92 │ Transform        │ Map fields and transform collections (bulk)         │
  93 │                  │ Example: Map Contact fields → Lead fields           │
  94 │                  │ USE WHEN: Data mapping, bulk assignments            │
  95 │                  │ 30-50% faster than Loop for field mapping           │
  96 ├──────────────────┼──────────────────────────────────────────────────────┤
  97 │ Custom Error     │ Display error message and stop flow execution       │
  98 │                  │ Example: "Amount must be greater than zero"         │
  99 └──────────────────┴──────────────────────────────────────────────────────┘
 100 ```
 101 
 102 ### Data Elements (CRUD Operations)
 103 
 104 ```
 105 ┌─────────────────────────────────────────────────────────────────────────┐
 106 │ DATA ELEMENTS                                                           │
 107 ├──────────────────┬──────────────────────────────────────────────────────┤
 108 │ Get Records      │ Query database (SOQL equivalent)                    │
 109 │                  │ TIP: Use filters! Unfiltered = governor limit risk  │
 110 │                  │ TIP: Can't traverse parent fields (use 2-step)      │
 111 ├──────────────────┼──────────────────────────────────────────────────────┤
 112 │ Create Records   │ Insert new records; supports collections            │
 113 │                  │ Example: Create Case from Opportunity data          │
 114 ├──────────────────┼──────────────────────────────────────────────────────┤
 115 │ Update Records   │ Modify existing records                             │
 116 │                  │ In Before-Save: No DML needed for trigger record    │
 117 │                  │ In After-Save: Use for related records              │
 118 ├──────────────────┼──────────────────────────────────────────────────────┤
 119 │ Delete Records   │ Remove records from database                        │
 120 │                  │ Example: Delete old cases older than 2 years        │
 121 ├──────────────────┼──────────────────────────────────────────────────────┤
 122 │ Roll Back Records│ Undo pending changes in current transaction         │
 123 │                  │ Use in fault paths for multi-step DML rollback      │
 124 └──────────────────┴──────────────────────────────────────────────────────┘
 125 ```
 126 
 127 ### Interaction Elements (UI & External)
 128 
 129 ```
 130 ┌─────────────────────────────────────────────────────────────────────────┐
 131 │ INTERACTION ELEMENTS                                                    │
 132 ├──────────────────┬──────────────────────────────────────────────────────┤
 133 │ Screen           │ UI canvas with standard/custom components           │
 134 │                  │ Supports: Text, Input, Picklist, Checkbox, LWC      │
 135 │                  │ TIP: Use Stage resource for multi-screen progress   │
 136 ├──────────────────┼──────────────────────────────────────────────────────┤
 137 │ Action           │ Call external processes                             │
 138 │                  │ Built-in: Send Email, Submit for Approval           │
 139 │                  │ Custom: Apex @InvocableMethod                       │
 140 ├──────────────────┼──────────────────────────────────────────────────────┤
 141 │ Subflow          │ Call another flow with input/output variables       │
 142 │                  │ Use for: Reusable logic, modular architecture       │
 143 │                  │ See: references/subflow-library.md for pre-built subflows │
 144 ├──────────────────┼──────────────────────────────────────────────────────┤
 145 │ Wait             │ Pause flow execution until condition met            │
 146 │                  │ Types: Duration, Date, Platform Event               │
 147 │                  │ See: references/wait-patterns.md for XML patterns         │
 148 └──────────────────┴──────────────────────────────────────────────────────┘
 149 ```
 150 
 151 ---
 152 
 153 ## Variable Types Reference
 154 
 155 ```
 156 ┌─────────────────────────────────────────────────────────────────────────┐
 157 │ FLOW RESOURCE TYPES                                                     │
 158 ├────────────────────┬────────────────────────────────────────────────────┤
 159 │ Type               │ Description & Use Case                            │
 160 ├────────────────────┼────────────────────────────────────────────────────┤
 161 │ Variable           │ Mutable container for data that changes           │
 162 │                    │ Types: Text, Number, Date, DateTime, Boolean,     │
 163 │                    │        Currency, Record, Collection               │
 164 │                    │ Naming: var_AccountName, col_Contacts, rec_Lead   │
 165 ├────────────────────┼────────────────────────────────────────────────────┤
 166 │ Constant           │ Immutable value (set once, never changes)         │
 167 │                    │ Use: Fixed rates, status codes, thresholds        │
 168 │                    │ Example: con_TaxRate = 0.08                        │
 169 ├────────────────────┼────────────────────────────────────────────────────┤
 170 │ Formula            │ Calculated result from variables/constants        │
 171 │                    │ Example: frm_Total = var_Subtotal * (1 + con_Tax) │
 172 ├────────────────────┼────────────────────────────────────────────────────┤
 173 │ Text Template      │ Dynamic text with variable interpolation          │
 174 │                    │ Use: Email bodies, notifications, messages        │
 175 │                    │ Example: "Hello {!var_FirstName}, order ready"    │
 176 ├────────────────────┼────────────────────────────────────────────────────┤
 177 │ Choice             │ Single picklist/radio option (label + value)      │
 178 │                    │ Use: Screen flow input controls                   │
 179 │                    │ Example: { Label: "High", Value: "1" }            │
 180 ├────────────────────┼────────────────────────────────────────────────────┤
 181 │ Collection Choice  │ Options populated from existing Collection        │
 182 │ Set                │ Use: Dynamic dropdown from variable data          │
 183 ├────────────────────┼────────────────────────────────────────────────────┤
 184 │ Record Choice Set  │ Options from SOQL query built into resource       │
 185 │                    │ Use: Query-based selection (e.g., Account list)   │
 186 ├────────────────────┼────────────────────────────────────────────────────┤
 187 │ Picklist Choice    │ Uses standard object picklist field values        │
 188 │ Set                │ Use: Industry, Stage, Status dropdowns            │
 189 ├────────────────────┼────────────────────────────────────────────────────┤
 190 │ Stage              │ Progress tracking across multiple screens         │
 191 │                    │ Use: Multi-screen wizards with visual progress    │
 192 │                    │ Example: Identity → Configuration → Payment       │
 193 └────────────────────┴────────────────────────────────────────────────────┘
 194 ```
 195 
 196 ### Variable Naming Conventions
 197 
 198 | Prefix | Type | Example |
 199 |--------|------|---------|
 200 | `var_` | Single variable | `var_AccountName` |
 201 | `col_` | Collection | `col_Contacts` |
 202 | `rec_` | Record variable | `rec_CurrentLead` |
 203 | `inp_` | Input variable | `inp_RecordId` |
 204 | `out_` | Output variable | `out_ResultMessage` |
 205 | `con_` | Constant | `con_MaxRetries` |
 206 | `frm_` | Formula | `frm_DiscountedPrice` |
 207 
 208 ---
 209 
 210 ## Governor Limit Optimization Patterns
 211 
 212 ### Pattern 1: Collection Filter vs Get Records in Loop
 213 
 214 ```
 215 ┌─────────────────────────────────────────────────────────────────────────┐
 216 │ ❌ ANTI-PATTERN: Get Records Inside Loop                               │
 217 └─────────────────────────────────────────────────────────────────────────┘
 218 
 219     Loop (Accounts)
 220     └── Get Records (Contacts WHERE AccountId = current Account)
 221         └── ⚠️ SOQL limit: 100 queries per transaction!
 222 
 223 ┌─────────────────────────────────────────────────────────────────────────┐
 224 │ ✅ BEST PRACTICE: Query Once + Collection Filter                       │
 225 └─────────────────────────────────────────────────────────────────────────┘
 226 
 227     Get Records (All Contacts for Account IDs in collection)
 228     └── 1 SOQL query total
 229     Loop (Accounts)
 230     └── Collection Filter (Contacts WHERE AccountId = current)
 231         └── In-memory filtering, no SOQL!
 232 ```
 233 
 234 ### Pattern 2: Entry Criteria for Record-Triggered Flows
 235 
 236 ```
 237 Always use Entry Criteria to limit when flows run:
 238 
 239 ┌─────────────────────────────────────────────────────────────────────────┐
 240 │ Entry Criteria Examples                                                 │
 241 ├─────────────────────────────────────────────────────────────────────────┤
 242 │ Run only when Status changes:                                          │
 243 │   ISNEW() || ISCHANGED({!$Record.Status})                             │
 244 ├─────────────────────────────────────────────────────────────────────────┤
 245 │ Run only for specific record types:                                    │
 246 │   {!$Record.RecordType.DeveloperName} = 'Enterprise'                  │
 247 ├─────────────────────────────────────────────────────────────────────────┤
 248 │ Skip during data loads (bypass pattern):                               │
 249 │   {!$Setup.Flow_Bypass__c.Bypass_All__c} = FALSE                      │
 250 └─────────────────────────────────────────────────────────────────────────┘
 251 ```
 252 
 253 ### Pattern 3: Transform vs Loop Decision
 254 
 255 ```
 256 ┌─────────────────────────────────────────────────────────────────────────┐
 257 │ When to Use Transform vs Loop                                          │
 258 ├───────────────────────────────┬─────────────────────────────────────────┤
 259 │ USE TRANSFORM (30-50% faster) │ USE LOOP                                │
 260 ├───────────────────────────────┼─────────────────────────────────────────┤
 261 │ Data mapping/shaping          │ Per-record IF/ELSE decisions            │
 262 │ Bulk field assignments        │ Counters, flags, state tracking         │
 263 │ Simple formula calculations   │ Varying business rules per record       │
 264 │ Record type conversion        │ Complex conditional transformations     │
 265 └───────────────────────────────┴─────────────────────────────────────────┘
 266 
 267 See: references/transform-vs-loop-guide.md for detailed decision criteria
 268 ```
 269 
 270 ---
 271 
 272 ## Before-Save vs After-Save Triggers
 273 
 274 ```
 275 ┌─────────────────────────────────────────────────────────────────────────┐
 276 │ BEFORE-SAVE TRIGGER                                                     │
 277 ├─────────────────────────────────────────────────────────────────────────┤
 278 │ When: Before record is committed to database                           │
 279 │ Can modify: Trigger record only ($Record)                              │
 280 │ DML needed: NO (changes auto-saved with record)                        │
 281 │ Use for:                                                               │
 282 │   • Field defaulting and auto-population                               │
 283 │   • Validation and Custom Errors                                       │
 284 │   • Same-record field calculations                                     │
 285 │   • Preventing record creation (throw error)                           │
 286 └─────────────────────────────────────────────────────────────────────────┘
 287 
 288 ┌─────────────────────────────────────────────────────────────────────────┐
 289 │ AFTER-SAVE TRIGGER                                                      │
 290 ├─────────────────────────────────────────────────────────────────────────┤
 291 │ When: After record is committed (has ID)                               │
 292 │ Can modify: Related/child records, external systems                    │
 293 │ DML needed: YES (explicit Create/Update/Delete required)               │
 294 │ Use for:                                                               │
 295 │   • Creating child records                                             │
 296 │   • Updating parent/related records                                    │
 297 │   • Sending emails, notifications                                      │
 298 │   • HTTP callouts to external systems                                  │
 299 │   ⚠️ CAUTION: Updating same object can cause infinite loop!           │
 300 └─────────────────────────────────────────────────────────────────────────┘
 301 ```
 302 
 303 ---
 304 
 305 ## Common Anti-Patterns to Avoid
 306 
 307 | Anti-Pattern | Problem | Solution |
 308 |--------------|---------|----------|
 309 | DML in Loop | Governor limit failure | Collect records, single DML after loop |
 310 | SOQL in Loop | Query limit exceeded | Query all data upfront, filter in memory |
 311 | No fault paths | Silent failures | Add fault connector to all DML elements |
 312 | No entry criteria | Runs on every update | Use ISCHANGED() or field conditions |
 313 | After-Save same object | Infinite recursion | Add recursion check or use Before-Save |
 314 | Hardcoded IDs | Fails in different orgs | Use Custom Metadata or Custom Labels |
 315 | Unfiltered Get Records | Too many records | Always add filter conditions |
 316 | Loop for field mapping | Slower processing | Use Transform element instead |
 317 
 318 ---
 319 
 320 ## Quick Reference: Element Connectors
 321 
 322 | Element | Connector Types |
 323 |---------|-----------------|
 324 | Decision | One per outcome + Default |
 325 | Loop | `nextValueConnector` (each item) + `noMoreValuesConnector` (after last) |
 326 | Get Records | `connector` (records found) + `faultConnector` (error) |
 327 | Create/Update/Delete | `connector` (success) + `faultConnector` (error) |
 328 | Screen | `connector` (next) |
 329 | Wait | `waitEvents` with `connector` per condition |
 330 
 331 ---
 332 
 333 ## Testing Checklist Quick Reference
 334 
 335 ```
 336 □ Path Coverage
 337   □ All Decision outcomes tested
 338   □ Loop with 0, 1, many records
 339   □ Fault paths triggered
 340 
 341 □ Bulk Testing (Record-Triggered)
 342   □ 1 record
 343   □ 10 records
 344   □ 50 records
 345   □ 200+ records (governor limit boundary)
 346 
 347 □ User Context
 348   □ Standard User profile
 349   □ Admin profile
 350   □ FLS restrictions applied
 351 
 352 □ Edge Cases
 353   □ Null/empty values
 354   □ Maximum field lengths
 355   □ Special characters
 356 ```
 357 
 358 ---
 359 
 360 ## Related Documentation
 361 
 362 | Topic | Document |
 363 |-------|----------|
 364 | Transform vs Loop | [transform-vs-loop-guide.md](./transform-vs-loop-guide.md) |
 365 | Best Practices | [flow-best-practices.md](./flow-best-practices.md) |
 366 | Testing Guide | [testing-guide.md](./testing-guide.md) |
 367 | Governance | [governance-checklist.md](./governance-checklist.md) |
 368 | Subflow Library | [subflow-library.md](./subflow-library.md) |
 369 | Wait Patterns | [wait-patterns.md](./wait-patterns.md) |
 370 | LWC Integration | [lwc-integration-guide.md](./lwc-integration-guide.md) |
 371 
 372 ---
 373 
 374 ## Attribution
 375 
 376 Content adapted from:
 377 - **Salesforce Ben** - [Flow Cheat Sheet](https://www.salesforceben.com/salesforce-flow-cheat-sheet-examples-infographic/)
 378 - **Official Salesforce Documentation** - Flow Builder Guide
 379 
 380 See [CREDITS.md](../CREDITS.md) for full attribution.
