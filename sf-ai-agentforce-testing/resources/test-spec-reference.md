# Test Spec Reference

Complete reference for the Agentforce agent test specification YAML format used by `sf agent test create`.

## Overview

Test specifications define automated test cases for Agentforce agents. The YAML is parsed by the `@salesforce/agents` CLI plugin, which converts it to `AiEvaluationDefinition` metadata and deploys it to the org.

**Related Documentation:**
- [SKILL.md](../SKILL.md) - Main skill documentation
- [docs/test-spec-guide.md](../docs/test-spec-guide.md) - Comprehensive test spec guide
- [docs/topic-name-resolution.md](../docs/topic-name-resolution.md) - Topic name format rules

---

## YAML Schema

### Required Structure

```yaml
# Required: Display name for the test (MasterLabel)
# Deploy FAILS with "Required fields are missing: [MasterLabel]" if omitted
name: "My Agent Tests"

# Required: Must be AGENT
subjectType: AGENT

# Required: Agent BotDefinition DeveloperName (API name)
subjectName: My_Agent_Name

testCases:
  - utterance: "User message"
    expectedTopic: topic_name
    expectedActions:
      - action_name
    expectedOutcome: "Expected behavior description"
```

> **Do NOT add** `apiVersion`, `kind`, `metadata`, or `settings` — these are not recognized by the CLI parser.

### Top-Level Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | **Yes** | string | Display name (MasterLabel). Deploy fails without this. |
| `subjectType` | **Yes** | string | Must be `AGENT` |
| `subjectName` | **Yes** | string | Agent BotDefinition DeveloperName |
| `testCases` | **Yes** | array | List of test case objects |

