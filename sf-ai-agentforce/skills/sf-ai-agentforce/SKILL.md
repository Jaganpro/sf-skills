---
name: sf-ai-agentforce
description: Creates Agentforce agents using Agent Script syntax. Generates complete agents with topics, actions, and variables. 100-point scoring across 6 categories. API v64+ required.
---

# sf-ai-agentforce: Agentforce Agent Creation with Agent Script

Expert Agentforce developer specializing in Agent Script syntax, topic design, and action integration. Generate production-ready agents that leverage LLM reasoning with deterministic business logic.

## Core Responsibilities

1. **Agent Creation**: Generate complete Agentforce agents using Agent Script
2. **Topic Management**: Create and configure agent topics with proper transitions
3. **Action Integration**: Connect actions to Flows, Apex, or external services
4. **Validation & Scoring**: Score agents against best practices (0-100 points)
5. **Deployment Integration**: Deploy via sf-deploy skill

## ⚠️ CRITICAL: API Version Requirement

**Agent Script requires API v64+ (Summer '25 or later)**

Before creating agents, verify:
```bash
sf org display --target-org [alias] --json | jq '.result.apiVersion'
```

If API version < 64, Agent Script features won't be available.

---

## ⚠️ CRITICAL: Indentation Rules

**Agent Script uses 4-SPACE indentation (NOT tabs, NOT 3 spaces)**

```agentscript
# ✅ CORRECT - 4 spaces
config:
    agent_name: "My_Agent"
    description: "My agent description"

# ❌ WRONG - 3 spaces (common mistake!)
config:
   agent_name: "My_Agent"
```

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- **Agent purpose**: What job should this agent do?
- **Topics needed**: What categories of actions? (e.g., FAQ, Order Management, Support)
- **Actions required**: Flow-based? Apex-based? External API?
- **Variables**: What state needs to be tracked?
- **System persona**: What tone/behavior should the agent have?

**Then**:
1. Check existing agents: `Glob: **/aiAuthoringBundles/**/*.agentscript`
2. Check for sfdx-project.json to confirm Salesforce project structure
3. Create TodoWrite tasks

### Phase 2: Template Selection / Design

**Select appropriate pattern** based on requirements:

| Pattern | Use When | Template |
|---------|----------|----------|
| Simple Q&A | Single topic, no actions | `templates/agent/simple-qa.agentscript` |
| Multi-Topic | Multiple conversation modes | `templates/topics/multi-topic.agentscript` |
| Action-Based | External integrations needed | `templates/actions/flow-action.agentscript` |
| Error Handling | Critical operations | `templates/topics/error-handling.agentscript` |

Load via: `Read: ../../templates/[path]` (relative to SKILL.md location)

### Phase 3: Generation / Validation

**Create Agent Script file** at:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agentscript
```

**Required blocks**:
1. `config:` - Agent metadata (name, label, description)
2. `system:` - Global instructions and messages
3. `start_agent topic_selector:` - Entry point topic
4. `topic [name]:` - At least one additional topic

**Validation Report Format** (6-Category Scoring 0-100):
```
Score: 85/100 ⭐⭐⭐⭐ Very Good
├─ Structure & Syntax:     18/20 (90%)
├─ Topic Design:           16/20 (80%)
├─ Action Integration:     18/20 (90%)
├─ Variable Management:    13/15 (87%)
├─ Instructions Quality:   12/15 (80%)
└─ Security & Guardrails:   8/10 (80%)

Issues:
⚠️ [Syntax] Line 15: Use 4-space indentation, found 3 spaces
⚠️ [Topic] Missing description for topic 'checkout'
✓ All topic references valid
✓ All variable references valid
```

### Phase 4: Deployment

**Step 1: Commit to Org**
```bash
sf agent generate version --name [AgentName] --target-org [alias]
```

**Step 2: Activate Version** (optional)
```bash
sf agent activate version --name [AgentName] --version-number [N] --target-org [alias]
```

**Step 3: Preview Agent**
```bash
sf agent preview --name [AgentName] --target-org [alias]
```

### Phase 5: Verification

```
✓ Agent Complete: [AgentName]
  Type: Agentforce Agent | API: 64.0
  Location: force-app/main/default/aiAuthoringBundles/[AgentName]/
  Validation: PASSED (Score: XX/100)
  Topics: [N] | Actions: [M] | Variables: [P]

Next Steps:
  1. Preview in org: sf agent preview --name [AgentName]
  2. Test in Agentforce Testing Center
  3. Activate when ready: sf agent activate version
```

---

## Agent Script Syntax Reference

### Block Structure

```agentscript
# Comments start with #

config:
    agent_name: "Agent_API_Name"
    agent_label: "Human Readable Name"
    description: "What this agent does"

system:
    messages:
        welcome: "Hello! How can I help?"
        error: "Sorry, something went wrong."
    instructions:
        | You are a helpful assistant.
        | Be concise and accurate.

variables:
    var_name: mutable string = ""
        description: "What this variable stores"

start_agent topic_selector:
    description: "Entry point - routes to topics"
    reasoning:
        instructions:->
            | Determine what the user needs.
        actions:
            go_to_help: @utils.transition to @topic.help
                description: "Get help"

topic help:
    description: "Provides help to users"
    reasoning:
        instructions:->
            | Answer the user's question helpfully.
```

### Resource Access (@ prefix)

| Resource | Syntax | Example |
|----------|--------|---------|
| Variables | `@variables.name` | `@variables.user_name` |
| Actions | `@actions.name` | `@actions.get_weather` |
| Topics | `@topic.name` | `@topic.checkout` |
| Outputs | `@outputs.field` | `@outputs.temperature` |
| Utilities | `@utils.transition` | `@utils.transition to @topic.X` |

### Variable Types

```agentscript
variables:
    # String (text)
    name: mutable string = ""
        description: "User's name"

    # Number (integer or decimal)
    age: mutable number = 0
        description: "User's age"

    # Boolean (True/False - capitalized!)
    confirmed: mutable boolean = False
        description: "User confirmed action"
```

### Action Definitions

```agentscript
# Flow-based action
get_account:
    description: "Retrieves account information"
    inputs:
        account_id: string
            description: "Salesforce Account ID"
    outputs:
        account_name: string
            description: "Account name"
        industry: string
            description: "Account industry"
    target: "flow://Get_Account_Info"

# Apex-based action
create_case:
    description: "Creates a support case"
    inputs:
        subject: string
            description: "Case subject"
        description: string
            description: "Case description"
    outputs:
        case_id: string
            description: "Created case ID"
    target: "apex://CaseService.createCase"
```

### Action Invocation

```agentscript
reasoning:
    actions:
        # LLM fills inputs (...)
        lookup: @actions.get_account
            with account_id=...
            set @variables.account_name = @outputs.account_name

        # Fixed value
        default_lookup: @actions.get_account
            with account_id="001XX000003NGFQ"

        # Variable binding
        bound_lookup: @actions.get_account
            with account_id=@variables.current_account_id
```

### Action Callbacks (Chaining)

```agentscript
process_order: @actions.create_order
    with items=...
    set @variables.order_id = @outputs.order_id
    run @actions.send_confirmation
        with order_id=@variables.order_id
    run @actions.update_inventory
        with order_id=@variables.order_id
```

**Note**: Only one level of nesting - cannot nest `run` inside `run`.

### Topic Transitions

```agentscript
# Simple transition
go_checkout: @utils.transition to @topic.checkout
    description: "Proceed to checkout"

# Conditional transition
go_checkout: @utils.transition to @topic.checkout
    description: "Proceed to checkout"
    available when @variables.cart_has_items == True
```

### Conditional Logic

```agentscript
instructions:->
    if @variables.amount > 10000:
        set @variables.needs_approval = True
        | This amount requires manager approval.
    else:
        set @variables.needs_approval = False
        | Processing your request.

    if @variables.user_name is None:
        | I don't have your name yet. What should I call you?
```

### Operators

| Type | Operators |
|------|-----------|
| Comparison | `==`, `!=`, `>`, `<`, `>=`, `<=` |
| Math | `+`, `-` |
| Null check | `is None`, `is not None` |

### Template Expressions

Use `{!...}` for variable interpolation in instructions:

```agentscript
instructions:->
    | Hello {!@variables.user_name}!
    | Your account balance is {!@variables.balance}.
```

---

## Scoring System (100 Points)

### Structure & Syntax (20 points)
- Valid Agent Script syntax (-10 if parsing fails)
- Correct 4-space indentation (-3 per violation)
- Required blocks present (config, system, start_agent) (-5 each missing)
- Valid file location in aiAuthoringBundles (-3 if wrong)

### Topic Design (20 points)
- All topics have descriptions (-3 each missing)
- Logical topic transitions (-3 per orphaned topic)
- Entry point topic exists (start_agent) (-5 if missing)
- Topic names follow snake_case (-2 each violation)

### Action Integration (20 points)
- Valid target format (flow:// or apex://) (-5 each invalid)
- All inputs have descriptions (-2 each missing)
- All outputs captured appropriately (-2 each unused)
- Action callbacks don't exceed one level (-5 if nested)

### Variable Management (15 points)
- All variables have descriptions (-2 each missing)
- Appropriate types used (-2 each mismatch)
- Variables initialized with defaults (-2 each missing)
- Variable names follow snake_case (-1 each violation)

### Instructions Quality (15 points)
- Clear, specific reasoning instructions (-3 if vague)
- Edge cases handled (-3 if missing)
- Appropriate use of conditionals (-2 if logic missing)
- Template expressions valid (-3 each invalid)

### Security & Guardrails (10 points)
- System-level guardrails present (-5 if missing)
- Sensitive operations have validation (-3 if missing)
- Error messages don't expose internals (-2 each violation)

### Scoring Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Deploy with confidence |
| 80-89 | ⭐⭐⭐⭐ Very Good | Minor improvements suggested |
| 70-79 | ⭐⭐⭐ Good | Review before deploy |
| 60-69 | ⭐⭐ Needs Work | Address issues before deploy |
| <60 | ⭐ Critical | **Block deployment** |

---

## Cross-Skill Integration

See [../../shared/docs/cross-skill-integration.md](../../shared/docs/cross-skill-integration.md)

| Direction | Pattern |
|-----------|---------|
| sf-agentforce → sf-apex | Create custom Apex actions for agent |
| sf-agentforce → sf-flow | Create Flow-based actions for agent |
| sf-agentforce → sf-deploy | Deploy agent metadata |
| sf-agentforce → sf-metadata | Query object structure for data actions |

**Example**: Creating an agent with a custom Apex action:
```
Skill(skill="sf-apex")
Request: "Create an Apex class CaseService with method createCase that accepts subject and description, returns case ID"

Skill(skill="sf-agentforce")
Request: "Create an agent that uses apex://CaseService.createCase to handle support requests"
```

---

## Common Patterns

### Pattern 1: Simple FAQ Agent
```agentscript
config:
    agent_name: "FAQ_Agent"
    agent_label: "FAQ Agent"
    description: "Answers frequently asked questions"

system:
    messages:
        welcome: "Hello! I can answer your questions."
        error: "Sorry, I encountered an issue."
    instructions:
        | You are a helpful FAQ assistant.
        | Answer questions concisely.

start_agent topic_selector:
    description: "Routes to FAQ handling"
    reasoning:
        instructions:->
            | Listen to the user's question.
            | Provide a helpful, accurate response.
```

### Pattern 2: Multi-Topic Router
```agentscript
start_agent topic_selector:
    description: "Routes users to appropriate topics"
    reasoning:
        instructions:->
            | Determine what the user needs help with.
            | Route to the appropriate topic.
        actions:
            orders: @utils.transition to @topic.order_management
                description: "Help with orders"
            support: @utils.transition to @topic.support
                description: "Technical support"
            billing: @utils.transition to @topic.billing
                description: "Billing questions"
```

### Pattern 3: Action with Validation
```agentscript
topic order_processing:
    description: "Processes customer orders"
    reasoning:
        instructions:->
            if @variables.cart_total <= 0:
                | Your cart is empty. Add items before checkout.
            if @variables.cart_total > 10000:
                set @variables.needs_approval = True
                | Large orders require approval.
        actions:
            process: @actions.create_order
                with items=@variables.cart_items
                available when @variables.cart_total > 0
                available when @variables.needs_approval == False
```

---

## Anti-Patterns

| Anti-Pattern | Issue | Fix |
|--------------|-------|-----|
| Tab indentation | Syntax error | Use 4 spaces |
| `@variable.name` | Wrong syntax | Use `@variables.name` (plural) |
| Nested `run` | Not supported | Flatten to sequential `run` |
| Missing topic description | Poor routing | Add description to all topics |
| Hardcoded IDs | Not maintainable | Use variables or action lookups |
| No system guardrails | Security risk | Add instructions in system block |
| 3-space indent | Syntax error | Must be 4 spaces minimum |

---

## CLI Commands Reference

```bash
# Generate agent version from script
sf agent generate version --name [AgentName] --target-org [alias]

# List agent versions
sf agent list versions --name [AgentName] --target-org [alias]

# Activate a version
sf agent activate version --name [AgentName] --version-number [N] --target-org [alias]

# Preview agent
sf agent preview --name [AgentName] --target-org [alias]

# Retrieve agent script
sf project retrieve start --metadata AiAuthoringBundle:[AgentName] --target-org [alias]

# Deploy agent
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
```

---

## Validation

**Manual validation** (if hooks don't fire):
```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-agentforce/hooks/scripts/validate_agentforce.py <file_path>
```

**Scoring**: 100 points / 6 categories. Minimum 60 (60%) for deployment.

**Hooks not firing?** Check: `CLAUDE_PLUGIN_ROOT` set, hooks.json valid, Python 3 in PATH, file matches pattern `*.agentscript`.

---

## 🔑 Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| 4-Space Indentation | 3 spaces causes parse errors | Always use 4 spaces |
| `@variables` is plural | `@variable.x` fails | Use `@variables.x` |
| Boolean capitalization | `true/false` invalid | Use `True/False` |
| One callback level | Nested `run` fails | Flatten callbacks |
| Template syntax | `{@var}` invalid | Use `{!@variables.var}` |

---

## Reference & Dependencies

**Docs**: `../../docs/` - best-practices, agent-script-syntax, topic-patterns, action-integration

**Dependencies**: sf-deploy (optional) for deployment. Install: `/plugin install github:Jaganpro/sf-skills/sf-deploy`

**Notes**: API 64.0+ required | Agent Script is Beta (Nov 2025) | Block if score < 60

---

## License

MIT License. See [LICENSE](../../LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
