---
name: sf-deploy
description: >
  Comprehensive Salesforce DevOps automation using sf CLI v2. Use when deploying
  metadata, managing scratch orgs, setting up CI/CD pipelines, or troubleshooting
  deployment errors.
license: MIT
metadata:
  version: "2.1.0"
  author: "Jag Valaiyapathy"
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
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-deploy"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-deploy"
      timeout: 5000
---

# sf-deploy: Comprehensive Salesforce DevOps Automation

Expert Salesforce DevOps engineer specializing in deployment automation, CI/CD pipelines, and metadata management using Salesforce CLI (sf v2).

## Core Responsibilities

1. **Deployment Management**: Execute, validate, and monitor deployments (metadata, Apex, LWC)
2. **DevOps Automation**: CI/CD pipelines, automated testing, deployment workflows
3. **Org Management**: Authentication, scratch orgs, environment management
4. **Quality Assurance**: Tests, code coverage, pre-production validation
5. **Troubleshooting**: Debug failures, analyze logs, provide solutions

---

## ⚠️ CRITICAL: Orchestration Order

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  sf-metadata → sf-flow → sf-deploy → sf-data                               │
│                              ▲                                              │
│                         YOU ARE HERE                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Deploy order WITHIN sf-deploy**: Objects/Fields → Permission Sets → Apex → Flows (Draft) → Activate Flows

| Phase | Metadata Type | Why This Order |
|-------|---------------|----------------|
| 1 | Custom Objects/Fields | Everything references these |
| 2 | Permission Sets | FLS requires fields to exist |
| 3 | Apex Classes | @InvocableMethod needed before Flows |
| 4 | Flows (as Draft) | Flows reference fields and Apex |
| 5 | Activate Flows | Safe to activate after validation |

See `docs/orchestration.md` for detailed deployment workflows and agent deployment patterns.

---

## 🔑 Key Insights for Deployment

### Always Use --dry-run First

```bash
# CORRECT: Validate before deploying
sf project deploy start --dry-run --source-dir force-app --target-org alias
sf project deploy start --source-dir force-app --target-org alias

# WRONG: Deploying without validation
sf project deploy start --source-dir force-app --target-org alias  # Risky!
```

### Deploy Permission Sets After Objects

**Common Error:**
```
Error: In field: field - no CustomObject named ObjectName__c found
```

**Solution:** Deploy objects first, THEN permission sets referencing them.

### Flow Activation (4-Step Process)

**Flows deploy as Draft by default.** Activation steps:
1. Deploy with `<status>Draft</status>`
2. Verify: `sf project deploy report --job-id [id]`
3. Edit XML: `Draft` → `Active`
4. Redeploy

**Why?** Draft lets you verify before activating; if activation fails, flow still exists.

**Common Errors**: "Flow is invalid" (deploy objects first) | "Insufficient permissions" (check Manage Flow) | "Version conflict" (deactivate old version)

### FLS Warning After Deployment

**⚠️ Deployed fields may be INVISIBLE without FLS!**

After deploying custom objects/fields:
1. Deploy Permission Set granting field access
2. Assign Permission Set to user: `sf org assign permset --name PermSetName --target-org alias`
3. Verify field visibility

---

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

**Deployment Variants**: Production (full + RunAllTests), Hotfix (targeted + RunLocalTests), CI/CD (scripted + gates), Scratch (push source).

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

---

## Trigger Deployment Safety

> 💡 *See `docs/trigger-deployment-safety.md` for comprehensive guide.*

### Pre-Deployment Guardrails

Before deploying triggers, verify:

| Check | Command/Action |
|-------|---------------|
| Trigger chain analysis | Map all triggers firing together |
| Cascade failure review | Identify atomic vs independent processes |
| Async decoupling | Use Queueable/Events for external calls |
| Savepoint usage | Verify explicit atomicity where needed |
| Test coverage | Include cascade success/failure tests |

### Common Trigger Cascade Risks

| Risk | Symptom | Solution |
|------|---------|----------|
| External callout in trigger | Cascade failure from HTTP timeout | Move to Queueable |
| Shared exception handling | One failure rolls back all | Isolate with try-catch or async |
| Recursive triggers | Stack overflow or DML errors | Use static flag recursion guard |
| Order-dependent triggers | Inconsistent behavior | Document and test trigger order |

### Pre-Deployment Checklist

```
TRIGGER SAFETY CHECKLIST:
□ Identify all triggers in deployment
□ Map trigger chains (which triggers fire together)
□ Verify cascade behavior is intentional
□ Check for external callouts → should be async
□ Confirm savepoint usage for atomic operations
□ Test both success and failure cascade scenarios
□ Validate with --dry-run before production deploy
```

### Recommended Async Patterns

```apex
// BAD: Synchronous external call in trigger
trigger AccountTrigger on Account (after insert) {
    ExternalService.sync(Trigger.new);  // Failure cascades
}

// GOOD: Async decoupling
trigger AccountTrigger on Account (after insert) {
    if (canEnqueueJob()) {
        System.enqueueJob(new AccountSyncQueueable(Trigger.newMap.keySet()));
    }
}
```

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

## Cross-Skill Dependency Checklist

**Before deploying, verify these prerequisites from other skills:**

| Dependency | Check Command | Required For |
|------------|---------------|--------------|
| **TAF Package** | `sf package installed list --target-org alias` | TAF trigger pattern (sf-apex) |
| **Custom Objects/Fields** | `sf sobject describe --sobject ObjectName --target-org alias` | Apex/Flow field references |
| **Trigger_Action__mdt** | Check Setup → Custom Metadata Types | TAF trigger execution |
| **Queues** | `sf data query --query "SELECT Id,Name FROM Group WHERE Type='Queue'"` | Flow queue assignments |
| **Permission Sets** | `sf org list metadata --metadata-type PermissionSet` | FLS for custom fields |

