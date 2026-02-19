<!-- Parent: sf-testing/SKILL.md -->
# Apex Testing Best Practices

## Overview

This guide covers best practices for writing effective, maintainable Apex tests that ensure code quality and prevent regressions.

## The Testing Pyramid

```
                    ╱╲
                   ╱  ╲
                  ╱ E2E╲        Few end-to-end tests
                 ╱──────╲
                ╱        ╲
               ╱Integration╲    Moderate integration tests
              ╱────────────╲
             ╱              ╲
            ╱   Unit Tests   ╲  Many unit tests
           ╱──────────────────╲
```

## Core Principles

### 1. Test One Thing Per Method

```apex
// ❌ BAD: Testing multiple things
@IsTest
static void testEverything() {
    Account acc = new Account(Name = 'Test');
    insert acc;
    acc.Name = 'Updated';
    update acc;
    delete acc;
    // What exactly are we testing?
}

// ✅ GOOD: Single responsibility
@IsTest
static void testAccountInsert_ValidName_Success() {
    Account acc = new Account(Name = 'Test');
    insert acc;
    Assert.isNotNull(acc.Id, 'Account should be inserted');
}

@IsTest
static void testAccountUpdate_ChangeName_Success() {
    Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
    acc.Name = 'Updated';
    update acc;
    Account updated = [SELECT Name FROM Account WHERE Id = :acc.Id];
    Assert.areEqual('Updated', updated.Name, 'Name should be updated');
}
```

### 2. Use Descriptive Test Names

```apex
// ❌ BAD: Unclear names
@IsTest static void test1() { }
@IsTest static void testMethod() { }

// ✅ GOOD: Describes scenario, condition, and expectation
@IsTest static void testCreateAccount_WithValidData_ReturnsId() { }
@IsTest static void testCreateAccount_WithNullName_ThrowsException() { }
@IsTest static void testBulkInsert_251Records_AllSucceed() { }
```

### 3. Follow AAA Pattern (Arrange-Act-Assert)

```apex
@IsTest
static void testCalculateDiscount_VIPCustomer_Returns20Percent() {
    // ARRANGE - Set up test data
    Account vipAccount = new Account(
        Name = 'VIP Customer',
        Type = 'VIP'
    );
    insert vipAccount;

    // ACT - Execute the code under test
    Test.startTest();
    Decimal discount = DiscountService.calculateDiscount(vipAccount.Id);
    Test.stopTest();

    // ASSERT - Verify results
    Assert.areEqual(0.20, discount, 'VIP customers should get 20% discount');
}
```

## Test Data Factory Pattern

### Why Use Test Data Factory?

1. **Consistency**: Same data creation logic everywhere
2. **Maintainability**: Change in one place affects all tests
3. **Readability**: Tests focus on logic, not data setup
4. **Flexibility**: Easy to create variations

### Factory Methods

```apex
@IsTest
public class TestDataFactory {

    // Basic creation (no insert)
    public static List<Account> createAccounts(Integer count) {
        List<Account> accounts = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            accounts.add(new Account(
                Name = 'Test Account ' + i,
                Industry = 'Technology'
            ));
        }
        return accounts;
    }

    // Create and insert
    public static List<Account> createAndInsertAccounts(Integer count) {
        List<Account> accounts = createAccounts(count);
        insert accounts;
        return accounts;
    }

    // With specific attributes
    public static Account createAccount(String name, String industry) {
        return new Account(Name = name, Industry = industry);
    }
}
```

## @TestSetup for Efficiency

```apex
@IsTest
private class AccountServiceTest {

    @TestSetup
    static void setupTestData() {
        // This runs ONCE for all test methods in the class
        // Data is rolled back after each test method
        List<Account> accounts = TestDataFactory.createAccounts(10);
        insert accounts;

        List<Contact> contacts = new List<Contact>();
        for (Account acc : accounts) {
            contacts.addAll(TestDataFactory.createContacts(5, acc.Id));
        }
        insert contacts;
    }

    @IsTest
    static void testMethod1() {
        // Has access to 10 accounts and 50 contacts
        List<Account> accounts = [SELECT Id FROM Account];
        Assert.areEqual(10, accounts.size());
    }

    @IsTest
    static void testMethod2() {
        // ALSO has access to 10 accounts and 50 contacts
        // @TestSetup data is available to all test methods
        List<Contact> contacts = [SELECT Id FROM Contact];
        Assert.areEqual(50, contacts.size());
    }
}
```

## Bulk Testing (251+ Records)

### Why 251 Records?

Triggers process records in batches of 200. Testing with 251 records ensures:
- First batch: 200 records
- Second batch: 51 records
- Crosses the batch boundary, revealing bulkification issues

