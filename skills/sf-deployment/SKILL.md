---
name: sf-deployment
description: Comprehensive Salesforce DevOps automation
version: 2.1.0
author: Jag Valaiyapathy
license: MIT
tags:
- salesforce
- devops
- sfdx
- deployment
- ci-cd
- automation
- apex
- metadata
allowed-tools:
- Bash
- Read
- Write
- Edit
- Grep
- Glob
- AskUserQuestion
- TodoWrite
examples: []
metadata:
  created: '2024-11-28'
  updated: '2025-12-02'
  format_version: 2.0.0
  license_file: LICENSE
dependencies: []
homepage: ''
repository: ''
keywords: []
test_config:
  enabled: false
  test_files: []
---

# sf-deployment: Comprehensive Salesforce DevOps Automation

Expert Salesforce DevOps engineer specializing in deployment automation, CI/CD pipelines, and metadata management using Salesforce CLI (sf v2).

## Core Responsibilities

1. **Deployment Management**: Execute, validate, and monitor deployments (metadata, Apex, LWC)
2. **DevOps Automation**: CI/CD pipelines, automated testing, deployment workflows
3. **Org Management**: Authentication, scratch orgs, environment management
4. **Quality Assurance**: Tests, code coverage, pre-production validation
5. **Troubleshooting**: Debug failures, analyze logs, provide solutions

## CLI Version (CRITICAL)

**This skill uses `sf` CLI (v2.x), NOT legacy `sfdx` (v1.x)**

| Legacy sfdx (v1) | Modern sf (v2) |
|-----------------|----------------|
| `--checkonly` / `--check-only` | `--dry-run` |
| `sfdx force:source:deploy` | `sf project deploy start` |

## Prerequisites

Before deployment, verify:
```bash
sf --version              # Requires v2.x
sf org list               # Check authenticated orgs
test -f sfdx-project.json # Valid SFDX project
```

## Deployment Workflow (5-Phase)

### Phase 1: Pre-Deployment Analysis

**Gather via AskUserQuestion**: Target org, deployment scope, validation requirements, rollback strategy.

**Analyze**:
- Read `sfdx-project.json` for package directories
- Glob for metadata: `**/force-app/**/*.{cls,trigger,xml,js,html,css}`
- Grep for dependencies

**TodoWrite tasks**: Validate auth, Pre-tests, Deploy, Monitor, Post-tests, Verify

### Phase 2: Pre-Deployment Validation

```bash
sf org display --target-org <alias>                    # Check connection
sf apex test run --test-level RunLocalTests --target-org <alias> --wait 10  # Local tests
sf project deploy start --dry-run --test-level RunLocalTests --target-org <alias> --wait 30  # Validate
```

### Phase 3: Deployment Execution

**Commands by scope**:
```bash
# Full metadata
sf project deploy start --target-org <alias> --wait 30

# Specific components
sf project deploy start --source-dir force-app/main/default/classes --target-org <alias>

# Manifest-based
sf project deploy start --manifest manifest/package.xml --target-org <alias> --test-level RunLocalTests --wait 30

# Quick deploy (after validation)
sf project deploy quick --job-id <validation-job-id> --target-org <alias>
```

Handle failures: Parse errors, identify failed components, suggest fixes.

### Phase 4: Post-Deployment Verification

```bash
sf project deploy report --job-id <job-id> --target-org <alias>
```

Verify components, run smoke tests, check coverage.

### Phase 5: Documentation

Provide summary with: deployed components, test results, coverage metrics, next steps.

See [examples/deployment-report-template.md](examples/deployment-report-template.md) for output format.

## Deployment Pattern

Standard workflow for all scenarios:

1. **Verify** org auth: `sf org display`
2. **Identify** scope: [full | components | hotfix | scratch]
3. **Validate**: `sf project deploy start --dry-run`
4. **Execute**: `sf project deploy start [options]`
5. **Verify**: `sf project deploy report`

**Variants**:
- **Production**: Full scope + backup + RunAllTests + documentation
- **Hotfix**: Targeted components + RunLocalTests + fast deploy
- **CI/CD**: Scripted + automated gates + notifications
- **Scratch**: `sf project deploy start` (push source)

## CLI Reference

**Deploy**: `sf project deploy start [--dry-run] [--source-dir <path>] [--manifest <xml>] [--test-level <level>]`
**Quick**: `sf project deploy quick --job-id <id>` | **Status**: `sf project deploy report`
**Test**: `sf apex test run --test-level RunLocalTests` | **Coverage**: `sf apex get test --code-coverage`
**Org**: `sf org list` | `sf org display` | `sf org create scratch` | `sf org open`
**Metadata**: `sf project retrieve start` | `sf org list metadata --metadata-type <type>`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| FIELD_CUSTOM_VALIDATION_EXCEPTION | Validation rule blocking | Deactivate rules or use valid test data |
| INVALID_CROSS_REFERENCE_KEY | Missing dependency | Include dependencies in deploy |
| CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY | Trigger/validation error | Review trigger logic, check recursion |
| TEST_FAILURE | Test class failure | Fix test or code under test |
| INSUFFICIENT_ACCESS | Permission issue | Verify user permissions, FLS |

### Flow-Specific Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Element X is duplicated" | Elements not alphabetically ordered | Reorder Flow XML elements |
| "Element bulkSupport invalid" | Deprecated element (API 60.0+) | Remove `<bulkSupport>` |
| "Error parsing file" | Malformed XML | Validate XML syntax |

### Failure Response

1. Parse error output, identify failed components
2. Explain error in plain language
3. Suggest specific fixes with code examples
4. Provide rollback options if needed

## Best Practices

- **Always validate first**: Use `--dry-run` for production
- **Appropriate test levels**: RunLocalTests (deploy), RunAllTests (packages)
- **Code coverage**: >75% for production, >90% recommended
- **Use manifests**: `package.xml` for controlled deployments
- **Version control**: Commit before deploying, tag releases
- **Incremental deploys**: Small, frequent changes over large batches
- **Sandbox first**: Always test before production
- **Backup metadata**: Retrieve before major deployments
- **Quick deploy**: Use for validated changesets

## CI/CD Integration

Standard pipeline workflow:
1. Authenticate (JWT/auth URL)
2. Validate metadata
3. Static analysis (PMD, ESLint)
4. Dry-run deployment
5. Run tests + coverage check
6. Deploy if validation passes
7. Notify

See [examples/deployment-workflows.md](examples/deployment-workflows.md) for scripts.

## Edge Cases

- **Large deployments**: Split into batches (limit: 10,000 files / 39 MB)
- **Test timeout**: Increase wait time or run tests separately
- **Namespace conflicts**: Handle managed package issues
- **API version**: Ensure source/target compatibility

## Notes

- **CLI**: Uses only `sf` (v2) with modern flag syntax
- **Auth**: Supports OAuth, JWT, Auth URL, web login
- **API**: Uses Metadata API (not Tooling API)
- **Async**: Use `--wait` to monitor; most deploys are async
- **Limits**: Be aware of Salesforce governor limits

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
