<!-- Parent: sf-ai-agentscript/SKILL.md -->
# Agent Script CLI Quick Reference

> Pro-Code Lifecycle: Git, CI/CD, and CLI for Agent Development

---

## The sf agent Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf project retrieve start` | Pull agent from org | `sf project retrieve start --metadata Agent:MyAgent --target-org sandbox` |
| `sf agent validate authoring-bundle` | Check syntax before deploy | `sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG` |
| `sf agent publish authoring-bundle` | Publish agent to org | `sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG --json` |
| `sf agent test run` | Run batch tests | `sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json` |
| `sf agent create` | Create agent from spec file | `sf agent create --api-name MyAgent --spec agent-spec.yaml -o TARGET_ORG --json` |
| `sf agent generate agent-spec` | Generate agent specification | `sf agent generate agent-spec --type customer --role "Service Rep" --output-file agent-spec.yaml` |
| `sf agent generate authoring-bundle` | Scaffold authoring bundle | `sf agent generate authoring-bundle --no-spec --name "My Agent" -o TARGET_ORG --json` |
| `sf agent generate template` | Generate agent template (ISV packaging) | `sf agent generate template --agent-file MyAgent.agent --agent-version 1.0 --json` |
| `sf agent activate` | Activate agent (make live) | `sf agent activate --api-name MyAgent -o TARGET_ORG` |
| `sf agent deactivate` | Deactivate agent (take offline) | `sf agent deactivate --api-name MyAgent -o TARGET_ORG` |
| `sf agent preview start` | Start programmatic preview session | `sf agent preview start --api-name MyAgent -o TARGET_ORG --json` (or `--authoring-bundle`) |
| `sf agent preview send` | Send utterance to preview session | `sf agent preview send --session-id <id> --utterance "Hello" --json` |
| `sf agent preview end` | End preview session | `sf agent preview end --session-id <id> --json` |
| `sf org open agent` | Open Agent Builder in browser | `sf org open agent --api-name MyAgent -o TARGET_ORG` |
| `sf org open authoring-bundle` | Open Agentforce Studio list view | `sf org open authoring-bundle -o TARGET_ORG` |

> ⚠️ **CRITICAL**: Use `sf agent publish authoring-bundle` for Agent Script deployment, NOT `sf project deploy start`. The metadata API deploy will fail with "Required fields are missing: [BundleType]".

---

## Authoring Bundle Structure

> ⚠️ **CRITICAL NAMING CONVENTION**: File must be named `AgentName.bundle-meta.xml`, NOT `AgentName.aiAuthoringBundle-meta.xml`. The metadata API expects `.bundle-meta.xml` suffix.

```
force-app/main/default/aiAuthoringBundles/
└── ProntoRefund/
    ├── ProntoRefund.agent           # Your Agent Script (REQUIRED)
    └── ProntoRefund.bundle-meta.xml # Metadata XML (REQUIRED)
```

### AgentName.bundle-meta.xml Content

```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

> ⚠️ **COMMON ERROR**: Using `<BundleType>` (PascalCase) instead of `<bundleType>` (camelCase) will NOT cause errors, but the field name in the XML element is `bundleType` (lowercase b).

### Bundle Naming Rules

| Component | Convention | Example |
|-----------|------------|---------|
| Folder name | PascalCase or snake_case | `ProntoRefund/` or `Pronto_Refund/` |
| Agent script | Same as folder + `.agent` | `ProntoRefund.agent` |
| Metadata XML | Same as folder + `.bundle-meta.xml` | `ProntoRefund.bundle-meta.xml` |

### Deployment Command (NOT sf project deploy!)

```bash
# ✅ CORRECT: Use sf agent publish authoring-bundle
sf agent publish authoring-bundle --api-name ProntoRefund -o TARGET_ORG

# ❌ WRONG: Do NOT use sf project deploy start
# This will fail with "Required fields are missing: [BundleType]"
```

---

## Pro-Code Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1 Retrieve  │ →  │ 2 Edit      │ →  │ 3 Validate  │ →  │ 4 Deploy    │
│ Pull agent  │    │ CLI/editor  │    │ Check syntax│    │ Push to prod│
│ from org    │    │ + Claude    │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Step 1: Retrieve

```bash
# Retrieve from sandbox
sf project retrieve start --metadata Agent:ProntoRefund --target-org sandbox --json
```

### Step 2: Edit

```bash
# Edit the agent script
vim ./ProntoRefund/main.agent
```

### Step 3: Validate

```bash
# Validate authoring bundle syntax
sf agent validate authoring-bundle --api-name ProntoRefund -o TARGET_ORG --json
```

### Step 4: Publish

```bash
# Publish agent to org (4-step process: Validate → Publish → Retrieve → Deploy)
sf agent publish authoring-bundle --api-name ProntoRefund -o TARGET_ORG --json

