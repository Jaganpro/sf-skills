---
name: sf-ai-agentforce
description: Creates Agentforce agents using Agent Script syntax. Generates complete agents with topics, actions, and variables. 100-point scoring across 6 categories. API v64+ required.
---

# sf-ai-agentforce: Agentforce Agent Creation with Agent Script

Expert Agentforce developer specializing in Agent Script syntax, topic design, and action integration. Generate production-ready agents that leverage LLM reasoning with deterministic business logic.

## Core Responsibilities

1. **Agent Creation**: Generate complete Agentforce agents using Agent Script
2. **Topic Management**: Create and configure agent topics with proper transitions
3. **Action Integration**: Connect actions to Flows (directly) or Apex (via Agent Actions)
4. **Validation & Scoring**: Score agents against best practices (0-100 points)
5. **Deployment**: Publish agents using `sf agent publish authoring-bundle`

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
| Variables without defaults | ✅ Supported | ✅ Supported |
| Lifecycle blocks (`before/after_reasoning`) | ✅ Supported | ✅ Supported |
| Topic transitions (`@utils.transition`) | ✅ Supported | ✅ Supported |
| Basic escalation (`@utils.escalate`) | ✅ Supported | ✅ Supported |
| API Version | v65.0+ required | v64.0+ |

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

**These words CANNOT be used as input/output parameter names:**

| Reserved Word | Why | Alternative |
|---------------|-----|-------------|
| `description` | Conflicts with `description:` keyword | `case_description`, `item_description` |
| `inputs` | Keyword for action inputs | `input_data`, `request_inputs` |
| `outputs` | Keyword for action outputs | `output_data`, `response_outputs` |
| `target` | Keyword for action target | `destination`, `endpoint` |
| `label` | Keyword for topic label | `display_label`, `title` |
| `source` | Keyword for linked variables | `data_source`, `origin` |

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
| **API Version** | API v64.0+ for AiAuthoringBundle, v65.0+ for GenAiPlannerBundle |
| **All Inputs Required** | Agent Script must define ALL inputs that Flow expects (missing inputs = Internal Error) |

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

For fine-grained control over action behavior, use the `object` type with `complex_data_type_name` and advanced field attributes:

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

**⚠️ Note**: The `sf agent publish` command is in beta and may fail with HTTP 404 errors. If it fails, use Option A (`sf project deploy start`) which is more reliable. Both methods result in the agent being available in the org.

The deploy/publish command:
- Creates Bot, BotVersion, and GenAi metadata
- Deploys the AiAuthoringBundle to the org
- Makes agent visible in Agentforce Studio

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
  Type: Agentforce Agent | API: 64.0+
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

## Agent Script Syntax Reference

### Complete Working Example

```agentscript
system:
	instructions: "You are a helpful assistant for Acme Corporation. Be professional and friendly. Never share confidential information."
	messages:
		welcome: "Hello! How can I help you today?"
		error: "I apologize, but I encountered an issue. Please try again."

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
	user_query: mutable string
		description: "The user's current question"

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
			| Route to the appropriate topic.
		actions:
			go_to_help: @utils.transition to @topic.help
			go_to_farewell: @utils.transition to @topic.farewell

topic help:
	label: "Help"
	description: "Provides help to users"

	reasoning:
		instructions: ->
			| Answer the user's question helpfully.
			| If you cannot help, offer alternatives.
		actions:
			back_to_selector: @utils.transition to @topic.topic_selector

topic farewell:
	label: "Farewell"
	description: "Ends the conversation gracefully"

	reasoning:
		instructions: ->
			| Thank the user for reaching out.
			| Wish them a great day.
```

### Block Order (CRITICAL)

The blocks MUST appear in this order:
1. `system:` (instructions and messages)
2. `config:` (agent_name, default_agent_user, agent_label, description)
3. `variables:` (linked variables first, then mutable variables)
4. `language:` (locale settings)
5. `start_agent [name]:` (entry point topic)
6. `topic [name]:` (additional topics)

### Config Block

