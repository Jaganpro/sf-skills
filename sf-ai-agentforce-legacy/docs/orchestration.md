# Multi-Skill Orchestration: sf-ai-agentforce Perspective

This document details how sf-ai-agentforce fits into the multi-skill workflow for Salesforce development.

---

## Standard Orchestration Order

sf-ai-agentforce requires an **extended orchestration** because agents depend on deployed Flows:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENTFORCE ORCHESTRATION ORDER                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. sf-metadata                                                             │
│     └── Create object/field definitions (LOCAL files)                       │
│                                                                             │
│  2. sf-apex (if custom logic needed)                                        │
│     └── Create @InvocableMethod classes (LOCAL files)                       │
│                                                                             │
│  3. sf-flow                                                                 │
│     └── Create flow definitions (LOCAL files)                               │
│     └── Create Flow wrappers for Apex (if using Apex)                       │
│                                                                             │
│  4. sf-deploy (FIRST DEPLOYMENT)                                            │
│     └── Deploy: Objects, Fields, Apex, Flows (REMOTE)                       │
│                                                                             │
│  5. sf-ai-agentforce  ◀── YOU ARE HERE                                     │
│     └── Create agent with flow:// targets                                   │
│                                                                             │
│  6. sf-deploy (SECOND DEPLOYMENT - Agent Publish)                           │
│     └── sf agent publish authoring-bundle --api-name [AgentName]           │
│     └── sf agent activate --api-name [AgentName]                           │
│                                                                             │
│  7. sf-ai-agentforce-testing (NEW)                                          │
│     └── Generate test spec from agent metadata                              │
│     └── Run agent tests (sf agent test run)                                 │
│     └── Agentic fix loop if failures detected                               │
│                                                                             │
│  8. sf-data (optional)                                                      │
│     └── Create test data for agent testing                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why sf-ai-agentforce Goes Near Last

Agents reference:
- **Flows** via `flow://FlowName` targets
- **Apex** via Flow wrappers (not directly)
- **Objects/Fields** indirectly through Flows

All dependencies must be deployed **BEFORE** creating the agent.

```
ERROR: "We couldn't find the flow, prompt, or apex class: flow://Missing_Flow"
CAUSE: Flow not deployed to org
FIX:   Deploy Flow via sf-deploy BEFORE creating agent
```

---

## Integration + External API Extended Order

When building agents with external API integrations:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INTEGRATION + AGENTFORCE ORCHESTRATION ORDER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. sf-connected-apps   → Create Connected App (if OAuth needed)            │
│  2. sf-integration      → Create Named Credential + External Service        │
│  3. sf-metadata         → Create custom objects (if needed)                 │
│  4. sf-apex             → Create @InvocableMethod (if custom logic)         │
│  5. sf-flow             → Create HTTP Callout Flow or Apex wrapper          │
│  6. sf-deploy           → Deploy all metadata (FIRST DEPLOYMENT)            │
│  7. sf-ai-agentforce  ◀── Create agent with flow:// target                 │
│  8. sf-deploy           → Publish agent (SECOND DEPLOYMENT)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ MANDATORY Skill Delegations

| Requirement | Skill to Use | Why |
|-------------|--------------|-----|
| **Flow Creation** | `Skill(skill="sf-flow")` | 110-point validation, proper XML |
| **Apex Creation** | `Skill(skill="sf-apex")` | 150-point validation, best practices |
| **ALL Deployments** | `Skill(skill="sf-deploy")` | Centralized deployment |

**Never manually write Flow or Apex XML** - delegate to specialized skills.

---

## Flow Integration Workflow

```
Step 1: Create Flow
        Skill(skill="sf-flow", args="Create Autolaunched Flow for agent")
        ↓
Step 2: Deploy Flow
        Skill(skill="sf-deploy", args="Deploy flow to [org]")
        ↓
Step 3: Create Agent (reference Flow)
        actions:
           get_account:
              target: "flow://Get_Account_Info"
        ↓
Step 4: Publish Agent
        Skill(skill="sf-deploy", args="Publish agent [AgentName]")
```

---

