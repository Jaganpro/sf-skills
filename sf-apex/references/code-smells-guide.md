<!-- Parent: sf-apex/SKILL.md -->
   1 # Code Smells & Refactoring Guide
   2 
   3 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
   4 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
   5 
   6 ## Overview
   7 
   8 Code smells are patterns that indicate potential problems in code structure. This guide helps identify common smells in Apex and provides refactoring strategies.
   9 
  10 ---
  11 
  12 ## 1. Long Methods
  13 
  14 ### The Smell
  15 
  16 Methods exceeding 20-30 lines, doing too much, hard to test in isolation.
  17 
  18 ### Signs
  19 
  20 - Method name is vague (`processData`, `handleStuff`)
  21 - Multiple levels of nesting
  22 - Many local variables
  23 - Comments separating "sections" of work
  24 
  25 ### Before
  26 
  27 ```apex
  28 public void processOpportunity(Opportunity opp) {
  29     // Validate opportunity
  30     if (opp == null) {
  31         throw new IllegalArgumentException('Opportunity cannot be null');
  32     }
  33     if (opp.AccountId == null) {
  34         throw new IllegalArgumentException('Account is required');
  35     }
  36     if (opp.Amount == null || opp.Amount <= 0) {
  37         throw new IllegalArgumentException('Valid amount required');
  38     }
  39 
  40     // Calculate discount
  41     Account acc = [SELECT Type, AnnualRevenue FROM Account WHERE Id = :opp.AccountId];
  42     Decimal discountRate = 0;
  43     if (acc.Type == 'Enterprise') {
  44         if (acc.AnnualRevenue > 1000000) {
  45             discountRate = 0.20;
  46         } else {
  47             discountRate = 0.15;
  48         }
  49     } else if (acc.Type == 'Partner') {
  50         discountRate = 0.10;
  51     }
  52     opp.Discount__c = opp.Amount * discountRate;
  53 
  54     // Assign to team
  55     if (opp.Amount > 100000) {
  56         opp.OwnerId = getEnterpriseTeamQueue();
  57     } else if (opp.Amount > 25000) {
  58         opp.OwnerId = getMidMarketQueue();
  59     }
  60 
  61     // Send notifications
  62     if (discountRate > 0.15) {
  63         sendApprovalRequest(opp);
  64     }
  65     if (opp.Amount > 500000) {
  66         notifyExecutiveTeam(opp);
  67     }
  68 
  69     update opp;
  70 }
  71 ```
  72 
  73 ### After
  74 
  75 ```apex
  76 public void processOpportunity(Opportunity opp) {
  77     validateOpportunity(opp);
  78 
  79     Account account = getAccountForOpportunity(opp);
  80     applyDiscount(opp, account);
  81     assignToAppropriateTeam(opp);
  82     sendRequiredNotifications(opp);
  83 
  84     update opp;
  85 }
  86 
  87 private void validateOpportunity(Opportunity opp) {
  88     if (opp == null) {
  89         throw new IllegalArgumentException('Opportunity cannot be null');
  90     }
  91     if (opp.AccountId == null) {
  92         throw new IllegalArgumentException('Account is required');
  93     }
  94     if (opp.Amount == null || opp.Amount <= 0) {
  95         throw new IllegalArgumentException('Valid amount required');
  96     }
  97 }
  98 
  99 private Account getAccountForOpportunity(Opportunity opp) {
 100     return [SELECT Type, AnnualRevenue FROM Account WHERE Id = :opp.AccountId];
 101 }
 102 
 103 private void applyDiscount(Opportunity opp, Account account) {
 104     Decimal discountRate = DiscountRules.calculateRate(account);
 105     opp.Discount__c = opp.Amount * discountRate;
 106 }
 107 
 108 private void assignToAppropriateTeam(Opportunity opp) {
 109     opp.OwnerId = TeamAssignment.getQueueForAmount(opp.Amount);
 110 }
 111 
 112 private void sendRequiredNotifications(Opportunity opp) {
 113     NotificationService.sendIfRequired(opp);
 114 }
 115 ```
 116 
 117 ### When to Extract
 118 
 119 Extract a method when:
 120 - The code block can be understood independently
 121 - It doesn't require knowledge of the caller's implementation
 122 - It serves a purpose beyond the immediate use case
 123 - You find yourself writing a comment to explain what a section does
 124 
 125 ---
 126 
 127 ## 2. Mixed Abstraction Levels
 128 
 129 ### The Smell
 130 
 131 A method mixing high-level orchestration with low-level implementation details.
 132 
 133 ### Signs
 134 
 135 - Business logic alongside HTTP request building
 136 - Validation mixed with string manipulation
 137 - SOQL queries interspersed with notification logic
 138 
 139 ### Before
 140 
 141 ```apex
 142 public void processNewCustomer(Account account) {
 143     // HIGH-LEVEL: Validation
 144     validateAccount(account);
 145 
 146     // LOW-LEVEL: String manipulation
 147     String sanitizedPhone = account.Phone.replaceAll('[^0-9]', '');
 148     if (sanitizedPhone.length() == 10) {
 149         sanitizedPhone = '1' + sanitizedPhone;
 150     }
 151     account.Phone = '+' + sanitizedPhone;
 152 
 153     // HIGH-LEVEL: Save
 154     insert account;
 155 
 156     // LOW-LEVEL: HTTP details
 157     HttpRequest req = new HttpRequest();
 158     req.setEndpoint('https://api.crm.com/customers');
 159     req.setMethod('POST');
 160     req.setHeader('Content-Type', 'application/json');
 161     req.setBody(JSON.serialize(account));
 162     Http http = new Http();
 163     HttpResponse res = http.send(req);
 164 
 165     // HIGH-LEVEL: Notification
 166     sendWelcomeEmail(account);
 167 }
 168 ```
 169 
 170 ### After
 171 
 172 ```apex
 173 public void processNewCustomer(Account account) {
 174     validateAccount(account);
 175     normalizePhoneNumber(account);
 176     insert account;
 177     syncToExternalCRM(account);
 178     sendWelcomeEmail(account);
 179 }
 180 
 181 private void normalizePhoneNumber(Account account) {
 182     if (String.isBlank(account.Phone)) return;
 183 
 184     String digitsOnly = account.Phone.replaceAll('[^0-9]', '');
 185     if (digitsOnly.length() == 10) {
 186         digitsOnly = '1' + digitsOnly;
 187     }
 188     account.Phone = '+' + digitsOnly;
 189 }
 190 
 191 private void syncToExternalCRM(Account account) {
 192     ExternalCRMService.syncCustomer(account);
 193 }
 194 ```
 195 
 196 ### Principle
 197 
 198 Each method should operate at **one level of abstraction**. High-level methods orchestrate; low-level methods implement.
 199 
 200 ---
 201 
 202 ## 3. Boolean Parameter Proliferation
 203 
 204 ### The Smell
 205 
 206 Methods with multiple boolean parameters that control behavior.
 207 
 208 ### Signs
 209 
 210 - Method calls like `process(acc, true, false, true)`
 211 - Hard to remember which boolean does what
 212 - Many if/else branches based on parameters
 213 
 214 ### Before
 215 
 216 ```apex
 217 public void createCase(
 218     String subject,
 219     String description,
 220     Id accountId,
 221     Boolean sendEmail,
 222     Boolean highPriority,
 223     Boolean assignToQueue,
 224     String origin
 225 ) {
 226     Case c = new Case(Subject = subject, Description = description);
 227     if (highPriority) {
 228         c.Priority = 'High';
 229     }
 230     if (assignToQueue) {
 231         c.OwnerId = getDefaultQueue();
 232     }
 233     // ... more conditionals
 234 }
 235 
 236 // Caller - which boolean is which?
 237 createCase('Issue', 'Desc', accId, true, false, true, 'Web');
 238 ```
 239 
 240 ### After: Options Object Pattern
 241 
 242 ```apex
 243 public class CaseOptions {
 244     public Boolean sendEmail = false;
 245     public Boolean highPriority = false;
 246     public Boolean assignToQueue = true;
 247     public String origin = 'Web';
 248 
 249     public CaseOptions withEmail() {
 250         this.sendEmail = true;
 251         return this;
 252     }
 253 
 254     public CaseOptions withHighPriority() {
 255         this.highPriority = true;
 256         return this;
 257     }
 258 
 259     public CaseOptions withOrigin(String origin) {
 260         this.origin = origin;
 261         return this;
 262     }
 263 }
 264 
 265 public Case createCase(String subject, String description, Id accountId, CaseOptions options) {
 266     Case c = new Case(
 267         Subject = subject,
 268         Description = description,
 269         AccountId = accountId,
 270         Priority = options.highPriority ? 'High' : 'Medium',
 271         Origin = options.origin
 272     );
 273 
 274     if (options.assignToQueue) {
 275         c.OwnerId = getDefaultQueue();
 276     }
 277 
 278     insert c;
 279 
 280     if (options.sendEmail) {
 281         sendCaseConfirmation(c);
 282     }
 283 
 284     return c;
 285 }
 286 
 287 // Clear, self-documenting caller
 288 Case newCase = createCase(
 289     'Login Issue',
 290     'Cannot access account',
 291     accountId,
 292     new CaseOptions()
 293         .withEmail()
 294         .withHighPriority()
 295         .withOrigin('Phone')
 296 );
 297 ```
 298 
 299 ---
 300 
 301 ## 4. Magic Numbers and Strings
 302 
 303 ### The Smell
 304 
 305 Hardcoded values scattered throughout code without explanation.
 306 
 307 ### Signs
 308 
 309 - Numbers like `5`, `100`, `1000000` without context
 310 - String literals like `'Enterprise'`, `'Active'`
 311 - Same value repeated in multiple places
 312 
 313 ### Before
 314 
 315 ```apex
 316 if (account.AnnualRevenue > 1000000) {
 317     if (retryCount < 5) {
 318         if (account.Type == 'Enterprise') {
 319             // process
 320         }
 321     }
 322 }
 323 
 324 // Elsewhere in code
 325 if (customer.Revenue__c > 1000000) { }  // Same threshold, different field
 326 ```
 327 
 328 ### After
 329 
 330 ```apex
 331 public class AccountConstants {
 332     public static final Decimal HIGH_VALUE_THRESHOLD = 1000000;
 333     public static final Integer MAX_RETRY_ATTEMPTS = 5;
 334     public static final String TYPE_ENTERPRISE = 'Enterprise';
 335     public static final String TYPE_PARTNER = 'Partner';
 336     public static final String STATUS_ACTIVE = 'Active';
 337 }
 338 
 339 // Usage
 340 if (account.AnnualRevenue > AccountConstants.HIGH_VALUE_THRESHOLD) {
 341     if (retryCount < AccountConstants.MAX_RETRY_ATTEMPTS) {
 342         if (account.Type == AccountConstants.TYPE_ENTERPRISE) {
 343             // process
 344         }
 345     }
 346 }
 347 ```
 348 
 349 ### Benefits
 350 
 351 - Single source of truth
 352 - Self-documenting code
 353 - Easy to change values globally
 354 - Prevents typos in string literals
 355 
 356 ---
 357 
 358 ## 5. Complex Conditionals
 359 
 360 ### The Smell
 361 
 362 Long, nested boolean expressions that are hard to understand.
 363 
 364 ### Signs
 365 
 366 - Multiple `&&` and `||` in one expression
 367 - Negations of negations
 368 - Conditions spanning multiple lines without names
 369 
 370 ### Before
 371 
 372 ```apex
 373 if (account.Type == 'Enterprise' &&
 374     account.AnnualRevenue > 1000000 &&
 375     account.NumberOfEmployees > 500 &&
 376     (account.Industry == 'Technology' || account.Industry == 'Finance') &&
 377     account.BillingCountry == 'United States' &&
 378     account.Rating == 'Hot') {
 379     // 50 lines of logic
 380 }
 381 ```
 382 
 383 ### After: Named Boolean Variables
 384 
 385 ```apex
 386 Boolean isEnterpriseCustomer = account.Type == 'Enterprise';
 387 Boolean isHighValue = account.AnnualRevenue > 1000000;
 388 Boolean isLargeCompany = account.NumberOfEmployees > 500;
 389 Boolean isTargetIndustry = account.Industry == 'Technology' ||
 390                            account.Industry == 'Finance';
 391 Boolean isDomestic = account.BillingCountry == 'United States';
 392 Boolean isHotLead = account.Rating == 'Hot';
 393 
 394 Boolean isStrategicAccount = isEnterpriseCustomer &&
 395                               isHighValue &&
 396                               isLargeCompany &&
 397                               isTargetIndustry &&
 398                               isDomestic &&
 399                               isHotLead;
 400 
 401 if (isStrategicAccount) {
 402     processStrategicAccount(account);
 403 }
 404 ```
 405 
 406 ### Even Better: Domain Class
 407 
 408 ```apex
 409 // Reusable business rules
 410 public class AccountRules {
 411     public static Boolean isStrategicAccount(Account account) {
 412         return isEnterpriseCustomer(account) &&
 413                isHighValue(account) &&
 414                isInTargetMarket(account);
 415     }
 416 
 417     public static Boolean isEnterpriseCustomer(Account account) {
 418         return account.Type == 'Enterprise' &&
 419                account.NumberOfEmployees > 500;
 420     }
 421 
 422     public static Boolean isHighValue(Account account) {
 423         return account.AnnualRevenue != null &&
 424                account.AnnualRevenue > 1000000;
 425     }
 426 
 427     public static Boolean isInTargetMarket(Account account) {
 428         Set<String> targetIndustries = new Set<String>{'Technology', 'Finance'};
 429         return targetIndustries.contains(account.Industry) &&
 430                account.BillingCountry == 'United States';
 431     }
 432 }
 433 
 434 // Clean usage
 435 if (AccountRules.isStrategicAccount(account)) {
 436     processStrategicAccount(account);
 437 }
 438 ```
 439 
 440 ---
 441 
 442 ## 6. Duplicate Code
 443 
 444 ### The Smell
 445 
 446 Same or similar code repeated in multiple places.
 447 
 448 ### Signs
 449 
 450 - Copy-paste patterns
 451 - Same SOQL query in multiple methods
 452 - Similar validation logic across classes
 453 
 454 ### Before
 455 
 456 ```apex
 457 // In AccountService
 458 public void processAccount(Id accountId) {
 459     Account acc = [
 460         SELECT Id, Name, Type, Industry, AnnualRevenue, OwnerId
 461         FROM Account
 462         WHERE Id = :accountId
 463     ];
 464     // process
 465 }
 466 
 467 // In ReportingService
 468 public void generateReport(Id accountId) {
 469     Account acc = [
 470         SELECT Id, Name, Type, Industry, AnnualRevenue, OwnerId
 471         FROM Account
 472         WHERE Id = :accountId
 473     ];
 474     // generate
 475 }
 476 
 477 // In IntegrationService
 478 public void syncAccount(Id accountId) {
 479     Account acc = [
 480         SELECT Id, Name, Type, Industry, AnnualRevenue, OwnerId
 481         FROM Account
 482         WHERE Id = :accountId
 483     ];
 484     // sync
 485 }
 486 ```
 487 
 488 ### After: Selector Pattern
 489 
 490 ```apex
 491 public class AccountSelector {
 492     private static final Set<String> STANDARD_FIELDS = new Set<String>{
 493         'Id', 'Name', 'Type', 'Industry', 'AnnualRevenue', 'OwnerId'
 494     };
 495 
 496     public Account selectById(Id accountId) {
 497         List<Account> accounts = selectByIds(new Set<Id>{accountId});
 498         return accounts.isEmpty() ? null : accounts[0];
 499     }
 500 
 501     public List<Account> selectByIds(Set<Id> accountIds) {
 502         if (accountIds == null || accountIds.isEmpty()) {
 503             return new List<Account>();
 504         }
 505         return [
 506             SELECT Id, Name, Type, Industry, AnnualRevenue, OwnerId
 507             FROM Account
 508             WHERE Id IN :accountIds
 509         ];
 510     }
 511 }
 512 
 513 // All services use the selector
 514 AccountSelector selector = new AccountSelector();
 515 Account acc = selector.selectById(accountId);
 516 ```
 517 
 518 ---
 519 
 520 ## 7. Deep Nesting
 521 
 522 ### The Smell
 523 
 524 Code with many levels of indentation, often from nested if statements.
 525 
 526 ### Signs
 527 
 528 - 4+ levels of nesting
 529 - Business logic hidden deep in conditionals
 530 - Hard to follow execution flow
 531 
 532 ### Solution: Guard Clauses
 533 
 534 See [Best Practices: Guard Clauses](best-practices.md#10-guard-clauses--fail-fast) for detailed refactoring patterns.
 535 
 536 ---
 537 
 538 ## 8. God Class
 539 
 540 ### The Smell
 541 
 542 A class that knows too much or does too much.
 543 
 544 ### Signs
 545 
 546 - Hundreds or thousands of lines
 547 - Many unrelated methods
 548 - Class name is vague (`Utility`, `Helper`, `Manager`)
 549 - Changes to any feature require modifying this class
 550 
 551 ### Solution
 552 
 553 Split by responsibility:
 554 - Extract domain classes for business rules
 555 - Create selectors for data access
 556 - Separate services for different business operations
 557 - Use interfaces for dependency injection
 558 
 559 See [Design Patterns: Domain Class Pattern](design-patterns.md#domain-class-pattern) for implementation guidance.
 560 
 561 ---
 562 
 563 ## Refactoring Decision Guide
 564 
 565 | Smell | Quick Fix | Proper Fix |
 566 |-------|-----------|------------|
 567 | Long method | Extract method | Separate concerns into classes |
 568 | Mixed abstraction | Extract low-level to methods | Create abstraction layers |
 569 | Boolean parameters | Options object | Strategy pattern |
 570 | Magic numbers | Named constants | Configuration class |
 571 | Complex conditionals | Named booleans | Domain class |
 572 | Duplicate code | Extract method | Selector/Service pattern |
 573 | Deep nesting | Guard clauses | Command pattern |
 574 | God class | Split methods | Proper architecture |
 575 
 576 ---
 577 
 578 ## When NOT to Refactor
 579 
 580 - **Working code under deadline**: Don't refactor what you don't have time to test
 581 - **No tests exist**: Write tests first, then refactor
 582 - **Code is being deprecated**: Don't polish what's being removed
 583 - **Premature abstraction**: Wait until you have 3 concrete examples before abstracting
 584 
 585 ---
 586 
 587 ## Testing After Refactoring
 588 
 589 Every refactoring should be validated:
 590 
 591 1. **Run existing tests** - They should still pass
 592 2. **Check code coverage** - Coverage shouldn't drop
 593 3. **Verify behavior** - Same inputs produce same outputs
 594 4. **Performance check** - No significant degradation
 595 
 596 If tests fail after refactoring that shouldn't change behavior, you've introduced a bug, not just refactored.
