<!-- Parent: sf-permissions/SKILL.md -->

# Common Workflows & Examples

## Workflow 1: Audit "Who can delete Accounts?"

```
User: "Who has delete access to the Account object?"

1. Run permission detector for object:Account with delete access
2. For each PS found, get PSG membership
3. For each PS/PSG, count assigned users
4. Display results in table format
```

## Workflow 2: Troubleshoot User Access

```
User: "Why can't John edit Opportunities?"

1. Run user analyzer for john@company.com
2. Check if any PS grants Opportunity edit
3. If not, suggest which PS/PSG to assign
4. Check for conflicting profile restrictions
```

## Workflow 3: Document Permission Set

```
User: "Export the Sales_Manager PS for documentation"

1. Run exporter for Sales_Manager
2. Generate CSV with all permissions
3. Optionally generate Mermaid diagram showing PSG membership
```

## Example 1: Full Org Audit

```
User: "Give me a complete picture of permissions in my org"

Claude:
1. Runs hierarchy viewer to show all PS/PSG
2. Identifies PSGs with "Outdated" status
3. Counts users per PS
4. Generates Mermaid diagram for documentation
```

## Example 2: Security Review

```
User: "Find all PS that grant ModifyAllData"

Claude:
1. Queries PermissionSet for PermissionsModifyAllData = true
2. Lists PS names and assigned user counts
3. Flags any non-admin PS with this powerful permission
```

## Example 3: Permission Set Creation

```
User: "Create a PS for contractors with read-only Account access"

Claude:
1. Uses permission_generator.py to create XML
2. Sets Account object to Read-only (no Create/Edit/Delete)
3. Outputs .permissionset-meta.xml file
```
