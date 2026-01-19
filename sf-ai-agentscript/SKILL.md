---
name: sf-ai-agentscript
description: >
  Agent Script DSL development skill for Salesforce Agentforce.
  Enables writing deterministic agents in a single .agent file with
  FSM architecture, instruction resolution, and hybrid reasoning.
  Covers syntax, debugging, testing, and CLI deployment.
license: MIT
compatibility: "Requires Agentforce license, API v65.0+, Einstein Agent User"
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 6 categories"
---

# SF-AI-AgentScript Skill

> **"Prompt engineering is like writing laws in poetry - beautiful, but not enforceable."**

Agent Script transforms agent development from prompt-based suggestions to **code-enforced guarantees**. This skill guides you through writing, debugging, testing, and deploying Agentforce agents using the Agent Script DSL.

---

## ⚠️ CRITICAL WARNINGS

### API & Version Requirements
| Requirement | Value | Notes |
|-------------|-------|-------|
| **API Version** | 65.0+ | Required for Agent Script support |
| **License** | Agentforce | Required for agent authoring |
| **Einstein Agent User** | Required | Must exist in org for `default_agent_user` |
| **File Extension** | `.agent` | Single file contains entire agent definition |

### MANDATORY Pre-Deployment Checks
1. **`default_agent_user` MUST be valid** - Query: `SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true`
2. **No mixed tabs/spaces** - Use consistent indentation (2-space, 3-space, or tabs - never mix)
3. **Booleans are capitalized** - Use `True`/`False`, not `true`/`false`
4. **Exactly one `start_agent` block** - Multiple entry points cause compilation failure

### Cross-Skill Orchestration

| Direction | Pattern | Priority |
|-----------|---------|----------|
| **Before Agent Script** | `/sf-flow` - Create Flows for `flow://` action targets | ⚠️ REQUIRED |
| **After Agent Script** | `/sf-ai-agentforce-testing` - Test topic routing and actions | ✅ RECOMMENDED |
| **For Deployment** | `/sf-deploy` - Publish agent with `sf agent publish` | ⚠️ REQUIRED |

---

## 📋 QUICK REFERENCE: Agent Script Syntax

### Block Structure (Required Order)
```yaml
system:        # Required: Global messages and instructions
config:        # Required: Agent metadata (agent_name, default_agent_user)
variables:     # Optional: State management (mutable/linked)
language:      # Optional: Supported languages
connections:   # Optional: External system integrations
topic:         # Required: Conversation topics (one or more)
start_agent:   # Required: Entry point (exactly one)
```

### Instruction Syntax Patterns
| Pattern | Purpose | Example |
|---------|---------|---------|
| `instructions: \|` | Simple multi-line text | `instructions: \| Help the user.` |
| `instructions: ->` | Arrow syntax (enables expressions) | `instructions: -> if @variables.x:` |
| `\| text` | Literal text for LLM prompt | `\| Hello {!@variables.name}!` |
| `if @variables.x:` | Conditional (resolves before LLM) | `if @variables.verified == True:` |
| `run @actions.x` | Execute action during resolution | `run @actions.load_customer` |
| `set @var = @outputs.y` | Capture action output | `set @variables.risk = @outputs.score` |
| `{!@variables.x}` | Variable injection in text | `Risk score: {!@variables.risk}` |
| `available when` | Control action visibility to LLM | `available when @variables.verified == True` |
| `transition to @topic.x` | Deterministic topic change | `transition to @topic.escalation` |
| `@utils.transition to` | LLM-chosen topic change | `go_main: @utils.transition to @topic.main` |
| `@utils.escalate` | Hand off to human agent | `escalate: @utils.escalate` |

### Variable Types
| Modifier | Behavior | Example |
|----------|----------|---------|
| `mutable` | Read/write state | `counter: mutable number = 0` |
| `linked` | Read-only from external source | `session_id: linked string` + `source: @session.sessionID` |

### Action Target Protocols
| Protocol | Use When | Example |
|----------|----------|---------|
| `flow://` | Data operations, business logic | `target: "flow://GetOrderStatus"` |
| `apex://` | Custom calculations, validation | `target: "apex://RefundCalculator"` |
| `generatePromptResponse://` | Grounded LLM responses | `target: "generatePromptResponse://Case_Summary"` |
| `retriever://` | RAG knowledge search | `target: "retriever://Policy_Index"` |
| `externalService://` | Third-party APIs | `target: "externalService://AddressValidation"` |
| `standardInvocableAction://` | Built-in SF actions | `target: "standardInvocableAction://emailSimple"` |

