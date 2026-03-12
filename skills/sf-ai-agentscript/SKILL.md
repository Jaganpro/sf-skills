---
name: sf-ai-agentscript
description: >
  Agent Script DSL for deterministic Agentforce agents.
  TRIGGER when: user writes or edits .agent files, builds FSM-based agents,
  uses Agent Script CLI (sf agent generate/publish), or asks about deterministic
  agent patterns, slot filling, or instruction resolution.
  DO NOT TRIGGER when: Setup UI agent building (use sf-ai-agentforce), agent
  testing (use sf-ai-agentforce-testing), or persona design
  (use sf-ai-agentforce-persona).
license: MIT
compatibility: "Requires Agentforce license, API v66.0+, Einstein Agent User"
metadata:
  version: "2.7.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 6 categories"
  validated: "0-shot generation tested (Pet_Adoption_Advisor, TechCorp_IT_Agent, Quiz_Master, Expense_Calculator, Order_Processor). Agent user setup validated against ORM1, ORM2, AutomotiveSupport, SalesforceProductAssistant."
  # Validation Framework
  last_validated: "2026-03-13"
  validation_status: "PASS"
  validation_agents: 24
  validate_by: "2026-04-10"  # 30 days from last validation
  validation_org: "AgentforceTesting"
---

# SF-AI-AgentScript Skill

> **"Prompt engineering is like writing laws in poetry - beautiful, but not enforceable."**

Agent Script transforms agent development from prompt-based suggestions to **code-enforced guarantees**. This skill guides you through writing, debugging, testing, and deploying Agentforce agents using the Agent Script DSL.

---

## ⚠️ CRITICAL WARNINGS

### API & Version Requirements
| Requirement | Value | Notes |
|-------------|-------|-------|
| **API Version** | 66.0+ | Required for Agent Script support |
| **License** | Agentforce | Required for agent authoring |
| **Einstein Agent User** | Service Agents only | Required for `AgentforceServiceAgent`; NOT needed for `AgentforceEmployeeAgent`. See [references/agent-user-setup.md](references/agent-user-setup.md) |
| **File Extension** | `.agent` | Single file contains entire agent definition |

### MANDATORY Pre-Deployment Checks
1. **`default_agent_user` MUST be valid (Service Agents only)** - Not needed for `AgentforceEmployeeAgent`. For Service Agents: verify Einstein Agent User exists, `AgentforceServiceAgentUser` system PS is assigned, and a custom `{AgentName}_Access` PS with `<classAccesses>` is deployed. Query: `SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true`. See [references/agent-user-setup.md](references/agent-user-setup.md) for full 6-step workflow.
2. **No mixed tabs/spaces** - Use consistent indentation (2-space, 3-space, or tabs - never mix)
3. **Booleans are capitalized** - Use `True`/`False`, not `true`/`false`
4. **Exactly one `start_agent` block** - Multiple entry points cause compilation failure

### ⛔ SYNTAX CONSTRAINTS (Validated via Testing + Official Spec)

| Constraint | ❌ WRONG | ✅ CORRECT |
|------------|----------|-----------|
| **No `else if` keyword; no nested if** | `else if x:` or `else:` + nested `if` (both invalid) | `if x and y:` (compound), or flatten to sequential ifs |
| **No comment-only `if` bodies** | `if @variables.x:` + only `# comment` (empty body) | Add executable statement: `| text`, `run`, `set`, or `transition` |
| **No top-level `actions:` block** | `actions:` at root level | Actions only inside `topic.reasoning.actions:` |
| **No `inputs:`/`outputs:` in action INVOCATIONS (Level 2)** | `inputs:` block inside `reasoning.actions:` invocation | Use `with`/`set` in `reasoning.actions:` invocations. The topic-level `actions:` definitions DO use `inputs:`/`outputs:` blocks. |
| **Multiple `available when` supported** | *(previously listed as error)* | `available when A` + `available when B` on same action is valid (TDD validated 2026-02-14). **Org-dependent**: compiles on AgentforceTesting but REJECTED on some orgs with "Duplicate 'available when' clause." Use compound `and` conditions for portability. |
| **Avoid reserved action names** | `escalate: @utils.escalate` | `escalate_now: @utils.escalate` |
| **`...` is slot-filling only** | `my_var: mutable string = ...` | `my_var: mutable string = ""` |
| **No defaults on linked vars** | `id: linked string = ""` | `id: linked string` + `source:` |
| **Linked vars: no object/list** | `data: linked object` | Use `linked string` or parse in Flow |
| **Post-action only on @actions** | `@utils.X` with `set`/`run` | Only `@actions.X` supports post-action |
| **agent_name must match folder** | Folder: `MyAgent`, config: `my_agent` | Both must be identical (case-sensitive) |
| **Reserved field names** | `description: string`, `label: string` | Use `descriptions`, `label_text`, or suffix with `_field` |
| **No `@inputs` in `set`** | `set @variables.x = @inputs.y` (unknown deploy error) | Use `@utils.setVariables` to capture input, then reference via `@variables` |
| **Always use `@actions.` prefix** | `run set_user_name` or `\| Use add_to_cart` | `run @actions.set_user_name` or `\| Use {!@actions.add_to_cart}` |
| **`run` only for topic-level actions** | `run @actions.X` where X is `@utils.setVariables` | `run @actions.X` resolves against `actions:` with `target:` — define utilities in `reasoning.actions:` |

