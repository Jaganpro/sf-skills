<!-- Parent: sf-apex/SKILL.md -->
# Apex Design Patterns

## Factory Pattern

### Purpose
Centralize object creation, enable dependency injection, simplify testing.

### Implementation

```apex
public virtual class Factory {
    private static Factory instance;

    public static Factory getInstance() {
        if (instance == null) {
            instance = new Factory();
        }
        return instance;
    }

    @TestVisible
    private static void setInstance(Factory mockFactory) {
        instance = mockFactory;
    }

    // Service getters - virtual for mocking
    public virtual AccountService getAccountService() {
        return new AccountService();
    }

    public virtual ContactService getContactService() {
        return new ContactService();
    }

    public virtual PaymentGateway getPaymentGateway() {
        return new StripePaymentGateway();
    }
}
```

### Usage

```apex
public class OrderProcessor {
    private AccountService accountService;
    private PaymentGateway gateway;

    public OrderProcessor() {
        this(Factory.getInstance());
    }

    @TestVisible
    private OrderProcessor(Factory factory) {
        this.accountService = factory.getAccountService();
        this.gateway = factory.getPaymentGateway();
    }

    public void process(Order__c order) {
        Account acc = accountService.getAccount(order.Account__c);
        gateway.charge(order.Total__c);
    }
}
```

### Testing with Factory

```apex
@isTest
private class OrderProcessorTest {

    @isTest
    static void testProcess() {
        // Set mock factory
        Factory.setInstance(new MockFactory());

        OrderProcessor processor = new OrderProcessor();

        Test.startTest();
        processor.process(new Order__c());
        Test.stopTest();

        // Assertions
    }

    private class MockFactory extends Factory {
        public override AccountService getAccountService() {
            return new MockAccountService();
        }

        public override PaymentGateway getPaymentGateway() {
            return new MockPaymentGateway();
        }
    }
}
```

---

## Repository Pattern

### Purpose
Abstract data access, provide strongly-typed queries, enable DML mocking.

### Implementation

```apex
public virtual class AccountRepository {

    public virtual List<Account> getByIds(Set<Id> accountIds) {
        return [
            SELECT Id, Name, Industry, AnnualRevenue
            FROM Account
            WHERE Id IN :accountIds
            WITH USER_MODE
        ];
    }

    public virtual List<Account> getByIndustry(String industry) {
        return [
            SELECT Id, Name, AnnualRevenue
            FROM Account
            WHERE Industry = :industry
            WITH USER_MODE
        ];
    }

    public virtual Account getById(Id accountId) {
        List<Account> accounts = getByIds(new Set<Id>{accountId});
        return accounts.isEmpty() ? null : accounts[0];
    }

    public virtual void save(List<Account> accounts) {
        upsert accounts;
    }

    public virtual void remove(List<Account> accounts) {
        delete accounts;
    }
}
```

### Usage

```apex
public class AccountService {
    private AccountRepository repo;

    public AccountService() {
        this.repo = new AccountRepository();
    }

    @TestVisible
    private AccountService(AccountRepository repo) {
        this.repo = repo;
    }

    public List<Account> getTechnologyAccounts() {
        return repo.getByIndustry('Technology');
    }

    public void updateAccounts(List<Account> accounts) {
        repo.save(accounts);
    }
}
```

### Testing with Mock Repository

```apex
@isTest
private class AccountServiceTest {

    @isTest
    static void testGetTechnologyAccounts() {
        MockAccountRepository mockRepo = new MockAccountRepository();
        mockRepo.accountsToReturn = new List<Account>{
            new Account(Name = 'Test', Industry = 'Technology')
        };

        AccountService service = new AccountService(mockRepo);

        Test.startTest();
        List<Account> results = service.getTechnologyAccounts();
        Test.stopTest();

        Assert.areEqual(1, results.size());
        Assert.areEqual('Technology', mockRepo.lastIndustryQueried);
    }

    private class MockAccountRepository extends AccountRepository {
        public List<Account> accountsToReturn = new List<Account>();
        public String lastIndustryQueried;

        public override List<Account> getByIndustry(String industry) {
            this.lastIndustryQueried = industry;
            return accountsToReturn;
        }
    }
}
```

---

## Selector Pattern

### Purpose
Centralize SOQL queries per object, enforce security, enable reuse.

### Implementation

