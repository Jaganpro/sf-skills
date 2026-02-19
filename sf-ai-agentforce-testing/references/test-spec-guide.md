<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->
# Test Specification Guide

Complete reference for creating YAML test specifications for Agentforce agents using `sf agent test create`.

---

## Overview

Test specifications define expected agent behavior using YAML format. When you run `sf agent test create`, the `@salesforce/agents` CLI plugin parses the YAML and deploys `AiEvaluationDefinition` metadata to the org.

> **Important:** The YAML format is defined by the `@salesforce/agents` TypeScript source — NOT a generic `AiEvaluationDefinition` XML format. Only the fields documented below are recognized.

---

## File Structure

```yaml
# Description: [Brief description of what this test suite validates]

# Required: Display name (becomes MasterLabel in metadata)
name: "My Agent Tests"

# Required: Must be AGENT
subjectType: AGENT

# Required: Agent BotDefinition DeveloperName (API name)
subjectName: My_Agent_Name

testCases:
  - utterance: "User message to test"
    expectedTopic: topic_name
    expectedActions:
      - action_name
    expectedOutcome: "Natural language description of expected response"
```

### Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name for the test (MasterLabel). **Deploy FAILS without this.** |
| `subjectType` | string | Must be `AGENT` |
| `subjectName` | string | Agent BotDefinition DeveloperName (API name) |
| `testCases` | array | List of test case objects |

> **Do NOT add** `apiVersion`, `kind`, `metadata`, or `settings` — these are not part of the CLI YAML schema and will be silently ignored or cause errors.

---

## Test Case Fields

Each test case supports these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `utterance` | string | **Yes** | User input message to test |
| `expectedTopic` | string | No | Expected topic the agent should route to |
| `expectedActions` | string[] | No | Flat list of action name strings expected to be invoked |
| `expectedOutcome` | string | No | Natural language description of expected agent response |
| `contextVariables` | array | No | Variables to inject into the test session |
| `conversationHistory` | array | No | Prior conversation turns for multi-turn context |

### What the CLI Actually Validates

The CLI runs three assertions per test case:

| Assertion | Based On | Behavior |
|-----------|----------|----------|
| `topic_assertion` | `expectedTopic` | Exact match against runtime topic `developerName` |
| `actions_assertion` | `expectedActions` | **Superset matching** — passes if agent invoked at least the expected actions |
| `output_validation` | `expectedOutcome` | LLM-as-judge evaluates if agent response satisfies the description |

---

## Topic Routing Tests

Verify the agent routes to the correct topic.

```yaml
testCases:
  - utterance: "Where is my order?"
    expectedTopic: order_lookup

  - utterance: "What are your business hours?"
    expectedTopic: faq

  - utterance: "I have a problem with my product"
    expectedTopic: support_case
```

### Topic Name Resolution

The `expectedTopic` value depends on the topic type:

| Topic Type | Format | Example |
|------------|--------|---------|
| Standard (Escalation, Off_Topic) | `localDeveloperName` | `Escalation` |
| Promoted (p_16j... prefix) | Full runtime `developerName` with hash | `p_16jPl000000GwEX_Topic_16j8eeef13560aa` |

See [topic-name-resolution.md](topic-name-resolution.md) for the complete guide, including the discovery workflow for promoted topics.

### Multiple Phrasings

Test the same topic with different phrasings to ensure robust routing:

```yaml
testCases:
  - utterance: "Where is my order?"
    expectedTopic: order_lookup

  - utterance: "Track my package"
    expectedTopic: order_lookup

  - utterance: "When will my stuff arrive?"
    expectedTopic: order_lookup
```

---

## Action Invocation Tests

Verify actions are invoked. `expectedActions` is a **flat list of action name strings**.

### Basic Action Test

```yaml
testCases:
  - utterance: "What's the status of order 12345?"
    expectedTopic: order_lookup
    expectedActions:
      - get_order_status
```

### Multiple Actions

```yaml
testCases:
  - utterance: "Look up my order and create a case for it"
    expectedTopic: order_lookup
    expectedActions:
      - get_order_status
      - create_support_case
```

### Superset Matching

Action assertions use **superset matching**:
- Expected: `[get_order_status]` / Actual: `[get_order_status, summarize_record]` → **PASS**
- The agent can invoke additional actions beyond what's expected and the test still passes.

### Empty Actions

| Pattern | Meaning | Current Behavior |
|---------|---------|------------------|
| `expectedActions:` omitted | "Not testing actions" | PASS regardless of what fires |
| `expectedActions: []` | "Testing that NO actions fire" | Currently same behavior (PASS regardless), but documents intent |

**Best practice:** Use `expectedActions: []` explicitly for opt-out tests to document your intent that no action should fire, even though the CLI currently treats it the same as omitted. This makes the test self-documenting and future-proofs against framework changes.

