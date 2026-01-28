# Data Cloud Query Patterns

Common query patterns for extracting and analyzing Agentforce session tracing data.

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

## Template Variables

The query templates use these placeholders:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{START_DATE}}` | Start timestamp | `2026-01-01T00:00:00.000Z` |
| `{{END_DATE}}` | End timestamp | `2026-01-28T23:59:59.000Z` |
| `{{AGENT_NAMES}}` | Comma-separated agent names | `'Agent1', 'Agent2'` |
| `{{SESSION_IDS}}` | Comma-separated session IDs | `'a0x...', 'a0x...'` |
| `{{INTERACTION_IDS}}` | Comma-separated interaction IDs | `'a0y...', 'a0y...'` |
