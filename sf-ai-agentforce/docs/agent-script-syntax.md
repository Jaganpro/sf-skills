# Agent Script Syntax Reference

Complete syntax reference for the Agent Script language used in Agentforce.

**Updated**: December 2025 - Corrected based on actual Salesforce implementation.

---

## File Structure

Agent Script files use the `.agent` extension and contain YAML-like syntax with specific Agent Script keywords.

### ⚠️ CRITICAL: Two Deployment Methods

There are **two deployment methods** with **different capabilities**:

| Aspect | GenAiPlannerBundle | AiAuthoringBundle |
|--------|-------------------|-------------------|
| Deploy Command | `sf project deploy start` | `sf agent publish authoring-bundle` |
| **Visible in Agentforce Studio** | ❌ NO | ✅ YES |
| Flow Actions (`flow://`) | ✅ Supported | ✅ Supported (with exact name matching) |
| Apex Actions (`apex://`) | ✅ Supported | ⚠️ Limited (class must exist) |
| Escalation (`@utils.escalate with reason`) | ✅ Supported (tested Dec 2025) | ❌ NOT Supported (SyntaxError) |
| `run` keyword (action callbacks) | ✅ Supported (tested Dec 2025) | ❌ NOT Supported (SyntaxError) |
| Variables without defaults | ✅ Supported | ✅ Supported (tested Dec 2025) |
| Lifecycle blocks (`before/after_reasoning`) | ✅ Supported | ✅ Supported (tested Dec 2025) |
| Topic transitions (`@utils.transition`) | ✅ Supported | ✅ Supported |
| Basic escalation (`@utils.escalate`) | ✅ Supported | ✅ Supported |
| API Version | v65.0+ required | v64.0+ |

**Why the difference?** These methods correspond to two authoring experiences:
- **Script View** (GenAiPlannerBundle): Full Agent Script syntax with utility actions (transition, set variables, escalate) inherent to the script
- **Canvas/Builder View** (AiAuthoringBundle): Low-code visual builder where some utility actions are not yet available

Salesforce is working on feature parity - future releases will add more actions and variable management to the Canvas view.

---

### AiAuthoringBundle (Visible in Agentforce Studio)

**Use this when**: You need agents visible in Agentforce Studio UI.

**Required Files**:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/
├── [AgentName].agent           # Agent definition
└── [AgentName].bundle-meta.xml # Metadata XML
```

**bundle-meta.xml content**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

---

### GenAiPlannerBundle (Full Feature Support)

**Use this when**: You need flow actions, escalation with reasons, or full Agent Script syntax.

**Required Files**:
```
force-app/main/default/genAiPlannerBundles/[AgentName]/
├── [AgentName].genAiPlannerBundle  # XML manifest
└── agentScript/
    └── [AgentName]_definition.agent  # Agent Script file
```

**genAiPlannerBundle content**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiPlannerBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Agent description</description>
    <masterLabel>Agent Label</masterLabel>
    <plannerType>Atlas__ConcurrentMultiAgentOrchestration</plannerType>
</GenAiPlannerBundle>
```

**⚠️ WARNING**: Agents deployed via GenAiPlannerBundle exist in org metadata but do **NOT appear** in Agentforce Studio UI!

### Block Order (CRITICAL)

Blocks MUST appear in this order:
1. `system:` - Instructions and messages
2. `config:` - Agent metadata
3. `variables:` - Linked and mutable variables
4. `language:` - Locale settings
5. `start_agent [name]:` - Entry point topic
6. `topic [name]:` - Additional topics

### Complete Working Example

```agentscript
system:
   instructions: "You are a helpful assistant. Be professional and friendly."
   messages:
      welcome: "Hello! How can I help you today?"
      error: "I apologize, but I encountered an issue."

config:
   agent_name: "My_Agent"
   default_agent_user: "user@org.salesforce.com"
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
      description: "User's current question"

language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False

start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes users to appropriate topics"

   reasoning:
      instructions: ->
         | Determine user intent and route.
      actions:
         go_help: @utils.transition to @topic.help
         go_farewell: @utils.transition to @topic.farewell

topic help:
   label: "Help"
   description: "Provides help to users"

   reasoning:
      instructions: ->
         | Answer the user's question helpfully.

topic farewell:
   label: "Farewell"
   description: "Ends conversation gracefully"

   reasoning:
      instructions: ->
         | Thank the user and say goodbye.
```

