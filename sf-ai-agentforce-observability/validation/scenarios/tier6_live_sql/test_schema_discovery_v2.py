"""
T6.D (v2): Extended Schema Discovery Tests

Based on internal diagrams (Jan 2026), probes for:
- AiAgentTagDefinitionAssociation DMO
- Additional fields on Tag/TagAssociation entities
- Hierarchical step relationships (ParentStepId)
- Knowledge retrieval step names and patterns
- SourceType and DataType enum values

Run with:
    pytest -v -s scenarios/tier6_live_sql/test_schema_discovery_v2.py
"""

import pytest
from typing import List, Dict, Any, Optional


# =============================================================================
# Discovery Result Tracking (v2)
# =============================================================================

class DiscoveryResultV2:
    """Track v2 discovery results."""

    def __init__(self):
        self.found_dmos: List[str] = []
        self.missing_dmos: List[str] = []
        self.found_fields: Dict[str, List[str]] = {}
        self.missing_fields: Dict[str, List[str]] = {}
        self.enum_values: Dict[str, List[str]] = {}
        self.step_names: List[str] = []
        self.hierarchical_steps_found: bool = False

    def report(self) -> str:
        lines = ["=" * 60, "EXTENDED SCHEMA DISCOVERY RESULTS (v2)", "=" * 60]

        if self.found_dmos:
            lines.append("\n✅ FOUND DMOs:")
            for dmo in self.found_dmos:
                lines.append(f"   - {dmo}")

        if self.missing_dmos:
            lines.append("\n❌ NOT FOUND DMOs:")
            for dmo in self.missing_dmos:
                lines.append(f"   - {dmo}")

        if self.found_fields:
            lines.append("\n✅ FOUND Fields:")
            for dmo, fields in self.found_fields.items():
                lines.append(f"   {dmo}:")
                for field in fields:
                    lines.append(f"     - {field}")

        if self.missing_fields:
            lines.append("\n❌ NOT FOUND Fields:")
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

        if self.step_names:
            lines.append("\n🔧 Discovered Step Names:")
            for name in sorted(set(self.step_names))[:30]:  # Top 30
                lines.append(f"   - {name}")

        lines.append(f"\n🔗 Hierarchical Steps Found: {self.hierarchical_steps_found}")
        lines.append("=" * 60)
        return "\n".join(lines)


discovery = DiscoveryResultV2()


@pytest.fixture(scope="module", autouse=True)
def print_discovery_report_v2(request):
    """Print discovery report after all tests complete."""
    yield
    print("\n" + discovery.report())


