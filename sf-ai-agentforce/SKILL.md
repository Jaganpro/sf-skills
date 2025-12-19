---
name: sf-ai-agentforce
description: >
  Creates Agentforce agents using Agent Script syntax with 100-point scoring.
  Use when building AI agents, defining topics and actions, or deploying
  AiAuthoringBundle (v65+) or GenAiPlannerBundle (v65+) metadata.
license: MIT
compatibility: "Requires API v65.0+ (Winter '26) for deployment"
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 6 categories"
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document - read this FIRST -->
<!-- Progressive disclosure: SKILL.md → Quick Refs → Detailed Refs → Specialized Guides -->

# sf-ai-agentforce: Agentforce Agent Creation with Agent Script

Expert Agentforce developer specializing in Agent Script syntax, topic design, and action integration. Generate production-ready agents that leverage LLM reasoning with deterministic business logic.

## Core Responsibilities

1. **Agent Creation**: Generate complete Agentforce agents using Agent Script
2. **Topic Management**: Create and configure agent topics with proper transitions
3. **Action Integration**: Connect actions to Flows (directly) or Apex (via Agent Actions)
4. **Validation & Scoring**: Score agents against best practices (0-100 points)
5. **Deployment**: Publish agents using `sf agent publish authoring-bundle`

## 📚 Document Map (Progressive Disclosure)

**Read documents in tier order based on what you need:**

### Tier 2: Quick References
| Need | Document | Description |
|------|----------|-------------|
| **What doesn't work** | [agent-script-quick-reference.md](../../docs/agent-script-quick-reference.md) | AiAuthoringBundle gotchas, error quick reference |
| **Which pattern to use** | [pattern-catalog.md](../../docs/pattern-catalog.md) | Decision tree for choosing patterns |
| **What command to run** | [agent-cli-reference.md](../../docs/agent-cli-reference.md) | sf agent commands, preview, publish |

### Tier 3: Detailed References
| Need | Document | Description |
|------|----------|-------------|
| **Full syntax** | [agent-script-syntax.md](../../docs/agent-script-syntax.md) | Complete Agent Script language spec |
| **Action implementation** | [agent-actions-guide.md](../../docs/agent-actions-guide.md) | Flow, Apex, API, Prompt Template actions |
| **Best practices** | [best-practices.md](../../docs/best-practices.md) | Production-ready agent design |

### Tier 4: Specialized Guides
| Need | Document | Description |
|------|----------|-------------|
| **Escalation/routing** | [connection-block-guide.md](../../docs/connection-block-guide.md) | OmniChannelFlow, human handoff |
| **Prompt templates** | [prompt-template-guide.md](../../docs/prompt-template-guide.md) | PromptTemplate metadata |
| **GenAiFunction metadata** | [genai-function-reference.md](../../docs/genai-function-reference.md) | Wrapping Apex/Flows as actions |
| **Testing/preview** | [agent-preview-guide.md](../../docs/agent-preview-guide.md) | sf agent preview guide |