### 🔴 Reserved Field Names (Breaking in Recent Releases)

Common field names that cause parse errors **when used as variable or I/O field names**:
```
❌ RESERVED as variable/field names:
description, label, is_required, is_displayable, is_used_by_planner

✅ WORKAROUNDS for variable/field names:
description  → descriptions, description_text, desc_field
label        → label_text, display_label, label_field
```

> **Important distinction**: `is_required`, `is_displayable`, `is_used_by_planner`, and `label` are reserved as **variable/field names** but are valid as **action I/O metadata properties**. For example, you cannot name a variable `label`, but you CAN use `label:` as a property on an action definition, input, or output. See [references/feature-validity.md](references/feature-validity.md).

> **Also reserved as `@InvocableVariable` names in Apex**: `model`, `description`, `label`. These compile as valid Apex but cause `SyntaxError` during Agent Script compilation. Use workarounds: `vehicle_model`, `issue_description`, `label_text`. See [references/production-gotchas.md](references/production-gotchas.md) for details.

### Feature Validity, Data Types & UI Bugs

> See [references/feature-validity.md](references/feature-validity.md) for the full feature validity by context table (which properties work on `@utils.transition` vs target-backed actions).

> See [references/complex-data-types.md](references/complex-data-types.md) for the `complex_data_type_name` mapping table and Agent Script → Lightning type mapping.

> **Canvas View** can silently corrupt syntax (`==` → `{! OPERATOR.EQUAL }`, missing colons, de-indentation). Always use **Script view** for structural edits. **Preview Mode** has known bugs with linked variables and output property access — see [references/known-issues.md](references/known-issues.md) for workarounds.

> **Conditional nesting**: `else if` is NOT valid, nested `if` inside `if`/`else:` is NOT valid (TDD disproved). Use compound `if A and B:` or flatten to sequential ifs. `...` is slot-filling only (for `with param=...`). Post-action `set`/`run` only works on `@actions.*`, NOT `@utils.*`. See [references/syntax-reference.md](references/syntax-reference.md) for detailed examples.

---

## 💰 PRODUCTION GOTCHAS

> See [references/production-gotchas.md](references/production-gotchas.md) for the full production guide including: credit consumption table, lifecycle hooks (`before_reasoning:`/`after_reasoning:` syntax), supervision vs handoff, zero-hallucination routing with `filter_from_agent`/`is_used_by_planner`, action I/O metadata properties, action chaining, latch variable pattern, loop protection, token limits, progress indicators, VS Code limitations, and language block quirks.

**Key highlights:**
- Framework operations (`@utils.*`, `if`/`else`, `set`, lifecycle hooks) are **FREE** — only Flow/Apex/API actions cost 20 credits each
- `before_reasoning:`/`after_reasoning:` content goes **directly** under the block (NO `instructions:` wrapper)
- Use `filter_from_agent: True` + `is_used_by_planner: True` on outputs for zero-hallucination routing

### Cross-Skill Orchestration

| Direction | Pattern | Priority |
|-----------|---------|----------|
| **Before Agent Script** | `/sf-flow` - Create Flows for `flow://` action targets | ⚠️ REQUIRED |
| **After Agent Script** | `/sf-ai-agentforce-testing` - Test topic routing and actions | ✅ RECOMMENDED |
| **For Deployment** | `/sf-deploy` - Publish agent with `sf agent publish authoring-bundle` | ⚠️ REQUIRED |

