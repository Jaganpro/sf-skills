# Agent Script Syntax Reference

Complete syntax reference for the Agent Script language used in Agentforce.

---

## File Structure

Agent Script files use the `.agentscript` extension and contain YAML-like syntax with specific Agent Script keywords.

### Single File Structure

```agentscript
# Comments start with #

config:
    agent_name: "Agent_API_Name"
    agent_label: "Human Readable Name"
    description: "What this agent does"

system:
    messages:
        welcome: "Welcome message"
        error: "Error message"
    instructions:
        | Global instructions
        | for the agent.

variables:
    var_name: mutable type = default
        description: "Description"

start_agent topic_selector:
    description: "Entry point"
    reasoning:
        instructions:->
            | Instructions here.

topic other_topic:
    description: "Another topic"
    reasoning:
        instructions:->
            | More instructions.
```

---

## Indentation Rules

**CRITICAL**: Agent Script requires **4-space indentation**.

```agentscript
# ✅ CORRECT - 4 spaces per level
config:
    agent_name: "My_Agent"
    description: "Description"

# ❌ WRONG - 3 spaces
config:
   agent_name: "My_Agent"

# ❌ WRONG - tabs
config:
	agent_name: "My_Agent"
```

---

## Blocks

### Config Block

Defines agent metadata.

```agentscript
config:
    agent_name: "Customer_Support_Agent"
    agent_label: "Customer Support"
    description: "Helps customers with orders and inquiries"
```

| Field | Required | Description |
|-------|----------|-------------|
| `agent_name` | Yes | API name (PascalCase with underscores) |
| `agent_label` | Yes | Human-readable name |
| `description` | Yes | What the agent does |

### System Block

Global agent settings and instructions.

```agentscript
system:
    messages:
        welcome: "Hello! How can I help you today?"
        error: "I'm sorry, something went wrong. Please try again."
    instructions:
        | You are a helpful customer service agent.
        | Be professional and courteous.
        | Never share confidential information.
```

### Variables Block

Declares state variables.

```agentscript
variables:
    user_name: mutable string = ""
        description: "The customer's name"

    order_count: mutable number = 0
        description: "Number of items in cart"

    is_verified: mutable boolean = False
        description: "Whether identity is verified"
```

### Topic Blocks

Define conversation topics.

```agentscript
# Entry point topic
start_agent topic_selector:
    description: "Routes users to appropriate topics"
    reasoning:
        instructions:->
            | Determine user intent and route.
        actions:
            go_orders: @utils.transition to @topic.orders
                description: "Help with orders"

# Regular topic
topic orders:
    description: "Handles order inquiries"
    reasoning:
        instructions:->
            | Help with order questions.
```

---

## Variable Types

| Type | Description | Default | Example |
|------|-------------|---------|---------|
| `string` | Text values | `""` | `"John Doe"` |
| `number` | Integers or decimals | `0` | `42`, `99.99` |
| `boolean` | True/False | `False` | `True`, `False` |
| `list[type]` | Array of values | `[]` | `list[string]` |
| `object` | Complex object | `{}` | Custom structure |

```agentscript
variables:
    name: mutable string = ""
    age: mutable number = 0
    active: mutable boolean = False
    tags: mutable list[string] = []
```

**Note**: Boolean values must be capitalized: `True`, `False`

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
```

---

## Instructions

### Prompt Mode (|)

Use `|` for natural language instructions:

```agentscript
instructions:
    | This is line one.
    | This is line two.
    | Each line starts with a pipe.
```

### Procedural Mode (->)

Use `->` for logic-based instructions:

```agentscript
instructions:->
    if @variables.amount > 1000:
        | This is a large order.
    else:
        | Standard order processing.
```

### Template Expressions

Use `{!...}` for variable interpolation:

```agentscript
instructions:->
    | Hello {!@variables.user_name}!
    | Your order total is ${!@variables.total}.
```

---

## Conditionals

### If/Else

```agentscript
instructions:->
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

---

## Actions

### Defining Actions

```agentscript
topic my_topic:
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
```

### Target Formats

| Type | Format | Example |
|------|--------|---------|
| Flow | `flow://FlowName` | `flow://Get_Order_Details` |
| Apex | `apex://ClassName.methodName` | `apex://OrderService.getOrder` |

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

## Topic Transitions

### Basic Transition

```agentscript
reasoning:
    actions:
        go_orders: @utils.transition to @topic.orders
            description: "Help with orders"
```

### Conditional Transition

```agentscript
go_checkout: @utils.transition to @topic.checkout
    description: "Proceed to checkout"
    available when @variables.cart_count > 0
```

### Automatic Transition (after action)

```agentscript
process: @actions.complete_order
    with order_id=...
    transition to @topic.confirmation
```

---

## Comments

```agentscript
# This is a comment
config:
    agent_name: "My_Agent"  # Inline comment (may not work everywhere)

# Multi-line comments require multiple # symbols
# Line 1
# Line 2
# Line 3
```

---

## Reserved Keywords

| Keyword | Purpose |
|---------|---------|
| `config` | Agent configuration block |
| `system` | System settings block |
| `variables` | Variable declarations |
| `start_agent` | Entry point topic |
| `topic` | Topic definition |
| `description` | Description field |
| `reasoning` | Reasoning block |
| `instructions` | Instructions field |
| `actions` | Actions block |
| `inputs` | Action inputs |
| `outputs` | Action outputs |
| `target` | Action target |
| `mutable` | Variable mutability |
| `if` | Conditional |
| `else` | Else branch |
| `set` | Assign value |
| `with` | Action parameter |
| `run` | Execute callback |
| `available when` | Conditional availability |
| `transition to` | Topic navigation |

---

## Common Patterns

### Simple Q&A Agent

```agentscript
config:
    agent_name: "FAQ_Agent"
    agent_label: "FAQ Assistant"
    description: "Answers frequently asked questions"

system:
    instructions:
        | You are a helpful FAQ assistant.
        | Answer questions concisely.

start_agent topic_selector:
    description: "Handles FAQ questions"
    reasoning:
        instructions:->
            | Answer the user's question.
            | If unsure, offer to connect them with support.
```

### Multi-Topic Router

```agentscript
start_agent topic_selector:
    description: "Routes to specialized topics"
    reasoning:
        instructions:->
            | Determine what the user needs.
            | Route to the appropriate topic.
        actions:
            orders: @utils.transition to @topic.orders
                description: "Order help"
            billing: @utils.transition to @topic.billing
                description: "Billing questions"
            support: @utils.transition to @topic.support
                description: "Technical support"
```

### Validation Pattern

```agentscript
instructions:->
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
| Parse error | Invalid syntax | Check indentation (4 spaces) |
| Unknown resource | Invalid `@` reference | Use `@variables`, `@actions`, etc. |
| Undefined variable | Variable not declared | Add to `variables:` block |
| Undefined topic | Topic not found | Add topic or fix reference |
| Invalid target | Wrong action target format | Use `flow://` or `apex://` |
| Nested run | `run` inside `run` | Flatten to sequential `run` |