# Expected output:
# ✔ Validate Bundle    ~1-2s
# ✔ Publish Agent      ~8-10s
# ✔ Retrieve Metadata  ~5-7s
# ✔ Deploy Metadata    ~4-6s
```

> ⚠️ Do NOT use `sf project deploy start` - it will fail with "Required fields are missing: [BundleType]"

### Step 5: Activate

> ⚠️ **Publishing does NOT activate.** The new BotVersion is created as `Inactive`. Tests, preview, and end users continue hitting the previously active version until you explicitly activate.

```bash
# Activate the latest published version
sf agent activate --api-name ProntoRefund -o TARGET_ORG

# Verify activation (optional)
sf data query --query "SELECT DeveloperName, VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = 'ProntoRefund' AND Status = 'Active' LIMIT 1" -o TARGET_ORG --json
```

> ℹ️ `sf agent activate` and `sf agent deactivate` do **not** support `--json`. The command prints a plain-text confirmation message on success.

---

## Testing Commands

```bash
# Run agent tests (--api-name refers to an AiEvaluationDefinition, not the agent)
sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
```

---

## Validation Commands

```bash
# Validate authoring bundle syntax
sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json

# Run tests against test definition
sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Internal Error, try again later` | Invalid `default_agent_user` | Query for Einstein Agent Users |
| `SyntaxError: You cannot mix spaces and tabs` | Mixed indentation | Use consistent spacing |
| `Transition to undefined topic "@topic.X"` | Typo in topic name | Check spelling |
| `Variables cannot be both mutable AND linked` | Conflicting modifiers | Choose one modifier |

---

## Einstein Agent User Setup

### Query Existing Users

```bash
sf data query --query "SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true"
```

### Username Format

```
agent_user@<org-id>.ext
```

Example: `agent_user@00drt00000limwjmal.ext`

### Get Org ID

```bash
sf org display --json | jq -r '.result.id'
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Agent Testing
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Agent
        run: sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
      - name: Run Tests
        run: sf agent test run --api-name MyTestDef --wait 10 -o TARGET_ORG --json
```

---

## Deployment Pipeline

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Sandbox    │ ───▶ │   Staging   │ ───▶ │ Production  │
│   v1.3.0    │      │  Validate   │      │   v1.3.0    │
└─────────────┘      └─────────────┘      └─────────────┘
```

### 6-Step Pipeline

1. **Retrieve from Sandbox** - Pull latest agent bundle
2. **Validate Syntax** - Check Agent Script for errors
3. **Run Tests** - Execute automated agent tests
4. **Code Review** - Automated best practices checks
5. **Deploy to Production** - Push validated bundle
6. **Verify Deployment** - Confirm agent is active

---

## Agent Creation Commands

### Create Agent from Spec File

```bash
# Generate an agent specification YAML first
sf agent generate agent-spec \
  --type customer \
  --role "Customer Service Representative" \
  --company-name "Acme Corp" \
  --company-description "E-commerce platform" \
  --output-file agent-spec.yaml

# Create the agent from the spec
sf agent create \
  --api-name MyServiceAgent \
  --spec agent-spec.yaml \
  -o TARGET_ORG --json
```

### Generate Agent Template (ISV Packaging)

```bash
# Generate template for managed package distribution
sf agent generate template \
  --agent-file force-app/main/default/aiAuthoringBundles/MyAgent/MyAgent.agent \
  --agent-version 1.0 \
  --json
```

---

## Programmatic Preview (Non-Interactive)

> ⛔ **NEVER run bare `sf agent preview`** — it launches an interactive terminal requiring keyboard input. Claude Code CANNOT use it. **ALWAYS use subcommands**: `start`, `send`, `end` with `--json`.

```bash
# 1. Start a preview session
SESSION_ID=$(sf agent preview start --api-name MyAgent -o TARGET_ORG --json | jq -r '.result.sessionId')

# 2. Send utterances programmatically
sf agent preview send --session-id $SESSION_ID --authoring-bundle MyAgent --utterance "I need a refund" --json

# 3. Send follow-up messages
sf agent preview send --session-id $SESSION_ID --authoring-bundle MyAgent --utterance "Order #12345" --json

# 4. End the session
sf agent preview end --session-id $SESSION_ID --json

# List active preview sessions
sf agent preview sessions -o TARGET_ORG --json
```

