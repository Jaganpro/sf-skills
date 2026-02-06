# Advanced Input Bindings

> Four patterns for populating action parameters

**Navigation**: [← Back to Index](actions-INDEX.md)

---

## Overview

Agent Script supports four primary input binding approaches for action parameters:

1. LLM Slot-Filling (`...`)
2. Variable Binding (`@variables.name`)
3. Fixed Values (constants)
4. Mixed Binding (combination)

---

## Pattern 1: LLM Slot-Filling

### Syntax: `...`

Allows AI to extract values from user conversation:

```agentscript
search_knowledge: @actions.search_kb
  with query=...
       max_results=...
```

### When to Use

- User-provided information (dates, names, queries)
- Dynamic values from conversation context
- Information the LLM should extract

### Example

```agentscript
create_case: @actions.create_support_case
  with subject=...           # LLM extracts from conversation
       description=...        # LLM summarizes issue
       priority=...           # LLM determines urgency
```

---

## Pattern 2: Variable Binding

### Syntax: `@variables.name`

Reuses previously stored data:

```agentscript
create_case: @actions.create_support_case
  with customer_id=@variables.user_id
       email=@variables.user_email
```

### When to Use

- Data from previous turns
- Stored preferences or session data
- Values captured from earlier actions

### Example

```agentscript
# Earlier in conversation - capture data
verify: @actions.verify_customer
  with email=...
  set @variables.customer_id = @outputs.id
  set @variables.verified = @outputs.success

# Later - reuse captured data
create_order: @actions.create_order
  with customer_id=@variables.customer_id      # Reuse captured value
       verified=@variables.verified            # Reuse verification status
```

---

## Pattern 3: Fixed Values

### Syntax: Literal constants

Hardcoded values that remain unchanged:

```agentscript
generate_report: @actions.create_report
  with format="pdf"
       include_charts=True
       page_size="letter"
```

### When to Use

- System constants
- Default settings
- Configuration values
- Immutable business rules

### Example

```agentscript
send_notification: @actions.send_email
  with template="order_confirmation"
       priority="high"
       include_logo=True
```

---

## Pattern 4: Mixed Binding

### Combining All Approaches

Sophisticated parameter handling using multiple sources:

```agentscript
send_notification: @actions.send_email
  with recipient=@variables.user_email          # Variable binding
       subject=...                               # LLM slot-filling
       template="case_confirmation"             # Fixed value
       priority="high"                          # Fixed value
       case_id=@variables.case_id               # Variable binding
```

### Real-World Example

```agentscript
process_refund: @actions.process_refund_request
  with order_id=@variables.order_id             # From previous action
       reason=...                                # User explains why
       amount=@variables.order_total            # Stored value
       refund_method="original_payment"         # Business rule
       require_approval=True                    # Policy constant
```

---

## Decision Matrix

| Binding Type | Use When | Example |
|--------------|----------|---------|
| `...` | User provides information | `with query=...` |
| `@variables.X` | Data already exists | `with customer_id=@variables.id` |
| Fixed values | System constants | `with format="pdf"` |
| Mixed | Complex actions | Combination of above |

---

## Best Practices

### ✅ DO

- Use variable binding when data already exists from prior interactions
- Reserve fixed values for system-level constants and business rules
- Allow LLM extraction for user-provided data
- Mix binding types when appropriate for the use case
- Document why each binding pattern was chosen

### ❌ DON'T

- Use LLM extraction for values the system already knows
- Hardcode user input (use `...` instead)
- Overuse fixed values when flexibility is needed
- Mix patterns without clear reasoning

---

## Common Patterns

### Pattern: Session Data + User Input

```agentscript
book_appointment: @actions.create_appointment
  with customer_id=@variables.customer_id       # Session data
       date=...                                  # User provides
       time=...                                  # User provides
       service_type=...                          # User selects
       duration=30                               # Fixed default
```

### Pattern: Captured Output + New Input

```agentscript
# First action - capture data
search: @actions.search_products
  with query=...
  set @variables.product_id = @outputs.top_result_id

# Second action - use captured + new input
add_to_cart: @actions.add_to_cart
  with product_id=@variables.product_id         # From previous action
       quantity=...                              # User specifies
       apply_discount=True                       # Business rule
```

### Pattern: Configuration + Dynamic Values

```agentscript
generate_analytics: @actions.create_analytics_report
  with report_type=...                          # User chooses
       date_range=...                            # User specifies
       format="pdf"                              # System default
       include_charts=True                       # System default
       email_recipient=@variables.user_email    # Session data
```

---

## Slot-Filling Constraints

### Where NOT to Use `...`

```agentscript
# ❌ WRONG - Using ... as default value in variable declaration
variables:
  order_id: mutable string = ...               # ERROR: Not valid here

# ✅ CORRECT - Use ... only in action parameter binding
reasoning:
  actions:
    search: @actions.search_products
      with query=...           # ✅ LLM extracts from user message
           category=...        # ✅ LLM decides based on context
           limit=10            # ✅ Fixed value
```

**The `...` syntax is for LLM slot-filling only** - it tells the LLM to extract the value from conversation context.

---

## Validation Tips

### Test Your Bindings

- **Fixed values**: Ensure they match your business requirements
- **Variable bindings**: Confirm variables are populated before use
- **LLM slot-filling**: Test that LLM correctly extracts values
- **Mixed patterns**: Verify each binding source works independently

---

## Related Topics

- **Prerequisites**: [actions-definitions.md](actions-definitions.md) - Define action inputs first
- **Related**: [actions-callbacks.md](actions-callbacks.md) - Passing values between actions
- **Troubleshooting**: [actions-troubleshooting.md](actions-troubleshooting.md) - Fix binding errors

---

*Part of the [Agent Script Actions Reference](actions-INDEX.md)*
