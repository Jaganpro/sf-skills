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
---

# sf-metadata: Salesforce Metadata Generation and Org Querying

Expert Salesforce administrator specializing in metadata architecture, security model design, and schema best practices. Generate production-ready metadata XML and query org structures using sf CLI v2.

## Core Responsibilities

1. **Metadata Generation**: Create Custom Objects, Fields, Profiles, Permission Sets, Validation Rules, Record Types, Page Layouts
2. **Org Querying**: Describe objects, list fields, query metadata using sf CLI v2
3. **Validation & Scoring**: Score metadata against 6 categories (0-120 points)
4. **Cross-Skill Integration**: Provide metadata discovery for sf-apex and sf-flow
5. **Deployment Integration**: Deploy metadata via sf-deploy skill

## Document Map

| Need | Document | Description |
|------|----------|-------------|
| **PermSet auto-gen** | [references/permset-auto-generation.md](references/permset-auto-generation.md) | Phase 3.5 rules, field type filters, XML example |
| **Scoring details** | [references/best-practices-scoring.md](references/best-practices-scoring.md) | 6-category breakdown, field template tips |
| **Field & CLI ref** | [references/field-and-cli-reference.md](references/field-and-cli-reference.md) | Field types, relationships, validation patterns, CLI commands |
| **Naming** | [references/naming-conventions.md](references/naming-conventions.md) | API name conventions |
| **Orchestration** | [references/orchestration.md](references/orchestration.md) | Extended orchestration patterns |

---

## CRITICAL: Orchestration Order

**sf-metadata → sf-flow → sf-deploy → sf-data** (you are here: sf-metadata)

sf-data requires objects deployed to org. Always deploy BEFORE creating test data.

---

## CRITICAL: Field-Level Security

**Deployed fields are INVISIBLE until FLS is configured!** Always prompt for Permission Set generation after creating objects/fields. See [references/permset-auto-generation.md](references/permset-auto-generation.md) for auto-generation workflow.

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Operation type: **Generate** metadata OR **Query** org metadata
- If generating: Metadata type, target object, specific requirements
- If querying: Query type, target org alias, object name or metadata type

**Then**: Check existing metadata (`Glob: **/*-meta.xml`), verify sfdx-project.json exists.

### Phase 2: Template Selection / Query Execution

#### For Generation

| Metadata Type | Template |
|---------------|----------|
| Custom Object | `assets/objects/custom-object.xml` |
| Text/Number/Currency/Date/Checkbox Field | `assets/fields/[type]-field.xml` |
| Picklist / Multi-Select Picklist | `assets/fields/picklist-field.xml` / `multi-select-picklist.xml` |
| Lookup / Master-Detail | `assets/fields/lookup-field.xml` / `master-detail-field.xml` |
| Formula / Roll-Up Summary | `assets/fields/formula-field.xml` / `rollup-summary-field.xml` |
| Email/Phone/URL/Text Area | `assets/fields/[type]-field.xml` |
| Profile / Permission Set | `assets/profiles/profile.xml` / `assets/permission-sets/permission-set.xml` |
| Validation Rule / Record Type / Layout | `assets/[type]/` |

**Template Path Resolution** (try in order):
1. Marketplace: `~/.claude/plugins/marketplaces/sf-skills/sf-metadata/assets/[path]`
2. Project: `[project-root]/sf-metadata/assets/[path]`

#### For Querying (sf CLI v2)

| Query Type | Command |
|------------|---------|
| Describe object | `sf sobject describe --sobject [Name] --target-org [alias] --json` |
| List custom objects | `sf org list metadata --metadata-type CustomObject --target-org [alias] --json` |
| List metadata types | `sf org list metadata-types --target-org [alias] --json` |

> See [references/field-and-cli-reference.md](references/field-and-cli-reference.md) for complete CLI commands and interactive generation.

### Phase 3: Generation / Validation

**File locations**:
- Objects: `force-app/main/default/objects/[ObjectName__c]/[ObjectName__c].object-meta.xml`
- Fields: `force-app/main/default/objects/[ObjectName]/fields/[FieldName__c].field-meta.xml`
- Permission Sets: `force-app/main/default/permissionsets/[PermSetName].permissionset-meta.xml`
- Validation Rules: `force-app/main/default/objects/[ObjectName]/validationRules/[RuleName].validationRule-meta.xml`

**Validation Report Format**:
```
Score: 105/120 ⭐⭐⭐⭐ Very Good
├─ Structure & Format:  20/20 (100%)
├─ Naming Conventions:  18/20 (90%)
├─ Data Integrity:      15/20 (75%)
├─ Security & FLS:      20/20 (100%)
├─ Documentation:       18/20 (90%)
└─ Best Practices:      14/20 (70%)
```

> See [references/best-practices-scoring.md](references/best-practices-scoring.md) for detailed category breakdowns and field template tips.

### Phase 3.5: Permission Set Auto-Generation

> See [references/permset-auto-generation.md](references/permset-auto-generation.md) for the complete workflow, field type rules, and XML template.

**Quick rules**: Exclude required fields (auto-visible) and Name fields. Formula/Roll-Up fields get `editable: false`. Master-Detail controlled by parent.

### Phase 4: Deployment

```
Skill(skill="sf-deploy", args="Deploy metadata at force-app/main/default/objects/[ObjectName] to [target-org]")
```

Post-deployment: `sf org assign permset --name [ObjectName]_Access --target-org [alias]`

### Phase 5: Verification

Verify in Setup → Object Manager, check FLS for new fields, add to Page Layouts if needed.

---

## Scoring (120 Points)

> See [references/best-practices-scoring.md](references/best-practices-scoring.md) for full criteria.

**Categories**: Structure & Format (20), Naming Conventions (20), Data Integrity (20), Security & FLS (20), Documentation (20), Best Practices (20).

**Thresholds**: 108+ Excellent | 96+ Good | 84+ Acceptable | <72 BLOCKED

---

## Cross-Skill Integration

| From Skill | To sf-metadata | When |
|------------|----------------|------|
| sf-apex | → sf-metadata | "Describe Invoice__c" (discover fields before coding) |
| sf-flow | → sf-metadata | "Describe object fields, record types, validation rules" |
| sf-data | → sf-metadata | "Describe Custom_Object__c fields" (discover structure) |

| From sf-metadata | To Skill | When |
|------------------|----------|------|
| sf-metadata | → sf-deploy | "Deploy with --dry-run" |
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
| No description on custom objects | Always document purpose |

---

## Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| FLS is the Silent Killer | Deployed fields invisible without FLS | Always prompt for Permission Set generation |
| Required Fields ≠ Permission Sets | Salesforce rejects required fields in PS | Filter out required fields from fieldPermissions |
| Orchestration Order | sf-data fails if objects not deployed | sf-metadata → sf-flow → sf-deploy → sf-data |

## Common Errors

| Error | Fix |
|-------|-----|
| `Cannot deploy to required field` | Remove from fieldPermissions (auto-visible) |
| `Field does not exist` | Create Permission Set with field access |
| `SObject type 'X' not supported` | Deploy metadata first |
| `Element X is duplicated` | Reorder XML elements alphabetically |

---

## Validation

```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-metadata/hooks/scripts/validate_metadata.py <file_path>
```

**Scoring**: 120 points / 6 categories. Minimum 84 (70%) for deployment.

---

## Dependencies

**Docs**: `references/` folder — metadata-types-reference, field-types-guide, fls-best-practices, naming-conventions
**Required**: sf-deploy (optional) for deployment | API 65.0 | Block if score < 72
