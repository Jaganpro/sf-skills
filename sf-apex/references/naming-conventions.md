<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Naming Conventions
   2 
   3 ## Classes
   4 
   5 ### Format: PascalCase
   6 
   7 | Type | Convention | Example |
   8 |------|------------|---------|
   9 | Standard class | `[Domain]Service` | `AccountService` |
  10 | Controller | `[Page]Controller` | `AccountPageController` |
  11 | Extension | `[Page]ControllerExt` | `AccountControllerExt` |
  12 | Trigger Action | `TA_[Object]_[Action]` | `TA_Account_SetDefaults` |
  13 | Batch | `[Domain]_Batch` | `AccountCleanup_Batch` |
  14 | Queueable | `[Domain]_Queueable` | `AccountSync_Queueable` |
  15 | Schedulable | `[Domain]_Schedule` | `DailyReport_Schedule` |
  16 | Selector | `[Object]Selector` | `AccountSelector` |
  17 | Domain | `[Object]Domain` | `AccountDomain` |
  18 | Test class | `[ClassName]Test` | `AccountServiceTest` |
  19 | Test factory | `TestDataFactory` | `TestDataFactory` |
  20 | Exception | `[Domain]Exception` | `InsufficientFundsException` |
  21 | Interface | `I[Name]` or descriptive | `IPaymentProcessor` |
  22 
  23 ### Examples
  24 
  25 ```apex
  26 public class AccountService { }
  27 public class TA_Account_ValidateAddress implements TriggerAction.BeforeInsert { }
  28 public class AccountCleanup_Batch implements Database.Batchable<SObject> { }
  29 public class AccountSync_Queueable implements Queueable { }
  30 public class AccountSelector { }
  31 ```
  32 
  33 ---
  34 
  35 ## Methods
  36 
  37 ### Format: camelCase, Start with Verb
  38 
  39 | Purpose | Convention | Example |
  40 |---------|------------|---------|
  41 | Get data | `get[Noun]` | `getAccounts()` |
  42 | Set data | `set[Noun]` | `setAccountStatus()` |
  43 | Check condition | `is[Adjective]` / `has[Noun]` | `isActive()`, `hasPermission()` |
  44 | Action | `[verb][Noun]` | `processOrders()`, `validateData()` |
  45 | Calculate | `calculate[Noun]` | `calculateTotal()` |
  46 | Create | `create[Noun]` | `createAccount()` |
  47 | Update | `update[Noun]` | `updateStatus()` |
  48 | Delete | `delete[Noun]` | `deleteRecords()` |
  49 
  50 ### Special Verbs
  51 
  52 - Use `obtain` instead of `get` for expensive operations
  53 - Use `specify` instead of `set` for configuration
  54 - Reserve `get`/`set` for actual property getters/setters
  55 
  56 ```apex
  57 // Good
  58 public Account getAccount(Id accountId) { }
  59 public void processRecords(List<Record__c> records) { }
  60 public Boolean isEligible(Account acc) { }
  61 public Decimal calculateTotalRevenue(List<Opportunity> opps) { }
  62 
  63 // Better for expensive operations
  64 public Account obtainAccountWithRelated(Id accountId) { }
  65 
  66 // Boolean methods read as assertions
  67 public Boolean hasActiveSubscription() { }
  68 public Boolean canModifyRecord() { }
  69 ```
  70 
  71 ---
  72 
  73 ## Variables
  74 
  75 ### Format: camelCase, Descriptive
  76 
  77 | Type | Convention | Example |
  78 |------|------------|---------|
  79 | Local variable | descriptive noun | `account`, `totalAmount` |
  80 | Loop iterator | single letter (temp) | `i`, `j`, `k` |
  81 | Boolean | `is[Adjective]` / `has[Noun]` | `isValid`, `hasError` |
  82 | Collection | plural noun | `accounts`, `contactList` |
  83 | Map | `[value]By[key]` | `accountsById`, `contactsByEmail` |
  84 | Set | `[noun]Set` or `[noun]Ids` | `accountIds`, `processedIdSet` |
  85 
  86 ### Anti-Patterns to Avoid
  87 
  88 ```apex
  89 // BAD: Abbreviations
  90 String acct;      // What is this?
  91 List<Task> tks;   // Unclear
  92 SObject rec;      // Too generic
  93 
  94 // GOOD: Descriptive names
  95 String accountName;
  96 List<Task> openTasks;
  97 Account parentAccount;
  98 ```
  99 
 100 ### Collection Naming
 101 
 102 ```apex
 103 // Lists - plural noun
 104 List<Account> accounts;
 105 List<Contact> relatedContacts;
 106 
 107 // Sets - noun + Ids or noun + Set
 108 Set<Id> accountIds;
 109 Set<String> processedEmailSet;
 110 
 111 // Maps - value + By + key description
 112 Map<Id, Account> accountsById;
 113 Map<String, List<Contact>> contactsByEmail;
 114 Map<Id, Map<String, Decimal>> metricsByAccountByType;
 115 ```
 116 
 117 ---
 118 
 119 ## Constants
 120 
 121 ### Format: UPPER_SNAKE_CASE
 122 
 123 ```apex
 124 public class Constants {
 125     public static final String STATUS_ACTIVE = 'Active';
 126     public static final String STATUS_INACTIVE = 'Inactive';
 127     public static final Integer MAX_RETRY_COUNT = 3;
 128     public static final Decimal TAX_RATE = 0.08;
 129 }
 130 ```
 131 
 132 ---
 133 
 134 ## Custom Objects & Fields
 135 
 136 ### Format: Title_Case_With_Underscores
 137 
 138 ```apex
 139 // Objects
 140 Account_Score__c
 141 Order_Line_Item__c
 142 
 143 // Fields
 144 Account_Status__c
 145 Total_Revenue__c
 146 Is_Primary__c
 147 
 148 // Reference in code (use API names)
 149 account.Account_Status__c = 'Active';
 150 ```
 151 
 152 ---
 153 
 154 ## Triggers
 155 
 156 ### Format: [ObjectName]Trigger
 157 
 158 ```apex
 159 trigger AccountTrigger on Account (...) { }
 160 trigger ContactTrigger on Contact (...) { }
 161 trigger OpportunityTrigger on Opportunity (...) { }
 162 ```
 163 
 164 ---
 165 
 166 ## Test Classes
 167 
 168 ### Format: [TestedClassName]Test
 169 
 170 ```apex
 171 // For AccountService.cls
 172 @isTest
 173 private class AccountServiceTest { }
 174 
 175 // For TA_Account_SetDefaults.cls
 176 @isTest
 177 private class TA_Account_SetDefaultsTest { }
 178 ```
 179 
 180 ### Test Methods
 181 
 182 ```apex
 183 // Format: test[Scenario]
 184 @isTest
 185 static void testPositiveScenario() { }
 186 
 187 @isTest
 188 static void testBulkInsert() { }
 189 
 190 @isTest
 191 static void testInvalidInput() { }
 192 
 193 @isTest
 194 static void testAsStandardUser() { }
 195 ```
 196 
 197 ---
 198 
 199 ## Quick Reference
 200 
 201 | Element | Convention | Example |
 202 |---------|------------|---------|
 203 | Class | PascalCase | `AccountService` |
 204 | Interface | I + PascalCase | `IPaymentProcessor` |
 205 | Method | camelCase verb | `processRecords()` |
 206 | Variable | camelCase noun | `accountList` |
 207 | Constant | UPPER_SNAKE | `MAX_RETRIES` |
 208 | Parameter | camelCase | `accountId` |
 209 | Boolean | is/has prefix | `isActive` |
 210 | Map | valueByKey | `accountsById` |
 211 | Set | nounIds/nounSet | `accountIds` |
 212 | List | plural noun | `accounts` |
 213 | Trigger | ObjectTrigger | `AccountTrigger` |
 214 | Trigger Action | TA_Object_Action | `TA_Account_Validate` |
 215 | Batch | Domain_Batch | `Cleanup_Batch` |
 216 | Test | ClassTest | `AccountServiceTest` |
