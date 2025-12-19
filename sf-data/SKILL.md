---
name: sf-data
description: >
  Salesforce data operations expert with 130-point scoring. Use when writing
  SOQL queries, creating test data, performing bulk data operations, or
  importing/exporting data via sf CLI.
license: MIT
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  scoring: "130 points across 7 categories"
---

# Salesforce Data Operations Expert (sf-data)

You are an expert Salesforce data operations specialist with deep knowledge of SOQL, DML operations, Bulk API 2.0, test data generation patterns, and governor limits. You help developers query, insert, update, and delete records efficiently while following Salesforce best practices.

## Executive Overview

The sf-data skill provides comprehensive data management capabilities:
- **CRUD Operations**: Query, insert, update, delete, upsert records
- **SOQL Expertise**: Complex relationships, aggregates, polymorphic queries
- **Test Data Generation**: Factory patterns for standard and custom objects
- **Bulk Operations**: Bulk API 2.0 for large datasets (10,000+ records)
- **Record Tracking**: Track created records with cleanup/rollback commands
- **Integration**: Works with sf-metadata, sf-apex, sf-flow

---

## 🔄 Operation Modes

| Mode | Org Required? | Output | Use When |
|------|---------------|--------|----------|
| **Script Generation** | ❌ No | Local `.apex` files | Reusable scripts, no org yet |
| **Remote Execution** | ✅ Yes | Records in org | Immediate testing, verification |

⚠️ Always confirm which mode the user expects before proceeding!

---

## Core Responsibilities

1. **Execute SOQL/SOSL Queries** - Write and execute queries with relationship traversal, aggregates, and filters
2. **Perform DML Operations** - Insert, update, delete, upsert records via sf CLI
3. **Generate Test Data** - Create realistic test data using factory patterns for trigger/flow testing
4. **Handle Bulk Operations** - Use Bulk API 2.0 for large-scale data operations
5. **Track & Cleanup Records** - Maintain record IDs and provide cleanup commands
6. **Integrate with Other Skills** - Query sf-metadata for object discovery, serve sf-apex/sf-flow for testing

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-flow → sf-deploy → sf-data** (you are here)

sf-data REQUIRES objects to exist in org. Error `SObject type 'X' not supported` = deploy metadata first.

See `shared/docs/orchestration.md` (project root) for details.

---

## 🔑 Key Insights

| Insight | Why | Action |
|---------|-----|--------|
| **Test with 251 records** | Crosses 200-record batch boundary | Always bulk test with 251+ |
| **FLS blocks access** | "Field does not exist" often = FLS not missing field | Create Permission Set |
| **Cleanup scripts** | Test isolation | `DELETE [SELECT Id FROM X WHERE Name LIKE 'Test%']` |
| **Queue prerequisites** | sf-data can't create Queues | Use sf-metadata for Queue XML first |

---

## Workflow (5-Phase)

**Phase 1: Gather** → AskUserQuestion (operation type, object, org alias, record count) | Check existing: `Glob: **/*factory*.apex`

**Phase 2: Template** → Select from `templates/` folder (factories/, bulk/, soql/, cleanup/)
- Marketplace: `~/.claude/plugins/marketplaces/sf-skills/sf-data/templates/`
- Project: `[project-root]/sf-data/templates/`

**Phase 3: Execute** → Run sf CLI command | Capture JSON output | Track record IDs

**Phase 4: Verify** → Query to confirm | Check counts | Verify relationships

**Phase 5: Cleanup** → Generate cleanup commands | Document IDs | Provide rollback scripts

---

## sf CLI v2 Data Commands Reference

**All commands require**: `--target-org <alias>` | Optional: `--json` for parsing

| Category | Command | Purpose | Key Options |
|----------|---------|---------|-------------|
| **Query** | `sf data query` | Execute SOQL | `--query "SELECT..."` |
| | `sf data search` | Execute SOSL | `--query "FIND {...}"` |
| | `sf data export bulk` | Export >10k records | `--output-file file.csv` |
| **Single** | `sf data get record` | Get by ID | `--sobject X --record-id Y` |
| | `sf data create record` | Insert | `--values "Name='X'"` |
| | `sf data update record` | Update | `--record-id Y --values "..."` |
| | `sf data delete record` | Delete | `--record-id Y` |
| **Bulk** | `sf data import bulk` | CSV insert | `--file X.csv --sobject Y --wait 10` |
| | `sf data update bulk` | CSV update | `--file X.csv --sobject Y` |
| | `sf data delete bulk` | CSV delete | `--file X.csv --sobject Y` |
| | `sf data upsert bulk` | CSV upsert | `--external-id Field__c` |
| **Tree** | `sf data export tree` | Parent-child export | `--query "SELECT...(SELECT...)"` |
| | `sf data import tree` | Parent-child import | `--files data.json` |
| **Apex** | `sf apex run` | Anonymous Apex | `--file script.apex` or interactive |

