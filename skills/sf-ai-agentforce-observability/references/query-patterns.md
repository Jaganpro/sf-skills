<!-- Parent: sf-ai-agentforce-observability/SKILL.md -->
# Data Cloud Query Patterns

Common query patterns for extracting and analyzing Agentforce session tracing data.

> **Official Reference**: [Get Insights from Agent Session Tracing Data](https://help.salesforce.com/s/articleView?id=ai.generative_ai_session_trace_use.htm)

## Basic Extraction Queries

### All Sessions (Last 7 Days)

```sql
SELECT
    ssot__Id__c,
    ssot__AiAgentChannelType__c,
    ssot__StartTimestamp__c,
    ssot__EndTimestamp__c,
    ssot__AiAgentSessionEndType__c
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-21T00:00:00.000Z'
ORDER BY ssot__StartTimestamp__c DESC;
```

### Sessions by Agent (via Moment Join)

> **Note:** Agent name is stored on the Moment table, not Session. Use a JOIN to filter by agent.

```sql
SELECT DISTINCT s.*
FROM ssot__AIAgentSession__dlm s
JOIN ssot__AiAgentMoment__dlm m
    ON m.ssot__AiAgentSessionId__c = s.ssot__Id__c
WHERE m.ssot__AiAgentApiName__c = 'Customer_Support_Agent'
  AND s.ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
ORDER BY s.ssot__StartTimestamp__c DESC;
```

### Failed/Escalated Sessions

```sql
SELECT *
FROM ssot__AIAgentSession__dlm
WHERE ssot__AiAgentSessionEndType__c IN ('Escalated', 'Abandoned', 'Failed')
  AND ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
ORDER BY ssot__StartTimestamp__c DESC;
```

---

## Aggregation Queries

### Session Count by Agent (via Moment)

> **Note:** Agent name is on the Moment table. Query Moments and count distinct sessions.

```sql
SELECT
    ssot__AiAgentApiName__c as agent,
    COUNT(DISTINCT ssot__AiAgentSessionId__c) as session_count
FROM ssot__AiAgentMoment__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY ssot__AiAgentApiName__c
ORDER BY session_count DESC;
```

### End Type Distribution

```sql
SELECT
    ssot__AiAgentSessionEndType__c as end_type,
    COUNT(*) as count
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY ssot__AiAgentSessionEndType__c;
```

### Topic Usage

```sql
SELECT
    ssot__TopicApiName__c as topic,
    COUNT(*) as turn_count
FROM ssot__AIAgentInteraction__dlm
WHERE ssot__AiAgentInteractionType__c = 'TURN'
GROUP BY ssot__TopicApiName__c
ORDER BY turn_count DESC;
```

### Action Invocation Frequency

```sql
SELECT
    ssot__Name__c as action_name,
    COUNT(*) as invocation_count
FROM ssot__AIAgentInteractionStep__dlm
WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
GROUP BY ssot__Name__c
ORDER BY invocation_count DESC;
```

---

## Relationship Queries

### Session with Turn Count

```sql
SELECT
    s.ssot__Id__c,
    s.ssot__AiAgentChannelType__c,
    COUNT(i.ssot__Id__c) as turn_count
FROM ssot__AIAgentSession__dlm s
LEFT JOIN ssot__AIAgentInteraction__dlm i
    ON i.ssot__AiAgentSessionId__c = s.ssot__Id__c
    AND i.ssot__AiAgentInteractionType__c = 'TURN'
WHERE s.ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
GROUP BY s.ssot__Id__c, s.ssot__AiAgentChannelType__c;
```

### Complete Session Tree

```sql
-- Step 1: Get session
SELECT * FROM ssot__AIAgentSession__dlm
WHERE ssot__Id__c = 'a0x1234567890ABC';

-- Step 2: Get interactions
SELECT * FROM ssot__AIAgentInteraction__dlm
WHERE ssot__AiAgentSessionId__c = 'a0x1234567890ABC';

-- Step 3: Get steps (using interaction IDs from step 2)
SELECT * FROM ssot__AIAgentInteractionStep__dlm
WHERE ssot__AiAgentInteractionId__c IN ('a0y...', 'a0y...');

-- Step 4: Get messages (using interaction IDs from step 2)
SELECT * FROM ssot__AIAgentMoment__dlm
WHERE ssot__AiAgentInteractionId__c IN ('a0y...', 'a0y...');
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
    ssot__AiAgentSessionId__c,
    COUNT(DISTINCT ssot__TopicApiName__c) as topic_count
FROM ssot__AIAgentInteraction__dlm
WHERE ssot__AiAgentInteractionType__c = 'TURN'
GROUP BY ssot__AiAgentSessionId__c
HAVING COUNT(DISTINCT ssot__TopicApiName__c) > 1;
```

### Long Sessions (Many Turns)

```sql
SELECT
    ssot__AiAgentSessionId__c,
    COUNT(*) as turn_count
FROM ssot__AIAgentInteraction__dlm
WHERE ssot__AiAgentInteractionType__c = 'TURN'
GROUP BY ssot__AiAgentSessionId__c
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
WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
GROUP BY ssot__Name__c;
```

---

## Performance Tips

### Use Date Filters Early

```sql
-- Good: Filter by date first
WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
  AND ssot__AiAgentSessionEndType__c = 'Completed'

-- Avoid: No date filter on large tables
WHERE ssot__AiAgentSessionEndType__c = 'Completed'
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
SELECT ssot__Id__c, ssot__AiAgentChannelType__c, ssot__StartTimestamp__c
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
    ON s.ssot__id__c = sp.ssot__AiAgentSessionId__c
JOIN ssot__AiAgentInteraction__dlm i
    ON s.ssot__id__c = i.ssot__AiAgentSessionId__c
JOIN ssot__AiAgentInteractionMessage__dlm im
    ON i.ssot__id__c = im.ssot__AiAgentInteractionId__c
JOIN ssot__AiAgentInteractionStep__dlm st
    ON i.ssot__id__c = st.ssot__AiAgentInteractionId__c
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
      ON i.ssot__Id__c = im.ssot__AiAgentInteractionId__c
    WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)
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
      ON i.ssot__Id__c = st.ssot__AiAgentInteractionId__c
    WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)
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

**Detector Types (Live API Verified - T6 Discovery):**

| Detector Type | Occurrences | Categories/Values |
|---------------|-------------|-------------------|
| `TOXICITY` | 627,603 | `hate`, `identity`, `physical`, `profanity`, `safety_score`, `sexual`, `toxicity`, `violence` |
| `PROMPT_DEFENSE` | 119,050 | `aggregatePromptAttackScore`, `isPromptAttackDetected` |
| `PII` | 27,805 | `CREDIT_CARD`, `EMAIL_ADDRESS`, `PERSON`, `US_PHONE_NUMBER` |
| `InstructionAdherence` | 16,380 | `High`, `Low`, `Uncertain` |

**Detection Thresholds:**
- **Toxicity**: `value__c >= 0.5` indicates toxic content
- **PII**: Any category present indicates PII detection
- **PROMPT_DEFENSE**: `isPromptAttackDetected` = `true` indicates attack
- **InstructionAdherence**: `Low` category indicates poor adherence

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

### PII Detection Analysis ✅ NEW

Find sessions where PII was detected in user inputs or agent responses:

```sql
SELECT
    c.category__c AS PiiType,
    COUNT(*) AS DetectionCount
FROM GenAIContentCategory__dlm c
WHERE c.detectorType__c = 'PII'
  AND c.timestamp__c >= current_date - INTERVAL '30' DAY
GROUP BY c.category__c
ORDER BY DetectionCount DESC;
```

**PII Categories:**
| Category | Description |
|----------|-------------|
| `CREDIT_CARD` | Credit card numbers |
| `EMAIL_ADDRESS` | Email addresses |
| `PERSON` | Person names |
| `US_PHONE_NUMBER` | US phone numbers |

### Prompt Attack Detection ✅ NEW

Find sessions with potential prompt injection attacks:

```sql
SELECT
    i.ssot__AiAgentSessionId__c AS SessionId,
    i.ssot__TopicApiName__c AS TopicName,
    c.category__c AS AttackCategory,
    c.value__c AS Score
FROM GenAIContentCategory__dlm c
JOIN GenAIGeneration__dlm g
    ON g.generationId__c = c.parent__c
JOIN ssot__AiAgentInteractionStep__dlm st
    ON st.ssot__GenerationId__c = g.generationId__c
JOIN ssot__AiAgentInteraction__dlm i
    ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
WHERE c.detectorType__c = 'PROMPT_DEFENSE'
  AND c.category__c = 'isPromptAttackDetected'
  AND c.value__c = 'true'
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

## GenAI Gateway Analysis ✅ NEW

Query patterns for analyzing LLM usage, token consumption, and model performance.

### Token Usage by Model

Analyze token consumption across different models:

```sql
SELECT
    model__c AS Model,
    COUNT(*) AS RequestCount,
    SUM(promptTokens__c) AS TotalPromptTokens,
    SUM(completionTokens__c) AS TotalCompletionTokens,
    SUM(totalTokens__c) AS TotalTokens,
    AVG(totalTokens__c) AS AvgTokensPerRequest
FROM GenAIGatewayRequest__dlm
WHERE timestamp__c >= current_date - INTERVAL '7' DAY
GROUP BY model__c
ORDER BY TotalTokens DESC;
```

### Prompt Template Usage

Find which prompt templates are most frequently used:

```sql
SELECT
    promptTemplateDevName__c AS TemplateName,
    promptTemplateVersionNo__c AS Version,
    COUNT(*) AS UsageCount,
    AVG(totalTokens__c) AS AvgTokens
FROM GenAIGatewayRequest__dlm
WHERE timestamp__c >= current_date - INTERVAL '30' DAY
  AND promptTemplateDevName__c IS NOT NULL
GROUP BY promptTemplateDevName__c, promptTemplateVersionNo__c
ORDER BY UsageCount DESC;
```

### Safety Configuration Analysis

Analyze which safety features are enabled across requests:

```sql
SELECT
    enableInputSafetyScoring__c AS InputSafety,
    enableOutputSafetyScoring__c AS OutputSafety,
    enablePiiMasking__c AS PiiMasking,
    COUNT(*) AS RequestCount
FROM GenAIGatewayRequest__dlm
WHERE timestamp__c >= current_date - INTERVAL '7' DAY
GROUP BY enableInputSafetyScoring__c, enableOutputSafetyScoring__c, enablePiiMasking__c
ORDER BY RequestCount DESC;
```

### User Feedback Summary

Analyze user feedback distribution:

```sql
SELECT
    feedback__c AS FeedbackType,
    COUNT(*) AS FeedbackCount
FROM GenAIFeedback__dlm
WHERE timestamp__c >= current_date - INTERVAL '30' DAY
GROUP BY feedback__c
ORDER BY FeedbackCount DESC;
```

### Feedback with Details

Get detailed feedback with user comments:

```sql
SELECT
    f.feedbackId__c,
    f.feedback__c AS FeedbackType,
    f.action__c AS UserAction,
    fd.feedbackText__c AS UserComment,
    f.timestamp__c
FROM GenAIFeedback__dlm f
LEFT JOIN GenAIFeedbackDetail__dlm fd
    ON fd.parent__c = f.feedbackId__c
WHERE f.timestamp__c >= current_date - INTERVAL '7' DAY
ORDER BY f.timestamp__c DESC
LIMIT 100;
```

### High-Cost Requests

Find requests with unusually high token consumption:

```sql
SELECT
    gatewayRequestId__c,
    model__c AS Model,
    promptTokens__c,
    completionTokens__c,
    totalTokens__c,
    feature__c,
    timestamp__c
FROM GenAIGatewayRequest__dlm
WHERE totalTokens__c > 4000
  AND timestamp__c >= current_date - INTERVAL '7' DAY
ORDER BY totalTokens__c DESC
LIMIT 50;
```

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
        s.ssot__AiAgentChannelType__c as channel_type,
        s.ssot__AiAgentSessionEndType__c as end_type,
        COUNT(DISTINCT i.ssot__Id__c) as turn_count,
        COUNT(DISTINCT st.ssot__Id__c) as step_count
    FROM ssot__AIAgentSession__dlm s
    LEFT JOIN ssot__AIAgentInteraction__dlm i
        ON i.ssot__AiAgentSessionId__c = s.ssot__Id__c
    LEFT JOIN ssot__AIAgentInteractionStep__dlm st
        ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
    WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
    GROUP BY s.ssot__Id__c, s.ssot__AiAgentChannelType__c, s.ssot__AiAgentSessionEndType__c
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
        ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
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
        i.ssot__AiAgentSessionId__c as session_id
    FROM ssot__AiAgentInteractionMessage__dlm im
    JOIN ssot__AiAgentInteraction__dlm i
        ON im.ssot__AiAgentInteractionId__c = i.ssot__Id__c
    WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)

    UNION ALL

    -- Steps
    SELECT
        st.ssot__AiAgentInteractionStepType__c as event_type,
        st.ssot__StartTimestamp__c as timestamp,
        st.ssot__Name__c as detail,
        i.ssot__AiAgentSessionId__c as session_id
    FROM ssot__AIAgentInteractionStep__dlm st
    JOIN ssot__AiAgentInteraction__dlm i
        ON st.ssot__AiAgentInteractionId__c = i.ssot__Id__c
    WHERE i.ssot__AiAgentSessionId__c = (SELECT session_id FROM params)
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
        curr.ssot__AiAgentSessionId__c as session_id,
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

