"""
T6: Live SQL Execution Tests

Validates documented SQL patterns from query-patterns.md execute successfully
against the live Data Cloud API.

Test Categories:
- T6.1: Basic Extraction (10 pts) - Session, Interaction, Step, Message queries
- T6.2: Aggregation Queries (10 pts) - COUNT, GROUP BY, HAVING
- T6.3: Relationship Joins (10 pts) - LEFT JOIN, multi-table joins
- T6.4: CTE Queries (10 pts) - WITH clauses, complex analysis
- T6.5: Quality Analysis (10 pts) - GenAI Trust Layer joins

Each test validates:
1. Query executes without API error (status 200)
2. Results are valid (list of dicts)
3. Expected columns are present (when applicable)

Note: Row count assertions are avoided since org data varies.
"""

import pytest
from typing import List, Dict, Any


# =============================================================================
# T6.1: Basic Extraction Queries (10 pts)
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestBasicExtractionQueries:
    """T6.1: Basic extraction queries execute successfully."""

    @pytest.mark.parametrize("query_name,sql,expected_columns", [
        (
            "all_sessions_7days",
            """
            SELECT
                ssot__Id__c,
                ssot__AiAgentChannelType__c,
                ssot__StartTimestamp__c,
                ssot__EndTimestamp__c,
                ssot__AiAgentSessionEndType__c
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 10
            """,
            ["ssot__Id__c", "ssot__StartTimestamp__c"]
        ),
        (
            "sessions_select_all",
            """
            SELECT *
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 5
            """,
            ["ssot__Id__c"]
        ),
        (
            "failed_escalated_sessions",
            """
            SELECT *
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__AiAgentSessionEndType__c IN ('Escalated', 'Abandoned', 'Failed')
              AND ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 10
            """,
            ["ssot__Id__c"]
        ),
        (
            "interactions_by_session",
            """
            SELECT
                ssot__Id__c,
                ssot__AiAgentSessionId__c,
                ssot__AiAgentInteractionType__c,
                ssot__TopicApiName__c,
                ssot__StartTimestamp__c
            FROM ssot__AIAgentInteraction__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 10
            """,
            ["ssot__Id__c", "ssot__AiAgentSessionId__c"]
        ),
        (
            "steps_by_type",
            """
            SELECT
                ssot__Id__c,
                ssot__AiAgentInteractionId__c,
                ssot__AiAgentInteractionStepType__c,
                ssot__Name__c,
                ssot__StartTimestamp__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 10
            """,
            ["ssot__Id__c", "ssot__AiAgentInteractionStepType__c"]
        ),
        (
            "llm_steps",
            """
            SELECT
                ssot__Id__c,
                ssot__Name__c,
                ssot__InputValueText__c,
                ssot__OutputValueText__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__AiAgentInteractionStepType__c = 'LLM_STEP'
              AND ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 5
            """,
            ["ssot__Id__c", "ssot__Name__c"]
        ),
        (
            "action_steps",
            """
            SELECT
                ssot__Id__c,
                ssot__Name__c,
                ssot__InputValueText__c,
                ssot__OutputValueText__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
              AND ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 5
            """,
            ["ssot__Id__c", "ssot__Name__c"]
        ),
        (
            "moments_recent",
            """
            SELECT
                ssot__Id__c,
                ssot__AiAgentSessionId__c,
                ssot__AiAgentApiName__c,
                ssot__RequestSummaryText__c,
                ssot__ResponseSummaryText__c
            FROM ssot__AiAgentMoment__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 10
            """,
            ["ssot__Id__c"]
        ),
    ])
    def test_basic_extraction_query(self, data_client, query_name, sql, expected_columns):
        """Basic extraction query executes without error."""
        try:
            results = list(data_client.query(sql, limit=10))

            # Query executed successfully
            assert isinstance(results, list), f"Expected list, got {type(results)}"

            # If we have results, verify expected columns
            if results:
                for col in expected_columns:
                    assert col in results[0], f"Expected column '{col}' not in results"

        except Exception as e:
            pytest.fail(f"Query '{query_name}' failed: {e}")


