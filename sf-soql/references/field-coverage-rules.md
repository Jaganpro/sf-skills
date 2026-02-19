<!-- Parent: sf-soql/SKILL.md -->
   1 # SOQL Field Coverage Rules
   2 
   3 This guide documents field coverage validation rules for SOQL queries—ensuring that all fields accessed in Apex code are actually queried. This is a common source of runtime errors, especially in LLM-generated code.
   4 
   5 > **Source**: [LLM Mistakes in Apex & LWC - Salesforce Diaries](https://salesforcediaries.com/2026/01/16/llm-mistakes-in-apex-lwc-salesforce-code-generation-rules/)
   6 
   7 ---
   8 
   9 ## Table of Contents
  10 
  11 1. [The Field Coverage Problem](#the-field-coverage-problem)
  12 2. [Direct Field Access](#direct-field-access)
  13 3. [Relationship Field Access](#relationship-field-access)
  14 4. [Dynamic Field Access](#dynamic-field-access)
  15 5. [Aggregate Queries](#aggregate-queries)
  16 6. [Subquery Fields](#subquery-fields)
  17 7. [Validation Patterns](#validation-patterns)
  18 
  19 ---
  20 
  21 ## The Field Coverage Problem
  22 
  23 When you query an sObject, only the fields in the SELECT clause are populated. Accessing any other field results in a runtime error:
  24 
  25 ```
  26 System.SObjectException: SObject row was retrieved via SOQL without querying the requested field: Account.Industry
  27 ```
  28 
  29 This error is particularly common in LLM-generated code because the LLM may:
  30 1. Query some fields but access others in subsequent code
  31 2. Forget to include relationship fields (e.g., `Account.Name` on Contact)
  32 3. Access fields in conditional logic that weren't anticipated in the query
  33 
  34 ---
  35 
  36 ## Direct Field Access
  37 
  38 ### Rule: Every field accessed must be in the SELECT clause
  39 
  40 ### ❌ BAD: Accessing Unqueried Fields
  41 
  42 ```apex
  43 // Query only includes Id and Name
  44 List<Account> accounts = [SELECT Id, Name FROM Account];
  45 
  46 for (Account acc : accounts) {
  47     // RUNTIME ERROR: Industry was not queried
  48     if (acc.Industry == 'Technology') {
  49         // RUNTIME ERROR: Description was not queried
  50         acc.Description = 'Tech company';
  51     }
  52 
  53     // RUNTIME ERROR: AnnualRevenue was not queried
  54     Decimal revenue = acc.AnnualRevenue;
  55 }
  56 ```
  57 
  58 ### ✅ GOOD: Query All Accessed Fields
  59 
  60 ```apex
  61 // Query ALL fields that will be accessed
  62 List<Account> accounts = [
  63     SELECT Id, Name, Industry, Description, AnnualRevenue
  64     FROM Account
  65 ];
  66 
  67 for (Account acc : accounts) {
  68     if (acc.Industry == 'Technology') {
  69         acc.Description = 'Tech company';  // OK - queried
  70     }
  71     Decimal revenue = acc.AnnualRevenue;  // OK - queried
  72 }
  73 ```
  74 
  75 ### Field Access Locations to Check
  76 
  77 Fields can be accessed in many places—ensure coverage for all:
  78 
  79 | Access Location | Example | Must Query |
  80 |-----------------|---------|------------|
  81 | Conditional (`if`) | `if (acc.Industry == 'Tech')` | `Industry` |
  82 | Assignment | `acc.Description = 'Text'` | `Description` |
  83 | Variable assignment | `String name = acc.Name` | `Name` |
  84 | Method argument | `sendEmail(acc.Email__c)` | `Email__c` |
  85 | Collection key | `map.put(acc.Name, acc)` | `Name` |
  86 | String interpolation | `'Hello ' + acc.Name` | `Name` |
  87 | SOQL bind | `[SELECT Id FROM Contact WHERE AccountId = :acc.Id]` | `Id` (usually included) |
  88 
  89 ---
  90 
  91 ## Relationship Field Access
  92 
  93 ### Rule: Parent relationship fields require dot notation in SELECT
  94 
  95 ### ❌ BAD: Missing Relationship Fields
  96 
  97 ```apex
  98 // Contact query without Account relationship fields
  99 List<Contact> contacts = [SELECT Id, Name, AccountId FROM Contact];
 100 
 101 for (Contact c : contacts) {
 102     // RUNTIME ERROR: Account.Name was not queried
 103     String accountName = c.Account.Name;
 104 
 105     // RUNTIME ERROR: Account.Industry was not queried
 106     if (c.Account.Industry == 'Technology') {
 107         // ...
 108     }
 109 }
 110 ```
 111 
 112 ### ✅ GOOD: Include Relationship Fields
 113 
 114 ```apex
 115 // Use dot notation to include parent fields
 116 List<Contact> contacts = [
 117     SELECT Id, Name, AccountId,
 118            Account.Name,           // Parent field
 119            Account.Industry,       // Parent field
 120            Account.Owner.Name      // Grandparent field (up to 5 levels)
 121     FROM Contact
 122 ];
 123 
 124 for (Contact c : contacts) {
 125     String accountName = c.Account.Name;  // OK - queried
 126 
 127     if (c.Account.Industry == 'Technology') {  // OK - queried
 128         String ownerName = c.Account.Owner.Name;  // OK - queried
 129     }
 130 }
 131 ```
 132 
 133 ### Relationship Traversal Limits
 134 
 135 | Direction | Limit | Example |
 136 |-----------|-------|---------|
 137 | Parent (lookup/master-detail) | 5 levels | `Contact.Account.Owner.Manager.Name` |
 138 | Child (subquery) | 1 level | `Account -> Contacts` (cannot nest subqueries) |
 139 
 140 ### ❌ BAD: Assuming Relationship is Populated
 141 
 142 ```apex
 143 List<Contact> contacts = [SELECT Id, AccountId FROM Contact];
 144 
 145 for (Contact c : contacts) {
 146     // AccountId is queried, but Account object is NOT populated
 147     // This will throw: Account.Name not queried
 148     if (c.Account != null) {
 149         String name = c.Account.Name;  // ERROR!
 150     }
 151 }
 152 ```
 153 
 154 ### ✅ GOOD: Query Relationship or Use Separate Query
 155 
 156 ```apex
 157 // Option 1: Include relationship field
 158 List<Contact> contacts = [SELECT Id, AccountId, Account.Name FROM Contact];
 159 
 160 for (Contact c : contacts) {
 161     if (c.Account != null) {
 162         String name = c.Account.Name;  // OK
 163     }
 164 }
 165 
 166 // Option 2: Separate query using collected IDs
 167 List<Contact> contacts = [SELECT Id, AccountId FROM Contact];
 168 Set<Id> accountIds = new Set<Id>();
 169 for (Contact c : contacts) {
 170     if (c.AccountId != null) {
 171         accountIds.add(c.AccountId);
 172     }
 173 }
 174 
 175 Map<Id, Account> accountMap = new Map<Id, Account>(
 176     [SELECT Id, Name FROM Account WHERE Id IN :accountIds]
 177 );
 178 
 179 for (Contact c : contacts) {
 180     Account acc = accountMap.get(c.AccountId);
 181     if (acc != null) {
 182         String name = acc.Name;  // OK
 183     }
 184 }
 185 ```
 186 
 187 ---
 188 
 189 ## Dynamic Field Access
 190 
 191 ### Rule: Dynamic field access (using `get()`) also requires queried fields
 192 
 193 ### ❌ BAD: Dynamic Access to Unqueried Field
 194 
 195 ```apex
 196 List<Account> accounts = [SELECT Id, Name FROM Account];
 197 String fieldName = 'Industry';  // Dynamic field name
 198 
 199 for (Account acc : accounts) {
 200     // RUNTIME ERROR: Industry was not queried
 201     Object value = acc.get(fieldName);
 202 }
 203 ```
 204 
 205 ### ✅ GOOD: Query Fields Used Dynamically
 206 
 207 ```apex
 208 // If you know which fields will be accessed dynamically, query them
 209 List<Account> accounts = [SELECT Id, Name, Industry FROM Account];
 210 String fieldName = 'Industry';
 211 
 212 for (Account acc : accounts) {
 213     Object value = acc.get(fieldName);  // OK - Industry is queried
 214 }
 215 ```
 216 
 217 ### ✅ GOOD: Build Dynamic Query
 218 
 219 ```apex
 220 // For truly dynamic scenarios, build the query dynamically
 221 Set<String> fieldsToQuery = new Set<String>{'Id', 'Name'};
 222 fieldsToQuery.addAll(dynamicFieldList);  // Add dynamic fields
 223 
 224 String query = 'SELECT ' + String.join(new List<String>(fieldsToQuery), ', ') +
 225                ' FROM Account WHERE Id IN :accountIds';
 226 
 227 List<Account> accounts = Database.query(query);
 228 ```
 229 
 230 ---
 231 
 232 ## Aggregate Queries
 233 
 234 ### Rule: Aggregate queries return `AggregateResult`, not sObjects
 235 
 236 ### ❌ BAD: Treating Aggregate as sObject
 237 
 238 ```apex
 239 // This returns AggregateResult, not Account
 240 List<Account> accounts = [
 241     SELECT Industry, COUNT(Id) cnt
 242     FROM Account
 243     GROUP BY Industry
 244 ];  // COMPILE ERROR - wrong type
 245 
 246 // Even with correct type, can't access normal fields
 247 AggregateResult[] results = [
 248     SELECT Industry, COUNT(Id) cnt
 249     FROM Account
 250     GROUP BY Industry
 251 ];
 252 
 253 for (AggregateResult ar : results) {
 254     // Cannot access like sObject fields
 255     String industry = ar.Industry;  // COMPILE ERROR
 256 }
 257 ```
 258 
 259 ### ✅ GOOD: Use get() for Aggregate Results
 260 
 261 ```apex
 262 AggregateResult[] results = [
 263     SELECT Industry, COUNT(Id) cnt, SUM(AnnualRevenue) totalRevenue
 264     FROM Account
 265     GROUP BY Industry
 266 ];
 267 
 268 for (AggregateResult ar : results) {
 269     // Use get() with field alias
 270     String industry = (String) ar.get('Industry');
 271     Integer count = (Integer) ar.get('cnt');
 272     Decimal totalRevenue = (Decimal) ar.get('totalRevenue');
 273 
 274     System.debug(industry + ': ' + count + ' accounts, $' + totalRevenue);
 275 }
 276 ```
 277 
 278 ### Aggregate Field Aliases
 279 
 280 | Function | Default Alias | Example |
 281 |----------|---------------|---------|
 282 | `COUNT(Field)` | `expr0`, `expr1`, etc. | Use explicit alias: `COUNT(Id) cnt` |
 283 | `SUM(Field)` | `expr0`, `expr1`, etc. | Use explicit alias: `SUM(Amount) total` |
 284 | `AVG(Field)` | `expr0`, `expr1`, etc. | Use explicit alias: `AVG(Age) avgAge` |
 285 | `MIN(Field)` | `expr0`, `expr1`, etc. | Use explicit alias: `MIN(CreatedDate) earliest` |
 286 | `MAX(Field)` | `expr0`, `expr1`, etc. | Use explicit alias: `MAX(Amount) largest` |
 287 | `GROUP BY Field` | Field API name | Access with field name: `ar.get('Industry')` |
 288 
 289 ---
 290 
 291 ## Subquery Fields
 292 
 293 ### Rule: Child relationship subqueries create nested lists
 294 
 295 ### ❌ BAD: Accessing Subquery Fields Incorrectly
 296 
 297 ```apex
 298 // Query with contact subquery
 299 List<Account> accounts = [
 300     SELECT Id, Name,
 301            (SELECT Id, Name FROM Contacts)
 302     FROM Account
 303 ];
 304 
 305 for (Account acc : accounts) {
 306     // ERROR: Contacts is a List, not a single Contact
 307     String contactName = acc.Contacts.Name;
 308 
 309     // ERROR: Cannot access unqueried field from subquery
 310     for (Contact c : acc.Contacts) {
 311         String email = c.Email;  // Email not in subquery SELECT!
 312     }
 313 }
 314 ```
 315 
 316 ### ✅ GOOD: Proper Subquery Field Access
 317 
 318 ```apex
 319 // Query all needed fields in subquery
 320 List<Account> accounts = [
 321     SELECT Id, Name,
 322            (SELECT Id, Name, Email, Phone FROM Contacts)
 323     FROM Account
 324 ];
 325 
 326 for (Account acc : accounts) {
 327     // Contacts is a List<Contact>
 328     List<Contact> contacts = acc.Contacts;
 329 
 330     if (contacts != null && !contacts.isEmpty()) {
 331         for (Contact c : contacts) {
 332             String name = c.Name;    // OK - in subquery SELECT
 333             String email = c.Email;  // OK - in subquery SELECT
 334             String phone = c.Phone;  // OK - in subquery SELECT
 335         }
 336     }
 337 }
 338 ```
 339 
 340 ### Subquery Null Safety
 341 
 342 ```apex
 343 List<Account> accounts = [
 344     SELECT Id, (SELECT Id FROM Contacts)
 345     FROM Account
 346 ];
 347 
 348 for (Account acc : accounts) {
 349     // Subquery result can be null if no child records
 350     if (acc.Contacts != null) {
 351         for (Contact c : acc.Contacts) {
 352             // Process contact
 353         }
 354     }
 355 
 356     // Or use null-safe size check
 357     Integer contactCount = acc.Contacts?.size() ?? 0;
 358 }
 359 ```
 360 
 361 ---
 362 
 363 ## Validation Patterns
 364 
 365 ### Pattern 1: Field-to-Query Mapping
 366 
 367 Create a systematic approach to track field usage:
 368 
 369 ```apex
 370 public class AccountProcessor {
 371     // Document required fields at the top
 372     private static final Set<String> REQUIRED_FIELDS = new Set<String>{
 373         'Id', 'Name', 'Industry', 'Description', 'AnnualRevenue',
 374         'OwnerId', 'Owner.Name', 'Owner.Email'
 375     };
 376 
 377     // Single method for consistent querying
 378     public static List<Account> queryAccounts(Set<Id> accountIds) {
 379         return [
 380             SELECT Id, Name, Industry, Description, AnnualRevenue,
 381                    OwnerId, Owner.Name, Owner.Email
 382             FROM Account
 383             WHERE Id IN :accountIds
 384         ];
 385     }
 386 
 387     public static void processAccounts(List<Account> accounts) {
 388         for (Account acc : accounts) {
 389             // All fields in REQUIRED_FIELDS are safe to access
 390             if (acc.Industry == 'Technology') {
 391                 acc.Description = 'Tech: ' + acc.Name;
 392             }
 393         }
 394     }
 395 }
 396 ```
 397 
 398 ### Pattern 2: Selector Layer
 399 
 400 Use a selector pattern to centralize query field management:
 401 
 402 ```apex
 403 public class AccountSelector {
 404 
 405     // Default fields for most operations
 406     private static final List<String> DEFAULT_FIELDS = new List<String>{
 407         'Id', 'Name', 'Industry', 'Type', 'OwnerId'
 408     };
 409 
 410     // Extended fields for detailed views
 411     private static final List<String> DETAIL_FIELDS = new List<String>{
 412         'Id', 'Name', 'Industry', 'Type', 'OwnerId',
 413         'Description', 'AnnualRevenue', 'NumberOfEmployees',
 414         'BillingCity', 'BillingState', 'BillingCountry',
 415         'Owner.Name', 'Owner.Email'
 416     };
 417 
 418     public List<Account> selectById(Set<Id> ids) {
 419         return selectByIdWithFields(ids, DEFAULT_FIELDS);
 420     }
 421 
 422     public List<Account> selectByIdDetailed(Set<Id> ids) {
 423         return selectByIdWithFields(ids, DETAIL_FIELDS);
 424     }
 425 
 426     private List<Account> selectByIdWithFields(Set<Id> ids, List<String> fields) {
 427         String query = 'SELECT ' + String.join(fields, ', ') +
 428                        ' FROM Account WHERE Id IN :ids';
 429         return Database.query(query);
 430     }
 431 }
 432 ```
 433 
 434 ### Pattern 3: Field Validation Helper
 435 
 436 ```apex
 437 public class SObjectFieldValidator {
 438 
 439     /**
 440      * Check if a field was queried on an sObject
 441      * @param obj The sObject to check
 442      * @param fieldName The API name of the field
 443      * @return true if the field is populated (was queried)
 444      */
 445     public static Boolean isFieldPopulated(SObject obj, String fieldName) {
 446         try {
 447             obj.get(fieldName);
 448             return true;
 449         } catch (SObjectException e) {
 450             return false;
 451         }
 452     }
 453 
 454     /**
 455      * Get field value with default if not queried
 456      * @param obj The sObject
 457      * @param fieldName The field API name
 458      * @param defaultValue Value to return if field not queried
 459      * @return The field value or default
 460      */
 461     public static Object getFieldOrDefault(SObject obj, String fieldName, Object defaultValue) {
 462         try {
 463             Object value = obj.get(fieldName);
 464             return value != null ? value : defaultValue;
 465         } catch (SObjectException e) {
 466             return defaultValue;
 467         }
 468     }
 469 }
 470 ```
 471 
 472 ---
 473 
 474 ## Quick Reference: Field Coverage Checklist
 475 
 476 Before running code that processes SOQL results:
 477 
 478 ### Direct Fields
 479 - [ ] All fields in `if` conditions are queried
 480 - [ ] All fields on left side of assignments are queried
 481 - [ ] All fields passed to methods are queried
 482 - [ ] All fields used in map keys/values are queried
 483 
 484 ### Relationship Fields
 485 - [ ] Parent fields use dot notation (e.g., `Account.Name`)
 486 - [ ] Parent object null checks before field access
 487 - [ ] Relationship traversal doesn't exceed 5 levels
 488 
 489 ### Subqueries
 490 - [ ] Child records accessed as List, not single record
 491 - [ ] Subquery SELECT includes all accessed child fields
 492 - [ ] Null check before iterating subquery results
 493 
 494 ### Dynamic Access
 495 - [ ] Fields accessed via `get(fieldName)` are queried
 496 - [ ] Dynamic queries include all needed fields
 497 
 498 ---
 499 
 500 ## Common LLM Mistakes Summary
 501 
 502 | Mistake | Example | Fix |
 503 |---------|---------|-----|
 504 | Query subset, use superset | Query `Id, Name`, use `Industry` | Add `Industry` to SELECT |
 505 | Forget relationship field | Use `c.Account.Name` without querying | Add `Account.Name` to SELECT |
 506 | Assume AccountId = Account | Query `AccountId`, access `Account.Name` | Query `Account.Name` explicitly |
 507 | Wrong subquery access | `acc.Contacts.Email` | `for (Contact c : acc.Contacts) { c.Email }` |
 508 | Missing subquery field | Subquery `SELECT Id`, use `Email` | Add `Email` to subquery SELECT |
 509 
 510 ---
 511 
 512 ## Reference
 513 
 514 - **SOQL Anti-Patterns**: See `references/anti-patterns.md` for general SOQL mistakes
 515 - **Selector Patterns**: See `references/selector-patterns.md` for query organization
 516 - **Source**: [Salesforce Diaries - LLM Mistakes](https://salesforcediaries.com/2026/01/16/llm-mistakes-in-apex-lwc-salesforce-code-generation-rules/)