**Common Cross-Skill Issues:**

| Error Message | Missing Dependency | Solution |
|--------------|-------------------|----------|
| `Invalid type: MetadataTriggerHandler` | TAF Package | Install apex-trigger-actions package |
| `Field does not exist: Field__c` | Custom Field or FLS | Deploy field or create Permission Set |
| `No such column 'Field__c'` | Field-Level Security | Assign Permission Set to running user |
| `SObject type 'Object__c' not supported` | Custom Object | Deploy object via sf-metadata first |
| `Queue 'QueueName' not found` | Queue Metadata | Deploy queue via sf-metadata first |

### sf-ai-agentscript Integration (Agent DevOps)

**Complete DevOps guide**: See `docs/agent-deployment-guide.md` for comprehensive agent deployment documentation.

#### Agent Metadata Types

| Metadata Type | Description |
|---------------|-------------|
| `Bot` | Top-level chatbot definition |
| `BotVersion` | Version configuration |
| `GenAiPlannerBundle` | Reasoning engine (LLM config) |
| `GenAiPlugin` | Topic definition |
| `GenAiFunction` | Action definition |

#### Agent Pseudo Metadata Type

The `Agent` pseudo type syncs all agent components at once:

```bash
# Retrieve agent + all dependencies from org
sf project retrieve start --metadata Agent:[AgentName] --target-org [alias]

# Deploy agent metadata to org
sf project deploy start --metadata Agent:[AgentName] --target-org [alias]
```

#### Agent Lifecycle Commands

```bash
# Activate agent (makes available to users)
sf agent activate --api-name [AgentName] --target-org [alias]

# Deactivate agent (REQUIRED before making changes)
sf agent deactivate --api-name [AgentName] --target-org [alias]

# Preview agent (simulated mode - safe testing)
sf agent preview --api-name [AgentName] --target-org [alias]

# Preview agent (live mode - real Apex/Flows)
sf agent preview --api-name [AgentName] --use-live-actions --client-app [App] --target-org [alias]

# Validate Agent Script syntax
sf afdx agent validate --api-name [AgentName] --target-org [alias]
```

#### Full Agent Deployment Workflow

```bash
# 1. Deploy Apex classes (if any)
sf project deploy start --metadata ApexClass --target-org [alias]

# 2. Deploy Flows
sf project deploy start --metadata Flow --target-org [alias]

# 3. Validate Agent Script
sf afdx agent validate --api-name [AgentName] --target-org [alias]

# 4. Publish agent
sf agent publish --api-name [AgentName] --target-org [alias]

# 5. Preview (simulated mode)
sf agent preview --api-name [AgentName] --target-org [alias]

# 6. Activate
sf agent activate --api-name [AgentName] --target-org [alias]
```

#### Modifying Existing Agents

**⚠️ Deactivation Required**: You MUST deactivate an agent before modifying topics, actions, or system instructions.

```bash
# 1. Deactivate
sf agent deactivate --api-name [AgentName] --target-org [alias]

# 2. Make changes to Agent Script

# 3. Re-publish
sf agent publish --api-name [AgentName] --target-org [alias]

# 4. Re-activate
sf agent activate --api-name [AgentName] --target-org [alias]
```

#### Sync Agent Between Orgs

```bash
# 1. Retrieve from source org
sf project retrieve start --metadata Agent:[AgentName] --target-org source-org

# 2. Deploy dependencies to target org first
sf project deploy start --metadata ApexClass,Flow --target-org target-org

# 3. Deploy agent metadata
sf project deploy start --metadata Agent:[AgentName] --target-org target-org

# 4. Publish agent in target org
sf agent publish --api-name [AgentName] --target-org target-org

# 5. Activate in target org
sf agent activate --api-name [AgentName] --target-org target-org
```

#### Agent-Specific CLI Reference

| Command | Description |
|---------|-------------|
| `sf agent publish --api-name X` | Publish authoring bundle |
| `sf agent activate --api-name X` | Activate published agent |
| `sf agent deactivate --api-name X` | Deactivate agent for changes |
| `sf agent preview --api-name X` | Preview agent behavior |
| `sf afdx agent validate --api-name X` | Validate Agent Script syntax |
| `sf org open agent --api-name X` | Open in Agentforce Builder |
| `sf project retrieve start --metadata Agent:X` | Retrieve agent + components |
| `sf project deploy start --metadata Agent:X` | Deploy agent metadata |

---

## Deployment Script Template

Reusable multi-step deployment script: **[examples/deploy.sh](examples/deploy.sh)**

Deploys in order: Objects → Permission Sets → Apex (with tests) → Flows (Draft)

---

## Generate Package Manifest

**Auto-generate package.xml from source directory:**

```bash
# Generate from source
sf project generate manifest --source-dir force-app --name manifest/package.xml

# Generate for specific metadata types
sf project generate manifest \
    --metadata CustomObject:Account \
    --metadata ApexClass \
    --metadata Flow \
    --name manifest/package.xml

# Deploy using manifest
sf project deploy start --manifest manifest/package.xml --target-org alias
```

**When to use manifest vs source-dir:**

| Scenario | Use | Command |
|----------|-----|---------|
| Deploy everything | `--source-dir` | `sf project deploy start --source-dir force-app` |
| Deploy specific components | `--manifest` | `sf project deploy start --manifest package.xml` |
| CI/CD pipelines | `--manifest` | Controlled, reproducible deployments |
| Development iteration | `--source-dir` | Quick local changes |

---

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
