---
name: sf-metadata
description: >
  Generates and queries Salesforce metadata with 120-point scoring. Use when
  creating custom objects, fields, profiles, permission sets, validation rules,
  or querying org metadata structures via sf CLI.
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
    - matcher: Write
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/post-write-validate.py"
          timeout: 10000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-metadata"
          timeout: 5000
    - matcher: Edit
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-metadata"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-metadata"
      timeout: 5000
---

# sf-metadata: Salesforce Metadata Generation and Org Querying

Expert Salesforce administrator specializing in metadata architecture, security model design, and schema best practices. Generate production-ready metadata XML and query org structures using sf CLI v2.

## Core Responsibilities

1. **Metadata Generation**: Create Custom Objects, Fields, Profiles, Permission Sets, Validation Rules, Record Types, Page Layouts
2. **Org Querying**: Describe objects, list fields, query metadata using sf CLI v2
3. **Validation & Scoring**: Score metadata against 6 categories (0-120 points)
4. **Cross-Skill Integration**: Provide metadata discovery for sf-apex and sf-flow
5. **Deployment Integration**: Deploy metadata via sf-deploy skill

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-flow → sf-deploy → sf-data** (you are here: sf-metadata)

⚠️ sf-data requires objects deployed to org. Always deploy BEFORE creating test data.

```
1. sf-metadata  ◀── YOU ARE HERE (create objects/fields locally)
2. sf-flow      → Create flow definitions (local)
3. sf-deploy    → Deploy all metadata (remote)
4. sf-data      → Create test data (remote - objects must exist!)
```

See `docs/orchestration.md` for extended orchestration patterns including Agentforce.

---

## ⚠️ CRITICAL: Field-Level Security

**Deployed fields are INVISIBLE until FLS is configured!** Always prompt for Permission Set generation after creating objects/fields. See **Phase 3.5** for auto-generation workflow.

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Operation type: **Generate** metadata OR **Query** org metadata
- If generating:
  - Metadata type (Object, Field, Profile, Permission Set, Validation Rule, Record Type, Layout)
  - Target object (for fields, validation rules, record types)
  - Specific requirements (field type, data type, relationships, picklist values)
- If querying:
  - Query type (describe object, list fields, list metadata)
  - Target org alias
  - Object name or metadata type to query

**Then**:
1. Check existing metadata: `Glob: **/*-meta.xml`, `Glob: **/objects/**/*.xml`
2. Check for sfdx-project.json to confirm Salesforce project structure
3. Create TodoWrite tasks

### Phase 2: Template Selection / Query Execution

#### For Generation

**Select template**:
| Metadata Type | Template |
|---------------|----------|
| Custom Object | `templates/objects/custom-object.xml` |
| Text Field | `templates/fields/text-field.xml` |
| Number Field | `templates/fields/number-field.xml` |
| Currency Field | `templates/fields/currency-field.xml` |
| Date Field | `templates/fields/date-field.xml` |
| Checkbox Field | `templates/fields/checkbox-field.xml` |
| Picklist Field | `templates/fields/picklist-field.xml` |
| Multi-Select Picklist | `templates/fields/multi-select-picklist.xml` |
| Lookup Field | `templates/fields/lookup-field.xml` |
| Master-Detail Field | `templates/fields/master-detail-field.xml` |
| Formula Field | `templates/fields/formula-field.xml` |
| Roll-Up Summary | `templates/fields/rollup-summary-field.xml` |
| Email Field | `templates/fields/email-field.xml` |
| Phone Field | `templates/fields/phone-field.xml` |
| URL Field | `templates/fields/url-field.xml` |
| Text Area (Long) | `templates/fields/textarea-field.xml` |
| Profile | `templates/profiles/profile.xml` |
| Permission Set | `templates/permission-sets/permission-set.xml` |
| Validation Rule | `templates/validation-rules/validation-rule.xml` |
| Record Type | `templates/record-types/record-type.xml` |
| Page Layout | `templates/layouts/page-layout.xml` |

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-metadata/templates/[path]`
2. **Project folder**: `[project-root]/sf-metadata/templates/[path]`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-metadata/templates/objects/custom-object.xml`

#### For Querying (sf CLI v2 Commands)

| Query Type | Command |
|------------|---------|
| Describe object | `sf sobject describe --sobject [ObjectName] --target-org [alias] --json` |
| List custom objects | `sf org list metadata --metadata-type CustomObject --target-org [alias] --json` |
| List all metadata types | `sf org list metadata-types --target-org [alias] --json` |
| List profiles | `sf org list metadata --metadata-type Profile --target-org [alias] --json` |
| List permission sets | `sf org list metadata --metadata-type PermissionSet --target-org [alias] --json` |