# =============================================================================
# T6.D2.1: TagDefinitionAssociation DMO Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestTagDefinitionAssociationProbes:
    """
    Probe for AiAgentTagDefinitionAssociation DMO.

    This entity links TagDefinitions to specific Agents or PromptTemplates.
    """

    @pytest.mark.parametrize("dmo_name", [
        "ssot__AiAgentTagDefinitionAssociation__dlm",
        "AiAgentTagDefinitionAssociation__dlm",
        "ssot__AIAgentTagDefinitionAssociation__dlm",  # Uppercase I variant
    ])
    def test_tag_definition_association_dmo(self, execute_query, dmo_name):
        """Probe if TagDefinitionAssociation DMO exists."""
        sql = f"SELECT * FROM {dmo_name} LIMIT 1"
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            discovery.missing_dmos.append(dmo_name)
            pytest.skip(f"DMO not found: {dmo_name}")

        discovery.found_dmos.append(dmo_name)
        if results:
            columns = list(results[0].keys())
            print(f"\n✅ {dmo_name} columns: {columns}")


    def test_tag_definition_association_fields(self, execute_query):
        """Probe specific fields on TagDefinitionAssociation."""
        # Try with ssot__ prefix first
        sql = """
            SELECT
                ssot__Id__c,
                ssot__AiAgentTagDefinitionId__c,
                ssot__AiAgentApiName__c,
                ssot__GenAiPromptTemplateId__c,
                ssot__CreatedDate__c
            FROM ssot__AiAgentTagDefinitionAssociation__dlm
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentTagDefinitionAssociation__dlm"
        fields = [
            "ssot__AiAgentTagDefinitionId__c",
            "ssot__AiAgentApiName__c",
            "ssot__GenAiPromptTemplateId__c",
        ]

        if not success:
            if "table" in error.lower() and "not exist" in error.lower():
                pytest.skip(f"TagDefinitionAssociation DMO not found")
            # Try to identify which fields are missing
            for field in fields:
                if field.lower() in error.lower():
                    discovery.missing_fields.setdefault(dmo, []).append(field)
            pytest.skip(f"Fields not found: {error}")

        discovery.found_fields.setdefault(dmo, []).extend(fields)
        print(f"\n✅ TagDefinitionAssociation fields verified")


# =============================================================================
# T6.D2.2: Extended Tag/TagAssociation Field Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestExtendedTagFieldProbes:
    """Probe for additional fields on Tag entities from diagrams."""

    def test_tag_value_field(self, execute_query):
        """
        Probe for Value field on AiAgentTag.

        Diagrams show: Id, AgentTagDefinitionId, Value, Description, IsActive
        """
        sql = """
            SELECT
                ssot__Id__c,
                ssot__AiAgentTagDefinitionId__c,
                ssot__Value__c,
                ssot__Description__c,
                ssot__IsActive__c
            FROM ssot__AiAgentTag__dlm
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentTag__dlm"
        field = "ssot__Value__c"

        if not success:
            if "column" in error.lower() or "field" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                pytest.skip(f"Value field not found: {error}")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)

        # Log discovered values
        if results:
            values = [r.get("ssot__Value__c") for r in results if r.get("ssot__Value__c")]
            if values:
                print(f"\n✅ Tag Value field found. Sample values: {values[:5]}")


    def test_tag_association_reason_field(self, execute_query):
        """
        Probe for AssociationReason field on TagAssociation.

        Diagrams show this field exists to explain why a tag was applied.
        """
        sql = """
            SELECT
                ssot__Id__c,
                ssot__AssociationReason__c,
                ssot__AiAgentSessionId__c,
                ssot__AiAgentMomentId__c
            FROM ssot__AiAgentTagAssociation__dlm
            WHERE ssot__AssociationReason__c IS NOT NULL
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentTagAssociation__dlm"
        field = "ssot__AssociationReason__c"

        if not success:
            if "column" in error.lower() or "field" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                pytest.skip(f"AssociationReason field not found: {error}")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)

        if results:
            reasons = [r.get("ssot__AssociationReason__c") for r in results if r.get("ssot__AssociationReason__c")]
            if reasons:
                discovery.enum_values["AssociationReason"] = list(set(reasons))
                print(f"\n✅ AssociationReason values: {set(reasons)}")


    def test_tag_association_tag_id_field(self, execute_query):
        """
        Probe for TagId field on TagAssociation.

        Diagrams show: MomentId, TagId, SessionId, AssociationReason, etc.
        """
        sql = """
            SELECT
                ssot__Id__c,
                ssot__TagId__c,
                ssot__AiAgentMomentId__c,
                ssot__AiAgentSessionId__c
            FROM ssot__AiAgentTagAssociation__dlm
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentTagAssociation__dlm"
        field = "ssot__TagId__c"

        if not success:
            if "column" in error.lower() or "field" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                pytest.skip(f"TagId field not found: {error}")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)


    def test_tag_definition_source_type_values(self, execute_query):
        """
        Discover SourceType enum values on TagDefinition.

        Diagrams show: SYSTEM_GENERATED, PREDEFINED, CUSTOM_PREDEFINED
        """
        sql = """
            SELECT DISTINCT ssot__SourceType__c
            FROM ssot__AiAgentTagDefinition__dlm
            WHERE ssot__SourceType__c IS NOT NULL
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            pytest.skip(f"Could not query SourceType: {error}")

        if results:
            values = [r.get("ssot__SourceType__c") for r in results if r.get("ssot__SourceType__c")]
            discovery.enum_values["SourceType"] = values
            print(f"\n📊 SourceType values: {values}")

        assert success


    def test_tag_definition_data_type_values(self, execute_query):
        """
        Discover DataType enum values on TagDefinition.

        Diagrams show: Text, Number, Boolean
        """
        sql = """
            SELECT DISTINCT ssot__DataType__c
            FROM ssot__AiAgentTagDefinition__dlm
            WHERE ssot__DataType__c IS NOT NULL
            LIMIT 20
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            pytest.skip(f"Could not query DataType: {error}")

        if results:
            values = [r.get("ssot__DataType__c") for r in results if r.get("ssot__DataType__c")]
            discovery.enum_values["DataType"] = values
            print(f"\n📊 DataType values: {values}")

        assert success


