# Agent Script Actions - Complete Reference

> **Quick Navigation**: Comprehensive action configuration patterns for Agent Script development

---

## 📚 Reference Files

### Core Configuration

**[actions-definitions.md](actions-definitions.md)** - Action structure fundamentals

- Basic action syntax (description, inputs, outputs, target)
- Target protocols (flow://, apex://, generatePromptResponse://)
- Output flags (is_displayable, is_used_by_planner)
- Complete working examples

**When to use**: Starting a new action, understanding action structure

---

**[actions-callbacks.md](actions-callbacks.md)** - Chaining actions with `run`

- Sequential action execution patterns
- Output capture and variable passing
- Callback limitations (no nesting)
- Payment processing example

**When to use**: Need to chain multiple actions, passing data between them

---

**[actions-input-bindings.md](actions-input-bindings.md)** - Parameter binding patterns

- LLM slot-filling with `...`
- Variable binding with `@variables.X`
- Fixed values
- Mixed binding strategies

**When to use**: Configuring action inputs, deciding how to populate parameters

---

### Advanced Patterns

**[actions-descriptions.md](actions-descriptions.md)** - Context-aware action descriptions

- Overriding descriptions per topic
- User expertise level adaptation
- Conditional action availability
- Improving LLM action selection

**When to use**: Same action needs different descriptions in different contexts

---

**[actions-instruction-refs.md](actions-instruction-refs.md)** - Guiding LLM action selection

- Using `{!@actions.action_name}` in instructions
- Conditional instruction patterns
- Improving action selection accuracy
- Business hours routing example

**When to use**: Need to guide LLM toward specific actions in certain situations

---

**[actions-prompt-templates.md](actions-prompt-templates.md)** - Prompt template integration

- Target syntax: `generatePromptResponse://TemplateName`
- Input binding with `"Input:fieldName"`
- Grounded data integration
- Complete examples

**When to use**: Invoking Salesforce Prompt Templates from Agent Script

---

### Troubleshooting

**[actions-troubleshooting.md](actions-troubleshooting.md)** - Common errors & fixes

- Syntax error checklist
- Indentation issues
- Input/output errors
- Target format mistakes
- Best practices summary

**When to use**: Debugging action syntax errors, linting failures

---

## 🎯 Quick Decision Tree

```
Need to create an action?
├─ Start here: actions-definitions.md
│
Need to chain multiple actions?
├─ Go to: actions-callbacks.md
│
Having input parameter issues?
├─ Go to: actions-input-bindings.md
│
Action description not clear to LLM?
├─ Go to: actions-descriptions.md OR actions-instruction-refs.md
│
Using Prompt Templates?
├─ Go to: actions-prompt-templates.md
│
Getting syntax errors?
└─ Go to: actions-troubleshooting.md
```

---

## 📖 Related Resources

- [syntax-reference.md](syntax-reference.md) - Complete Agent Script syntax
- [instruction-resolution.md](instruction-resolution.md) - Three-phase execution model
- [debugging-guide.md](debugging-guide.md) - Trace analysis & debugging

---

## 🔗 Official Sources

These resources consolidate patterns from:

- [Agent Script Recipes - Action Configuration](https://developer.salesforce.com/sample-apps/agent-script-recipes/action-configuration)
- [Salesforce Agent Script Documentation](https://developer.salesforce.com/docs/einstein/genai/guide/agent-script.html)
- [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes)

---

*Last updated: 2025-02-06*
