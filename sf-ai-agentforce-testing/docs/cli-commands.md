# CLI Commands Reference

Complete reference for SF CLI commands related to Agentforce testing.

---

## Command Overview

```
sf agent test
├── create          Create agent test in org from spec
├── list            List available test runs
├── run             Start agent test execution
├── results         Get completed test results
└── resume          Resume incomplete test run

sf agent
├── preview         Interactive agent testing
├── generate
│   └── test-spec   Generate test specification YAML
└── (other agent commands in sf-ai-agentforce)
```

---

## Test Specification Generation

### sf agent generate test-spec

Generate a YAML test specification interactively.

```bash
sf agent generate test-spec [--output-file <path>]
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--output-file` | Path for generated YAML (default: `specs/agentTestSpec.yaml`) |
| `--api-version` | Override API version |

**Interactive Prompts:**

The command interactively prompts for:
1. **Utterance** - Test input (user message)
2. **Expected topic** - Which topic should be selected
3. **Expected actions** - Which actions should be invoked
4. **Expected outcome** - Response validation rules
5. **Custom evaluations** - JSONPath expressions for complex validation
6. **Add another?** - Continue adding test cases

**Example:**

```bash
sf agent generate test-spec --output-file ./tests/support-agent-tests.yaml

# Interactive session:
# > Enter utterance: Where is my order?
# > Expected topic: order_lookup
# > Expected actions (comma-separated): get_order_status
# > Expected outcome: action_invoked
# > Add another test case? (y/n): y
```

---

## Test Creation

### sf agent test create

Create an agent test in the org from a YAML specification.

```bash
sf agent test create --spec <file> --target-org <alias> [--api-name <name>] [--force-overwrite]
```

**Required Flags:**

| Flag | Description |
|------|-------------|
| `-s, --spec` | Path to test spec YAML file |
| `-o, --target-org` | Target org alias or username |

**Optional Flags:**

| Flag | Description |
|------|-------------|
| `-n, --api-name` | API name for the test (auto-generated if omitted) |
| `--force-overwrite` | Skip confirmation if test exists |
| `--preview` | Dry-run - view metadata without deploying |

**Example:**

```bash
# Create test from spec
sf agent test create --spec ./tests/support-agent-tests.yaml --target-org dev

# Force overwrite existing test
sf agent test create --spec ./tests/updated-spec.yaml --api-name MyAgentTest --force-overwrite --target-org dev

# Preview without deploying
sf agent test create --spec ./tests/spec.yaml --preview --target-org dev
```

**Output:**

Creates `AiEvaluationDefinition` metadata in the org at:
```
force-app/main/default/aiEvaluationDefinitions/[TestName].aiEvaluationDefinition-meta.xml
```

---

## Test Execution

### sf agent test run

Execute agent tests asynchronously.

```bash
sf agent test run --api-name <name> --target-org <alias> [--wait <minutes>]
```

**Required Flags:**

| Flag | Description |
|------|-------------|
| `-n, --api-name` | Test API name (created via `test create`) |
| `-o, --target-org` | Target org alias or username |

**Optional Flags:**

| Flag | Description |
|------|-------------|
| `-w, --wait` | Minutes to wait for completion (default: async) |
| `-r, --result-format` | Output format: `human` (default), `json`, `junit`, `tap` |
| `-d, --output-dir` | Directory to save results |
| `--verbose` | Include detailed action data |

**Example:**

```bash
# Run test and wait up to 10 minutes
sf agent test run --api-name CustomerSupportTests --wait 10 --target-org dev

# Run async (returns job ID immediately)
sf agent test run --api-name MyAgentTest --target-org dev

# Run with JSON output for CI/CD
sf agent test run --api-name MyAgentTest --wait 15 --result-format json --output-dir ./results --target-org dev

# Run with verbose output
sf agent test run --api-name MyAgentTest --wait 10 --verbose --target-org dev
```

**Async Behavior:**

Without `--wait`, the command:
1. Starts the test
2. Returns a job ID
3. Exits immediately