```agentscript
config:
   agent_name: "Agent_API_Name"
   default_agent_user: "user@org.salesforce.com"
   agent_label: "Human Readable Name"
   description: "What this agent does"
```

| Field | Required | Description |
|-------|----------|-------------|
| `agent_name` | Yes | API name (letters, numbers, underscores only, max 80 chars) |
| `default_agent_user` | Yes | Username for agent execution context |
| `agent_label` | Yes | Human-readable name |
| `description` | Yes | What the agent does |

**IMPORTANT**: Use `agent_name` (not `developer_name`)!

**⚠️ default_agent_user Requirements**:
- Must be a valid username in the target org
- User must have Agentforce-related permissions
- Using an invalid user causes "Internal Error" during publish
- Recommended: Use a dedicated service account or admin user with proper licenses

### System Block

```agentscript
system:
   instructions: "Global instructions for the agent. Be helpful and professional."
   messages:
      welcome: "Hello! How can I help you today?"
      error: "I'm sorry, something went wrong. Please try again."
```

**⚠️ IMPORTANT**: System instructions MUST be a single quoted string. The `|` pipe multiline syntax does NOT work in the `system:` block (it only works in `reasoning: instructions: ->`).

```agentscript
# ✅ CORRECT - Single quoted string
system:
   instructions: "You are a helpful assistant. Be professional. Never share secrets."

# ❌ WRONG - Pipe syntax fails in system block
system:
   instructions:
      | You are a helpful assistant.
      | Be professional.
```

### Variables Block

#### Variable Types (Complete Reference)

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text values | `name: mutable string = "John"` |
| `number` | Floating-point (decimals) | `price: mutable number = 99.99` |
| `integer` | Integer values only | `count: mutable integer = 5` |
| `long` | Long integers | `big_num: mutable long = 9999999999` |
| `boolean` | True/False (capitalized!) | `active: mutable boolean = True` |
| `date` | YYYY-MM-DD format | `start: mutable date = 2025-01-15` |
| `datetime` | Full timestamp | `created: mutable datetime` |
| `time` | Time only | `appointment: mutable time` |
| `currency` | Money values | `total: mutable currency` |
| `id` | Salesforce Record ID | `record_id: mutable id` |
| `object` | Complex JSON objects | `data: mutable object = {}` |
| `list[type]` | Collections | `items: mutable list[string]` |

**Note**: Linked variables support only: `string`, `number`, `boolean`, `date`, `id`

#### Variable Declaration Syntax

```
variable_name: [linked|mutable] type [= default_value]
   description: "..."
   [source: @Object.Field]  # Only for linked variables
```

**Linked Variables** (connect to Salesforce data):
```agentscript
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
```

**Mutable Variables** (agent state):
```agentscript
variables:
   # Without defaults - works in both deployment methods (tested Dec 2025)
   user_name: mutable string
      description: "User's name"
   order_count: mutable integer
      description: "Number of items in cart"
   price_total: mutable number
      description: "Total price with decimals"
   is_verified: mutable boolean
      description: "Whether identity is verified"
   appointment_time: mutable time
      description: "Scheduled appointment time"
   birth_date: mutable date
      description: "Customer's date of birth"

   # With explicit defaults - also valid (optional)
   status: mutable string = ""
      description: "Current status"
```

### Language Block

```agentscript
language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False
```

### Connection Block (Optional)

**Required for**: `@utils.escalate` to work with Omni-Channel for human handoff.

```agentscript
connection messaging:
   outbound_route_type: "queue"
   outbound_route_name: "Support_Queue"
```

| Property | Description |
|----------|-------------|
| `outbound_route_type` | Type of routing: `"queue"`, `"skill"`, or `"agent"` |
| `outbound_route_name` | API name of the Omni-Channel queue, skill, or agent |

**Note**: Without a connection block, `@utils.escalate` may not properly route to human agents. Configure this when building agents that need live agent escalation.

### Topic Blocks

**Entry point topic** (required):
```agentscript
start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes users to appropriate topics"

   reasoning:
      instructions: ->
         | Determine what the user needs.
         | Route to the appropriate topic.
      actions:
         go_to_orders: @utils.transition to @topic.orders
         go_to_support: @utils.transition to @topic.support
```

