---
name: sf-soql
description: >
  Advanced SOQL skill with natural language to query generation, query optimization,
  relationship traversal, aggregate functions, and performance analysis. Build efficient
  queries that respect governor limits and security requirements.
license: MIT
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 5 categories"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/post-tool-validate.py"
          timeout: 10000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-soql"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-soql"
      timeout: 5000
---

# sf-soql: Salesforce SOQL Query Expert

Expert database engineer specializing in Salesforce Object Query Language (SOQL). Generate optimized queries from natural language, analyze query performance, and ensure best practices for governor limits and security.

## Core Responsibilities

1. **Natural Language → SOQL**: Convert plain English requests to optimized queries
2. **Query Optimization**: Analyze and improve query performance
3. **Relationship Queries**: Build parent-child and child-parent traversals
4. **Aggregate Functions**: COUNT, SUM, AVG, MIN, MAX with GROUP BY
5. **Security Enforcement**: Ensure FLS and sharing rules compliance
6. **Governor Limit Awareness**: Design queries within limits

## Workflow (4-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- What data is needed (objects, fields)
- Filter criteria (WHERE conditions)
- Sort requirements (ORDER BY)
- Record limit requirements
- Use case (display, processing, reporting)

### Phase 2: Query Generation

**Natural Language Examples**:

| Request | Generated SOQL |
|---------|----------------|
| "Get all active accounts with their contacts" | `SELECT Id, Name, (SELECT Id, Name FROM Contacts) FROM Account WHERE IsActive__c = true` |
| "Find contacts created this month" | `SELECT Id, Name, Email FROM Contact WHERE CreatedDate = THIS_MONTH` |
| "Count opportunities by stage" | `SELECT StageName, COUNT(Id) FROM Opportunity GROUP BY StageName` |
| "Get accounts with revenue over 1M sorted by name" | `SELECT Id, Name, AnnualRevenue FROM Account WHERE AnnualRevenue > 1000000 ORDER BY Name` |

### Phase 3: Optimization

**Query Optimization Checklist**:

1. **Selectivity**: Does WHERE clause use indexed fields?
2. **Field Selection**: Only query needed fields (not SELECT *)
3. **Limit**: Is LIMIT appropriate for use case?
4. **Relationship Depth**: Avoid deep traversals (max 5 levels)
5. **Aggregate Queries**: Use for counts instead of loading all records

### Phase 4: Validation & Execution

```bash
# Test query
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org

# Analyze query plan
sf data query --query "..." --target-org my-org --use-tooling-api --plan
```

---

## Best Practices (100-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Selectivity** | 25 | Indexed fields in WHERE, selective filters |
| **Performance** | 25 | Appropriate LIMIT, minimal fields, no unnecessary joins |
| **Security** | 20 | WITH SECURITY_ENFORCED or stripInaccessible |
| **Correctness** | 15 | Proper syntax, valid field references |
| **Readability** | 15 | Formatted, meaningful aliases, comments |

**Scoring Thresholds**:
```
⭐⭐⭐⭐⭐ 90-100 pts → Production-optimized query
⭐⭐⭐⭐   80-89 pts  → Good query, minor optimizations possible
⭐⭐⭐    70-79 pts   → Functional, performance concerns
⭐⭐      60-69 pts   → Basic query, needs improvement
⭐        <60 pts    → Problematic query
```

---

## SOQL Reference

### Basic Query Structure

```sql
SELECT field1, field2, ...
FROM ObjectName
WHERE condition1 AND condition2
ORDER BY field1 ASC/DESC
LIMIT number
OFFSET number
```

### Field Selection

```sql
-- Specific fields (recommended)
SELECT Id, Name, Industry FROM Account

-- All fields (avoid in Apex - use only in Developer Console)
SELECT FIELDS(ALL) FROM Account LIMIT 200

-- Standard fields only
SELECT FIELDS(STANDARD) FROM Account
```

### WHERE Clause Operators

| Operator | Example | Notes |
|----------|---------|-------|
| `=` | `Name = 'Acme'` | Exact match |
| `!=` | `Status != 'Closed'` | Not equal |
| `<`, `>`, `<=`, `>=` | `Amount > 1000` | Comparison |
| `LIKE` | `Name LIKE 'Acme%'` | Wildcard match |
| `IN` | `Status IN ('New', 'Open')` | Multiple values |
| `NOT IN` | `Type NOT IN ('Other')` | Exclude values |
| `INCLUDES` | `Interests__c INCLUDES ('Golf')` | Multi-select picklist |
| `EXCLUDES` | `Interests__c EXCLUDES ('Golf')` | Multi-select exclude |