Use `sf agent test results --job-id <id>` to retrieve results later.

---

## Test Results

### sf agent test results

Retrieve results from a completed test run.

```bash
sf agent test results --job-id <id> --target-org <alias> [--result-format <format>]
```

**Flags:**

| Flag | Description |
|------|-------------|
| `-i, --job-id` | Job ID from `test run` command |
| `-o, --target-org` | Target org alias or username |
| `-r, --result-format` | Output format: `human`, `json`, `junit`, `tap` |
| `-d, --output-dir` | Directory to save results |
| `--verbose` | Include generated data (actions, objects touched) |

**Example:**

```bash
# Get results from specific job
sf agent test results --job-id 0Ah7X0000000001 --result-format json --target-org dev

# Save results to file
sf agent test results --job-id 0Ah7X0000000001 --output-dir ./results --target-org dev
```

---

## Test Resume

### sf agent test resume

Resume or retrieve results from an incomplete test.

```bash
sf agent test resume --job-id <id> --target-org <alias> [--wait <minutes>]
sf agent test resume --use-most-recent --target-org <alias>
```

**Flags:**

| Flag | Description |
|------|-------------|
| `-i, --job-id` | Job ID to resume |
| `-r, --use-most-recent` | Resume most recent test run |
| `-o, --target-org` | Target org alias or username |
| `-w, --wait` | Minutes to wait for completion |
| `--result-format` | Output format |
| `--output-dir` | Directory to save results |

**Example:**

```bash
# Resume specific job
sf agent test resume --job-id 0Ah7X0000000001 --wait 5 --target-org dev

# Resume most recent test
sf agent test resume --use-most-recent --wait 10 --target-org dev
```

---

## Test Listing

### sf agent test list

List all agent test runs in the org.

```bash
sf agent test list --target-org <alias>
```

**Example:**

```bash
sf agent test list --target-org dev
```

**Output:**

```
Test Name                  Status      Created
─────────────────────────────────────────────────
CustomerSupportTests       Completed   2025-01-01
OrderAgentTests           Running     2025-01-01
FAQAgentTests             Failed      2024-12-30
```

---

## Interactive Preview

### sf agent preview

Test agent interactively via conversation.

```bash
sf agent preview --api-name <name> --target-org <alias> [options]
```

**Required Flags:**

| Flag | Description |
|------|-------------|
| `-n, --api-name` | Agent API name |
| `-o, --target-org` | Target org alias or username |

**Optional Flags:**

| Flag | Description |
|------|-------------|
| `--use-live-actions` | Execute real Flows/Apex (vs simulated) |
| `-c, --client-app` | Connected app name (required for live mode) |
| `--authoring-bundle` | Specific authoring bundle to preview |
| `-d, --output-dir` | Directory to save transcripts |
| `-x, --apex-debug` | Capture Apex debug logs |

**Modes:**

| Mode | Command | Description |
|------|---------|-------------|
| **Simulated** | `sf agent preview --api-name Agent` | LLM simulates action results |
| **Live** | `sf agent preview --api-name Agent --use-live-actions --client-app App` | Real Flows/Apex execute |

**Example:**

```bash
# Simulated preview (default - safe for testing)
sf agent preview --api-name Customer_Support_Agent --target-org dev

# Save transcripts
sf agent preview --api-name Customer_Support_Agent --output-dir ./logs --target-org dev

# Live preview with real actions
sf agent preview --api-name Customer_Support_Agent --use-live-actions --client-app MyConnectedApp --target-org dev

# Live preview with debug logs
sf agent preview --api-name Customer_Support_Agent --use-live-actions --client-app MyApp --apex-debug --output-dir ./logs --target-org dev
```

**Interactive Session:**

```
> Hello, how can I help you today?

You: Where is my order?

Agent: I'd be happy to help you check your order status. Let me look that up...
[Action: get_order_status invoked]
Your order #12345 is currently in transit and expected to arrive tomorrow.

You: [ESC to exit]

Save transcript? (y/n): y
Saved to: ./logs/transcript.json
```

**Output Files:**