### Preview Modes

| Mode | Flag | Behavior |
|------|------|----------|
| **Simulated** (default) | *(none)* | AI simulates/mocks action responses — no real data changes |
| **Live** | `--use-live-actions` | Executes real actions in the org (Flows, Apex, APIs) |

Additional preview flags:

| Flag | Purpose |
|------|---------|
| `--apex-debug` | Enable Apex debug logging during preview session |
| `--output-dir <path>` | Save conversation transcripts to directory |
| `--authoring-bundle` | Specify authoring bundle name instead of `--api-name` |

```bash
# Live preview with Apex debug logging and transcript saving
SESSION_ID=$(sf agent preview start --api-name MyAgent --use-live-actions --apex-debug --output-dir ./transcripts -o TARGET_ORG --json | jq -r '.result.sessionId')

# Preview using authoring bundle name instead of api-name
SESSION_ID=$(sf agent preview start --authoring-bundle MyBundle -o TARGET_ORG --json | jq -r '.result.sessionId')

# End session (also supports --authoring-bundle)
sf agent preview end --session-id $SESSION_ID --json
```

---

## Activate / Deactivate Agent

After publishing, activate the agent to make it live. Deactivate before re-publishing updates.

> ⚠️ **`--json` is NOT supported** on `sf agent activate` / `sf agent deactivate`. These commands output plain text only.

```bash
# Activate agent (makes it live for end users)
sf agent activate --api-name MyAgent -o TARGET_ORG

# Deactivate agent (takes it offline — required before re-publishing)
sf agent deactivate --api-name MyAgent -o TARGET_ORG
```

**Verify activation status**:
```bash
sf data query --query "SELECT DeveloperName, VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = 'MyAgent' AND Status = 'Active' LIMIT 1" -o TARGET_ORG --json
```

**Full update lifecycle**: Deactivate → Re-publish → Re-activate

```bash
# Update an already-active agent:
sf agent deactivate --api-name MyAgent -o TARGET_ORG
sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG --json
sf agent activate --api-name MyAgent -o TARGET_ORG
```

---

## Generate Authoring Bundle (`--no-spec`)

The `--no-spec` flag skips requiring an agent spec YAML file and uses default Agent Script boilerplate:

```bash
# Scaffold a new authoring bundle without an agent spec
sf agent generate authoring-bundle --no-spec --name "My Agent" -o TARGET_ORG --json

# With a spec file (standard flow)
sf agent generate authoring-bundle --spec agent-spec.yaml --name "My Agent" -o TARGET_ORG --json

# Overwrite existing bundle without confirmation (v2.125.1+)
sf agent generate authoring-bundle --spec agent-spec.yaml --name "My Agent" --force-overwrite -o TARGET_ORG --json
```

---

## Generate Agent Spec — Full Flag Reference

| Flag | Values / Type | Description |
|------|---------------|-------------|
| `--type` | `customer \| internal` | **Required.** Agent audience type |
| `--role` | string | **Required.** Agent's role description |
| `--company-name` | string | Company name for context |
| `--company-description` | string | Company description for context |
| `--company-website` | URL | Company website URL for grounding |
| `--tone` | `formal \| casual \| neutral` | Conversational style |
| `--enrich-logs` | `true \| false` | Add agent conversation data to event logs |
| `--max-topics` | number | Maximum topics to generate (default: 5) |
| `--agent-user` | username | Einstein Agent User to assign |
| `--output-file` | path | Output path (default: `specs/agentSpec.yaml`) |
| `--full-interview` | *(flag)* | Prompt for both required AND optional flags |
| `--spec` | file path | Use existing spec for iterative refinement |
| `--prompt-template` | API name | Custom prompt template reference |
| `--grounding-context` | string | Context value for custom prompt template |
| `--force-overwrite` | *(flag)* | Overwrite existing spec without confirmation |

```bash
# Full example with optional flags
sf agent generate agent-spec \
  --type customer \
  --role "Customer Service Representative" \
  --company-name "Acme Corp" \
  --company-description "E-commerce platform" \
  --company-website "https://acme.example.com" \
  --tone formal \
  --enrich-logs true \
  --max-topics 8 \
  --agent-user "agent_user@00dxx000001234.ext" \
  --output-file specs/my-agent-spec.yaml

# Iterative refinement — feed existing spec back in
sf agent generate agent-spec \
  --spec specs/my-agent-spec.yaml \
  --max-topics 3 \
  --tone casual \
  --force-overwrite
```

---

