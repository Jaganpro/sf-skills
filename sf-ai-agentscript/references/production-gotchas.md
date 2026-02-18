<!-- Parent: sf-ai-agentscript/SKILL.md -->

# PRODUCTION GOTCHAS: Billing, Determinism & Performance

## Credit Consumption Table

> **Key insight**: Framework operations are FREE. Only actions that invoke external services consume credits.

| Operation | Credits | Notes |
|-----------|---------|-------|
| `@utils.transition` | FREE | Framework navigation |
| `@utils.setVariables` | FREE | Framework state management |
| `@utils.escalate` | FREE | Framework escalation |
| `if`/`else` control flow | FREE | Deterministic resolution |
| `before_reasoning` | FREE | Deterministic pre-processing (see note below) |
| `after_reasoning` | FREE | Deterministic post-processing (see note below) |
| `reasoning` (LLM turn) | FREE | LLM reasoning itself is not billed |
| Prompt Templates | 2-16 | Per invocation (varies by complexity) |
| Flow actions | 20 | Per action execution |
| Apex actions | 20 | Per action execution |
| Any other action | 20 | Per action execution |

> **✅ Lifecycle Hooks Validated (v1.3.0)**: The `before_reasoning:` and `after_reasoning:` lifecycle hooks are now TDD-validated. Content goes **directly** under the block (no `instructions:` wrapper). See "Lifecycle Hooks" section below for correct syntax.

**Cost Optimization Pattern**: Fetch data once in `before_reasoning:`, cache in variables, reuse across topics.

## Lifecycle Hooks: `before_reasoning:` and `after_reasoning:`

> **TDD Validated (2026-01-20)**: These hooks enable deterministic pre/post-processing around LLM reasoning.

```yaml
topic main:
   description: "Topic with lifecycle hooks"

   # BEFORE: Runs deterministically BEFORE LLM sees instructions
   before_reasoning:
      # Content goes DIRECTLY here (NO instructions: wrapper!)
      set @variables.pre_processed = True
      set @variables.customer_tier = "gold"

   # LLM reasoning phase
   reasoning:
      instructions: ->
         | Customer tier: {!@variables.customer_tier}
         | How can I help you today?

   # AFTER: Runs deterministically AFTER LLM finishes reasoning
   after_reasoning:
      # Content goes DIRECTLY here (NO instructions: wrapper!)
      set @variables.interaction_logged = True
      if @variables.needs_audit == True:
         set @variables.audit_flag = True
```

**Key Points:**
- Content goes **directly** under `before_reasoning:` / `after_reasoning:` (NO `instructions:` wrapper)
- Supports `set`, `if`, `run` statements (same as procedural `instructions: ->`)
- `before_reasoning:` is FREE (no credit cost) - use for data prep
- `after_reasoning:` is FREE (no credit cost) - use for logging, cleanup

**❌ WRONG Syntax (causes compile error):**
```yaml
before_reasoning:
   instructions: ->      # ❌ NO! Don't wrap with instructions:
      set @variables.x = True
```

**✅ CORRECT Syntax:**
```yaml
before_reasoning:
   set @variables.x = True   # ✅ Direct content under the block
```

## Supervision vs Handoff (Clarified Terminology)

| Term | Syntax | Behavior | Use When |
|------|--------|----------|----------|
| **Handoff** | `@utils.transition to @topic.X` | Control transfers completely, child generates final response | Checkout, escalation, terminal states |
| **Supervision** | `@topic.X` (as action reference) | Parent orchestrates, child returns, parent synthesizes | Expert consultation, sub-tasks |

```yaml
# HANDOFF - child topic takes over completely:
checkout: @utils.transition to @topic.order_checkout
   description: "Proceed to checkout"
# → @topic.order_checkout generates the user-facing response

# SUPERVISION - parent remains in control:
get_advice: @topic.product_expert
   description: "Consult product expert"
# → @topic.product_expert returns, parent topic synthesizes final response
```

**KNOWN BUG**: Adding ANY new action in Canvas view may inadvertently change Supervision references to Handoff transitions.

## Action Output Flags for Zero-Hallucination Routing

> **Key Pattern for Determinism**: Control what the LLM can see and say.

When defining actions in Agentforce Assets, use these output flags:

| Flag | Effect | Use When |
|------|--------|----------|
| `is_displayable: False` | LLM **cannot** show this value to user | Preventing hallucinated responses |
| `is_used_by_planner: True` | LLM **can** reason about this value | Decision-making, routing |

**Zero-Hallucination Intent Classification Pattern:**
```yaml
# In Agentforce Assets - Action Definition outputs:
outputs:
   intent_classification: string
      is_displayable: False       # LLM cannot show this to user
      is_used_by_planner: True    # LLM can use for routing decisions

# In Agent Script - LLM routes but cannot hallucinate:
topic intent_router:
   reasoning:
      instructions: ->
         run @actions.classify_intent
         set @variables.intent = @outputs.intent_classification

         if @variables.intent == "refund":
            transition to @topic.refunds
         if @variables.intent == "order_status":
            transition to @topic.orders
```