When using `--output-dir`:
- `transcript.json` - Conversation record
- `responses.json` - Full API messages with internal details
- `apex-debug.log` - Debug logs (if `--apex-debug`)

---

## Result Formats

### Human (Default)

Formatted for terminal display with colors and tables.

```bash
sf agent test run --api-name Test --result-format human --target-org dev
```

### JSON

Machine-parseable for CI/CD pipelines.

```bash
sf agent test run --api-name Test --result-format json --target-org dev
```

**JSON Structure:**

```json
{
  "status": "Completed",
  "summary": {
    "passed": 18,
    "failed": 2,
    "total": 20
  },
  "testResults": [
    {
      "name": "route_to_order_lookup",
      "status": "Passed",
      "expectedTopic": "order_lookup",
      "actualTopic": "order_lookup",
      "expectedActions": ["get_order_status"],
      "actualActions": ["get_order_status"]
    }
  ],
  "metrics": {
    "topicSelectionAccuracy": 95.0,
    "actionInvocationRate": 90.0,
    "duration": 45200
  }
}
```

### JUnit

XML format for test reporting tools.

```bash
sf agent test run --api-name Test --result-format junit --output-dir ./results --target-org dev
```

**JUnit Structure:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="CustomerSupportTests" tests="20" failures="2" time="45.2">
  <testcase name="route_to_order_lookup" classname="topic_routing" time="2.1"/>
  <testcase name="action_invocation_test" classname="action_invocation" time="3.2">
    <failure type="ACTION_NOT_INVOKED">Expected action get_order_status was not invoked</failure>
  </testcase>
</testsuite>
```

### TAP (Test Anything Protocol)

Simple text format for basic parsing.

```bash
sf agent test run --api-name Test --result-format tap --target-org dev
```

**TAP Output:**

```
TAP version 13
1..20
ok 1 route_to_order_lookup
ok 2 action_output_validation
not ok 3 complex_order_inquiry
  ---
  message: Expected get_order_status invoked 2 times, actual 1
  category: ACTION_INVOCATION_COUNT_MISMATCH
  ...
```

---

## Common Workflows

### Workflow 1: First-Time Test Setup

```bash
# 1. Generate test spec
sf agent generate test-spec --output-file ./tests/my-agent-tests.yaml

# 2. Edit YAML to add test cases (manual step)

# 3. Create test in org
sf agent test create --spec ./tests/my-agent-tests.yaml --api-name MyAgentTests --target-org dev

# 4. Run tests
sf agent test run --api-name MyAgentTests --wait 10 --target-org dev
```

### Workflow 2: CI/CD Pipeline

```bash
# Run tests with JSON output
sf agent test run --api-name MyAgentTests --wait 15 --result-format junit --output-dir ./results --target-org dev

# Check exit code
if [ $? -ne 0 ]; then
  echo "Agent tests failed"
  exit 1
fi
```

### Workflow 3: Debug Failing Agent

```bash
# 1. Run preview with debug logs
sf agent preview --api-name MyAgent --use-live-actions --client-app App --apex-debug --output-dir ./debug --target-org dev

# 2. Analyze transcripts
cat ./debug/responses.json | jq '.messages'

# 3. Check debug logs
cat ./debug/apex-debug.log | grep ERROR
```

---

## Error Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "Agent not found" | Agent not published | Run `sf agent publish authoring-bundle` |
| "Test not found" | Test not created | Run `sf agent test create` first |
| "401 Unauthorized" | Connected app issue | Check OAuth setup via sf-connected-apps |
| "Job ID not found" | Test timed out | Use `sf agent test resume` |
| "No results" | Test still running | Wait longer or use `--wait` |

---

## Related Commands

| Command | Skill | Purpose |
|---------|-------|---------|
| `sf agent publish authoring-bundle` | sf-ai-agentforce | Publish agent before testing |
| `sf agent validate authoring-bundle` | sf-ai-agentforce | Validate agent syntax |
| `sf agent activate` | sf-ai-agentforce | Activate for preview |
| `sf org login web` | - | OAuth for live preview |