**Present query results** in structured format:
```
📊 Object: Account
════════════════════════════════════════

📁 Standard Fields: 45
📁 Custom Fields: 12
🔗 Relationships: 8
📝 Validation Rules: 3
📋 Record Types: 2

Custom Fields:
├── Industry_Segment__c (Picklist)
├── Annual_Revenue__c (Currency)
├── Primary_Contact__c (Lookup → Contact)
└── ...
```

### Phase 3: Generation / Validation

**For Generation**:
1. Create metadata file in appropriate directory:
   - Objects: `force-app/main/default/objects/[ObjectName__c]/[ObjectName__c].object-meta.xml`
   - Fields: `force-app/main/default/objects/[ObjectName]/fields/[FieldName__c].field-meta.xml`
   - Profiles: `force-app/main/default/profiles/[ProfileName].profile-meta.xml`
   - Permission Sets: `force-app/main/default/permissionsets/[PermSetName].permissionset-meta.xml`
   - Validation Rules: `force-app/main/default/objects/[ObjectName]/validationRules/[RuleName].validationRule-meta.xml`
   - Record Types: `force-app/main/default/objects/[ObjectName]/recordTypes/[RecordTypeName].recordType-meta.xml`
   - Layouts: `force-app/main/default/layouts/[ObjectName]-[LayoutName].layout-meta.xml`

2. Populate template with user requirements

3. Apply naming conventions (see `docs/naming-conventions.md` in sf-metadata folder)

4. Run validation (automatic via hooks or manual)

**Validation Report Format** (6-Category Scoring 0-120):
```
Score: 105/120 ⭐⭐⭐⭐ Very Good
├─ Structure & Format:  20/20 (100%)
├─ Naming Conventions:  18/20 (90%)
├─ Data Integrity:      15/20 (75%)
├─ Security & FLS:      20/20 (100%)
├─ Documentation:       18/20 (90%)
└─ Best Practices:      14/20 (70%)

Issues:
⚠️ [Naming] Field API name should use PascalCase: 'account_status__c' → 'Account_Status__c'
⚠️ [Best Practice] Consider using Global Value Set for reusable picklist
```

### Phase 3.5: Permission Set Auto-Generation (NEW)

**After creating Custom Objects or Fields, ALWAYS prompt the user:**

```
AskUserQuestion:
  question: "Would you like me to generate a Permission Set for [ObjectName__c] field access?"
  header: "FLS Setup"
  options:
    - label: "Yes, generate Permission Set"
      description: "Creates [ObjectName]_Access.permissionset-meta.xml with object CRUD and field access"
    - label: "No, I'll handle FLS manually"
      description: "Skip Permission Set generation - you'll configure FLS via Setup or Profile"
```

**If user selects "Yes":**

1. **Collect field information** from created metadata
2. **Filter out required fields** (they are auto-visible, cannot be in Permission Sets)
3. **Filter out formula fields** (can only be readable, not editable)
4. **Generate Permission Set** at: `force-app/main/default/permissionsets/[ObjectName]_Access.permissionset-meta.xml`

**Permission Set Generation Rules:**

| Field Type | Include in Permission Set? | Notes |
|------------|---------------------------|-------|
| Required fields | ❌ NO | Auto-visible, Salesforce rejects in Permission Set |
| Optional fields | ✅ YES | Include with `editable: true, readable: true` |
| Formula fields | ✅ YES | Include with `editable: false, readable: true` |
| Roll-Up Summary | ✅ YES | Include with `editable: false, readable: true` |
| Master-Detail | ❌ NO | Controlled by parent object permissions |
| Name field | ❌ NO | Always visible, cannot be in Permission Set |

**Example Auto-Generated Permission Set:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Auto-generated: Grants access to Customer_Feedback__c and its fields</description>
    <hasActivationRequired>false</hasActivationRequired>
    <label>Customer Feedback Access</label>

    <objectPermissions>
        <allowCreate>true</allowCreate>
        <allowDelete>true</allowDelete>
        <allowEdit>true</allowEdit>
        <allowRead>true</allowRead>
        <modifyAllRecords>false</modifyAllRecords>
        <object>Customer_Feedback__c</object>
        <viewAllRecords>true</viewAllRecords>
    </objectPermissions>

    <!-- NOTE: Required fields are EXCLUDED (auto-visible) -->
    <!-- NOTE: Formula fields have editable=false -->

    <fieldPermissions>
        <editable>true</editable>
        <field>Customer_Feedback__c.Optional_Field__c</field>
        <readable>true</readable>
    </fieldPermissions>
</PermissionSet>
```

---

### Phase 4: Deployment

```
Skill(skill="sf-deploy", args="Deploy metadata at force-app/main/default/objects/[ObjectName] and permission set to [target-org]")
```

**Post-deployment** (optional - assign permission set):
```bash
sf org assign permset --name [ObjectName]_Access --target-org [alias]
```

### Phase 5: Verification

**For Generated Metadata**:
```
✓ Metadata Complete: [MetadataName]
  Type: [CustomObject/CustomField/Profile/etc.] | API: 65.0
  Location: force-app/main/default/[path]
  Validation: PASSED (Score: XX/120)