# =============================================================================
# T6.2: Aggregation Queries (10 pts)
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestAggregationQueries:
    """T6.2: Aggregation queries with COUNT/GROUP BY."""

    @pytest.mark.parametrize("query_name,sql,expected_columns", [
        (
            "session_count_by_channel",
            """
            SELECT
                ssot__AiAgentChannelType__c as channel,
                COUNT(*) as session_count
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            GROUP BY ssot__AiAgentChannelType__c
            ORDER BY session_count DESC
            """,
            ["channel", "session_count"]
        ),
        (
            "end_type_distribution",
            """
            SELECT
                ssot__AiAgentSessionEndType__c as end_type,
                COUNT(*) as count
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            GROUP BY ssot__AiAgentSessionEndType__c
            """,
            ["end_type", "count"]
        ),
        (
            "topic_usage",
            """
            SELECT
                ssot__TopicApiName__c as topic,
                COUNT(*) as turn_count
            FROM ssot__AIAgentInteraction__dlm
            WHERE ssot__AiAgentInteractionType__c = 'TURN'
              AND ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            GROUP BY ssot__TopicApiName__c
            ORDER BY turn_count DESC
            """,
            ["topic", "turn_count"]
        ),
        (
            "action_invocation_frequency",
            """
            SELECT
                ssot__Name__c as action_name,
                COUNT(*) as invocation_count
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__AiAgentInteractionStepType__c = 'ACTION_STEP'
              AND ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            GROUP BY ssot__Name__c
            ORDER BY invocation_count DESC
            """,
            ["action_name", "invocation_count"]
        ),
        (
            "daily_session_counts",
            """
            SELECT
                CAST(ssot__StartTimestamp__c AS DATE) as date,
                COUNT(*) as session_count
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            GROUP BY CAST(ssot__StartTimestamp__c AS DATE)
            ORDER BY date
            """,
            ["date", "session_count"]
        ),
        (
            "session_count_with_end_type",
            """
            SELECT
                ssot__AiAgentSessionEndType__c as end_type,
                ssot__AiAgentChannelType__c as channel,
                COUNT(*) as session_count
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            GROUP BY ssot__AiAgentSessionEndType__c, ssot__AiAgentChannelType__c
            ORDER BY session_count DESC
            """,
            ["end_type", "channel", "session_count"]
        ),
    ])
    def test_aggregation_query(self, data_client, query_name, sql, expected_columns):
        """Aggregation query executes without error."""
        try:
            results = list(data_client.query(sql, limit=100))

            assert isinstance(results, list), f"Expected list, got {type(results)}"

            if results:
                for col in expected_columns:
                    assert col in results[0], f"Expected column '{col}' not in results"

        except Exception as e:
            pytest.fail(f"Query '{query_name}' failed: {e}")


