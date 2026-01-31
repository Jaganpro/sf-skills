# Session Tracing Data Model (STDM) Reference

Complete documentation of the Agentforce Session Tracing Data Model stored in Salesforce Data 360.

> **Source**: [Salesforce Help - Data Model for Agentforce Session Tracing](https://help.salesforce.com/s/articleView?id=ai.generative_ai_session_trace_data_model.htm)

## Overview

The STDM captures detailed telemetry from Agentforce agent conversations, enabling:
- **Debugging**: Understand why an agent behaved a certain way
- **Analytics**: Measure agent performance and usage patterns
- **Optimization**: Identify bottlenecks and improvement opportunities

The data model is a collection of DLOs (Data Lake Objects) and DMOs (Data Model Objects) that contain detailed session trace logs of agent behavior. Data is streamed to DLOs in Data 360 and then mapped to the applicable DMOs.

## Data Model Hierarchy

The Agentforce Analytics data model consists of two main components:
1. **Session Tracing Data Model** - Detailed turn-by-turn logs
2. **Optimization Data Model** - Moments and tagging for analytics

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

Represents an overarching container capturing contiguous interactions with one or more AI agents. A typical session might start when the customer asks their first question and end when the customer closes the agent chat window.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | Text | Primary key - unique session identifier | `01999669-0a54-724f-80d6-9cb495a7cee4` |
| `ssot__StartTimestamp__c` | DateTime | Timestamp when the session began | `2026-01-28T10:15:23.000Z` |
| `ssot__EndTimestamp__c` | DateTime | Timestamp when the session concluded or timed out | `2026-01-28T10:19:55.000Z` |
| `ssot__VariableText__c` | Text | *Reserved*. Key-value pairs of contextual session data | `{}` |
| `ssot__SessionOwnerId__c` | Text | *Reserved*. ID of the participant who initiated the session | `0051234567890ABC` |
| `ssot__SessionOwnerObject__c` | Text | *Reserved*. Name of DMO for Session Owner (e.g., `Individual`) | `Individual` |
| `ssot__IndividualId__c` | Text (Lookup) | *Reserved*. Reference to Individual record if owner is Individual | `a0p...` |
| `ssot__AiAgentChannelTypeId__c` | Text (Lookup) | Type of communication channel (PSTN, Messaging, etc.) | `Messaging` |
| `ssot__VoiceCallId__c` | Text (Lookup) | ID linking to voice call origin (if voice-initiated) | `0Lx...` |
| `ssot__MessagingSessionId__c` | Text (Lookup) | ID linking to messaging session origin | `5701234567890ABC` |
| `ssot__PreviousSessionId__c` | Text (Lookup) | *Reserved*. Reference to previous session (multi-agent scenarios) | `a0x...` |
| `ssot__AiAgentSessionEndTypeId__c` | Text (Lookup) | How the session ended | `resolved` |

**Session End Types (Official):**

| Value | Description |
|-------|-------------|
| `resolved` | Session resolved successfully |
| `escalated` | Transferred to human agent |
| `deflected` | User redirected elsewhere |
| `other` | Other outcome |

---

### AIAgentSessionParticipant (ssot__AiAgentSessionParticipant__dlm)

Represents an entity (human or AI) that takes part in an AIAgentSession.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | Text | Primary key | `a0p1234567890ABC` |
| `ssot__AiAgentSessionId__c` | Text (Parent) | Reference to the specific AiAgentSession | `a0x1234567890ABC` |
| `ssot__AiAgentTypeId__c` | Text (Lookup) | Type of AI Agent | `EinsteinServiceAgent` |
| `ssot__AiAgentTemplateApiName__c` | Text | Template used to create the agent | `Service_Agent_Template` |
| `ssot__StartTimestamp__c` | DateTime | Timestamp when participant joined the session | `2026-01-28T10:15:23.000Z` |
| `ssot__EndTimestamp__c` | DateTime | Timestamp when participant left/stopped interacting | `2026-01-28T10:19:55.000Z` |
| `ssot__ParticipantAttributeText__c` | Text | *Reserved*. JSON key-value pairs of participant metadata | `{}` |
| `ssot__ParticipantId__c` | Text | Reference to the record representing the participant | `0051234567890ABC` |
| `ssot__ParticipantObject__c` | Text | Name of DMO for the Participant record (e.g., `Individual`) | `Individual` |
| `ssot__AiAgentVersionApiName__c` | Text | API name of the AI agent version (if participant is AI) | `v1.2.3` |
| `ssot__AiAgentApiName__c` | Text | API name of the AI agent (if participant is AI) | `Customer_Support_Agent` |
| `ssot__IndividualId__c` | Text (Lookup) | *Reserved*. Reference to Individual if participant DMO is Individual | `a0i...` |
| `ssot__AiAgentSessionParticipantRoleId__c` | Text (Lookup) | Role of participant within the session | `Owner` |

**AI Agent Types:**

| Value | Description |
|-------|-------------|
| `Employee` | Employee-facing agent |
| `EinsteinSDR` | Sales Development Representative agent |
| `EinsteinServiceAgent` | Service agent for customer support |

**Participant Roles:**

| Value | Description |
|-------|-------------|
| `Owner` | Initiated/owns the session |
| `Observer` | Observing the session |

---

### AIAgentInteraction (ssot__AIAgentInteraction__dlm)

Represents a segment within a session. It typically begins with a user's request and ends when the AI agent provides a response to that request.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | Text | Primary key | `a0y1234567890ABC` |
| `ssot__AiAgentSessionId__c` | Text (Parent) | Reference to the parent session | `a0x1234567890ABC` |
| `ssot__PrevInteractionId__c` | Text (Lookup) | Reference to previous interaction (enables sequencing) | `a0y...` |
| `ssot__AiAgentInteractionTypeId__c` | Text (Lookup) | Categorizes the interaction type | `Turn` |
| `ssot__StartTimestamp__c` | DateTime | Timestamp when the interaction began | `2026-01-28T10:15:23.000Z` |
| `ssot__EndTimestamp__c` | DateTime | Timestamp when the interaction completed | `2026-01-28T10:15:26.000Z` |
| `ssot__AttributeText__c` | Text | JSON key-value pairs of additional metadata | `{"confidence": 0.95}` |
| `ssot__TelemetryTraceId__c` | Text | Identifier for distributed tracing (OpenTelemetry) | `abc123def456...` |
| `ssot__TelemetryTraceSpanId__c` | Text (Lookup) | Span ID within distributed tracing context | `span_xyz...` |
| `ssot__SessionOwnerId__c` | Text | *Reserved*. ID of participant who initiated the session | `005...` |
| `ssot__SessionOwnerObject__c` | Text | *Reserved*. DMO name for Session Owner (e.g., `Individual`) | `Individual` |
| `ssot__IndividualId__c` | Text (Lookup) | *Reserved*. Reference to Individual record | `a0i...` |
| `ssot__TopicApiName__c` | Text | API name of the topic classified for this interaction | `Order_Tracking` |

**Interaction Types:**

| Value | Description |
|-------|-------------|
| `Turn` | Normal user input → agent response cycle |
| `SESSION_END` | Final interaction marking session close |

**OpenTelemetry Integration**: The `TelemetryTraceId` and `TelemetryTraceSpanId` fields enable distributed tracing across system components, supporting export to platforms like Datadog, Splunk, and other OTEL-compatible tools.

---

### AIAgentInteractionMessage (ssot__AiAgentInteractionMessage__dlm)

Represents a single communication provided by the user or generated by the AI agent during a session.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | Text | Primary key | `a0i1234567890ABC` |
| `ssot__AiAgentInteractionId__c` | Text (Parent) | Reference to the interaction this message belongs to | `a0y1234567890ABC` |
| `ssot__AiAgentSessionParticipantId__c` | Text (Lookup) | Reference to the participant who sent the message | `a0p...` |
| `ssot__ParentMessageId__c` | Text (Lookup) | Reference to parent message (for reply/continuation threads) | `a0i...` |
| `ssot__AiAgentInteractionMessageTypeId__c` | Text (Lookup) | Type of message (Input/Output) | `Input` |
| `ssot__MessageSentTimestamp__c` | DateTime | Exact time when the message was sent | `2026-01-28T10:15:23.000Z` |
| `ssot__AiAgentInteractionMsgContentTypeId__c` | Text (Lookup) | Format/type of message content (MIME type) | `text/plain` |
| `ssot__ContentText__c` | Text | Textual content (contains `NA` if not text-based) | `What is the status of my order?` |
| `ssot__AiAgentSessionId__c` | Text (Lookup) | Reference to the session this message belongs to | `a0x...` |
| `ssot__SessionOwnerId__c` | Text | *Reserved*. ID of session owner participant | `005...` |
| `ssot__SessionOwnerObject__c` | Text | *Reserved*. DMO name for Session Owner | `Individual` |
| `ssot__IndividualId__c` | Text (Lookup) | *Reserved*. Reference to Individual record | `a0i...` |

**Message Types:**

| Value | Description |
|-------|-------------|
| `Input` | User message to agent |
| `Output` | Agent response to user |

**Content Types (MIME):**

| Value | Description |
|-------|-------------|
| `text/plain` | Plain text message |
| `application/json` | JSON-formatted content |
| `audio/wav` | Audio content (voice interactions) |

**Note:** InteractionMessage differs from Moment:
- **InteractionMessage**: Raw user/agent text per turn with threading support
- **Moment**: Summarized request/response with agent API name

---

### AIAgentInteractionStep (ssot__AIAgentInteractionStep__dlm)

Represents a discrete action or operation performed during an interaction to fulfill the user's request.

| Field API Name | Type | Description | Example |
|----------------|------|-------------|---------|
| `ssot__Id__c` | Text | Primary key | `a0z1234567890ABC` |
| `ssot__AiAgentInteractionId__c` | Text (Parent) | Reference to the interaction this step belongs to | `a0y1234567890ABC` |
| `ssot__PrevStepId__c` | Text (Lookup) | *Reserved*. Reference to previous step (enables sequencing) | `a0z...` |
| `ssot__AiAgentInteractionStepTypeId__c` | Text (Lookup) | Categorizes the step type | `LLMExecutionStep` |
| `ssot__StartTimestamp__c` | DateTime | Timestamp when step execution began | `2026-01-28T10:15:23.000Z` |
| `ssot__EndTimestamp__c` | DateTime | Timestamp when step execution completed | `2026-01-28T10:15:24.000Z` |
| `ssot__PreStepVariableText__c` | Text | *Reserved*. State of variables before step execution | `{"customer_id": "C001"}` |
| `ssot__PostStepVariableText__c` | Text | *Reserved*. State of variables after step execution | `{"order_status": "Shipped"}` |
| `ssot__InputValueText__c` | Text | Input data provided to the step (JSON) | `{"orderId": "12345"}` |
| `ssot__OutputValueText__c` | Text | Output data resulting from step execution (JSON) | `{"status": "Shipped"}` |
| `ssot__ErrorMessageText__c` | Text | Error details if step encountered issues | `Action timeout after 30s` |
| `ssot__AttributeText__c` | Text | JSON key-value pairs of additional step metadata | `{"latency_ms": 150}` |
| `ssot__TelemetryTraceSpanId__c` | Text (Lookup) | Identifier for distributed tracing (OTEL span) | `span_abc...` |
| `ssot__GenerationId__c` | Text | Reference to GenAiGeneration record (if LLM step) | `gen_abc123...` |
| `ssot__GenAiGatewayRequestId__c` | Text | Reference to GenAiGatewayRequest record (if LLM step) | `req_xyz...` |
| `ssot__GenAiGatewayResponseId__c` | Text | Reference to GenAiGatewayResponse record (if LLM step) | `resp_xyz...` |
| `ssot__Name__c` | Text | Name of the step/action performed by the AI Agent | `Get_Order_Status` |

**Step Types (Official):**

| Value | Description | When Used |
|-------|-------------|-----------|
| `UserInputStep` | User input processing | Initial user message handling |
| `LLMExecutionStep` | LLM call execution | Intent detection, response generation |
| `FunctionStep` | Function/action execution | Calling flows, Apex actions |

**GenAI Reference Fields:**

The Step entity includes references to every LLM call the reasoning engine makes, enabling joins with feedback data or guardrails metrics:
- `GenerationId` → Links to `GenAIGeneration__dlm` for quality analysis
- `GenAiGatewayRequestId` → Links to `GenAIGatewayRequest__dlm` for prompts
- `GenAiGatewayResponseId` → Links to `GenAIGatewayResponse__dlm` for raw responses

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
