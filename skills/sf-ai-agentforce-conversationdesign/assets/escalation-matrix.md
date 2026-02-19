# Escalation Matrix

## Agent Overview

**Agent Name:** {{AGENT_NAME}}
**Escalation Channel:** {{CHANNEL}} <!-- Omni-Channel / SMS / Email / Voice -->
**Default Queue:** {{DEFAULT_QUEUE}}
**Fallback Queue:** {{FALLBACK_QUEUE}}

<!--
Instructions: Define how this agent hands off to human agents. Escalation
should be strategic, not a catch-all for every failure.
-->

## Trigger Conditions

| Trigger Type | Condition | Priority | Routing Rule | Estimated Volume |
|--------------|-----------|----------|--------------|------------------|
| {{TRIGGER_1_TYPE}} | {{CONDITION_1}} | {{PRIORITY_1}} | {{ROUTING_1}} | {{VOLUME_1}} |
| {{TRIGGER_2_TYPE}} | {{CONDITION_2}} | {{PRIORITY_2}} | {{ROUTING_2}} | {{VOLUME_2}} |
| {{TRIGGER_3_TYPE}} | {{CONDITION_3}} | {{PRIORITY_3}} | {{ROUTING_3}} | {{VOLUME_3}} |
| {{TRIGGER_4_TYPE}} | {{CONDITION_4}} | {{PRIORITY_4}} | {{ROUTING_4}} | {{VOLUME_4}} |

<!--
Trigger Types:
- Complexity: User request exceeds agent capabilities
- Sentiment: User is frustrated/angry (detected via sentiment analysis)
- Compliance: Request requires human judgment (legal, medical, financial)
- Policy: User requests exception to policy (refund outside window, etc.)
- Technical: System error or integration failure
- Explicit: User directly asks for human agent
- Stalled: Conversation exceeds N turns without resolution

Priority Levels:
- P1 (Immediate): <1 min SLA, emergency situations
- P2 (Urgent): <5 min SLA, frustrated customers, high-value accounts
- P3 (Normal): <15 min SLA, standard escalations
- P4 (Low): <1 hour SLA, follow-up requests

Estimated Volume: Daily escalation count for capacity planning
-->

## Context Handoff Specification

### Trigger: {{TRIGGER_1_TYPE}}

**Data to Pass:**
- {{DATA_FIELD_1}}: {{DATA_DESCRIPTION_1}}
- {{DATA_FIELD_2}}: {{DATA_DESCRIPTION_2}}
- {{DATA_FIELD_3}}: {{DATA_DESCRIPTION_3}}

**Conversation Summary:**
```
{{SUMMARY_TEMPLATE_1}}
```

**Omni-Channel Work Item Fields:**
- `Subject`: {{SUBJECT_FORMAT_1}}
- `Priority`: {{PRIORITY_1}}
- `Skill Requirements`: {{SKILLS_1}}
- `Custom Field {{FIELD_1}}`: {{VALUE_1}}

---

### Trigger: {{TRIGGER_2_TYPE}}

**Data to Pass:**
- {{DATA_FIELD_1}}: {{DATA_DESCRIPTION_1}}
- {{DATA_FIELD_2}}: {{DATA_DESCRIPTION_2}}

**Conversation Summary:**
```
{{SUMMARY_TEMPLATE_2}}
```

**Omni-Channel Work Item Fields:**
- `Subject`: {{SUBJECT_FORMAT_2}}
- `Priority`: {{PRIORITY_2}}
- `Skill Requirements`: {{SKILLS_2}}

<!--
Repeat for each trigger type. Data to pass should include:
- User context (Account ID, Contact ID, Case Number)
- Conversation history (summarized, not verbatim)
- Agent's attempted actions and results
- Reason for escalation
- Any SLA or compliance requirements
-->

## Omni-Channel Configuration

### Queue: {{QUEUE_1_NAME}}

**Purpose:** {{QUEUE_1_PURPOSE}}

**Routing Model:** {{ROUTING_MODEL_1}} <!-- Most Available / Least Active / External Routing -->

**Skills Required:**
- {{SKILL_1}}: {{SKILL_LEVEL_1}} <!-- e.g., Billing: Expert -->
- {{SKILL_2}}: {{SKILL_LEVEL_2}}

**Service Level Agreement:**
- Target Response Time: {{SLA_1}}
- Escalation Path: {{ESCALATION_PATH_1}}

**Agent Capacity:**
- Max Concurrent Chats: {{MAX_CHATS_1}}
- Overflow Queue: {{OVERFLOW_QUEUE_1}}

---

### Queue: {{QUEUE_2_NAME}}

**Purpose:** {{QUEUE_2_PURPOSE}}

**Routing Model:** {{ROUTING_MODEL_2}}

**Skills Required:**
- {{SKILL_1}}: {{SKILL_LEVEL_1}}
- {{SKILL_2}}: {{SKILL_LEVEL_2}}