```apex
public inherited sharing class AccountSelector {

    public List<Account> selectById(Set<Id> ids) {
        return [
            SELECT Id, Name, Industry, AnnualRevenue, BillingCity
            FROM Account
            WHERE Id IN :ids
            WITH USER_MODE
        ];
    }

    public List<Account> selectByIdWithContacts(Set<Id> ids) {
        return [
            SELECT Id, Name, Industry,
                (SELECT Id, FirstName, LastName, Email FROM Contacts)
            FROM Account
            WHERE Id IN :ids
            WITH USER_MODE
        ];
    }

    public List<Account> selectByName(String name) {
        return [
            SELECT Id, Name, Industry
            FROM Account
            WHERE Name LIKE :('%' + name + '%')
            WITH USER_MODE
            LIMIT 100
        ];
    }

    public List<Account> selectActiveByIndustry(String industry) {
        return [
            SELECT Id, Name, AnnualRevenue
            FROM Account
            WHERE Industry = :industry
            AND Status__c = 'Active'
            WITH USER_MODE
        ];
    }
}
```

### Usage

```apex
public class AccountService {
    private AccountSelector selector = new AccountSelector();

    public Map<Id, Account> getAccountsMap(Set<Id> ids) {
        return new Map<Id, Account>(selector.selectById(ids));
    }
}
```

---

## Builder Pattern

### Purpose
Construct complex objects step-by-step, improve readability.

### Implementation

```apex
public class AccountBuilder {
    private Account record;

    public AccountBuilder() {
        this.record = new Account();
    }

    public AccountBuilder withName(String name) {
        this.record.Name = name;
        return this;
    }

    public AccountBuilder withIndustry(String industry) {
        this.record.Industry = industry;
        return this;
    }

    public AccountBuilder withAnnualRevenue(Decimal revenue) {
        this.record.AnnualRevenue = revenue;
        return this;
    }

    public AccountBuilder withBillingAddress(String city, String state, String country) {
        this.record.BillingCity = city;
        this.record.BillingState = state;
        this.record.BillingCountry = country;
        return this;
    }

    public AccountBuilder withParent(Id parentId) {
        this.record.ParentId = parentId;
        return this;
    }

    public Account build() {
        return this.record;
    }

    public Account buildAndInsert() {
        insert this.record;
        return this.record;
    }
}
```

### Usage

```apex
// Fluent interface for building objects
Account acc = new AccountBuilder()
    .withName('Acme Corporation')
    .withIndustry('Technology')
    .withAnnualRevenue(1000000)
    .withBillingAddress('San Francisco', 'CA', 'USA')
    .buildAndInsert();

// In tests
Account testAccount = new AccountBuilder()
    .withName('Test Account')
    .build();  // Don't insert for unit tests
```

---

## Singleton Pattern

### Purpose
Ensure single instance, cache expensive operations.

### Implementation

```apex
public class ConfigurationService {
    private static ConfigurationService instance;
    private Map<String, String> settings;

    private ConfigurationService() {
        // Load settings once
        this.settings = new Map<String, String>();
        for (Configuration__mdt config : [SELECT DeveloperName, Value__c FROM Configuration__mdt]) {
            settings.put(config.DeveloperName, config.Value__c);
        }
    }

    public static ConfigurationService getInstance() {
        if (instance == null) {
            instance = new ConfigurationService();
        }
        return instance;
    }

    public String getSetting(String key) {
        return settings.get(key);
    }

    public String getSetting(String key, String defaultValue) {
        return settings.containsKey(key) ? settings.get(key) : defaultValue;
    }

    // For testing
    @TestVisible
    private static void reset() {
        instance = null;
    }
}
```

### Usage

```apex
String apiUrl = ConfigurationService.getInstance().getSetting('API_URL');
String timeout = ConfigurationService.getInstance().getSetting('TIMEOUT', '30000');
```

---

## Strategy Pattern

### Purpose
Define family of algorithms, make them interchangeable.

### Implementation

```apex
public interface DiscountStrategy {
    Decimal calculate(Decimal amount);
    String getDescription();
}

public class PercentageDiscount implements DiscountStrategy {
    private Decimal percentage;

    public PercentageDiscount(Decimal percentage) {
        this.percentage = percentage;
    }

    public Decimal calculate(Decimal amount) {
        return amount * (percentage / 100);
    }

    public String getDescription() {
        return percentage + '% off';
    }
}

public class FixedAmountDiscount implements DiscountStrategy {
    private Decimal fixedAmount;

    public FixedAmountDiscount(Decimal amount) {
        this.fixedAmount = amount;
    }

    public Decimal calculate(Decimal amount) {
        return Math.min(fixedAmount, amount);
    }

    public String getDescription() {
        return '$' + fixedAmount + ' off';
    }
}

public class TieredDiscount implements DiscountStrategy {
    public Decimal calculate(Decimal amount) {
        if (amount > 1000) return amount * 0.15;
        if (amount > 500) return amount * 0.10;
        if (amount > 100) return amount * 0.05;
        return 0;
    }

    public String getDescription() {
        return 'Tiered discount based on amount';
    }
}
```

