<!-- Parent: sf-testing/SKILL.md -->
   1 # Apex Testing Best Practices
   2 
   3 ## Overview
   4 
   5 This guide covers best practices for writing effective, maintainable Apex tests that ensure code quality and prevent regressions.
   6 
   7 ## The Testing Pyramid
   8 
   9 ```
  10                     ╱╲
  11                    ╱  ╲
  12                   ╱ E2E╲        Few end-to-end tests
  13                  ╱──────╲
  14                 ╱        ╲
  15                ╱Integration╲    Moderate integration tests
  16               ╱────────────╲
  17              ╱              ╲
  18             ╱   Unit Tests   ╲  Many unit tests
  19            ╱──────────────────╲
  20 ```
  21 
  22 ## Core Principles
  23 
  24 ### 1. Test One Thing Per Method
  25 
  26 ```apex
  27 // ❌ BAD: Testing multiple things
  28 @IsTest
  29 static void testEverything() {
  30     Account acc = new Account(Name = 'Test');
  31     insert acc;
  32     acc.Name = 'Updated';
  33     update acc;
  34     delete acc;
  35     // What exactly are we testing?
  36 }
  37 
  38 // ✅ GOOD: Single responsibility
  39 @IsTest
  40 static void testAccountInsert_ValidName_Success() {
  41     Account acc = new Account(Name = 'Test');
  42     insert acc;
  43     Assert.isNotNull(acc.Id, 'Account should be inserted');
  44 }
  45 
  46 @IsTest
  47 static void testAccountUpdate_ChangeName_Success() {
  48     Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
  49     acc.Name = 'Updated';
  50     update acc;
  51     Account updated = [SELECT Name FROM Account WHERE Id = :acc.Id];
  52     Assert.areEqual('Updated', updated.Name, 'Name should be updated');
  53 }
  54 ```
  55 
  56 ### 2. Use Descriptive Test Names
  57 
  58 ```apex
  59 // ❌ BAD: Unclear names
  60 @IsTest static void test1() { }
  61 @IsTest static void testMethod() { }
  62 
  63 // ✅ GOOD: Describes scenario, condition, and expectation
  64 @IsTest static void testCreateAccount_WithValidData_ReturnsId() { }
  65 @IsTest static void testCreateAccount_WithNullName_ThrowsException() { }
  66 @IsTest static void testBulkInsert_251Records_AllSucceed() { }
  67 ```
  68 
  69 ### 3. Follow AAA Pattern (Arrange-Act-Assert)
  70 
  71 ```apex
  72 @IsTest
  73 static void testCalculateDiscount_VIPCustomer_Returns20Percent() {
  74     // ARRANGE - Set up test data
  75     Account vipAccount = new Account(
  76         Name = 'VIP Customer',
  77         Type = 'VIP'
  78     );
  79     insert vipAccount;
  80 
  81     // ACT - Execute the code under test
  82     Test.startTest();
  83     Decimal discount = DiscountService.calculateDiscount(vipAccount.Id);
  84     Test.stopTest();
  85 
  86     // ASSERT - Verify results
  87     Assert.areEqual(0.20, discount, 'VIP customers should get 20% discount');
  88 }
  89 ```
  90 
  91 ## Test Data Factory Pattern
  92 
  93 ### Why Use Test Data Factory?
  94 
  95 1. **Consistency**: Same data creation logic everywhere
  96 2. **Maintainability**: Change in one place affects all tests
  97 3. **Readability**: Tests focus on logic, not data setup
  98 4. **Flexibility**: Easy to create variations
  99 
 100 ### Factory Methods
 101 
 102 ```apex
 103 @IsTest
 104 public class TestDataFactory {
 105 
 106     // Basic creation (no insert)
 107     public static List<Account> createAccounts(Integer count) {
 108         List<Account> accounts = new List<Account>();
 109         for (Integer i = 0; i < count; i++) {
 110             accounts.add(new Account(
 111                 Name = 'Test Account ' + i,
 112                 Industry = 'Technology'
 113             ));
 114         }
 115         return accounts;
 116     }
 117 
 118     // Create and insert
 119     public static List<Account> createAndInsertAccounts(Integer count) {
 120         List<Account> accounts = createAccounts(count);
 121         insert accounts;
 122         return accounts;
 123     }
 124 
 125     // With specific attributes
 126     public static Account createAccount(String name, String industry) {
 127         return new Account(Name = name, Industry = industry);
 128     }
 129 }
 130 ```
 131 
 132 ## @TestSetup for Efficiency
 133 
 134 ```apex
 135 @IsTest
 136 private class AccountServiceTest {
 137 
 138     @TestSetup
 139     static void setupTestData() {
 140         // This runs ONCE for all test methods in the class
 141         // Data is rolled back after each test method
 142         List<Account> accounts = TestDataFactory.createAccounts(10);
 143         insert accounts;
 144 
 145         List<Contact> contacts = new List<Contact>();
 146         for (Account acc : accounts) {
 147             contacts.addAll(TestDataFactory.createContacts(5, acc.Id));
 148         }
 149         insert contacts;
 150     }
 151 
 152     @IsTest
 153     static void testMethod1() {
 154         // Has access to 10 accounts and 50 contacts
 155         List<Account> accounts = [SELECT Id FROM Account];
 156         Assert.areEqual(10, accounts.size());
 157     }
 158 
 159     @IsTest
 160     static void testMethod2() {
 161         // ALSO has access to 10 accounts and 50 contacts
 162         // @TestSetup data is available to all test methods
 163         List<Contact> contacts = [SELECT Id FROM Contact];
 164         Assert.areEqual(50, contacts.size());
 165     }
 166 }
 167 ```
 168 
 169 ## Bulk Testing (251+ Records)
 170 
 171 ### Why 251 Records?
 172 
 173 Triggers process records in batches of 200. Testing with 251 records ensures:
 174 - First batch: 200 records
 175 - Second batch: 51 records
 176 - Crosses the batch boundary, revealing bulkification issues
 177 
 178 ```apex
 179 @IsTest
 180 static void testTrigger_BulkInsert_NoDMLInLoop() {
 181     // ARRANGE
 182     List<Account> accounts = TestDataFactory.createAccounts(251);
 183 
 184     // ACT
 185     Test.startTest();
 186     insert accounts;  // Trigger fires twice: 200, then 51
 187     Test.stopTest();
 188 
 189     // ASSERT
 190     Assert.areEqual(251, [SELECT COUNT() FROM Account],
 191         'All 251 accounts should be created');
 192 
 193     // Verify governor limits not approached
 194     Assert.isTrue(Limits.getQueries() < 90,
 195         'Should not approach SOQL limit');
 196 }
 197 ```
 198 
 199 ## Negative Testing
 200 
 201 ### Test for Expected Failures
 202 
 203 ```apex
 204 @IsTest
 205 static void testCreateAccount_NullName_ThrowsException() {
 206     try {
 207         Account acc = new Account(Name = null);
 208         insert acc;
 209         Assert.fail('Expected DmlException was not thrown');
 210     } catch (DmlException e) {
 211         Assert.isTrue(
 212             e.getMessage().contains('REQUIRED_FIELD_MISSING'),
 213             'Should throw required field error'
 214         );
 215     }
 216 }
 217 
 218 @IsTest
 219 static void testWithdraw_InsufficientFunds_ReturnsFalse() {
 220     Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
 221     acc.AnnualRevenue = 100;
 222     update acc;
 223 
 224     Test.startTest();
 225     Boolean result = AccountService.withdraw(acc.Id, 200);
 226     Test.stopTest();
 227 
 228     Assert.isFalse(result, 'Withdrawal should fail with insufficient funds');
 229 }
 230 ```
 231 
 232 ## Mock Framework Patterns
 233 
 234 ### HttpCalloutMock
 235 
 236 ```apex
 237 private class SuccessHttpMock implements HttpCalloutMock {
 238     public HttpResponse respond(HttpRequest req) {
 239         HttpResponse res = new HttpResponse();
 240         res.setStatusCode(200);
 241         res.setBody('{"success": true}');
 242         return res;
 243     }
 244 }
 245 
 246 @IsTest
 247 static void testExternalAPICall_Success() {
 248     Test.setMock(HttpCalloutMock.class, new SuccessHttpMock());
 249 
 250     Test.startTest();
 251     String result = MyService.callExternalAPI();
 252     Test.stopTest();
 253 
 254     Assert.isTrue(result.contains('success'));
 255 }
 256 ```
 257 
 258 ### Stub API (Test.StubProvider)
 259 
 260 ```apex
 261 @IsTest
 262 private class AccountServiceTest {
 263 
 264     // Stub for dependency injection
 265     private class SelectorStub implements System.StubProvider {
 266         public Object handleMethodCall(
 267             Object stubbedObject,
 268             String stubbedMethodName,
 269             Type returnType,
 270             List<Type> paramTypes,
 271             List<String> paramNames,
 272             List<Object> args
 273         ) {
 274             if (stubbedMethodName == 'getAccountById') {
 275                 return new Account(Name = 'Mocked Account');
 276             }
 277             return null;
 278         }
 279     }
 280 
 281     @IsTest
 282     static void testServiceWithMockedSelector() {
 283         // Create stub
 284         AccountSelector mockSelector = (AccountSelector) Test.createStub(
 285             AccountSelector.class,
 286             new SelectorStub()
 287         );
 288 
 289         // Inject into service
 290         AccountService service = new AccountService(mockSelector);
 291 
 292         // Test with mocked dependency
 293         Test.startTest();
 294         Account result = service.getAccount('001xx000000001');
 295         Test.stopTest();
 296 
 297         Assert.areEqual('Mocked Account', result.Name);
 298     }
 299 }
 300 ```
 301 
 302 ## Governor Limit Testing
 303 
 304 ```apex
 305 @IsTest
 306 static void testBulkOperation_StaysWithinLimits() {
 307     List<Account> accounts = TestDataFactory.createAccounts(200);
 308 
 309     Test.startTest();
 310     insert accounts;
 311     Test.stopTest();
 312 
 313     // Assert limits not exceeded
 314     System.debug('SOQL queries used: ' + Limits.getQueries());
 315     System.debug('DML statements used: ' + Limits.getDmlStatements());
 316 
 317     Assert.isTrue(Limits.getQueries() < 100,
 318         'Should stay under SOQL limit: ' + Limits.getQueries());
 319     Assert.isTrue(Limits.getDmlStatements() < 150,
 320         'Should stay under DML limit: ' + Limits.getDmlStatements());
 321 }
 322 ```
 323 
 324 ## Common Anti-Patterns to Avoid
 325 
 326 ### ❌ SeeAllData=true
 327 
 328 ```apex
 329 // ❌ BAD: Depends on org data
 330 @IsTest(SeeAllData=true)
 331 static void testBadPattern() {
 332     Account acc = [SELECT Id FROM Account LIMIT 1];
 333     // This will fail in empty orgs!
 334 }
 335 
 336 // ✅ GOOD: Creates own data
 337 @IsTest
 338 static void testGoodPattern() {
 339     Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
 340     // Works in any org
 341 }
 342 ```
 343 
 344 ### ❌ No Assertions
 345 
 346 ```apex
 347 // ❌ BAD: No assertions - test passes even if code is broken
 348 @IsTest
 349 static void testNoAssertions() {
 350     Account acc = new Account(Name = 'Test');
 351     insert acc;
 352     // Test "passes" but proves nothing
 353 }
 354 
 355 // ✅ GOOD: Meaningful assertions
 356 @IsTest
 357 static void testWithAssertions() {
 358     Account acc = new Account(Name = 'Test');
 359     insert acc;
 360     Assert.isNotNull(acc.Id, 'Account should have an Id after insert');
 361     Account inserted = [SELECT Name FROM Account WHERE Id = :acc.Id];
 362     Assert.areEqual('Test', inserted.Name, 'Name should be preserved');
 363 }
 364 ```
 365 
 366 ### ❌ Hardcoded IDs
 367 
 368 ```apex
 369 // ❌ BAD: Hardcoded IDs fail across orgs
 370 Account acc = [SELECT Id FROM Account WHERE Id = '001xx0000000001'];
 371 
 372 // ✅ GOOD: Query or create dynamically
 373 Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
 374 ```
 375 
 376 ## Test Method Template
 377 
 378 ```apex
 379 /**
 380  * @description Tests [method] with [condition] expecting [outcome]
 381  */
 382 @IsTest
 383 static void test[Method]_[Condition]_[ExpectedOutcome]() {
 384     // ═══════════════════════════════════════════════════════════════
 385     // ARRANGE - Set up test data and conditions
 386     // ═══════════════════════════════════════════════════════════════
 387     // Create test data using TestDataFactory
 388     // Set up any mocks needed
 389 
 390     // ═══════════════════════════════════════════════════════════════
 391     // ACT - Execute the code under test
 392     // ═══════════════════════════════════════════════════════════════
 393     Test.startTest();
 394     // Call the method being tested
 395     Test.stopTest();
 396 
 397     // ═══════════════════════════════════════════════════════════════
 398     // ASSERT - Verify expected outcomes
 399     // ═══════════════════════════════════════════════════════════════
 400     // Assert.areEqual(expected, actual, 'Descriptive message');
 401     // Assert.isTrue(condition, 'Descriptive message');
 402     // Assert.isNotNull(value, 'Descriptive message');
 403 }
 404 ```
 405 
 406 ---
 407 
 408 ## Test Speed Philosophy
 409 
 410 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
 411 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
 412 
 413 ### Why Test Speed Matters
 414 
 415 Fast tests enable continuous integration. Slow tests become barriers to frequent commits.
 416 
 417 ### Target Metrics
 418 
 419 | Test Type | Target Speed | Purpose |
 420 |-----------|--------------|---------|
 421 | Unit test (no DML) | < 50ms | Test pure business logic |
 422 | Unit test (mocked DML) | < 100ms | Test with stubbed database |
 423 | Integration test | < 500ms | Verify real database behavior |
 424 | Full scenario test | < 2000ms | End-to-end validation |
 425 
 426 ### Speed Strategy
 427 
 428 ```
 429 ┌─────────────────────────────────────────────────────────────┐
 430 │  INTEGRATION TESTS (Few)                                    │
 431 │  - Real DML, real triggers                                  │
 432 │  - Test happy path completely                               │
 433 │  - Slow but high confidence                                 │
 434 └─────────────────────────────────────────────────────────────┘
 435                             │
 436                             ▼
 437 ┌─────────────────────────────────────────────────────────────┐
 438 │  UNIT TESTS WITH MOCKS (Many)                               │
 439 │  - Stub database operations                                 │
 440 │  - Test edge cases, variations                              │
 441 │  - Fast, run on every save                                  │
 442 └─────────────────────────────────────────────────────────────┘
 443 ```
 444 
 445 ### Balance Reality vs Speed
 446 
 447 ```apex
 448 // INTEGRATION TEST: Full database interaction (slower, realistic)
 449 @IsTest
 450 static void testAccountCreation_Integration() {
 451     Test.startTest();
 452     Account acc = new Account(Name = 'Test');
 453     insert acc;
 454     Test.stopTest();
 455 
 456     Account queried = [SELECT Name, Status__c FROM Account WHERE Id = :acc.Id];
 457     Assert.areEqual('Active', queried.Status__c, 'Trigger should set status');
 458 }
 459 
 460 // UNIT TEST: Mocked database (faster, tests logic only)
 461 @IsTest
 462 static void testAccountRules_IsHighValue() {
 463     // No database interaction - tests pure logic
 464     Account acc = new Account(AnnualRevenue = 1500000);
 465     Assert.isTrue(AccountRules.isHighValue(acc), 'Should be high value');
 466 
 467     Account lowValue = new Account(AnnualRevenue = 500000);
 468     Assert.isFalse(AccountRules.isHighValue(lowValue), 'Should not be high value');
 469 }
 470 ```
 471 
 472 ### Techniques for Faster Tests
 473 
 474 | Technique | Benefit | Trade-off |
 475 |-----------|---------|-----------|
 476 | @TestSetup | Reuse data across methods | Small setup overhead |
 477 | Stub API | No real DML | Less realistic |
 478 | Selector mocking | Skip SOQL | Must trust Selector |
 479 | Domain class testing | Pure logic, no DB | Limited scope |
 480 | Avoid SeeAllData | Predictable data | Must create test data |
 481 
 482 ### When to Prioritize Speed vs Reality
 483 
 484 | Scenario | Priority | Approach |
 485 |----------|----------|----------|
 486 | Business logic validation | Speed | Unit test with mocks |
 487 | Trigger behavior | Reality | Integration test |
 488 | Edge case coverage | Speed | Many unit tests |
 489 | Deployment validation | Reality | RunLocalTests |
 490 | Developer feedback loop | Speed | Fast unit tests |
 491 
 492 ### Measuring Test Speed
 493 
 494 ```bash
 495 # Run tests and view timing
 496 sf apex test run --test-level RunLocalTests --target-org alias --result-format human
 497 
 498 # Check individual test timing
 499 sf apex test get --test-run-id [id] --code-coverage --result-format json | jq '.tests[] | {name: .MethodName, time: .RunTime}'
 500 ```
 501 
 502 ### Fast Test Checklist
 503 
 504 ```
 505 □ Is there a pure logic portion that can be unit tested?
 506 □ Can database operations be mocked for edge cases?
 507 □ Is @TestSetup reused across multiple test methods?
 508 □ Are tests avoiding SeeAllData=true?
 509 □ Are integration tests reserved for critical paths only?
 510 □ Can SOQL be mocked via Selector pattern?
 511 ```
