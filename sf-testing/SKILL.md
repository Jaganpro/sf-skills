---
name: sf-testing
description: >
  Comprehensive Salesforce testing skill with test execution, code coverage analysis,
  and agentic test-fix loops. Run Apex tests, analyze coverage, generate test patterns,
  and automatically fix failing tests with 120-point scoring.
license: MIT
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/parse-test-results.py"
          timeout: 30000
---

# sf-testing: Salesforce Test Execution & Coverage Analysis

Expert testing engineer specializing in Apex test execution, code coverage analysis, mock frameworks, and agentic test-fix loops. Execute tests, analyze failures, and automatically fix issues.

## Core Responsibilities

1. **Test Execution**: Run Apex tests via `sf apex run test` with coverage analysis
2. **Coverage Analysis**: Parse coverage reports, identify untested code paths
3. **Failure Analysis**: Parse test failures, identify root causes, suggest fixes
4. **Agentic Test-Fix Loop**: Automatically fix failing tests and re-run until passing
5. **Test Generation**: Create test classes using sf-apex patterns
6. **Bulk Testing**: Validate with 251+ records for governor limit safety

## Workflow (5-Phase Pattern)

### Phase 1: Test Discovery

Use **AskUserQuestion** to gather:
- Test scope (single class, all tests, specific test suite)
- Target org alias
- Coverage threshold requirement (default: 75%, recommended: 90%)
- Whether to enable agentic fix loop

**Then**:
1. Check existing tests: `Glob: **/*Test*.cls`, `Glob: **/*_Test.cls`
2. Check for Test Data Factories: `Glob: **/*TestDataFactory*.cls`
3. Create TodoWrite tasks

### Phase 2: Test Execution

**Run Single Test Class**:
```bash
sf apex run test --class-names MyClassTest --code-coverage --result-format json --output-dir test-results --target-org [alias]
```

**Run All Tests**:
```bash
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --output-dir test-results --target-org [alias]
```

**Run Specific Methods**:
```bash
sf apex run test --tests MyClassTest.testMethod1 --tests MyClassTest.testMethod2 --code-coverage --result-format json --target-org [alias]
```

**Run Test Suite**:
```bash
sf apex run test --suite-names MySuite --code-coverage --result-format json --target-org [alias]
```

**Run All Tests (Concise — Failures Only)**:
```bash
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --concise --target-org [alias]
```

### Phase 3: Results Analysis

**Parse test-results JSON**:
```
Read: test-results/test-run-id.json
```

**Coverage Summary Output**:
```
📊 TEST EXECUTION RESULTS
════════════════════════════════════════════════════════════════

Test Run ID: 707xx0000000000
Org: my-sandbox
Duration: 45.2s

SUMMARY
───────────────────────────────────────────────────────────────
✅ Passed:    42
❌ Failed:    3
⏭️ Skipped:   0
📈 Coverage: 78.5%

FAILED TESTS
───────────────────────────────────────────────────────────────
❌ AccountServiceTest.testBulkInsert
   Line 45: System.AssertException: Assertion Failed
   Expected: 200, Actual: 199

❌ LeadScoringTest.testNullHandling
   Line 23: System.NullPointerException: Attempt to de-reference null

❌ OpportunityTriggerTest.testValidation
   Line 67: System.DmlException: FIELD_CUSTOM_VALIDATION_EXCEPTION

COVERAGE BY CLASS
───────────────────────────────────────────────────────────────
Class                          Lines    Covered  Uncovered  %
AccountService                 150      142      8          94.7% ✅
LeadScoringService            85       68       17         80.0% ✅
OpportunityTrigger            45       28       17         62.2% ⚠️
ContactHelper                 30       15       15         50.0% ❌

UNCOVERED LINES (OpportunityTrigger)
───────────────────────────────────────────────────────────────
Lines 23-28: Exception handling block
Lines 45-52: Bulk processing edge case
Lines 78-82: Null check branch
```

### Phase 4: Agentic Test-Fix Loop