---

## 🔄 WORKFLOW: Agent Development Lifecycle

### Phase 1: Requirements & Design
1. **Identify deterministic vs. subjective logic**
   - Deterministic: Security checks, financial thresholds, data lookups, counters
   - Subjective: Greetings, context understanding, natural language generation
2. **Design FSM architecture** - Map topics as states, transitions as edges
3. **Define variables** - Mutable for state tracking, linked for session context

### Phase 2: Agent Script Authoring
1. **Create `.agent` file** with required blocks
2. **Write topics** with instruction resolution pattern:
   - Post-action checks at TOP (triggers on loop)
   - Pre-LLM data loading
   - Dynamic instructions for LLM
3. **Configure actions** with appropriate target protocols
4. **Add `available when` guards** to enforce security

### Phase 3: Validation (LSP + CLI)

> **AUTOMATIC**: LSP validation runs on every Write/Edit to `.agent` files. Errors are reported with line numbers and autofix suggestions.

#### LSP Validation Loop (Find Error → Autofix)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Write/Edit  │ ──▶ │ LSP Analyze │ ──▶ │ Report      │
│ .agent file │     │ (automatic) │     │ Errors      │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
      ┌────────────────────────────────────────┘
      ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Claude      │ ──▶ │ Apply Fix   │ ──▶ │ Re-validate │
│ Suggests Fix│     │ (Edit tool) │     │ (loop)      │
└─────────────┘     └─────────────┘     └─────────────┘
```

#### LSP Checks (Automatic)
| Check | Severity | Autofix |
|-------|----------|---------|
| Mixed tabs/spaces | ❌ Error | Convert to consistent spacing |
| Lowercase booleans (`true`/`false`) | ❌ Error | Capitalize to `True`/`False` |
| Missing required blocks | ❌ Error | Add missing block template |
| Missing `default_agent_user` | ❌ Error | Add placeholder with comment |
| Mutable + linked conflict | ❌ Error | Remove conflicting modifier |
| Undefined topic references | ⚠️ Warning | Create topic stub |
| Post-action check position | ⚠️ Warning | Move to top of instructions |

#### CLI Validation (Before Deploy)
```bash
# Validate authoring bundle syntax
sf agent validate authoring-bundle --source-dir ./force-app/main/default/aiAuthoringBundles/MyAgent
```

#### Manual Checks
- `default_agent_user` exists and is active Einstein Agent User
- All topic references resolve to existing topics
- Action targets (`flow://`, `apex://`, etc.) exist in org

### Phase 4: Testing (Delegate to `/sf-ai-agentforce-testing`)
1. **Batch testing** - Run up to 100 test cases simultaneously
2. **Quality metrics** - Completeness, Coherence, Topic/Action Assertions
3. **LLM-as-Judge** - Automated scoring against golden responses

### Phase 5: Deployment

> ⚠️ **CRITICAL**: Use `sf agent publish authoring-bundle`, NOT `sf project deploy start`

1. **Create bundle directory**: `force-app/main/default/aiAuthoringBundles/AgentName/`
2. **Add files**:
   - `AgentName.agent` - Your Agent Script
   - `AgentName.bundle-meta.xml` - Metadata XML (NOT `.aiAuthoringBundle-meta.xml`!)
3. **Publish**: `sf agent publish authoring-bundle --source-dir ./force-app/main/default/aiAuthoringBundles/AgentName`
4. **Monitor** - Use trace debugging for production issues

### Phase 6: CLI Operations
```bash
# Retrieve from org
sf agent retrieve --name MyAgent --target-org sandbox

# Validate syntax
sf agent validate authoring-bundle --source-dir ./force-app/main/default/aiAuthoringBundles/MyAgent

# Publish to org (NOT sf project deploy!)
sf agent publish authoring-bundle --source-dir ./force-app/main/default/aiAuthoringBundles/MyAgent
```

### Bundle Structure (CRITICAL)
```
force-app/main/default/aiAuthoringBundles/
└── MyAgent/
    ├── MyAgent.agent              # Agent Script file
    └── MyAgent.bundle-meta.xml    # NOT .aiAuthoringBundle-meta.xml!
```

**bundle-meta.xml content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

---

## 📊 SCORING SYSTEM (100 Points)

