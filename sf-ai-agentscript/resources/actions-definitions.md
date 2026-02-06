# Action Definitions

> Core structure for defining actions in Agent Script

**Navigation**: [← Back to Index](actions-INDEX.md)

---

## Overview

Action definitions comprise four essential components:

1. **Description** - Explains the action's purpose to the LLM
2. **Inputs** - Specifies required parameters with types
3. **Outputs** - Describes returned data structures
4. **Target** - Indicates where execution occurs

---

## Basic Syntax

```agentscript
actions:
  action_name:
    description: "Clear, user-focused explanation of what this action does"
    inputs:
      parameter_name: type
        description: "What this parameter represents"
        is_required: True
    outputs:
      output_field: type
        description: "What this output contains"
        is_used_by_planner: True
        is_displayable: True
    target: "flow://FlowName" or "apex://ClassName"
```

---

## Complete Example

```agentscript
actions:
  Get_Weather:
    description: "Retrieves current weather conditions for a specified location"
    inputs:
      location: string
        description: "City name or ZIP code"
        is_required: True
      units: string
        description: "Temperature units (fahrenheit or celsius)"
        is_required: False
    outputs:
      temperature: number
        description: "Current temperature in specified units"
        is_used_by_planner: True
        is_displayable: True
      conditions: string
        description: "Weather conditions description"
        is_displayable: True
    target: "flow://GetCurrentWeather"
```

---

## Target Types

### Salesforce Flow Integration

```agentscript
target: "flow://FlowAPIName"
```

### Apex Class Integration

```agentscript
target: "apex://ClassName"
```

### Prompt Template Integration

```agentscript
target: "generatePromptResponse://TemplateName"
```

**See also**: [actions-prompt-templates.md](actions-prompt-templates.md) for prompt template details

---

## Output Configuration Flags

### is_displayable

Controls whether the LLM can show this value to users:

- `is_displayable: True` - LLM can include in responses
- `is_displayable: False` - Hidden from LLM (prevents hallucination)

### is_used_by_planner

Controls whether the LLM can use this for decision-making:

- `is_used_by_planner: True` - LLM can reason about this value
- `is_used_by_planner: False` - LLM cannot see or use

### Zero-Hallucination Pattern

Use flags together to enable deterministic routing:

```agentscript
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

---

## Input Configuration

### is_required Flag

Specifies whether a parameter must be provided:

```agentscript
inputs:
  email: string
    description: "Customer email address"
    is_required: True
  phone: string
    description: "Optional phone number"
    is_required: False
```

---

## Action Invocation

Once defined in Agentforce Assets, actions are invoked in Agent Script:

```agentscript
topic weather_check:
  reasoning:
    actions:
      check_weather: @actions.Get_Weather
        with location=...
             units="fahrenheit"
        set @variables.temp = @outputs.temperature
```

**See also**: [actions-input-bindings.md](actions-input-bindings.md) for input binding patterns

---

## Best Practices

### ✅ DO

- Write clear, user-focused descriptions
- Keep input parameters minimal
- Use descriptive parameter names
- Mark outputs as `is_displayable: True` when user-facing
- Mark outputs as `is_used_by_planner: True` when needed for decision-making
- Use proper type annotations

### ❌ DON'T

- Use vague descriptions like "Does a search"
- Include technical jargon unnecessarily
- Create excessive input parameters
- Forget to specify `is_required` for inputs
- Leave output flags unspecified

---

## Common Types

### Supported Input/Output Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text values | "customer@example.com" |
| `number` | Numeric values | 42, 3.14 |
| `boolean` | True/False | True |
| `date` | Date values | 2025-02-06 |
| `currency` | Monetary values | 199.99 |
| `id` | Salesforce IDs | 001xx000003DGb2AAG |
| `list[T]` | Collections | ["item1", "item2"] |
| `object` | Structured data | Complex structures |

**Note**: Some types are valid only for actions, not Agent Script variables. See SKILL.md for complete type matrix.

---

## Related Topics

- **Next**: [actions-callbacks.md](actions-callbacks.md) - Chain actions together
- **Next**: [actions-input-bindings.md](actions-input-bindings.md) - Configure inputs
- **Troubleshooting**: [actions-troubleshooting.md](actions-troubleshooting.md) - Fix common errors

---

*Part of the [Agent Script Actions Reference](actions-INDEX.md)*