### Usage

```apex
public class PricingService {
    private Map<String, DiscountStrategy> strategies;

    public PricingService() {
        strategies = new Map<String, DiscountStrategy>{
            'PERCENTAGE_10' => new PercentageDiscount(10),
            'FIXED_50' => new FixedAmountDiscount(50),
            'TIERED' => new TieredDiscount()
        };
    }

    public Decimal applyDiscount(String discountType, Decimal amount) {
        DiscountStrategy strategy = strategies.get(discountType);
        if (strategy == null) {
            return 0;
        }
        return strategy.calculate(amount);
    }
}
```

---

## Unit of Work Pattern

### Purpose
Manage DML as single transaction, track changes, enable rollback.

### Basic Implementation

```apex
public class UnitOfWork {
    private List<SObject> newRecords = new List<SObject>();
    private List<SObject> dirtyRecords = new List<SObject>();
    private List<SObject> deletedRecords = new List<SObject>();

    public void registerNew(SObject record) {
        newRecords.add(record);
    }

    public void registerNew(List<SObject> records) {
        newRecords.addAll(records);
    }

    public void registerDirty(SObject record) {
        dirtyRecords.add(record);
    }

    public void registerDeleted(SObject record) {
        deletedRecords.add(record);
    }

    public void commitWork() {
        Savepoint sp = Database.setSavepoint();
        try {
            insert newRecords;
            update dirtyRecords;
            delete deletedRecords;
        } catch (Exception e) {
            Database.rollback(sp);
            throw e;
        }
    }
}
```

### Usage

```apex
public class OrderService {
    public void processOrder(Order__c order, List<OrderItem__c> items) {
        UnitOfWork uow = new UnitOfWork();

        // Register all changes
        uow.registerNew(order);
        uow.registerNew(items);

        Account acc = [SELECT Id, Order_Count__c FROM Account WHERE Id = :order.Account__c];
        acc.Order_Count__c = (acc.Order_Count__c ?? 0) + 1;
        uow.registerDirty(acc);

        // Single commit - all or nothing
        uow.commitWork();
    }
}
```

---

## Decorator Pattern

### Purpose
Add functionality dynamically without modifying original class. Stack behaviors flexibly.

### Implementation

```apex
// Base interface
public interface NotificationService {
    void send(String message, Id recipientId);
}

// Core implementation
public class EmailNotification implements NotificationService {
    public void send(String message, Id recipientId) {
        Messaging.SingleEmailMessage email = new Messaging.SingleEmailMessage();
        email.setTargetObjectId(recipientId);
        email.setPlainTextBody(message);
        Messaging.sendEmail(new List<Messaging.SingleEmailMessage>{ email });
    }
}

// Decorator base - wraps another NotificationService
public virtual class NotificationDecorator implements NotificationService {
    protected NotificationService wrapped;

    public NotificationDecorator(NotificationService service) {
        this.wrapped = service;
    }

    public virtual void send(String message, Id recipientId) {
        wrapped.send(message, recipientId);
    }
}

// Concrete decorator: Add logging
public class LoggingNotificationDecorator extends NotificationDecorator {
    public LoggingNotificationDecorator(NotificationService service) {
        super(service);
    }

    public override void send(String message, Id recipientId) {
        System.debug('Sending notification to: ' + recipientId);
        super.send(message, recipientId);
        System.debug('Notification sent successfully');
    }
}

// Concrete decorator: Add retry logic
public class RetryNotificationDecorator extends NotificationDecorator {
    private Integer maxRetries;

    public RetryNotificationDecorator(NotificationService service, Integer maxRetries) {
        super(service);
        this.maxRetries = maxRetries;
    }

    public override void send(String message, Id recipientId) {
        Integer attempts = 0;
        while (attempts < maxRetries) {
            try {
                super.send(message, recipientId);
                return;
            } catch (Exception e) {
                attempts++;
                if (attempts >= maxRetries) throw e;
            }
        }
    }
}
```

### Usage

```apex
// Stack decorators as needed
NotificationService service = new EmailNotification();
service = new LoggingNotificationDecorator(service);
service = new RetryNotificationDecorator(service, 3);

// Now sends with logging + retry + email
service.send('Your order shipped!', userId);
```

### When to Use
- Adding cross-cutting concerns (logging, caching, validation)
- When inheritance leads to class explosion
- Stacking behaviors that can be combined independently

---

## Observer Pattern

