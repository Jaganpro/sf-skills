---
name: sf-flow
description: >
  Creates and validates Salesforce flows with 110-point scoring and Winter '26
  best practices. Use when building record-triggered flows, screen flows,
  autolaunched flows, scheduled flows, or reviewing existing flow performance.
license: MIT
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "110 points across 6 categories"
---

# sf-flow: Salesforce Flow Creation and Validation

Expert Salesforce Flow Builder with deep knowledge of best practices, bulkification, and Winter '26 (API 62.0) metadata. Create production-ready, performant, secure, and maintainable flows.

## 📋 Quick Reference: Validation Script

**Validate Flow XML before deployment:**
```bash
# Path to validation script
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-flow-builder/hooks/scripts/validate_flow.py <flow-file.xml>

# Example
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-flow-builder/hooks/scripts/validate_flow.py \
  force-app/main/default/flows/Auto_Lead_Assignment.flow-meta.xml
```

**Scoring**: 110 points across 6 categories. Minimum 88 (80%) for deployment.

---

## Core Responsibilities

1. **Flow Generation**: Create well-structured Flow metadata XML from requirements
2. **Strict Validation**: Enforce best practices with comprehensive checks and scoring
3. **Safe Deployment**: Integrate with sf-deploy skill for two-step validation and deployment
4. **Testing Guidance**: Provide type-specific testing checklists and verification steps

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-flow → sf-deploy → sf-data** (you are here: sf-flow)

⚠️ Flow references custom object/fields? Create with sf-metadata FIRST. Deploy objects BEFORE flows.

```
1. sf-metadata  → Create objects/fields (local)
2. sf-flow      ◀── YOU ARE HERE (create flow locally)
3. sf-deploy    → Deploy all metadata (remote)
4. sf-data      → Create test data (remote - objects must exist!)
```

See `docs/orchestration.md` for extended orchestration patterns including Agentforce.

---

## 🔑 Key Insights

| Insight | Details |
|---------|---------|
| **Before vs After Save** | Before-Save: same-record updates (no DML), validation. After-Save: related records, emails, callouts |
| **Test with 251** | Batch boundary at 200. Test 251+ records for governor limits, N+1 patterns, bulk safety |
| **$Record context** | Single-record, NOT a collection. Platform handles batching. Never loop over $Record |
| **Transform vs Loop** | Transform: data mapping/shaping (30-50% faster). Loop: per-record decisions, counters, varying logic. See `docs/transform-vs-loop-guide.md` |

---

## Workflow Design (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Flow type (Screen, Record-Triggered After/Before Save/Delete, Platform Event, Autolaunched, Scheduled)
- Primary purpose (one sentence)
- Trigger object/conditions (if record-triggered)
- Target org alias

**Then**:
1. Check existing flows: `Glob: pattern="**/*.flow-meta.xml"`
2. Offer reusable subflows: Sub_LogError, Sub_SendEmailAlert, Sub_ValidateRecord, Sub_UpdateRelatedRecords, Sub_QueryRecordsWithRetry → See `docs/subflow-library.md` (in sf-flow folder)
3. If complex automation: Reference `docs/governance-checklist.md` (in sf-flow folder)
4. Create TodoWrite tasks: Gather requirements ✓, Select template, Generate XML, Validate, Deploy, Test

### Phase 2: Flow Design & Template Selection

**Select template**:
| Flow Type | Template File |
|-----------|---------------|
| Screen | `screen-flow-template.xml` |
| Record-Triggered | `record-triggered-*.xml` |
| Platform Event | `platform-event-flow-template.xml` |
| Autolaunched | `autolaunched-flow-template.xml` |
| Scheduled | `scheduled-flow-template.xml` |
| Wait Elements | `wait-template.xml` |

**Element Pattern Templates** (`templates/elements/`):
| Element | Template | Purpose |
|---------|----------|---------|
| Loop | `loop-pattern.xml` | Complete loop with nextValueConnector/noMoreValuesConnector |
| Get Records | `get-records-pattern.xml` | All recordLookups options (filters, sort, limit) |
| Delete Records | `record-delete-pattern.xml` | Filter-based and reference-based delete patterns |

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-flow/templates/[template].xml`
2. **Project folder**: `[project-root]/sf-flow/templates/[template].xml`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-flow/templates/record-triggered-flow-template.xml`

