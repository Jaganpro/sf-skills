<!-- Parent: sf-soql/SKILL.md -->
   1 # Selector Patterns: Query Abstraction in Vanilla Apex
   2 
   3 This guide teaches query abstraction patterns using pure Apex - no external libraries required. These patterns improve testability, maintainability, and security compliance.
   4 
   5 > **Sources**: [James Simone - Repository Pattern](https://www.jamessimone.net/blog/joys-of-apex/repository-pattern/), [Beyond the Cloud - Selector Layer](https://blog.beyondthecloud.dev/blog/why-do-you-need-selector-layer)
   6 
   7 ---
   8 
   9 ## Why Use a Selector Layer?
  10 
  11 ### The Problem
  12 
  13 Without abstraction, SOQL queries are scattered everywhere:
  14 
  15 ```apex
  16 // In TriggerHandler.cls
  17 List<Account> accounts = [SELECT Id, Name FROM Account WHERE Id IN :accountIds];
  18 
  19 // In BatchJob.cls (duplicate!)
  20 List<Account> accounts = [SELECT Id, Name FROM Account WHERE Id IN :ids];
  21 
  22 // In ServiceClass.cls (slightly different fields!)
  23 List<Account> accounts = [SELECT Id, Name, Industry FROM Account WHERE Id IN :accountIds];
  24 ```
  25 
  26 **Problems**:
  27 1. **Duplication**: Same query logic repeated
  28 2. **Inconsistency**: Different fields queried in different places
  29 3. **Fragility**: Field deletion breaks multiple classes
  30 4. **Testability**: Must create real records to test
  31 5. **Security**: FLS/sharing often forgotten
  32 
  33 ### The Solution
  34 
  35 Centralize queries in Selector classes:
  36 
  37 ```apex
  38 // Single source of truth
  39 public class AccountSelector {
  40     public static List<Account> byIds(Set<Id> accountIds) {
  41         return [
  42             SELECT Id, Name, Industry
  43             FROM Account
  44             WHERE Id IN :accountIds
  45             WITH SECURITY_ENFORCED
  46         ];
  47     }
  48 }
  49 
  50 // Usage everywhere
  51 List<Account> accounts = AccountSelector.byIds(accountIds);
  52 ```
  53 
  54 ---
  55 
  56 ## Pattern 1: Basic Selector Class
  57 
  58 The simplest approach - a class with static query methods.
  59 
  60 ```apex
  61 /**
  62  * AccountSelector - Centralized queries for Account object
  63  *
  64  * @see https://blog.beyondthecloud.dev/blog/why-do-you-need-selector-layer
  65  */
  66 public inherited sharing class AccountSelector {
  67 
  68     // ═══════════════════════════════════════════════════════════════════
  69     // FIELD SETS (centralized field lists)
  70     // ═══════════════════════════════════════════════════════════════════
  71 
  72     private static final List<SObjectField> STANDARD_FIELDS = new List<SObjectField>{
  73         Account.Id,
  74         Account.Name,
  75         Account.Industry,
  76         Account.AnnualRevenue,
  77         Account.OwnerId
  78     };
  79 
  80     // ═══════════════════════════════════════════════════════════════════
  81     // QUERY METHODS
  82     // ═══════════════════════════════════════════════════════════════════
  83 
  84     /**
  85      * Query accounts by their IDs
  86      */
  87     public static List<Account> byIds(Set<Id> accountIds) {
  88         if (accountIds == null || accountIds.isEmpty()) {
  89             return new List<Account>();
  90         }
  91         return [
  92             SELECT Id, Name, Industry, AnnualRevenue, OwnerId
  93             FROM Account
  94             WHERE Id IN :accountIds
  95             WITH SECURITY_ENFORCED
  96         ];
  97     }
  98 
  99     /**
 100      * Query accounts by Owner
 101      */
 102     public static List<Account> byOwnerId(Id ownerId) {
 103         return [
 104             SELECT Id, Name, Industry, AnnualRevenue, OwnerId
 105             FROM Account
 106             WHERE OwnerId = :ownerId
 107             WITH SECURITY_ENFORCED
 108             LIMIT 1000
 109         ];
 110     }
 111 
 112     /**
 113      * Query accounts with their contacts
 114      */
 115     public static List<Account> withContactsByIds(Set<Id> accountIds) {
 116         return [
 117             SELECT Id, Name,
 118                    (SELECT Id, FirstName, LastName, Email
 119                     FROM Contacts
 120                     WHERE IsActive__c = true
 121                     LIMIT 50)
 122             FROM Account
 123             WHERE Id IN :accountIds
 124             WITH SECURITY_ENFORCED
 125         ];
 126     }
 127 }
 128 ```
 129 
 130 **Usage**:
 131 ```apex
 132 // Clean, readable, testable
 133 List<Account> accounts = AccountSelector.byIds(accountIdSet);
 134 List<Account> myAccounts = AccountSelector.byOwnerId(UserInfo.getUserId());
 135 ```
 136 
 137 ---
 138 
 139 ## Pattern 2: Selector with Sharing Modes
 140 
 141 Control sharing rules at the selector level.
 142 
 143 ```apex
 144 /**
 145  * ContactSelector with sharing mode control
 146  */
 147 public class ContactSelector {
 148 
 149     // ═══════════════════════════════════════════════════════════════════
 150     // USER MODE (respects sharing rules - default)
 151     // ═══════════════════════════════════════════════════════════════════
 152 
 153     public inherited sharing class UserMode {
 154         public static List<Contact> byAccountIds(Set<Id> accountIds) {
 155             return [
 156                 SELECT Id, FirstName, LastName, Email, AccountId
 157                 FROM Contact
 158                 WHERE AccountId IN :accountIds
 159                 WITH USER_MODE
 160             ];
 161         }
 162     }
 163 
 164     // ═══════════════════════════════════════════════════════════════════
 165     // SYSTEM MODE (bypasses sharing - use carefully!)
 166     // ═══════════════════════════════════════════════════════════════════
 167 
 168     public without sharing class SystemMode {
 169         public static List<Contact> byAccountIds(Set<Id> accountIds) {
 170             return [
 171                 SELECT Id, FirstName, LastName, Email, AccountId
 172                 FROM Contact
 173                 WHERE AccountId IN :accountIds
 174                 WITH SYSTEM_MODE
 175             ];
 176         }
 177     }
 178 }
 179 
 180 // Usage
 181 List<Contact> visibleContacts = ContactSelector.UserMode.byAccountIds(ids);
 182 List<Contact> allContacts = ContactSelector.SystemMode.byAccountIds(ids);
 183 ```
 184 
 185 ---
 186 
 187 ## Pattern 3: Mockable Selector (for Unit Tests)
 188 
 189 Enable query mocking without database calls.
 190 
 191 ```apex
 192 /**
 193  * OpportunitySelector with mocking support
 194  *
 195  * @see https://www.jamessimone.net/blog/joys-of-apex/repository-pattern/
 196  */
 197 public inherited sharing class OpportunitySelector {
 198 
 199     // Test-visible mock data
 200     @TestVisible
 201     private static List<Opportunity> mockData;
 202 
 203     /**
 204      * Query opportunities by Account IDs
 205      * Returns mock data in tests if set
 206      */
 207     public static List<Opportunity> byAccountIds(Set<Id> accountIds) {
 208         if (Test.isRunningTest() && mockData != null) {
 209             return mockData;
 210         }
 211         return [
 212             SELECT Id, Name, StageName, Amount, CloseDate, AccountId
 213             FROM Opportunity
 214             WHERE AccountId IN :accountIds
 215             WITH SECURITY_ENFORCED
 216         ];
 217     }
 218 
 219     /**
 220      * Set mock data for testing
 221      */
 222     @TestVisible
 223     private static void setMockData(List<Opportunity> opportunities) {
 224         mockData = opportunities;
 225     }
 226 }
 227 ```
 228 
 229 **Test Usage**:
 230 ```apex
 231 @IsTest
 232 private class OpportunitySelectorTest {
 233     @IsTest
 234     static void testByAccountIds_returnsMockData() {
 235         // Arrange - no database records needed!
 236         List<Opportunity> mockOpps = new List<Opportunity>{
 237             new Opportunity(Name = 'Test Opp', StageName = 'Prospecting', Amount = 1000)
 238         };
 239         OpportunitySelector.setMockData(mockOpps);
 240 
 241         // Act
 242         List<Opportunity> result = OpportunitySelector.byAccountIds(new Set<Id>());
 243 
 244         // Assert
 245         System.assertEquals(1, result.size());
 246         System.assertEquals('Test Opp', result[0].Name);
 247     }
 248 }
 249 ```
 250 
 251 ---
 252 
 253 ## Pattern 4: Query Builder (Dynamic SOQL)
 254 
 255 For complex, dynamic queries that vary at runtime.
 256 
 257 ```apex
 258 /**
 259  * Dynamic query builder for flexible SOQL construction
 260  *
 261  * @see https://www.jamessimone.net/blog/joys-of-apex/you-need-a-strongly-typed-query-builder/
 262  */
 263 public inherited sharing class QueryBuilder {
 264 
 265     private String objectName;
 266     private Set<String> fields = new Set<String>();
 267     private List<String> conditions = new List<String>();
 268     private Map<String, Object> bindings = new Map<String, Object>();
 269     private String orderByClause;
 270     private Integer limitCount;
 271 
 272     /**
 273      * Constructor
 274      */
 275     public QueryBuilder(String objectName) {
 276         this.objectName = objectName;
 277     }
 278 
 279     /**
 280      * Add fields to select
 281      */
 282     public QueryBuilder selectFields(List<String> fieldList) {
 283         fields.addAll(fieldList);
 284         return this;
 285     }
 286 
 287     /**
 288      * Add fields using SObjectField tokens (type-safe!)
 289      */
 290     public QueryBuilder selectFields(List<SObjectField> fieldTokens) {
 291         for (SObjectField token : fieldTokens) {
 292             fields.add(String.valueOf(token));
 293         }
 294         return this;
 295     }
 296 
 297     /**
 298      * Add WHERE condition with binding
 299      */
 300     public QueryBuilder whereEquals(String field, Object value) {
 301         String bindName = 'bind' + bindings.size();
 302         conditions.add(field + ' = :' + bindName);
 303         bindings.put(bindName, value);
 304         return this;
 305     }
 306 
 307     /**
 308      * Add WHERE IN condition
 309      */
 310     public QueryBuilder whereIn(String field, Set<Id> ids) {
 311         String bindName = 'bind' + bindings.size();
 312         conditions.add(field + ' IN :' + bindName);
 313         bindings.put(bindName, ids);
 314         return this;
 315     }
 316 
 317     /**
 318      * Add ORDER BY
 319      */
 320     public QueryBuilder orderBy(String field, Boolean ascending) {
 321         orderByClause = field + (ascending ? ' ASC' : ' DESC');
 322         return this;
 323     }
 324 
 325     /**
 326      * Add LIMIT
 327      */
 328     public QueryBuilder setLimit(Integer count) {
 329         limitCount = count;
 330         return this;
 331     }
 332 
 333     /**
 334      * Build and execute the query
 335      */
 336     public List<SObject> execute() {
 337         String query = buildQuery();
 338         return Database.queryWithBinds(query, bindings, AccessLevel.USER_MODE);
 339     }
 340 
 341     /**
 342      * Build query string (for debugging)
 343      */
 344     public String buildQuery() {
 345         List<String> parts = new List<String>();
 346 
 347         // SELECT
 348         if (fields.isEmpty()) {
 349             fields.add('Id');
 350         }
 351         parts.add('SELECT ' + String.join(new List<String>(fields), ', '));
 352 
 353         // FROM
 354         parts.add('FROM ' + objectName);
 355 
 356         // WHERE
 357         if (!conditions.isEmpty()) {
 358             parts.add('WHERE ' + String.join(conditions, ' AND '));
 359         }
 360 
 361         // ORDER BY
 362         if (orderByClause != null) {
 363             parts.add('ORDER BY ' + orderByClause);
 364         }
 365 
 366         // LIMIT
 367         if (limitCount != null) {
 368             parts.add('LIMIT ' + limitCount);
 369         }
 370 
 371         return String.join(parts, ' ');
 372     }
 373 }
 374 ```
 375 
 376 **Usage**:
 377 ```apex
 378 // Fluent API for dynamic queries
 379 List<SObject> results = new QueryBuilder('Account')
 380     .selectFields(new List<SObjectField>{Account.Id, Account.Name, Account.Industry})
 381     .whereEquals('Industry', 'Technology')
 382     .whereIn('Id', accountIds)
 383     .orderBy('Name', true)
 384     .setLimit(100)
 385     .execute();
 386 
 387 // Debug the generated query
 388 System.debug(new QueryBuilder('Account').selectFields(...).buildQuery());
 389 // "SELECT Id, Name, Industry FROM Account WHERE Industry = :bind0 AND Id IN :bind1 ORDER BY Name ASC LIMIT 100"
 390 ```
 391 
 392 ---
 393 
 394 ## Pattern 5: Bulkified Query Pattern
 395 
 396 The Map-based lookup pattern for bulk operations.
 397 
 398 ```apex
 399 /**
 400  * BulkQueryHelper - Reusable bulk query patterns
 401  */
 402 public inherited sharing class BulkQueryHelper {
 403 
 404     /**
 405      * Get Accounts by ID as a Map (O(1) lookup)
 406      */
 407     public static Map<Id, Account> getAccountMapByIds(Set<Id> accountIds) {
 408         return new Map<Id, Account>([
 409             SELECT Id, Name, Industry
 410             FROM Account
 411             WHERE Id IN :accountIds
 412             WITH SECURITY_ENFORCED
 413         ]);
 414     }
 415 
 416     /**
 417      * Get Contacts grouped by AccountId
 418      */
 419     public static Map<Id, List<Contact>> getContactsByAccountId(Set<Id> accountIds) {
 420         Map<Id, List<Contact>> contactsByAccount = new Map<Id, List<Contact>>();
 421 
 422         for (Contact c : [
 423             SELECT Id, FirstName, LastName, Email, AccountId
 424             FROM Contact
 425             WHERE AccountId IN :accountIds
 426             WITH SECURITY_ENFORCED
 427         ]) {
 428             if (!contactsByAccount.containsKey(c.AccountId)) {
 429                 contactsByAccount.put(c.AccountId, new List<Contact>());
 430             }
 431             contactsByAccount.get(c.AccountId).add(c);
 432         }
 433 
 434         return contactsByAccount;
 435     }
 436 }
 437 ```
 438 
 439 **Usage in Trigger**:
 440 ```apex
 441 // ❌ WRONG: Query per record
 442 for (Opportunity opp : Trigger.new) {
 443     Account a = [SELECT Name FROM Account WHERE Id = :opp.AccountId];
 444 }
 445 
 446 // ✅ CORRECT: Bulk query with Map lookup
 447 Set<Id> accountIds = new Set<Id>();
 448 for (Opportunity opp : Trigger.new) {
 449     accountIds.add(opp.AccountId);
 450 }
 451 
 452 Map<Id, Account> accountMap = BulkQueryHelper.getAccountMapByIds(accountIds);
 453 
 454 for (Opportunity opp : Trigger.new) {
 455     Account a = accountMap.get(opp.AccountId);
 456     if (a != null) {
 457         // Use account data
 458     }
 459 }
 460 ```
 461 
 462 ---
 463 
 464 ## Best Practices Summary
 465 
 466 | Practice | Benefit |
 467 |----------|---------|
 468 | Centralize in Selector classes | One place to update field lists |
 469 | Use `WITH SECURITY_ENFORCED` | Automatic FLS enforcement |
 470 | Return empty List, not null | Prevents NullPointerException |
 471 | Use `inherited sharing` | Respects caller's sharing context |
 472 | Make fields list a constant | Easy to update across queries |
 473 | Add null/empty checks | Prevent unnecessary queries |
 474 | Support mocking in tests | Faster tests, no database dependencies |
 475 
 476 ---
 477 
 478 ## When to Use Each Pattern
 479 
 480 | Scenario | Pattern |
 481 |----------|---------|
 482 | Simple, static queries | Pattern 1: Basic Selector |
 483 | Need sharing mode control | Pattern 2: Sharing Modes |
 484 | Heavy unit testing | Pattern 3: Mockable Selector |
 485 | Dynamic filters at runtime | Pattern 4: Query Builder |
 486 | Trigger/batch bulk operations | Pattern 5: Bulkified Query |