---

## Indentation Rules

**CRITICAL**: Agent Script is whitespace-sensitive (like Python/YAML). Use **CONSISTENT indentation** throughout.

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
	description: "Description"

# ✅ ALSO CORRECT - consistent spaces (if you prefer)
config:
   agent_name: "My_Agent"
   description: "Description"

# ❌ WRONG - mixing tabs and spaces
config:
	agent_name: "My_Agent"    # tab
   description: "My agent"    # spaces - PARSE ERROR!
```

---

## Blocks

### System Block

Global agent settings and instructions. **Must be first block**.

```agentscript
system:
   instructions: "You are a helpful assistant. Be professional."
   messages:
      welcome: "Hello! How can I help you today?"
      error: "I'm sorry, something went wrong. Please try again."
```

⚠️ **NOTE**: System instructions must be a single quoted string. The `|` pipe multiline syntax does NOT work in the `system:` block (only in `reasoning: instructions: ->`).

```agentscript
# ✅ CORRECT - Single quoted string
system:
   instructions: "You are a helpful customer service agent. Be professional and courteous. Never share confidential information."
   messages:
      welcome: "Hello!"
      error: "Sorry, an error occurred."
```

### Config Block

Defines agent metadata. **Required fields**: agent_name, default_agent_user, agent_label, description.

**📝 NOTE: No Separate Config File!** All configuration goes directly in the `.agent` file's `config:` block. There is no separate `.agentscript`, `.agentconfig`, or similar config file format.

```agentscript
config:
   agent_name: "Customer_Support_Agent"
   default_agent_user: "agent.user@company.salesforce.com"
   agent_label: "Customer Support"
   description: "Helps customers with orders and inquiries"
```

| Field | Required | Description |
|-------|----------|-------------|
| `agent_name` | Yes | API name (letters, numbers, underscores only) |
| `default_agent_user` | Yes | Username for agent execution context |
| `agent_label` | Yes | Human-readable name |
| `description` | Yes | What the agent does |

**IMPORTANT**: Use `agent_name` (not `developer_name`)!

### Variables Block

Declares state variables. **Linked variables first, then mutable**.

**Linked Variables** (connect to Salesforce data - REQUIRED):
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
   # Without defaults - works in both deployment methods
   user_name: mutable string
      description: "The customer's name"
   order_count: mutable number
      description: "Number of items in cart"
   is_verified: mutable boolean
      description: "Whether identity is verified"

   # With explicit defaults - also valid (optional)
   status: mutable string = ""
      description: "Current status"
   counter: mutable number = 0
      description: "A counter"
```

**Note**: Both syntaxes (with or without defaults) work in **both** GenAiPlannerBundle and AiAuthoringBundle deployments. Tested December 2025.

### Language Block

Locale settings. **Required for deployment**.

```agentscript
language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False
```

### Topic Blocks

Define conversation topics. **Each topic requires `label:` and `description:`**.

**Entry point topic** (required):
```agentscript
start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes users to appropriate topics"

   reasoning:
      instructions: ->
         | Determine user intent and route.
      actions:
         go_orders: @utils.transition to @topic.orders
```

**Regular topic**:
```agentscript
topic orders:
   label: "Order Management"
   description: "Handles order inquiries"

   reasoning:
      instructions: ->
         | Help with order questions.
      actions:
         back: @utils.transition to @topic.topic_selector
```

---

## Variable Types

### Complete Type Reference

| Type | Description | Example | AiAuthoringBundle |
|------|-------------|---------|-------------------|
| `string` | Text values | `name: mutable string = "John"` | ✅ Supported |
| `number` | Numeric (integers & decimals) | `price: mutable number = 99.99` | ✅ Supported |
| `boolean` | True/False (capitalized!) | `active: mutable boolean = True` | ✅ Supported |
| `date` | YYYY-MM-DD format | `start: mutable date = 2025-01-15` | ✅ Supported |
| `datetime` | Full timestamp | `created: mutable datetime` | ✅ Supported |
| `time` | Time only | `appointment: mutable time` | ✅ Supported |
| `currency` | Money values | `total: mutable currency` | ✅ Supported |
| `id` | Salesforce Record ID | `record_id: mutable id` | ✅ Supported |
| `object` | Complex object with Lightning type | See advanced syntax below | ✅ Supported |
| `list[type]` | Array of values | `list[string]`, `list[number]` | ✅ Supported |
| `integer` | Integer values only | `count: mutable integer = 5` | ❌ NOT Supported |
| `long` | Long integers | `big_num: mutable long = 9999999999` | ❌ NOT Supported |