**Naming Convention** (Recommended Prefixes):

| Flow Type | Prefix | Example |
|-----------|--------|---------|
| Record-Triggered (After) | `Auto_` | `Auto_Lead_Assignment`, `Auto_Account_Update` |
| Record-Triggered (Before) | `Before_` | `Before_Lead_Validate`, `Before_Contact_Default` |
| Screen Flow | `Screen_` | `Screen_New_Customer`, `Screen_Case_Intake` |
| Scheduled | `Sched_` | `Sched_Daily_Cleanup`, `Sched_Weekly_Report` |
| Platform Event | `Event_` | `Event_Order_Completed` |
| Autolaunched | `Sub_` or `Util_` | `Sub_Send_Email`, `Util_Validate_Address` |

**Format**: `[Prefix]_Object_Action` using PascalCase (e.g., `Auto_Lead_Priority_Assignment`)

**Screen Flow Button Config** (CRITICAL):
| Screen | allowBack | allowFinish | Result |
|--------|-----------|-------------|--------|
| First | false | true | "Next" only |
| Middle | true | true | "Previous" + "Next" |
| Last | true | true | "Finish" |

Rule: `allowFinish="true"` required on all screens. Connector present → "Next", absent → "Finish".

**Orchestration**: For complex flows (multiple objects/steps), suggest Parent-Child or Sequential pattern.
- **CRITICAL**: Record-triggered flows CANNOT call subflows via XML deployment. Use inline orchestration instead. See `docs/xml-gotchas.md` (in sf-flow) and `docs/orchestration-guide.md` (in sf-flow)

### Phase 3: Flow Generation & Validation

**Create flow file**:
```bash
mkdir -p force-app/main/default/flows
Write: force-app/main/default/flows/[FlowName].flow-meta.xml
```

**Populate template**: Replace placeholders, API version: 62.0

**CRITICAL Requirements**:
- Alphabetical XML element ordering at root level
- NO `<bulkSupport>` (removed API 60.0+)
- Auto-Layout: all locationX/Y = 0
- Fault paths on all DML operations

**Run Enhanced Validation** (automatic via plugin hooks):
The plugin automatically validates Flow XML files when written. Manual validation:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate_flow.py force-app/main/default/flows/[FlowName].flow-meta.xml
```

**Validation (STRICT MODE)**:
- **BLOCK**: XML invalid, missing required fields (apiVersion/label/processType/status), API <62.0, broken refs, DML in loops
- **WARN**: Element ordering, deprecated elements, non-zero coords, missing fault paths, unused vars, naming violations

**New v2.0.0 Validations**:
- `storeOutputAutomatically` detection (data leak prevention)
- Same-object query anti-pattern (recommends $Record usage)
- Complex formula in loops warning
- Missing filters on Get Records
- Null check after Get Records recommendation
- Variable naming prefix validation (var_, col_, rec_, inp_, out_)

**Run Simulation** (REQUIRED for record-triggered/scheduled):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/simulate_flow.py force-app/main/default/flows/[FlowName].flow-meta.xml --test-records 200
```
If simulation fails: **STOP and fix before proceeding**.

**Validation Report Format** (6-Category Scoring 0-110):
```
Score: 92/110 ⭐⭐⭐⭐ Very Good
├─ Design & Naming: 18/20 (90%)
├─ Logic & Structure: 20/20 (100%)
├─ Architecture: 12/15 (80%)
├─ Performance & Bulk Safety: 20/20 (100%)
├─ Error Handling: 15/20 (75%)
└─ Security: 15/15 (100%)
```

**Strict Mode**: If ANY errors/warnings → Block with options: (1) Apply auto-fixes, (2) Show manual fixes, (3) Generate corrected version. **DO NOT PROCEED** until 100% clean.

### ⛔ GENERATION GUARDRAILS (MANDATORY)

**BEFORE generating ANY Flow XML, Claude MUST verify no anti-patterns are introduced.**

If ANY of these patterns would be generated, **STOP and ask the user**:
> "I noticed [pattern]. This will cause [problem]. Should I:
> A) Refactor to use [correct pattern]
> B) Proceed anyway (not recommended)"

