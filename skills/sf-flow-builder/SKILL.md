---
name: sf-flow-builder
description: Creates and validates Salesforce flows using best practices and metadata standards
version: 1.4.0
author: Jag Valaiyapathy
license: MIT
tags:
  - salesforce
  - flow
  - automation
  - builder
  - metadata
  - sfdx
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - TodoWrite
  - Skill
  - WebFetch
dependencies:
  - name: sf-deployment
    version: ">=2.0.0"
    required: true
metadata:
  format_version: "2.0.0"
  created: "2024-11-28"
  updated: "2025-12-02"
  api_version: "62.0"
  license_file: "LICENSE"
  features:
    - transform-element
    - bulk-validation
    - strict-mode
    - simulation-mode
    - platform-events
    - before-save-triggers
    - before-delete-triggers
---

# sf-flow-builder: Salesforce Flow Creation and Validation

Expert Salesforce Flow Builder with deep knowledge of best practices, bulkification, and Winter '26 (API 62.0) metadata. Create production-ready, performant, secure, and maintainable flows.

## Core Responsibilities

1. **Flow Generation**: Create well-structured Flow metadata XML from requirements
2. **Strict Validation**: Enforce best practices with comprehensive checks and scoring
3. **Safe Deployment**: Integrate with sf-deployment skill for two-step validation and deployment
4. **Testing Guidance**: Provide type-specific testing checklists and verification steps

## Workflow Design (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Flow type (Screen, Record-Triggered After/Before Save/Delete, Platform Event, Autolaunched, Scheduled)
- Primary purpose (one sentence)
- Trigger object/conditions (if record-triggered)
- Target org alias

**Then**:
1. Check existing flows: `Glob: pattern="**/*.flow-meta.xml"`
2. Offer reusable subflows: Sub_LogError, Sub_SendEmailAlert, Sub_ValidateRecord, Sub_UpdateRelatedRecords, Sub_QueryRecordsWithRetry → See [docs/subflow-library.md](docs/subflow-library.md)
3. If complex automation: Reference [docs/governance-checklist.md](docs/governance-checklist.md)
4. Create TodoWrite tasks: Gather requirements ✓, Select template, Generate XML, Validate, Deploy, Test

### Phase 2: Flow Design & Template Selection

**Select template**:
| Flow Type | Template |
|-----------|----------|
| Screen | `templates/screen-flow-template.xml` |
| Record-Triggered | `templates/record-triggered-*.xml` |
| Platform Event | `templates/platform-event-flow-template.xml` |
| Autolaunched | `templates/autolaunched-flow-template.xml` |
| Scheduled | `templates/scheduled-flow-template.xml` |

Load via: `Read: ~/.claude/skills/sf-flow-builder/templates/[template].xml`

**Naming**: API Name = PascalCase_With_Underscores (e.g., `Account_Creation_Screen_Flow`)

**Screen Flow Button Config** (CRITICAL):
| Screen | allowBack | allowFinish | Result |
|--------|-----------|-------------|--------|
| First | false | true | "Next" only |
| Middle | true | true | "Previous" + "Next" |
| Last | true | true | "Finish" |

Rule: `allowFinish="true"` required on all screens. Connector present → "Next", absent → "Finish".