**⚠️ CRITICAL: `integer` and `long` types are NOT supported in AiAuthoringBundle!**
- Validation fails with: "Variable with type integer is not supported for mutable variables"
- Use `number` instead for all numeric values (works for both integers and decimals)

**⚠️ CRITICAL: Collection syntax uses SQUARE BRACKETS, not angle brackets!**
- ✅ CORRECT: `list[string]`, `list[number]`, `list[boolean]`
- ❌ WRONG: `list<string>` (causes "Unexpected '<'" syntax error)
- Only primitive types allowed in lists: `string`, `number`, `boolean`
- `list[object]` is NOT supported

**Notes**:
- Boolean values must be capitalized: `True`, `False`
- Linked variables support only: `string`, `number`, `boolean`, `date`, `id`

### Advanced `object` Type with Lightning Data Types (Tested Dec 2025)

The `object` type enables fine-grained control over action inputs/outputs using Lightning data types:

```agentscript
inputs:
   order_number: object
      description: "The Order Number"
      label: "order_number"
      is_required: False
      is_user_input: False
      complex_data_type_name: "lightning__textType"
outputs:
   order_id: object
      description: "The Record ID"
      label: "order_id"
      complex_data_type_name: "lightning__textType"
      filter_from_agent: False
      is_used_by_planner: True
      is_displayable: False
```

**Lightning Data Types (`complex_data_type_name`):**
- `lightning__textType` - Text/String values
- `lightning__numberType` - Numeric values
- `lightning__booleanType` - Boolean True/False
- `lightning__dateTimeStringType` - DateTime as string

**Input Attributes:** `is_required`, `is_user_input`, `label`, `complex_data_type_name`

**Output Attributes:** `filter_from_agent`, `is_used_by_planner`, `is_displayable`, `complex_data_type_name`

**⚠️ CRITICAL: `filter_from_agent` is NOT supported in AiAuthoringBundle!**
- Causes "Unexpected 'filter_from_agent'" syntax error
- Use conditional topic routing in instructions as alternative
- May work in GenAiPlannerBundle

### Data Type Mappings with Flow (Tested Dec 2025)

| Agent Script Type | Flow Data Type | Status | Notes |
|-------------------|----------------|--------|-------|
| `string` | String | ✅ Works | Standard text values |
| `number` | Number (scale=0) | ✅ Works | Integer values |
| `number` | Number (scale>0) | ✅ Works | Decimal values |
| `boolean` | Boolean | ✅ Works | Use `True`/`False` |
| `list[string]` | Text Collection | ✅ Works | Use `isCollection=true` in Flow |
| `string` | Date | ✅ Works* | *See String I/O pattern below |
| `string` | DateTime | ✅ Works* | *See String I/O pattern below |

**⚠️ All Flow inputs must be provided!** If Flow has more input variables than Agent Script defines, publish fails with "Internal Error".

### Date/DateTime Handling (No Native Types)

Agent Script does NOT have native `date` or `datetime` types. Direct type coercion between `string` (Agent Script) and `Date`/`DateTime` (Flow) will fail.

**Use the String I/O Pattern:**

1. Flow accepts String inputs (not Date/DateTime)
2. Flow parses strings internally with `DATEVALUE()` or `DATETIMEVALUE()`
3. Flow converts back to String for output with `TEXT()`

```xml
<!-- Flow variables use String, not Date -->
<variables>
    <name>inp_DateString</name>
    <dataType>String</dataType>  <!-- NOT Date -->
    <isInput>true</isInput>
</variables>
<formulas>
    <name>parsedDate</name>
    <dataType>Date</dataType>
    <expression>DATEVALUE({!inp_DateString})</expression>
</formulas>
```

```agentscript
# Agent Script uses string type for dates
inputs:
   inp_DateString: string
      description: "Date in YYYY-MM-DD format"
```

---

## Resource References

Use the `@` prefix to reference resources.

| Resource | Syntax | Usage |
|----------|--------|-------|
| Variables | `@variables.name` | Access stored values |
| Actions | `@actions.name` | Invoke defined actions |
| Topics | `@topic.name` | Reference topics |
| Outputs | `@outputs.field` | Action output values |
| Utilities | `@utils.transition` | Built-in utilities |
| Utilities | `@utils.escalate` | Escalate to human |