> **Tip**: Open Agentforce Studio list view with `sf org open authoring-bundle -o TARGET_ORG` (v2.121.7+). Open a specific agent with `sf org open agent --api-name MyAgent -o TARGET_ORG`.

---

## 📋 QUICK REFERENCE: Agent Script Syntax

### Block Structure (CORRECTED Order per Official Spec)
```yaml
config:        # 1. Required: Agent metadata (developer_name, agent_type, default_agent_user)
variables:     # 2. Optional: State management (mutable/linked)
system:        # 3. Required: Global messages and instructions
connection:    # 4. Optional: Escalation routing — use `connection messaging:` (singular, NOT `connections:`)
knowledge:     # 5. Optional: Knowledge base config
language:      # 6. Optional: Locale settings
start_agent:   # 7. Required: Entry point (exactly one)
topic:         # 8. Required: Conversation topics (one or more)
# Note: Topics can override agent-level system: with a topic-level system: block
```

### Config Block Field Names (CRITICAL)

| Documented Field (Wrong) | Actual Field (Correct) | Notes |
|--------------------------|------------------------|-------|
| `agent_name` | `developer_name` | Must match folder name (case-sensitive) |
| `description` | `agent_description` | Agent's purpose description |
| *(missing)* | `agent_type` | **Required**: `AgentforceServiceAgent` or `AgentforceEmployeeAgent`. Determines the entire permission model — see [references/agent-user-setup.md](references/agent-user-setup.md) |

```yaml
# ✅ CORRECT: Service Agent config
config:
  developer_name: "my_service_agent"
  agent_description: "Handles customer support inquiries"
  agent_type: "AgentforceServiceAgent"
  default_agent_user: "agent_user@00dxx000001234.ext"

# ✅ CORRECT: Employee Agent config (simpler -- no dedicated user)
config:
  developer_name: "my_employee_agent"
  agent_description: "Internal assistant for employees"
  agent_type: "AgentforceEmployeeAgent"
  # NO default_agent_user -- agent runs as logged-in employee
```

> **Omitting `agent_type` defaults to Service Agent behavior.** If you also omit `default_agent_user`, publish will fail with HTTP 500. Always set `agent_type` explicitly.

### Naming Rules
- Only letters, numbers, underscores. Must begin with a letter.
- No spaces, no consecutive underscores, cannot end with underscore. **Max 80 characters.**

### Instruction Syntax Patterns
| Pattern | Purpose | Example |
|---------|---------|---------|
| `instructions: \|` | Literal multi-line (no expressions) | `instructions: \| Help the user.` |
| `instructions: ->` | Procedural (enables expressions) | `instructions: -> if @variables.x:` |
| `\| text` | Literal text for LLM prompt | `\| Hello` + variable injection |
| `if @variables.x:` | Conditional (resolves before LLM) | `if @variables.verified == True:` |
| `run @actions.x` | Execute action during resolution | `run @actions.load_customer` |
| `set @var = @outputs.y` | Capture action output | `set @variables.risk = @outputs.score` |
| `{!@variables.x}` | Variable injection in text | `Risk score: {!@variables.risk}` |
| `available when` | Control action visibility to LLM | `available when @variables.verified == True` |
| `with param=...` | LLM slot-filling (extracts from conversation) | `with query=...` |

### Transition vs Delegation (CRITICAL DISTINCTION)
| Syntax | Behavior | Returns? | Use When |
|--------|----------|----------|----------|
| `@utils.transition to @topic.X` | Permanent handoff | ❌ No | Checkout, escalation, final states |
| `@topic.X` (in reasoning.actions) | Delegation | ✅ Yes | Get expert advice, sub-tasks |
| `transition to @topic.X` (inline) | Deterministic jump | ❌ No | Post-action routing, gates |

### Expression Operators (Safe Subset)
| Category | Operators | NOT Supported |
|----------|-----------|---------------|
| Comparison | `==`, `!=`, `<`, `<=`, `>`, `>=`, `is`, `is not` | ❌ `<>` (not valid, use `!=`) |
| Logical | `and`, `or`, `not` | |
| Arithmetic | `+`, `-` | ❌ `*`, `/`, `%` |