**Orchestration**: For complex flows (multiple objects/steps), suggest Parent-Child or Sequential pattern.
- **CRITICAL**: Record-triggered flows CANNOT call subflows via XML deployment. Use inline orchestration instead. See [docs/xml-gotchas.md](docs/xml-gotchas.md#subflow-calling-limitation) and [docs/orchestration-guide.md](docs/orchestration-guide.md)

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

**Run Enhanced Validation**:
```bash
python3 ~/.claude/skills/sf-flow-builder/validators/enhanced_validator.py \
  force-app/main/default/flows/[FlowName].flow-meta.xml
```

**Validation (STRICT MODE)**:
- **BLOCK**: XML invalid, missing required fields (apiVersion/label/processType/status), API <62.0, broken refs, DML in loops
- **WARN**: Element ordering, deprecated elements, non-zero coords, missing fault paths, unused vars, naming violations

**Run Simulation** (REQUIRED for record-triggered/scheduled):
```bash
python3 ~/.claude/skills/sf-flow-builder/validators/flow_simulator.py \
  force-app/main/default/flows/[FlowName].flow-meta.xml --test-records 200
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

### Phase 4: Deployment & Integration

**Step 1: Validation (Check-Only)**
```
Skill(skill="sf-deployment")
Request: "Deploy flow at force-app/main/default/flows/[FlowName].flow-meta.xml to [target-org] with --dry-run. Do NOT deploy yet."
```

Review: Check for field access, permissions, conflicts.

**Step 2: Actual Deployment** (only if validation succeeds)
```
Skill(skill="sf-deployment")
Request: "Proceed with actual deployment of flow to [target-org]."
```

**Step 3: Activation**
```bash
Edit: <status>Draft</status> → <status>Active</status>
Skill(skill="sf-deployment") "Deploy activated flow to [target-org]"
```

**Generate Documentation**:
```bash
python3 ~/.claude/skills/sf-flow-builder/generators/doc_generator.py \
  force-app/main/default/flows/[FlowName].flow-meta.xml \
  docs/flows/[FlowName]_documentation.md
```

For complex flows: [docs/governance-checklist.md](docs/governance-checklist.md) (min score: 140/200 for production)

### Phase 5: Testing & Documentation

**Type-specific testing**: See [docs/testing-guide.md](docs/testing-guide.md)

Quick reference:
- **Screen**: Setup → Flows → Run, test all paths/profiles
- **Record-Triggered**: Create record, verify Debug Logs, **bulk test 200+ records**
- **Autolaunched**: Apex test class, edge cases, bulkification
- **Scheduled**: Verify schedule, manual Run first, monitor logs

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
Resources: examples/, docs/subflow-library.md, docs/orchestration-guide.md, docs/governance-checklist.md
```

## Best Practices (Built-In Enforcement)

### Critical Requirements
- **API 62.0**: Latest features
- **No DML in Loops**: Collect in loop → DML after loop (causes bulk failures otherwise)
- **Bulkify**: MUST handle collections for record-triggered flows
- **Fault Paths**: All DML must have fault connectors
- **Auto-Layout**: All locationX/Y = 0 (cleaner git diffs)
  - UI may show "Free-Form" dropdown, but locationX/Y = 0 IS Auto-Layout in XML

### XML Element Ordering (CRITICAL)
Required alphabetical order: `apiVersion` → `assignments` → `decisions` → `description` → `label` → `loops` → `processType` → `recordCreates` → `recordUpdates` → `start` → `status` → `variables`

### Performance
- **Batch DML**: Get Records → Assignment → Update Records pattern
- **Filters over loops**: Use Get Records with filters instead of loops + decisions
- **Transform element**: Powerful but complex XML - NOT recommended for hand-written flows

### Design & Security
- **Names**: Variables (camelCase), Elements (PascalCase_With_Underscores)
- **System vs User Mode**: Understand implications, validate FLS for sensitive fields
- **No hardcoded data**: Use variables/custom settings

## Common Error Patterns

**DML in Loop**: Collect records in collection variable → Single DML after loop
**Missing Fault Path**: Add fault connector from DML → error handling → log/display
**Field Not Found**: Verify field exists, deploy field first if missing
**Insufficient Permissions**: Check profile permissions, consider System mode

**$Record__Prior** (CRITICAL):
- NEVER use in Create-only triggers (`<recordTriggerType>Create</recordTriggerType>`)
- Valid only for: `Update` or `CreateAndUpdate` triggers
- Error: "$Record__Prior can only be used...with recordTriggerType of Update or CreateAndUpdate"

**XML Gotchas**: See [docs/xml-gotchas.md](docs/xml-gotchas.md) for recordLookups conflicts, element ordering, Transform issues, and subflow limitations.

## Edge Cases

- **Large Data (>200 records)**: Warn governor limits, suggest scheduled flow
- **Complex Branching (>5 paths)**: Suggest subflows, document criteria
- **Cross-Object Updates**: Check circular dependencies, test for recursion
- **Production**: Keep Draft initially, require explicit activation, provide rollback

**Common Issues**:
- Flow not visible → Check `sf project deploy report`, verify permissions, refresh Setup
- Validation passes but testing fails → Check Debug Logs, test bulk (200+ records)
- Sandbox works, production fails → Check FLS differences, verify dependencies

## Notes

- **Strict Mode**: All warnings block deployment
- **API 62.0 Required**
- **Two-Step Deployment**: Validate before deploying
- **Dependencies**: Requires sf-deployment ≥2.0.0
- **Python Validators**: Optional but recommended

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
