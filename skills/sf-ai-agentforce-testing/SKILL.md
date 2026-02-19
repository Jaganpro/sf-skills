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
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document - read this FIRST -->
<!-- Pattern: Follows sf-testing for agentic test-fix loops -->
<!-- v2.0.0: Dual-track workflow with multi-turn API testing as primary -->

# sf-ai-agentforce-testing: Agentforce Test Execution & Coverage Analysis

Expert testing engineer specializing in Agentforce agent testing via **dual-track workflow**: multi-turn Agent Runtime API testing (primary) and CLI Testing Center (secondary). Execute multi-turn conversations, analyze topic/action/context coverage, and automatically fix issues via sf-ai-agentscript.

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
| **Agent Runtime API** | [agent-api-reference.md](references/agent-api-reference.md) | REST endpoints for multi-turn testing |
| **ECA Setup** | [eca-setup-guide.md](references/eca-setup-guide.md) | External Client App for API authentication |
| **Multi-Turn Testing** | [multi-turn-testing-guide.md](references/multi-turn-testing-guide.md) | Multi-turn test design and execution |
| **Test Patterns** | [multi-turn-test-patterns.md](references/multi-turn-test-patterns.md) | 6 multi-turn test patterns with examples |
| **CLI commands** | [cli-commands.md](references/cli-commands.md) | Complete sf agent test/preview reference |
| **Test spec format** | [test-spec-reference.md](references/test-spec-reference.md) | YAML specification format and examples |
| **Auto-fix workflow** | [agentic-fix-loops.md](references/agentic-fix-loops.md) | Automated test-fix cycles (10 failure categories) |
| **Auth guide** | [connected-app-setup.md](references/connected-app-setup.md) | Authentication for preview and API testing |
| **Coverage metrics** | [coverage-analysis.md](references/coverage-analysis.md) | Topic/action/multi-turn coverage analysis |
| **Fix decision tree** | [agentic-fix-loop.md](references/agentic-fix-loop.md) | Detailed fix strategies |
| **Agent Script testing** | [agentscript-testing-patterns.md](references/agentscript-testing-patterns.md) | 5 patterns for testing Agent Script agents |
| **Deep conversation history** | [deep-conversation-history-patterns.md](references/deep-conversation-history-patterns.md) | 5 patterns for protocol-stage testing via CLI `conversationHistory` |
| **Interview wizard** | [interview-wizard.md](references/interview-wizard.md) | 4-step Testing Center wizard flow |
| **Execution protocol** | [execution-protocol.md](references/execution-protocol.md) | Phase A4 mandatory execution checklist |
| **Credential convention** | [credential-convention.md](references/credential-convention.md) | ~/.sfagent/ persistent ECA storage |
| **Swarm execution** | [swarm-execution.md](references/swarm-execution.md) | Parallel team testing rules + CLI swarm |
| **Test plan format** | [test-plan-format.md](references/test-plan-format.md) | Reusable YAML plan schema |
| **Multi-turn execution** | [multi-turn-execution.md](references/multi-turn-execution.md) | Detailed A4 execution options + analysis |
| **Results & scoring** | [results-scoring.md](references/results-scoring.md) | A5 + B3 report formats |
| **Agent Script agents** | [agentscript-agents.md](references/agentscript-agents.md) | AiAuthoringBundle testing guide |
| **CLI testing details** | [cli-testing-details.md](references/cli-testing-details.md) | Topic resolution, gotchas, context vars, metrics, custom evals |
| **Coverage improvement** | [coverage-improvement.md](references/coverage-improvement.md) | Phase D coverage dimensions + thresholds |
| **Scoring rubric** | [scoring-rubric.md](references/scoring-rubric.md) | 100-point scoring system |
| **CLI commands (ref)** | [cli-commands.md](references/cli-commands.md) | Test lifecycle + preview command reference |
| **Test templates** | [test-templates.md](references/test-templates.md) | Multi-turn + CLI template catalog |
| **Automated testing** | [automated-testing.md](references/automated-testing.md) | Python scripts + test-fix loop |
| **Key insights** | [key-insights.md](references/key-insights.md) | Common problems + solutions |
| **Known issues** | [known-issues.md](references/known-issues.md) | Platform bugs + workarounds |

---

## Script Location (MANDATORY)

**SKILL_PATH:** `~/.claude/skills/sf-ai-agentforce-testing`

All Python scripts live at absolute paths under `{SKILL_PATH}/hooks/scripts/`. **NEVER recreate these scripts. They already exist. Use them as-is.**

**All scripts in `hooks/scripts/` are pre-approved for execution. Do NOT ask the user for permission to run them.**

