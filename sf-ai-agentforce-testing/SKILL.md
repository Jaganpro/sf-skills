---
name: sf-ai-agentforce-testing
description: >
  Comprehensive Agentforce testing skill with dual-track workflow: multi-turn API testing
  (primary) and CLI Testing Center (secondary). Execute multi-turn conversations via Agent
  Runtime API, run single-utterance tests via sf CLI, analyze topic/action/context coverage,
  and automatically fix failing agents with 100-point scoring across 7 categories.
license: MIT
compatibility: "Requires API v65.0+ (Winter '26) and Agentforce enabled org"
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 7 categories"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/parse-agent-test-results.py"
          timeout: 10000
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-ai-agentforce-testing"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-ai-agentforce-testing"
      timeout: 5000
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document - read this FIRST -->
<!-- Pattern: Follows sf-testing for agentic test-fix loops -->
<!-- v2.0.0: Dual-track workflow with multi-turn API testing as primary -->

# sf-ai-agentforce-testing: Agentforce Test Execution & Coverage Analysis

Expert testing engineer specializing in Agentforce agent testing via **dual-track workflow**: multi-turn Agent Runtime API testing (primary) and CLI Testing Center (secondary). Execute multi-turn conversations, analyze topic/action/context coverage, and automatically fix issues via sf-ai-agentscript (or sf-ai-agentforce-legacy for existing agents).

## Core Responsibilities

1. **Multi-Turn API Testing** (PRIMARY): Execute multi-turn conversations via Agent Runtime API
2. **CLI Test Execution** (SECONDARY): Run single-utterance tests via `sf agent test run`
3. **Test Spec / Scenario Generation**: Create YAML test specifications and multi-turn scenarios
4. **Coverage Analysis**: Track topic, action, context preservation, and re-matching coverage
5. **Preview Testing**: Interactive simulated and live agent testing
6. **Agentic Fix Loop**: Automatically fix failing agents and re-test
7. **Cross-Skill Orchestration**: Delegate fixes to sf-ai-agentscript, data to sf-data
8. **Observability Integration**: Guide to sf-ai-agentforce-observability for STDM analysis

## 📚 Document Map

| Need | Document | Description |
|------|----------|-------------|
| **Agent Runtime API** | [agent-api-reference.md](docs/agent-api-reference.md) | REST endpoints for multi-turn testing |
| **ECA Setup** | [eca-setup-guide.md](docs/eca-setup-guide.md) | External Client App for API authentication |
| **Multi-Turn Testing** | [multi-turn-testing-guide.md](docs/multi-turn-testing-guide.md) | Multi-turn test design and execution |
| **Test Patterns** | [multi-turn-test-patterns.md](resources/multi-turn-test-patterns.md) | 6 multi-turn test patterns with examples |
| **CLI commands** | [cli-commands.md](docs/cli-commands.md) | Complete sf agent test/preview reference |
| **Test spec format** | [test-spec-reference.md](resources/test-spec-reference.md) | YAML specification format and examples |
| **Auto-fix workflow** | [agentic-fix-loops.md](resources/agentic-fix-loops.md) | Automated test-fix cycles (10 failure categories) |
| **Live preview setup** | [connected-app-setup.md](docs/connected-app-setup.md) | OAuth for live preview mode |
| **Coverage metrics** | [coverage-analysis.md](docs/coverage-analysis.md) | Topic/action/multi-turn coverage analysis |
| **Fix decision tree** | [agentic-fix-loop.md](docs/agentic-fix-loop.md) | Detailed fix strategies |