```yaml
# Omitted — "I'm not testing actions for this test case"
- utterance: "Hello"
  expectedTopic: greeting
  # (expectedActions omitted entirely)

# Empty list — DELIBERATE assertion: "NO action should fire"
- utterance: "No thanks, I'm all set"
  expectedTopic: feedback_collection
  expectedActions: []    # Documents intent: opt-out should NOT trigger feedback action
  expectedOutcome: "Agent gracefully accepts the opt-out without pushing for feedback"
```

### Action Name Discovery for GenAiPlannerBundle Agents

For GenAiPlannerBundle agents, action names in test results include a hash suffix (e.g., `Store_Feedback_179a9701f17c194`). Short name **prefix matching** works — you can use the prefix in `expectedActions` and the CLI will match.

**Discovery workflow:**
```bash
# Run with --verbose to see full action names
sf agent test run --api-name Discovery --wait 10 --verbose --result-format json --json --target-org [alias]

# Extract action names from results
jq '.result.testCases[].generatedData | {topic, actionsSequence}' results.json

# For detailed action input/output inspection
jq '.result.testCases[].generatedData.invokedActions | fromjson | .[0][0].function' results.json
```

> **Note:** The multi-turn API may report `has_action_result: false` for actions that actually fired. CLI `--verbose` output is authoritative for action verification.

---

## Outcome Validation Tests

Verify the agent's response content using natural language descriptions.

```yaml
testCases:
  - utterance: "What are your business hours?"
    expectedTopic: faq
    expectedOutcome: "Agent should provide specific business hours including days and times"

  - utterance: "How do I return an item?"
    expectedTopic: returns
    expectedOutcome: "Agent should explain the return process with step-by-step instructions"
```

The CLI uses an LLM-as-judge to evaluate whether the agent's actual response satisfies the `expectedOutcome` description.

> **Gotcha:** Omitting `expectedOutcome` causes `output_validation` to report `ERROR` status with "Skip metric result due to missing expected input". This is **harmless** — `topic_assertion` and `actions_assertion` still run normally.

> **Important: `output_validation` judges TEXT, not actions.** The LLM-as-judge evaluates the agent's **text response** only — it does NOT inspect action results, sObject writes, or internal state changes. Write `expectedOutcome` about what the agent *says*, not what it *does* internally.
>
> ```yaml
> # ❌ WRONG — references internal action behavior
> expectedOutcome: "Agent should create a Survey_Result__c record with rating=4"
>
> # ❌ WRONG — references sObject changes
> expectedOutcome: "Agent should update the MessagingSession.Bot_Support_Path__c field"
>
> # ✅ RIGHT — describes what the agent SAYS
> expectedOutcome: "Agent acknowledges the rating and thanks the user for feedback"
>
> # ✅ RIGHT — describes observable text behavior
> expectedOutcome: "Agent confirms the payment is being processed and provides next steps"
> ```

---

## Multi-Turn Conversation Tests

Provide conversation history to test context retention.

```yaml
testCases:
  - utterance: "When will it arrive?"
    expectedTopic: order_lookup
    conversationHistory:
      - role: user
        message: "I want to check on order 12345"
      - role: agent
        topic: order_lookup
        message: "I'd be happy to help you check on order 12345. Let me look that up."

  - utterance: "Yes, please create one"
    expectedTopic: support_case
    expectedActions:
      - create_support_case
    conversationHistory:
      - role: user
        message: "My product is broken"
      - role: agent
        topic: support_case
        message: "I'm sorry to hear that. Would you like me to create a support case?"
```

### Conversation History Format

| Field | Required | Description |
|-------|----------|-------------|
| `role` | Yes | `user` or `agent` (NOT `assistant`) |
| `message` | Yes | The message content |
| `topic` | Agent only | Topic name for agent turns |

### Deep Conversation History for Protocol Stage Testing

By providing 4-8 turns of `conversationHistory`, you can position the agent at a specific point in a multi-step protocol and test its behavior at that exact stage. The `topic` field on agent turns **anchors the planner** to the correct topic context, making ambiguous utterances (like "thanks" or "I'm done") route deterministically.

```yaml
# Without history: "Thanks for the help" routes stochastically (greeting? escalation? feedback?)
# With history: anchored to feedback_collection after completed business interaction
- utterance: "Thanks for the help"
  expectedTopic: feedback_collection
  conversationHistory:
    - role: user
      message: "I need to check my account status"
    - role: agent
      topic: account_support          # Local developer name — no hash suffix needed
      message: "I found your account. Everything looks good — your balance is current."
    - role: user
      message: "Great, that answers my question"
    - role: agent
      topic: account_support
      message: "Glad I could help! Is there anything else you need?"
```

