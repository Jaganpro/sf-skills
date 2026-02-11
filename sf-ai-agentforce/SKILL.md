---
name: sf-ai-agentforce
description: >
  Standard Agentforce platform skill. Covers Setup UI-based agent building,
  topic/action configuration, PromptTemplate metadata, Einstein Models API,
  GenAiFunction/GenAiPlugin setup, and custom Lightning types.
  For Agent Script DSL development, use sf-ai-agentscript instead.
license: MIT
compatibility: "Requires API v65.0+ (Winter '26)"
metadata:
  version: "2.0.0"
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
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-ai-agentforce"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-ai-agentforce"
      timeout: 5000
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document — read this FIRST -->
<!-- Progressive disclosure: SKILL.md → Detailed Docs (Tier 2–3) -->

# sf-ai-agentforce: Standard Agentforce Platform Development

Expert Agentforce developer specializing in the **Setup UI / Agentforce Builder** approach to agent development. Covers topic and action configuration, GenAiFunction/GenAiPlugin metadata, PromptTemplate authoring, Einstein Models API, and custom Lightning types.

> **Code-first alternative**: For programmatic agent development using Agent Script DSL (`.agent` files), use **sf-ai-agentscript** instead. This skill covers the declarative, UI-driven approach.

---

## Overview

Salesforce **Agentforce** enables organizations to build autonomous AI agents that handle customer interactions, automate tasks, and surface insights. This skill focuses on the **standard platform approach**:

- **Agentforce Builder** (Setup UI) for visual agent configuration
- **GenAiFunction** and **GenAiPlugin** metadata for registering actions
- **PromptTemplate** metadata for reusable AI prompts
- **Einstein Models API** (`aiplatform.ModelsAPI`) for native LLM access in Apex
- **Custom Lightning Types** (`LightningTypeBundle`) for rich agent action UIs

### Two Approaches to Agentforce

| Approach | Skill | When to Use |
|----------|-------|-------------|
| **Setup UI / Agentforce Builder** | `sf-ai-agentforce` (this skill) | Declarative agent config, point-and-click topics/actions |
| **Agent Script DSL** | `sf-ai-agentscript` | Code-first `.agent` files, FSM architecture, version-controlled agents |

Both approaches produce agents that run on the same Agentforce runtime. Choose based on team preference and complexity requirements.

---

## Core Concepts

### Topics

Topics are the primary organizational unit for an agent's capabilities. Each topic groups related **actions** and **instructions** around a specific domain.

- **Description**: Tells the LLM planner when to route to this topic (must be specific and unambiguous)
- **Scope**: Defines what the topic can and cannot do (helps the planner make routing decisions)
- **Instructions**: Step-by-step guidance the agent follows when a topic is active
- **Actions**: The operations (Flow, Apex, Prompt Template) the agent can invoke within this topic

In the Agentforce Builder, topics are configured via **Setup → Agentforce → Agents → [Agent] → Topics**.

### Actions

Actions are the executable operations an agent can perform. Each action wraps an underlying invocation target:

| Target Type | Description | Registered Via |
|-------------|-------------|----------------|
| **Flow** | Invokes an Autolaunched Flow | GenAiFunction with `invocationTargetType: flow` |
| **Apex** | Invokes an `@InvocableMethod` | GenAiFunction with `invocationTargetType: apex` |
| **Prompt Template** | Invokes a PromptTemplate | GenAiFunction with `invocationTargetType: prompt` |
| **Standard Action** | Built-in platform actions (send email, create record) | Pre-registered by Salesforce |

### Instructions

Instructions guide the agent's behavior within a topic. They are natural language directives that tell the LLM:
- What steps to follow
- When to invoke specific actions
- How to handle edge cases and errors
- When to escalate to a human agent

---

## Agent Builder Workflow

### Step-by-Step: Creating an Agent via Setup UI

**1. Navigate to Agentforce Builder**
```
Setup → Agentforce → Agents → New Agent
```

**2. Choose Agent Type**
- **Service Agent** — Customer-facing support and service
- **Employee Agent** — Internal productivity and automation

