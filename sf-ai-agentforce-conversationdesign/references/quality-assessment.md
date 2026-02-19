<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->

# Quality Assessment

Use the [Quality Scorecard](../assets/quality-scorecard.md) to assess any Agentforce agent against the 120-point rubric.

## Assessment Process

1. **Gather artifacts** — Collect agent configuration, instructions, topic definitions, test results
2. **Score each category** — Use the detailed criteria in the scorecard
3. **Calculate total** — Sum all category scores
4. **Assign grade** — Map total to A/B/C/D/F
5. **Identify gaps** — Categories scoring below 70% of their maximum
6. **Build improvement plan** — Prioritize by impact and effort

## Quick Health Check

Before a full assessment, answer these five questions:

| # | Question | Red Flag |
|---|----------|----------|
| 1 | Can you describe the agent's persona in one sentence? | No persona defined |
| 2 | Are topic classification descriptions mutually exclusive? | Overlapping descriptions |
| 3 | Do instructions use positive framing? | Heavy use of "don't"/"never" |
| 4 | Is there an escalation path for every failure mode? | Missing escalation triggers |
| 5 | Are business rules in Flow/Apex, not instructions? | If/then logic in instructions |

If any red flag appears, start your improvement plan there.
