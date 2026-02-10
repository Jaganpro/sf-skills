"""
Tier 3 — CLI Test Spec Template Schema Validation.

Validates that CLI YAML templates (for `sf agent test create --spec`) have
the correct structure. These templates use a DIFFERENT schema from the
multi-turn templates:

  Required: name, subjectType, subjectName, testCases
  Each testCase: utterance (required), expectedTopic, expectedActions,
                 expectedOutcome, conversationHistory

Parametrized over both standard and Agent Script CLI templates.
"""

import yaml
import pytest
from pathlib import Path

CLI_TEMPLATES = [
    "standard-test-spec.yaml",
    "agentscript-test-spec.yaml",
]

# Required top-level fields for sf agent test create YAML
REQUIRED_CLI_FIELDS = {"name", "subjectType", "subjectName", "testCases"}

# Valid fields in a testCase entry
VALID_TEST_CASE_FIELDS = {
    "utterance",
    "expectedTopic",
    "expectedActions",
    "expectedOutcome",
    "conversationHistory",
    "contextVariables",
}

# Valid fields in a conversationHistory entry
VALID_HISTORY_FIELDS = {"role", "message", "topic"}

# Valid roles in conversationHistory
VALID_ROLES = {"user", "agent"}


@pytest.mark.tier3
@pytest.mark.offline
@pytest.mark.parametrize("template_name", CLI_TEMPLATES)
class TestCLITemplateSchema:
    """Schema validation for CLI test spec YAML templates."""

    def _load(self, templates_dir, template_name):
        """Helper: load and return parsed YAML data."""
        path = templates_dir / template_name
        with open(path) as f:
            return yaml.safe_load(f)

    def test_yaml_parses(self, templates_dir, template_name):
        """Template can be parsed by yaml.safe_load without error."""
        data = self._load(templates_dir, template_name)
        assert data is not None
        assert isinstance(data, dict)

    def test_required_cli_fields(self, templates_dir, template_name):
        """Template has required CLI fields: name, subjectType, subjectName, testCases."""
        data = self._load(templates_dir, template_name)
        missing = REQUIRED_CLI_FIELDS - set(data.keys())
        assert not missing, (
            f"Template {template_name} missing required CLI fields: {missing}"
        )

    def test_subject_type_is_agent(self, templates_dir, template_name):
        """subjectType must be 'AGENT'."""
        data = self._load(templates_dir, template_name)
        assert data["subjectType"] == "AGENT", (
            f"Template {template_name}: subjectType must be 'AGENT', "
            f"got '{data['subjectType']}'"
        )

    def test_name_is_string(self, templates_dir, template_name):
        """name field must be a non-empty string."""
        data = self._load(templates_dir, template_name)
        assert isinstance(data["name"], str), (
            f"Template {template_name}: 'name' must be a string"
        )
        assert len(data["name"]) > 0, (
            f"Template {template_name}: 'name' must not be empty"
        )

    def test_subject_name_is_string(self, templates_dir, template_name):
        """subjectName must be a non-empty string."""
        data = self._load(templates_dir, template_name)
        assert isinstance(data["subjectName"], str), (
            f"Template {template_name}: 'subjectName' must be a string"
        )
        assert len(data["subjectName"]) > 0, (
            f"Template {template_name}: 'subjectName' must not be empty"
        )

    def test_test_cases_is_list(self, templates_dir, template_name):
        """testCases must be a non-empty list."""
        data = self._load(templates_dir, template_name)
        assert isinstance(data["testCases"], list), (
            f"Template {template_name}: 'testCases' must be a list"
        )
        assert len(data["testCases"]) >= 1, (
            f"Template {template_name}: 'testCases' must have at least 1 entry"
        )

    def test_every_test_case_has_utterance(self, templates_dir, template_name):
        """Every test case must have an 'utterance' string."""
        data = self._load(templates_dir, template_name)
        for i, tc in enumerate(data["testCases"]):
            assert "utterance" in tc, (
                f"{template_name} testCase[{i}]: missing required 'utterance'"
            )
            assert isinstance(tc["utterance"], str), (
                f"{template_name} testCase[{i}]: 'utterance' must be a string"
            )

    def test_test_case_fields_are_valid(self, templates_dir, template_name):
        """Every field in every testCase must be a recognized CLI field."""
        data = self._load(templates_dir, template_name)
        for i, tc in enumerate(data["testCases"]):
            unknown = set(tc.keys()) - VALID_TEST_CASE_FIELDS
            assert not unknown, (
                f"{template_name} testCase[{i}]: unrecognized fields {unknown}. "
                f"Valid fields: {sorted(VALID_TEST_CASE_FIELDS)}"
            )

    def test_expected_actions_is_flat_list(self, templates_dir, template_name):
        """expectedActions must be a flat list of strings (not objects)."""
        data = self._load(templates_dir, template_name)
        for i, tc in enumerate(data["testCases"]):
            actions = tc.get("expectedActions")
            if actions is None:
                continue
            assert isinstance(actions, list), (
                f"{template_name} testCase[{i}]: 'expectedActions' must be a list"
            )
            for j, action in enumerate(actions):
                assert isinstance(action, str), (
                    f"{template_name} testCase[{i}] expectedActions[{j}]: "
                    f"must be a string, got {type(action).__name__}"
                )

    def test_conversation_history_structure(self, templates_dir, template_name):
        """conversationHistory entries must have valid role + message fields."""
        data = self._load(templates_dir, template_name)
        for i, tc in enumerate(data["testCases"]):
            history = tc.get("conversationHistory")
            if history is None:
                continue
            assert isinstance(history, list), (
                f"{template_name} testCase[{i}]: 'conversationHistory' must be a list"
            )
            for j, entry in enumerate(history):
                assert isinstance(entry, dict), (
                    f"{template_name} testCase[{i}] history[{j}]: must be a dict"
                )
                # Check required fields
                assert "role" in entry, (
                    f"{template_name} testCase[{i}] history[{j}]: missing 'role'"
                )
                assert "message" in entry, (
                    f"{template_name} testCase[{i}] history[{j}]: missing 'message'"
                )
                # Check role is valid
                assert entry["role"] in VALID_ROLES, (
                    f"{template_name} testCase[{i}] history[{j}]: "
                    f"role must be {VALID_ROLES}, got '{entry['role']}'"
                )
                # Check field names are valid
                unknown = set(entry.keys()) - VALID_HISTORY_FIELDS
                assert not unknown, (
                    f"{template_name} testCase[{i}] history[{j}]: "
                    f"unrecognized fields {unknown}"
                )


