"""
T6.D (v3): Comprehensive DMO/DLO Discovery Tests

Systematically discovers ALL available DMOs and their fields using:
1. Metadata API endpoint (/ssot/querybuilder/metadata)
2. SQL SELECT * probes for field discovery
3. DISTINCT queries for enum value discovery

DMO Categories from internal documentation:
- Audit & Feedback DLO/DMOs (13)
- Session Trace DMOs (5)
- RAG Quality Monitoring (3)
- Agent Optimizer DLOs (6)

Run with:
    pytest -v -s scenarios/tier6_live_sql/test_comprehensive_dmo_discovery.py

For full output saved to file:
    pytest -v -s scenarios/tier6_live_sql/test_comprehensive_dmo_discovery.py 2>&1 | tee dmo-discovery-full.txt
"""

import pytest
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# DMO Registry - All Known DMOs to Probe
# =============================================================================

# Audit & Feedback DLO/DMOs (13)
AUDIT_FEEDBACK_DMOS = [
    "GenAIAppGeneration__dlm",
    "GenAIContentCategory__dlm",
    "GenAIContentQuality__dlm",
    "GenAIFeedback__dlm",
    "GenAIFeedbackDetail__dlm",
    "GenAIGatewayRequest__dlm",
    "GenAIGatewayRequestTag__dlm",
    "GenAIGatewayResponse__dlm",
    "GenAIGeneration__dlm",
    "GenAIGtwyObjRecCitationRef__dlm",
    "GenAIGtwyObjRecord__dlm",
    "GenAIGtwyRequestLLM__dlm",
    "GenAIGtwyRequestMetadata__dlm",
]

# Session Trace DMOs (5) - with ssot__ prefix
SESSION_TRACE_DMOS = [
    "ssot__AIAgentInteraction__dlm",
    "ssot__AiAgentInteractionMessage__dlm",
    "ssot__AIAgentInteractionStep__dlm",
    "ssot__AIAgentSession__dlm",
    "ssot__AIAgentSessionParticipant__dlm",
]

# RAG Quality Monitoring (3)
RAG_QUALITY_DMOS = [
    "GenAIRetrieverResponse__dlm",
    "GenAIRetrieverRequest__dlm",
    "GenAIRetrieverQualityMetric__dlm",
]

# Agent Optimizer DLOs (6) - with ssot__ prefix
AGENT_OPTIMIZER_DMOS = [
    "ssot__AiAgentMoment__dlm",
    "ssot__AiAgentTagDefinition__dlm",
    "ssot__AiAgentTagAssociation__dlm",
    "ssot__AiAgentMomentInteraction__dlm",
    "ssot__AiAgentTag__dlm",
    "ssot__AiAgentTagDefinitionAssociation__dlm",
]

# All DMOs combined
ALL_DMOS = AUDIT_FEEDBACK_DMOS + SESSION_TRACE_DMOS + RAG_QUALITY_DMOS + AGENT_OPTIMIZER_DMOS


# =============================================================================
# Discovery Result Tracking
# =============================================================================

@dataclass
class DmoDiscoveryResult:
    """Result of probing a single DMO."""
    dmo_name: str
    exists: bool = False
    fields: List[str] = field(default_factory=list)
    field_types: Dict[str, str] = field(default_factory=dict)
    sample_row: Dict[str, Any] = field(default_factory=dict)
    record_count: Optional[int] = None
    error: Optional[str] = None
    enum_values: Dict[str, List[str]] = field(default_factory=dict)