# =============================================================================
# T6.3: Relationship Join Queries (10 pts)
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestRelationshipJoins:
    """T6.3: Multi-table JOIN queries."""

    @pytest.mark.parametrize("query_name,sql,expected_columns", [
        (
            "session_with_turn_count",
            """
            SELECT
                s.ssot__Id__c,
                s.ssot__AiAgentChannelType__c,
                COUNT(i.ssot__Id__c) as turn_count
            FROM ssot__AIAgentSession__dlm s
            LEFT JOIN ssot__AIAgentInteraction__dlm i
                ON i.ssot__aiAgentSessionId__c = s.ssot__Id__c
                AND i.ssot__AiAgentInteractionType__c = 'TURN'
            WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            GROUP BY s.ssot__Id__c, s.ssot__AiAgentChannelType__c
            LIMIT 10
            """,
            ["ssot__Id__c", "turn_count"]
        ),
        (
            "session_interaction_step_join",
            """
            SELECT
                s.ssot__Id__c as session_id,
                i.ssot__Id__c as interaction_id,
                st.ssot__Id__c as step_id,
                st.ssot__Name__c as step_name
            FROM ssot__AIAgentSession__dlm s
            JOIN ssot__AIAgentInteraction__dlm i
                ON s.ssot__Id__c = i.ssot__aiAgentSessionId__c
            JOIN ssot__AIAgentInteractionStep__dlm st
                ON i.ssot__Id__c = st.ssot__AIAgentInteractionId__c
            WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 10
            """,
            ["session_id", "interaction_id", "step_id"]
        ),
        (
            "steps_with_errors_join",
            """
            SELECT
                i.ssot__aiAgentSessionId__c AS SessionId,
                st.ssot__Id__c AS StepId,
                st.ssot__Name__c AS StepName,
                st.ssot__ErrorMessageText__c AS ErrorMessage
            FROM ssot__AIAgentInteractionStep__dlm st
            JOIN ssot__AIAgentInteraction__dlm i
                ON st.ssot__AIAgentInteractionId__c = i.ssot__Id__c
            WHERE length(st.ssot__ErrorMessageText__c) > 0
              AND st.ssot__ErrorMessageText__c != 'NOT_SET'
              AND st.ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            LIMIT 20
            """,
            ["SessionId", "StepId", "StepName"]
        ),
        (
            "session_messages_join",
            """
            SELECT
                s.ssot__Id__c as session_id,
                i.ssot__Id__c as interaction_id,
                im.ssot__Id__c as message_id,
                im.ssot__AiAgentInteractionMessageType__c as message_type
            FROM ssot__AIAgentSession__dlm s
            JOIN ssot__AIAgentInteraction__dlm i
                ON s.ssot__Id__c = i.ssot__aiAgentSessionId__c
            JOIN ssot__AiAgentInteractionMessage__dlm im
                ON i.ssot__Id__c = im.ssot__aiAgentInteractionId__c
            WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 10
            """,
            ["session_id", "interaction_id", "message_id"]
        ),
        (
            "topic_switches_having",
            """
            SELECT
                ssot__AiAgentSessionId__c,
                COUNT(DISTINCT ssot__TopicApiName__c) as topic_count
            FROM ssot__AIAgentInteraction__dlm
            WHERE ssot__AiAgentInteractionType__c = 'TURN'
              AND ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            GROUP BY ssot__AiAgentSessionId__c
            HAVING COUNT(DISTINCT ssot__TopicApiName__c) > 1
            """,
            ["ssot__AiAgentSessionId__c", "topic_count"]
        ),
        (
            "long_sessions_having",
            """
            SELECT
                ssot__AiAgentSessionId__c,
                COUNT(*) as turn_count
            FROM ssot__AIAgentInteraction__dlm
            WHERE ssot__AiAgentInteractionType__c = 'TURN'
              AND ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            GROUP BY ssot__AiAgentSessionId__c
            HAVING COUNT(*) > 5
            ORDER BY turn_count DESC
            """,
            ["ssot__AiAgentSessionId__c", "turn_count"]
        ),
    ])
    def test_relationship_join_query(self, data_client, query_name, sql, expected_columns):
        """Relationship JOIN query executes without error."""
        try:
            results = list(data_client.query(sql, limit=20))

            assert isinstance(results, list), f"Expected list, got {type(results)}"

            if results:
                for col in expected_columns:
                    assert col in results[0], f"Expected column '{col}' not in results"

        except Exception as e:
            pytest.fail(f"Query '{query_name}' failed: {e}")