**Additional topics**:
```agentscript
topic orders:
   label: "Order Management"
   description: "Handles order inquiries and processing"

   reasoning:
      instructions: ->
         | Help the user with their order.
         | Provide status updates and assistance.
      actions:
         back_to_menu: @utils.transition to @topic.topic_selector
```

**IMPORTANT**: Each topic MUST have both `label:` and `description:`!

### Resource Access (@ prefix)

| Resource | Syntax | Example |
|----------|--------|---------|
| Variables | `@variables.name` | `@variables.user_name` |
| Actions | `@actions.name` | `@actions.get_weather` |
| Topics | `@topic.name` | `@topic.checkout` |
| Outputs | `@outputs.field` | `@outputs.temperature` |
| Utilities | `@utils.transition` | `@utils.transition to @topic.X` |
| Utilities | `@utils.escalate` | `@utils.escalate` |

### Instructions Syntax

**CRITICAL**: Use `instructions: ->` (space before arrow), NOT `instructions:->`

**Procedural mode** (with logic):
```agentscript
reasoning:
   instructions: ->
      | Determine user intent.
      | Provide helpful response.
      | If unclear, ask clarifying questions.
```

**System instructions** (must be single string):
```agentscript
# ✅ CORRECT - System instructions as single string
system:
   instructions: "You are a helpful assistant. Be professional and courteous. Never share confidential information."
```

**⚠️ NOTE**: The `|` pipe multiline syntax ONLY works inside `reasoning: instructions: ->` blocks, NOT in the top-level `system:` block.

### Action Definitions

**Actions must be defined INSIDE topics**, not at the top level.

#### Action Properties (Complete Reference)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `target` | String | Yes | Executable: `flow://`, `apex://`, `prompt://` |
| `description` | String | Yes | Explains behavior/purpose for LLM decision-making |
| `inputs` | Object | No | Input parameters and requirements |
| `outputs` | Object | No | Return parameters |
| `label` | String | No | Display name (auto-generated from action name if omitted) |
| `available_when` | Expression | No | Conditional availability for the LLM |
| `require_user_confirmation` | Boolean | No | Ask customer to confirm before execution |
| `include_in_progress_indicator` | Boolean | No | Show progress indicator during execution |

#### Output Properties

| Property | Type | Description |
|----------|------|-------------|
| `description` | String | Explains the output parameter |
| `filter_from_agent` | Boolean | Set `True` to hide sensitive data from LLM reasoning context |
| `complex_data_type_name` | String | Lightning data type (e.g., `lightning__textType`) |

**Example with all properties:**

```agentscript
topic account_lookup:
   label: "Account Lookup"
   description: "Looks up account information"

   # ✅ CORRECT - Actions inside topic with full properties
   actions:
      get_account:
         description: "Retrieves account information"
         label: "Get Account"
         require_user_confirmation: False
         include_in_progress_indicator: True
         inputs:
            account_id: string
               description: "Salesforce Account ID"
         outputs:
            account_name: string
               description: "Account name"
            ssn: string
               description: "Social Security Number"
               filter_from_agent: True    # Hide sensitive data from LLM
            industry: string
               description: "Account industry"
         target: "flow://Get_Account_Info"
         available_when: @variables.is_authenticated == True

   reasoning:
      instructions: ->
         | Help the user look up account information.
      actions:
         lookup: @actions.get_account
            with account_id=...
            set @variables.account_name = @outputs.account_name
```

### Action Invocation

**Slot Filling with `...` (Ellipsis)**

The `...` (ellipsis) syntax enables **LLM slot filling** - the agent automatically extracts parameter values from the conversation context.

```agentscript
reasoning:
   actions:
      # SLOT FILLING: LLM extracts value from conversation
      # If user says "Look up account 001ABC", the LLM fills account_id="001ABC"
      lookup: @actions.get_account
         with account_id=...
         set @variables.account_name = @outputs.account_name

      # FIXED VALUE: Always uses this specific value
      default_lookup: @actions.get_account
         with account_id="001XX000003NGFQ"

      # VARIABLE BINDING: Uses value from a variable
      bound_lookup: @actions.get_account
         with account_id=@variables.current_account_id
```

