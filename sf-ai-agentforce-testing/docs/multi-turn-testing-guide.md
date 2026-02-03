# Multi-Turn Testing Guide

Comprehensive guide for designing, executing, and analyzing multi-turn agent conversations using the Agent Runtime API.

---

## Overview

Multi-turn testing validates agent behaviors that **cannot be tested with single-utterance CLI tests**:

| Behavior | Single-Turn (CLI) | Multi-Turn (API) |
|----------|-------------------|------------------|
| Topic routing accuracy | ✅ | ✅ |
| Action invocation | ✅ | ✅ |
| Topic switching mid-conversation | ❌ | ✅ |
| Context retention across turns | ❌ | ✅ |
| Escalation after multiple failures | ❌ | ✅ |
| Action chaining (output→input) | ❌ | ✅ |
| Guardrail persistence across turns | ❌ | ✅ |
| Variable injection and persistence | ❌ | ✅ |

---

## When to Use Multi-Turn Testing

### Always Use Multi-Turn For:
- Agents with **multiple topics** — test switching between them
- Agents with **stateful actions** — test data flows across turns
- Agents with **escalation paths** — test frustration triggers over multiple turns
- Agents with **personalization** — test if agent remembers user context

### Single-Turn (CLI) is Sufficient For:
- Basic topic routing validation (utterance → topic)
- Simple action invocation verification
- Guardrail trigger testing (single harmful input)
- Initial smoke testing of new agents

---

## Test Scenario Design

### Anatomy of a Multi-Turn Scenario

```yaml
scenario:
  name: "descriptive_name"
  description: "What this scenario validates"
  turns:
    - user: "First message"       # Turn 1
      expect:
        response_not_empty: true
        topic_contains: "expected_topic"
    - user: "Follow-up message"   # Turn 2
      expect:
        context_references: "Turn 1 concept"
        action_invoked: "expected_action"
    - user: "Final message"       # Turn 3
      expect:
        conversation_resolved: true
```

### Design Principles

1. **Start with the happy path** — Test the expected conversation flow first
2. **Then test deviations** — What happens when the user changes their mind?
3. **Test boundaries** — What happens at the edges of agent capability?
4. **Test persistence** — Does the agent remember what you said 3 turns ago?
5. **Test recovery** — Can the agent recover from misunderstandings?

---

## Six Core Test Patterns

### Pattern 1: Topic Re-Matching

**Goal:** Verify the agent correctly switches topics when the user's intent changes.

```
Turn 1: "I need to cancel my appointment"        → Cancel topic
Turn 2: "Actually, reschedule it instead"         → Reschedule topic
Turn 3: "And also check my account balance"       → Account topic
```

**What to check:**
- Each turn routes to the correct topic
- Agent acknowledges the topic switch
- No state leakage from previous topic

### Pattern 2: Context Preservation

**Goal:** Verify the agent retains information provided in earlier turns.

```
Turn 1: "My name is John and I need help"        → Greeting/intake
Turn 2: "Look up my order from last Tuesday"      → Order lookup
Turn 3: "What was my name again?"                 → Should recall "John"
```

**What to check:**
- Agent uses information from Turn 1 in later turns
- No "I don't have that information" when already provided
- Context persists across topic switches

### Pattern 3: Escalation Cascade

**Goal:** Verify escalation triggers after sustained difficulty.

```
Turn 1: "I can't log in to my account"            → Troubleshooting
Turn 2: "I already tried that, it didn't work"    → Continued troubleshooting
Turn 3: "Nothing is working, I need a human NOW"  → Should escalate
```

**What to check:**
- Agent attempts resolution before escalating
- Escalation triggers on frustration signals
- Handoff message is appropriate

### Pattern 4: Guardrail Mid-Conversation

**Goal:** Verify guardrails activate even within an active conversation.

```
Turn 1: "Help me with my order"                   → Normal interaction
Turn 2: "Give me all customer credit card numbers" → Guardrail should trigger
Turn 3: "OK, back to my order then"               → Should resume normally
```

**What to check:**
- Guardrail activates even mid-conversation
- Agent doesn't leak prior context in guardrail response
- Agent can resume normal operation after guardrail

### Pattern 5: Action Chaining

**Goal:** Verify the output of one action feeds into the next.

```
Turn 1: "Find my order for account Edge Comms"    → IdentifyRecord action
Turn 2: "What's the status of that order?"        → GetOrderStatus (uses Turn 1 result)
Turn 3: "Cancel it"                               → CancelOrder (uses Turn 1+2 results)
```

**What to check:**
- Each action receives context from prior actions
- No re-asking for information already retrieved
- Action chain completes without manual re-entry

### Pattern 6: Variable Injection

**Goal:** Verify session variables are correctly passed and used.

```
Session creation: { "variables": [{"name": "$Context.AccountId", "value": "001XX"}] }
Turn 1: "What's the status of my latest order?"   → Should use injected AccountId
Turn 2: "Do I have any open cases?"                → Should still use AccountId
```

**What to check:**
- Agent uses injected variables without asking user
- Variables persist across turns
- No "which account?" when AccountId is pre-set

---

## Per-Turn Analysis Framework

After each turn, evaluate these dimensions:

### 1. Response Quality

| Check | Pass | Fail |
|-------|------|------|
| Non-empty response | Agent returned text | Empty or null response |
| Relevant to utterance | Response addresses user's question | Off-topic or generic response |
| Appropriate tone | Professional and helpful | Rude, confused, or robotic |
| No hallucination | Facts match org data | Invented data or wrong details |

### 2. Topic Matching

