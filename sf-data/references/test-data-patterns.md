<!-- Parent: sf-data/SKILL.md -->
   1 # Test Data Patterns Guide
   2 
   3 Best practices for creating realistic and effective test data.
   4 
   5 ## Factory Pattern
   6 
   7 ### Standard Implementation
   8 
   9 ```apex
  10 public class TestDataFactory_Account {
  11 
  12     public static List<Account> create(Integer count) {
  13         return create(count, true);
  14     }
  15 
  16     public static List<Account> create(Integer count, Boolean doInsert) {
  17         List<Account> records = new List<Account>();
  18         for (Integer i = 0; i < count; i++) {
  19             records.add(buildRecord(i));
  20         }
  21         if (doInsert) {
  22             insert records;
  23         }
  24         return records;
  25     }
  26 
  27     private static Account buildRecord(Integer index) {
  28         return new Account(
  29             Name = 'Test Account ' + index,
  30             Industry = 'Technology'
  31         );
  32     }
  33 }
  34 ```
  35 
  36 ### Key Principles
  37 
  38 1. **Always create in lists** - Support bulk operations
  39 2. **Provide doInsert parameter** - Caller controls insertion
  40 3. **Track IDs for cleanup** - Return inserted records
  41 4. **Use realistic data** - Valid picklist values
  42 
  43 ## Record Count Recommendations
  44 
  45 | Test Scenario | Record Count | Why |
  46 |---------------|--------------|-----|
  47 | Basic unit test | 1-10 | Quick validation |
  48 | Trigger testing | 201 | Batch boundary |
  49 | Flow testing | 200 | Single transaction |
  50 | Batch Apex | 500+ | Multiple batches |
  51 | Performance | 1000+ | Stress testing |
  52 
  53 ## Edge Cases to Test
  54 
  55 ### Null Values
  56 ```apex
  57 account.Industry = null;  // Test null handling
  58 ```
  59 
  60 ### Boundary Values
  61 ```apex
  62 account.Name = 'A';  // Min length
  63 account.Name = String.valueOf('X').repeat(255);  // Max length
  64 ```
  65 
  66 ### Special Characters
  67 ```apex
  68 account.Name = 'Test & "Special" <Characters>';
  69 ```
  70 
  71 ### Date Boundaries
  72 ```apex
  73 opp.CloseDate = Date.today();  // Today
  74 opp.CloseDate = Date.today().addDays(-1);  // Yesterday
  75 opp.CloseDate = Date.newInstance(2000, 1, 1);  // Old date
  76 ```
  77 
  78 ## Relationship Testing
  79 
  80 ### Create Hierarchy
  81 ```apex
  82 // Create parent first
  83 List<Account> accounts = TestDataFactory_Account.create(10);
  84 
  85 // Create children with parent references
  86 List<Contact> contacts = TestDataFactory_Contact.createForAccounts(
  87     new List<Id>(new Map<Id, Account>(accounts).keySet()),
  88     5  // 5 contacts per account
  89 );
  90 ```
  91 
  92 ## Best Practices
  93 
  94 1. **Avoid hardcoded IDs** - Use dynamic references
  95 2. **Create all required fields** - Prevent validation errors
  96 3. **Use unique values** - Prevent duplicate errors
  97 4. **Document patterns** - Explain test scenarios
