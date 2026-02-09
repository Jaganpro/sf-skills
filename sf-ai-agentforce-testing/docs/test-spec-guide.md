# Test Specification Guide

Complete reference for creating YAML test specifications for Agentforce agents using `sf agent test create`.

---

## Overview

Test specifications define expected agent behavior using YAML format. When you run `sf agent test create`, the `@salesforce/agents` CLI plugin parses the YAML and deploys `AiEvaluationDefinition` metadata to the org.

> **Important:** The YAML format is defined by the `@salesforce/agents` TypeScript source — NOT a generic `AiEvaluationDefinition` XML format. Only the fields documented below are recognized.

---

## File Structure

```yaml
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

```yaml
# These are equivalent — both mean "not testing actions":
- utterance: "Hello"
  expectedTopic: greeting
  expectedActions: []

- utterance: "Hello"
  expectedTopic: greeting
  # (expectedActions omitted entirely)
```

Both pass even if the agent invokes actions.

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

---

## Context Variables

Inject session context variables for testing.

```yaml
testCases:
  - utterance: "What's the status of my account?"
    expectedTopic: account_lookup
    contextVariables:
      - name: "$Context.RoutableId"
        value: "0Mw8X000000XXXXX"
      - name: "$Context.CaseId"
        value: "5008X000000XXXXX"
```

> **Important:** Agents with authentication flows (e.g., `User_Authentication` topic) typically require `$Context.RoutableId` and `$Context.CaseId`. Without them, the authentication flow fails and the agent escalates on Turn 1.

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

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Required fields are missing: [MasterLabel]" | Missing `name:` field | Add `name:` to top of YAML |
| Topic assertion fails | Wrong topic name format | See [topic-name-resolution.md](topic-name-resolution.md) |
| Action assertion unexpected PASS | Superset matching | Expected is subset of actual — this is correct behavior |
| `output_validation` shows ERROR | No `expectedOutcome` provided | Add `expectedOutcome` or ignore — harmless |
| "Agent not found" | Wrong `subjectName` | Verify agent DeveloperName in org |
