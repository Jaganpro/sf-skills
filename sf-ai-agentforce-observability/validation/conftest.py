"""
Shared pytest fixtures for sf-ai-agentforce-observability validation.

Provides:
- Auth client fixtures (live and mocked)
- Test data directory fixtures
- Sample Parquet data fixtures
- Pytest markers for test categorization

Usage:
    @pytest.mark.live_api
    def test_requires_salesforce(auth_client):
        # Uses real Salesforce connection
        pass

    @pytest.mark.offline
    def test_with_fixtures(sample_data_dir):
        # Uses local fixture data
        pass
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, Optional
from unittest.mock import MagicMock, patch

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

# Add skill scripts to path
SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from scripts.models import (
    SCHEMAS,
    DMO_NAMES,
    SESSION_SCHEMA,
    INTERACTION_SCHEMA,
    STEP_SCHEMA,
    MESSAGE_SCHEMA,
)


# =============================================================================
# Pytest Markers
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "live_api: mark test as requiring live Salesforce API"
    )
    config.addinivalue_line(
        "markers", "offline: mark test as using only local fixtures"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow-running"
    )
    config.addinivalue_line(
        "markers", "tier1: Tier 1 - Auth & Connectivity tests"
    )
    config.addinivalue_line(
        "markers", "tier2: Tier 2 - Extraction Command tests"
    )
    config.addinivalue_line(
        "markers", "tier3: Tier 3 - Analysis Command tests"
    )
    config.addinivalue_line(
        "markers", "tier4: Tier 4 - Schema/Data Model tests"
    )
    config.addinivalue_line(
        "markers", "tier5: Tier 5 - Negative/Error Case tests"
    )
    config.addinivalue_line(
        "markers", "tier6: Tier 6 - Live SQL Execution tests (bonus)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip live_api tests when --offline flag is passed."""
    if config.getoption("--offline", default=False):
        skip_live = pytest.mark.skip(reason="Skipping live API tests (--offline)")
        for item in items:
            if "live_api" in item.keywords:
                item.add_marker(skip_live)


def pytest_addoption(parser):
    """Add custom CLI options."""
    parser.addoption(
        "--offline",
        action="store_true",
        default=False,
        help="Run only offline tests (skip live API tests)"
    )
    parser.addoption(
        "--org",
        action="store",
        default="Vivint-DevInt",
        help="Salesforce org alias for live tests"
    )
    parser.addoption(
        "--tier",
        action="store",
        default=None,
        help="Run only specific tier (T1, T2, T3, T4, T5, T6)"
    )


# =============================================================================
# Auth Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def org_alias(request) -> str:
    """Get org alias from CLI or default."""
    return request.config.getoption("--org")


@pytest.fixture(scope="session")
def auth_client(org_alias: str):
    """
    Create authenticated Data360Auth client.

    Requires:
    - JWT key at ~/.sf/jwt/{org}.key or ~/.sf/jwt/{org}-agentforce-observability.key
    - Consumer key at ~/.sf/jwt/{org}.consumer-key or in environment

    Skips test if auth files not found.
    """
    from scripts.auth import Data360Auth

    try:
        auth = Data360Auth(org_alias=org_alias)
        # Verify connection works
        auth.test_connection()
        return auth
    except FileNotFoundError as e:
        pytest.skip(f"Auth files not found: {e}")
    except ValueError as e:
        pytest.skip(f"Auth configuration error: {e}")
    except RuntimeError as e:
        pytest.skip(f"Cannot connect to Salesforce: {e}")


@pytest.fixture
def mock_auth():
    """Create a mocked auth client for offline testing."""
    mock = MagicMock()
    mock.org_alias = "test-org"
    mock.key_path = Path("/tmp/test.key")
    mock.consumer_key = "test-consumer-key"
    mock.instance_url = "https://test.salesforce.com"
    mock.get_token.return_value = "mock-access-token"
    mock.get_headers.return_value = {
        "Authorization": "Bearer mock-access-token",
        "Content-Type": "application/json"
    }
    mock.test_connection.return_value = True

    # Mock org_info property
    mock.org_info.instance_url = "https://test.salesforce.com"
    mock.org_info.username = "test@example.com"
    mock.org_info.is_sandbox = False

    return mock


# =============================================================================
# Data Client Fixtures
# =============================================================================

@pytest.fixture
def data_client(auth_client):
    """Create authenticated Data360Client."""
    from scripts.datacloud_client import Data360Client
    return Data360Client(auth_client)


@pytest.fixture
def mock_data_client(mock_auth):
    """Create mocked Data360Client for offline testing."""
    mock = MagicMock()
    mock.auth = mock_auth
    mock.api_version = "v65.0"
    mock.base_url = "https://test.salesforce.com"
    mock.query_url = "https://test.salesforce.com/services/data/v65.0/ssot/query-sql"
    return mock


# =============================================================================
# Test Data Directory Fixtures
# =============================================================================

