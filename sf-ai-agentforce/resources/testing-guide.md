# Agent Testing Guide

Comprehensive guide to testing Agentforce agents using preview mode, Agent Testing Center, and automated test generation.

## Table of Contents

- [Testing Overview](#testing-overview)
- [Preview Mode Testing](#preview-mode-testing)
- [Agent Testing Center](#agent-testing-center)
- [Automated Testing Workflow](#automated-testing-workflow)
- [Test Spec Generation](#test-spec-generation)
- [Agentic Fix Loops](#agentic-fix-loops)
- [Coverage Analysis](#coverage-analysis)
- [Best Practices](#best-practices)

---

## Testing Overview

There are **three main approaches** to testing Agentforce agents:

| Approach | Use When | Command | Requires Org |
|----------|----------|---------|--------------|
| **Preview (Simulated)** | Quick syntax/logic testing | `sf agent preview` | Yes |
| **Preview (Live)** | End-to-end testing with real actions | `sf agent preview --use-live-actions` | Yes + Connected App |
| **Agent Testing Center** | Automated regression testing | `sf agent test run` | Yes + Feature Enabled |

---

## Preview Mode Testing

**Agent Preview** provides an interactive CLI chat interface to test your agent.

### Simulated Mode (Default)

**LLM simulates action responses** - safe for testing without executing real Flows/Apex.

```bash
# Preview agent in simulated mode
sf agent preview --api-name My_Agent --target-org MyOrg
```

**What happens:**
- Agent reasoning executes normally
- LLM generates simulated outputs for actions
- No actual Flows/Apex are executed
- Safe for testing logic without side effects

**Best for:**
- Testing topic routing
- Validating reasoning instructions
- Checking conversation flow
- Quick iteration during development

### Live Mode

**Uses actual Apex/Flows in org** - executes real actions with real data.

```bash
# Preview in live mode (requires connected app)
sf agent preview --api-name My_Agent --use-live-actions --client-app MyConnectedApp --target-org MyOrg
```

**Requirements:**
1. **Connected App** must be created in org
2. Agent must be **activated**
3. All Flow/Apex dependencies must be **deployed**

**Best for:**
- End-to-end testing
- Validating actual Flow/Apex execution
- Testing with real org data
- Pre-production verification

### Connected App Setup (for Live Mode)

**Step 1: Create Connected App in Salesforce**

1. Setup → App Manager → New Connected App
2. Enable OAuth Settings
3. Callback URL: `http://localhost:1717/OauthRedirect`
4. Selected OAuth Scopes:
   - `api` - Access the API
   - `refresh_token` - Refresh token
5. Save and note the **Consumer Key**

**Step 2: Use in Preview**

```bash
sf agent preview --api-name My_Agent \
  --use-live-actions \
  --client-app MyConnectedApp \
  --target-org MyOrg
```

### Debug Output

Save conversation logs and debug information:

```bash
# Save debug logs
sf agent preview --api-name My_Agent \
  --output-dir ./logs \
  --apex-debug \
  --target-org MyOrg
```

**Outputs:**
- Conversation transcript
- LLM reasoning steps
- Action execution details
- Apex debug logs (if `--apex-debug`)

---

## Agent Testing Center

**Prerequisite**: Agent Testing Center must be enabled in your org.

### Verify Availability

```bash
# Check if Agent Testing Center is available
sf agent test list --target-org MyOrg
```

If not available, contact Salesforce support to enable the feature.

### Manual Test Creation

**Step 1: Create test spec YAML**

```yaml
# test-spec.yaml
subjectType: AGENT
subjectName: My_Agent
testCases:
  - utterance: "What's on your menu?"
    expectation:
      topic: coffee_faq
      actionSequence: []
  - utterance: "I'd like to order a coffee"
    expectation:
      topic: place_order
      actionSequence: [flow://Create_Order]
```

**Step 2: Create test definition in org**

```bash
sf agent test create --spec ./test-spec.yaml --target-org MyOrg
```

**Step 3: Run tests**

```bash
sf agent test run --api-name My_Agent_Tests --wait 10 --target-org MyOrg
```

### Test Spec Format

```yaml
subjectType: AGENT
subjectName: [AgentAPIName]
testCases:
  - utterance: "[User input]"
    expectation:
      topic: [expected_topic_name]
      actionSequence:
        - [expected_action_1]
        - [expected_action_2]
  - utterance: "[Another user input]"
    expectation:
      topic: [expected_topic_name]
      actionSequence: []
```

**Key Fields:**
- `utterance` - User input to test
- `topic` - Expected topic the agent should route to
- `actionSequence` - Expected actions in order (empty array if no actions)

---

## Automated Testing Workflow

**Use the sf-ai-agentforce-testing skill** for comprehensive automated testing.

### Invoke Testing Skill

```bash
# From Claude Code
Skill(skill="sf-ai-agentforce-testing", args="Test agent My_Agent and fix any failures")
```

**What it provides:**
1. **Test spec generation** from agent metadata
2. **100-point test scoring** across 5 categories
3. **Agentic fix loops** - auto-fix failing tests (max 3 iterations)
4. **Coverage analysis** for topics, actions, guardrails, escalation

### Test Workflow (Automated)

```bash
# 1. Generate test specification
sf agent generate test-spec --api-name My_Agent --output-dir ./tests

# 2. Create test definition in org
sf agent test create --spec ./tests/test-spec.yaml --target-org MyOrg

# 3. Run tests
sf agent test run --api-name My_Agent_Tests --wait 10 --target-org MyOrg

# 4. View results
sf agent test results --api-name My_Agent_Tests --target-org MyOrg
```

---

## Test Spec Generation

### From Agent Definition (.agent file)

The test generator parses `.agent` files to extract:
- **Topics** - Generates routing tests
- **Actions** - Generates action invocation tests
- **Transitions** - Verifies topic routing
- **Edge cases** - Off-topic handling, graceful declines

**Example: Generated test spec**

```yaml
subjectType: AGENT
subjectName: Coffee_Shop_FAQ_Agent
testCases:
  # Topic routing tests
  - utterance: "What drinks do you have?"
    expectation:
      topic: coffee_faq
      actionSequence: []

  # Action invocation tests
  - utterance: "I want to order a cappuccino"
    expectation:
      topic: place_order
      actionSequence:
        - flow://Create_Coffee_Order

  # Edge case tests
  - utterance: "What's the weather today?"
    expectation:
      topic: topic_selector
      actionSequence: []
```

### Agent Script DSL Parsing

**Challenge**: Agent Script uses indentation-based blocks, NOT YAML.

**Solution**: Custom parser handles:
- Indentation-based block detection
- Topic extraction with labels/descriptions
- Action target parsing (`flow://`, `apex://`, etc.)
- Transition detection (`@utils.transition to @topic.x`)

---

## Agentic Fix Loops

**Automated failure remediation** with Claude Code integration.

### How It Works

```
1. Run tests → Some tests fail
       │
       ▼
2. Parse failure details
       │
       ▼
3. Generate fix suggestions
       │
       ▼
4. Apply fixes to agent
       │
       ▼
5. Re-run tests (max 3 iterations)
       │
       ▼
6. Report final results
```

### Fix Strategies

| Failure Type | Fix Strategy |
|--------------|--------------|
| **Wrong topic routing** | Update topic descriptions for better LLM routing |
| **Missing actions** | Add action definitions to topic |
| **Incorrect action sequence** | Adjust reasoning instructions to guide action order |
| **Escalation not triggered** | Add escalation action with proper conditions |

### Example: Auto-Fix Flow

```bash
# Test fails: "Expected topic 'order_lookup' but got 'topic_selector'"

# Fix: Update topic description
# BEFORE:
topic order_lookup:
   label: "Orders"
   description: "Handle orders"

# AFTER (auto-generated fix):
topic order_lookup:
   label: "Order Lookup"
   description: "Look up order status, track shipments, and provide order details when customer asks about their orders"
```

**Then re-run tests automatically.**

---

## Coverage Analysis

### Test Coverage Categories

| Category | What It Tests | Example |
|----------|---------------|---------|
| **Topic Coverage** | All topics reachable? | Test utterances for each topic |
| **Action Coverage** | All actions invoked? | Test scenarios that trigger each action |
| **Transition Coverage** | All transitions tested? | Test routing from start_agent to all topics |
| **Guardrail Coverage** | Edge cases handled? | Test off-topic requests, harmful inputs |
| **Escalation Coverage** | Escalation triggers? | Test scenarios requiring human assistance |

### 100-Point Test Scoring

| Category | Points | Criteria |
|----------|--------|----------|
| **Topic Coverage** | 25 | % of topics with at least 1 test case |
| **Action Coverage** | 25 | % of actions with at least 1 test case |
| **Edge Case Handling** | 20 | Tests for off-topic, errors, escalation |
| **Transition Coverage** | 15 | % of topic transitions tested |
| **Test Quality** | 15 | Assertions completeness, expectation clarity |

**Scoring Thresholds:**

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Production-ready |
| 80-89 | Very Good | Minor gaps acceptable |
| 70-79 | Good | Add more edge case tests |
| 60-69 | Needs Work | Improve coverage |
| <60 | Critical | Block production deployment |

---

## Best Practices

### Test Design Principles

1. **Test each topic** - At least 1 test per topic
2. **Test each action** - Verify all actions can be invoked
3. **Test edge cases** - Off-topic, errors, escalation
4. **Test transitions** - Verify routing works as expected
5. **Test with real utterances** - Use natural language, not keywords

### Test Utterance Best Practices

| Good | Bad | Why |
|------|-----|-----|
| "What's on your coffee menu?" | "menu" | Natural language tests LLM routing |
| "I'd like to order a cappuccino" | "order" | Tests slot filling and action invocation |
| "Can you help me track my order #12345?" | "track order" | Tests with realistic data |

### When to Test

| Phase | Test Type | Purpose |
|-------|-----------|---------|
| **Development** | Preview (Simulated) | Quick iteration |
| **Pre-deployment** | Preview (Live) + Agent Testing Center | End-to-end validation |
| **Post-deployment** | Agent Testing Center | Regression testing |
| **Continuous** | Automated tests | CI/CD integration |

### Test Maintenance

- **Update tests when agent changes** - Add tests for new topics/actions
- **Review failing tests** - Failures may indicate agent issues OR test issues
- **Archive old tests** - Remove tests for deprecated features
- **Version test specs** - Track test changes alongside agent changes

---

## Troubleshooting

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Agent Testing Center not available" | Feature not enabled in org | Contact Salesforce support |
| Tests pass but preview fails | Simulated vs live behavior | Use `--use-live-actions` in preview |
| Action not invoked in tests | LLM routing issue | Update topic/action descriptions |
| Test timeouts | Long-running Flows | Increase `--wait` time |

### Debug Tips

1. **Enable debug logging**: `sf agent preview --apex-debug --output-dir ./logs`
2. **Check topic routing**: Verify LLM routes to expected topic
3. **Verify action conditions**: Check `available when` clauses
4. **Test in isolation**: Test one topic at a time
5. **Compare simulated vs live**: Identify discrepancies

---

## References

For additional information, see:
- **sf-ai-agentforce-testing/SKILL.md** - Complete testing skill documentation
- [../docs/cli-commands.md](../docs/cli-commands.md) - CLI commands reference
- [deployment-guide.md](deployment-guide.md) - Deployment workflow
- [agent-script-reference.md](agent-script-reference.md) - Agent Script syntax

---

## Example: Complete Test Workflow

```bash
# 1. Deploy agent to org
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/My_Agent

# 2. Activate agent
sf agent activate --api-name My_Agent --target-org MyOrg

# 3. Preview in simulated mode (quick check)
sf agent preview --api-name My_Agent --target-org MyOrg

# 4. Generate test spec (if using automated testing)
python3 hooks/scripts/generate-test-spec.py \
  force-app/main/default/aiAuthoringBundles/My_Agent/My_Agent.agent \
  > tests/My_Agent_test_spec.yaml

# 5. Create test definition
sf agent test create --spec tests/My_Agent_test_spec.yaml --target-org MyOrg

# 6. Run tests
sf agent test run --api-name My_Agent_Tests --wait 10 --target-org MyOrg

# 7. Review results and fix failures (manual or via sf-ai-agentforce-testing)

# 8. Preview in live mode (final validation)
sf agent preview --api-name My_Agent --use-live-actions --client-app MyApp --target-org MyOrg
```