```agentscript
# Variable reference
if @variables.user_name is None:

# Action reference
invoke: @actions.get_order
    with order_id=@variables.current_order_id

# Topic reference
go: @utils.transition to @topic.checkout

# Output capture
set @variables.status = @outputs.order_status

# Escalation
escalate: @utils.escalate
    description: "Transfer to human agent"
```

---

## Instructions

### Syntax (CRITICAL)

Use `instructions: ->` (with space before arrow), NOT `instructions:->`.

```agentscript
# ✅ CORRECT
reasoning:
   instructions: ->
      | Determine user intent.

# ❌ WRONG - missing space before arrow
reasoning:
   instructions:->
      | Determine user intent.
```

### Prompt Mode (|)

Use `|` for natural language instructions:

```agentscript
instructions: ->
   | This is line one.
   | This is line two.
   | Each line starts with a pipe.
```

### Procedural Mode (->)

Use `->` for logic-based instructions:

```agentscript
instructions: ->
   if @variables.amount > 1000:
      | This is a large order.
   else:
      | Standard order processing.
```

**⚠️ CRITICAL: Pipes Cannot Be Nested Inside Pipes!**

```agentscript
# ❌ WRONG - Nested pipes cause "Start token somehow not of the form | + 2 spaces" error
instructions: ->
   | Some text.
   | if @variables.name is None:
   | 	| Please provide your name.    # NESTED PIPE - FAILS!

# ✅ CORRECT - Conditionals at same level as pipes, not nested inside
instructions: ->
   | Some introductory text.
   if @variables.name is None:
      | Please provide your name.
   | More text continues here.
```

### Template Expressions

Use `{!...}` for variable interpolation:

```agentscript
instructions: ->
   | Hello {!@variables.user_name}!
   | Your order total is ${!@variables.total}.
```

---

## Conditionals

### If/Else

```agentscript
instructions: ->
   if @variables.amount > 1000:
      | Large order - requires approval.
   else:
      | Standard order.

   if @variables.status == "shipped":
      | Your order is on its way!

   if @variables.email is None:
      | Please provide your email address.

   if @variables.verified == True:
      | Identity confirmed.
```

### Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `==` | Equals | `@variables.status == "active"` |
| `!=` | Not equals | `@variables.count != 0` |
| `>` | Greater than | `@variables.amount > 100` |
| `<` | Less than | `@variables.count < 10` |
| `>=` | Greater or equal | `@variables.age >= 18` |
| `<=` | Less or equal | `@variables.priority <= 5` |

### Null Checks

```agentscript
if @variables.name is None:
   | Name not provided.

if @variables.email is not None:
   | Email is available.
```

### Logical Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `and` | Both conditions true | `@variables.a and @variables.b` |
| `or` | At least one true | `@variables.x or @variables.y` |
| `not` | Negation | `not @variables.flag` |

```agentscript
# Combine conditions with AND
if @variables.verified == True and @variables.amount > 0:
   | Processing verified request.

# Check multiple conditions with OR
if @variables.is_vip == True or @variables.loyalty_years > 5:
   | Premium customer detected.

# Negate a condition
if not @variables.is_blocked:
   | Access granted.
```

---

## Comments

Use the `#` symbol to add comments. Everything after `#` on a line is ignored.

```agentscript
# This is a comment - the parser ignores this line
config:
   agent_name: "My_Agent"    # Inline comment explaining the field
   description: "A helpful agent"

# Comments help document your agent script
# Use them to explain complex logic
```

---

## Actions

### Defining Actions

```agentscript
topic my_topic:
   label: "My Topic"
   description: "Topic description"

   actions:
      get_order:
         description: "Retrieves order details"
         inputs:
            order_id: string
               description: "The order ID"
         outputs:
            status: string
               description: "Order status"
            total: number
               description: "Order total"
         target: "flow://Get_Order_Details"

   reasoning:
      instructions: ->
         | Help the user with their order.
```

### Target Formats

**Common Target Types:**

