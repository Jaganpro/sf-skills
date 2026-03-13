---
name: sf-industries-callable-apex
description: >
  Generates and reviews Salesforce Industries (OmniStudio/Vlocity) Apex callable implementations.
  Use when creating or reviewing System.Callable classes, Industries callable extensions, or when
  the user mentions callable implementations, OmniStudio, Vlocity, or Industries Apex extensions.
  DO NOT TRIGGER when: generic Apex classes/triggers (use sf-apex), LWC, Flow XML, or SOQL-only work.
license: MIT
metadata:
  version: "1.0.0"
  author: "Shreyas Dhond"
  scoring: "120 points across 7 categories"
---

# sf-industries-callable-apex: Callable Implementations for Salesforce Industries

Specialist for Salesforce Industries callable implementations. Produce secure, deterministic, and
configurable Apex that cleanly integrates with Industries extension points.

## Core Responsibilities

1. **Callable Generation**: Build `System.Callable` classes with safe action dispatch
2. **Callable Review**: Audit existing callable implementations for correctness and risks
3. **Validation & Scoring**: Evaluate against the 120-point rubric
4. **Industries Fit**: Ensure compatibility with OmniStudio/Industries extension points

---

## Workflow (4-Phase Pattern)

### Phase 1: Requirements Gathering

Ask for:
- Entry point (OmniScript, Integration Procedure, DataRaptor, or other Industries hook)
- Action names (strings passed into `call`)
- Input/output contract (required keys, types, and response shape)
- Data access needs (objects/fields, CRUD/FLS rules)
- Side effects (DML, callouts, async requirements)

Then:
1. Scan for existing callable classes: `Glob: **/*Callable*.cls`
2. Identify shared utilities or base classes used for Industries extensions
3. Create a task list

---

### Phase 2: Design & Contract Definition

**Define the callable contract**:
- Action list (explicit, versioned strings)
- Input schema (required keys + types)
- Output schema (consistent response envelope)

**Recommended response envelope**:
```
{
  "success": true|false,
  "data": {...},
  "errors": [ { "code": "...", "message": "..." } ]
}
```

**Action dispatch rules**:
- Use `switch on action`
- Default case throws a typed exception
- No dynamic method invocation or reflection

---

### Phase 3: Implementation Pattern

**Callable skeleton**:
```apex
public with sharing class Industries_OrderCallable implements System.Callable {
    public Object call(String action, Map<String, Object> args) {
        switch on action {
            when 'createOrder' {
                return createOrder(args);
            }
            when else {
                throw new IndustriesCallableException('Unsupported action: ' + action);
            }
        }
    }

    private Map<String, Object> createOrder(Map<String, Object> args) {
        // Validate input, run business logic, return response envelope
        return new Map<String, Object>{ 'success' => true };
    }
}
```

**Implementation rules**:
1. Keep `call()` thin; delegate to private methods or service classes
2. Validate and coerce input types early (null-safe)
3. Enforce CRUD/FLS and sharing (`with sharing`, `Security.stripInaccessible()`)
4. Bulkify when args include record collections
5. Use `WITH USER_MODE` for SOQL when appropriate

---

### Phase 4: Testing & Validation

Minimum tests:
- **Positive**: Supported action executes successfully
- **Negative**: Unsupported action throws expected exception
- **Contract**: Missing/invalid inputs return error envelope
- **Bulk**: Handles list inputs without hitting limits

**Example test class**:
```apex
@IsTest
private class Industries_OrderCallableTest {
    @IsTest
    static void testCreateOrder() {
        System.Callable svc = new Industries_OrderCallable();
        Map<String, Object> args = new Map<String, Object>{
            'orderId' => '001000000000001'
        };
        Map<String, Object> result =
            (Map<String, Object>) svc.call('createOrder', args);
        Assert.isTrue((Boolean) result.get('success'));
    }

    @IsTest
    static void testUnsupportedAction() {
        try {
            System.Callable svc = new Industries_OrderCallable();
            svc.call('unknownAction', new Map<String, Object>());
            Assert.fail('Expected IndustriesCallableException');
        } catch (IndustriesCallableException e) {
            Assert.isTrue(e.getMessage().contains('Unsupported action'));
        }
    }
}
```

---

## Migration: VlocityOpenInterface to System.Callable

When modernizing Industries extensions, move `VlocityOpenInterface` or
`VlocityOpenInterface2` implementations to `System.Callable` and keep the
action contract stable. Use the Salesforce guidance as the source of truth.
[Salesforce Help](https://help.salesforce.com/s/articleView?id=ind.v_dev_t_callable_implementations_651821.htm&type=5)

**Guidance**:
- Preserve action names (`methodName`) as `action` strings in `call()`
- Convert `(input, outMap, options)` into a single `args` map
- Return a consistent response envelope instead of mutating `outMap`
- Keep `call()` thin; delegate to the same internal methods
- Add tests for each action and unsupported action

**Example migration (pattern)**:
```apex
// BEFORE: VlocityOpenInterface2
global class OrderOpenInterface implements omnistudio.VlocityOpenInterface2 {
    global Boolean invokeMethod(String methodName, Map<String, Object> input,
                                Map<String, Object> output,
                                Map<String, Object> options) {
        if (methodName == 'createOrder') {
            output.putAll(createOrder(input, options));
            return true;
        }
        return false;
    }
}

// AFTER: System.Callable
public with sharing class OrderCallable implements System.Callable {
    public Object call(String action, Map<String, Object> args) {
        switch on action {
            when 'createOrder' {
                return createOrder(args);
            }
            when else {
                throw new IndustriesCallableException('Unsupported action: ' + action);
            }
        }
    }
}
```

---

## Best Practices (120-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Contract & Dispatch** | 20 | Explicit action list; `switch on`; versioned action strings |
| **Input Validation** | 20 | Required keys validated; types coerced safely; null guards |
| **Security** | 20 | `with sharing`; CRUD/FLS checks; `Security.stripInaccessible()` |
| **Error Handling** | 15 | Typed exceptions; consistent error envelope; no empty catch |
| **Bulkification & Limits** | 20 | No SOQL/DML in loops; supports list inputs |
| **Testing** | 15 | Positive/negative/contract/bulk tests |
| **Documentation** | 10 | ApexDoc for class and action methods |

**Thresholds**: ✅ 90+ (Ready) | ⚠️ 70-89 (Review) | ❌ <70 (Block)

---

## ⛔ Guardrails (Mandatory)

Stop and ask the user if any of these would be introduced:
- Dynamic method execution based on user input (no reflection)
- SOQL/DML inside loops
- `without sharing` on callable classes
- Silent failures (empty catch, swallowed exceptions)
- Inconsistent response shapes across actions

---

## Common Anti-Patterns

- `call()` contains business logic instead of delegating
- Action names are unversioned or not documented
- Input maps assumed to have keys without checks
- Mixed response types (sometimes Map, sometimes String)
- No tests for unsupported actions

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-apex | General Apex work beyond callable implementations | "Create trigger for Account" |
| sf-metadata | Verify object/field availability before coding | "Describe Product2" |
| sf-deploy | Validate/deploy callable classes | "Deploy to sandbox" |

---

## Reference Skill

Use the core Apex standards, testing patterns, and guardrails in:
- [skills/sf-apex/SKILL.md](../sf-apex/SKILL.md)

---

## Notes

- Prefer deterministic, side-effect-aware callable actions
- Keep action contracts stable; introduce new actions for breaking changes
- Avoid long-running work in synchronous callables; use async when needed

---
