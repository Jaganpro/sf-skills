# Topic Architecture Worksheet

## Agent Overview

**Agent Name:** {{AGENT_NAME}}
**Agent Purpose:** {{AGENT_PURPOSE}}
**Primary Channel:** {{CHANNEL}}
**Deployment Scope:** {{SCOPE}} <!-- Internal / External / Hybrid -->

<!--
Instructions: Start by defining what your agent does at a high level.
The topic architecture should support this purpose.
-->

## Action Inventory

<!-- List ALL actions before organizing into topics. This prevents overlooking capabilities. -->

| Action ID | Action Name | Type | Backend | Description |
|-----------|-------------|------|---------|-------------|
| {{ACTION_ID_1}} | {{ACTION_NAME_1}} | {{TYPE_1}} | {{BACKEND_1}} | {{DESCRIPTION_1}} |
| {{ACTION_ID_2}} | {{ACTION_NAME_2}} | {{TYPE_2}} | {{BACKEND_2}} | {{DESCRIPTION_2}} |
| {{ACTION_ID_3}} | {{ACTION_NAME_3}} | {{TYPE_3}} | {{BACKEND_3}} | {{DESCRIPTION_3}} |
| {{ACTION_ID_4}} | {{ACTION_NAME_4}} | {{TYPE_4}} | {{BACKEND_4}} | {{DESCRIPTION_4}} |

<!--
Action Types: Knowledge, Apex, Flow
Backend: Knowledge Article Set, Apex Class Name, Flow API Name
Add rows as needed for all actions.
-->

**Total Actions:** {{TOTAL_ACTIONS}}

## Topic Groupings

### Topic 1: {{TOPIC_1_NAME}}

**Classification Description:**
```
{{TOPIC_1_CLASSIFICATION}}
```

**Actions Assigned:**
- {{ACTION_1_1}}
- {{ACTION_1_2}}
- {{ACTION_1_3}}

**Scope Definition:**
{{TOPIC_1_SCOPE}}

**Out-of-Scope (within this topic):**
{{TOPIC_1_OUT_OF_SCOPE}}

---

### Topic 2: {{TOPIC_2_NAME}}

**Classification Description:**
```
{{TOPIC_2_CLASSIFICATION}}
```

**Actions Assigned:**
- {{ACTION_2_1}}
- {{ACTION_2_2}}
- {{ACTION_2_3}}

**Scope Definition:**
{{TOPIC_2_SCOPE}}

**Out-of-Scope (within this topic):**
{{TOPIC_2_OUT_OF_SCOPE}}

---

### Topic 3: {{TOPIC_3_NAME}}

**Classification Description:**
```
{{TOPIC_3_CLASSIFICATION}}
```

**Actions Assigned:**
- {{ACTION_3_1}}
- {{ACTION_3_2}}

**Scope Definition:**
{{TOPIC_3_SCOPE}}

**Out-of-Scope (within this topic):**
{{TOPIC_3_OUT_OF_SCOPE}}

<!--
Instructions: Add more topics as needed. Guidelines:
- 3-7 topics is optimal (too few = poor routing, too many = confusion)
- Each topic should have 2-5 actions
- Classification descriptions are used by Einstein to route user requests
- Write classifications from the USER's perspective, not the system's
- Good: "Questions about tracking packages, delivery status, and shipment updates"
- Bad: "Uses OrderTrackingFlow to query ShipmentHistory object"
-->

## Topic Distinctness Matrix

| Topic Pair | Semantic Overlap | Confusable Utterances | Mitigation |
|------------|------------------|----------------------|------------|
| {{TOPIC_A}} ↔ {{TOPIC_B}} | {{OVERLAP_LEVEL}} | {{EXAMPLE_UTTERANCE}} | {{MITIGATION_STRATEGY}} |
| {{TOPIC_C}} ↔ {{TOPIC_D}} | {{OVERLAP_LEVEL}} | {{EXAMPLE_UTTERANCE}} | {{MITIGATION_STRATEGY}} |

<!--
Instructions: Identify topics that might overlap. For each pair:
- Overlap Level: None / Low / Medium / High
- List 1-2 utterances that could fit both topics
- Mitigation: How you'll distinguish (keywords, context, follow-up questions)
-->

## Cross-Topic Interaction Matrix

| From Topic | To Topic | Interaction Type | Trigger | Example |
|------------|----------|------------------|---------|---------|
| {{FROM_1}} | {{TO_1}} | {{TYPE_1}} | {{TRIGGER_1}} | {{EXAMPLE_1}} |
| {{FROM_2}} | {{TO_2}} | {{TYPE_2}} | {{TRIGGER_2}} | {{EXAMPLE_2}} |

