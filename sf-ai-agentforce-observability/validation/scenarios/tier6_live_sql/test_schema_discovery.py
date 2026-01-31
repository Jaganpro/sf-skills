"""
T6.D: Schema Discovery Tests

Probes for new DMOs and fields from internal documentation (Jan 2026 diagrams).
Tests are designed to DISCOVER what exists, not assert requirements.

Results inform documentation updates:
- PASS → Field/DMO exists, add to skill documentation
- SKIP (dmo_not_found) → DMO not in this org/API version
- SKIP (field_not_found) → Field not on this DMO

Test Categories:
- T6.D1: New DMO Existence Probes (TelemetryTraceSpan, MomentInteraction, Tags)
- T6.D2: New Field Probes on Existing DMOs
- T6.D3: Enum Value Discovery
- T6.D4: New Relationship Probes

Run with:
    pytest -v -s scenarios/tier6_live_sql/test_schema_discovery.py

For verbose discovery output:
    pytest -v -s --tb=short scenarios/tier6_live_sql/test_schema_discovery.py 2>&1 | tee discovery-results.txt
"""

import pytest
from typing import List, Dict, Any, Optional


# =============================================================================
# Discovery Result Tracking
# =============================================================================

class DiscoveryResult:
    """Track discovery results for documentation updates."""

    def __init__(self):
        self.found_dmos: List[str] = []
        self.missing_dmos: List[str] = []
        self.found_fields: Dict[str, List[str]] = {}  # dmo -> [fields]
        self.missing_fields: Dict[str, List[str]] = {}  # dmo -> [fields]
        self.enum_values: Dict[str, List[str]] = {}  # field -> [values]

    def report(self) -> str:
        """Generate discovery report."""
        lines = ["=" * 60, "SCHEMA DISCOVERY RESULTS", "=" * 60]

        if self.found_dmos:
            lines.append("\n✅ FOUND DMOs (add to documentation):")
            for dmo in self.found_dmos:
                lines.append(f"   - {dmo}")

        if self.missing_dmos:
            lines.append("\n❌ NOT FOUND DMOs (skip in documentation):")
            for dmo in self.missing_dmos:
                lines.append(f"   - {dmo}")

        if self.found_fields:
            lines.append("\n✅ FOUND Fields (add to schema docs):")
            for dmo, fields in self.found_fields.items():
                lines.append(f"   {dmo}:")
                for field in fields:
                    lines.append(f"     - {field}")

        if self.missing_fields:
            lines.append("\n❌ NOT FOUND Fields (skip in schema docs):")
            for dmo, fields in self.missing_fields.items():
                lines.append(f"   {dmo}:")
                for field in fields:
                    lines.append(f"     - {field}")

        if self.enum_values:
            lines.append("\n📊 Discovered Enum Values:")
            for field, values in self.enum_values.items():
                lines.append(f"   {field}:")
                for val in values:
                    lines.append(f"     - {val}")

        lines.append("=" * 60)
        return "\n".join(lines)


# Module-level discovery tracker
discovery = DiscoveryResult()


@pytest.fixture(scope="module", autouse=True)
def print_discovery_report(request):
    """Print discovery report after all tests complete."""
    yield
    print("\n" + discovery.report())