**Input Binding Patterns:**

| Pattern | Syntax | When to Use |
|---------|--------|-------------|
| **Slot Filling** | `with param=...` | LLM extracts from conversation |
| **Fixed Value** | `with param="value"` | Always use a constant |
| **Variable** | `with param=@variables.x` | Use stored state |
| **Output** | `with param=@outputs.x` | Chain from previous action |

**How Slot Filling Works:**
1. User mentions a value in conversation (e.g., "Check order ORD-12345")
2. LLM recognizes this matches an action's input description
3. LLM automatically populates the `...` with the extracted value
4. Action executes with the filled parameter

### Deterministic vs Non-Deterministic Actions

Agent Script supports two invocation methods with different behaviors:

| Method | Syntax | Behavior |
|--------|--------|----------|
| **Deterministic** | `run @actions.x` | Always executes when code path is reached |
| **Non-Deterministic** | `{!@actions.x}` in reasoning | LLM decides whether to execute |

**Deterministic (Always Executes):**
```agentscript
# In before_reasoning, after_reasoning, or action callbacks
before_reasoning:
   run @actions.log_event           # ALWAYS runs
      with event_type="turn_started"

# In action callbacks
process_order: @actions.create_order
   run @actions.send_confirmation   # ALWAYS runs after create_order
```

**Non-Deterministic (LLM Chooses):**
```agentscript
# In reasoning instructions - LLM decides based on context
reasoning:
   instructions: ->
      | Help the user with their order.
      | Use {!@actions.get_order} to look up order details.
      | Use {!@actions.update_order} if they want to modify it.

   # Alternative: actions block - LLM chooses which to call
   actions:
      lookup: @actions.get_order
         with order_id=...
      update: @actions.update_order
         with order_id=...
```

**When to Use Each:**
- **Deterministic (`run`)**: Audit logging, required follow-ups, guaranteed side effects
- **Non-Deterministic (actions block)**: User-driven choices, context-dependent operations

### Action Callbacks (Chaining)

Use the `run` keyword to execute follow-up actions after a primary action completes:

```agentscript
process_order: @actions.create_order
   with items=...
   set @variables.order_id = @outputs.order_id
   run @actions.send_confirmation
      with order_id=@variables.order_id
   run @actions.update_inventory
      with order_id=@variables.order_id
```

**Note**: Only one level of nesting - cannot nest `run` inside `run`.

### Tools (Reasoning Actions)

**Tools** are wrapped actions or utils functions exposed to the LLM for decision-making. They differ from regular actions in how they're invoked.

#### Tools vs Actions

| Aspect | Actions | Tools (Reasoning Actions) |
|--------|---------|---------------------------|
| **Purpose** | Define executable tasks | Expose to LLM for context-based decisions |
| **Binding** | Optional | Required (`with` or `to`) |
| **Availability** | Always | Conditional (`available when`) |
| **Location** | `topic.actions:` block | `reasoning.actions:` block |

#### Tool Definition

Tools are defined in the `reasoning.actions` block and wrap actions with parameter binding:

```agentscript
topic order_management:
   label: "Order Management"
   description: "Manages customer orders"

   # Define the base action
   actions:
      get_order_details:
         description: "Retrieves order information"
         inputs:
            order_id: string
               description: "The order ID"
         outputs:
            status: string
               description: "Order status"
         target: "flow://Get_Order_Details"

   reasoning:
      instructions: ->
         | Help the customer with their order.
         | Look up order details when they provide an order ID.

      # Tools: wrapped actions with binding
      actions:
         # Tool with slot filling
         lookup_order: @actions.get_order_details
            with order_id=...
            available when @variables.has_order_id == True

         # Tool with topic delegation (returns to caller)
         check_shipping: @topic.shipping
            available when @variables.order_status == "shipped"

         # Tool with one-way transition (no return)
         go_to_returns: @utils.transition to @topic.returns
            available when @variables.wants_return == True
```

