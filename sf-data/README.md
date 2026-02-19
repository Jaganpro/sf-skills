# sf-data

Salesforce data operations skill for Claude Code. Provides SOQL expertise, test data factories, bulk operations, and comprehensive validation with 130-point scoring.

## Features

- **CRUD Operations**: Create, read, update, delete records via sf CLI
- **SOQL Expertise**: Complex relationship queries, polymorphic fields, aggregations
- **Test Data Factories**: Bulk-ready Apex factories for standard objects
- **Bulk Operations**: Import/export via Bulk API 2.0
- **Record Tracking & Cleanup**: Savepoint/rollback, cleanup scripts
- **130-Point Validation**: Automated scoring across 7 categories

## Installation

```bash
/plugin install github:Jaganpro/sf-skills/sf-data
```

Or install the complete sf-skills suite:
```bash
/plugin install github:Jaganpro/sf-skills
```

## Usage

Invoke the skill:
```
Skill(skill="sf-data")
Request: "Create 251 test Account records with varying Industries for trigger testing in org dev"
```

### Common Operations

| Operation | Example Request |
|-----------|-----------------|
| Query | "Query all Accounts with related Contacts in org dev" |
| Create | "Create 10 test Opportunities at various stages" |
| Bulk Insert | "Insert 500 accounts from accounts.csv" |
| Update | "Update Account 001xxx with new Industry" |
| Delete | "Delete all test records with Name LIKE 'Test%'" |
| Cleanup | "Generate cleanup script for all records created today" |

## Validation Scoring (130 Points)

| Category | Points | Focus |
|----------|--------|-------|
| Query Efficiency | 25 | SOQL selectivity, indexed fields, no N+1 |
| Bulk Safety | 25 | Governor limits, batch sizing |
| Data Integrity | 20 | Required fields, relationships |
| Security & FLS | 20 | Field-level security, no PII |
| Test Patterns | 15 | 200+ records, edge cases |
| Cleanup & Isolation | 15 | Rollback, cleanup scripts |
| Documentation | 10 | Purpose, expected outcomes |

## Cross-Skill Integration

### With sf-metadata
```
Skill(skill="sf-metadata")
Request: "Describe Invoice__c in org dev - show all fields"
```
Then use sf-data with accurate field names.

### From sf-apex / sf-flow
```
Skill(skill="sf-data")
Request: "Create 251 test Accounts to trigger AccountTrigger bulk testing"
```

## Directory Structure

```
sf-data/
├── SKILL.md                   # Main skill prompt
├── assets/
│   ├── factories/             # Apex test data factories
│   ├── soql/                  # SOQL query templates
│   ├── bulk/                  # Bulk operation templates
│   ├── csv/                   # CSV import templates
│   ├── json/                  # JSON tree templates
│   └── cleanup/               # Cleanup scripts
├── hooks/                     # Validation hooks
├── references/                      # Documentation
└── references/                  # Usage examples
```

## sf CLI Commands Wrapped

| Operation | Command |
|-----------|---------|
| Query | `sf data query --query "..." --target-org [alias]` |
| Create | `sf data create record --sobject [Object] --values "..."` |
| Update | `sf data update record --sobject [Object] --record-id [Id] --values "..."` |
| Delete | `sf data delete record --sobject [Object] --record-id [Id]` |
| Bulk Import | `sf data import bulk --file [csv] --sobject [Object]` |
| Bulk Delete | `sf data delete bulk --file [csv] --sobject [Object]` |
| Tree Export | `sf data export tree --query "..." --output-dir [dir]` |
| Tree Import | `sf data import tree --files [json]` |
| Apex Run | `sf apex run --file [script.apex]` |

## Requirements

- sf CLI v2
- Target Salesforce org (sandbox or production)
- Claude Code with skill plugins enabled

## License

MIT License. See LICENSE file.
Copyright (c) 2024-2025 Jag Valaiyapathy