| Type | Format | Example |
|------|--------|---------|
| Flow | `flow://FlowName` | `flow://Get_Order_Details` |
| Apex | `apex://ClassName.methodName` | `apex://OrderService.getOrder` |
| Prompt | `prompt://PromptTemplateName` | `prompt://Customer_Greeting` |
| Quick Action | `quickAction://ObjectName.ActionName` | `quickAction://Case.Close` |
| External Service | `externalService://ServiceName` | `externalService://PaymentAPI` |

**All 22 Valid Action Types:**
```
apex, apexRest, api, auraEnabled, cdpMlPrediction,
createCatalogItemRequest, executeIntegrationProcedure,
expressionSet, externalConnector, externalService, flow,
generatePromptResponse, integrationProcedureAction, mcpTool,
namedQuery, prompt, quickAction, retriever, runExpressionSet,
serviceCatalog, slack, standardInvocableAction
```

### ⚠️ CRITICAL: Flow Action Requirements (Both Methods)

**`flow://` actions work in BOTH AiAuthoringBundle and GenAiPlannerBundle**, but require **EXACT variable name matching**:

```
ERROR: "property account_id was not found in the available list of
        properties: [inp_AccountId]"

This error appears as generic "Internal Error, try again later" in CLI.
```

**The "Internal Error" typically means your Agent Script input/output names don't match the Flow variable names!**

**✅ Correct Pattern:**
```xml
<!-- Flow variable -->
<variables>
    <name>inp_AccountId</name>     <!-- This is the API name -->
    <isInput>true</isInput>
</variables>
```

```agentscript
# Agent Script - MUST use exact same name
inputs:
   inp_AccountId: string           # ← MATCHES Flow variable!
      description: "Account ID"
```

**❌ Wrong Pattern (causes Internal Error):**
```agentscript
# Agent Script - different name fails!
inputs:
   account_id: string              # ← DOES NOT MATCH "inp_AccountId"!
      description: "Account ID"
```

**Requirements for Flow Actions:**
1. Agent Script input/output names **MUST exactly match** Flow variable API names
2. Flow must be **Autolaunched Flow** (not Screen Flow)
3. Flow variables marked "Available for input" / "Available for output"
4. Flow must be deployed to org **BEFORE** agent publish

**⚠️ Flow Validation Timing:**
- `sf agent validate authoring-bundle` checks **syntax only** - does NOT verify flow exists
- `sf project deploy start` validates flow existence at **deployment time**
- Agent can PASS validation but FAIL deployment if flow is missing!

```bash
# ✅ Passes - only checks syntax
sf agent validate authoring-bundle --api-name My_Agent
# Status: COMPLETED, Errors: 0

# ❌ Fails if flow doesn't exist
sf project deploy start --source-dir .../My_Agent
# Error: "We couldn't find the flow: flow://Missing_Flow"
```

### Invoking Actions

```agentscript
reasoning:
   actions:
      # LLM fills input from conversation
      lookup: @actions.get_order
         with order_id=...

      # Fixed value
      default: @actions.get_order
         with order_id="DEFAULT"

      # Variable binding
      bound: @actions.get_order
         with order_id=@variables.current_order_id

      # Capture outputs
      full: @actions.get_order
         with order_id=...
         set @variables.status = @outputs.status
         set @variables.total = @outputs.total
```

### Action Callbacks (Chaining)

```agentscript
process: @actions.create_order
   with items=...
   set @variables.order_id = @outputs.order_id
   run @actions.send_confirmation
      with order_id=@variables.order_id
   run @actions.update_inventory
      with items=@variables.cart_items
```

**Note**: Only one level of `run` nesting is supported.

### Conditional Availability

```agentscript
checkout: @actions.process_payment
   with amount=@variables.total
   available when @variables.cart_count > 0
   available when @variables.verified == True
```

---

## Lifecycle Blocks

Use `before_reasoning` and `after_reasoning` blocks for automatic initialization and cleanup.

### ⚠️ CRITICAL SYNTAX RULES for Lifecycle Blocks

| Rule | Details |
|------|---------|
| **Transition Syntax** | Use `transition to` NOT `@utils.transition to` |
| **No Pipe (`\|`)** | The pipe command is NOT supported - use only logic/actions |
| **after_reasoning May Skip** | If a transition occurs mid-topic, `after_reasoning` won't execute |

```agentscript
# ❌ WRONG - @utils.transition doesn't work in lifecycle blocks
before_reasoning:
   if @variables.expired == True:
      @utils.transition to @topic.expired   # FAILS!

# ✅ CORRECT - Use "transition to" (no @utils)
before_reasoning:
   if @variables.expired == True:
      transition to @topic.expired         # WORKS!
```