class ComprehensiveDiscoveryTracker:
    """Track all discovery results."""

    def __init__(self):
        self.results: Dict[str, DmoDiscoveryResult] = {}
        self.metadata_api_available: bool = False
        self.all_dmos_from_api: List[str] = []

    def add_result(self, result: DmoDiscoveryResult):
        self.results[result.dmo_name] = result

    def generate_report(self) -> str:
        lines = [
            "=" * 80,
            "COMPREHENSIVE DMO/DLO DISCOVERY REPORT",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 80,
        ]

        # Summary
        found = [r for r in self.results.values() if r.exists]
        not_found = [r for r in self.results.values() if not r.exists]

        lines.append(f"\n📊 SUMMARY: {len(found)} found, {len(not_found)} not found")
        lines.append(f"   Metadata API available: {self.metadata_api_available}")
        if self.all_dmos_from_api:
            lines.append(f"   DMOs from API: {len(self.all_dmos_from_api)}")

        # Found DMOs with details
        if found:
            lines.append("\n" + "=" * 80)
            lines.append("✅ FOUND DMOs (Add to documentation)")
            lines.append("=" * 80)

            for result in sorted(found, key=lambda x: x.dmo_name):
                lines.append(f"\n📦 {result.dmo_name}")
                lines.append(f"   Fields: {len(result.fields)}")
                if result.record_count is not None:
                    lines.append(f"   Records (last 30 days): {result.record_count}")

                # List fields
                if result.fields:
                    lines.append("   Field List:")
                    for f in sorted(result.fields)[:30]:  # First 30 fields
                        ftype = result.field_types.get(f, "?")
                        lines.append(f"      - {f} ({ftype})")
                    if len(result.fields) > 30:
                        lines.append(f"      ... and {len(result.fields) - 30} more")

                # Enum values
                if result.enum_values:
                    lines.append("   Enum Values:")
                    for field_name, values in result.enum_values.items():
                        lines.append(f"      {field_name}: {values[:10]}")
                        if len(values) > 10:
                            lines.append(f"         ... and {len(values) - 10} more")

        # Not found DMOs
        if not_found:
            lines.append("\n" + "=" * 80)
            lines.append("❌ NOT FOUND DMOs (Skip in documentation)")
            lines.append("=" * 80)
            for result in sorted(not_found, key=lambda x: x.dmo_name):
                error_snippet = result.error[:80] if result.error else "No error"
                lines.append(f"   - {result.dmo_name}: {error_snippet}")

        # DMOs from API not in our list
        if self.all_dmos_from_api:
            known_names = {r.dmo_name for r in self.results.values()}
            unknown = [d for d in self.all_dmos_from_api if d not in known_names]
            if unknown:
                lines.append("\n" + "=" * 80)
                lines.append("🆕 ADDITIONAL DMOs FROM API (Not in our probe list)")
                lines.append("=" * 80)
                for dmo in sorted(unknown)[:50]:
                    lines.append(f"   - {dmo}")
                if len(unknown) > 50:
                    lines.append(f"   ... and {len(unknown) - 50} more")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


# Module-level tracker
tracker = ComprehensiveDiscoveryTracker()


@pytest.fixture(scope="module", autouse=True)
def print_comprehensive_report(request):
    """Print comprehensive report after all tests."""
    yield
    print("\n" + tracker.generate_report())


# =============================================================================
# T6.D3.1: Metadata API Discovery
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestMetadataApiDiscovery:
    """Test the metadata API endpoints for DMO discovery."""

    def test_list_all_dmos_via_api(self, data_client):
        """
        Use the metadata API to list all available DMOs.

        Endpoint: /ssot/querybuilder/metadata
        """
        try:
            dmos = data_client.list_dmos()
            tracker.metadata_api_available = True

            if dmos:
                # Extract DMO names
                dmo_names = []
                for dmo in dmos:
                    name = dmo.get("name") or dmo.get("apiName") or dmo.get("developerName")
                    if name:
                        dmo_names.append(name)

                tracker.all_dmos_from_api = dmo_names
                print(f"\n✅ Metadata API returned {len(dmo_names)} DMOs")
                print(f"   Sample: {dmo_names[:10]}")

                # Look for AI/GenAI related DMOs
                ai_dmos = [d for d in dmo_names if "AI" in d.upper() or "GENAI" in d.upper()]
                print(f"\n   AI-related DMOs: {len(ai_dmos)}")
                for d in sorted(ai_dmos)[:20]:
                    print(f"      - {d}")

            assert len(dmos) > 0, "No DMOs returned from metadata API"

        except Exception as e:
            tracker.metadata_api_available = False
            pytest.skip(f"Metadata API not available: {e}")


    @pytest.mark.parametrize("dmo_name", SESSION_TRACE_DMOS[:2])  # Sample 2
    def test_get_dmo_metadata(self, data_client, dmo_name):
        """
        Get detailed metadata for a specific DMO.

        Endpoint: /ssot/querybuilder/metadata/{dmo_name}
        """
        try:
            metadata = data_client.get_dmo_metadata(dmo_name)

            if metadata:
                print(f"\n✅ Metadata for {dmo_name}:")
                print(f"   Keys: {list(metadata.keys())[:10]}")

                # Try to extract field information
                fields = metadata.get("fields") or metadata.get("columns") or []
                if fields:
                    print(f"   Fields from metadata: {len(fields)}")
                    for f in fields[:5]:
                        print(f"      - {f}")

        except Exception as e:
            pytest.skip(f"Could not get metadata for {dmo_name}: {e}")


