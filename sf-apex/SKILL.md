---
name: sf-apex
description: >
  Generates and reviews Salesforce Apex code with 2025 best practices and 150-point
  scoring. Use when writing Apex classes, triggers, test classes, batch jobs, or
  reviewing existing Apex code for bulkification, security, and SOLID principles.
license: MIT
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  scoring: "150 points across 8 categories"
hooks:
  SessionStart:
    - type: command
      command: "${SHARED_HOOKS}/check-env-weekly.sh"
      timeout: 5000
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/apex-lsp-validate.py"
          timeout: 15000
        - type: command
          command: "python3 ${SKILL_HOOKS}/post-tool-validate.py"
          timeout: 120000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-apex"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-apex"
      timeout: 5000
---

# sf-apex: Salesforce Apex Code Generation and Review

Expert Apex developer specializing in clean code, SOLID principles, and 2025 best practices. Generate production-ready, secure, performant, and maintainable Apex code.

## Core Responsibilities

1. **Code Generation**: Create Apex classes, triggers (TAF), tests, async jobs from requirements
2. **Code Review**: Analyze existing Apex for best practices violations with actionable fixes
3. **Validation & Scoring**: Score code against 8 categories (0-150 points)
4. **Deployment Integration**: Validate and deploy via sf-deploy skill

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Class type (Trigger, Service, Selector, Batch, Queueable, Test, Controller)
- Primary purpose (one sentence)
- Target object(s)
- Test requirements

**Then**:
1. Check existing code: `Glob: **/*.cls`, `Glob: **/*.trigger`
2. Check for existing Trigger Actions Framework setup: `Glob: **/*TriggerAction*.cls`
3. Create TodoWrite tasks

---

### Phase 2: Design & Template Selection

**Select template**:
| Class Type | Template |
|------------|----------|
| Trigger | `templates/trigger.trigger` |
| Trigger Action | `templates/trigger-action.cls` |
| Service | `templates/service.cls` |
| Selector | `templates/selector.cls` |
| Batch | `templates/batch.cls` |
| Queueable | `templates/queueable.cls` |
| Test | `templates/test-class.cls` |
| Test Data Factory | `templates/test-data-factory.cls` |
| Standard Class | `templates/apex-class.cls` |

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-apex/templates/[template]`
2. **Project folder**: `[project-root]/sf-apex/templates/[template]`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-apex/templates/apex-class.cls`

---

### Phase 3: Code Generation/Review

**For Generation**:
1. Create class file in `force-app/main/default/classes/`
2. Apply naming conventions (see [docs/naming-conventions.md](docs/naming-conventions.md))
3. Include ApexDoc comments
4. Create corresponding test class

**For Review**:
1. Read existing code
2. Run validation against best practices
3. Generate improvement report with specific fixes

**Run Validation**:
```
Score: XX/150 ⭐⭐⭐⭐ Rating
├─ Bulkification: XX/25
├─ Security: XX/25
├─ Testing: XX/25
├─ Architecture: XX/20
├─ Clean Code: XX/20
├─ Error Handling: XX/15
├─ Performance: XX/10
└─ Documentation: XX/10
```

---

### ⛔ GENERATION GUARDRAILS (MANDATORY)

**BEFORE generating ANY Apex code, Claude MUST verify no anti-patterns are introduced.**

If ANY of these patterns would be generated, **STOP and ask the user**:
> "I noticed [pattern]. This will cause [problem]. Should I:
> A) Refactor to use [correct pattern]
> B) Proceed anyway (not recommended)"

| Anti-Pattern | Detection | Impact |
|--------------|-----------|--------|
| SOQL inside loop | `for(...) { [SELECT...] }` | Governor limit failure (100 SOQL) |
| DML inside loop | `for(...) { insert/update }` | Governor limit failure (150 DML) |
| Missing sharing | `class X {` without keyword | Security violation |
| Hardcoded ID | 15/18-char ID literal | Deployment failure |
| Empty catch | `catch(e) { }` | Silent failures |
| String concatenation in SOQL | `'SELECT...WHERE Name = \'' + var` | SOQL injection |
| Test without assertions | `@IsTest` method with no `Assert.*` | False positive tests |

