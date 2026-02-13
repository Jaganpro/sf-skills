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
| **Agent Runtime API** | [agent-api-reference.md](docs/agent-api-reference.md) | REST endpoints for multi-turn testing |
| **ECA Setup** | [eca-setup-guide.md](docs/eca-setup-guide.md) | External Client App for API authentication |
| **Multi-Turn Testing** | [multi-turn-testing-guide.md](docs/multi-turn-testing-guide.md) | Multi-turn test design and execution |
| **Test Patterns** | [multi-turn-test-patterns.md](resources/multi-turn-test-patterns.md) | 6 multi-turn test patterns with examples |
| **CLI commands** | [cli-commands.md](docs/cli-commands.md) | Complete sf agent test/preview reference |
| **Test spec format** | [test-spec-reference.md](resources/test-spec-reference.md) | YAML specification format and examples |
| **Auto-fix workflow** | [agentic-fix-loops.md](resources/agentic-fix-loops.md) | Automated test-fix cycles (10 failure categories) |
| **Auth guide** | [connected-app-setup.md](docs/connected-app-setup.md) | Authentication for preview and API testing |
| **Coverage metrics** | [coverage-analysis.md](docs/coverage-analysis.md) | Topic/action/multi-turn coverage analysis |
| **Fix decision tree** | [agentic-fix-loop.md](docs/agentic-fix-loop.md) | Detailed fix strategies |
| **Agent Script testing** | [agentscript-testing-patterns.md](docs/agentscript-testing-patterns.md) | 5 patterns for testing Agent Script agents |
| **Deep conversation history** | [deep-conversation-history-patterns.md](docs/deep-conversation-history-patterns.md) | 5 patterns for protocol-stage testing via CLI `conversationHistory` |