# =============================================================================
# T6.D2.3: Moment Field Verification
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestMomentFieldProbes:
    """Verify Moment fields match diagrams."""

    def test_moment_summary_fields(self, execute_query):
        """
        Verify RequestSummary and ResponseSummary field naming.

        Diagrams show: RequestSummary, ResponseSummary (Text type)
        Need to verify if it's __c or __Text__c suffix.
        """
        # Try RequestSummaryText__c (current assumption)
        sql_text = """
            SELECT
                ssot__Id__c,
                ssot__RequestSummaryText__c,
                ssot__ResponseSummaryText__c,
                ssot__AiAgentApiName__c
            FROM ssot__AiAgentMoment__dlm
            WHERE ssot__RequestSummaryText__c IS NOT NULL
            LIMIT 3
        """
        success_text, results_text, error_text = execute_query(sql_text, skip_if_template_missing=False)

        if success_text:
            discovery.found_fields.setdefault("ssot__AiAgentMoment__dlm", []).extend([
                "ssot__RequestSummaryText__c",
                "ssot__ResponseSummaryText__c",
            ])
            print(f"\n✅ Moment uses *SummaryText__c naming")
            if results_text:
                sample = results_text[0]
                print(f"   Sample: {sample.get('ssot__RequestSummaryText__c', '')[:80]}...")
            return

        # Try RequestSummary__c (alternate)
        sql_plain = """
            SELECT
                ssot__Id__c,
                ssot__RequestSummary__c,
                ssot__ResponseSummary__c
            FROM ssot__AiAgentMoment__dlm
            WHERE ssot__RequestSummary__c IS NOT NULL
            LIMIT 3
        """
        success_plain, results_plain, error_plain = execute_query(sql_plain, skip_if_template_missing=False)

        if success_plain:
            discovery.found_fields.setdefault("ssot__AiAgentMoment__dlm", []).extend([
                "ssot__RequestSummary__c",
                "ssot__ResponseSummary__c",
            ])
            print(f"\n✅ Moment uses *Summary__c naming (no Text suffix)")
            return

        pytest.skip(f"Could not determine summary field naming. Text: {error_text}, Plain: {error_plain}")


    def test_moment_agent_version_field(self, execute_query):
        """Verify AiAgentVersionApiName field on Moment."""
        sql = """
            SELECT
                ssot__Id__c,
                ssot__AiAgentApiName__c,
                ssot__AiAgentVersionApiName__c
            FROM ssot__AiAgentMoment__dlm
            WHERE ssot__AiAgentVersionApiName__c IS NOT NULL
            LIMIT 3
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentMoment__dlm"
        field = "ssot__AiAgentVersionApiName__c"

        if not success:
            if "column" in error.lower() or "field" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                pytest.skip(f"AiAgentVersionApiName not found: {error}")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)

        if results:
            versions = list(set(r.get("ssot__AiAgentVersionApiName__c") for r in results if r.get("ssot__AiAgentVersionApiName__c")))
            print(f"\n✅ AgentVersionApiName values: {versions}")


# =============================================================================
# T6.D2.4: Hierarchical Step Relationship Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestHierarchicalStepProbes:
    """
    Probe for hierarchical step relationships.

    Diagrams show steps can have parent-child nesting (not just linear PrevStepId).
    Example: FunctionExecutionStep → ExecutePromptTemplate → ExecuteRetriever → PerformSemanticQuery
    """

    def test_parent_step_id_field(self, execute_query):
        """
        Probe for ParentStepId field vs PrevStepId.

        If hierarchical steps exist, there should be a ParentStepId field.
        """
        sql = """
            SELECT
                ssot__Id__c,
                ssot__PrevStepId__c,
                ssot__ParentStepId__c,
                ssot__Name__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__ParentStepId__c IS NOT NULL
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AIAgentInteractionStep__dlm"
        field = "ssot__ParentStepId__c"

        if not success:
            if "column" in error.lower() or "field" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                print(f"\n❌ ParentStepId field not found - steps may only use PrevStepId")
                pytest.skip(f"ParentStepId not found")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)
        discovery.hierarchical_steps_found = True

        if results:
            print(f"\n✅ Hierarchical steps confirmed (ParentStepId field exists)")
            for r in results[:3]:
                print(f"   Step: {r.get('ssot__Name__c')}, Parent: {r.get('ssot__ParentStepId__c')}")


    def test_step_nesting_depth(self, execute_query):
        """
        Attempt to find deeply nested steps by looking at step chains.
        """
        sql = """
            SELECT
                s1.ssot__Id__c as child_id,
                s1.ssot__Name__c as child_name,
                s1.ssot__PrevStepId__c as prev_id,
                s2.ssot__Name__c as prev_name,
                s2.ssot__PrevStepId__c as grandprev_id
            FROM ssot__AIAgentInteractionStep__dlm s1
            LEFT JOIN ssot__AIAgentInteractionStep__dlm s2
                ON s1.ssot__PrevStepId__c = s2.ssot__Id__c
            WHERE s1.ssot__PrevStepId__c IS NOT NULL
              AND s2.ssot__PrevStepId__c IS NOT NULL
              AND s1.ssot__StartTimestamp__c >= current_date - INTERVAL '7' DAY
            LIMIT 10
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            pytest.skip(f"Could not query step nesting: {error}")

        if results:
            print(f"\n📊 Step chain examples (Child → Prev → GrandPrev):")
            for r in results[:5]:
                child = r.get("child_name", "?")
                prev = r.get("prev_name", "?")
                print(f"   {child} → {prev}")


    def test_knowledge_retrieval_step_names(self, execute_query):
        """
        Discover step names related to knowledge retrieval.

        Diagrams show: GetRetrieverId, ExecutePromptTemplate, ExecuteRetriever, PerformSemanticQuery
        """
        sql = """
            SELECT DISTINCT ssot__Name__c
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
              AND (
                ssot__Name__c LIKE '%Retriev%'
                OR ssot__Name__c LIKE '%Semantic%'
                OR ssot__Name__c LIKE '%Knowledge%'
                OR ssot__Name__c LIKE '%PromptTemplate%'
                OR ssot__Name__c LIKE '%Execute%'
              )
            LIMIT 30
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            pytest.skip(f"Could not query step names: {error}")

        if results:
            names = [r.get("ssot__Name__c") for r in results if r.get("ssot__Name__c")]
            discovery.step_names.extend(names)
            print(f"\n🔧 Knowledge-related step names found: {names}")


    def test_all_unique_step_names(self, execute_query):
        """
        Discover all unique step names in the org.

        This helps identify step patterns for documentation.
        """
        sql = """
            SELECT
                ssot__Name__c,
                ssot__AiAgentInteractionStepType__c,
                COUNT(*) as occurrence_count
            FROM ssot__AIAgentInteractionStep__dlm
            WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
              AND ssot__Name__c IS NOT NULL
            GROUP BY ssot__Name__c, ssot__AiAgentInteractionStepType__c
            ORDER BY occurrence_count DESC
            LIMIT 50
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            pytest.skip(f"Could not query step names: {error}")

        if results:
            print(f"\n📊 Top Step Names by Frequency:")
            for r in results[:20]:
                name = r.get("ssot__Name__c", "?")
                step_type = r.get("ssot__AiAgentInteractionStepType__c", "?")
                count = r.get("occurrence_count", 0)
                discovery.step_names.append(name)
                print(f"   [{step_type}] {name}: {count} occurrences")


# =============================================================================
# T6.D2.5: MomentInteraction Type Field Probe
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestMomentInteractionProbes:
    """Probe additional fields on MomentInteraction junction."""

    def test_moment_interaction_type_field(self, execute_query):
        """
        Diagrams show AiAgentMomentId has a "Type" indicator.

        Check if there's a Type field on the junction table.
        """
        sql = """
            SELECT
                ssot__Id__c,
                ssot__AiAgentMomentId__c,
                ssot__AiAgentInteractionId__c,
                ssot__Type__c
            FROM ssot__AiAgentMomentInteraction__dlm
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentMomentInteraction__dlm"
        field = "ssot__Type__c"

        if not success:
            if "column" in error.lower() or "field" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                pytest.skip(f"Type field not found on MomentInteraction")
            if "table" in error.lower() and "not exist" in error.lower():
                pytest.skip(f"MomentInteraction DMO not found")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)

        if results:
            types = [r.get("ssot__Type__c") for r in results if r.get("ssot__Type__c")]
            if types:
                discovery.enum_values["MomentInteractionType"] = list(set(types))
                print(f"\n📊 MomentInteraction Type values: {set(types)}")