### Categories

| Category | Points | Key Criteria |
|----------|--------|--------------|
| **Structure & Syntax** | 20 | Block ordering, indentation consistency, required fields present |
| **Deterministic Logic** | 25 | Security via `available when`, post-action checks, proper conditionals |
| **Instruction Resolution** | 20 | Correct use of `->` vs `\|`, template injection, action execution |
| **FSM Architecture** | 15 | Clear topic separation, explicit transitions, state management |
| **Action Configuration** | 10 | Correct protocols, input/output mapping, error handling |
| **Deployment Readiness** | 10 | Valid `default_agent_user`, no compilation errors, metadata complete |

### Scoring Rubric Details

#### Structure & Syntax (20 points)
| Points | Criteria |
|--------|----------|
| 20 | All required blocks present, consistent indentation, valid identifiers |
| 15 | Minor issues (e.g., inconsistent spacing within tolerance) |
| 10 | Missing optional blocks that would improve clarity |
| 5 | Block ordering issues or mixed indentation |
| 0 | Missing required blocks or compilation failures |

#### Deterministic Logic (25 points)
| Points | Criteria |
|--------|----------|
| 25 | All security actions guarded with `available when`, post-action patterns used |
| 20 | Most guards present, minor gaps in deterministic enforcement |
| 15 | Some security logic relies on prompts instead of guards |
| 10 | Critical actions lack `available when` guards |
| 0 | Security logic entirely prompt-based (LLM can bypass) |

#### Instruction Resolution (20 points)
| Points | Criteria |
|--------|----------|
| 20 | Arrow syntax for complex logic, proper template injection, correct action execution |
| 15 | Mostly correct, minor syntax issues |
| 10 | Uses pipe syntax where arrow needed, template injection errors |
| 5 | Incorrect phase ordering (data loads after LLM sees instructions) |
| 0 | Fundamental misunderstanding of resolution order |

#### FSM Architecture (15 points)
| Points | Criteria |
|--------|----------|
| 15 | Clear topic boundaries, explicit transitions, appropriate escalation paths |
| 12 | Good structure with minor redundancy |
| 9 | Topics too broad or transitions unclear |
| 5 | Monolithic topic handling multiple concerns |
| 0 | No topic separation, all logic in start_agent |

#### Action Configuration (10 points)
| Points | Criteria |
|--------|----------|
| 10 | Correct protocols, proper I/O mapping, descriptions present |
| 8 | Minor issues (missing descriptions) |
| 5 | Wrong protocol for use case |
| 2 | Input/output mapping errors |
| 0 | Actions don't compile |

#### Deployment Readiness (10 points)
| Points | Criteria |
|--------|----------|
| 10 | Valid user, clean validation, metadata complete |
| 8 | Minor warnings |
| 5 | Validation errors that need fixing |
| 2 | Missing metadata files |
| 0 | Cannot deploy |

### Score Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Deploy with confidence |
| 80-89 | ⭐⭐⭐⭐ Very Good | Minor improvements recommended |
| 70-79 | ⭐⭐⭐ Good | Review flagged issues before deploy |
| 60-69 | ⭐⭐ Needs Work | Address issues before deploy |
| <60 | ⭐ Critical | **BLOCK** - Fix critical issues |

### Score Report Format
```
📊 AGENT SCRIPT SCORE REPORT
════════════════════════════════════════

Score: 85/100 ⭐⭐⭐⭐ Very Good
├─ Structure & Syntax:    18/20 (90%)
├─ Deterministic Logic:   22/25 (88%)
├─ Instruction Resolution: 16/20 (80%)
├─ FSM Architecture:      12/15 (80%)
├─ Action Configuration:   9/10 (90%)
└─ Deployment Readiness:   8/10 (80%)

Issues:
⚠️ [Deterministic] Missing `available when` on process_refund action
⚠️ [Resolution] Post-action check should be at TOP of instructions
✓ All Structure & Syntax checks passed
✓ All Action Configuration checks passed
```

---

## 🔧 THE 6 DETERMINISTIC BUILDING BLOCKS

These execute as **code**, not suggestions. The LLM cannot override them.