```apex
@IsTest
static void testTrigger_BulkInsert_NoDMLInLoop() {
    // ARRANGE
    List<Account> accounts = TestDataFactory.createAccounts(251);

    // ACT
    Test.startTest();
    insert accounts;  // Trigger fires twice: 200, then 51
    Test.stopTest();

    // ASSERT
    Assert.areEqual(251, [SELECT COUNT() FROM Account],
        'All 251 accounts should be created');

    // Verify governor limits not approached
    Assert.isTrue(Limits.getQueries() < 90,
        'Should not approach SOQL limit');
}
```

## Negative Testing

### Test for Expected Failures

```apex
@IsTest
static void testCreateAccount_NullName_ThrowsException() {
    try {
        Account acc = new Account(Name = null);
        insert acc;
        Assert.fail('Expected DmlException was not thrown');
    } catch (DmlException e) {
        Assert.isTrue(
            e.getMessage().contains('REQUIRED_FIELD_MISSING'),
            'Should throw required field error'
        );
    }
}

@IsTest
static void testWithdraw_InsufficientFunds_ReturnsFalse() {
    Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
    acc.AnnualRevenue = 100;
    update acc;

    Test.startTest();
    Boolean result = AccountService.withdraw(acc.Id, 200);
    Test.stopTest();

    Assert.isFalse(result, 'Withdrawal should fail with insufficient funds');
}
```

## Mock Framework Patterns

### HttpCalloutMock

```apex
private class SuccessHttpMock implements HttpCalloutMock {
    public HttpResponse respond(HttpRequest req) {
        HttpResponse res = new HttpResponse();
        res.setStatusCode(200);
        res.setBody('{"success": true}');
        return res;
    }
}

@IsTest
static void testExternalAPICall_Success() {
    Test.setMock(HttpCalloutMock.class, new SuccessHttpMock());

    Test.startTest();
    String result = MyService.callExternalAPI();
    Test.stopTest();

    Assert.isTrue(result.contains('success'));
}
```

### Stub API (Test.StubProvider)

```apex
@IsTest
private class AccountServiceTest {

    // Stub for dependency injection
    private class SelectorStub implements System.StubProvider {
        public Object handleMethodCall(
            Object stubbedObject,
            String stubbedMethodName,
            Type returnType,
            List<Type> paramTypes,
            List<String> paramNames,
            List<Object> args
        ) {
            if (stubbedMethodName == 'getAccountById') {
                return new Account(Name = 'Mocked Account');
            }
            return null;
        }
    }

    @IsTest
    static void testServiceWithMockedSelector() {
        // Create stub
        AccountSelector mockSelector = (AccountSelector) Test.createStub(
            AccountSelector.class,
            new SelectorStub()
        );

        // Inject into service
        AccountService service = new AccountService(mockSelector);

        // Test with mocked dependency
        Test.startTest();
        Account result = service.getAccount('001xx000000001');
        Test.stopTest();

        Assert.areEqual('Mocked Account', result.Name);
    }
}
```

## Governor Limit Testing

```apex
@IsTest
static void testBulkOperation_StaysWithinLimits() {
    List<Account> accounts = TestDataFactory.createAccounts(200);

    Test.startTest();
    insert accounts;
    Test.stopTest();

    // Assert limits not exceeded
    System.debug('SOQL queries used: ' + Limits.getQueries());
    System.debug('DML statements used: ' + Limits.getDmlStatements());

    Assert.isTrue(Limits.getQueries() < 100,
        'Should stay under SOQL limit: ' + Limits.getQueries());
    Assert.isTrue(Limits.getDmlStatements() < 150,
        'Should stay under DML limit: ' + Limits.getDmlStatements());
}
```

## Common Anti-Patterns to Avoid

### ❌ SeeAllData=true

```apex
// ❌ BAD: Depends on org data
@IsTest(SeeAllData=true)
static void testBadPattern() {
    Account acc = [SELECT Id FROM Account LIMIT 1];
    // This will fail in empty orgs!
}

// ✅ GOOD: Creates own data
@IsTest
static void testGoodPattern() {
    Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
    // Works in any org
}
```

### ❌ No Assertions

```apex
// ❌ BAD: No assertions - test passes even if code is broken
@IsTest
static void testNoAssertions() {
    Account acc = new Account(Name = 'Test');
    insert acc;
    // Test "passes" but proves nothing
}

// ✅ GOOD: Meaningful assertions
@IsTest
static void testWithAssertions() {
    Account acc = new Account(Name = 'Test');
    insert acc;
    Assert.isNotNull(acc.Id, 'Account should have an Id after insert');
    Account inserted = [SELECT Name FROM Account WHERE Id = :acc.Id];
    Assert.areEqual('Test', inserted.Name, 'Name should be preserved');
}
```

### ❌ Hardcoded IDs

