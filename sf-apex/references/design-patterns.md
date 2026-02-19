<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Design Patterns
   2 
   3 ## Factory Pattern
   4 
   5 ### Purpose
   6 Centralize object creation, enable dependency injection, simplify testing.
   7 
   8 ### Implementation
   9 
  10 ```apex
  11 public virtual class Factory {
  12     private static Factory instance;
  13 
  14     public static Factory getInstance() {
  15         if (instance == null) {
  16             instance = new Factory();
  17         }
  18         return instance;
  19     }
  20 
  21     @TestVisible
  22     private static void setInstance(Factory mockFactory) {
  23         instance = mockFactory;
  24     }
  25 
  26     // Service getters - virtual for mocking
  27     public virtual AccountService getAccountService() {
  28         return new AccountService();
  29     }
  30 
  31     public virtual ContactService getContactService() {
  32         return new ContactService();
  33     }
  34 
  35     public virtual PaymentGateway getPaymentGateway() {
  36         return new StripePaymentGateway();
  37     }
  38 }
  39 ```
  40 
  41 ### Usage
  42 
  43 ```apex
  44 public class OrderProcessor {
  45     private AccountService accountService;
  46     private PaymentGateway gateway;
  47 
  48     public OrderProcessor() {
  49         this(Factory.getInstance());
  50     }
  51 
  52     @TestVisible
  53     private OrderProcessor(Factory factory) {
  54         this.accountService = factory.getAccountService();
  55         this.gateway = factory.getPaymentGateway();
  56     }
  57 
  58     public void process(Order__c order) {
  59         Account acc = accountService.getAccount(order.Account__c);
  60         gateway.charge(order.Total__c);
  61     }
  62 }
  63 ```
  64 
  65 ### Testing with Factory
  66 
  67 ```apex
  68 @isTest
  69 private class OrderProcessorTest {
  70 
  71     @isTest
  72     static void testProcess() {
  73         // Set mock factory
  74         Factory.setInstance(new MockFactory());
  75 
  76         OrderProcessor processor = new OrderProcessor();
  77 
  78         Test.startTest();
  79         processor.process(new Order__c());
  80         Test.stopTest();
  81 
  82         // Assertions
  83     }
  84 
  85     private class MockFactory extends Factory {
  86         public override AccountService getAccountService() {
  87             return new MockAccountService();
  88         }
  89 
  90         public override PaymentGateway getPaymentGateway() {
  91             return new MockPaymentGateway();
  92         }
  93     }
  94 }
  95 ```
  96 
  97 ---
  98 
  99 ## Repository Pattern
 100 
 101 ### Purpose
 102 Abstract data access, provide strongly-typed queries, enable DML mocking.
 103 
 104 ### Implementation
 105 
 106 ```apex
 107 public virtual class AccountRepository {
 108 
 109     public virtual List<Account> getByIds(Set<Id> accountIds) {
 110         return [
 111             SELECT Id, Name, Industry, AnnualRevenue
 112             FROM Account
 113             WHERE Id IN :accountIds
 114             WITH USER_MODE
 115         ];
 116     }
 117 
 118     public virtual List<Account> getByIndustry(String industry) {
 119         return [
 120             SELECT Id, Name, AnnualRevenue
 121             FROM Account
 122             WHERE Industry = :industry
 123             WITH USER_MODE
 124         ];
 125     }
 126 
 127     public virtual Account getById(Id accountId) {
 128         List<Account> accounts = getByIds(new Set<Id>{accountId});
 129         return accounts.isEmpty() ? null : accounts[0];
 130     }
 131 
 132     public virtual void save(List<Account> accounts) {
 133         upsert accounts;
 134     }
 135 
 136     public virtual void remove(List<Account> accounts) {
 137         delete accounts;
 138     }
 139 }
 140 ```
 141 
 142 ### Usage
 143 
 144 ```apex
 145 public class AccountService {
 146     private AccountRepository repo;
 147 
 148     public AccountService() {
 149         this.repo = new AccountRepository();
 150     }
 151 
 152     @TestVisible
 153     private AccountService(AccountRepository repo) {
 154         this.repo = repo;
 155     }
 156 
 157     public List<Account> getTechnologyAccounts() {
 158         return repo.getByIndustry('Technology');
 159     }
 160 
 161     public void updateAccounts(List<Account> accounts) {
 162         repo.save(accounts);
 163     }
 164 }
 165 ```
 166 
 167 ### Testing with Mock Repository
 168 
 169 ```apex
 170 @isTest
 171 private class AccountServiceTest {
 172 
 173     @isTest
 174     static void testGetTechnologyAccounts() {
 175         MockAccountRepository mockRepo = new MockAccountRepository();
 176         mockRepo.accountsToReturn = new List<Account>{
 177             new Account(Name = 'Test', Industry = 'Technology')
 178         };
 179 
 180         AccountService service = new AccountService(mockRepo);
 181 
 182         Test.startTest();
 183         List<Account> results = service.getTechnologyAccounts();
 184         Test.stopTest();
 185 
 186         Assert.areEqual(1, results.size());
 187         Assert.areEqual('Technology', mockRepo.lastIndustryQueried);
 188     }
 189 
 190     private class MockAccountRepository extends AccountRepository {
 191         public List<Account> accountsToReturn = new List<Account>();
 192         public String lastIndustryQueried;
 193 
 194         public override List<Account> getByIndustry(String industry) {
 195             this.lastIndustryQueried = industry;
 196             return accountsToReturn;
 197         }
 198     }
 199 }
 200 ```
 201 
 202 ---
 203 
 204 ## Selector Pattern
 205 
 206 ### Purpose
 207 Centralize SOQL queries per object, enforce security, enable reuse.
 208 
 209 ### Implementation
 210 
 211 ```apex
 212 public inherited sharing class AccountSelector {
 213 
 214     public List<Account> selectById(Set<Id> ids) {
 215         return [
 216             SELECT Id, Name, Industry, AnnualRevenue, BillingCity
 217             FROM Account
 218             WHERE Id IN :ids
 219             WITH USER_MODE
 220         ];
 221     }
 222 
 223     public List<Account> selectByIdWithContacts(Set<Id> ids) {
 224         return [
 225             SELECT Id, Name, Industry,
 226                 (SELECT Id, FirstName, LastName, Email FROM Contacts)
 227             FROM Account
 228             WHERE Id IN :ids
 229             WITH USER_MODE
 230         ];
 231     }
 232 
 233     public List<Account> selectByName(String name) {
 234         return [
 235             SELECT Id, Name, Industry
 236             FROM Account
 237             WHERE Name LIKE :('%' + name + '%')
 238             WITH USER_MODE
 239             LIMIT 100
 240         ];
 241     }
 242 
 243     public List<Account> selectActiveByIndustry(String industry) {
 244         return [
 245             SELECT Id, Name, AnnualRevenue
 246             FROM Account
 247             WHERE Industry = :industry
 248             AND Status__c = 'Active'
 249             WITH USER_MODE
 250         ];
 251     }
 252 }
 253 ```
 254 
 255 ### Usage
 256 
 257 ```apex
 258 public class AccountService {
 259     private AccountSelector selector = new AccountSelector();
 260 
 261     public Map<Id, Account> getAccountsMap(Set<Id> ids) {
 262         return new Map<Id, Account>(selector.selectById(ids));
 263     }
 264 }
 265 ```
 266 
 267 ---
 268 
 269 ## Builder Pattern
 270 
 271 ### Purpose
 272 Construct complex objects step-by-step, improve readability.
 273 
 274 ### Implementation
 275 
 276 ```apex
 277 public class AccountBuilder {
 278     private Account record;
 279 
 280     public AccountBuilder() {
 281         this.record = new Account();
 282     }
 283 
 284     public AccountBuilder withName(String name) {
 285         this.record.Name = name;
 286         return this;
 287     }
 288 
 289     public AccountBuilder withIndustry(String industry) {
 290         this.record.Industry = industry;
 291         return this;
 292     }
 293 
 294     public AccountBuilder withAnnualRevenue(Decimal revenue) {
 295         this.record.AnnualRevenue = revenue;
 296         return this;
 297     }
 298 
 299     public AccountBuilder withBillingAddress(String city, String state, String country) {
 300         this.record.BillingCity = city;
 301         this.record.BillingState = state;
 302         this.record.BillingCountry = country;
 303         return this;
 304     }
 305 
 306     public AccountBuilder withParent(Id parentId) {
 307         this.record.ParentId = parentId;
 308         return this;
 309     }
 310 
 311     public Account build() {
 312         return this.record;
 313     }
 314 
 315     public Account buildAndInsert() {
 316         insert this.record;
 317         return this.record;
 318     }
 319 }
 320 ```
 321 
 322 ### Usage
 323 
 324 ```apex
 325 // Fluent interface for building objects
 326 Account acc = new AccountBuilder()
 327     .withName('Acme Corporation')
 328     .withIndustry('Technology')
 329     .withAnnualRevenue(1000000)
 330     .withBillingAddress('San Francisco', 'CA', 'USA')
 331     .buildAndInsert();
 332 
 333 // In tests
 334 Account testAccount = new AccountBuilder()
 335     .withName('Test Account')
 336     .build();  // Don't insert for unit tests
 337 ```
 338 
 339 ---
 340 
 341 ## Singleton Pattern
 342 
 343 ### Purpose
 344 Ensure single instance, cache expensive operations.
 345 
 346 ### Implementation
 347 
 348 ```apex
 349 public class ConfigurationService {
 350     private static ConfigurationService instance;
 351     private Map<String, String> settings;
 352 
 353     private ConfigurationService() {
 354         // Load settings once
 355         this.settings = new Map<String, String>();
 356         for (Configuration__mdt config : [SELECT DeveloperName, Value__c FROM Configuration__mdt]) {
 357             settings.put(config.DeveloperName, config.Value__c);
 358         }
 359     }
 360 
 361     public static ConfigurationService getInstance() {
 362         if (instance == null) {
 363             instance = new ConfigurationService();
 364         }
 365         return instance;
 366     }
 367 
 368     public String getSetting(String key) {
 369         return settings.get(key);
 370     }
 371 
 372     public String getSetting(String key, String defaultValue) {
 373         return settings.containsKey(key) ? settings.get(key) : defaultValue;
 374     }
 375 
 376     // For testing
 377     @TestVisible
 378     private static void reset() {
 379         instance = null;
 380     }
 381 }
 382 ```
 383 
 384 ### Usage
 385 
 386 ```apex
 387 String apiUrl = ConfigurationService.getInstance().getSetting('API_URL');
 388 String timeout = ConfigurationService.getInstance().getSetting('TIMEOUT', '30000');
 389 ```
 390 
 391 ---
 392 
 393 ## Strategy Pattern
 394 
 395 ### Purpose
 396 Define family of algorithms, make them interchangeable.
 397 
 398 ### Implementation
 399 
 400 ```apex
 401 public interface DiscountStrategy {
 402     Decimal calculate(Decimal amount);
 403     String getDescription();
 404 }
 405 
 406 public class PercentageDiscount implements DiscountStrategy {
 407     private Decimal percentage;
 408 
 409     public PercentageDiscount(Decimal percentage) {
 410         this.percentage = percentage;
 411     }
 412 
 413     public Decimal calculate(Decimal amount) {
 414         return amount * (percentage / 100);
 415     }
 416 
 417     public String getDescription() {
 418         return percentage + '% off';
 419     }
 420 }
 421 
 422 public class FixedAmountDiscount implements DiscountStrategy {
 423     private Decimal fixedAmount;
 424 
 425     public FixedAmountDiscount(Decimal amount) {
 426         this.fixedAmount = amount;
 427     }
 428 
 429     public Decimal calculate(Decimal amount) {
 430         return Math.min(fixedAmount, amount);
 431     }
 432 
 433     public String getDescription() {
 434         return '$' + fixedAmount + ' off';
 435     }
 436 }
 437 
 438 public class TieredDiscount implements DiscountStrategy {
 439     public Decimal calculate(Decimal amount) {
 440         if (amount > 1000) return amount * 0.15;
 441         if (amount > 500) return amount * 0.10;
 442         if (amount > 100) return amount * 0.05;
 443         return 0;
 444     }
 445 
 446     public String getDescription() {
 447         return 'Tiered discount based on amount';
 448     }
 449 }
 450 ```
 451 
 452 ### Usage
 453 
 454 ```apex
 455 public class PricingService {
 456     private Map<String, DiscountStrategy> strategies;
 457 
 458     public PricingService() {
 459         strategies = new Map<String, DiscountStrategy>{
 460             'PERCENTAGE_10' => new PercentageDiscount(10),
 461             'FIXED_50' => new FixedAmountDiscount(50),
 462             'TIERED' => new TieredDiscount()
 463         };
 464     }
 465 
 466     public Decimal applyDiscount(String discountType, Decimal amount) {
 467         DiscountStrategy strategy = strategies.get(discountType);
 468         if (strategy == null) {
 469             return 0;
 470         }
 471         return strategy.calculate(amount);
 472     }
 473 }
 474 ```
 475 
 476 ---
 477 
 478 ## Unit of Work Pattern
 479 
 480 ### Purpose
 481 Manage DML as single transaction, track changes, enable rollback.
 482 
 483 ### Basic Implementation
 484 
 485 ```apex
 486 public class UnitOfWork {
 487     private List<SObject> newRecords = new List<SObject>();
 488     private List<SObject> dirtyRecords = new List<SObject>();
 489     private List<SObject> deletedRecords = new List<SObject>();
 490 
 491     public void registerNew(SObject record) {
 492         newRecords.add(record);
 493     }
 494 
 495     public void registerNew(List<SObject> records) {
 496         newRecords.addAll(records);
 497     }
 498 
 499     public void registerDirty(SObject record) {
 500         dirtyRecords.add(record);
 501     }
 502 
 503     public void registerDeleted(SObject record) {
 504         deletedRecords.add(record);
 505     }
 506 
 507     public void commitWork() {
 508         Savepoint sp = Database.setSavepoint();
 509         try {
 510             insert newRecords;
 511             update dirtyRecords;
 512             delete deletedRecords;
 513         } catch (Exception e) {
 514             Database.rollback(sp);
 515             throw e;
 516         }
 517     }
 518 }
 519 ```
 520 
 521 ### Usage
 522 
 523 ```apex
 524 public class OrderService {
 525     public void processOrder(Order__c order, List<OrderItem__c> items) {
 526         UnitOfWork uow = new UnitOfWork();
 527 
 528         // Register all changes
 529         uow.registerNew(order);
 530         uow.registerNew(items);
 531 
 532         Account acc = [SELECT Id, Order_Count__c FROM Account WHERE Id = :order.Account__c];
 533         acc.Order_Count__c = (acc.Order_Count__c ?? 0) + 1;
 534         uow.registerDirty(acc);
 535 
 536         // Single commit - all or nothing
 537         uow.commitWork();
 538     }
 539 }
 540 ```
 541 
 542 ---
 543 
 544 ## Decorator Pattern
 545 
 546 ### Purpose
 547 Add functionality dynamically without modifying original class. Stack behaviors flexibly.
 548 
 549 ### Implementation
 550 
 551 ```apex
 552 // Base interface
 553 public interface NotificationService {
 554     void send(String message, Id recipientId);
 555 }
 556 
 557 // Core implementation
 558 public class EmailNotification implements NotificationService {
 559     public void send(String message, Id recipientId) {
 560         Messaging.SingleEmailMessage email = new Messaging.SingleEmailMessage();
 561         email.setTargetObjectId(recipientId);
 562         email.setPlainTextBody(message);
 563         Messaging.sendEmail(new List<Messaging.SingleEmailMessage>{ email });
 564     }
 565 }
 566 
 567 // Decorator base - wraps another NotificationService
 568 public virtual class NotificationDecorator implements NotificationService {
 569     protected NotificationService wrapped;
 570 
 571     public NotificationDecorator(NotificationService service) {
 572         this.wrapped = service;
 573     }
 574 
 575     public virtual void send(String message, Id recipientId) {
 576         wrapped.send(message, recipientId);
 577     }
 578 }
 579 
 580 // Concrete decorator: Add logging
 581 public class LoggingNotificationDecorator extends NotificationDecorator {
 582     public LoggingNotificationDecorator(NotificationService service) {
 583         super(service);
 584     }
 585 
 586     public override void send(String message, Id recipientId) {
 587         System.debug('Sending notification to: ' + recipientId);
 588         super.send(message, recipientId);
 589         System.debug('Notification sent successfully');
 590     }
 591 }
 592 
 593 // Concrete decorator: Add retry logic
 594 public class RetryNotificationDecorator extends NotificationDecorator {
 595     private Integer maxRetries;
 596 
 597     public RetryNotificationDecorator(NotificationService service, Integer maxRetries) {
 598         super(service);
 599         this.maxRetries = maxRetries;
 600     }
 601 
 602     public override void send(String message, Id recipientId) {
 603         Integer attempts = 0;
 604         while (attempts < maxRetries) {
 605             try {
 606                 super.send(message, recipientId);
 607                 return;
 608             } catch (Exception e) {
 609                 attempts++;
 610                 if (attempts >= maxRetries) throw e;
 611             }
 612         }
 613     }
 614 }
 615 ```
 616 
 617 ### Usage
 618 
 619 ```apex
 620 // Stack decorators as needed
 621 NotificationService service = new EmailNotification();
 622 service = new LoggingNotificationDecorator(service);
 623 service = new RetryNotificationDecorator(service, 3);
 624 
 625 // Now sends with logging + retry + email
 626 service.send('Your order shipped!', userId);
 627 ```
 628 
 629 ### When to Use
 630 - Adding cross-cutting concerns (logging, caching, validation)
 631 - When inheritance leads to class explosion
 632 - Stacking behaviors that can be combined independently
 633 
 634 ---
 635 
 636 ## Observer Pattern
 637 
 638 ### Purpose
 639 Define one-to-many dependency where observers are notified of state changes automatically.
 640 
 641 ### Implementation
 642 
 643 ```apex
 644 // Observer interface
 645 public interface AccountObserver {
 646     void onAccountUpdated(Account oldAccount, Account newAccount);
 647 }
 648 
 649 // Subject that notifies observers
 650 public class AccountSubject {
 651     private static List<AccountObserver> observers = new List<AccountObserver>();
 652 
 653     public static void attach(AccountObserver observer) {
 654         observers.add(observer);
 655     }
 656 
 657     public static void detach(AccountObserver observer) {
 658         Integer index = observers.indexOf(observer);
 659         if (index >= 0) observers.remove(index);
 660     }
 661 
 662     public static void notifyObservers(Account oldAccount, Account newAccount) {
 663         for (AccountObserver observer : observers) {
 664             observer.onAccountUpdated(oldAccount, newAccount);
 665         }
 666     }
 667 }
 668 
 669 // Concrete observers
 670 public class SalesNotificationObserver implements AccountObserver {
 671     public void onAccountUpdated(Account oldAcc, Account newAcc) {
 672         if (newAcc.AnnualRevenue > 1000000 && (oldAcc.AnnualRevenue == null || oldAcc.AnnualRevenue <= 1000000)) {
 673             // Notify sales team about new enterprise account
 674             createTask(newAcc.OwnerId, 'New Enterprise Account: ' + newAcc.Name);
 675         }
 676     }
 677 
 678     private void createTask(Id ownerId, String subject) {
 679         insert new Task(OwnerId = ownerId, Subject = subject, Status = 'Open');
 680     }
 681 }
 682 
 683 public class IntegrationSyncObserver implements AccountObserver {
 684     public void onAccountUpdated(Account oldAcc, Account newAcc) {
 685         // Queue sync to external system
 686         System.enqueueJob(new AccountSyncQueueable(newAcc.Id));
 687     }
 688 }
 689 ```
 690 
 691 ### Usage in Trigger
 692 
 693 ```apex
 694 // TriggerHandler or Action class
 695 public class AccountTriggerHandler {
 696 
 697     static {
 698         // Register observers once
 699         AccountSubject.attach(new SalesNotificationObserver());
 700         AccountSubject.attach(new IntegrationSyncObserver());
 701     }
 702 
 703     public void afterUpdate(List<Account> newList, Map<Id, Account> oldMap) {
 704         for (Account acc : newList) {
 705             AccountSubject.notifyObservers(oldMap.get(acc.Id), acc);
 706         }
 707     }
 708 }
 709 ```
 710 
 711 ### Platform Events Alternative
 712 For decoupled, async observers, use Platform Events:
 713 
 714 ```apex
 715 // Publish event
 716 EventBus.publish(new Account_Updated__e(Account_Id__c = acc.Id, Field_Changed__c = 'Status'));
 717 
 718 // Subscribe via trigger on platform event
 719 trigger AccountUpdatedSubscriber on Account_Updated__e (after insert) {
 720     // Handle event
 721 }
 722 ```
 723 
 724 ---
 725 
 726 ## Command Pattern
 727 
 728 ### Purpose
 729 Encapsulate requests as objects, enabling queuing, logging, undo, and parameterized execution.
 730 
 731 ### Implementation
 732 
 733 ```apex
 734 // Command interface
 735 public interface Command {
 736     void execute();
 737     void undo();
 738     String getDescription();
 739 }
 740 
 741 // Concrete command: Update Field
 742 public class UpdateFieldCommand implements Command {
 743     private Id recordId;
 744     private String fieldName;
 745     private Object newValue;
 746     private Object oldValue;
 747     private SObjectType objectType;
 748 
 749     public UpdateFieldCommand(Id recordId, String fieldName, Object newValue) {
 750         this.recordId = recordId;
 751         this.fieldName = fieldName;
 752         this.newValue = newValue;
 753         this.objectType = recordId.getSObjectType();
 754     }
 755 
 756     public void execute() {
 757         // Store old value for undo
 758         SObject record = Database.query(
 759             'SELECT ' + fieldName + ' FROM ' + objectType + ' WHERE Id = :recordId'
 760         );
 761         this.oldValue = record.get(fieldName);
 762 
 763         // Apply new value
 764         record.put(fieldName, newValue);
 765         update record;
 766     }
 767 
 768     public void undo() {
 769         SObject record = objectType.newSObject(recordId);
 770         record.put(fieldName, oldValue);
 771         update record;
 772     }
 773 
 774     public String getDescription() {
 775         return 'Update ' + objectType + '.' + fieldName + ' to ' + newValue;
 776     }
 777 }
 778 
 779 // Command invoker with history
 780 public class CommandInvoker {
 781     private List<Command> history = new List<Command>();
 782     private List<Command> queue = new List<Command>();
 783 
 784     public void addToQueue(Command cmd) {
 785         queue.add(cmd);
 786     }
 787 
 788     public void executeQueue() {
 789         for (Command cmd : queue) {
 790             cmd.execute();
 791             history.add(cmd);
 792             // Log for audit trail
 793             System.debug('Executed: ' + cmd.getDescription());
 794         }
 795         queue.clear();
 796     }
 797 
 798     public void undoLast() {
 799         if (!history.isEmpty()) {
 800             Command lastCommand = history.remove(history.size() - 1);
 801             lastCommand.undo();
 802         }
 803     }
 804 }
 805 ```
 806 
 807 ### Usage
 808 
 809 ```apex
 810 CommandInvoker invoker = new CommandInvoker();
 811 
 812 // Queue multiple field updates
 813 invoker.addToQueue(new UpdateFieldCommand(accountId, 'Status__c', 'Active'));
 814 invoker.addToQueue(new UpdateFieldCommand(accountId, 'Priority__c', 'High'));
 815 
 816 // Execute all
 817 invoker.executeQueue();
 818 
 819 // Undo last operation
 820 invoker.undoLast();
 821 ```
 822 
 823 ### Use Cases
 824 - Wizard/multi-step processes with undo
 825 - Audit trail with replayable operations
 826 - Batch processing with deferred execution
 827 - Macro recording and playback
 828 
 829 ---
 830 
 831 ## Facade Pattern
 832 
 833 ### Purpose
 834 Provide simplified interface to complex subsystems. Reduce coupling between client and implementation details.
 835 
 836 ### Implementation
 837 
 838 ```apex
 839 // Complex subsystems
 840 public class CustomerVerificationService {
 841     public Boolean verifyIdentity(String customerId) {
 842         // Complex identity verification logic
 843         return true;
 844     }
 845 }
 846 
 847 public class CreditCheckService {
 848     public Integer getCreditScore(String customerId) {
 849         // Call external credit bureau
 850         return 720;
 851     }
 852 
 853     public Decimal getAvailableCredit(String customerId) {
 854         return 50000.00;
 855     }
 856 }
 857 
 858 public class RiskAssessmentService {
 859     public String assessRisk(Integer creditScore, Decimal requestedAmount) {
 860         if (creditScore > 700 && requestedAmount < 25000) return 'LOW';
 861         if (creditScore > 600) return 'MEDIUM';
 862         return 'HIGH';
 863     }
 864 }
 865 
 866 public class LoanApplicationService {
 867     public Id createApplication(Id accountId, Decimal amount) {
 868         Loan_Application__c app = new Loan_Application__c(
 869             Account__c = accountId,
 870             Amount__c = amount,
 871             Status__c = 'Pending'
 872         );
 873         insert app;
 874         return app.Id;
 875     }
 876 }
 877 
 878 // FACADE: Simplified interface
 879 public class LoanFacade {
 880     private CustomerVerificationService verificationService;
 881     private CreditCheckService creditService;
 882     private RiskAssessmentService riskService;
 883     private LoanApplicationService applicationService;
 884 
 885     public LoanFacade() {
 886         this.verificationService = new CustomerVerificationService();
 887         this.creditService = new CreditCheckService();
 888         this.riskService = new RiskAssessmentService();
 889         this.applicationService = new LoanApplicationService();
 890     }
 891 
 892     // Single method hides all complexity
 893     public LoanResult applyForLoan(Id accountId, String customerId, Decimal amount) {
 894         LoanResult result = new LoanResult();
 895 
 896         // Step 1: Verify customer
 897         if (!verificationService.verifyIdentity(customerId)) {
 898             result.success = false;
 899             result.message = 'Identity verification failed';
 900             return result;
 901         }
 902 
 903         // Step 2: Check credit
 904         Integer creditScore = creditService.getCreditScore(customerId);
 905         Decimal availableCredit = creditService.getAvailableCredit(customerId);
 906 
 907         if (amount > availableCredit) {
 908             result.success = false;
 909             result.message = 'Requested amount exceeds available credit';
 910             return result;
 911         }
 912 
 913         // Step 3: Assess risk
 914         String riskLevel = riskService.assessRisk(creditScore, amount);
 915 
 916         // Step 4: Create application
 917         result.applicationId = applicationService.createApplication(accountId, amount);
 918         result.success = true;
 919         result.riskLevel = riskLevel;
 920         result.message = 'Loan application submitted successfully';
 921 
 922         return result;
 923     }
 924 
 925     public class LoanResult {
 926         public Boolean success;
 927         public Id applicationId;
 928         public String riskLevel;
 929         public String message;
 930     }
 931 }
 932 ```
 933 
 934 ### Usage
 935 
 936 ```apex
 937 // Client code is simple - no knowledge of subsystems
 938 LoanFacade facade = new LoanFacade();
 939 LoanFacade.LoanResult result = facade.applyForLoan(accountId, 'CUST-123', 15000.00);
 940 
 941 if (result.success) {
 942     System.debug('Loan approved with risk level: ' + result.riskLevel);
 943 } else {
 944     System.debug('Loan denied: ' + result.message);
 945 }
 946 ```
 947 
 948 ### When to Use
 949 - Simplifying access to complex subsystems
 950 - Creating API layers for external integrations
 951 - Reducing dependencies on multiple services
 952 - Providing entry points for different client needs
 953 
 954 ---
 955 
 956 ## Domain Class Pattern
 957 
 958 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
 959 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
 960 
 961 ### Purpose
 962 
 963 Encapsulate business rules in domain-specific classes, making code read like plain English and enabling reuse across the application.
 964 
 965 ### Implementation
 966 
 967 ```apex
 968 /**
 969  * Domain class encapsulating Account business rules
 970  * Rules live here, not scattered across triggers/services
 971  */
 972 public class AccountRules {
 973 
 974     public static Boolean isStrategicAccount(Account account) {
 975         return isEnterpriseCustomer(account) &&
 976                isHighValue(account) &&
 977                isInTargetMarket(account);
 978     }
 979 
 980     public static Boolean isEnterpriseCustomer(Account account) {
 981         return account.Type == 'Enterprise' &&
 982                account.NumberOfEmployees > 500;
 983     }
 984 
 985     public static Boolean isHighValue(Account account) {
 986         return account.AnnualRevenue != null &&
 987                account.AnnualRevenue > 1000000;
 988     }
 989 
 990     public static Boolean isInTargetMarket(Account account) {
 991         Set<String> targetIndustries = new Set<String>{
 992             'Technology', 'Finance', 'Healthcare'
 993         };
 994         Set<String> targetCountries = new Set<String>{
 995             'United States', 'Canada', 'United Kingdom'
 996         };
 997 
 998         return targetIndustries.contains(account.Industry) &&
 999                targetCountries.contains(account.BillingCountry);
1000     }
1001 
1002     public static Boolean requiresExecutiveApproval(Account account, Decimal dealValue) {
1003         return isStrategicAccount(account) && dealValue > 500000;
1004     }
1005 
1006     public static Boolean isEligibleForDiscount(Account account) {
1007         return account.Customer_Since__c != null &&
1008                account.Customer_Since__c.monthsBetween(Date.today()) > 24 &&
1009                isHighValue(account);
1010     }
1011 }
1012 ```
1013 
1014 ### Usage
1015 
1016 ```apex
1017 // Reads like plain English
1018 public void processOpportunity(Opportunity opp, Account account) {
1019     if (AccountRules.isStrategicAccount(account)) {
1020         assignToEnterpriseTeam(opp);
1021     }
1022 
1023     if (AccountRules.requiresExecutiveApproval(account, opp.Amount)) {
1024         routeForApproval(opp);
1025     }
1026 
1027     if (AccountRules.isEligibleForDiscount(account)) {
1028         applyLoyaltyDiscount(opp);
1029     }
1030 }
1031 ```
1032 
1033 ### When to Use
1034 
1035 - Business rules are reused across multiple classes
1036 - Complex boolean logic needs to be readable
1037 - Rules change frequently (centralized = easier updates)
1038 - You want trigger/service code to read like business requirements
1039 
1040 ### Relationship to Other Patterns
1041 
1042 | Pattern | Relationship |
1043 |---------|--------------|
1044 | Selector | Domain class uses Selector for data access |
1045 | Service | Service orchestrates, Domain validates |
1046 | Repository | Domain class is data-agnostic |
1047 | Strategy | Domain rules can use Strategy for variations |
1048 
1049 ---
1050 
1051 ## Abstraction Level Management
1052 
1053 > 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
1054 > [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*
1055 
1056 ### Purpose
1057 
1058 Ensure each method operates at a consistent level of abstraction. Don't mix high-level orchestration with low-level implementation details.
1059 
1060 ### The Problem
1061 
1062 ```apex
1063 // BAD: Mixed abstraction levels
1064 public void processNewCustomer(Account account) {
1065     // HIGH-LEVEL: Validation
1066     validateAccount(account);
1067 
1068     // LOW-LEVEL: String manipulation (doesn't belong here)
1069     String sanitizedPhone = account.Phone.replaceAll('[^0-9]', '');
1070     if (sanitizedPhone.length() == 10) {
1071         sanitizedPhone = '1' + sanitizedPhone;
1072     }
1073     account.Phone = '+' + sanitizedPhone;
1074 
1075     // HIGH-LEVEL: Save
1076     insert account;
1077 
1078     // LOW-LEVEL: HTTP details (doesn't belong here)
1079     HttpRequest req = new HttpRequest();
1080     req.setEndpoint('https://api.crm.com/customers');
1081     req.setMethod('POST');
1082     req.setHeader('Content-Type', 'application/json');
1083     req.setBody(JSON.serialize(account));
1084     Http http = new Http();
1085     HttpResponse res = http.send(req);
1086 
1087     // HIGH-LEVEL: Notification
1088     sendWelcomeEmail(account);
1089 }
1090 ```
1091 
1092 ### The Solution
1093 
1094 ```apex
1095 // GOOD: Consistent high-level abstraction
1096 public void processNewCustomer(Account account) {
1097     validateAccount(account);
1098     normalizePhoneNumber(account);
1099     insert account;
1100     syncToExternalCRM(account);
1101     sendWelcomeEmail(account);
1102 }
1103 
1104 // Low-level details extracted to focused methods
1105 private void normalizePhoneNumber(Account account) {
1106     if (String.isBlank(account.Phone)) return;
1107 
1108     String digitsOnly = account.Phone.replaceAll('[^0-9]', '');
1109     if (digitsOnly.length() == 10) {
1110         digitsOnly = '1' + digitsOnly;
1111     }
1112     account.Phone = '+' + digitsOnly;
1113 }
1114 
1115 private void syncToExternalCRM(Account account) {
1116     CRMIntegrationService.syncCustomer(account);
1117 }
1118 ```
1119 
1120 ### Abstraction Layers in Apex
1121 
1122 ```
1123 ┌─────────────────────────────────────────────────────────────┐
1124 │  TRIGGER LAYER                                              │
1125 │  - Routes events to handlers                                │
1126 │  - No business logic                                        │
1127 └─────────────────────────────────────────────────────────────┘
1128                             │
1129                             ▼
1130 ┌─────────────────────────────────────────────────────────────┐
1131 │  HANDLER/SERVICE LAYER (High-level)                         │
1132 │  - Orchestrates business operations                         │
1133 │  - Coordinates between components                           │
1134 │  - Each step is a method call, not implementation           │
1135 └─────────────────────────────────────────────────────────────┘
1136                             │
1137                             ▼
1138 ┌─────────────────────────────────────────────────────────────┐
1139 │  DOMAIN LAYER (Business rules)                              │
1140 │  - Encapsulates business logic                              │
1141 │  - AccountRules, OpportunityRules, etc.                     │
1142 │  - Pure logic, no infrastructure                            │
1143 └─────────────────────────────────────────────────────────────┘
1144                             │
1145                             ▼
1146 ┌─────────────────────────────────────────────────────────────┐
1147 │  DATA ACCESS LAYER (Low-level)                              │
1148 │  - Selectors for SOQL                                       │
1149 │  - Repositories for DML                                     │
1150 │  - Integration services for external calls                  │
1151 └─────────────────────────────────────────────────────────────┘
1152 ```
1153 
1154 ### Guidelines
1155 
1156 | Level | Should Contain | Should NOT Contain |
1157 |-------|---------------|-------------------|
1158 | High (Orchestration) | Method calls, flow control | SOQL, DML, string parsing |
1159 | Mid (Domain) | Business rules, validation | HTTP calls, database queries |
1160 | Low (Data Access) | SOQL, DML, HTTP | Business decisions |
1161 
1162 ### Signs of Mixed Abstraction
1163 
1164 - A method has both `[SELECT ...]` and business logic
1165 - HTTP request building next to email sending
1166 - String manipulation in a method that also updates records
1167 - Governor limit checks scattered among business rules
1168 
1169 ### Benefits
1170 
1171 - Each method is easier to understand in isolation
1172 - Methods at the same level can be tested with similar techniques
1173 - Changes to implementation don't affect orchestration
1174 - Code reads like a high-level description of the process
1175 
1176 ---
1177 
1178 ## Pattern Selection Guide
1179 
1180 | Need | Pattern |
1181 |------|---------|
1182 | Centralize object creation | Factory |
1183 | Abstract data access | Repository / Selector |
1184 | Build complex objects | Builder |
1185 | Single cached instance | Singleton |
1186 | Interchangeable algorithms | Strategy |
1187 | Transactional DML | Unit of Work |
1188 | Add behavior without modification | Decorator |
1189 | React to state changes | Observer |
1190 | Queue/undo operations | Command |
1191 | Simplify complex systems | Facade |
1192 | Encapsulate business rules | Domain Class |
1193 | Consistent method structure | Abstraction Levels |