**⚡ Quick Links:**
- [Key Insights Table](#-key-insights) - Common errors and fixes
- [Scoring System](#scoring-system-100-points) - 6-category validation
- [Required Files Checklist](#required-files-checklist) - Pre-deployment verification

**📚 Official Reference:**
- [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) - Salesforce's official Agent Script examples

---

## 🆕 New Patterns (December 2025)

Patterns added from cross-comparison with official Salesforce agent-script-recipes repository:

| Pattern | Template | Description |
|---------|----------|-------------|
| **Prompt Template Actions** | `patterns/prompt-template-action.agent` | Invoke PromptTemplates directly using `generatePromptResponse://` target |
| **Multi-Step Workflows** | `patterns/multi-step-workflow.agent` | Boolean flags for progress tracking through complex processes |
| **Procedural Instructions** | `patterns/procedural-instructions.agent` | Execute `run @actions.x` inside `instructions:->` for conditional data loading |
| **Topic System Overrides** | `patterns/system-instruction-overrides.agent` | Use `system:` blocks inside topics for persona switching |
| **Input Binding Patterns** | See [best-practices.md](../../docs/best-practices.md) | When to use `...`, `@variables.x`, or fixed values |

### Prompt Template Action Syntax (NEW)

```agentscript
actions:
   Generate_Content:
      description: "Generate AI content using a prompt template"
      inputs:
         # MUST use "Input:" prefix for template variables
         "Input:email": string
            description: "User's email"
            is_required: True
      outputs:
         # Standard output field name
         promptResponse: string
            description: "Generated content"
            is_used_by_planner: True
      # Target protocol for prompt templates
      target: "generatePromptResponse://Template_API_Name"
```

### Topic-Level System Override Syntax (NEW)

```agentscript
topic formal_mode:
   label: "Formal Mode"
   description: "Professional communication"

   # Topic-level system: OVERRIDES global system instructions
   system:
      instructions: "You are a formal business professional. Use professional language."

   reasoning:
      instructions: ->
         | [Formal Mode Engaged]
         | How may I assist you today?
```

---

## ⚠️ CRITICAL: Two Deployment Methods (Tested Dec 2025)

There are **two deployment methods** with **different capabilities**:

| Aspect | GenAiPlannerBundle | AiAuthoringBundle |
|--------|-------------------|-------------------|
| Deploy Command | `sf project deploy start` | `sf agent publish authoring-bundle` |
| **Visible in Agentforce Studio** | ❌ NO | ✅ YES |
| Flow Actions (`flow://`) | ✅ Supported | ✅ Supported (see requirements below) |
| Apex Actions (`apex://`) | ✅ Supported | ⚠️ Limited (class must exist) |
| Escalation (`@utils.escalate with reason`) | ✅ Supported | ❌ NOT Supported (SyntaxError) |
| `run` keyword (action callbacks) | ✅ Supported | ❌ NOT Supported (SyntaxError) |
| `filter_from_agent` (conditional actions) | ✅ Supported | ❌ NOT Supported (SyntaxError) |
| Variables without defaults | ✅ Supported | ✅ Supported |
| Lifecycle blocks (`before/after_reasoning`) | ✅ Supported | ✅ Supported |
| Topic transitions (`@utils.transition`) | ✅ Supported | ✅ Supported |
| Basic escalation (`@utils.escalate`) | ✅ Supported | ✅ Supported |
| API Version | v65.0+ required | v65.0+ required |

**Why the difference?** These methods correspond to two authoring experiences:
- **Script View** (GenAiPlannerBundle): Full Agent Script syntax with utility actions inherent to the script
- **Canvas/Builder View** (AiAuthoringBundle): Low-code visual builder where some utility actions are not yet available

**Recommendation**: Use **AiAuthoringBundle** if you need agents visible in Agentforce Studio. Use **GenAiPlannerBundle** if you need full Agent Script features (`run` keyword, escalate with reason).

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-apex → sf-flow → sf-devops-architect → sf-ai-agentforce** (you are here: sf-ai-agentforce)

**Why this order?**
1. **sf-metadata**: Custom objects/fields must exist before Apex or Flows reference them
2. **sf-apex**: InvocableMethod classes must be deployed before Flow wrappers call them
3. **sf-flow**: Flows must be created AND deployed before agents can reference them
4. **sf-devops-architect**: MANDATORY gateway for ALL deployments (delegates to sf-deploy)
5. **sf-ai-agentforce**: Agent is published LAST after all dependencies are in place

**⚠️ MANDATORY Delegation:**
- **Flows**: ALWAYS use `Skill(skill="sf-flow")` - never manually write Flow XML
- **Deployments**: ALWAYS use `Task(subagent_type="sf-devops-architect")` - never use direct CLI or sf-deploy skill
- **Apex**: ALWAYS use `Skill(skill="sf-apex")` for InvocableMethod classes
- **Agent Publishing**: Route through `sf-devops-architect` which delegates to sf-deploy

❌ NEVER use `Skill(skill="sf-deploy")` directly - always route through sf-devops-architect.

See `shared/docs/orchestration.md` (project root) for cross-skill orchestration details.

---

## ⚠️ CRITICAL: API Version Requirement

**Agent Script requires API v64+ (Summer '25 or later)**

Before creating agents, verify:
```bash
sf org display --target-org [alias] --json | jq '.result.apiVersion'
```

If API version < 64, Agent Script features won't be available.

---

## ⚠️ CRITICAL: File Structure

| Method | Path | Files | Deploy Command |
|--------|------|-------|----------------|
| **AiAuthoringBundle** | `aiAuthoringBundles/[Name]/` | `[Name].agent` + `.bundle-meta.xml` | `sf agent publish authoring-bundle --api-name [Name]` |
| **GenAiPlannerBundle** | `genAiPlannerBundles/[Name]/` | `[Name].genAiPlannerBundle` + `agentScript/[Name]_definition.agent` | `sf project deploy start --source-dir [path]` |

**XML templates**: See `templates/` for bundle-meta.xml and genAiPlannerBundle examples.

⚠️ GenAiPlannerBundle agents do NOT appear in Agentforce Studio UI.

---

## ⚠️ CRITICAL: Indentation Rules

**Agent Script is whitespace-sensitive (like Python/YAML). Use CONSISTENT indentation throughout.**

| Rule | Details |
|------|---------|
| **Tabs (Recommended)** | ✅ Use tabs for easier manual editing and consistent alignment |
| **Spaces** | 2, 3, or 4 spaces also work if used consistently |
| **Mixing** | ❌ NEVER mix tabs and spaces (causes parse errors) |
| **Consistency** | All lines at same nesting level must use same indentation |

**⚠️ RECOMMENDED: Use TAB indentation for all Agent Script files.** Tabs are easier to edit manually and provide consistent visual alignment across editors.

```agentscript
# ✅ RECOMMENDED - consistent tabs (best for manual editing)
config:
	agent_name: "My_Agent"
	description: "My agent description"

variables:
	user_name: mutable string
		description: "The user's name"

# ✅ ALSO CORRECT - consistent spaces (if you prefer)
config:
   agent_name: "My_Agent"

# ❌ WRONG - mixing tabs and spaces
config:
	agent_name: "My_Agent"    # tab
   description: "My agent"    # spaces - PARSE ERROR!
```

**Why Tabs are Recommended:**
- Easier to edit manually in any text editor
- Consistent visual alignment regardless of editor tab width settings
- Single keypress per indentation level
- Clear distinction between indentation levels

---

## Comments Syntax

**Single-line comments** use the `#` (pound/hash) symbol:

```agentscript
# This is a top-level comment
system:
   # Comment explaining the instructions
   instructions: "You are a helpful assistant."

config:
   agent_name: "My_Agent"  # Inline comment
   # This describes the agent
   description: "A helpful assistant"

topic help:
   # This topic handles help requests
   label: "Help"
   description: "Provides assistance"
```

**Notes:**
- Everything after `#` on a line is ignored
- Use comments to document complex logic or business rules
- Comments are recommended for clarity but don't affect execution

---

## ⚠️ CRITICAL: System Instructions Syntax

**System instructions MUST be a single quoted string. The `|` pipe multiline syntax does NOT work in the `system:` block.**

```agentscript
# ✅ CORRECT - Single quoted string
system:
   instructions: "You are a helpful assistant. Be professional and friendly. Never share confidential information."
   messages:
      welcome: "Hello!"
      error: "Sorry, an error occurred."

# ❌ WRONG - Pipe syntax fails with SyntaxError
system:
   instructions:
      | You are a helpful assistant.
      | Be professional.
```

**Note**: The `|` pipe syntax ONLY works inside `reasoning: instructions: ->` blocks within topics.

---

## ⚠️ CRITICAL: Escalation Description

**`@utils.escalate` REQUIRES a `description:` on a separate indented line.**

```agentscript
# ✅ CORRECT - description on separate line
actions:
   escalate_to_human: @utils.escalate
      description: "Transfer to human when customer requests or issue cannot be resolved"

# ❌ WRONG - inline description fails
actions:
   escalate: @utils.escalate "description here"
```

---

## ⚠️ CRITICAL: Reserved Words

**These words CANNOT be used as input/output parameter names OR action names:**

| Reserved Word | Why | Alternative |
|---------------|-----|-------------|
| `description` | Conflicts with `description:` keyword | `case_description`, `item_description` |
| `inputs` | Keyword for action inputs | `input_data`, `request_inputs` |
| `outputs` | Keyword for action outputs | `output_data`, `response_outputs` |
| `target` | Keyword for action target | `destination`, `endpoint` |
| `label` | Keyword for topic label | `display_label`, `title` |
| `source` | Keyword for linked variables | `data_source`, `origin` |
| `escalate` | Reserved for `@utils.escalate` | `go_to_escalate`, `transfer_to_human` |

**Example of Reserved Word Conflict:**
```agentscript
# ❌ WRONG - 'description' conflicts with keyword
inputs:
   description: string
      description: "The description field"

# ✅ CORRECT - Use alternative name
inputs:
   case_description: string
      description: "The description field"
```

---

## ⚠️ CRITICAL: Action Target Syntax (Tested Dec 2025)

### Action Targets by Deployment Method

| Target Type | GenAiPlannerBundle | AiAuthoringBundle |
|-------------|-------------------|-------------------|
| `flow://FlowName` | ✅ Works | ✅ Works (with exact name matching) |
| `apex://ClassName` | ✅ Works | ⚠️ Limited (class must exist) |
| `prompt://TemplateName` | ✅ Works | ⚠️ Requires asset in org |

### ⚠️ CRITICAL: Flow Action Requirements (Both Methods)

**`flow://` actions work in BOTH AiAuthoringBundle and GenAiPlannerBundle**, but require:

1. **EXACT variable name matching** between Agent Script and Flow
2. Flow must be an **Autolaunched Flow** (not Screen Flow)
3. Flow variables must be marked "Available for input" / "Available for output"
4. Flow must be deployed to org **BEFORE** agent publish

**⚠️ The "Internal Error" occurs when input/output names don't match Flow variables!**

```
ERROR: "property account_id was not found in the available list of
        properties: [inp_AccountId]"

This error appears as generic "Internal Error, try again later" in CLI.
```

### ✅ Correct Flow Action Pattern

**Step 1: Create Flow with specific variable names**
```xml
<!-- Get_Account_Info.flow-meta.xml -->
<variables>
    <name>inp_AccountId</name>     <!-- INPUT variable -->
    <dataType>String</dataType>
    <isInput>true</isInput>
    <isOutput>false</isOutput>
</variables>
<variables>
    <name>out_AccountName</name>   <!-- OUTPUT variable -->
    <dataType>String</dataType>
    <isInput>false</isInput>
    <isOutput>true</isOutput>
</variables>
```

**Step 2: Agent Script MUST use EXACT same names**
```agentscript
actions:
   get_account:
      description: "Retrieves account information"
      inputs:
         inp_AccountId: string        # ← MUST match Flow variable name!
            description: "Salesforce Account ID"
      outputs:
         out_AccountName: string      # ← MUST match Flow variable name!
            description: "Account name"
      target: "flow://Get_Account_Info"
```

### ❌ Common Mistake (Causes "Internal Error")

```agentscript
# ❌ WRONG - Names don't match Flow variables
actions:
   get_account:
      inputs:
         account_id: string           # Flow expects "inp_AccountId"!
      outputs:
         account_name: string         # Flow expects "out_AccountName"!
      target: "flow://Get_Account_Info"
```

This will fail with "Internal Error, try again later" because the schema validation fails silently.

### Requirements Summary

| Requirement | Details |
|-------------|---------|
| **Variable Name Matching** | Agent Script input/output names MUST exactly match Flow variable API names |
| **Flow Type** | Must be **Autolaunched Flow** (not Screen Flow) |
| **Flow Variables** | Mark as "Available for input" / "Available for output" |
| **Deploy Order** | Deploy Flow to org BEFORE publishing agent |
| **API Version** | API v65.0+ required for both AiAuthoringBundle and GenAiPlannerBundle |
| **All Inputs Required** | Agent Script must define ALL inputs that Flow expects (missing inputs = Internal Error) |

### ⚠️ CRITICAL: Flow Validation Timing (Tested Dec 2025)

**Flow existence is validated at DEPLOYMENT time, NOT during `sf agent validate`!**

| Command | What It Checks | Flow Validation |
|---------|----------------|-----------------|
| `sf agent validate authoring-bundle` | Syntax only | ❌ Does NOT check if flows exist |
| `sf project deploy start` | Full deployment | ✅ Validates flow existence |

**This means:**
- An agent can **PASS validation** with `sf agent validate authoring-bundle`
- But **FAIL deployment** if the referenced flow doesn't exist in the org

```bash
# ✅ Passes - only checks Agent Script syntax
sf agent validate authoring-bundle --api-name My_Agent --target-org MyOrg
# Status: COMPLETED, Errors: 0

# ❌ Fails - flow doesn't exist in org
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/My_Agent
# Error: "We couldn't find the flow, prompt, or apex class: flow://Missing_Flow"
```

**Best Practice: Always deploy flows BEFORE deploying agents that reference them.**

### ⚠️ CRITICAL: Data Type Mappings (Tested Dec 2025)

**Confirmed working data types between Agent Script and Flow:**

| Agent Script Type | Flow Data Type | Status | Notes |
|-------------------|----------------|--------|-------|
| `string` | String | ✅ Works | Standard text values |
| `number` | Number (scale=0) | ✅ Works | Integer values |
| `number` | Number (scale>0) | ✅ Works | Decimal values (e.g., 3.14) |
| `boolean` | Boolean | ✅ Works | Use `True`/`False` (capitalized) |
| `list[string]` | Text Collection | ✅ Works | Collection with `isCollection=true` |
| `string` | Date | ✅ Works* | *Use String I/O pattern (see below) |
| `string` | DateTime | ✅ Works* | *Use String I/O pattern (see below) |

**⚠️ Date/DateTime Workaround Pattern**

Agent Script does NOT have native `date` or `datetime` types. If you try to connect an Agent Script `string` input to a Flow `Date` or `DateTime` input, it will fail with "Internal Error" because the platform cannot coerce types.

**Solution: Use String I/O pattern**

1. **Flow accepts/returns Strings** (not Date/DateTime)
2. **Flow parses strings internally** using `DATEVALUE()` or `DATETIMEVALUE()`
3. **Flow converts back to string** using `TEXT()` for output

```xml
<!-- Flow with String I/O for Date handling -->
<variables>
    <name>inp_DateString</name>
    <dataType>String</dataType>       <!-- NOT Date -->
    <isInput>true</isInput>
</variables>
<variables>
    <name>out_DateString</name>
    <dataType>String</dataType>       <!-- NOT Date -->
    <isOutput>true</isOutput>
</variables>
<formulas>
    <name>formula_ParseDate</name>
    <dataType>Date</dataType>
    <expression>DATEVALUE({!inp_DateString})</expression>
</formulas>
<formulas>
    <name>formula_DateAsString</name>
    <dataType>String</dataType>
    <expression>TEXT({!formula_ParseDate})</expression>
</formulas>
```

```agentscript
# Agent Script with string type for date
actions:
   process_date:
      inputs:
         inp_DateString: string
            description: "A date value in YYYY-MM-DD format"
      outputs:
         out_DateString: string
            description: "The processed date as string"
      target: "flow://Test_Date_Type_StringIO"
```

**Collection Types (list[string])**

`list[string]` maps directly to Flow Text Collection:

```xml
<variables>
    <name>inp_TextList</name>
    <dataType>String</dataType>
    <isCollection>true</isCollection>  <!-- This makes it a list -->
    <isInput>true</isInput>
</variables>
```

```agentscript
actions:
   process_collection:
      inputs:
         inp_TextList: list[string]
            description: "A list of text values"
      target: "flow://Test_Collection_StringIO"
```

**Important: All Flow inputs must be provided!**

If Flow defines 6 input variables but Agent Script only provides 4, publish fails with "Internal Error":

```
❌ FAILS - Missing inputs
   Flow inputs:    inp_String, inp_Number, inp_Boolean, inp_Date
   Agent inputs:   inp_String, inp_Number, inp_Boolean
   Result: "Internal Error, try again later"

✅ WORKS - All inputs provided
   Flow inputs:    inp_String, inp_Number, inp_Boolean
   Agent inputs:   inp_String, inp_Number, inp_Boolean
   Result: Success
```

### Advanced Action Fields with `object` Type (Tested Dec 2025)

For fine-grained control over action behavior, use the `object` type with `complex_data_type_name` and advanced field attributes.

> **⚠️ Note**: The `filter_from_agent` attribute shown below is **GenAiPlannerBundle only**. It causes "Unexpected 'filter_from_agent'" errors in AiAuthoringBundle. Omit this attribute when using `sf agent publish authoring-bundle`.

```agentscript
actions:
   lookup_order:
      description: "Retrieve order details for a given Order Number."
      inputs:
         order_number: object
            description: "The Order Number the user has provided"
            label: "order_number"
            is_required: False
            is_user_input: False
            complex_data_type_name: "lightning__textType"
      outputs:
         order_id: object
            description: "The Record ID of the Order"
            label: "order_id"
            complex_data_type_name: "lightning__textType"
            filter_from_agent: False
            is_used_by_planner: True
            is_displayable: False
         order_is_current: object
            description: "Whether the order is current"
            label: "order_is_current"
            complex_data_type_name: "lightning__booleanType"
            filter_from_agent: False
            is_used_by_planner: True
            is_displayable: False
      target: "flow://lookup_order"
      label: "Lookup Order"
      require_user_confirmation: False
      include_in_progress_indicator: False
```

**Lightning Data Types (`complex_data_type_name`):**

| Type | Description |
|------|-------------|
| `lightning__textType` | Text/String values |
| `lightning__numberType` | Numeric values |
| `lightning__booleanType` | Boolean True/False |
| `lightning__dateTimeStringType` | DateTime as string |

**Input Field Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_required` | Boolean | Whether the input must be provided |
| `is_user_input` | Boolean | Whether the LLM should collect from user |
| `label` | String | Display label for the field |
| `complex_data_type_name` | String | Lightning data type mapping |

**Output Field Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `filter_from_agent` | Boolean | Hide output from agent reasoning |
| `is_used_by_planner` | Boolean | Whether planner uses this output |
| `is_displayable` | Boolean | Show output to user |
| `complex_data_type_name` | String | Lightning data type mapping |

**Action-Level Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `label` | String | Display name for the action |
| `require_user_confirmation` | Boolean | Ask user before executing |
| `include_in_progress_indicator` | Boolean | Show progress during execution |

**Minimum Required Attributes:**

Only `description` and `complex_data_type_name` are required. All other attributes are optional:

```agentscript
# Minimal object type - works!
inputs:
   input_text: object
      description: "Text input"
      complex_data_type_name: "lightning__textType"
```

**Mixing Simple and Object Types:**

You can mix `string`/`number`/`boolean` with `object` types in the same action:

```agentscript
inputs:
   # Simple type (basic syntax)
   simple_text: string
      description: "A simple text input"
   # Object type (advanced syntax)
   advanced_text: object
      description: "An advanced text input"
      label: "Advanced Text"
      is_required: True
      is_user_input: True
      complex_data_type_name: "lightning__textType"
```

### Apex Actions in GenAiPlannerBundle

**`apex://` targets work in GenAiPlannerBundle if the Apex class exists:**

```agentscript
# ✅ Works in GenAiPlannerBundle (if class exists in org)
target: "apex://CaseCreationService"
```

**The following do NOT work in either method:**
```agentscript
# ❌ DOES NOT WORK - Invalid format
target: "apex://CaseService.createCase"  # No method name allowed
target: "action://Create_Support_Case"   # action:// not supported
```

**RECOMMENDED: Use Flow Wrapper Pattern**

The only reliable way to call Apex from Agent Script is to wrap the Apex in an Autolaunched Flow:

1. **Create Apex class** with `@InvocableMethod` annotation (use sf-apex skill)
2. **Deploy Apex** to org using `sf project deploy start`
3. **Create Autolaunched Flow wrapper** that calls the Apex via Action element:
   ```xml
   <actionCalls>
       <actionName>YourApexClassName</actionName>
       <actionType>apex</actionType>
       <!-- Map input/output variables -->
   </actionCalls>
   ```
4. **Deploy Flow** to org
5. **Reference Flow** in Agent Script:
```agentscript
# ✅ CORRECT - Use flow:// target pointing to Flow wrapper
target: "flow://Create_Support_Case"  # Flow that wraps Apex InvocableMethod
```

**Flow Wrapper Example:**

```xml
<!-- Create_Support_Case.flow-meta.xml -->
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <actionCalls>
        <name>Call_Apex_Service</name>
        <actionName>CaseCreationService</actionName>
        <actionType>apex</actionType>
        <inputParameters>
            <name>subject</name>
            <value><elementReference>inp_Subject</elementReference></value>
        </inputParameters>
        <outputParameters>
            <assignToReference>var_CaseNumber</assignToReference>
            <name>caseNumber</name>
        </outputParameters>
    </actionCalls>
    <!-- ... variables with isInput=true/isOutput=true ... -->
</Flow>
```

**Alternative: GenAiFunction Metadata (Advanced)**

For advanced users, you can deploy Apex actions via GenAiFunction metadata directly to the org, then associate them with agents through GenAiPlugin (topics). This bypasses Agent Script but requires manual metadata management:

```xml
<!-- GenAiFunction structure -->
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <invocationTarget>CaseCreationService</invocationTarget>
    <invocationTargetType>apex</invocationTargetType>
    <!-- ... -->
</GenAiFunction>
```

This approach is NOT recommended for Agent Script-based agents.

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- **Agent purpose**: What job should this agent do?
- **Topics needed**: What categories of actions? (e.g., FAQ, Order Management, Support)
- **Actions required**: Flow-based? Apex-based? External API?
- **Variables**: What state needs to be tracked?
- **System persona**: What tone/behavior should the agent have?

**Then**:
1. Check existing agents: `Glob: **/aiAuthoringBundles/**/*.agent`
2. Check for sfdx-project.json to confirm Salesforce project structure
3. Create TodoWrite tasks

### Phase 2: Template Selection / Design

**Select appropriate pattern** based on requirements:

| Pattern | Use When | Template |
|---------|----------|----------|
| Hello World | Learning / Minimal agent | `templates/getting-started/hello-world.agent` |
| Simple Q&A | Single topic, no actions | `templates/agent/simple-qa.agent` |
| Multi-Topic | Multiple conversation modes | `templates/agent/multi-topic.agent` |
| Action-Based | External integrations needed | `templates/actions/flow-action.agent` |
| Error Handling | Critical operations | `templates/topics/error-handling.agent` |
| Lifecycle Events | Before/after reasoning logic | `templates/patterns/lifecycle-events.agent` |
| Action Callbacks | Guaranteed post-action steps | `templates/patterns/action-callbacks.agent` |
| Bidirectional Routing | Consult specialist, return | `templates/patterns/bidirectional-routing.agent` |
| **Prompt Template Actions** | AI content generation | `templates/patterns/prompt-template-action.agent` |
| **Multi-Step Workflows** | Complex processes with progress | `templates/patterns/multi-step-workflow.agent` |
| **Procedural Instructions** | Conditional data loading | `templates/patterns/procedural-instructions.agent` |
| **System Overrides** | Persona/mode switching | `templates/patterns/system-instruction-overrides.agent` |

**Pattern Decision Guide**: See `docs/pattern-catalog.md` for detailed decision tree.

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/templates/[path]`
2. **Project folder**: `[project-root]/sf-ai-agentforce/templates/[path]`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/templates/single-topic-agent/`

### Phase 3: Generation / Validation

**Create TWO files** at:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml
```

**Required bundle-meta.xml content**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

**Required .agent blocks**:
1. `system:` - Instructions and messages (MUST BE FIRST)
2. `config:` - Agent metadata (agent_name, agent_label, description, default_agent_user)
3. `variables:` - Linked and mutable variables
4. `language:` - Locale settings
5. `start_agent topic_selector:` - Entry point topic with label and description
6. `topic [name]:` - Additional topics (each with label and description)

**Validation Report Format** (6-Category Scoring 0-100):
```
Score: 85/100 ⭐⭐⭐⭐ Very Good
├─ Structure & Syntax:     18/20 (90%)
├─ Topic Design:           16/20 (80%)
├─ Action Integration:     18/20 (90%)
├─ Variable Management:    13/15 (87%)
├─ Instructions Quality:   12/15 (80%)
└─ Security & Guardrails:   8/10 (80%)

Issues:
⚠️ [Syntax] Line 15: Inconsistent indentation (mixing tabs and spaces)
⚠️ [Topic] Missing label for topic 'checkout'
✓ All topic references valid
✓ All variable references valid
```

### Phase 4: Deployment

**Step 1: Deploy Dependencies First (if using Flow/Apex actions)**
```bash
# Deploy Flows
sf project deploy start --metadata Flow --test-level NoTestRun --target-org [alias]

# Deploy Apex classes (if any)
sf project deploy start --metadata ApexClass --test-level NoTestRun --target-org [alias]
```

**Step 2: ⚠️ VALIDATE AGENT (MANDATORY)**

**⚠️ CRITICAL: Always validate before deployment to catch syntax errors early!**

```bash
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]
```

This validation:
- Checks Agent Script syntax and structure
- Verifies all topic references are valid
- Confirms variable declarations are correct
- Takes ~3 seconds (much faster than failed deployments)

**DO NOT proceed to Step 3 if validation fails!** Fix all errors first.

**Step 3: Deploy Agent Bundle**

**Option A: Deploy via Metadata API (Recommended - More Reliable)**
```bash
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
```

**Option B: Publish via Agent CLI (Beta - May fail with HTTP 404)**
```bash
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

**⚠️ CRITICAL: NEW Agents vs UPDATING Existing Agents**

| Operation | Use This Method | Reason |
|-----------|-----------------|--------|
| **Create NEW agent** | `sf agent publish authoring-bundle` | Required to create BotDefinition |
| **Update EXISTING agent** | `sf project deploy start` | More reliable, avoids HTTP 404 |

**HTTP 404 Error is BENIGN for BotDefinition, but BLOCKS UI Visibility**:
- The `sf agent publish authoring-bundle` command may fail with `ERROR_HTTP_404` during "Retrieve Metadata" step
- If "Publish Agent" step completed (✔), the **BotDefinition WAS created** successfully
- However, the **AiAuthoringBundle metadata is NOT deployed** to the org
- This means **agents will be INVISIBLE in Agentforce Studio UI** even though they exist!
- **FIX**: After HTTP 404 error, run `sf project deploy start` to deploy the AiAuthoringBundle metadata:
  ```bash
  sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
  ```
- Verify deployment: `sf org list metadata --metadata-type AiAuthoringBundle --target-org [alias]`

**Workflow for NEW Agents** (with HTTP 404 fix):
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

**Workflow for UPDATING Existing Agents**:
```bash
# Use sf project deploy start (more reliable, no HTTP 404 issues)
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
```

The deploy/publish command:
- Creates Bot, BotVersion, and GenAi metadata
- Deploys the AiAuthoringBundle to the org
- Makes agent visible in Agentforce Studio (after activation)

**Step 4: Verify Deployment**
```bash
# Open agent in Agentforce Studio to verify
sf org open agent --api-name [AgentName] --target-org [alias]

# Or query to confirm agent exists
sf data query --query "SELECT Id, DeveloperName FROM BotDefinition WHERE DeveloperName = '[AgentName]'" --target-org [alias]
```

**Step 5: Activate Agent (When Ready for Production)**
```bash
sf agent activate --api-name [AgentName] --target-org [alias]
```

### Phase 5: Verification

```
✓ Agent Complete: [AgentName]
  Type: Agentforce Agent | API: 65.0+
  Location: force-app/main/default/aiAuthoringBundles/[AgentName]/
  Files: [AgentName].agent, [AgentName].bundle-meta.xml
  Validation: PASSED (Score: XX/100)
  Topics: [N] | Actions: [M] | Variables: [P]
  Published: Yes | Activated: [Yes/No]

Next Steps:
  1. Open in Studio: sf org open agent --api-name [AgentName]
  2. Test in Agentforce Testing Center
  3. Activate when ready: sf agent activate
```

---

## Agent Script Syntax Reference (Essentials)

> **📖 Complete Reference**: See [agent-script-syntax.md](../../docs/agent-script-syntax.md) for full documentation.

### Block Order (CRITICAL)

Blocks MUST appear in this order:
1. `system:` → 2. `config:` → 3. `variables:` → 4. `language:` → 5. `start_agent [name]:` → 6. `topic [name]:`

### Minimal Working Example

```agentscript
system:
	instructions: "You are a helpful assistant. Be professional and friendly."
	messages:
		welcome: "Hello! How can I help you today?"
		error: "I apologize, but I encountered an issue."

config:
	agent_name: "My_Agent"
	default_agent_user: "user@example.com"
	agent_label: "My Agent"
	description: "A helpful assistant agent"

variables:
	EndUserId: linked string
		source: @MessagingSession.MessagingEndUserId
		description: "Messaging End User ID"
	RoutableId: linked string
		source: @MessagingSession.Id
		description: "Messaging Session ID"
	ContactId: linked string
		source: @MessagingEndUser.ContactId
		description: "Contact ID"

language:
	default_locale: "en_US"
	additional_locales: ""
	all_additional_locales: False

start_agent topic_selector:
	label: "Topic Selector"
	description: "Routes users to appropriate topics"

	reasoning:
		instructions: ->
			| Determine what the user needs.
		actions:
			go_help: @utils.transition to @topic.help

topic help:
	label: "Help"
	description: "Provides help to users"

	reasoning:
		instructions: ->
			| Answer the user's question helpfully.
```

### Quick Syntax Reference

| Block | Key Rules |
|-------|-----------|
| **system** | `instructions:` MUST be a single quoted string (NO pipes `\|`) |
| **config** | Use `agent_name` (not `developer_name`). `default_agent_user` must be valid org user. |
| **variables** | Use `number` not `integer/long`. Use `list[type]` not `list<type>`. |
| **language** | Required block - include even if only `en_US`. |
| **topics** | Each topic MUST have both `label:` and `description:`. |
| **instructions** | Use `instructions: ->` (space before arrow). |

### ⚠️ AiAuthoringBundle Limitations (Tested Dec 2025)

| Feature | Status | Workaround |
|---------|--------|------------|
| `run` keyword | ❌ NOT Supported | Use `reasoning.actions` block (LLM chooses) |
| `{!@actions.x}` | ❌ NOT Supported | Define actions with descriptions, LLM auto-selects |
| `@utils.setVariables` | ❌ NOT Supported | Use `set @variables.x = ...` in instructions |
| `@utils.escalate with reason` | ❌ NOT Supported | Use basic `@utils.escalate` with `description:` |
| `integer`, `long` types | ❌ NOT Supported | Use `number` type |
| `list<type>` syntax | ❌ NOT Supported | Use `list[type]` syntax |
| Nested if statements | ❌ NOT Supported | Use flat `and` conditionals |

### Connection Block (for Escalation)

```agentscript
connection messaging:
   outbound_route_type: "OmniChannelFlow"    # MUST be this value!
   outbound_route_name: "Support_Queue_Flow" # Must exist in org
   escalation_message: "Transferring you..."  # REQUIRED field
```

### Resource Access

| Resource | Syntax |
|----------|--------|
| Variables | `@variables.name` |
| Actions | `@actions.name` |
| Topics | `@topic.name` |
| Outputs | `@outputs.field` |
| Utilities | `@utils.transition to`, `@utils.escalate` |

### Action Invocation (Simplified)

```agentscript
# Define action in topic
actions:
   get_account:
      description: "Gets account info"
      inputs:
         account_id: string
            description: "Account ID"
      outputs:
         account_name: string
            description: "Account name"
      target: "flow://Get_Account_Info"

# Invoke in reasoning (LLM chooses when to call)
reasoning:
   instructions: ->
      | Help user look up accounts.
   actions:
      lookup: @actions.get_account
         with account_id=...    # Slot filling
         set @variables.name = @outputs.account_name
```

---

## Scoring System (100 Points)

### Structure & Syntax (20 points)
- Valid Agent Script syntax (-10 if parsing fails)
- Consistent indentation (no mixing tabs/spaces) (-3 per violation)
- Required blocks present (system, config, start_agent, language) (-5 each missing)
- Uses `agent_name` not `developer_name` (-5 if wrong)
- File extension is `.agent` (-5 if wrong)

### Topic Design (20 points)
- All topics have `label:` and `description:` (-3 each missing)
- Logical topic transitions (-3 per orphaned topic)
- Entry point topic exists (start_agent) (-5 if missing)
- Topic names follow snake_case (-2 each violation)

### Action Integration (20 points)
- Valid target format (`flow://` supported, `apex://` NOT supported) (-5 each invalid)
- All inputs have descriptions (-2 each missing)
- All outputs captured appropriately (-2 each unused)
- Action callbacks don't exceed one level (-5 if nested)
- No reserved words used as input/output names (-3 each violation)

### Variable Management (15 points)
- All variables have descriptions (-2 each missing)
- Required linked variables present (EndUserId, RoutableId, ContactId) (-3 each missing)
- Appropriate types used (-2 each mismatch)
- Variable names follow snake_case (-1 each violation)

### Instructions Quality (15 points)
- Uses `instructions: ->` syntax (space before arrow) (-5 if wrong)
- Clear, specific reasoning instructions (-3 if vague)
- Edge cases handled (-3 if missing)
- Template expressions valid (-3 each invalid)

### Security & Guardrails (10 points)
- System-level guardrails present (-5 if missing)
- Sensitive operations have validation (-3 if missing)
- Error messages don't expose internals (-2 each violation)

### Scoring Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Deploy with confidence |
| 80-89 | ⭐⭐⭐⭐ Very Good | Minor improvements suggested |
| 70-79 | ⭐⭐⭐ Good | Review before deploy |
| 60-69 | ⭐⭐ Needs Work | Address issues before deploy |
| <60 | ⭐ Critical | **Block deployment** |

---

## Cross-Skill Integration

### ⚠️ MANDATORY Delegations

| Requirement | Skill/Agent | Why | Never Do |
|-------------|-------------|-----|----------|
| **Flow Creation** | `Skill(skill="sf-flow")` | 110-point validation, proper XML ordering, prevents errors | Manually write Flow XML |
| **ALL Deployments** | `Task(subagent_type="sf-devops-architect")` | Centralized orchestration, dry-run validation, proper ordering | `Skill(skill="sf-deploy")` or direct CLI |

### Flow Integration Workflow

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `Skill(skill="sf-flow")` → Create Autolaunched Flow | Build Flow with inputs/outputs |
| 2 | `Task(subagent_type="sf-devops-architect")` → Deploy Flow | Validate and deploy Flow |
| 3 | Use `target: "flow://FlowApiName"` in Agent Script | Reference Flow as action |
| 4 | `Task(subagent_type="sf-devops-architect")` → Publish agent | Deploy agent |

### Apex Integration (via Flow Wrapper)

**⚠️ `apex://` targets DON'T work in Agent Script. Use Flow Wrapper pattern.**

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `Skill(skill="sf-apex")` → Create `@InvocableMethod` class | Build callable Apex |
| 2 | Deploy Apex via sf-devops-architect | Get Apex in org |
| 3 | `Skill(skill="sf-flow")` → Create wrapper Flow calling Apex | Bridge to Agent Script |
| 4 | Deploy Flow + Publish agent via sf-devops-architect | Complete deployment |
| 5 | Use `target: "flow://WrapperFlowName"` in Agent Script | Reference wrapper Flow |

| Direction | Pattern | Supported |
|-----------|---------|-----------|
| sf-agentforce → sf-flow | Create Flow-based actions | ✅ Full |
| sf-agentforce → sf-apex | Create Apex via Flow wrapper | ✅ Via Flow |
| sf-agentforce → **sf-devops-architect** | Deploy agent metadata | ✅ MANDATORY |
| sf-agentforce → sf-metadata | Query object structure | ✅ Full |
| sf-agentforce → sf-integration | External API actions | ✅ Via Flow |

---

## Agent Actions (Summary)

> **📖 Complete Reference**: See [agent-actions-guide.md](../../docs/agent-actions-guide.md) for detailed implementation of all action types.

### Action Target Summary

| Action Type | Target Syntax | Recommended |
|-------------|---------------|-------------|
| **Flow** (native) | `flow://FlowAPIName` | ✅ Best choice |
| **Apex** (via Flow) | `flow://ApexWrapperFlow` | ✅ Recommended |
| **External API** | `flow://HttpCalloutFlow` | ✅ Via sf-integration |
| **Prompt Template** | Deploy via metadata | ✅ For LLM tasks |

### Key Requirements for Flow Actions

- Flow must be **Autolaunched Flow** (not Screen Flow)
- Variables marked "Available for input/output"
- Variable names **must match** Agent Script input/output names
- Flow must be deployed **BEFORE** agent publish

### Cross-Skill Integration

| Need | Skill | Example |
|------|-------|---------|
| External API | sf-integration | "Create Named Credential for agent API action" |
| Flow wrapper | sf-flow | "Create HTTP Callout Flow for agent" |
| Apex logic | sf-apex | "Create Apex @InvocableMethod for case creation" |
| **Deployment** | **sf-devops-architect** | `Task(subagent_type="sf-devops-architect")` **MANDATORY** |

---

## Common Patterns

### Pattern 1: Simple FAQ Agent
```agentscript
system:
   instructions: "You are a helpful FAQ assistant. Answer questions concisely. Never share confidential information."
   messages:
      welcome: "Hello! I can answer your questions."
      error: "Sorry, I encountered an issue."

config:
   agent_name: "FAQ_Agent"
   default_agent_user: "agent.user@company.com"
   agent_label: "FAQ Agent"
   description: "Answers frequently asked questions"

variables:
   EndUserId: linked string
      source: @MessagingSession.MessagingEndUserId
      description: "Messaging End User ID"
   RoutableId: linked string
      source: @MessagingSession.Id
      description: "Messaging Session ID"
   ContactId: linked string
      source: @MessagingEndUser.ContactId
      description: "Contact ID"

language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False

start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes to FAQ handling"

   reasoning:
      instructions: ->
         | Listen to the user's question.
         | Provide a helpful, accurate response.
```

### Pattern 2: Flow Action with Variable Binding
```agentscript
topic account_lookup:
   label: "Account Lookup"
   description: "Looks up account information using Flow"

   actions:
      get_account:
         description: "Retrieves account information by ID"
         inputs:
            inp_AccountId: string
               description: "The Salesforce Account ID"
         outputs:
            out_AccountName: string
               description: "Account name"
            out_Industry: string
               description: "Account industry"
            out_IsFound: boolean
               description: "Whether account was found"
         target: "flow://Get_Account_Info"

   reasoning:
      instructions: ->
         | Ask for the Account ID if not provided.
         | Use the get_account action to look up the account.
         |
         | if @variables.account_found == True:
         |     | Here is the account: {!@variables.account_name}
         | else:
         |     | Account not found. Please check the ID.
      actions:
         lookup: @actions.get_account
            with inp_AccountId=...
            set @variables.account_name = @outputs.out_AccountName
            set @variables.account_found = @outputs.out_IsFound
         back: @utils.transition to @topic.topic_selector
```

### Pattern 3: Conditional Transitions
```agentscript
topic order_processing:
   label: "Order Processing"
   description: "Processes customer orders"

   reasoning:
      instructions: ->
         if @variables.cart_total <= 0:
            | Your cart is empty. Add items before checkout.
         if @variables.cart_total > 10000:
            set @variables.needs_approval = True
            | Large orders require approval.
      actions:
         process: @actions.create_order
            with items=@variables.cart_items
            available when @variables.cart_total > 0
            available when @variables.needs_approval == False
         get_approval: @utils.transition to @topic.approval
            available when @variables.needs_approval == True
```

---

## SF CLI Agent Commands Reference

Complete CLI reference for Agentforce agent DevOps. For detailed guides, see:
- `docs/agent-cli-reference.md` - Full CLI command reference
- `docs/agent-preview-guide.md` - Preview setup with connected app

### Command Quick Reference

| Command | Purpose |
|---------|---------|
| `sf agent validate authoring-bundle` | Validate Agent Script syntax |
| `sf agent publish authoring-bundle` | Publish authoring bundle |
| `sf agent preview` | Preview agent (simulated/live) |
| `sf agent activate` | Activate published agent |
| `sf agent deactivate` | Deactivate agent for changes |
| `sf org open -f <agent-file>` | Open in Agentforce Builder |
| `sf project retrieve start --metadata Agent:Name` | Sync agent from org |
| `sf project deploy start --metadata Agent:Name` | Deploy agent to org |

> ⚠️ Commands are in beta. Use `--help` to verify flags. See [agent-cli-reference.md](../../docs/agent-cli-reference.md).

### Authoring Commands

```bash
# Validate Agent Script syntax (RECOMMENDED before publish)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Publish agent to org (creates Bot, BotVersion, AiAuthoringBundle metadata)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

> ⚠️ **No `--source-dir` or `--async` flags!** Commands auto-find bundles in DX project.

### Preview Commands

```bash
# Preview with agent selection prompt
sf agent preview --target-org [alias]

# Preview specific agent (simulated mode - default)
sf agent preview --api-name [AgentName] --target-org [alias]

# Preview in live mode (requires connected app)
sf agent preview --api-name [AgentName] --use-live-actions --client-app [AppName] --target-org [alias]

# Preview with debug output saved
sf agent preview --api-name [AgentName] --output-dir ./logs --apex-debug --target-org [alias]
```

**Preview Modes:**
| Mode | Flag | Description |
|------|------|-------------|
| Simulated | (default) | LLM simulates action responses - safe for testing |
| Live | `--use-live-actions` | Uses actual Apex/Flows in org - requires connected app |

**See `docs/agent-preview-guide.md`** for connected app setup instructions.

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

# 8. Preview (live mode - optional, requires connected app)
sf agent preview --api-name [AgentName] --use-live-actions --client-app [App] --target-org [alias]
```

**IMPORTANT**:
- Always run `sf agent validate authoring-bundle` BEFORE deployment to catch errors early (~3 seconds vs minutes for failed deploys)
- If `sf agent publish` fails with HTTP 404, use `sf project deploy start --source-dir` instead - both work for AiAuthoringBundles

---

## Agent Metadata Types Reference

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

## Validation

**Manual validation** (if hooks don't fire):
```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-agentforce/hooks/scripts/validate_agentforce.py <file_path>
```

**Scoring**: 100 points / 6 categories. Minimum 60 (60%) for deployment.

**Hooks not firing?** Check: `CLAUDE_PLUGIN_ROOT` set, hooks.json valid, Python 3 in PATH, file matches pattern `*.agent`.

---

## 🔑 Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| File Extension | `.agentscript` not recognized | Use `.agent` |
| Config Field | `developer_name` causes deploy failure | Use `agent_name` |
| Instructions Syntax | `instructions:->` fails | Use `instructions: ->` (space!) |
| Topic Fields | Missing `label` fails deploy | Add both `label` and `description` |
| Linked Variables | Missing context variables | Add EndUserId, RoutableId, ContactId |
| Language Block | Missing causes deploy failure | Add `language:` block |
| Bundle XML | Missing causes deploy failure | Create `.bundle-meta.xml` file |
| **Indentation Consistency** | **Mixing tabs/spaces causes parse errors** | **Use TABS consistently (recommended) - easier for manual editing** |
| `@variables` is plural | `@variable.x` fails | Use `@variables.x` |
| Boolean capitalization | `true/false` invalid | Use `True/False` |
| **⚠️ Validation Required** | **Skipping validation causes late-stage failures** | **ALWAYS run `sf agent validate authoring-bundle` BEFORE deploy** |
| Deploy Command | `sf agent publish` may fail with HTTP 404 | Use `sf project deploy start --source-dir` as reliable alternative |
| **HTTP 404 UI Visibility** | **HTTP 404 creates Bot but NOT AiAuthoringBundle** | **Run `sf project deploy start` after HTTP 404 to deploy metadata** |
| **System Instructions** | Pipe `\|` syntax fails in system: block | Use single quoted string only |
| **Escalate Description** | Inline description fails | Put `description:` on separate indented line |
| **Agent User** | Invalid user causes "Internal Error" | Use valid org user with proper permissions |
| **Reserved Words** | `description` as input fails | Use alternative names (e.g., `case_description`) |
| **Flow Variable Names** | **Mismatched names cause "Internal Error"** | **Agent Script input/output names MUST match Flow variable API names exactly** |
| **Action Location** | Top-level actions fail | Define actions inside topics |
| **Flow Targets** | `flow://` works in both deployment methods | Ensure Flow deployed before agent publish, names match exactly |
| **`run` Keyword** | Action chaining syntax | Use `run @actions.x` for callbacks (GenAiPlannerBundle only) |
| **Lifecycle Blocks** | before/after_reasoning available | Use for initialization and cleanup |
| **`@utils.set`/`setVariables`** | "Unknown utils declaration type" error | Use `set` keyword in instructions instead (AiAuthoringBundle) |
| **`escalate` Action Name** | "Unexpected 'escalate'" error | `escalate` is reserved - use `go_to_escalate` or `transfer_to_human` |
| **Connection `outbound_route_type`** | Invalid values cause validation errors | MUST be `"OmniChannelFlow"` - not `queue`/`skill`/`agent` |
| **Connection `escalation_message`** | Missing field causes parse errors | REQUIRED when other connection fields are present |
| **Connection OmniChannelFlow** | HTTP 404 at "Publish Agent" step | Referenced flow must exist in org or BotDefinition NOT created |
| **Nested if statements** | Parse errors ("Missing required element", "Unexpected 'else'") | Use flat conditionals with `and` operators instead |
| **Math operators (`+`, `-`)** | Works in set and conditions | `set @variables.x = @variables.x + 1` is valid |
| **Action attributes** | `require_user_confirmation`, `include_in_progress_indicator`, `label` | Work in AiAuthoringBundle (validated Dec 2025) |

---

## Required Files Checklist

Before deployment, ensure you have:

- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent`
- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml`
- [ ] `sfdx-project.json` in project root
- [ ] Valid `default_agent_user` in config block
- [ ] All linked variables (EndUserId, RoutableId, ContactId)
- [ ] Language block present
- [ ] **⚠️ Validation passed**: `sf agent validate authoring-bundle --api-name [AgentName]` returns 0 errors
- [ ] All topics have `label:` and `description:`
- [ ] No reserved words used as input/output names
- [ ] Flow/Apex dependencies deployed to org first

---

## Reference & Dependencies

**Docs**: `docs/` folder (in sf-ai-agentforce) - best-practices, agent-script-syntax
- **Path**: `~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/docs/`

**Dependencies**: sf-deploy (optional) for additional deployment options. Install: `/plugin install github:Jaganpro/sf-skills/sf-deploy`

**Notes**: API 65.0+ required | Agent Script is GA (2025) | Block if score < 60

---

## License

MIT License. See LICENSE file in sf-ai-agentforce folder.
Copyright (c) 2024-2025 Jag Valaiyapathy