### before_reasoning

Runs **BEFORE** each reasoning step. Use for:
- Incrementing turn counters
- Refreshing context data
- Initializing session state
- Conditional routing based on state

```agentscript
topic conversation:
   before_reasoning:
      set @variables.turn_count = @variables.turn_count + 1

      # First turn initialization
      if @variables.turn_count == 1:
         run @actions.get_timestamp
            set @variables.session_start = @outputs.current_timestamp

      # Refresh context every turn
      run @actions.refresh_context
         with user_id=@variables.EndUserId
         set @variables.current_context = @outputs.context

   reasoning:
      instructions: ->
         | Turn {!@variables.turn_count}: Use the context above.
```

### after_reasoning

Runs **AFTER** each reasoning step. Use for:
- Logging analytics
- Updating timestamps
- Cleanup operations

```agentscript
topic conversation:
   reasoning:
      instructions: ->
         | Respond to the user.

   after_reasoning:
      run @actions.log_turn
         with turn_number=@variables.turn_count
         with topic="conversation"

      run @actions.update_last_activity
         set @variables.last_activity = @outputs.timestamp
```

### Block Order

When using lifecycle blocks, the order must be:

1. `before_reasoning:` (optional)
2. `reasoning:` (required)
3. `after_reasoning:` (optional)

```agentscript
topic my_topic:
   label: "My Topic"
   description: "Topic with lifecycle blocks"

   before_reasoning:
      # Runs first
      set @variables.ready = True

   reasoning:
      # Main logic
      instructions: ->
         | Help the user.

   after_reasoning:
      # Runs last
      run @actions.log_event
```

---

## Topic Transitions

### Basic Transition

```agentscript
reasoning:
   actions:
      go_orders: @utils.transition to @topic.orders
```

### Conditional Transition

```agentscript
go_checkout: @utils.transition to @topic.checkout
   available when @variables.cart_count > 0
```

### Escalation to Human

**AiAuthoringBundle** (basic escalation only):
```agentscript
topic escalation:
   label: "Escalation"
   description: "Transfers to human agent"

   reasoning:
      instructions: ->
         | Transfer the conversation to a human.
      actions:
         escalate: @utils.escalate
            description: "Escalate to a human agent"
```

**GenAiPlannerBundle** (supports reason parameter):
```agentscript
reasoning:
   actions:
      escalate_human: @utils.escalate with reason="Customer requested human agent"
```

⚠️ **CRITICAL**: The `with reason="..."` syntax is **ONLY supported in GenAiPlannerBundle**!
- AiAuthoringBundle will fail with `SyntaxError: Unexpected 'with'` or `SyntaxError: Unexpected 'escalate'`
- Use the basic `@utils.escalate` with `description:` for AiAuthoringBundle agents

---

## Deployment

### Choose Your Deployment Method

| Need | Method | Command |
|------|--------|---------|
| Agent visible in Agentforce Studio | AiAuthoringBundle | `sf agent publish authoring-bundle` |
| Flow actions (`flow://`) | GenAiPlannerBundle | `sf project deploy start` |
| Escalation with reason | GenAiPlannerBundle | `sf project deploy start` |
| Variables without defaults | GenAiPlannerBundle | `sf project deploy start` |
| Both visibility AND flow actions | ❌ Not currently possible | - |

---

### AiAuthoringBundle Deployment

**Deploy command**:
```bash
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

This command:
- Validates Agent Script syntax
- Creates Bot, BotVersion, GenAi metadata
- Deploys the AiAuthoringBundle
- **Agent appears in Agentforce Studio** ✅

**Other commands**:
```bash
# Validate without publishing
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Open in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]
```

---

### GenAiPlannerBundle Deployment

**Deploy command**:
```bash
sf project deploy start --source-dir force-app/main/default/genAiPlannerBundles/[AgentName] --target-org [alias]

# Or deploy all agent bundles
sf project deploy start --metadata GenAiPlannerBundle --target-org [alias]
```

This command:
- Deploys agent to org metadata
- Supports full Agent Script syntax (flow actions, escalation with reason)
- ⚠️ **Agent does NOT appear in Agentforce Studio UI**

**Retrieve command**:
```bash
sf project retrieve start --metadata "GenAiPlannerBundle:[AgentName]" --target-org [alias]
```

**Requirements**:
- `sourceApiVersion: "65.0"` or higher in sfdx-project.json
- Flows must be deployed before agent if using `flow://` targets

