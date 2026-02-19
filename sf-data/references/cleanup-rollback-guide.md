<!-- Parent: sf-data/SKILL.md -->
   1 # Cleanup and Rollback Guide
   2 
   3 Strategies for test data isolation and cleanup.
   4 
   5 ## Savepoint/Rollback Pattern
   6 
   7 Best for synchronous test isolation.
   8 
   9 ```apex
  10 // Create savepoint BEFORE any DML
  11 Savepoint sp = Database.setSavepoint();
  12 
  13 try {
  14     // Create test data
  15     List<Account> accounts = TestDataFactory_Account.create(100);
  16 
  17     // Run your tests
  18     Test.startTest();
  19     MyClass.processAccounts(accounts);
  20     Test.stopTest();
  21 
  22     // Assert results
  23     System.assertEquals(expected, actual);
  24 
  25 } finally {
  26     // Always rollback
  27     Database.rollback(sp);
  28 }
  29 ```
  30 
  31 **Limitations:**
  32 - Does not roll back async operations
  33 - Maximum 5 savepoints per transaction
  34 
  35 ## Cleanup by Name Pattern
  36 
  37 ```apex
  38 String pattern = 'Test%';
  39 
  40 DELETE [SELECT Id FROM Opportunity WHERE Name LIKE :pattern];
  41 DELETE [SELECT Id FROM Contact WHERE LastName LIKE :pattern];
  42 DELETE [SELECT Id FROM Account WHERE Name LIKE :pattern];
  43 ```
  44 
  45 **Order matters:** Delete children before parents.
  46 
  47 ## Cleanup by Date
  48 
  49 ```apex
  50 DateTime startTime = DateTime.now().addHours(-1);
  51 
  52 DELETE [
  53     SELECT Id FROM Account
  54     WHERE CreatedDate >= :startTime
  55     AND Name LIKE 'Test%'
  56 ];
  57 ```
  58 
  59 ## Cleanup via sf CLI
  60 
  61 ```bash
  62 # Export IDs to delete
  63 sf data query \
  64   --query "SELECT Id FROM Account WHERE Name LIKE 'Test%'" \
  65   --target-org myorg \
  66   --result-format csv \
  67   > delete.csv
  68 
  69 # Bulk delete
  70 sf data delete bulk \
  71   --file delete.csv \
  72   --sobject Account \
  73   --target-org myorg \
  74   --wait 30
  75 ```
  76 
  77 ## Best Practices
  78 
  79 1. **Track created IDs** - Store in Set<Id>
  80 2. **Delete in order** - Children first, parents last
  81 3. **Use test prefixes** - 'Test', 'BulkTest'
  82 4. **Preview before delete** - Verify records first
  83 5. **Use @isTest** - Auto-rollback in tests