Next Steps:
  1. Verify in Setup → Object Manager → [Object]
  2. Check Field-Level Security for new fields
  3. Add to Page Layouts if needed
```

**For Queries**:
- Present results in structured format
- Highlight relevant information
- Offer follow-up actions (create field, modify permissions, etc.)

---

## Best Practices (Built-In Enforcement)

### Critical Requirements

**Structure & Format** (20 points):
- Valid XML syntax (-10 if invalid)
- Correct Salesforce namespace: `http://soap.sforce.com/2006/04/metadata` (-5 if missing)
- API version present and >= 65.0 (-5 if outdated)
- Correct file path and naming structure (-5 if wrong)

**Naming Conventions** (20 points):
- Custom objects/fields end with `__c` (-3 each violation)
- Use PascalCase for API names: `Account_Status__c` not `account_status__c` (-2 each)
- Meaningful labels (no abbreviations like `Acct`, `Sts`) (-2 each)
- Relationship names follow pattern: `[ParentObject]_[ChildObjects]` (-3)

**Data Integrity** (20 points):
- Required fields have sensible defaults or validation (-5)
- Number fields have appropriate precision/scale (-3)
- Picklist values properly defined with labels (-3)
- Relationship delete constraints specified (SetNull, Restrict, Cascade) (-3)
- Formula field syntax valid (-5)
- Roll-up summaries reference correct fields (-3)

**Security & FLS** (20 points):
- Field-Level Security considerations documented (-5 if sensitive field exposed)
- Sensitive field types flagged (SSN patterns, Credit Card patterns) (-10)
- Object sharing model appropriate for data sensitivity (-5)
- Permission Sets preferred over Profile modifications (advisory)

**Documentation** (20 points):
- Description present and meaningful on objects/fields (-5 if missing)
- Help text for user-facing fields (-3 each)
- Clear error messages for validation rules (-3)
- Inline comments in complex formulas (-3)

**Best Practices** (20 points):
- Use Permission Sets over Profiles when possible (-3 if Profile-first)
- Avoid hardcoded Record IDs in formulas (-5 if found)
- Use Global Value Sets for reusable picklists (advisory)
- Master-Detail vs Lookup selection appropriate for use case (-3)
- Record Types have associated Page Layouts (-3)

### Scoring

**Thresholds**: ⭐⭐⭐⭐⭐ 108+ | ⭐⭐⭐⭐ 96-107 | ⭐⭐⭐ 84-95 | Block: <72

---

## Field Template Tips

### Number Field: Omit Empty Defaults

**⚠️ Don't include `<defaultValue>` if it's empty or zero - Salesforce ignores it:**

```xml
<!-- ❌ WRONG: Empty default is ignored, adds noise -->
<CustomField>
    <fullName>Score__c</fullName>
    <type>Number</type>
    <precision>3</precision>
    <scale>0</scale>
    <defaultValue></defaultValue>  <!-- Remove this! -->
</CustomField>

<!-- ✅ CORRECT: Omit defaultValue entirely if not needed -->
<CustomField>
    <fullName>Score__c</fullName>
    <type>Number</type>
    <precision>3</precision>
    <scale>0</scale>
</CustomField>

<!-- ✅ CORRECT: Include defaultValue only if you need a specific value -->
<CustomField>
    <fullName>Priority__c</fullName>
    <type>Number</type>
    <precision>1</precision>
    <scale>0</scale>
    <defaultValue>3</defaultValue>  <!-- Meaningful default -->
</CustomField>
```

### Standard vs Custom Object Paths

**⚠️ Standard objects use different path than custom objects:**

| Object Type | Path Example |
|-------------|--------------|
| Standard (Lead) | `objects/Lead/fields/Lead_Score__c.field-meta.xml` |
| Custom | `objects/MyObject__c/fields/MyField__c.field-meta.xml` |

**Common Mistake**: Using `Lead__c` (with suffix) for standard Lead object.

---

## Field Type Selection Guide

| Type | Salesforce | Notes |
|------|------------|-------|
| Text | Text / Text Area (Long/Rich) | ≤255 chars / multi-line / HTML |
| Numbers | Number / Currency | Decimals or money (org currency) |
| Boolean | Checkbox | True/False |
| Choice | Picklist / Multi-Select | Single/multiple predefined options |
| Date | Date / DateTime | With or without time |
| Contact | Email / Phone / URL | Validated formats |
| Relationship | Lookup / Master-Detail | Optional / required parent |
| Calculated | Formula / Roll-Up | Derived from fields / children |

---

## Relationship Decision Matrix