# =============================================================================
# T6.D2.6: GenAI PromptTemplate Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestGenAiPromptTemplateProbes:
    """Probe for GenAiPromptTemplate DMO referenced in diagrams."""

    @pytest.mark.parametrize("dmo_name", [
        "ssot__GenAiPromptTemplate__dlm",
        "GenAiPromptTemplate__dlm",
        "ssot__GenAIPromptTemplate__dlm",  # Uppercase variant
        "GenAIPromptTemplate__dlm",
    ])
    def test_prompt_template_dmo(self, execute_query, dmo_name):
        """Probe if GenAiPromptTemplate DMO exists."""
        sql = f"SELECT * FROM {dmo_name} LIMIT 1"
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            discovery.missing_dmos.append(dmo_name)
            pytest.skip(f"DMO not found: {dmo_name}")

        discovery.found_dmos.append(dmo_name)
        if results:
            columns = list(results[0].keys())
            print(f"\n✅ {dmo_name} columns: {columns}")


# =============================================================================
# T6.D2.7: BotDefinition Reference Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestBotDefinitionProbes:
    """Probe for BotDefinition references shown in Setup BPO diagrams."""

    def test_bot_definition_id_on_tag_def_assoc(self, execute_query):
        """
        Diagrams show BotDefinitionId on TagDefinitionAssociation (Setup BPO).

        Check if this field exists.
        """
        sql = """
            SELECT
                ssot__Id__c,
                ssot__BotDefinitionId__c,
                ssot__AiAgentApiName__c
            FROM ssot__AiAgentTagDefinitionAssociation__dlm
            LIMIT 5
        """
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        dmo = "ssot__AiAgentTagDefinitionAssociation__dlm"
        field = "ssot__BotDefinitionId__c"

        if not success:
            if "table" in error.lower() and "not exist" in error.lower():
                pytest.skip(f"TagDefinitionAssociation DMO not found")
            if "column" in error.lower() or "field" in error.lower():
                discovery.missing_fields.setdefault(dmo, []).append(field)
                pytest.skip(f"BotDefinitionId field not found")
            pytest.fail(f"Unexpected error: {error}")

        discovery.found_fields.setdefault(dmo, []).append(field)


