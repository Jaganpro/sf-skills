<!-- Parent: sf-data/SKILL.md -->
   1 # Governor Limits Reference
   2 
   3 Essential limits for Salesforce data operations.
   4 
   5 ## SOQL Limits
   6 
   7 | Limit | Synchronous | Asynchronous |
   8 |-------|-------------|--------------|
   9 | Total queries | 100 | 200 |
  10 | Rows retrieved | 50,000 | 50,000 |
  11 | QueryLocator rows | N/A | 50,000,000 |
  12 | Query timeout | 120 seconds | 120 seconds |
  13 
  14 ## DML Limits
  15 
  16 | Limit | Synchronous | Asynchronous |
  17 |-------|-------------|--------------|
  18 | DML statements | 150 | 150 |
  19 | Rows processed | 10,000 | 10,000 |
  20 
  21 ## CPU and Memory
  22 
  23 | Limit | Synchronous | Asynchronous |
  24 |-------|-------------|--------------|
  25 | CPU time | 10,000 ms | 60,000 ms |
  26 | Heap size | 6 MB | 12 MB |
  27 
  28 ## Bulk API Limits
  29 
  30 | Limit | Value |
  31 |-------|-------|
  32 | Batches per 24 hours | 10,000 |
  33 | Records per 24 hours | 10,000,000 |
  34 | Max file size | 100 MB |
  35 | Concurrent jobs | 100 |
  36 
  37 ## Staying Within Limits
  38 
  39 ### SOQL Best Practices
  40 ```apex
  41 // BAD: Query in loop
  42 for (Account acc : accounts) {
  43     List<Contact> cons = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];  // ❌
  44 }
  45 
  46 // GOOD: Single query with relationship
  47 List<Account> accs = [
  48     SELECT Id, (SELECT Id FROM Contacts)
  49     FROM Account
  50     WHERE Id IN :accountIds
  51 ];  // ✓
  52 ```
  53 
  54 ### DML Best Practices
  55 ```apex
  56 // BAD: DML in loop
  57 for (Account acc : accounts) {
  58     update acc;  // ❌
  59 }
  60 
  61 // GOOD: Bulk DML
  62 update accounts;  // ✓
  63 ```
  64 
  65 ## Monitoring Limits
  66 
  67 ```apex
  68 System.debug('SOQL Queries: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
  69 System.debug('DML Statements: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
  70 System.debug('DML Rows: ' + Limits.getDmlRows() + '/' + Limits.getLimitDmlRows());
  71 System.debug('CPU Time: ' + Limits.getCpuTime() + '/' + Limits.getLimitCpuTime());
  72 System.debug('Heap Size: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize());
  73 ```
