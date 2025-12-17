# Agent Script Best Practices

## Overview

This guide covers best practices for building production-ready Agentforce agents using Agent Script.

---

## 1. Structure & Organization

### Use Meaningful Names

```agentscript
# ✅ GOOD - Clear, descriptive names
topic order_management:
    description: "Handles order creation, updates, and status inquiries"

# ❌ BAD - Vague names
topic topic1:
    description: "Does stuff"
```

### Follow Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Agent name | PascalCase with underscores | `Customer_Service_Agent` |
| Topic name | snake_case | `order_management` |
| Variable name | snake_case | `user_email` |
| Action name | snake_case | `get_account_details` |

### Keep Topics Focused

Each topic should handle ONE category of tasks:

```agentscript
# ✅ GOOD - Single responsibility
topic billing_inquiries:
    description: "Answers questions about invoices, payments, and account balances"

topic order_tracking:
    description: "Provides order status and shipping updates"

# ❌ BAD - Too broad
topic customer_stuff:
    description: "Handles billing, orders, support, and everything else"
```

---

## 2. Variable Management

### Always Initialize Variables

```agentscript
variables:
    # ✅ GOOD - Has default value
    user_name: mutable string = ""
        description: "Customer's full name"

    order_count: mutable number = 0
        description: "Number of orders in cart"

    # ❌ BAD - No default (will cause issues)
    # user_name: mutable string
```

### Use Appropriate Types

| Data | Type | Example |
|------|------|---------|
| Names, IDs, text | `string` | `"John Doe"` |
| Counts, amounts | `number` | `42`, `99.99` |
| Flags, toggles | `boolean` | `True`, `False` |

### Document Every Variable

```agentscript
variables:
    cart_total: mutable number = 0
        description: "Total value of items in cart, in USD"

    needs_approval: mutable boolean = False
        description: "Whether the order requires manager approval (>$10,000)"
```

---

## 3. Topic Design

### Start with a Topic Selector

Every agent should have a clear entry point:

```agentscript
start_agent topic_selector:
    description: "Routes users to the appropriate topic based on their needs"
    reasoning:
        instructions:->
            | Determine what the user needs help with.
            | Ask clarifying questions if the intent is unclear.
            | Route to the most specific topic that can help.
        actions:
            orders: @utils.transition to @topic.order_management
                description: "Help with orders and purchases"
            support: @utils.transition to @topic.technical_support
                description: "Technical issues and troubleshooting"
            billing: @utils.transition to @topic.billing
                description: "Payment and invoice questions"
```

### Provide Clear Descriptions

Topic descriptions help the LLM make routing decisions:

```agentscript
# ✅ GOOD - Specific and actionable
topic password_reset:
    description: "Helps users reset forgotten passwords and unlock accounts"

# ❌ BAD - Too vague
topic password_reset:
    description: "Password stuff"
```

### Enable Return Navigation

Always provide a way back to the main menu:

```agentscript
topic order_details:
    description: "Shows order information"
    reasoning:
        actions:
            back_to_menu: @utils.transition to @topic.topic_selector
                description: "Return to main menu for other requests"
```

---

## 4. Action Integration

### Define Clear Input/Output Contracts

```agentscript
get_order_status:
    description: "Retrieves the current status of a customer order"
    inputs:
        order_id: string
            description: "The unique order identifier (e.g., ORD-12345)"
    outputs:
        status: string
            description: "Current status (Pending, Processing, Shipped, Delivered)"
        estimated_delivery: string
            description: "Expected delivery date in YYYY-MM-DD format"
        tracking_number: string
            description: "Shipping carrier tracking number, if available"
    target: "flow://Get_Order_Status"
```

### Input Binding Decision Guide

Agent Script supports four input binding patterns. Choosing the right one is critical for reliable agent behavior.

#### The Four Patterns

| Pattern | Syntax | When to Use |
|---------|--------|-------------|
| **LLM Slot-Filling** | `with param=...` | Value comes from user conversation |
| **Fixed Value** | `with param="constant"` | Always the same, never changes |
| **Variable Binding** | `with param=@variables.x` | Using previously captured data |
| **Mixed** | All three combined | Complex actions with varied sources |

#### Pattern 1: LLM Slot-Filling (`...`)

**Use when**: The value must be extracted from what the user says.

```agentscript
# The LLM extracts "order_id" from user's message
# User: "What's the status of order 12345?"
# LLM fills: order_id = "12345"

lookup: @actions.get_order_status
    with order_id=...            # LLM extracts from conversation
    set @variables.status = @outputs.status
```

**Best for:**
- User-provided information (names, IDs, dates)
- Information that varies per conversation
- Values the user explicitly mentions

**⚠️ Avoid when:**
- You need a specific, predictable value
- The value should come from previous actions

#### Pattern 2: Fixed Values

