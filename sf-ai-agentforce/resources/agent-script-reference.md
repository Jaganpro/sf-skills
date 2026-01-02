# Agent Script DSL Reference

Complete syntax reference for Agent Script, the domain-specific language for building Agentforce agents.

## Table of Contents

- [New Patterns (December 2025)](#new-patterns-december-2025)
- [Indentation Rules](#indentation-rules)
- [Comments Syntax](#comments-syntax)
- [System Instructions](#system-instructions)
- [Escalation Syntax](#escalation-syntax)
- [Reserved Words](#reserved-words)
- [Invalid Keywords](#invalid-keywords)
- [Block Order](#block-order)
- [Complete Syntax Reference](#complete-syntax-reference)
- [Common Patterns](#common-patterns)

---

## New Patterns (December 2025)

Patterns added from cross-comparison with official Salesforce agent-script-recipes repository:

| Pattern | Template | Description |
|---------|----------|-------------|
| **Prompt Template Actions** | `patterns/prompt-template-action.agent` | Invoke PromptTemplates directly using `generatePromptResponse://` target |
| **Multi-Step Workflows** | `patterns/multi-step-workflow.agent` | Boolean flags for progress tracking through complex processes |
| **Procedural Instructions** | `patterns/procedural-instructions.agent` | Execute `run @actions.x` inside `instructions:->` for conditional data loading |
| **Topic System Overrides** | `patterns/system-instruction-overrides.agent` | Use `system:` blocks inside topics for persona switching |
| **Input Binding Patterns** | See [../docs/patterns-and-practices.md](../docs/patterns-and-practices.md) | When to use `...`, `@variables.x`, or fixed values |

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

## Indentation Rules

**Agent Script is whitespace-sensitive (like Python/YAML). Use CONSISTENT indentation throughout.**

| Rule | Details |
|------|---------|
| **Tabs (Recommended)** | Use tabs for easier manual editing and consistent alignment |
| **Spaces** | 2, 3, or 4 spaces also work if used consistently |
| **Mixing** | NEVER mix tabs and spaces (causes parse errors) |
| **Consistency** | All lines at same nesting level must use same indentation |

**RECOMMENDED: Use TAB indentation for all Agent Script files.** Tabs are easier to edit manually and provide consistent visual alignment across editors.

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

## System Instructions

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

## Escalation Syntax

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

## Reserved Words

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

## Invalid Keywords

**The following keywords DO NOT EXIST in Agent Script. Using them causes SyntaxError.**

| Invalid Keyword | Error | Why It Happens | Correct Pattern |
|-----------------|-------|----------------|-----------------|
| `internal_actions` | `SyntaxError: Unexpected 'internal_actions'` | Claude may invent this for "local helper functions" | Use `set` statements directly in action blocks |
| `helper_actions` | Not a valid keyword | Same as above | Use `set` statements directly |
| `private_actions` | Not a valid keyword | Same as above | Use `set` statements directly |
| `local_actions` | Not a valid keyword | Same as above | Use `set` statements directly |

**Root Cause**: When needing simple post-action operations (like incrementing a counter), Claude may extrapolate from general programming patterns and invent "local function" syntax that doesn't exist.

**Example: Simple Variable Update After Action**

```agentscript
# ❌ WRONG - internal_actions does not exist
internal_actions:
    increment_counter:
        set @variables.count = @variables.count + 1

reasoning:
    actions:
        process: @actions.create_case
            run @actions.increment_counter   # ❌ Can't reference internal action

# ✅ CORRECT - Use set directly in the action block
reasoning:
    actions:
        create_support_case: @actions.create_case
            with inp_CustomerId=@variables.ContactId
            with inp_Subject=...
            set @variables.case_number = @outputs.out_CaseNumber
            set @variables.cases_created = @variables.cases_created + 1  # ✅ Direct set!
```

**For AiAuthoringBundle**: The `run` keyword is NOT supported. Use only `set` statements for post-action variable updates.

---

## Block Order

Blocks MUST appear in this order:

1. `system:` - Global system instructions and messages
2. `config:` - Agent metadata (name, label, description)
3. `variables:` - Linked and mutable variables
4. `language:` - Locale settings
5. `start_agent [name]:` - Entry point topic
6. `topic [name]:` - Additional topics
7. `connection [name]:` - Escalation routes (optional)

---

## Complete Syntax Reference

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
| **config** | Use `agent_name` or `developer_name` (both work). `default_agent_user` must be valid org user. |
| **variables** | Use `number` not `integer/long`. Use `timestamp` not `datetime`. Use `list[type]` not `list<type>`. Linked vars don't support lists/objects. |
| **language** | Required block - include even if only `en_US`. |
| **topics** | Each topic MUST have both `label:` and `description:`. |
| **instructions** | Use `instructions: ->` (space before arrow). |

### AiAuthoringBundle Limitations (Tested Dec 2025)

| Feature | Status | Workaround |
|---------|--------|------------|
| `run` keyword | NOT Supported | Define actions in topic, LLM chooses when to call |
| `with`/`set` in `reasoning.actions` | NOT Supported | Define actions in topic `actions:` block only |
| `{!@actions.x}` | NOT Supported | Define actions with descriptions, LLM auto-selects |
| `@utils.setVariables` | NOT Supported | Use `set @variables.x = ...` in instructions |
| `@utils.escalate with reason` | NOT Supported | Use basic `@utils.escalate` with `description:` |
| `integer`, `long` types | NOT Supported | Use `number` type |
| `list<type>` syntax | NOT Supported | Use `list[type]` syntax |
| Nested if statements | NOT Supported | Use flat `and` conditionals |
| `filter_from_agent` | NOT Supported | Use `available when @var == val` syntax |

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

### Pattern 4: Action Invocation (Simplified)

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

## Variable Types

| Agent Script Type | Description | Example |
|-------------------|-------------|---------|
| `string` | Text values | "Hello World" |
| `number` | Numeric values (integer or decimal) | 42, 3.14 |
| `boolean` | True/False values | True, False |
| `timestamp` | Date/time values | System-managed |
| `list[string]` | List of strings | ["a", "b", "c"] |
| `list[number]` | List of numbers | [1, 2, 3] |

**Notes:**
- Use `number` (not `integer` or `long`)
- Use `timestamp` (not `datetime`)
- Use `list[type]` (not `list<type>`)
- Boolean values: `True`, `False` (capitalized)

---

## Math and Boolean Operations

### Math Operators

```agentscript
# Increment counter
set @variables.count = @variables.count + 1

# Decrement
set @variables.remaining = @variables.total - @variables.used

# Basic arithmetic in set statements
set @variables.total = @variables.price * @variables.quantity
```

### Boolean Operations

```agentscript
# N-ary boolean operations (3+ conditions) are supported
if @variables.a and @variables.b and @variables.c:
   | All three conditions are true

# Flat conditionals with 'and'
actions:
   process_order: @actions.create_order
      available when @variables.cart_total > 0
      available when @variables.payment_verified == True
      available when @variables.shipping_address != ""
```

**NOT supported: Nested if statements**

```agentscript
# ❌ WRONG - Nested if statements cause parse errors
if @variables.a:
   if @variables.b:
      | Both a and b are true

# ✅ CORRECT - Use flat conditionals with 'and'
if @variables.a and @variables.b:
   | Both a and b are true
```

---

## References

For additional patterns and best practices, see:
- [../docs/patterns-and-practices.md](../docs/patterns-and-practices.md) - Pattern decision tree and best practices
- [../docs/agent-script-reference.md](../docs/agent-script-reference.md) - Official Agent Script reference
- [topics-guide.md](topics-guide.md) - Topic design and routing patterns
- [actions-guide.md](actions-guide.md) - Action implementation patterns
