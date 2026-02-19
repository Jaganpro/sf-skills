<!-- Parent: sf-testing/SKILL.md -->
   1 # Mocking Patterns in Apex Tests
   2 
   3 This guide covers mocking and stubbing patterns that enable true unit testing in Apex. By replacing database operations and external services with mock implementations, you can write fast, isolated, reliable tests.
   4 
   5 > **Sources**: [Beyond the Cloud](https://blog.beyondthecloud.dev/blog/salesforce-mock-in-apex-tests), [James Simone](https://www.jamessimone.net/blog/joys-of-apex/mocking-dml/), [Trailhead](https://trailhead.salesforce.com/content/learn/modules/unit-testing-on-the-lightning-platform/mock-stub-objects)
   6 
   7 ---
   8 
   9 ## Mocking vs Stubbing
  10 
  11 Understanding the distinction is crucial for effective test design:
  12 
  13 | Aspect | Mocking | Stubbing |
  14 |--------|---------|----------|
  15 | **Purpose** | Replace objects with fakes returning predefined values | Create fake implementations with dynamic logic |
  16 | **Complexity** | Simple, static responses | Complex, behavioral simulation |
  17 | **When to Use** | HTTP callouts, simple return values | Interface implementations, dynamic behavior |
  18 | **Example** | `HttpCalloutMock` returns fixed response | `StubProvider` with conditional logic |
  19 
  20 ---
  21 
  22 ## Pattern 1: HttpCalloutMock (Required for HTTP Tests)
  23 
  24 Salesforce **requires** mock callouts - you cannot make real HTTP requests in tests.
  25 
  26 ### Basic Implementation
  27 
  28 ```apex
  29 /**
  30  * Simple HTTP mock returning a fixed response
  31  *
  32  * @see https://www.apexhours.com/testing-web-services-callouts-in-salesforce/
  33  */
  34 @IsTest
  35 public class MockHttpResponse implements HttpCalloutMock {
  36 
  37     private Integer statusCode;
  38     private String body;
  39 
  40     public MockHttpResponse(Integer statusCode, String body) {
  41         this.statusCode = statusCode;
  42         this.body = body;
  43     }
  44 
  45     public HttpResponse respond(HttpRequest req) {
  46         HttpResponse res = new HttpResponse();
  47         res.setStatusCode(this.statusCode);
  48         res.setHeader('Content-Type', 'application/json');
  49         res.setBody(this.body);
  50         return res;
  51     }
  52 }
  53 
  54 // Usage in test
  55 @IsTest
  56 static void testApiCall_Success() {
  57     String mockBody = '{"success": true, "data": {"id": "12345"}}';
  58     Test.setMock(HttpCalloutMock.class, new MockHttpResponse(200, mockBody));
  59 
  60     Test.startTest();
  61     ApiResponse result = MyApiService.callExternalApi('endpoint');
  62     Test.stopTest();
  63 
  64     Assert.isTrue(result.success, 'API call should succeed');
  65 }
  66 ```
  67 
  68 ### Multi-Endpoint Mock
  69 
  70 ```apex
  71 /**
  72  * Mock that responds differently based on request endpoint
  73  */
  74 @IsTest
  75 public class MultiEndpointMock implements HttpCalloutMock {
  76 
  77     public HttpResponse respond(HttpRequest req) {
  78         HttpResponse res = new HttpResponse();
  79         res.setStatusCode(200);
  80         res.setHeader('Content-Type', 'application/json');
  81 
  82         String endpoint = req.getEndpoint();
  83 
  84         if (endpoint.contains('/users')) {
  85             res.setBody('{"users": [{"id": 1, "name": "John"}]}');
  86         } else if (endpoint.contains('/orders')) {
  87             res.setBody('{"orders": [{"id": 100, "total": 250.00}]}');
  88         } else {
  89             res.setStatusCode(404);
  90             res.setBody('{"error": "Not Found"}');
  91         }
  92 
  93         return res;
  94     }
  95 }
  96 ```
  97 
  98 ### Error Scenario Mock
  99 
 100 ```apex
 101 /**
 102  * Mock for testing error handling
 103  */
 104 @IsTest
 105 static void testApiCall_ServerError_HandlesGracefully() {
 106     Test.setMock(HttpCalloutMock.class, new MockHttpResponse(500, '{"error": "Server Error"}'));
 107 
 108     Test.startTest();
 109     try {
 110         MyApiService.callExternalApi('endpoint');
 111         Assert.fail('Expected CalloutException was not thrown');
 112     } catch (CalloutException e) {
 113         Assert.isTrue(e.getMessage().contains('Server Error'), 'Should contain error message');
 114     }
 115     Test.stopTest();
 116 }
 117 ```
 118 
 119 ---
 120 
 121 ## Pattern 2: DML Mocking (No Database Operations)
 122 
 123 This pattern eliminates database operations from tests, achieving 35x faster execution.
 124 
 125 ### The DML Interface
 126 
 127 ```apex
 128 /**
 129  * Interface for DML operations - enables mocking
 130  *
 131  * @see https://www.jamessimone.net/blog/joys-of-apex/mocking-dml/
 132  */
 133 public interface IDML {
 134     void doInsert(SObject record);
 135     void doInsert(List<SObject> records);
 136     void doUpdate(SObject record);
 137     void doUpdate(List<SObject> records);
 138     void doUpsert(SObject record);
 139     void doUpsert(List<SObject> records);
 140     void doDelete(SObject record);
 141     void doDelete(List<SObject> records);
 142 }
 143 ```
 144 
 145 ### Production Implementation
 146 
 147 ```apex
 148 /**
 149  * Production DML implementation - performs actual database operations
 150  */
 151 public class DML implements IDML {
 152 
 153     public void doInsert(SObject record) {
 154         insert record;
 155     }
 156 
 157     public void doInsert(List<SObject> records) {
 158         insert records;
 159     }
 160 
 161     public void doUpdate(SObject record) {
 162         update record;
 163     }
 164 
 165     public void doUpdate(List<SObject> records) {
 166         update records;
 167     }
 168 
 169     public void doUpsert(SObject record) {
 170         upsert record;
 171     }
 172 
 173     public void doUpsert(List<SObject> records) {
 174         upsert records;
 175     }
 176 
 177     public void doDelete(SObject record) {
 178         delete record;
 179     }
 180 
 181     public void doDelete(List<SObject> records) {
 182         delete records;
 183     }
 184 }
 185 ```
 186 
 187 ### Mock Implementation
 188 
 189 ```apex
 190 /**
 191  * Mock DML implementation - tracks operations without database
 192  */
 193 @IsTest
 194 public class DMLMock implements IDML {
 195 
 196     // Static lists to track operations
 197     public static List<SObject> InsertedRecords = new List<SObject>();
 198     public static List<SObject> UpdatedRecords = new List<SObject>();
 199     public static List<SObject> UpsertedRecords = new List<SObject>();
 200     public static List<SObject> DeletedRecords = new List<SObject>();
 201 
 202     // Counter for generating fake IDs
 203     private static Integer idCounter = 1;
 204 
 205     public void doInsert(SObject record) {
 206         doInsert(new List<SObject>{ record });
 207     }
 208 
 209     public void doInsert(List<SObject> records) {
 210         for (SObject record : records) {
 211             // Generate fake ID to simulate insert
 212             if (record.Id == null) {
 213                 record.Id = generateFakeId(record.getSObjectType());
 214             }
 215             InsertedRecords.add(record);
 216         }
 217     }
 218 
 219     public void doUpdate(SObject record) {
 220         doUpdate(new List<SObject>{ record });
 221     }
 222 
 223     public void doUpdate(List<SObject> records) {
 224         UpdatedRecords.addAll(records);
 225     }
 226 
 227     public void doUpsert(SObject record) {
 228         doUpsert(new List<SObject>{ record });
 229     }
 230 
 231     public void doUpsert(List<SObject> records) {
 232         UpsertedRecords.addAll(records);
 233     }
 234 
 235     public void doDelete(SObject record) {
 236         doDelete(new List<SObject>{ record });
 237     }
 238 
 239     public void doDelete(List<SObject> records) {
 240         DeletedRecords.addAll(records);
 241     }
 242 
 243     /**
 244      * Generate a fake Salesforce ID for testing
 245      */
 246     private static Id generateFakeId(Schema.SObjectType sObjectType) {
 247         String keyPrefix = sObjectType.getDescribe().getKeyPrefix();
 248         String idBody = String.valueOf(idCounter++).leftPad(12, '0');
 249         return Id.valueOf(keyPrefix + idBody);
 250     }
 251 
 252     /**
 253      * Reset all tracked operations (call in @TestSetup or between tests)
 254      */
 255     public static void reset() {
 256         InsertedRecords.clear();
 257         UpdatedRecords.clear();
 258         UpsertedRecords.clear();
 259         DeletedRecords.clear();
 260         idCounter = 1;
 261     }
 262 
 263     /**
 264      * Get inserted records of a specific type
 265      */
 266     public static List<SObject> getInsertedOfType(Schema.SObjectType sObjectType) {
 267         List<SObject> result = new List<SObject>();
 268         for (SObject record : InsertedRecords) {
 269             if (record.getSObjectType() == sObjectType) {
 270                 result.add(record);
 271             }
 272         }
 273         return result;
 274     }
 275 }
 276 ```
 277 
 278 ### Using DML Mocking in Services
 279 
 280 ```apex
 281 /**
 282  * Service class that accepts injected DML
 283  */
 284 public class AccountService {
 285 
 286     private IDML dml;
 287 
 288     // Production constructor - uses real DML
 289     public AccountService() {
 290         this(new DML());
 291     }
 292 
 293     // Test constructor - accepts mock DML
 294     @TestVisible
 295     private AccountService(IDML dml) {
 296         this.dml = dml;
 297     }
 298 
 299     public Id createAccount(Account acc) {
 300         if (acc == null) {
 301             throw new IllegalArgumentException('Account cannot be null');
 302         }
 303         dml.doInsert(acc);
 304         return acc.Id;
 305     }
 306 }
 307 
 308 // Test using mock DML
 309 @IsTest
 310 static void testCreateAccount_NoDatabase() {
 311     // Arrange
 312     DMLMock.reset();
 313     AccountService service = new AccountService(new DMLMock());
 314     Account testAcc = new Account(Name = 'Test Account');
 315 
 316     // Act
 317     Test.startTest();
 318     Id accountId = service.createAccount(testAcc);
 319     Test.stopTest();
 320 
 321     // Assert
 322     Assert.isNotNull(accountId, 'Should have fake ID');
 323     Assert.areEqual(1, DMLMock.InsertedRecords.size(), 'Should have 1 inserted record');
 324     Account inserted = (Account) DMLMock.InsertedRecords[0];
 325     Assert.areEqual('Test Account', inserted.Name, 'Name should match');
 326 }
 327 ```
 328 
 329 ---
 330 
 331 ## Pattern 3: StubProvider (Dynamic Behavior)
 332 
 333 Use `StubProvider` when you need dynamic, conditional behavior in your mocks.
 334 
 335 ### Basic StubProvider Implementation
 336 
 337 ```apex
 338 /**
 339  * StubProvider for dynamic service mocking
 340  *
 341  * @see https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_interface_System_StubProvider.htm
 342  */
 343 @IsTest
 344 public class AccountServiceStub implements System.StubProvider {
 345 
 346     private Map<String, Object> methodResponses = new Map<String, Object>();
 347 
 348     /**
 349      * Configure what a method should return
 350      */
 351     public AccountServiceStub withMethodReturn(String methodName, Object returnValue) {
 352         methodResponses.put(methodName, returnValue);
 353         return this;
 354     }
 355 
 356     public Object handleMethodCall(
 357         Object stubbedObject,
 358         String stubbedMethodName,
 359         Type returnType,
 360         List<Type> paramTypes,
 361         List<String> paramNames,
 362         List<Object> paramValues
 363     ) {
 364         // Return pre-configured response if available
 365         if (methodResponses.containsKey(stubbedMethodName)) {
 366             return methodResponses.get(stubbedMethodName);
 367         }
 368 
 369         // Default responses based on method name
 370         if (stubbedMethodName == 'getAccount') {
 371             return new Account(Id = generateFakeId(), Name = 'Stubbed Account');
 372         }
 373         if (stubbedMethodName == 'getAccounts') {
 374             return new List<Account>{
 375                 new Account(Id = generateFakeId(), Name = 'Stubbed 1'),
 376                 new Account(Id = generateFakeId(), Name = 'Stubbed 2')
 377             };
 378         }
 379 
 380         return null;
 381     }
 382 
 383     private static Integer idCounter = 1;
 384     private static Id generateFakeId() {
 385         String idBody = String.valueOf(idCounter++).leftPad(12, '0');
 386         return Id.valueOf('001' + idBody);
 387     }
 388 }
 389 ```
 390 
 391 ### Using StubProvider
 392 
 393 ```apex
 394 // Create stub with Test.createStub()
 395 @IsTest
 396 static void testWithStub() {
 397     // Create the stub
 398     AccountServiceStub stub = new AccountServiceStub()
 399         .withMethodReturn('getAccountCount', 42);
 400 
 401     IAccountService service = (IAccountService) Test.createStub(
 402         IAccountService.class,
 403         stub
 404     );
 405 
 406     // Use the stubbed service
 407     Test.startTest();
 408     Integer count = service.getAccountCount();
 409     Account acc = service.getAccount('001000000000001');
 410     Test.stopTest();
 411 
 412     // Verify
 413     Assert.areEqual(42, count, 'Should return configured value');
 414     Assert.areEqual('Stubbed Account', acc.Name, 'Should return stub default');
 415 }
 416 ```
 417 
 418 ---
 419 
 420 ## Pattern 4: Selector Mocking (Query Results)
 421 
 422 Mock SOQL query results without hitting the database.
 423 
 424 ```apex
 425 /**
 426  * Mockable selector pattern
 427  */
 428 public class AccountSelector {
 429 
 430     @TestVisible
 431     private static List<Account> mockResults;
 432 
 433     public static List<Account> getActiveAccounts() {
 434         if (Test.isRunningTest() && mockResults != null) {
 435             return mockResults;
 436         }
 437         return [
 438             SELECT Id, Name, Industry
 439             FROM Account
 440             WHERE IsActive__c = true
 441             WITH SECURITY_ENFORCED
 442         ];
 443     }
 444 
 445     @TestVisible
 446     private static void setMockResults(List<Account> accounts) {
 447         mockResults = accounts;
 448     }
 449 }
 450 
 451 // Usage in test
 452 @IsTest
 453 static void testWithMockedQuery() {
 454     // Arrange - no database insert needed!
 455     List<Account> mockAccounts = new List<Account>{
 456         new Account(Name = 'Mock 1', Industry = 'Tech'),
 457         new Account(Name = 'Mock 2', Industry = 'Finance')
 458     };
 459     AccountSelector.setMockResults(mockAccounts);
 460 
 461     // Act
 462     Test.startTest();
 463     List<Account> result = AccountSelector.getActiveAccounts();
 464     Test.stopTest();
 465 
 466     // Assert
 467     Assert.areEqual(2, result.size(), 'Should return mock data');
 468     Assert.areEqual('Mock 1', result[0].Name);
 469 }
 470 ```
 471 
 472 ---
 473 
 474 ## When to Use Each Pattern
 475 
 476 | Scenario | Pattern | Why |
 477 |----------|---------|-----|
 478 | HTTP callouts | HttpCalloutMock | Required by Salesforce |
 479 | Fast unit tests | DML Mocking | Eliminates database overhead |
 480 | Complex interfaces | StubProvider | Dynamic, conditional behavior |
 481 | Query isolation | Selector Mocking | Test without data setup |
 482 | Simple replacements | Direct mocking | Static @TestVisible fields |
 483 
 484 ---
 485 
 486 ## Performance Comparison
 487 
 488 | Approach | 10,000 Records | Notes |
 489 |----------|----------------|-------|
 490 | Actual DML | ~50 seconds | Database operations are slow |
 491 | DML Mocking | <1 second | 35x faster |
 492 | StubProvider | <1 second | No database at all |
 493 
 494 ---
 495 
 496 ## Best Practices
 497 
 498 1. **Mock at the seams**: DML, callouts, and queries are natural mock points
 499 2. **Use dependency injection**: Constructor injection enables easy test swapping
 500 3. **Prefer interfaces**: `IDML` interface allows production/mock implementations
 501 4. **Reset between tests**: Call `DMLMock.reset()` to prevent test pollution
 502 5. **Verify mock behavior**: Assert on `DMLMock.InsertedRecords` to confirm operations
 503 6. **Generate fake IDs**: Use key prefix + counter for realistic test IDs
