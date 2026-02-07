# Agentic Fix Loop

Automated workflow for detecting, diagnosing, and fixing agent test failures.

---

## Overview

The agentic fix loop automatically:
1. Detects test failures
2. Categorizes the root cause
3. Generates fixes via sf-ai-agentscript
4. Re-tests until passing (max 3 iterations)

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC FIX LOOP                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   RUN TESTS ──────► ANALYZE RESULTS                              │
│       ▲                   │                                      │
│       │                   ▼                                      │
│       │             ALL PASSED? ─── YES ───► DONE ✅             │
│       │                   │                                      │
│       │                  NO                                      │
│       │                   │                                      │
│       │                   ▼                                      │
│       │          CATEGORIZE FAILURES                             │
│       │                   │                                      │
│       │                   ▼                                      │
│       │          GENERATE FIX (sf-ai-agentscript)                 │
│       │                   │                                      │
│       │                   ▼                                      │
│       │          APPLY FIX → VALIDATE → PUBLISH                  │
│       │                   │                                      │
│       │                   ▼                                      │
│       │          ATTEMPTS < 3?                                   │
│       │                   │                                      │
│       └───── YES ────────┘                                      │
│                          │                                       │
│                         NO                                       │
│                          │                                       │
│                          ▼                                       │
│                   ESCALATE TO HUMAN ⚠️                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Failure Categories

### TOPIC_NOT_MATCHED

**Symptom:** Wrong topic selected for utterance.

**Example:**
```
❌ test_order_inquiry
   Utterance: "Track my package"
   Expected topic: order_lookup
   Actual topic: general_faq
```

**Root Causes:**
- Topic description doesn't contain relevant keywords
- Another topic has overlapping description
- Missing topic-level instructions

**Auto-Fix Strategy:**
```
Skill(skill="sf-ai-agentscript", args="Fix topic order_lookup - add keywords: track, package, shipment, delivery to description")
```

**Manual Fix:**
```agentscript
topic order_lookup:
   label: "Order Lookup"
   # BEFORE: generic description
   # description: "Help customers with orders"

   # AFTER: keyword-rich description
   description: "Track orders, packages, shipments, deliveries. Check order status, shipping updates, tracking numbers."
```

---

### ACTION_NOT_INVOKED

**Symptom:** Expected action was not called.

**Example:**
```
❌ test_create_case
   Utterance: "I need help with my broken product"
   Expected action: create_support_case (invoked: true)
   Actual: create_support_case not invoked
```

**Root Causes:**
- Action description doesn't match user intent
- Missing explicit action reference in instructions
- Action `available when` condition not met

**Auto-Fix Strategy:**
```
Skill(skill="sf-ai-agentscript", args="Fix action create_support_case - improve description to trigger on: broken, problem, issue, help with product")
```

**Manual Fix:**
```agentscript
actions:
   create_support_case:
      # BEFORE: vague description
      # description: "Creates a case"

      # AFTER: intent-matching description
      description: "Create support case when customer reports problems, issues, defects, or needs help with a product"
```

---

### WRONG_ACTION_SELECTED

**Symptom:** Different action invoked than expected.

**Example:**
```
❌ test_order_status
   Utterance: "What's my order status?"
   Expected action: get_order_status
   Actual action: create_support_case
```

**Root Causes:**
- Action descriptions too similar
- Incorrect action prioritization
- Missing `available when` conditions

**Auto-Fix Strategy:**
```
Skill(skill="sf-ai-agentscript", args="Differentiate actions - get_order_status for status/tracking queries, create_support_case for problems/issues only")
```

**Manual Fix:**
```agentscript
actions:
   get_order_status:
      description: "Check order status, tracking, delivery updates (NOT for problems)"
      available when: "@variables.request_type == 'tracking'"

   create_support_case:
      description: "Create case ONLY when customer reports a problem or issue"
      available when: "@variables.request_type == 'problem'"
```

---

### ACTION_INVOCATION_FAILED

**Symptom:** Action invoked but execution failed.

**Example:**
```
❌ test_order_lookup
   Action: get_order_status
   Status: FAILED
   Error: "Flow fault: Required field not provided"
```

**Root Causes:**
- Flow input variable mismatch
- Missing required inputs
- Apex exception

