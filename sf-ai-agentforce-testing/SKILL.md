---
name: sf-ai-agentforce-testing
description: >
  Comprehensive Agentforce testing skill with test execution, coverage analysis,
  and agentic fix loops. Run agent tests via sf CLI, analyze topic/action coverage,
  generate test specs, and automatically fix failing agents with 100-point scoring.
license: MIT
compatibility: "Requires API v65.0+ (Winter '26) and Agentforce enabled org"
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 5 categories"
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

# sf-ai-agentforce-testing: Agentforce Test Execution & Coverage Analysis

Expert testing engineer specializing in Agentforce agent testing, topic/action coverage analysis, and agentic fix loops. Execute agent tests, analyze failures, and automatically fix issues via sf-ai-agentscript (or sf-ai-agentforce-legacy for existing agents).

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

**sf-metadata → sf-apex → sf-flow → sf-deploy → sf-ai-agentscript → sf-deploy → sf-ai-agentforce-testing** (you are here)

**Why testing is LAST:**
1. Agent must be **published** before running automated tests
2. Agent must be **activated** for preview mode
3. All dependencies (Flows, Apex) must be deployed first
4. Test data (via sf-data) should exist before testing actions

**⚠️ MANDATORY Delegation:**
- **Fixes**: ALWAYS use `Skill(skill="sf-ai-agentscript")` for agent script fixes (or `sf-ai-agentforce-legacy` for existing legacy agents)
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

**When tests fail, automatically fix via sf-ai-agentscript:**

| Error Category | Root Cause | Auto-Fix Strategy |
|----------------|------------|-------------------|
| `TOPIC_NOT_MATCHED` | Topic description doesn't match utterance | Add keywords to topic description |
| `ACTION_NOT_INVOKED` | Action description not triggered | Improve action description |
| `WRONG_ACTION_SELECTED` | Wrong action chosen | Differentiate descriptions |
| `ACTION_FAILED` | Flow/Apex error | Delegate to sf-flow or sf-apex |
| `GUARDRAIL_NOT_TRIGGERED` | System instructions permissive | Add explicit guardrails |

**Auto-Fix Command Example**:
```bash
Skill(skill="sf-ai-agentscript", args="Fix agent [AgentName] - Error: [category] - [details]")
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
| Fix agent script | sf-ai-agentscript | `Skill(skill="sf-ai-agentscript", args="Fix...")` |
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
| **`sf agent test create` fails** | "Required fields are missing: [MasterLabel]" | Use `sf agent generate test-spec` (interactive) or UI instead |
| Tests fail silently | No results returned | Agent not published - run `sf agent publish authoring-bundle` |
| Topic not matched | Wrong topic selected | Add keywords to topic description (see [Fix Loops](resources/agentic-fix-loops.md)) |
| Action not invoked | Action never called | Improve action description, add explicit reference |
| Live preview 401 | Authentication error | Connected App not configured - use sf-connected-apps |
| Async tests stuck | Job never completes | Use `sf agent test resume --use-most-recent` |
| Empty responses | Agent doesn't respond | Check agent is activated |
| Agent Testing Center unavailable | "INVALID_TYPE" error | Use `sf agent preview` as fallback |
| Topic expectation empty | Test always passes topic check | Bug in CLI YAML→XML conversion; use interactive mode |
| **⚠️ `--use-most-recent` broken** | **"Nonexistent flag" error on `sf agent test results`** | **Use `--job-id` explicitly - the flag is documented but NOT implemented** |
| **Topic name mismatch** | **Expected `GeneralCRM`, got `MigrationDefaultTopic`** | **Standard Salesforce copilots route to `MigrationDefaultTopic` - verify actual topic names from first test run** |
| **Test data missing** | **"No matching records" in outcome** | **Verify test utterances reference records that actually exist in org (e.g., "Edge Communications" not "Acme")** |
| **Action assertion fails unexpectedly** | **Expected `[A]`, actual `[A,B]` but marked PASS** | **Action matching uses SUPERSET logic - actual can have MORE actions than expected and still pass** |

---

## 🔄 Two Fix Strategies

When agent tests fail, there are TWO valid approaches:

| Agent Type | Fix Strategy | When to Use |
|------------|--------------|-------------|
| **Custom Agent** (you control it) | Fix the agent via `sf-ai-agentforce` | Topic descriptions, action configurations need adjustment |
| **Managed/Standard Agent** (Salesforce copilot) | Fix test expectations in YAML | Test expectations don't match actual agent behavior |

**Decision Flow:**
```
Test Failed → Can you modify the agent?
                    │
          ┌────────┴────────┐
          ↓                 ↓
         YES                NO
          ↓                 ↓
    Fix Agent          Fix Test Spec
    (sf-ai-agentforce)  (update YAML)