#### Tool Reference Methods

| Method | Syntax | Behavior |
|--------|--------|----------|
| **Topic Delegation** | `@topic.<name>` | Delegates to topic, returns control after |
| **Transition** | `@utils.transition to` | One-way flow, no return to caller |
| **Action Binding** | `@actions.<name>` | Wraps action with parameter binding |

### Lifecycle Blocks (before_reasoning / after_reasoning)

**NEW**: Use lifecycle blocks for initialization and cleanup logic that runs automatically.

#### ⚠️ CRITICAL SYNTAX RULES for Lifecycle Blocks

| Rule | Details |
|------|---------|
| **Transition Syntax** | Use `transition to` NOT `@utils.transition to` |
| **No Pipe (`\|`)** | The pipe command is NOT supported - use only logic/actions |
| **after_reasoning May Skip** | If a transition occurs mid-topic, `after_reasoning` won't execute |

```agentscript
topic conversation:
   label: "Conversation"
   description: "Main conversation topic"

   # Runs BEFORE each reasoning step - use for initialization, logging, validation
   before_reasoning:
      set @variables.turn_count = @variables.turn_count + 1
      if @variables.turn_count == 1:
         run @actions.get_timestamp
            set @variables.session_start = @outputs.current_timestamp
      # ✅ CORRECT - Use "transition to" in lifecycle blocks
      if @variables.needs_reset == True:
         transition to @topic.reset_session
      run @actions.log_event
         with event_type="reasoning_started"

   # Main reasoning block
   reasoning:
      instructions: ->
         | Respond to the user.
         | Session started: {!@variables.session_start}
         | Current turn: {!@variables.turn_count}

   # Runs AFTER each reasoning step - use for cleanup, analytics, final logging
   # ⚠️ NOTE: This block may NOT run if a transition occurred during reasoning
   after_reasoning:
      run @actions.log_event
         with event_type="reasoning_completed"
```

**❌ Common Mistakes in Lifecycle Blocks:**
```agentscript
# ❌ WRONG - @utils.transition doesn't work in lifecycle blocks
before_reasoning:
   if @variables.expired == True:
      @utils.transition to @topic.expired   # FAILS!

# ❌ WRONG - Pipe (|) is not supported
before_reasoning:
   | Setting up the session...             # FAILS!

# ✅ CORRECT - Use "transition to" (no @utils)
before_reasoning:
   if @variables.expired == True:
      transition to @topic.expired         # WORKS!
```

**When to use:**
- `before_reasoning`: Session initialization, turn counting, pre-validation, state setup, conditional routing
- `after_reasoning`: Cleanup, analytics, audit logging, state updates (note: may not run if transition occurs)

### Variable Setting Utilities

**@utils.setVariables** - Set multiple variables at once:

```agentscript
reasoning:
   actions:
      update_state: @utils.setVariables
         with user_name=...
         with is_verified=True
```

**@utils.set** - Set a single variable with LLM slot filling:

```agentscript
reasoning:
   actions:
      # LLM determines the value based on conversation context
      capture_name: @utils.set
         with user_name=...
         description: "Extract the user's name from the conversation"
```

| Utility | Purpose | Use Case |
|---------|---------|----------|
| `@utils.setVariables` | Set multiple variables | Bulk state updates |
| `@utils.set` | Set single variable with slot filling | LLM-driven data capture |

**Note**: Both support slot filling (`...`) to let the LLM extract values from conversation.

### Topic Transitions

```agentscript
# Simple transition
go_checkout: @utils.transition to @topic.checkout

# Conditional transition
go_checkout: @utils.transition to @topic.checkout
    available when @variables.cart_has_items == True
```

### Escalation to Human

**⚠️ IMPORTANT**: `@utils.escalate` REQUIRES a `description:` on a separate indented line. The description tells the LLM when to trigger escalation.