| Scenario | Use | Reason |
|----------|-----|--------|
| Parent optional | Lookup | Child can exist without parent |
| Parent required | Master-Detail | Cascade delete, roll-up summaries |
| Many-to-Many | Junction Object | Two Master-Detail relationships |
| Self-referential | Hierarchical Lookup | Same object (e.g., Account hierarchy) |
| Cross-object formula | Master-Detail or Formula | Access parent fields |

---

## Common Validation Rule Patterns

| Pattern | Formula | Use |
|---------|---------|-----|
| Conditional Required | `AND(ISPICKVAL(Status,'Closed'), ISBLANK(Close_Date__c))` | Field required when condition met |
| Email Regex | `NOT(REGEX(Email__c, "^[a-zA-Z0-9._-]+@..."))` | Format validation |
| Future Date | `Due_Date__c < TODAY()` | Date constraints |
| Cross-Object | `AND(Account.Type != 'Customer', Amount__c > 100000)` | Related field checks |

---

## Cross-Skill Integration

| From Skill | To sf-metadata | When |
|------------|----------------|------|
| sf-apex | → sf-metadata | "Describe Invoice__c" (discover fields before coding) |
| sf-flow | → sf-metadata | "Describe object fields, record types, validation rules" |
| sf-data | → sf-metadata | "Describe Custom_Object__c fields" (discover structure) |

| From sf-metadata | To Skill | When |
|------------------|----------|------|
| sf-metadata | → sf-deploy | "Deploy with --dry-run" (validate & deploy metadata) |
| sf-metadata | → sf-flow | After creating objects/fields that Flow will reference |

---

## Metadata Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Profile-based FLS | Use Permission Sets for granular access |
| Hardcoded IDs in formulas | Use Custom Settings or Custom Metadata |
| Validation rule without bypass | Add `$Permission.Bypass_Validation__c` check |
| Too many picklist values (>200) | Consider Custom Object instead |
| Auto-number without prefix | Add meaningful prefix: `INV-{0000}` |
| Roll-up on non-M-D | Use trigger-based calculation or DLRS |
| Field label = API name | Use user-friendly labels |
| No description on custom objects | Always document purpose |

---

## sf CLI Quick Reference

### Object & Field Queries

```bash
# Describe standard or custom object
sf sobject describe --sobject Account --target-org [alias] --json

# List all custom objects
sf org list metadata --metadata-type CustomObject --target-org [alias] --json

# List all custom fields on an object
sf org list metadata --metadata-type CustomField --folder Account --target-org [alias] --json
```

### Metadata Operations

```bash
# List all metadata types available
sf org list metadata-types --target-org [alias] --json

# Retrieve specific metadata
sf project retrieve start --metadata CustomObject:Account --target-org [alias]

# Generate package.xml from source
sf project generate manifest --source-dir force-app --name package.xml
```

### Interactive Generation

```bash
# Generate custom object interactively
sf schema generate sobject --label "My Object"

# Generate custom field interactively
sf schema generate field --label "My Field" --object Account
```

---

## Reference & Dependencies

**Docs**: `docs/` folder (in sf-metadata) - metadata-types-reference, field-types-guide, fls-best-practices, naming-conventions
- **Path**: `~/.claude/plugins/marketplaces/sf-skills/sf-metadata/docs/`

**Dependencies**: sf-deploy (optional) for deployment. Install: `/plugin install github:Jaganpro/sf-skills/sf-deploy`

**Notes**: API 65.0 required | Permission Sets over Profiles | Block if score < 72

---

## Validation

**Manual validation** (if hooks don't fire):
```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-metadata/hooks/scripts/validate_metadata.py <file_path>
```

**Scoring**: 120 points / 6 categories. Minimum 84 (70%) for deployment.

**Hooks not firing?** Check: `CLAUDE_PLUGIN_ROOT` set, hooks.json valid, Python 3 in PATH, file matches pattern.

---

## 🔑 Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| FLS is the Silent Killer | Deployed fields invisible without FLS | Always prompt for Permission Set generation |
| Required Fields ≠ Permission Sets | Salesforce rejects required fields in PS | Filter out required fields from fieldPermissions |
| Orchestration Order | sf-data fails if objects not deployed | sf-metadata → sf-flow → sf-deploy → sf-data |
| Before-Save Efficiency | Before-Save auto-saves, no DML needed | Use Before-Save for same-record updates |
| Test with 251 Records | Batch boundary at 200 records | Always bulk test with 251+ records |

## Common Errors

| Error | Fix |
|-------|-----|
| `Cannot deploy to required field` | Remove from fieldPermissions (auto-visible) |
| `Field does not exist` | Create Permission Set with field access |
| `SObject type 'X' not supported` | Deploy metadata first |
| `Element X is duplicated` | Reorder XML elements alphabetically |

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
