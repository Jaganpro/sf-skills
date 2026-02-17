# Agent Script Syntax Reference

> Complete syntax guide for the Agent Script DSL. Your entire agent in one `.agent` file.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Declarative Over Imperative** | Describe WHAT the agent should do, not HOW step-by-step |
| **Human-Readable by Design** | Syntax resembles structured English - non-engineers can read it |
| **Single File Portability** | Entire agent definition in one `.agent` file - copy/paste ready |
| **Version Control Friendly** | Plain text works with Git - diff, review, rollback |

---

## Block Structure

### Required Block Order

```
system → config → variables → language → connections → topic → start_agent
```

| Block | Required | Purpose |
|-------|----------|---------|
| `system:` | ✅ Yes | Global messages and instructions |
| `config:` | ✅ Yes | Agent metadata and identification |
| `variables:` | Optional | State management (mutable/linked) |
| `language:` | Optional | Supported languages |
| `connections:` | Optional | External system integrations |
| `topic:` | ✅ Yes | Conversation topics (one or more) |
| `start_agent:` | ✅ Yes | Entry point (exactly one) |

> ✅ **Validated Finding**: Documentation implies strict ordering, but both config-first and system-first orderings compile. Pick one convention and be consistent.

---

## Block Definitions

### 1. system: Block (Required)

```yaml
system:
  messages:
    welcome: "Hello! How can I help?"
    error: "Sorry, something went wrong."
  instructions: "You are a helpful assistant."
```

| Field | Purpose |
|-------|---------|
| `messages.welcome` | Initial greeting message |
| `messages.error` | Fallback error message |
| `instructions` | Global system prompt for the agent |

---

### 2. config: Block (Required)

```yaml
config:
  developer_name: "refund_agent"
  agent_description: "Handles refund requests"
  agent_type: "AgentforceServiceAgent"
  default_agent_user: "admin@yourorg.com"
```

| Field | Required | Purpose |
|-------|----------|---------|
| `developer_name` | ✅ Yes | Internal identifier (must match folder name, case-sensitive) |
| `agent_description` | ✅ Yes | Agent's purpose description |
| `agent_type` | ✅ Yes | `AgentforceServiceAgent` or `AgentforceEmployeeAgent` |
| `default_agent_user` | ⚠️ **REQUIRED** | Must be valid Einstein Agent User |

> ⚠️ **Critical**: `default_agent_user` must exist in the org with the "Einstein Agent User" profile. Query: `SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true`

---

### 3. variables: Block (Optional)

```yaml
variables:
  # Mutable: State we track and modify
  failed_attempts: mutable number = 0
  customer_verified: mutable boolean = False
  order_ids: mutable list[string] = []

  # Linked: Read-only from external sources
  session_id: linked string
    source: @session.sessionID
    description: "Current session identifier"
  customer_id: linked string
    source: @context.customerId
    description: "Customer ID from context"
```

#### Variable Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text values | `name: mutable string = ""` |
| `number` | Numeric values | `count: mutable number = 0` |
| `boolean` | True/false flags | `verified: mutable boolean = False` |
| `object` | Structured data | `data: mutable object = {}` |
| `date` | Calendar dates | `created: mutable date` |
| `timestamp` | Date and time | `updated: mutable timestamp` |
| `currency` | Money values | `amount: mutable currency` |
| `id` | Unique identifiers | `record_id: mutable id` |
| `list[T]` | Arrays of type T | `items: mutable list[string] = []` |

#### Variable Modifiers

| Modifier | Behavior | Use Case |
|----------|----------|----------|
| `mutable` | Read/write - can be changed during conversation | Counters, flags, accumulated state |
| `linked` | Read-only - populated from external source | Session IDs, user profiles, context data |

> ⚠️ **Booleans are capitalized**: Use `True`/`False`, not `true`/`false`

---

### 4. language: Block (Optional)

```yaml
language:
  default: "en_US"
  supported: ["en_US", "es_ES", "fr_FR"]
```

---

### 5. connections: Block (Optional)

```yaml
connections:
  crm_system:
    type: "http"
    credential: "CRM_Named_Credential"
    base_url: "https://api.example.com/v1"
```

#### Connection Types