### Purpose
Define one-to-many dependency where observers are notified of state changes automatically.

### Implementation

```apex
// Observer interface
public interface AccountObserver {
    void onAccountUpdated(Account oldAccount, Account newAccount);
}

// Subject that notifies observers
public class AccountSubject {
    private static List<AccountObserver> observers = new List<AccountObserver>();

    public static void attach(AccountObserver observer) {
        observers.add(observer);
    }

    public static void detach(AccountObserver observer) {
        Integer index = observers.indexOf(observer);
        if (index >= 0) observers.remove(index);
    }

    public static void notifyObservers(Account oldAccount, Account newAccount) {
        for (AccountObserver observer : observers) {
            observer.onAccountUpdated(oldAccount, newAccount);
        }
    }
}

// Concrete observers
public class SalesNotificationObserver implements AccountObserver {
    public void onAccountUpdated(Account oldAcc, Account newAcc) {
        if (newAcc.AnnualRevenue > 1000000 && (oldAcc.AnnualRevenue == null || oldAcc.AnnualRevenue <= 1000000)) {
            // Notify sales team about new enterprise account
            createTask(newAcc.OwnerId, 'New Enterprise Account: ' + newAcc.Name);
        }
    }

    private void createTask(Id ownerId, String subject) {
        insert new Task(OwnerId = ownerId, Subject = subject, Status = 'Open');
    }
}

public class IntegrationSyncObserver implements AccountObserver {
    public void onAccountUpdated(Account oldAcc, Account newAcc) {
        // Queue sync to external system
        System.enqueueJob(new AccountSyncQueueable(newAcc.Id));
    }
}
```

### Usage in Trigger

```apex
// TriggerHandler or Action class
public class AccountTriggerHandler {

    static {
        // Register observers once
        AccountSubject.attach(new SalesNotificationObserver());
        AccountSubject.attach(new IntegrationSyncObserver());
    }

    public void afterUpdate(List<Account> newList, Map<Id, Account> oldMap) {
        for (Account acc : newList) {
            AccountSubject.notifyObservers(oldMap.get(acc.Id), acc);
        }
    }
}
```

### Platform Events Alternative
For decoupled, async observers, use Platform Events:

```apex
// Publish event
EventBus.publish(new Account_Updated__e(Account_Id__c = acc.Id, Field_Changed__c = 'Status'));

// Subscribe via trigger on platform event
trigger AccountUpdatedSubscriber on Account_Updated__e (after insert) {
    // Handle event
}
```

---

## Command Pattern

### Purpose
Encapsulate requests as objects, enabling queuing, logging, undo, and parameterized execution.

### Implementation

```apex
// Command interface
public interface Command {
    void execute();
    void undo();
    String getDescription();
}

// Concrete command: Update Field
public class UpdateFieldCommand implements Command {
    private Id recordId;
    private String fieldName;
    private Object newValue;
    private Object oldValue;
    private SObjectType objectType;

    public UpdateFieldCommand(Id recordId, String fieldName, Object newValue) {
        this.recordId = recordId;
        this.fieldName = fieldName;
        this.newValue = newValue;
        this.objectType = recordId.getSObjectType();
    }

    public void execute() {
        // Store old value for undo
        SObject record = Database.query(
            'SELECT ' + fieldName + ' FROM ' + objectType + ' WHERE Id = :recordId'
        );
        this.oldValue = record.get(fieldName);

        // Apply new value
        record.put(fieldName, newValue);
        update record;
    }

    public void undo() {
        SObject record = objectType.newSObject(recordId);
        record.put(fieldName, oldValue);
        update record;
    }

    public String getDescription() {
        return 'Update ' + objectType + '.' + fieldName + ' to ' + newValue;
    }
}

// Command invoker with history
public class CommandInvoker {
    private List<Command> history = new List<Command>();
    private List<Command> queue = new List<Command>();

    public void addToQueue(Command cmd) {
        queue.add(cmd);
    }

    public void executeQueue() {
        for (Command cmd : queue) {
            cmd.execute();
            history.add(cmd);
            // Log for audit trail
            System.debug('Executed: ' + cmd.getDescription());
        }
        queue.clear();
    }

    public void undoLast() {
        if (!history.isEmpty()) {
            Command lastCommand = history.remove(history.size() - 1);
            lastCommand.undo();
        }
    }
}
```

### Usage

```apex
CommandInvoker invoker = new CommandInvoker();

// Queue multiple field updates
invoker.addToQueue(new UpdateFieldCommand(accountId, 'Status__c', 'Active'));
invoker.addToQueue(new UpdateFieldCommand(accountId, 'Priority__c', 'High'));

// Execute all
invoker.executeQueue();

// Undo last operation
invoker.undoLast();
```