---

## Common Patterns

### Simple Q&A Agent

```agentscript
system:
   instructions: "You are a helpful FAQ assistant. Answer concisely."
   messages:
      welcome: "Hello! How can I help?"
      error: "Sorry, an error occurred."

config:
   agent_name: "FAQ_Agent"
   default_agent_user: "agent@company.com"
   agent_label: "FAQ Assistant"
   description: "Answers frequently asked questions"

variables:
   EndUserId: linked string
      source: @MessagingSession.MessagingEndUserId
      description: "End User ID"
   RoutableId: linked string
      source: @MessagingSession.Id
      description: "Session ID"
   ContactId: linked string
      source: @MessagingEndUser.ContactId
      description: "Contact ID"

language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False

start_agent topic_selector:
   label: "Topic Selector"
   description: "Handles FAQ questions"

   reasoning:
      instructions: ->
         | Answer the user's question.
         | If unsure, offer to connect them with support.
```

### Multi-Topic Router

```agentscript
start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes to specialized topics"

   reasoning:
      instructions: ->
         | Determine what the user needs.
         | Route to the appropriate topic.
      actions:
         orders: @utils.transition to @topic.orders
         billing: @utils.transition to @topic.billing
         support: @utils.transition to @topic.support
```

### Validation Pattern

```agentscript
instructions: ->
   if @variables.email is None:
      set @variables.valid = False
      | Please provide your email address.

   if @variables.amount <= 0:
      set @variables.valid = False
      | Amount must be greater than zero.

   if @variables.valid == True:
      | All validations passed. Proceeding.
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| Parse error | Invalid syntax | Check indentation consistency (use tabs) |
| Unknown resource | Invalid `@` reference | Use `@variables`, `@actions`, etc. |
| Undefined variable | Variable not declared | Add to `variables:` block |
| Undefined topic | Topic not found | Add topic or fix reference |
| Invalid target | Wrong action target format | Use `flow://` or `apex://` |
| Nested run | `run` inside `run` | Flatten to sequential `run` |
| Missing label | Topic without label | Add `label:` to all topics |
| Wrong config field | Using `developer_name` | Use `agent_name` |
| Missing space | `instructions:->` | Use `instructions: ->` |
| **Internal Error, try again later** | **Flow variable names don't match** | **Ensure Agent Script input/output names EXACTLY match Flow variable API names** |
| SyntaxError: Unexpected 'with' | Escalate with reason in AiAuthoringBundle | Use basic `@utils.escalate` or GenAiPlannerBundle |
| SyntaxError: Unexpected 'escalate' | Invalid escalation syntax in AiAuthoringBundle | Use GenAiPlannerBundle for `with reason=` syntax |
| SyntaxError: Unexpected 'run' | `run` keyword in AiAuthoringBundle | Use GenAiPlannerBundle for action callbacks |

---

## Anti-Patterns

| Anti-Pattern | Issue | Fix |
|--------------|-------|-----|
| Mixed tabs/spaces | Syntax error | Use tabs consistently (recommended) or spaces consistently |
| Inconsistent indentation | Syntax may fail | Ensure same indentation at same nesting level |
| `@variable.name` | Wrong syntax | Use `@variables.name` (plural) |
| `developer_name:` | Wrong field | Use `agent_name:` |
| `instructions:->` | Missing space | Use `instructions: ->` |
| Missing `label:` | Deploy fails | Add label to all topics |
| `.agentscript` | Wrong extension | Use `.agent` |
| No bundle XML | Deploy fails | Create `.bundle-meta.xml` |
| No language block | Deploy fails | Add `language:` block |
| Missing linked vars | Missing context | Add EndUserId, RoutableId, ContactId |
| **Mismatched Flow variable names** | **Internal Error** | **Agent Script input/output names MUST match Flow variable API names exactly** |
| `@utils.escalate with reason=` in AiAuthoringBundle | SyntaxError | Use basic escalation or GenAiPlannerBundle |
| `run` keyword in AiAuthoringBundle | SyntaxError | Use GenAiPlannerBundle for action callbacks |
| Expecting UI visibility with GenAiPlannerBundle | Agent not visible | Use AiAuthoringBundle for UI visibility |