### Date Literals

| Literal | Meaning |
|---------|---------|
| `TODAY` | Current day |
| `YESTERDAY` | Previous day |
| `THIS_WEEK` | Current week (Sun-Sat) |
| `LAST_WEEK` | Previous week |
| `THIS_MONTH` | Current month |
| `LAST_MONTH` | Previous month |
| `THIS_QUARTER` | Current quarter |
| `THIS_YEAR` | Current year |
| `LAST_N_DAYS:n` | Last n days |
| `NEXT_N_DAYS:n` | Next n days |

```sql
-- Created in last 30 days
SELECT Id FROM Account WHERE CreatedDate = LAST_N_DAYS:30

-- Modified this month
SELECT Id FROM Contact WHERE LastModifiedDate = THIS_MONTH
```

---

## Relationship Queries

### Child-to-Parent (Dot Notation)

```sql
-- Access parent fields
SELECT Id, Name, Account.Name, Account.Industry
FROM Contact
WHERE Account.AnnualRevenue > 1000000

-- Up to 5 levels
SELECT Id, Contact.Account.Owner.Manager.Name
FROM Case
```

### Parent-to-Child (Subquery)

```sql
-- Get parent with related children
SELECT Id, Name,
       (SELECT Id, FirstName, LastName FROM Contacts),
       (SELECT Id, Name, Amount FROM Opportunities WHERE StageName = 'Closed Won')
FROM Account
WHERE Industry = 'Technology'
```

### Relationship Names

| Object | Relationship Name | Example |
|--------|-------------------|---------|
| Account → Contacts | `Contacts` | `(SELECT Id FROM Contacts)` |
| Account → Opportunities | `Opportunities` | `(SELECT Id FROM Opportunities)` |
| Account → Cases | `Cases` | `(SELECT Id FROM Cases)` |
| Contact → Cases | `Cases` | `(SELECT Id FROM Cases)` |
| Opportunity → OpportunityLineItems | `OpportunityLineItems` | `(SELECT Id FROM OpportunityLineItems)` |

### Custom Object Relationships

```sql
-- Custom relationship: add __r suffix
SELECT Id, Name, Custom_Object__r.Name
FROM Another_Object__c

-- Child relationship: add __r suffix
SELECT Id, (SELECT Id FROM Custom_Children__r)
FROM Parent_Object__c
```

---

## Aggregate Queries

### Basic Aggregates

```sql
-- Count all records
SELECT COUNT() FROM Account

-- Count with alias
SELECT COUNT(Id) cnt FROM Account

-- Sum, Average, Min, Max
SELECT SUM(Amount), AVG(Amount), MIN(Amount), MAX(Amount)
FROM Opportunity
WHERE StageName = 'Closed Won'
```

### GROUP BY

```sql
-- Count by field
SELECT Industry, COUNT(Id)
FROM Account
GROUP BY Industry

-- Multiple groupings
SELECT StageName, CALENDAR_YEAR(CloseDate), COUNT(Id)
FROM Opportunity
GROUP BY StageName, CALENDAR_YEAR(CloseDate)
```

### HAVING Clause

```sql
-- Filter aggregated results
SELECT Industry, COUNT(Id) cnt
FROM Account
GROUP BY Industry
HAVING COUNT(Id) > 10
```

### GROUP BY ROLLUP

```sql
-- Subtotals
SELECT LeadSource, Rating, COUNT(Id)
FROM Lead
GROUP BY ROLLUP(LeadSource, Rating)
```

---

## Query Optimization

### Indexing Strategy

**Indexed Fields** (Always Selective):
- Id
- Name
- OwnerId
- CreatedDate
- LastModifiedDate
- RecordTypeId
- External ID fields
- Master-Detail relationship fields
- Lookup fields (when unique)

**Standard Indexed Fields by Object**:
- Account: AccountNumber, Site
- Contact: Email
- Lead: Email
- Case: CaseNumber
- Opportunity: -

### Selectivity Rules

