"""
Tier 2 — Agent Script (.agent file) discovery and parsing tests.

Verifies that agent_discovery._parse_agent_script() correctly extracts:
- config block: developer_name, description, default_agent_user
- topics: start_agent (entry) and regular topics
- actions: Level 1 definitions with targets
- invocations: Level 2 action refs, transitions, escalations
- inputs/outputs fields are NOT treated as actions
"""

import json
import tempfile
import textwrap
import pytest
import sys
from pathlib import Path

# Add hooks/scripts to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "hooks" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from agent_discovery import _parse_agent_script, discover_local


# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════

SAMPLE_AGENT_SCRIPT = textwrap.dedent("""\
    config:
       developer_name: "Test_Agent"
       agent_description: "A test agent for validation"
       agent_type: "AgentforceServiceAgent"
       default_agent_user: "test@example.com"

    variables:
       my_var: mutable string = ""

    start_agent entry:
       description: "Entry point"
       reasoning:
          instructions: |
             Route the user to the appropriate topic.
          actions:
             go_main_topic: @utils.transition to @topic.main_topic
                description: "Route to main topic"
             escalate_entry: @utils.escalate
                description: "Escalate to human"

    topic main_topic:
       description: "The main topic for testing"

       actions:
          do_something:
             description: "Performs the main action"
             inputs:
                input_field: string
                   description: "An input field"
             outputs:
                output_field: string
                   description: "An output field"
                success: boolean
                   description: "Whether it succeeded"
             target: "apex://TestService"

       reasoning:
          instructions: |
             Help the user with the main topic.
          actions:
             run_action: @actions.do_something
                description: "Execute the action"
                with input_field = ...
                set @variables.my_var = @outputs.output_field
             escalate_now: @utils.escalate
                description: "Escalate if needed"
""")


@pytest.fixture
def sample_agent_file(tmp_path):
    """Write a sample .agent file and return its path."""
    agent_path = tmp_path / "Test_Agent.agent"
    agent_path.write_text(SAMPLE_AGENT_SCRIPT)
    return str(agent_path)


# ═══════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.tier2
@pytest.mark.offline
class TestAgentScriptParsing:
    """Validate _parse_agent_script() extracts correct metadata."""

    def test_parses_config_block(self, sample_agent_file):
        """Config block extracts developer_name, description, default_agent_user."""
        result = _parse_agent_script(sample_agent_file)
        assert result is not None
        assert result["name"] == "Test_Agent"
        assert result["type"] == "AiAuthoringBundle"
        assert result["description"] == "A test agent for validation"
        assert result["default_agent_user"] == "test@example.com"

    def test_discovers_two_topics(self, sample_agent_file):
        """Parser finds both start_agent (entry) and regular topic."""
        result = _parse_agent_script(sample_agent_file)
        assert len(result["topics"]) == 2
        topic_names = [t["name"] for t in result["topics"]]
        assert "entry" in topic_names
        assert "main_topic" in topic_names

    def test_start_agent_is_marked(self, sample_agent_file):
        """start_agent topic has is_start_agent=True and scope=entry."""
        result = _parse_agent_script(sample_agent_file)
        entry = next(t for t in result["topics"] if t["name"] == "entry")
        assert entry.get("is_start_agent") is True
        assert entry.get("scope") == "entry"

    def test_start_agent_transitions(self, sample_agent_file):
        """start_agent has transitions to main_topic."""
        result = _parse_agent_script(sample_agent_file)
        entry = next(t for t in result["topics"] if t["name"] == "entry")
        assert "main_topic" in entry.get("transitions", [])

    def test_start_agent_invocations(self, sample_agent_file):
        """start_agent has transition and escalation invocations."""
        result = _parse_agent_script(sample_agent_file)
        entry = next(t for t in result["topics"] if t["name"] == "entry")
        invocations = entry.get("invocations", [])
        inv_names = [i["name"] for i in invocations]
        assert "go_main_topic" in inv_names
        assert "escalate_entry" in inv_names

        # Check types
        transition = next(i for i in invocations if i["name"] == "go_main_topic")
        assert transition["type"] == "transition"
        assert transition["target_topic"] == "main_topic"

        escalation = next(i for i in invocations if i["name"] == "escalate_entry")
        assert escalation["type"] == "escalation"

    def test_topic_actions_not_polluted_by_io_fields(self, sample_agent_file):
        """inputs/outputs field definitions are NOT parsed as separate actions."""
        result = _parse_agent_script(sample_agent_file)
        main = next(t for t in result["topics"] if t["name"] == "main_topic")
        actions = main.get("actions", [])
        action_names = [a["name"] for a in actions]

        # Should have exactly 1 action (do_something), not 4+ from io fields
        assert len(actions) == 1, (
            f"Expected 1 action, got {len(actions)}: {action_names}"
        )
        assert "do_something" in action_names
        assert "input_field" not in action_names
        assert "output_field" not in action_names
        assert "success" not in action_names

    def test_action_has_correct_target(self, sample_agent_file):
        """Action has the apex:// target from the .agent file."""
        result = _parse_agent_script(sample_agent_file)
        main = next(t for t in result["topics"] if t["name"] == "main_topic")
        action = main["actions"][0]
        assert action["name"] == "do_something"
        assert action["invocationTarget"] == "apex://TestService"

    def test_topic_invocations_parsed(self, sample_agent_file):
        """Topic reasoning.actions block is parsed for invocations."""
        result = _parse_agent_script(sample_agent_file)
        main = next(t for t in result["topics"] if t["name"] == "main_topic")
        invocations = main.get("invocations", [])
        inv_names = [i["name"] for i in invocations]
        assert "run_action" in inv_names
        assert "escalate_now" in inv_names

        # Check action invocation references
        run_action = next(i for i in invocations if i["name"] == "run_action")
        assert run_action["type"] == "action"
        assert run_action["references"] == "do_something"

    def test_can_escalate_flags(self, sample_agent_file):
        """Topics with escalation invocations have canEscalate=True."""
        result = _parse_agent_script(sample_agent_file)
        entry = next(t for t in result["topics"] if t["name"] == "entry")
        main = next(t for t in result["topics"] if t["name"] == "main_topic")
        assert entry["canEscalate"] is True
        assert main["canEscalate"] is True

    def test_all_actions_list(self, sample_agent_file):
        """Top-level actions list contains only action definitions."""
        result = _parse_agent_script(sample_agent_file)
        all_actions = result["actions"]
        assert len(all_actions) == 1
        assert all_actions[0]["name"] == "do_something"
        assert all_actions[0]["target"] == "apex://TestService"

    def test_nonexistent_file_returns_none(self):
        """Parsing a nonexistent file returns None (with warning)."""
        result = _parse_agent_script("/nonexistent/path/Agent.agent")
        assert result is None

    def test_empty_file_returns_minimal(self, tmp_path):
        """An empty .agent file returns a minimal agent with filename as name."""
        empty = tmp_path / "Empty_Agent.agent"
        empty.write_text("")
        result = _parse_agent_script(str(empty))
        assert result is not None
        assert result["name"] == "Empty_Agent"
        assert result["type"] == "AiAuthoringBundle"
        assert result["topics"] == []