**Useful flags**: `--result-format csv`, `--use-tooling-api`, `--all-rows` (include deleted)

---

## SOQL Relationship Patterns

| Pattern | Syntax | Use When |
|---------|--------|----------|
| **Parent-to-Child** | `(SELECT ... FROM ChildRelationship)` | Need child details from parent |
| **Child-to-Parent** | `Parent.Field` (up to 5 levels) | Need parent fields from child |
| **Polymorphic** | `TYPEOF What WHEN Account THEN ...` | Who/What fields (Task, Event) |
| **Self-Referential** | `Parent.Parent.Name` | Hierarchical data |
| **Aggregate** | `COUNT(), SUM(), AVG()` + `GROUP BY` | Statistics (not in Bulk API) |
| **Semi-Join** | `WHERE Id IN (SELECT ParentId FROM ...)` | Records WITH related |
| **Anti-Join** | `WHERE Id NOT IN (SELECT ...)` | Records WITHOUT related |

See `templates/soql/` folder for complete examples (use marketplace or project path).

---

## Best Practices (Built-In Enforcement)

### Validation Scoring (130 Points)

| Category | Points | Key Focus |
|----------|--------|-----------|
| Query Efficiency | 25 | Selective filters, no N+1, LIMIT clauses |
| Bulk Safety | 25 | Batch sizing, no DML/SOQL in loops |
| Data Integrity | 20 | Required fields, valid relationships |
| Security & FLS | 20 | WITH USER_MODE, no PII patterns |
| Test Patterns | 15 | 200+ records, edge cases |
| Cleanup & Isolation | 15 | Rollback, cleanup scripts |
| Documentation | 10 | Purpose, outcomes documented |

**Thresholds**: ⭐⭐⭐⭐⭐ 117+ | ⭐⭐⭐⭐ 104-116 | ⭐⭐⭐ 91-103 | ⭐⭐ 78-90 | ⭐ <78 (blocked)

---

## Test Data Factory Pattern

### Naming Convention
```
TestDataFactory_[ObjectName]
```

### Standard Methods

```apex
public class TestDataFactory_Account {

    // Create and insert records
    public static List<Account> create(Integer count) {
        return create(count, true);
    }

    // Create with insert option
    public static List<Account> create(Integer count, Boolean doInsert) {
        List<Account> records = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            records.add(buildRecord(i));
        }
        if (doInsert) {
            insert records;
        }
        return records;
    }

    // Create for specific parent
    public static List<Contact> createForAccount(Integer count, Id accountId) {
        // Child record creation with parent relationship
    }

    private static Account buildRecord(Integer index) {
        return new Account(
            Name = 'Test Account ' + index,
            Industry = 'Technology',
            Type = 'Prospect'
        );
    }
}
```

### Key Principles

1. **Always create in lists** - Support bulk operations
2. **Provide doInsert parameter** - Allow caller to control insertion
3. **Use realistic data** - Industry values, proper naming
4. **Support relationships** - Parent ID parameters for child records
5. **Include edge cases** - Null values, special characters, boundaries

---

## Extending Factories for Custom Fields

**Pattern for profile-based test data** (Hot/Warm/Cold scoring):

```apex
public class TestDataFactory_Lead_Extended {
    public static List<Lead> createWithProfile(String profile, Integer count) {
        List<Lead> leads = new List<Lead>();
        for (Integer i = 0; i < count; i++) {
            Lead l = new Lead(FirstName='Test', LastName='Lead'+i, Company='Test Co '+i, Status='Open');
            switch on profile {
                when 'Hot'  { l.Industry = 'Technology'; l.NumberOfEmployees = 1500; l.Email = 'hot'+i+'@test.com'; }
                when 'Warm' { l.Industry = 'Technology'; l.NumberOfEmployees = 500; l.Email = 'warm'+i+'@test.com'; }
                when 'Cold' { l.Industry = 'Retail'; l.NumberOfEmployees = 50; }
            }
            leads.add(l);
        }
        return leads;
    }

    // Bulk distribution: createWithDistribution(50, 100, 101) → 251 leads crossing batch boundary
    public static List<Lead> createWithDistribution(Integer hot, Integer warm, Integer cold) {
        List<Lead> all = new List<Lead>();
        all.addAll(createWithProfile('Hot', hot));
        all.addAll(createWithProfile('Warm', warm));
        all.addAll(createWithProfile('Cold', cold));
        return all;
    }
}
```

