---
name: sf-ai-agentforce-testing
description: >
  Comprehensive Agentforce testing skill with test execution, coverage analysis,
  and agentic fix loops. Run agent tests via sf CLI, analyze topic/action coverage,
  generate test specs, and automatically fix failing agents with 100-point scoring.
license: MIT
compatibility: "Requires API v65.0+ (Winter '26) and Agentforce enabled org"
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 5 categories"
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document - read this FIRST -->
<!-- Pattern: Follows sf-testing for agentic test-fix loops -->

# sf-ai-agentforce-testing: Agentforce Test Execution & Coverage Analysis

Expert testing engineer specializing in Agentforce agent testing, topic/action coverage analysis, and agentic fix loops. Execute agent tests, analyze failures, and automatically fix issues via sf-ai-agentforce.

## Core Responsibilities

1. **Test Execution**: Run agent tests via `sf agent test run` with coverage analysis
2. **Test Spec Generation**: Create YAML test specifications for agents
3. **Coverage Analysis**: Track topic selection accuracy, action invocation rates
4. **Preview Testing**: Interactive simulated and live agent testing
5. **Agentic Fix Loop**: Automatically fix failing agents and re-test
6. **Cross-Skill Orchestration**: Delegate fixes to sf-ai-agentforce, data to sf-data

## 📚 Document Map

| Need | Document | Description |
|------|----------|-------------|
| **CLI commands** | [cli-commands.md](docs/cli-commands.md) | Complete sf agent test/preview reference |
| **Test spec format** | [test-spec-reference.md](resources/test-spec-reference.md) | YAML specification format and examples |
| **Auto-fix workflow** | [agentic-fix-loops.md](resources/agentic-fix-loops.md) | Automated test-fix cycles and Python scripts |
| **Live preview setup** | [connected-app-setup.md](docs/connected-app-setup.md) | OAuth for live preview mode |
| **Coverage metrics** | [coverage-analysis.md](docs/coverage-analysis.md) | Topic/action coverage analysis |
| **Fix decision tree** | [agentic-fix-loop.md](docs/agentic-fix-loop.md) | Detailed fix strategies |

