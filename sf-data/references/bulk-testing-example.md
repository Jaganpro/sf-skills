<!-- Parent: sf-data/SKILL.md -->
   1 # Bulk Testing Example
   2 
   3 Testing Apex triggers and flows with bulk data operations.
   4 
   5 ## Scenario
   6 
   7 Test an Account trigger that:
   8 - Fires on insert with 200+ records
   9 - Updates a custom field based on Industry
  10 - Creates a related Task for high-value accounts
  11 
  12 ## Why 201 Records?
  13 
  14 Salesforce processes triggers in batches of 200. Testing with 201+ records ensures:
  15 - Trigger handles batch boundaries
  16 - No governor limit violations in loops
  17 - SOQL/DML operations are bulkified
  18 
  19 ## Method 1: Anonymous Apex Factory
  20 
  21 ### Create Test Data
  22 ```apex
  23 // Create 251 Accounts to test trigger bulkification
  24 List<Account> accounts = new List<Account>();
  25 
  26 List<String> industries = new List<String>{
  27     'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail'
  28 };
  29 
  30 for (Integer i = 0; i < 251; i++) {
  31     accounts.add(new Account(
  32         Name = 'BulkTest Account ' + i,
  33         Industry = industries[Math.mod(i, industries.size())],
  34         AnnualRevenue = Math.round(Math.random() * 10000000)
  35     ));
  36 }
  37 
  38 // Single DML - triggers fire in batches of 200
  39 insert accounts;
  40 
  41 System.debug('Created ' + accounts.size() + ' accounts');
  42 System.debug('SOQL Queries Used: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
  43 System.debug('DML Statements: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
  44 ```
  45 
  46 Save as `bulk-test-accounts.apex` and run:
  47 ```bash
  48 sf apex run --file bulk-test-accounts.apex --target-org dev
  49 ```
  50 
  51 ## Method 2: CSV Bulk Import
  52 
  53 ### Create CSV File
  54 ```csv
  55 Name,Industry,AnnualRevenue
  56 BulkTest Account 1,Technology,1000000
  57 BulkTest Account 2,Healthcare,2000000
  58 BulkTest Account 3,Finance,5000000
  59 ... (251 rows)
  60 ```
  61 
  62 ### Import via sf CLI
  63 ```bash
  64 sf data import bulk \
  65   --file accounts-bulk.csv \
  66   --sobject Account \
  67   --target-org dev \
  68   --wait 30
  69 ```
  70 
  71 ## Method 3: JSON Tree Import
  72 
  73 For hierarchical test data with relationships:
  74 
  75 ```json
  76 {
  77   "records": [
  78     {
  79       "attributes": {"type": "Account", "referenceId": "AccountRef1"},
  80       "Name": "BulkTest Parent 1",
  81       "Industry": "Technology",
  82       "Contacts": {
  83         "records": [
  84           {
  85             "attributes": {"type": "Contact"},
  86             "FirstName": "Test",
  87             "LastName": "Contact 1"
  88           }
  89         ]
  90       }
  91     }
  92   ]
  93 }
  94 ```
  95 
  96 ```bash
  97 sf data import tree \
  98   --files bulk-hierarchy.json \
  99   --target-org dev
 100 ```
 101 
 102 ## Verify Trigger Executed Correctly
 103 
 104 ### Check Trigger Results
 105 ```bash
 106 sf data query \
 107   --query "SELECT Id, Name, Industry, Custom_Field__c FROM Account WHERE Name LIKE 'BulkTest%' LIMIT 10" \
 108   --target-org dev \
 109   --json
 110 ```
 111 
 112 ### Check Related Tasks Created
 113 ```bash
 114 sf data query \
 115   --query "SELECT Id, Subject, WhatId, What.Name FROM Task WHERE What.Name LIKE 'BulkTest%'" \
 116   --target-org dev
 117 ```
 118 
 119 ### Count Records
 120 ```bash
 121 sf data query \
 122   --query "SELECT COUNT(Id) total FROM Account WHERE Name LIKE 'BulkTest%'" \
 123   --target-org dev
 124 ```
 125 
 126 ## Test Bulk Update
 127 
 128 ```apex
 129 // Update all test records - triggers fire again
 130 List<Account> accounts = [
 131     SELECT Id, Name, Industry
 132     FROM Account
 133     WHERE Name LIKE 'BulkTest%'
 134 ];
 135 
 136 for (Account acc : accounts) {
 137     acc.Description = 'Bulk updated on ' + DateTime.now();
 138 }
 139 
 140 update accounts;
 141 
 142 System.debug('Updated ' + accounts.size() + ' accounts');
 143 ```
 144 
 145 ## Test Bulk Delete
 146 
 147 ```apex
 148 // Delete in reverse order (children first)
 149 List<Task> tasks = [SELECT Id FROM Task WHERE What.Name LIKE 'BulkTest%'];
 150 delete tasks;
 151 
 152 List<Contact> contacts = [SELECT Id FROM Contact WHERE Account.Name LIKE 'BulkTest%'];
 153 delete contacts;
 154 
 155 List<Account> accounts = [SELECT Id FROM Account WHERE Name LIKE 'BulkTest%'];
 156 delete accounts;
 157 
 158 System.debug('Cleanup complete');
 159 ```
 160 
 161 ## Governor Limits Monitoring
 162 
 163 ```apex
 164 // Add to your test script to monitor limits
 165 System.debug('=== GOVERNOR LIMITS ===');
 166 System.debug('SOQL: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
 167 System.debug('DML Statements: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
 168 System.debug('DML Rows: ' + Limits.getDmlRows() + '/' + Limits.getLimitDmlRows());
 169 System.debug('CPU Time: ' + Limits.getCpuTime() + 'ms/' + Limits.getLimitCpuTime() + 'ms');
 170 System.debug('Heap: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize());
 171 ```
 172 
 173 ## Validation Score
 174 
 175 ```
 176 Score: 128/130 ⭐⭐⭐⭐⭐ Excellent
 177 ├─ Query Efficiency: 25/25 (bulk queries)
 178 ├─ Bulk Safety: 25/25 (251 records, limits monitored)
 179 ├─ Data Integrity: 20/20 (valid field values)
 180 ├─ Security & FLS: 20/20 (no sensitive data)
 181 ├─ Test Patterns: 15/15 (201+ records, variations)
 182 ├─ Cleanup & Isolation: 13/15 (cleanup script provided)
 183 └─ Documentation: 10/10 (fully documented)
 184 ```
 185 
 186 ## Common Issues
 187 
 188 | Issue | Cause | Solution |
 189 |-------|-------|----------|
 190 | `SOQL 101` | Query in loop | Use Map or Set for bulk queries |
 191 | `DML 151` | DML in loop | Collect records, single DML |
 192 | `CPU timeout` | Complex logic | Optimize loops, async processing |
 193 | `Too many records` | >10,000 DML rows | Use Bulk API or Batch Apex |