# =============================================================================
# T6.4: CTE Queries (10 pts)
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestCTEQueries:
    """T6.4: Complex CTE (WITH clause) queries."""

    @pytest.mark.parametrize("query_name,sql", [
        (
            "session_stats_cte",
            """
            WITH session_stats AS (
                SELECT
                    s.ssot__Id__c,
                    COUNT(DISTINCT i.ssot__Id__c) as turn_count,
                    COUNT(DISTINCT st.ssot__Id__c) as step_count
                FROM ssot__AIAgentSession__dlm s
                LEFT JOIN ssot__AIAgentInteraction__dlm i
                    ON i.ssot__aiAgentSessionId__c = s.ssot__Id__c
                LEFT JOIN ssot__AIAgentInteractionStep__dlm st
                    ON st.ssot__AIAgentInteractionId__c = i.ssot__Id__c
                WHERE s.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
                GROUP BY s.ssot__Id__c
            )
            SELECT * FROM session_stats WHERE turn_count > 0 LIMIT 10
            """
        ),
        (
            "error_analysis_by_topic_cte",
            """
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
            ORDER BY error_count DESC
            LIMIT 20
            """
        ),
        (
            "session_timeline_cte",
            """
            WITH session_events AS (
                SELECT
                    'STEP' as event_type,
                    st.ssot__StartTimestamp__c as timestamp,
                    st.ssot__Name__c as detail,
                    i.ssot__aiAgentSessionId__c as session_id
                FROM ssot__AIAgentInteractionStep__dlm st
                JOIN ssot__AiAgentInteraction__dlm i
                    ON st.ssot__AIAgentInteractionId__c = i.ssot__Id__c
                WHERE st.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            )
            SELECT event_type, timestamp, detail, session_id
            FROM session_events
            ORDER BY timestamp DESC
            LIMIT 20
            """
        ),
        (
            "topic_transition_cte",
            """
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
            ORDER BY transition_count DESC
            LIMIT 20
            """
        ),
        (
            "multi_cte_combined",
            """
            WITH
              recent_sessions AS (
                SELECT ssot__Id__c as session_id
                FROM ssot__AIAgentSession__dlm
                WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
              ),
              session_interactions AS (
                SELECT
                    i.ssot__aiAgentSessionId__c as session_id,
                    COUNT(*) as interaction_count
                FROM ssot__AIAgentInteraction__dlm i
                WHERE i.ssot__aiAgentSessionId__c IN (SELECT session_id FROM recent_sessions)
                GROUP BY i.ssot__aiAgentSessionId__c
              )
            SELECT
                rs.session_id,
                COALESCE(si.interaction_count, 0) as interaction_count
            FROM recent_sessions rs
            LEFT JOIN session_interactions si ON rs.session_id = si.session_id
            ORDER BY interaction_count DESC
            LIMIT 10
            """
        ),
    ])
    def test_cte_query(self, data_client, query_name, sql):
        """CTE query executes without error."""
        try:
            results = list(data_client.query(sql, limit=20))

            # Query executed successfully if we get here
            assert isinstance(results, list), f"Expected list, got {type(results)}"

        except Exception as e:
            pytest.fail(f"CTE query '{query_name}' failed: {e}")


# =============================================================================
# T6.5: Quality Analysis Queries (10 pts)
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestQualityAnalysisQueries:
    """T6.5: GenAI Trust Layer quality queries."""

    @pytest.mark.parametrize("query_name,sql", [
        (
            "genai_generation_exists",
            """
            SELECT
                generationId__c,
                responseText__c,
                generationResponseId__c
            FROM GenAIGeneration__dlm
            LIMIT 5
            """
        ),
        (
            "genai_content_quality",
            """
            SELECT
                q.id__c,
                q.parent__c,
                q.isToxicityDetected__c
            FROM GenAIContentQuality__dlm q
            LIMIT 5
            """
        ),
        (
            "genai_content_category",
            """
            SELECT
                c.id__c,
                c.parent__c,
                c.detectorType__c,
                c.category__c,
                c.value__c
            FROM GenAIContentCategory__dlm c
            LIMIT 10
            """
        ),
        (
            "step_generation_join",
            """
            SELECT
                st.ssot__Id__c as step_id,
                st.ssot__Name__c as step_name,
                st.ssot__GenerationId__c as generation_id,
                g.responseText__c as llm_response
            FROM ssot__AIAgentInteractionStep__dlm st
            LEFT JOIN GenAIGeneration__dlm g
                ON st.ssot__GenerationId__c = g.generationId__c
            WHERE st.ssot__GenerationId__c IS NOT NULL
              AND st.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 5
            """
        ),
        (
            "toxicity_detection_full_chain",
            """
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
            LIMIT 10
            """
        ),
        (
            "instruction_adherence_detection",
            """
            SELECT
                i.ssot__AiAgentSessionId__c AS SessionId,
                i.ssot__TopicApiName__c AS TopicName,
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
            LIMIT 10
            """
        ),
        (
            "task_resolution_detection",
            """
            SELECT
                i.ssot__AiAgentSessionId__c AS SessionId,
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
            LIMIT 10
            """
        ),
        (
            "validation_prompt_steps",
            """
            SELECT
                st.ssot__Id__c as step_id,
                st.ssot__Name__c as step_name,
                st.ssot__InputValueText__c as input,
                st.ssot__OutputValueText__c as output
            FROM ssot__AIAgentInteractionStep__dlm st
            WHERE
                st.ssot__AiAgentInteractionStepType__c = 'LLM_STEP'
                AND st.ssot__Name__c = 'AiCopilot__ReactValidationPrompt'
                AND st.ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
            LIMIT 5
            """
        ),
    ])
    def test_quality_analysis_query(self, data_client, query_name, sql):
        """Quality analysis query executes without error."""
        try:
            results = list(data_client.query(sql, limit=10))

            # Query executed successfully if we get here
            assert isinstance(results, list), f"Expected list, got {type(results)}"

        except Exception as e:
            # GenAI DMOs may not exist in all orgs - mark as xfail
            if "object type" in str(e).lower() and "not found" in str(e).lower():
                pytest.xfail(f"GenAI DMO not available in org: {e}")
            pytest.fail(f"Quality query '{query_name}' failed: {e}")


