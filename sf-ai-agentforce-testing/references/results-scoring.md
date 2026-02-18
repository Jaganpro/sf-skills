<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->

# Results & Scoring

## Phase A5: Multi-Turn API Results

Claude generates a terminal-friendly results report:

```
📊 MULTI-TURN TEST RESULTS
════════════════════════════════════════════════════════════════

Agent: Customer_Support_Agent
Org: vivint-DevInt
Mode: Agent Runtime API (multi-turn)

SCENARIO RESULTS
───────────────────────────────────────────────────────────────
✅ topic_switch_natural        3/3 turns passed
✅ context_user_identity       3/3 turns passed
❌ escalation_frustration      2/3 turns passed (Turn 3: no escalation)
✅ guardrail_mid_conversation  3/3 turns passed
✅ action_chain_identify       3/3 turns passed
⚠️ variable_injection          2/3 turns passed (Turn 3: re-asked for account)

SUMMARY
───────────────────────────────────────────────────────────────
Scenarios: 6 total | 4 passed | 1 failed | 1 partial
Turns: 18 total | 16 passed | 2 failed
Topic Re-matching: 100% ✅
Context Preservation: 83% ⚠️
Escalation Accuracy: 67% ❌

FAILED TURNS
───────────────────────────────────────────────────────────────
❌ escalation_frustration → Turn 3
   Input: "Nothing is working! I need a human NOW"
   Expected: Escalation triggered
   Actual: Agent continued troubleshooting
   Category: MULTI_TURN_ESCALATION_FAILURE
   Fix: Add frustration keywords to escalation triggers

⚠️ variable_injection → Turn 3
   Input: "Create a new case for a billing issue"
   Expected: Uses pre-set $Context.AccountId
   Actual: "Which account is this for?"
   Category: CONTEXT_PRESERVATION_FAILURE
   Fix: Wire $Context.AccountId to CreateCase action input

SCORING
───────────────────────────────────────────────────────────────
Topic Selection Coverage          13/15
Action Invocation                 14/15
Multi-Turn Topic Re-matching      15/15  ✅
Context Preservation              10/15  ⚠️
Edge Case & Guardrail Coverage    12/15
Test Spec / Scenario Quality       9/10
Agentic Fix Success               --/15  (pending)

TOTAL: 73/85 (86%) + Fix Loop pending
```

---

## Phase B3: CLI Results Analysis

Parse test results JSON and display formatted summary:

```
📊 AGENT TEST RESULTS (CLI)
════════════════════════════════════════════════════════════════

Agent: Customer_Support_Agent
Org: vivint-DevInt
Duration: 45.2s
Mode: Simulated

SUMMARY
───────────────────────────────────────────────────────────────
✅ Passed:    18
❌ Failed:    2
⏭️ Skipped:   0
📈 Topic Selection: 95%
🎯 Action Invocation: 90%

FAILED TESTS
───────────────────────────────────────────────────────────────
❌ test_complex_order_inquiry
   Utterance: "What's the status of orders 12345 and 67890?"
   Expected: get_order_status invoked 2 times
   Actual: get_order_status invoked 1 time
   Category: ACTION_INVOCATION_COUNT_MISMATCH

COVERAGE SUMMARY
───────────────────────────────────────────────────────────────
Topics Tested:       4/5 (80%) ⚠️
Actions Tested:      6/8 (75%) ⚠️
Guardrails Tested:   3/3 (100%) ✅
```
