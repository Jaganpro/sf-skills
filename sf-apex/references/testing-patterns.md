<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Testing Patterns
   2 
   3 Comprehensive guide to Apex testing including exception types, test patterns, mocking, and achieving 90%+ code coverage.
   4 
   5 ---
   6 
   7 ## Table of Contents
   8 
   9 1. [Testing Fundamentals](#testing-fundamentals)
  10 2. [Common Exception Types](#common-exception-types)
  11 3. [Test Patterns](#test-patterns)
  12 4. [Test Data Factory](#test-data-factory)
  13 5. [Mocking and Stubs](#mocking-and-stubs)
  14 6. [Bulk Testing](#bulk-testing)
  15 7. [Code Coverage Strategies](#code-coverage-strategies)
  16 
  17 ---
  18 
  19 ## Testing Fundamentals
  20 
  21 ### Test Class Structure
  22 
  23 ```apex
  24 @IsTest
  25 private class AccountServiceTest {
  26 
  27     @TestSetup
  28     static void setup() {
  29         // Runs ONCE before all test methods
  30         // Create shared test data
  31         TestDataFactory.createAccounts(10);
  32     }
  33 
  34     @IsTest
  35     static void testPositiveCase() {
  36         // Arrange: Set up test data
  37         Account acc = new Account(Name = 'Test', Industry = 'Technology');
  38 
  39         // Act: Execute code under test
  40         Test.startTest();
  41         insert acc;
  42         Test.stopTest();
  43 
  44         // Assert: Verify results
  45         Account inserted = [SELECT Id, Industry FROM Account WHERE Id = :acc.Id];
  46         Assert.areEqual('Technology', inserted.Industry, 'Industry should be set');
  47     }
  48 
  49     @IsTest
  50     static void testNegativeCase() {
  51         // Test error conditions
  52         try {
  53             insert new Account(); // Missing required Name
  54             Assert.fail('Expected DmlException was not thrown');
  55         } catch (DmlException e) {
  56             Assert.isTrue(e.getMessage().contains('REQUIRED_FIELD_MISSING'));
  57         }
  58     }
  59 
  60     @IsTest
  61     static void testBulkCase() {
  62         // Test with 251+ records
  63         List<Account> accounts = new List<Account>();
  64         for (Integer i = 0; i < 251; i++) {
  65             accounts.add(new Account(Name = 'Bulk ' + i));
  66         }
  67 
  68         Test.startTest();
  69         insert accounts;
  70         Test.stopTest();
  71 
  72         Assert.areEqual(251, [SELECT COUNT() FROM Account WHERE Name LIKE 'Bulk%']);
  73     }
  74 }
  75 ```
  76 
  77 ---
  78 
  79 ### @TestSetup vs Test Methods
  80 
  81 | Feature | @TestSetup | Test Methods |
  82 |---------|------------|--------------|
  83 | **Runs** | Once before all tests | Once per test |
  84 | **Data Isolation** | Shared across tests (read-only view) | Isolated per test |
  85 | **Performance** | Faster (reuses data) | Slower (recreates each time) |
  86 | **When to Use** | Common baseline data | Test-specific scenarios |
  87 
  88 **Example**:
  89 ```apex
  90 @TestSetup
  91 static void setup() {
  92     // Common data for all tests
  93     insert new Account(Name = 'Shared Account');
  94 }
  95 
  96 @IsTest
  97 static void test1() {
  98     // Can query the Shared Account
  99     Account acc = [SELECT Id FROM Account WHERE Name = 'Shared Account'];
 100     acc.Industry = 'Tech';
 101     update acc;  // Only visible in this test
 102 }
 103 
 104 @IsTest
 105 static void test2() {
 106     // Shared Account still has Industry = null (data rollback between tests)
 107     Account acc = [SELECT Id, Industry FROM Account WHERE Name = 'Shared Account'];
 108     Assert.isNull(acc.Industry);
 109 }
 110 ```
 111 
 112 ---
 113 
 114 ### Test.startTest() and Test.stopTest()
 115 
 116 **Purpose**: Reset governor limits and execute async code.
 117 
 118 ```apex
 119 @IsTest
 120 static void testAsyncOperation() {
 121     Account acc = new Account(Name = 'Test');
 122     insert acc;
 123 
 124     // Limits reset here
 125     Test.startTest();
 126 
 127     // Enqueue async job
 128     System.enqueueJob(new AccountProcessor(acc.Id));
 129 
 130     // Async job executes synchronously here
 131     Test.stopTest();
 132 
 133     // Verify async results
 134     Account updated = [SELECT Id, Description FROM Account WHERE Id = :acc.Id];
 135     Assert.isNotNull(updated.Description);
 136 }
 137 ```
 138 
 139 **Key Points**:
 140 - Governor limits reset at `Test.startTest()`
 141 - Async code (@future, Queueable, Batch) executes at `Test.stopTest()`
 142 - Only one `startTest/stopTest` block per test method
 143 
 144 ---
 145 
 146 ## Common Exception Types
 147 
 148 When writing test classes, use these specific exception types to validate error handling.
 149 
 150 ### Exception Type Reference
 151 
 152 | Exception Type | When to Use | Example |
 153 |----------------|-------------|---------|
 154 | `DmlException` | Insert/update/delete failures | `Assert.isTrue(e.getMessage().contains('FIELD_CUSTOM_VALIDATION'))` |
 155 | `QueryException` | SOQL query failures | Malformed query, no rows for assignment |
 156 | `NullPointerException` | Null reference access | Accessing field on null object |
 157 | `ListException` | List operation failures | Index out of bounds |
 158 | `MathException` | Mathematical errors | Division by zero |
 159 | `TypeException` | Type conversion failures | Invalid type casting |
 160 | `LimitException` | Governor limit exceeded | Too many SOQL queries, DML statements |
 161 | `CalloutException` | HTTP callout failures | Timeout, invalid endpoint |
 162 | `JSONException` | JSON parsing failures | Malformed JSON |
 163 | `InvalidParameterValueException` | Invalid method parameters | Bad input values |
 164 
 165 ---
 166 
 167 ### Testing DmlException
 168 
 169 ```apex
 170 @IsTest
 171 static void testRequiredFieldMissing() {
 172     try {
 173         insert new Account(); // Missing Name
 174         Assert.fail('Expected DmlException was not thrown');
 175     } catch (DmlException e) {
 176         Assert.isTrue(
 177             e.getMessage().contains('REQUIRED_FIELD_MISSING'),
 178             'Expected REQUIRED_FIELD_MISSING but got: ' + e.getMessage()
 179         );
 180     }
 181 }
 182 
 183 @IsTest
 184 static void testDuplicateValue() {
 185     Account acc1 = new Account(Name = 'Test', Unique_Field__c = 'ABC123');
 186     insert acc1;
 187 
 188     try {
 189         Account acc2 = new Account(Name = 'Test2', Unique_Field__c = 'ABC123');
 190         insert acc2; // Violates unique constraint
 191         Assert.fail('Expected DmlException');
 192     } catch (DmlException e) {
 193         Assert.isTrue(e.getMessage().contains('DUPLICATE_VALUE'));
 194     }
 195 }
 196 
 197 @IsTest
 198 static void testCustomValidationRule() {
 199     Account acc = new Account(Name = 'Test', AnnualRevenue = -100);
 200 
 201     try {
 202         insert acc; // Validation rule: Revenue must be > 0
 203         Assert.fail('Expected DmlException');
 204     } catch (DmlException e) {
 205         Assert.isTrue(e.getMessage().contains('FIELD_CUSTOM_VALIDATION_EXCEPTION'));
 206     }
 207 }
 208 ```
 209 
 210 ---
 211 
 212 ### Testing QueryException
 213 
 214 ```apex
 215 @IsTest
 216 static void testNoRowsForAssignment() {
 217     try {
 218         // Query expects exactly 1 row but finds 0
 219         Account acc = [SELECT Id FROM Account WHERE Name = 'Nonexistent'];
 220         Assert.fail('Expected QueryException');
 221     } catch (QueryException e) {
 222         Assert.isTrue(e.getMessage().contains('List has no rows for assignment'));
 223     }
 224 }
 225 
 226 @IsTest
 227 static void testTooManyRows() {
 228     TestDataFactory.createAccounts(5); // All with same Name
 229 
 230     try {
 231         // Query expects 1 row but finds 5
 232         Account acc = [SELECT Id FROM Account WHERE Name LIKE 'Test%'];
 233         Assert.fail('Expected QueryException');
 234     } catch (QueryException e) {
 235         Assert.isTrue(e.getMessage().contains('List has more than 1 row'));
 236     }
 237 }
 238 ```
 239 
 240 ---
 241 
 242 ### Testing NullPointerException
 243 
 244 ```apex
 245 @IsTest
 246 static void testNullReferenceAccess() {
 247     Account acc = null;
 248 
 249     try {
 250         String name = acc.Name; // NullPointerException
 251         Assert.fail('Expected NullPointerException');
 252     } catch (NullPointerException e) {
 253         Assert.isNotNull(e.getMessage());
 254     }
 255 }
 256 
 257 @IsTest
 258 static void testSafeNavigationOperator() {
 259     Account acc = null;
 260 
 261     // No exception - returns null
 262     String name = acc?.Name;
 263     Assert.isNull(name, 'Safe navigation should return null');
 264 }
 265 ```
 266 
 267 ---
 268 
 269 ### Testing LimitException
 270 
 271 ```apex
 272 @IsTest
 273 static void testSoqlLimitExceeded() {
 274     // Artificially trigger SOQL limit (for demonstration - don't do this in real code!)
 275     try {
 276         for (Integer i = 0; i < 101; i++) {
 277             List<Account> accounts = [SELECT Id FROM Account LIMIT 1];
 278         }
 279         Assert.fail('Expected LimitException');
 280     } catch (System.LimitException e) {
 281         Assert.isTrue(e.getMessage().contains('Too many SOQL queries'));
 282     }
 283 }
 284 ```
 285 
 286 **Note**: In real tests, you should NEVER hit limits - tests should validate limit-safe code.
 287 
 288 ---
 289 
 290 ### Testing CalloutException
 291 
 292 ```apex
 293 @IsTest
 294 static void testCalloutTimeout() {
 295     // Set mock callout
 296     Test.setMock(HttpCalloutMock.class, new TimeoutMock());
 297 
 298     Test.startTest();
 299     try {
 300         CalloutService.sendData('test');
 301         Assert.fail('Expected CalloutException');
 302     } catch (CalloutException e) {
 303         Assert.isTrue(e.getMessage().contains('Read timed out'));
 304     }
 305     Test.stopTest();
 306 }
 307 
 308 // Mock class
 309 private class TimeoutMock implements HttpCalloutMock {
 310     public HttpResponse respond(HttpRequest req) {
 311         throw new CalloutException('Read timed out');
 312     }
 313 }
 314 ```
 315 
 316 ---
 317 
 318 ## Test Patterns
 319 
 320 ### Pattern 1: Positive, Negative, Bulk (PNB)
 321 
 322 **Every feature needs 3 tests:**
 323 
 324 ```apex
 325 // 1. POSITIVE: Happy path
 326 @IsTest
 327 static void testCreateAccountSuccess() {
 328     Account acc = new Account(Name = 'Test', Industry = 'Tech');
 329 
 330     Test.startTest();
 331     insert acc;
 332     Test.stopTest();
 333 
 334     Account inserted = [SELECT Id, Industry FROM Account WHERE Id = :acc.Id];
 335     Assert.areEqual('Tech', inserted.Industry);
 336 }
 337 
 338 // 2. NEGATIVE: Error handling
 339 @IsTest
 340 static void testCreateAccountMissingName() {
 341     try {
 342         insert new Account();
 343         Assert.fail('Expected exception');
 344     } catch (DmlException e) {
 345         Assert.isTrue(e.getMessage().contains('REQUIRED_FIELD_MISSING'));
 346     }
 347 }
 348 
 349 // 3. BULK: 251+ records
 350 @IsTest
 351 static void testCreateAccountsBulk() {
 352     List<Account> accounts = new List<Account>();
 353     for (Integer i = 0; i < 251; i++) {
 354         accounts.add(new Account(Name = 'Bulk ' + i));
 355     }
 356 
 357     Test.startTest();
 358     insert accounts;
 359     Test.stopTest();
 360 
 361     Assert.areEqual(251, [SELECT COUNT() FROM Account]);
 362 }
 363 ```
 364 
 365 ---
 366 
 367 ### Pattern 2: System.runAs() for Permission Testing
 368 
 369 ```apex
 370 @IsTest
 371 static void testUserCannotAccessRestrictedField() {
 372     // Create user without field permission
 373     User restrictedUser = TestDataFactory.createStandardUser();
 374 
 375     Account acc = new Account(Name = 'Test', Restricted_Field__c = 'Secret');
 376     insert acc;
 377 
 378     System.runAs(restrictedUser) {
 379         try {
 380             List<Account> accounts = [
 381                 SELECT Id, Restricted_Field__c
 382                 FROM Account
 383                 WHERE Id = :acc.Id
 384                 WITH USER_MODE
 385             ];
 386             Assert.fail('Expected QueryException due to FLS');
 387         } catch (QueryException e) {
 388             Assert.isTrue(e.getMessage().contains('Insufficient privileges'));
 389         }
 390     }
 391 }
 392 ```
 393 
 394 ---
 395 
 396 ### Pattern 3: Database Methods for Partial Success
 397 
 398 ```apex
 399 @IsTest
 400 static void testPartialInsertSuccess() {
 401     List<Account> accounts = new List<Account>{
 402         new Account(Name = 'Valid Account'),
 403         new Account(), // Invalid - missing Name
 404         new Account(Name = 'Another Valid')
 405     };
 406 
 407     Test.startTest();
 408     Database.SaveResult[] results = Database.insert(accounts, false); // allOrNone = false
 409     Test.stopTest();
 410 
 411     // Verify results
 412     Integer successCount = 0;
 413     Integer failureCount = 0;
 414 
 415     for (Database.SaveResult result : results) {
 416         if (result.isSuccess()) {
 417             successCount++;
 418         } else {
 419             failureCount++;
 420             for (Database.Error err : result.getErrors()) {
 421                 Assert.areEqual(StatusCode.REQUIRED_FIELD_MISSING, err.getStatusCode());
 422             }
 423         }
 424     }
 425 
 426     Assert.areEqual(2, successCount, 'Two accounts should succeed');
 427     Assert.areEqual(1, failureCount, 'One account should fail');
 428 }
 429 ```
 430 
 431 ---
 432 
 433 ### Pattern 4: Testing Async Code
 434 
 435 **Testing @future:**
 436 ```apex
 437 @IsTest
 438 static void testFutureMethod() {
 439     Account acc = new Account(Name = 'Test');
 440     insert acc;
 441 
 442     Test.startTest();
 443     AccountService.updateAsync(acc.Id); // @future method
 444     Test.stopTest(); // Future executes here
 445 
 446     Account updated = [SELECT Id, Description FROM Account WHERE Id = :acc.Id];
 447     Assert.areEqual('Updated by future', updated.Description);
 448 }
 449 ```
 450 
 451 **Testing Queueable:**
 452 ```apex
 453 @IsTest
 454 static void testQueueable() {
 455     Account acc = new Account(Name = 'Test');
 456     insert acc;
 457 
 458     Test.startTest();
 459     System.enqueueJob(new AccountProcessor(acc.Id));
 460     Test.stopTest(); // Queueable executes here
 461 
 462     Account updated = [SELECT Id, Description FROM Account WHERE Id = :acc.Id];
 463     Assert.areEqual('Processed', updated.Description);
 464 }
 465 ```
 466 
 467 **Testing Batch:**
 468 ```apex
 469 @IsTest
 470 static void testBatch() {
 471     TestDataFactory.createAccounts(200);
 472 
 473     Test.startTest();
 474     Database.executeBatch(new AccountBatchProcessor(), 100);
 475     Test.stopTest(); // Batch executes here
 476 
 477     Integer processed = [SELECT COUNT() FROM Account WHERE Description = 'Processed'];
 478     Assert.areEqual(200, processed);
 479 }
 480 ```
 481 
 482 **Testing Schedulable:**
 483 ```apex
 484 @IsTest
 485 static void testSchedulable() {
 486     String cronExp = '0 0 0 * * ?'; // Daily at midnight
 487 
 488     Test.startTest();
 489     String jobId = System.schedule('Test Job', cronExp, new AccountScheduler());
 490     Test.stopTest();
 491 
 492     // Verify job was scheduled
 493     CronTrigger ct = [SELECT Id, CronExpression FROM CronTrigger WHERE Id = :jobId];
 494     Assert.areEqual(cronExp, ct.CronExpression);
 495 }
 496 ```
 497 
 498 ---
 499 
 500 ## Test Data Factory
 501 
 502 ### Basic Factory Pattern
 503 
 504 ```apex
 505 @IsTest
 506 public class TestDataFactory {
 507 
 508     public static List<Account> createAccounts(Integer count) {
 509         return createAccounts(count, true);
 510     }
 511 
 512     public static List<Account> createAccounts(Integer count, Boolean doInsert) {
 513         List<Account> accounts = new List<Account>();
 514 
 515         for (Integer i = 0; i < count; i++) {
 516             accounts.add(new Account(
 517                 Name = 'Test Account ' + i,
 518                 Industry = 'Technology',
 519                 AnnualRevenue = 1000000
 520             ));
 521         }
 522 
 523         if (doInsert) {
 524             insert accounts;
 525         }
 526 
 527         return accounts;
 528     }
 529 
 530     public static List<Contact> createContacts(Integer count, Id accountId) {
 531         return createContacts(count, accountId, true);
 532     }
 533 
 534     public static List<Contact> createContacts(Integer count, Id accountId, Boolean doInsert) {
 535         List<Contact> contacts = new List<Contact>();
 536 
 537         for (Integer i = 0; i < count; i++) {
 538             contacts.add(new Contact(
 539                 FirstName = 'Test',
 540                 LastName = 'Contact ' + i,
 541                 AccountId = accountId,
 542                 Email = 'test' + i + '@example.com'
 543             ));
 544         }
 545 
 546         if (doInsert) {
 547             insert contacts;
 548         }
 549 
 550         return contacts;
 551     }
 552 
 553     public static User createStandardUser() {
 554         Profile standardProfile = [SELECT Id FROM Profile WHERE Name = 'Standard User' LIMIT 1];
 555 
 556         User u = new User(
 557             FirstName = 'Test',
 558             LastName = 'User',
 559             Email = 'testuser@example.com',
 560             Username = 'testuser' + System.currentTimeMillis() + '@example.com',
 561             Alias = 'tuser',
 562             TimeZoneSidKey = 'America/Los_Angeles',
 563             LocaleSidKey = 'en_US',
 564             EmailEncodingKey = 'UTF-8',
 565             LanguageLocaleKey = 'en_US',
 566             ProfileId = standardProfile.Id
 567         );
 568 
 569         insert u;
 570         return u;
 571     }
 572 }
 573 ```
 574 
 575 **Usage:**
 576 ```apex
 577 @TestSetup
 578 static void setup() {
 579     // Create 251 accounts
 580     TestDataFactory.createAccounts(251);
 581 
 582     // Create account with 10 contacts
 583     Account acc = TestDataFactory.createAccounts(1)[0];
 584     TestDataFactory.createContacts(10, acc.Id);
 585 }
 586 ```
 587 
 588 ---
 589 
 590 ### Advanced Factory with Builder Pattern
 591 
 592 ```apex
 593 @IsTest
 594 public class AccountBuilder {
 595 
 596     private Account record;
 597 
 598     public AccountBuilder() {
 599         record = new Account(
 600             Name = 'Default Account',
 601             Industry = 'Technology'
 602         );
 603     }
 604 
 605     public AccountBuilder withName(String name) {
 606         record.Name = name;
 607         return this;
 608     }
 609 
 610     public AccountBuilder withIndustry(String industry) {
 611         record.Industry = industry;
 612         return this;
 613     }
 614 
 615     public AccountBuilder withRevenue(Decimal revenue) {
 616         record.AnnualRevenue = revenue;
 617         return this;
 618     }
 619 
 620     public Account build() {
 621         return record;
 622     }
 623 
 624     public Account buildAndInsert() {
 625         insert record;
 626         return record;
 627     }
 628 }
 629 ```
 630 
 631 **Usage:**
 632 ```apex
 633 @IsTest
 634 static void testWithBuilder() {
 635     Account acc = new AccountBuilder()
 636         .withName('Custom Account')
 637         .withIndustry('Finance')
 638         .withRevenue(5000000)
 639         .buildAndInsert();
 640 
 641     Assert.areEqual('Finance', acc.Industry);
 642 }
 643 ```
 644 
 645 ---
 646 
 647 ## Mocking and Stubs
 648 
 649 ### HTTP Callout Mocking
 650 
 651 ```apex
 652 @IsTest
 653 public class ExternalServiceMock implements HttpCalloutMock {
 654 
 655     public HttpResponse respond(HttpRequest req) {
 656         // Verify request
 657         Assert.areEqual('POST', req.getMethod());
 658         Assert.areEqual('https://api.example.com/accounts', req.getEndpoint());
 659 
 660         // Create mock response
 661         HttpResponse res = new HttpResponse();
 662         res.setHeader('Content-Type', 'application/json');
 663         res.setBody('{"status": "success", "id": "12345"}');
 664         res.setStatusCode(200);
 665 
 666         return res;
 667     }
 668 }
 669 ```
 670 
 671 **Test:**
 672 ```apex
 673 @IsTest
 674 static void testExternalCallout() {
 675     Test.setMock(HttpCalloutMock.class, new ExternalServiceMock());
 676 
 677     Test.startTest();
 678     String result = CalloutService.sendData('test data');
 679     Test.stopTest();
 680 
 681     Assert.areEqual('12345', result);
 682 }
 683 ```
 684 
 685 ---
 686 
 687 ### Multi-Request Callout Mock
 688 
 689 ```apex
 690 @IsTest
 691 public class MultiCalloutMock implements HttpCalloutMock {
 692 
 693     public HttpResponse respond(HttpRequest req) {
 694         HttpResponse res = new HttpResponse();
 695         res.setHeader('Content-Type', 'application/json');
 696 
 697         // Different responses based on endpoint
 698         if (req.getEndpoint().endsWith('/accounts')) {
 699             res.setBody('{"accounts": [{"id": "1"}]}');
 700             res.setStatusCode(200);
 701         } else if (req.getEndpoint().endsWith('/contacts')) {
 702             res.setBody('{"contacts": [{"id": "2"}]}');
 703             res.setStatusCode(200);
 704         } else {
 705             res.setStatusCode(404);
 706         }
 707 
 708         return res;
 709     }
 710 }
 711 ```
 712 
 713 ---
 714 
 715 ### Stub API (Test Doubles)
 716 
 717 ```apex
 718 @IsTest
 719 public class AccountSelectorStub implements IAccountSelector {
 720 
 721     private List<Account> stubbedAccounts;
 722 
 723     public AccountSelectorStub(List<Account> accounts) {
 724         this.stubbedAccounts = accounts;
 725     }
 726 
 727     public List<Account> selectById(Set<Id> accountIds) {
 728         // Return stubbed data instead of querying
 729         return stubbedAccounts;
 730     }
 731 }
 732 ```
 733 
 734 **Test with stub:**
 735 ```apex
 736 @IsTest
 737 static void testWithStub() {
 738     // Create stub data (no DML needed!)
 739     List<Account> stubbedAccounts = new List<Account>{
 740         new Account(Id = TestUtility.getFakeId(Account.SObjectType), Name = 'Stub Account')
 741     };
 742 
 743     IAccountSelector selector = new AccountSelectorStub(stubbedAccounts);
 744 
 745     // Inject stub into service
 746     AccountService service = new AccountService(selector);
 747 
 748     Test.startTest();
 749     List<Account> results = service.getAccounts();
 750     Test.stopTest();
 751 
 752     Assert.areEqual(1, results.size());
 753     Assert.areEqual('Stub Account', results[0].Name);
 754 }
 755 ```
 756 
 757 ---
 758 
 759 ## Bulk Testing
 760 
 761 ### The 251 Record Test
 762 
 763 ```apex
 764 @IsTest
 765 static void testBulkTriggerExecution() {
 766     List<Account> accounts = new List<Account>();
 767 
 768     for (Integer i = 0; i < 251; i++) {
 769         accounts.add(new Account(
 770             Name = 'Bulk Test ' + i,
 771             Industry = 'Technology'
 772         ));
 773     }
 774 
 775     Test.startTest();
 776 
 777     insert accounts;
 778 
 779     Test.stopTest();
 780 
 781     // Verify trigger logic executed for all 251
 782     List<Account> inserted = [SELECT Id, Description FROM Account WHERE Name LIKE 'Bulk Test%'];
 783     Assert.areEqual(251, inserted.size());
 784 
 785     for (Account acc : inserted) {
 786         Assert.isNotNull(acc.Description, 'Description should be set by trigger');
 787     }
 788 }
 789 ```
 790 
 791 ---
 792 
 793 ### Testing Governor Limits
 794 
 795 ```apex
 796 @IsTest
 797 static void testDoesNotHitSoqlLimit() {
 798     TestDataFactory.createAccounts(251);
 799 
 800     Integer queriesBefore = Limits.getQueries();
 801 
 802     Test.startTest();
 803     AccountService.processAllAccounts();
 804     Test.stopTest();
 805 
 806     Integer queriesAfter = Limits.getQueries();
 807     Integer queriesUsed = queriesAfter - queriesBefore;
 808 
 809     Assert.isTrue(queriesUsed <= 5, 'Should use no more than 5 SOQL queries, used: ' + queriesUsed);
 810 }
 811 ```
 812 
 813 ---
 814 
 815 ## Code Coverage Strategies
 816 
 817 ### Achieving 90%+ Coverage
 818 
 819 **1. Test all branches (if/else):**
 820 ```apex
 821 // Code
 822 public static String getStatus(Account acc) {
 823     if (acc.AnnualRevenue > 1000000) {
 824         return 'Enterprise';
 825     } else {
 826         return 'SMB';
 827     }
 828 }
 829 
 830 // Test BOTH branches
 831 @IsTest
 832 static void testEnterpriseStatus() {
 833     Account acc = new Account(Name = 'Test', AnnualRevenue = 2000000);
 834     Assert.areEqual('Enterprise', AccountService.getStatus(acc));
 835 }
 836 
 837 @IsTest
 838 static void testSmbStatus() {
 839     Account acc = new Account(Name = 'Test', AnnualRevenue = 500000);
 840     Assert.areEqual('SMB', AccountService.getStatus(acc));
 841 }
 842 ```
 843 
 844 **2. Test all catch blocks:**
 845 ```apex
 846 // Code
 847 try {
 848     insert accounts;
 849 } catch (DmlException e) {
 850     // Handle DML error
 851     logError(e);
 852 }
 853 
 854 // Test
 855 @IsTest
 856 static void testCatchBlock() {
 857     List<Account> invalid = new List<Account>{ new Account() }; // Missing Name
 858 
 859     try {
 860         insert invalid;
 861     } catch (DmlException e) {
 862         // Catch block is now covered
 863     }
 864 }
 865 ```
 866 
 867 **3. Test all methods:**
 868 ```apex
 869 // Every public/global method needs at least one test
 870 @IsTest
 871 static void testEveryMethod() {
 872     AccountService.method1();
 873     AccountService.method2();
 874     AccountService.method3();
 875     // etc.
 876 }
 877 ```
 878 
 879 ---
 880 
 881 ### Identifying Uncovered Code
 882 
 883 **Developer Console:**
 884 1. Open class
 885 2. Click Tests → New Run
 886 3. Select test class
 887 4. View coverage % and red highlights
 888 
 889 **VS Code:**
 890 1. Run tests: `Ctrl+Shift+P` → "SFDX: Run Apex Tests"
 891 2. View coverage in Problems panel
 892 
 893 **CLI:**
 894 ```bash
 895 sf apex run test --code-coverage --result-format human --test-level RunLocalTests
 896 ```
 897 
 898 ---
 899 
 900 ## Reference
 901 
 902 **Full Documentation**: See `references/` folder for comprehensive guides:
 903 - `testing-guide.md` - Complete testing reference
 904 - `best-practices.md` - Test best practices
 905 - `code-review-checklist.md` - Testing scoring criteria
 906 
 907 **Back to Main**: [SKILL.md](../SKILL.md)