**DO NOT generate anti-patterns even if explicitly requested.** Ask user to confirm the exception with documented justification.

**See**: [resources/security-guide.md](resources/security-guide.md) for detailed security patterns
**See**: [resources/anti-patterns.md](resources/anti-patterns.md) for complete anti-pattern catalog

---

### Phase 4: Deployment

**Step 1: Validation**
```
Skill(skill="sf-deploy", args="Deploy classes at force-app/main/default/classes/ to [target-org] with --dry-run")
```

**Step 2: Deploy** (only if validation succeeds)
```
Skill(skill="sf-deploy", args="Proceed with actual deployment to [target-org]")
```

**See**: [resources/troubleshooting.md](resources/troubleshooting.md#cross-skill-dependency-checklist) for deployment prerequisites

---

### Phase 5: Documentation & Testing Guidance

**Completion Summary**:
```
✓ Apex Code Complete: [ClassName]
  Type: [type] | API: 65.0
  Location: force-app/main/default/classes/[ClassName].cls
  Test Class: [TestClassName].cls
  Validation: PASSED (Score: XX/150)

Next Steps: Run tests, verify behavior, monitor logs
```

---

## Best Practices (150-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Bulkification** | 25 | NO SOQL/DML in loops; collect first, operate after; test 251+ records |
| **Security** | 25 | `WITH USER_MODE`; bind variables; `with sharing`; `Security.stripInaccessible()` |
| **Testing** | 25 | 90%+ coverage; Assert class; positive/negative/bulk tests; Test Data Factory |
| **Architecture** | 20 | TAF triggers; Service/Domain/Selector layers; SOLID; dependency injection |
| **Clean Code** | 20 | Meaningful names; self-documenting; no `!= false`; single responsibility |
| **Error Handling** | 15 | Specific before generic catch; no empty catch; custom business exceptions |
| **Performance** | 10 | Monitor with `Limits`; cache expensive ops; scope variables; async for heavy |
| **Documentation** | 10 | ApexDoc on classes/methods; meaningful params |

**Thresholds**: ✅ 90+ (Deploy) | ⚠️ 67-89 (Review) | ❌ <67 (Block - fix required)

**Deep Dives**:
- [resources/bulkification-guide.md](resources/bulkification-guide.md) - Governor limits, collection handling
- [resources/security-guide.md](resources/security-guide.md) - CRUD/FLS, sharing, injection prevention
- [resources/testing-patterns.md](resources/testing-patterns.md) - Exception types, mocking, coverage
- [resources/patterns-deep-dive.md](resources/patterns-deep-dive.md) - TAF, @InvocableMethod, async patterns

---

## Trigger Actions Framework (TAF)

### Quick Reference

**When to Use**: If TAF package is installed in target org (check: `sf package installed list`)

**Trigger Pattern** (one per object):
```apex
trigger AccountTrigger on Account (before insert, after insert, before update, after update, before delete, after delete, after undelete) {
    new MetadataTriggerHandler().run();
}
```

**Action Class** (one per behavior):
```apex
public class TA_Account_SetDefaults implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Account> newList) {
        for (Account acc : newList) {
            if (acc.Industry == null) {
                acc.Industry = 'Other';
            }
        }
    }
}
```

**⚠️ CRITICAL**: TAF triggers do NOTHING without `Trigger_Action__mdt` records! Each action class needs a corresponding Custom Metadata record.

**Installation**:
```bash
sf package install --package 04tKZ000000gUEFYA2 --target-org [alias] --wait 10
```

**Fallback**: If TAF is NOT installed, use standard trigger pattern (see [resources/patterns-deep-dive.md](resources/patterns-deep-dive.md#standard-trigger-pattern))

**See**: [resources/patterns-deep-dive.md](resources/patterns-deep-dive.md#trigger-actions-framework-taf) for complete TAF patterns and Custom Metadata setup

---

## Async Decision Matrix

| Scenario | Use |
|----------|-----|
| Simple callout, fire-and-forget | `@future(callout=true)` |
| Complex logic, needs chaining | `Queueable` |
| Process millions of records | `Batch Apex` |
| Scheduled/recurring job | `Schedulable` |
| Post-queueable cleanup | `Queueable Finalizer` |

**See**: [resources/patterns-deep-dive.md](resources/patterns-deep-dive.md#async-patterns) for detailed async patterns

---

## Modern Apex Features (API 62.0)

- **Null coalescing**: `value ?? defaultValue`
- **Safe navigation**: `record?.Field__c`
- **User mode**: `WITH USER_MODE` in SOQL
- **Assert class**: `Assert.areEqual()`, `Assert.isTrue()`

**Breaking Change (API 62.0)**: Cannot modify Set while iterating - throws `System.FinalException`

**See**: [resources/bulkification-guide.md](resources/bulkification-guide.md#collection-handling-best-practices) for collection usage

---

## Flow Integration (@InvocableMethod)

Apex classes can be called from Flow using `@InvocableMethod`. This pattern enables complex business logic, DML, callouts, and integrations from declarative automation.

### Quick Pattern

```apex
public with sharing class RecordProcessor {

    @InvocableMethod(label='Process Record' category='Custom')
    public static List<Response> execute(List<Request> requests) {
        List<Response> responses = new List<Response>();
        for (Request req : requests) {
            Response res = new Response();
            res.isSuccess = true;
            res.processedId = req.recordId;
            responses.add(res);
        }
        return responses;
    }

    public class Request {
        @InvocableVariable(label='Record ID' required=true)
        public Id recordId;
    }

    public class Response {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Processed ID')
        public Id processedId;
    }
}
```

**Template**: Use `templates/invocable-method.cls` for complete pattern

**See**:
- [resources/patterns-deep-dive.md](resources/patterns-deep-dive.md#flow-integration-invocablemethod) - Complete @InvocableMethod guide
- [docs/flow-integration.md](docs/flow-integration.md) - Advanced Flow-Apex patterns
- [docs/triangle-pattern.md](docs/triangle-pattern.md) - Flow-LWC-Apex triangle

---

## Testing Best Practices

### The 3 Test Types (PNB Pattern)

Every feature needs:
1. **Positive**: Happy path test
2. **Negative**: Error handling test
3. **Bulk**: 251+ records test

**Example**:
```apex
@IsTest
static void testPositive() {
    Account acc = new Account(Name = 'Test', Industry = 'Tech');
    insert acc;
    Assert.areEqual('Tech', [SELECT Industry FROM Account WHERE Id = :acc.Id].Industry);
}

@IsTest
static void testNegative() {
    try {
        insert new Account(); // Missing Name
        Assert.fail('Expected DmlException');
    } catch (DmlException e) {
        Assert.isTrue(e.getMessage().contains('REQUIRED_FIELD_MISSING'));
    }
}

@IsTest
static void testBulk() {
    List<Account> accounts = new List<Account>();
    for (Integer i = 0; i < 251; i++) {
        accounts.add(new Account(Name = 'Bulk ' + i));
    }
    insert accounts;
    Assert.areEqual(251, [SELECT COUNT() FROM Account]);
}
```

**See**:
- [resources/testing-patterns.md](resources/testing-patterns.md) - Exception types, mocking, Test Data Factory
- [docs/testing-guide.md](docs/testing-guide.md) - Complete testing reference

---

## Common Exception Types

When writing test classes, use these specific exception types:

| Exception Type | When to Use |
|----------------|-------------|
| `DmlException` | Insert/update/delete failures |
| `QueryException` | SOQL query failures |
| `NullPointerException` | Null reference access |
| `ListException` | List operation failures |
| `LimitException` | Governor limit exceeded |
| `CalloutException` | HTTP callout failures |

**Example**:
```apex
@IsTest
static void testExceptionHandling() {
    try {
        insert new Account(); // Missing required Name
        Assert.fail('Expected DmlException was not thrown');
    } catch (DmlException e) {
        Assert.isTrue(e.getMessage().contains('REQUIRED_FIELD_MISSING'),
            'Expected REQUIRED_FIELD_MISSING but got: ' + e.getMessage());
    }
}
```

**See**: [resources/testing-patterns.md](resources/testing-patterns.md#common-exception-types) for complete reference

---

## LSP-Based Validation (Auto-Fix Loop)

The sf-apex skill includes Language Server Protocol (LSP) integration for real-time syntax validation. This enables Claude to automatically detect and fix Apex syntax errors during code authoring.

### How It Works

1. **PostToolUse Hook**: After every Write/Edit operation on `.cls` or `.trigger` files, the LSP hook validates syntax
2. **Apex Language Server**: Uses Salesforce's official `apex-jorje-lsp.jar` (from VS Code extension)
3. **Auto-Fix Loop**: If errors are found, Claude receives diagnostics and auto-fixes them (max 3 attempts)
4. **Two-Layer Validation**:
   - **LSP Validation**: Fast syntax checking (~500ms)
   - **150-Point Validation**: Semantic analysis for best practices

### Prerequisites

For LSP validation to work, users must have:
- **VS Code Salesforce Extension Pack**: VS Code → Extensions → "Salesforce Extension Pack"
- **Java 11+**: https://adoptium.net/temurin/releases/

**Graceful Degradation**: If LSP is unavailable, validation silently skips - the skill continues to work with only 150-point semantic validation.

**See**: [resources/troubleshooting.md](resources/troubleshooting.md#lsp-based-validation-auto-fix-loop) for complete LSP guide

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-metadata | Discover object/fields before coding | `Skill(skill="sf-metadata")` → "Describe Invoice__c" |
| sf-data | Generate 251+ test records after deploy | `Skill(skill="sf-data")` → "Create 251 Accounts for bulk testing" |
| sf-deploy | Deploy to org - see Phase 4 | `Skill(skill="sf-deploy", args="Deploy to [org]")` |
| sf-flow | Create Flow that calls your Apex | See @InvocableMethod section above |
| sf-lwc | Create LWC that calls your Apex | `@AuraEnabled` controller patterns |

---

## Reference Documentation

### Quick Guides (resources/)
| Guide | Description |
|-------|-------------|
| [patterns-deep-dive.md](resources/patterns-deep-dive.md) | TAF, @InvocableMethod, async patterns, service layer |
| [security-guide.md](resources/security-guide.md) | CRUD/FLS, sharing, SOQL injection, guardrails |
| [bulkification-guide.md](resources/bulkification-guide.md) | Governor limits, collections, monitoring |
| [testing-patterns.md](resources/testing-patterns.md) | Exception types, mocking, Test Data Factory, coverage |
| [anti-patterns.md](resources/anti-patterns.md) | Code smells, red flags, refactoring patterns |
| [troubleshooting.md](resources/troubleshooting.md) | LSP validation, deployment errors, debug logs |

### Full Documentation (docs/)
| Document | Description |
|----------|-------------|
| `best-practices.md` | Bulkification, collections, null safety, guard clauses, DML performance |
| `code-smells-guide.md` | Code smells detection and refactoring patterns |
| `design-patterns.md` | 12 patterns including Domain Class, Abstraction Levels |
| `trigger-actions-framework.md` | TAF setup and advanced patterns |
| `security-guide.md` | Complete CRUD/FLS and sharing reference |
| `testing-guide.md` | Complete test patterns and mocking |
| `naming-conventions.md` | Variable, method, class naming rules |
| `solid-principles.md` | SOLID principles for Apex |
| `code-review-checklist.md` | 150-point scoring criteria |
| `flow-integration.md` | Complete @InvocableMethod guide |
| `triangle-pattern.md` | Flow-LWC-Apex integration |
| `llm-anti-patterns.md` | **NEW**: Common LLM code generation mistakes (Java types, non-existent methods, Map patterns) |

**Path**: `~/.claude/plugins/marketplaces/sf-skills/sf-apex/docs/`

---

## Dependencies

**All optional**: sf-deploy, sf-metadata, sf-data. Install: `/plugin install github:Jaganpro/sf-skills/[skill-name]`

---

## Notes

- **API Version**: 62.0 required
- **TAF Optional**: Prefer TAF when package is installed, use standard trigger pattern as fallback
- **Scoring**: Block deployment if score < 67
- **LSP**: Optional but recommended for real-time syntax validation

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
