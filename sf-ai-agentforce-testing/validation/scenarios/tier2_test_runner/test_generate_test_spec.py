"""
Tier 2 — generate-test-spec.py unit tests for Agent Script support.

Validates that parse_agent_file() and generate_test_cases() correctly handle
Agent Script (.agent) files:
- Config block parsing (developer_name, agent_description)
- Topic discovery (start_agent + regular topics)
- Action extraction (skips inputs/outputs field definitions)
- Transition action detection from start_agent reasoning.actions
- Test case generation: routing tests with go_<topic> transition actions
- Test case generation: action tests with conversationHistory for apex://
- Edge case test generation
"""

import tempfile
import textwrap
import pytest
import sys
from pathlib import Path

# Add hooks/scripts to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "hooks" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Import from generate-test-spec.py (module name has hyphens, use importlib)
import importlib
generate_mod = importlib.import_module("generate-test-spec")

parse_agent_file = generate_mod.parse_agent_file
generate_test_cases = generate_mod.generate_test_cases
extract_value = generate_mod.extract_value
manual_yaml_output = generate_mod.manual_yaml_output
AgentStructure = generate_mod.AgentStructure
AgentTopic = generate_mod.AgentTopic
AgentAction = generate_mod.AgentAction


# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════

SAMPLE_AGENT = textwrap.dedent("""\
    config:
       developer_name: "Test_Agent"
       agent_description: "A test agent"
       agent_type: "AgentforceServiceAgent"
       default_agent_user: "test@example.com"

    start_agent entry:
       description: "Entry point"
       reasoning:
          instructions: |
             Route the user to the right topic.
          actions:
             go_order_status: @utils.transition to @topic.order_status
                description: "Route to order status"
             go_support: @utils.transition to @topic.support
                description: "Route to support"
             escalate_entry: @utils.escalate
                description: "Escalate to human"

    topic order_status:
       description: "Look up order details"

       actions:
          get_order_status:
             description: "Fetch order information by ID"
             inputs:
                order_id: string
                   description: "The Order record ID"
             outputs:
                order_number: string
                   description: "Order number"
                status: string
                   description: "Order status"
                total_amount: currency
                   description: "Total amount"
             target: "apex://OrderStatusService"

       reasoning:
          instructions: |
             Help the customer check their order status.
          actions:
             check_status: @actions.get_order_status
                with order_id = ...
                set @variables.status = @outputs.status

    topic support:
       description: "Create support cases"

       actions:
          create_case:
             description: "Create a support case"
             inputs:
                subject: string
                   description: "Case subject"
             outputs:
                case_number: string
                   description: "Created case number"
             target: "flow://Create_Support_Case"

       reasoning:
          instructions: |
             Help the customer create a support case.
          actions:
             open_case: @actions.create_case
                with subject = ...
""")


@pytest.fixture
def sample_agent_file(tmp_path):
    """Write a sample .agent file and return its path."""
    agent_path = tmp_path / "Test_Agent.agent"
    agent_path.write_text(SAMPLE_AGENT)
    return str(agent_path)