@pytest.mark.tier3
@pytest.mark.offline
class TestAgentScriptTemplateContent:
    """Agent Script template has specific content requirements."""

    def _load(self, templates_dir):
        """Load the agentscript template."""
        path = templates_dir / "agentscript-test-spec.yaml"
        with open(path) as f:
            return yaml.safe_load(f)

    def test_has_routing_test_with_transition_action(self, templates_dir):
        """At least one testCase has expectedActions with go_ prefix (transition)."""
        data = self._load(templates_dir)
        has_transition = False
        for tc in data["testCases"]:
            actions = tc.get("expectedActions", [])
            for a in actions:
                if isinstance(a, str) and a.startswith("go_"):
                    has_transition = True
                    break
            if has_transition:
                break
        assert has_transition, (
            "agentscript-test-spec.yaml should have at least one routing test "
            "with a go_<topic> transition action in expectedActions"
        )

    def test_has_conversation_history_test(self, templates_dir):
        """At least one testCase uses conversationHistory (for action testing)."""
        data = self._load(templates_dir)
        has_history = any(
            "conversationHistory" in tc for tc in data["testCases"]
        )
        assert has_history, (
            "agentscript-test-spec.yaml should have at least one test case "
            "with conversationHistory for testing business actions"
        )

    def test_has_escalation_test(self, templates_dir):
        """At least one testCase targets Escalation topic."""
        data = self._load(templates_dir)
        has_escalation = any(
            tc.get("expectedTopic") == "Escalation" for tc in data["testCases"]
        )
        assert has_escalation, (
            "agentscript-test-spec.yaml should have at least one escalation test"
        )