<!--
Interaction Types:
- Sequential: User needs Topic A, then Topic B in order
- Conditional: Topic A result determines if Topic B is needed
- Parallel: User needs both topics simultaneously
- Fallback: If Topic A fails, try Topic B

Example: From "Order Status" to "Returns" - User finds order is damaged, wants to return
-->

## Global Out-of-Scope Definition

**What This Agent Does NOT Handle:**

1. {{OUT_OF_SCOPE_1}}
   - **User Might Say:** {{UTTERANCE_1}}
   - **Agent Response:** {{RESPONSE_1}}

2. {{OUT_OF_SCOPE_2}}
   - **User Might Say:** {{UTTERANCE_2}}
   - **Agent Response:** {{RESPONSE_2}}

3. {{OUT_OF_SCOPE_3}}
   - **User Might Say:** {{UTTERANCE_3}}
   - **Agent Response:** {{RESPONSE_3}}

<!--
Instructions: Define what NO topic should handle. This prevents agents from
attempting tasks they can't complete. Include legal, compliance, or policy
restrictions (e.g., "no password resets", "no medical advice").
-->

## Topic-Level Instructions

### {{TOPIC_1_NAME}} Instructions
```
{{TOPIC_1_INSTRUCTIONS}}
```

### {{TOPIC_2_NAME}} Instructions
```
{{TOPIC_2_INSTRUCTIONS}}
```

### {{TOPIC_3_NAME}} Instructions
```
{{TOPIC_3_INSTRUCTIONS}}
```

<!--
Instructions: Write 2-5 sentences per topic. Should cover:
- When to use actions within this topic
- Required data collection before action execution
- Error handling specific to this topic
- Escalation criteria for this topic
- Example: "For returns, always verify order is within 30-day window before
  initiating RefundFlow. If item was a gift, collect gift receipt number."
-->

## Utterance Coverage Plan

### {{TOPIC_1_NAME}} Utterances

**Happy Path:**
- {{UTTERANCE_1}}
- {{UTTERANCE_2}}
- {{UTTERANCE_3}}

**Synonyms/Variants:**
- {{UTTERANCE_4}}
- {{UTTERANCE_5}}

**Edge Cases:**
- {{UTTERANCE_6}}
- {{UTTERANCE_7}}

---

### {{TOPIC_2_NAME}} Utterances

**Happy Path:**
- {{UTTERANCE_1}}
- {{UTTERANCE_2}}
- {{UTTERANCE_3}}

**Synonyms/Variants:**
- {{UTTERANCE_4}}
- {{UTTERANCE_5}}

**Edge Cases:**
- {{UTTERANCE_6}}
- {{UTTERANCE_7}}

<!--
Repeat for all topics. Aim for 10-15 utterances per topic covering:
- Happy path: Standard ways users ask
- Synonyms: Different words, same intent
- Edge cases: Unusual phrasing, multi-intent, ambiguous
-->

## Topic Architecture Validation

### Semantic Distinctness Checklist
- [ ] No two topics have >40% classification description overlap
- [ ] Each topic name clearly indicates its purpose
- [ ] Classification descriptions use user language, not technical jargon
- [ ] Ambiguous utterances have mitigation strategies
- [ ] Cross-topic interactions are documented

### Completeness Checklist
- [ ] All actions from inventory are assigned to a topic
- [ ] Each topic has 2+ actions (no single-action topics)
- [ ] Agent-level out-of-scope is defined
- [ ] Topic-level instructions exist for all topics
- [ ] Utterance coverage plan includes edge cases

### Performance Checklist
- [ ] Total topics: 3-7 (optimal range)
- [ ] Topic count justification: {{JUSTIFICATION}}
- [ ] No topics with >50% overlap in classification descriptions
- [ ] All topics have distinct primary intents

## Version Control

**Version:** {{VERSION}}
**Last Updated:** {{DATE}}
**Author:** {{AUTHOR}}
**Approved By:** {{APPROVER}}
**Next Review:** {{REVIEW_DATE}}

## Notes and Assumptions

{{NOTES}}

<!--
Instructions: Document any assumptions made during design:
- Data availability (e.g., "assumes ShipmentHistory has trackingNumber field")
- Integration dependencies (e.g., "requires UPS API for real-time tracking")
- Business rules (e.g., "returns only allowed within 30 days per policy XYZ")
-->
