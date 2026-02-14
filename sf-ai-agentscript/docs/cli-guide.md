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
| `sf agent generate template` | Generate agent template (ISV packaging) | `sf agent generate template --agent-file MyAgent.agent --agent-version 1.0 --json` |
| `sf agent preview start` | Start programmatic preview session | `sf agent preview start --api-name MyAgent -o TARGET_ORG --json` |
| `sf agent preview send` | Send utterance to preview session | `sf agent preview send --session-id <id> --message "Hello" --json` |
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

> Unlike `sf agent preview` (interactive terminal), these subcommands enable scripted/automated agent testing — critical for CI/CD.

```bash
# 1. Start a preview session
SESSION_ID=$(sf agent preview start --api-name MyAgent -o TARGET_ORG --json | jq -r '.result.sessionId')

# 2. Send utterances programmatically
sf agent preview send --session-id $SESSION_ID --message "I need a refund" --json

# 3. Send follow-up messages
sf agent preview send --session-id $SESSION_ID --message "Order #12345" --json

# 4. End the session
sf agent preview end --session-id $SESSION_ID --json

# List active preview sessions
sf agent preview sessions -o TARGET_ORG --json
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