### Test Case Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `utterance` | **Yes** | string | User input message to test |
| `expectedTopic` | No | string | Expected topic name (see [topic name resolution](#topic-name-resolution)) |
| `expectedActions` | No | string[] | Flat list of expected action name strings |
| `expectedOutcome` | No | string | Natural language description of expected response |
| `contextVariables` | No | array | Session context variables to inject |
| `conversationHistory` | No | array | Prior conversation turns for multi-turn tests |

### Context Variable Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Variable name (e.g., `$Context.RoutableId`) |
| `value` | Yes | string | Variable value |

### Conversation History Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `role` | Yes | string | `user` or `agent` (NOT `assistant`) |
| `message` | Yes | string | Message content |
| `topic` | Agent only | string | Topic name for agent turns |

---

## Test Categories

### 1. Topic Routing Tests

Verify the agent selects the correct topic based on user input.

```yaml
testCases:
  - utterance: "Where is my order?"
    expectedTopic: order_lookup

  - utterance: "I have a question about my bill"
    expectedTopic: billing_inquiry

  - utterance: "What are your business hours?"
    expectedTopic: faq
```

**Best Practice:** Test multiple phrasings per topic (minimum 3):

```yaml
testCases:
  - utterance: "Where is my order?"
    expectedTopic: order_lookup

  - utterance: "Track my package"
    expectedTopic: order_lookup

  - utterance: "When will my stuff arrive?"
    expectedTopic: order_lookup
```

### 2. Action Invocation Tests

Verify actions are called. `expectedActions` is a **flat list of strings**, NOT objects.

```yaml
testCases:
  # Single action
  - utterance: "What's the status of order 12345?"
    expectedTopic: order_lookup
    expectedActions:
      - get_order_status

  # Multiple actions
  - utterance: "Look up my order and create a case"
    expectedTopic: order_lookup
    expectedActions:
      - get_order_status
      - create_support_case
```

**Superset matching:** The CLI passes if the agent invokes *at least* the expected actions. Extra actions don't cause failure.

### 3. Outcome Validation Tests

Verify agent response content via LLM-as-judge evaluation.

```yaml
testCases:
  - utterance: "How do I return an item?"
    expectedTopic: returns
    expectedOutcome: "Agent should explain the return process with step-by-step instructions"
```

### 4. Escalation Tests

Test routing to the standard `Escalation` topic.

```yaml
testCases:
  - utterance: "I need to speak to a manager"
    expectedTopic: Escalation

  - utterance: "Transfer me to a human agent"
    expectedTopic: Escalation
```

### 5. Multi-Turn Tests

Use `conversationHistory` to provide prior turns.

```yaml
testCases:
  - utterance: "Can you create a case for this?"
    expectedTopic: support_case
    expectedActions:
      - create_support_case
    conversationHistory:
      - role: user
        message: "My product arrived damaged"
      - role: agent
        topic: support_case
        message: "I'm sorry to hear that. Would you like me to create a support case?"
```

---

## Topic Name Resolution

The `expectedTopic` format depends on the topic type:

| Topic Type | Use | Example |
|------------|-----|---------|
| **Standard** (Escalation, Off_Topic, etc.) | `localDeveloperName` | `Escalation` |
| **Promoted** (p_16j... prefix) | Full runtime `developerName` with hash | `p_16jPl000000GwEX_Topic_16j8eeef13560aa` |

**Standard topics** resolve automatically — the CLI framework maps `Escalation` to the full hash-suffixed runtime name.

**Promoted topics** require the exact runtime `developerName`. The `localDeveloperName` does NOT resolve.

**Discovery workflow:**
1. Run a test with your best guess
2. Check results: `jq '.result.testCases[].generatedData.topic'`
3. Update spec with actual runtime names

See [topic-name-resolution.md](../docs/topic-name-resolution.md) for the complete guide.

---

## CLI Assertions

The CLI evaluates three assertions per test case:

| Assertion | Field | Logic |
|-----------|-------|-------|
| `topic_assertion` | `expectedTopic` | Exact match (with resolution for standard topics) |
| `actions_assertion` | `expectedActions` | Superset — passes if actual contains all expected |
| `output_validation` | `expectedOutcome` | LLM-as-judge semantic evaluation |

### Result JSON Structure

```json
{
  "result": {
    "runId": "4KBbb...",
    "testCases": [
      {
        "testNumber": 1,
        "inputs": {
          "utterance": "Where is my order?"
        },
        "generatedData": {
          "topic": "p_16jPl000000GwEX_Order_Lookup_16j8eeef13560aa",
          "actionsSequence": "['get_order_status']",
          "outcome": "I can help you track your order...",
          "sessionId": "uuid-string"
        },
        "testResults": [
          {
            "name": "topic_assertion",
            "expectedValue": "order_lookup",
            "actualValue": "p_16jPl000000GwEX_Order_Lookup_16j8eeef13560aa",
            "result": "PASS",
            "score": 1
          },
          {
            "name": "actions_assertion",
            "expectedValue": "['get_order_status']",
            "actualValue": "['get_order_status', 'summarize_record']",
            "result": "PASS",
            "score": 1
          },
          {
            "name": "output_validation",
            "expectedValue": "",
            "actualValue": "I can help you track your order...",
            "result": "FAILURE",
            "errorMessage": "Skip metric result due to missing expected input"
          }
        ]
      }
    ]
  }
}
```

> Note: `output_validation` shows `FAILURE` when `expectedOutcome` is omitted — this is **harmless**.

---

## Test Spec Templates

| Template | Purpose | CLI Compatible |
|----------|---------|----------------|
| `standard-test-spec.yaml` | Reference format with all field types | **Yes** |
| `basic-test-spec.yaml` | Quick start (5 tests) | **Yes** |
| `comprehensive-test-spec.yaml` | Full coverage (20+ tests) | **Yes** |
| `escalation-tests.yaml` | Escalation scenarios | **No** — Phase A (API) only |
| `guardrail-tests.yaml` | Guardrail scenarios | **No** — Phase A (API) only |
| `multi-turn-*.yaml` | Multi-turn API scenarios | **No** — Phase A (API) only |

---

## Test Generation

### Automated (Python Script)

```bash
python3 hooks/scripts/generate-test-spec.py \
  --agent-file /path/to/Agent.agent \
  --output tests/agent-spec.yaml \
  --verbose
```

### Interactive (CLI)

```bash
# Interactive wizard — no batch/scripted mode available
sf agent generate test-spec --output-file ./tests/agent-spec.yaml
```

### Deploy and Run

```bash
# Deploy spec to org
sf agent test create --spec ./tests/agent-spec.yaml --api-name My_Agent_Tests --target-org dev

# Run tests
sf agent test run --api-name My_Agent_Tests --wait 10 --result-format json --json --target-org dev

# Get results (ALWAYS use --job-id, NOT --use-most-recent)
sf agent test results --job-id <JOB_ID> --result-format json --json --target-org dev
```

---

## Known Gotchas

| Gotcha | Detail |
|--------|--------|
| `name:` is mandatory | Deploy fails with "Required fields are missing: [MasterLabel]" |
| `expectedActions` is flat strings | `- action_name` NOT `- name: action_name, invoked: true` |
| Empty `expectedActions: []` | Means "not testing" — passes even when actions are invoked |
| Missing `expectedOutcome` | `output_validation` reports ERROR — this is harmless |
| `--use-most-recent` broken | Always use `--job-id` for `sf agent test results` |
| No MessagingSession context | CLI tests have no session — flows needing `recordId` error at runtime |
| Promoted topic names | Must use full runtime `developerName` with hash suffix |
| YAML→XML field mapping | `expectedTopic` → `topic_sequence_match`, `expectedActions` → `action_sequence_match` |

---

## Related Resources

- [SKILL.md](../SKILL.md) - Main skill documentation
- [docs/test-spec-guide.md](../docs/test-spec-guide.md) - Detailed test spec guide
- [docs/topic-name-resolution.md](../docs/topic-name-resolution.md) - Topic name format rules
- [docs/cli-commands.md](../docs/cli-commands.md) - Complete CLI reference
- [resources/agentic-fix-loops.md](./agentic-fix-loops.md) - Auto-fix workflow
- [docs/coverage-analysis.md](../docs/coverage-analysis.md) - Coverage metrics