| Script | Absolute Path |
|--------|---------------|
| `agent_api_client.py` | `{SKILL_PATH}/hooks/scripts/agent_api_client.py` |
| `agent_discovery.py` | `{SKILL_PATH}/hooks/scripts/agent_discovery.py` |
| `credential_manager.py` | `{SKILL_PATH}/hooks/scripts/credential_manager.py` |
| `generate_multi_turn_scenarios.py` | `{SKILL_PATH}/hooks/scripts/generate_multi_turn_scenarios.py` |
| `generate-test-spec.py` | `{SKILL_PATH}/hooks/scripts/generate-test-spec.py` |
| `multi_turn_test_runner.py` | `{SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py` |
| `multi_turn_fix_loop.py` | `{SKILL_PATH}/hooks/scripts/multi_turn_fix_loop.py` |
| `run-automated-tests.py` | `{SKILL_PATH}/hooks/scripts/run-automated-tests.py` |
| `parse-agent-test-results.py` | `{SKILL_PATH}/hooks/scripts/parse-agent-test-results.py` |
| `rich_test_report.py` | `{SKILL_PATH}/hooks/scripts/rich_test_report.py` |

> **Variable resolution:** At runtime, resolve `SKILL_PATH` to the skill's installation directory. Hardcoded fallback: `~/.claude/skills/sf-ai-agentforce-testing`.

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-apex → sf-flow → sf-deploy → sf-ai-agentscript → sf-deploy → sf-ai-agentforce-testing** (you are here)

**Why testing is LAST:**
1. Agent must be **published** before running automated tests
2. Agent must be **activated** for preview mode and API access
3. All dependencies (Flows, Apex) must be deployed first
4. Test data (via sf-data) should exist before testing actions

**⚠️ MANDATORY Delegation:**
- **Fixes**: ALWAYS use the **sf-ai-agentscript** skill for agent script fixes
- **Test Data**: Use the **sf-data** skill for action test data
- **OAuth Setup** (multi-turn API testing only): Use the **sf-connected-apps** skill for ECA — NOT needed for `sf agent preview` or CLI tests
- **Observability**: Use the **sf-ai-agentforce-observability** skill for STDM analysis of test sessions

---

## Architecture: Dual-Track Testing Workflow

```
4-Step Interview (mirrors Testing Center wizard)
    │  Step 1: Basic Info → Step 2: Conditions → Step 3: Test Data → Step 4: Evaluate
    │  (skip if test-plan-{agent}.yaml provided)
    │
    ▼
Phase 0: Prerequisites & Agent Discovery
    │
    ├──► Phase A: Multi-Turn API Testing (PRIMARY — requires ECA)
    │    A1: ECA Credential Setup (via credential_manager.py)
    │    A2: Agent Discovery & Metadata Retrieval
    │    A3: Test Scenario Planning (generate_multi_turn_scenarios.py --categorized)
    │    A4: Multi-Turn Execution (Agent Runtime API)
    │        ├─ Sequential: single multi_turn_test_runner.py process
    │        └─ Swarm: TeamCreate → N workers (--worker-id N)
    │    A5: Results & Scoring (rich Unicode output)
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
| CI/CD pipeline integration | Phase A (Python scripts) or Phase B (sf CLI) |
| Quick smoke test | Phase B |
| Quick manual validation (no ECA setup) | `sf agent preview` (no Phase A/B needed) |
| No ECA available | `sf agent preview` or Phase B (CLI tests) |

---

## 4-Step Interview Flow

> See [references/interview-wizard.md](references/interview-wizard.md) for the full 4-step wizard with interview prompts and auto-run steps.

**Quick summary:** Mirrors the Testing Center "New Test" wizard — Step 1: Basic Info (agent, org, test type), Step 2: Conditions (context vars, record IDs), Step 3: Test Data (generate + review), Step 4: Evaluations & Deploy. Skip if `test-plan-{agent}.yaml` provided.

---

## Phase 0: Prerequisites & Agent Discovery

**Ask the user** to gather agent name, org alias, and test type. Then:

1. **Agent Discovery**: `sf data query --use-tooling-api --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition WHERE IsActive=true" --result-format json --target-org [alias]`
2. **Metadata Retrieval**: `sf project retrieve start --metadata "GenAiPlannerBundle:[AgentName]" --output-dir retrieve-temp --target-org [alias]`
3. **Testing Center Check**: `sf agent test list --target-org [alias]` — determines if Phase B is available