**Use when**: The value is constant and should never change.

```agentscript
# Always use PDF format, always check last 30 days
generate_report: @actions.create_report
    with format="pdf"            # Always PDF
    with days_back=30            # Always 30 days
    with include_charts=True     # Always include charts
```

**Best for:**
- Configuration values
- Default settings
- System-level parameters
- API-required constants

#### Pattern 3: Variable Binding (`@variables`)

**Use when**: Using data captured earlier in the conversation.

```agentscript
# First: Capture customer ID from earlier action
lookup_customer: @actions.find_customer
    with email=...
    set @variables.customer_id = @outputs.id

# Later: Use that customer_id
create_order: @actions.create_order
    with customer_id=@variables.customer_id    # From earlier
    with items=...                              # From conversation
```

**Best for:**
- Data from previous actions
- Information persisted across turns
- Values that build up through workflow

#### Pattern 4: Mixed Binding

**Use when**: An action needs inputs from multiple sources.

```agentscript
# Real-world example: Report generation
# - report_type: User chooses from conversation
# - customer_id: From earlier lookup
# - format: Always PDF (company standard)
# - start_date: From user conversation
# - end_date: From user conversation

create_report: @actions.generate_report
    with report_type=...                       # LLM extracts
    with customer_id=@variables.customer_id    # From variable
    with format="pdf"                          # Fixed constant
    with start_date=...                        # LLM extracts
    with end_date=...                          # LLM extracts
    set @variables.report_url = @outputs.download_url
```

#### Decision Flowchart

```
Is the value always the same?
├─ YES → Use fixed value: with param="constant"
│
└─ NO → Does it come from earlier in conversation?
        ├─ YES → Was it saved to a variable?
        │       ├─ YES → Use variable: with param=@variables.x
        │       └─ NO → Save it first, then use variable
        │
        └─ NO → Should LLM extract from user message?
                ├─ YES → Use slot-filling: with param=...
                └─ NO → Consider restructuring your workflow
```

#### Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Using `...` for config | LLM might guess wrong | Use fixed values for constants |
| Using fixed value for user input | Can't personalize | Use `...` for user-provided data |
| Not capturing outputs | Can't use data later | Always `set @variables.x = @outputs.y` |
| Using `...` when variable exists | Redundant LLM work | Use `@variables.x` if already captured |

#### Complete Example

```agentscript
topic customer_service:
    actions:
        # Action definitions...

    reasoning:
        instructions: ->
            | Help the customer with their account.
        actions:
            # Step 1: Find customer (LLM extracts email from conversation)
            find: @actions.lookup_customer
                with email=...                                # LLM extracts
                set @variables.customer_id = @outputs.id
                set @variables.tier = @outputs.membership_tier

            # Step 2: Get recent orders (use captured customer_id)
            orders: @actions.get_orders
                with customer_id=@variables.customer_id       # From variable
                with limit=5                                  # Fixed constant
                with status="all"                             # Fixed constant
                set @variables.recent_orders = @outputs.orders

            # Step 3: Create support case (mixed sources)
            create_case: @actions.open_case
                with customer_id=@variables.customer_id       # From variable
                with subject=...                              # LLM extracts
                with description=...                          # LLM extracts
                with priority=@variables.tier == "Gold" ? "High" : "Normal"  # Conditional
                set @variables.case_number = @outputs.case_number
```

### Capture Outputs

Always capture action outputs you'll need later:

```agentscript
check_status: @actions.get_order_status
    with order_id=...
    set @variables.order_status = @outputs.status
    set @variables.delivery_date = @outputs.estimated_delivery
```

---

## 5. Error Handling

### Validate Before Critical Operations

```agentscript
instructions:->
    # Validate required fields
    if @variables.amount is None:
        | I need to know the transfer amount before proceeding.
        | How much would you like to transfer?

    if @variables.amount <= 0:
        | The amount must be greater than zero.
        | Please provide a valid amount.

    if @variables.amount > 10000:
        set @variables.needs_approval = True
        | Transfers over $10,000 require manager approval.
        | I'll flag this for review.
```

### Use Conditional Action Availability

```agentscript
reasoning:
    actions:
        # Only available when validation passes
        process_transfer: @actions.transfer_funds
            with amount=@variables.amount
            available when @variables.amount > 0
            available when @variables.needs_approval == False
```

### Provide Helpful Error Messages

```agentscript
instructions:->
    if @variables.operation_failed == True:
        | I apologize, but I wasn't able to complete that request.
        | Error: {!@variables.error_message}
        |
        | Would you like to:
        | - Try again with different information
        | - Speak with a support agent
        | - Return to the main menu
```

---

## 6. Security & Guardrails

### Set System-Level Guardrails