# =============================================================================
# T6.D1: DMO Existence Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestDmoExistenceProbes:
    """
    T6.D1: Probe for new DMO existence.

    These DMOs were identified in internal diagrams (Jan 2026) but may not
    be available in all orgs or API versions.
    """

    @pytest.mark.parametrize("dmo_name,description", [
        # TelemetryTraceSpan - OpenTelemetry distributed tracing
        ("ssot__TelemetryTraceSpan__dlm", "OpenTelemetry span data (ssot prefix)"),
        ("TelemetryTraceSpan__dlm", "OpenTelemetry span data (no ssot prefix)"),

        # AiAgentMomentInteraction - Junction between Moment and Interaction
        ("ssot__AiAgentMomentInteraction__dlm", "Moment-Interaction junction table"),
        ("AiAgentMomentInteraction__dlm", "Moment-Interaction junction (no ssot)"),

        # Tag-related DMOs - Tagging/categorization system
        ("ssot__AiAgentTagAssociation__dlm", "Tag associations to sessions/interactions"),
        ("ssot__AiAgentTagDefinition__dlm", "Tag definitions/metadata"),
        ("ssot__AiAgentTag__dlm", "Tag values"),

        # Alternative naming conventions
        ("AiAgentTagAssociation__dlm", "Tag associations (no ssot)"),
        ("AiAgentTagDefinition__dlm", "Tag definitions (no ssot)"),
        ("AiAgentTag__dlm", "Tag values (no ssot)"),
    ])
    def test_dmo_exists(self, execute_query, dmo_name, description):
        """
        Probe if DMO exists and is queryable.

        Uses SELECT * LIMIT 1 to check existence without requiring
        knowledge of specific column names.
        """
        sql = f"SELECT * FROM {dmo_name} LIMIT 1"
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            # Record as missing and skip
            discovery.missing_dmos.append(dmo_name)
            pytest.skip(f"DMO not found: {dmo_name} - {error}")

        # DMO exists - record and pass
        discovery.found_dmos.append(dmo_name)

        # Log column names if we got results
        if results:
            columns = list(results[0].keys())
            print(f"\n✅ {dmo_name} exists with columns: {columns[:10]}...")  # First 10

        assert success, f"DMO {dmo_name} query unexpectedly failed: {error}"


    def test_telemetry_span_join_to_step(self, execute_query):
        """
        Probe if TelemetryTraceSpan can be joined to InteractionStep.

        Steps have ssot__TelemetryTraceSpanId__c - check if we can join to span table.
        """
        # First check if the span DMO exists
        dmo_candidates = [
            "ssot__TelemetryTraceSpan__dlm",
            "TelemetryTraceSpan__dlm",
        ]

        for dmo_name in dmo_candidates:
            sql = f"""
                SELECT
                    st.ssot__Id__c AS step_id,
                    st.ssot__TelemetryTraceSpanId__c AS span_id,
                    sp.*
                FROM ssot__AIAgentInteractionStep__dlm st
                LEFT JOIN {dmo_name} sp
                    ON st.ssot__TelemetryTraceSpanId__c = sp.ssot__Id__c
                WHERE st.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
                LIMIT 1
            """

            success, results, error = execute_query(sql, skip_if_template_missing=False)

            if success:
                print(f"\n✅ {dmo_name} is joinable to InteractionStep via TelemetryTraceSpanId")
                if results:
                    print(f"   Sample span columns: {list(results[0].keys())[:15]}")
                return

        pytest.skip("TelemetryTraceSpan DMO not found or not joinable")


