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

## ⚠️ CRITICAL: API Version Requirement

**Agent Script requires API v64+ (Summer '25 or later)**

Before creating agents, verify:
```bash
sf org display --target-org [alias] --json | jq '.result.apiVersion'
```

If API version < 64, Agent Script features won't be available.

---

## ⚠️ CRITICAL: File Extension

**Agent Script files use `.agent` extension (NOT `.agentscript`)**

Files must be placed at:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent
```

Each bundle also requires a metadata XML file:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml
```

---

## ⚠️ CRITICAL: Indentation Rules

**Agent Script uses 4-SPACE indentation (NOT tabs, NOT 3 spaces)**

```agentscript
# ✅ CORRECT - 4 spaces
config:
    developer_name: "My_Agent"
    description: "My agent description"

# ❌ WRONG - 3 spaces (common mistake!)
config:
   developer_name: "My_Agent"
```

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

## ⚠️ CRITICAL: Action Target Syntax

### Flow Actions (SUPPORTED - Works Directly)

**Flow targets work directly with `flow://FlowAPIName` syntax:**

```agentscript
actions:
    get_account:
        description: "Retrieves account information"
        inputs:
            account_id: string
                description: "Salesforce Account ID"
        outputs:
            account_name: string
                description: "Account name"
        target: "flow://Get_Account_Info"  # ✅ Works directly!
```

**Requirements for Flow Integration:**
1. Flow must be an **Autolaunched Flow** (not Screen Flow)
2. Flow variables must be marked "Available for input" / "Available for output"
3. Variable names in Agent Script must match Flow variable API names exactly
4. Flow must be deployed to org BEFORE agent publish

### Apex Actions (USE FLOW WRAPPER - RECOMMENDED)

**⚠️ ONLY `flow://` targets work in Agent Script!**

The following target types do **NOT** work:
```agentscript
# ❌ DOES NOT WORK - Invalid target format
target: "apex://CaseService.createCase"
target: "apex://CaseService"
target: "action://Create_Support_Case"  # Also invalid!
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
| Simple Q&A | Single topic, no actions | `templates/agent/simple-qa.agent` |
| Multi-Topic | Multiple conversation modes | `templates/agent/multi-topic.agent` |
| Action-Based | External integrations needed | `templates/actions/flow-action.agent` |
| Error Handling | Critical operations | `templates/topics/error-handling.agent` |

Load via: `Read: ../../templates/[path]` (relative to SKILL.md location)

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
2. `config:` - Agent metadata (developer_name, agent_label, description, default_agent_user)
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
⚠️ [Syntax] Line 15: Use 4-space indentation, found 3 spaces
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

**Step 2: Validate (Optional but Recommended)**
```bash
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]
```

**Step 3: Publish Agent**
```bash
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

This command:
- Validates the Agent Script syntax
- Creates Bot, BotVersion, and GenAi metadata
- Retrieves generated metadata back to project
- Deploys the AiAuthoringBundle to the org

**Step 4: Open in Agentforce Studio (Optional)**
```bash
sf org open agent --api-name [AgentName] --target-org [alias]
```

**Step 5: Activate Agent (Optional)**
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
    developer_name: "My_Agent"
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
2. `config:` (developer_name, default_agent_user, agent_label, description)
3. `variables:` (linked variables first, then mutable variables)
4. `language:` (locale settings)
5. `start_agent [name]:` (entry point topic)
6. `topic [name]:` (additional topics)

### Config Block

```agentscript
config:
    developer_name: "Agent_API_Name"
    default_agent_user: "user@org.salesforce.com"
    agent_label: "Human Readable Name"
    description: "What this agent does"
```

| Field | Required | Description |
|-------|----------|-------------|
| `developer_name` | Yes | API name (PascalCase with underscores) |
| `default_agent_user` | Yes | Username for agent execution context |
| `agent_label` | Yes | Human-readable name |
| `description` | Yes | What the agent does |

**IMPORTANT**: Use `developer_name`, NOT `agent_name`!

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
    user_name: mutable string
        description: "User's name"
    order_count: mutable number
        description: "Number of items in cart"
    is_verified: mutable boolean
        description: "Whether identity is verified"
```

### Language Block

```agentscript
language:
    default_locale: "en_US"
    additional_locales: ""
    all_additional_locales: False
