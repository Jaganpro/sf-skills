# sf-ai-agentforce

🤖 **Agentforce Agent Creation Skill for Claude Code**

Create Agentforce agents using Agent Script syntax with 100-point validation scoring.

## Features

- ✅ **Agent Script Generation** - Create complete agents using the official Agent Script syntax
- ✅ **100-Point Validation** - Score agents across 6 categories
- ✅ **Templates** - Pre-built patterns for common agent types
- ✅ **Best Practices** - Built-in enforcement of Agentforce patterns
- ✅ **CLI Integration** - Seamless deployment with sf CLI v2

## Requirements

| Requirement | Value |
|-------------|-------|
| API Version | **64.0+** (Summer '25 or later) |
| Licenses | Agentforce (Default), Einstein Prompt Templates |
| sf CLI | v2.x with agent commands |

## Installation

```bash
# Install as part of sf-skills
claude /plugin install github:Jaganpro/sf-skills

# Or install standalone
claude /plugin install github:Jaganpro/sf-skills/sf-ai-agentforce
```

## Quick Start

### 1. Invoke the skill

```
Skill: sf-ai-agentforce
Request: "Create a simple FAQ agent"
```

### 2. Answer the requirements questions

The skill will ask about:
- Agent purpose
- Topics needed
- Actions required
- System persona

### 3. Review and deploy

```bash
# Generate agent version
sf agent generate version --name My_Agent --target-org dev

# Preview
sf agent preview --name My_Agent --target-org dev
```

## Scoring System

| Category | Points | Focus |
|----------|--------|-------|
| Structure & Syntax | 20 | Valid syntax, 4-space indentation |
| Topic Design | 20 | Clear descriptions, proper transitions |
| Action Integration | 20 | Valid targets, input/output mapping |
| Variable Management | 15 | Typed variables, meaningful names |
| Instructions Quality | 15 | Clear reasoning, edge cases |
| Security & Guardrails | 10 | System guardrails, validation |

**Thresholds**: ⭐⭐⭐⭐⭐ 90+ | ⭐⭐⭐⭐ 80-89 | ⭐⭐⭐ 70-79 | Block: <60

## Agent Script Syntax

### Basic Structure

```agentscript
config:
    agent_name: "My_Agent"
    agent_label: "My Agent"
    description: "What this agent does"

system:
    messages:
        welcome: "Hello! How can I help?"
    instructions:
        | You are a helpful assistant.
        | Be concise and accurate.

variables:
    user_input: mutable string = ""
        description: "User's input"

start_agent topic_selector:
    description: "Entry point"
    reasoning:
        instructions:->
            | Route the user appropriately.
        actions:
            go_help: @utils.transition to @topic.help
                description: "Get help"

topic help:
    description: "Provides help"
    reasoning:
        instructions:->
            | Help the user.
```

### Key Rules

| Rule | Details |
|------|---------|
| Indentation | **4 spaces** (not tabs, not 3 spaces) |
| Variables | `@variables.name` (plural!) |
| Booleans | `True` / `False` (capitalized) |
| Templates | `{!@variables.name}` in instructions |

## Templates

| Template | Use Case |
|----------|----------|
| `simple-qa.agentscript` | Single topic FAQ agent |
| `multi-topic.agentscript` | Multiple conversation modes |
| `topic-with-actions.agentscript` | External integrations |
| `error-handling.agentscript` | Validation patterns |

## Documentation

- [Best Practices](docs/best-practices.md)
- [Agent Script Syntax](docs/agent-script-syntax.md)
- [Simple FAQ Example](examples/simple-faq-agent/)

## Official Resources

- [Agent Script (Beta) Guide](https://developer.salesforce.com/docs/einstein/genai/guide/agent-script.html)
- [Agent Script Recipes](https://developer.salesforce.com/sample-apps/agent-script-recipes/getting-started/overview)
- [Agentforce DX](https://developer.salesforce.com/docs/einstein/genai/guide/agent-dx.html)

## License

MIT License - See [LICENSE](LICENSE)
