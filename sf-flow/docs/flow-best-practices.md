# Salesforce Flow Best Practices Guide

> **Version**: 2.0.0
> **Last Updated**: December 2025
> **Applies to**: All flow types (Screen, Record-Triggered, Scheduled, Platform Event, Autolaunched)

This guide consolidates best practices for building maintainable, performant, and secure Salesforce Flows.

---

## Table of Contents

**Strategy & Planning**
1. [When NOT to Use Flow](#1-when-not-to-use-flow) ⚠️ NEW
2. [Pre-Development Planning](#2-pre-development-planning) ⚠️ NEW
3. [When to Escalate to Apex](#3-when-to-escalate-to-apex) ⚠️ NEW

**Flow Element Design**
4. [Flow Element Organization](#4-flow-element-organization)
5. [Using $Record in Record-Triggered Flows](#5-using-record-in-record-triggered-flows)
6. [Querying Relationship Data](#6-querying-relationship-data)
7. [Query Optimization](#7-query-optimization)
8. [Transform vs Loop Elements](#8-transform-vs-loop-elements)
9. [Collection Filter Optimization](#9-collection-filter-optimization)

**Architecture & Integration**
10. [When to Use Subflows](#10-when-to-use-subflows)
11. [Custom Metadata for Business Logic](#11-custom-metadata-for-business-logic) ⚠️ NEW

**Error Handling & Transactions**
12. [Three-Tier Error Handling](#12-three-tier-error-handling)
13. [Multi-Step DML Rollback Strategy](#13-multi-step-dml-rollback-strategy)
14. [Transaction Management](#14-transaction-management)

**User Experience & Maintenance**
15. [Screen Flow UX Best Practices](#15-screen-flow-ux-best-practices)
16. [Bypass Mechanism for Data Loads](#16-bypass-mechanism-for-data-loads)
17. [Flow Activation Guidelines](#17-flow-activation-guidelines)
18. [Variable Naming Conventions](#18-variable-naming-conventions)
19. [Flow & Element Descriptions](#19-flow--element-descriptions) ⚠️ NEW

---

## 1. When NOT to Use Flow

Before building a Flow, evaluate whether simpler declarative tools might better serve your needs. Flows add maintenance overhead and consume runtime resources—use them when their power is needed.

### Prefer Declarative Configuration Over Flow

| Requirement | Better Alternative | Why |
|-------------|-------------------|-----|
| Same-record field calculation | **Formula Field** | No runtime cost, always current, no maintenance |
| Data validation with error message | **Validation Rule** | Built-in UI, simpler to debug, better performance |
| Parent aggregate from children | **Roll-Up Summary Field** | Automatic, real-time, zero maintenance |
| Field defaulting on create | **Field Default Value** | Native platform feature, cleaner |
| Simple required field logic | **Page Layout / Field-Level Security** | Declarative, no code |
| Conditional field visibility | **Dynamic Forms** | UI-native, better UX |
| Simple field updates on related records | **Workflow Rule** (if already in use) | Simpler for basic use cases |

### When Flow IS the Right Choice

| Scenario | Why Flow |
|----------|----------|
| Complex multi-object updates | Orchestrate related changes in transaction |
| Conditional branching (3+ paths) | Decision logic beyond validation rules |
| User interaction required | Screen Flows for guided processes |
| Scheduled automation | Time-based execution |
| Platform Event handling | Real-time event processing |
| Integration callouts | HTTP callouts with error handling |
| Complex approval routing | Dynamic approval matrix |

### Decision Checklist

Before creating a Flow, ask:

- [ ] Can a Formula Field calculate this value?
- [ ] Can a Validation Rule enforce this business requirement?
- [ ] Is this a simple "if changed, update field" scenario? (Consider Process Builder migration later)
- [ ] Does this require user interaction? (If no, consider automation alternatives)
- [ ] Will this run on every record save? (High-frequency = high scrutiny needed)

> **Rule of Thumb**: If you can solve it with clicks (formula, validation, roll-up), do that first. Flows are powerful but add complexity.

---

## 2. Pre-Development Planning

Define business requirements and map logic **before** opening Flow Builder. Planning prevents rework and ensures stakeholder alignment.

### Step 1: Document Requirements

Before building, answer these questions:

| Question | Purpose |
|----------|---------|
| What triggers this automation? | Defines Flow type (Record-Triggered, Scheduled, Screen) |
| What are ALL outcomes? | Identifies branches (happy path + edge cases) |
| Who are the affected users? | Determines User vs System Mode |
| What objects/fields are involved? | Identifies dependencies |
| Are there existing automations? | Prevents conflicts/duplicates |

### Step 2: Visual Mapping

Sketch your Flow logic before building. Recommended tools:

| Tool | Cost | Best For |
|------|------|----------|
| **draw.io / diagrams.net** | Free | Quick flowcharts, team sharing |
| **Lucidchart** | Paid | Professional diagrams, Salesforce shapes |
| **Miro / FigJam** | Freemium | Collaborative whiteboarding |
| **Paper/Whiteboard** | Free | Initial brainstorming |

### Step 3: Identify Dependencies

| Dependency Type | Check Before Building |
|-----------------|----------------------|
| Custom Objects/Fields | Do they exist? Create with sf-metadata first |
| Custom Metadata Types | Bypass settings, thresholds, config values |
| Permission Sets | Required for System Mode considerations |
| External Systems | Callout endpoints, credentials |
| Other Automations | Triggers, Process Builders, other Flows on same object |

### Step 4: Define Test Scenarios

Before building, list your test cases:

```
Test Scenarios for: Auto_Lead_Assignment
├── Happy Path: New Lead with valid data → Assigns correctly
├── Edge Case: Lead missing required field → Handles gracefully
├── Bulk Test: 200+ Leads created → No governor limits
├── Permission Test: User without edit access → Appropriate error
└── Conflict Test: Existing trigger on Lead → No infinite loop
```

### Planning Deliverable Template

```
FLOW PLANNING DOCUMENT
═══════════════════════════════════════════════════

Flow Name: [Auto_Lead_Assignment]
Type: Record-Triggered (After Save)
Object: Lead
Trigger: On Create, On Update (when Status changes)

BUSINESS REQUIREMENTS:
1. Assign leads to reps based on territory
2. Send notification email to assigned rep
3. Update Lead Status to "Assigned"

ENTRY CONDITIONS:
- Status changed to 'New' OR Record is new
- NOT assigned to a rep yet

DECISION LOGIC:
- If Region = 'West' → Assign to User A
- If Region = 'East' → Assign to User B
- Else → Assign to Queue

ERROR HANDLING:
- If assignment fails → Log error, don't block save

DEPENDENCIES:
- Custom field: Region__c (exists ✓)
- Queue: Unassigned_Leads (exists ✓)
═══════════════════════════════════════════════════
```

---

## 3. When to Escalate to Apex

Flow is powerful, but Apex is sometimes the better tool. Know when to escalate to Invocable Apex.

### Escalation Decision Matrix

| Scenario | Why Apex is Better |
|----------|-------------------|
| **>5 nested decision branches** | Flow becomes unreadable; Apex switch/if is cleaner |
| **Complex math/string manipulation** | Apex is more expressive (regex, math libraries) |
| **External HTTP callouts** | Better error handling, retry logic, timeout control |
| **Database transactions with partial commit** | Apex Savepoints for precise rollback control |
| **Complex data transformations** | Apex collections (Maps, Sets) are more powerful |
| **Performance-critical bulk operations** | Apex is faster for large datasets (10K+ records) |
| **Unit testing requirements** | Apex test classes provide better coverage metrics |
| **Governor limit gymnastics** | Apex gives finer control over limits |

### Red Flags: When Flow is Fighting You

If you encounter these patterns, consider Apex:

```
🚩 RED FLAGS (Consider Apex Instead)
═══════════════════════════════════════════════════

❌ Building workarounds for Flow limitations
   → "I need to loop twice because Flow can't..."

❌ Flow canvas is unreadably complex
   → More than 20 elements, crossing connectors

❌ Performance issues at scale
   → Flow times out with realistic data volumes

❌ Need precise error messages
   → $Flow.FaultMessage isn't granular enough

❌ Complex JSON/XML parsing
   → Flow formulas are awkward for nested structures

❌ Multi-object transactions with partial rollback
   → Flow's all-or-nothing isn't sufficient
═══════════════════════════════════════════════════
```

### The Hybrid Approach: Flow + Invocable Apex

Best practice: Use Flow for orchestration, Apex for complexity.

```
┌─────────────────────────────────────────────────────────────┐
│ HYBRID PATTERN: Flow orchestrates, Apex handles complexity │
└─────────────────────────────────────────────────────────────┘

Flow (Auto_Process_Order):
├── Start: Record-Triggered (Order)
├── Decision: Is Complex Processing Needed?
│   ├── Yes → Apex Action: ProcessComplexOrder (Invocable)
│   └── No  → Simple Assignment Elements
├── Get Records: Related Line Items
├── Apex Action: CalculateTaxAndDiscount (Invocable)
└── Update Records: Order with calculated values

Benefits:
✓ Flow handles simple orchestration (readable)
✓ Apex handles complex math (maintainable)
✓ Apex is unit-testable (reliable)
✓ Admins can modify flow logic (accessible)
```

### Invocable Apex Template

When escalating to Apex, use this pattern:

```apex
/**
 * Invocable Apex for Flow: Complex Order Processing
 * Called from: Auto_Process_Order Flow
 */
public class OrderProcessor {

    @InvocableMethod(
        label='Process Complex Order'
        description='Calculates tax, discounts, and validates inventory'
        category='Order Management'
    )
    public static List<OutputWrapper> processOrders(List<InputWrapper> inputs) {
        List<OutputWrapper> results = new List<OutputWrapper>();

        for (InputWrapper input : inputs) {
            OutputWrapper output = new OutputWrapper();
            try {
                // Complex logic here
                output.isSuccess = true;
                output.message = 'Processed successfully';
            } catch (Exception e) {
                output.isSuccess = false;
                output.message = e.getMessage();
            }
            results.add(output);
        }
        return results;
    }

    public class InputWrapper {
        @InvocableVariable(required=true label='Order ID')
        public Id orderId;
    }

    public class OutputWrapper {
        @InvocableVariable(label='Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Message')
        public String message;
    }
}
```

> **Rule of Thumb**: If you're building workarounds for Flow limitations, use Apex. Flow should feel natural—if it doesn't, escalate.

---

## 4. Flow Element Organization

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

## 5. Using $Record in Record-Triggered Flows

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

## 6. Querying Relationship Data

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

## 7. Query Optimization

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

### Use Indexed Fields for Large Data Volumes

For orgs with **100K+ records** on an object, filter on indexed fields to ensure fast query performance.

#### Always Indexed Fields

| Field Type | Examples | Notes |
|------------|----------|-------|
| **Id** | Record ID | Primary key, fastest |
| **Name** | Account Name, Contact Name | Standard name field |
| **CreatedDate** | - | Useful for recent records |
| **SystemModstamp** | - | Last modified timestamp |
| **RecordTypeId** | - | If using Record Types |
| **OwnerId** | - | User lookup |

#### Custom Indexed Fields

| Field Type | Notes |
|------------|-------|
| **External ID fields** | Automatically indexed |
| **Lookup/Master-Detail fields** | Relationship fields are indexed |
| **Custom fields with indexing** | Request via Salesforce Support |
| **Unique fields** | Automatically indexed |

#### Performance Impact

```
┌─────────────────────────────────────────────────────────────────┐
│ QUERY PERFORMANCE: Indexed vs Non-Indexed                       │
└─────────────────────────────────────────────────────────────────┘

❌ NON-INDEXED FILTER (Slow on large objects):
   Get Records: Account
   Filter: Custom_Text__c = "ValueABC"
   → Full table scan = slow + timeout risk

✅ INDEXED FILTER (Fast at any scale):
   Get Records: Account
   Filter: External_Id__c = "ValueABC"
   → Index lookup = milliseconds
```

#### When to Request Custom Indexing

Contact Salesforce Support to request indexing when:
- Object has 100K+ records
- Query frequently filters on a specific field
- Flow timeouts occur with non-indexed filters

> **Tip**: Use `SELECT Id FROM Object WHERE Field = 'value'` in Developer Console to test query performance before building the Flow.

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

## 8. Transform vs Loop Elements

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

## 9. Collection Filter Optimization

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

## 10. When to Use Subflows

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

## 11. Custom Metadata for Business Logic

Store frequently changing business logic values in **Custom Metadata Types (CMDT)** rather than hard-coding them in Flow. This enables admins to change thresholds, settings, and routing logic without modifying the Flow.

### Why Use CMDT for Business Logic

| Benefit | Description |
|---------|-------------|
| **No deployment needed** | Change values in Setup, no Flow modification |
| **Environment-specific** | Different values per sandbox/production |
| **Audit trail** | Changes tracked in Setup Audit Trail |
| **Admin-friendly** | Non-developers can update business rules |
| **Testable** | CMDT records are accessible in test context |

### Two Access Patterns

| Pattern | Syntax | SOQL Count | Use When |
|---------|--------|------------|----------|
| **Formula Reference** | `$CustomMetadata.Type__mdt.Record.Field__c` | 0 | Single known record, simple value |
| **Get Records Query** | Get Records → CMDT object | 1 | Multiple records, dynamic filtering |

#### Formula Pattern (Preferred for Single Values)

- **No SOQL consumed** - platform resolves at runtime
- Direct reference in conditions/assignments
- Syntax: `{!$CustomMetadata.Flow_Settings__mdt.Discount_Threshold.Numeric_Value__c}`

```
Decision: Check_Threshold
├── Condition: {!$Record.Amount} >= {!$CustomMetadata.Flow_Settings__mdt.Discount_Threshold.Numeric_Value__c}
└── Outcome: Apply_Discount
```

#### Get Records Pattern (For Dynamic Queries)

- **Consumes 1 SOQL** per query
- Enables filtering, multiple record retrieval
- Visible in Flow debug logs for troubleshooting
- Useful when CMDT record name is dynamic or you need to iterate

```
Get Records: Flow_Settings__mdt
├── Filter: Category__c = "Discount"
├── Store All Records: col_DiscountSettings
└── Use in Loop or Transform
```

> **Rule of Thumb**: Use Formula Reference when you know the exact CMDT record at design time. Use Get Records when the record selection is dynamic or you need multiple records.

### What to Store in CMDT

| Value Type | Example CMDT Field | ⚠️ Key Guidance |
|------------|-------------------|-----------------|
| **Business Thresholds** | `Discount_Threshold__c`, `Max_Approval_Amount__c` | Ideal for values that change quarterly or less |
| **Feature Toggles** | `Enable_Auto_Assignment__c` | Boolean flags for gradual rollouts |
| **Record Type Names** | `RecordType_DeveloperName__c` | Store DeveloperName, NOT 15/18-char IDs |
| **Queue/User Names** | `Assignment_Queue_Name__c` | Store DeveloperName, resolve ID at runtime |
| **Email Recipients** | `Notification_Email__c`, `Template_Name__c` | Store template API names, not IDs |
| **URLs/Endpoints** | `External_API_Endpoint__c` | Enables sandbox vs production differences |
| **Picklist Mappings** | `Source_Value__c` → `Target_Value__c` | Great for value translations |

> ⚠️ **CRITICAL: Never Store Salesforce IDs in CMDT**
>
> Salesforce 15/18-character IDs (RecordTypeId, QueueId, UserId, ProfileId) are **org-specific**.
> The same Queue has different IDs in sandbox vs production. Storing IDs in CMDT causes deployment failures.
>
> **❌ Wrong**: `Queue_Id__c = '00G5f000004XXXX'`
> **✅ Right**: `Queue_Name__c = 'Support_Queue'` → Resolve ID at runtime with Get Records

#### Runtime ID Resolution Pattern

When you need to route to a Queue, User, or RecordType stored in CMDT:

```
1. Get CMDT Value:
   Formula: {!$CustomMetadata.Flow_Settings__mdt.Support_Queue.Queue_Name__c}
   → Returns: "Support_Queue" (DeveloperName)

2. Get Records: Group (Queue)
   Filter: DeveloperName = {!var_QueueName} AND Type = 'Queue'
   Store: rec_Queue

3. Assignment:
   Set {!$Record.OwnerId} = {!rec_Queue.Id}
```

### Common Use Cases

| Use Case | CMDT Field Example | Flow Usage |
|----------|-------------------|------------|
| Discount thresholds | `Discount_Threshold__c = 10000` | Decision: Amount > {!$CustomMetadata...} |
| Feature toggles | `Enable_Auto_Assignment__c = true` | Decision: Feature enabled? |
| Approval limits | `Max_Approval_Amount__c = 50000` | Route based on amount threshold |
| Email recipients | `Notification_Email__c` | Send email to CMDT value |
| SLA thresholds | `SLA_Warning_Hours__c = 24` | Decision: Hours > threshold |
| API endpoints | `External_API_Endpoint__c` | HTTP Callout URL |

### Implementation Pattern

#### Step 1: Create Custom Metadata Type

```
Object: Flow_Settings__mdt
Fields:
├── Setting_Name__c (Text, Unique)
├── Numeric_Value__c (Number)
├── Text_Value__c (Text)
├── Boolean_Value__c (Checkbox)
└── Description__c (Text Area)
```

#### Step 2: Create Records

```
Record: Discount_Threshold
├── Setting_Name__c = "Discount_Threshold"
├── Numeric_Value__c = 10000
├── Text_Value__c = null
├── Boolean_Value__c = false
└── Description__c = "Minimum order amount for automatic discount"
```

#### Step 3: Reference in Flow

```
Decision Element: Check_Discount_Eligibility
├── Condition: {!$Record.Amount} >= {!$CustomMetadata.Flow_Settings__mdt.Discount_Threshold.Numeric_Value__c}
│   └── Outcome: Apply_Discount
└── Default: No_Discount
```

### Best Practices

| Practice | Reason |
|----------|--------|
| **Use descriptive DeveloperNames** | `Discount_Threshold` not `Setting_1` |
| **Document in Description field** | Future maintainers understand purpose |
| **Group related settings** | One CMDT type per domain (Sales, Service, etc.) |
| **Include in deployment packages** | CMDT records are metadata, deploy with code |
| **Test with realistic values** | Verify Flow behavior with production thresholds |

### Identifying Hard-Coded Candidates (Migration Checklist)

Review existing flows for these hard-coded patterns that should migrate to CMDT:

```
HARD-CODED PATTERN AUDIT
═══════════════════════════════════════════════════════════

📋 CHECK YOUR FLOWS FOR:

□ 15/18-character Salesforce IDs
  └─ RecordTypeIds, QueueIds, UserIds, ProfileIds
  └─ Example: OwnerId = '005...' → Store Queue DeveloperName

□ Hardcoded URLs or endpoints
  └─ HTTP callout URLs, redirect paths
  └─ Example: endpoint = 'https://api.prod...' → Store in CMDT

□ Magic numbers (thresholds, limits, percentages)
  └─ Discount rates, approval limits, SLA hours
  └─ Example: Amount > 10000 → Use CMDT threshold

□ Email addresses in Send Email actions
  └─ Notification recipients, CC lists
  └─ Example: To = 'admin@company.com' → Store in CMDT

□ Profile/Permission Set names
  └─ Used in Decision conditions
  └─ Store as text, query Profile/PermissionSet at runtime

□ Object API names used in dynamic references
  └─ Hard-coded object strings for generic patterns

□ Picklist values used in conditions
  └─ Values that might change across regions/deployments

═══════════════════════════════════════════════════════════
```

> **Validator Note**: The sf-flow validator automatically flags `HardcodedId` and `HardcodedUrl` patterns during analysis.

### When NOT to Use CMDT

| Scenario | Better Alternative |
|----------|-------------------|
| User-specific preferences | Custom Settings (Hierarchy) |
| Frequently changing data | Custom Object with query |
| Large datasets (1000+ records) | Custom Object |
| Binary file storage | Static Resource or Files |

> **Tip**: CMDT is ideal for business rules that change quarterly or less. For daily-changing values, use Custom Objects or Custom Settings.

#### Deployment vs Data Load Distinction

CMDT records are **metadata**, not data. This has important implications:

| Aspect | Custom Metadata Type | Custom Object / Custom Setting |
|--------|---------------------|-------------------------------|
| **Move between orgs** | Change Sets, Metadata API, sf deploy | Data Loader, sf data import |
| **Update in production** | Setup → Custom Metadata Types | Data operations (update records) |
| **Included in packages** | ✅ Yes (managed/unmanaged) | ❌ No (data must be seeded separately) |
| **Test context access** | ✅ Accessible without `@TestSetup` | Requires test data creation |

> **Common Mistake**: Trying to use Data Loader to update CMDT values. CMDT records are deployed as metadata—use Change Sets, Metadata API (`sf project deploy`), or Setup UI to modify values between environments.

---

## 12. Three-Tier Error Handling

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

## 13. Multi-Step DML Rollback Strategy

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

## 14. Transaction Management

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

## 15. Screen Flow UX Best Practices

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

## 16. Bypass Mechanism for Data Loads

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

## 17. Flow Activation Guidelines

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

## 18. Variable Naming Conventions

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

## 19. Flow & Element Descriptions

Clear descriptions are essential for maintenance, collaboration, and **Agentforce integration**. AI agents use Flow descriptions to understand and select appropriate automations.

### Flow Description (Critical for Agentforce)

#### Why This Matters

| Consumer | How They Use Descriptions |
|----------|--------------------------|
| **Agentforce Agents** | AI uses descriptions to understand what automation does and when to invoke it |
| **Future Developers** | Quick understanding without reading the entire flow |
| **Flow Orchestrator** | Discovery of available subflows |
| **Governance Tools** | Auditing and documentation generation |
| **Setup Search** | Finding flows by purpose |

#### What to Include in Flow Description

Every Flow description should contain:

1. **Purpose**: One sentence explaining what the flow does
2. **Trigger**: When/how the flow is invoked
3. **Objects**: Which objects are read/written
4. **Outcome**: What changes when the flow completes
5. **Dependencies**: Any required configurations or prerequisites

#### Examples

```
✅ GOOD DESCRIPTION:
───────────────────────────────────────────────────────────────
"Automatically assigns new Leads to the appropriate sales rep
based on territory and product interest. Updates Lead Owner,
sets Assignment_Date__c, and sends notification email to the
assigned rep. Triggered on Lead creation when Status = 'New'.
Requires Territory__c field and Lead_Assignment_Queue__c queue."
───────────────────────────────────────────────────────────────

❌ BAD DESCRIPTION:
"Lead flow"
"Auto assignment"
"Created by Admin"
```

#### Description Template

```
[ACTION] [OBJECT(S)] [CONDITION].
[WHAT CHANGES]. [TRIGGER/SCHEDULE].
[DEPENDENCIES if any].
```

Examples using template:
- "Creates Task and sends email when Opportunity Stage changes to Closed Won. Updates Account Last_Deal_Date__c. Runs after Opportunity update."
- "Validates Contact email format and enriches with external data. Blocks save if validation fails. Runs before Contact insert/update."

### Element Descriptions

Add descriptions to complex elements (Decisions, Assignments, Get Records, Loops) to explain **why** the element exists, not just what it does.

#### When to Add Element Descriptions

| Element Type | Add Description When... |
|--------------|------------------------|
| **Decision** | Logic has business meaning beyond obvious field comparison |
| **Get Records** | Query has specific filter reasoning |
| **Assignment** | Calculation or transformation isn't self-evident |
| **Loop** | Processing order or exit conditions matter |
| **Subflow** | Purpose of delegation isn't obvious |

#### Element Description Format

```
WHY: [Business reason this element exists]
WHAT: [Technical summary if complex]
EDGE CASE: [Special handling if applicable]
```

#### Examples

```
Decision: Check_Discount_Eligibility
Description: "Customers with >$100K annual revenue OR
Premium tier get automatic 15% discount. Edge case:
New customers without revenue history default to no discount."

Get Records: Get_Active_Contracts
Description: "Retrieves only contracts expiring in next 90 days
to avoid processing historical data. Filtered by Status=Active
to reduce collection size for bulk safety."

Assignment: Calculate_Renewal_Date
Description: "Adds 365 days to current contract end date.
Uses formula to handle leap years. Returns null if
original end date is null (new contracts)."
```

### Benefits of Good Descriptions

| Benefit | Impact |
|---------|--------|
| **6-month test** | Can you understand the flow in 6 months? |
| **Handoff ready** | New team member can maintain without meetings |
| **Agentforce-ready** | AI can discover and use your flows correctly |
| **Audit-friendly** | Compliance reviews understand business logic |
| **Debug faster** | Element descriptions explain expected behavior |

> **Rule of Thumb**: If you had to explain this Flow or element to a colleague, put that explanation in the description.

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