# =============================================================================
# T6.D3.2: Audit & Feedback DMO Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestAuditFeedbackDmos:
    """Probe all Audit & Feedback DLO/DMOs."""

    @pytest.mark.parametrize("dmo_name", AUDIT_FEEDBACK_DMOS)
    def test_audit_feedback_dmo_exists(self, data_client, dmo_name):
        """Probe Audit & Feedback DMO existence and fields."""
        result = DmoDiscoveryResult(dmo_name=dmo_name)

        try:
            # Try SELECT * to get all fields
            sql = f"SELECT * FROM {dmo_name} LIMIT 1"
            rows = list(data_client.query(sql, limit=1))

            result.exists = True

            if rows:
                result.sample_row = rows[0]
                result.fields = list(rows[0].keys())
                # Infer types from values
                for k, v in rows[0].items():
                    if v is None:
                        result.field_types[k] = "null"
                    elif isinstance(v, bool):
                        result.field_types[k] = "boolean"
                    elif isinstance(v, int):
                        result.field_types[k] = "integer"
                    elif isinstance(v, float):
                        result.field_types[k] = "number"
                    elif isinstance(v, dict):
                        result.field_types[k] = "object"
                    elif isinstance(v, list):
                        result.field_types[k] = "array"
                    else:
                        result.field_types[k] = "string"

            print(f"\n✅ {dmo_name}: {len(result.fields)} fields")

        except Exception as e:
            result.exists = False
            result.error = str(e)
            print(f"\n❌ {dmo_name}: {str(e)[:80]}")

        tracker.add_result(result)

        if not result.exists:
            pytest.skip(f"DMO not found: {dmo_name}")