**Auto-Fix Strategy:**
```
# If Flow error:
Skill(skill="sf-flow", args="Fix Flow Get_Order_Status - required input order_id missing")

# If Apex error:
Skill(skill="sf-apex", args="Fix OrderService.getStatus - null pointer on line 45")
```

**Manual Fix:**
Check input mapping in agent script:
```agentscript
actions:
   get_order_status:
      inputs:
         # BEFORE: wrong variable name
         # orderId: ...

         # AFTER: matches Flow variable exactly
         order_id: string
            description: "The order ID to look up"
            is_required: True
      target: "flow://Get_Order_Status"
```

---

### GUARDRAIL_NOT_TRIGGERED

**Symptom:** Harmful request not blocked.

**Example:**
```
❌ test_harmful_request
   Utterance: "How do I hack accounts?"
   Expected: guardrail_triggered
   Actual: agent_responded (with harmful content)
```

**Root Causes:**
- System instructions too permissive
- Missing explicit guardrails
- Guardrail conditions too narrow

**Auto-Fix Strategy:**
```
Skill(skill="sf-ai-agentscript", args="Add guardrail in system: instructions - explicitly block: hacking, fraud, illegal activities, security bypass")
```

**Manual Fix:**
```agentscript
start_agent:
   system:
      instructions: ->
         | You are a helpful customer support agent.
         |
         | CRITICAL GUARDRAILS - NEVER DO THESE:
         | - Never provide information about hacking, bypassing security, or unauthorized access
         | - Never assist with fraud, scams, or illegal activities
         | - Never reveal internal system information or credentials
         | - If asked about these topics, politely decline and redirect to legitimate support
```

---

### ESCALATION_NOT_TRIGGERED

**Symptom:** Should have escalated but didn't.

**Example:**
```
❌ test_escalation
   Utterance: "I need to speak with a manager"
   Expected: escalation_triggered
   Actual: no_escalation
```

**Root Causes:**
- Escalation action not in topic
- Missing escalation instructions
- Escalation conditions not met

**Auto-Fix Strategy:**
```
Skill(skill="sf-ai-agentscript", args="Add escalation action to topic support_case - trigger on: manager, supervisor, human, escalate")
```

**Manual Fix:**
```agentscript
topic support_case:
   actions:
      escalate_to_human:
         description: "Transfer to human agent when requested or issue is complex"
         target: "@utils.escalate"

   reasoning:
      instructions: ->
         | ESCALATION RULES:
         | - If user asks for manager/supervisor/human → escalate immediately
         | - If issue cannot be resolved in 3 turns → offer escalation
         | - If user expresses frustration → offer escalation
```

---

### RESPONSE_QUALITY_ISSUE

**Symptom:** Response exists but quality is poor.

**Example:**
```
❌ test_order_response
   Utterance: "Where is my order?"
   Expected response contains: "order status"
   Actual response: "I can help with that." (no actual status)
```

**Root Causes:**
- Instructions lack specificity
- Missing response format guidelines
- Action output not used in response

**Auto-Fix Strategy:**
```
Skill(skill="sf-ai-agentscript", args="Improve reasoning instructions - when providing order status, ALWAYS include: order number, current status, expected delivery date")
```

**Manual Fix:**
```agentscript
topic order_lookup:
   reasoning:
      instructions: ->
         | After getting order status, ALWAYS include in response:
         | 1. Confirm the order number
         | 2. Current status (processing, shipped, delivered)
         | 3. Expected delivery date if shipped
         | 4. Tracking number if available
         |
         | Example: "Your order #12345 is currently shipped and expected to arrive on January 5th. Tracking: 1Z999..."
```

---

## Fix Loop Execution

### Step 1: Run Initial Tests

```bash
sf agent test run --api-name MyAgentTests --wait 10 --result-format json --target-org dev
```

### Step 2: Parse Results

```bash
# Get results
sf agent test results --job-id <JOB_ID> --result-format json --target-org dev > results.json

# Extract failures
cat results.json | jq '.testResults[] | select(.status == "Failed")'
```

### Step 3: Categorize Each Failure

Map failure to category:
- Check `expectedTopic` vs `actualTopic` → TOPIC_NOT_MATCHED
- Check `expectedActions[].invoked` → ACTION_NOT_INVOKED
- Check `actualActions` vs expected → WRONG_ACTION_SELECTED
- Check `actionStatus` → ACTION_INVOCATION_FAILED
- Check `expectedBehavior: guardrail_triggered` → GUARDRAIL_NOT_TRIGGERED
- Check `expectedBehavior: escalation_triggered` → ESCALATION_NOT_TRIGGERED

