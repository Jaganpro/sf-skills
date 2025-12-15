# Agent Script Quick Reference

**AiAuthoringBundle Compatibility Guide - December 2025**

This document provides a comprehensive quick reference for Agent Script features, their support status in AiAuthoringBundle, and practical examples. All findings have been verified through systematic testing with `sf agent publish authoring-bundle`.

---

## Table of Contents

- [Not Supported Features](#-not-supported-features)
- [Supported Features](#-supported-features)
- [Deployment Gotchas](#%EF%B8%8F-deployment-gotchas)
- [Reserved Words](#-reserved-words)
- [Error Quick Reference](#-error-quick-reference)

---

## ❌ Not Supported Features

### Variable Types: `integer` and `long`

| Aspect | Details |
|--------|---------|
| **Error** | "Variable with type integer is not supported for mutable variables" |
| **Impact** | Cannot use integer or long types for mutable variables |
| **Workaround** | Use `number` type instead (works for both integers and decimals) |

```agentscript
# ❌ WRONG
count: mutable integer = 0
big_num: mutable long = 9999999999

# ✅ CORRECT
count: mutable number = 0
big_num: mutable number = 9999999999
```

---

### Nested Pipe Syntax

| Aspect | Details |
|--------|---------|
| **Error** | "Start token somehow not of the form \| + 2 spaces" |
| **Impact** | Cannot nest pipes inside other pipes or conditionals |
| **Workaround** | Keep conditionals at same level as pipes, not nested inside |

```agentscript
# ❌ WRONG - Nested pipes
instructions: ->
   | Some text.
   | if @variables.x:
   |    | Nested text.       # FAILS!

# ✅ CORRECT - Flat structure
instructions: ->
   | Some text.
   if @variables.x:
      | Conditional text.
   | More text.
```

---

### Nested If Statements

| Aspect | Details |
|--------|---------|
| **Error** | "Missing required element" + "Unexpected 'else'" |
| **Impact** | Cannot nest if/else blocks inside other if/else blocks |
| **Workaround** | Use flat conditionals with `and` operators |

```agentscript
# ❌ WRONG - Nested if
if @variables.is_premium == True:
   | Premium user.
   if @variables.order_total > 1000:    # NESTED - FAILS!
      | Large order.
   else:
      | Regular order.
else:
   | Standard user.

# ✅ CORRECT - Flat with `and`
if @variables.is_premium == True and @variables.order_total > 1000:
   | Premium user with large order.
if @variables.is_premium == True and @variables.order_total <= 1000:
   | Premium user with regular order.
if @variables.is_premium == False:
   | Standard user.
```

---

### Collection Syntax (Angle Brackets)

| Aspect | Details |
|--------|---------|
| **Error** | "Unexpected '<'" |
| **Impact** | Cannot use Java/TypeScript-style generics syntax |
| **Workaround** | Use square brackets for collections |

```agentscript
# ❌ WRONG
items: mutable list<string>
numbers: mutable list<number>

# ✅ CORRECT
items: mutable list[string]
numbers: mutable list[number]
```

**Supported collection types:** `list[string]`, `list[number]`, `list[boolean]`

**NOT supported:** `list[object]`

---

### `@utils.setVariables` and `@utils.set`

| Aspect | Details |
|--------|---------|
| **Error** | "Unknown utils declaration type" |
| **Impact** | Cannot use utility actions for setting variables |
| **Workaround** | Use `set` keyword directly in instructions |
| **Note** | These work in GenAiPlannerBundle, just not in AiAuthoringBundle |

```agentscript
# ❌ WRONG - @utils.setVariables not supported
reasoning:
   actions:
      update_state: @utils.setVariables
         with user_name=...
         with is_verified=True

# ❌ WRONG - @utils.set not supported
reasoning:
   actions:
      capture_name: @utils.set
         with user_name=...

# ✅ CORRECT - Use `set` in instructions
reasoning:
   instructions: ->
      | Ask for the user's name.
      set @variables.user_name = ...
      | Verify the user.
      set @variables.is_verified = True
```

---

### `filter_from_agent` Output Attribute

| Aspect | Details |
|--------|---------|
| **Error** | "Unexpected 'filter_from_agent'" |
| **Impact** | Cannot filter outputs from agent visibility |
| **Workaround** | Use conditional topic routing in instructions |
| **Note** | May work in GenAiPlannerBundle |

```agentscript
# ❌ WRONG
outputs:
   order_id: object
      description: "The order ID"
      filter_from_agent: False    # NOT SUPPORTED

# ✅ CORRECT - Omit the attribute
outputs:
   order_id: object
      description: "The order ID"
      is_used_by_planner: True
      is_displayable: False
```

---

### `escalate` as Action Name (Reserved Word)

| Aspect | Details |
|--------|---------|
| **Error** | "Unexpected 'escalate'" |
| **Impact** | Cannot use "escalate" as an action name |
| **Workaround** | Use alternative names like `go_to_escalate`, `transfer_to_human` |

```agentscript
# ❌ WRONG
actions:
   escalate: @utils.escalate       # "escalate" is reserved!
      description: "Transfer to human"

# ✅ CORRECT
actions:
   go_to_escalate: @utils.escalate
      description: "Transfer to human agent"

# ✅ ALSO CORRECT
actions:
   transfer_to_human: @utils.escalate
      description: "Hand off to live agent"
```

---

### `outbound_route_type` Invalid Values

| Aspect | Details |
|--------|---------|
| **Error** | "Invalid value for restricted picklist field" |
| **Impact** | Connection block fails if wrong route type used |
| **Valid Value** | `"OmniChannelFlow"` (ONLY this value works) |
| **Invalid Values** | `"queue"`, `"skill"`, `"agent"` |

```agentscript
# ❌ WRONG
connection messaging:
   outbound_route_type: "queue"
   outbound_route_name: "Support_Queue"

# ❌ WRONG
connection messaging:
   outbound_route_type: "skill"
   outbound_route_name: "Support_Skill"

# ✅ CORRECT
connection messaging:
   outbound_route_type: "OmniChannelFlow"
   outbound_route_name: "Support_Queue_Flow"
   escalation_message: "Transferring you to a human agent..."
```

---

### `@utils.escalate with reason` Syntax

| Aspect | Details |
|--------|---------|
| **Error** | "SyntaxError: Unexpected 'with'" or "SyntaxError: Unexpected 'escalate'" |
| **Impact** | Cannot use `with reason=` parameter for escalation |
| **Workaround** | Use basic `@utils.escalate` with `description:` attribute |
| **Note** | Works in GenAiPlannerBundle |

```agentscript
# ❌ WRONG - `with reason` not supported in AiAuthoringBundle
reasoning:
   actions:
      escalate_human: @utils.escalate with reason="Customer requested human agent"

# ✅ CORRECT - Use description attribute instead
reasoning:
   actions:
      go_to_escalate: @utils.escalate
         description: "Customer requested human agent"
```

---

### `run` Keyword (Action Callbacks)

| Aspect | Details |
|--------|---------|
| **Error** | "SyntaxError: Unexpected 'run'" |
| **Impact** | Cannot chain actions with callbacks |
| **Workaround** | Use GenAiPlannerBundle for action chaining |

```agentscript
# ❌ WRONG - `run` not supported in AiAuthoringBundle
reasoning:
   actions:
      lookup: @actions.get_order
         with order_id=...
         set @variables.order_id = @outputs.order_id
         run @actions.send_confirmation    # FAILS!
            with order_id=@variables.order_id

# ✅ For AiAuthoringBundle - Sequential actions without chaining
# (Action chaining requires GenAiPlannerBundle)
```

---

## ✅ Supported Features

### Math Operators (`+`, `-`)

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Operators** | `+` (addition), `-` (subtraction) |
| **Contexts** | Works in both `set` statements and `if` conditions |

```agentscript
# ✅ Addition in set statement
set @variables.counter = @variables.counter + 1

# ✅ Subtraction in set statement
set @variables.remaining = @variables.total - 100

# ✅ Math in conditions
if @variables.counter + 5 > 10:
   | Counter plus 5 exceeds 10.

if @variables.total - 50 < 0:
   | Would go negative.
```

---

### Action Attributes

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Attributes** | `require_user_confirmation`, `include_in_progress_indicator`, `label` |

```agentscript
actions:
   delete_record:
      description: "Permanently delete a record"
      label: "Delete Record"
      require_user_confirmation: True
      include_in_progress_indicator: False
      inputs:
         inp_RecordId: string
            description: "The record ID to delete"
      outputs:
         out_Success: boolean
            description: "Whether deletion succeeded"
      target: "flow://Delete_Record"

   lookup_account:
      description: "Look up an account by name"
      label: "Account Lookup"
      require_user_confirmation: False
      include_in_progress_indicator: True
      inputs:
         inp_AccountName: string
            description: "The account name"
      outputs:
         out_AccountId: string
            description: "The Account ID"
      target: "flow://Lookup_Account_By_Name"
```

---

### `available when` with Logical Operators

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Operators** | `and`, `or` |

```agentscript
reasoning:
   actions:
      # Both conditions must be true
      go_vip: @utils.transition to @topic.vip_service
         available when @variables.is_verified == True and @variables.tier == "gold"

      # Either condition can be true
      go_priority: @utils.transition to @topic.priority_service
         available when @variables.is_vip == True or @variables.order_total > 1000

      # Multiple available when clauses (all must be true)
      go_checkout: @actions.process_payment
         with amount=@variables.total
         available when @variables.cart_count > 0
         available when @variables.is_verified == True
```

---

### Template Expressions

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Syntax** | `{!@variables.variable_name}` |

```agentscript
reasoning:
   instructions: ->
      | Hello {!@variables.user_name}! Welcome back.
      | Your current account balance is ${!@variables.account_balance}.
      | You have {!@variables.items_in_cart} items in your cart.
      | Your membership tier is: {!@variables.membership_tier}.
```

---

### Topic Delegation Pattern

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Patterns** | `@topic.name` (delegate/return) vs `@utils.transition to` (one-way) |

```agentscript
start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes to specialist topics"

   reasoning:
      instructions: ->
         | Determine what the user needs.
         | Delegate to appropriate specialist topic.
      actions:
         # Delegate and return (consult pattern)
         # Control returns to this topic after specialist is done
         consult_billing: @topic.billing_specialist
         consult_technical: @topic.technical_specialist

         # One-way transition (no return)
         # Control does NOT return to this topic
         go_farewell: @utils.transition to @topic.farewell

topic billing_specialist:
   label: "Billing Specialist"
   description: "Handles billing questions then returns control"

   reasoning:
      instructions: ->
         | Handle the billing question.
         | Provide the answer.
         | Control will return to the caller topic automatically.
```

---

### Lifecycle Blocks

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Blocks** | `before_reasoning`, `after_reasoning` |
| **Important** | Use `transition to` NOT `@utils.transition to` in lifecycle blocks |

```agentscript
topic conversation:
   label: "Conversation"
   description: "Main conversation topic with lifecycle"

   before_reasoning:
      # Runs BEFORE each reasoning step
      set @variables.turn_count = @variables.turn_count + 1

      # First turn initialization
      if @variables.turn_count == 1:
         run @actions.get_timestamp
            set @variables.session_start = @outputs.current_timestamp

      # Conditional routing (use "transition to" not "@utils.transition to")
      if @variables.expired == True:
         transition to @topic.session_expired

   reasoning:
      instructions: ->
         | Turn {!@variables.turn_count}: Help the user.
      actions:
         go_help: @utils.transition to @topic.help

   after_reasoning:
      # Runs AFTER each reasoning step
      # Note: May not run if transition occurs mid-topic
      run @actions.log_turn
         with turn_number=@variables.turn_count
         with topic="conversation"
```

---

### `flow://` Actions

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Critical** | Input/output names must EXACTLY match Flow variable API names |

```agentscript
# Flow variables (in your .flow-meta.xml):
# - inp_AccountId (String, isInput=true)
# - out_AccountName (String, isOutput=true)

actions:
   get_account:
      description: "Get account details by ID"
      inputs:
         # ✅ Name EXACTLY matches Flow variable
         inp_AccountId: string
            description: "The Account ID"
      outputs:
         # ✅ Name EXACTLY matches Flow variable
         out_AccountName: string
            description: "The Account Name"
      target: "flow://Get_Account_Details"

# ❌ WRONG - Name mismatch causes "Internal Error"
actions:
   get_account:
      inputs:
         account_id: string    # Does NOT match "inp_AccountId"!
```

---

### Connection Block

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Required Fields** | `outbound_route_type`, `outbound_route_name`, `escalation_message` |
| **Important** | Referenced OmniChannelFlow must exist in org |

```agentscript
# ✅ CORRECT - All required fields present
connection messaging:
   outbound_route_type: "OmniChannelFlow"
   outbound_route_name: "Support_Queue_Flow"    # Must exist in org!
   escalation_message: "Transferring you to a human agent now..."
```

---

### Variables Without Defaults

| Aspect | Details |
|--------|---------|
| **Status** | ✅ SUPPORTED in AiAuthoringBundle |
| **Note** | Works in both AiAuthoringBundle and GenAiPlannerBundle |

```agentscript
variables:
   # Without defaults - valid
   user_name: mutable string
      description: "The customer's name"
   order_count: mutable number
      description: "Number of items in cart"
   is_verified: mutable boolean
      description: "Whether identity is verified"

   # With defaults - also valid
   status: mutable string = ""
      description: "Current status"
   counter: mutable number = 0
      description: "A counter"
```

---

## ⚠️ Deployment Gotchas

### HTTP 404 During "Retrieve Metadata"

| Aspect | Details |
|--------|---------|
| **What Happens** | BotDefinition IS created ✔ but agent INVISIBLE in Agentforce Studio UI |
| **Why** | AiAuthoringBundle metadata not deployed to org |
| **Fix** | Run `sf project deploy start` after seeing this error |

```bash
# After seeing HTTP 404 during "Retrieve Metadata":
sf project deploy start \
  --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] \
  --target-org [alias]

# Verify metadata deployed:
sf org list metadata --metadata-type AiAuthoringBundle --target-org [alias]
```

---

### HTTP 404 During "Publish Agent"

| Aspect | Details |
|--------|---------|
| **What Happens** | BotDefinition NOT created ✘ |
| **Common Cause** | Referenced OmniChannelFlow doesn't exist in org |
| **Fix** | Create the OmniChannelFlow before publishing agent |

```bash
# Check if flow exists:
sf org list metadata --metadata-type Flow --target-org [alias] | grep [FlowName]

# Deploy the flow first:
sf project deploy start \
  --source-dir force-app/main/default/flows/[FlowName].flow-meta.xml \
  --target-org [alias]

# Then publish agent:
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

---

### "Internal Error, try again later"

| Aspect | Details |
|--------|---------|
| **Common Cause** | Flow variable name mismatch between Agent Script and Flow |
| **Fix** | Ensure Agent Script input/output names EXACTLY match Flow variable API names |

```
ERROR: "property account_id was not found in the available list of
        properties: [inp_AccountId]"

This appears as generic "Internal Error, try again later" in CLI.
```

---

### Validation Passes, Deploy Fails

| Aspect | Details |
|--------|---------|
| **Why** | `sf agent validate` only checks syntax, not org resources |
| **Fix** | Deploy referenced Flows BEFORE publishing agent |

```bash
# 1. Deploy flows first
sf project deploy start --metadata Flow:Get_Order_Details --target-org [alias]

# 2. Then publish agent
sf agent publish authoring-bundle --api-name My_Agent --target-org [alias]
```

---

## 🔑 Reserved Words

These words cannot be used as input/output parameter names or action names:

| Reserved Word | Why Reserved | Alternative Names |
|---------------|--------------|-------------------|
| `description` | Keyword for descriptions | `case_description`, `item_description`, `desc` |
| `inputs` | Keyword for action inputs | `input_data`, `request_inputs`, `params` |
| `outputs` | Keyword for action outputs | `output_data`, `response_outputs`, `results` |
| `target` | Keyword for action target | `destination`, `endpoint`, `flow_target` |
| `label` | Keyword for topic label | `display_label`, `title`, `name` |
| `source` | Keyword for linked variables | `data_source`, `origin`, `source_field` |
| `escalate` | Reserved for `@utils.escalate` | `go_to_escalate`, `transfer_to_human`, `human_handoff` |

---

## 📋 Error Quick Reference

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| "type integer is not supported" | Using `integer` or `long` type | Use `number` instead |
| "Start token somehow not of the form \| + 2 spaces" | Nested pipes | Flatten structure |
| "Missing required element" + "Unexpected 'else'" | Nested if statements | Use flat `and` conditionals |
| "Unexpected '<'" | Using `list<type>` syntax | Use `list[type]` |
| "Unknown utils declaration type" | Using `@utils.setVariables` or `@utils.set` | Use `set` keyword in instructions |
| "Unexpected 'filter_from_agent'" | Using `filter_from_agent` attribute | Omit attribute |
| "Unexpected 'escalate'" | Using `escalate` as action name | Use `go_to_escalate` |
| "Invalid value for restricted picklist" | Wrong `outbound_route_type` | Use `"OmniChannelFlow"` |
| "Unexpected 'with'" (escalation) | Using `@utils.escalate with reason=` | Use basic `@utils.escalate` |
| "Unexpected 'run'" | Using `run` for action chaining | Use GenAiPlannerBundle |
| "Internal Error, try again later" | Flow variable name mismatch | Match names exactly |
| HTTP 404 at "Retrieve Metadata" | Metadata not deployed | Run `sf project deploy start` |
| HTTP 404 at "Publish Agent" | Missing OmniChannelFlow | Create flow first |
| "Unexpected 'if'" (slot filling) | `set x = ...` inside conditional | Move slot filling outside conditionals |
| "SyntaxError" on `@utils.transition` | `description:` on transition action | Remove description from transitions |
| "ValidationError" on `@utils.escalate` | Missing `description:` field | Add required description field |
| "SyntaxError" in lifecycle block | Empty `before/after_reasoning` block | Remove empty blocks or add content |
| "Unexpected '{'" in action | `{!@actions.x}` interpolation | Define actions explicitly, LLM auto-selects |

---

## Testing Methodology

All findings in this document were verified through systematic testing:

1. Create test agent with specific feature
2. Run: `sf agent validate authoring-bundle --api-name [Agent]`
3. If validates, run: `sf agent publish authoring-bundle --api-name [Agent]`
4. Document errors and workarounds
5. Fix agent and re-test to confirm workaround
6. Update documentation

**Total Test Agents Created:** 22

**Last Updated:** December 2025