# =============================================================================
# T6.D3.3: Session Trace DMO Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestSessionTraceDmos:
    """Probe all Session Trace DMOs with full field discovery."""

    @pytest.mark.parametrize("dmo_name", SESSION_TRACE_DMOS)
    def test_session_trace_dmo_full_discovery(self, data_client, dmo_name):
        """
        Full discovery of Session Trace DMOs including:
        - All fields
        - Enum values for type fields
        - Record counts
        """
        result = DmoDiscoveryResult(dmo_name=dmo_name)

        try:
            # Get all fields via SELECT *
            sql = f"SELECT * FROM {dmo_name} LIMIT 3"
            rows = list(data_client.query(sql, limit=3))

            result.exists = True

            if rows:
                # Collect all unique fields across rows
                all_fields = set()
                for row in rows:
                    all_fields.update(row.keys())
                result.fields = sorted(all_fields)

                # Type inference from first row
                for k, v in rows[0].items():
                    if v is None:
                        result.field_types[k] = "null"
                    elif isinstance(v, bool):
                        result.field_types[k] = "boolean"
                    elif isinstance(v, (int, float)):
                        result.field_types[k] = "number"
                    else:
                        result.field_types[k] = "string"

                result.sample_row = rows[0]

            # Get record count (last 30 days)
            try:
                count_sql = f"""
                    SELECT COUNT(*) as cnt FROM {dmo_name}
                    WHERE ssot__StartTimestamp__c >= current_date - INTERVAL '30' DAY
                """
                count_result = list(data_client.query(count_sql, limit=1))
                if count_result:
                    result.record_count = count_result[0].get("cnt")
            except:
                pass  # Count may fail if no timestamp field

            # Discover enum values for type/status fields
            type_fields = [f for f in result.fields if "Type" in f or "Status" in f or "Role" in f]
            for type_field in type_fields[:5]:  # Limit to 5 enum fields
                try:
                    enum_sql = f"""
                        SELECT DISTINCT {type_field}
                        FROM {dmo_name}
                        WHERE {type_field} IS NOT NULL
                        LIMIT 20
                    """
                    enum_rows = list(data_client.query(enum_sql, limit=20))
                    if enum_rows:
                        values = [r.get(type_field) for r in enum_rows if r.get(type_field)]
                        if values:
                            result.enum_values[type_field] = values
                except:
                    pass

            print(f"\n✅ {dmo_name}:")
            print(f"   Fields: {len(result.fields)}")
            if result.record_count:
                print(f"   Records (30d): {result.record_count}")
            if result.enum_values:
                print(f"   Enum fields: {list(result.enum_values.keys())}")

        except Exception as e:
            result.exists = False
            result.error = str(e)
            print(f"\n❌ {dmo_name}: {str(e)[:80]}")

        tracker.add_result(result)

        if not result.exists:
            pytest.skip(f"DMO not found: {dmo_name}")


# =============================================================================
# T6.D3.4: RAG Quality Monitoring DMO Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestRagQualityDmos:
    """Probe RAG Quality Monitoring DMOs."""

    @pytest.mark.parametrize("dmo_name", RAG_QUALITY_DMOS)
    def test_rag_quality_dmo_exists(self, data_client, dmo_name):
        """Probe RAG Quality Monitoring DMO."""
        result = DmoDiscoveryResult(dmo_name=dmo_name)

        try:
            sql = f"SELECT * FROM {dmo_name} LIMIT 1"
            rows = list(data_client.query(sql, limit=1))

            result.exists = True
            if rows:
                result.fields = list(rows[0].keys())
                result.sample_row = rows[0]

            print(f"\n✅ {dmo_name}: {len(result.fields)} fields")

        except Exception as e:
            result.exists = False
            result.error = str(e)
            print(f"\n❌ {dmo_name}: {str(e)[:80]}")

        tracker.add_result(result)

        if not result.exists:
            pytest.skip(f"DMO not found: {dmo_name}")


# =============================================================================
# T6.D3.5: Agent Optimizer DMO Probes
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestAgentOptimizerDmos:
    """Probe all Agent Optimizer DLOs."""

    @pytest.mark.parametrize("dmo_name", AGENT_OPTIMIZER_DMOS)
    def test_agent_optimizer_dmo_full_discovery(self, data_client, dmo_name):
        """Full discovery of Agent Optimizer DMOs."""
        result = DmoDiscoveryResult(dmo_name=dmo_name)

        try:
            sql = f"SELECT * FROM {dmo_name} LIMIT 3"
            rows = list(data_client.query(sql, limit=3))

            result.exists = True

            if rows:
                all_fields = set()
                for row in rows:
                    all_fields.update(row.keys())
                result.fields = sorted(all_fields)
                result.sample_row = rows[0]

                # Type inference
                for k, v in rows[0].items():
                    result.field_types[k] = type(v).__name__ if v is not None else "null"

            # Discover enum values
            type_fields = [f for f in result.fields if "Type" in f or "Source" in f]
            for type_field in type_fields[:3]:
                try:
                    enum_sql = f"""
                        SELECT DISTINCT {type_field}
                        FROM {dmo_name}
                        WHERE {type_field} IS NOT NULL
                        LIMIT 20
                    """
                    enum_rows = list(data_client.query(enum_sql, limit=20))
                    if enum_rows:
                        values = [r.get(type_field) for r in enum_rows if r.get(type_field)]
                        if values:
                            result.enum_values[type_field] = values
                except:
                    pass

            print(f"\n✅ {dmo_name}: {len(result.fields)} fields")
            if result.enum_values:
                print(f"   Enums: {result.enum_values}")

        except Exception as e:
            result.exists = False
            result.error = str(e)
            print(f"\n❌ {dmo_name}: {str(e)[:80]}")

        tracker.add_result(result)

        if not result.exists:
            pytest.skip(f"DMO not found: {dmo_name}")