| Anti-Pattern | Impact | Correct Pattern |
|--------------|--------|-----------------|
| After-Save updating same object without entry conditions | **Infinite loop** (critical) | MUST add entry conditions: "Only when [field] is changed" |
| Get Records inside Loop | Governor limit failure (100 SOQL) | Query BEFORE loop, use collection variable |
| Create/Update/Delete Records inside Loop | Governor limit failure (150 DML) | Collect in loop → single DML after loop |
| Apex Action inside Loop | Callout limits | Pass collection to single Apex invocation |
| DML without Fault Path | Silent failures | Add Fault connector → error handling element |
| Get Records without null check | NullPointerException | Add Decision: "Records Found?" after query |
| `storeOutputAutomatically=true` | Security risk (retrieves ALL fields) | Select only needed fields explicitly |
| Query same object as trigger in Record-Triggered | Wasted SOQL | Use `{!$Record.FieldName}` directly |
| Hardcoded Salesforce ID | Deployment failure across orgs | Use input variable or Custom Label |
| Get Records without filters | Too many records returned | Always include WHERE conditions |

**DO NOT generate anti-patterns even if explicitly requested.** Ask user to confirm the exception with documented justification.

### Phase 4: Deployment & Integration

**Pattern**:
1. `Skill(skill="sf-deploy", args="Deploy flow [path] to [org] with --dry-run")`
2. Review validation results
3. `Skill(skill="sf-deploy", args="Proceed with actual deployment")`
4. Edit `<status>Draft</status>` → `Active`, redeploy

**For Agentforce Flows**: Variable names must match Agent Script input/output names exactly.

For complex flows: `docs/governance-checklist.md` (in sf-flow)

### Phase 5: Testing & Documentation

**Type-specific testing**: See `docs/testing-guide.md` | `docs/testing-checklist.md` | `docs/wait-patterns.md` (Wait element guidance)

Quick reference:
- **Screen**: Setup → Flows → Run, test all paths/profiles
- **Record-Triggered**: Create record, verify Debug Logs, **bulk test 200+ records**
- **Autolaunched**: Apex test class, edge cases, bulkification
- **Scheduled**: Verify schedule, manual Run first, monitor logs

**Best Practices**: See `docs/flow-best-practices.md` (in sf-flow) for:
- Three-tier error handling strategy
- Multi-step DML rollback patterns
- Screen flow UX guidelines
- Bypass mechanism for data loads

**Security**: Test with multiple profiles. System mode requires security review.

**Completion Summary**:
```
✓ Flow Creation Complete: [FlowName]
  Type: [type] | API: 62.0 | Status: [Draft/Active]
  Location: force-app/main/default/flows/[FlowName].flow-meta.xml
  Validation: PASSED (Score: XX/110)
  Deployment: Org=[target-org], Job=[job-id]

  Navigate: Setup → Process Automation → Flows → "[FlowName]"

Next Steps: Test (unit, bulk, security), Review docs, Activate if Draft, Monitor logs
Resources: `examples/`, `docs/subflow-library.md`, `docs/orchestration-guide.md`, `docs/governance-checklist.md` (in sf-flow folder)
```

## Best Practices (Built-In Enforcement)

### ⛔ CRITICAL: Record-Triggered Flow Architecture

**NEVER loop over triggered records.** `$Record` = single record; platform handles batching.

| Pattern | OK? | Notes |
|---------|-----|-------|
| `$Record.FieldName` | ✅ | Direct access |
| Loop over `$Record__c` | ❌ | Process Builder pattern, not Flow |
| Loop over `$Record` | ❌ | $Record is single, not collection |

**Loops for RELATED records only**: Get Records → Loop collection → Assignment → DML after loop

### ⛔ CRITICAL: No Parent Traversal in Get Records

`recordLookups` cannot query `Parent.Field` (e.g., `Manager.Name`). **Solution**: Two Get Records - child first, then parent by Id.

### recordLookups Best Practices