```

**Example: Fixing Test Expectations**
```yaml
# BEFORE (wrong expectations)
expectedTopic: GeneralCRM
expectedActions:
  - IdentifyRecordByName
  - GetRecordDetails

# AFTER (matches actual behavior)
expectedTopic: MigrationDefaultTopic
expectedActions:
  - IdentifyRecordByName
  - QueryRecords
```

---

## 🔄 Automated Test-Fix Loop

> **NEW in v1.1.0** | Claude Code can now orchestrate fully automated test-fix cycles

### Overview

The test-fix loop enables Claude Code to:
1. **Run tests** → `sf agent test run` with JSON output
2. **Analyze failures** → Parse results and categorize issues
3. **Fix agent** → Invoke `sf-ai-agentforce` skill to apply fixes
4. **Retest** → Loop until all tests pass or max retries (3) reached
5. **Escalate** → Skip unfixable tests and continue with others

### Quick Start

```bash
# Run the test-fix loop
./hooks/scripts/test-fix-loop.sh Test_Agentforce_v1 AgentforceTesting 3

# Exit codes:
#   0 = All tests passed
#   1 = Fixes needed (Claude Code should invoke sf-ai-agentforce)
#   2 = Max attempts reached, escalate to human
#   3 = Error (org unreachable, test not found, etc.)
```

### Claude Code Integration

When Claude Code runs the test-fix loop:

```
USER: Run automated test-fix loop for Coral_Cloud_Agent

CLAUDE CODE:
1. bash hooks/scripts/test-fix-loop.sh Test_Agentforce_v1 AgentforceTesting
2. If exit code 1 (FIX_NEEDED):
   - Parse failure details from output
   - Invoke: Skill(skill="sf-ai-agentscript", args="Fix topic X: add keyword Y")
   - Re-run: CURRENT_ATTEMPT=2 bash hooks/scripts/test-fix-loop.sh ...
3. Repeat until exit code 0 (success) or 2 (max retries)
```

### Ralph Wiggum Integration (Hands-Off)

For fully automated loops without user intervention:

```
/ralph-wiggum:ralph-loop
> Run agentic test-fix loop for Test_Agentforce_v1 in AgentforceTesting until all tests pass
```

Claude Code will autonomously:
- Execute test-fix cycles
- Apply fixes via sf-ai-agentscript skill
- Track attempts and escalate when needed
- Report final status

### Failure Categories & Auto-Fix Strategies

| Category | Auto-Fixable | Fix Strategy |
|----------|--------------|--------------|
| `TOPIC_NOT_MATCHED` | ✅ Yes | Add keywords to topic classificationDescription |
| `ACTION_NOT_INVOKED` | ✅ Yes | Improve action description, add trigger conditions |
| `WRONG_ACTION_SELECTED` | ✅ Yes | Differentiate action descriptions |
| `GUARDRAIL_NOT_TRIGGERED` | ✅ Yes | Add explicit guardrails to system instructions |
| `ACTION_INVOCATION_FAILED` | ⚠️ Conditional | Delegate to sf-flow or sf-apex skill |
| `RESPONSE_QUALITY_ISSUE` | ✅ Yes | Add response format rules to topic instructions |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CURRENT_ATTEMPT` | Current attempt number (auto-incremented) | 1 |
| `MAX_WAIT_MINUTES` | Timeout for test execution | 10 |
| `SKIP_TESTS` | Comma-separated test names to skip | (none) |
| `VERBOSE` | Enable detailed output | false |