| # | Block | Description | Example |
|---|-------|-------------|---------|
| 1 | **Conditionals** | if/else resolves before LLM | `if @variables.attempts >= 3:` |
| 2 | **Topic Filters** | Control action visibility | `available when @variables.verified == True` |
| 3 | **Variable Checks** | Numeric/boolean comparisons | `if @variables.churn_risk >= 80:` |
| 4 | **Inline Actions** | Immediate execution | `run @actions.load_customer` |
| 5 | **Utility Actions** | Built-in helpers | `@utils.transition`, `@utils.escalate` |
| 6 | **Variable Injection** | Template values | `{!@variables.customer_name}` |

---

## 📐 ARCHITECTURE PATTERNS

### Pattern 1: Hub and Spoke
Central router (hub) to specialized topics (spokes). Use for multi-purpose agents.
```
       ┌─────────────┐
       │ topic_sel   │
       │   (hub)     │
       └──────┬──────┘
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│refunds │ │ orders │ │support │
└────────┘ └────────┘ └────────┘
```

### Pattern 2: Verification Gate
Security gate before protected topics. Mandatory for sensitive data.
```
┌─────────┐     ┌──────────┐     ┌───────────┐
│  entry  │ ──▶ │ VERIFY   │ ──▶ │ protected │
└─────────┘     │  (GATE)  │     │  topics   │
                └────┬─────┘     └───────────┘
                     │ 3 fails
                     ▼
                ┌──────────┐
                │ lockout  │
                └──────────┘
```

### Pattern 3: Post-Action Loop
Topic re-resolves after action completes - put checks at TOP.
```yaml
topic refund:
  reasoning:
    instructions: ->
      # POST-ACTION CHECK (at TOP - triggers on next loop)
      if @variables.refund_status == "Approved":
        run @actions.create_crm_case
        transition to @topic.success

      # PRE-LLM DATA LOADING
      run @actions.check_churn_risk
      set @variables.risk = @outputs.score

      # DYNAMIC INSTRUCTIONS FOR LLM
      if @variables.risk >= 80:
        | Offer full refund to retain customer.
      else:
        | Offer $10 credit instead.
```

---

## 🐛 DEBUGGING: Trace Analysis

### The 6 Span Types
| Span | Description |
|------|-------------|
| ➡️ `topic_enter` | Execution enters a topic |
| ▶ `before_reasoning` | Deterministic pre-processing |
| 🧠 `reasoning` | LLM processes instructions |
| ⚡ `action_call` | Action invoked |
| → `transition` | Topic navigation |
| ✓ `after_reasoning` | Deterministic post-processing |

### Debugging Workflow
1. **Interaction Details** - Quick understanding of what happened
2. **Trace Waterfall** - Technical view with exact prompts, latencies
3. **Variable State** - Entry vs Exit values reveal when state was ignored
4. **Script View** - Red squiggles show syntax errors

### Common Debug Patterns
| Symptom | Check | Fix |
|---------|-------|-----|
| Wrong policy applied | Variable Entry values | Change `mutable` to `linked` with `source:` |
| Action executed without auth | `available when` presence | Add guard clause |
| LLM ignores variable | Instruction resolution order | Move data load before LLM text |
| Infinite loop | Transition conditions | Add exit condition |

---

## ⚠️ COMMON ISSUES & FIXES

| Issue | Symptom | Fix |
|-------|---------|-----|
| `Internal Error, try again later` | Invalid `default_agent_user` | Query for valid Einstein Agent User |
| `SyntaxError: cannot mix spaces and tabs` | Mixed indentation | Use consistent spacing throughout |
| `Transition to undefined topic` | Typo in topic reference | Check spelling, ensure topic exists |
| `Variables cannot be both mutable AND linked` | Conflicting modifiers | Choose one: mutable for state, linked for external |
| `Required fields missing: [BundleType]` | Using wrong deploy command | Use `sf agent publish authoring-bundle`, NOT `sf project deploy start` |
| `Cannot find a bundle-meta.xml file` | Wrong file naming | Rename to `AgentName.bundle-meta.xml`, NOT `.aiAuthoringBundle-meta.xml` |
| LLM bypasses security check | Using prompts for security | Use `available when` guards instead |
| Post-action logic doesn't run | Check not at TOP | Move post-action check to first lines |
| Wrong data retrieved | Missing filter | Wrap retriever in Flow with filter inputs |

### Deployment Gotchas (Validated by Testing)

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| `AgentName.aiAuthoringBundle-meta.xml` | `AgentName.bundle-meta.xml` |
| `sf project deploy start` | `sf agent publish authoring-bundle` |
| `sf agent validate --source-dir` | `sf agent validate authoring-bundle --source-dir` |