### Variable Types
| Modifier | Behavior | Supported Types | Default Required? |
|----------|----------|-----------------|-------------------|
| `mutable` | Read/write state | `string`, `number`, `boolean`, `object`, `date`, `id`, `list[T]` | ✅ Yes |
| `linked` | Read-only from source | `string`, `number`, `boolean`, `date`, `id` | ❌ No (has `source:`) |

> ⚠️ **Linked variables CANNOT use `object` or `list` types**. `timestamp`, `currency`, `datetime`, `time`, `integer`, `long` compile but are absent from official GA variable type docs — prefer `date` for date/time. These types are valid for action I/O only. See [references/actions-reference.md](references/actions-reference.md) for the full type matrix.

### Connection Block (Escalation Routing)

> ⚠️ **Service Agents Only**. Use `connection messaging:` (singular, NOT `connections:`). The `outbound_route_name` requires `flow://` prefix.

```yaml
# Minimal form (no routing):
connection messaging:
   adaptive_response_allowed: True

# Full form with escalation routing:
connection messaging:
   outbound_route_type: "OmniChannelFlow"
   outbound_route_name: "flow://Route_from_Agent"
   escalation_message: "Connecting you with a specialist."
   adaptive_response_allowed: False
```

**All-or-nothing rule**: When `outbound_route_type` is present, ALL three route properties are required (`outbound_route_type`, `outbound_route_name`, `escalation_message`). Valid channel types: `messaging`, `voice`, `web`.

### Two-Level Action System

```
Level 1: ACTION DEFINITION (in topic's `actions:` block)
   → Has `target:`, `inputs:`, `outputs:`, `description:`

Level 2: ACTION INVOCATION (in `reasoning.actions:` block)
   → References Level 1 via `@actions.name`
   → Specifies HOW to call it (with/set clauses)
```

> For AiAuthoringBundle (Agent Script): `flow://` and `apex://` targets work **directly** — no GenAiFunction registration needed. I/O schemas (`inputs:` + `outputs:`) are REQUIRED for publish — omitting them causes "Internal Error." See [references/actions-reference.md](references/actions-reference.md) for complete action types, target protocols, I/O name matching rules, and the Bare @InvocableMethod pattern.

---

## 🔄 WORKFLOW: Agent Development Lifecycle

### Phase 1: Requirements & Design
1. **Identify deterministic vs. subjective logic** — Deterministic: security checks, thresholds, data lookups. Subjective: greetings, context understanding, NLG.
2. **Design FSM architecture** — Map topics as states, transitions as edges
3. **Define variables** — Mutable for state tracking, linked for session context

