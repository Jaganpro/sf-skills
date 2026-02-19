<!-- Parent: sf-testing/SKILL.md -->
   1 # Performance Optimization for Apex Tests
   2 
   3 Fast tests enable faster development. When test suites run quickly, developers refactor confidently. This guide covers techniques to dramatically reduce test execution time.
   4 
   5 > **Source**: [James Simone - Writing Performant Apex Tests](https://www.jamessimone.net/blog/joys-of-apex/writing-performant-apex-tests/)
   6 
   7 ---
   8 
   9 ## Why Test Speed Matters
  10 
  11 | Test Suite Duration | Impact |
  12 |---------------------|--------|
  13 | **< 5 minutes** | Developers run frequently, catch issues early |
  14 | **5-30 minutes** | Developers run occasionally, issues slip through |
  15 | **30+ minutes** | Developers avoid running, tests become stale |
  16 | **Hours** | CI/CD bottleneck, blocked deployments |
  17 
  18 The goal: **Sub-second unit tests**, with integration tests taking seconds, not minutes.
  19 
  20 ---
  21 
  22 ## Technique 1: Mock DML Operations
  23 
  24 Database operations are the #1 cause of slow tests.
  25 
  26 ### The Numbers
  27 
  28 | Operation | 10,000 Records | Notes |
  29 |-----------|----------------|-------|
  30 | Actual insert | ~50 seconds | Database round-trips |
  31 | DML mocking | <1 second | In-memory only |
  32 | **Improvement** | **~35x faster** | |
  33 
  34 ### Implementation
  35 
  36 See `assets/dml-mock.cls` and `references/mocking-patterns.md` for complete implementation.
  37 
  38 ```apex
  39 // ❌ SLOW: Actual database insert
  40 List<Account> accounts = TestDataFactory.createAccounts(1000);
  41 insert accounts;  // ~5 seconds
  42 
  43 // ✅ FAST: Mock DML
  44 DMLMock.reset();
  45 AccountService service = new AccountService(new DMLMock());
  46 service.createAccounts(accounts);  // <0.1 seconds
  47 Assert.areEqual(1000, DMLMock.InsertedRecords.size());
  48 ```
  49 
  50 ---
  51 
  52 ## Technique 2: Mock SOQL Queries
  53 
  54 Query execution adds overhead, especially with large result sets.
  55 
  56 ```apex
  57 // ❌ SLOW: Actual query requiring test data setup
  58 @TestSetup
  59 static void setup() {
  60     List<Account> accounts = new List<Account>();
  61     for (Integer i = 0; i < 1000; i++) {
  62         accounts.add(new Account(Name = 'Test ' + i));
  63     }
  64     insert accounts;  // Slow
  65 }
  66 
  67 // ✅ FAST: Mock query results
  68 AccountSelector.setMockResults(new List<Account>{
  69     new Account(Name = 'Mock 1'),
  70     new Account(Name = 'Mock 2')
  71 });
  72 List<Account> results = AccountSelector.getActiveAccounts();  // Instant
  73 ```
  74 
  75 ---
  76 
  77 ## Technique 3: Minimize @TestSetup
  78 
  79 `@TestSetup` runs before every test method. Large setups compound execution time.
  80 
  81 ```apex
  82 // ❌ SLOW: Heavy @TestSetup
  83 @TestSetup
  84 static void setup() {
  85     List<Account> accounts = TestDataFactory.createAccounts(100);
  86     insert accounts;
  87     List<Contact> contacts = TestDataFactory.createContacts(500, accounts);
  88     insert contacts;
  89     List<Opportunity> opps = TestDataFactory.createOpportunities(200, accounts);
  90     insert opps;
  91     // Total: 800 DML operations, runs before EACH test method
  92 }
  93 
  94 // ✅ FAST: Minimal @TestSetup, mock what you can
  95 @TestSetup
  96 static void setup() {
  97     // Only create what MUST exist in database
  98     Account parentAccount = new Account(Name = 'Required Parent');
  99     insert parentAccount;
 100 }
 101 ```
 102 
 103 ---
 104 
 105 ## Technique 4: Choose Efficient Loop Constructs
 106 
 107 Loop performance varies significantly with large iterations.
 108 
 109 ### Benchmark Results (10,000 iterations)
 110 
 111 | Loop Type | Duration | Notes |
 112 |-----------|----------|-------|
 113 | While loop | ~0.4s | Fastest |
 114 | Cached iterator | ~0.8s | Good alternative |
 115 | For loop (index) | ~1.4s | Acceptable |
 116 | Enhanced for loop | ~2.4s | Convenient but slower |
 117 | Uncached iterator | CPU limit | Avoid |
 118 
 119 ### Recommendation
 120 
 121 ```apex
 122 // ✅ PREFERRED: While loop for large iterations
 123 Iterator<Account> iter = accounts.iterator();
 124 while (iter.hasNext()) {
 125     Account acc = iter.next();
 126     // process
 127 }
 128 
 129 // ✅ ACCEPTABLE: Standard for loop
 130 for (Integer i = 0; i < accounts.size(); i++) {
 131     Account acc = accounts[i];
 132     // process
 133 }
 134 
 135 // ⚠️ CONVENIENT BUT SLOWER: Enhanced for
 136 for (Account acc : accounts) {
 137     // process
 138 }
 139 ```
 140 
 141 ---
 142 
 143 ## Technique 5: Batch Test Data Creation
 144 
 145 Creating records one-by-one is slow. Batch operations are faster.
 146 
 147 ```apex
 148 // ❌ SLOW: One-by-one creation
 149 for (Integer i = 0; i < 200; i++) {
 150     Account acc = new Account(Name = 'Test ' + i);
 151     insert acc;  // 200 DML statements!
 152 }
 153 
 154 // ✅ FAST: Batch creation
 155 List<Account> accounts = new List<Account>();
 156 for (Integer i = 0; i < 200; i++) {
 157     accounts.add(new Account(Name = 'Test ' + i));
 158 }
 159 insert accounts;  // 1 DML statement
 160 ```
 161 
 162 ---
 163 
 164 ## Technique 6: Use Assert Instead of System.assert
 165 
 166 The modern `Assert` class is cleaner and provides better error messages.
 167 
 168 ```apex
 169 // ❌ OLD: System.assert (still works but verbose)
 170 System.assert(result != null, 'Result should not be null');
 171 System.assertEquals(expected, actual, 'Values should match');
 172 
 173 // ✅ MODERN: Assert class (Apex 56.0+)
 174 Assert.isNotNull(result, 'Result should not be null');
 175 Assert.areEqual(expected, actual, 'Values should match');
 176 Assert.isTrue(condition, 'Condition should be true');
 177 Assert.fail('Should not reach here');
 178 ```
 179 
 180 ---
 181 
 182 ## Technique 7: Avoid SOSL in Tests
 183 
 184 SOSL searches return empty results in tests unless configured.
 185 
 186 ```apex
 187 // ❌ PROBLEM: SOSL returns nothing in tests by default
 188 List<List<SObject>> results = [FIND 'test' IN ALL FIELDS RETURNING Account];
 189 // results[0] is EMPTY even with matching records!
 190 
 191 // ✅ SOLUTION: Use Test.setFixedSearchResults()
 192 @IsTest
 193 static void testSearch() {
 194     Account acc = new Account(Name = 'Searchable');
 195     insert acc;
 196 
 197     // Configure what SOSL will return
 198     Test.setFixedSearchResults(new List<Id>{ acc.Id });
 199 
 200     Test.startTest();
 201     List<List<SObject>> results = [FIND 'test' IN ALL FIELDS RETURNING Account];
 202     Test.stopTest();
 203 
 204     Assert.areEqual(1, results[0].size(), 'Should find configured record');
 205 }
 206 ```
 207 
 208 ---
 209 
 210 ## Technique 8: Strategic Test Method Scoping
 211 
 212 Run only the tests you need during development.
 213 
 214 ```bash
 215 # ❌ SLOW: Run all tests (minutes to hours)
 216 sf apex run test --test-level RunLocalTests --target-org sandbox
 217 
 218 # ✅ FAST: Run single test class
 219 sf apex run test --class-names MyClassTest --target-org sandbox
 220 
 221 # ✅ FASTER: Run single test method
 222 sf apex run test --tests MyClassTest.testSpecificMethod --target-org sandbox
 223 ```
 224 
 225 ---
 226 
 227 ## Technique 9: Async Test Execution
 228 
 229 Use async mode for large test suites to avoid blocking.
 230 
 231 ```bash
 232 # Start tests asynchronously
 233 sf apex run test --class-names MyClassTest --wait 0 --target-org sandbox
 234 # Returns test run ID: 707xx0000000000
 235 
 236 # Check status later
 237 sf apex get test --test-run-id 707xx0000000000 --target-org sandbox
 238 ```
 239 
 240 ---
 241 
 242 ## Anti-Patterns to Avoid
 243 
 244 | Anti-Pattern | Problem | Solution |
 245 |--------------|---------|----------|
 246 | DML in loops | N operations instead of 1 | Bulk DML outside loops |
 247 | Large @TestSetup | Runs before every test | Minimize or mock |
 248 | No mocking | Full database round-trips | Mock DML, queries, callouts |
 249 | SeeAllData=true | Depends on org data | Create test data |
 250 | Deep nested loops | O(n²) or worse | Flatten with Maps |
 251 | String concatenation in loops | New string objects each iteration | Use List and join |
 252 
 253 ---
 254 
 255 ## Optimization Checklist
 256 
 257 Before committing tests, verify:
 258 
 259 - [ ] DML operations are mocked where possible
 260 - [ ] @TestSetup is minimal
 261 - [ ] No SOQL/DML inside loops
 262 - [ ] Uses bulk patterns (200+ records)
 263 - [ ] Individual test methods run in <1 second
 264 - [ ] Full test class runs in <10 seconds
 265 - [ ] Uses Assert class (not System.assert)
 266 
 267 ---
 268 
 269 ## Performance Testing Your Tests
 270 
 271 ```apex
 272 @IsTest
 273 static void testPerformance() {
 274     Long startTime = System.currentTimeMillis();
 275 
 276     // Your test code here
 277 
 278     Long duration = System.currentTimeMillis() - startTime;
 279     System.debug('Test duration: ' + duration + 'ms');
 280 
 281     // Assert performance constraint
 282     Assert.isTrue(duration < 1000, 'Test should complete in <1 second, took: ' + duration + 'ms');
 283 }
 284 ```