```agentscript
topic escalation:
   label: "Escalation"
   description: "Handles requests to transfer to a live human agent"

   reasoning:
      instructions: ->
         | If a user explicitly asks to transfer, escalate.
         | Acknowledge and apologize for any inconvenience.
      actions:
         # ✅ CORRECT - description on separate indented line
         escalate_to_human: @utils.escalate
            description: "Transfer to human when customer requests or issue cannot be resolved"

# ❌ WRONG - inline description fails
#     escalate: @utils.escalate "description here"
```

### Conditional Logic

```agentscript
instructions: ->
   if @variables.amount > 10000:
      set @variables.needs_approval = True
      | This amount requires manager approval.
   else:
      set @variables.needs_approval = False
      | Processing your request.

   if @variables.user_name is None:
      | I don't have your name yet. What should I call you?
```

**Boolean Capitalization**: Use `True` and `False` (capital T and F), not `true`/`false`.

### Operators

| Type | Operators | Example |
|------|-----------|---------|
| Comparison | `==`, `!=`, `>`, `<`, `>=`, `<=` | `@variables.count == 10` |
| Logical | `and`, `or`, `not` | `@variables.a and @variables.b` |
| Math | `+`, `-` | `@variables.count + 1` |
| Null check | `is`, `is not` | `@variables.value is None` |

**Logical Operator Examples:**
```agentscript
# AND - both conditions must be true
if @variables.verified == True and @variables.amount > 0:
   | Processing your verified request.

# OR - at least one condition must be true
if @variables.is_vip == True or @variables.amount > 10000:
   | You qualify for premium service.

# NOT - negates the condition
if not @variables.is_blocked:
   | Access granted.
```

### Template Expressions

Use `{!...}` for variable interpolation in instructions:

```agentscript
instructions: ->
   | Hello {!@variables.user_name}!
   | Your account balance is {!@variables.balance}.
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

## Agent Actions (Expanded)

This section covers all four action types. See **Action Target Syntax** section above for deployment method compatibility.

### Action Target Summary

| Action Type | Agent Script Target | Deployment Method | Recommended |
|-------------|---------------------|-------------------|-------------|
| Flow (native) | `flow://FlowAPIName` | Agent Script | ✅ Best choice |
| Apex (via Flow wrapper) | `flow://ApexWrapperFlow` | Agent Script | ✅ Recommended |
| Apex (via GenAiFunction) | N/A (metadata deploy) | Metadata API | ⚠️ Advanced |
| External API | `flow://HttpCalloutFlow` | Agent Script + sf-integration | ✅ Via Flow |
| Prompt Template | N/A (invoked by agent) | Metadata API | ✅ For LLM tasks |

### A. Apex Actions (Direct via GenAiFunction)

**Bypass Agent Script Limitation**: While `apex://` targets don't work in Agent Script, you can deploy Apex actions directly via GenAiFunction metadata.

**Template**: `templates/genai-metadata/genai-function-apex.xml`

**Workflow**:
1. Create Apex class with `@InvocableMethod` annotation
2. Generate GenAiFunction metadata pointing to Apex class
3. Deploy both to org via Metadata API
4. Optionally create GenAiPlugin to group functions
5. Agent discovers function automatically

**Example GenAiFunction Apex invocation**:
```xml
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Create Support Case</masterLabel>
    <description>Creates a support case from user request</description>
    <invocationTarget>CaseCreationService</invocationTarget>
    <invocationTargetType>apex</invocationTargetType>
    <isConfirmationRequired>true</isConfirmationRequired>
    <capability>Create support cases for customers</capability>
    <genAiFunctionParameters>
        <parameterName>Subject</parameterName>
        <parameterType>Input</parameterType>
        <isRequired>true</isRequired>
        <description>Case subject</description>
        <dataType>Text</dataType>
    </genAiFunctionParameters>
</GenAiFunction>
```

**⚠️ NOTE**: This approach works but functions deployed via GenAiFunction are NOT managed via Agent Script. The agent will have access to the function, but it won't appear in your `.agent` file.

### B. API Actions (External Service via sf-integration)

**For agents that need to call external APIs**, use sf-integration to set up the connection:

