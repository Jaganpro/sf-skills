<!-- Parent: sf-ai-agentforce-conversationdesign/SKILL.md -->

# Continuous Improvement

Conversation design is never "done." Production usage reveals gaps that testing cannot fully predict.

## The Iteration Cycle

```
    ┌─────────┐
    │ MONITOR │  Track KPIs, review dashboards
    └────┬────┘
         ▼
    ┌─────────┐
    │ ANALYZE │  Identify misrouted utterances, low-CSAT sessions
    └────┬────┘
         ▼
    ┌─────────┐
    │   FIX   │  Update instructions, adjust classifications, add actions
    └────┬────┘
         ▼
    ┌─────────┐
    │ RETEST  │  Run regression tests, add new test cases
    └────┬────┘
         ▼
    ┌─────────┐
    │ DEPLOY  │  Push changes, monitor for improvement
    └────┬────┘
         │
         └──────→ (back to MONITOR)
```

## Key Performance Indicators

| KPI | Target | Measurement |
|-----|--------|-------------|
| Resolution Rate | >70% | Conversations resolved without escalation |
| Classification Accuracy | >90% | Utterances routed to correct topic |
| Avg Turns to Resolution | <6 | Efficiency of information gathering |
| Customer Satisfaction | >4.0/5 | Post-conversation survey |
| Escalation Rate | <30% | Percentage escalated to human |
| Containment Rate | >65% | Percentage staying within agent |
| First Contact Resolution | >60% | Resolved in first session |
| Error Recovery Rate | >80% | Errors gracefully recovered |

## Utterance Analysis Process

1. **Export unmatched utterances** — Pull from Agentforce analytics
2. **Categorize** — New intent? Phrasing gap? True out-of-scope?
3. **Update** — Add new utterances to library, adjust classifications if needed
4. **Test** — Verify changes don't break existing routing
5. **Deploy** — Push updated agent configuration
6. **Schedule** — Repeat weekly for first month, then bi-weekly

> **Deep Dive:** [Quality Metrics](../references/quality-metrics.md) | **Template:** [Improvement Plan](../assets/improvement-plan.md)