**When tests fail, automatically:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC TEST-FIX LOOP                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Parse failure message and stack trace                        │
│  2. Identify root cause:                                         │
│     - Assertion failure → Check expected vs actual               │
│     - NullPointerException → Add null checks                     │
│     - DmlException → Check validation rules, required fields     │
│     - LimitException → Reduce SOQL/DML in test                  │
│  3. Read the failing test class                                  │
│  4. Read the class under test                                    │
│  5. Generate fix using sf-apex skill                             │
│  6. Re-run the specific failing test                             │
│  7. Repeat until passing (max 3 attempts)                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Failure Analysis Decision Tree**:

| Error Type | Root Cause | Auto-Fix Strategy |
|------------|------------|-------------------|
| `System.AssertException` | Wrong expected value or logic bug | Analyze assertion, check if test or code is wrong |
| `System.NullPointerException` | Missing null check or test data | Add null safety or fix test data setup |
| `System.DmlException` | Validation rule, required field, trigger | Check org config, add required fields to test data |
| `System.LimitException` | Governor limit hit | Refactor to use bulkified patterns |
| `System.QueryException` | No rows returned | Add test data or adjust query |
| `System.TypeException` | Type mismatch | Fix type casting or data format |

**Auto-Fix Command**:
```
Skill(skill="sf-apex", args="Fix failing test [TestClassName].[methodName] - Error: [error message]")
```

### Cross-Skill: Flow Testing

For Flow-specific tests (not Apex), use `sf flow run test`:
```bash
sf flow run test --test-names FlowTest1,FlowTest2 --target-org [alias]
sf flow get test --test-run-id <id> --target-org [alias]
```

> See `/sf-flow` for full Flow testing documentation.

### Unified Test Runner [Beta]

`sf logic run test` runs both Apex and Flow tests in a single command (Beta, v2.107.6+):
```bash
sf logic run test --test-level RunLocalTests --code-coverage --target-org [alias]
```

> **⚠️ Beta**: This command may change. For production use, prefer `sf apex run test` and `sf flow run test` separately.

### Phase 5: Coverage Improvement

**If coverage < threshold**:

1. **Identify Uncovered Lines**:
```bash
sf apex run test --class-names MyClassTest --code-coverage --detailed-coverage --result-format json --target-org [alias]
```

2. **Generate Tests for Uncovered Code**:
```
Read: force-app/main/default/classes/MyClass.cls (lines 45-52)
```
Then use sf-apex to generate test methods targeting those lines.

3. **Bulk Test Validation**:
```
Skill(skill="sf-data", args="Create 251 [ObjectName] records for bulk testing")
```

4. **Re-run with New Tests**:
```bash
sf apex run test --class-names MyClassTest --code-coverage --result-format json --target-org [alias]
```

---

## Best Practices (120-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Test Coverage** | 25 | 90%+ class coverage; all public methods tested; edge cases covered |
| **Assertion Quality** | 25 | Assert class used; meaningful messages; positive AND negative tests |
| **Bulk Testing** | 20 | Test with 251+ records; verify no SOQL/DML in loops under load |
| **Test Data** | 20 | Test Data Factory used; no hardcoded IDs; @TestSetup for efficiency |
| **Isolation** | 15 | SeeAllData=false; no org dependencies; mock external callouts |
| **Documentation** | 15 | Test method names describe scenario; comments for complex setup |

**Scoring Thresholds**:
```
⭐⭐⭐⭐⭐ 108-120 pts (90%+)  → Production Ready
⭐⭐⭐⭐   96-107 pts (80-89%) → Good, minor improvements
⭐⭐⭐    84-95 pts  (70-79%) → Acceptable, needs work
⭐⭐      72-83 pts  (60-69%) → Below standard
⭐        <72 pts   (<60%)   → BLOCKED - Major issues
```

---

## ⛔ TESTING GUARDRAILS (MANDATORY)

**BEFORE running tests, verify:**

| Check | Command | Why |
|-------|---------|-----|
| Org authenticated | `sf org display --target-org [alias]` | Tests need valid org connection |
| Classes deployed | `sf project deploy report --target-org [alias]` | Can't test undeployed code |
| Test data exists | Check @TestSetup or TestDataFactory | Tests need data to operate on |