# =============================================================================
# T6.D2: Field Existence Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestFieldExistenceProbes:
    """
    T6.D2: Probe for new fields on existing DMOs.

    These fields were identified in internal diagrams but may not be
    documented or available in all API versions.
    """

    def test_message_timestamp_fields(self, execute_query):
        """
        Probe for MessageStartTimestamp and MessageEndTimestamp on Message DMO.

        Diagrams show these as separate from the general Start/EndTimestamp.
        """
        sql = """
            SELECT
                ssot__Id__c,
                ssot__MessageStartTimestamp__c,
                ssot__MessageEndTimestamp__c
            FROM ssot__AiAgentInteractionMessage__dlm
            WHERE ssot__MessageStartTimestamp__c IS NOT NULL
            LIMIT 1
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentInteractionMessage__dlm"
        fields = ["ssot__MessageStartTimestamp__c", "ssot__MessageEndTimestamp__c"]

        if not success:
            # Check for both "field" and "column" in error message
            if "field" in error.lower() or "column" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).extend(fields)
                pytest.skip(f"Message timestamp fields not found: {error}")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).extend(fields)
        assert success, error


    def test_message_modality_field(self, execute_query):
        """
        Probe for Modality field on Message DMO.

        Modality indicates the communication channel type (text, voice, etc.).
        """
        sql = """
            SELECT ssot__Id__c, ssot__Modality__c
            FROM ssot__AiAgentInteractionMessage__dlm
            WHERE ssot__Modality__c IS NOT NULL
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentInteractionMessage__dlm"
        field = "ssot__Modality__c"

        if not success:
            # Check for both "field" and "column" in error message
            if "field" in error.lower() or "column" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                pytest.skip(f"Modality field not found: {error}")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)

        # Log discovered modality values
        if results:
            values = [r.get("ssot__Modality__c") for r in results if r.get("ssot__Modality__c")]
            if values:
                discovery.enum_values["Modality"] = list(set(values))
                print(f"\n📊 Discovered Modality values: {set(values)}")

        assert success, error


    def test_step_parent_step_field(self, execute_query):
        """
        Probe for ParentStep vs PrevStepId naming on InteractionStep.

        Internal diagrams show 'ParentStep' but existing docs have 'PrevStepId'.
        Check which naming convention is actually used.
        """
        dmo = "ssot__AIAgentInteractionStep__dlm"

        # Check for ParentStep variant
        sql_parent = """
            SELECT ssot__Id__c, ssot__ParentStepId__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__ParentStepId__c IS NOT NULL
            LIMIT 1
        """
        success_parent, _, error_parent = execute_query(sql_parent, skip_if_template_missing=False)

        # Check for PrevStep variant (already documented)
        sql_prev = """
            SELECT ssot__Id__c, ssot__PrevStepId__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__PrevStepId__c IS NOT NULL
            LIMIT 1
        """
        success_prev, _, error_prev = execute_query(sql_prev, skip_if_template_missing=False)

        if success_parent:
            discovery.found_fields.setdefault(dmo, []).append("ssot__ParentStepId__c")
            print("\n✅ Found ssot__ParentStepId__c (new field)")
        else:
            discovery.missing_fields.setdefault(dmo, []).append("ssot__ParentStepId__c")

        if success_prev:
            discovery.found_fields.setdefault(dmo, []).append("ssot__PrevStepId__c")
            print("\n✅ Confirmed ssot__PrevStepId__c (existing field)")

        # At least one should exist
        assert success_parent or success_prev, \
            f"Neither ParentStepId nor PrevStepId found. Errors: parent={error_parent}, prev={error_prev}"


    def test_interaction_telemetry_fields(self, execute_query):
        """
        Probe for telemetry-related fields on Interaction DMO.

        Check for TelemetryTraceId, TelemetryTraceSpanId on Interaction level.
        """
        dmo = "ssot__AIAgentInteraction__dlm"
        fields_to_probe = [
            "ssot__TelemetryTraceId__c",
            "ssot__TelemetryTraceSpanId__c",
        ]

        for field in fields_to_probe:
            sql = f"""
                SELECT ssot__Id__c, {field}
                FROM ssot__AIAgentInteraction__dlm
                WHERE {field} IS NOT NULL
                LIMIT 1
            """
            success, results, error = execute_query(sql, skip_if_template_missing=False)

            if success:
                discovery.found_fields.setdefault(dmo, []).append(field)
                print(f"\n✅ Found {field} on Interaction")
            else:
                discovery.missing_fields.setdefault(dmo, []).append(field)
                print(f"\n❌ Not found: {field}")


    def test_session_participant_field(self, execute_query):
        """
        Probe for Participant-related fields on Session DMO.

        Diagrams show AIAgentSessionParticipant as a related entity.
        """
        # Check for participant DMO
        sql_dmo = """
            SELECT *
            FROM ssot__AIAgentSessionParticipant__dlm
            LIMIT 1
        """
        success, results, error = execute_query(sql_dmo, skip_if_template_missing=False)

        if success:
            discovery.found_dmos.append("ssot__AIAgentSessionParticipant__dlm")
            if results:
                print(f"\n✅ Found AIAgentSessionParticipant with columns: {list(results[0].keys())}")
        else:
            discovery.missing_dmos.append("ssot__AIAgentSessionParticipant__dlm")
            pytest.skip(f"AIAgentSessionParticipant DMO not found: {error}")


