<!-- Parent: sf-data/SKILL.md -->
   1 # Test Data Factory Usage
   2 
   3 How to use and customize the test data factory templates.
   4 
   5 ## Basic Factory Pattern
   6 
   7 ### Account Factory
   8 ```apex
   9 public class TestDataFactory_Account {
  10 
  11     // Basic creation - inserted
  12     public static List<Account> create(Integer count) {
  13         return create(count, true);
  14     }
  15 
  16     // Control insertion
  17     public static List<Account> create(Integer count, Boolean doInsert) {
  18         List<Account> records = new List<Account>();
  19         for (Integer i = 0; i < count; i++) {
  20             records.add(new Account(
  21                 Name = 'Test Account ' + i,
  22                 Industry = 'Technology'
  23             ));
  24         }
  25         if (doInsert) {
  26             insert records;
  27         }
  28         return records;
  29     }
  30 }
  31 ```
  32 
  33 ### Usage Examples
  34 
  35 ```apex
  36 // Create 10 accounts (inserted)
  37 List<Account> accounts = TestDataFactory_Account.create(10);
  38 
  39 // Create 10 accounts (not inserted - for customization)
  40 List<Account> accounts = TestDataFactory_Account.create(10, false);
  41 accounts[0].AnnualRevenue = 1000000;
  42 accounts[1].Rating = 'Hot';
  43 insert accounts;
  44 ```
  45 
  46 ## Factory with Variations
  47 
  48 ### Industry Variations
  49 ```apex
  50 public static List<Account> createWithVariedIndustries(Integer count) {
  51     List<Account> records = new List<Account>();
  52     List<String> industries = new List<String>{
  53         'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail'
  54     };
  55 
  56     for (Integer i = 0; i < count; i++) {
  57         records.add(new Account(
  58             Name = 'Test Account ' + i,
  59             Industry = industries[Math.mod(i, industries.size())]
  60         ));
  61     }
  62     insert records;
  63     return records;
  64 }
  65 ```
  66 
  67 ### Revenue Tiers
  68 ```apex
  69 public static List<Account> createWithRevenueTiers(Integer count) {
  70     List<Account> records = new List<Account>();
  71     List<Decimal> tiers = new List<Decimal>{
  72         100000, 500000, 1000000, 5000000, 10000000
  73     };
  74 
  75     for (Integer i = 0; i < count; i++) {
  76         records.add(new Account(
  77             Name = 'Test Account ' + i,
  78             AnnualRevenue = tiers[Math.mod(i, tiers.size())]
  79         ));
  80     }
  81     insert records;
  82     return records;
  83 }
  84 ```
  85 
  86 ## Factory with Relationships
  87 
  88 ### Contact Factory with Account
  89 ```apex
  90 public class TestDataFactory_Contact {
  91 
  92     // Create contacts for existing accounts
  93     public static List<Contact> createForAccounts(Set<Id> accountIds, Integer perAccount) {
  94         List<Contact> contacts = new List<Contact>();
  95         Integer i = 0;
  96 
  97         for (Id accId : accountIds) {
  98             for (Integer j = 0; j < perAccount; j++) {
  99                 contacts.add(new Contact(
 100                     FirstName = 'Test',
 101                     LastName = 'Contact ' + i,
 102                     AccountId = accId,
 103                     Email = 'test' + i + '@example.com'
 104                 ));
 105                 i++;
 106             }
 107         }
 108         insert contacts;
 109         return contacts;
 110     }
 111 }
 112 ```
 113 
 114 ### Usage
 115 ```apex
 116 // Create 10 accounts with 3 contacts each
 117 List<Account> accounts = TestDataFactory_Account.create(10);
 118 Set<Id> accountIds = new Map<Id, Account>(accounts).keySet();
 119 List<Contact> contacts = TestDataFactory_Contact.createForAccounts(accountIds, 3);
 120 // Total: 10 accounts + 30 contacts
 121 ```
 122 
 123 ## Hierarchy Factory
 124 
 125 ### Complete Hierarchy in One Call
 126 ```apex
 127 public class TestDataFactory_Hierarchy {
 128 
 129     public class HierarchyResult {
 130         public List<Account> accounts;
 131         public List<Contact> contacts;
 132         public List<Opportunity> opportunities;
 133     }
 134 
 135     public static HierarchyResult create(
 136         Integer accountCount,
 137         Integer contactsPerAccount,
 138         Integer oppsPerAccount
 139     ) {
 140         HierarchyResult result = new HierarchyResult();
 141 
 142         // Create accounts
 143         result.accounts = TestDataFactory_Account.create(accountCount);
 144         Set<Id> accountIds = new Map<Id, Account>(result.accounts).keySet();
 145 
 146         // Create contacts
 147         result.contacts = TestDataFactory_Contact.createForAccounts(
 148             accountIds, contactsPerAccount
 149         );
 150 
 151         // Create opportunities
 152         result.opportunities = TestDataFactory_Opportunity.createForAccounts(
 153             accountIds, oppsPerAccount
 154         );
 155 
 156         return result;
 157     }
 158 }
 159 ```
 160 
 161 ### Usage
 162 ```apex
 163 // Create complete test hierarchy
 164 HierarchyResult data = TestDataFactory_Hierarchy.create(
 165     10,  // accounts
 166     3,   // contacts per account
 167     2    // opportunities per account
 168 );
 169 // Total: 10 accounts + 30 contacts + 20 opportunities
 170 
 171 System.debug('Accounts: ' + data.accounts.size());
 172 System.debug('Contacts: ' + data.contacts.size());
 173 System.debug('Opportunities: ' + data.opportunities.size());
 174 ```
 175 
 176 ## Edge Case Factories
 177 
 178 ### Boundary Values
 179 ```apex
 180 public static Account createWithMinValues() {
 181     return new Account(
 182         Name = 'A'  // Minimum name length
 183     );
 184 }
 185 
 186 public static Account createWithMaxValues() {
 187     return new Account(
 188         Name = 'X'.repeat(255),  // Maximum name length
 189         Description = 'Y'.repeat(32000)  // Maximum description
 190     );
 191 }
 192 ```
 193 
 194 ### Special Characters
 195 ```apex
 196 public static Account createWithSpecialCharacters() {
 197     return new Account(
 198         Name = 'Test & "Special" <Characters> \'Quotes\''
 199     );
 200 }
 201 ```
 202 
 203 ### Null/Empty Values
 204 ```apex
 205 public static List<Account> createWithNullableFields(Integer count) {
 206     List<Account> records = new List<Account>();
 207     for (Integer i = 0; i < count; i++) {
 208         Account acc = new Account(Name = 'Test ' + i);
 209         // Leave optional fields null
 210         // acc.Industry = null;
 211         // acc.AnnualRevenue = null;
 212         records.add(acc);
 213     }
 214     insert records;
 215     return records;
 216 }
 217 ```
 218 
 219 ## Using Factories for Testing
 220 
 221 ### Trigger Test Example
 222 ```apex
 223 @isTest
 224 public class AccountTriggerTest {
 225 
 226     @isTest
 227     static void testBulkInsert() {
 228         // Setup - 201 records to test batch boundaries
 229         Test.startTest();
 230         List<Account> accounts = TestDataFactory_Account.create(201);
 231         Test.stopTest();
 232 
 233         // Verify trigger logic executed
 234         List<Account> results = [
 235             SELECT Id, Custom_Field__c
 236             FROM Account
 237             WHERE Id IN :accounts
 238         ];
 239 
 240         for (Account acc : results) {
 241             System.assertNotEquals(null, acc.Custom_Field__c,
 242                 'Trigger should have set Custom_Field__c');
 243         }
 244     }
 245 
 246     @isTest
 247     static void testWithRelatedRecords() {
 248         // Setup hierarchy
 249         HierarchyResult data = TestDataFactory_Hierarchy.create(5, 2, 1);
 250 
 251         Test.startTest();
 252         // Test logic that involves relationships
 253         MyClass.processAccountsWithContacts(data.accounts);
 254         Test.stopTest();
 255 
 256         // Verify results
 257     }
 258 }
 259 ```
 260 
 261 ### Flow Test Example
 262 ```apex
 263 @isTest
 264 static void testRecordTriggeredFlow() {
 265     // Create data that matches flow entry criteria
 266     List<Account> accounts = TestDataFactory_Account.create(10, false);
 267     for (Account acc : accounts) {
 268         acc.Industry = 'Technology';  // Matches flow filter
 269         acc.AnnualRevenue = 1000000;  // Triggers flow action
 270     }
 271 
 272     Test.startTest();
 273     insert accounts;  // Flow fires on insert
 274     Test.stopTest();
 275 
 276     // Verify flow results
 277     List<Task> tasks = [SELECT Id FROM Task WHERE WhatId IN :accounts];
 278     System.assertEquals(10, tasks.size(), 'Flow should create task for each account');
 279 }
 280 ```
 281 
 282 ## Best Practices
 283 
 284 1. **Always return inserted records** - Caller may need IDs
 285 2. **Provide doInsert parameter** - Allow customization before insert
 286 3. **Use bulk patterns** - Single DML for multiple records
 287 4. **Handle required fields** - Prevent validation errors
 288 5. **Use unique values** - Avoid duplicate rule violations
 289 6. **Track IDs for cleanup** - Enable proper test isolation