**NEVER do these:**

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| `@IsTest(SeeAllData=true)` | Tests depend on org data, break in clean orgs | Always `SeeAllData=false` (default) |
| Hardcoded Record IDs | IDs differ between orgs | Query or create in test |
| No assertions | Tests pass without validating anything | Assert every expected outcome |
| Single record tests only | Misses bulk trigger issues | Always test with 200+ records |
| `Test.startTest()` without `Test.stopTest()` | Async code won't execute | Always pair start/stop |

---

## CLI Command Reference

### Test Execution Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf apex run test` | Run tests | See examples above |
| `sf apex get test` | Get async test status | `sf apex get test --test-run-id 707xx...` |
| `sf apex list log` | List debug logs | `sf apex list log --target-org alias` |
| `sf apex tail log` | Stream logs real-time | `sf apex tail log --target-org alias` |

### Useful Flags

| Flag | Purpose |
|------|---------|
| `--code-coverage` | Include coverage in results |
| `--detailed-coverage` | Line-by-line coverage (slower) |
| `--result-format json` | Machine-parseable output |
| `--output-dir` | Save results to directory |
| `--synchronous` | Wait for completion (default) |
| `--test-level RunLocalTests` | All tests except managed packages |
| `--test-level RunAllTestsInOrg` | Every test including packages |

---

## Test Patterns & Templates

### Pattern 1: Basic Test Class

Use template: `templates/basic-test.cls`

```apex
@IsTest
private class AccountServiceTest {

    @TestSetup
    static void setupTestData() {
        // Use Test Data Factory for consistent data creation
        List<Account> accounts = TestDataFactory.createAccounts(5);
        insert accounts;
    }

    @IsTest
    static void testCreateAccount_Success() {
        // Given
        Account testAccount = new Account(Name = 'Test Account');

        // When
        Test.startTest();
        Id accountId = AccountService.createAccount(testAccount);
        Test.stopTest();

        // Then
        Assert.isNotNull(accountId, 'Account ID should not be null');
        Account inserted = [SELECT Name FROM Account WHERE Id = :accountId];
        Assert.areEqual('Test Account', inserted.Name, 'Account name should match');
    }

    @IsTest
    static void testCreateAccount_NullInput_ThrowsException() {
        // Given
        Account nullAccount = null;

        // When/Then
        try {
            Test.startTest();
            AccountService.createAccount(nullAccount);
            Test.stopTest();
            Assert.fail('Expected IllegalArgumentException was not thrown');
        } catch (IllegalArgumentException e) {
            Assert.isTrue(e.getMessage().contains('cannot be null'),
                'Error message should mention null: ' + e.getMessage());
        }
    }
}
```

### Pattern 2: Bulk Test (251+ Records)

Use template: `templates/bulk-test.cls`

```apex
@IsTest
static void testBulkInsert_251Records() {
    // Given - 251 records crosses the 200-record batch boundary
    List<Account> accounts = TestDataFactory.createAccounts(251);

    // When
    Test.startTest();
    insert accounts;  // Triggers fire in batches of 200, then 51
    Test.stopTest();

    // Then
    Integer count = [SELECT COUNT() FROM Account];
    Assert.areEqual(251, count, 'All 251 accounts should be inserted');

    // Verify no governor limits hit
    Assert.isTrue(Limits.getQueries() < 100,
        'Should not approach SOQL limit: ' + Limits.getQueries());
}
```

### Pattern 3: Mock Callout Test

Use template: `templates/mock-callout-test.cls`

```apex
@IsTest
private class ExternalAPIServiceTest {

    // Mock class for HTTP callouts
    private class MockHttpResponse implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            res.setBody('{"success": true, "data": {"id": "12345"}}');
            return res;
        }
    }

    @IsTest
    static void testCallExternalAPI_Success() {
        // Given
        Test.setMock(HttpCalloutMock.class, new MockHttpResponse());

        // When
        Test.startTest();
        String result = ExternalAPIService.callAPI('test-endpoint');
        Test.stopTest();

        // Then
        Assert.isTrue(result.contains('success'), 'Response should indicate success');
    }
}
```

### Pattern 4: Test Data Factory

Use template: `templates/test-data-factory.cls`