# =============================================================================
# T6.D3.6: GenAI Quality Chain Deep Dive
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestGenAiQualityChain:
    """Deep dive into GenAI quality analysis chain."""

    def test_genai_generation_fields(self, data_client):
        """Discover all fields on GenAIGeneration."""
        sql = "SELECT * FROM GenAIGeneration__dlm LIMIT 5"
        try:
            rows = list(data_client.query(sql, limit=5))
            if rows:
                fields = sorted(rows[0].keys())
                print(f"\n📊 GenAIGeneration fields ({len(fields)}):")
                for f in fields:
                    print(f"   - {f}")
        except Exception as e:
            pytest.skip(f"GenAIGeneration not available: {e}")


    def test_genai_content_quality_fields(self, data_client):
        """Discover all fields on GenAIContentQuality."""
        sql = "SELECT * FROM GenAIContentQuality__dlm LIMIT 5"
        try:
            rows = list(data_client.query(sql, limit=5))
            if rows:
                fields = sorted(rows[0].keys())
                print(f"\n📊 GenAIContentQuality fields ({len(fields)}):")
                for f in fields:
                    print(f"   - {f}")
        except Exception as e:
            pytest.skip(f"GenAIContentQuality not available: {e}")


    def test_genai_content_category_detector_types(self, data_client):
        """Discover all detector types in GenAIContentCategory."""
        sql = """
            SELECT DISTINCT detectorType__c, category__c
            FROM GenAIContentCategory__dlm
            WHERE detectorType__c IS NOT NULL
            LIMIT 50
        """
        try:
            rows = list(data_client.query(sql, limit=50))
            if rows:
                detector_types = {}
                for row in rows:
                    dt = row.get("detectorType__c")
                    cat = row.get("category__c")
                    if dt:
                        if dt not in detector_types:
                            detector_types[dt] = set()
                        if cat:
                            detector_types[dt].add(cat)

                print(f"\n📊 GenAI Detector Types and Categories:")
                for dt, cats in sorted(detector_types.items()):
                    print(f"   {dt}:")
                    for c in sorted(cats):
                        print(f"      - {c}")
        except Exception as e:
            pytest.skip(f"GenAIContentCategory not available: {e}")


# =============================================================================
# T6.D3.7: Exhaustive Enum Discovery
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestExhaustiveEnumDiscovery:
    """Discover ALL enum values across key entities."""

    @pytest.mark.parametrize("dmo,field", [
        ("ssot__AIAgentSession__dlm", "ssot__AiAgentSessionEndType__c"),
        ("ssot__AIAgentSession__dlm", "ssot__AiAgentChannelType__c"),
        ("ssot__AIAgentInteraction__dlm", "ssot__AiAgentInteractionType__c"),
        ("ssot__AIAgentInteractionStep__dlm", "ssot__AiAgentInteractionStepType__c"),
        ("ssot__AiAgentInteractionMessage__dlm", "ssot__AiAgentInteractionMessageType__c"),
        ("ssot__AIAgentSessionParticipant__dlm", "ssot__AiAgentType__c"),
        ("ssot__AIAgentSessionParticipant__dlm", "ssot__AiAgentSessionParticipantRole__c"),
        ("ssot__AiAgentTagDefinition__dlm", "ssot__SourceType__c"),
        ("ssot__AiAgentTagDefinition__dlm", "ssot__DataType__c"),
        ("GenAIContentCategory__dlm", "detectorType__c"),
    ])
    def test_enum_values(self, data_client, dmo, field):
        """Discover all values for an enum field."""
        sql = f"""
            SELECT DISTINCT {field} as value, COUNT(*) as cnt
            FROM {dmo}
            WHERE {field} IS NOT NULL
            GROUP BY {field}
            ORDER BY cnt DESC
            LIMIT 30
        """
        try:
            rows = list(data_client.query(sql, limit=30))
            if rows:
                print(f"\n📊 {dmo}.{field}:")
                for row in rows:
                    value = row.get("value")
                    cnt = row.get("cnt", "?")
                    print(f"   - {value}: {cnt} occurrences")
        except Exception as e:
            pytest.skip(f"Could not query {dmo}.{field}: {e}")