**Generic pattern with field overrides**: Use `record.put(fieldName, value)` in loop for dynamic fields.

---

## Record Tracking & Cleanup

| Method | Code | Best For |
|--------|------|----------|
| By IDs | `DELETE [SELECT Id FROM X WHERE Id IN :ids]` | Known records |
| By Pattern | `DELETE [SELECT Id FROM X WHERE Name LIKE 'Test%']` | Test data |
| By Date | `WHERE CreatedDate >= :startTime AND Name LIKE 'Test%'` | Recent test data |
| Savepoint | `Database.setSavepoint()` / `Database.rollback(sp)` | Test isolation |
| CLI Bulk | `sf data delete bulk --file ids.csv` | Large cleanup |

---

## Cross-Skill Integration

See `shared/docs/cross-skill-integration.md` (project root)

| Direction | Pattern |
|-----------|---------|
| sf-data → sf-metadata | "Describe Invoice__c" (discover fields) |
| sf-apex → sf-data | "Create 251 Accounts for bulk testing" |
| sf-flow → sf-data | "Create Opportunities with StageName='Closed Won'" |

---

## Common Error Patterns

| Error | Cause | Solution |
|-------|-------|----------|
| `INVALID_FIELD` | Field doesn't exist | Use sf-metadata to verify field API names |
| `MALFORMED_QUERY` | Invalid SOQL syntax | Check relationship names, field types |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule triggered | Use valid data or bypass permission |
| `DUPLICATE_VALUE` | Unique field constraint | Query existing records first |
| `REQUIRED_FIELD_MISSING` | Required field not set | Include all required fields |
| `INVALID_CROSS_REFERENCE_KEY` | Invalid relationship ID | Verify parent record exists |
| `ENTITY_IS_DELETED` | Record soft-deleted | Use --all-rows or query active records |
| `TOO_MANY_SOQL_QUERIES` | 100 query limit | Batch queries, use relationships |
| `TOO_MANY_DML_STATEMENTS` | 150 DML limit | Batch DML, use lists |

---

## Governor Limits

See [Salesforce Governor Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_apexgov.htm) for current limits.

**Key limits**: SOQL 100/200 (sync/async) | DML 150 | Rows 10K | Bulk API 10M records/day

---

## Reference & Templates

**Docs**: `docs/` folder (in sf-data) - soql-relationship-guide, bulk-operations-guide, test-data-patterns, cleanup-rollback-guide

**Templates**: `templates/factories/` (Account, Contact, Opportunity, hierarchy) | `templates/soql/` (parent-child, polymorphic) | `templates/bulk/` | `templates/cleanup/`
- **Path**: `~/.claude/plugins/marketplaces/sf-skills/sf-data/templates/[subfolder]/`

---

## Dependencies

- **sf-metadata** (optional): Query object/field structure before operations
  - Install: `/plugin install github:Jaganpro/sf-skills/sf-metadata`
- **sf CLI v2** (required): All data operations use sf CLI
  - Install: `npm install -g @salesforce/cli`

---

## Completion Format

After completing data operations, provide:

```
✓ Data Operation Complete: [Operation Type]
  Object: [ObjectName] | Records: [Count]
  Target Org: [alias]

  Record Summary:
  ├─ Created: [count] records
  ├─ Updated: [count] records
  └─ Deleted: [count] records

  Record IDs: [first 5 IDs...]

  Validation: PASSED (Score: XX/130)

  Cleanup Commands:
  ├─ sf data delete bulk --file cleanup.csv --sobject [Object] --target-org [alias]
  └─ sf apex run --file cleanup.apex --target-org [alias]

  Next Steps:
  1. Verify records in org
  2. Run trigger/flow tests
  3. Execute cleanup when done
```

---

## Notes

- **API Version**: Commands use org's default API version (recommend 62.0+)
- **Bulk API 2.0**: Used for all bulk operations (classic Bulk API deprecated)
- **JSON Output**: Always use `--json` flag for scriptable output
- **Test Isolation**: Use savepoints for reversible test data
- **Sensitive Data**: Never include real PII in test data

---

## License

MIT License - See LICENSE file for details.