**⚡ Quick Links:**
- [Scoring System](#scoring-system-100-points) - 7-category validation
- [Phase A: Multi-Turn API Testing](#phase-a-multi-turn-api-testing-primary) - Primary workflow
- [Phase B: CLI Testing Center](#phase-b-cli-testing-center-secondary) - Secondary workflow
- [Agentic Fix Loop](#phase-c-agentic-fix-loop) - Auto-fix workflow
- [Multi-Turn Templates](#multi-turn-test-templates) - Pre-built test scenarios

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-apex → sf-flow → sf-deploy → sf-ai-agentscript → sf-deploy → sf-ai-agentforce-testing** (you are here)

**Why testing is LAST:**
1. Agent must be **published** before running automated tests
2. Agent must be **activated** for preview mode and API access
3. All dependencies (Flows, Apex) must be deployed first
4. Test data (via sf-data) should exist before testing actions

**⚠️ MANDATORY Delegation:**
- **Fixes**: ALWAYS use `Skill(skill="sf-ai-agentscript")` for agent script fixes (or `sf-ai-agentforce-legacy` for existing legacy agents)
- **Test Data**: Use `Skill(skill="sf-data")` for action test data
- **OAuth Setup**: Use `Skill(skill="sf-connected-apps")` for ECA or Connected App
- **Observability**: Use `Skill(skill="sf-ai-agentforce-observability")` for STDM analysis of test sessions

---

## Architecture: Dual-Track Testing Workflow

```
Phase 0: Prerequisites & Agent Discovery
    │
    ├──► Phase A: Multi-Turn API Testing (PRIMARY)
    │    A1: ECA Credential Setup
    │    A2: Agent Discovery & Metadata Retrieval
    │    A3: Test Scenario Planning (interview user)
    │    A4: Multi-Turn Execution (Agent Runtime API)
    │    A5: Results & Scoring
    │
    └──► Phase B: CLI Testing Center (SECONDARY)
         B1: Test Spec Creation
         B2: Test Execution (sf agent test run)
         B3: Results Analysis
    │
Phase C: Agentic Fix Loop (shared)
Phase D: Coverage Improvement (shared)
Phase E: Observability Integration (STDM analysis)
```

**When to use which track:**

| Condition | Use |
|-----------|-----|
| Agent Testing Center NOT available | Phase A only |
| Need multi-turn conversation testing | Phase A |
| Need topic re-matching validation | Phase A |
| Need context preservation testing | Phase A |
| Agent Testing Center IS available + single-utterance tests | Phase B |
| CI/CD pipeline integration | Phase B (or Phase A with scripting) |
| Quick smoke test | Phase B |

---

## Phase 0: Prerequisites & Agent Discovery

### Step 1: Gather User Information

Use **AskUserQuestion** to gather:

```
AskUserQuestion:
  questions:
    - question: "Which agent do you want to test?"
      header: "Agent"
      options:
        - label: "Let me discover agents in the org"
          description: "Query BotDefinition to find available agents"
        - label: "I know the agent name"
          description: "Provide agent name/API name directly"

    - question: "What is your target org alias?"
      header: "Org"
      options:
        - label: "vivint-DevInt"
          description: "Development integration org"
        - label: "Other"
          description: "Specify a different org alias"

    - question: "What type of testing do you need?"
      header: "Test Type"
      options:
        - label: "Multi-turn API testing (Recommended)"
          description: "Full conversation testing via Agent Runtime API — tests topic switching, context retention, escalation cascades"
        - label: "CLI single-utterance testing"
          description: "Traditional sf agent test run — requires Agent Testing Center feature"
        - label: "Both"
          description: "Run both multi-turn and CLI tests for comprehensive coverage"
```

### Step 2: Agent Discovery

```bash
# Auto-discover active agents in the org
sf data query --use-tooling-api \
  --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition WHERE IsActive=true" \
  --result-format json --target-org [alias]
```

### Step 3: Agent Metadata Retrieval

```bash
# Retrieve agent configuration (topics, actions, instructions)
sf project retrieve start \
  --metadata "GenAiPlannerBundle:[AgentDeveloperName]" \
  --output-dir retrieve-temp --target-org [alias]
```

Claude reads the GenAiPlannerBundle to understand:
- All topics and their `classificationDescription` values
- All actions and their configurations
- System instructions and guardrails
- Escalation paths

### Step 4: Check Agent Testing Center Availability

```bash
# This determines if Phase B is available
sf agent test list --target-org [alias]

# If error: "INVALID_TYPE: Cannot use: AiEvaluationDefinition"
# → Agent Testing Center NOT enabled → Phase A only
# If success: → Both Phase A and Phase B available
```

### Step 5: Prerequisites Checklist

| Check | Command | Why |
|-------|---------|-----|
| **Agent exists** | `sf data query --use-tooling-api --query "SELECT Id FROM BotDefinition WHERE DeveloperName='X'"` | Can't test non-existent agent |
| **Agent published** | `sf agent validate authoring-bundle --api-name X` | Must be published to test |
| **Agent activated** | Check activation status | Required for API access |
| **Dependencies deployed** | Flows and Apex in org | Actions will fail without them |
| **ECA configured** (Phase A) | Token request test | Required for Agent Runtime API |
| **Agent Testing Center** (Phase B) | `sf agent test list` | Required for CLI testing |

---

## Phase A: Multi-Turn API Testing (PRIMARY)

### A1: ECA Credential Setup

```
AskUserQuestion:
  question: "Do you have an External Client App (ECA) with Client Credentials flow configured?"
  header: "ECA Setup"
  options:
    - label: "Yes, I have credentials"
      description: "I have Consumer Key, Secret, and My Domain URL ready"
    - label: "No, I need to create one"
      description: "Delegate to sf-connected-apps skill to create ECA"
```

**If YES:** Collect credentials (kept in conversation context only, NEVER written to files):
- Consumer Key
- Consumer Secret
- My Domain URL (e.g., `your-domain.my.salesforce.com`)

**If NO:** Delegate to sf-connected-apps:
```
Skill(skill="sf-connected-apps", args="Create External Client App with Client Credentials flow for Agent Runtime API testing. Scopes: cdp_api, einstein_gpt_api. Name: Agent_API_Testing")
```

**Verify credentials work:**
```bash
# Test token request (credentials passed inline, never stored in files)
curl -s -X POST "https://${SF_MY_DOMAIN}/services/oauth2/token" \
  -d "grant_type=client_credentials&client_id=${CONSUMER_KEY}&client_secret=${CONSUMER_SECRET}" \
  | jq '.access_token | length'
```

See [ECA Setup Guide](docs/eca-setup-guide.md) for complete instructions.

### A2: Agent Discovery & Metadata Retrieval

```bash
# Get agent ID for API calls
AGENT_ID=$(sf data query --use-tooling-api \
  --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition WHERE DeveloperName='[AgentName]' AND IsActive=true LIMIT 1" \
  --result-format json --target-org [alias] | jq -r '.result.records[0].Id')

# Retrieve full agent configuration
sf project retrieve start \
  --metadata "GenAiPlannerBundle:[AgentName]" \
  --output-dir retrieve-temp --target-org [alias]
```

Claude reads the GenAiPlannerBundle to understand:
- **Topics**: Names, classificationDescriptions, instructions
- **Actions**: Types (flow, apex), triggers, inputs/outputs
- **System Instructions**: Global rules and guardrails
- **Escalation Paths**: When and how the agent escalates

This metadata drives automatic test scenario generation in A3.

### A3: Test Scenario Planning

```
AskUserQuestion:
  question: "What testing do you need?"
  header: "Scenarios"
  options:
    - label: "Comprehensive coverage (Recommended)"
      description: "All 6 test patterns: topic routing, context preservation, escalation, guardrails, action chaining, variable injection"
    - label: "Topic routing accuracy"
      description: "Test that utterances route to correct topics, including mid-conversation topic switches"
    - label: "Context preservation"
      description: "Test that the agent retains information across turns"
    - label: "Specific bug reproduction"
      description: "Reproduce a known issue with targeted multi-turn scenario"
  multiSelect: true
```

Claude uses the agent metadata from A2 to **auto-generate multi-turn scenarios** tailored to the specific agent:
- Generates topic switching scenarios based on actual topic names
- Creates context preservation tests using actual action inputs/outputs
- Builds escalation tests based on actual escalation configuration
- Creates guardrail tests based on system instructions

**Available templates** (see [templates/](#multi-turn-test-templates)):

| Template | Pattern | Scenarios |
|----------|---------|-----------|
| `multi-turn-topic-routing.yaml` | Topic switching | 4 |
| `multi-turn-context-preservation.yaml` | Context retention | 4 |
| `multi-turn-escalation-flows.yaml` | Escalation cascades | 4 |
| `multi-turn-comprehensive.yaml` | All 6 patterns | 6 |

### A4: Multi-Turn Execution

Execute conversations via Agent Runtime API. All commands run inline in bash — no external script dependencies.

**Step 1: Authenticate**
```bash
# Get access token (credentials from conversation context)
SF_TOKEN=$(curl -s -X POST "https://${SF_MY_DOMAIN}/services/oauth2/token" \
  -d "grant_type=client_credentials&client_id=${CONSUMER_KEY}&client_secret=${CONSUMER_SECRET}" \
  | jq -r '.access_token')
```

**Step 2: Create Session**
```bash
# Start agent session
SESSION_ID=$(curl -s -X POST \
  "https://api.salesforce.com/einstein/ai-agent/v1/agents/${AGENT_ID}/sessions" \
  -H "Authorization: Bearer ${SF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "externalSessionKey":"'"$(uuidgen | tr A-Z a-z)"'",
    "instanceConfig":{"endpoint":"https://'"${SF_MY_DOMAIN}"'"},
    "streamingCapabilities":{"chunkTypes":["Text"]},
    "bypassUser":true
  }' | jq -r '.sessionId')
```

**Step 3: Send Messages (increment sequenceId per turn)**
```bash
# Turn 1
SEQ=1
MSG="I need to cancel my appointment"
R1=$(curl -s -X POST \
  "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}/messages" \
  -H "Authorization: Bearer ${SF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":{"sequenceId":'"${SEQ}"',"type":"Text","text":"'"${MSG}"'"}}')

# Turn 2
SEQ=2
MSG="Actually, reschedule it instead"
R2=$(curl -s -X POST \
  "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}/messages" \
  -H "Authorization: Bearer ${SF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":{"sequenceId":'"${SEQ}"',"type":"Text","text":"'"${MSG}"'"}}')

# Continue for each turn in the scenario...
```

**Step 4: End Session**
```bash
curl -s -X DELETE \
  "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}" \
  -H "Authorization: Bearer ${SF_TOKEN}"
```

**Per-Turn Analysis Checklist:**

For each turn response, Claude evaluates:

| # | Check | How to Evaluate |
|---|-------|-----------------|
| 1 | Response non-empty? | `messages[0].message` has content |
| 2 | Correct topic matched? | Infer from response language and actions |
| 3 | Expected actions invoked? | Check for `ActionResult` type in response |
| 4 | Context preserved from prior turns? | Agent references prior information |
| 5 | Error indicators? | Check for `Escalation`, `Failure` types |
| 6 | Guardrail respected? | Harmful requests declined |

See [Agent API Reference](docs/agent-api-reference.md) for complete response format.

### A5: Results & Scoring

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

## Phase B: CLI Testing Center (SECONDARY)

> **Availability:** Requires Agent Testing Center feature enabled in org.
> If unavailable, use Phase A exclusively.

### B1: Test Spec Creation

**Option A: Interactive Generation** (no automation)
```bash
# Interactive test spec generation
sf agent generate test-spec --output-file ./tests/agent-spec.yaml
# ⚠️ NOTE: No --api-name flag! Interactive-only.
```

**Option B: Automated Generation** (Python script)
```bash
python3 hooks/scripts/generate-test-spec.py \
  --agent-file /path/to/Agent.agent \
  --output tests/agent-spec.yaml \
  --verbose
```

**Create Test in Org:**
```bash
sf agent test create --spec ./tests/agent-spec.yaml --api-name MyAgentTest --target-org [alias]
```

See [Test Spec Reference](resources/test-spec-reference.md) for complete YAML format guide.

### B2: Test Execution

```bash
# Run automated tests
sf agent test run --api-name MyAgentTest --wait 10 --result-format json --target-org [alias]
```

**Interactive Preview (Simulated):**
```bash
sf agent preview --api-name AgentName --output-dir ./logs --target-org [alias]
```

**Interactive Preview (Live):**
```bash
sf agent preview --api-name AgentName --use-live-actions --client-app AppName --apex-debug --target-org [alias]
```

### B3: Results Analysis

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

---

## Phase C: Agentic Fix Loop

When tests fail (either Phase A or Phase B), automatically fix via sf-ai-agentscript:

### Failure Categories (10 total)

| Category | Source | Auto-Fix | Strategy |
|----------|--------|----------|----------|
| `TOPIC_NOT_MATCHED` | A+B | ✅ | Add keywords to topic description |
| `ACTION_NOT_INVOKED` | A+B | ✅ | Improve action description |
| `WRONG_ACTION_SELECTED` | A+B | ✅ | Differentiate descriptions |
| `ACTION_INVOCATION_FAILED` | A+B | ⚠️ | Delegate to sf-flow or sf-apex |
| `GUARDRAIL_NOT_TRIGGERED` | A+B | ✅ | Add explicit guardrails |
| `ESCALATION_NOT_TRIGGERED` | A+B | ✅ | Add escalation action/triggers |
| `TOPIC_RE_MATCHING_FAILURE` | A | ✅ | Add transition phrases to target topic |
| `CONTEXT_PRESERVATION_FAILURE` | A | ✅ | Add context retention instructions |
| `MULTI_TURN_ESCALATION_FAILURE` | A | ✅ | Add frustration detection triggers |
| `ACTION_CHAIN_FAILURE` | A | ✅ | Fix action output variable mappings |

### Auto-Fix Command Example
```bash
Skill(skill="sf-ai-agentscript", args="Fix agent [AgentName] - Error: [category] - [details]")
```

### Fix Loop Flow
```
Test Failed → Analyze failure category
    │
    ├─ Single-turn failure → Standard fix (topics, actions, guardrails)
    │
    └─ Multi-turn failure → Enhanced fix (context, re-matching, escalation, chaining)
    │
    ▼
Apply fix via sf-ai-agentscript → Re-publish → Re-test
    │
    ├─ Pass → ✅ Move to next failure
    └─ Fail → Retry (max 3 attempts) → Escalate to human
```

See [Agentic Fix Loops Guide](resources/agentic-fix-loops.md) for complete decision tree and 10 fix strategies.

### Two Fix Strategies

| Agent Type | Fix Strategy | When to Use |
|------------|--------------|-------------|
| **Custom Agent** (you control it) | Fix the agent via `sf-ai-agentscript` | Topic descriptions, action configs need adjustment |
| **Managed/Standard Agent** | Fix test expectations | Test expectations don't match actual behavior |

---

## Phase D: Coverage Improvement

If coverage < threshold:

1. Identify untested topics/actions/patterns from results
2. Add test cases (YAML for CLI, scenarios for API)
3. Re-run tests
4. Repeat until threshold met

### Coverage Dimensions

| Dimension | Phase A | Phase B | Target |
|-----------|---------|---------|--------|
| Topic Selection | ✅ | ✅ | 100% |
| Action Invocation | ✅ | ✅ | 100% |
| Topic Re-matching | ✅ | ❌ | 90%+ |
| Context Preservation | ✅ | ❌ | 95%+ |
| Conversation Completion | ✅ | ❌ | 85%+ |
| Guardrails | ✅ | ✅ | 100% |
| Escalation | ✅ | ✅ | 100% |
| Phrasing Diversity | ✅ | ✅ | 3+ per topic |

See [Coverage Analysis](docs/coverage-analysis.md) for complete metrics and improvement guide.

---

## Phase E: Observability Integration

After test execution, guide user to analyze agent behavior with session-level observability:

```
Skill(skill="sf-ai-agentforce-observability", args="Analyze STDM sessions for agent [AgentName] in org [alias] - focus on test session behavior patterns")
```

**What observability adds to testing:**
- **STDM Session Analysis**: Examine actual session traces from test conversations
- **Latency Profiling**: Identify slow actions or topic routing delays
- **Error Pattern Detection**: Find recurring failures across sessions
- **Action Execution Traces**: Detailed view of Flow/Apex execution during tests

---

## Scoring System (100 Points)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Topic Selection Coverage** | 15 | All topics have test cases; various phrasings tested |
| **Action Invocation** | 15 | All actions tested with valid inputs/outputs |
| **Multi-Turn Topic Re-matching** | 15 | Topic switching accuracy across turns |
| **Context Preservation** | 15 | Information retention across turns |
| **Edge Case & Guardrail Coverage** | 15 | Negative tests; guardrails; escalation |
| **Test Spec / Scenario Quality** | 10 | Proper YAML; descriptions; clear expectations |
| **Agentic Fix Success** | 15 | Auto-fixes resolve issues within 3 attempts |

**Scoring Thresholds:**
```
⭐⭐⭐⭐⭐ 90-100 pts → Production Ready
⭐⭐⭐⭐   80-89 pts → Good, minor improvements
⭐⭐⭐    70-79 pts → Acceptable, needs work
⭐⭐      60-69 pts → Below standard
⭐        <60 pts  → BLOCKED - Major issues
```

---

## ⛔ TESTING GUARDRAILS (MANDATORY)

**BEFORE running tests, verify:**

| Check | Command | Why |
|-------|---------|-----|
| Agent published | `sf agent list --target-org [alias]` | Can't test unpublished agent |
| Agent activated | Check status | API and preview require activation |
| Flows deployed | `sf org list metadata --metadata-type Flow` | Actions need Flows |
| ECA configured (Phase A) | Token request test | API auth required |
| Connected App (Phase B live) | Check OAuth | Live mode requires auth |

**NEVER do these:**

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| Test unpublished agent | Tests fail silently | Publish first |
| Skip simulated testing | Live mode hides logic bugs | Always test simulated first |
| Ignore guardrail tests | Security gaps in production | Always test harmful/off-topic inputs |
| Single phrasing per topic | Misses routing failures | Test 3+ phrasings per topic |
| Write ECA credentials to files | Security risk | Keep in shell variables only |
| Skip session cleanup | Resource leaks and rate limits | Always DELETE sessions after tests |

---

## CLI Command Reference

### Test Lifecycle Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf agent generate test-spec` | Create test YAML | `sf agent generate test-spec --output-dir ./tests` |
| `sf agent test create` | Deploy test to org | `sf agent test create --spec ./tests/spec.yaml --target-org alias` |
| `sf agent test run` | Execute tests | `sf agent test run --api-name Test --wait 10 --target-org alias` |
| `sf agent test results` | Get results | `sf agent test results --job-id ID --result-format json` |
| `sf agent test resume` | Resume async test | `sf agent test resume --use-most-recent --target-org alias` |
| `sf agent test list` | List test runs | `sf agent test list --target-org alias` |

### Preview Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf agent preview` | Interactive testing | `sf agent preview --api-name Agent --target-org alias` |
| `--use-live-actions` | Use real Flows/Apex | `sf agent preview --use-live-actions --client-app App` |
| `--output-dir` | Save transcripts | `sf agent preview --output-dir ./logs` |
| `--apex-debug` | Capture debug logs | `sf agent preview --apex-debug` |

### Result Formats

| Format | Use Case | Flag |
|--------|----------|------|
| `human` | Terminal display (default) | `--result-format human` |
| `json` | CI/CD parsing | `--result-format json` |
| `junit` | Test reporting | `--result-format junit` |
| `tap` | Test Anything Protocol | `--result-format tap` |

---

## Multi-Turn Test Templates

| Template | Pattern | Scenarios | Location |
|----------|---------|-----------|----------|
| `multi-turn-topic-routing.yaml` | Topic switching | 4 | `templates/` |
| `multi-turn-context-preservation.yaml` | Context retention | 4 | `templates/` |
| `multi-turn-escalation-flows.yaml` | Escalation cascades | 4 | `templates/` |
| `multi-turn-comprehensive.yaml` | All 6 patterns | 6 | `templates/` |

### CLI Test Templates

| Template | Purpose | Location |
|----------|---------|----------|
| `basic-test-spec.yaml` | Quick start (3-5 tests) | `templates/` |
| `comprehensive-test-spec.yaml` | Full coverage (20+ tests) | `templates/` |
| `guardrail-tests.yaml` | Security/safety scenarios | `templates/` |
| `escalation-tests.yaml` | Human handoff scenarios | `templates/` |
| `standard-test-spec.yaml` | Reference format | `templates/` |

---

## Cross-Skill Integration

**Required Delegations:**

| Scenario | Skill to Call | Command |
|----------|---------------|---------|
| Fix agent script | sf-ai-agentscript | `Skill(skill="sf-ai-agentscript", args="Fix...")` |
| Create test data | sf-data | `Skill(skill="sf-data", args="Create...")` |
| Fix failing Flow | sf-flow | `Skill(skill="sf-flow", args="Fix...")` |
| Setup ECA or OAuth | sf-connected-apps | `Skill(skill="sf-connected-apps", args="Create...")` |
| Analyze debug logs | sf-debug | `Skill(skill="sf-debug", args="Analyze...")` |
| Session observability | sf-ai-agentforce-observability | `Skill(skill="sf-ai-agentforce-observability", args="Analyze...")` |

---

## Automated Testing (Python Scripts)

| Script | Purpose |
|--------|---------|
| `generate-test-spec.py` | Parse .agent files, generate YAML test specs |
| `run-automated-tests.py` | Orchestrate full test workflow with fix suggestions |

**Quick Usage:**
```bash
# Generate test spec from agent file
python3 hooks/scripts/generate-test-spec.py \
  --agent-file /path/to/Agent.agent \
  --output specs/Agent-tests.yaml

# Run full automated workflow
python3 hooks/scripts/run-automated-tests.py \
  --agent-name MyAgent \
  --agent-dir /path/to/project \
  --target-org dev
```

---

## 🔄 Automated Test-Fix Loop

> **v2.0.0** | Supports both multi-turn API failures and CLI test failures

### Quick Start

```bash
# Run the test-fix loop (CLI tests)
./hooks/scripts/test-fix-loop.sh Test_Agentforce_v1 AgentforceTesting 3

# Exit codes:
#   0 = All tests passed
#   1 = Fixes needed (Claude Code should invoke sf-ai-agentforce)
#   2 = Max attempts reached, escalate to human
#   3 = Error (org unreachable, test not found, etc.)
```

### Claude Code Integration

```
USER: Run automated test-fix loop for Coral_Cloud_Agent

CLAUDE CODE:
1. Phase A: Run multi-turn scenarios via Agent Runtime API
2. Analyze failures (10 categories)
3. If fixable: Skill(skill="sf-ai-agentscript", args="Fix...")
4. Re-run failed scenarios
5. Phase B (if available): Run CLI tests
6. Repeat until passing or max retries (3)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CURRENT_ATTEMPT` | Current attempt number | 1 |
| `MAX_WAIT_MINUTES` | Timeout for test execution | 10 |
| `SKIP_TESTS` | Comma-separated test names to skip | (none) |
| `VERBOSE` | Enable detailed output | false |

---

## 💡 Key Insights

| Problem | Symptom | Solution |
|---------|---------|----------|
| **`sf agent test create` fails** | "Required fields are missing: [MasterLabel]" | Use `sf agent generate test-spec` (interactive) or UI instead |
| Tests fail silently | No results returned | Agent not published - run `sf agent publish authoring-bundle` |
| Topic not matched | Wrong topic selected | Add keywords to topic description |
| Action not invoked | Action never called | Improve action description |
| Live preview 401 | Authentication error | Connected App not configured |
| API 401 | Token expired or wrong credentials | Re-authenticate ECA |
| API 404 on session create | Wrong Agent ID | Re-query BotDefinition for correct Id |
| Empty API response | Agent not activated | Activate and publish agent |
| Context lost between turns | Agent re-asks for known info | Add context retention instructions to topic |
| Topic doesn't switch | Agent stays on old topic | Add transition phrases to target topic |
| **⚠️ `--use-most-recent` broken** | **"Nonexistent flag" error** | **Use `--job-id` explicitly** |
| **Topic name mismatch** | **Expected `GeneralCRM`, got `MigrationDefaultTopic`** | **Verify actual topic names from first test run** |
| **Action superset matching** | **Expected `[A]`, actual `[A,B]` but PASS** | **CLI uses SUPERSET logic** |

---

## Quick Start Example

### Multi-Turn API Testing (Recommended)
```bash
# 1. Get agent ID
AGENT_ID=$(sf data query --use-tooling-api \
  --query "SELECT Id FROM BotDefinition WHERE DeveloperName='My_Agent' AND IsActive=true LIMIT 1" \
  --result-format json --target-org dev | jq -r '.result.records[0].Id')

# 2. Get access token (ECA credentials from conversation)
SF_TOKEN=$(curl -s -X POST "https://${SF_MY_DOMAIN}/services/oauth2/token" \
  -d "grant_type=client_credentials&client_id=${KEY}&client_secret=${SECRET}" \
  | jq -r '.access_token')

# 3. Create session
SESSION_ID=$(curl -s -X POST \
  "https://api.salesforce.com/einstein/ai-agent/v1/agents/${AGENT_ID}/sessions" \
  -H "Authorization: Bearer ${SF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"externalSessionKey":"'"$(uuidgen | tr A-Z a-z)"'",
       "instanceConfig":{"endpoint":"https://'"${SF_MY_DOMAIN}"'"},
       "streamingCapabilities":{"chunkTypes":["Text"]},
       "bypassUser":true}' | jq -r '.sessionId')

# 4. Send multi-turn messages (increment sequenceId)
# ... (see Phase A4 above)

# 5. End session
curl -s -X DELETE \
  "https://api.salesforce.com/einstein/ai-agent/v1/sessions/${SESSION_ID}" \
  -H "Authorization: Bearer ${SF_TOKEN}"
```

### CLI Testing (If Agent Testing Center Available)
```bash
# 1. Generate test spec
python3 hooks/scripts/generate-test-spec.py \
  --agent-file ./agents/MyAgent.agent \
  --output ./tests/myagent-tests.yaml

# 2. Create test in org
sf agent test create --spec ./tests/myagent-tests.yaml --api-name MyAgentTest --target-org dev

# 3. Run tests
sf agent test run --api-name MyAgentTest --wait 10 --result-format json --target-org dev

# 4. View results (use --job-id, NOT --use-most-recent)
sf agent test results --job-id [JOB_ID] --verbose --result-format json --target-org dev
```

---

## 🐛 Known Issues & CLI Bugs

> **Last Updated**: 2026-02-02 | **Tested With**: sf CLI v2.118.16+

### CRITICAL: `sf agent test create` MasterLabel Bug

**Status**: 🔴 BLOCKING - Prevents YAML-based test creation

**Error**: `Required fields are missing: [MasterLabel]`

**Root Cause**: CLI generates XML from YAML but omits the required `<name>` element.

**Workarounds**:
1. ✅ Use `sf agent generate test-spec --from-definition` (correct format)
2. ✅ Use interactive `sf agent generate test-spec` wizard
3. ✅ Create tests via Salesforce Testing Center UI
4. ✅ Deploy XML metadata directly
5. ✅ **Use Phase A (Agent Runtime API) instead** — bypasses CLI entirely

### MEDIUM: Interactive Mode Not Scriptable

**Status**: 🟡 Blocks CI/CD automation

**Issue**: `sf agent generate test-spec` only works interactively.

**Workaround**: Use Python scripts in `hooks/scripts/` or Phase A multi-turn templates.

### MEDIUM: YAML vs XML Format Discrepancy

**Key Mappings**:
| YAML Field | XML Element |
|------------|-------------|
| `expectedTopic` | `topic_sequence_match` |
| `expectedActions` | `action_sequence_match` |
| `expectedOutcome` | `bot_response_rating` |

### LOW: `--use-most-recent` Not Implemented

**Status**: Flag documented but NOT functional. Always use `--job-id` explicitly.

---

## License

MIT License. See LICENSE file.
Copyright (c) 2024-2026 Jag Valaiyapathy
