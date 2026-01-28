-- Extract sessions from Data Cloud
-- DMO: ssot__AIAgentSession__dlm
--
-- Usage: Replace {{START_DATE}}, {{END_DATE}}, and optionally {{AGENT_NAMES}}
--
-- This query extracts session-level data including:
-- - Session ID and timestamps
-- - Agent that handled the session
-- - How the session ended (Completed, Abandoned, Escalated, etc.)
-- - Related messaging session (if applicable)

SELECT
    ssot__Id__c,
    ssot__AIAgentApiName__c,
    ssot__StartTimestamp__c,
    ssot__EndTimestamp__c,
    ssot__AIAgentSessionEndType__c,
    ssot__RelatedMessagingSessionId__c,
    ssot__OrganizationId__c
FROM ssot__AIAgentSession__dlm
WHERE ssot__StartTimestamp__c >= '{{START_DATE}}'
  AND ssot__StartTimestamp__c < '{{END_DATE}}'
  -- Optional: Filter by agent names
  -- AND ssot__AIAgentApiName__c IN ({{AGENT_NAMES}})
ORDER BY ssot__StartTimestamp__c;


-- ============================================================================
-- EXAMPLE QUERIES
-- ============================================================================

-- Last 7 days of sessions
-- SELECT * FROM ssot__AIAgentSession__dlm
-- WHERE ssot__StartTimestamp__c >= '2026-01-21T00:00:00.000Z'
-- ORDER BY ssot__StartTimestamp__c;

-- Sessions for specific agent
-- SELECT * FROM ssot__AIAgentSession__dlm
-- WHERE ssot__AIAgentApiName__c = 'Customer_Support_Agent'
--   AND ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z';

-- Failed/escalated sessions only
-- SELECT * FROM ssot__AIAgentSession__dlm
-- WHERE ssot__AIAgentSessionEndType__c IN ('Escalated', 'Abandoned', 'Failed')
--   AND ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z';

-- Session count by agent
-- SELECT
--     ssot__AIAgentApiName__c,
--     COUNT(*) as session_count
-- FROM ssot__AIAgentSession__dlm
-- WHERE ssot__StartTimestamp__c >= '2026-01-01T00:00:00.000Z'
-- GROUP BY ssot__AIAgentApiName__c;