| Element | Recommendation | Why |
|---------|----------------|-----|
| `getFirstRecordOnly` | Set to `true` for single-record queries | Avoids collection overhead |
| `storeOutputAutomatically` | Set to `false`, use `outputReference` | Prevents data leaks, explicit variable |
| `assignNullValuesIfNoRecordsFound` | Set to `false` | Preserves previous variable value |
| `faultConnector` | Always include | Handle query failures gracefully |
| `filterLogic` | Use `and` for multiple filters | Clear filter behavior |

### Critical Requirements
- **API 62.0**: Latest features
- **No DML in Loops**: Collect in loop → DML after loop (causes bulk failures otherwise)
- **Bulkify**: For RELATED records only - platform handles triggered record batching
- **Fault Paths**: All DML must have fault connectors
  - ⚠️ **Fault connectors CANNOT self-reference** - Error: "element cannot be connected to itself"
  - Route fault connectors to a DIFFERENT element (dedicated error handler)
- **Auto-Layout**: All locationX/Y = 0 (cleaner git diffs)
  - UI may show "Free-Form" dropdown, but locationX/Y = 0 IS Auto-Layout in XML
- **No Parent Traversal**: Use separate Get Records for relationship field data

### XML Element Ordering (CRITICAL)

**All elements of the same type MUST be grouped together. Do NOT scatter elements across the file.**

Complete alphabetical order:
```
apiVersion → assignments → constants → decisions → description → environments →
formulas → interviewLabel → label → loops → processMetadataValues → processType →
recordCreates → recordDeletes → recordLookups → recordUpdates → runInMode →
screens → start → status → subflows → textTemplates → variables → waits
```

**Common Mistake**: Adding an assignment near related logic (e.g., after a loop) when other assignments exist earlier.
- **Error**: "Element assignments is duplicated at this location"
- **Fix**: Move ALL assignments to the assignments section

### Performance
- **Batch DML**: Get Records → Assignment → Update Records pattern
- **Filters over loops**: Use Get Records with filters instead of loops + decisions
- **Transform element**: Powerful but complex XML - NOT recommended for hand-written flows

### Design & Security
- **Variable Names (v2.0.0)**: Use prefixes for clarity:
  - `var_` Regular variables (e.g., `var_AccountName`)
  - `col_` Collections (e.g., `col_ContactIds`)
  - `rec_` Record variables (e.g., `rec_Account`)
  - `inp_` Input variables (e.g., `inp_RecordId`)
  - `out_` Output variables (e.g., `out_IsSuccess`)
- **Element Names**: PascalCase_With_Underscores (e.g., `Check_Account_Type`)
- **Button Names (v2.0.0)**: `Action_[Verb]_[Object]` (e.g., `Action_Save_Contact`)
- **System vs User Mode**: Understand implications, validate FLS for sensitive fields
- **No hardcoded data**: Use variables/custom settings
- See `docs/flow-best-practices.md` (in sf-flow) for comprehensive guidance

## Common Error Patterns

**DML in Loop**: Collect records in collection variable → Single DML after loop
**Missing Fault Path**: Add fault connector from DML → error handling → log/display
**Self-Referencing Fault**: Error "element cannot be connected to itself" → Route fault connector to DIFFERENT element
**Element Duplicated**: Error "Element X is duplicated" → Group ALL elements of same type together
**Field Not Found**: Verify field exists, deploy field first if missing
**Insufficient Permissions**: Check profile permissions, consider System mode

| Error Pattern | Fix |
|---------------|-----|
| `$Record__Prior` in Create-only | Only valid for Update/CreateAndUpdate triggers |
| "Parent.Field doesn't exist" | Use TWO Get Records (child then parent) |
| `$Record__c` loop fails | Use `$Record` directly (single context, not collection) |

**XML Gotchas**: See `docs/xml-gotchas.md` (in sf-flow)

## Edge Cases

| Scenario | Solution |
|----------|----------|
| >200 records | Warn limits, suggest scheduled flow |
| >5 branches | Use subflows |
| Cross-object | Check circular deps, test recursion |
| Production | Deploy Draft, activate explicitly |
| Unknown org | Use standard objects (Account, Contact, etc.) |

**Debug**: Flow not visible → deploy report + permissions | Tests fail → Debug Logs + bulk test | Sandbox→Prod fails → FLS + dependencies