**Step 1: Create Named Credential (call sf-integration)**
```
Skill(skill="sf-integration")
Request: "Create Named Credential for Stripe API with OAuth 2.0 Client Credentials"
```

**Step 2: Create HTTP Callout Flow wrapper**
```
Skill(skill="sf-flow")
Request: "Create Autolaunched HTTP Callout Flow that calls Stripe_API Named Credential"
```
Or use template: `templates/flows/http-callout-flow.flow-meta.xml`

**Step 3: Reference Flow in Agent Script**
```agentscript
topic payment_lookup:
   label: "Payment Lookup"
   description: "Looks up payment information from Stripe"

   actions:
      check_payment:
         description: "Retrieves payment status from Stripe API"
         inputs:
            payment_id: string
               description: "The Stripe payment ID"
         outputs:
            payment_status: string
               description: "Current payment status"
            amount: string
               description: "Payment amount"
         target: "flow://Get_Stripe_Payment"

   reasoning:
      instructions: ->
         | Ask for the payment ID.
         | Look up the payment status.
         | Report the status and amount to the user.
      actions:
         lookup: @actions.check_payment
            with payment_id=...
            set @variables.payment_status = @outputs.payment_status
```

### C. Flow Actions (Already Working)

Flow actions work directly with `flow://FlowAPIName` syntax. This is the **recommended approach** for most agent actions.

**Templates**:
- `templates/flows/http-callout-flow.flow-meta.xml` - For external API callouts
- Use sf-flow skill for custom Flow creation

**Key Requirements**:
- Flow must be **Autolaunched Flow** (not Screen Flow)
- Variables must be marked "Available for input" / "Available for output"
- Variable names must match Agent Script input/output names exactly
- Flow must be deployed BEFORE agent publish

### D. Prompt Template Actions

**Use Case**: LLM-powered actions for content generation, summarization, or analysis

**Templates**:
- `templates/prompt-templates/basic-prompt-template.promptTemplate-meta.xml`
- `templates/prompt-templates/record-grounded-prompt.promptTemplate-meta.xml`

**Deployment**:
1. Create PromptTemplate metadata
2. Deploy via Metadata API
3. Reference in GenAiFunction or Flow

**Example PromptTemplate for record summarization**:
```xml
<PromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Summarize_Account</fullName>
    <masterLabel>Summarize Account</masterLabel>
    <type>recordSummary</type>
    <objectType>Account</objectType>
    <promptContent>
Summarize this account for a sales rep:
- Name: {!recordName}
- Industry: {!industry}
- Annual Revenue: {!annualRevenue}

Provide 3-4 bullet points highlighting key information.
    </promptContent>
    <promptTemplateVariables>
        <developerName>recordName</developerName>
        <promptTemplateVariableType>recordField</promptTemplateVariableType>
        <objectType>Account</objectType>
        <fieldName>Name</fieldName>
    </promptTemplateVariables>
</PromptTemplate>
```

### Full Example: Agent with External API Integration

**User Request**: "Create an agent that can look up order status from our ERP API"

**Step 1: Create Named Credential (sf-integration)**
```bash
Skill(skill="sf-integration")
Request: "Create Named Credential for ERP API at https://erp.company.com with OAuth 2.0 Client Credentials"
```

**Step 2: Create HTTP Callout Flow (sf-flow)**
```bash
Skill(skill="sf-flow")
Request: "Create Autolaunched Flow Get_Order_Status with input order_id (Text) that calls ERP_API Named Credential GET /orders/{order_id}"
```

**Step 3: Deploy Dependencies (sf-deploy)**
```bash
sf project deploy start --metadata NamedCredential:ERP_API,Flow:Get_Order_Status --target-org [alias]
```