> **Key detail:** The `topic` field in `conversationHistory` resolves **local developer names** (e.g., `account_support`, `feedback_collection`). You do NOT need the hash-suffixed runtime `developerName` in history — only in `expectedTopic` for promoted topics.

See [Deep Conversation History Patterns](deep-conversation-history-patterns.md) for 5 patterns: protocol activation, mid-protocol stage, action invocation, opt-out assertion, and session persistence.

---

## Context Variables

Inject session context variables for testing.

```yaml
testCases:
  - utterance: "What's the status of my account?"
    expectedTopic: account_lookup
    contextVariables:
      - name: "$Context.RoutableId"    # Prefixed format (recommended) — bare RoutableId also works
        value: "0Mw8X000000XXXXX"
      - name: CaseId
        value: "5008X000000XXXXX"
```

> **Important:** Agents with authentication flows (e.g., `User_Authentication` topic) typically require `RoutableId` and `CaseId` context variables. Without them, the authentication flow fails and the agent escalates on Turn 1. Both prefixed names (`$Context.RoutableId`) and bare names (`RoutableId`) work — the runtime resolves both formats. The `$Context.` prefix is recommended as it matches the Merge Field syntax used in Flow Builder.

---

## Escalation Tests

Standard `Escalation` topic uses `localDeveloperName`:

```yaml
testCases:
  - utterance: "I need to speak to a manager about my billing issue"
    expectedTopic: Escalation

  - utterance: "This is too complicated, I need a human"
    expectedTopic: Escalation
```

---

## Complete Example

```yaml
name: "Customer Support Agent Tests"
subjectType: AGENT
subjectName: Customer_Support_Agent

testCases:
  # ═══ TOPIC ROUTING ═══
  - utterance: "Where is my order?"
    expectedTopic: order_lookup

  - utterance: "Track my package"
    expectedTopic: order_lookup

  - utterance: "What are your business hours?"
    expectedTopic: faq

  - utterance: "I have a problem with my product"
    expectedTopic: support_case

  # ═══ ACTION TESTS ═══
  - utterance: "What's the status of order 12345?"
    expectedTopic: order_lookup
    expectedActions:
      - get_order_status

  - utterance: "Create a support case for my broken item"
    expectedTopic: support_case
    expectedActions:
      - create_support_case

  # ═══ OUTCOME TESTS ═══
  - utterance: "How do I return an item?"
    expectedTopic: returns
    expectedOutcome: "Agent should explain the return process and any time limits"

  # ═══ ESCALATION ═══
  - utterance: "I need to speak with a manager"
    expectedTopic: Escalation

  # ═══ MULTI-TURN ═══
  - utterance: "Can you create a case for this?"
    expectedTopic: support_case
    expectedActions:
      - create_support_case
    conversationHistory:
      - role: user
        message: "My product arrived damaged"
      - role: agent
        topic: support_case
        message: "I'm sorry to hear that. I can help you create a support case."
```

---

## Agent Script Agents (AiAuthoringBundle)

Agent Script agents (`.agent` files) have unique testing requirements due to their two-level action system and `start_agent` routing.

### Key Differences from GenAiPlannerBundle Agents

| Aspect | Agent Script | GenAiPlannerBundle |
|--------|-------------|-------------------|
| Single-utterance test | Captures transition action only | May capture business action |
| Action names in results | Level 1 definition name | GenAiFunction name |
| `subjectName` source | `config.developer_name` in `.agent` | Directory name of bundle |
| Action test approach | Use `conversationHistory` for `apex://` | Standard single-utterance |

### Routing Test (Transition Action)

```yaml
testCases:
  - utterance: "I want to check my order status"
    expectedTopic: order_status
    expectedActions:
      - go_order_status    # Transition action from start_agent
```

### Action Test (with conversationHistory)

```yaml
testCases:
  - utterance: "The order ID is 801ak00001g59JlAAI"
    conversationHistory:
      - role: "user"
        message: "I want to check my order status"
      - role: "agent"
        topic: "order_status"
        message: "Could you provide the Order ID?"
    expectedTopic: order_status
    expectedActions:
      - get_order_status    # Level 1 definition name, NOT check_status
```

### Permission Pre-Check

If the Apex class uses `WITH USER_MODE`, the Einstein Agent User (`default_agent_user` in `.agent` config) must have read permissions on queried objects. Missing permissions cause **silent failures** (0 rows returned, no error).

See [agentscript-testing-patterns.md](agentscript-testing-patterns.md) for 5 detailed test patterns and the permission pre-check workflow.

---

## Best Practices

### Test Coverage