## Action I/O Metadata Properties (TDD Validated v2.2.0)

> **Complete reference** for all metadata properties available on action definitions, inputs, and outputs.

**Action-Level Properties:**

| Property | Type | Effect | TDD Status |
|----------|------|--------|------------|
| `label` | String | Display name in UI | ✅ v2.2.0 |
| `description` | String | LLM reads this for decision-making | ✅ v1.3.0 |
| `require_user_confirmation` | Boolean | Request user confirmation before execution | ✅ Compiles (runtime Issue 6) |
| `include_in_progress_indicator` | Boolean | Show spinner during execution | ✅ v2.2.0 |
| `progress_indicator_message` | String | Custom spinner text | ✅ v2.2.0 |

**Input Properties:**

| Property | Type | Effect | TDD Status |
|----------|------|--------|------------|
| `description` | String | Explains parameter to LLM | ✅ v1.3.0 |
| `label` | String | Display name in UI | ✅ v2.2.0 |
| `is_required` | Boolean | Marks input as mandatory for LLM | ✅ v2.2.0 |
| `is_user_input` | Boolean | LLM extracts value from conversation | ✅ v2.2.0 |
| `complex_data_type_name` | String | Lightning type mapping | ✅ v2.1.0 |

**Output Properties:**

| Property | Type | Effect | TDD Status |
|----------|------|--------|------------|
| `description` | String | Explains output to LLM | ✅ v1.3.0 |
| `label` | String | Display name in UI | ✅ v2.2.0 |
| `is_displayable` | Boolean | `False` = hide from user (alias: `filter_from_agent`) | ✅ v2.2.0 |
| `is_used_by_planner` | Boolean | `True` = LLM can reason about value | ✅ v2.2.0 |
| `complex_data_type_name` | String | Lightning type mapping | ✅ v2.1.0 |

> **Cross-reference**: `filter_from_agent: True` (in actions-reference.md) is equivalent to `is_displayable: False`.

**User Input Pattern** (`is_user_input: True`):
```yaml
inputs:
   customer_name: string
      description: "Customer's full name"
      is_user_input: True    # LLM pulls from what user already said
      is_required: True      # Must have a value before action executes
```

## Action Chaining with `run` Keyword

> **Known quirk**: Parent action may complain about inputs needed by chained action - this is expected.

```yaml
process_order: @actions.create_order
   with customer_id = @variables.customer_id
   run @actions.send_confirmation        # Chains after create_order completes
   set @variables.order_id = @outputs.id
```

**KNOWN BUG**: Chained actions with Prompt Templates don't properly map inputs using `Input:Query` format.

> **📖 For prompt template action definitions, input binding syntax, and grounded data patterns**, see [resources/action-prompt-templates.md](../resources/action-prompt-templates.md).

## Latch Variable Pattern for Topic Re-entry

> **Problem**: Topic selector doesn't properly re-evaluate after user provides missing input.

**Solution**: Use a "latch" variable to force re-entry:

```yaml
variables:
   verification_in_progress: mutable boolean = False

start_agent topic_selector:
   reasoning:
      instructions: ->
         if @variables.verification_in_progress == True:
            transition to @topic.verification
         | How can I help you today?
      actions:
         start_verify: @topic.verification
            description: "Start identity verification"
            set @variables.verification_in_progress = True

topic verification:
   reasoning:
      instructions: ->
         | Please provide your email to verify your identity.
      actions:
         verify: @actions.verify_identity
            with email = ...
            set @variables.verified = @outputs.success
            set @variables.verification_in_progress = False
```

## Loop Protection Guardrail

> Agent Scripts have a built-in guardrail that limits iterations to approximately **3-4 loops** before breaking out and returning to the Topic Selector.

**Best Practice**: Map out your execution paths and test for unintended circular references between topics.

## Token & Size Limits

| Limit Type | Value | Notes |
|------------|-------|-------|
| Max response size | 1,048,576 bytes (1MB) | Per agent response |
| Plan trace limit (Frontend) | 1M characters | For debugging UI |
| Transformed plan trace (Backend) | 32k tokens | Internal processing |
| Active/Committed Agents per org | 100 max | Org limit |

## Progress Indicators

```yaml
actions:
   fetch_data: @actions.get_customer_data
      description: "Fetch customer information"
      include_in_progress_indicator: True
      progress_indicator_message: "Fetching your account details..."
```

## VS Code Pull/Push NOT Supported

```bash
# ❌ ERROR when using source tracking:
Failed to retrieve components using source tracking:
[SfError [UnsupportedBundleTypeError]: Unsupported Bundle Type: AiAuthoringBundle

# ✅ WORKAROUND - Use CLI directly:
sf project retrieve start -m AiAuthoringBundle:MyAgent
sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG
```

## Language Block Quirks

- Hebrew and Indonesian appear **twice** in the language dropdown
- Selecting from the second set causes save errors
- Use `adaptive_response_allowed: True` for automatic language adaptation