| Type | Label | Purpose |
|------|-------|---------|
| `http` | API | External REST/SOAP services via Named Credentials |
| `dataCloud` | DATACLOUD | Customer 360 data for personalization |
| `mulesoft` | MULESOFT | Enterprise integrations and API orchestration |
| `flow` | FLOW | Salesforce automation and internal data |

---

### 6. topic: Block (Required - one or more)

```yaml
topic main:
  description: "Main conversation handler"
  reasoning:
    instructions: |
      Help the user with their request.
    actions:
      do_something: @actions.my_action
        description: "Action description"
```

| Field | Purpose |
|-------|---------|
| `description` | Helps LLM understand topic purpose |
| `reasoning.instructions` | Instructions for this topic |
| `reasoning.actions` | Available actions in this topic |

---

### 7. start_agent: Block (Required - exactly one)

```yaml
start_agent entry:
  description: "Entry point for conversations"
  reasoning:
    instructions: |
      Greet the user and route appropriately.
    actions:
      go_main: @utils.transition to @topic.main
        description: "Navigate to main topic"
```

> 💡 The name can be anything - "main", "entry", "topic_selector" - just be consistent.

---

## Instruction Syntax

### Pipe vs Arrow Syntax

| Syntax | Use When | Example |
|--------|----------|---------|
| `instructions: \|` | Simple multi-line text (no expressions) | `instructions: \| Help the user.` |
| `instructions: ->` | Complex logic with conditionals/actions | `instructions: -> if @variables.x:` |

### Arrow Syntax (`->`) Patterns

```yaml
reasoning:
  instructions: ->
    # Conditional (resolves BEFORE LLM)
    if @variables.customer_verified == True:
      | Welcome back, verified customer!
    else:
      | Please verify your identity first.

    # Inline action execution
    run @actions.load_customer
      with customer_id = @variables.customer_id
      set @variables.customer_data = @outputs.data

    # Variable injection in text
    | Customer name: {!@variables.customer_name}

    # Deterministic transition
    if @variables.failed_attempts >= 3:
      transition to @topic.escalation
```

### Instruction Syntax Elements

| Element | Syntax | Purpose |
|---------|--------|---------|
| Literal text | `\| text` | Text that becomes part of LLM prompt |
| Conditional | `if @variables.x:` | Resolves before LLM sees instructions |
| Else clause | `else:` | Alternative path |
| Inline action | `run @actions.x` | Execute action during resolution |
| Set variable | `set @var = @outputs.y` | Capture action output |
| Template injection | Curly-bang syntax: {!@variables.x} | Insert variable value into text |
| Deterministic transition | `transition to @topic.x` | Change topic without LLM |

---

## Action Configuration

### Action Declaration

```yaml
actions:
  action_name: @actions.my_action
    description: "What this action does"
    with input_param = @variables.some_value
    set @variables.result = @outputs.output_field
    available when @variables.is_authorized == True
```

### Action Metadata Properties (TDD Validated v2.2.0)

Action definitions with `target:` support the following metadata properties. These are NOT valid on `@utils.transition` utility actions.

**Action-Level:**

| Property | Type | Context | Notes |
|----------|------|---------|-------|
| `label` | String | Action def, topic, I/O | Display name in UI |
| `description` | String | Action def, I/O | LLM decision-making context |
| `require_user_confirmation` | Boolean | Action def | Compiles; runtime no-op (Issue 6) |
| `include_in_progress_indicator` | Boolean | Action def | Shows spinner during execution |
| `progress_indicator_message` | String | Action def | Custom spinner text |

**Input-Level:**

| Property | Type | Notes |
|----------|------|-------|
| `is_required` | Boolean | Marks input as mandatory |
| `is_user_input` | Boolean | LLM extracts from conversation |
| `label` | String | Display name |
| `description` | String | LLM context |
| `complex_data_type_name` | String | Lightning type mapping |

**Output-Level:**

| Property | Type | Notes |
|----------|------|-------|
| `is_displayable` | Boolean | `False` = hide from user (alias: `filter_from_agent`) |
| `is_used_by_planner` | Boolean | `True` = LLM can reason about value |
| `label` | String | Display name |
| `description` | String | LLM context |
| `complex_data_type_name` | String | Lightning type mapping |

---