```
A filter is selective when it returns:
- < 10% of total records for first 1 million
- < 5% of total records for additional records
- OR uses an indexed field
```

### Optimization Patterns

```sql
-- ❌ NON-SELECTIVE (scans all records)
SELECT Id FROM Lead WHERE Status = 'Open'

-- ✅ SELECTIVE (uses index + selective filter)
SELECT Id FROM Lead
WHERE Status = 'Open'
AND CreatedDate = LAST_N_DAYS:30
LIMIT 10000

-- ❌ LEADING WILDCARD (can't use index)
SELECT Id FROM Account WHERE Name LIKE '%corp'

-- ✅ TRAILING WILDCARD (uses index)
SELECT Id FROM Account WHERE Name LIKE 'Acme%'
```

### Query Plan Analysis

```bash
# Get query plan
sf data query \
  --query "SELECT Id FROM Account WHERE Name = 'Test'" \
  --target-org my-org \
  --use-tooling-api \
  --plan
```

**Plan Output Interpretation**:
- `Cardinality`: Estimated rows returned
- `Cost`: Relative query cost (lower is better)
- `Fields`: Index fields used
- `LeadingOperationType`: How the query starts (Index vs TableScan)

---

## Security Patterns

### WITH SECURITY_ENFORCED

```sql
-- Throws exception if user lacks FLS
SELECT Id, Name, Phone
FROM Account
WITH SECURITY_ENFORCED
```

### WITH USER_MODE / SYSTEM_MODE

```sql
-- Respects sharing rules (default in Apex)
SELECT Id, Name FROM Account WITH USER_MODE

-- Bypasses sharing rules (use with caution)
SELECT Id, Name FROM Account WITH SYSTEM_MODE
```

### In Apex: stripInaccessible

```apex
// Strip inaccessible fields instead of throwing
SObjectAccessDecision decision = Security.stripInaccessible(
    AccessType.READABLE,
    [SELECT Id, Name, SecretField__c FROM Account]
);
List<Account> safeAccounts = decision.getRecords();
```

---

## Governor Limits

| Limit | Synchronous | Asynchronous |
|-------|-------------|--------------|
| Total SOQL Queries | 100 | 200 |
| Records Retrieved | 50,000 | 50,000 |
| Query Rows (queryMore) | 2,000 | 2,000 |
| Query Locator Rows | 10 million | 10 million |

### Efficient Patterns

```sql
-- ❌ Query all, filter in Apex
SELECT Id, Name FROM Account
-- Then filter 50,000 records in Apex

-- ✅ Filter in SOQL
SELECT Id, Name FROM Account
WHERE Industry = 'Technology' AND IsActive__c = true
LIMIT 1000

-- ❌ Multiple queries in loop
for (Contact c : contacts) {
    Account a = [SELECT Name FROM Account WHERE Id = :c.AccountId];
}

-- ✅ Single query with Map
Map<Id, Account> accounts = new Map<Id, Account>(
    [SELECT Id, Name FROM Account WHERE Id IN :accountIds]
);
```

---

## SOQL FOR Loops

```apex
// For large datasets - doesn't load all into heap
for (Account acc : [SELECT Id, Name FROM Account WHERE Industry = 'Technology']) {
    // Process one record at a time
    // Governor: Uses queryMore internally (200 at a time)
}

// With explicit batch size
for (List<Account> accs : [SELECT Id, Name FROM Account]) {
    // Process 200 records at a time
}
```

---

## Advanced Features

### Polymorphic Relationships (What)

```sql
-- Query polymorphic fields
SELECT Id, What.Name, What.Type
FROM Task
WHERE What.Type IN ('Account', 'Opportunity')

-- TYPEOF for conditional fields
SELECT
    TYPEOF What
        WHEN Account THEN Name, Phone
        WHEN Opportunity THEN Name, Amount
    END
FROM Task
```

### Semi-Joins and Anti-Joins

```sql
-- Semi-join: Records that HAVE related records
SELECT Id, Name FROM Account
WHERE Id IN (SELECT AccountId FROM Contact)

-- Anti-join: Records that DON'T HAVE related records
SELECT Id, Name FROM Account
WHERE Id NOT IN (SELECT AccountId FROM Opportunity)
```

### Format in Aggregate Queries

```sql
-- Format currency/date in results
SELECT FORMAT(Amount), FORMAT(CloseDate)
FROM Opportunity
```