**⚡ Quick Links:**
- [4-Step Interview Flow](#4-step-interview-flow-testing-center-wizard) - Testing Center wizard (4 steps)
- [Credential Convention](#credential-convention-sfagent) - Persistent ECA storage
- [Swarm Execution Rules](#swarm-execution-rules-native-claude-code-teams) - Parallel team testing
- [Test Plan Format](#test-plan-file-format) - Reusable YAML plans
- [Phase A: Multi-Turn API Testing](#phase-a-multi-turn-api-testing-primary) - Primary workflow
- [Phase B: CLI Testing Center](#phase-b-cli-testing-center-secondary) - Secondary workflow
- [Agent Script Testing](#-agent-script-agents-aiauthoringbundle) - Agent Script-specific patterns
- [Scoring System](#scoring-system-100-points) - 7-category validation
- [Agentic Fix Loop](#phase-c-agentic-fix-loop) - Auto-fix workflow

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

> **Variable resolution:** At runtime, resolve `SKILL_PATH` from the `${SKILL_HOOKS}` environment variable (strip `/hooks` suffix). Hardcoded fallback: `~/.claude/skills/sf-ai-agentforce-testing`.

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-apex → sf-flow → sf-deploy → sf-ai-agentscript → sf-deploy → sf-ai-agentforce-testing** (you are here)

**Why testing is LAST:**
1. Agent must be **published** before running automated tests
2. Agent must be **activated** for preview mode and API access
3. All dependencies (Flows, Apex) must be deployed first
4. Test data (via sf-data) should exist before testing actions

**⚠️ MANDATORY Delegation:**
- **Fixes**: ALWAYS use `Skill(skill="sf-ai-agentscript")` for agent script fixes
- **Test Data**: Use `Skill(skill="sf-data")` for action test data
- **OAuth Setup** (multi-turn API testing only): Use `Skill(skill="sf-connected-apps")` for ECA — NOT needed for `sf agent preview` or CLI tests
- **Observability**: Use `Skill(skill="sf-ai-agentforce-observability")` for STDM analysis of test sessions

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
| **ECA configured** (Phase A only) | Token request test | Multi-turn API testing only. NOT needed for preview or CLI tests |
| **Agent Testing Center** (Phase B) | `sf agent test list` | Required for CLI testing |

---

## 4-Step Interview Flow (Testing Center Wizard)

When the testing skill is invoked, follow these 4 steps in order.
Each step mirrors one tab of the Salesforce Testing Center "New Test" wizard.

> **Skip the interview** if the user provides a `test-plan-{agent}.yaml` file — load it directly and jump to execution.

### Step 1: Basic Information

| Input | Source | Fallback |
|-------|--------|----------|
| Skill Path | Auto-resolve from `${SKILL_HOOKS}` env var (strip `/hooks` suffix). If unset → hardcoded `~/.claude/skills/sf-ai-agentforce-testing`. | Hardcoded path |
| Agent Name | User provided or auto-discover via `agent_discovery.py` | AskUserQuestion |
| Org Alias | User provided or `sfdx-config.json` → `target-org` | AskUserQuestion |
| Description | ALWAYS ask — used for test generation context | AskUserQuestion |
| Test Type | User selects: CLI / API / Both | AskUserQuestion |

```
AskUserQuestion:
  questions:
    - question: "Which agent do you want to test?"
      header: "Agent"
      options:
        - label: "Discover from org (Recommended)"
          description: "Auto-discover agents via agent_discovery.py live"
        - label: "I know the API name"
          description: "I'll provide the BotDefinition DeveloperName directly"
    - question: "What is your target org alias?"
      header: "Org"
      options:
        - label: "{auto-detected org alias} (Recommended)"
          description: "Detected from sfdx-config.json target-org"
        - label: "Different org"
          description: "I'll provide a different org alias"
    - question: "What is this test suite validating?"
      header: "Description"
      options:
        - label: "Topic routing accuracy"
          description: "Verify utterances route to correct topics"
        - label: "Guardrail & safety compliance"
          description: "Test deflection, injection, and abuse handling"
        - label: "Full agent coverage"
          description: "Comprehensive coverage across all topics, actions, and edge cases"
    - question: "What type of testing?"
      header: "Test Type"
      options:
        - label: "CLI Testing Center (Recommended)"
          description: "Single-utterance tests via sf agent test — no ECA required"
        - label: "Multi-turn API"
          description: "Multi-turn conversations via Agent Runtime API — requires ECA"
        - label: "Both"
          description: "CLI tests first, then multi-turn API for conversation flow validation"
```

**Auto-runs after Step 1:**
- Skill path resolution (`SKILL_HOOKS` env var or hardcoded fallback)
- Agent metadata retrieval: `python3 {SKILL_PATH}/hooks/scripts/agent_discovery.py live --target-org {org} --agent-name {agent}`
- Testing Center availability check: `sf agent test list -o {org}`

### Step 2: Test Conditions

| Input | Source | Fallback |
|-------|--------|----------|
| Context Variables | Extract from agent metadata (`attributeMappings` where `mappingType=ContextVariable`) | AskUserQuestion |
| Record IDs | User provides or auto-discover from org | AskUserQuestion |
| Credentials | Auto-discover via `credential_manager.py` (API only) | AskUserQuestion |

```
AskUserQuestion:
  questions:
    - question: "Your agent uses context variables: {discovered_vars}. Provide test record IDs?"
      header: "Variables"
      options:
        - label: "Use test record IDs (Recommended)"
          description: "I'll provide real MessagingSession and Case IDs for testing"
        - label: "Auto-discover from org"
          description: "Query the org for recent MessagingSession and Case records"
        - label: "Skip context variables"
          description: "WARNING: Auth topics will likely fail without RoutableId + CaseId"
    - question: "How should conversation history be set up?"
      header: "History"
      options:
        - label: "Single-turn only (Recommended for CLI)"
          description: "Each test is an independent utterance — no prior context"
        - label: "Include multi-turn patterns"
          description: "Add conversationHistory entries for context retention tests"
```

> **⚠️ WARNING:** If the agent has a `User_Authentication` topic, you MUST provide `$Context.RoutableId` and `$Context.CaseId`. Without them, the verification flow fails → agent escalates → `SessionEnded` on Turn 1.

### Step 3: Test Data (HUMAN-IN-THE-LOOP)

Claude generates test cases based on agent metadata, then presents for review.

**Generation inputs:**
- Agent topics + `classificationDescription` from each topic
- System instructions + guardrails from agent metadata
- Description from Step 1 (guides test focus)
- Context variables from Step 2

**Generation rules:**
- ALWAYS include `expectedOutcome` with behavioral description
- Group by category: auth routing, escalation, guardrail, edge cases, global instructions
- Include `$Context.` variables on every test case that needs session context
- Omit `expectedTopic` for ambiguous routing — use `expectedOutcome` instead
- Add `# Description:` comment block at the top of each YAML file

```
AskUserQuestion:
  questions:
    - question: "I generated {N} test cases across {M} categories. Review the test plan?"
      header: "Review"
      options:
        - label: "Approve all (Recommended)"
          description: "Deploy and run all generated test cases as-is"
        - label: "Add more tests"
          description: "I'll suggest additional scenarios to cover"
        - label: "Remove tests"
          description: "I'll identify tests to remove from the suite"
        - label: "Edit specific tests"
          description: "I'll modify specific utterances or expected values"
```

### Step 4: Evaluations & Deploy

```
AskUserQuestion:
  questions:
    - question: "Which quality metrics to include?"
      header: "Metrics"
      multiSelect: true
      options:
        - label: "coherence (Recommended)"
          description: "Response clarity and logical flow — scores 4-5 for clear responses"
        - label: "output_latency_milliseconds (Recommended)"
          description: "Raw latency in ms — useful for performance baselining"
        - label: "instruction_following (CLI only — crashes UI)"
          description: "Whether agent follows instructions. Works in CLI but breaks Testing Center UI"
    - question: "Deploy and run strategy?"
      header: "Strategy"
      options:
        - label: "Swarm: parallel deploy+run (Recommended for 3+ suites)"
          description: "Use agent teams to deploy and run suites in parallel — fastest for large test sets"
        - label: "Sequential: one suite at a time"
          description: "Deploy and run each suite sequentially — simpler but slower"
```

**After confirmation:**
1. Save test plan as `test-plan-{agent_name}.yaml`
2. Deploy suites via `sf agent test create --spec`
3. Run suites via `sf agent test run`
4. Collect results via `sf agent test results --job-id`
5. Present formatted results summary

---

## ⚡ MANDATORY: Phase A4 Execution Protocol

> **This protocol is NON-NEGOTIABLE.** After I-7 confirmation, you MUST follow EXACTLY these steps based on the partition strategy. DO NOT improvise, skip steps, or run sequentially when the plan says swarm.

### Path A: Sequential Execution (worker_count == 1)

Run a single `multi_turn_test_runner.py` process. No team needed.

```bash
set -a; source ~/.sfagent/{org_alias}/{eca_name}/credentials.env; set +a
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --scenarios {scenario_file} \
  --agent-id {agent_id} \
  --var '$Context.RoutableId={routable_id}' \
  --var '$Context.CaseId={case_id}' \
  --output {working_dir}/results.json \
  --report-file {working_dir}/report.ansi \
  --verbose
```

### Path B: Swarm Execution (worker_count == 2) — MANDATORY CHECKLIST

**YOU MUST EXECUTE EVERY STEP BELOW IN ORDER. DO NOT SKIP ANY STEP.**

☐ **Step 1: Split scenarios into 2 partitions**
  Group the generated category YAML files into 2 balanced buckets by total scenario count.
  Write `{working_dir}/scenarios-part1.yaml` and `{working_dir}/scenarios-part2.yaml`.
  Each partition file must be valid YAML with a `scenarios:` key containing its subset.

☐ **Step 2: Create team**
  ```
  TeamCreate(team_name="sf-test-{agent_name}")
  ```

☐ **Step 3: Create 2 tasks** (one per partition)
  ```
  TaskCreate(subject="Run partition 1", description="Execute scenarios-part1.yaml")
  TaskCreate(subject="Run partition 2", description="Execute scenarios-part2.yaml")
  ```

☐ **Step 4: Spawn 2 workers IN PARALLEL** (single message with 2 Task tool calls)
  Use the **Worker Agent Prompt Template** below. CRITICAL: Both Task calls MUST be in the SAME message.
  ```
  Task(subagent_type="general-purpose", team_name="sf-test-{agent_name}", name="worker-1", prompt=WORKER_PROMPT_1)
  Task(subagent_type="general-purpose", team_name="sf-test-{agent_name}", name="worker-2", prompt=WORKER_PROMPT_2)
  ```

☐ **Step 5: Wait for both workers to report** (they SendMessage when done)
  Do NOT proceed until both workers have sent their results via SendMessage.

☐ **Step 6: Aggregate results**
  ```bash
  python3 {SKILL_PATH}/hooks/scripts/rich_test_report.py \
    --results {working_dir}/worker-1-results.json {working_dir}/worker-2-results.json
  ```

☐ **Step 7: Present unified report** to the user

☐ **Step 8: Offer fix loop** if any failures detected

☐ **Step 9: Shutdown workers**
  ```
  SendMessage(type="shutdown_request", recipient="worker-1")
  SendMessage(type="shutdown_request", recipient="worker-2")
  ```

☐ **Step 10: Clean up**
  ```
  TeamDelete
  ```

---

## Credential Convention (~/.sfagent/)

Persistent ECA credential storage managed by `hooks/scripts/credential_manager.py`.

### Directory Structure

```
~/.sfagent/
├── .gitignore          ("*" — auto-created, prevents accidental commits)
├── {Org-Alias}/        (org alias — case-sensitive, e.g. Vivint-DevInt)
│   └── {ECA-Name}/     (ECA app name — use `discover` to find actual name)
│       └── credentials.env
└── Other-Org/
    └── My_ECA/
        └── credentials.env
```

### File Format

```env
# credentials.env — managed by credential_manager.py
# 'export' prefix allows direct `source credentials.env` in shell
export SF_MY_DOMAIN=yourdomain.my.salesforce.com
export SF_CONSUMER_KEY=3MVG9...
export SF_CONSUMER_SECRET=ABC123...
```

### Security Rules

| Rule | Implementation |
|------|---------------|
| Directory permissions | `0700` (owner only) |
| File permissions | `0600` (owner only) |
| Git protection | `.gitignore` with `*` auto-created in `~/.sfagent/` |
| Secret display | NEVER show full secrets — mask as `ABC...XYZ` (first 3 + last 3) |
| Credential passing | Export as env vars for subprocesses, never write to temp files |

### CLI Reference

```bash
# Discover orgs and ECAs
python3 {SKILL_PATH}/hooks/scripts/credential_manager.py discover
python3 {SKILL_PATH}/hooks/scripts/credential_manager.py discover --org-alias Vivint-DevInt

# Load credentials (secrets masked in output)
python3 {SKILL_PATH}/hooks/scripts/credential_manager.py load --org-alias {org} --eca-name {eca}

# Save new credentials
python3 {SKILL_PATH}/hooks/scripts/credential_manager.py save \
  --org-alias {org} --eca-name {eca} \
  --domain yourdomain.my.salesforce.com \
  --consumer-key 3MVG9... --consumer-secret ABC123...

# Validate OAuth flow
python3 {SKILL_PATH}/hooks/scripts/credential_manager.py validate --org-alias {org} --eca-name {eca}

# Source credentials for shell use (set -a auto-exports all vars)
set -a; source ~/.sfagent/{org}/{eca}/credentials.env; set +a
```

---

## Swarm Execution Rules (Native Claude Code Teams)

When `worker_count > 1` in the test plan, use Claude Code's native team orchestration for parallel test execution. When `worker_count == 1`, run sequentially without creating a team.

### Team Lead Rules (Claude Code)

```
RULE: Create team via TeamCreate("sf-test-{agent_name}")
RULE: Create one TaskCreate per partition (category or count split)
RULE: Spawn one Task(subagent_type="general-purpose") per worker
RULE: Each worker gets credentials as env vars in its prompt (NEVER in files)
RULE: Wait for all workers to report via SendMessage
RULE: After all workers complete, run rich_test_report.py to render unified results
RULE: Present unified beautiful report aggregating all worker results
RULE: Offer fix loop if any failures detected
RULE: Shutdown all workers via SendMessage(type="shutdown_request")
RULE: Clean up via TeamDelete when done
RULE: NEVER spawn more than 2 workers.
RULE: When categories > 2, group into 2 balanced buckets.
RULE: Queue remaining work to existing workers after they complete first batch.
```

### Worker Agent Prompt Template

Each worker receives this prompt (team lead fills in the variables):

```
You are a multi-turn test worker for Agentforce agent testing.

YOUR TASK:
1. Claim your task via TaskUpdate(status="in_progress", owner=your_name)

2. Load credentials and run the test:
   set -a; source ~/.sfagent/{org_alias}/{eca_name}/credentials.env; set +a

   python3 {skill_path}/hooks/scripts/multi_turn_test_runner.py \
     --scenarios {scenario_file} \
     --agent-id {agent_id} \
     --var '$Context.RoutableId={routable_id}' \
     --var '$Context.CaseId={case_id}' \
     --output {working_dir}/worker-{N}-results.json \
     --report-file {working_dir}/worker-{N}-report.ansi \
     --worker-id {N} --verbose

3. IMPORTANT — RENDER RICH TUI REPORT IN YOUR PANE:
   After the test runner completes, render the results visually so they appear
   in your conversation pane (the tmux panel the user can see):

   python3 -c "
   import sys, json
   sys.path.insert(0, '{skill_path}/hooks/scripts')
   from multi_turn_test_runner import format_results_rich
   with open('{working_dir}/worker-{N}-results.json') as f:
       results = json.load(f)
   print(format_results_rich(results, worker_id={N}, scenario_file='{scenario_file}'))
   "

   Then copy-paste that output into your conversation as a text message so it
   renders in your Claude Code pane for the user to see.

4. Analyze: which scenarios passed, which failed, and WHY

5. SendMessage to team lead with:
   - Pass/fail summary (counts + percentages)
   - For each failure: scenario name, turn number, what went wrong, suggested fix
   - Total execution time
   - Any patterns noticed (e.g., "all context_preservation tests failed — may be a systemic issue")

6. Mark your task as completed via TaskUpdate

IMPORTANT:
- If a test fails with an auth error (exit code 2), report it immediately — do NOT retry
- If a test fails with scenario failures (exit code 1), analyze and report all failures
- You CAN communicate with other workers if you discover related issues
- The --report-file flag writes a persistent ANSI report file viewable with `cat` or `bat`
```

### Partition Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| `by_category` | One worker per test pattern (topic_routing, context, etc.) | Most runs — natural isolation |
| `by_count` | Split N scenarios evenly across W workers | Large scenario counts |
| `sequential` | Single process, no team | Quick runs, debugging |

### Team Lead Aggregation

After all workers report, the team lead:

1. **Aggregates** all worker result JSON files via `rich_test_report.py`:
   ```bash
   python3 {SKILL_PATH}/hooks/scripts/rich_test_report.py \
     --results /tmp/sf-test-{session}/worker-*-results.json
   ```
2. **Deduplicates** any shared failure patterns across workers
3. **Presents** the unified Rich report (colored Panels, Tables, Tree) to the user
4. **Calculates** aggregate scoring across the 7 categories
5. **Offers** fix loop: if failures exist, ask user whether to auto-fix via `sf-ai-agentscript`
6. **Shuts down** all workers and deletes the team

---

## Test Plan File Format

Test plans (`test-plan-{agent}.yaml`) capture the full interview output for reuse. See `templates/test-plan-template.yaml` for the complete schema.

### Key Sections

| Section | Purpose |
|---------|---------|
| `metadata` | Agent name, ID, org alias, timestamps |
| `credentials` | Path to `~/.sfagent/` credentials.env or `use_env: true` |
| `agent_metadata` | Topics, actions, type — populated by `agent_discovery.py` |
| `scenarios` | List of YAML scenario files + pattern filters |
| `partition` | Strategy (`by_category`/`by_count`/`sequential`) + worker count |
| `session_variables` | Context variables injected into every session |
| `execution` | Timeout, retry, verbose, rich output settings |

### Re-Running from a Saved Plan

When a user provides a test plan file, skip the interview entirely:

```
1. Load test-plan-{agent}.yaml
2. Validate credentials: credential_manager.py validate --org-alias {org} --eca-name {eca}
3. If invalid → ask user to update credentials only (skip other interview steps)
4. Load scenario files from plan
5. Apply partition strategy from plan
6. Execute (team or sequential based on worker_count)
```

This enables rapid re-runs after fixing agent issues — the user just says "re-run" and the skill picks up the saved plan.

---

## Phase A: Multi-Turn API Testing (PRIMARY)

> **⚠️ NEVER use `curl` for OAuth token validation.** Domains containing `--` (e.g., `my-org--devint.sandbox.my.salesforce.com`) cause shell expansion failures with curl's `--` argument parsing. Use `credential_manager.py validate` instead.

### A1: ECA Credential Setup

> **Why ECA?** Multi-turn API testing uses the Agent Runtime API (`/einstein/ai-agent/v1`), which requires OAuth Client Credentials. If you only need interactive testing, use `sf agent preview` instead — no ECA needed, just `sf org login web` (v2.121.7+). See [connected-app-setup.md](docs/connected-app-setup.md).

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
Skill(skill="sf-connected-apps", args="Create External Client App with Client Credentials flow for Agent Runtime API testing. Scopes: api, chatbot_api, sfap_api, refresh_token, offline_access. Name: Agent_API_Testing")
```

**Verify credentials work:**
```bash
# Validate OAuth credentials via credential_manager.py (handles token request internally)
python3 {SKILL_PATH}/hooks/scripts/credential_manager.py \
  validate --org-alias {org} --eca-name {eca}
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

Execute conversations via Agent Runtime API using the **reusable Python scripts** in `hooks/scripts/`.

> ⚠️ **Agent API is NOT supported for agents of type "Agentforce (Default)".** Only custom agents created via Agentforce Builder are supported.

**Option 1: Run Test Scenarios from YAML Templates (Recommended)**

Use the multi-turn test runner to execute entire scenario suites:

```bash
# Run comprehensive test suite against an agent
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --my-domain "${SF_MY_DOMAIN}" \
  --consumer-key "${CONSUMER_KEY}" \
  --consumer-secret "${CONSUMER_SECRET}" \
  --agent-id "${AGENT_ID}" \
  --scenarios templates/multi-turn-comprehensive.yaml \
  --verbose

# Run specific scenario within a suite
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --my-domain "${SF_MY_DOMAIN}" \
  --consumer-key "${CONSUMER_KEY}" \
  --consumer-secret "${CONSUMER_SECRET}" \
  --agent-id "${AGENT_ID}" \
  --scenarios templates/multi-turn-topic-routing.yaml \
  --scenario-filter topic_switch_natural \
  --verbose

# With context variables and JSON output for fix loop
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --my-domain "${SF_MY_DOMAIN}" \
  --consumer-key "${CONSUMER_KEY}" \
  --consumer-secret "${CONSUMER_SECRET}" \
  --agent-id "${AGENT_ID}" \
  --scenarios templates/multi-turn-comprehensive.yaml \
  --var '$Context.AccountId=001XXXXXXXXXXXX' \
  --var '$Context.EndUserLanguage=en_US' \
  --output results.json \
  --verbose
```

**Exit codes:** `0` = all passed, `1` = some failed (fix loop should process), `2` = execution error

**Option 2: Use Environment Variables (cleaner for repeated runs)**

```bash
export SF_MY_DOMAIN="your-domain.my.salesforce.com"
export SF_CONSUMER_KEY="your_key"
export SF_CONSUMER_SECRET="your_secret"
export SF_AGENT_ID="0XxRM0000004ABC"

# Now run without credential flags
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --scenarios templates/multi-turn-comprehensive.yaml \
  --verbose
```

**Option 3: Python API for Ad-Hoc Testing**

For custom scenarios or debugging, use the client directly:

```python
from hooks.scripts.agent_api_client import AgentAPIClient

client = AgentAPIClient(
    my_domain="your-domain.my.salesforce.com",
    consumer_key="...",
    consumer_secret="..."
)

# Context manager auto-ends session
with client.session(agent_id="0XxRM000...") as session:
    r1 = session.send("I need to cancel my appointment")
    print(f"Turn 1: {r1.agent_text}")

    r2 = session.send("Actually, reschedule instead")
    print(f"Turn 2: {r2.agent_text}")

    r3 = session.send("What was my original request?")
    print(f"Turn 3: {r3.agent_text}")
    # Check context preservation
    if "cancel" in r3.agent_text.lower():
        print("✅ Context preserved")

# With initial variables
variables = [
    {"name": "$Context.AccountId", "type": "Id", "value": "001XXXXXXXXXXXX"},
    {"name": "$Context.EndUserLanguage", "type": "Text", "value": "en_US"},
]
with client.session(agent_id="0Xx...", variables=variables) as session:
    r1 = session.send("What orders do I have?")
```

**Connectivity Test:**
```bash
# Verify ECA credentials and API connectivity
python3 {SKILL_PATH}/hooks/scripts/agent_api_client.py
# Reads SF_MY_DOMAIN, SF_CONSUMER_KEY, SF_CONSUMER_SECRET from env
```

**Per-Turn Analysis Checklist:**

The test runner automatically evaluates each turn against expectations defined in the YAML template:

| # | Check | YAML Key | How Evaluated |
|---|-------|----------|---------------|
| 1 | Response non-empty? | `response_not_empty: true` | `messages[0].message` has content |
| 2 | Correct topic matched? | `topic_contains: "cancel"` | Heuristic: inferred from response text |
| 3 | Expected actions invoked? | `action_invoked: true` | Checks for `result` array entries |
| 4 | Response content? | `response_contains: "reschedule"` | Substring match on response |
| 5 | Context preserved? | `context_retained: true` | Heuristic: checks for prior-turn references |
| 6 | Guardrail respected? | `guardrail_triggered: true` | Regex patterns for refusal language |
| 7 | Escalation triggered? | `escalation_triggered: true` | Checks for `Escalation` message type |
| 8 | Response excludes? | `response_not_contains: "error"` | Substring exclusion check |

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

### ⚡ Agent Script Agents (AiAuthoringBundle)

Agent Script agents (`.agent` files in `aiAuthoringBundles/`) deploy as `BotDefinition` and use the same `sf agent test` CLI commands. However, they have unique testing challenges:

**Two-Level Action System:**
- **Level 1 (Definition):** `topic.actions:` block — defines actions with `target: "apex://ClassName"`
- **Level 2 (Invocation):** `reasoning.actions:` block — invokes via `@actions.<name>` with variable bindings

**Single-Utterance Limitation:**
Multi-topic Agent Script agents with `start_agent` routing have a "1 action per reasoning cycle" budget in CLI tests. The first cycle is consumed by the **transition action** (`go_<topic>`). The actual business action (e.g., `get_order_status`) fires in a second cycle that single-utterance tests don't reach.

**Solution — Use `conversationHistory`:**
```yaml
testCases:
  # ROUTING TEST — captures transition action only
  - utterance: "I want to check my order status"
    expectedTopic: order_status
    expectedActions:
      - go_order_status          # Transition action from start_agent

  # ACTION TEST — use conversationHistory to skip routing
  - utterance: "The order ID is 801ak00001g59JlAAI"
    conversationHistory:
      - role: "user"
        message: "I want to check my order status"
      - role: "agent"
        topic: "order_status"    # Pre-positions agent in target topic
        message: "I'd be happy to help! Could you provide the Order ID?"
    expectedTopic: order_status
    expectedActions:
      - get_order_status         # Level 1 DEFINITION name (NOT invocation name)
    expectedOutcome: "Agent retrieves and displays order details"
```

**Key Rules for Agent Script CLI Tests:**
- `expectedActions` uses the **Level 1 definition name** (e.g., `get_order_status`), NOT the Level 2 invocation name (e.g., `check_status`)
- Agent Script topic names may differ in org — use the [topic name discovery workflow](#b15-topic-name-resolution)
- Agents with `WITH USER_MODE` Apex require the Einstein Agent User to have object permissions — missing permissions cause **silent failures** (0 rows, no error)
- `subjectName` in the YAML spec maps to `config.developer_name` in the `.agent` file

**⚠️ Agent Script API Testing Caveat:**

Agent Script agents embed action results differently via the Agent Runtime API:
- **Agent Builder agents**: Return separate `ActionResult` message types with structured data
- **Agent Script agents**: Embed action outputs within `Inform` text messages — no separate `ActionResult` type

This means:
- `action_invoked: true` (boolean) may fail even when the action runs — use `response_contains` to verify action output instead
- `action_invoked: "action_name"` uses `plannerSurfaces` fallback parsing but is less reliable
- For robust testing, prefer `response_contains` / `response_contains_any` checks over `action_invoked`

**Agent Script Templates & Docs:**
- Template: [agentscript-test-spec.yaml](templates/agentscript-test-spec.yaml) — 5 test patterns (CLI)
- Template: [multi-turn-agentscript-comprehensive.yaml](templates/multi-turn-agentscript-comprehensive.yaml) — 6 multi-turn API scenarios
- Guide: [agentscript-testing-patterns.md](docs/agentscript-testing-patterns.md) — detailed patterns with worked examples

**Automated Test Spec Generation:**
```bash
python3 {SKILL_PATH}/hooks/scripts/generate-test-spec.py \
  --agent-file /path/to/Agent.agent \
  --output tests/agent-spec.yaml --verbose

# Generates both routing tests (with transition actions) and
# action tests (with conversationHistory for apex:// targets)
```

**Agent Discovery:**
```bash
# Discover Agent Script agents alongside XML-based agents
python3 {SKILL_PATH}/hooks/scripts/agent_discovery.py local \
  --project-dir /path/to/project --agent-name MyAgent
# Returns type: "AiAuthoringBundle" for .agent files
```

### B1: Test Spec Creation

**⚠️ CRITICAL: YAML Schema**

The CLI YAML spec uses a **FLAT structure** parsed by `@salesforce/agents` — NOT the fabricated `apiVersion`/`kind`/`metadata` format.
See [test-spec-guide.md](docs/test-spec-guide.md) for the correct schema.

Required top-level fields:
- `name:` — Display name (MasterLabel). **Deploy FAILS without this.**
- `subjectType: AGENT`
- `subjectName:` — Agent BotDefinition DeveloperName

**Description convention:** Since `AiEvaluationDefinition` has no XML `<description>` element, use YAML comments to document the test suite's purpose:
```yaml
# Description: Validates auth-first routing for all greeting patterns
name: "VVS Greeting Auth Tests"
subjectType: AGENT
subjectName: Product_Troubleshooting2
```

Test case fields (flat, NOT nested):
- `utterance:` — User message
- `expectedTopic:` — NOT `expectation.topic`
- `expectedActions:` — Flat list of strings, NOT objects with `name`/`invoked`/`outputs`
- `expectedOutcome:` — Optional natural language description

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

**Option A: Interactive Generation** (no automation)
```bash
# Interactive test spec generation
sf agent generate test-spec --output-file ./tests/agent-spec.yaml
# ⚠️ NOTE: No --api-name flag! Interactive-only.
```

**Option B: Automated Generation** (Python script)
```bash
python3 {SKILL_PATH}/hooks/scripts/generate-test-spec.py \
  --agent-file /path/to/Agent.agent \
  --output tests/agent-spec.yaml \
  --verbose
```

**Create Test in Org:**
```bash
sf agent test create --spec ./tests/agent-spec.yaml --api-name MyAgentTest --target-org [alias]
```

See [Test Spec Reference](resources/test-spec-reference.md) for complete YAML format guide.

### B1.5: Topic Name Resolution

Topic name format in `expectedTopic` depends on the topic type:

| Topic Type | YAML Value | Resolution |
|------------|-----------|------------|
| **Standard** (Escalation, Off_Topic) | `localDeveloperName` (e.g., `Escalation`) | Framework resolves automatically |
| **Promoted** (p_16j... prefix) | Full runtime `developerName` with hash | Must be exact match |

**Standard topics** like `Escalation` can use the short name — the CLI framework resolves to the hash-suffixed runtime name.

**Promoted topics** (custom topics created in Setup UI) MUST use the full runtime `developerName` including hash suffix. The short `localDeveloperName` does NOT resolve.

**Discovery workflow:**
1. Write spec with best guesses for topic names
2. Deploy and run: `sf agent test run --api-name X --wait 10 --result-format json --json`
3. Extract actual names: `jq '.result.testCases[].generatedData.topic'`
4. Update spec with actual runtime names
5. Re-deploy with `--force-overwrite` and re-run

See [topic-name-resolution.md](docs/topic-name-resolution.md) for the complete guide.

### B1.6: Known CLI Gotchas

| Gotcha | Detail |
|--------|--------|
| `name:` mandatory | Deploy fails: "Required fields are missing: [MasterLabel]" |
| `expectedActions` is flat strings | `- action_name` NOT `- name: action_name, invoked: true` |
| Empty `expectedActions: []` | Means "not testing" — PASS even when actions invoked |
| Missing `expectedOutcome` | `output_validation` reports ERROR — harmless |
| No MessagingSession context | Flows needing `recordId` error (agent handles gracefully) |
| `--use-most-recent` broken | Always use `--job-id` for `sf agent test results` |
| contextVariables `name` format | Both `RoutableId` and `$Context.RoutableId` work — runtime resolves both. Prefer `$Context.` prefix for clarity. |
| customEvaluations RETRY bug | **⚠️ Spring '26:** Server returns RETRY → REST API 500. See [Known Issues](#critical-custom-evaluations-retry-bug-spring-26). |
| `conciseness` metric broken | Returns score=0, empty explanation — platform bug |
| `instruction_following` threshold | Labels FAILURE even at score=1 — use score value, ignore label |

### B1.7: Context Variables

Context variables inject session-level data (record IDs, user info) into CLI test cases. Without them, action flows receive the topic's internal name as `recordId`. With them, they receive a real record ID.

**When to use:** Any test case where action flows need real record IDs (e.g., updating a MessagingSession, creating a Case).

**YAML syntax:**
```yaml
contextVariables:
  - name: "$Context.RoutableId"   # Prefixed format (recommended)
    value: "0Mwbb000007MGoTCAW"
  - name: "$Context.CaseId"
    value: "500XX0000000001"
```

**Key rules:**
- Both prefixed (`$Context.RoutableId`) and bare (`RoutableId`) formats work — the **runtime resolves both**
- `$Context.` prefix is recommended as it matches the Merge Field syntax used in Flow Builder and Apex
- The CLI passes the `name` verbatim to `<contextVariable><variableName>` in XML metadata — no prefix is added or stripped

**Discovery — find valid IDs:**
```bash
sf data query --query "SELECT Id FROM MessagingSession WHERE Status='Active' LIMIT 1" --target-org [alias]
sf data query --query "SELECT Id FROM Case ORDER BY CreatedDate DESC LIMIT 1" --target-org [alias]
```

**Verified effect (IRIS testing, 2026-02-09):**
- Without `RoutableId`: action receives `recordId: "p_16jPl000000GwEX_Field_Support_Routing_16j8eeef13560aa"` (topic name)
- With `RoutableId`: action receives `recordId: "0Mwbb000007MGoTCAW"` (real MessagingSession ID)

> **Note:** Standard context variables (`RoutableId`, `CaseId`) do NOT unlock authentication-gated topics. Injecting them does not satisfy `User_Authentication` flows. However, **custom boolean auth-state variables** (e.g., `Verified_Check`) CAN bypass the authentication flow — inject the boolean variable as `true` via `contextVariables` to test post-auth business topics directly.

See [context-vars-test-spec.yaml](templates/context-vars-test-spec.yaml) for a dedicated template.

### B1.8: Metrics

Metrics add platform quality scoring to test cases. Specify as a flat list of metric names in the YAML.

**YAML syntax:**
```yaml
metrics:
  - coherence
  - instruction_following
  - output_latency_milliseconds
```

**Available metrics (observed behavior from IRIS testing, 2026-02-09):**

| Metric | Score Range | Status | Notes |
|--------|-------------|--------|-------|
| `coherence` | 1-5 | ✅ Works | Scores 4-5 for clear responses. Recommended. |
| `completeness` | 1-5 | ⚠️ Misleading | Penalizes triage/routing agents for "not solving" — skip for routing agents. |
| `conciseness` | 1-5 | 🔴 Broken | Returns score=0, empty explanation. Platform bug. |
| `instruction_following` | 0-1 | ⚠️ Threshold bug | Labels "FAILURE" at score=1 when explanation says "follows perfectly." |
| `output_latency_milliseconds` | Raw ms | ✅ Works | No pass/fail — useful for performance baselining. |

**Recommendation:** Use `coherence` + `output_latency_milliseconds` for baseline quality. Skip `conciseness` (broken) and `completeness` (misleading for routing agents).

### B1.9: Custom Evaluations (⚠️ Spring '26 Bug)

Custom evaluations allow JSONPath-based assertions on action inputs and outputs — e.g., "verify the action received `supportPath = 'Field Support'`."

**YAML syntax:**
```yaml
customEvaluations:
  - label: "supportPath is Field Support"
    name: string_comparison
    parameters:
      - name: operator
        value: equals
        isReference: false
      - name: actual
        value: "$.generatedData.invokedActions[0][0].function.input.supportPath"
        isReference: true       # JSONPath resolved against generatedData
      - name: expected
        value: "Field Support"
        isReference: false
```

**Evaluation types:**
- `string_comparison`: `equals`, `contains`, `startswith`, `endswith`
- `numeric_comparison`: `equals`, `greater_than`, `less_than`, `greater_than_or_equal`, `less_than_or_equal`

**Building JSONPath expressions:**
1. Run tests with `--verbose` to see `generatedData.invokedActions`
2. Parse the stringified JSON (it's `"[[{...}]]"`, not a parsed array)
3. Common paths: `$.generatedData.invokedActions[0][0].function.input.[field]`

> **⚠️ BLOCKED — Spring '26 Platform Bug:** Custom evaluations with `isReference: true` cause the server to return "RETRY" status. The results API crashes with `INTERNAL_SERVER_ERROR`. This is server-side (confirmed via direct `curl`). **Workaround:** Use `expectedOutcome` (LLM-as-judge) or the Testing Center UI until patched.

See [custom-eval-test-spec.yaml](templates/custom-eval-test-spec.yaml) for a dedicated template.

### B2: Test Execution

> **Context optimization**: The `--json` flag suppresses CLI spinner output (saves context tokens). The `--result-format json` flag formats *test results* as JSON (for programmatic parsing). Use both together for minimal, machine-readable output.

```bash
# Run automated tests (--json = no spinners, --result-format json = structured results)
sf agent test run --api-name MyAgentTest --wait 10 --result-format json --json --target-org [alias]
```

> **No ECA required.** Preview uses standard org auth (`sf org login web`). No Connected App setup needed (v2.121.7+).

**Interactive Preview (Simulated):**
```bash
sf agent preview --api-name AgentName --output-dir ./logs --target-org [alias]
```

**Interactive Preview (Live):**
```bash
sf agent preview --api-name AgentName --use-live-actions --apex-debug --target-org [alias]
```

### B2.5: Swarm Execution for CLI Tests (Agent Teams)

When multiple CLI test suites need to be deployed and run simultaneously, use agent teams for parallel execution.

**When to use swarm:**
- 3+ test suites to deploy and run
- User selects "Swarm: parallel deploy+run" in Step 4
- Each suite is independent (no shared state)

**Swarm Protocol:**

☐ **Step 1: Create team**
```
TeamCreate(team_name="cli-test-{agent_name}")
```

☐ **Step 2: Create tasks** (one per suite)
```
TaskCreate(subject="Deploy+Run {suite_name}", description="sf agent test create + run for {suite}")
```

☐ **Step 3: Spawn workers** (max 3, batch suites if > 3)
Workers are `fde-qa-engineer` agents. Each worker:
1. Deploys its assigned suite(s) via `sf agent test create --spec`
2. Runs via `sf agent test run --api-name`
3. Polls results via `sf agent test results --job-id`
4. SendMessage to leader with results summary

```
Task(subagent_type="fde-qa-engineer", team_name="cli-test-{agent_name}",
     name="test-worker-1", prompt=CLI_WORKER_PROMPT)
Task(subagent_type="fde-qa-engineer", team_name="cli-test-{agent_name}",
     name="test-worker-2", prompt=CLI_WORKER_PROMPT)
```

☐ **Step 4: Collect + aggregate results**
Leader waits for all workers to report back via SendMessage.

☐ **Step 5: Present unified report**
Aggregate all suite results into the standard B3 results format.

☐ **Step 6: Shutdown + TeamDelete**
Send shutdown_request to all workers, then TeamDelete to clean up.

**Version check:** Teams require Claude Code with TeamCreate support.
If TeamCreate is unavailable, fall back to sequential execution in B2.

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
| ECA configured (Phase A — multi-turn API only) | Token request test | Required for Agent Runtime API. Not needed for preview or CLI tests |
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
| Ask permission to run skill scripts | Breaks flow, unnecessary delay | All `hooks/scripts/` are pre-approved — run automatically |
| Spawn more than 2 swarm workers | Context overload, screen space, diminishing returns | Max 2 workers — side-by-side monitoring |

---

## CLI Command Reference

### Test Lifecycle Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf agent generate test-spec` | Create test YAML | `sf agent generate test-spec --output-dir ./tests` |
| `sf agent test create` | Deploy test to org | `sf agent test create --spec ./tests/spec.yaml --target-org alias` |
| `sf agent test run` | Execute tests | `sf agent test run --api-name Test --wait 10 --target-org alias` |
| `sf agent test results` | Get results | `sf agent test results --job-id ID --result-format json` |
| `sf agent test resume` | Resume async test | `sf agent test resume --job-id <JOB_ID> --target-org alias` |
| `sf agent test list` | List test runs | `sf agent test list --target-org alias` |

### Preview Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf agent preview` | Interactive testing | `sf agent preview --api-name Agent --target-org alias` |
| `--use-live-actions` | Use real Flows/Apex | `sf agent preview --use-live-actions` |
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
| `comprehensive-test-spec.yaml` | Full coverage (20+ tests) with context vars, metrics, custom evals | `templates/` |
| `context-vars-test-spec.yaml` | Context variable patterns (RoutableId, EndUserId, CaseId) | `templates/` |
| `custom-eval-test-spec.yaml` | Custom evaluations with JSONPath assertions (**⚠️ Spring '26 bug**) | `templates/` |
| `cli-auth-guardrail-tests.yaml` | Auth gate, guardrail, ambiguous routing, session tests (CLI) | `templates/` |
| `cli-deep-history-tests.yaml` | Deep conversation history patterns (protocol activation, mid-stage, opt-out, session persistence) | `templates/` |
| `guardrail-tests.yaml` | Security/safety scenarios | `templates/` |
| `escalation-tests.yaml` | Human handoff scenarios | `templates/` |
| `agentscript-test-spec.yaml` | Agent Script agents with conversationHistory pattern | `templates/` |
| `standard-test-spec.yaml` | Reference format | `templates/` |

---

## Cross-Skill Integration

**Required Delegations:**

| Scenario | Skill to Call | Command |
|----------|---------------|---------|
| Fix agent script | sf-ai-agentscript | `Skill(skill="sf-ai-agentscript", args="Fix...")` |
| Agent Script agents | sf-ai-agentscript | Parse `.agent` for topic/action discovery; use `conversationHistory` pattern for action tests |
| Create test data | sf-data | `Skill(skill="sf-data", args="Create...")` |
| Fix failing Flow | sf-flow | `Skill(skill="sf-flow", args="Fix...")` |
| Setup ECA or OAuth (multi-turn API only) | sf-connected-apps | `Skill(skill="sf-connected-apps", args="Create...")` |
| Analyze debug logs | sf-debug | `Skill(skill="sf-debug", args="Analyze...")` |
| Session observability | sf-ai-agentforce-observability | `Skill(skill="sf-ai-agentforce-observability", args="Analyze...")` |

---

## Automated Testing (Python Scripts)

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `agent_api_client.py` | Reusable Agent Runtime API v1 client (auth, sessions, messaging, variables) | stdlib only |
| `multi_turn_test_runner.py` | Multi-turn test orchestrator (reads YAML, executes, evaluates, Rich colored reports) | pyyaml, rich + agent_api_client |
| `rich_test_report.py` | Aggregate N worker result JSONs into one unified Rich terminal report | rich |
| `generate-test-spec.py` | Parse .agent files, generate CLI test YAML specs | stdlib only |
| `run-automated-tests.py` | Orchestrate full CLI test workflow with fix suggestions | stdlib only |

**CLI Flags (multi_turn_test_runner.py):**

| Flag | Default | Purpose |
|------|---------|---------|
| `--report-file PATH` | none | Write Rich terminal report to file (ANSI codes included) — viewable with `cat` or `bat` |
| `--no-rich` | off | Disable Rich colored output; use plain-text format |
| `--width N` | auto | Override terminal width (auto-detects from $COLUMNS; fallback 80) |
| `--rich-output` | _(deprecated)_ | No-op — Rich is now default when installed |

**Multi-Turn Testing (Agent Runtime API):**
```bash
# Install test runner dependency
pip3 install pyyaml

# Run multi-turn test suite against an agent
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --my-domain your-domain.my.salesforce.com \
  --consumer-key YOUR_KEY \
  --consumer-secret YOUR_SECRET \
  --agent-id 0XxRM0000004ABC \
  --scenarios templates/multi-turn-comprehensive.yaml \
  --output results.json --verbose

# Or set env vars and omit credential flags
export SF_MY_DOMAIN=your-domain.my.salesforce.com
export SF_CONSUMER_KEY=YOUR_KEY
export SF_CONSUMER_SECRET=YOUR_SECRET
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --agent-id 0XxRM0000004ABC \
  --scenarios templates/multi-turn-topic-routing.yaml \
  --var '$Context.AccountId=001XXXXXXXXXXXX' \
  --verbose

# Connectivity test (verify ECA credentials work)
python3 {SKILL_PATH}/hooks/scripts/agent_api_client.py
```

**CLI Testing (Agent Testing Center):**
```bash
# Generate test spec from agent file
python3 {SKILL_PATH}/hooks/scripts/generate-test-spec.py \
  --agent-file /path/to/Agent.agent \
  --output specs/Agent-tests.yaml

# Run full automated workflow
python3 {SKILL_PATH}/hooks/scripts/run-automated-tests.py \
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
{SKILL_PATH}/hooks/scripts/test-fix-loop.sh Test_Agentforce_v1 AgentforceTesting 3

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
1. Phase A: Run multi-turn scenarios via Python test runner
   python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
     --agent-id ${AGENT_ID} \
     --scenarios templates/multi-turn-comprehensive.yaml \
     --output results.json --verbose
2. Analyze failures from results.json (10 categories)
3. If fixable: Skill(skill="sf-ai-agentscript", args="Fix...")
4. Re-run failed scenarios with --scenario-filter
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
| **`sf agent test create` fails** | "Required fields are missing: [MasterLabel]" | Add `name:` field to top of YAML spec (see Phase B1) |
| Tests fail silently | No results returned | Agent not published - run `sf agent publish authoring-bundle` |
| Topic not matched | Wrong topic selected | Add keywords to topic description |
| Action not invoked | Action never called | Improve action description |
| Live preview 401 | Authentication error | Re-authenticate: `sf org login web` |
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

**Quick Start with Python Scripts:**
```bash
# 1. Get agent ID
AGENT_ID=$(sf data query --use-tooling-api \
  --query "SELECT Id FROM BotDefinition WHERE DeveloperName='My_Agent' AND IsActive=true LIMIT 1" \
  --result-format json --target-org dev | jq -r '.result.records[0].Id')

# 2. Run multi-turn tests (credentials from env or flags)
python3 {SKILL_PATH}/hooks/scripts/multi_turn_test_runner.py \
  --my-domain "${SF_MY_DOMAIN}" \
  --consumer-key "${CONSUMER_KEY}" \
  --consumer-secret "${CONSUMER_SECRET}" \
  --agent-id "${AGENT_ID}" \
  --scenarios templates/multi-turn-comprehensive.yaml \
  --output results.json --verbose
```

**Ad-Hoc Python Usage:**
```python
from hooks.scripts.agent_api_client import AgentAPIClient

client = AgentAPIClient()  # reads SF_MY_DOMAIN, SF_CONSUMER_KEY, SF_CONSUMER_SECRET from env
with client.session(agent_id="0XxRM000...") as session:
    r1 = session.send("I need to cancel my appointment")
    r2 = session.send("Actually, reschedule it instead")
    r3 = session.send("What was my original request about?")
    # Session auto-ends when exiting context manager
```

### CLI Testing (If Agent Testing Center Available)
```bash
# 1. Generate test spec
python3 {SKILL_PATH}/hooks/scripts/generate-test-spec.py \
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

> **Last Updated**: 2026-02-11 | **Tested With**: sf CLI v2.118.16+

### RESOLVED: `sf agent test create` MasterLabel Error

**Status**: 🟢 RESOLVED — Add `name:` field to YAML spec

**Error**: `Required fields are missing: [MasterLabel]`

**Root Cause**: The YAML spec must include a `name:` field at the top level, which maps to `MasterLabel` in the `AiEvaluationDefinition` XML. Our templates previously omitted this field.

**Fix**: Add `name:` to the top of your YAML spec:
```yaml
name: "My Agent Tests"    # ← This was the missing field
subjectType: AGENT
subjectName: My_Agent
```

**If you still encounter issues**:
1. ✅ Use interactive `sf agent generate test-spec` wizard (interactive-only, no CLI flags)
2. ✅ Create tests via Salesforce Testing Center UI
3. ✅ Deploy XML metadata directly
4. ✅ **Use Phase A (Agent Runtime API) instead** — bypasses CLI entirely

### MEDIUM: Interactive Mode Not Scriptable

**Status**: 🟡 Blocks CI/CD automation

**Issue**: `sf agent generate test-spec` only works interactively.

**Workaround**: Use Python scripts in `hooks/scripts/` or Phase A multi-turn templates.

### MEDIUM: YAML vs XML Format Discrepancy

**Key Mappings**:
| YAML Field | XML Element / Assertion Type |
|------------|------------------------------|
| `expectedTopic` | `topic_assertion` |
| `expectedActions` | `actions_assertion` |
| `expectedOutcome` | `output_validation` |
| `contextVariables` | `contextVariable` (`variableName` / `variableValue`) |
| `customEvaluations` | `string_comparison` / `numeric_comparison` (`parameter`) |
| `metrics` | `expectation` (name only, no expectedValue) |

### LOW: BotDefinition Not Always in Tooling API

**Status**: 🟡 Handled automatically

**Issue**: In some org configurations, `BotDefinition` is not queryable via the Tooling API but works via the regular Data API (`sf data query` without `--use-tooling-api`).

**Fix**: `agent_discovery.py live` now has automatic fallback — if the Tooling API returns no results for BotDefinition, it retries with the regular API.

### LOW: `--use-most-recent` Not Implemented

**Status**: Flag documented but NOT functional. Always use `--job-id` explicitly.

### CRITICAL: Custom Evaluations RETRY Bug (Spring '26)

**Status**: 🔴 PLATFORM BUG — Blocks all `string_comparison` / `numeric_comparison` evaluations with JSONPath

**Error**: `INTERNAL_SERVER_ERROR: The specified enum type has no constant with the specified name: RETRY`

**Scope**:
- Server returns "RETRY" status for test cases with custom evaluations using `isReference: true`
- Results API endpoint crashes with HTTP 500 when fetching results
- Both filter expressions `[?(@.field == 'value')]` AND direct indexing `[0][0]` trigger the bug
- Tests WITHOUT custom evaluations on the same run complete normally

**Confirmed**: Direct `curl` to REST endpoint returns same 500 — NOT a CLI parsing issue

**Workaround**:
1. Use Testing Center UI (Setup → Agent Testing) — may display results
2. Skip custom evaluations until platform patch
3. Use `expectedOutcome` (LLM-as-judge) for response validation instead

**Tracking**: Discovered 2026-02-09 on DevInt sandbox (Spring '26). TODO: Retest after platform patch.

### MEDIUM: `conciseness` Metric Returns Score=0

**Status**: 🟡 Platform bug — metric evaluation appears non-functional

**Issue**: The `conciseness` metric consistently returns `score: 0` with an empty `metricExplainability` field across all test cases tested on DevInt (Spring '26).

**Workaround**: Skip `conciseness` in metrics lists until platform patch.

### LOW: `instruction_following` FAILURE at Score=1

**Status**: 🟡 Threshold mismatch — score and label disagree

**Issue**: The `instruction_following` metric labels results as "FAILURE" even when `score: 1` and the explanation text says the agent "follows instructions perfectly." This appears to be a pass/fail threshold configuration error on the platform side.

**Workaround**: Use the numeric `score` value (0 or 1) for evaluation. Ignore the PASS/FAILURE label.

### HIGH: `instruction_following` Crashes Testing Center UI

**Status**: 🔴 Blocks Testing Center UI entirely — separate from threshold bug above

**Error**: `Unable to get test suite: No enum constant einstein.gpt.shared.testingcenter.enums.AiEvaluationMetricType.INSTRUCTION_FOLLOWING_EVALUATION`

**Scope**: The Testing Center UI (Setup → Agent Testing) throws a Java exception when opening **any** test suite that includes the `instruction_following` metric. The CLI (`sf agent test run`) works fine — only the UI rendering is broken.

**Workaround**: Remove `- instruction_following` from the YAML metrics list and redeploy the test spec via `sf agent test create --force-overwrite`.

**Note**: This is a **different bug** from the threshold mismatch above. The threshold bug affects score interpretation; this bug blocks the entire UI from loading.

**Discovered**: 2026-02-11 on DevInt sandbox (Spring '26).

### MEDIUM: Topic Hash Drift on Agent Republish

**Status**: 🟡 Affects all hardcoded promoted topic names

**Issue**: The runtime `developerName` hash suffix (e.g., `Escalation_16j9d687a53f890`) changes each time an agent is republished. Tests with hardcoded full runtime names break silently — `topic_assertion` reports `FAILURE` because the expected hash no longer matches.

**Mitigation**:
1. Use `localDeveloperName` for standard topics (framework resolves automatically)
2. For promoted topics, re-run the [discovery workflow](docs/topic-name-resolution.md#discovery-workflow) after each agent publish
3. Keep a topic name mapping file that gets updated as part of the publish-and-test cycle

### INFO: API vs CLI Action Visibility Gap

**Status**: ℹ️ Informational — affects multi-turn API testing results

**Issue**: The multi-turn Agent Runtime API may report `has_action_result: false` or omit action results for actions that actually executed. This happens because Agent Script agents embed action outputs within `Inform` text messages rather than returning separate `ActionResult` message types.

**Impact**: Multi-turn API test assertions for `action_invoked` may fail even when the action ran correctly. CLI `--verbose` output is authoritative for action verification.

**Workaround**: When API tests show missing actions, cross-validate with CLI `--verbose` results. For Agent Script agents, prefer `response_contains` checks over `action_invoked` assertions.

---

## License

MIT License. See LICENSE file.
Copyright (c) 2024-2026 Jag Valaiyapathy
