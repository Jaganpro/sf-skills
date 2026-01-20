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
  agent_name: "RefundAgent"
  agent_label: "Refund Agent"
  description: "Handles refund requests"
  default_agent_user: "admin@yourorg.com"
```

| Field | Required | Purpose |
|-------|----------|---------|
| `agent_name` | ✅ Yes | Internal identifier (snake_case, no spaces) |
| `agent_label` | ✅ Yes | Display name in UI |
| `description` | ✅ Yes | Agent description |
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
| Template injection | `{!@variables.x}` | Insert variable value into text |
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
  agent_name: "pronto_refund_agent"
  agent_label: "Pronto Refund Agent"
  description: "Handles customer refund requests with churn risk assessment"
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

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Mixed tabs/spaces | `SyntaxError: cannot mix` | Use consistent indentation |
| Invalid boolean | Type mismatch | Use `True`/`False` (capitalized) |
| Spaces in variable names | Parse error | Use `snake_case` |
| Mutable + linked | Conflicting modifiers | Choose one modifier |
| Missing `source:` for linked | Variable empty | Add `source: @session.X` |
| Missing `default_agent_user` | Internal error on deploy | Add valid Einstein Agent User |
