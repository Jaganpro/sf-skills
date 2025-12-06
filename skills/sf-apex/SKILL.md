---
name: sf-apex
description: Generates and reviews Salesforce Apex code with 2025 best practices. 150-point scoring across 8 categories including bulkification, security, and testing. Enforces Trigger Actions Framework (TAF) pattern.
---

# sf-apex: Salesforce Apex Code Generation and Review

Expert Apex developer specializing in clean code, SOLID principles, and 2025 best practices. Generate production-ready, secure, performant, and maintainable Apex code.

## Core Responsibilities

1. **Code Generation**: Create Apex classes, triggers (TAF), tests, async jobs from requirements
2. **Code Review**: Analyze existing Apex for best practices violations with actionable fixes
3. **Validation & Scoring**: Score code against 8 categories (0-150 points)
4. **Deployment Integration**: Validate and deploy via sf-deployment skill

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

Load via: `Read: skills/sf-apex/templates/[template]` (relative to plugin root)

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

### Phase 4: Deployment

**Step 1: Validation**
```
Skill(skill="sf-deployment")
Request: "Deploy classes at force-app/main/default/classes/ to [target-org] with --dry-run --test-level RunLocalTests"
```

**Step 2: Deploy** (only if validation succeeds)
```
Skill(skill="sf-deployment")
Request: "Proceed with actual deployment to [target-org]"
```

### Phase 5: Documentation & Testing Guidance

**Completion Summary**:
```
✓ Apex Code Complete: [ClassName]
  Type: [type] | API: 62.0
  Location: force-app/main/default/classes/[ClassName].cls
  Test Class: [TestClassName].cls
  Validation: PASSED (Score: XX/150)

Next Steps: Run tests, verify behavior, monitor logs
```

---

## Best Practices (Built-In Enforcement)

### Critical Requirements

**Bulkification** (25 points):
- NO SOQL/DML inside loops - collect records, operate after loop
- Use List, Set, Map for collections
- Handle 200+ records per transaction
- Test with 251+ records

**Security** (25 points):
- Use `WITH USER_MODE` for SOQL queries
- Bind variables for dynamic SOQL (`:variable`)
- Use `with sharing` by default, `inherited sharing` for utilities
- Never hardcode credentials - use Named Credentials
- Use `Security.stripInaccessible()` for FLS

**Testing** (25 points):
- 90%+ coverage (75% minimum)
- Always use Assert class (Winter '23+)
- Test positive, negative, bulk (251+), single record
- Use Test Data Factory pattern
- Use `Test.startTest()`/`Test.stopTest()` for async

**Architecture** (20 points):
- One trigger per object using Trigger Actions Framework
- Separation of concerns: Service, Domain, Selector layers
- SOLID principles compliance
- Dependency injection for testability

**Clean Code** (20 points):
- Meaningful names (no abbreviations like `tks`, `rec`)
- Self-documenting code
- Boolean clarity (no `!= false`)
- Single responsibility per method

**Error Handling** (15 points):
- Catch specific exceptions before generic
- Never empty catch blocks
- Use custom exceptions for business logic
- Log errors appropriately

**Performance** (10 points):
- Use `Limits` class to monitor
- Cache expensive operations
- Let variables go out of scope for heap
- Use async for heavy operations

**Documentation** (10 points):
- ApexDoc comments on classes/methods
- Meaningful parameter names
- Clear intent without external docs

### Scoring Thresholds

| Rating | Score |
|--------|-------|
| ⭐⭐⭐⭐⭐ Excellent | 135-150 |
| ⭐⭐⭐⭐ Very Good | 112-134 |
| ⭐⭐⭐ Good | 90-111 |
| ⭐⭐ Needs Work | 67-89 |
| ⭐ Critical Issues | <67 |

---

## Trigger Actions Framework (TAF)

All triggers MUST use the Trigger Actions Framework pattern:

**Trigger** (one per object):
```apex
trigger AccountTrigger on Account (
    before insert, after insert,
    before update, after update,
    before delete, after delete, after undelete
) {
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

See [docs/trigger-actions-framework.md](docs/trigger-actions-framework.md) for full patterns.

---

## Async Decision Matrix

| Scenario | Use |
|----------|-----|
| Simple callout, fire-and-forget | `@future(callout=true)` |
| Complex logic, needs chaining | `Queueable` |
| Process millions of records | `Batch Apex` |
| Scheduled/recurring job | `Schedulable` |
| Post-queueable cleanup | `Queueable Finalizer` |

---

## Code Review Red Flags

| Anti-Pattern | Fix |
|--------------|-----|
| SOQL/DML in loop | Collect in loop, operate after |
| `without sharing` everywhere | Use `with sharing` by default |
| No trigger bypass flag | Add Boolean Custom Setting |
| Multiple triggers on object | Single trigger + TAF |
| SOQL without WHERE/LIMIT | Always filter and limit |
| `System.debug()` everywhere | Control via Custom Metadata |
| `isEmpty()` before DML | Remove - empty list = 0 DMLs |
| Generic Exception only | Catch specific types first |
| Hard-coded Record IDs | Query dynamically |
| No Test Data Factory | Implement Factory pattern |

---

## Modern Apex Features (API 62.0)

- **Null coalescing**: `value ?? defaultValue`
- **Safe navigation**: `record?.Field__c`
- **User mode**: `WITH USER_MODE` in SOQL
- **Assert class**: `Assert.areEqual()`, `Assert.isTrue()`

**Breaking Change (API 62.0)**: Cannot modify Set while iterating - throws `System.FinalException`

---

## Reference Documentation

- [docs/best-practices.md](docs/best-practices.md) - Comprehensive best practices
- [docs/trigger-actions-framework.md](docs/trigger-actions-framework.md) - TAF patterns
- [docs/security-guide.md](docs/security-guide.md) - Security patterns
- [docs/testing-guide.md](docs/testing-guide.md) - Testing patterns
- [docs/naming-conventions.md](docs/naming-conventions.md) - Naming standards
- [docs/solid-principles.md](docs/solid-principles.md) - SOLID in Apex
- [docs/design-patterns.md](docs/design-patterns.md) - Factory, Repository, Builder
- [docs/code-review-checklist.md](docs/code-review-checklist.md) - Review checklist

---

## Notes

- **API Version**: 62.0 required
- **TAF Required**: All triggers must use Trigger Actions Framework
- **Dependencies**: Requires sf-deployment ≥2.0.0
- **Scoring**: Block deployment if score < 67

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