```

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

**Actions must be defined INSIDE topics**, not at the top level:

```agentscript
topic account_lookup:
    label: "Account Lookup"
    description: "Looks up account information"

    # ✅ CORRECT - Actions inside topic
    actions:
        get_account:
            description: "Retrieves account information"
            inputs:
                account_id: string
                    description: "Salesforce Account ID"
            outputs:
                account_name: string
                    description: "Account name"
                industry: string
                    description: "Account industry"
            target: "flow://Get_Account_Info"

    reasoning:
        instructions: ->
            | Help the user look up account information.
        actions:
            lookup: @actions.get_account
                with account_id=...
                set @variables.account_name = @outputs.account_name
```

### Action Invocation

```agentscript
reasoning:
    actions:
        # LLM fills inputs (...)
        lookup: @actions.get_account
            with account_id=...
            set @variables.account_name = @outputs.account_name

        # Fixed value
        default_lookup: @actions.get_account
            with account_id="001XX000003NGFQ"

        # Variable binding
        bound_lookup: @actions.get_account
            with account_id=@variables.current_account_id
```

### Action Callbacks (Chaining)

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

| Type | Operators |
|------|-----------|
| Comparison | `==`, `!=`, `>`, `<`, `>=`, `<=` |
| Math | `+`, `-` |
| Null check | `is None`, `is not None` |

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
- Correct 4-space indentation (-3 per violation)
- Required blocks present (system, config, start_agent, language) (-5 each missing)
- Uses `developer_name` not `agent_name` (-5 if wrong)
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

### Flow Integration (Fully Supported)

**Workflow:**
```bash
# 1. Create Flow using sf-flow skill
Skill(skill="sf-flow")
Request: "Create an Autolaunched Flow Get_Account_Info with input account_id and outputs account_name, industry"

# 2. Deploy Flow to org
sf project deploy start --metadata Flow --test-level NoTestRun --target-org [alias]

# 3. Create Agent with flow:// target
Skill(skill="sf-agentforce")
Request: "Create an agent that uses flow://Get_Account_Info"

# 4. Publish Agent
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

### Apex Integration (Use Flow Wrapper)

**⚠️ ONLY `flow://` targets work in Agent Script. Use Flow Wrapper pattern for Apex.**

**Workflow:**
```bash
# 1. Create Apex class with @InvocableMethod
Skill(skill="sf-apex")
Request: "Create CaseCreationService with @InvocableMethod createCase"

# 2. Deploy Apex to org
sf project deploy start --metadata ApexClass --test-level NoTestRun --target-org [alias]

# 3. Create Autolaunched Flow wrapper that calls the Apex
Skill(skill="sf-flow")
Request: "Create Autolaunched Flow Create_Support_Case that wraps CaseCreationService Apex"

# 4. Deploy Flow to org
sf project deploy start --metadata Flow --test-level NoTestRun --target-org [alias]

# 5. Reference Flow in Agent Script
target: "flow://Create_Support_Case"  # Flow wrapper that calls Apex

# 6. Publish Agent
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

| Direction | Pattern | Supported |
|-----------|---------|-----------|
| sf-agentforce → sf-flow | Create Flow-based actions | ✅ Full |
| sf-agentforce → sf-apex | Create Apex via Flow wrapper | ✅ Via Flow |
| sf-agentforce → sf-deploy | Deploy agent metadata | ✅ Full |
| sf-agentforce → sf-metadata | Query object structure | ✅ Full |
| sf-agentforce → sf-integration | External API actions | ✅ Via Flow |

---

## Agent Actions (Expanded)

This section covers all four action types supported in Agentforce agents.

### ⚠️ CRITICAL: Action Target Summary

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
    developer_name: "Order_Status_Agent"
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

| From Skill | To Skill | When | Example |
|------------|----------|------|---------|
| sf-ai-agentforce | sf-integration | External API actions | "Create Named Credential for agent API action" |
| sf-ai-agentforce | sf-flow | Flow wrappers for Apex/API | "Create HTTP Callout Flow for agent" |
| sf-ai-agentforce | sf-apex | Business logic @InvocableMethod | "Create Apex for case creation" |
| sf-ai-agentforce | sf-deploy | Deploy all components | "Deploy integration metadata" |

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
    developer_name: "FAQ_Agent"
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

### Pattern 2: Multi-Topic Router
```agentscript
start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes users to appropriate topics"

    reasoning:
        instructions: ->
            | Determine what the user needs help with.
            | Route to the appropriate topic.
        actions:
            orders: @utils.transition to @topic.order_management
            support: @utils.transition to @topic.support
            billing: @utils.transition to @topic.billing

topic order_management:
    label: "Order Management"
    description: "Helps with orders"

    reasoning:
        instructions: ->
            | Help with order-related questions.
        actions:
            back: @utils.transition to @topic.topic_selector
