# Actions Troubleshooting

> Common syntax errors, fixes, and best practices for Agent Script actions

**Navigation**: [← Back to Index](actions-INDEX.md)

---

## Quick Error Reference

| Error Pattern | Section |
|---------------|---------|
| Missing colon, indentation | [Syntax Errors](#syntax-errors) |
| Input/output format | [Input/Output Errors](#inputoutput-errors) |
| Target format | [Target Errors](#target-errors) |
| Callback issues | [Callback Errors](#callback-errors) |
| Binding problems | [Input Binding Errors](#input-binding-errors) |

---

## Syntax Errors

### Missing Colon After Action Name

```agentscript
# ❌ WRONG
actions:
  my_action  # ERROR: Missing colon
    description: "..."

# ✅ CORRECT
actions:
  my_action:
    description: "..."
```

### Inconsistent Indentation

```agentscript
# ❌ WRONG
actions:
  my_action:
    description: "..."
      inputs:  # ERROR: Wrong indentation level

# ✅ CORRECT (2-space indentation)
actions:
  my_action:
    description: "..."
    inputs:
```

**Rule**: Use consistent 2-space indentation throughout. Never mix tabs and spaces.

---

## Input/Output Errors

### Missing Type Annotation

```agentscript
# ❌ WRONG
inputs:
  email:  # ERROR: Missing type
    description: "User email"

# ✅ CORRECT
inputs:
  email: string
    description: "User email"
```

### Incorrect Input/Output Block Location

```agentscript
# ❌ WRONG - inputs:/outputs: in reasoning.actions
topic main:
  reasoning:
    actions:
      search_kb: @actions.search
        inputs:  # ERROR: Not valid in Agent Script
          query: string

# ✅ CORRECT - Define in Agentforce Assets, invoke in Agent Script
# In Agentforce Assets:
actions:
  search:
    inputs:
      query: string
        description: "Search query"

# In Agent Script:
topic main:
  reasoning:
    actions:
      search_kb: @actions.search
        with query=...  # ✅ Use 'with' to bind inputs
```

**Rule**: Define `inputs:` and `outputs:` in Agentforce Assets only, not in Agent Script `reasoning.actions`.

---

## Target Errors

### Missing Protocol

```agentscript
# ❌ WRONG
target: FlowName  # ERROR: Missing protocol

# ✅ CORRECT
target: "flow://FlowName"
```

### Invalid Protocol

```agentscript
# ❌ WRONG
target: "flows://MyFlow"  # ERROR: Wrong protocol

# ✅ CORRECT
target: "flow://MyFlow"
```

### Common Valid Protocols

- `flow://` - Salesforce Flow
- `apex://` - Apex class
- `generatePromptResponse://` - Prompt template
- `api://` - REST API
- `retriever://` - Knowledge retriever

**See also**: SKILL.md for complete protocol list.

---

## Callback Errors

### Nested Callbacks (Not Allowed)

```agentscript
# ❌ WRONG - Nested callbacks
action1: @actions.first
  run @actions.second
    run @actions.third  # ERROR: Nested callbacks not allowed

# ✅ CORRECT - Flatten callbacks
action1: @actions.first
  run @actions.second
  run @actions.third
```

**Rule**: Only one level of callbacks permitted. Use sequential `run` statements.

### Callbacks on @utils.* (Not Supported)

```agentscript
# ❌ WRONG
go_next: @utils.transition to @topic.main
  set @variables.visited = True   # ERROR: @utils doesn't support set/run/if

# ✅ CORRECT - Only @actions.* supports post-action directives
process: @actions.process_order
  with order_id=@variables.order_id
  set @variables.status = @outputs.status        # ✅ Works
  run @actions.send_notification                 # ✅ Works
```

**Rule**: Post-action directives (`set`, `run`, `if`) only work on `@actions.*`.

**See also**: [actions-callbacks.md](actions-callbacks.md) for correct callback patterns.

---

## Input Binding Errors

### Missing Equals Sign

```agentscript
# ❌ WRONG
with email @variables.user_email  # ERROR: Missing =

# ✅ CORRECT
with email=@variables.user_email
```

### Incorrect Prompt Template Syntax

```agentscript
# ❌ WRONG
with Input:email=...  # ERROR: Missing quotes

# ✅ CORRECT
with "Input:email"=...
```

**Rule**: Prompt template inputs must be quoted: `"Input:fieldName"`

**See also**: [actions-prompt-templates.md](actions-prompt-templates.md) for prompt template patterns.

### Using `...` as Default Value

```agentscript
# ❌ WRONG - Using ... as variable default
variables:
  order_id: mutable string = ...  # ERROR: Not valid here

# ✅ CORRECT - Use ... only in action parameter binding
reasoning:
  actions:
    search: @actions.search_products
      with query=...           # ✅ LLM extracts from conversation
```

**Rule**: `...` is for LLM slot-filling in action inputs only.

**See also**: [actions-input-bindings.md](actions-input-bindings.md) for binding patterns.

---

## Description Errors

### Vague or Unhelpful Descriptions

```agentscript
# ❌ WRONG
description: "Does a search"

# ✅ CORRECT
description: "Searches the knowledge base for articles matching the query and returns the top 5 most relevant results"
```

**Rule**: Be specific about what the action does, what inputs it needs, and what it returns.

---

## Common Validation Errors

### Missing is_required

```agentscript
# ⚠️ INCOMPLETE
inputs:
  email: string
    description: "User email"
    # Missing is_required flag

# ✅ COMPLETE
inputs:
  email: string
    description: "User email"
    is_required: True
```

### Missing Output Flags

```agentscript
# ⚠️ INCOMPLETE
outputs:
  result: string  # Missing is_displayable and is_used_by_planner

# ✅ COMPLETE
outputs:
  result: string
    description: "The formatted result to show the user"
    is_used_by_planner: True
    is_displayable: True
```

---

## Best Practices Summary

### Action Naming

```agentscript
# ✅ Good names (descriptive, action-oriented)
Search_Knowledge_Base
Create_Support_Case
Generate_Report

# ❌ Bad names (vague, unclear)
do_something
action1
helper
```

### Description Quality

```agentscript
# ✅ Clear and specific
description: "Searches the knowledge base for articles matching the query and returns the top 5 most relevant results"

# ❌ Vague
description: "Does a search"
```

### Input Parameter Design

```agentscript
# ✅ Minimal, focused parameters
inputs:
  query: string
  max_results: number

# ❌ Excessive parameters (too many options)
inputs:
  query: string
  max_results: number
  sort_order: string
  include_archived: boolean
  filter_by_date: string
  filter_by_author: string
  # ... too many options
```

### Output Configuration

```agentscript
# ✅ Properly configured
outputs:
  result_text: string
    description: "The formatted result to show the user"
    is_used_by_planner: True
    is_displayable: True

# ❌ Missing configuration
outputs:
  result: string  # Missing flags
```

### Variable Management

```agentscript
# ✅ Clear variable naming
set @variables.customer_email = @outputs.email
set @variables.case_number = @outputs.case_id

# ❌ Unclear variable names
set @variables.temp = @outputs.data
set @variables.x = @outputs.id
```

---

## Testing Checklist

Validate your actions by checking:

- [ ] **Syntax validation** - Use Agent Script CLI linter
- [ ] **Input binding** - Ensure all required inputs can be satisfied
- [ ] **Output usage** - Verify outputs are captured and used correctly
- [ ] **Callback chains** - Test sequential action execution
- [ ] **Error handling** - Confirm graceful failure behavior
- [ ] **Description clarity** - LLM understands when to use action
- [ ] **Type correctness** - All types match expected values

---

## Quick Reference: Action Structure

```agentscript
# Complete action structure template
actions:
  Action_Name:
    description: "Clear, concise explanation of what this action does"
    inputs:
      parameter_name: type
        description: "Parameter description"
        is_required: True
    outputs:
      output_field: type
        description: "Output description"
        is_used_by_planner: True
        is_displayable: True
    target: "protocol://TargetName"

# Action invocation template
perform_action: @actions.Action_Name
  with parameter_name=...
  set @variables.result = @outputs.output_field
  run @actions.Next_Action
    with input=@variables.result
```

---

## Related Topics

- **Action Structure**: [actions-definitions.md](actions-definitions.md)
- **Chaining**: [actions-callbacks.md](actions-callbacks.md)
- **Input Binding**: [actions-input-bindings.md](actions-input-bindings.md)
- **Descriptions**: [actions-descriptions.md](actions-descriptions.md)
- **Prompt Templates**: [actions-prompt-templates.md](actions-prompt-templates.md)

---

## Additional Help

If you're still encountering issues:

1. Check SKILL.md for Agent Script-wide patterns
2. Review [syntax-reference.md](syntax-reference.md) for overall syntax
3. Use [debugging-guide.md](debugging-guide.md) for trace analysis
4. Consult [Agent Script Recipes](https://developer.salesforce.com/sample-apps/agent-script-recipes)

---

*Part of the [Agent Script Actions Reference](actions-INDEX.md)*