## Browser Quick-Open Commands

```bash
# Open specific agent in Agentforce Builder
sf org open agent --api-name MyAgent -o TARGET_ORG

# Open Agentforce Studio (list view of all authoring bundles)
sf org open authoring-bundle -o TARGET_ORG

# Get URL only (for CI/CD logs or scripts)
sf org open agent --api-name MyAgent -o TARGET_ORG --url-only
```

---

## Three-Phase Lifecycle

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   ✏️ Draft   │  →   │  🔒 Commit  │  →   │  ✅ Activate │
│   EDITABLE  │      │  READ-ONLY  │      │    LIVE     │
└─────────────┘      └─────────────┘      └─────────────┘
```

| Phase | Capabilities |
|-------|--------------|
| **Draft** | Edit freely, preview, run batch tests |
| **Commit** | Script frozen, version assigned, bundle compiled |
| **Activate** | Assign to Connections, go live, monitor |

> **Key Insight**: Commit doesn't deploy - it freezes. Activate makes it live.

---

## API Versioning Behavior

Agent versions share the same `agentId` (the `BotDefinition` / `Agent` record) but have **distinct version IDs**.

| Concept | Description |
|---------|-------------|
| `agentId` / `BotDefinition.Id` | Unique per agent — does NOT change between versions |
| `versionId` / `BotVersion.Id` | Unique per version — changes with each commit |
| Default API behavior | API calls target the **active** version unless a specific `versionId` is provided |

```bash
# The Agent Runtime API defaults to the active version:
curl -X POST ".../einstein/ai-agent/v1" \
  -d '{"agentDefinitionId": "0XxXXXXXXXXXXX"}'   # Uses active version

# To target a specific version (draft/committed), include versionId:
curl -X POST ".../einstein/ai-agent/v1" \
  -d '{"agentDefinitionId": "0XxXXXXXXXXXXX", "agentVersionId": "4KdXXXXXXXXXXX"}'
```

> **Key implication**: When testing draft versions via API, you must explicitly pass the version ID. Otherwise, the API will use the last activated version — which may not reflect your latest changes.

---

## ⛔ CLI Anti-Patterns

### DO NOT SOQL query metadata types

These are **metadata types**, NOT sObjects. SOQL queries against them return `INVALID_TYPE`.

| Type | ❌ WRONG (SOQL) | ✅ CORRECT (Metadata API) |
|------|-----------------|--------------------------|
| GenAiPlannerBundle | `SELECT ... FROM GenAiPlannerBundle` | `sf project retrieve start --metadata "GenAiPlannerBundle:Name"` |
| AiAuthoringBundle | `SELECT ... FROM AiAuthoringBundle` | `sf project retrieve start --metadata "AiAuthoringBundle:Name"` |
| GenAiFunction | `SELECT ... FROM GenAiFunction` | `sf project retrieve start --metadata "GenAiFunction:Name"` |

> For SOQL, query `BotDefinition` and `BotVersion` instead — these ARE sObjects.

### BotDefinition vs BotVersion field reference

| Field | BotDefinition | BotVersion |
|-------|:---:|:---:|
| Id, DeveloperName | ✅ | ✅ |
| MasterLabel | ✅ | ❌ |
| **Status** | ❌ | ✅ |
| VersionNumber | ❌ | ✅ |

> ⚠️ `Status` lives on `BotVersion`, NOT `BotDefinition`. Querying `BotDefinition.Status` returns "No such column."

### DO NOT run bare `sf agent preview`

| ❌ WRONG (interactive, hangs) | ✅ CORRECT (programmatic) |
|-------------------------------|--------------------------|
| `sf agent preview` | `sf agent preview start --authoring-bundle MyAgent --json` |
| *(waits for keyboard input)* | `sf agent preview send --session-id $ID --authoring-bundle MyAgent --utterance "..." --json` |
| | `sf agent preview end --session-id $ID --json` |

### DO NOT pass context variables via `sf agent preview`

> ⛔ `sf agent preview` does NOT support context or session variable injection. There are no `--context`, `--session-var`, or `--variables` flags.

| Variable Source | Works in Preview? | Alternative |
|----------------|:-----------------:|-------------|
| `@session.sessionID` | ❌ | Agent Runtime API with session context |
| `@context.customerId` | ❌ | Agent Runtime API with `contextVariables` |
| `@context.RoutableId` | ❌ | Agent Runtime API with `contextVariables` |
| Mutable vars (defaults) | ✅ | Works normally via default values |
| `with param=...` (slot-filling) | ✅ | Works normally via LLM extraction |
