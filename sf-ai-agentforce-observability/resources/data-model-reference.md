# Session Tracing Data Model (STDM) Reference

Complete documentation of the Agentforce Session Tracing Data Model stored in Salesforce Data Cloud.

## Overview

The STDM captures detailed telemetry from Agentforce agent conversations, enabling:
- **Debugging**: Understand why an agent behaved a certain way
- **Analytics**: Measure agent performance and usage patterns
- **Optimization**: Identify bottlenecks and improvement opportunities

## Data Model Hierarchy

The Agentforce Analytics data model consists of two main components:
1. **Session Tracing Data Model** - Detailed turn-by-turn logs
2. **Optimization Data Model** - Moments and tagging for analytics (coming soon)

### Session Tracing Data Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    AIAgentSession (Session)                     │
│  One session = one complete conversation with an agent          │
├─────────────────────────────────────────────────────────────────┤
│  ssot__Id__c                    Primary key                     │
│  ssot__StartTimestamp__c        When session started            │
│  ssot__EndTimestamp__c          When session ended              │
│  ssot__AiAgentSessionEndType__c How session ended               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │ 1:N         │ 1:N         │ 1:N
         ▼             ▼             ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ SessionParti-  │ │  Interaction   │ │    Moment      │
│   cipant       │ │    (Turn)      │ │ (Summaries)    │
├────────────────┤ ├────────────────┤ ├────────────────┤
│ Participants   │ │ User input →   │ │ Request/resp   │
│ in session     │ │ agent response │ │ summaries      │
│ (user, agent)  │ │ cycle          │ │ Agent API name │
└────────────────┘ └───────┬────────┘ └────────────────┘
                           │
              ┌────────────┼────────────┐
              │ 1:N        │ 1:N        │
              ▼            ▼            ▼
       ┌────────────┐ ┌────────────┐
       │ Interaction│ │ Interaction│
       │   Message  │ │    Step    │
       ├────────────┤ ├────────────┤
       │ User/agent │ │ LLM_STEP   │
       │ messages   │ │ ACTION_STEP│
       │ per turn   │ │ processing │
       └────────────┘ └─────┬──────┘
                            │
                            │ links via GenerationId
                            ▼
                    ┌────────────────┐
                    │ GenAIGeneration│
                    │ (Trust Layer)  │
                    └────────────────┘
