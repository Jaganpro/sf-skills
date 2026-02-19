<!-- Parent: sf-ai-agentforce-testing/SKILL.md -->

# Phase D: Coverage Improvement

If coverage < threshold:

1. Identify untested topics/actions/patterns from results
2. Add test cases (YAML for CLI, scenarios for API)
3. Re-run tests
4. Repeat until threshold met

## Coverage Dimensions

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

See [Coverage Analysis](../references/coverage-analysis.md) for complete metrics and improvement guide.
