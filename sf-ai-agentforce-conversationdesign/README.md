# sf-ai-agentforce-conversationdesign

Conversation design skill for Salesforce Agentforce agents. Design before you build.

## What This Skill Does

Generates and validates conversation design artifacts for Agentforce agents:

- **Persona Documents** — Agent personality, tone, communication style
- **Topic Architectures** — Bottom-up topic design with classification descriptions
- **Instruction Sets** — Three-level instruction framework (agent/topic/action)
- **Utterance Libraries** — Test cases for classification validation
- **Escalation Matrices** — Trigger conditions, routing rules, context handoff
- **Guardrail Configurations** — Four-layer safety model
- **Quality Scorecards** — 120-point assessment against best practices

## Quick Start

### Design a New Agent
```
"Design a conversation for a customer service Agentforce agent"
```

### Assess an Existing Agent
```
"Score my agent's conversation design against best practices"
```

### Fix Conversation Issues
```
"Review my agent's instructions for anti-patterns"
```

## Scoring

120 points across 8 categories:

| Category | Points |
|----------|--------|
| Persona & Tone | 15 |
| Topic Architecture | 20 |
| Instruction Quality | 20 |
| Dialog Flow Design | 15 |
| Utterance Coverage | 15 |
| Escalation Design | 15 |
| Guardrails & Safety | 10 |
| Continuous Improvement | 10 |

**Grades:** A (108-120) · B (96-107) · C (84-95) · D (72-83) · F (<72)

## Prerequisites

- Salesforce org with Agentforce license
- API version 65.0+
- Einstein Agent User in org
- Familiarity with Agent Builder Setup UI

## Chain Position

This skill is the **first step** in the Agentforce development chain:

```
conversationdesign → metadata → apex → flow → deploy → agentscript → deploy → testing
```

## Documentation

See [SKILL.md](SKILL.md) for the complete reference, scoring rubric, and methodology.

## License

MIT — See [LICENSE](LICENSE)
