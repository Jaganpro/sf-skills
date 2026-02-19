<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Code Review Checklist
   2 
   3 ## Critical Issues (Must Fix)
   4 
   5 ### Bulkification
   6 
   7 | Check | Status |
   8 |-------|--------|
   9 | No SOQL queries inside loops | ☐ |
  10 | No DML statements inside loops | ☐ |
  11 | Uses collections (List, Set, Map) properly | ☐ |
  12 | Handles 200+ records per trigger batch | ☐ |
  13 | Test class includes bulk test (251+ records) | ☐ |
  14 
  15 **Anti-Pattern:**
  16 ```apex
  17 // BAD
  18 for (Account acc : accounts) {
  19     Contact c = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
  20     update c;
  21 }
  22 ```
  23 
  24 **Fix:**
  25 ```apex
  26 // GOOD
  27 Set<Id> accountIds = new Map<Id, Account>(accounts).keySet();
  28 List<Contact> contacts = [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds];
  29 update contacts;
  30 ```
  31 
  32 ---
  33 
  34 ### Security
  35 
  36 | Check | Status |
  37 |-------|--------|
  38 | Uses `WITH USER_MODE` for SOQL | ☐ |
  39 | Uses bind variables (no SOQL injection) | ☐ |
  40 | Uses `with sharing` by default | ☐ |
  41 | `without sharing` justified and documented | ☐ |
  42 | No hardcoded credentials | ☐ |
  43 | No hardcoded Record IDs | ☐ |
  44 | Named Credentials used for callouts | ☐ |
  45 
  46 **Anti-Pattern:**
  47 ```apex
  48 // BAD
  49 String query = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';
  50 ```
  51 
  52 **Fix:**
  53 ```apex
  54 // GOOD
  55 String query = 'SELECT Id FROM Account WHERE Name = :userInput';
  56 List<Account> accounts = Database.query(query);
  57 ```
  58 
  59 ---
  60 
  61 ### Testing
  62 
  63 | Check | Status |
  64 |-------|--------|
  65 | Test class exists | ☐ |
  66 | Coverage > 75% (90%+ recommended) | ☐ |
  67 | Uses Assert class (not System.assert) | ☐ |
  68 | Assert in every test method | ☐ |
  69 | Tests positive scenario | ☐ |
  70 | Tests negative scenario (error handling) | ☐ |
  71 | Tests bulk scenario (251+ records) | ☐ |
  72 | Uses `Test.startTest()`/`Test.stopTest()` for async | ☐ |
  73 | Uses `seeAllData=false` | ☐ |
  74 | Uses Test Data Factory pattern | ☐ |
  75 
  76 **Anti-Pattern:**
  77 ```apex
  78 // BAD: No assertion
  79 @isTest
  80 static void testMethod() {
  81     Account acc = new Account(Name = 'Test');
  82     insert acc;
  83     // No assert!
  84 }
  85 ```
  86 
  87 **Fix:**
  88 ```apex
  89 // GOOD
  90 @isTest
  91 static void testAccountInsert() {
  92     Account acc = new Account(Name = 'Test');
  93 
  94     Test.startTest();
  95     insert acc;
  96     Test.stopTest();
  97 
  98     Account result = [SELECT Name FROM Account WHERE Id = :acc.Id];
  99     Assert.areEqual('Test', result.Name, 'Name should match');
 100 }
 101 ```
 102 
 103 ---
 104 
 105 ## Important Issues (Should Fix)
 106 
 107 ### Architecture
 108 
 109 | Check | Status |
 110 |-------|--------|
 111 | One trigger per object | ☐ |
 112 | Uses Trigger Actions Framework (or similar) | ☐ |
 113 | Logic-less triggers (delegates to handler) | ☐ |
 114 | Service layer for business logic | ☐ |
 115 | Selector pattern for queries | ☐ |
 116 | Single responsibility per class | ☐ |
 117 
 118 **Anti-Pattern:**
 119 ```apex
 120 // BAD: Logic in trigger
 121 trigger AccountTrigger on Account (before insert) {
 122     for (Account acc : Trigger.new) {
 123         if (acc.Industry == null) {
 124             acc.Industry = 'Other';
 125         }
 126         // 100 more lines of logic...
 127     }
 128 }
 129 ```
 130 
 131 **Fix:**
 132 ```apex
 133 // GOOD: Delegate to framework
 134 trigger AccountTrigger on Account (before insert, after insert, ...) {
 135     new MetadataTriggerHandler().run();
 136 }
 137 ```
 138 
 139 ---
 140 
 141 ### Error Handling
 142 
 143 | Check | Status |
 144 |-------|--------|
 145 | Catches specific exceptions before generic | ☐ |
 146 | No empty catch blocks | ☐ |
 147 | Errors logged appropriately | ☐ |
 148 | Uses `AuraHandledException` for LWC | ☐ |
 149 | Custom exceptions for business logic | ☐ |
 150 
 151 **Anti-Pattern:**
 152 ```apex
 153 // BAD
 154 try {
 155     insert accounts;
 156 } catch (Exception e) {
 157     // Silent failure
 158 }
 159 ```
 160 
 161 **Fix:**
 162 ```apex
 163 // GOOD
 164 try {
 165     insert accounts;
 166 } catch (DmlException e) {
 167     for (Integer i = 0; i < e.getNumDml(); i++) {
 168         System.debug(LoggingLevel.ERROR, 'DML Error: ' + e.getDmlMessage(i));
 169     }
 170     throw new AccountServiceException('Failed to insert accounts: ' + e.getMessage());
 171 }
 172 ```
 173 
 174 ---
 175 
 176 ### Naming
 177 
 178 | Check | Status |
 179 |-------|--------|
 180 | Class names are PascalCase | ☐ |
 181 | Method names are camelCase verbs | ☐ |
 182 | Variable names are descriptive | ☐ |
 183 | No abbreviations (tks, rec, acc) | ☐ |
 184 | Constants are UPPER_SNAKE_CASE | ☐ |
 185 | Collections indicate type (accountsById) | ☐ |
 186 
 187 ---
 188 
 189 ### Performance
 190 
 191 | Check | Status |
 192 |-------|--------|
 193 | Uses `Limits` class to monitor | ☐ |
 194 | Caches expensive operations | ☐ |
 195 | Heavy processing in async | ☐ |
 196 | SOQL filters on indexed fields | ☐ |
 197 | Variables go out of scope (heap) | ☐ |
 198 | No class-level large collections | ☐ |
 199 
 200 ---
 201 
 202 ## Minor Issues (Nice to Fix)
 203 
 204 ### Clean Code
 205 
 206 | Check | Status |
 207 |-------|--------|
 208 | No double negatives (`!= false`) | ☐ |
 209 | Boolean conditions extracted to variables | ☐ |
 210 | Methods do one thing | ☐ |
 211 | No side effects in methods | ☐ |
 212 | Consistent formatting | ☐ |
 213 | ApexDoc comments on public methods | ☐ |
 214 
 215 ---
 216 
 217 ### Common Anti-Patterns Quick Reference
 218 
 219 | Anti-Pattern | Fix |
 220 |--------------|-----|
 221 | SOQL in loop | Query before loop, use Map |
 222 | DML in loop | Collect in loop, DML after |
 223 | `without sharing` everywhere | `with sharing` default |
 224 | Multiple triggers per object | One trigger + TAF |
 225 | SOQL without WHERE/LIMIT | Always filter |
 226 | `isEmpty()` before DML | Remove (empty = 0 DMLs) |
 227 | Generic Exception only | Catch specific first |
 228 | Hard-coded IDs | Query dynamically |
 229 | No Test Data Factory | Create factory class |
 230 | `System.debug` everywhere | Use Custom Metadata toggle |
 231 | No trigger bypass | Boolean Custom Setting |
 232 | Exactly 75% coverage | Aim for 90%+ |
 233 | No assertions in tests | Assert in every test |
 234 | Public Read/Write OWD | Private + sharing rules |
 235 
 236 ---
 237 
 238 ## Review Process
 239 
 240 1. **Static Analysis**: Run PMD, check code coverage
 241 2. **Bulkification**: Verify no SOQL/DML in loops
 242 3. **Security**: Check sharing, CRUD/FLS, injection
 243 4. **Testing**: Review test coverage and quality
 244 5. **Architecture**: Verify patterns and separation
 245 6. **Naming**: Check conventions
 246 7. **Performance**: Review limits awareness
 247 8. **Documentation**: Verify ApexDoc comments
 248 
 249 ---
 250 
 251 ## Scoring
 252 
 253 | Category | Weight |
 254 |----------|--------|
 255 | Critical (Bulkification, Security, Testing) | 75 points |
 256 | Important (Architecture, Error Handling, Naming) | 55 points |
 257 | Minor (Clean Code, Performance, Docs) | 20 points |
 258 | **Total** | **150 points** |
 259 
 260 **Pass Threshold**: 90+ points (no critical issues)
