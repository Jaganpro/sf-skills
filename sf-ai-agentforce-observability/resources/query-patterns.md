# Data Cloud Query Patterns

Common query patterns for extracting and analyzing Agentforce session tracing data.

> **Official Reference**: [Get Insights from Agent Session Tracing Data](https://help.salesforce.com/s/articleView?id=ai.generative_ai_session_trace_use.htm)

## Basic Extraction Queries

### All Sessions (Last 7 Days)

```sql
SELECT
    ssot__Id__c,
    ssot__AIAgentApiName__c,
    ssot__StartTimestamp__c,
    ssot__EndTimestamp__c,
    ssot__AIAgentSessionEndType__c
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-21T00:00:00.000Z'
ORDER BY ssot__StartTimestamp__c DESC;
```

### Sessions by Agent

```sql
SELECT *
FROM ssot__AIAgentSession__dlm
WHERE ssot__AIAgentApiName__c = 'Customer_Support_Agent'
  AND ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
ORDER BY ssot__StartTimestamp__c DESC;
```

### Failed/Escalated Sessions

```sql
SELECT *
FROM ssot__AIAgentSession__dlm
WHERE ssot__AIAgentSessionEndType__c IN ('Escalated', 'Abandoned', 'Failed')
  AND ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
ORDER BY ssot__StartTimestamp__c DESC;
```

---

## Aggregation Queries

### Session Count by Agent

```sql
SELECT
    ssot__AIAgentApiName__c as agent,
    COUNT(*) as session_count
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY ssot__AIAgentApiName__c
ORDER BY session_count DESC;
```

### End Type Distribution

```sql
SELECT
    ssot__AIAgentSessionEndType__c as end_type,
    COUNT(*) as count
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY ssot__AIAgentSessionEndType__c;
```

### Topic Usage

```sql
SELECT
    ssot__TopicApiName__c as topic,
    COUNT(*) as turn_count
FROM ssot__AIAgentInteraction__dlm
WHERE ssot__InteractionType__c = 'TURN'
GROUP BY ssot__TopicApiName__c
ORDER BY turn_count DESC;
```

### Action Invocation Frequency

```sql
SELECT
    ssot__Name__c as action_name,
    COUNT(*) as invocation_count
FROM ssot__AIAgentInteractionStep__dlm
WHERE ssot__AIAgentInteractionStepType__c = 'ACTION_STEP'
GROUP BY ssot__Name__c
ORDER BY invocation_count DESC;
```

---

## Relationship Queries

### Session with Turn Count

```sql
SELECT
    s.ssot__Id__c,
    s.ssot__AIAgentApiName__c,
    COUNT(i.ssot__Id__c) as turn_count
FROM ssot__AIAgentSession__dlm s
LEFT JOIN ssot__AIAgentInteraction__dlm i
    ON i.ssot__aiAgentSessionId__c = s.ssot__Id__c
    AND i.ssot__InteractionType__c = 'TURN'
WHERE s.ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY s.ssot__Id__c, s.ssot__AIAgentApiName__c;
```

### Complete Session Tree

```sql
-- Step 1: Get session
SELECT * FROM ssot__AIAgentSession__dlm
WHERE ssot__Id__c = 'a0x1234567890ABC';

-- Step 2: Get interactions
SELECT * FROM ssot__AIAgentInteraction__dlm
WHERE ssot__aiAgentSessionId__c = 'a0x1234567890ABC';

-- Step 3: Get steps (using interaction IDs from step 2)
SELECT * FROM ssot__AIAgentInteractionStep__dlm
WHERE ssot__AIAgentInteractionId__c IN ('a0y...', 'a0y...');

-- Step 4: Get messages (using interaction IDs from step 2)
SELECT * FROM ssot__AIAgentMoment__dlm
WHERE ssot__AIAgentInteractionId__c IN ('a0y...', 'a0y...');
```

---

## Time-Based Queries

### Daily Session Counts

```sql
SELECT
    SUBSTRING(ssot__StartTimestamp__c, 1, 10) as date,
    COUNT(*) as session_count
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY SUBSTRING(ssot__StartTimestamp__c, 1, 10)
ORDER BY date;
```

### Hourly Distribution

```sql
SELECT
    SUBSTRING(ssot__StartTimestamp__c, 12, 2) as hour,
    COUNT(*) as session_count
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY SUBSTRING(ssot__StartTimestamp__c, 12, 2)
ORDER BY hour;
```

---

## Analysis Queries

### Sessions with Topic Switches

```sql
SELECT
    ssot__aiAgentSessionId__c,
    COUNT(DISTINCT ssot__TopicApiName__c) as topic_count
FROM ssot__AIAgentInteraction__dlm
WHERE ssot__InteractionType__c = 'TURN'
GROUP BY ssot__aiAgentSessionId__c
HAVING COUNT(DISTINCT ssot__TopicApiName__c) > 1;
```

### Long Sessions (Many Turns)

```sql
SELECT
    ssot__aiAgentSessionId__c,
    COUNT(*) as turn_count
FROM ssot__AIAgentInteraction__dlm
WHERE ssot__InteractionType__c = 'TURN'
GROUP BY ssot__aiAgentSessionId__c
HAVING COUNT(*) > 10
ORDER BY turn_count DESC;
```

### Actions with High Failure Rate

```sql
-- Note: This requires output parsing for error detection
SELECT
    ssot__Name__c as action_name,
    COUNT(*) as total_invocations,
    COUNT(CASE WHEN ssot__OutputValueText__c LIKE '%error%' THEN 1 END) as errors
FROM ssot__AIAgentInteractionStep__dlm
WHERE ssot__AIAgentInteractionStepType__c = 'ACTION_STEP'
GROUP BY ssot__Name__c;
```

---

## Performance Tips

### Use Date Filters Early

```sql
-- Good: Filter by date first
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
  AND ssot__AIAgentApiName__c = 'My_Agent'

-- Avoid: No date filter on large tables
WHERE ssot__AIAgentApiName__c = 'My_Agent'
```

### Limit Result Sets

```sql
-- Use LIMIT for exploration
SELECT * FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
ORDER BY ssot__StartTimestamp__c DESC
LIMIT 100;
```

### Select Only Needed Columns

```sql
-- Good: Select specific columns
SELECT ssot__Id__c, ssot__AIAgentApiName__c, ssot__StartTimestamp__c
FROM ssot__AIAgentSession__dlm;

-- Avoid: SELECT * on wide tables
SELECT * FROM ssot__AIAgentInteractionStep__dlm;  -- Has large text fields
```

---

## Official Example Queries (from Salesforce Help)

These are official query patterns from the Salesforce documentation.

### Full Session Join (All Entities)

```sql
SELECT *
FROM "AiAgentSession__dlm"
JOIN "AiAgentSessionParticipant__dlm"
    ON "AiAgentSession__dlm"."id__c" = "AiAgentSessionParticipant__dlm"."aiAgentSessionId__c"
JOIN "AiAgentInteraction__dlm"
    ON "AiAgentSession__dlm"."id__c" = "AiAgentInteraction__dlm"."aiAgentSessionId__c"
JOIN "AiAgentInteractionMessage__dlm"
    ON "AiAgentInteraction__dlm"."id__c" = "AiAgentInteractionMessage__dlm"."aiAgentInteractionId__c"
JOIN "AiAgentInteractionStep__dlm"
    ON "AiAgentInteraction__dlm"."id__c" = "AiAgentInteractionStep__dlm"."aiAgentInteractionId__c"
WHERE "AiAgentSession__dlm"."id__c" = '{{SESSION_ID}}'
LIMIT 10;
```

### Recent Sessions (Last N Days)

```sql
SELECT
    ssot__Id__c,
    ssot__StartTimestamp__c
FROM ssot__AiAgentSession__dlm s
WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
ORDER BY s.ssot__StartTimestamp__c DESC;
```

### All Messages in an Interaction

```sql
SELECT
    ssot__AiAgentInteractionId__c AS InteractionId,
    ssot__AiAgentInteractionMessageType__c,     -- user or agent
    ssot__AiAgentInteractionMsgContentType__c,  -- e.g., text
    ssot__ContentText__c,
    ssot__AiAgentSessionParticipantId__c AS SenderParticipantId,
    ssot__ParentMessageId__c                    -- if part of a thread
FROM "ssot__AiAgentInteractionMessage__dlm"
WHERE ssot__AiAgentInteractionId__c = '{{INTERACTION_ID}}'
ORDER BY ssot__MessageSentTimestamp__c ASC;
```

### Steps with Errors

Find all interaction steps that encountered errors:

```sql
SELECT
    ssot__AiAgentInteractionId__c AS InteractionId,
    ssot__Id__c AS StepId,
    ssot__Name__c AS StepName,
    ssot__InputValueText__c AS Input,
    ssot__ErrorMessageText__c AS StepErrorMessage
FROM "ssot__AiAgentInteractionStep__dlm"
WHERE length(ssot__ErrorMessageText__c) > 0
  AND ssot__ErrorMessageText__c != 'NOT_SET'
LIMIT 100;
```

### Join with GenAI Feedback Data

Combine session tracing with feedback and guardrails metrics:

```sql
SELECT
    ssot__AiAgentInteractionId__c AS InteractionId,
    ssot__Name__c AS StepName,
    GenAIGatewayRequest__dlm.prompt__c AS Input_Prompt,
    GenAIGeneration__dlm.responseText__c AS LLM_Response,
    GenAIFeedback__dlm.feedback__c AS Feedback
FROM ssot__AiAgentInteractionStep__dlm
LEFT JOIN GenAIGeneration__dlm
    ON ssot__AiAgentInteractionStep__dlm.ssot__GenerationId__c = GenAIGeneration__dlm.generationId__c
LEFT JOIN GenAIGatewayRequest__dlm
    ON ssot__AiAgentInteractionStep__dlm.ssot__GenAiGatewayRequestId__c = GenAIGatewayRequest__dlm.gatewayRequestId__c
LEFT JOIN GenAIGatewayResponse__dlm
    ON GenAIGatewayRequest__dlm.gatewayRequestId__c = GenAIGatewayResponse__dlm.generationRequestId__c
LEFT JOIN GenAIFeedback__dlm
    ON GenAIGeneration__dlm.generationId__c = GenAIFeedback__dlm.generationId__c
WHERE GenAIGatewayResponse__dlm.generationResponseId__c = GenAIGeneration__dlm.generationResponseId__c
LIMIT 100;
```

---

## Advanced Session Inspection

### Full Session Details (All Related Entities)

Join all session tracing entities for complete visibility:

```sql
SELECT *
FROM ssot__AiAgentSession__dlm s
JOIN ssot__AiAgentSessionParticipant__dlm sp
    ON s.ssot__id__c = sp.ssot__aiAgentSessionId__c
JOIN ssot__AiAgentInteraction__dlm i
    ON s.ssot__id__c = i.ssot__aiAgentSessionId__c
JOIN ssot__AiAgentInteractionMessage__dlm im
    ON i.ssot__id__c = im.ssot__aiAgentInteractionId__c
JOIN ssot__AiAgentInteractionStep__dlm st
    ON i.ssot__id__c = st.ssot__aiAgentInteractionId__c
WHERE s.ssot__id__c = '{{SESSION_ID}}'
LIMIT 100;
```

**Note:** This query includes `SessionParticipant` and `InteractionMessage` entities not in basic extraction.

### Session Insights with CTEs

Use CTEs for complex session analysis with messages and steps:

```sql
WITH
  -- Store session ID for reuse
  params AS (
    SELECT '{{SESSION_ID}}' AS session_id
  ),

  -- Get interactions with their messages
  interactionsWithMessages AS (
    SELECT
      i.ssot__Id__c AS InteractionId,
      i.ssot__TopicApiName__c AS TopicName,
      i.ssot__AiAgentInteractionType__c AS InteractionType,
      i.ssot__StartTimestamp__c AS InteractionStartTime,
      i.ssot__EndTimestamp__c AS InteractionEndTime,
      im.ssot__SentTime__c AS MessageSentTime,
      im.ssot__MessageType__c AS InteractionMessageType,
      im.ssot__ContextText__c AS ContextText,
      NULL AS InteractionStepType,
      NULL AS Name,
      NULL AS InputValueText,
      NULL AS OutputValueText,
      NULL AS PreStepVariableText,
      NULL AS PostStepVariableText
    FROM ssot__AiAgentInteraction__dlm i
    JOIN ssot__AiAgentInteractionMessage__dlm im
      ON i.ssot__Id__c = im.ssot__aiAgentInteractionId__c
    WHERE i.ssot__aiAgentSessionId__c = (SELECT session_id FROM params)
  ),

  -- Get interactions with their steps
  interactionsWithSteps AS (
    SELECT
      i.ssot__Id__c AS InteractionId,
      i.ssot__TopicApiName__c AS TopicName,
      i.ssot__AiAgentInteractionType__c AS InteractionType,
      i.ssot__StartTimestamp__c AS InteractionStartTime,
      i.ssot__EndTimestamp__c AS InteractionEndTime,
      st.ssot__StartTimestamp__c AS MessageSentTime,
      NULL AS InteractionMessageType,
      NULL AS ContextText,
      st.ssot__AiAgentInteractionStepType__c AS InteractionStepType,
      st.ssot__Name__c AS Name,
      st.ssot__InputValueText__c AS InputValueText,
      st.ssot__OutputValueText__c AS OutputValueText,
      st.ssot__PreStepVariableText__c AS PreStepVariableText,
      st.ssot__PostStepVariableText__c AS PostStepVariableText
    FROM ssot__AiAgentInteraction__dlm i
    JOIN ssot__AiAgentInteractionStep__dlm st
      ON i.ssot__Id__c = st.ssot__aiAgentInteractionId__c
    WHERE i.ssot__aiAgentSessionId__c = (SELECT session_id FROM params)
  ),

  -- Combine messages and steps
  combined AS (
    SELECT * FROM interactionsWithMessages
    UNION ALL
    SELECT * FROM interactionsWithSteps
  )

-- Final output sorted chronologically
SELECT
  TopicName,
  InteractionType,
  InteractionStartTime,
  InteractionEndTime,
  MessageSentTime,
  InteractionMessageType,
  ContextText,
  InteractionStepType,
  Name,
  InputValueText,
  OutputValueText,
  PreStepVariableText,
  PostStepVariableText
FROM combined
ORDER BY MessageSentTime ASC;
```

**Tips for Finding Session IDs:**
- For Service Agent: Use `ssot__RelatedMessagingSessionId__c` field on `ssot__AiAgentSession__dlm`
- Use start/end timestamp fields to narrow down timeframes

---

## Quality Analysis Queries

### Toxic Response Detection

Find generations flagged as toxic and trace back to sessions:

```sql
SELECT
    i.ssot__AiAgentSessionId__c AS SessionId,
    i.ssot__TopicApiName__c AS TopicName,
    g.responseText__c AS ResponseText,
    c.category__c AS ToxicityCategory,
    c.value__c AS ConfidenceScore
FROM GenAIContentQuality__dlm AS q
JOIN GenAIContentCategory__dlm AS c
    ON c.parent__c = q.id__c
JOIN GenAIGeneration__dlm AS g
    ON g.generationId__c = q.parent__c
JOIN ssot__AiAgentInteractionStep__dlm st
    ON st.ssot__GenerationId__c = g.generationId__c
JOIN ssot__AiAgentInteraction__dlm i
    ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
WHERE
    q.isToxicityDetected__c = 'true'
    AND TRY_CAST(c.value__c AS DECIMAL) >= 0.5
LIMIT 100;
```

**Join Chain:** ContentQuality → ContentCategory → Generation → Step → Interaction → Session

### Low Instruction Adherence Detection

Find sessions where agent responses didn't follow instructions well:

```sql
SELECT
    i.ssot__AiAgentSessionId__c AS SessionId,
    i.ssot__TopicApiName__c AS TopicName,
    g.responseText__c AS ResponseText,
    c.category__c AS AdherenceLevel,
    c.value__c AS ConfidenceScore
FROM GenAIContentCategory__dlm AS c
JOIN GenAIGeneration__dlm AS g
    ON g.generationId__c = c.parent__c
JOIN ssot__AiAgentInteractionStep__dlm st
    ON st.ssot__GenerationId__c = g.generationId__c
JOIN ssot__AiAgentInteraction__dlm i
    ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
WHERE
    c.detectorType__c = 'InstructionAdherence'
    AND c.category__c = 'Low'
LIMIT 100;
```

**Detector Types:**
- `InstructionAdherence`: Categories are `Low`, `Medium`, `High`
- `TaskResolution`: Categories are `FULLY_RESOLVED`, `PARTIALLY_RESOLVED`, `NOT_RESOLVED`
- `Toxicity`: `value__c >= 0.5` indicates toxic content

### Unresolved Tasks Detection

Find sessions where user requests weren't fully resolved:

```sql
SELECT
    i.ssot__AiAgentSessionId__c AS SessionId,
    i.ssot__TopicApiName__c AS TopicName,
    g.responseText__c AS ResponseText,
    c.category__c AS ResolutionStatus,
    c.value__c AS ConfidenceScore
FROM GenAIContentCategory__dlm AS c
JOIN GenAIGeneration__dlm AS g
    ON g.generationId__c = c.parent__c
JOIN ssot__AiAgentInteractionStep__dlm st
    ON st.ssot__GenerationId__c = g.generationId__c
JOIN ssot__AiAgentInteraction__dlm i
    ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
WHERE
    c.detectorType__c = 'TaskResolution'
    AND c.category__c != 'FULLY_RESOLVED'
LIMIT 100;
```

### Hallucination Detection (UNGROUNDED Responses)

Find responses flagged as ungrounded by the validation prompt:

```sql
-- Note: Uses JSON parsing functions
WITH llmResponses AS (
    SELECT
        i.ssot__AiAgentSessionId__c AS SessionId,
        ssot__InputValueText__c::JSON->'messages'->-1->>'content' AS LastMessage,
        ssot__OutputValueText__c::JSON->>'llmResponse' AS llmResponse,
        st.ssot__StartTimestamp__c AS InteractionStepStartTime
    FROM ssot__AiAgentInteractionStep__dlm st
    JOIN ssot__AiAgentInteraction__dlm i
        ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
    WHERE
        st.ssot__AiAgentInteractionStepType__c = 'LLM_STEP'
        AND st.ssot__Name__c = 'AiCopilot__ReactValidationPrompt'
        AND st.ssot__OutputValueText__c LIKE '%UNGROUNDED%'
    LIMIT 100
)
SELECT
    InteractionStepStartTime,
    SessionId,
    TRIM('"' FROM SPLIT_PART(SPLIT_PART(LastMessage, '"response": "', 2), '"', 1)) AS AgentResponse,
    CAST(llmResponse AS JSON)->>'reason' AS UngroundedReason
FROM llmResponses
ORDER BY InteractionStepStartTime;
```

**Key Step Names for Analysis:**

| Step Name | Purpose |
|-----------|---------|
| `AiCopilot__ReactTopicPrompt` | Topic routing decision |
| `AiCopilot__ReactInitialPrompt` | Initial planning/reasoning |
| `AiCopilot__ReactValidationPrompt` | Response validation (hallucination check) |

---

## Knowledge Retrieval Analysis

### Vector Search for Knowledge Gaps

Query the knowledge search index to understand what chunks were retrieved for a user query:

```sql
SELECT
    v.Score__c AS Score,
    kav.Chat_Answer__c AS KnowledgeAnswer,
    c.Chunk__c AS ChunkText,
    c.SourceRecordId__c AS SourceRecordId,
    c.DataSource__c AS DataSource
FROM vector_search(
    TABLE("External_Knowledge_Search_Index_index__dlm"),
    '{{USER_QUERY}}',
    '{{FILTER_CLAUSE}}',
    30
) v
INNER JOIN "External_Knowledge_Search_Index_chunk__dlm" c
    ON c.RecordId__c = v.RecordId__c
INNER JOIN "{{KNOWLEDGE_ARTICLE_DMO}}" kav
    ON c.SourceRecordId__c = kav.Id__c
ORDER BY Score DESC
LIMIT 10;
```

**Parameters:**
- `{{USER_QUERY}}`: The search query text
- `{{FILTER_CLAUSE}}`: Optional filter like `'Country_Code__c=''US'''`
- `{{KNOWLEDGE_ARTICLE_DMO}}`: Your org's Knowledge DMO name (e.g., `Knowledge_kav_Prod_00D58000000JmkM__dlm`)

### Improving Knowledge Articles Workflow

1. **Identify low-quality moments**: Agentforce Studio → Observe → Optimization → Insights
2. **Filter by topic and quality**: Topics includes `General_FAQ...`, Quality Score < Medium
3. **Get Session ID** from Moments view
4. **Query STDM** with session ID to inspect ACTION_STEP
5. **Examine actionName and actionInput** in step output
6. **Run vector_search** with the user query to see retrieved chunks
7. **Identify SourceRecordId** to find knowledge articles needing improvement

### Inspecting Action Steps for Knowledge Calls

Find ACTION_STEP details for a session:

```sql
SELECT
    st.ssot__Name__c AS ActionName,
    st.ssot__AiAgentInteractionStepType__c AS StepType,
    st.ssot__InputValueText__c AS InputValue,
    st.ssot__OutputValueText__c AS OutputValue,
    st.ssot__StartTimestamp__c AS StartTime
FROM ssot__AiAgentInteractionStep__dlm st
JOIN ssot__AiAgentInteraction__dlm i
    ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
WHERE
    i.ssot__AiAgentSessionId__c = '{{SESSION_ID}}'
    AND st.ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
ORDER BY st.ssot__StartTimestamp__c;
```

**ACTION_STEP Output Contains:**
- `actionName`: The invoked action (e.g., `General_FAQ0_16jWi00000001...`)
- `actionInput`: Parameters passed to the action
- Retrieved knowledge chunks in the response

---

## Advanced CTE Patterns

Complex CTE (Common Table Expression) patterns for advanced session analysis.

### CTE Pattern 1: Session Summary with Stats

Aggregate turn counts and step counts per session:

```sql
WITH session_stats AS (
    SELECT
        s.ssot__Id__c,
        s.ssot__AIAgentApiName__c as agent_name,
        s.ssot__AIAgentSessionEndType__c as end_type,
        COUNT(DISTINCT i.ssot__Id__c) as turn_count,
        COUNT(DISTINCT st.ssot__Id__c) as step_count
    FROM ssot__AIAgentSession__dlm s
    LEFT JOIN ssot__AIAgentInteraction__dlm i
        ON i.ssot__aiAgentSessionId__c = s.ssot__Id__c
    LEFT JOIN ssot__AIAgentInteractionStep__dlm st
        ON st.ssot__AIAgentInteractionId__c = i.ssot__Id__c
    WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
    GROUP BY s.ssot__Id__c, s.ssot__AIAgentApiName__c, s.ssot__AIAgentSessionEndType__c
)
SELECT * FROM session_stats WHERE turn_count > 5
ORDER BY step_count DESC;
```

### CTE Pattern 2: Error Analysis by Topic

Find which topics have the most action errors:

```sql
WITH topic_errors AS (
    SELECT
        i.ssot__TopicApiName__c as topic,
        st.ssot__Name__c as action_name,
        st.ssot__ErrorMessageText__c as error
    FROM ssot__AIAgentInteractionStep__dlm st
    JOIN ssot__AIAgentInteraction__dlm i
        ON st.ssot__AIAgentInteractionId__c = i.ssot__Id__c
    WHERE length(st.ssot__ErrorMessageText__c) > 0
      AND st.ssot__ErrorMessageText__c != 'NOT_SET'
      AND st.ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
)
SELECT topic, action_name, COUNT(*) as error_count
FROM topic_errors
GROUP BY topic, action_name
ORDER BY error_count DESC;
```

### CTE Pattern 3: Session Timeline Reconstruction

Reconstruct the full timeline of events (messages + steps) for a session:

```sql
WITH
  params AS (
    SELECT '{{SESSION_ID}}' AS session_id
  ),
  session_events AS (
    -- Messages
    SELECT
        'MESSAGE' as event_type,
        im.ssot__MessageSentTimestamp__c as timestamp,
        im.ssot__AiAgentInteractionMessageType__c as detail,
        i.ssot__aiAgentSessionId__c as session_id
    FROM ssot__AiAgentInteractionMessage__dlm im
    JOIN ssot__AiAgentInteraction__dlm i
        ON im.ssot__aiAgentInteractionId__c = i.ssot__Id__c
    WHERE i.ssot__aiAgentSessionId__c = (SELECT session_id FROM params)

    UNION ALL

    -- Steps
    SELECT
        st.ssot__AiAgentInteractionStepType__c as event_type,
        st.ssot__StartTimestamp__c as timestamp,
        st.ssot__Name__c as detail,
        i.ssot__aiAgentSessionId__c as session_id
    FROM ssot__AIAgentInteractionStep__dlm st
    JOIN ssot__AiAgentInteraction__dlm i
        ON st.ssot__AIAgentInteractionId__c = i.ssot__Id__c
    WHERE i.ssot__aiAgentSessionId__c = (SELECT session_id FROM params)
  )
SELECT event_type, timestamp, detail
FROM session_events
ORDER BY timestamp ASC;
```

### CTE Pattern 4: Quality Metrics Dashboard

Aggregate quality metrics by detector type:

```sql
WITH quality_summary AS (
    SELECT
        c.detectorType__c,
        c.category__c,
        COUNT(*) as count,
        AVG(TRY_CAST(c.value__c AS DECIMAL)) as avg_score
    FROM GenAIContentCategory__dlm c
    GROUP BY c.detectorType__c, c.category__c
)
SELECT
    detectorType__c as detector,
    category__c as category,
    count,
    ROUND(avg_score, 3) as avg_confidence
FROM quality_summary
ORDER BY detector, count DESC;
```

**Note:** This query requires GenAI Trust Layer DMOs to be enabled.

### CTE Pattern 5: Topic Routing Analysis

Analyze how users are routed between topics within sessions:

```sql
WITH topic_transitions AS (
    SELECT
        curr.ssot__aiAgentSessionId__c as session_id,
        prev.ssot__TopicApiName__c as from_topic,
        curr.ssot__TopicApiName__c as to_topic,
        curr.ssot__StartTimestamp__c as transition_time
    FROM ssot__AIAgentInteraction__dlm curr
    JOIN ssot__AIAgentInteraction__dlm prev
        ON curr.ssot__PrevInteractionId__c = prev.ssot__Id__c
    WHERE curr.ssot__TopicApiName__c != prev.ssot__TopicApiName__c
      AND curr.ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
)
SELECT
    from_topic,
    to_topic,
    COUNT(*) as transition_count
FROM topic_transitions
GROUP BY from_topic, to_topic
ORDER BY transition_count DESC;
```

**Use Cases:**
- Identify common topic escalation paths
- Find topics that frequently need fallback routing
- Understand user journey patterns

---

## Entity Relationship Reference

### Session Tracing Data Model (STDM)

```
Session (ssot__AiAgentSession__dlm)
├── SessionParticipant (ssot__AiAgentSessionParticipant__dlm)  [1:N]
├── Interaction (ssot__AiAgentInteraction__dlm)                [1:N]
│   ├── InteractionMessage (ssot__AiAgentInteractionMessage__dlm)  [1:N]
│   └── InteractionStep (ssot__AiAgentInteractionStep__dlm)        [1:N]
│       └── → links to GenAIGeneration via GenerationId
└── Moment (ssot__AiAgentMoment__dlm)                          [1:N]
```

### Quality Data Model (GenAI Trust Layer)

```
GenAIGeneration__dlm
└── GenAIContentQuality__dlm          [1:1]
    └── GenAIContentCategory__dlm     [1:N]
        ├── detectorType__c: 'Toxicity' | 'InstructionAdherence' | 'TaskResolution'
        ├── category__c: Result category
        └── value__c: Confidence score (0.0-1.0, string format)
```

**Key Join Fields:**
- `ssot__GenerationId__c` on Steps → `generationId__c` on Generation
- `parent__c` on ContentQuality → `generationId__c` on Generation
- `parent__c` on ContentCategory → `id__c` on ContentQuality

---

## Template Variables

The query templates use these placeholders:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{START_DATE}}` | Start timestamp | `2026-01-01T00:00:00.000Z` |
| `{{END_DATE}}` | End timestamp | `2026-01-28T23:59:59.000Z` |
| `{{AGENT_NAMES}}` | Comma-separated agent names | `'Agent1', 'Agent2'` |
| `{{SESSION_IDS}}` | Comma-separated session IDs | `'a0x...', 'a0x...'` |
| `{{SESSION_ID}}` | Single session ID | `'01999669-0a54-724f-80d6-9cb495a7cee4'` |
| `{{INTERACTION_IDS}}` | Comma-separated interaction IDs | `'a0y...', 'a0y...'` |