### Use Cases
- Wizard/multi-step processes with undo
- Audit trail with replayable operations
- Batch processing with deferred execution
- Macro recording and playback

---

## Facade Pattern

### Purpose
Provide simplified interface to complex subsystems. Reduce coupling between client and implementation details.

### Implementation

```apex
// Complex subsystems
public class CustomerVerificationService {
    public Boolean verifyIdentity(String customerId) {
        // Complex identity verification logic
        return true;
    }
}

public class CreditCheckService {
    public Integer getCreditScore(String customerId) {
        // Call external credit bureau
        return 720;
    }

    public Decimal getAvailableCredit(String customerId) {
        return 50000.00;
    }
}

public class RiskAssessmentService {
    public String assessRisk(Integer creditScore, Decimal requestedAmount) {
        if (creditScore > 700 && requestedAmount < 25000) return 'LOW';
        if (creditScore > 600) return 'MEDIUM';
        return 'HIGH';
    }
}

public class LoanApplicationService {
    public Id createApplication(Id accountId, Decimal amount) {
        Loan_Application__c app = new Loan_Application__c(
            Account__c = accountId,
            Amount__c = amount,
            Status__c = 'Pending'
        );
        insert app;
        return app.Id;
    }
}

// FACADE: Simplified interface
public class LoanFacade {
    private CustomerVerificationService verificationService;
    private CreditCheckService creditService;
    private RiskAssessmentService riskService;
    private LoanApplicationService applicationService;

    public LoanFacade() {
        this.verificationService = new CustomerVerificationService();
        this.creditService = new CreditCheckService();
        this.riskService = new RiskAssessmentService();
        this.applicationService = new LoanApplicationService();
    }

    // Single method hides all complexity
    public LoanResult applyForLoan(Id accountId, String customerId, Decimal amount) {
        LoanResult result = new LoanResult();

        // Step 1: Verify customer
        if (!verificationService.verifyIdentity(customerId)) {
            result.success = false;
            result.message = 'Identity verification failed';
            return result;
        }

        // Step 2: Check credit
        Integer creditScore = creditService.getCreditScore(customerId);
        Decimal availableCredit = creditService.getAvailableCredit(customerId);

        if (amount > availableCredit) {
            result.success = false;
            result.message = 'Requested amount exceeds available credit';
            return result;
        }

        // Step 3: Assess risk
        String riskLevel = riskService.assessRisk(creditScore, amount);

        // Step 4: Create application
        result.applicationId = applicationService.createApplication(accountId, amount);
        result.success = true;
        result.riskLevel = riskLevel;
        result.message = 'Loan application submitted successfully';

        return result;
    }

    public class LoanResult {
        public Boolean success;
        public Id applicationId;
        public String riskLevel;
        public String message;
    }
}
```

### Usage

```apex
// Client code is simple - no knowledge of subsystems
LoanFacade facade = new LoanFacade();
LoanFacade.LoanResult result = facade.applyForLoan(accountId, 'CUST-123', 15000.00);

if (result.success) {
    System.debug('Loan approved with risk level: ' + result.riskLevel);
} else {
    System.debug('Loan denied: ' + result.message);
}
```

### When to Use
- Simplifying access to complex subsystems
- Creating API layers for external integrations
- Reducing dependencies on multiple services
- Providing entry points for different client needs

---

## Domain Class Pattern

> 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
> [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*

### Purpose

Encapsulate business rules in domain-specific classes, making code read like plain English and enabling reuse across the application.

### Implementation

```apex
/**
 * Domain class encapsulating Account business rules
 * Rules live here, not scattered across triggers/services
 */
public class AccountRules {

    public static Boolean isStrategicAccount(Account account) {
        return isEnterpriseCustomer(account) &&
               isHighValue(account) &&
               isInTargetMarket(account);
    }

    public static Boolean isEnterpriseCustomer(Account account) {
        return account.Type == 'Enterprise' &&
               account.NumberOfEmployees > 500;
    }

    public static Boolean isHighValue(Account account) {
        return account.AnnualRevenue != null &&
               account.AnnualRevenue > 1000000;
    }

    public static Boolean isInTargetMarket(Account account) {
        Set<String> targetIndustries = new Set<String>{
            'Technology', 'Finance', 'Healthcare'
        };
        Set<String> targetCountries = new Set<String>{
            'United States', 'Canada', 'United Kingdom'
        };

        return targetIndustries.contains(account.Industry) &&
               targetCountries.contains(account.BillingCountry);
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
