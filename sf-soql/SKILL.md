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
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org --json

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

**Scoring Thresholds**: 90-100 = Production-optimized, 80-89 = Good (minor optimizations possible), 70-79 = Performance concerns, <70 = Needs improvement.

---

## Quick Reference

### Security (Always Apply)

```sql
-- Enforce FLS (throws exception on inaccessible fields)
SELECT Id, Name, Phone FROM Account WITH SECURITY_ENFORCED

-- Respect sharing rules
SELECT Id, Name FROM Account WITH USER_MODE
```

> See [references/query-optimization.md](references/query-optimization.md) for `stripInaccessible` in Apex, `SYSTEM_MODE`, governor limits, SOQL FOR loops, indexing strategy, and selectivity rules.

### Governor Limits (Key Numbers)

| Limit | Synchronous | Asynchronous |
|-------|-------------|--------------|
| Total SOQL Queries | 100 | 200 |
| Records Retrieved | 50,000 | 50,000 |

> **Anti-pattern**: Never query inside a loop. Use `Map<Id, SObject>` with `WHERE Id IN :idSet` instead.

---

## SOQL Syntax, Relationships & Aggregates

> See [references/soql-syntax-reference.md](references/soql-syntax-reference.md) for the complete reference including: basic query structure, WHERE operators, date literals, child-to-parent dot notation, parent-to-child subqueries, relationship names, aggregate functions (COUNT, SUM, AVG, GROUP BY, HAVING, ROLLUP), polymorphic queries (TYPEOF), semi-joins, and anti-joins.

**Key patterns:**
- **Child-to-Parent**: `SELECT Contact.Account.Name FROM Case` (up to 5 levels)
- **Parent-to-Child**: `SELECT Id, (SELECT Id FROM Contacts) FROM Account`
- **Custom relationships**: Use `__r` suffix (e.g., `Custom_Object__r.Name`)
- **Aggregates**: `SELECT Industry, COUNT(Id) FROM Account GROUP BY Industry HAVING COUNT(Id) > 10`

## Query Optimization

> See [references/query-optimization.md](references/query-optimization.md) for indexing strategy, selectivity rules, optimization patterns, query plan analysis, and efficient Apex patterns.

**Key rules:**
- Use indexed fields in WHERE (Id, Name, CreatedDate, Email, External IDs)
- Trailing wildcards use indexes (`LIKE 'Acme%'`), leading wildcards don't (`LIKE '%corp'`)
- Filter in SOQL, not in Apex — use `LIMIT` appropriate to use case
- Use `sf data query --plan` to analyze query cost

---

## Natural Language Examples

| Request | SOQL |
|---------|------|
| "Get me all accounts" | `SELECT Id, Name FROM Account LIMIT 1000` |
| "Find contacts without email" | `SELECT Id, Name FROM Contact WHERE Email = null` |
| "Top 10 opportunities by amount" | `SELECT Id, Name, Amount FROM Opportunity ORDER BY Amount DESC LIMIT 10` |
| "Contacts with @gmail emails" | `SELECT Id, Name, Email FROM Contact WHERE Email LIKE '%@gmail.com'` |
| "Opportunities closing this quarter" | `SELECT Id, Name, CloseDate FROM Opportunity WHERE CloseDate = THIS_QUARTER` |
| "Total revenue by industry" | `SELECT Industry, SUM(AnnualRevenue) FROM Account GROUP BY Industry` |

---

## CLI Commands

```bash
# Basic query (JSON output)
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org --json

# CSV output to file
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --result-format csv --output-file accounts.csv

# Bulk export (> 2,000 records)
sf data export bulk --query "SELECT Id, Name FROM Account" --target-org my-org --output-file accounts.csv

# SOSL search
sf data search --query "FIND {Acme} IN ALL FIELDS RETURNING Account(Id, Name), Contact(Id, Name)" --target-org my-org
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

## Document Map

### References (Extracted)
| Document | Description |
|----------|-------------|
| [SOQL Syntax Reference](references/soql-syntax-reference.md) | Complete syntax, operators, dates, relationships, aggregates, advanced features |
| [Query Optimization](references/query-optimization.md) | Indexing, selectivity, patterns, query plan, governor limits, security |

### Docs
| Document | Description |
|----------|-------------|
| [soql-reference.md](docs/soql-reference.md) | Complete SOQL syntax reference |
| [cli-commands.md](docs/cli-commands.md) | SF CLI query commands |
| [anti-patterns.md](docs/anti-patterns.md) | Common mistakes and how to avoid them |
| [selector-patterns.md](docs/selector-patterns.md) | Query abstraction patterns (vanilla Apex) |
| [field-coverage-rules.md](docs/field-coverage-rules.md) | Ensure queries include all accessed fields |

### Templates
| Template | Description |
|----------|-------------|
| [basic-queries.soql](templates/basic-queries.soql) | Basic SOQL syntax examples |
| [aggregate-queries.soql](templates/aggregate-queries.soql) | COUNT, SUM, GROUP BY patterns |
| [relationship-queries.soql](templates/relationship-queries.soql) | Parent-child traversals |
| [optimization-patterns.soql](templates/optimization-patterns.soql) | Selectivity and indexing |
| [selector-class.cls](templates/selector-class.cls) | Selector class template |
| [bulkified-query-pattern.cls](templates/bulkified-query-pattern.cls) | Map-based bulk lookups |

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated

**Recommended**: sf-debug (for query plan analysis), sf-apex (for embedding in Apex code)

---

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments of community resources that shaped this skill.
