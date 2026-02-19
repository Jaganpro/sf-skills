<!-- Parent: sf-data/SKILL.md -->
   1 # Anonymous Apex Guide
   2 
   3 Using anonymous Apex for complex data operations.
   4 
   5 ## When to Use Anonymous Apex
   6 
   7 - Complex data setup requiring Apex logic
   8 - Testing triggers with specific data patterns
   9 - One-time data migrations
  10 - Debugging and troubleshooting
  11 
  12 ## sf CLI Execution
  13 
  14 ### From File
  15 ```bash
  16 sf apex run --file setup-data.apex --target-org myorg
  17 ```
  18 
  19 ### Interactive
  20 ```bash
  21 sf apex run --target-org myorg
  22 # Then type Apex code and press Ctrl+D
  23 ```
  24 
  25 ## Common Patterns
  26 
  27 ### Bulk Data Creation
  28 ```apex
  29 List<Account> accounts = new List<Account>();
  30 for (Integer i = 0; i < 500; i++) {
  31     accounts.add(new Account(
  32         Name = 'Test Account ' + i,
  33         Industry = 'Technology'
  34     ));
  35 }
  36 insert accounts;
  37 System.debug('Created ' + accounts.size() + ' accounts');
  38 ```
  39 
  40 ### Data Transformation
  41 ```apex
  42 List<Account> accounts = [
  43     SELECT Id, Name, Industry
  44     FROM Account
  45     WHERE Name LIKE 'Old%'
  46 ];
  47 
  48 for (Account acc : accounts) {
  49     acc.Name = acc.Name.replace('Old', 'New');
  50 }
  51 
  52 update accounts;
  53 ```
  54 
  55 ### Testing Trigger Logic
  56 ```apex
  57 // Setup test data
  58 Account acc = new Account(Name = 'Trigger Test');
  59 insert acc;
  60 
  61 // Force trigger to fire
  62 acc.Industry = 'Technology';
  63 update acc;
  64 
  65 // Verify results
  66 acc = [SELECT Id, Field__c FROM Account WHERE Id = :acc.Id];
  67 System.debug('Result: ' + acc.Field__c);
  68 ```
  69 
  70 ## Error Handling
  71 
  72 ```apex
  73 try {
  74     insert accounts;
  75 } catch (DmlException e) {
  76     System.debug('Error: ' + e.getMessage());
  77     for (Integer i = 0; i < e.getNumDml(); i++) {
  78         System.debug('Row ' + e.getDmlIndex(i) + ': ' + e.getDmlMessage(i));
  79     }
  80 }
  81 ```
  82 
  83 ## Limits in Anonymous Apex
  84 
  85 | Limit | Value |
  86 |-------|-------|
  87 | SOQL Queries | 100 |
  88 | DML Rows | 10,000 |
  89 | CPU Time | 10,000 ms |
  90 | Heap Size | 6 MB |
  91 
  92 ## Best Practices
  93 
  94 1. **Test in sandbox first** - Validate before production
  95 2. **Add debug statements** - Track progress
  96 3. **Handle errors gracefully** - Use try/catch
  97 4. **Keep scripts idempotent** - Safe to re-run