### convertCurrency()

```sql
-- Convert to user's currency
SELECT Id, convertCurrency(Amount)
FROM Opportunity
```

---

## CLI Commands

### Execute Query

```bash
# Basic query
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org

# JSON output
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --json

# CSV output
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --result-format csv

# Direct to file
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --result-format csv --output-file accounts.csv
```

### Bulk Data Export

```bash
# For large datasets (> 2,000 records)
sf data export bulk --query "SELECT Id, Name FROM Account" --target-org my-org --output-file accounts.csv
```

### Query Plan

```bash
sf data query \
  --query "SELECT Id FROM Account WHERE Name = 'Test'" \
  --target-org my-org \
  --use-tooling-api \
  --plan
```

---

### SOSL Search

```bash
# For full-text search across objects, use SOSL:
sf data search --query "FIND {Acme} IN ALL FIELDS RETURNING Account(Id, Name), Contact(Id, Name)"  --target-org my-org
```

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-apex | Embed queries in Apex | `Skill(skill="sf-apex", args="Create service with SOQL query for accounts")` |
| sf-data | Execute queries against org | `Skill(skill="sf-data", args="Query active accounts from production")` |
| sf-debug | Analyze query performance | `Skill(skill="sf-debug", args="Analyze slow query in debug logs")` |
| sf-lwc | Generate wire queries | `Skill(skill="sf-lwc", args="Create component with wired account query")` |

---

## Natural Language Examples

| Request | SOQL |
|---------|------|
| "Get me all accounts" | `SELECT Id, Name FROM Account LIMIT 1000` |
| "Find contacts without email" | `SELECT Id, Name FROM Contact WHERE Email = null` |
| "Accounts created by John Smith" | `SELECT Id, Name FROM Account WHERE CreatedBy.Name = 'John Smith'` |
| "Top 10 opportunities by amount" | `SELECT Id, Name, Amount FROM Opportunity ORDER BY Amount DESC LIMIT 10` |
| "Accounts in California" | `SELECT Id, Name FROM Account WHERE BillingState = 'CA'` |
| "Contacts with @gmail emails" | `SELECT Id, Name, Email FROM Contact WHERE Email LIKE '%@gmail.com'` |
| "Opportunities closing this quarter" | `SELECT Id, Name, CloseDate FROM Opportunity WHERE CloseDate = THIS_QUARTER` |
| "Cases opened in last 7 days" | `SELECT Id, Subject FROM Case WHERE CreatedDate = LAST_N_DAYS:7` |
| "Total revenue by industry" | `SELECT Industry, SUM(AnnualRevenue) FROM Account GROUP BY Industry` |
| "Accounts with more than 5 contacts" | `SELECT Id, Name, (SELECT Id FROM Contacts) FROM Account` + filter in Apex |

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated

**Recommended**:
- sf-debug (for query plan analysis)
- sf-apex (for embedding in Apex code)

Install: `/plugin install github:Jaganpro/sf-skills/sf-soql`

---

## Documentation

| Document | Description |
|----------|-------------|
| [soql-reference.md](docs/soql-reference.md) | Complete SOQL syntax reference |
| [cli-commands.md](docs/cli-commands.md) | SF CLI query commands |
| [anti-patterns.md](docs/anti-patterns.md) | Common mistakes and how to avoid them |
| [selector-patterns.md](docs/selector-patterns.md) | Query abstraction patterns (vanilla Apex) |
| [field-coverage-rules.md](docs/field-coverage-rules.md) | **NEW**: Ensure queries include all accessed fields (LLM mistake prevention) |

## Templates

| Template | Description |
|----------|-------------|
| [basic-queries.soql](templates/basic-queries.soql) | Basic SOQL syntax examples |
| [aggregate-queries.soql](templates/aggregate-queries.soql) | COUNT, SUM, GROUP BY patterns |
| [relationship-queries.soql](templates/relationship-queries.soql) | Parent-child traversals |
| [optimization-patterns.soql](templates/optimization-patterns.soql) | Selectivity and indexing |
| [selector-class.cls](templates/selector-class.cls) | Selector class template |
| [bulkified-query-pattern.cls](templates/bulkified-query-pattern.cls) | Map-based bulk lookups |

---

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments of community resources that shaped this skill.

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