> 📋 **Discovery Questions**: Use the pre-authoring questionnaire in [references/patterns-quick-ref.md](references/patterns-quick-ref.md#discovery-questions-pre-authoring) to clarify Agent Identity, Topics, State, Actions, and Reasoning requirements before writing any code.

### Phase 2: Agent Script Authoring
1. **Create `.agent` file** with required blocks (see Block Structure above)
2. **Write topics** with instruction resolution pattern: post-action checks at TOP, pre-LLM data loading, dynamic instructions for LLM
3. **Configure actions** with appropriate target protocols
4. **Add `available when` guards** to enforce security deterministically

### Phase 3: Validation (LSP + CLI)

> **AUTOMATIC**: validation runs on every Write/Edit to `.agent` files — catches mixed tabs/spaces, invalid Service-vs-Employee `default_agent_user` usage, invalid `@utils.transition` metadata, empty-list expression gotchas, bare `run` calls, common variable/reference errors, and now **org-aware Service Agent user checks** against the configured validation org. Fix errors, re-save, repeat until clean.

```bash
# CLI Validation (before deploy):
sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json

# Native CLI pre-publish verification for Service Agents:
sf data query --query "
SELECT Username, IsActive, UserType, Profile.Name
FROM User
WHERE Username = 'myagent_agent@00Dxxxx.ext'
LIMIT 1
" -o TARGET_ORG --json
```

For Service Agents, confirm all four before publish:
- record exists
- `IsActive = true`
- `UserType != AutomatedProcess`
- `Profile.Name = 'Einstein Agent User'`

The write/edit validator now enforces this automatically against the configured validation org (`metadata.validation_org` in this skill, or `AGENTSCRIPT_VALIDATION_ORG` / `SF_TARGET_ORG` env override). Employee Agents are exempt and instead must omit `default_agent_user` entirely.

**Native pre-publish checklist:**
1. `sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json`
2. `sf data query` the exact `default_agent_user` from the `.agent` file
3. `sf agent preview start` / `send` / `end` against the authoring bundle
4. `sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG --json`
5. If publish fails after validate + preview pass, retry with `--skip-retrieve`

### Phase 3.5: Preview Smoke Test Loop (Pre-Publish)

> **When**: After Phase 3 validation passes, before Phase 5 publish.
> **Prerequisite**: Agent must be published at least once (authoring bundle exists in org).

Run 3-5 smoke test utterances via `sf agent preview start --authoring-bundle AgentName` to catch topic routing and action invocation issues **without publishing**. ~15s iteration cycles.

> ⛔ **NEVER run bare `sf agent preview`** — it is interactive and requires terminal input. ALWAYS use `sf agent preview start`/`send`/`end` subcommands with `--json`.

**How it works:**
1. **Derive utterances** — One per non-start topic (from `description:` keywords), one per key action, one off-topic (guardrail test), one multi-turn pair if agent has transitions
2. **Run preview** — `sf agent preview start --authoring-bundle` → `send` each utterance → `end` session → get traces
3. **Analyze traces** — Read trace JSON with `jq`, checking 6 things:
   - Topic routing (`TransitionStep.data.to` matches expected topic)
   - Action invocation (`FunctionStep.data.function` matches expected action)
   - Grounding (`ReasoningStep.data.groundingAssessment` != `"UNGROUNDED"`)
   - Safety (`PlannerResponseStep.data.safetyScore.overall` >= 0.9)
   - Tool visibility (`EnabledToolsStep.data.enabled_tools` includes expected actions)
   - Response quality (`PlannerResponseStep.data.responseText` is relevant)
4. **Fix loop** — If issues found → apply specific `.agent` edits → LSP auto-validates → re-run preview. **Max 3 iterations.**
5. **Decision** — All pass → Phase 5 (publish). Still failing after 3 → Phase 5 with warnings in commit message.

> 📋 **Full reference**: See [references/preview-test-loop.md](references/preview-test-loop.md) for the complete workflow, `jq` recipes, failure categories, fix strategies, and a walkthrough example.

### Phase 4: Testing (Delegate to `/sf-ai-agentforce-testing`)
Batch testing (up to 100 cases), quality metrics (Completeness, Coherence, Topic/Action Assertions), LLM-as-Judge scoring. If Phase 3.5 smoke tests passed, basic topic routing and action invocation are pre-validated. Formal testing adds multi-turn, re-matching, context preservation, and edge case coverage.

### Phase 5: Deployment & Activation

> ⚠️ **CRITICAL**: Use `sf agent publish authoring-bundle`, NOT `sf project deploy start`

1. **Create bundle directory**: `force-app/main/default/aiAuthoringBundles/AgentName/`
2. **Add files**: `AgentName.agent` + `AgentName.bundle-meta.xml` (NOT `.aiAuthoringBundle-meta.xml`)
3. **Publish**: `sf agent publish authoring-bundle --api-name AgentName -o TARGET_ORG --json`
   - If plain publish fails **after** `validate` and `preview` pass, retry with:
     `sf agent publish authoring-bundle --api-name AgentName -o TARGET_ORG --skip-retrieve --json`
   - In org-backed testing, this isolates a common CLI failure where publish succeeds but the retrieve-back phase fails.
4. **Activate**: `sf agent activate --api-name AgentName -o TARGET_ORG` _(no `--json` support)_

> ⚠️ **Publishing does NOT activate.** After `sf agent publish`, the new BotVersion is `Inactive`. Tests and preview run against the previous active version. You MUST run `sf agent activate` separately.
>
> ⚠️ **Validate ≠ publish safety**. A Service Agent can pass `sf agent validate` and still fail publish if `default_agent_user` is not a real **Einstein Agent User**. Before publishing, run the native `sf data query` check above.

**Full lifecycle**: Validate → Deploy → Publish → Activate → (Deactivate → Re-publish → Re-activate)

> **Preview modes**: Before activating, test with `sf agent preview`. Default mode simulates actions; add `--use-live-actions` to test with real org data. Use `--apex-debug` for Apex logging and `--output-dir` to save transcripts. See [references/cli-guide.md](references/cli-guide.md) for details.

### Phase 5.5: CustomerWebClient Surface Enablement

> ⚠️ **Without `CustomerWebClient` surface, Agent Builder Preview shows "Something went wrong" and Agent Runtime API returns 500.** See [references/customer-web-client.md](references/customer-web-client.md) for the required 6-step post-publish patch workflow.

### Phase 6: CLI Operations

> See [references/cli-guide.md](references/cli-guide.md) for retrieve, validate, publish, and generate commands. Always use `--json` to suppress spinner output.

### Bundle Structure
```
force-app/main/default/aiAuthoringBundles/MyAgent/
├── MyAgent.agent            # Agent Script file
└── MyAgent.bundle-meta.xml  # NOT .aiAuthoringBundle-meta.xml!
```
The `bundle-meta.xml` contains only: `<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata"><bundleType>AGENT</bundleType></AiAuthoringBundle>`

---

## 📊 SCORING SYSTEM (100 Points)

> See [references/scoring-rubric.md](references/scoring-rubric.md) for the full 6-category breakdown, rubric details, and score report format.

**Quick summary:** Structure & Syntax (20), Deterministic Logic (25), Instruction Resolution (20), FSM Architecture (15), Action Configuration (10), Deployment Readiness (10). Score 90+ = deploy with confidence. Score <60 = BLOCK.

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

> See [references/architecture-patterns.md](references/architecture-patterns.md) for Hub-and-Spoke, Verification Gate, and Post-Action Loop patterns with diagrams and code examples.

**Post-Action Loop** (most important): Topic re-resolves after action completes — put checks at TOP of `instructions: ->`.

---

## 🐛 DEBUGGING & COMMON ISSUES

> See [references/debugging-guide.md](references/debugging-guide.md) for the 6 span types (topic_enter, before_reasoning, reasoning, action_call, transition, after_reasoning), trace analysis workflow, forensic debugging patterns, and **programmatic trace access via `sf agent preview` CLI**.
>
> See [references/instruction-resolution.md](references/instruction-resolution.md) § "What the LLM Actually Receives" for the 4-message prompt structure, compilation output verification, and how DSL compiles into system prompts + tool definitions.

### Common Issues Quick Reference

| Issue | Symptom | Fix |
|-------|---------|-----|
| `Internal Error, try again later` | Often invalid `default_agent_user` for Service Agent publish | Verify the user is active, not `AutomatedProcess`, and has Profile.Name = `Einstein Agent User` |
| Plain publish fails, `--skip-retrieve` works | CLI retrieve-back phase failure after successful publish | Re-run `sf agent publish authoring-bundle ... --skip-retrieve --json` |
| `No .agent file found in directory` | `agent_name` doesn't match folder | Make `developer_name` identical to folder name |
| `SyntaxError: cannot mix spaces and tabs` | Mixed indentation | Use consistent spacing throughout |
| `SyntaxError: Unexpected 'if'` | Nested if statements | Use compound `if A and B:` or flatten |
| `SyntaxError: Unexpected 'actions'` | Top-level actions block | Move inside `topic.reasoning.actions:` |
| `SyntaxError: Unexpected 'inputs'` | `inputs:` in Level 2 invocation | Use `with param=value` in invocations |
| `ValidationError: Tool target 'X'...` | Action not defined or target missing | Ensure Level 1 definition + valid target |
| `Required fields missing: [BundleType]` | Wrong deploy command | Use `sf agent publish authoring-bundle` |
| `Cannot find a bundle-meta.xml file` | Wrong file naming | Use `AgentName.bundle-meta.xml` |
| `INVALID_TYPE: GenAiPlannerBundle` | SOQL query on metadata type | Use `sf project retrieve start --metadata` — NOT an sObject |
| `No such column 'Status' on BotDefinition` | Wrong sObject | `Status` is on `BotVersion`, not `BotDefinition` |
| `sf agent preview` hangs | Ran interactive mode | Use subcommands `start`/`send`/`end` with `--json` |
| Linked variables empty in preview | Context vars not injected | `sf agent preview` can't inject `@context`/`@session` — use Runtime API |
| `@context.*` fails in Service Agent | "Unsupported data type" at runtime | `@context` is Employee Agent only (LEX pages). Use `@MessagingSession.*` for Service Agents (Issue 39) |
| `is_required` not enforced by planner | Action invoked with empty required inputs | Use `available when @variables.X is not None` guard instead (Issue 26) |
| `date` type fails in action I/O | Runtime error `'Date'` | Use `object` + `complex_data_type_name: "lightning__dateType"` (Issue 28) |

> **Full issue catalog**: See [references/known-issues.md](references/known-issues.md) for 39 platform bugs and workarounds.

### Verification Protocol

When something fails, fetch the relevant canonical URL from [references/official-sources.md](references/official-sources.md) and verify. See the diagnostic decision tree mapping 6 error categories to specific doc pages.

### Self-Improvement

This skill's resource files are editable. When you discover errors, new patterns, or platform bugs during a session — fix them in place. See [references/known-issues.md](references/known-issues.md) for the issue template.

---

### Deployment Gotchas (Validated by Testing)

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| `AgentName.aiAuthoringBundle-meta.xml` | `AgentName.bundle-meta.xml` |
| `sf project deploy start` | `sf agent publish authoring-bundle` |
| `sf agent validate --source-dir` | `sf agent validate authoring-bundle --api-name AgentName` |
| Query user from wrong org | Query **target org** specifically with `-o` flag |

### Einstein Agent User & Permission Setup (Service Agents Only)

Formats vary: `username@orgid.ext` (production) or `username.suffix@orgfarm.salesforce.com` (dev). **MANDATORY: Ask user to confirm which Einstein Agent User when creating a new agent.**

```bash
sf data query -q "SELECT Username FROM User WHERE Profile.Name = 'Einstein Agent User' AND IsActive = true" -o YOUR_TARGET_ORG --json
```

> **Auto-generated PS warning**: Salesforce creates `NextGen_{AgentName}_Permissions` on publish, but it is often incomplete (missing Apex classes). Always create a custom `{AgentName}_Access` PS. See [references/agent-user-setup.md](references/agent-user-setup.md) for the full 6-step provisioning workflow, permission set XML template, and verification checklist.

---

## 📚 DOCUMENT MAP (Progressive Disclosure)

### Tier 1: Reference Guides (Extracted from this skill)
| Need | Document | Description |
|------|----------|-------------|
| Agent user setup | [references/agent-user-setup.md](references/agent-user-setup.md) | Einstein Agent User provisioning, permission model, service vs employee |
| Production gotchas | [references/production-gotchas.md](references/production-gotchas.md) | Credits, lifecycle hooks, supervision, I/O metadata, latch pattern, limits |
| Feature validity | [references/feature-validity.md](references/feature-validity.md) | Property validity by context |
| Data type mapping | [references/complex-data-types.md](references/complex-data-types.md) | `complex_data_type_name` + Lightning type mapping |
| CustomerWebClient | [references/customer-web-client.md](references/customer-web-client.md) | Post-publish 6-step patch workflow |
| Scoring rubric | [references/scoring-rubric.md](references/scoring-rubric.md) | 100-point scoring system details |
| Architecture patterns | [references/architecture-patterns.md](references/architecture-patterns.md) | Hub-and-spoke, verification gate, post-action loop |
| Sources | [references/sources.md](references/sources.md) | Source attributions & acknowledgments |
| Version history | [references/version-history.md](references/version-history.md) | Changelog from v1.0.0 to current |

### Tier 2: Resource Guides (Comprehensive)
| Need | Document | Description |
|------|----------|-------------|
| Syntax reference | [references/syntax-reference.md](references/syntax-reference.md) | Complete block & expression syntax |
| FSM design | [references/fsm-architecture.md](references/fsm-architecture.md) | State machine patterns & examples |
| Instruction resolution | [references/instruction-resolution.md](references/instruction-resolution.md) | Three-phase execution model |
| Data & multi-agent | [references/grounding-multiagent.md](references/grounding-multiagent.md) | Retriever actions & SOMA patterns |
| Debugging | [references/debugging-guide.md](references/debugging-guide.md) | Trace analysis & forensics |
| Metadata lifecycle | [references/metadata-lifecycle.md](references/metadata-lifecycle.md) | Agent versioning, cleanup & deletion patterns |
| Preview test loop | [references/preview-test-loop.md](references/preview-test-loop.md) | Smoke test loop before publish |
| Testing | [references/testing-guide.md](references/testing-guide.md) | Batch testing & quality metrics |
| Prompt template actions | [references/action-prompt-templates.md](references/action-prompt-templates.md) | `generatePromptResponse://` binding, grounded data |
| Advanced action patterns | [references/action-patterns.md](references/action-patterns.md) | Context-aware descriptions, `{!@actions.X}` refs |
| Actions reference | [references/actions-reference.md](references/actions-reference.md) | Complete action types, GenAiFunction, I/O matching |
| Official sources | [references/official-sources.md](references/official-sources.md) | Canonical SF docs + diagnostic decision tree |
| Known issues | [references/known-issues.md](references/known-issues.md) | Platform bugs & workarounds |
| Migration guide | [references/migration-guide.md](references/migration-guide.md) | Builder UI → Agent Script DSL mapping |

### Tier 3: Quick References (Docs)
| Need | Document | Description |
|------|----------|-------------|
| CLI commands | [references/cli-guide.md](references/cli-guide.md) | sf project retrieve/agent validate/deploy |
| Minimal examples | [references/minimal-examples.md](references/minimal-examples.md) | Hello-world agent script |
| Patterns | [references/patterns-quick-ref.md](references/patterns-quick-ref.md) | Decision tree for pattern selection |

### Tier 4: Templates
| Category | Directory | Contents |
|----------|-----------|----------|
| Root templates | [assets/](assets/) | 7 .agent templates (minimal-starter, hub-and-spoke, etc.) |
| Complete agents | [assets/agents/](assets/agents/) | 5 full agent examples (4 Service + 1 Employee) |
| Components | [assets/components/](assets/components/) | 6 component fragments |
| Advanced patterns | [assets/patterns/](assets/patterns/) | 11 pattern templates |
| Metadata XML | [assets/metadata/](assets/metadata/) | 6 XML templates |
| Apex | [assets/apex/](assets/apex/) | Models API queueable class |

---

## 🔗 CROSS-SKILL INTEGRATION

### MANDATORY Delegations
| Task | Delegate To | Reason |
|------|-------------|--------|
| Create Flows for `flow://` targets | `/sf-flow` | Flows must exist before agent uses them |
| Test agent routing & actions | `/sf-ai-agentforce-testing` | Specialized testing patterns |
| Deploy agent to org | `/sf-deploy` | Proper deployment validation |
| Smoke test (pre-publish) | **Internal** (Phase 3.5) | `sf agent preview --authoring-bundle` — no cross-skill delegation |

### Integration Patterns
| From | To | Pattern |
|------|-----|---------|
| `/sf-ai-agentscript` | `/sf-flow` | Create Flow, then reference in agent |
| `/sf-ai-agentscript` | `/sf-apex` | Create Apex class with `@InvocableMethod`, then use `apex://ClassName` target directly (NO GenAiFunction needed) |
| `/sf-ai-agentscript` | `/sf-integration` | Set up Named Credentials for `externalService://` |

---

## ✅ DEPLOYMENT CHECKLIST

> **Deployment Checklist**: Validate → Deploy → Publish → Activate. Each step has specific CLI commands and required flags.
> See [references/cli-guide.md](references/cli-guide.md) for the full deployment workflow with examples.

---

## 🚀 MINIMAL WORKING EXAMPLE

> **Minimal Working Example**: See [references/minimal-examples.md](references/minimal-examples.md) for a complete hello-world agent script with explanatory comments.

---

## 📖 OFFICIAL RESOURCES

- [Agent Script Documentation](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-script.html) — Primary reference
- [Agent Script Recipes](https://github.com/trailheadapps/agent-script-recipes) — Official examples
- [Agentforce DX Guide](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx.html) — Platform architecture and authoring workflow

**Full Registry:** See [references/official-sources.md](references/official-sources.md) for 14 primary doc URLs, 8 recipe URLs, diagnostic decision tree, and fallback search patterns.

---

## 📚 SOURCES & VERSION HISTORY

> See [references/sources.md](references/sources.md) for full source attributions (trailheadapps/agent-script-recipes, @kunello PR #20, aquivalabs/my-org-butler, and more).

> See [references/version-history.md](references/version-history.md) for the complete changelog from v1.0.0 through v2.7.0.