**Step 4: Create Agent with API Action**
```agentscript
system:
   instructions: "You are an order status assistant. Help customers check their order status. Be helpful and professional."
   messages:
      welcome: "Hello! I can help you check your order status."
      error: "Sorry, I couldn't retrieve that information."

config:
   agent_name: "Order_Status_Agent"
   default_agent_user: "agent@company.com"
   agent_label: "Order Status Agent"
   description: "Helps customers check order status from ERP system"

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
   order_status: mutable string
      description: "Current order status"
   expected_delivery: mutable string
      description: "Expected delivery date"

language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False

start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes to order status lookup"

   reasoning:
      instructions: ->
         | Greet the user.
         | Ask for their order ID.
         | Route to order lookup.
      actions:
         check_order: @utils.transition to @topic.order_lookup

topic order_lookup:
   label: "Order Status"
   description: "Looks up order status from ERP system"

   actions:
      get_order:
         description: "Retrieves order status by order ID"
         inputs:
            order_id: string
               description: "The order ID to look up"
         outputs:
            status: string
               description: "Current order status"
            delivery_date: string
               description: "Expected delivery date"
         target: "flow://Get_Order_Status"

   reasoning:
      instructions: ->
         | Ask for the order ID if not provided.
         | Look up the order status.
         | Report the status and expected delivery.
         |
         | if @variables.order_status is None:
         |     | I couldn't find that order. Please verify the order ID.
      actions:
         lookup: @actions.get_order
            with order_id=...
            set @variables.order_status = @outputs.status
            set @variables.expected_delivery = @outputs.delivery_date
         back: @utils.transition to @topic.topic_selector
```

**Step 5: Publish Agent**
```bash
sf agent publish authoring-bundle --api-name Order_Status_Agent --target-org [alias]
```

### Cross-Skill Integration for Actions

| From Skill | To Agent/Skill | When | Example |
|------------|----------------|------|---------|
| sf-ai-agentforce | sf-integration | External API actions | "Create Named Credential for agent API action" |
| sf-ai-agentforce | sf-flow | Flow wrappers for Apex/API | "Create HTTP Callout Flow for agent" |
| sf-ai-agentforce | sf-apex | Business logic @InvocableMethod | "Create Apex for case creation" |
| sf-ai-agentforce | **sf-devops-architect** | Deploy all components | `Task(subagent_type="sf-devops-architect")` - **MANDATORY** |

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
| `sf afdx agent validate` | Validate Agent Script syntax |
| `sf agent publish` | Publish authoring bundle |
| `sf agent preview` | Preview agent (simulated/live) |
| `sf agent activate` | Activate published agent |
| `sf agent deactivate` | Deactivate agent for changes |
| `sf org open agent` | Open in Agentforce Builder |
| `sf project retrieve start --metadata Agent:Name` | Sync agent from org |
| `sf project deploy start --metadata Agent:Name` | Deploy agent to org |

### Authoring Commands

```bash
# Validate Agent Script syntax (RECOMMENDED before publish)
sf afdx agent validate --api-name [AgentName] --target-org [alias]

# Publish agent to org (creates Bot, BotVersion, GenAi metadata)
sf agent publish --api-name [AgentName] --target-org [alias]

# Publish async (don't wait for completion)
sf agent publish --api-name [AgentName] --async --target-org [alias]
```

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
| **System Instructions** | Pipe `\|` syntax fails in system: block | Use single quoted string only |
| **Escalate Description** | Inline description fails | Put `description:` on separate indented line |
| **Agent User** | Invalid user causes "Internal Error" | Use valid org user with proper permissions |
| **Reserved Words** | `description` as input fails | Use alternative names (e.g., `case_description`) |
| **Flow Variable Names** | **Mismatched names cause "Internal Error"** | **Agent Script input/output names MUST match Flow variable API names exactly** |
| **Action Location** | Top-level actions fail | Define actions inside topics |
| **Flow Targets** | `flow://` works in both deployment methods | Ensure Flow deployed before agent publish, names match exactly |
| **`run` Keyword** | Action chaining syntax | Use `run @actions.x` for callbacks (GenAiPlannerBundle only) |
| **Lifecycle Blocks** | before/after_reasoning available | Use for initialization and cleanup |

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

**Notes**: API 64.0+ required | Agent Script is GA (2025) | Block if score < 60

---

## License

MIT License. See LICENSE file in sf-ai-agentforce folder.
Copyright (c) 2024-2025 Jag Valaiyapathy
