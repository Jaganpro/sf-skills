<!-- Parent: sf-data/SKILL.md -->
   1 # Cleanup and Rollback Examples
   2 
   3 Strategies for test data isolation and proper cleanup.
   4 
   5 ## Method 1: Savepoint/Rollback
   6 
   7 Best for synchronous operations in a single transaction.
   8 
   9 ### Basic Pattern
  10 ```apex
  11 // Create savepoint BEFORE any DML
  12 Savepoint sp = Database.setSavepoint();
  13 
  14 try {
  15     // Create test data
  16     Account acc = new Account(Name = 'Test Account');
  17     insert acc;
  18 
  19     Contact con = new Contact(
  20         FirstName = 'Test',
  21         LastName = 'Contact',
  22         AccountId = acc.Id
  23     );
  24     insert con;
  25 
  26     // Perform operations
  27     MyClass.processAccount(acc);
  28 
  29     // Assert results
  30     acc = [SELECT Custom_Field__c FROM Account WHERE Id = :acc.Id];
  31     System.assert(acc.Custom_Field__c != null, 'Field should be populated');
  32 
  33 } finally {
  34     // ALWAYS rollback - even on success
  35     Database.rollback(sp);
  36 }
  37 
  38 // Data is now completely removed
  39 ```
  40 
  41 ### In Unit Tests
  42 ```apex
  43 @isTest
  44 static void testWithRollback() {
  45     Savepoint sp = Database.setSavepoint();
  46 
  47     try {
  48         // Create 1000 test records
  49         List<Account> accounts = new List<Account>();
  50         for (Integer i = 0; i < 1000; i++) {
  51             accounts.add(new Account(Name = 'Rollback Test ' + i));
  52         }
  53         insert accounts;
  54 
  55         // Run business logic
  56         Test.startTest();
  57         BatchProcessor.process(accounts);
  58         Test.stopTest();
  59 
  60         // Assertions
  61         Integer count = [SELECT COUNT() FROM Account WHERE Name LIKE 'Rollback Test%'];
  62         System.assertEquals(1000, count);
  63 
  64     } finally {
  65         Database.rollback(sp);
  66     }
  67 
  68     // Verify cleanup
  69     Integer remaining = [SELECT COUNT() FROM Account WHERE Name LIKE 'Rollback Test%'];
  70     System.assertEquals(0, remaining, 'All records should be rolled back');
  71 }
  72 ```
  73 
  74 ### Limitations
  75 - **Does NOT rollback async operations** (future, queueable, batch)
  76 - Maximum 5 savepoints per transaction
  77 - Cannot rollback across transaction boundaries
  78 
  79 ## Method 2: Cleanup by Name Pattern
  80 
  81 Best when savepoint isn't possible (async tests, multi-transaction).
  82 
  83 ### Single Object Cleanup
  84 ```apex
  85 // Delete all test accounts
  86 List<Account> toDelete = [
  87     SELECT Id FROM Account
  88     WHERE Name LIKE 'Test%'
  89     LIMIT 10000
  90 ];
  91 delete toDelete;
  92 ```
  93 
  94 ### Multi-Object Cleanup (Correct Order)
  95 ```apex
  96 // CRITICAL: Delete children before parents!
  97 String testPattern = 'Test%';
  98 
  99 // 1. Delete grandchildren first
 100 delete [SELECT Id FROM Task WHERE What.Name LIKE :testPattern];
 101 delete [SELECT Id FROM Event WHERE What.Name LIKE :testPattern];
 102 
 103 // 2. Delete children
 104 delete [SELECT Id FROM Opportunity WHERE Account.Name LIKE :testPattern];
 105 delete [SELECT Id FROM Contact WHERE Account.Name LIKE :testPattern];
 106 delete [SELECT Id FROM Case WHERE Account.Name LIKE :testPattern];
 107 
 108 // 3. Delete parents last
 109 delete [SELECT Id FROM Account WHERE Name LIKE :testPattern];
 110 
 111 System.debug('Cleanup complete');
 112 ```
 113 
 114 ### sf CLI Cleanup
 115 ```bash
 116 # Query records to delete
 117 sf data query \
 118   --query "SELECT Id FROM Account WHERE Name LIKE 'Test%'" \
 119   --target-org dev \
 120   --result-format csv \
 121   > delete-accounts.csv
 122 
 123 # Bulk delete
 124 sf data delete bulk \
 125   --file delete-accounts.csv \
 126   --sobject Account \
 127   --target-org dev \
 128   --wait 30
 129 ```
 130 
 131 ## Method 3: Cleanup by Time Window
 132 
 133 Best for cleaning up after a specific test run.
 134 
 135 ### By CreatedDate
 136 ```apex
 137 // Clean up records created in the last hour
 138 DateTime startTime = DateTime.now().addHours(-1);
 139 String testPattern = 'Test%';
 140 
 141 delete [
 142     SELECT Id FROM Account
 143     WHERE CreatedDate >= :startTime
 144     AND Name LIKE :testPattern
 145 ];
 146 ```
 147 
 148 ### With Timestamp Tracking
 149 ```apex
 150 // At start of test - capture timestamp
 151 DateTime testStartTime = DateTime.now();
 152 
 153 // ... run tests ...
 154 
 155 // Cleanup - only records created during this test
 156 delete [
 157     SELECT Id FROM Account
 158     WHERE CreatedDate >= :testStartTime
 159     AND Name LIKE 'Test%'
 160 ];
 161 ```
 162 
 163 ## Method 4: ID-Based Cleanup
 164 
 165 Most precise - track exactly what you created.
 166 
 167 ### Track IDs During Creation
 168 ```apex
 169 // Collection to track all created record IDs
 170 Set<Id> createdAccountIds = new Set<Id>();
 171 Set<Id> createdContactIds = new Set<Id>();
 172 Set<Id> createdOppIds = new Set<Id>();
 173 
 174 // Create and track
 175 List<Account> accounts = TestDataFactory_Account.create(100);
 176 createdAccountIds.addAll(new Map<Id, Account>(accounts).keySet());
 177 
 178 List<Contact> contacts = TestDataFactory_Contact.createForAccounts(createdAccountIds, 3);
 179 createdContactIds.addAll(new Map<Id, Contact>(contacts).keySet());
 180 
 181 // ... run tests ...
 182 
 183 // Cleanup exactly what we created
 184 delete [SELECT Id FROM Contact WHERE Id IN :createdContactIds];
 185 delete [SELECT Id FROM Account WHERE Id IN :createdAccountIds];
 186 ```
 187 
 188 ### Wrapper Class for Tracking
 189 ```apex
 190 public class TestDataTracker {
 191     private Map<String, Set<Id>> trackedIds = new Map<String, Set<Id>>();
 192 
 193     public void track(SObject record) {
 194         String objType = record.getSObjectType().getDescribe().getName();
 195         if (!trackedIds.containsKey(objType)) {
 196             trackedIds.put(objType, new Set<Id>());
 197         }
 198         trackedIds.get(objType).add(record.Id);
 199     }
 200 
 201     public void trackAll(List<SObject> records) {
 202         for (SObject rec : records) {
 203             track(rec);
 204         }
 205     }
 206 
 207     public void cleanup() {
 208         // Delete in reverse dependency order
 209         List<String> deleteOrder = new List<String>{
 210             'Task', 'Event', 'Opportunity', 'Contact', 'Case', 'Account'
 211         };
 212 
 213         for (String objType : deleteOrder) {
 214             if (trackedIds.containsKey(objType)) {
 215                 Set<Id> ids = trackedIds.get(objType);
 216                 String query = 'SELECT Id FROM ' + objType + ' WHERE Id IN :ids';
 217                 delete Database.query(query);
 218             }
 219         }
 220     }
 221 }
 222 
 223 // Usage
 224 TestDataTracker tracker = new TestDataTracker();
 225 
 226 List<Account> accounts = TestDataFactory_Account.create(100);
 227 tracker.trackAll(accounts);
 228 
 229 List<Contact> contacts = TestDataFactory_Contact.create(50);
 230 tracker.trackAll(contacts);
 231 
 232 // ... run tests ...
 233 
 234 // Clean up everything tracked
 235 tracker.cleanup();
 236 ```
 237 
 238 ## Method 5: @testSetup Isolation
 239 
 240 Automatic rollback with @isTest annotation.
 241 
 242 ```apex
 243 @isTest
 244 public class MyTestClass {
 245 
 246     @testSetup
 247     static void setup() {
 248         // This data is automatically rolled back after ALL tests complete
 249         List<Account> accounts = TestDataFactory_Account.create(100);
 250     }
 251 
 252     @isTest
 253     static void testMethod1() {
 254         // Access setup data
 255         List<Account> accounts = [SELECT Id FROM Account];
 256         // Modify data - changes rolled back after this test
 257         delete accounts[0];
 258     }
 259 
 260     @isTest
 261     static void testMethod2() {
 262         // Fresh copy of @testSetup data - all 100 accounts available
 263         List<Account> accounts = [SELECT Id FROM Account];
 264         System.assertEquals(100, accounts.size());
 265     }
 266 }
 267 ```
 268 
 269 ## Cleanup via sf CLI
 270 
 271 ### Generate Cleanup CSV
 272 ```bash
 273 # Export IDs of test records
 274 sf data query \
 275   --query "SELECT Id FROM Account WHERE Name LIKE 'Test%'" \
 276   --target-org dev \
 277   --result-format csv \
 278   > cleanup-accounts.csv
 279 
 280 sf data query \
 281   --query "SELECT Id FROM Contact WHERE Account.Name LIKE 'Test%'" \
 282   --target-org dev \
 283   --result-format csv \
 284   > cleanup-contacts.csv
 285 ```
 286 
 287 ### Execute Bulk Delete
 288 ```bash
 289 # Delete children first
 290 sf data delete bulk \
 291   --file cleanup-contacts.csv \
 292   --sobject Contact \
 293   --target-org dev \
 294   --wait 30
 295 
 296 # Then delete parents
 297 sf data delete bulk \
 298   --file cleanup-accounts.csv \
 299   --sobject Account \
 300   --target-org dev \
 301   --wait 30
 302 ```
 303 
 304 ## Best Practices Summary
 305 
 306 | Method | Best For | Limitations |
 307 |--------|----------|-------------|
 308 | Savepoint/Rollback | Synchronous tests | No async, max 5 savepoints |
 309 | Name Pattern | Ad-hoc cleanup | May delete unintended records |
 310 | Time Window | Post-test cleanup | Needs accurate timestamp |
 311 | ID Tracking | Precise cleanup | Requires tracking discipline |
 312 | @testSetup | Unit tests | Only in @isTest classes |
 313 | sf CLI Bulk | Large volumes | External tool required |
 314 
 315 ## Golden Rules
 316 
 317 1. **Always delete children before parents** - Respect relationships
 318 2. **Use specific patterns** - 'Test%', 'BulkTest%' to avoid accidents
 319 3. **Verify before delete** - Query first to see what will be deleted
 320 4. **Test cleanup in sandbox** - Never run unverified cleanup in prod
 321 5. **Track created IDs** - Most reliable cleanup method