| Aspect | Recommendation |
|--------|----------------|
| Topics | Test every topic with 3+ phrasings |
| Actions | Test every action at least once |
| Escalation | Test trigger and non-trigger scenarios |
| Edge cases | Test typos, gibberish, long inputs |

### Organization

Group test cases by category using comments:

```yaml
testCases:
  # ═══ TOPIC ROUTING ═══
  - utterance: "..."
  - utterance: "..."

  # ═══ ACTION TESTS ═══
  - utterance: "..."
  - utterance: "..."
```

### Ambiguous Routing

When multiple topics are acceptable destinations for an utterance, **omit `expectedTopic`** and use `expectedOutcome` for behavioral validation instead. This prevents false failures from non-deterministic routing.

```yaml
testCases:
  # ❌ FRAGILE — fails if planner picks Off_Topic instead of Escalation
  - utterance: "What is the meaning of life?"
    expectedTopic: Escalation

  # ✅ ROBUST — validates behavior regardless of which topic fires
  - utterance: "What is the meaning of life?"
    expectedOutcome: "Agent deflects gracefully. Does NOT crash. Does NOT attempt to answer."
```

### Auth Gate Verification

For agents with authentication flows, include tests confirming that business-domain requests route to the auth topic first — not to a broad catch-all:

```yaml
testCases:
  - utterance: "I need to check my order status"
    expectedTopic: User_Authentication0

  - utterance: "Can I update my billing information?"
    expectedTopic: User_Authentication0

  - utterance: "I want to return a product"
    expectedTopic: User_Authentication0
```

If any of these route to a non-auth topic (e.g., Escalation), the catch-all topic's description is likely too broad and absorbing business intents.

### Description Convention

Since `AiEvaluationDefinition` metadata has no XML `<description>` element, document each test suite's purpose using a YAML comment at the top of the spec file:

```yaml
# Description: Validates auth-first routing for all greeting patterns
name: "VVS Greeting Auth Tests"
subjectType: AGENT
subjectName: Product_Troubleshooting2
```

This convention helps teams understand the intent of each test suite at a glance.

### Parallel Test Suites

For agents with 20+ test cases, split into category-based YAML specs for parallel execution:

```
tests/
├── agent-routing-tests.yaml      # Topic routing (8 tests)
├── agent-guardrail-tests.yaml    # Guardrails and deflection (10 tests)
├── agent-auth-tests.yaml         # Auth gate verification (5 tests)
└── agent-session-tests.yaml      # Session/context tests (3 tests)
```

Each spec is deployed independently via `sf agent test create`, then executed in parallel via separate `sf agent test run` commands. This reduces total wall-clock time and makes failures easier to categorize.

---

## Known Gotchas

| Issue | Detail |
|-------|--------|
| **`name:` is mandatory** | Deploy fails with "Required fields are missing: [MasterLabel]" if omitted |
| **`expectedActions` is a flat string list** | NOT objects with `name`/`invoked`/`outputs` — those are fabricated fields |
| **Empty `expectedActions: []` means "not testing"** | Will PASS even if actions are invoked |
| **Missing `expectedOutcome` causes harmless ERROR** | `output_validation` reports ERROR but topic/action assertions still work |
| **CLI has NO MessagingSession context** | Flows that need `recordId` will error at runtime (agent handles gracefully) |
| **`--use-most-recent` flag is broken** | Always use `--job-id` explicitly for `sf agent test results` |
| **Promoted topics need full runtime name** | `localDeveloperName` only resolves for standard topics |
| **`instruction_following` crashes Testing Center UI** | `No enum constant AiEvaluationMetricType.INSTRUCTION_FOLLOWING_EVALUATION` — CLI works fine but UI breaks. Remove this metric if users need Testing Center UI access. |
| **Standard platform topics intercept before custom routing** | `Inappropriate_Content`, `Prompt_Injection`, `Reverse_Engineering` fire BEFORE the custom planner. Don't use custom topic names for these guardrail tests. See [topic-name-resolution.md](topic-name-resolution.md#standard-platform-topics-intercept-before-custom-routing). |
| **`coherence` misleading for deflection agents** | Evaluates whether the response "answers" the user's question — scores 2-3 for correct deflections. Use `expectedOutcome` for guardrail/deflection tests instead. |

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Required fields are missing: [MasterLabel]" | Missing `name:` field | Add `name:` to top of YAML |
| Topic assertion fails | Wrong topic name format | See [topic-name-resolution.md](topic-name-resolution.md) |
| Action assertion unexpected PASS | Superset matching | Expected is subset of actual — this is correct behavior |
| `output_validation` shows ERROR | No `expectedOutcome` provided | Add `expectedOutcome` or ignore — harmless |
| "Agent not found" | Wrong `subjectName` | Verify agent DeveloperName in org |