### Two-Level Action System

Agent Script uses a two-level system for actions. Understanding this distinction is critical:

```
Level 1: ACTION DEFINITION (in topic's `actions:` block)
   → Has `target:`, `inputs:`, `outputs:`, `description:`
   → Specifies WHAT to call (e.g., "flow://GetOrderStatus")

Level 2: ACTION INVOCATION (in `reasoning.actions:` block)
   → References Level 1 via `@actions.name`
   → Specifies HOW to call it (`with`, `set` clauses)
   → Does NOT use `inputs:`/`outputs:` (use `with`/`set` instead)
```

**Complete Example:**
```yaml
topic order_lookup:
   description: "Look up order details"

   # Level 1: DEFINE the action (with target + I/O schemas)
   actions:
      get_order:
         description: "Retrieves order information by ID"
         inputs:
            order_id: string
               description: "Customer's order number"
         outputs:
            status: string
               description: "Current order status"
         target: "flow://Get_Order_Details"

   reasoning:
      instructions: |
         Help the customer check their order status.
      # Level 2: INVOKE the action (with/set, NOT inputs/outputs)
      actions:
         lookup: @actions.get_order
            with order_id = ...
            set @variables.order_status = @outputs.status
```

> ⚠️ **I/O schemas are REQUIRED for publish**: Action definitions with only `description:` and `target:` (no `inputs:`/`outputs:`) will PASS LSP and CLI validation but FAIL server-side compilation with "Internal Error." Always include complete I/O schemas in Level 1 definitions.

---

### Lifecycle Hooks: `before_reasoning:` and `after_reasoning:`

Lifecycle hooks enable deterministic pre/post-processing around LLM reasoning. They are FREE (no credit cost).

```yaml
topic main:
   description: "Topic with lifecycle hooks"

   # BEFORE: Runs deterministically BEFORE LLM sees instructions
   before_reasoning:
      # Content goes DIRECTLY here (NO instructions: wrapper!)
      set @variables.turn_count = @variables.turn_count + 1
      if @variables.needs_redirect == True:
         transition to @topic.redirect

   # LLM reasoning phase
   reasoning:
      instructions: ->
         | Turn {!@variables.turn_count}: How can I help?

   # AFTER: Runs deterministically AFTER LLM finishes reasoning
   after_reasoning:
      # Content goes DIRECTLY here (NO instructions: wrapper!)
      set @variables.interaction_logged = True
```

**Key Rules:**
- Content goes **directly** under the block (NO `instructions:` wrapper)
- Supports `set`, `if`, `transition` statements
- `run` does NOT work reliably in lifecycle blocks (use it in `reasoning.actions:` or `instructions: ->` instead)
- Both hooks are FREE (no credit cost) — use for data prep, logging, cleanup

---

### Action Target Protocols

**Core Targets (Validated)**

| Protocol | Use When | Status |
|----------|----------|--------|
| `flow://` | Data operations, business logic | ✅ Validated |
| `apex://` | Custom calculations, validation | ✅ Validated |
| `generatePromptResponse://` | Grounded LLM responses | ✅ Validated |
| `api://` | REST API callouts | ✅ Validated |
| `retriever://` | RAG knowledge search | ✅ Validated |
| `externalService://` | Third-party APIs via Named Credential | ✅ Validated |
| `standardInvocableAction://` | Built-in SF actions | ✅ Validated |

**Additional Targets (From agent-script-recipes)**

| Protocol | Use When | Status |
|----------|----------|--------|
| `datacloudDataGraphAction://` | Data Cloud graph queries | ⚠️ Untested |
| `datacloudSegmentAction://` | Data Cloud segment operations | ⚠️ Untested |
| `triggerByKnowledgeSource://` | Knowledge-triggered actions | ⚠️ Untested |
| `contextGrounding://` | Context grounding operations | ⚠️ Untested |
| `predictiveAI://` | Einstein predictions | ⚠️ Untested |
| `runAction://` | Sub-action execution | ⚠️ Untested |
| `external://` | External services | ⚠️ Untested |
| `copilotAction://` | Copilot actions | ⚠️ Untested |
| `@topic.X` | Topic delegation (supervision) | ✅ Validated |