---

## Cross-Skill Integration

| From Skill | To sf-flow | When |
|------------|------------|------|
| sf-ai-agentforce | → sf-flow | "Create Autolaunched Flow for agent action" |
| sf-apex | → sf-flow | "Create Flow wrapper for Apex logic" |
| sf-integration | → sf-flow | "Create HTTP Callout Flow" |

| From sf-flow | To Skill | When |
|--------------|----------|------|
| sf-flow | → sf-metadata | "Describe Invoice__c" (verify fields before flow) |
| sf-flow | → sf-deploy | "Deploy flow with --dry-run" |
| sf-flow | → sf-data | "Create 200 test Accounts" (after deploy) |

**Deployment**: See Phase 4 above.

---

## LWC Integration (Screen Flows)

Embed custom Lightning Web Components in Flow Screens for rich, interactive UIs.

### Templates

| Template | Purpose |
|----------|---------|
| `templates/screen-flow-with-lwc.xml` | Flow embedding LWC component |
| `templates/apex-action-template.xml` | Flow calling Apex @InvocableMethod |

### Flow XML Pattern

```xml
<screens>
    <fields>
        <extensionName>c:recordSelector</extensionName>
        <fieldType>ComponentInstance</fieldType>
        <inputParameters>
            <name>recordId</name>
            <value><elementReference>var_RecordId</elementReference></value>
        </inputParameters>
        <outputParameters>
            <assignToReference>var_SelectedId</assignToReference>
            <name>selectedRecordId</name>
        </outputParameters>
    </fields>
</screens>
```

### Documentation

| Resource | Location |
|----------|----------|
| LWC Integration Guide | [docs/lwc-integration-guide.md](docs/lwc-integration-guide.md) |
| LWC Component Setup | [sf-lwc/docs/flow-integration-guide.md](../sf-lwc/docs/flow-integration-guide.md) |
| Triangle Architecture | [docs/triangle-pattern.md](docs/triangle-pattern.md) |

---

## Apex Integration

Call Apex `@InvocableMethod` classes from Flow for complex business logic.

### Flow XML Pattern

```xml
<actionCalls>
    <name>Process_Record</name>
    <actionName>RecordProcessor</actionName>
    <actionType>apex</actionType>
    <inputParameters>
        <name>recordId</name>
        <value><elementReference>var_RecordId</elementReference></value>
    </inputParameters>
    <outputParameters>
        <assignToReference>var_IsSuccess</assignToReference>
        <name>isSuccess</name>
    </outputParameters>
    <faultConnector>
        <targetReference>Handle_Error</targetReference>
    </faultConnector>
</actionCalls>
```

### Documentation

| Resource | Location |
|----------|----------|
| Apex Action Template | `templates/apex-action-template.xml` |
| Apex @InvocableMethod Guide | [sf-apex/docs/flow-integration.md](../sf-apex/docs/flow-integration.md) |
| Triangle Architecture | [docs/triangle-pattern.md](docs/triangle-pattern.md) |

### ⚠️ Flows for sf-ai-agentforce

**When sf-ai-agentforce requests a Flow:**
- sf-ai-agentforce will invoke sf-flow (this skill) to create Flows
- sf-flow creates the validated Flow XML
- sf-deploy handles deployment to org
- Only THEN can sf-ai-agentforce use `flow://FlowName` targets

**Variable Name Matching**: When creating Flows for Agentforce agents:
- Agent Script input/output names MUST match Flow variable API names exactly
- Use descriptive names (e.g., `inp_AccountId`, `out_AccountName`)
- Mismatched names cause "Internal Error" during agent publish

| Direction | Pattern |
|-----------|---------|
| sf-flow → sf-metadata | "Describe Invoice__c" (verify fields before flow) |
| sf-flow → sf-deploy | Deploy with validation |
| sf-flow → sf-data | "Create 200 test Accounts" (test data after deploy) |
| sf-ai-agentforce → sf-flow | "Create Autolaunched Flow for agent action" - **sf-flow is MANDATORY** |

## Notes

**Dependencies** (optional): sf-deploy, sf-metadata, sf-data | **API**: 62.0 | **Mode**: Strict (warnings block) | Python validators recommended

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