# =============================================================================
# T6.D3.8: GenAI Gateway Deep Dive
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestGenAiGatewayDmos:
    """Deep dive into GenAI Gateway DMOs."""

    @pytest.mark.parametrize("dmo_name", [
        "GenAIGatewayRequest__dlm",
        "GenAIGatewayResponse__dlm",
        "GenAIGatewayRequestTag__dlm",
        "GenAIGtwyRequestLLM__dlm",
        "GenAIGtwyRequestMetadata__dlm",
        "GenAIGtwyObjRecord__dlm",
        "GenAIGtwyObjRecCitationRef__dlm",
    ])
    def test_gateway_dmo_discovery(self, data_client, dmo_name):
        """Discover Gateway DMO fields."""
        try:
            sql = f"SELECT * FROM {dmo_name} LIMIT 3"
            rows = list(data_client.query(sql, limit=3))

            if rows:
                fields = sorted(rows[0].keys())
                print(f"\n📊 {dmo_name} ({len(fields)} fields):")
                for f in fields[:15]:
                    print(f"   - {f}")
                if len(fields) > 15:
                    print(f"   ... and {len(fields) - 15} more")
        except Exception as e:
            pytest.skip(f"{dmo_name} not available: {e}")


# =============================================================================
# T6.D3.9: Feedback DMO Deep Dive
# =============================================================================

@pytest.mark.tier6
@pytest.mark.live_api
@pytest.mark.slow
class TestFeedbackDmos:
    """Deep dive into GenAI Feedback DMOs."""

    def test_genai_feedback_fields(self, data_client):
        """Discover GenAIFeedback fields."""
        sql = "SELECT * FROM GenAIFeedback__dlm LIMIT 5"
        try:
            rows = list(data_client.query(sql, limit=5))
            if rows:
                fields = sorted(rows[0].keys())
                print(f"\n📊 GenAIFeedback ({len(fields)} fields):")
                for f in fields:
                    print(f"   - {f}")
        except Exception as e:
            pytest.skip(f"GenAIFeedback not available: {e}")


    def test_genai_feedback_detail_fields(self, data_client):
        """Discover GenAIFeedbackDetail fields."""
        sql = "SELECT * FROM GenAIFeedbackDetail__dlm LIMIT 5"
        try:
            rows = list(data_client.query(sql, limit=5))
            if rows:
                fields = sorted(rows[0].keys())
                print(f"\n📊 GenAIFeedbackDetail ({len(fields)} fields):")
                for f in fields:
                    print(f"   - {f}")
        except Exception as e:
            pytest.skip(f"GenAIFeedbackDetail not available: {e}")


    def test_feedback_types(self, data_client):
        """Discover feedback type values."""
        sql = """
            SELECT DISTINCT feedback__c, COUNT(*) as cnt
            FROM GenAIFeedback__dlm
            WHERE feedback__c IS NOT NULL
            GROUP BY feedback__c
            ORDER BY cnt DESC
            LIMIT 20
        """
        try:
            rows = list(data_client.query(sql, limit=20))
            if rows:
                print(f"\n📊 Feedback values:")
                for row in rows:
                    print(f"   - {row.get('feedback__c')}: {row.get('cnt')}")
        except Exception as e:
            pytest.skip(f"Could not query feedback types: {e}")