### Machine-Readable Output

The script outputs structured data for Claude Code parsing:

```
---BEGIN_MACHINE_READABLE---
FIX_NEEDED: true
TEST_API_NAME: Test_Agentforce_v1
TARGET_ORG: AgentforceTesting
CURRENT_ATTEMPT: 1
MAX_ATTEMPTS: 3
NEXT_COMMAND: CURRENT_ATTEMPT=2 ./test-fix-loop.sh Test_Agentforce_v1 AgentforceTesting 3
---END_MACHINE_READABLE---
```

---

## 🐛 Known Issues & CLI Bugs

> **Last Updated**: 2026-01-04 | **Tested With**: sf CLI v2.118.16

### CRITICAL: `sf agent test create` MasterLabel Bug

**Status**: 🔴 BLOCKING - Prevents YAML-based test creation

**Error**:
```
Error (SfError): Required fields are missing: [MasterLabel]
```

**Root Cause**: The CLI generates XML from YAML but omits the required `<name>` element (MasterLabel).

**Generated XML** (broken):
```xml
<AiEvaluationDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <subjectName>My_Agent</subjectName>
    <subjectType>AGENT</subjectType>
    <!-- ❌ MISSING: <name>Test Name</name> -->
    <testCase>...</testCase>
</AiEvaluationDefinition>
```

**Working XML** (from existing tests):
```xml
<AiEvaluationDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Test description</description>
    <name>Test Name</name>  <!-- ✅ REQUIRED -->
    <subjectName>My_Agent</subjectName>
    <subjectType>AGENT</subjectType>
    <testCase>...</testCase>
</AiEvaluationDefinition>
```

**Workarounds**:
1. ✅ Use `sf agent generate test-spec --from-definition` to convert existing XML to YAML (produces correct format)
2. ✅ Use interactive `sf agent generate test-spec` wizard (works correctly)
3. ✅ Create tests via Salesforce Testing Center UI
4. ✅ Deploy XML metadata directly (bypass YAML conversion)

---

### MEDIUM: Interactive Mode Not Scriptable

**Status**: 🟡 Blocks CI/CD automation

**Issue**: `sf agent generate test-spec` only works interactively:
- No `--quiet`, `--json`, or non-interactive flags
- Piped input causes "User force closed the prompt" error
- Cannot automate in CI/CD pipelines

**What Works**:
```bash
# Interactive (requires terminal)
sf agent generate test-spec --output-file ./tests/my-test.yaml

# Convert existing XML to YAML (non-interactive)
sf agent generate test-spec --from-definition path/to/test.xml --output-file ./output.yaml
```

**Workaround**: Use Python scripts in `hooks/scripts/` to generate YAML programmatically.

---

### MEDIUM: YAML vs XML Format Discrepancy

**Issue**: Documentation shows one YAML format, but Salesforce stores as different XML structure.

**Doc Shows** (doesn't map correctly):
```yaml
testCases:
  - utterance: "Hello"
    expectation:
      topic: Welcome
      actionSequence: []
```

**Actual Working Format** (from `--from-definition`):
```yaml
testCases:
  - utterance: "Hello"
    expectedTopic: Welcome
    expectedActions: []
    expectedOutcome: "Greeting response shown"
```

**Key Mappings**:
| YAML Field | XML Element |
|------------|-------------|
| `expectedTopic` | `<expectation><name>topic_sequence_match</name><expectedValue>...</expectedValue>` |
| `expectedActions` | `<expectation><name>action_sequence_match</name><expectedValue>[...]</expectedValue>` |
| `expectedOutcome` | `<expectation><name>bot_response_rating</name><expectedValue>...</expectedValue>` |

---

### LOW: Expectation Name Variations

**Issue**: Different test creation methods use different expectation names:

| CLI Generates | Manually Created Tests Use |
|---------------|---------------------------|
| `topic_assertion` | `topic_sequence_match` |
| `actions_assertion` | `action_sequence_match` |
| `output_validation` | `bot_response_rating` |

**Impact**: May cause confusion when comparing test results from different sources.

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