**⚡ Quick Links:**
- [Scoring System](#scoring-system-100-points) - 5-category validation
- [CLI Command Reference](#cli-command-reference) - Essential commands
- [Agentic Fix Loop](#phase-5-agentic-fix-loop) - Auto-fix workflow
- [Test Spec Reference](resources/test-spec-reference.md) - Complete YAML format guide
- [Automated Testing](resources/agentic-fix-loops.md) - Python scripts and workflows

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-apex → sf-flow → sf-deploy → sf-ai-agentforce → sf-deploy → sf-ai-agentforce-testing** (you are here)

**Why testing is LAST:**
1. Agent must be **published** before running automated tests
2. Agent must be **activated** for preview mode
3. All dependencies (Flows, Apex) must be deployed first
4. Test data (via sf-data) should exist before testing actions

**⚠️ MANDATORY Delegation:**
- **Fixes**: ALWAYS use `Skill(skill="sf-ai-agentforce")` for agent script fixes
- **Test Data**: Use `Skill(skill="sf-data")` for action test data
- **OAuth Setup**: Use `Skill(skill="sf-connected-apps")` for live preview

---

## ⚠️ CRITICAL: Org Requirements (Agent Testing Center)

**Agent testing requires the Agent Testing Center feature**, which is NOT enabled by default in all orgs.

### Check if Agent Testing Center is Enabled

```bash
# This will fail if Agent Testing Center is not enabled
sf agent test list --target-org [alias]

# Expected errors if NOT enabled:
# "Not available for deploy for this organization"
# "INVALID_TYPE: Cannot use: AiEvaluationDefinition in this organization"
```

### Orgs WITHOUT Agent Testing Center

| Org Type | Agent Testing | Workaround |
|----------|---------------|------------|
| Standard DevHub | ❌ Not available | Request feature enablement |
| SDO Demo Orgs | ❌ Not available | Use scratch org with feature |
| Scratch Orgs | ✅ If feature enabled | Include in scratch-def.json |

### Enabling Agent Testing Center

1. **Scratch Org** - Add to scratch-def.json:
   ```json
   {
     "features": ["AgentTestingCenter", "EinsteinGPTForSalesforce"]
   }
   ```

2. **Production/Sandbox** - Contact Salesforce to enable the feature

3. **Fallback** - Use `sf agent preview` for manual testing (see [Automated Testing Guide](resources/agentic-fix-loops.md))

---

## ⚠️ CRITICAL: Prerequisites Checklist

Before running agent tests, verify:

| Check | Command | Why |
|-------|---------|-----|
| **Agent Testing Center enabled** | `sf agent test list --target-org [alias]` | ⚠️ **CRITICAL** - tests will fail without this |
| **Agent exists** | `sf data query --use-tooling-api --query "SELECT Id FROM BotDefinition WHERE DeveloperName='X'"` | Can't test non-existent agent |
| **Agent published** | `sf agent validate authoring-bundle --api-name X` | Must be published to test |
| **Agent activated** | Check activation status | Required for preview mode |
| **Dependencies deployed** | Flows and Apex in org | Actions will fail without them |
| **Connected App** (live) | OAuth configured | Required for `--use-live-actions` |

---

## Workflow (6-Phase Pattern)

### Phase 1: Prerequisites

Use **AskUserQuestion** to gather:
- Agent name/API name
- Target org alias
- Test mode (simulated vs live)
- Coverage threshold (default: 80%)
- Enable agentic fix loop?

**Then**:
1. Verify agent is published and activated
2. Check for existing test specs: `Glob: **/*.yaml`, `Glob: **/tests/*.yaml`
3. Create TodoWrite tasks

### Phase 2: Test Spec Creation

**Option A: Interactive Generation** (no automation available)
```bash
# Interactive test spec generation
sf agent generate test-spec --output-file ./tests/agent-spec.yaml

# ⚠️ NOTE: There is NO --api-name flag! The command is interactive-only.
```

**Option B: Automated Generation** (Python script)
```bash
# Generate from agent file
python3 hooks/scripts/generate-test-spec.py \
  --agent-file /path/to/Agent.agent \
  --output tests/agent-spec.yaml \
  --verbose
```

See [Test Spec Reference](resources/test-spec-reference.md) for complete YAML format guide.

**Create Test in Org**:
```bash
sf agent test create --spec ./tests/agent-spec.yaml --api-name MyAgentTest --target-org [alias]
```

### Phase 3: Test Execution

**Automated Tests**:
```bash
sf agent test run --api-name MyAgentTest --wait 10 --result-format json --target-org [alias]
```

**Interactive Preview (Simulated)**:
```bash
sf agent preview --api-name AgentName --output-dir ./logs --target-org [alias]
```

**Interactive Preview (Live)**:
```bash
sf agent preview --api-name AgentName --use-live-actions --client-app AppName --apex-debug --target-org [alias]
```

### Phase 4: Results Analysis

Parse test results JSON and display formatted summary:

```
📊 AGENT TEST RESULTS
════════════════════════════════════════════════════════════════

Agent: Customer_Support_Agent
Org: my-sandbox
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

### Phase 5: Agentic Fix Loop

**When tests fail, automatically fix via sf-ai-agentforce:**

| Error Category | Root Cause | Auto-Fix Strategy |
|----------------|------------|-------------------|
| `TOPIC_NOT_MATCHED` | Topic description doesn't match utterance | Add keywords to topic description |
| `ACTION_NOT_INVOKED` | Action description not triggered | Improve action description |
| `WRONG_ACTION_SELECTED` | Wrong action chosen | Differentiate descriptions |
| `ACTION_FAILED` | Flow/Apex error | Delegate to sf-flow or sf-apex |
| `GUARDRAIL_NOT_TRIGGERED` | System instructions permissive | Add explicit guardrails |

**Auto-Fix Command Example**:
```bash
Skill(skill="sf-ai-agentforce", args="Fix agent [AgentName] - Error: [category] - [details]")
```

**See [Agentic Fix Loops Guide](resources/agentic-fix-loops.md) for:**
- Complete decision tree
- Detailed fix strategies for each error type
- Cross-skill orchestration workflow
- Python scripts for automated testing
- Example fix loop executions

### Phase 6: Coverage Improvement

**If coverage < threshold**:

1. Identify untested topics/actions from results
2. Add test cases to spec YAML
3. Update test: `sf agent test create --spec ./tests/agent-spec.yaml --force-overwrite`
4. Re-run: `sf agent test run --api-name MyAgentTest --wait 10`

---

## Scoring System (100 Points)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Topic Selection Coverage** | 25 | All topics have test cases; various phrasings tested |
| **Action Invocation** | 25 | All actions tested with valid inputs/outputs |
| **Edge Case Coverage** | 20 | Negative tests; empty inputs; special characters; boundaries |
| **Test Spec Quality** | 15 | Proper YAML; descriptions provided; categories assigned |
| **Agentic Fix Success** | 15 | Auto-fixes resolve issues within 3 attempts |

**Scoring Thresholds**:
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
| Agent activated | Check status | Preview requires activation |
| Flows deployed | `sf org list metadata --metadata-type Flow` | Actions need Flows |
| Connected App (live) | Check OAuth | Live mode requires auth |

**NEVER do these:**

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| Test unpublished agent | Tests fail silently | Publish first: `sf agent publish authoring-bundle` |
| Skip simulated testing | Live mode hides logic bugs | Always test simulated first |
| Ignore guardrail tests | Security gaps in production | Always test harmful/off-topic inputs |
| Single phrasing per topic | Misses routing failures | Test 3+ phrasings per topic |

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

## Test Spec Quick Reference

**Basic Template:**
```yaml
subjectType: AGENT
subjectName: <Agent_Name>

testCases:
  # Topic routing
  - utterance: "What's on your menu?"
    expectation:
      topic: product_faq
      actionSequence: []

  # Action invocation
  - utterance: "Search for Harry Potter books"
    expectation:
      topic: book_search
      actionSequence:
        - search_catalog

  # Edge case
  - utterance: ""
    expectation:
      graceful_handling: true
```

**For complete YAML format reference, see [Test Spec Reference](resources/test-spec-reference.md)**

---

## Cross-Skill Integration

**Required Delegations:**

| Scenario | Skill to Call | Command |
|----------|---------------|---------|
| Fix agent script | sf-ai-agentforce | `Skill(skill="sf-ai-agentforce", args="Fix...")` |
| Create test data | sf-data | `Skill(skill="sf-data", args="Create...")` |
| Fix failing Flow | sf-flow | `Skill(skill="sf-flow", args="Fix...")` |
| Setup OAuth | sf-connected-apps | `Skill(skill="sf-connected-apps", args="Create...")` |
| Analyze debug logs | sf-debug | `Skill(skill="sf-debug", args="Analyze...")` |

**For complete orchestration workflow, see [Agentic Fix Loops](resources/agentic-fix-loops.md)**

---

## Automated Testing (Python Scripts)

This skill includes Python scripts for fully automated agent testing:

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

**For complete documentation, see [Agentic Fix Loops Guide](resources/agentic-fix-loops.md)**

---

## Templates Reference

| Template | Purpose | Location |
|----------|---------|----------|
| `basic-test-spec.yaml` | Quick start (3-5 tests) | `templates/` |
| `comprehensive-test-spec.yaml` | Full coverage (20+ tests) | `templates/` |
| `guardrail-tests.yaml` | Security/safety scenarios | `templates/` |
| `escalation-tests.yaml` | Human handoff scenarios | `templates/` |
| `standard-test-spec.yaml` | Reference format | `templates/` |

---

## 💡 Key Insights

| Problem | Symptom | Solution |
|---------|---------|----------|
| Tests fail silently | No results returned | Agent not published - run `sf agent publish authoring-bundle` |
| Topic not matched | Wrong topic selected | Add keywords to topic description (see [Fix Loops](resources/agentic-fix-loops.md)) |
| Action not invoked | Action never called | Improve action description, add explicit reference |
| Live preview 401 | Authentication error | Connected App not configured - use sf-connected-apps |
| Async tests stuck | Job never completes | Use `sf agent test resume --use-most-recent` |
| Empty responses | Agent doesn't respond | Check agent is activated |
| Agent Testing Center unavailable | "INVALID_TYPE" error | Use `sf agent preview` as fallback |

---

## Quick Start Example

```bash
# 1. Check if Agent Testing Center is enabled
sf agent test list --target-org dev

# 2. Generate test spec (automated)
python3 hooks/scripts/generate-test-spec.py \
  --agent-file ./agents/MyAgent.agent \
  --output ./tests/myagent-tests.yaml

# 3. Create test in org
sf agent test create \
  --spec ./tests/myagent-tests.yaml \
  --api-name MyAgentTest \
  --target-org dev

# 4. Run tests
sf agent test run \
  --api-name MyAgentTest \
  --wait 10 \
  --result-format json \
  --target-org dev

# 5. View results
sf agent test results \
  --use-most-recent \
  --verbose \
  --result-format json \
  --target-org dev
```

**For complete workflows and fix loops, see:**
- [Agentic Fix Loops](resources/agentic-fix-loops.md) - Automated testing and fix workflows
- [Test Spec Reference](resources/test-spec-reference.md) - Complete YAML format guide

---

## License

MIT License. See LICENSE file.
Copyright (c) 2024-2025 Jag Valaiyapathy