# =============================================================================
# T6.D3: Enum Value Discovery
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestEnumValueProbes:
    """
    T6.D3: Discover actual enum values used in the API.

    Internal diagrams may show different enum values than what's
    actually returned by the API. These tests discover real values.
    """

    def test_step_type_enum_values(self, execute_query):
        """
        Discover all StepType enum values in use.

        Known values from existing docs: LLM_STEP, ACTION_STEP
        Diagrams may show additional values like: UserInputStep, LlmStep, etc.
        """
        sql = """
            SELECT DISTINCT ssot__AiAgentInteractionStepType__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
              AND ssot__AiAgentInteractionStepType__c IS NOT NULL
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)
        assert success, error

        if results:
            values = [r.get("ssot__AiAgentInteractionStepType__c") for r in results]
            values = [v for v in values if v]
            discovery.enum_values["AiAgentInteractionStepType"] = values
            print(f"\n📊 Discovered StepType values: {values}")


    def test_interaction_type_enum_values(self, execute_query):
        """
        Discover all InteractionType enum values in use.

        Known: TURN
        May also have: SYSTEM, INTERNAL, etc.
        """
        sql = """
            SELECT DISTINCT ssot__AiAgentInteractionType__c
            FROM ssot__AIAgentInteraction__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
              AND ssot__AiAgentInteractionType__c IS NOT NULL
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)
        assert success, error

        if results:
            values = [r.get("ssot__AiAgentInteractionType__c") for r in results]
            values = [v for v in values if v]
            discovery.enum_values["AiAgentInteractionType"] = values
            print(f"\n📊 Discovered InteractionType values: {values}")


    def test_session_end_type_enum_values(self, execute_query):
        """
        Discover all SessionEndType enum values in use.

        Known: Completed, Escalated, Abandoned, Failed
        May have additional values.
        """
        sql = """
            SELECT DISTINCT ssot__AiAgentSessionEndType__c
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
              AND ssot__AiAgentSessionEndType__c IS NOT NULL
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)
        assert success, error

        if results:
            values = [r.get("ssot__AiAgentSessionEndType__c") for r in results]
            values = [v for v in values if v]
            discovery.enum_values["AiAgentSessionEndType"] = values
            print(f"\n📊 Discovered SessionEndType values: {values}")


    def test_channel_type_enum_values(self, execute_query):
        """
        Discover all ChannelType enum values in use.

        Known: Messaging
        May also have: Voice, Chat, Email, etc.
        """
        sql = """
            SELECT DISTINCT ssot__AiAgentChannelType__c
            FROM ssot__AIAgentSession__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
              AND ssot__AiAgentChannelType__c IS NOT NULL
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)
        assert success, error

        if results:
            values = [r.get("ssot__AiAgentChannelType__c") for r in results]
            values = [v for v in values if v]
            discovery.enum_values["AiAgentChannelType"] = values
            print(f"\n📊 Discovered ChannelType values: {values}")


    def test_message_type_enum_values(self, execute_query):
        """
        Discover all MessageType enum values in use.
        """
        sql = """
            SELECT DISTINCT ssot__AiAgentInteractionMessageType__c
            FROM ssot__AiAgentInteractionMessage__dlm
            WHERE ssot__AiAgentInteractionMessageType__c IS NOT NULL
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)
        assert success, error

        if results:
            values = [r.get("ssot__AiAgentInteractionMessageType__c") for r in results]
            values = [v for v in values if v]
            discovery.enum_values["AiAgentInteractionMessageType"] = values
            print(f"\n📊 Discovered MessageType values: {values}")


# =============================================================================
# T6.D4: Relationship Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestRelationshipProbes:
    """
    T6.D4: Probe for new relationships between DMOs.

    Internal diagrams show relationships that may not be documented.
    These tests verify join paths work.
    """

    def test_moment_to_interaction_relationship(self, execute_query):
        """
        Probe the relationship between Moment and Interaction.

        Diagrams show AiAgentMomentInteraction as a junction table.
        Alternative: Moment may have direct InteractionId field.
        """
        # First try junction table
        junction_sql = """
            SELECT *
            FROM ssot__AiAgentMomentInteraction__dlm
            LIMIT 1
        """
        success_junction, results_junction, error_junction = execute_query(
            junction_sql, skip_if_template_missing=False
        )

        if success_junction:
            discovery.found_dmos.append("ssot__AiAgentMomentInteraction__dlm")
            if results_junction:
                print(f"\n✅ MomentInteraction junction exists: {list(results_junction[0].keys())}")
            return

        # Try direct join via session
        direct_sql = """
            SELECT
                m.ssot__Id__c AS moment_id,
                m.ssot__AiAgentSessionId__c AS session_id,
                i.ssot__Id__c AS interaction_id
            FROM ssot__AiAgentMoment__dlm m
            JOIN ssot__AIAgentInteraction__dlm i
                ON m.ssot__AiAgentSessionId__c = i.ssot__AiAgentSessionId__c
            WHERE m.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 5
        """
        success_direct, results_direct, error_direct = execute_query(
            direct_sql, skip_if_template_missing=False
        )

        if success_direct:
            print("\n✅ Moment→Session→Interaction join path works (no junction table)")
            return

        pytest.skip(f"No Moment-Interaction relationship found. Junction: {error_junction}, Direct: {error_direct}")


    def test_step_to_generation_relationship(self, execute_query):
        """
        Verify Step→GenAIGeneration join via GenerationId.

        This is documented but worth confirming the join works.
        """
        sql = """
            SELECT
                st.ssot__Id__c AS step_id,
                st.ssot__GenerationId__c AS generation_id,
                g.generationId__c AS gen_table_id,
                g.responseText__c
            FROM ssot__AIAgentInteractionStep__dlm st
            LEFT JOIN GenAIGeneration__dlm g
                ON st.ssot__GenerationId__c = g.generationId__c
            WHERE st.ssot__GenerationId__c IS NOT NULL
              AND st.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 3
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            if "object type" in error.lower() and "not found" in error.lower():
                pytest.skip(f"GenAIGeneration DMO not available: {error}")
            pytest.fail(f"Step→Generation join failed: {error}")

        print("\n✅ Step→Generation relationship confirmed")
        if results:
            for r in results[:2]:
                print(f"   step={r.get('step_id')}, gen={r.get('generation_id')}")


    def test_generation_to_quality_chain(self, execute_query):
        """
        Verify the GenAI quality analysis chain:
        GenAIGeneration → GenAIContentQuality → GenAIContentCategory
        """
        sql = """
            SELECT
                g.generationId__c,
                q.id__c AS quality_id,
                q.isToxicityDetected__c,
                c.detectorType__c,
                c.category__c,
                c.value__c
            FROM GenAIGeneration__dlm g
            JOIN GenAIContentQuality__dlm q
                ON g.generationId__c = q.parent__c
            LEFT JOIN GenAIContentCategory__dlm c
                ON q.id__c = c.parent__c
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            if "object type" in error.lower() and "not found" in error.lower():
                pytest.skip(f"GenAI quality DMOs not available: {error}")
            pytest.fail(f"Quality chain join failed: {error}")

        print("\n✅ GenAI quality chain confirmed: Generation→Quality→Category")

        # Log discovered detector types
        if results:
            detector_types = list(set(r.get("detectorType__c") for r in results if r.get("detectorType__c")))
            if detector_types:
                discovery.enum_values["detectorType"] = detector_types
                print(f"   Detector types: {detector_types}")


# =============================================================================
# T6.D5: Schema Introspection (If Available)
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestSchemaIntrospection:
    """
    T6.D5: Attempt schema introspection queries.

    Some Data Cloud implementations may support DESCRIBE or metadata queries.
    """

    def test_describe_session_dmo(self, execute_query):
        """
        Attempt to describe Session DMO schema.

        May not be supported - skip if fails.
        """
        sql = "DESCRIBE ssot__AIAgentSession__dlm"
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            pytest.skip(f"DESCRIBE not supported: {error}")

        print(f"\n✅ DESCRIBE supported. Session columns: {results}")


    def test_information_schema_tables(self, execute_query):
        """
        Attempt to query information_schema for available DMOs.

        May not be supported in Data Cloud.
        """
        sql = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE '%AiAgent%'
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            pytest.skip(f"information_schema not supported: {error}")

        if results:
            tables = [r.get("table_name") for r in results]
            print(f"\n✅ information_schema query worked. Tables: {tables}")