```apex
@IsTest
public class TestDataFactory {

    public static List<Account> createAccounts(Integer count) {
        List<Account> accounts = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            accounts.add(new Account(
                Name = 'Test Account ' + i,
                Industry = 'Technology',
                BillingCity = 'San Francisco'
            ));
        }
        return accounts;
    }

    public static List<Contact> createContacts(Integer count, Id accountId) {
        List<Contact> contacts = new List<Contact>();
        for (Integer i = 0; i < count; i++) {
            contacts.add(new Contact(
                FirstName = 'Test',
                LastName = 'Contact ' + i,
                AccountId = accountId,
                Email = 'test' + i + '@example.com'
            ));
        }
        return contacts;
    }

    // Convenience method with insert
    public static List<Account> createAndInsertAccounts(Integer count) {
        List<Account> accounts = createAccounts(count);
        insert accounts;
        return accounts;
    }
}
```

---

## Agentic Test-Fix Loop Implementation

### How It Works

When the agentic loop is enabled, sf-testing will:

1. **Run tests** and capture results
2. **Parse failures** to identify error type and location
3. **Read source files** (test class + class under test)
4. **Analyze root cause** using the decision tree above
5. **Generate fix** by invoking sf-apex skill
6. **Re-run failing test** to verify fix
7. **Iterate** until passing or max attempts (3)

### Example Agentic Flow

```
User: "Run tests for AccountService with auto-fix enabled"

Claude:
1. sf apex run test --class-names AccountServiceTest --code-coverage --result-format json
2. Parse results: 1 failure - testBulkInsert line 45 NullPointerException
3. Read AccountServiceTest.cls (line 45 context)
4. Read AccountService.cls (trace the null reference)
5. Identify: Missing null check in AccountService.processAccounts()
6. Skill(sf-apex): Add null safety to AccountService.processAccounts()
7. Deploy fix
8. Re-run: sf apex run test --tests AccountServiceTest.testBulkInsert
9. ✅ Passing! Report success.
```

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-apex | Generate test classes, fix failing code | `Skill(skill="sf-apex", args="Create test class for LeadService")` |
| sf-data | Create bulk test data (251+ records) | `Skill(skill="sf-data", args="Create 251 Leads for bulk testing")` |
| sf-deploy | Deploy test classes to org | `Skill(skill="sf-deploy", args="Deploy tests to sandbox")` |
| sf-debug | Analyze failures with debug logs | `Skill(skill="sf-debug", args="Analyze test failure logs")` |

---

## Common Test Failures & Fixes

| Failure | Likely Cause | Fix |
|---------|--------------|-----|
| `MIXED_DML_OPERATION` | User + non-setup object in same transaction | Use `System.runAs()` or separate transactions |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | Trigger or flow error | Check trigger logic with debug logs |
| `REQUIRED_FIELD_MISSING` | Test data incomplete | Add required fields to TestDataFactory |
| `DUPLICATE_VALUE` | Unique field conflict | Use dynamic values or delete existing |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule fired | Meet validation criteria in test data |
| `UNABLE_TO_LOCK_ROW` | Record lock conflict | Use `FOR UPDATE` or retry logic |

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated
**Recommended**: sf-apex (for auto-fix), sf-data (for bulk test data), sf-debug (for log analysis)

Install: `/plugin install github:Jaganpro/sf-skills/sf-testing`

---

## Documentation

| Document | Description |
|----------|-------------|
| [testing-best-practices.md](docs/testing-best-practices.md) | General testing guidelines |
| [cli-commands.md](docs/cli-commands.md) | SF CLI test commands |
| [mocking-patterns.md](docs/mocking-patterns.md) | Mocking vs Stubbing, DML mocking, HttpCalloutMock |
| [performance-optimization.md](docs/performance-optimization.md) | Fast tests, reduce execution time |

## Templates

| Template | Description |
|----------|-------------|
| [basic-test.cls](templates/basic-test.cls) | Standard test class with Given-When-Then |
| [bulk-test.cls](templates/bulk-test.cls) | 251+ record bulk testing |
| [mock-callout-test.cls](templates/mock-callout-test.cls) | HTTP callout mocking |
| [test-data-factory.cls](templates/test-data-factory.cls) | Reusable test data creation |
| [dml-mock.cls](templates/dml-mock.cls) | DML abstraction for 35x faster tests |
| [stub-provider-example.cls](templates/stub-provider-example.cls) | StubProvider for dynamic behavior |

---

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments of community resources that shaped this skill.

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