```

**Key Relationships:**
- Session has multiple Participants (user, agent, human handoff)
- Session has multiple Interactions (turns)
- Session has multiple Moments (summaries)
- Each Interaction has Messages (actual user/agent text)
- Each Interaction has Steps (processing logic)
- Steps link to GenAIGeneration for quality metrics

## Entity Details

### AIAgentSession (ssot__AIAgentSession__dlm)

Represents a complete conversation session from start to finish.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | String | Unique session identifier | `a0x1234567890ABC` |
| `ssot__AIAgentApiName__c` | String | API name of the handling agent | `Customer_Support_Agent` |
| `ssot__StartTimestamp__c` | DateTime | When the session began | `2026-01-28T10:15:23.000Z` |
| `ssot__EndTimestamp__c` | DateTime | When the session ended | `2026-01-28T10:19:55.000Z` |
| `ssot__AIAgentSessionEndType__c` | String | How the session concluded | `Completed` |
| `ssot__RelatedMessagingSessionId__c` | String | Related messaging session ID | `5701234567890ABC` |
| `ssot__OrganizationId__c` | String | Salesforce org ID | `00D1234567890ABC` |

**Session End Types:**

| Value | Description |
|-------|-------------|
| `Completed` | Session ended normally |
| `Escalated` | Transferred to human agent |
| `Abandoned` | User left without completing |
| `Failed` | Agent encountered an error |
| `Timeout` | Session timed out |

---

### AIAgentSessionParticipant (ssot__AiAgentSessionParticipant__dlm)

Represents participants involved in a session (user, agent, human agents for escalation).

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | String | Unique participant identifier | `a0p1234567890ABC` |
| `ssot__aiAgentSessionId__c` | String | FK to parent session | `a0x1234567890ABC` |
| `ssot__ParticipantType__c` | String | Type of participant | `User` |
| `ssot__ParticipantId__c` | String | ID of the participant entity | `0051234567890ABC` |

**Participant Types:**

| Value | Description |
|-------|-------------|
| `User` | End user interacting with agent |
| `Agent` | AI agent handling the session |
| `HumanAgent` | Human agent (if escalated) |

---

### AIAgentInteraction (ssot__AIAgentInteraction__dlm)

Represents a single turn in the conversation (user input → agent processing → response).

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | String | Unique interaction identifier | `a0y1234567890ABC` |
| `ssot__aiAgentSessionId__c` | String | FK to parent session | `a0x1234567890ABC` |
| `ssot__InteractionType__c` | String | Type of interaction | `TURN` |
| `ssot__TopicApiName__c` | String | Topic that handled this turn | `Order_Tracking` |
| `ssot__StartTimestamp__c` | DateTime | When turn processing started | `2026-01-28T10:15:23.000Z` |
| `ssot__EndTimestamp__c` | DateTime | When turn processing completed | `2026-01-28T10:15:26.000Z` |

**Interaction Types:**

| Value | Description |
|-------|-------------|
| `TURN` | Normal user input → agent response |
| `SESSION_END` | Final interaction marking session close |

---

### AIAgentInteractionMessage (ssot__AiAgentInteractionMessage__dlm)

Represents actual user/agent messages within an interaction turn.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | String | Unique message identifier | `a0i1234567890ABC` |
| `ssot__aiAgentInteractionId__c` | String | FK to parent interaction | `a0y1234567890ABC` |
| `ssot__MessageType__c` | String | Direction of message | `INPUT` |
| `ssot__ContextText__c` | Text | Message content | `What is the status of my order?` |
| `ssot__SentTime__c` | DateTime | When message was sent | `2026-01-28T10:15:23.000Z` |

**Message Types:**

| Value | Description |
|-------|-------------|
| `INPUT` | User message to agent |
| `OUTPUT` | Agent response to user |

**Note:** InteractionMessage differs from Moment:
- **InteractionMessage**: Raw user/agent text per turn
- **Moment**: Summarized request/response with agent API name

---

### AIAgentInteractionStep (ssot__AIAgentInteractionStep__dlm)

Represents an individual processing step within a turn.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | String | Unique step identifier | `a0z1234567890ABC` |
| `ssot__AIAgentInteractionId__c` | String | FK to parent interaction | `a0y1234567890ABC` |
| `ssot__AIAgentInteractionStepType__c` | String | Type of step | `ACTION_STEP` |
| `ssot__Name__c` | String | Step/action name | `Get_Order_Status` |
| `ssot__InputValueText__c` | Text | Input to this step (JSON) | `{"orderId": "12345"}` |
| `ssot__OutputValueText__c` | Text | Output from this step (JSON) | `{"status": "Shipped"}` |
| `ssot__PreStepVariableText__c` | Text | Variable state before step | `{"customer_id": "C001"}` |
| `ssot__PostStepVariableText__c` | Text | Variable state after step | `{"order_status": "Shipped"}` |
| `ssot__GenerationId__c` | String | LLM generation ID | `gen_abc123...` |

**Step Types:**

| Value | Description | When Used |
|-------|-------------|-----------|
| `LLM_STEP` | Language model reasoning/generation | Intent detection, response generation |
| `ACTION_STEP` | Flow or Apex action execution | Calling Get_Order_Status flow |

---

### AIAgentMoment (ssot__AIAgentMoment__dlm)

Represents actual message content in the conversation.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | String | Unique message identifier | `a0m1234567890ABC` |
| `ssot__AIAgentInteractionId__c` | String | FK to parent interaction | `a0y1234567890ABC` |
| `ssot__ContentText__c` | Text | Message content | `What's the status of order #12345?` |
| `ssot__AIAgentInteractionMessageType__c` | String | Message direction | `INPUT` |
| `ssot__MessageSentTimestamp__c` | DateTime | When message was sent | `2026-01-28T10:15:23.000Z` |

**Message Types:**

| Value | Description |
|-------|-------------|
| `INPUT` | User message to agent |
| `OUTPUT` | Agent response to user |

---

## Data Relationships

```sql
-- Session → Interactions
SELECT i.*
FROM ssot__AIAgentInteraction__dlm i
WHERE i.ssot__aiAgentSessionId__c = 'SESSION_ID';

-- Interaction → Steps
SELECT s.*
FROM ssot__AIAgentInteractionStep__dlm s
WHERE s.ssot__AIAgentInteractionId__c = 'INTERACTION_ID';

-- Interaction → Messages
SELECT m.*
FROM ssot__AIAgentMoment__dlm m
WHERE m.ssot__AIAgentInteractionId__c = 'INTERACTION_ID';
```

---

## Data Volume Considerations

| Scenario | Sessions/Day | Total Records/Day |
|----------|--------------|-------------------|
| Low volume | 100-1K | 10K-100K |
| Medium volume | 1K-10K | 100K-1M |
| High volume | 10K-100K | 1M-10M |
| Enterprise | 100K+ | 10M+ |

**Estimation Formula:**
```
Total records ≈ Sessions × Avg turns × (1 + Avg steps + 2)
Example: 10K sessions × 4 turns × 5 = 200K records
```

---

## Data Retention

Session tracing data in Data Cloud follows the org's data retention policy. Default:
- **Production**: 13 months
- **Sandbox**: 30 days

---

## Enabling Session Tracing

1. **Setup** → **Agentforce** → **Settings**
2. Enable **Session Tracing**
3. Configure which agents to trace
4. Wait 5-15 minutes for data to appear in Data Cloud

---

## Related Resources

- [Query Patterns](query-patterns.md) - Example queries
- [Analysis Cookbook](analysis-cookbook.md) - Common analysis patterns
- [Troubleshooting](troubleshooting.md) - Common issues