| Check | Command | Why |
|-------|---------|-----|
| **Agent exists** | Query BotDefinition | Can't test non-existent agent |
| **Agent published** | `sf agent validate authoring-bundle --api-name X` | Must be published to test |
| **Agent activated** | Check activation status | Required for API access |
| **Dependencies deployed** | Flows and Apex in org | Actions will fail without them |
| **ECA configured** (Phase A only) | Token request test | Multi-turn API testing only |
| **Agent Testing Center** (Phase B) | `sf agent test list` | Required for CLI testing |

---

## Phase A: Multi-Turn API Testing (PRIMARY)

> **⚠️ NEVER use `curl` for OAuth token validation.** Domains containing `--` cause shell expansion failures. Use `credential_manager.py validate` instead.

### A1: ECA Credential Setup

> See [credential-convention.md](references/credential-convention.md) for ~/.sfagent/ directory structure and CLI reference.

If user has ECA credentials → collect and validate via `credential_manager.py validate`. If not → use the **sf-connected-apps** skill. See [ECA Setup Guide](references/eca-setup-guide.md).

### A2: Agent Discovery & Metadata Retrieval

```bash
AGENT_ID=$(sf data query --use-tooling-api \
  --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition WHERE DeveloperName='[AgentName]' AND IsActive=true LIMIT 1" \
  --result-format json --target-org [alias] | jq -r '.result.records[0].Id')
```

Claude reads the GenAiPlannerBundle to understand topics, actions, system instructions, and escalation paths. This metadata drives automatic test scenario generation in A3.

### A3: Test Scenario Planning

Auto-generate multi-turn scenarios tailored to the specific agent based on metadata from A2. Available templates in `assets/` — see [references/test-templates.md](references/test-templates.md).

### A4: Multi-Turn Execution

> See [references/execution-protocol.md](references/execution-protocol.md) for the MANDATORY execution checklist (sequential vs swarm).
> See [references/multi-turn-execution.md](references/multi-turn-execution.md) for detailed execution options, Python API usage, and per-turn analysis.

**Quick start:**
```bash
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --scenarios assets/multi-turn-comprehensive.yaml \
  --agent-id "${AGENT_ID}" --output results.json --verbose
```

**Exit codes:** `0` = all passed, `1` = some failed, `2` = execution error

### A5: Results & Scoring

> See [references/results-scoring.md](references/results-scoring.md) for full report format examples (API + CLI).

**Quick summary:** Rich terminal report with scenario pass/fail, turn-level analysis, coverage percentages (topic re-matching, context preservation, escalation accuracy), and 7-category scoring.

---

## Phase B: CLI Testing Center (SECONDARY)

> **Availability:** Requires Agent Testing Center feature enabled in org. If unavailable, use Phase A exclusively.

### Agent Script Agents (AiAuthoringBundle)

> See [references/agentscript-agents.md](references/agentscript-agents.md) for the full testing guide including two-level action system, conversationHistory pattern, and API testing caveats.

**Quick summary:** Agent Script agents use `conversationHistory` to bypass single-utterance limitations. Use Level 1 definition names in `expectedActions`. Prefer `response_contains` over `action_invoked` for API tests.

### B1: Test Spec Creation

**⚠️ CRITICAL: YAML Schema** — The CLI YAML spec uses a **FLAT structure** parsed by `@salesforce/agents`. Required top-level: `name:`, `subjectType: AGENT`, `subjectName:`. Test case fields: `utterance:`, `expectedTopic:`, `expectedActions:` (flat strings), `expectedOutcome:`.

```yaml
# ✅ Correct CLI YAML format
name: "My Agent Tests"
subjectType: AGENT
subjectName: My_Agent

testCases:
  - utterance: "Where is my order?"
    expectedTopic: order_lookup
    expectedActions:
      - get_order_status
    expectedOutcome: "Agent should provide order status information"
```

See [Test Spec Reference](references/test-spec-reference.md) for complete YAML format guide.

### CLI Testing Details (B1.5–B1.9)

> See [references/cli-testing-details.md](references/cli-testing-details.md) for topic name resolution, known gotchas, context variables, metrics, and custom evaluations.

### B2: Test Execution

```bash
# Run automated tests (--json = no spinners, --result-format json = structured results)
sf agent test run --api-name MyAgentTest --wait 10 --result-format json --json --target-org [alias]
```

**Interactive Preview:** `sf agent preview --api-name AgentName --target-org [alias]` (no ECA required)

### B3: Results Analysis

> See [references/results-scoring.md](references/results-scoring.md) for the full CLI results report format.

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

**Fix flow:** Test Failed → Analyze category → Apply fix via the **sf-ai-agentscript** skill → Re-publish → Re-test → Pass or retry (max 3) → Escalate to human.