---

## 📚 DOCUMENT MAP (Progressive Disclosure)

### Tier 2: Resource Guides (Comprehensive)
| Need | Document | Description |
|------|----------|-------------|
| Syntax reference | [resources/syntax-reference.md](resources/syntax-reference.md) | Complete block & expression syntax |
| FSM design | [resources/fsm-architecture.md](resources/fsm-architecture.md) | State machine patterns & examples |
| Instruction resolution | [resources/instruction-resolution.md](resources/instruction-resolution.md) | Three-phase execution model |
| Data & multi-agent | [resources/grounding-multiagent.md](resources/grounding-multiagent.md) | Retriever actions & SOMA patterns |
| Debugging | [resources/debugging-guide.md](resources/debugging-guide.md) | Trace analysis & forensics |
| Testing | [resources/testing-guide.md](resources/testing-guide.md) | Batch testing & quality metrics |

### Tier 3: Quick References (Docs)
| Need | Document | Description |
|------|----------|-------------|
| CLI commands | [docs/cli-guide.md](docs/cli-guide.md) | sf agent retrieve/validate/deploy |
| Patterns | [docs/patterns-quick-ref.md](docs/patterns-quick-ref.md) | Decision tree for pattern selection |

---

## 🔗 CROSS-SKILL INTEGRATION

### MANDATORY Delegations
| Task | Delegate To | Reason |
|------|-------------|--------|
| Create Flows for `flow://` targets | `/sf-flow` | Flows must exist before agent uses them |
| Test agent routing & actions | `/sf-ai-agentforce-testing` | Specialized testing patterns |
| Deploy agent to org | `/sf-deploy` | Proper deployment validation |

### Integration Patterns
| From | To | Pattern |
|------|-----|---------|
| `/sf-ai-agentscript` | `/sf-flow` | Create Flow, then reference in agent |
| `/sf-ai-agentscript` | `/sf-apex` | Create Apex class, then use `apex://` protocol |
| `/sf-ai-agentscript` | `/sf-integration` | Set up Named Credentials for `externalService://` |

---

## ✅ DEPLOYMENT CHECKLIST

### Configuration
- [ ] `default_agent_user` is valid Einstein Agent User
- [ ] `agent_name` uses snake_case (no spaces)

### Syntax
- [ ] No mixed tabs/spaces
- [ ] Booleans use `True`/`False`
- [ ] Variable names use snake_case

### Structure
- [ ] Exactly one `start_agent` block
- [ ] At least one `topic` block
- [ ] All transitions reference existing topics

### Security
- [ ] Critical actions have `available when` guards
- [ ] Session data uses `linked` variables (not `mutable`)

### Testing
- [ ] `sf agent validate --source-dir ./my-agent` passes
- [ ] Preview mode tested before activation

---

## 🚀 MINIMAL WORKING EXAMPLE

```yaml
system:
  messages:
    welcome: "Hello! How can I help you today?"
    error: "Sorry, something went wrong."
  instructions: "You are a helpful customer service agent."

config:
  agent_name: "simple_agent"
  agent_label: "Simple Agent"
  description: "A minimal working agent example"
  default_agent_user: "agent_user@yourorg.com"

variables:
  customer_verified: mutable boolean = False

topic main:
  description: "Main conversation handler"
  reasoning:
    instructions: ->
      if @variables.customer_verified == True:
        | You are speaking with a verified customer.
        | Help them with their request.
      else:
        | Please verify the customer's identity first.
    actions:
      verify: @actions.verify_customer
        description: "Verify customer identity"
        set @variables.customer_verified = @outputs.verified

start_agent entry:
  description: "Entry point for all conversations"
  reasoning:
    instructions: |
      Greet the customer and route to the main topic.
    actions:
      go_main: @utils.transition to @topic.main
        description: "Navigate to main conversation"
```

---

## 📖 OFFICIAL RESOURCES

- [Agent Script Documentation](https://developer.salesforce.com/docs/einstein/genai/guide/agent-script.html)
- [Agentforce Builder Guide](https://help.salesforce.com/s/articleView?id=sf.copilot_builder_overview.htm)
- [Atlas Reasoning Engine](https://developer.salesforce.com/docs/einstein/genai/guide/atlas-reasoning-engine.html)

---

## 🏷️ VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01 | Initial release with 8-module coverage |