# ═══════════════════════════════════════════════════════════════════════
# Tests: parse_agent_file()
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.tier2
@pytest.mark.offline
class TestParseAgentFile:
    """Validate parse_agent_file() extracts correct structure from .agent files."""

    def test_extracts_agent_name(self, sample_agent_file):
        """Config block developer_name becomes agent_name."""
        structure = parse_agent_file(sample_agent_file)
        assert structure.agent_name == "Test_Agent"

    def test_extracts_description(self, sample_agent_file):
        """Config block agent_description is extracted."""
        structure = parse_agent_file(sample_agent_file)
        assert structure.description == "A test agent"

    def test_finds_all_topics(self, sample_agent_file):
        """Parser finds start_agent + 2 regular topics = 3 total."""
        structure = parse_agent_file(sample_agent_file)
        assert len(structure.topics) == 3
        names = [t.name for t in structure.topics]
        assert "entry" in names
        assert "order_status" in names
        assert "support" in names

    def test_start_agent_marked(self, sample_agent_file):
        """start_agent topic has is_start_agent=True."""
        structure = parse_agent_file(sample_agent_file)
        entry = structure.get_topic("entry")
        assert entry is not None
        assert entry.is_start_agent is True

    def test_start_agent_transitions(self, sample_agent_file):
        """start_agent has transitions to order_status and support."""
        structure = parse_agent_file(sample_agent_file)
        entry = structure.get_topic("entry")
        assert "order_status" in entry.transitions
        assert "support" in entry.transitions

    def test_topic_actions_not_polluted_by_io(self, sample_agent_file):
        """Input/output field definitions are NOT parsed as actions."""
        structure = parse_agent_file(sample_agent_file)
        order_topic = structure.get_topic("order_status")
        action_names = [a.name for a in order_topic.actions]

        # Should have exactly 1 action (get_order_status)
        assert len(order_topic.actions) == 1, (
            f"Expected 1 action, got {len(order_topic.actions)}: {action_names}"
        )
        assert "get_order_status" in action_names
        # These are input/output fields, NOT actions
        assert "order_id" not in action_names
        assert "order_number" not in action_names
        assert "status" not in action_names
        assert "total_amount" not in action_names

    def test_action_has_target(self, sample_agent_file):
        """Action has the apex:// target from the .agent file."""
        structure = parse_agent_file(sample_agent_file)
        order_topic = structure.get_topic("order_status")
        action = order_topic.actions[0]
        assert action.name == "get_order_status"
        assert action.target == "apex://OrderStatusService"

    def test_flow_action_target(self, sample_agent_file):
        """Flow action target is correctly extracted."""
        structure = parse_agent_file(sample_agent_file)
        support = structure.get_topic("support")
        assert len(support.actions) == 1
        action = support.actions[0]
        assert action.name == "create_case"
        assert action.target == "flow://Create_Support_Case"

    def test_topic_description(self, sample_agent_file):
        """Topic descriptions are extracted."""
        structure = parse_agent_file(sample_agent_file)
        order_topic = structure.get_topic("order_status")
        assert order_topic.description == "Look up order details"


# ═══════════════════════════════════════════════════════════════════════
# Tests: generate_test_cases()
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.tier2
@pytest.mark.offline
class TestGenerateTestCases:
    """Validate generate_test_cases() produces correct test cases for Agent Script."""

    def _get_structure(self, sample_agent_file):
        return parse_agent_file(sample_agent_file)

    def test_generates_routing_tests(self, sample_agent_file):
        """Generates routing tests for each non-start_agent topic."""
        structure = self._get_structure(sample_agent_file)
        test_cases = generate_test_cases(structure)

        # Find routing tests (have expectedTopic but may or may not have expectedActions)
        routing_topics = {tc["expectedTopic"] for tc in test_cases
                         if tc["expectedTopic"] not in ("entry",)}
        assert "order_status" in routing_topics
        assert "support" in routing_topics

    def test_routing_tests_include_transition_actions(self, sample_agent_file):
        """Routing tests for Agent Script include go_<topic> transition actions."""
        structure = self._get_structure(sample_agent_file)
        test_cases = generate_test_cases(structure)

        # Find routing test for order_status
        order_routing = [tc for tc in test_cases
                         if tc["expectedTopic"] == "order_status"
                         and "conversationHistory" not in tc]
        assert len(order_routing) >= 1, "Should have at least one routing test for order_status"

        # The routing test should include go_order_status transition action
        first = order_routing[0]
        assert "expectedActions" in first, "Routing test should include expectedActions"
        assert "go_order_status" in first["expectedActions"]

    def test_apex_action_uses_conversation_history(self, sample_agent_file):
        """apex:// actions generate tests WITH conversationHistory."""
        structure = self._get_structure(sample_agent_file)
        test_cases = generate_test_cases(structure)

        # Find action tests with conversationHistory
        history_tests = [tc for tc in test_cases if "conversationHistory" in tc]
        assert len(history_tests) >= 1, (
            "Should generate at least one test with conversationHistory for apex:// action"
        )

        # Check the apex action test
        apex_test = history_tests[0]
        assert apex_test["expectedTopic"] == "order_status"
        assert "get_order_status" in apex_test["expectedActions"]

        # Check conversationHistory structure
        history = apex_test["conversationHistory"]
        assert len(history) == 2  # user + agent
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "agent"
        assert history[1]["topic"] == "order_status"

    def test_flow_action_no_conversation_history(self, sample_agent_file):
        """flow:// actions generate single-utterance tests (no conversationHistory)."""
        structure = self._get_structure(sample_agent_file)
        test_cases = generate_test_cases(structure)

        # Find flow action test
        flow_tests = [tc for tc in test_cases
                      if tc.get("expectedActions") and "create_case" in tc["expectedActions"]]
        assert len(flow_tests) >= 1, "Should generate test for flow:// action"

        # Flow actions don't need conversationHistory
        flow_test = flow_tests[0]
        assert "conversationHistory" not in flow_test

    def test_edge_cases_generated(self, sample_agent_file):
        """Edge case tests are appended."""
        structure = self._get_structure(sample_agent_file)
        test_cases = generate_test_cases(structure)

        # Edge case tests target the router topic
        edge_cases = [tc for tc in test_cases if tc["expectedTopic"] == "entry"]
        assert len(edge_cases) >= 1, "Should generate edge case tests"

    def test_no_test_for_start_agent_topic(self, sample_agent_file):
        """No routing test is generated for the start_agent topic itself."""
        structure = self._get_structure(sample_agent_file)
        test_cases = generate_test_cases(structure)

        # Routing tests should NOT target start_agent
        routing_tests = [tc for tc in test_cases
                         if tc["expectedTopic"] == "entry"
                         and "conversationHistory" not in tc
                         and tc.get("expectedActions")]
        # The only "entry" tests should be edge cases (no expectedActions with go_)
        for tc in routing_tests:
            actions = tc.get("expectedActions", [])
            assert not any(a.startswith("go_") for a in actions), (
                "Should not generate a routing test for start_agent itself"
            )