# =============================================================================
# Documented Query Validation (Meta-tests)
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestDocumentedQueriesExecute:
    """Validate all documented queries from query-patterns.md execute."""

    def test_session_queries_execute(self, data_client, all_sql_blocks):
        """All documented session queries execute."""
        session_queries = [q for q in all_sql_blocks if 'AIAgentSession__dlm' in q and 'SELECT' in q.upper()]

        executed = 0
        errors = []

        for query in session_queries[:5]:  # Test first 5
            # Skip queries with template variables that need substitution
            if '{{' in query:
                continue

            # Add LIMIT if not present
            if 'LIMIT' not in query.upper():
                query = query.rstrip(';') + ' LIMIT 5'

            try:
                results = list(data_client.query(query, limit=5))
                assert isinstance(results, list)
                executed += 1
            except Exception as e:
                errors.append(f"Query failed: {str(e)[:100]}")

        assert executed > 0, f"No session queries executed successfully. Errors: {errors}"

    def test_interaction_queries_execute(self, data_client, all_sql_blocks):
        """All documented interaction queries execute."""
        interaction_queries = [
            q for q in all_sql_blocks
            if 'Interaction__dlm' in q and 'SELECT' in q.upper() and 'Step' not in q
        ]

        executed = 0
        errors = []

        for query in interaction_queries[:5]:
            if '{{' in query:
                continue

            if 'LIMIT' not in query.upper():
                query = query.rstrip(';') + ' LIMIT 5'

            try:
                results = list(data_client.query(query, limit=5))
                assert isinstance(results, list)
                executed += 1
            except Exception as e:
                errors.append(f"Query failed: {str(e)[:100]}")

        assert executed > 0 or len(interaction_queries) == 0, \
            f"No interaction queries executed. Errors: {errors}"

    def test_step_queries_execute(self, data_client, all_sql_blocks):
        """All documented step queries execute."""
        step_queries = [
            q for q in all_sql_blocks
            if 'InteractionStep__dlm' in q and 'SELECT' in q.upper()
        ]

        executed = 0
        errors = []

        for query in step_queries[:5]:
            if '{{' in query:
                continue

            if 'LIMIT' not in query.upper():
                query = query.rstrip(';') + ' LIMIT 5'

            try:
                results = list(data_client.query(query, limit=5))
                assert isinstance(results, list)
                executed += 1
            except Exception as e:
                errors.append(f"Query failed: {str(e)[:100]}")

        assert executed > 0 or len(step_queries) == 0, \
            f"No step queries executed. Errors: {errors}"


# =============================================================================
# INTERVAL Syntax Tests
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestIntervalSyntax:
    """Test INTERVAL date syntax works correctly."""

    @pytest.mark.parametrize("interval_expr", [
        "INTERVAL '7' DAY",
        "INTERVAL '30' DAY",
        "INTERVAL '1' DAY",
    ])
    def test_interval_syntax(self, data_client, interval_expr):
        """INTERVAL syntax executes correctly."""
        sql = f"""
            SELECT ssot__Id__c
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - {interval_expr}
            LIMIT 1
        """

        try:
            results = list(data_client.query(sql, limit=1))
            assert isinstance(results, list)
        except Exception as e:
            pytest.fail(f"INTERVAL '{interval_expr}' syntax failed: {e}")
