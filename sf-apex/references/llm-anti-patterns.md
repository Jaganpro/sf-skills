<!-- Parent: sf-apex/SKILL.md -->
   1 # LLM-Specific Anti-Patterns in Apex
   2 
   3 This guide documents systematic errors that LLMs (including Claude) commonly make when generating Salesforce Apex code. These patterns are critical to validate in generated code.
   4 
   5 > **Source**: [LLM Mistakes in Apex & LWC - Salesforce Diaries](https://salesforcediaries.com/2026/01/16/llm-mistakes-in-apex-lwc-salesforce-code-generation-rules/)
   6 
   7 ---
   8 
   9 ## Table of Contents
  10 
  11 1. [Non-Existent Methods](#1-non-existent-methods)
  12 2. [Java Types Instead of Apex Types](#2-java-types-instead-of-apex-types)
  13 3. [Map Access Without Null Safety](#3-map-access-without-null-safety)
  14 4. [Missing SOQL Fields](#4-missing-soql-fields)
  15 5. [Recursive Trigger Loops](#5-recursive-trigger-loops)
  16 6. [Invalid InvocableVariable Types](#6-invalid-invocablevariable-types)
  17 7. [Missing @JsonAccess Annotations](#7-missing-jsonaccess-annotations)
  18 8. [Null Pointer from Missing Checks](#8-null-pointer-from-missing-checks)
  19 9. [Incorrect DateTime Methods](#9-incorrect-datetime-methods)
  20 10. [Collection Initialization Patterns](#10-collection-initialization-patterns)
  21 
  22 ---
  23 
  24 ## 1. Non-Existent Methods
  25 
  26 LLMs often hallucinate methods that don't exist in Apex, borrowing syntax from Java or other languages.
  27 
  28 ### Common Hallucinated Methods
  29 
  30 | Hallucinated Method | What LLM Expected | Correct Apex Alternative |
  31 |---------------------|-------------------|--------------------------|
  32 | `Datetime.addMilliseconds()` | Add milliseconds | `Datetime.addSeconds(ms/1000)` |
  33 | `String.isEmpty(str)` | Static empty check | `String.isBlank(str)` |
  34 | `List.stream()` | Java streams | Use `for` loops |
  35 | `Map.getOrDefault()` | Default value | `map.get(key) ?? defaultValue` |
  36 | `String.format()` | String formatting | `String.format()` exists but with different syntax |
  37 | `Object.equals()` | Equality check | Use `==` or custom method |
  38 | `List.sort(comparator)` | Custom sorting | Implement `Comparable` interface |
  39 | `String.join(list)` | Join with delimiter | `String.join(list, delimiter)` |
  40 
  41 ### ❌ BAD: Hallucinated Datetime Method
  42 
  43 ```apex
  44 // LLM generates this - DOES NOT EXIST
  45 Datetime future = Datetime.now().addMilliseconds(500);
  46 ```
  47 
  48 ### ✅ GOOD: Correct Apex Pattern
  49 
  50 ```apex
  51 // Apex has no millisecond precision - use seconds
  52 Datetime future = Datetime.now().addSeconds(1);
  53 
  54 // For sub-second timing, use System.currentTimeMillis()
  55 Long startMs = System.currentTimeMillis();
  56 // ... operation ...
  57 Long elapsedMs = System.currentTimeMillis() - startMs;
  58 ```
  59 
  60 ### ❌ BAD: Java Stream Syntax
  61 
  62 ```apex
  63 // LLM generates this - Java streams don't exist in Apex
  64 List<String> names = accounts.stream()
  65     .map(a -> a.Name)
  66     .collect(Collectors.toList());
  67 ```
  68 
  69 ### ✅ GOOD: Apex Loop Pattern
  70 
  71 ```apex
  72 // Use traditional loops in Apex
  73 List<String> names = new List<String>();
  74 for (Account a : accounts) {
  75     names.add(a.Name);
  76 }
  77 ```
  78 
  79 ---
  80 
  81 ## 2. Java Types Instead of Apex Types
  82 
  83 LLMs trained on Java code often use Java collection types that don't exist in Apex.
  84 
  85 ### Java Types to Avoid
  86 
  87 | Java Type | Apex Equivalent |
  88 |-----------|-----------------|
  89 | `ArrayList<T>` | `List<T>` |
  90 | `HashMap<K,V>` | `Map<K,V>` |
  91 | `HashSet<T>` | `Set<T>` |
  92 | `StringBuffer` | `String` (immutable) or `List<String>` + `String.join()` |
  93 | `StringBuilder` | `String` (immutable) or `List<String>` + `String.join()` |
  94 | `LinkedList<T>` | `List<T>` |
  95 | `TreeMap<K,V>` | `Map<K,V>` (no ordering guarantee) |
  96 | `Vector<T>` | `List<T>` |
  97 | `Hashtable<K,V>` | `Map<K,V>` |
  98 
  99 ### ❌ BAD: Java Collection Types
 100 
 101 ```apex
 102 // LLM generates these - COMPILE ERROR
 103 ArrayList<Account> accounts = new ArrayList<Account>();
 104 HashMap<Id, Contact> contactMap = new HashMap<Id, Contact>();
 105 StringBuilder sb = new StringBuilder();
 106 ```
 107 
 108 ### ✅ GOOD: Apex Native Types
 109 
 110 ```apex
 111 // Apex uses these types
 112 List<Account> accounts = new List<Account>();
 113 Map<Id, Contact> contactMap = new Map<Id, Contact>();
 114 
 115 // For string concatenation
 116 String result = '';
 117 for (String s : parts) {
 118     result += s;  // OK for small strings
 119 }
 120 
 121 // For large string building
 122 List<String> parts = new List<String>();
 123 parts.add('Part 1');
 124 parts.add('Part 2');
 125 String result = String.join(parts, '');
 126 ```
 127 
 128 ### Detection Rule
 129 
 130 ```
 131 REGEX: \b(ArrayList|HashMap|HashSet|StringBuffer|StringBuilder|LinkedList|TreeMap|Vector|Hashtable)\s*<
 132 SEVERITY: CRITICAL
 133 MESSAGE: Java type "{match}" does not exist in Apex. Use Apex native collections.
 134 ```
 135 
 136 ---
 137 
 138 ## 3. Map Access Without Null Safety
 139 
 140 LLMs often use `Map.get()` without checking if the key exists, causing null pointer exceptions.
 141 
 142 ### ❌ BAD: Unsafe Map Access
 143 
 144 ```apex
 145 Map<Id, Account> accountMap = new Map<Id, Account>([SELECT Id, Name FROM Account]);
 146 
 147 for (Contact c : contacts) {
 148     // DANGER: If AccountId not in map, .Name throws NPE
 149     String accountName = accountMap.get(c.AccountId).Name;
 150 }
 151 ```
 152 
 153 ### ✅ GOOD: Safe Map Access (Option 1 - containsKey)
 154 
 155 ```apex
 156 Map<Id, Account> accountMap = new Map<Id, Account>([SELECT Id, Name FROM Account]);
 157 
 158 for (Contact c : contacts) {
 159     if (accountMap.containsKey(c.AccountId)) {
 160         String accountName = accountMap.get(c.AccountId).Name;
 161     }
 162 }
 163 ```
 164 
 165 ### ✅ GOOD: Safe Map Access (Option 2 - Null Check)
 166 
 167 ```apex
 168 Map<Id, Account> accountMap = new Map<Id, Account>([SELECT Id, Name FROM Account]);
 169 
 170 for (Contact c : contacts) {
 171     Account acc = accountMap.get(c.AccountId);
 172     if (acc != null) {
 173         String accountName = acc.Name;
 174     }
 175 }
 176 ```
 177 
 178 ### ✅ GOOD: Safe Map Access (Option 3 - Safe Navigation)
 179 
 180 ```apex
 181 Map<Id, Account> accountMap = new Map<Id, Account>([SELECT Id, Name FROM Account]);
 182 
 183 for (Contact c : contacts) {
 184     // Safe navigation operator (?.) - returns null if key not found
 185     String accountName = accountMap.get(c.AccountId)?.Name;
 186     if (accountName != null) {
 187         // Process
 188     }
 189 }
 190 ```
 191 
 192 ### ✅ GOOD: Safe Map Access (Option 4 - Null Coalescing)
 193 
 194 ```apex
 195 Map<Id, Account> accountMap = new Map<Id, Account>([SELECT Id, Name FROM Account]);
 196 
 197 for (Contact c : contacts) {
 198     // Null coalescing operator (??) for default values
 199     String accountName = accountMap.get(c.AccountId)?.Name ?? 'Unknown';
 200 }
 201 ```
 202 
 203 ---
 204 
 205 ## 4. Missing SOQL Fields
 206 
 207 LLMs often query fields but then access different fields not in the SELECT clause.
 208 
 209 ### ❌ BAD: Accessing Unqueried Fields
 210 
 211 ```apex
 212 // Only querying Id and Name
 213 List<Account> accounts = [SELECT Id, Name FROM Account];
 214 
 215 for (Account acc : accounts) {
 216     // RUNTIME ERROR: Industry was not queried!
 217     if (acc.Industry == 'Technology') {
 218         acc.Description = 'Tech company';  // Description also not queried!
 219     }
 220 }
 221 ```
 222 
 223 ### ✅ GOOD: Query All Accessed Fields
 224 
 225 ```apex
 226 // Query all fields that will be accessed
 227 List<Account> accounts = [SELECT Id, Name, Industry, Description FROM Account];
 228 
 229 for (Account acc : accounts) {
 230     if (acc.Industry == 'Technology') {
 231         acc.Description = 'Tech company';
 232     }
 233 }
 234 ```
 235 
 236 ### ❌ BAD: Missing Relationship Fields
 237 
 238 ```apex
 239 // Missing Account.Name in query
 240 List<Contact> contacts = [SELECT Id, Name, AccountId FROM Contact];
 241 
 242 for (Contact c : contacts) {
 243     // RUNTIME ERROR: Account.Name not queried
 244     System.debug('Account: ' + c.Account.Name);
 245 }
 246 ```
 247 
 248 ### ✅ GOOD: Include Relationship Fields
 249 
 250 ```apex
 251 // Include relationship fields using dot notation
 252 List<Contact> contacts = [SELECT Id, Name, AccountId, Account.Name FROM Contact];
 253 
 254 for (Contact c : contacts) {
 255     System.debug('Account: ' + c.Account.Name);  // Works!
 256 }
 257 ```
 258 
 259 ### Validation Checklist
 260 
 261 Before running code, verify:
 262 1. All fields accessed in `if` statements are queried
 263 2. All fields accessed in assignments are queried
 264 3. All relationship fields (e.g., `Account.Name`) are in SELECT
 265 4. Parent relationship uses `.` notation in query (e.g., `Contact.Account.Name`)
 266 
 267 ---
 268 
 269 ## 5. Recursive Trigger Loops
 270 
 271 LLMs often forget to add recursion prevention in triggers, causing infinite loops.
 272 
 273 ### ❌ BAD: No Recursion Prevention
 274 
 275 ```apex
 276 // Trigger that updates related records
 277 trigger AccountTrigger on Account (after update) {
 278     List<Contact> contactsToUpdate = new List<Contact>();
 279 
 280     for (Account acc : Trigger.new) {
 281         // This update might trigger another trigger, which might update Account...
 282         for (Contact c : [SELECT Id FROM Contact WHERE AccountId = :acc.Id]) {
 283             c.MailingCity = acc.BillingCity;
 284             contactsToUpdate.add(c);
 285         }
 286     }
 287 
 288     update contactsToUpdate;  // Could cause recursion!
 289 }
 290 ```
 291 
 292 ### ✅ GOOD: Static Flag Pattern
 293 
 294 ```apex
 295 // TriggerHelper.cls
 296 public class TriggerHelper {
 297     private static Boolean isFirstRun = true;
 298 
 299     public static Boolean isFirstRun() {
 300         if (isFirstRun) {
 301             isFirstRun = false;
 302             return true;
 303         }
 304         return false;
 305     }
 306 
 307     public static void reset() {
 308         isFirstRun = true;
 309     }
 310 }
 311 
 312 // AccountTrigger.trigger
 313 trigger AccountTrigger on Account (after update) {
 314     if (!TriggerHelper.isFirstRun()) {
 315         return;  // Skip on recursive calls
 316     }
 317 
 318     // ... trigger logic ...
 319 }
 320 ```
 321 
 322 ### ✅ BETTER: Set-Based Recursion Control
 323 
 324 ```apex
 325 // TriggerRecursionHandler.cls
 326 public class TriggerRecursionHandler {
 327     private static Set<Id> processedIds = new Set<Id>();
 328 
 329     public static Boolean hasProcessed(Id recordId) {
 330         return processedIds.contains(recordId);
 331     }
 332 
 333     public static void markProcessed(Id recordId) {
 334         processedIds.add(recordId);
 335     }
 336 
 337     public static void markProcessed(Set<Id> recordIds) {
 338         processedIds.addAll(recordIds);
 339     }
 340 }
 341 
 342 // In trigger handler
 343 for (Account acc : Trigger.new) {
 344     if (TriggerRecursionHandler.hasProcessed(acc.Id)) {
 345         continue;
 346     }
 347     TriggerRecursionHandler.markProcessed(acc.Id);
 348     // Process record...
 349 }
 350 ```
 351 
 352 ### ✅ BEST: Trigger Actions Framework
 353 
 354 ```apex
 355 // Use TAF for built-in recursion control via metadata
 356 // See: references/trigger-actions-framework.md
 357 ```
 358 
 359 ---
 360 
 361 ## 6. Invalid InvocableVariable Types
 362 
 363 LLMs often use unsupported types in `@InvocableVariable` annotations for Flow/Process Builder integration.
 364 
 365 ### Supported InvocableVariable Types
 366 
 367 | Category | Supported Types |
 368 |----------|----------------|
 369 | **Primitives** | `Boolean`, `Date`, `DateTime`, `Decimal`, `Double`, `Id`, `Integer`, `Long`, `String`, `Time` |
 370 | **Collections** | `List<T>` where T is a supported type |
 371 | **sObjects** | Any standard or custom sObject |
 372 | **Apex-Defined** | Classes with `@InvocableVariable` on fields |
 373 
 374 ### Unsupported Types
 375 
 376 | Type | Why Unsupported | Alternative |
 377 |------|----------------|-------------|
 378 | `Map<K,V>` | Not serializable to Flow | Use List of wrapper class |
 379 | `Set<T>` | Not serializable to Flow | Use `List<T>` |
 380 | `Object` | Too generic | Use specific type |
 381 | `Blob` | Not serializable | Use `String` (Base64) |
 382 | Custom classes without `@InvocableVariable` | Not marked for Flow | Add annotations |
 383 
 384 ### ❌ BAD: Unsupported InvocableVariable Types
 385 
 386 ```apex
 387 public class FlowInput {
 388     @InvocableVariable
 389     public Map<String, String> options;  // NOT SUPPORTED!
 390 
 391     @InvocableVariable
 392     public Set<Id> recordIds;  // NOT SUPPORTED!
 393 
 394     @InvocableVariable
 395     public Blob fileContent;  // NOT SUPPORTED!
 396 }
 397 ```
 398 
 399 ### ✅ GOOD: Supported Types with Wrapper Pattern
 400 
 401 ```apex
 402 public class FlowInput {
 403     @InvocableVariable(label='Record IDs' description='Comma-separated IDs')
 404     public List<Id> recordIds;  // List is supported
 405 
 406     @InvocableVariable(label='Options JSON' description='JSON string of options')
 407     public String optionsJson;  // Serialize Map to JSON string
 408 
 409     @InvocableVariable(label='File Content' description='Base64 encoded content')
 410     public String fileContentBase64;  // Base64 encode Blob
 411 }
 412 
 413 // In your method, deserialize as needed
 414 public static void process(List<FlowInput> inputs) {
 415     for (FlowInput input : inputs) {
 416         Map<String, String> options = (Map<String, String>)JSON.deserialize(
 417             input.optionsJson,
 418             Map<String, String>.class
 419         );
 420 
 421         Blob fileContent = EncodingUtil.base64Decode(input.fileContentBase64);
 422     }
 423 }
 424 ```
 425 
 426 ---
 427 
 428 ## 7. Missing @JsonAccess Annotations
 429 
 430 When using `JSON.serialize()` / `JSON.deserialize()` with inner classes or non-public classes, LLMs forget the `@JsonAccess` annotation required since API version 49.0.
 431 
 432 ### ❌ BAD: Missing JsonAccess
 433 
 434 ```apex
 435 public class AccountService {
 436     // Inner class without @JsonAccess - JSON.serialize() fails silently
 437     private class AccountWrapper {
 438         public String name;
 439         public String industry;
 440     }
 441 
 442     public static String getAccountsJson() {
 443         List<AccountWrapper> wrappers = new List<AccountWrapper>();
 444         // ... populate ...
 445         return JSON.serialize(wrappers);  // Returns "[]" or throws error!
 446     }
 447 }
 448 ```
 449 
 450 ### ✅ GOOD: With JsonAccess Annotation
 451 
 452 ```apex
 453 public class AccountService {
 454     @JsonAccess(serializable='always' deserializable='always')
 455     private class AccountWrapper {
 456         public String name;
 457         public String industry;
 458     }
 459 
 460     public static String getAccountsJson() {
 461         List<AccountWrapper> wrappers = new List<AccountWrapper>();
 462         // ... populate ...
 463         return JSON.serialize(wrappers);  // Works correctly!
 464     }
 465 }
 466 ```
 467 
 468 ### When @JsonAccess is Required
 469 
 470 | Class Type | Needs @JsonAccess? |
 471 |------------|-------------------|
 472 | Public top-level class | No |
 473 | Private inner class | **Yes** |
 474 | Protected inner class | **Yes** |
 475 | Public inner class | No (but recommended for clarity) |
 476 | Class used only internally | No (unless serialized) |
 477 
 478 ---
 479 
 480 ## 8. Null Pointer from Missing Checks
 481 
 482 LLMs often chain method calls without null safety, leading to null pointer exceptions.
 483 
 484 ### ❌ BAD: Chained Calls Without Null Checks
 485 
 486 ```apex
 487 // Any of these could be null!
 488 String city = [SELECT Id, Account.BillingAddress FROM Contact LIMIT 1]
 489     .Account
 490     .BillingAddress
 491     .getCity();
 492 ```
 493 
 494 ### ✅ GOOD: Safe Navigation Operator
 495 
 496 ```apex
 497 // Use ?. for safe navigation
 498 Contact c = [SELECT Id, Account.BillingCity FROM Contact LIMIT 1];
 499 String city = c?.Account?.BillingCity;
 500 
 501 // With default value
 502 String city = c?.Account?.BillingCity ?? 'Unknown';
 503 ```
 504 
 505 ### ✅ GOOD: Explicit Null Checks
 506 
 507 ```apex
 508 Contact c = [SELECT Id, Account.BillingCity FROM Contact LIMIT 1];
 509 
 510 String city = 'Unknown';
 511 if (c != null && c.Account != null && c.Account.BillingCity != null) {
 512     city = c.Account.BillingCity;
 513 }
 514 ```
 515 
 516 ---
 517 
 518 ## 9. Incorrect DateTime Methods
 519 
 520 LLMs confuse Date and DateTime methods, which have different APIs.
 521 
 522 ### Date vs DateTime Method Confusion
 523 
 524 | Operation | Date Method | DateTime Method |
 525 |-----------|-------------|-----------------|
 526 | Add days | `addDays(n)` | `addDays(n)` |
 527 | Add months | `addMonths(n)` | `addMonths(n)` |
 528 | Add years | `addYears(n)` | N/A (use `addMonths(n*12)`) |
 529 | Add hours | N/A | `addHours(n)` |
 530 | Add minutes | N/A | `addMinutes(n)` |
 531 | Add seconds | N/A | `addSeconds(n)` |
 532 | Get day | `day()` | `day()` |
 533 | Get month | `month()` | `month()` |
 534 | Get year | `year()` | `year()` |
 535 | Get hour | N/A | `hour()` |
 536 | Get minute | N/A | `minute()` |
 537 | Today | `Date.today()` | N/A |
 538 | Now | N/A | `DateTime.now()` |
 539 
 540 ### ❌ BAD: Mixing Date/DateTime Methods
 541 
 542 ```apex
 543 // Date doesn't have addHours!
 544 Date d = Date.today();
 545 Date future = d.addHours(5);  // COMPILE ERROR
 546 
 547 // DateTime doesn't have a static today()!
 548 DateTime now = DateTime.today();  // COMPILE ERROR
 549 ```
 550 
 551 ### ✅ GOOD: Correct Method Usage
 552 
 553 ```apex
 554 // For Date operations
 555 Date d = Date.today();
 556 Date future = d.addDays(5);
 557 
 558 // For DateTime operations
 559 DateTime now = DateTime.now();
 560 DateTime future = now.addHours(5);
 561 
 562 // Converting between Date and DateTime
 563 Date d = Date.today();
 564 DateTime dt = DateTime.newInstance(d, Time.newInstance(0, 0, 0, 0));
 565 
 566 DateTime dt = DateTime.now();
 567 Date d = dt.date();
 568 ```
 569 
 570 ---
 571 
 572 ## 10. Collection Initialization Patterns
 573 
 574 LLMs sometimes use incorrect patterns for initializing collections from SOQL or other collections.
 575 
 576 ### ❌ BAD: Incorrect Map Initialization
 577 
 578 ```apex
 579 // This doesn't work - can't construct Map from SOQL directly with fields
 580 Map<Id, String> nameMap = new Map<Id, String>(
 581     [SELECT Id, Name FROM Account]
 582 );  // COMPILE ERROR - wrong constructor
 583 ```
 584 
 585 ### ✅ GOOD: Correct Map Initialization
 586 
 587 ```apex
 588 // Map<Id, SObject> works directly with SOQL
 589 Map<Id, Account> accountMap = new Map<Id, Account>(
 590     [SELECT Id, Name FROM Account]
 591 );
 592 
 593 // For Map<Id, SpecificField>, use a loop
 594 Map<Id, String> nameMap = new Map<Id, String>();
 595 for (Account acc : [SELECT Id, Name FROM Account]) {
 596     nameMap.put(acc.Id, acc.Name);
 597 }
 598 ```
 599 
 600 ### ❌ BAD: List to Set Conversion
 601 
 602 ```apex
 603 // Can't directly convert List to Set in constructor
 604 List<Id> idList = new List<Id>{'001...', '001...'};
 605 Set<Id> idSet = new Set<Id>(idList);  // Actually this DOES work in Apex!
 606 ```
 607 
 608 ### ✅ GOOD: Collection Conversions
 609 
 610 ```apex
 611 // List to Set - this works!
 612 List<Id> idList = new List<Id>{'001...', '001...'};
 613 Set<Id> idSet = new Set<Id>(idList);
 614 
 615 // Set to List
 616 Set<Id> idSet = new Set<Id>{'001...', '001...'};
 617 List<Id> idList = new List<Id>(idSet);
 618 
 619 // Map keys to Set
 620 Map<Id, Account> accountMap = new Map<Id, Account>([SELECT Id FROM Account]);
 621 Set<Id> accountIds = accountMap.keySet();
 622 
 623 // Map values to List
 624 List<Account> accounts = accountMap.values();
 625 ```
 626 
 627 ---
 628 
 629 ## Quick Reference: LLM Validation Checklist
 630 
 631 Before accepting LLM-generated Apex code, verify:
 632 
 633 ### Methods & Types
 634 - [ ] No Java collection types (ArrayList, HashMap, etc.)
 635 - [ ] No hallucinated methods (addMilliseconds, stream(), etc.)
 636 - [ ] Correct Date vs DateTime methods
 637 
 638 ### Null Safety
 639 - [ ] Map.get() has null check or uses containsKey()
 640 - [ ] Chained method calls use safe navigation (?.)
 641 - [ ] SOQL results checked before accessing
 642 
 643 ### SOQL
 644 - [ ] All accessed fields are in SELECT clause
 645 - [ ] Relationship fields use dot notation in query
 646 - [ ] Parent records accessed safely
 647 
 648 ### Flow Integration
 649 - [ ] InvocableVariable uses supported types
 650 - [ ] No Map/Set in @InvocableVariable
 651 - [ ] @JsonAccess on inner classes if serialized
 652 
 653 ### Triggers
 654 - [ ] Recursion prevention mechanism in place
 655 - [ ] Static flag or processed ID tracking
 656 
 657 ---
 658 
 659 ## Detection Script
 660 
 661 Add this validation to your CI/CD pipeline:
 662 
 663 ```python
 664 # detect_llm_patterns.py
 665 import re
 666 
 667 JAVA_TYPES = [
 668     r'\bArrayList\s*<',
 669     r'\bHashMap\s*<',
 670     r'\bHashSet\s*<',
 671     r'\bStringBuffer\b',
 672     r'\bStringBuilder\b',
 673     r'\bLinkedList\s*<',
 674     r'\bTreeMap\s*<',
 675 ]
 676 
 677 HALLUCINATED_METHODS = [
 678     r'\.addMilliseconds\s*\(',
 679     r'\.stream\s*\(\)',
 680     r'\.getOrDefault\s*\(',
 681     r'DateTime\.today\s*\(\)',
 682 ]
 683 
 684 def validate_apex(content):
 685     issues = []
 686 
 687     for pattern in JAVA_TYPES:
 688         if re.search(pattern, content):
 689             issues.append(f"Java type detected: {pattern}")
 690 
 691     for pattern in HALLUCINATED_METHODS:
 692         if re.search(pattern, content):
 693             issues.append(f"Non-existent method: {pattern}")
 694 
 695     return issues
 696 ```
 697 
 698 ---
 699 
 700 ## Reference
 701 
 702 - **Existing Anti-Patterns**: See `references/anti-patterns.md` for traditional Apex anti-patterns
 703 - **Best Practices**: See `references/best-practices.md` for correct patterns
 704 - **Source**: [Salesforce Diaries - LLM Mistakes](https://salesforcediaries.com/2026/01/16/llm-mistakes-in-apex-lwc-salesforce-code-generation-rules/)
