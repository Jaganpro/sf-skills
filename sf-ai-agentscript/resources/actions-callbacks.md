# Action Callbacks

> Chaining actions with the `run` keyword for sequential execution

**Navigation**: [← Back to Index](actions-INDEX.md)

---

## Overview

Action callbacks enable post-action execution chaining, allowing sequential action invocation after a primary action completes successfully.

---

## Core Syntax

```agentscript
primary_action: @actions.do_something
  with input=...
  set @variables.result = @outputs.data
  run @actions.handle_result
    with result_data=@variables.result
```

---

## Key Characteristics

### Execution Rules

- The `run` keyword triggers callback execution
- **Only one nesting level permitted** - callbacks cannot contain nested callbacks
- Output capture occurs before chaining subsequent actions
- Multiple sequential `run` statements execute in order

### Restriction: No Nested Callbacks

```agentscript
# ❌ WRONG - Nested callbacks (not allowed)
action1: @actions.first
  run @actions.second
    run @actions.third  # ERROR: Nested callbacks not supported

# ✅ CORRECT - Sequential callbacks (flat structure)
action1: @actions.first
  run @actions.second
  run @actions.third
```

---

## Complete Example: Payment Processing

```agentscript
topic payment:
  reasoning:
    actions:
      make_payment: @actions.process_payment
        with amount=@variables.payment_amount
             customer_id=...
        set @variables.transaction_id = @outputs.transaction_id
        run @actions.send_receipt
          with transaction_id=@variables.transaction_id
          set @variables.receipt_sent = @outputs.sent
        run @actions.award_points
          with amount=@variables.payment_amount
          set @variables.points_awarded = @outputs.points
```

**Execution flow**:

1. `@actions.process_payment` executes
2. Capture `transaction_id` to variable
3. `@actions.send_receipt` executes with transaction_id
4. Capture `receipt_sent` status
5. `@actions.award_points` executes with payment amount
6. Capture `points_awarded`

---

## When to Use Callbacks

### ✅ Appropriate Use Cases

- **Dependent operations** - Payment completion triggers receipt generation
- **Audit trails** - Sequential logging of related actions
- **Data passing** - Transferring data between related actions via variables
- **Workflow sequences** - Multi-step processes that must occur in order

### ❌ Avoid When

- **Independent actions** - Actions that don't depend on each other
- **Deep nesting needed** - Refactor into separate topics instead
- **Complex branching** - Use conditional transitions instead

---

## Variable Passing Pattern

Always capture outputs before chaining:

```agentscript
create_order: @actions.create_order
  with customer_id=...
       items=@variables.cart_items
  set @variables.order_id = @outputs.id           # Capture first
  run @actions.create_invoice
    with order_id=@variables.order_id             # Use captured value
    set @variables.invoice_id = @outputs.id
  run @actions.send_confirmation
    with order_id=@variables.order_id             # Reuse captured value
         invoice_id=@variables.invoice_id
```

---

## Callback Limitations

### Only Works with @actions.*

Post-action directives (`set`, `run`, `if`) only work on `@actions.*`:

```agentscript
# ❌ WRONG - @utils does NOT support callbacks
go_next: @utils.transition to @topic.main
  set @variables.visited = True   # ERROR!

# ✅ CORRECT - Only @actions.* supports post-action directives
process: @actions.process_order
  with order_id=@variables.order_id
  set @variables.status = @outputs.status        # ✅ Works
  run @actions.send_notification                 # ✅ Works
```

**See SKILL.md** for the Helper Topic Pattern workaround.

---

## Error Handling

Callbacks only execute if the parent action succeeds:

```agentscript
verify_payment: @actions.verify_payment_method
  with payment_method_id=...
  set @variables.verified = @outputs.success
  run @actions.process_payment                    # Only runs if verify succeeds
    with payment_method_id=...
```

If `verify_payment` fails, `process_payment` will not execute.

---

## Best Practices

### ✅ DO

- Capture outputs immediately before chaining
- Document callback dependencies clearly in descriptions
- Use variables for inter-action data transfer
- Keep callback chains short and focused (2-4 actions max)
- Test the entire callback chain as a unit

### ❌ DON'T

- Nest `run` statements within callbacks (not supported)
- Chain unrelated actions together
- Create circular dependencies
- Skip capturing outputs you'll need later
- Mix `@utils.*` and `@actions.*` expecting same behavior

---

## Common Pattern: Create → Notify → Log

```agentscript
create_case: @actions.create_support_case
  with subject=...
       description=...
       priority=@variables.priority
  set @variables.case_id = @outputs.id
  run @actions.notify_team
    with case_id=@variables.case_id
         priority=@variables.priority
  run @actions.log_case_creation
    with case_id=@variables.case_id
         timestamp=@outputs.created_date
```

---

## Related Topics

- **Prerequisites**: [actions-definitions.md](actions-definitions.md) - Define actions first
- **Next**: [actions-input-bindings.md](actions-input-bindings.md) - Configure inputs
- **Troubleshooting**: [actions-troubleshooting.md](actions-troubleshooting.md) - Fix callback errors

---

*Part of the [Agent Script Actions Reference](actions-INDEX.md)*