> **Note**: Untested targets are documented in the official AGENT_SCRIPT.md rules. They may require specific licenses, org configurations, or future API versions.

### Utility Actions

| Action | Purpose | Example |
|--------|---------|---------|
| `@utils.transition to @topic.x` | LLM-chosen topic navigation | `go_main: @utils.transition to @topic.main` |
| `@utils.escalate` | Hand off to human agent | `escalate: @utils.escalate` |
| `@utils.setVariables` | Set multiple variables | `set_vars: @utils.setVariables` |

---

## Resource References

| Syntax | Purpose | Example |
|--------|---------|---------|
| `@variables.x` | Reference a variable | `@variables.customer_id` |
| `@actions.x` | Reference an action | `@actions.process_refund` |
| `@topic.x` | Reference a topic | `@topic.escalation` |
| `@outputs.x` | Reference action output | `@outputs.status` |
| `@session.x` | Reference session data | `@session.sessionID` |
| `@context.x` | Reference context data | `@context.userProfile` |

---

## Whitespace Rules

### Indentation

| ✅ CORRECT | ❌ INCORRECT |
|------------|-------------|
| 2-space consistent | Mixed tabs and spaces |
| 3-space consistent | Inconsistent spacing |
| Tabs consistent | Tab in one block, spaces in another |

> **CRITICAL**: Never mix tabs and spaces in the same file. This causes compilation errors.

### Boolean Values

| ✅ CORRECT | ❌ INCORRECT |
|------------|-------------|
| `True` | `true` |
| `False` | `false` |

---

## Complete Example

```yaml
system:
  messages:
    welcome: "Welcome to Pronto Support!"
    error: "Sorry, something went wrong. Let me connect you with a human."
  instructions: "You are a helpful customer service agent for Pronto Delivery."

config:
  developer_name: "pronto_refund_agent"
  agent_description: "Handles customer refund requests with churn risk assessment"
  agent_type: "AgentforceServiceAgent"
  default_agent_user: "agent_user@myorg.com"

variables:
  # Mutable state
  customer_verified: mutable boolean = False
  failed_attempts: mutable number = 0
  churn_risk_score: mutable number = 0
  refund_status: mutable string = ""

  # Linked from session
  customer_id: linked string
    source: @session.customerId
    description: "Customer ID from messaging session"

topic identity_verification:
  description: "Verify customer identity before refund processing"
  reasoning:
    instructions: ->
      if @variables.failed_attempts >= 3:
        | Too many failed attempts. Escalating to human agent.
        transition to @topic.escalation

      if @variables.customer_verified == True:
        | Identity verified. Proceeding to refund assessment.
        transition to @topic.refund_processor

      | Please verify your identity by providing your email address.
    actions:
      verify: @actions.verify_customer
        description: "Verify customer by email"
        set @variables.customer_verified = @outputs.verified

topic refund_processor:
  description: "Process refund based on churn risk assessment"
  reasoning:
    instructions: ->
      # Post-action check (triggers on loop after refund)
      if @variables.refund_status == "Approved":
        run @actions.create_crm_case
          with customer_id = @variables.customer_id
        transition to @topic.success

      # Pre-LLM: Load churn data
      run @actions.get_churn_score
        with customer_id = @variables.customer_id
        set @variables.churn_risk_score = @outputs.score

      # Dynamic instructions based on score
      | Customer churn risk: {!@variables.churn_risk_score}%

      if @variables.churn_risk_score >= 80:
        | HIGH RISK - Offer full cash refund to retain customer.
      else:
        | LOW RISK - Offer $10 store credit as goodwill.
    actions:
      process_refund: @actions.process_refund
        description: "Issue the refund"
        available when @variables.customer_verified == True
        set @variables.refund_status = @outputs.status

topic escalation:
  description: "Escalate to human agent"
  reasoning:
    instructions: |
      Apologize for the inconvenience and transfer to a human agent.
    actions:
      handoff: @utils.escalate
        description: "Transfer to live support"

topic success:
  description: "Successful refund confirmation"
  reasoning:
    instructions: |
      Thank the customer and confirm their refund has been processed.

start_agent topic_selector:
  description: "Entry point - route to identity verification"
  reasoning:
    instructions: |
      Greet the customer and begin identity verification.
    actions:
      start: @utils.transition to @topic.identity_verification
        description: "Begin refund process"
```

