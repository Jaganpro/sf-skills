<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->

# CLI Command Reference

## Test Lifecycle Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf agent generate test-spec` | Create test YAML | `sf agent generate test-spec --output-dir ./tests` |
| `sf agent test create` | Deploy test to org | `sf agent test create --spec ./tests/spec.yaml --target-org alias` |
| `sf agent test run` | Execute tests | `sf agent test run --api-name Test --wait 10 --target-org alias` |
| `sf agent test results` | Get results | `sf agent test results --job-id ID --result-format json` |
| `sf agent test resume` | Resume async test | `sf agent test resume --job-id <JOB_ID> --target-org alias` |
| `sf agent test list` | List test runs | `sf agent test list --target-org alias` |

## Preview Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf agent preview` | Interactive testing | `sf agent preview --api-name Agent --target-org alias` |
| `--use-live-actions` | Use real Flows/Apex | `sf agent preview --use-live-actions` |
| `--output-dir` | Save transcripts | `sf agent preview --output-dir ./logs` |
| `--apex-debug` | Capture debug logs | `sf agent preview --apex-debug` |

## Result Formats

| Format | Use Case | Flag |
|--------|----------|------|
| `human` | Terminal display (default) | `--result-format human` |
| `json` | CI/CD parsing | `--result-format json` |
| `junit` | Test reporting | `--result-format junit` |
| `tap` | Test Anything Protocol | `--result-format tap` |
