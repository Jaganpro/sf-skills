# Agent Script CLI Quick Reference

> Pro-Code Lifecycle: Git, CI/CD, and CLI for Agent Development

---

## The sf agent Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf project retrieve start` | Pull agent from org | `sf project retrieve start --metadata Agent:MyAgent --target-org sandbox` |
| `sf agent validate authoring-bundle` | Check syntax before deploy | `sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG` |
| `sf agent publish authoring-bundle` | Publish agent to org | `sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG` |
| `sf agent deploy` | Push to target org | `sf agent deploy --source-dir ./my-agent --target-org prod` |
| `sf agent test run` | Run batch tests | `sf agent test run --name MyAgent --test-suite AllTests` |

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
sf agent validate authoring-bundle --source-dir ./force-app/main/default/aiAuthoringBundles/ProntoRefund
```

### Step 4: Publish

```bash
# Publish agent to org (4-step process: Validate → Publish → Retrieve → Deploy)
sf agent publish authoring-bundle --source-dir ./force-app/main/default/aiAuthoringBundles/ProntoRefund

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
# Run against draft version
sf agent test run --name MyAgent --version draft

# Run against committed version
sf agent test run --name MyAgent --version v1.0

# Run specific test suite
sf agent test run --name MyAgent --test-suite Regression
```

---

## Validation Commands

```bash
# Validate syntax
sf agent validate --source-dir ./my-agent

# Check specific version
sf agent test run --name MyAgent --version v1.0 --test-suite Regression
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
        run: sf agent validate --source-dir ./agents/my-agent
      - name: Run Tests
        run: sf agent test run --name MyAgent --test-suite CI
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