---

## Expression Operators

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equal to | `if @variables.status == "active":` |
| `!=` | Not equal to | `if @variables.status != "closed":` |
| `<` | Less than | `if @variables.count < 10:` |
| `<=` | Less than or equal | `if @variables.count <= 5:` |
| `>` | Greater than | `if @variables.risk > 80:` |
| `>=` | Greater than or equal | `if @variables.attempts >= 3:` |
| `is` | Identity check | `if @variables.data is None:` |
| `is not` | Negated identity check | `if @variables.data is not None:` |

> **Note**: Use `!=` for not-equal comparisons. The `<>` operator does NOT compile (TDD validated v1.9.0).

### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `and` | Logical AND | `if @variables.verified == True and @variables.active == True:` |
| `or` | Logical OR | `if @variables.status == "open" or @variables.status == "pending":` |
| `not` | Logical NOT | `if not @variables.blocked:` |

### Arithmetic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `set @variables.count = @variables.count + 1` |
| `-` | Subtraction | `set @variables.remaining = @variables.total - @variables.used` |

> ⚠️ **NOT supported**: `*` (multiplication), `/` (division), `%` (modulo). For complex arithmetic, use a Flow or Apex action.

### Access Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `.` | Property access | `@outputs.result.status` |
| `[]` | Index access | `@variables.items[0]` |

### Conditional Expression (Ternary-like)

```yaml
| Status: {!@variables.status if @variables.status else "pending"}
```

### Expression Limitations (Sandboxed Python AST Subset)

Agent Script expressions use a sandboxed subset of Python. Not all Python operations are available.

**Supported:**

| Category | Operations |
|----------|-----------|
| Arithmetic | `+`, `-` |
| Comparison | `==`, `!=`, `<`, `<=`, `>`, `>=`, `is`, `is not` |
| Logical | `and`, `or`, `not` |
| Ternary | `x if condition else y` |
| Built-in functions | `len()`, `max()`, `min()` |
| Attribute access | `@outputs.result.field` |
| Index access | `@variables.items[0]` |
| String methods | `contains`, `startswith`, `endswith` |

**NOT Supported:**

| Operation | Workaround |
|-----------|-----------|
| Multiplication (`*`) | Use Flow/Apex action |
| Division (`/`) | Use Flow/Apex action |
| Modulo (`%`) | Use Flow/Apex action |
| String concatenation (`+` on strings) | Use `{!var1}{!var2}` template injection |
| List slicing (`items[1:3]`) | Use Flow to extract sublist |
| List comprehensions (`[x for x in ...]`) | Use Flow/Apex for list transformation |
| Lambda expressions | Use Flow/Apex action |
| `for`/`while` loops | Use topic loop pattern (re-entry) |
| `import` statements | Not available (security sandbox) |

### Apex Complex Type Notation

When action inputs or outputs reference Apex inner classes, use the `@apexClassType` notation:

```
@apexClassType/c__OuterClass$InnerClass
```

| Component | Description | Example |
|-----------|-------------|---------|
| `@apexClassType/` | Required prefix | — |
| `c__` | Default namespace (or your package namespace) | `c__`, `myns__` |
| `OuterClass` | The containing Apex class | `OrderService` |
| `$` | Inner class separator | — |
| `InnerClass` | The inner class name | `LineItem` |

**Example:**
```yaml
actions:
   process_order:
      inputs:
         line_items: list[object]
            complex_data_type_name: "@apexClassType/c__OrderService$LineItem"
      target: "apex://OrderService"
```

> **Note**: This notation is used in the `complex_data_type_name` field of action input/output definitions in Agentforce Assets, not in the `.agent` file directly.

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Mixed tabs/spaces | `SyntaxError: cannot mix` | Use consistent indentation |
| Invalid boolean | Type mismatch | Use `True`/`False` (capitalized) |
| Spaces in variable names | Parse error | Use `snake_case` |
| Mutable + linked | Conflicting modifiers | Choose one modifier |
| Missing `source:` for linked | Variable empty | Add `source: @session.X` |
| Missing `default_agent_user` | Internal error on deploy | Add valid Einstein Agent User |
