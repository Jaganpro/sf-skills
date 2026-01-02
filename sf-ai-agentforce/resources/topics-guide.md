# Topics Design Guide

Guide to designing topics, routing patterns, and transitions in Agentforce agents.

## Table of Contents

- [Topic Fundamentals](#topic-fundamentals)
- [Topic Structure](#topic-structure)
- [Topic Transitions](#topic-transitions)
- [Topic Delegation vs Transition](#topic-delegation-vs-transition)
- [Routing Patterns](#routing-patterns)
- [Multi-Topic Agents](#multi-topic-agents)
- [Bidirectional Routing](#bidirectional-routing)
- [Best Practices](#best-practices)

---

## Topic Fundamentals

**Topics** are conversation modes that group related actions and reasoning logic. Think of them as "skill areas" or "conversation contexts" for your agent.

### Why Use Topics?

| Benefit | Description |
|---------|-------------|
| **Separation of Concerns** | Group related functionality (e.g., "Order Management", "Support") |
| **Focused Instructions** | Each topic has its own reasoning instructions |
| **Action Scoping** | Actions defined in a topic are available only in that topic |
| **Persona Switching** | Topics can override system instructions for different modes |

---

## Topic Structure

### Required Fields

Every topic MUST have:
- `label:` - Display name for the topic
- `description:` - What the topic does (used by LLM for routing)

```agentscript
topic order_lookup:
   label: "Order Lookup"
   description: "Helps customers look up their order status and details"

   reasoning:
      instructions: ->
         | Help the user find their order.
```

### Optional Blocks

| Block | Purpose | Example |
|-------|---------|---------|
| `system:` | Override global system instructions | Persona switching |
| `actions:` | Define topic-specific actions | Flow/Apex actions |
| `reasoning:` | Topic reasoning logic | Instructions + action invocations |

---

## Topic Transitions

### `@utils.transition to @topic.[name]`

Permanently move to another topic. The user CANNOT return to the previous topic without explicit routing.

```agentscript
start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes users to topics"

   reasoning:
      instructions: ->
         | What would you like to do?
         | 1. Check order status
         | 2. Get support
      actions:
         go_orders: @utils.transition to @topic.order_lookup
         go_support: @utils.transition to @topic.support
```

**When to Use:**
- **Permanent mode switches** (e.g., "I want to check my order" → order_lookup)
- **One-way transitions** where user won't return to previous topic
- **Entry point routing** (start_agent → specific topics)

---

## Topic Delegation vs Transition

There are TWO ways to reference other topics:

### 1. `@utils.transition to @topic.[name]` - Permanent Transition

**Behavior:**
- Permanently moves to the target topic
- User CANNOT automatically return
- Current topic is abandoned
- Target topic becomes the active context

**Use Cases:**
- Main menu routing (start_agent → feature topics)
- Mode switches (FAQ → Support)
- One-way workflows

```agentscript
# Permanent transition
actions:
   go_to_orders: @utils.transition to @topic.order_management
```

### 2. `@topic.[name]` - Topic Delegation (Sub-Agent Pattern)

**Behavior:**
- Temporarily delegates to target topic
- Target topic can "return" control to caller
- Original topic resumes after delegation completes
- Like calling a subroutine

**Use Cases:**
- Specialist consultation (Main Agent → Tax Expert → Main Agent)
- Reusable sub-workflows (Address Collection)
- Modular agent design

```agentscript
# Topic delegation (can return)
actions:
   consult_specialist: @topic.tax_specialist
```

**Example: Bidirectional Routing**

```agentscript
topic main_agent:
   label: "Main Agent"
   description: "General assistant"

   reasoning:
      instructions: ->
         | I can help with general questions.
         | For tax questions, I'll consult our tax specialist.
      actions:
         consult_tax: @topic.tax_specialist   # Delegation - can return

topic tax_specialist:
   label: "Tax Specialist"
   description: "Tax expert sub-agent"

   reasoning:
      instructions: ->
         | Provide tax advice.
         | When done, return control to main agent.
      actions:
         back_to_main: @utils.transition to @topic.main_agent  # Return
```

**Key Difference:**

| Pattern | Control Flow | Returns? |
|---------|--------------|----------|
| `@utils.transition to @topic.x` | Permanent move | No |
| `@topic.x` | Temporary delegation | Yes (if target topic transitions back) |

---

## Routing Patterns

### Pattern 1: Hub-and-Spoke (Recommended)

```agentscript
start_agent topic_selector:
   label: "Topic Selector"
   description: "Main menu / router"

   reasoning:
      instructions: ->
         | What can I help you with?
      actions:
         go_orders: @utils.transition to @topic.order_management
         go_support: @utils.transition to @topic.support
         go_faq: @utils.transition to @topic.faq

topic order_management:
   label: "Order Management"
   description: "Order lookup and tracking"

   reasoning:
      instructions: ->
         | Help with orders.
      actions:
         back: @utils.transition to @topic.topic_selector

topic support:
   label: "Support"
   description: "Customer support"

   reasoning:
      instructions: ->
         | Provide support.
      actions:
         back: @utils.transition to @topic.topic_selector
```

**Benefits:**
- Clear entry point
- Easy to add new topics
- Users can always "go back to menu"

### Pattern 2: Linear Workflow

```agentscript
start_agent onboarding:
   label: "Onboarding"
   description: "Collect user information"

   reasoning:
      instructions: ->
         | Welcome! Let's get started.
      actions:
         next: @utils.transition to @topic.collect_address

topic collect_address:
   label: "Collect Address"
   description: "Get shipping address"

   reasoning:
      instructions: ->
         | What's your address?
      actions:
         next: @utils.transition to @topic.confirm_details

topic confirm_details:
   label: "Confirm Details"
   description: "Review and confirm"

   reasoning:
      instructions: ->
         | Please confirm your information.
```

**Benefits:**
- Guided, step-by-step experience
- Prevents users from skipping steps
- Good for onboarding or multi-step processes

### Pattern 3: Contextual Routing

```agentscript
topic order_lookup:
   label: "Order Lookup"
   description: "Look up order by number"

   reasoning:
      instructions: ->
         | if @variables.order_found == False:
         |    | I couldn't find that order.
      actions:
         lookup: @actions.get_order
         # Conditional routing based on outcome
         go_support: @utils.transition to @topic.support
            available when @variables.order_found == False
         back: @utils.transition to @topic.topic_selector
            available when @variables.order_found == True
```

**Benefits:**
- Dynamic routing based on data
- Handles error cases gracefully
- Provides context-aware navigation

---

## Multi-Topic Agents

### When to Use Multiple Topics

| Scenario | Topics Needed |
|----------|---------------|
| **Multi-feature agent** | 1 topic per feature + 1 router topic |
| **Workflow with steps** | 1 topic per step + 1 entry topic |
| **Persona switching** | 1 topic per persona + 1 selector |
| **Specialist delegation** | 1 main topic + N specialist topics |

### Example: Multi-Feature Agent

```agentscript
system:
   instructions: "You are a customer service agent for an e-commerce store."

config:
   agent_name: "Customer_Service_Agent"
   agent_label: "Customer Service"
   description: "Handles orders, returns, and support"

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
   order_number: mutable string
      description: "Current order number"
   return_requested: mutable boolean
      description: "Whether user wants to return an order"

language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False

start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes customers to the right feature"

   reasoning:
      instructions: ->
         | Hello! I can help you with:
         | - Order status and tracking
         | - Returns and refunds
         | - General support questions
         |
         | What do you need help with?
      actions:
         go_orders: @utils.transition to @topic.order_management
         go_returns: @utils.transition to @topic.returns_processing
         go_support: @utils.transition to @topic.general_support

topic order_management:
   label: "Order Management"
   description: "Order lookup, tracking, and status updates"

   actions:
      get_order:
         description: "Retrieves order details by order number"
         inputs:
            inp_OrderNumber: string
               description: "Order number"
         outputs:
            out_OrderStatus: string
               description: "Current order status"
         target: "flow://Get_Order_Details"

   reasoning:
      instructions: ->
         | I can help you check your order status.
         | What's your order number?
      actions:
         lookup: @actions.get_order
         back: @utils.transition to @topic.topic_selector

topic returns_processing:
   label: "Returns Processing"
   description: "Handles return requests and refunds"

   actions:
      create_return:
         description: "Creates a return request"
         inputs:
            inp_OrderNumber: string
               description: "Order number to return"
         outputs:
            out_ReturnNumber: string
               description: "Return authorization number"
         target: "flow://Create_Return_Request"

   reasoning:
      instructions: ->
         | I can help you return your order.
         | What's your order number?
      actions:
         process_return: @actions.create_return
         back: @utils.transition to @topic.topic_selector

topic general_support:
   label: "General Support"
   description: "Answers general questions and provides support"

   reasoning:
      instructions: ->
         | I'm here to help with any questions.
         | What can I answer for you?
      actions:
         back: @utils.transition to @topic.topic_selector
         escalate: @utils.escalate
            description: "Transfer to human agent if needed"
```

---

## Bidirectional Routing

**Pattern: Specialist Consultation**

```agentscript
topic main_agent:
   label: "Main Agent"
   description: "General assistant that can consult specialists"

   reasoning:
      instructions: ->
         | I can help with most questions.
         | For specialized topics, I'll consult our experts.
      actions:
         # Delegation - specialist can return control
         consult_tax: @topic.tax_specialist
         consult_legal: @topic.legal_specialist

topic tax_specialist:
   label: "Tax Specialist"
   description: "Expert on tax questions"

   reasoning:
      instructions: ->
         | [Tax Specialist Mode]
         | Provide detailed tax guidance.
      actions:
         # Return to main agent when done
         return_to_main: @utils.transition to @topic.main_agent

topic legal_specialist:
   label: "Legal Specialist"
   description: "Expert on legal questions"

   reasoning:
      instructions: ->
         | [Legal Specialist Mode]
         | Provide legal information.
      actions:
         return_to_main: @utils.transition to @topic.main_agent
```

**Benefits:**
- Main agent stays in control
- Specialists provide focused expertise
- Clean separation of concerns
- Reusable specialist topics

---

## Best Practices

### Topic Design Principles

1. **Single Responsibility**: Each topic should have ONE clear purpose
2. **Clear Labels**: Use descriptive labels that users understand
3. **Comprehensive Descriptions**: LLM uses description for routing - make it detailed
4. **Provide Exit Routes**: Always give users a way to go back or exit
5. **Avoid Orphaned Topics**: Every topic should be reachable from start_agent

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Topic name | snake_case | `order_management` |
| Topic label | Title Case | "Order Management" |
| Action name | snake_case | `get_order_status` |

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `label` or `description` | Add both to every topic |
| Orphaned topics (unreachable) | Ensure all topics have incoming transitions |
| No way to go back | Add transition to topic_selector or escalation |
| Too many topics | Combine related functionality |
| Too few topics | Split complex topics into focused ones |

### Topic Transitions Checklist

- [ ] `start_agent` transitions to at least one topic
- [ ] All topics are reachable from `start_agent` (directly or indirectly)
- [ ] Each topic has at least one outbound transition (or escalation)
- [ ] Users can navigate back to main menu or exit
- [ ] Topic descriptions are clear and detailed for LLM routing

---

## References

For additional information, see:
- [agent-script-reference.md](agent-script-reference.md) - Full Agent Script syntax
- [../docs/patterns-and-practices.md](../docs/patterns-and-practices.md) - Pattern decision tree
- [../templates/patterns/bidirectional-routing.agent](../templates/patterns/bidirectional-routing.agent) - Bidirectional routing example