## Apex Integration (via Flow Wrapper)

`apex://` targets **don't work** in AiAuthoringBundle. Use Flow wrapper pattern:

```
Step 1: Create Apex @InvocableMethod
        Skill(skill="sf-apex", args="Create InvocableMethod for case creation")
        ↓
Step 2: Deploy Apex
        Skill(skill="sf-deploy", args="Deploy ApexClass")
        ↓
Step 3: Create Flow Wrapper (calls Apex)
        Skill(skill="sf-flow", args="Create Flow wrapper for CaseService")
        ↓
Step 4: Deploy Flow Wrapper
        Skill(skill="sf-deploy", args="Deploy flow")
        ↓
Step 5: Reference Flow in Agent
        target: "flow://Create_Support_Case"  # Flow that wraps Apex
```

---

## Common Errors from Wrong Order

| Error | Cause | Fix |
|-------|-------|-----|
| `flow://X not found` | Flow not deployed | Deploy Flow before agent |
| `Internal Error` | Flow variable name mismatch | Match agent I/O names to Flow variable names |
| `apex://X not found` | Apex targets don't work | Use Flow wrapper pattern |
| `Invalid reference` | Object not deployed | Deploy metadata before Flow |

---

## Cross-Skill Integration Table

| From sf-ai-agentforce | To Skill | When |
|-----------------------|----------|------|
| → sf-flow | "Create Autolaunched Flow for agent action" |
| → sf-apex | "Create @InvocableMethod for complex logic" |
| → sf-integration | "Create HTTP Callout Flow for external API" |
| → sf-deploy | "Deploy and publish agent" |
| → sf-metadata | "Describe object structure" |

| From Skill | To sf-ai-agentforce | When |
|------------|---------------------|------|
| sf-deploy | → sf-ai-agentforce | "Agent dependencies deployed, ready to create agent" |

---

## Agent Deployment Workflow (Complete)

```bash
# 1. Deploy dependencies (Apex, Flows, Objects)
sf project deploy start --source-dir force-app/main/default/classes --target-org alias
sf project deploy start --source-dir force-app/main/default/flows --target-org alias

# 2. Validate agent syntax
sf agent validate authoring-bundle --api-name AgentName --target-org alias

# 3. Publish agent
sf agent publish authoring-bundle --api-name AgentName --target-org alias

# 4. Verify deployment
sf org open agent --api-name AgentName --target-org alias

# 5. Activate agent
sf agent activate --api-name AgentName --target-org alias
```

---

## Testing Phase (sf-ai-agentforce-testing)

After agent deployment, use **sf-ai-agentforce-testing** for comprehensive validation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENTIC TEST-FIX LOOP                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Generate test spec from agent metadata                                   │
│     └── sf agent generate test-spec  (interactive wizard)                   │
│                                                                             │
│  2. Create and run tests                                                     │
│     └── sf agent test run --api-name [AgentName]_Tests --wait 10            │
│                                                                             │
│  3. IF failures detected:                                                    │
│     └── Parse failure type (topic routing, action, guardrail, escalation)   │
│     └── Call sf-ai-agentforce to apply fix                                  │
│     └── Re-publish agent                                                    │
│     └── Re-run tests (max 3 iterations)                                     │
│                                                                             │
│  4. Report coverage and pass rate                                            │
│     └── Topic coverage, action coverage, guardrail coverage                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Invoke the testing skill:**
```
Skill(skill="sf-ai-agentforce-testing", args="Test agent [AgentName] and fix any failures")
```

See `sf-ai-agentforce-testing/SKILL.md` for full testing workflow.

---

## Related Documentation

| Topic | Location |
|-------|----------|
| Agent Script reference | `sf-ai-agentforce/docs/agent-script-reference.md` |
| CLI guide | `sf-ai-agentforce/docs/cli-guide.md` |
| Actions reference | `sf-ai-agentforce/docs/actions-reference.md` |
| sf-deploy agent guide | `sf-deploy/docs/agent-deployment-guide.md` |
| **Agent testing** | `sf-ai-agentforce-testing/SKILL.md` |
