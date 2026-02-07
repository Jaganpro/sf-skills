# Agent Deployment Guide

Complete guide to deploying Agentforce agents, including deployment methods, CLI commands, validation, activation, and troubleshooting.

## Table of Contents

- [Deployment Methods](#deployment-methods)
- [File Structure](#file-structure)
- [Deployment Workflow](#deployment-workflow)
- [CLI Commands Reference](#cli-commands-reference)
- [Agent Metadata Types](#agent-metadata-types)
- [Troubleshooting](#troubleshooting)
- [Versioning and Promotion](#versioning-and-promotion)

---

## Deployment Methods

There are **two deployment methods** with **different capabilities**:

| Aspect | GenAiPlannerBundle | AiAuthoringBundle |
|--------|-------------------|-------------------|
| Deploy Command | `sf project deploy start` | `sf agent publish authoring-bundle` |
| **Visible in Agentforce Studio** | NO | YES |
| Flow Actions (`flow://`) | Supported | Supported (see requirements below) |
| Apex Actions (`apex://`) | Supported | Limited (class must exist) |
| Escalation (`@utils.escalate with reason`) | Supported | NOT Supported (SyntaxError) |
| `run` keyword (action callbacks) | Supported | NOT Supported (SyntaxError) |
| `filter_from_agent` (conditional actions) | Supported | NOT Supported (SyntaxError) |
| Variables without defaults | Supported | Supported |
| Lifecycle blocks (`before/after_reasoning`) | Supported | Supported |
| Topic transitions (`@utils.transition`) | Supported | Supported |
| Basic escalation (`@utils.escalate`) | Supported | Supported |
| API Version | v65.0+ required | v65.0+ required |

**Why the difference?** These methods correspond to two authoring experiences:
- **Script View** (GenAiPlannerBundle): Full Agent Script syntax with utility actions inherent to the script
- **Canvas/Builder View** (AiAuthoringBundle): Low-code visual builder where some utility actions are not yet available

**Recommendation**: Use **AiAuthoringBundle** if you need agents visible in Agentforce Studio. Use **GenAiPlannerBundle** if you need full Agent Script features (`run` keyword, escalate with reason).

---

## File Structure

| Method | Path | Files | Deploy Command |
|--------|------|-------|----------------|
| **AiAuthoringBundle** | `aiAuthoringBundles/[Name]/` | `[Name].agent` + `.bundle-meta.xml` | `sf agent publish authoring-bundle --api-name [Name]` |
| **GenAiPlannerBundle** | `genAiPlannerBundles/[Name]/` | `[Name].genAiPlannerBundle` + `agentScript/[Name]_definition.agent` | `sf project deploy start --source-dir [path]` |

### AiAuthoringBundle Structure

```
force-app/main/default/aiAuthoringBundles/
└── My_Agent/
    ├── My_Agent.agent                   # Agent Script file
    └── My_Agent.bundle-meta.xml         # Bundle metadata
```

**bundle-meta.xml content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

### GenAiPlannerBundle Structure

```
force-app/main/default/genAiPlannerBundles/
└── My_Agent/
    ├── My_Agent.genAiPlannerBundle      # Planner bundle metadata
    └── agentScript/
        └── My_Agent_definition.agent    # Agent Script file
```

**GenAiPlannerBundle agents do NOT appear in Agentforce Studio UI.**

---

## Deployment Workflow

### Step 1: Deploy Dependencies First

**If using Flow/Apex actions**, deploy them BEFORE deploying the agent:

```bash
# Deploy Flows
sf project deploy start --metadata Flow --test-level NoTestRun --target-org [alias]

# Deploy Apex classes (if any)
sf project deploy start --metadata ApexClass --test-level NoTestRun --target-org [alias]
```

### Step 2: VALIDATE AGENT (MANDATORY)

**CRITICAL: Always validate before deployment to catch syntax errors early!**

```bash
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]
```

This validation:
- Checks Agent Script syntax and structure
- Verifies all topic references are valid
- Confirms variable declarations are correct
- Takes ~3 seconds (much faster than failed deployments)

**DO NOT proceed to Step 3 if validation fails!** Fix all errors first.

### Step 3: Deploy Agent Bundle

#### Option A: Deploy via Metadata API (Recommended - More Reliable)

```bash
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
```

**Best for:**
- Updating existing agents
- Production deployments
- CI/CD pipelines
- Reliability (no HTTP 404 issues)

#### Option B: Publish via Agent CLI (Beta - May fail with HTTP 404)

```bash
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

**Best for:**
- Creating NEW agents (required to create BotDefinition)
- Development/sandbox testing

### Step 4: Verify Deployment

```bash
# Open agent in Agentforce Studio to verify
sf org open agent --api-name [AgentName] --target-org [alias]

# Or query to confirm agent exists
sf data query --query "SELECT Id, DeveloperName FROM BotDefinition WHERE DeveloperName = '[AgentName]'" --target-org [alias]
```

### Step 5: Activate Agent (When Ready for Production)

```bash
sf agent activate --api-name [AgentName] --target-org [alias]
```

---

## NEW Agents vs UPDATING Existing Agents

| Operation | Use This Method | Reason |
|-----------|-----------------|--------|
| **Create NEW agent** | `sf agent publish authoring-bundle` | Required to create BotDefinition |
| **Update EXISTING agent** | `sf project deploy start` | More reliable, avoids HTTP 404 |

### HTTP 404 Error is BENIGN for BotDefinition, but BLOCKS UI Visibility

- The `sf agent publish authoring-bundle` command may fail with `ERROR_HTTP_404` during "Retrieve Metadata" step
- If "Publish Agent" step completed (✔), the **BotDefinition WAS created** successfully
- However, the **AiAuthoringBundle metadata is NOT deployed** to the org
- This means **agents will be INVISIBLE in Agentforce Studio UI** even though they exist!
- **FIX**: After HTTP 404 error, run `sf project deploy start` to deploy the AiAuthoringBundle metadata:
  ```bash
  sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
  ```
- Verify deployment: `sf org list metadata --metadata-type AiAuthoringBundle --target-org [alias]`

### Workflow for NEW Agents (with HTTP 404 fix)

```bash
# 1. Deploy dependencies first (flows, apex)
sf project deploy start --source-dir force-app/main/default/flows --target-org [alias]
sf project deploy start --source-dir force-app/main/default/classes --target-org [alias]

# 2. Publish agent (may show HTTP 404 but BotDefinition is still created)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# 3. ⚠️ CRITICAL: Deploy AiAuthoringBundle metadata (required for UI visibility!)
# This step is REQUIRED if you got HTTP 404 error above
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]

# 4. Verify agent was created AND metadata deployed
sf data query --query "SELECT Id, DeveloperName FROM BotDefinition WHERE DeveloperName = '[AgentName]'" --target-org [alias]
sf org list metadata --metadata-type AiAuthoringBundle --target-org [alias]

# 5. Activate (required to enable agent)
sf agent activate --api-name [AgentName] --target-org [alias]
```

### Workflow for UPDATING Existing Agents

```bash
# Use sf project deploy start (more reliable, no HTTP 404 issues)
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
```

---

## CLI Commands Reference

Complete CLI reference for Agentforce agent DevOps.

### Authoring Commands

```bash
# Validate Agent Script syntax (RECOMMENDED before publish)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Publish agent to org (creates Bot, BotVersion, AiAuthoringBundle metadata)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

**⚠️ No `--source-dir` or `--async` flags!** Commands auto-find bundles in DX project.

### Preview Commands

```bash
# Preview with agent selection prompt
sf agent preview --target-org [alias]

# Preview specific agent (simulated mode - default)
sf agent preview --api-name [AgentName] --target-org [alias]

# Preview in live mode
sf agent preview --api-name [AgentName] --use-live-actions --target-org [alias]

# Preview with debug output saved
sf agent preview --api-name [AgentName] --output-dir ./logs --apex-debug --target-org [alias]
```

**Preview Modes:**

| Mode | Flag | Description |
|------|------|-------------|
| Simulated | (default) | LLM simulates action responses - safe for testing |
| Live | `--use-live-actions` | Uses actual Apex/Flows in org — standard org auth (v2.121.7+) |

> **v2.121.7+**: Live preview no longer requires a Connected App. Standard org auth (`sf org login web`) suffices.

### Lifecycle Commands

```bash
# Activate agent (makes available to users)
sf agent activate --api-name [AgentName] --target-org [alias]

# Deactivate agent (REQUIRED before making changes)
sf agent deactivate --api-name [AgentName] --target-org [alias]
```

**⚠️ Deactivation Required:** You MUST deactivate an agent before modifying topics, actions, or system instructions. After changes, re-publish and re-activate.

### Sync Commands (Agent Pseudo Metadata Type)

The `Agent` pseudo metadata type retrieves/deploys all agent components:

```bash
# Retrieve agent + dependencies from org
sf project retrieve start --metadata Agent:[AgentName] --target-org [alias]

# Deploy agent metadata to org
sf project deploy start --metadata Agent:[AgentName] --target-org [alias]
```

**What Gets Synced:** Bot, BotVersion, GenAiPlannerBundle, GenAiPlugin, GenAiFunction

### Management Commands

```bash
# Open agent in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Update plugin to latest (if commands missing)
sf plugins install @salesforce/plugin-agent@latest
```

### Full Deployment Workflow

```bash
# 1. Deploy Apex classes (if any)
sf project deploy start --metadata ApexClass --target-org [alias]

# 2. Deploy Flows
sf project deploy start --metadata Flow --target-org [alias]

# 3. ⚠️ VALIDATE Agent Script (MANDATORY - DO NOT SKIP!)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]
# If validation fails, fix errors before proceeding!

# 4. Deploy/Publish agent (choose one method)
# Option A: Metadata API (more reliable)
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
# Option B: Agent CLI (beta - may fail with HTTP 404)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# 5. Verify deployment
sf org open agent --api-name [AgentName] --target-org [alias]

# 6. Preview (simulated mode)
sf agent preview --api-name [AgentName] --target-org [alias]

# 7. Activate (when ready for production)
sf agent activate --api-name [AgentName] --target-org [alias]

# 8. Preview (live mode - optional)
sf agent preview --api-name [AgentName] --use-live-actions --target-org [alias]
```

**IMPORTANT**:
- Always run `sf agent validate authoring-bundle` BEFORE deployment to catch errors early (~3 seconds vs minutes for failed deploys)
- If `sf agent publish authoring-bundle` fails with HTTP 404, use `sf project deploy start --source-dir` instead - both work for AiAuthoringBundles

---

## Agent Metadata Types

When working with agent metadata directly, these are the component types:

| Metadata Type | Description | Example API Name |
|---------------|-------------|------------------|
| `Bot` | Top-level chatbot definition | `Customer_Support_Agent` |
| `BotVersion` | Version configuration | `Customer_Support_Agent.v1` |
| `GenAiPlannerBundle` | Reasoning engine (LLM config) | `Customer_Support_Agent_Planner` |
| `GenAiPlugin` | Topic definition | `Order_Management_Plugin` |
| `GenAiFunction` | Action definition | `Get_Order_Status_Function` |

### Agent Pseudo Metadata Type

The `Agent` pseudo type is a convenience wrapper that retrieves/deploys all related components:

```bash
# Retrieves: Bot + BotVersion + GenAiPlannerBundle + GenAiPlugin + GenAiFunction
sf project retrieve start --metadata Agent:My_Agent --target-org [alias]
```

### Retrieving Specific Components

```bash
# Retrieve just the bot definition
sf project retrieve start --metadata Bot:[AgentName] --target-org [alias]

# Retrieve just the planner bundle
sf project retrieve start --metadata GenAiPlannerBundle:[BundleName] --target-org [alias]

# Retrieve all plugins (topics)
sf project retrieve start --metadata GenAiPlugin --target-org [alias]

# Retrieve all functions (actions)
sf project retrieve start --metadata GenAiFunction --target-org [alias]
```

### Metadata Relationships

```
Bot (Agent Definition)
└── BotVersion (Version Config)
    └── GenAiPlannerBundle (Reasoning Engine)
        ├── GenAiPlugin (Topic 1)
        │   ├── GenAiFunction (Action 1)
        │   └── GenAiFunction (Action 2)
        └── GenAiPlugin (Topic 2)
            └── GenAiFunction (Action 3)
```

---

## Troubleshooting

### Common Deployment Errors

| Error | Cause | Fix |
|-------|-------|-----|
| **"Internal Error, try again later"** | Input/output names don't match Flow variables | Ensure Agent Script input/output names EXACTLY match Flow variable API names |
| **HTTP 404 during publish** | Metadata API issue | Run `sf project deploy start` after publish to deploy AiAuthoringBundle |
| **"We couldn't find the flow..."** | Flow not deployed to org | Deploy Flow BEFORE deploying agent |
| **"Unexpected 'run'"** | Using GenAiPlannerBundle-only feature in AiAuthoringBundle | Remove `run` keyword for AiAuthoringBundle |
| **SyntaxError during validation** | Invalid Agent Script syntax | Check indentation, reserved words, block order |
| **Agent invisible in Studio** | AiAuthoringBundle not deployed (HTTP 404 issue) | Run `sf project deploy start` to deploy metadata |

### Validation Errors

| Error | Fix |
|-------|-----|
| Missing `label` or `description` | Add both to every topic |
| Reserved word as input/output name | Use alternative names (e.g., `case_description` instead of `description`) |
| Inconsistent indentation | Use tabs consistently (recommended) |
| Invalid variable type | Use `number` (not `integer`), `list[type]` (not `list<type>`) |

### Debug Tips

1. **Always validate first**: `sf agent validate authoring-bundle --api-name [Name]`
2. **Check deployment logs**: Look for specific error messages
3. **Verify Flow deployment**: `sf org list metadata --metadata-type Flow`
4. **Test in preview mode**: `sf agent preview --api-name [Name]` before activating
5. **Check org permissions**: Ensure `default_agent_user` has proper permissions

---

## Versioning and Promotion

### Version Management

Salesforce automatically creates versions when you publish agents:

```bash
# View agent versions
sf data query --query "SELECT Id, Name, Version FROM BotVersion WHERE BotDefinition.DeveloperName = '[AgentName]'" --target-org [alias]
```

**Versions are incremental**: v1, v2, v3, etc.

### Promoting Between Orgs

**Recommended approach: Use source control + deployments**

```bash
# 1. Retrieve agent from sandbox
sf project retrieve start --metadata Agent:[AgentName] --target-org SandboxAlias

# 2. Commit to source control
git add force-app/main/default/aiAuthoringBundles/
git commit -m "Add agent [AgentName]"
git push

# 3. Deploy to production
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org ProdAlias

# 4. Activate in production
sf agent activate --api-name [AgentName] --target-org ProdAlias
```

### Change Sets (Alternative)

1. Navigate to **Setup → Change Sets** in source org
2. Create new outbound change set
3. Add components:
   - Bot: [AgentName]
   - BotVersion: [AgentName].v[N]
   - AiAuthoringBundle: [AgentName]
   - All related Flows/Apex classes
4. Upload to target org
5. Deploy in target org
6. Activate agent in target org

---

## Best Practices

### Pre-Deployment Checklist

- [ ] All Flow/Apex dependencies deployed to org
- [ ] Agent passes `sf agent validate authoring-bundle`
- [ ] All input/output names match Flow variables exactly
- [ ] Agent tested in preview mode (simulated)
- [ ] `default_agent_user` is valid org user with permissions
- [ ] All topics have `label:` and `description:`
- [ ] No reserved words used as input/output names

### Post-Deployment Checklist

- [ ] Agent visible in Agentforce Studio (if using AiAuthoringBundle)
- [ ] Agent activated successfully
- [ ] Agent tested in preview mode (live)
- [ ] All actions execute correctly
- [ ] Topic routing works as expected
- [ ] Escalation works (if applicable)

### Deployment Strategy

| Environment | Strategy | Frequency |
|-------------|----------|-----------|
| **Development** | Direct deployment | Every change |
| **Sandbox** | Deploy via CLI | After feature completion |
| **UAT** | Change sets or CLI | After testing in sandbox |
| **Production** | Change sets + deployment window | Scheduled releases |

---

## References

For additional information, see:
- [testing-guide.md](testing-guide.md) - Agent testing approaches
- [agent-script-reference.md](agent-script-reference.md) - Full Agent Script syntax
- [actions-guide.md](actions-guide.md) - Action implementation patterns
- [../docs/cli-guide.md](../docs/cli-guide.md) - Complete CLI command reference