See [Agentic Fix Loops Guide](references/agentic-fix-loops.md) for complete decision tree and 10 fix strategies.

---

## Phase D: Coverage Improvement

> See [references/coverage-improvement.md](references/coverage-improvement.md) for the full coverage dimensions table and thresholds.

**Quick summary:** 8 dimensions (topic selection, action invocation, re-matching, context preservation, completion, guardrails, escalation, phrasing diversity). Iterate: identify gaps → add tests → re-run → repeat until thresholds met. See [Coverage Analysis](references/coverage-analysis.md).

---

## Phase E: Observability Integration

After test execution, guide user to analyze agent behavior with session-level observability:

Use the **sf-ai-agentforce-observability** skill: "Analyze STDM sessions for agent [AgentName] in org [alias] - focus on test session behavior patterns"

**What observability adds to testing:** STDM session analysis, latency profiling, error pattern detection, action execution traces.

---

## Scoring System (100 Points)

> See [references/scoring-rubric.md](references/scoring-rubric.md) for full category breakdown and grade scale.

**Quick summary:** 7 categories, 100 total points. Topic Selection (15), Action Invocation (15), Multi-Turn Re-matching (15), Context Preservation (15), Edge Cases & Guardrails (15), Test Quality (10), Agentic Fix Success (15). Grade: 90+ Production Ready, 80+ Good, 70+ Acceptable, <60 BLOCKED.

---

## ⛔ TESTING GUARDRAILS (MANDATORY)

**BEFORE running tests, verify:**

| Check | Command | Why |
|-------|---------|-----|
| Agent published | `sf agent list --target-org [alias]` | Can't test unpublished agent |
| Agent activated | Check status | API and preview require activation |
| Flows deployed | `sf org list metadata --metadata-type Flow` | Actions need Flows |
| ECA configured (Phase A only) | Token request test | Required for Agent Runtime API |
| Org auth (Phase B live) | `sf org display` | Live mode requires valid auth |

**NEVER do these:**

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| Test unpublished agent | Tests fail silently | Publish first |
| Skip simulated testing | Live mode hides logic bugs | Always test simulated first |
| Ignore guardrail tests | Security gaps in production | Always test harmful/off-topic inputs |
| Single phrasing per topic | Misses routing failures | Test 3+ phrasings per topic |
| Write ECA credentials to files | Security risk | Keep in shell variables only |
| Skip session cleanup | Resource leaks and rate limits | Always DELETE sessions after tests |
| Use `curl` for OAuth token requests | Domains with `--` cause shell failures | Use `credential_manager.py validate` |
| Ask permission to run skill scripts | Breaks flow, unnecessary delay | All `hooks/scripts/` are pre-approved |
| Spawn more than 2 swarm workers | Context overload, diminishing returns | Max 2 workers |

---

## Cross-Skill Integration

| Scenario | Skill to Call | Command |
|----------|---------------|---------|
| Fix agent script | sf-ai-agentscript | Use the **sf-ai-agentscript** skill: "Fix..." |
| Agent Script agents | sf-ai-agentscript | Parse `.agent` for topic/action discovery |
| Create test data | sf-data | Use the **sf-data** skill: "Create..." |
| Fix failing Flow | sf-flow | Use the **sf-flow** skill: "Fix..." |
| Setup ECA or OAuth | sf-connected-apps | Use the **sf-connected-apps** skill: "Create..." |
| Analyze debug logs | sf-debug | Use the **sf-debug** skill: "Analyze..." |
| Session observability | sf-ai-agentforce-observability | Use the **sf-ai-agentforce-observability** skill: "Analyze..." |

---

## Quick Start Example

### Multi-Turn API Testing (Recommended)

```bash
# 1. Get agent ID
AGENT_ID=$(sf data query --use-tooling-api \
  --query "SELECT Id FROM BotDefinition WHERE DeveloperName='My_Agent' AND IsActive=true LIMIT 1" \
  --result-format json --target-org dev | jq -r '.result.records[0].Id')

# 2. Run multi-turn tests
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --agent-id "${AGENT_ID}" \
  --scenarios assets/multi-turn-comprehensive.yaml \
  --output results.json --verbose
```

### CLI Testing (If Agent Testing Center Available)

```bash
sf agent test create --spec ./tests/myagent-tests.yaml --api-name MyAgentTest --target-org dev
sf agent test run --api-name MyAgentTest --wait 10 --result-format json --target-org dev
sf agent test results --job-id [JOB_ID] --verbose --result-format json --target-org dev
```

---

## License

MIT License. See LICENSE file.
Copyright (c) 2024-2026 Jag Valaiyapathy