**Service Level Agreement:**
- Target Response Time: {{SLA_2}}
- Escalation Path: {{ESCALATION_PATH_2}}

**Agent Capacity:**
- Max Concurrent Chats: {{MAX_CHATS_2}}
- Overflow Queue: {{OVERFLOW_QUEUE_2}}

<!--
Instructions: Define one queue per routing rule. Queues should map to
specialized teams (Billing, Technical, VIP, etc.).
-->

## Escalation Messages

### Pre-Escalation (Before Handoff)

**Default Message:**
```
{{PRE_ESCALATION_MESSAGE}}
```

**Frustrated User Variant:**
```
{{PRE_ESCALATION_FRUSTRATED}}
```

**High-Priority Variant:**
```
{{PRE_ESCALATION_PRIORITY}}
```

<!--
Instructions: What the agent says BEFORE transferring. Should:
- Acknowledge why escalation is needed
- Set expectations for wait time
- Reassure user they'll be helped
- Maintain persona tone
-->

### During Handoff (Wait State)

**Initial Wait Message:**
```
{{WAIT_MESSAGE_INITIAL}}
```

**Extended Wait Message (if >{{WAIT_THRESHOLD}} seconds):**
```
{{WAIT_MESSAGE_EXTENDED}}
```

<!--
Instructions: Keep users informed during wait. Provide estimated time if possible.
Extended message should offer alternatives (callback, email, self-service).
-->

### Post-Escalation (Human Takes Over)

**Human Agent Greeting Template:**
```
{{HUMAN_GREETING}}
```

**Context Summary for Human:**
```
Agent attempted: {{ATTEMPTED_ACTIONS}}
User's goal: {{USER_GOAL}}
Escalation reason: {{REASON}}
Relevant data: {{DATA_SUMMARY}}
```

<!--
Instructions: Template for human agent to use when joining conversation.
Should include all context from agent conversation to avoid re-asking questions.
-->

## Post-Escalation Workflow

### Agent Behavior After Handoff

- [ ] Agent remains in conversation: {{YES_NO}}
- [ ] Agent monitors for human agent join: {{YES_NO}}
- [ ] Agent logs escalation reason: {{YES_NO}}
- [ ] Agent creates follow-up task: {{YES_NO}}

**If Human Agent Unavailable:**
{{UNAVAILABLE_BEHAVIOR}}

<!--
Options:
- Create case and email user
- Offer callback scheduling
- Return to agent with degraded capabilities
- Queue user and notify when agent available
-->

### Escalation Metrics

**Success Criteria:**
- First Contact Resolution (FCR) after escalation: {{FCR_TARGET}}%
- Human agent accepts transfer within: {{ACCEPT_SLA}} seconds
- User satisfaction (CSAT) for escalated conversations: {{CSAT_TARGET}}

**Monitoring:**
- Daily escalation rate: {{RATE_TARGET}}% of total conversations
- Top escalation reasons (weekly review): {{TOP_REASONS}}
- Escalation trend threshold: Alert if rate exceeds {{THRESHOLD}}%

<!--
Instructions: Define how you'll measure escalation effectiveness. High
escalation rates may indicate agent needs more capabilities or training.
-->

## De-Escalation Strategies

### Before Triggering Escalation

**Attempt:**
1. {{STRATEGY_1}} <!-- e.g., Rephrase question to clarify intent -->
2. {{STRATEGY_2}} <!-- e.g., Offer knowledge article or self-service option -->
3. {{STRATEGY_3}} <!-- e.g., Break complex request into smaller actions -->

**If De-Escalation Succeeds:**
{{SUCCESS_ACTION}}

**If De-Escalation Fails:**
{{FAILURE_ACTION}}

<!--
Instructions: Not every failed action needs escalation. Define what the
agent should try before handing off. This reduces escalation volume and
improves agent deflection rate.
-->

## Edge Cases

### Edge Case 1: {{EDGE_CASE_1_NAME}}

**Scenario:** {{SCENARIO_1}}

**Escalation Decision:** {{DECISION_1}}

**Rationale:** {{RATIONALE_1}}

---

### Edge Case 2: {{EDGE_CASE_2_NAME}}

**Scenario:** {{SCENARIO_2}}

**Escalation Decision:** {{DECISION_2}}

**Rationale:** {{RATIONALE_2}}

<!--
Examples:
- User requests escalation but issue is resolvable by agent
- User is abusive or violates terms of service
- System outage prevents all actions (escalate or notify?)
- VIP customer with minor issue (escalate for service level?)
-->

## Version Control

**Version:** {{VERSION}}
**Last Updated:** {{DATE}}
**Author:** {{AUTHOR}}
**Approved By:** {{APPROVER}}
**Next Review:** {{REVIEW_DATE}}

## Notes and Assumptions

{{NOTES}}

<!--
Document dependencies:
- Omni-Channel setup requirements
- Skill definitions in Salesforce
- Queue membership and capacity planning
- Integration with Case Management
-->
