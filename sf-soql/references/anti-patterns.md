<!-- Parent: sf-soql/SKILL.md -->
   1 # SOQL Anti-Patterns: What to Avoid
   2 
   3 A catalog of common SOQL mistakes and their solutions. Avoiding these patterns will help you stay within governor limits, improve query performance, and write more maintainable code.
   4 
   5 > **Sources**: [Apex Hours](https://www.apexhours.com/soql-best-practices/), [Beyond the Cloud](https://blog.beyondthecloud.dev/), [Medium - Bulkification Patterns](https://medium.com/@saurabh.samirs/salesforce-apex-triggers-5-bulkification-patterns-to-avoid-soql-dml-limits-f4e9c8bbfb3a)
   6 
   7 ---
   8 
   9 ## Anti-Pattern #1: SOQL Inside Loops
  10 
  11 **The Problem**: Executing queries inside a loop quickly exhausts the 100 SOQL query limit.
  12 
  13 ```apex
  14 // ❌ ANTI-PATTERN: Query per record
  15 for (Contact c : Trigger.new) {
  16     Account a = [SELECT Name FROM Account WHERE Id = :c.AccountId];
  17     c.Account_Name__c = a.Name;
  18 }
  19 // 200 contacts = 200 queries = LIMIT EXCEEDED
  20 ```
  21 
  22 **The Solution**: Query once, use a Map for lookups.
  23 
  24 ```apex
  25 // ✅ CORRECT: Single query with Map lookup
  26 Set<Id> accountIds = new Set<Id>();
  27 for (Contact c : Trigger.new) {
  28     accountIds.add(c.AccountId);
  29 }
  30 
  31 Map<Id, Account> accountMap = new Map<Id, Account>(
  32     [SELECT Id, Name FROM Account WHERE Id IN :accountIds]
  33 );
  34 
  35 for (Contact c : Trigger.new) {
  36     Account a = accountMap.get(c.AccountId);
  37     if (a != null) {
  38         c.Account_Name__c = a.Name;
  39     }
  40 }
  41 // 200 contacts = 1 query = SAFE
  42 ```
  43 
  44 **Key Insight**: Collect IDs first, query once with `IN` clause, then use Map for O(1) lookups.
  45 
  46 ---
  47 
  48 ## Anti-Pattern #2: Non-Selective WHERE Clauses
  49 
  50 **The Problem**: Queries on non-indexed fields cause full table scans, which fail on large objects (100k+ records).
  51 
  52 ```apex
  53 // ❌ ANTI-PATTERN: Non-selective filter
  54 SELECT Id FROM Lead WHERE Status = 'Open'
  55 // Status is not indexed - scans ALL Lead records
  56 ```
  57 
  58 **The Solution**: Add an indexed field to make the query selective.
  59 
  60 ```apex
  61 // ✅ CORRECT: Add indexed field filter
  62 SELECT Id FROM Lead
  63 WHERE Status = 'Open'
  64 AND CreatedDate = LAST_N_DAYS:30
  65 // CreatedDate is indexed - uses index
  66 
  67 // ✅ ALTERNATIVE: Use OwnerId (indexed)
  68 SELECT Id FROM Lead
  69 WHERE Status = 'Open'
  70 AND OwnerId = :UserInfo.getUserId()
  71 ```
  72 
  73 **Indexed Fields** (Always use these in WHERE):
  74 - `Id`, `Name`, `OwnerId`, `CreatedDate`, `LastModifiedDate`
  75 - `RecordTypeId`, External ID fields, Master-Detail fields
  76 - Standard indexed fields: `Account.AccountNumber`, `Contact.Email`, `Case.CaseNumber`
  77 
  78 ---
  79 
  80 ## Anti-Pattern #3: Leading Wildcards
  81 
  82 **The Problem**: `LIKE '%value'` cannot use indexes and scans all records.
  83 
  84 ```apex
  85 // ❌ ANTI-PATTERN: Leading wildcard
  86 SELECT Id FROM Account WHERE Name LIKE '%Corporation'
  87 // Cannot use index - full table scan
  88 ```
  89 
  90 **The Solution**: Use trailing wildcards or exact matches.
  91 
  92 ```apex
  93 // ✅ CORRECT: Trailing wildcard (uses index)
  94 SELECT Id FROM Account WHERE Name LIKE 'Acme%'
  95 
  96 // ✅ CORRECT: Exact match
  97 SELECT Id FROM Account WHERE Name = 'Acme Corporation'
  98 
  99 // ✅ CORRECT: Contains check (if absolutely necessary)
 100 // Do the filtering in Apex after a selective query
 101 List<Account> allAccounts = [
 102     SELECT Id, Name FROM Account
 103     WHERE CreatedDate = THIS_YEAR
 104 ];
 105 List<Account> filtered = new List<Account>();
 106 for (Account a : allAccounts) {
 107     if (a.Name.contains('Corporation')) {
 108         filtered.add(a);
 109     }
 110 }
 111 ```
 112 
 113 ---
 114 
 115 ## Anti-Pattern #4: Negative Operators
 116 
 117 **The Problem**: `!=`, `NOT IN`, `NOT LIKE` often prevent index usage.
 118 
 119 ```apex
 120 // ❌ ANTI-PATTERN: Negative operators
 121 SELECT Id FROM Opportunity WHERE StageName != 'Closed Lost'
 122 SELECT Id FROM Contact WHERE AccountId NOT IN :excludedIds
 123 ```
 124 
 125 **The Solution**: Query for what you want, not what you don't want.
 126 
 127 ```apex
 128 // ✅ CORRECT: Positive filter with specific values
 129 SELECT Id FROM Opportunity
 130 WHERE StageName IN ('Prospecting', 'Qualification', 'Proposal', 'Negotiation')
 131 
 132 // ✅ CORRECT: Use a formula field for complex exclusions
 133 // Create IsExcluded__c formula, then:
 134 SELECT Id FROM Contact WHERE IsExcluded__c = false
 135 ```
 136 
 137 ---
 138 
 139 ## Anti-Pattern #5: Querying for NULL
 140 
 141 **The Problem**: `WHERE Field = null` is non-selective and scans all records.
 142 
 143 ```apex
 144 // ❌ ANTI-PATTERN: Null check in WHERE
 145 SELECT Id FROM Contact WHERE Email = null
 146 // Non-selective - scans all contacts
 147 ```
 148 
 149 **The Solution**: Combine with selective filters or redesign data model.
 150 
 151 ```apex
 152 // ✅ CORRECT: Add selective filter
 153 SELECT Id FROM Contact
 154 WHERE Email = null
 155 AND CreatedDate = LAST_N_DAYS:30
 156 
 157 // ✅ BETTER: Use a checkbox field
 158 // Create HasEmail__c formula checkbox
 159 SELECT Id FROM Contact WHERE HasEmail__c = false
 160 ```
 161 
 162 ---
 163 
 164 ## Anti-Pattern #6: SELECT * (All Fields)
 165 
 166 **The Problem**: Querying all fields wastes resources and can hit heap limits.
 167 
 168 ```apex
 169 // ❌ ANTI-PATTERN: Selecting everything
 170 SELECT FIELDS(ALL) FROM Account LIMIT 200
 171 // Loads ALL fields into memory
 172 
 173 // ❌ ANTI-PATTERN: Listing every field manually
 174 SELECT Id, Name, Description, BillingStreet, BillingCity,
 175        BillingState, BillingPostalCode, BillingCountry, ...
 176 FROM Account
 177 ```
 178 
 179 **The Solution**: Query only the fields you need.
 180 
 181 ```apex
 182 // ✅ CORRECT: Minimal field selection
 183 SELECT Id, Name, Industry FROM Account
 184 
 185 // ✅ FOR DISPLAY: Just display fields
 186 SELECT Id, Name FROM Account
 187 
 188 // ✅ FOR PROCESSING: Just processing fields
 189 SELECT Id, Status__c, ProcessedDate__c FROM Account
 190 ```
 191 
 192 ---
 193 
 194 ## Anti-Pattern #7: No LIMIT on Queries
 195 
 196 **The Problem**: Unbounded queries can return 50,000 records and consume heap memory.
 197 
 198 ```apex
 199 // ❌ ANTI-PATTERN: No limit
 200 SELECT Id, Name FROM Account
 201 // Could return 50,000 records!
 202 
 203 // ❌ ANTI-PATTERN: Excessive limit
 204 SELECT Id, Name FROM Account LIMIT 50000
 205 ```
 206 
 207 **The Solution**: Use appropriate limits for your use case.
 208 
 209 ```apex
 210 // ✅ CORRECT: Reasonable limit for UI display
 211 SELECT Id, Name FROM Account LIMIT 200
 212 
 213 // ✅ CORRECT: Pagination
 214 SELECT Id, Name FROM Account
 215 ORDER BY Name
 216 LIMIT 50 OFFSET 0
 217 
 218 // ✅ CORRECT: Single record lookup
 219 SELECT Id, Name FROM Account WHERE Name = 'Acme' LIMIT 1
 220 
 221 // ✅ CORRECT: Existence check
 222 SELECT Id FROM Account WHERE Name = 'Acme' LIMIT 1
 223 // In Apex: if (!results.isEmpty()) { /* exists */ }
 224 ```
 225 
 226 ---
 227 
 228 ## Anti-Pattern #8: Deep Relationship Traversal
 229 
 230 **The Problem**: Deep nesting (>3 levels) hurts performance and readability.
 231 
 232 ```apex
 233 // ❌ ANTI-PATTERN: Deep traversal
 234 SELECT Id,
 235        Account.Owner.Manager.Department.Name
 236 FROM Contact
 237 // 4 levels deep - hard to maintain, performance hit
 238 ```
 239 
 240 **The Solution**: Flatten queries or use multiple queries.
 241 
 242 ```apex
 243 // ✅ CORRECT: Flatten to 1-2 levels
 244 SELECT Id, Account.Name, Account.OwnerId FROM Contact
 245 
 246 // Then query Owner separately if needed
 247 Map<Id, User> owners = new Map<Id, User>(
 248     [SELECT Id, ManagerId FROM User WHERE Id IN :ownerIds]
 249 );
 250 ```
 251 
 252 ---
 253 
 254 ## Anti-Pattern #9: Unfiltered Subqueries
 255 
 256 **The Problem**: Child subqueries without filters can return massive datasets.
 257 
 258 ```apex
 259 // ❌ ANTI-PATTERN: Unfiltered subquery
 260 SELECT Id,
 261        (SELECT Id FROM Contacts),
 262        (SELECT Id FROM Opportunities)
 263 FROM Account
 264 // Could return thousands of child records per account
 265 ```
 266 
 267 **The Solution**: Always filter and limit subqueries.
 268 
 269 ```apex
 270 // ✅ CORRECT: Filtered and limited subqueries
 271 SELECT Id,
 272        (SELECT Id, Name FROM Contacts
 273         WHERE IsActive__c = true
 274         LIMIT 5),
 275        (SELECT Id, Name FROM Opportunities
 276         WHERE StageName != 'Closed Lost'
 277         LIMIT 5)
 278 FROM Account
 279 WHERE Industry = 'Technology'
 280 ```
 281 
 282 ---
 283 
 284 ## Anti-Pattern #10: Formula Fields in WHERE
 285 
 286 **The Problem**: Formula fields are not indexed and require full table scans.
 287 
 288 ```apex
 289 // ❌ ANTI-PATTERN: Filter on formula field
 290 SELECT Id FROM Opportunity
 291 WHERE Days_Since_Created__c > 30
 292 // Formula field - cannot use index
 293 ```
 294 
 295 **The Solution**: Use the underlying indexed field.
 296 
 297 ```apex
 298 // ✅ CORRECT: Use base field
 299 SELECT Id FROM Opportunity
 300 WHERE CreatedDate < LAST_N_DAYS:30
 301 
 302 // ✅ ALTERNATIVE: Store computed value in regular field
 303 // Use workflow/flow to update a Number field
 304 SELECT Id FROM Opportunity
 305 WHERE Days_Open__c > 30
 306 ```
 307 
 308 ---
 309 
 310 ## Quick Reference: Selectivity Rules
 311 
 312 ```
 313 A filter is SELECTIVE when:
 314 ├── Uses an indexed field, AND
 315 ├── Returns < 10% of first million records, OR
 316 ├── Returns < 5% of records beyond first million
 317 └── Absolute max: 333,333 records (1M / 3)
 318 ```
 319 
 320 **Always Indexed Fields**:
 321 - `Id`, `Name`, `OwnerId`, `CreatedDate`, `LastModifiedDate`
 322 - `RecordTypeId`, External ID fields, Master-Detail relationship fields
 323 
 324 **Request Custom Index**: Contact Salesforce Support with:
 325 - Object name and field API name
 326 - Sample SOQL query
 327 - Cardinality (unique values count)
 328 - Business justification
 329 
 330 ---
 331 
 332 ## Testing Checklist
 333 
 334 Before deploying SOQL to production:
 335 
 336 1. [ ] Run Query Plan tool (Developer Console or CLI)
 337 2. [ ] Verify `LeadingOperationType` is "Index" not "TableScan"
 338 3. [ ] Test with 200+ records in trigger context
 339 4. [ ] Verify query count stays under 100 per transaction
 340 5. [ ] Check heap usage for large result sets
 341 
 342 ```bash
 343 # CLI Query Plan
 344 sf data query \
 345   --query "SELECT Id FROM Account WHERE Name = 'Test'" \
 346   --target-org my-org \
 347   --use-tooling-api \
 348   --plan
 349 ```
