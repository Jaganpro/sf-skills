# Action Description Overrides

> Context-specific action descriptions to improve LLM action selection

**Navigation**: [← Back to Index](actions-INDEX.md)

---

## Overview

Action Description Overrides allow developers to customize how actions are presented to the LLM based on context, user expertise, and conversation state. This improves tool selection accuracy by providing relevant descriptions for different scenarios.

---

## Core Concept

The same underlying action can have different descriptions across various topics to match user skill levels or situational requirements.

**Key insight**: Master context-specific action descriptions to improve LLM action selection.

---

## Basic Pattern

### Same Action, Different Contexts

```agentscript
topic beginner_mode:
  actions:
    search_action:
      description: "Search the knowledge base for helpful articles"
      inputs:
        query: string
          description: "What you want to find"
      target: "flow://SearchKB"

topic advanced_mode:
  actions:
    search_action:
      description: "Execute knowledge base query with advanced filters (type, date range, tags). Returns paginated results with relevance scoring."
      inputs:
        query: string
          description: "Lucene-style search query with operators"
      target: "flow://SearchKB"
```

**Result**: Beginner users see simple language, advanced users see technical details.

---

## Context-Aware Availability

Combine description overrides with conditional availability:

```agentscript
topic account_search:
  actions:
    find_account: @actions.search_records
      available when @variables.search_context == "accounts"
      description: "Find customer accounts by name, ID, or other criteria"

topic contact_search:
  actions:
    find_contact: @actions.search_records
      available when @variables.search_context == "contacts"
      description: "Find contact records by name, email, or phone"
```

**Result**: Same base action, different descriptions and availability based on context.

---

## User Expertise Adaptation

### Beginner Mode Example

```agentscript
topic beginner_help:
  description: "Simplified interface for new users"
  reasoning:
    actions:
      search_help: @actions.search_knowledge_base
        description: "Search for help articles"
        # Simple, outcome-focused description
```

### Advanced Mode Example

```agentscript
topic advanced_help:
  description: "Power user interface with advanced features"
  reasoning:
    actions:
      search_help: @actions.search_knowledge_base
        description: "Execute knowledge base query with advanced filters (type, date range, tags). Returns paginated results with relevance scoring. Supports Boolean operators and wildcards."
        # Technical, capability-focused description
```

---

## Situational Descriptions

### Example: Time-Based Context

```agentscript
topic business_hours:
  reasoning:
    actions:
      create_case: @actions.create_support_case
        available when @variables.during_business_hours == True
        description: "Create a support case for immediate assignment to available agents"

topic after_hours:
  reasoning:
    actions:
      create_case: @actions.create_support_case
        available when @variables.during_business_hours == False
        description: "Create a support case for next-business-day follow-up"
```

---

## Multi-Context Example

Complete scenario showing expertise and context adaptation:

```agentscript
variables:
  user_experience_level: mutable string = "beginner"
  search_context: mutable string = "general"

topic search_general_beginner:
  description: "General search for beginners"
  reasoning:
    actions:
      search: @actions.universal_search
        available when @variables.user_experience_level == "beginner" and @variables.search_context == "general"
        description: "Search for information"

topic search_general_advanced:
  description: "General search for advanced users"
  reasoning:
    actions:
      search: @actions.universal_search
        available when @variables.user_experience_level == "advanced" and @variables.search_context == "general"
        description: "Execute search query with filters, sorting, and pagination. Supports regex and Boolean operators."

topic search_accounts_advanced:
  description: "Account search for advanced users"
  reasoning:
    actions:
      search: @actions.universal_search
        available when @variables.user_experience_level == "advanced" and @variables.search_context == "accounts"
        description: "Execute SOQL-powered account search with field-level filters, related object traversal, and custom sort orders."
```

---

## How It Works

When you provide a description override:

- The system embeds a reference to the **full action definition**
- The LLM receives the **contextual description** plus complete action metadata
- Action selection accuracy improves because the description matches the situation

---

## Use Cases

### ✅ When to Use Description Overrides

- Multiple actions could apply, but one is contextually preferred
- User expertise levels vary (beginner vs advanced)
- Business context changes behavior (hours, location, account type)
- Same action serves different purposes in different topics
- Action name alone doesn't convey when it should be used

### ❌ When NOT to Use

- Action is always used the same way
- Description would be identical across all contexts
- Over-engineering simple scenarios

---

## Best Practices

### ✅ DO

- Tailor descriptions to user expertise levels
- Be specific about capabilities and parameters
- Customize descriptions when context matters significantly
- Use clear, appropriate language for each audience
- Combine with `available when` for stronger control

### ❌ DON'T

- Use generic descriptions across different modes
- Include vague explanations that confuse the LLM
- Over-complicate beginner descriptions
- Forget to test description effectiveness
- Create too many context variations (maintain simplicity)

---

## Testing Description Overrides

### Validation Checklist

- [ ] Each description accurately reflects the action's purpose in context
- [ ] Descriptions are distinct enough for the LLM to differentiate
- [ ] Language level matches target user expertise
- [ ] Contextual clues help LLM select correct action
- [ ] `available when` conditions properly restrict visibility

---

## Related Topics

- **Alternative approach**: [actions-instruction-refs.md](actions-instruction-refs.md) - Guide LLM with instruction references
- **Prerequisites**: [actions-definitions.md](actions-definitions.md) - Base action definitions
- **Troubleshooting**: [actions-troubleshooting.md](actions-troubleshooting.md) - Fix description issues

---

*Part of the [Agent Script Actions Reference](actions-INDEX.md)*
