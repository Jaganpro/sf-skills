# Salesforce Flow Best Practices Guide

> **Version**: 2.0.0
> **Last Updated**: December 2025
> **Applies to**: All flow types (Screen, Record-Triggered, Scheduled, Platform Event, Autolaunched)

This guide consolidates best practices for building maintainable, performant, and secure Salesforce Flows.

---

## Table of Contents

1. [Flow Element Organization](#1-flow-element-organization)
2. [Using $Record in Record-Triggered Flows](#2-using-record-in-record-triggered-flows)
3. [Querying Relationship Data](#3-querying-relationship-data)
4. [Query Optimization](#4-query-optimization)
5. [Transform vs Loop Elements](#5-transform-vs-loop-elements) ⚠️ NEW
6. [Collection Filter Optimization](#6-collection-filter-optimization) ⚠️ NEW
7. [When to Use Subflows](#7-when-to-use-subflows)
8. [Three-Tier Error Handling](#8-three-tier-error-handling)
9. [Multi-Step DML Rollback Strategy](#9-multi-step-dml-rollback-strategy)
10. [Transaction Management](#10-transaction-management)
11. [Screen Flow UX Best Practices](#11-screen-flow-ux-best-practices)
12. [Bypass Mechanism for Data Loads](#12-bypass-mechanism-for-data-loads)
13. [Flow Activation Guidelines](#13-flow-activation-guidelines)
14. [Variable Naming Conventions](#14-variable-naming-conventions)

---

## 1. Flow Element Organization

Structure your flow elements in this sequence for maintainability:

| Order | Element Type | Purpose |
|-------|--------------|---------|
| 1 | Variables & Constants | Define all data containers first |
| 2 | Start Element | Entry conditions, triggers, schedules |
| 3 | Initial Record Lookups | Retrieve needed data early |
| 4 | Formula Definitions | Define calculations before use |
| 5 | Decision Elements | Branching logic |
| 6 | Assignment Elements | Data preparation/manipulation |
| 7 | Screens (if Screen Flow) | User interaction |
| 8 | DML Operations | Create/Update/Delete records |
| 9 | Error Handling | Fault paths and rollback |
| 10 | Ending Elements | Complete flow, return outputs |

### Why This Order Matters

- **Readability**: Reviewers can follow the logical flow
- **Maintainability**: Easy to locate elements by function
- **Debugging**: Errors trace back to predictable locations

---

## 2. Using $Record in Record-Triggered Flows

When your flow is triggered by a record change, use `$Record` to access field values instead of querying the same object again.

### ⚠️ CRITICAL: $Record vs $Record__c

**Do NOT confuse Flow's `$Record` with Process Builder's `$Record__c`.**

| Variable | Platform | Meaning |
|----------|----------|---------|
| `$Record` | **Flow** | Single record that triggered the flow |
| `$Record__c` | Process Builder (legacy) | Collection of records in trigger batch |

**Common Mistake**: Developers migrating from Process Builder try to loop over `$Record__c` in Flows. This doesn't work because:
- `$Record__c` does not exist in Flows
- `$Record` in Flows is a single record, not a collection
- The platform handles bulk batching automatically - you don't need to loop

**Correct Approach**: Use `$Record` directly without loops:
```
Decision: {!$Record.StageName} equals "Closed Won"
Assignment: Set rec_Task.WhatId = {!$Record.Id}
Create Records: rec_Task
```

### Anti-Pattern (Avoid)

```
Trigger: Account record updated
Step 1: Get Records → Query Account where Id = {!$Record.Id}
Step 2: Use queried Account fields
```

**Problems**:
- Wastes a SOQL query (you already have the record!)
- Adds unnecessary complexity
- Can cause timing issues with stale data

### Best Practice

```
Trigger: Account record updated
Step 1: Use {!$Record.Name}, {!$Record.Industry} directly
```

**Benefits**:
- Zero additional SOQL queries
- Always has current field values
- Simpler, more readable flow

### When You DO Need to Query

Query the trigger object only when you need:
- Related records (e.g., Account's Contacts)
- Fields not included in the trigger context
- Historical comparison (`$Record__Prior`)

---

## 3. Querying Relationship Data

### ⚠️ Get Records Does NOT Support Parent Traversal

**Critical Limitation**: You CANNOT query parent relationship fields in Flow's Get Records.

#### What Doesn't Work

```
Get Records: User
Fields: Id, Name, Manager.Name  ← FAILS!
```

**Error**: "The field 'Manager.Name' for the object 'User' doesn't exist."

#### The Solution: Two-Step Pattern

Query the child object first, then query the parent using the lookup ID:

```
Step 1: Get Records → User
        Fields: Id, Name, ManagerId
        Store in: rec_User

Step 2: Get Records → User
        Filter: Id equals {!rec_User.ManagerId}
        Fields: Id, Name
        Store in: rec_Manager

Step 3: Use {!rec_Manager.Name} in your flow
```

#### Common Relationship Queries That Need This Pattern

| Child Object | Parent Field | Two-Step Approach |
|--------------|--------------|-------------------|
| Contact | Account.Name | Get Contact → Get Account by AccountId |
| Case | Account.Owner.Email | Get Case → Get Account → Get User |
| Opportunity | Account.Industry | Get Opportunity → Get Account by AccountId |
| User | Manager.Name | Get User → Get User by ManagerId |

#### Why This Matters

- Flow's Get Records uses simple field retrieval, not SOQL relationship queries
- This is different from Apex where you can write `SELECT Account.Name FROM Contact`
- Always check for null on the parent record before using its fields

---

## 4. Query Optimization

### Use 'In' and 'Not In' Operators

When filtering against a collection of values, use `In` or `Not In` operators instead of multiple OR conditions.

**Best Practice**:
```
Get Records where Status IN {!col_StatusValues}
```

**Avoid**:
```
Get Records where Status = 'Open' OR Status = 'Pending' OR Status = 'Review'
```

### Always Add Filter Conditions

Every Get Records element should have filter conditions to:
- Limit the result set
- Improve query performance
- Avoid hitting governor limits

### Use getFirstRecordOnly

When you expect a single record (e.g., looking up by unique ID), enable `getFirstRecordOnly`:
- Improves performance
- Clearer intent
- Simpler variable handling

### Avoid storeOutputAutomatically

When `storeOutputAutomatically="true"`, ALL fields are retrieved and stored:

**Risks**:
- Exposes sensitive data unintentionally
- Impacts performance with large objects
- Security issue in screen flows (external users see all data)

**Fix**: Explicitly specify only the fields you need in the Get Records element.

---

## 5. Transform vs Loop Elements

When processing collections, choosing between **Transform** and **Loop** elements significantly impacts performance and maintainability.

### Quick Decision Rule

> **Shaping data** → Use **Transform** (30-50% faster)
> **Making decisions per record** → Use **Loop**

### When to Use Transform

Transform is the right choice for:

| Use Case | Example |
|----------|---------|
| **Mapping collections** | Contact[] → OpportunityContactRole[] |
| **Bulk field assignments** | Set Status = "Processed" for all records |
| **Simple formulas** | Calculate FullName from FirstName + LastName |
| **Preparing records for DML** | Build collection for Create Records |

### When to Use Loop

Loop is required when:

| Use Case | Example |
|----------|---------|
| **Per-record IF/ELSE** | Different processing based on Amount threshold |
| **Counters/flags** | Count records meeting criteria |
| **State tracking** | Running totals, comma-separated lists |
| **Varying business rules** | Different logic paths per record type |

### Visual Comparison

```
❌ ANTI-PATTERN: Loop for simple field mapping
   Get Records → Loop → Assignment → Add to Collection → Create Records
   (5 elements, client-side iteration)

✅ BEST PRACTICE: Transform for field mapping
   Get Records → Transform → Create Records
   (3 elements, server-side bulk operation, 30-50% faster)
```

### Performance Impact

Transform processes the entire collection server-side as a single bulk operation, while Loop iterates client-side. For collections of 100+ records, Transform can be **30-50% faster**.

### XML Recommendation

> ⚠️ **Create Transform elements in Flow Builder UI, then deploy.**
> Transform XML is complex with strict ordering—do not hand-write.

See [Transform vs Loop Guide](./transform-vs-loop-guide.md) for detailed decision criteria, examples, and testing strategies.

---

## 6. Collection Filter Optimization

Collection Filter is a powerful tool for reducing governor limit usage by filtering in memory instead of making additional SOQL queries.

### The Pattern

Instead of multiple Get Records calls, query once and filter in memory:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ❌ ANTI-PATTERN: Multiple Get Records calls                            │
└─────────────────────────────────────────────────────────────────────────┘

For each Account in loop:
  → Get Records: Contacts WHERE AccountId = {!current_Account.Id}
  → Process contacts...

Problem: N SOQL queries (one per Account) = Governor limit risk!

┌─────────────────────────────────────────────────────────────────────────┐
│ ✅ BEST PRACTICE: Query once + Collection Filter                       │
└─────────────────────────────────────────────────────────────────────────┘

1. Get Records: ALL Contacts WHERE AccountId IN {!col_AccountIds}
   → 1 SOQL query total

2. Loop through Accounts:
   → Collection Filter: Contacts WHERE AccountId = {!current_Account.Id}
   → Process filtered contacts (in-memory, no SOQL!)
```

### Benefits

| Metric | Multiple Queries | Query Once + Filter |
|--------|------------------|---------------------|
| SOQL Queries | N (one per parent) | 1 |
| Performance | Slow | Fast |
| Governor Risk | High | Low |
| Scalability | Poor | Excellent |

### Implementation Steps

1. **Collect parent IDs** into a collection variable
2. **Single Get Records** using `IN` operator with ID collection
3. **Loop through parents**, using Collection Filter to get related records
4. **Process filtered subset** in each iteration

### When to Use

- Parent-child processing (Account → Contacts, Opportunity → Line Items)
- Batch operations where you need related records
- Any scenario requiring records from the same object for multiple parents

### Governor Limit Savings

With Collection Filter, you can process thousands of related records with a **single SOQL query** instead of hitting the 100-query limit.

---

## 7. When to Use Subflows

Use subflows for:

### 1. Reusability
Same logic needed in multiple flows? Extract it to a subflow.
- Error logging
- Email notifications
- Common validations

### 2. Complex Orchestration
Break large flows into manageable pieces:
- Main flow orchestrates
- Subflows handle specific responsibilities
- Easier to test individually

### 3. Permission Elevation
When a flow running in user context needs elevated permissions:
- Main flow runs in user context
- Subflow runs in system context for specific operations
- Maintains security while enabling functionality

### 4. Organizational Clarity
If your flow diagram is unwieldy:
- Extract logical sections into subflows
- Name subflows descriptively
- Document the orchestration pattern

### Subflow Naming Convention

Use the `Sub_` prefix:
- `Sub_LogError`
- `Sub_SendEmailAlert`
- `Sub_ValidateRecord`
- `Sub_BulkUpdater`

---

## 8. Three-Tier Error Handling

Implement comprehensive error handling at three levels:

### Tier 1: Input Validation (Pre-Execution)

**When**: Before any DML operations
**What to Check**:
- Null/empty required values
- Business rule prerequisites
- Data format validation

**Action**: Show validation error screen or set error output variable

### Tier 2: DML Error Handling (During Execution)

**When**: On every DML element (Create, Update, Delete)
**What to Do**:
- Add fault paths to ALL DML elements
- Capture `{!$Flow.FaultMessage}` for context
- Include record IDs and operation type in error messages

**Action**: Route to error handler, prepare for rollback

### Tier 3: Rollback Handling (Post-Failure)

**When**: After a DML failure when prior operations succeeded
**What to Do**:
- Delete records created earlier in the transaction
- Restore original values if updates failed
- Log the failure for debugging

**Action**: Execute rollback, notify user/admin

### Error Message Best Practice

Include context in every error message:
```
"Failed to create Contact for Account {!rec_Account.Id}: {!$Flow.FaultMessage}"
"Update failed on Opportunity {!rec_Opportunity.Id} during {!var_CurrentOperation}"
```

---

## 9. Multi-Step DML Rollback Strategy

When a flow performs multiple DML operations, implement rollback paths.

### Pattern: Primary → Dependent → Rollback Chain

#### Step 1: Create Primary Record (e.g., Account)
- On success → Continue to step 2
- On failure → Show error, stop flow

#### Step 2: Create Dependent Records (e.g., Contacts, Opportunities)
- On success → Continue to step 3
- On failure → **DELETE primary record**, show error

#### Step 3: Update Related Records
- On success → Complete flow
- On failure → **DELETE dependents, DELETE primary**, show error

### Implementation Pattern

```
1. Create Account → Store ID in var_AccountId
2. Create Contacts → On fault: Delete Account using var_AccountId
3. Create Opportunities → On fault: Delete Contacts, Delete Account
4. Success → Return output variables
```

### Error Message Pattern

Use `errorMessage` output variable to surface failures:
```
"Failed to create Account: {!$Flow.FaultMessage}"
"Failed to create Contact: {!$Flow.FaultMessage}. Account rolled back."
```

---

## 10. Transaction Management

### Understanding Flow Transactions

- All DML in a flow runs in a **single transaction** (unless using async)
- If any DML fails, **all changes roll back automatically**
- Use this to your advantage for data integrity

### Save Point Pattern

For complex multi-step flows where you need manual rollback control:

1. Create primary records
2. Store IDs of created records in a collection
3. Create dependent records
4. On failure → Use stored IDs for manual rollback

### Transaction Limits to Consider

| Limit | Value |
|-------|-------|
| DML statements per transaction | 150 |
| SOQL queries per transaction | 100 |
| Records retrieved by SOQL | 50,000 |
| DML rows per transaction | 10,000 |

### Document Transaction Boundaries

Add comments in flow description:
```
TRANSACTION: Creates Account → Creates Contact → Updates related Opportunities
```

---

## 11. Screen Flow UX Best Practices

### Progress Indicators

For multi-step flows (3+ screens):
- Use Screen component headers to show "Step X of Y"
- Consider visual progress bars for long wizards
- Update progress on each screen transition

### Stage Resource for Multi-Screen Flows

The **Stage** resource provides visual progress tracking across multiple screens, showing users where they are in a multi-step process.

#### When to Use Stage

- Flows with 3+ screens that represent distinct phases
- Onboarding wizards (Identity → Configuration → Confirmation)
- Order processes (Cart → Shipping → Payment → Review)
- Application workflows with logical sections

#### How Stages Work

1. **Define stages** in your flow resources (Stage elements)
2. **Assign current stage** using Assignment element at each phase transition
3. **Display progress** using the Stage component in screens

#### Stage Example

```
Flow: New Customer Onboarding

Stages:
1. Identity (collect customer info)
2. Configuration (set preferences)
3. Payment (billing details)
4. Confirmation (review and submit)

Each screen shows visual indicator: ● ○ ○ ○ → ● ● ○ ○ → ● ● ● ○ → ● ● ● ●
```

#### Benefits

| Feature | Benefit |
|---------|---------|
| Visual progress | Users know how far along they are |
| Reduced abandonment | Clear expectation of remaining steps |
| Better UX | Professional wizard-like experience |
| Navigation context | Users understand their position |

#### Implementation Tips

- Keep stage names short (1-3 words)
- Use consistent naming pattern (nouns: "Identity", "Payment" vs verbs: "Collect Info", "Enter Payment")
- Consider allowing users to click back to previous stages (if safe)

### Button Design

#### Naming Pattern
Use: `Action_[Verb]_[Object]`
- `Action_Save_Contact`
- `Action_Submit_Application`
- `Action_Cancel_Request`

#### Button Ordering
1. **Primary action** first (Submit, Save, Confirm)
2. **Secondary actions** next (Save Draft, Back)
3. **Tertiary/Cancel** last (Cancel, Exit)

### Navigation Controls

#### Standard Navigation Pattern

| Button | Position | When to Show |
|--------|----------|--------------|
| Previous | Left | After first screen (if safe) |
| Cancel | Left | Always |
| Next | Right | Before final screen |
| Finish/Submit | Right | Final screen only |

#### When to Disable Back Button

Disable "Previous" when returning would:
- Cause duplicate record creation
- Lose unsaved complex data
- Break transaction integrity
- Confuse business process state

### Screen Instructions

For complex screens, add instruction text at the top:
- Use Display Text component
- Keep instructions concise (1-2 sentences)
- Highlight required fields or important notes

Example: "Complete all required fields (*) before proceeding."

### Performance Tips

- **Lazy Loading**: Don't load all data upfront; query as needed per screen
- **Minimize Screens**: Each screen = user wait time; combine where logical
- **Avoid Complex Formulas**: In screen components (impacts render time)
- **LWC for Complex UI**: Consider Lightning Web Components for rich interactions

---

## 12. Bypass Mechanism for Data Loads

When loading large amounts of data, flows can cause performance issues. Implement a bypass mechanism using Custom Metadata.

### Setup Pattern

#### Step 1: Create Custom Metadata Type

Create `Flow_Bypass_Settings__mdt` with fields:
- `Bypass_Flows__c` (Checkbox)
- `Flow_API_Name__c` (Text) - optional, for granular control

#### Step 2: Add Decision at Flow Start

Add a Decision element as the first step after Start:

**Condition**: `{!$CustomMetadata.Flow_Bypass_Settings__mdt.Default.Bypass_Flows__c} = true`
- **If true** → End flow early (no processing)
- **If false** → Continue normal processing

### Use Cases

- Data migrations
- Bulk data loads via Data Loader
- Integration batch processing
- Initial org setup/seeding

### Best Practice

- Document which flows support bypass
- Ensure bypass is disabled after data load completes
- Consider logging when bypass is active

---

## 13. Flow Activation Guidelines

### When to Keep Flows in Draft

- During development and testing
- Before user acceptance testing (UAT) is complete
- When dependent configurations aren't deployed yet

### Deployment Recommendation

1. Deploy flows as **Draft** initially
2. Validate in target environment
3. Test with representative data
4. Activate only after verification
5. Keep previous version as backup before activating new version

### Scheduled Flow Considerations

Scheduled flows run automatically without user interaction:
- Test thoroughly before activation
- Verify schedule frequency is correct
- Ensure error notifications are configured
- Monitor first few executions

---

## 14. Variable Naming Conventions

Use consistent prefixes for all variables:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `var_` | Regular variables | `var_AccountName` |
| `col_` | Collections | `col_ContactIds` |
| `rec_` | Record variables | `rec_Account` |
| `inp_` | Input variables | `inp_RecordId` |
| `out_` | Output variables | `out_IsSuccess` |

### Why Prefixes Matter

- **Clarity**: Immediately understand variable type
- **Debugging**: Easier to trace values in debug logs
- **Maintenance**: New developers understand intent quickly
- **Consistency**: Team-wide standards reduce confusion

### Element Naming

For flow elements (decisions, assignments, etc.):
- Use `PascalCase_With_Underscores`
- Be descriptive: `Check_Account_Type` not `Decision_1`
- Include context: `Get_Related_Contacts` not `Get_Records`

---

## Quick Reference Checklist

### Record-Triggered Flow Essentials
- [ ] Use `$Record` directly - do NOT create loops over triggered records
- [ ] Never use `$Record__c` (Process Builder pattern, doesn't exist in Flows)
- [ ] Platform handles bulk batching - you don't need manual loops

### Get Records Best Practices
- [ ] Use `$Record` instead of querying trigger object
- [ ] Add filters to all Get Records elements
- [ ] Enable `getFirstRecordOnly` when expecting single record
- [ ] Disable `storeOutputAutomatically` (specify fields explicitly)
- [ ] **For relationship data**: Use two-step query pattern (child → parent by ID)
- [ ] Never query `Parent.Field` in queriedFields (not supported)

### Error Handling & DML
- [ ] Add fault paths to all DML operations
- [ ] Implement rollback for multi-step DML
- [ ] Capture `$Flow.FaultMessage` in error handlers

### Naming & Organization
- [ ] Use variable naming prefixes (`var_`, `col_`, `rec_`, etc.)
- [ ] Add progress indicators to multi-screen flows

### Testing & Deployment
- [ ] Test with bulk data (200+ records)
- [ ] Keep flows in Draft until fully tested
- [ ] **Always use sf-deploy skill** - never direct CLI commands

---

## Related Documentation

- [Transform vs Loop Guide](./transform-vs-loop-guide.md) - When to use each element
- [Flow Quick Reference](./flow-quick-reference.md) - Comprehensive cheat sheet
- [Orchestration Guide](./orchestration-guide.md) - Parent-child and sequential patterns
- [Subflow Library](./subflow-library.md) - Reusable subflow templates
- [Testing Guide](./testing-guide.md) - Comprehensive testing strategies
- [Governance Checklist](./governance-checklist.md) - Security and compliance
- [XML Gotchas](./xml-gotchas.md) - Common XML pitfalls