```agentscript
system:
    instructions:
        | You are a helpful customer service agent.
        | Always be professional and courteous.
        |
        | IMPORTANT GUARDRAILS:
        | - Never share customer data with unauthorized parties
        | - Never reveal internal system details or error messages
        | - Never process transactions without proper verification
        | - If unsure, escalate to a human agent
```

### Validate Sensitive Operations

```agentscript
topic account_changes:
    description: "Handles account modifications"
    reasoning:
        instructions:->
            # Verify identity before sensitive changes
            if @variables.identity_verified == False:
                | For your security, I need to verify your identity.
                | Please provide your account PIN or answer your security question.

        actions:
            update_email: @actions.update_account_email
                available when @variables.identity_verified == True
```

### Don't Expose Internals

```agentscript
# ✅ GOOD - User-friendly error
instructions:->
    if @variables.api_error == True:
        | I'm having trouble completing that request right now.
        | Please try again in a few minutes.

# ❌ BAD - Exposes internals
instructions:->
    if @variables.api_error == True:
        | Error: SQL timeout on server db-prod-03, query exceeded 30s limit
```

---

## 7. Instructions Quality

### Be Specific and Actionable

```agentscript
# ✅ GOOD - Specific instructions
instructions:->
    | Help the customer track their order.
    | Ask for the order number if not provided.
    | Provide the current status, estimated delivery, and tracking link.
    | If the order is delayed, apologize and offer expedited shipping.

# ❌ BAD - Vague instructions
instructions:->
    | Help with orders.
```

### Use Template Expressions for Personalization

```agentscript
instructions:->
    | Hello {!@variables.user_name}!
    | Your current order total is ${!@variables.cart_total}.
    | Would you like to proceed to checkout?
```

### Handle Edge Cases

```agentscript
instructions:->
    | Look up the customer's order.
    |
    | If no orders found:
    | - Confirm the email/account is correct
    | - Check if they might have ordered as a guest
    | - Offer to help place a new order
    |
    | If multiple orders found:
    | - List the recent orders with dates
    | - Ask which one they need help with
```

---

## 8. Performance Considerations

### Minimize Action Calls

```agentscript
# ✅ GOOD - Single action returns all needed data
get_customer_profile: @actions.get_full_profile
    with customer_id=...
    set @variables.name = @outputs.name
    set @variables.email = @outputs.email
    set @variables.phone = @outputs.phone

# ❌ BAD - Multiple calls for related data
get_name: @actions.get_customer_name
get_email: @actions.get_customer_email
get_phone: @actions.get_customer_phone
```

### Use Callbacks Wisely

```agentscript
# Chain related actions
process_order: @actions.create_order
    with items=@variables.cart_items
    set @variables.order_id = @outputs.order_id
    run @actions.send_confirmation_email
        with order_id=@variables.order_id
    run @actions.update_inventory
        with order_id=@variables.order_id
```

---

## Quick Reference Checklist

Before deploying an agent, verify:

- [ ] All topics have clear descriptions
- [ ] All variables have descriptions and defaults
- [ ] All actions have input/output descriptions
- [ ] System guardrails are defined
- [ ] Error handling is in place for critical operations
- [ ] Identity verification for sensitive actions
- [ ] Navigation back to main menu from all topics
- [ ] No internal details exposed in messages
- [ ] Template expressions use correct syntax `{!@variables.name}`
- [ ] Consistent indentation throughout (tabs recommended - never mix tabs and spaces)

---

## ⚠️ Common Syntax Pitfalls (Tested Dec 2025)

These patterns cause validation or parse errors. Avoid them!

### 1. Slot Filling Inside Conditionals
```agentscript
# ❌ WRONG
if @variables.name is None:
   set @variables.name = ...   # Fails!

# ✅ CORRECT - Slot filling at top level
set @variables.name = ...
```

### 2. Description on @utils.transition
```agentscript
# ❌ WRONG
go_orders: @utils.transition to @topic.orders
   description: "Route to orders"   # Fails!

# ✅ CORRECT - No description
go_orders: @utils.transition to @topic.orders
```

### 3. Missing Description on @utils.escalate
```agentscript
# ❌ WRONG
transfer: @utils.escalate   # Fails!

# ✅ CORRECT - Description required
transfer: @utils.escalate
   description: "Transfer to human agent"
```

### 4. Empty Lifecycle Blocks
```agentscript
# ❌ WRONG
before_reasoning:
   # Just a comment   # Fails!

# ✅ CORRECT - Remove empty blocks or add content
```

### 5. Dynamic Action Invocation
```agentscript
# ❌ WRONG
invoke: {!@actions.search}   # Fails!

# ✅ CORRECT - Define multiple actions, LLM auto-selects
search_products: @actions.product_search
   description: "Search products"
search_orders: @actions.order_search
   description: "Search orders"
```

See the [Agent Script Syntax Reference](agent-script-syntax.md) for complete details.