```

### Pattern 3: Flow Action with Variable Binding
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

### Pattern 4: Conditional Transitions
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

## Anti-Patterns

| Anti-Pattern | Issue | Fix |
|--------------|-------|-----|
| Tab indentation | Syntax error | Use 4 spaces |
| `@variable.name` | Wrong syntax | Use `@variables.name` (plural) |
| `agent_name:` in config | Wrong field | Use `developer_name:` |
| `instructions:->` | Missing space | Use `instructions: ->` |
| Missing `label:` | Deployment fails | Add label to all topics |
| Missing linked variables | Missing context | Add EndUserId, RoutableId, ContactId |
| `.agentscript` extension | Wrong format | Use `.agent` extension |
| Nested `run` | Not supported | Flatten to sequential `run` |
| Missing bundle-meta.xml | Deployment fails | Create XML alongside .agent |
| No language block | Deployment fails | Add language block |
| Pipe syntax in system: | SyntaxError | Use single quoted string for system instructions |
| Inline escalate description | SyntaxError | Put `description:` on separate indented line |
| Invalid default_agent_user | Internal Error | Use valid org user with Agentforce permissions |
| `apex://` target | Not supported | Wrap Apex in Flow, use `flow://` |
| `action://` target | Not supported | Wrap Apex in Flow, use `flow://` |
| `description` as input name | Reserved word | Use `case_description` or similar |
| `true`/`false` booleans | Wrong case | Use `True`/`False` |
| Actions at top level | Wrong location | Define actions inside topics |
| Direct Apex call | Only flow:// works | Create Flow wrapper for Apex InvocableMethod |

---

## CLI Commands Reference

```bash
# Validate agent script (optional but recommended)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Publish agent to org (creates Bot, BotVersion, GenAi metadata)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# Open agent in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]

# Preview agent (requires connected app setup)
sf agent preview --api-name [AgentName] --target-org [alias] --client-app [app]

# Update plugin to latest (if commands missing)
sf plugins install @salesforce/plugin-agent@latest
```

**IMPORTANT**: Do NOT use `sf project deploy start` for Agent Script files. The standard Metadata API doesn't support direct `.agent` file deployment. Use `sf agent publish authoring-bundle` instead.

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
| Config Field | `agent_name` causes deploy failure | Use `developer_name` |
| Instructions Syntax | `instructions:->` fails | Use `instructions: ->` (space!) |
| Topic Fields | Missing `label` fails deploy | Add both `label` and `description` |
| Linked Variables | Missing context variables | Add EndUserId, RoutableId, ContactId |
| Language Block | Missing causes deploy failure | Add `language:` block |
| Bundle XML | Missing causes deploy failure | Create `.bundle-meta.xml` file |
| 4-Space Indentation | 3 spaces causes parse errors | Always use 4 spaces |
| `@variables` is plural | `@variable.x` fails | Use `@variables.x` |
| Boolean capitalization | `true/false` invalid | Use `True/False` |
| Deploy Command | `sf project deploy` fails | Use `sf agent publish authoring-bundle` |
| **System Instructions** | Pipe `\|` syntax fails in system: block | Use single quoted string only |
| **Escalate Description** | Inline description fails | Put `description:` on separate indented line |
| **Agent User** | Invalid user causes "Internal Error" | Use valid org user with proper permissions |
| **Reserved Words** | `description` as input fails | Use alternative names (e.g., `case_description`) |
| **Apex Targets** | `apex://` syntax not supported | Wrap Apex in Flow, use `flow://` |
| **Action Targets** | `action://` syntax not supported | Wrap Apex in Flow, use `flow://` |
| **Only flow:// Works** | Only `flow://` targets supported | All actions must use Flow targets |
| **Action Location** | Top-level actions fail | Define actions inside topics |
| **Flow Targets** | `flow://` works directly | Ensure Flow deployed before agent publish |

---

## Required Files Checklist

Before deployment, ensure you have:

- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent`
- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml`
- [ ] `sfdx-project.json` in project root
- [ ] Valid `default_agent_user` in config block
- [ ] All linked variables (EndUserId, RoutableId, ContactId)
- [ ] Language block present
- [ ] All topics have `label:` and `description:`
- [ ] No reserved words used as input/output names
- [ ] Flow/Apex dependencies deployed to org first

---

## Reference & Dependencies

**Docs**: `../../docs/` - best-practices, agent-script-syntax

**Dependencies**: sf-deploy (optional) for additional deployment options. Install: `/plugin install github:Jaganpro/sf-skills/sf-deploy`

**Notes**: API 64.0+ required | Agent Script is GA (2025) | Block if score < 60

---

## License

MIT License. See [LICENSE](../../LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