```apex
// ❌ BAD: Hardcoded IDs fail across orgs
Account acc = [SELECT Id FROM Account WHERE Id = '001xx0000000001'];

// ✅ GOOD: Query or create dynamically
Account acc = TestDataFactory.createAndInsertAccounts(1)[0];
```

## Test Method Template

```apex
/**
 * @description Tests [method] with [condition] expecting [outcome]
 */
@IsTest
static void test[Method]_[Condition]_[ExpectedOutcome]() {
    // ═══════════════════════════════════════════════════════════════
    // ARRANGE - Set up test data and conditions
    // ═══════════════════════════════════════════════════════════════
    // Create test data using TestDataFactory
    // Set up any mocks needed

    // ═══════════════════════════════════════════════════════════════
    // ACT - Execute the code under test
    // ═══════════════════════════════════════════════════════════════
    Test.startTest();
    // Call the method being tested
    Test.stopTest();

    // ═══════════════════════════════════════════════════════════════
    // ASSERT - Verify expected outcomes
    // ═══════════════════════════════════════════════════════════════
    // Assert.areEqual(expected, actual, 'Descriptive message');
    // Assert.isTrue(condition, 'Descriptive message');
    // Assert.isNotNull(value, 'Descriptive message');
}
```

---

## Test Speed Philosophy

> 💡 *Principles inspired by "Clean Apex Code" by Pablo Gonzalez.
> [Purchase the book](https://link.springer.com/book/10.1007/979-8-8688-1411-2) for complete coverage.*

### Why Test Speed Matters

Fast tests enable continuous integration. Slow tests become barriers to frequent commits.

### Target Metrics

| Test Type | Target Speed | Purpose |
|-----------|--------------|---------|
| Unit test (no DML) | < 50ms | Test pure business logic |
| Unit test (mocked DML) | < 100ms | Test with stubbed database |
| Integration test | < 500ms | Verify real database behavior |
| Full scenario test | < 2000ms | End-to-end validation |

### Speed Strategy

```
┌─────────────────────────────────────────────────────────────┐
│  INTEGRATION TESTS (Few)                                    │
│  - Real DML, real triggers                                  │
│  - Test happy path completely                               │
│  - Slow but high confidence                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  UNIT TESTS WITH MOCKS (Many)                               │
│  - Stub database operations                                 │
│  - Test edge cases, variations                              │
│  - Fast, run on every save                                  │
└─────────────────────────────────────────────────────────────┘
```

### Balance Reality vs Speed

```apex
// INTEGRATION TEST: Full database interaction (slower, realistic)
@IsTest
static void testAccountCreation_Integration() {
    Test.startTest();
    Account acc = new Account(Name = 'Test');
    insert acc;
    Test.stopTest();

    Account queried = [SELECT Name, Status__c FROM Account WHERE Id = :acc.Id];
    Assert.areEqual('Active', queried.Status__c, 'Trigger should set status');
}

// UNIT TEST: Mocked database (faster, tests logic only)
@IsTest
static void testAccountRules_IsHighValue() {
    // No database interaction - tests pure logic
    Account acc = new Account(AnnualRevenue = 1500000);
    Assert.isTrue(AccountRules.isHighValue(acc), 'Should be high value');

    Account lowValue = new Account(AnnualRevenue = 500000);
    Assert.isFalse(AccountRules.isHighValue(lowValue), 'Should not be high value');
}
```

### Techniques for Faster Tests

| Technique | Benefit | Trade-off |
|-----------|---------|-----------|
| @TestSetup | Reuse data across methods | Small setup overhead |
| Stub API | No real DML | Less realistic |
| Selector mocking | Skip SOQL | Must trust Selector |
| Domain class testing | Pure logic, no DB | Limited scope |
| Avoid SeeAllData | Predictable data | Must create test data |

### When to Prioritize Speed vs Reality

| Scenario | Priority | Approach |
|----------|----------|----------|
| Business logic validation | Speed | Unit test with mocks |
| Trigger behavior | Reality | Integration test |
| Edge case coverage | Speed | Many unit tests |
| Deployment validation | Reality | RunLocalTests |
| Developer feedback loop | Speed | Fast unit tests |

### Measuring Test Speed

```bash
# Run tests and view timing
sf apex test run --test-level RunLocalTests --target-org alias --result-format human

# Check individual test timing
sf apex test get --test-run-id [id] --code-coverage --result-format json | jq '.tests[] | {name: .MethodName, time: .RunTime}'
```

### Fast Test Checklist

```
□ Is there a pure logic portion that can be unit tested?
□ Can database operations be mocked for edge cases?
□ Is @TestSetup reused across multiple test methods?
□ Are tests avoiding SeeAllData=true?
□ Are integration tests reserved for critical paths only?
□ Can SOQL be mocked via Selector pattern?
```
