# Instruction Action References

> Using `{!@actions.action_name}` to guide LLM action selection

**Navigation**: [← Back to Index](actions-INDEX.md)

---

## Overview

Instruction Action References enable developers to guide LLM decision-making by explicitly mentioning actions within reasoning instructions using the syntax `{!@actions.action_name}`.

**Key benefit**: Creates a stronger association between the context and the tool when multiple actions could apply but one is preferred in specific situations.

---

## Core Syntax

### Action Reference

```agentscript
{!@actions.action_name}
```

### Variable Reference

```agentscript
{!@variables.variable_name}
```

---

## How It Works

When you embed an action reference in instructions:

- The system doesn't simply insert the action name
- It embeds **a reference to the full action definition**
- Provides the LLM with richer context about:
  - Action's purpose
  - Required inputs
  - Expected outputs
  - When to use it

---

## Conditional Instruction Pattern

Combine action references with procedural logic:

```agentscript
topic business_hours_routing:
  data:
    @variables.next_open_time: ...

  reasoning:
    instructions: ->
      if @variables.next_open_time:
        | We are currently OUTSIDE business hours.
          The next available time is {!@variables.next_open_time}.
          Create a support case using {!@actions.create_case} to ensure
          follow-up during business hours.
      else:
        | We are currently WITHIN business hours.
          Connect the customer to live support using {!@actions.transfer_to_agent}.
```

---

## Complete Example: Payment Workflow

```agentscript
topic payment_processing:
  reasoning:
    instructions: ->
      | When processing payments, follow this workflow:
        1. Verify payment details using {!@actions.verify_payment_info}
        2. If verification succeeds, process with {!@actions.process_payment}
        3. If verification fails, request corrections using {!@actions.request_payment_update}

    actions:
      verify_payment_info:
        description: "Verify customer payment information"
        # ... action definition ...

      process_payment:
        description: "Process the payment transaction"
        # ... action definition ...

      request_payment_update:
        description: "Request updated payment information"
        # ... action definition ...
```

---

## Use Cases

### ✅ When to Use Action References

- **Multiple valid actions** - Several could apply, one is contextually preferred
- **Enforce workflow** - Specific sequence must be followed
- **Clarify ambiguity** - Action name alone doesn't convey when to use it
- **Complex routing** - Conditional logic determines best action
- **Policy enforcement** - Business rules dictate action selection

### Real-World Examples

#### Security Verification Flow

```agentscript
topic identity_verification:
  reasoning:
    instructions: ->
      if @variables.verification_attempts < 3:
        | Please verify your identity using {!@actions.verify_email_code}
          or {!@actions.verify_phone_code}.
      else:
        | Maximum attempts reached. Escalate using {!@actions.escalate_to_security}.
```

#### Order Status Routing

```agentscript
topic order_inquiry:
  reasoning:
    instructions: ->
      if @variables.order_status == "shipped":
        | Track the shipment using {!@actions.get_tracking_info}.
      if @variables.order_status == "processing":
        | Check processing status using {!@actions.get_fulfillment_status}.
      if @variables.order_status == "cancelled":
        | Handle cancellation using {!@actions.initiate_refund}.
```

---

## Benefits

### Improved Action Selection

By embedding full action context, the LLM has more information to make accurate decisions:

- **Without references**: "Use create_case action"
- **With references**: Full definition of create_case (inputs, outputs, purpose) embedded inline

### Contextual Prompts

Combine with dynamic variables for targeted guidance:

```agentscript
instructions: ->
  | Customer tier: {!@variables.customer_tier}
    Priority level: {!@variables.priority}

  if @variables.customer_tier == "premium":
    | Offer immediate assistance using {!@actions.premium_support}.
  else:
    | Create standard case using {!@actions.standard_support}.
```

---

## Pattern: Multi-Step Guided Workflow

```agentscript
topic refund_workflow:
  reasoning:
    instructions: ->
      | To process a refund:
        1. Verify eligibility using {!@actions.check_refund_eligibility}
        2. If eligible:
           - Calculate amount with {!@actions.calculate_refund_amount}
           - Process using {!@actions.issue_refund}
           - Notify customer with {!@actions.send_refund_confirmation}
        3. If not eligible:
           - Explain with {!@actions.explain_refund_policy}
```

---

## Combining with Available When

Strengthen control by combining instruction references with action guards:

```agentscript
topic secure_operations:
  reasoning:
    instructions: ->
      if @variables.verified == True:
        | You can now access sensitive operations using {!@actions.view_account_details}.
      else:
        | Please verify your identity first.

    actions:
      view_account_details: @actions.get_account_info
        available when @variables.verified == True
        description: "View sensitive account information"
```

**Result**: Both instruction guidance AND deterministic guard prevent unauthorized access.

---

## Best Practices

### ✅ DO

- Combine action references with dynamic variable expressions
- Use to guide the LLM toward specific actions in context
- Include action references in conditional instructions
- Create targeted prompts that improve action selection accuracy
- Test that references actually improve LLM decision-making

### ❌ DON'T

- Overuse references where action names are already clear
- Reference actions that aren't defined in the topic
- Rely solely on references without clear instructions
- Forget to define the referenced actions
- Use for actions with obvious use cases

---

## Comparison: Descriptions vs References

| Approach | When to Use |
|----------|-------------|
| [Description Overrides](actions-descriptions.md) | Action needs different descriptions per topic/context |
| **Instruction References** | Need to explicitly guide LLM toward action in instructions |
| Both | Maximum control - override description AND reference in instructions |

---

## Testing Tips

### Validate References Are Helping

1. Test without references - observe action selection
2. Add references - observe if selection improves
3. Compare LLM decision accuracy
4. Keep references if they provide measurable benefit

---

## Related Topics

- **Alternative approach**: [actions-descriptions.md](actions-descriptions.md) - Context-aware descriptions
- **Prerequisites**: [actions-definitions.md](actions-definitions.md) - Define actions first
- **Troubleshooting**: [actions-troubleshooting.md](actions-troubleshooting.md) - Fix reference errors

---

*Part of the [Agent Script Actions Reference](actions-INDEX.md)*