@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test output."""
    temp_dir = tempfile.mkdtemp(prefix="stdm_test_")
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Path to validation fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_data_dir(fixtures_dir: Path) -> Path:
    """
    Path to sample Parquet data for offline testing.

    If fixtures don't exist, creates minimal sample data.
    """
    if not fixtures_dir.exists():
        fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Create sample data if not exists
    sessions_dir = fixtures_dir / "sessions"
    if not sessions_dir.exists():
        _create_sample_fixtures(fixtures_dir)

    return fixtures_dir


def _create_sample_fixtures(fixtures_dir: Path):
    """Create minimal sample Parquet fixtures for offline testing."""

    # Sample session data
    sessions_data = [
        {
            "ssot__Id__c": "session-001",
            "ssot__StartTimestamp__c": "2026-01-28T10:00:00.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T10:15:00.000Z",
            "ssot__AiAgentSessionEndType__c": "Completed",
            "ssot__AiAgentChannelType__c": "Messaging",
            "ssot__RelatedMessagingSessionId__c": None,
            "ssot__RelatedVoiceCallId__c": None,
            "ssot__InternalOrganizationId__c": "00D000000000001",
            "ssot__SessionOwnerId__c": "005000000000001",
            "ssot__SessionOwnerObject__c": "User",
            "ssot__IndividualId__c": "ind-001",
            "ssot__PreviousSessionId__c": None,
            "ssot__VariableText__c": None,
        },
        {
            "ssot__Id__c": "session-002",
            "ssot__StartTimestamp__c": "2026-01-28T11:00:00.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T11:30:00.000Z",
            "ssot__AiAgentSessionEndType__c": "Escalated",
            "ssot__AiAgentChannelType__c": "Messaging",
            "ssot__RelatedMessagingSessionId__c": None,
            "ssot__RelatedVoiceCallId__c": None,
            "ssot__InternalOrganizationId__c": "00D000000000001",
            "ssot__SessionOwnerId__c": "005000000000002",
            "ssot__SessionOwnerObject__c": "User",
            "ssot__IndividualId__c": "ind-002",
            "ssot__PreviousSessionId__c": None,
            "ssot__VariableText__c": None,
        },
    ]

    # Sample interaction data
    interactions_data = [
        {
            "ssot__Id__c": "interaction-001",
            "ssot__AiAgentSessionId__c": "session-001",
            "ssot__AiAgentInteractionType__c": "TURN",
            "ssot__TopicApiName__c": "General_Support",
            "ssot__StartTimestamp__c": "2026-01-28T10:00:30.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T10:01:00.000Z",
            "ssot__PrevInteractionId__c": None,
            "ssot__SessionOwnerId__c": "005000000000001",
            "ssot__IndividualId__c": "ind-001",
            "ssot__InternalOrganizationId__c": "00D000000000001",
            "ssot__TelemetryTraceId__c": "trace-001",
            "ssot__TelemetryTraceSpanId__c": "span-001",
            "ssot__AttributeText__c": None,
        },
        {
            "ssot__Id__c": "interaction-002",
            "ssot__AiAgentSessionId__c": "session-001",
            "ssot__AiAgentInteractionType__c": "TURN",
            "ssot__TopicApiName__c": "Order_Status",
            "ssot__StartTimestamp__c": "2026-01-28T10:02:00.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T10:03:00.000Z",
            "ssot__PrevInteractionId__c": "interaction-001",
            "ssot__SessionOwnerId__c": "005000000000001",
            "ssot__IndividualId__c": "ind-001",
            "ssot__InternalOrganizationId__c": "00D000000000001",
            "ssot__TelemetryTraceId__c": "trace-001",
            "ssot__TelemetryTraceSpanId__c": "span-002",
            "ssot__AttributeText__c": None,
        },
    ]

    # Sample step data
    steps_data = [
        {
            "ssot__Id__c": "step-001",
            "ssot__AiAgentInteractionId__c": "interaction-001",
            "ssot__AiAgentInteractionStepType__c": "LLM_STEP",
            "ssot__Name__c": "PlannerPrompt",
            "ssot__InputValueText__c": '{"user_input": "What is my order status?"}',
            "ssot__OutputValueText__c": '{"plan": "Check order status"}',
            "ssot__PreStepVariableText__c": None,
            "ssot__PostStepVariableText__c": None,
            "ssot__GenerationId__c": "gen-001",
            "ssot__ErrorMessageText__c": None,
            "ssot__StartTimestamp__c": "2026-01-28T10:00:31.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T10:00:35.000Z",
            "ssot__PrevStepId__c": None,
            "ssot__InternalOrganizationId__c": "00D000000000001",
            "ssot__TelemetryTraceSpanId__c": "span-001-step-001",
            "ssot__AttributeText__c": None,
            "ssot__GenAiGatewayRequestId__c": "req-001",
            "ssot__GenAiGatewayResponseId__c": "resp-001",
        },
        {
            "ssot__Id__c": "step-002",
            "ssot__AiAgentInteractionId__c": "interaction-001",
            "ssot__AiAgentInteractionStepType__c": "ACTION_STEP",
            "ssot__Name__c": "Get_Order_Status_Flow",
            "ssot__InputValueText__c": '{"order_id": "ORD-12345"}',
            "ssot__OutputValueText__c": '{"status": "Shipped", "tracking": "1Z999"}',
            "ssot__PreStepVariableText__c": None,
            "ssot__PostStepVariableText__c": '{"$Output.Order_Status": "Shipped"}',
            "ssot__GenerationId__c": None,
            "ssot__ErrorMessageText__c": None,
            "ssot__StartTimestamp__c": "2026-01-28T10:00:36.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T10:00:40.000Z",
            "ssot__PrevStepId__c": "step-001",
            "ssot__InternalOrganizationId__c": "00D000000000001",
            "ssot__TelemetryTraceSpanId__c": "span-001-step-002",
            "ssot__AttributeText__c": None,
            "ssot__GenAiGatewayRequestId__c": None,
            "ssot__GenAiGatewayResponseId__c": None,
        },
    ]

    # Sample message/moment data
    messages_data = [
        {
            "ssot__Id__c": "moment-001",
            "ssot__AiAgentSessionId__c": "session-001",
            "ssot__AiAgentApiName__c": "Customer_Support_Agent",
            "ssot__AiAgentVersionApiName__c": "Customer_Support_Agent_v1",
            "ssot__RequestSummaryText__c": "User asked about order status",
            "ssot__ResponseSummaryText__c": "Agent provided order tracking information",
            "ssot__StartTimestamp__c": "2026-01-28T10:00:30.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T10:01:00.000Z",
            "ssot__InternalOrganizationId__c": "00D000000000001",
        },
        {
            "ssot__Id__c": "moment-002",
            "ssot__AiAgentSessionId__c": "session-002",
            "ssot__AiAgentApiName__c": "Customer_Support_Agent",
            "ssot__AiAgentVersionApiName__c": "Customer_Support_Agent_v1",
            "ssot__RequestSummaryText__c": "User reported a problem with their order",
            "ssot__ResponseSummaryText__c": "Agent escalated to human support",
            "ssot__StartTimestamp__c": "2026-01-28T11:00:00.000Z",
            "ssot__EndTimestamp__c": "2026-01-28T11:30:00.000Z",
            "ssot__InternalOrganizationId__c": "00D000000000001",
        },
    ]

    # Write Parquet files
    for name, data, schema in [
        ("sessions", sessions_data, SESSION_SCHEMA),
        ("interactions", interactions_data, INTERACTION_SCHEMA),
        ("steps", steps_data, STEP_SCHEMA),
        ("messages", messages_data, MESSAGE_SCHEMA),
    ]:
        dir_path = fixtures_dir / name
        dir_path.mkdir(parents=True, exist_ok=True)

        # Convert to PyArrow table and write
        table = pa.Table.from_pylist(data, schema=schema)
        pq.write_table(table, dir_path / "data.parquet")

    # Create metadata
    metadata = {
        "created": datetime.utcnow().isoformat(),
        "description": "Sample fixtures for offline validation testing",
        "record_counts": {
            "sessions": len(sessions_data),
            "interactions": len(interactions_data),
            "steps": len(steps_data),
            "messages": len(messages_data),
        }
    }

    with open(fixtures_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


# =============================================================================
# CLI Testing Fixtures
# =============================================================================

@pytest.fixture
def cli_runner():
    """Create Click CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def cli_app():
    """Import CLI application."""
    from scripts.cli import cli
    return cli


# =============================================================================
# Scoring Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def scenario_registry() -> dict:
    """Load scenario registry configuration."""
    registry_path = Path(__file__).parent / "scenario_registry.json"
    with open(registry_path) as f:
        return json.load(f)


# =============================================================================
# Utility Functions
# =============================================================================

def assert_parquet_schema(parquet_path: Path, expected_schema: pa.Schema):
    """Assert that a Parquet file has the expected schema."""
    table = pq.read_table(parquet_path)
    actual_fields = set(table.schema.names)
    expected_fields = set(expected_schema.names)

    missing = expected_fields - actual_fields
    assert not missing, f"Missing fields in Parquet: {missing}"


def assert_cli_success(result, expected_in_output: list[str] = None):
    """Assert CLI command succeeded and optionally check output."""
    assert result.exit_code == 0, f"CLI failed with: {result.output}"

    if expected_in_output:
        for expected in expected_in_output:
            assert expected in result.output, f"Expected '{expected}' in output: {result.output}"


def assert_cli_failure(result, expected_error: str = None):
    """Assert CLI command failed and optionally check error message."""
    assert result.exit_code != 0, f"Expected failure but got: {result.output}"

    if expected_error:
        assert expected_error in result.output, f"Expected '{expected_error}' in: {result.output}"