# ═══════════════════════════════════════════════════════════════════════
# Tests: extract_value() helper
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.tier2
@pytest.mark.offline
class TestExtractValue:
    """Validate extract_value() handles various value formats."""

    def test_unquoted_value(self):
        assert extract_value('name: hello') == "hello"

    def test_double_quoted_value(self):
        assert extract_value('name: "hello world"') == "hello world"

    def test_single_quoted_value(self):
        assert extract_value("name: 'hello world'") == "hello world"

    def test_no_colon(self):
        assert extract_value("no colon here") == ""

    def test_empty_value(self):
        assert extract_value("name:") == ""

    def test_value_with_protocol(self):
        assert extract_value('target: "apex://OrderService"') == "apex://OrderService"


# ═══════════════════════════════════════════════════════════════════════
# Tests: manual_yaml_output()
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.tier2
@pytest.mark.offline
class TestManualYamlOutput:
    """Validate manual_yaml_output() produces correct YAML without pyyaml."""

    def test_includes_required_fields(self):
        """Output includes name, subjectType, subjectName."""
        spec = {
            "name": "My Tests",
            "subjectType": "AGENT",
            "subjectName": "My_Agent",
            "testCases": [
                {"utterance": "Hello", "expectedTopic": "greeting"}
            ],
        }
        output = manual_yaml_output(spec)
        assert 'name: "My Tests"' in output
        assert "subjectType: AGENT" in output
        assert "subjectName: My_Agent" in output
        assert "testCases:" in output

    def test_includes_conversation_history(self):
        """Output includes conversationHistory block for Agent Script tests."""
        spec = {
            "name": "Agent Tests",
            "subjectType": "AGENT",
            "subjectName": "Test_Agent",
            "testCases": [
                {
                    "utterance": "Order ID is 12345",
                    "expectedTopic": "order_status",
                    "expectedActions": ["get_order_status"],
                    "conversationHistory": [
                        {"role": "user", "message": "Check my order"},
                        {"role": "agent", "message": "Provide the ID", "topic": "order_status"},
                    ],
                }
            ],
        }
        output = manual_yaml_output(spec)
        assert "conversationHistory:" in output
        assert 'role: "user"' in output
        assert 'role: "agent"' in output
        assert 'topic: "order_status"' in output
        assert "expectedActions:" in output
        assert "- get_order_status" in output

    def test_includes_expected_outcome(self):
        """Output includes expectedOutcome field."""
        spec = {
            "name": "Tests",
            "subjectType": "AGENT",
            "subjectName": "Agent",
            "testCases": [
                {
                    "utterance": "Hello",
                    "expectedTopic": "greeting",
                    "expectedOutcome": "Agent should greet the user",
                }
            ],
        }
        output = manual_yaml_output(spec)
        assert 'expectedOutcome: "Agent should greet the user"' in output