# =============================================================================
# T6.D2.8: AITagDefinition/AITagValue Setup BPO Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestSetupBpoEntityProbes:
    """
    Probe for Setup BPO entities shown in diagrams.

    These may be separate from the Engagement entities (AIAgent* prefix).
    """

    @pytest.mark.parametrize("dmo_name", [
        "ssot__AITagDefinition__dlm",
        "AITagDefinition__dlm",
        "ssot__AiTagDefinition__dlm",
    ])
    def test_ai_tag_definition_dmo(self, execute_query, dmo_name):
        """Probe for AITagDefinition (Setup BPO) DMO."""
        sql = f"SELECT * FROM {dmo_name} LIMIT 1"
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            discovery.missing_dmos.append(dmo_name)
            pytest.skip(f"DMO not found: {dmo_name}")

        discovery.found_dmos.append(dmo_name)
        if results:
            columns = list(results[0].keys())
            print(f"\n✅ {dmo_name} columns: {columns}")


    @pytest.mark.parametrize("dmo_name", [
        "ssot__AITagValue__dlm",
        "AITagValue__dlm",
        "ssot__AiTagValue__dlm",
    ])
    def test_ai_tag_value_dmo(self, execute_query, dmo_name):
        """Probe for AITagValue (Setup BPO) DMO."""
        sql = f"SELECT * FROM {dmo_name} LIMIT 1"
        success, results, error = execute_query(sql, skip_if_template_missing=False)

        if not success:
            discovery.missing_dmos.append(dmo_name)
            pytest.skip(f"DMO not found: {dmo_name}")

        discovery.found_dmos.append(dmo_name)
        if results:
            columns = list(results[0].keys())
            print(f"\n✅ {dmo_name} columns: {columns}")
