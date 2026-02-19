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

## Document Map

| Need | Document | Description |
|------|----------|-------------|
| **Test patterns** | [references/test-patterns.md](references/test-patterns.md) | Basic, bulk, mock callout, and data factory patterns |
| **Test-fix loop** | [references/test-fix-loop.md](references/test-fix-loop.md) | Agentic loop implementation & failure decision tree |
| **Best practices** | [references/testing-best-practices.md](references/testing-best-practices.md) | General testing guidelines |
| **CLI commands** | [references/cli-commands.md](references/cli-commands.md) | SF CLI test commands |
| **Mocking** | [references/mocking-patterns.md](references/mocking-patterns.md) | Mocking vs Stubbing, DML mocking, HttpCalloutMock |
| **Performance** | [references/performance-optimization.md](references/performance-optimization.md) | Fast tests, reduce execution time |

---

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

**Run Test Suite / All Tests (Concise)**:
```bash
sf apex run test --suite-names MySuite --code-coverage --result-format json --target-org [alias]
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --concise --target-org [alias]
```

### Phase 3: Results Analysis

Parse `test-results/test-run-id.json` and report:

```
📊 TEST EXECUTION RESULTS
════════════════════════════════════════════════════════════════

SUMMARY
───────────────────────────────────────────────────────────────
✅ Passed:    42    ❌ Failed:    3    📈 Coverage: 78.5%

FAILED TESTS
───────────────────────────────────────────────────────────────
❌ AccountServiceTest.testBulkInsert
   Line 45: System.AssertException: Assertion Failed

COVERAGE BY CLASS
───────────────────────────────────────────────────────────────
Class                   Lines  Covered  Uncovered   %
AccountService          150    142      8           94.7% ✅
OpportunityTrigger      45     28       17          62.2% ⚠️
ContactHelper           30     15       15          50.0% ❌
```

### Phase 4: Agentic Test-Fix Loop

> See [references/test-fix-loop.md](references/test-fix-loop.md) for the full implementation flow and failure analysis decision tree.

When tests fail, the agentic loop: parses failures → reads source → identifies root cause → invokes sf-apex to fix → re-runs (max 3 attempts). Key error types: AssertException, NullPointerException, DmlException, LimitException, QueryException.

### Cross-Skill: Flow Testing

For Flow-specific tests (not Apex), use `sf flow run test`:
```bash
sf flow run test --test-names FlowTest1,FlowTest2 --target-org [alias]
sf flow get test --test-run-id <id> --target-org [alias]
```

> **Unified Test Runner [Beta]**: `sf logic run test --test-level RunLocalTests --code-coverage --target-org [alias]` (v2.107.6+). For production, prefer separate `sf apex run test` and `sf flow run test`.

### Phase 5: Coverage Improvement

**If coverage < threshold**:
1. `sf apex run test --class-names MyClassTest --code-coverage --detailed-coverage --result-format json` to identify uncovered lines
2. Use sf-apex to generate test methods targeting those lines
3. `Skill(skill="sf-data", args="Create 251 [ObjectName] records for bulk testing")`
4. Re-run and verify

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

**Thresholds**: 108+ Excellent | 96+ Good | 84+ Acceptable | 72+ Below standard | <72 BLOCKED

---

## Test Patterns & Templates

> See [references/test-patterns.md](references/test-patterns.md) for full Apex code examples of all 4 patterns.

| Pattern | Template | Use Case |
|---------|----------|----------|
| Basic Test Class | `assets/basic-test.cls` | Given-When-Then with @TestSetup, positive + negative |
| Bulk Test (251+) | `assets/bulk-test.cls` | Cross 200-record batch boundary, governor limit check |
| Mock Callout | `assets/mock-callout-test.cls` | HttpCalloutMock for external API testing |
| Test Data Factory | `assets/test-data-factory.cls` | Reusable data creation with convenience insert |

Additional templates: `assets/dml-mock.cls` (35x faster tests), `assets/stub-provider-example.cls` (dynamic behavior)

---

## Testing Guardrails (MANDATORY)

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

| Command | Purpose | Example |
|---------|---------|---------|
| `sf apex run test` | Run tests | See Phase 2 examples |
| `sf apex get test` | Get async test status | `--test-run-id 707xx...` |
| `sf apex list log` | List debug logs | `--target-org alias` |
| `sf apex tail log` | Stream logs real-time | `--target-org alias` |

**Key flags**: `--code-coverage`, `--detailed-coverage`, `--result-format json`, `--output-dir`, `--test-level RunLocalTests`, `--concise`

---

## Common Test Failures & Fixes

| Failure | Likely Cause | Fix |
|---------|--------------|-----|
| `MIXED_DML_OPERATION` | User + non-setup object in same txn | Use `System.runAs()` or separate transactions |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | Trigger or flow error | Check trigger logic with debug logs |
| `REQUIRED_FIELD_MISSING` | Test data incomplete | Add required fields to TestDataFactory |
| `DUPLICATE_VALUE` | Unique field conflict | Use dynamic values or delete existing |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule fired | Meet validation criteria in test data |
| `UNABLE_TO_LOCK_ROW` | Record lock conflict | Use `FOR UPDATE` or retry logic |

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-apex | Generate test classes, fix failing code | `Skill(skill="sf-apex", args="Create test class for LeadService")` |
| sf-data | Create bulk test data (251+ records) | `Skill(skill="sf-data", args="Create 251 Leads for bulk testing")` |
| sf-deploy | Deploy test classes to org | `Skill(skill="sf-deploy", args="Deploy tests to sandbox")` |
| sf-debug | Analyze failures with debug logs | `Skill(skill="sf-debug", args="Analyze test failure logs")` |

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated
**Recommended**: sf-apex (auto-fix), sf-data (bulk test data), sf-debug (log analysis)