**3. Add Topics**
For each capability area:
- Provide a clear **Name** and **Description**
- Write **Instructions** that guide the agent's reasoning
- Add a **Scope** statement (what's in/out of bounds)

**4. Configure Actions per Topic**
Assign actions to each topic. Actions can target:
- Autolaunched Flows (most common)
- Apex InvocableMethods (via GenAiFunction)
- Prompt Templates (for LLM-generated content)
- Standard platform actions

**5. Set Action Inputs & Outputs**
For each action:
- Define **inputs** the agent collects from the user (slot filling)
- Define **outputs** the agent uses in its response
- Mark which outputs are **displayable** to the user

**6. Configure Agent-Level Settings**
- **System Instructions**: Global persona and behavior guidelines
- **Default Agent User**: The running user context for the agent
- **Welcome Message**: Initial greeting
- **Error Message**: Fallback when something goes wrong

**7. Preview & Test**
```bash
# Preview in Agentforce Builder (uses standard org auth)
sf agent preview --api-name MyAgent --target-org MyOrg
```

**8. Publish**
```bash
sf agent publish authoring-bundle --api-name MyAgent --target-org MyOrg

# Publish (skip metadata retrieve for CI/CD pipelines, v2.122.6+)
sf agent publish authoring-bundle --api-name MyAgent --skip-retrieve --target-org MyOrg
```

---

## GenAiFunction & GenAiPlugin Metadata

### GenAiFunction

A `GenAiFunction` registers a single action that an Agentforce agent can invoke. It wraps an underlying Flow, Apex method, or Prompt Template.

**Metadata XML Structure:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Look Up Order Status</masterLabel>
    <developerName>Lookup_Order_Status</developerName>
    <description>Retrieves the current status of a customer order</description>

    <!-- Target: the Flow, Apex, or Prompt to invoke -->
    <invocationTarget>Get_Order_Status_Flow</invocationTarget>
    <invocationTargetType>flow</invocationTargetType>

    <!-- Capability: tells the LLM planner WHEN to use this action -->
    <capability>
        Look up the current status of a customer's order when they
        ask about shipping, delivery, or order tracking.
    </capability>

    <!-- Inputs: what the agent collects from the user -->
    <genAiFunctionInputs>
        <developerName>orderNumber</developerName>
        <description>The customer's order number</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionInputs>

    <!-- Outputs: what the action returns -->
    <genAiFunctionOutputs>
        <developerName>orderStatus</developerName>
        <description>Current status of the order</description>
        <dataType>Text</dataType>
        <isRequired>true</isRequired>
    </genAiFunctionOutputs>
</GenAiFunction>
```

**File Location:**
```
force-app/main/default/genAiFunctions/Lookup_Order_Status.genAiFunction-meta.xml
```

### Invocation Target Types

| `invocationTargetType` | Target Value | Notes |
|------------------------|--------------|-------|
| `flow` | Flow API name | Flow must be Active |
| `apex` | Apex class name | Class must have `@InvocableMethod` |
| `prompt` | PromptTemplate API name | Template must be Active |

### GenAiPlugin

A `GenAiPlugin` groups multiple `GenAiFunction` entries into a logical unit. This is useful for organizing related actions.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiPlugin xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Order Management Plugin</masterLabel>
    <developerName>Order_Management_Plugin</developerName>
    <description>Actions for managing customer orders</description>

    <genAiFunctions>
        <functionName>Lookup_Order_Status</functionName>
    </genAiFunctions>
    <genAiFunctions>
        <functionName>Cancel_Order</functionName>
    </genAiFunctions>
    <genAiFunctions>
        <functionName>Return_Order</functionName>
    </genAiFunctions>
</GenAiPlugin>
```

**File Location:**
```
force-app/main/default/genAiPlugins/Order_Management_Plugin.genAiPlugin-meta.xml
```

### Deployment Order

1. Deploy the underlying **Flow** / **Apex** / **PromptTemplate** first
2. Deploy **GenAiFunction** metadata (references the targets)
3. Deploy **GenAiPlugin** metadata (references the functions)
4. Publish the **Agent** (references the plugin/functions via topics)

```bash
# Step 1: Deploy targets
sf project deploy start -m "Flow:Get_Order_Status_Flow" --target-org MyOrg

# Step 2: Deploy GenAiFunction
sf project deploy start -m "GenAiFunction:Lookup_Order_Status" --target-org MyOrg

# Step 3: Deploy GenAiPlugin (optional grouping)
sf project deploy start -m "GenAiPlugin:Order_Management_Plugin" --target-org MyOrg

# Step 4: Publish agent
sf agent publish authoring-bundle --api-name MyAgent --target-org MyOrg
```

---

## PromptTemplate Configuration

`PromptTemplate` is the metadata type for creating reusable AI prompts. Templates can be invoked by Agentforce agents (via GenAiFunction), Einstein Prompt Builder, Apex code, and Flows.

**Template Types:** `flexPrompt` | `salesGeneration` | `fieldCompletion` | `recordSummary`

**Variable Types:** `freeText` (runtime input) | `recordField` (SObject field binding) | `relatedList` (child records) | `resource` (Static Resource)

**Key Integration Points:**
- **Agent Action**: Register a GenAiFunction with `invocationTargetType: prompt`
- **Apex**: `ConnectApi.EinsteinLlm.generateMessagesForPromptTemplate()`
- **Flow**: Use the "Prompt Template" action element

> **Full reference**: See [docs/prompt-templates.md](docs/prompt-templates.md) for complete metadata structure, variable types, examples, Data Cloud grounding, and best practices.

---

## Models API

The **Einstein Models API** (`aiplatform.ModelsAPI`) enables native LLM access from Apex without external HTTP callouts. Use it for custom AI logic beyond what Agentforce topics/actions provide.

**Available Models:**
- `sfdc_ai__DefaultOpenAIGPT4OmniMini` — Cost-effective general tasks
- `sfdc_ai__DefaultOpenAIGPT4Omni` — Complex reasoning
- `sfdc_ai__DefaultAnthropic` — Nuanced understanding
- `sfdc_ai__DefaultGoogleGemini` — Multimodal tasks

**Key Patterns:**
- **Queueable** for single-record async AI processing
- **Batch** for bulk processing (scope size 10–20)
- **Platform Events** for notifying completion to LWC/Flow

**Prerequisites:** Einstein Generative AI enabled, API v61.0+, Einstein Generative AI User permission set assigned.

> **Full reference**: See [docs/models-api.md](docs/models-api.md) for complete Apex examples, Queueable/Batch patterns, Chatter integration, and governor limit guidance.

---

## Custom Lightning Types

**Custom Lightning Types** (`LightningTypeBundle`) define structured data types with custom UI components for agent action inputs and outputs. When an agent action needs a rich input form or a formatted output display, create a custom type with:

- **schema.json** — JSON Schema data structure definition
- **editor.json** — Custom input collection UI (lightning components)
- **renderer.json** — Custom output display UI (lightning components)

**Requirements:** API v64.0+ (Fall '25), Enhanced Chat V2 enabled in Service Cloud.

**File Structure:**
```
force-app/main/default/lightningTypeBundles/OrderDetails/
├── schema.json
├── editor.json
├── renderer.json
└── OrderDetails.lightningTypeBundle-meta.xml
```

> **Full reference**: See [docs/custom-lightning-types.md](docs/custom-lightning-types.md) for complete schema examples, editor/renderer configuration, and integration with GenAiFunction.

---

## Orchestration Order

**Prerequisite skills must run in this order:**

```
sf-metadata → sf-apex → sf-flow → sf-ai-agentforce → sf-deploy
```

**Why this order:**

1. **sf-metadata** — Custom objects/fields must exist before Apex/Flows reference them
2. **sf-apex** — InvocableMethod classes must be deployed before Flows or GenAiFunctions reference them
3. **sf-flow** — Flows must be active before GenAiFunctions can target them
4. **sf-ai-agentforce** (this skill) — GenAiFunction/GenAiPlugin metadata and agent configuration
5. **sf-deploy** — Final deployment and agent publishing

**MANDATORY Delegations:**

| Requirement | Delegate To | Why |
|-------------|-------------|-----|
| Flow creation | `Skill(skill="sf-flow")` | 110-point validation, proper XML |
| Apex creation | `Skill(skill="sf-apex")` | InvocableMethod generation, 150-point scoring |
| Deployment | `Skill(skill="sf-deploy")` | Centralized deployment orchestration |

---

## Cross-Skill Integration

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **sf-ai-agentscript** | Agent Script DSL (code-first) | Writing `.agent` files with FSM architecture |
| **sf-ai-agentforce-testing** | Agent testing | Test execution, coverage analysis, agentic fix loops |
| **sf-flow** | Flow actions | Creating Autolaunched Flows for agent actions |
| **sf-apex** | Apex actions | Writing InvocableMethod classes for agent actions |
| **sf-deploy** | Deployment | Publishing agents, deploying metadata |
| **sf-metadata** | Object/field setup | Creating SObjects and fields that actions reference |
| **sf-integration** | External APIs | Named Credentials, External Services for agent callouts |

### Integration Patterns

| Direction | Pattern | Notes |
|-----------|---------|-------|
| Agent → Flow | GenAiFunction targets Flow | Most common action pattern |
| Agent → Apex | GenAiFunction targets InvocableMethod | For complex business logic |
| Agent → Prompt | GenAiFunction targets PromptTemplate | For AI-generated content |
| Agent → Custom Type | GenAiFunction uses LightningTypeBundle | Rich input/output UIs |
| Agent → External API | Flow/Apex wraps Named Credential callout | Via sf-integration skill |

---

## Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| **GenAiFunction requires active target** | Deploying GenAiFunction before its Flow/Apex target | Deploy targets first, then GenAiFunction |
| **PromptTemplate field bindings** | `{!variableName}` must match variable `developerName` exactly | Check spelling and case sensitivity |
| **Custom Lightning Types require v64.0+** | Bundle won't deploy on older API versions | Set `<version>64.0</version>` or higher in package.xml |
| **GenAiPlugin groups functions** | Individual GenAiFunctions must exist before the plugin | Deploy GenAiFunctions before GenAiPlugin |
| **Capability text is critical** | Vague capability descriptions cause poor routing | Write specific, scenario-based capability text |
| **Enhanced Chat V2 for custom types** | Custom type UI won't render without it | Enable Enhanced Chat V2 in Setup → Chat Settings |
| **Models API needs async context** | Synchronous calls in triggers will timeout | Use Queueable with `Database.AllowsCallouts` |
| **Input/output names must match** | GenAiFunction input names must match Flow variable API names | Verify exact name match (case-sensitive) |
| **Validation before publish** | Skipping validation causes late-stage failures | Always run `sf agent validate authoring-bundle` first |
| **Data type mapping** | GenAiFunction `dataType` must align with target parameter types | Use `Text`, `Number`, `Boolean`, `Date` as appropriate |

---

## Scoring System (100 Points)

### Categories

| Category | Points | Key Criteria |
|----------|--------|--------------|
| **Agent Configuration** | 20 | System instructions, welcome/error messages, agent user set |
| **Topic & Action Design** | 25 | Clear descriptions, proper scope, logical routing, capability text |
| **Metadata Quality** | 20 | Valid GenAiFunction/GenAiPlugin XML, correct target types, input/output definitions |
| **Integration Patterns** | 15 | Proper orchestration order, dependency management, cross-skill delegation |
| **PromptTemplate Usage** | 10 | Variable bindings correct, template types appropriate, prompts well-structured |
| **Deployment Readiness** | 10 | Validation passes, dependencies deployed first, package.xml correct |

### Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90–100 | Excellent | Deploy with confidence |
| 80–89 | Very Good | Minor improvements suggested |
| 70–79 | Good | Review before deploy |
| 60–69 | Needs Work | Address issues before deploy |
| < 60 | Critical | **Block deployment** |

### Validation Report Format

```
Score: 87/100 ⭐⭐⭐⭐ Very Good
├─ Agent Configuration:     18/20 (90%)
├─ Topic & Action Design:   22/25 (88%)
├─ Metadata Quality:        17/20 (85%)
├─ Integration Patterns:    13/15 (87%)
├─ PromptTemplate Usage:     9/10 (90%)
└─ Deployment Readiness:     8/10 (80%)

Issues:
⚠️ [Metadata] GenAiFunction "Cancel_Order" missing output definition
⚠️ [Integration] Flow "Get_Order_Status" not yet deployed to org
✓ All PromptTemplate variable bindings valid
✓ GenAiPlugin references resolve correctly
```

---

## Document Map

**Tier 2: Detailed References**

| Document | Description | Read When |
|----------|-------------|-----------|
| [docs/prompt-templates.md](docs/prompt-templates.md) | Complete PromptTemplate metadata, variable types, Data Cloud grounding | Authoring reusable AI prompts |
| [docs/models-api.md](docs/models-api.md) | `aiplatform.ModelsAPI` Apex patterns, Queueable/Batch integration | Building custom AI logic in Apex |
| [docs/custom-lightning-types.md](docs/custom-lightning-types.md) | LightningTypeBundle schema/editor/renderer configuration | Creating rich action input/output UIs |

**Cross-Skill References**

| Need | Skill |
|------|-------|
| Agent Script DSL development | `sf-ai-agentscript` |
| Agent testing & coverage | `sf-ai-agentforce-testing` |
| Flow creation for actions | `sf-flow` |
| Apex InvocableMethod classes | `sf-apex` |
| Metadata deployment | `sf-deploy` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.0.0** | 2026-02-07 | Complete rewrite. Skill refocused on standard Agentforce platform (Setup UI, GenAiFunction/GenAiPlugin, PromptTemplate, Models API, Custom Lightning Types). Agent Script DSL content moved to `sf-ai-agentscript`. |

---

## Sources & Acknowledgments

| Source | Contribution |
|--------|-------------|
| [Salesforce Agentforce Documentation](https://developer.salesforce.com/docs/einstein/genai/overview) | Official platform reference |
| [Salesforce Diaries](https://salesforcediaries.com) | Models API patterns, Custom Lightning Types guide |
| [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) | Official Salesforce examples |
| Jag Valaiyapathy | Skill authoring, scoring system, orchestration design |

---

## License

MIT License. See LICENSE file in sf-ai-agentforce folder.
Copyright (c) 2024–2026 Jag Valaiyapathy