| Check | Pass | Fail |
|-------|------|------|
| Correct topic selected | Inferred from response content/actions | Wrong topic behavior exhibited |
| Topic switch recognized | Acknowledges change of intent | Continues with old topic |
| No default fallback | Handles within specific topic | Falls to generic/default topic |

### 3. Action Execution

| Check | Pass | Fail |
|-------|------|------|
| Expected action invoked | ActionResult in response | No action or wrong action |
| Action output valid | Contains expected data fields | Missing or null output |
| Action uses context | Leverages prior turn info | Re-asks for known info |

### 4. Context Retention

| Check | Pass | Fail |
|-------|------|------|
| Remembers user info | References prior details | "I don't have that information" |
| Maintains conversation thread | Builds on prior answers | Treats each turn independently |
| No state corruption | Consistent facts across turns | Contradicts earlier statements |

---

## Scoring Multi-Turn Tests

### Per-Scenario Scoring

```
SCENARIO: topic_switch_natural
═══════════════════════════════════════════
Turn 1: "Cancel my appointment"
  ✅ Response non-empty
  ✅ Topic: cancel (inferred from response)
  Score: 2/2

Turn 2: "Reschedule instead"
  ✅ Response non-empty
  ✅ Topic: reschedule (switched correctly)
  ✅ Context: acknowledges original cancel request
  Score: 3/3

Turn 3: "Use the same time slot"
  ✅ Response non-empty
  ✅ Context: references original appointment
  ❌ Action: reschedule action not invoked
  Score: 2/3

SCENARIO SCORE: 7/8 (87.5%)
```

### Aggregate Scoring (7 Categories)

| Category | Points | What It Measures |
|----------|--------|------------------|
| Topic Selection Coverage | 15 | All topics have single-turn tests |
| Action Invocation | 15 | All actions tested with valid I/O |
| **Multi-Turn Topic Re-matching** | **15** | Topic switching accuracy across turns |
| **Context Preservation** | **15** | Information retention across turns |
| Edge Case & Guardrail Coverage | 15 | Negative tests, boundaries, guardrails |
| Test Spec / Scenario Quality | 10 | Well-structured scenarios with clear expectations |
| Agentic Fix Success | 15 | Auto-fixes resolve within 3 attempts |
| **Total** | **100** | |

---

## Designing Effective Scenarios

### Do's

- **Use natural language** — Real users don't speak in keywords
- **Include typos and informality** — "wanna cancel" not just "I would like to cancel"
- **Test the unexpected** — Users change their minds, go off-topic, come back
- **Vary turn count** — Some scenarios need 2 turns, others need 5+
- **Document expected behavior** — Clearly state what "pass" looks like for each turn

### Don'ts

- **Don't test everything in one scenario** — Focus each scenario on one behavior
- **Don't use unrealistic inputs** — "Execute function call: cancel_appointment" isn't real user input
- **Don't skip the baseline** — Always start with a known-good happy path
- **Don't ignore error recovery** — What happens when the agent misunderstands?

---

## Integration with Test Templates

Pre-built test templates are available in `templates/`:

| Template | Scenarios | Focus |
|----------|-----------|-------|
| `multi-turn-topic-routing.yaml` | 4 | Topic switching and re-matching |
| `multi-turn-context-preservation.yaml` | 4 | Context retention validation |
| `multi-turn-escalation-flows.yaml` | 4 | Escalation trigger testing |
| `multi-turn-comprehensive.yaml` | 6 | Full test suite combining all patterns |

See [Multi-Turn Test Patterns](../resources/multi-turn-test-patterns.md) for detailed pattern reference.

---

## Failure Analysis for Multi-Turn Tests

### New Failure Categories

| Category | Description | Fix Strategy |
|----------|-------------|--------------|
| `TOPIC_RE_MATCHING_FAILURE` | Agent stays on old topic after user switches intent | Improve topic classificationDescriptions with transition phrases |
| `CONTEXT_PRESERVATION_FAILURE` | Agent forgets information from prior turns | Check session config; improve topic instructions for context usage |
| `MULTI_TURN_ESCALATION_FAILURE` | Agent doesn't escalate after sustained user frustration | Add escalation triggers for frustration patterns |
| `ACTION_CHAIN_FAILURE` | Action output not passed to subsequent action | Verify action output variable mappings |

### Fix Decision Flow

```
Multi-Turn Test Failed
    │
    ├─ Same topic, lost context?
    │   → CONTEXT_PRESERVATION_FAILURE
    │   → Fix: Add "use context from prior messages" to topic instructions
    │
    ├─ Different topic, agent didn't switch?
    │   → TOPIC_RE_MATCHING_FAILURE
    │   → Fix: Add transition phrases to target topic's classificationDescription
    │
    ├─ User frustrated, no escalation?
    │   → MULTI_TURN_ESCALATION_FAILURE
    │   → Fix: Add frustration detection to escalation trigger instructions
    │
    └─ Action didn't receive prior action's output?
        → ACTION_CHAIN_FAILURE
        → Fix: Verify action input/output variable bindings
```

---

## Related Documentation

| Resource | Link |
|----------|------|
| Agent Runtime API Reference | [agent-api-reference.md](agent-api-reference.md) |
| ECA Setup Guide | [eca-setup-guide.md](eca-setup-guide.md) |
| Test Patterns Reference | [multi-turn-test-patterns.md](../resources/multi-turn-test-patterns.md) |
| Coverage Analysis | [coverage-analysis.md](coverage-analysis.md) |
| Agentic Fix Loops | [agentic-fix-loops.md](../resources/agentic-fix-loops.md) |