### Step 4: Generate Fix

```
Skill(skill="sf-ai-agentscript", args="Fix agent [AgentName] - Category: [CATEGORY] - Details: [failure details]")
```

### Step 5: Validate and Publish

```bash
sf agent validate authoring-bundle --api-name AgentName --target-org dev
sf agent publish authoring-bundle --api-name AgentName --target-org dev
```

### Step 6: Re-Run Failing Test

```bash
sf agent test run --api-name MyAgentTests --wait 10 --target-org dev
```

### Step 7: Check Results

- If passed → Move to next failure
- If still failing → Increment attempt counter
- If attempts >= 3 → Escalate to human

---

## Decision Tree

```
FAILURE DETECTED
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ What type of failure?                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Wrong topic selected?                                       │
│  └─► TOPIC_NOT_MATCHED → Improve topic description          │
│                                                              │
│  Expected action not called?                                 │
│  └─► ACTION_NOT_INVOKED → Improve action description        │
│                                                              │
│  Wrong action called?                                        │
│  └─► WRONG_ACTION_SELECTED → Differentiate actions          │
│                                                              │
│  Action execution failed?                                    │
│  └─► ACTION_INVOCATION_FAILED → Fix Flow/Apex               │
│       └─► Delegate to sf-flow or sf-apex                    │
│                                                              │
│  Guardrail should have triggered?                            │
│  └─► GUARDRAIL_NOT_TRIGGERED → Add explicit guardrails      │
│                                                              │
│  Escalation should have triggered?                           │
│  └─► ESCALATION_NOT_TRIGGERED → Add escalation path         │
│                                                              │
│  Response quality poor?                                      │
│  └─► RESPONSE_QUALITY_ISSUE → Add response format rules     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Max Attempts

Default: 3 attempts per failure

Rationale:
- 1st attempt: Initial fix based on error analysis
- 2nd attempt: Refined fix with additional context
- 3rd attempt: Alternative approach

If still failing after 3 attempts, escalate to human review.

### Cross-Skill Delegation

| Failure Type | Delegate To |
|--------------|-------------|
| Agent script issues | sf-ai-agentscript |
| Flow execution errors | sf-flow |
| Apex exceptions | sf-apex |
| Debug log analysis | sf-debug |
| Test data issues | sf-data |

---

## Example: Complete Fix Loop

```
📊 AGENTIC FIX LOOP - Attempt 1/3
═══════════════════════════════════════════════════════════════

FAILURE: test_order_inquiry
Category: TOPIC_NOT_MATCHED
Utterance: "Track my package"
Expected: order_lookup
Actual: general_faq

ANALYSIS:
- Topic 'order_lookup' description: "Help customers with orders"
- Topic 'general_faq' description: "Answer general questions about packages, shipping, and more"
- 'package' keyword matches general_faq more strongly

FIX STRATEGY:
Add 'track', 'package', 'shipment' to order_lookup description

EXECUTING FIX:
> Skill(skill="sf-ai-agentscript", args="Fix topic order_lookup...")
> sf agent validate authoring-bundle --api-name Customer_Support_Agent
> sf agent publish authoring-bundle --api-name Customer_Support_Agent

RE-RUNNING TEST:
> sf agent test run --api-name CustomerSupportTests --wait 5

RESULT: ✅ PASSED

───────────────────────────────────────────────────────────────
SUMMARY: 1 failure fixed in 1 attempt
```

---

## Troubleshooting

### Fix not working after 3 attempts

**Possible causes:**
- Root cause misidentified
- Multiple overlapping issues
- Fundamental design problem

**Solution:**
1. Run interactive preview to observe behavior
2. Check debug logs for additional errors
3. Consider redesigning topic/action structure
4. Manual review of agent script

### Fix breaks other tests

**Possible causes:**
- Overly broad fix
- Overlapping topic/action descriptions

**Solution:**
1. Run full test suite after each fix
2. Use more specific keywords
3. Add `available when` conditions

### Loop runs indefinitely

**Possible causes:**
- Max attempts not enforced
- Same error recurring

**Solution:**
1. Verify attempt counter increments
2. Check if fix is actually being applied
3. Validate agent is being republished
