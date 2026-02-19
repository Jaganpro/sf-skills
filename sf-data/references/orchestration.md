<!-- Parent: sf-data/SKILL.md -->
   1 # Multi-Skill Orchestration: sf-data Perspective
   2 
   3 This document details how sf-data fits into the multi-skill workflow for Salesforce development.
   4 
   5 ---
   6 
   7 ## Standard Orchestration Order
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────────────┐
  11 │  STANDARD MULTI-SKILL ORCHESTRATION ORDER                                   │
  12 ├─────────────────────────────────────────────────────────────────────────────┤
  13 │  1. sf-metadata                                                             │
  14 │     └── Create object/field definitions (LOCAL files)                       │
  15 │                                                                             │
  16 │  2. sf-flow                                                                 │
  17 │     └── Create flow definitions (LOCAL files)                               │
  18 │                                                                             │
  19 │  3. sf-deploy                                                               │
  20 │     └── Deploy all metadata (REMOTE)                                        │
  21 │                                                                             │
  22 │  4. sf-data  ◀── YOU ARE HERE (LAST!)                                      │
  23 │     └── Create test data (REMOTE - objects must exist!)                     │
  24 └─────────────────────────────────────────────────────────────────────────────┘
  25 ```
  26 
  27 ---
  28 
  29 ## ⚠️ Why sf-data Goes LAST
  30 
  31 **sf-data operates on REMOTE org data.** Objects/fields must be deployed before sf-data can:
  32 - Insert records
  33 - Query existing data
  34 - Run test factories
  35 - Generate bulk test data
  36 
  37 ```
  38 ERROR: "SObject type 'Quote__c' is not supported"
  39 CAUSE: Quote__c object was never deployed to the org
  40 FIX:   Run sf-deploy BEFORE sf-data
  41 ```
  42 
  43 ---
  44 
  45 ## Common Errors from Wrong Order
  46 
  47 | Error | Cause | Fix |
  48 |-------|-------|-----|
  49 | `SObject type 'X' not supported` | Object not deployed | Deploy via sf-deploy first |
  50 | `INVALID_FIELD: No such column 'Field__c'` | Field not deployed OR FLS | Deploy field + Permission Set |
  51 | `REQUIRED_FIELD_MISSING` | Validation rule requires field | Include all required fields |
  52 | `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule triggered | Use valid test data values |
  53 
  54 ---
  55 
  56 ## Test Data After Triggers/Flows
  57 
  58 When testing triggers or flows, always create test data AFTER deployment:
  59 
  60 ```
  61 1. sf-apex   → Create trigger handler class
  62 2. sf-flow   → Create record-triggered flow
  63 3. sf-deploy → Deploy trigger + flow + objects
  64 4. sf-data   ◀── CREATE TEST DATA NOW
  65               └── Triggers and flows will fire!
  66 ```
  67 
  68 **Why?** Test data insertion triggers flows/triggers. If those aren't deployed, you're not testing realistic behavior.
  69 
  70 ---
  71 
  72 ## The 251-Record Pattern
  73 
  74 Always test with **251 records** to cross the 200-record batch boundary:
  75 
  76 ```
  77 ┌─────────────────────────────────────────────────────────────────────────────┐
  78 │  BATCH BOUNDARY TESTING                                                     │
  79 ├─────────────────────────────────────────────────────────────────────────────┤
  80 │  Records 1-200:    First batch                                              │
  81 │  Records 201-251:  Second batch (crosses boundary!)                         │
  82 │                                                                             │
  83 │  Tests: N+1 queries, bulkification, governor limits                         │
  84 └─────────────────────────────────────────────────────────────────────────────┘
  85 ```
  86 
  87 **Command:**
  88 ```bash
  89 sf apex run --file test-factory.apex --target-org alias
  90 # test-factory.apex creates 251 records
  91 ```
  92 
  93 ---
  94 
  95 ## Cross-Skill Integration Table
  96 
  97 | From Skill | To sf-data | When |
  98 |------------|------------|------|
  99 | sf-apex | → sf-data | "Create 251 Accounts for bulk testing" |
 100 | sf-flow | → sf-data | "Create Opportunities with StageName='Closed Won'" |
 101 | sf-testing | → sf-data | "Generate test records for test class" |
 102 
 103 | From sf-data | To Skill | When |
 104 |--------------|----------|------|
 105 | sf-data | → sf-metadata | "Describe Invoice__c" (discover object structure) |
 106 | sf-data | → sf-deploy | "Redeploy field after adding validation rule" |
 107 
 108 ---
 109 
 110 ## Prerequisites Check
 111 
 112 Before using sf-data, verify:
 113 
 114 ```bash
 115 # Check org connection
 116 sf org display --target-org alias
 117 
 118 # Check objects exist
 119 sf sobject describe --sobject MyObject__c --target-org alias --json
 120 
 121 # Check field-level security (if field not visible)
 122 sf data query --query "SELECT Id FROM FieldPermissions WHERE SobjectType='MyObject__c'" --use-tooling-api --target-org alias
 123 ```
 124 
 125 ---
 126 
 127 ## Factory Pattern Integration
 128 
 129 Test Data Factory classes work with sf-data:
 130 
 131 ```
 132 sf-apex:  Creates TestDataFactory_Account.cls
 133           ↓
 134 sf-deploy: Deploys factory class
 135           ↓
 136 sf-data:  Calls factory via Anonymous Apex
 137           ↓
 138           251 records created → triggers fire → flows run
 139 ```
 140 
 141 **Anonymous Apex:**
 142 ```apex
 143 List<Account> accounts = TestDataFactory_Account.create(251);
 144 System.debug('Created ' + accounts.size() + ' accounts');
 145 ```
 146 
 147 ---
 148 
 149 ## Cleanup Sequence
 150 
 151 After testing, clean up in reverse order:
 152 
 153 ```
 154 1. sf-data   → Delete test records
 155 2. sf-deploy → Deactivate flows (if needed)
 156 3. sf-deploy → Remove test metadata (if needed)
 157 ```
 158 
 159 **Cleanup command:**
 160 ```bash
 161 sf apex run --file cleanup.apex --target-org alias
 162 # cleanup.apex: DELETE [SELECT Id FROM Account WHERE Name LIKE 'Test%']
 163 ```
 164 
 165 ---
 166 
 167 ## Related Documentation
 168 
 169 | Topic | Location |
 170 |-------|----------|
 171 | Test data patterns | `sf-data/references/test-data-patterns.md` |
 172 | Cleanup guide | `sf-data/references/cleanup-rollback-guide.md` |
 173 | Factory templates | `sf-data/assets/factories/` |
