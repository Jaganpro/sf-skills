<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->

# Test Templates

## Multi-Turn Test Templates

| Template | Pattern | Scenarios | Location |
|----------|---------|-----------|----------|
| `multi-turn-topic-routing.yaml` | Topic switching | 4 | `templates/` |
| `multi-turn-context-preservation.yaml` | Context retention | 4 | `templates/` |
| `multi-turn-escalation-flows.yaml` | Escalation cascades | 4 | `templates/` |
| `multi-turn-comprehensive.yaml` | All 6 patterns | 6 | `templates/` |

## CLI Test Templates

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
