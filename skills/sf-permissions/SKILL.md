---
name: sf-permissions
description: >
  Permission Set analysis, hierarchy viewer, and "Who has X?" auditing.
  Use when analyzing permissions, visualizing PS/PSG hierarchies, or finding
  which Permission Sets grant access to specific objects, fields, or Apex classes.
license: MIT
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  inspiration: "PSLab by Oumaima Arbani (github.com/OumArbani/PSLab)"
---

# sf-permissions

> Salesforce Permission Set analysis, visualization, and auditing tool

## When to Use This Skill

Use `sf-permissions` when the user needs to:
- Visualize Permission Set and Permission Set Group hierarchies
- Find out "who has access to X?" (objects, fields, Apex classes, custom permissions)
- Analyze what permissions a specific user has
- Export Permission Set configurations for auditing
- Generate Permission Set XML metadata
- Grant agent access via `<agentAccesses>` element

## Capabilities

| Capability | Description |
|------------|-------------|
| **Hierarchy Viewer** | Visualize all PS/PSG in an org as ASCII trees |
| **Permission Detector** | Find which PS/PSG grant a specific permission |
| **User Analyzer** | Show all permissions assigned to a user |
| **CSV Exporter** | Export PS configuration for documentation |
| **Metadata Generator** | Generate Permission Set XML (delegates to sf-metadata) |
| **Tooling API** | Query tab settings, system permissions via Tooling API |

## Prerequisites

```bash
pip install simple-salesforce rich  # Python dependencies
sf --version                         # Must be installed and authenticated
sf org display                       # Check current org
```

---

## Phase 1: Understanding the Request

| User Says | Capability | Function |
|-----------|------------|----------|
| "Show permission hierarchy" | Hierarchy Viewer | `hierarchy_viewer.py` |
| "Who has access to Account?" | Permission Detector | `permission_detector.py` |
| "What permissions does John have?" | User Analyzer | `user_analyzer.py` |
| "Export Sales_Manager PS to CSV" | CSV Exporter | `permission_exporter.py` |
| "Generate PS XML with these permissions" | Metadata Generator | `permission_generator.py` |

---

## Phase 2: Connecting to the Org

```bash
sf org list                          # List available orgs
sf org display --target-org <alias>  # Check specific org
```

```python
# Run from sf-permissions/scripts/
from auth import get_sf_connection
sf = get_sf_connection('myorg')  # or None for default
```

---

## Phase 3: Executing Queries

### 3.1 Permission Hierarchy Viewer

```bash
cd ~/.claude/plugins/marketplaces/sf-skills/sf-permissions/scripts
python cli.py hierarchy [--target-org ALIAS] [--format ascii|mermaid]
```

**Output Example**:
```
📦 ORG PERMISSION HIERARCHY
════════════════════════════════════════

📁 Permission Set Groups (3)
├── 🔒 Sales_Cloud_User (Active)
│   ├── View_All_Accounts
│   ├── Edit_Opportunities
│   └── Run_Reports
└── 🔒 Service_Cloud_User (Active)
    └── Case_Management

📁 Standalone Permission Sets (12)
├── Admin_Tools
├── API_Access
└── ... (10 more)
```

### 3.2 Permission Detector ("Who has access to X?")

**Supported Permission Types**: `object`, `field`, `apex`, `vf`, `flow`, `custom`, `tab`

```bash
python cli.py detect object Account --access delete
python cli.py detect field Account.AnnualRevenue --access edit
python cli.py detect apex MyApexClass
python cli.py detect custom Can_Approve_Expenses
```

### 3.3 User Permission Analyzer

```bash
python cli.py user "john.smith@company.com"
python cli.py user 005xx000001234AAA  # User ID also works
```

### 3.4 Permission Set Exporter

```bash
python cli.py export Sales_Manager --output /tmp/sales_manager.csv
```

### 3.5 Agent Access Permissions

> See [references/agent-access-guide.md](references/agent-access-guide.md) for full `<agentAccesses>` XML structure, deploy steps, and visibility troubleshooting (missing icon, name mismatch, CopilotSalesforceUser PS).

Employee Agents require `<agentAccesses>` in a Permission Set — `<agentName>` must match the agent's `developer_name` exactly.

---

## Phase 4: Rendering Output

- **ASCII Tree** (Terminal): Uses `rich` library for trees, tables, panels
- **Mermaid Diagrams** (Docs): `python cli.py hierarchy --format mermaid > hierarchy.md`

## Phase 5: Generating Metadata

```bash
python cli.py generate \
    --name "New_Sales_PS" \
    --label "New Sales Permission Set" \
    --objects Account:crud,Opportunity:cru \
    --fields Account.AnnualRevenue:rw \
    --apex MyApexClass,AnotherClass \
    --output /tmp/New_Sales_PS.permissionset-meta.xml
```

Or delegate to `sf-metadata` for more complex generation.

---

## SOQL Reference

> See [references/permission-soql-queries.md](references/permission-soql-queries.md) for the complete query catalog: Permission Set/Group queries, object permissions, field permissions, setup entity access (Apex, VF, Flows, Custom Permissions).

**Quick queries:**
```sql
-- All Permission Sets (non-profile)
SELECT Id, Name, Label FROM PermissionSet WHERE IsOwnedByProfile = false AND Type != 'Group'

-- User's PS Assignments
SELECT PermissionSetId, PermissionSet.Name FROM PermissionSetAssignment WHERE AssigneeId = '005...'

-- Find PS with delete access to Account
SELECT Parent.Name FROM ObjectPermissions WHERE SobjectType = 'Account' AND PermissionsDelete = true
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `INVALID_SESSION_ID` | Re-authenticate: `sf org login web --alias myorg` |
| Slow queries | Filter by name: `WHERE Name LIKE 'Sales%'` |
| Tab settings | Requires Tooling API: `tooling_query(sf, ...)` |

---

## Common Workflows & Examples

> See [references/workflow-examples.md](references/workflow-examples.md) for detailed step-by-step workflows: audit "Who can delete Accounts?", troubleshoot user access, document a Permission Set, full org audit, security review, and PS creation examples.

---

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `sf-metadata` | Generate Permission Set XML from analysis results |
| `sf-apex` | Identify Apex classes to grant access to |
| `sf-deploy` | Deploy generated Permission Sets |
| `sf-data` | Query user assignments in bulk |