## Tag System Queries ✅ NEW

Query the Agentforce tagging system for session categorization and analytics.

### Get Tag Definitions

List all available tag definitions in the org:

```sql
SELECT
    ssot__Id__c,
    ssot__Name__c,
    ssot__DeveloperName__c,
    ssot__Description__c,
    ssot__DataType__c,
    ssot__SourceType__c
FROM ssot__AiAgentTagDefinition__dlm
ORDER BY ssot__CreatedDate__c DESC
LIMIT 50;
```

### Get Tag Values for a Definition

List all values for a specific tag definition:

```sql
SELECT
    t.ssot__Id__c,
    t.ssot__Description__c,
    t.ssot__IsActive__c,
    td.ssot__Name__c as TagDefinitionName
FROM ssot__AiAgentTag__dlm t
JOIN ssot__AiAgentTagDefinition__dlm td
    ON t.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
WHERE td.ssot__DeveloperName__c = 'Escalation_Reason'
  AND t.ssot__IsActive__c = true
ORDER BY t.ssot__CreatedDate__c DESC;
```

### Sessions with Tag Associations

Find sessions that have been tagged:

```sql
SELECT
1000     s.ssot__Id__c AS SessionId,
1001     s.ssot__StartTimestamp__c,
1002     ta.ssot__AiAgentTagDefinitionAssociationId__c AS TagAssociation,
1003     ta.ssot__CreatedDate__c AS TaggedAt
1004 FROM ssot__AIAgentSession__dlm s
1005 JOIN ssot__AiAgentTagAssociation__dlm ta
1006     ON s.ssot__Id__c = ta.ssot__AiAgentSessionId__c
1007 WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
1008 ORDER BY s.ssot__StartTimestamp__c DESC
1009 LIMIT 100;
1010 ```
1011 
1012 ### Tag Distribution Analysis
1013 
1014 Count sessions by tag:
1015 
1016 ```sql
1017 SELECT
1018     td.ssot__Name__c AS TagName,
1019     COUNT(DISTINCT ta.ssot__AiAgentSessionId__c) AS SessionCount
1020 FROM ssot__AiAgentTagAssociation__dlm ta
1021 JOIN ssot__AiAgentTagDefinitionAssociation__dlm tda
1022     ON ta.ssot__AiAgentTagDefinitionAssociationId__c = tda.ssot__Id__c
1023 JOIN ssot__AiAgentTagDefinition__dlm td
1024     ON tda.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
1025 WHERE ta.ssot__CreatedDate__c >= current_date - INTERVAL '30' DAY
1026 GROUP BY td.ssot__Name__c
1027 ORDER BY SessionCount DESC;
1028 ```
1029 
1030 ### Tags by Agent
1031 
1032 Find which tags are configured for each agent:
1033 
1034 ```sql
1035 SELECT
1036     tda.ssot__AiAgentApiName__c AS AgentName,
1037     td.ssot__Name__c AS TagName,
1038     td.ssot__DataType__c AS DataType,
1039     td.ssot__SourceType__c AS SourceType
1040 FROM ssot__AiAgentTagDefinitionAssociation__dlm tda
1041 JOIN ssot__AiAgentTagDefinition__dlm td
1042     ON tda.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
1043 ORDER BY tda.ssot__AiAgentApiName__c, td.ssot__Name__c;
1044 ```
1045 
1046 ### Tag Values with Ratings
1047 
1048 Get tag values (useful for rating-based tags):
1049 
1050 ```sql
1051 SELECT
1052     td.ssot__Name__c AS TagName,
1053     t.ssot__Value__c AS Value,
1054     t.ssot__Description__c AS Description,
1055     t.ssot__IsActive__c AS IsActive
1056 FROM ssot__AiAgentTag__dlm t
1057 JOIN ssot__AiAgentTagDefinition__dlm td
1058     ON t.ssot__AiAgentTagDefinitionId__c = td.ssot__Id__c
1059 WHERE t.ssot__IsActive__c = true
1060 ORDER BY td.ssot__Name__c, t.ssot__Value__c;
1061 ```
1062 
1063 ---
1064 
1065 ## Step Analysis Patterns ✅ NEW
1066 
1067 Query patterns for analyzing step execution, LLM calls, and action performance.
1068 
1069 ### LLM Step Analysis by Prompt Type
1070 
1071 Analyze LLM steps by the prompt type:
1072 
1073 ```sql
1074 SELECT
1075     ssot__Name__c AS PromptName,
1076     COUNT(*) AS Invocations,
1077     AVG(EXTRACT(EPOCH FROM (ssot__EndTimestamp__c - ssot__StartTimestamp__c))) AS AvgDurationSeconds
1078 FROM ssot__AIAgentInteractionStep__dlm
1079 WHERE ssot__AiAgentInteractionStepType__c = 'LLM_STEP'
1080   AND ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
1081   AND ssot__Name__c LIKE 'AiCopilot%'
1082 GROUP BY ssot__Name__c
1083 ORDER BY Invocations DESC;
1084 ```
1085 
1086 ### Common LLM Prompts
1087 
1088 | Prompt Name | Purpose |
1089 |-------------|---------|
1090 | `AiCopilot__ReactInitialPrompt` | Initial planning/reasoning |
1091 | `AiCopilot__ReactTopicPrompt` | Topic classification/routing |
1092 | `AiCopilot__ReactValidationPrompt` | Response validation (hallucination check) |
1093 
1094 ### Top Actions by Invocation
1095 
1096 Find the most frequently called actions:
1097 
1098 ```sql
1099 SELECT
1100     ssot__Name__c AS ActionName,
1101     COUNT(*) AS InvocationCount,
1102     COUNT(CASE WHEN length(ssot__ErrorMessageText__c) > 0
1103                AND ssot__ErrorMessageText__c != 'NOT_SET' THEN 1 END) AS ErrorCount
1104 FROM ssot__AIAgentInteractionStep__dlm
1105 WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
1106   AND ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
1107 GROUP BY ssot__Name__c
1108 ORDER BY InvocationCount DESC
1109 LIMIT 20;
1110 ```
1111 
1112 ### Step Chain Analysis (Following PrevStepId)
1113 
1114 Trace the step execution chain within an interaction:
1115 
1116 ```sql
1117 WITH RECURSIVE step_chain AS (
1118     -- Base: find the first step (no PrevStepId)
1119     SELECT
1120         ssot__Id__c,
1121         ssot__Name__c,
1122         ssot__AiAgentInteractionStepType__c,
1123         ssot__PrevStepId__c,
1124         1 as depth
1125     FROM ssot__AIAgentInteractionStep__dlm
1126     WHERE ssot__AiAgentInteractionId__c = '{{INTERACTION_ID}}'
1127       AND ssot__PrevStepId__c IS NULL
1128 
1129     UNION ALL
1130 
1131     -- Recursive: follow PrevStepId chain
1132     SELECT
1133         s.ssot__Id__c,
1134         s.ssot__Name__c,
1135         s.ssot__AiAgentInteractionStepType__c,
1136         s.ssot__PrevStepId__c,
1137         sc.depth + 1
1138     FROM ssot__AIAgentInteractionStep__dlm s
1139     JOIN step_chain sc ON s.ssot__PrevStepId__c = sc.ssot__Id__c
1140     WHERE sc.depth < 20
1141 )
1142 SELECT depth, ssot__AiAgentInteractionStepType__c, ssot__Name__c
1143 FROM step_chain
1144 ORDER BY depth;
1145 ```
1146 
1147 **Note:** Steps use linear `PrevStepId` sequencing. There is no hierarchical parent-child relationship.
1148 
1149 ---
1150 
1151 ## Moment-Interaction Junction Queries ✅ NEW
1152 
1153 Query the junction table linking Moments to Interactions for many-to-many analysis.
1154 
1155 ### Moments with Their Interactions
1156 
1157 Get all interactions associated with a moment:
1158 
1159 ```sql
1160 SELECT
1161     m.ssot__Id__c AS MomentId,
1162     m.ssot__RequestSummaryText__c,
1163     mi.ssot__AiAgentInteractionId__c AS InteractionId,
1164     i.ssot__TopicApiName__c AS Topic
1165 FROM ssot__AiAgentMoment__dlm m
1166 JOIN ssot__AiAgentMomentInteraction__dlm mi
1167     ON m.ssot__Id__c = mi.ssot__AiAgentMomentId__c
1168 JOIN ssot__AIAgentInteraction__dlm i
1169     ON mi.ssot__AiAgentInteractionId__c = i.ssot__Id__c
1170 WHERE m.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
1171 LIMIT 50;
1172 ```
1173 
1174 ### Interactions per Moment (Aggregated)
1175 
1176 Count interactions associated with each moment:
1177 
1178 ```sql
1179 SELECT
1180     mi.ssot__AiAgentMomentId__c AS MomentId,
1181     COUNT(*) AS InteractionCount
1182 FROM ssot__AiAgentMomentInteraction__dlm mi
1183 GROUP BY mi.ssot__AiAgentMomentId__c
1184 HAVING COUNT(*) > 1
1185 ORDER BY InteractionCount DESC
1186 LIMIT 20;
1187 ```
1188 
1189 ### Full Session Tree with Moments
1190 
1191 Get complete session data including the Moment-Interaction relationship:
1192 
1193 ```sql
1194 SELECT
1195     s.ssot__Id__c AS SessionId,
1196     m.ssot__AiAgentApiName__c AS AgentName,
1197     m.ssot__RequestSummaryText__c AS RequestSummary,
1198     m.ssot__ResponseSummaryText__c AS ResponseSummary,
1199     i.ssot__Id__c AS InteractionId,
1200     i.ssot__TopicApiName__c AS Topic
1201 FROM ssot__AIAgentSession__dlm s
1202 JOIN ssot__AiAgentMoment__dlm m
1203     ON s.ssot__Id__c = m.ssot__AiAgentSessionId__c
1204 LEFT JOIN ssot__AiAgentMomentInteraction__dlm mi
1205     ON m.ssot__Id__c = mi.ssot__AiAgentMomentId__c
1206 LEFT JOIN ssot__AIAgentInteraction__dlm i
1207     ON mi.ssot__AiAgentInteractionId__c = i.ssot__Id__c
1208 WHERE s.ssot__Id__c = '{{SESSION_ID}}'
1209 ORDER BY m.ssot__StartTimestamp__c, i.ssot__StartTimestamp__c;
1210 ```
1211 
1212 ---
1213 
1214 ## Entity Relationship Reference
1215 
1216 ### Session Tracing Data Model (STDM)
1217 
1218 ```
1219 Session (ssot__AiAgentSession__dlm)
1220 ├── SessionParticipant (ssot__AIAgentSessionParticipant__dlm)  [1:N]
1221 ├── Interaction (ssot__AiAgentInteraction__dlm)                [1:N]
1222 │   ├── InteractionMessage (ssot__AiAgentInteractionMessage__dlm)  [1:N]
1223 │   └── InteractionStep (ssot__AiAgentInteractionStep__dlm)        [1:N]
1224 │       └── → links to GenAIGeneration via GenerationId
1225 ├── Moment (ssot__AiAgentMoment__dlm)                          [1:N]
1226 │   └── MomentInteraction (ssot__AiAgentMomentInteraction__dlm)    [N:M junction]
1227 │       └── → links Moment ↔ Interaction
1228 └── TagAssociation (ssot__AiAgentTagAssociation__dlm)          [1:N] ✅ NEW
1229     └── → links to TagDefinition & Tag
1230 ```
1231 
1232 ### Tagging Data Model ✅ NEW
1233 
1234 ```
1235 TagDefinition (ssot__AiAgentTagDefinition__dlm)
1236 └── Tag (ssot__AiAgentTag__dlm)                    [1:N]
1237     └── TagAssociation                              [N:M]
1238         ├── → Session (AiAgentSessionId)
1239         └── → Moment (AiAgentMomentId)
1240 ```
1241 
1242 ### Quality Data Model (GenAI Trust Layer) ✅ T6 Verified
1243 
1244 ```
1245 GenAIGeneration__dlm
1246 ├── GenAIContentQuality__dlm          [1:1]
1247 │   └── GenAIContentCategory__dlm     [1:N]
1248 │       ├── detectorType__c: 'TOXICITY' | 'PII' | 'PROMPT_DEFENSE' | 'InstructionAdherence'
1249 │       ├── category__c: Result category (see tables below)
1250 │       └── value__c: Confidence score (0.0-1.0, string format)
1251 └── GenAIFeedback__dlm                [1:N]
1252     └── GenAIFeedbackDetail__dlm      [1:N]
1253 ```
1254 
1255 **Detector Categories (Live API Verified):**
1256 
1257 | Detector | Categories |
1258 |----------|------------|
1259 | `TOXICITY` | `hate`, `identity`, `physical`, `profanity`, `safety_score`, `sexual`, `toxicity`, `violence` |
1260 | `PII` | `CREDIT_CARD`, `EMAIL_ADDRESS`, `PERSON`, `US_PHONE_NUMBER` |
1261 | `PROMPT_DEFENSE` | `aggregatePromptAttackScore`, `isPromptAttackDetected` |
1262 | `InstructionAdherence` | `High`, `Low`, `Uncertain` |
1263 
1264 ### Gateway Data Model (GenAI Request/Response) ✅ T6 Verified
1265 
1266 ```
1267 GenAIGatewayRequest__dlm (30 fields)
1268 ├── GenAIGatewayResponse__dlm         [1:1]
1269 ├── GenAIGatewayRequestTag__dlm       [1:N]
1270 ├── GenAIGtwyRequestMetadata__dlm     [1:N]
1271 ├── GenAIGtwyObjRecord__dlm           [1:N]
1272 │   └── GenAIGtwyObjRecCitationRef__dlm  [1:N]
1273 └── GenAIGeneration__dlm              [1:N] (via generationGroupId)
1274 ```
1275 
1276 **Key Join Fields:**
1277 - `ssot__GenerationId__c` on Steps → `generationId__c` on Generation
1278 - `ssot__GenAiGatewayRequestId__c` on Steps → `gatewayRequestId__c` on GatewayRequest
1279 - `parent__c` on ContentQuality → `generationId__c` on Generation
1280 - `parent__c` on ContentCategory → `id__c` on ContentQuality
1281 - `parent__c` on FeedbackDetail → `feedbackId__c` on Feedback
1282 
1283 ---
1284 
1285 ## Template Variables
1286 
1287 The query templates use these placeholders:
1288 
1289 | Variable | Description | Example |
1290 |----------|-------------|---------|
1291 | `{{START_DATE}}` | Start timestamp | `2026-01-01T00:00:00.000Z` |
1292 | `{{END_DATE}}` | End timestamp | `2026-01-28T23:59:59.000Z` |
1293 | `{{AGENT_NAMES}}` | Comma-separated agent names | `'Agent1', 'Agent2'` |
1294 | `{{SESSION_IDS}}` | Comma-separated session IDs | `'a0x...', 'a0x...'` |
1295 | `{{SESSION_ID}}` | Single session ID | `'01999669-0a54-724f-80d6-9cb495a7cee4'` |
1296 | `{{INTERACTION_IDS}}` | Comma-separated interaction IDs | `'a0y...', 'a0y...'` |
