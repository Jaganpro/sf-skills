<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Testing Guide
   2 
   3 ## Testing Fundamentals
   4 
   5 ### Coverage Requirements
   6 - **Minimum**: 75% for deployment
   7 - **Recommended**: 90%+ for quality
   8 - **Best Practice**: Maintain buffer above 75%
   9 
  10 ### Test Class Structure
  11 
  12 ```apex
  13 @isTest
  14 private class AccountServiceTest {
  15 
  16     @TestSetup
  17     static void setup() {
  18         // Create test data once, available to all test methods
  19         TestDataFactory.createAccounts(10);
  20     }
  21 
  22     @isTest
  23     static void testPositiveScenario() {
  24         // Arrange
  25         Account acc = [SELECT Id FROM Account LIMIT 1];
  26 
  27         // Act
  28         Test.startTest();
  29         String result = AccountService.processAccount(acc.Id);
  30         Test.stopTest();
  31 
  32         // Assert
  33         Assert.areEqual('Success', result, 'Should return success');
  34     }
  35 
  36     @isTest
  37     static void testNegativeScenario() {
  38         // Test error handling
  39         Test.startTest();
  40         try {
  41             AccountService.processAccount(null);
  42             Assert.fail('Should have thrown exception');
  43         } catch (IllegalArgumentException e) {
  44             Assert.isTrue(e.getMessage().contains('null'), 'Should mention null');
  45         }
  46         Test.stopTest();
  47     }
  48 
  49     @isTest
  50     static void testBulkScenario() {
  51         // Test with 251+ records (spans two trigger batches)
  52         List<Account> accounts = TestDataFactory.createAccounts(251);
  53 
  54         Test.startTest();
  55         List<String> results = AccountService.processAccounts(accounts);
  56         Test.stopTest();
  57 
  58         Assert.areEqual(251, results.size(), 'Should process all records');
  59     }
  60 }
  61 ```
  62 
  63 ---
  64 
  65 ## Assert Class (Winter '23+)
  66 
  67 ### Preferred Assert Methods
  68 
  69 ```apex
  70 // Equality
  71 Assert.areEqual(expected, actual, 'Optional message');
  72 Assert.areNotEqual(unexpected, actual);
  73 
  74 // Boolean
  75 Assert.isTrue(condition, 'Should be true');
  76 Assert.isFalse(condition, 'Should be false');
  77 
  78 // Null
  79 Assert.isNull(value, 'Should be null');
  80 Assert.isNotNull(value, 'Should not be null');
  81 
  82 // Instance type
  83 Assert.isInstanceOfType(obj, Account.class, 'Should be Account');
  84 
  85 // Explicit failure
  86 Assert.fail('This should not be reached');
  87 ```
  88 
  89 ### Testing Exceptions
  90 
  91 ```apex
  92 @isTest
  93 static void testExceptionThrown() {
  94     Test.startTest();
  95     try {
  96         MyService.riskyOperation();
  97         Assert.fail('Expected MyCustomException');
  98     } catch (MyCustomException e) {
  99         Assert.isTrue(e.getMessage().contains('expected text'));
 100     }
 101     Test.stopTest();
 102 }
 103 ```
 104 
 105 ---
 106 
 107 ## Test Data Factory Pattern
 108 
 109 ### Factory Class
 110 
 111 ```apex
 112 @isTest
 113 public class TestDataFactory {
 114 
 115     public static List<Account> createAccounts(Integer count) {
 116         return createAccounts(count, true);
 117     }
 118 
 119     public static List<Account> createAccounts(Integer count, Boolean doInsert) {
 120         List<Account> accounts = new List<Account>();
 121         for (Integer i = 0; i < count; i++) {
 122             accounts.add(new Account(
 123                 Name = 'Test Account ' + i,
 124                 Industry = 'Technology',
 125                 BillingCity = 'San Francisco'
 126             ));
 127         }
 128         if (doInsert) {
 129             insert accounts;
 130         }
 131         return accounts;
 132     }
 133 
 134     public static List<Contact> createContacts(Integer count, Id accountId) {
 135         List<Contact> contacts = new List<Contact>();
 136         for (Integer i = 0; i < count; i++) {
 137             contacts.add(new Contact(
 138                 FirstName = 'Test',
 139                 LastName = 'Contact ' + i,
 140                 Email = 'test' + i + '@example.com',
 141                 AccountId = accountId
 142             ));
 143         }
 144         insert contacts;
 145         return contacts;
 146     }
 147 
 148     public static User createUser(String profileName) {
 149         Profile p = [SELECT Id FROM Profile WHERE Name = :profileName LIMIT 1];
 150         String uniqueKey = String.valueOf(DateTime.now().getTime());
 151 
 152         User u = new User(
 153             Alias = 'test' + uniqueKey.right(4),
 154             Email = 'test' + uniqueKey + '@example.com',
 155             EmailEncodingKey = 'UTF-8',
 156             LastName = 'Test',
 157             LanguageLocaleKey = 'en_US',
 158             LocaleSidKey = 'en_US',
 159             ProfileId = p.Id,
 160             TimeZoneSidKey = 'America/Los_Angeles',
 161             Username = 'test' + uniqueKey + '@example.com.test'
 162         );
 163         insert u;
 164         return u;
 165     }
 166 }
 167 ```
 168 
 169 ### Builder Pattern (Complex Objects)
 170 
 171 ```apex
 172 @isTest
 173 public class AccountBuilder {
 174     private Account record;
 175 
 176     public AccountBuilder() {
 177         this.record = new Account(
 178             Name = 'Default Account',
 179             Industry = 'Other'
 180         );
 181     }
 182 
 183     public AccountBuilder withName(String name) {
 184         this.record.Name = name;
 185         return this;
 186     }
 187 
 188     public AccountBuilder withIndustry(String industry) {
 189         this.record.Industry = industry;
 190         return this;
 191     }
 192 
 193     public AccountBuilder withBillingAddress(String city, String state) {
 194         this.record.BillingCity = city;
 195         this.record.BillingState = state;
 196         return this;
 197     }
 198 
 199     public Account build() {
 200         return this.record;
 201     }
 202 
 203     public Account buildAndInsert() {
 204         insert this.record;
 205         return this.record;
 206     }
 207 }
 208 
 209 // Usage
 210 Account acc = new AccountBuilder()
 211     .withName('Acme Corp')
 212     .withIndustry('Technology')
 213     .withBillingAddress('San Francisco', 'CA')
 214     .buildAndInsert();
 215 ```
 216 
 217 ---
 218 
 219 ## @TestSetup
 220 
 221 ### Benefits
 222 - Runs once per test class
 223 - Data available to all test methods
 224 - Rolled back after each test method
 225 
 226 ```apex
 227 @TestSetup
 228 static void setup() {
 229     // Create accounts
 230     List<Account> accounts = TestDataFactory.createAccounts(5);
 231 
 232     // Create contacts for first account
 233     TestDataFactory.createContacts(10, accounts[0].Id);
 234 
 235     // Create custom settings
 236     insert new MySettings__c(SetupOwnerId = UserInfo.getOrganizationId());
 237 }
 238 ```
 239 
 240 ### Accessing TestSetup Data
 241 
 242 ```apex
 243 @isTest
 244 static void testMethod1() {
 245     // Query the data created in @TestSetup
 246     List<Account> accounts = [SELECT Id, Name FROM Account];
 247     Assert.areEqual(5, accounts.size());
 248 }
 249 ```
 250 
 251 ---
 252 
 253 ## Testing Async Code
 254 
 255 ### Test.startTest() / Test.stopTest()
 256 
 257 ```apex
 258 @isTest
 259 static void testQueueable() {
 260     Account acc = TestDataFactory.createAccounts(1)[0];
 261 
 262     Test.startTest();
 263     System.enqueueJob(new MyQueueable(acc.Id));
 264     Test.stopTest();  // Forces async to complete
 265 
 266     // Assert results
 267     Account updated = [SELECT Status__c FROM Account WHERE Id = :acc.Id];
 268     Assert.areEqual('Processed', updated.Status__c);
 269 }
 270 
 271 @isTest
 272 static void testFuture() {
 273     Test.startTest();
 274     MyService.asyncMethod();  // @future method
 275     Test.stopTest();
 276 
 277     // Assert results after async completes
 278 }
 279 
 280 @isTest
 281 static void testBatch() {
 282     Test.startTest();
 283     Database.executeBatch(new MyBatch(), 200);
 284     Test.stopTest();
 285 
 286     // Assert batch results
 287 }
 288 ```
 289 
 290 ---
 291 
 292 ## Mocking HTTP Callouts
 293 
 294 ### HttpCalloutMock Implementation
 295 
 296 ```apex
 297 @isTest
 298 public class MockHttpResponse implements HttpCalloutMock {
 299     private Integer statusCode;
 300     private String body;
 301 
 302     public MockHttpResponse(Integer statusCode, String body) {
 303         this.statusCode = statusCode;
 304         this.body = body;
 305     }
 306 
 307     public HTTPResponse respond(HTTPRequest req) {
 308         HttpResponse res = new HttpResponse();
 309         res.setStatusCode(this.statusCode);
 310         res.setBody(this.body);
 311         return res;
 312     }
 313 }
 314 
 315 // Usage
 316 @isTest
 317 static void testCallout() {
 318     Test.setMock(HttpCalloutMock.class, new MockHttpResponse(200, '{"success": true}'));
 319 
 320     Test.startTest();
 321     String result = MyCalloutService.makeCallout();
 322     Test.stopTest();
 323 
 324     Assert.areEqual('success', result);
 325 }
 326 ```
 327 
 328 ### Multi-Response Mock
 329 
 330 ```apex
 331 public class MultiMockHttpResponse implements HttpCalloutMock {
 332     private Map<String, HttpResponse> responses = new Map<String, HttpResponse>();
 333 
 334     public void addResponse(String endpoint, Integer statusCode, String body) {
 335         HttpResponse res = new HttpResponse();
 336         res.setStatusCode(statusCode);
 337         res.setBody(body);
 338         responses.put(endpoint, res);
 339     }
 340 
 341     public HTTPResponse respond(HTTPRequest req) {
 342         String endpoint = req.getEndpoint();
 343         if (responses.containsKey(endpoint)) {
 344             return responses.get(endpoint);
 345         }
 346         throw new CalloutException('No mock for: ' + endpoint);
 347     }
 348 }
 349 ```
 350 
 351 ---
 352 
 353 ## Dependency Injection for Testing
 354 
 355 ### Factory Pattern
 356 
 357 ```apex
 358 // Production code
 359 public virtual class Factory {
 360     private static Factory instance;
 361 
 362     public static Factory getInstance() {
 363         if (instance == null) {
 364             instance = new Factory();
 365         }
 366         return instance;
 367     }
 368 
 369     @TestVisible
 370     private static void setInstance(Factory mockFactory) {
 371         instance = mockFactory;
 372     }
 373 
 374     public virtual AccountService getAccountService() {
 375         return new AccountService();
 376     }
 377 }
 378 
 379 // Test
 380 @isTest
 381 static void testWithMock() {
 382     Factory.setInstance(new MockFactory());
 383 
 384     Test.startTest();
 385     // Code uses MockFactory.getAccountService() which returns mock
 386     Test.stopTest();
 387 }
 388 
 389 private class MockFactory extends Factory {
 390     public override AccountService getAccountService() {
 391         return new MockAccountService();
 392     }
 393 }
 394 ```
 395 
 396 ---
 397 
 398 ## Testing with Different Users
 399 
 400 ### System.runAs()
 401 
 402 ```apex
 403 @isTest
 404 static void testAsStandardUser() {
 405     User standardUser = TestDataFactory.createUser('Standard User');
 406 
 407     System.runAs(standardUser) {
 408         Test.startTest();
 409         // Code executes as standardUser
 410         List<Account> accounts = AccountService.getAccounts();
 411         Test.stopTest();
 412 
 413         // User only sees records they have access to
 414         Assert.areEqual(0, accounts.size());
 415     }
 416 }
 417 
 418 @isTest
 419 static void testAsAdmin() {
 420     User adminUser = TestDataFactory.createUser('System Administrator');
 421 
 422     System.runAs(adminUser) {
 423         // Test admin-specific functionality
 424     }
 425 }
 426 ```
 427 
 428 ---
 429 
 430 ## Testing Private Methods
 431 
 432 ### @TestVisible Annotation
 433 
 434 ```apex
 435 public class MyService {
 436     @TestVisible
 437     private static String privateMethod(String input) {
 438         return input.toUpperCase();
 439     }
 440 }
 441 
 442 // Test can now access private method
 443 @isTest
 444 static void testPrivateMethod() {
 445     String result = MyService.privateMethod('test');
 446     Assert.areEqual('TEST', result);
 447 }
 448 ```
 449 
 450 ---
 451 
 452 ## Test Checklist
 453 
 454 | Scenario | Required |
 455 |----------|----------|
 456 | Positive test (happy path) | ✓ |
 457 | Negative test (error handling) | ✓ |
 458 | Bulk test (251+ records) | ✓ |
 459 | Single record test | ✓ |
 460 | Null/empty input | ✓ |
 461 | Boundary conditions | ✓ |
 462 | Different user profiles | ✓ |
 463 | Assert statements in every test | ✓ |
 464 | Test.startTest()/stopTest() for async | ✓ |
