"""
Tier 3 - Template Schema Validation Tests (10 points)

Deeper structural validation of multi-turn YAML templates:
- Required top-level fields (apiVersion, kind, metadata, scenarios)
- Metadata structure (name, testMode, description)
- Turn structure (user string, expect dict)
- Expect keys use only recognized check types from scenario_registry

Each test is parametrized over all 4 multi-turn templates.
"""

import yaml
import pytest
from pathlib import Path

MULTI_TURN_TEMPLATES = [
    "multi-turn-comprehensive.yaml",
    "multi-turn-topic-routing.yaml",
    "multi-turn-context-preservation.yaml",
    "multi-turn-escalation-flows.yaml",
    "multi-turn-agentscript-comprehensive.yaml",
]

VALID_CHECK_TYPES = {
    "response_not_empty",
    "response_contains",
    "response_contains_any",
    "response_not_contains",
    "response_references",
    "response_references_both",
    "topic_contains",
    "escalation_triggered",
    "guardrail_triggered",
    "response_declines_gracefully",
    "context_retained",
    "context_uses",
    "no_re_ask_for",
    "action_invoked",
    "has_action_result",
    "action_uses_variable",
    "action_uses_prior_output",
    "response_acknowledges_change",
    "response_offers_help",
    "response_offers_alternative",
    "response_acknowledges_error",
    "resumes_normal",
    "conversation_resolved",
    "turn_elapsed_max",
    "response_matches_regex",
    "response_length_min",
    "response_length_max",
    "action_result_contains",
}

REQUIRED_TOP_LEVEL_FIELDS = {"apiVersion", "kind", "metadata", "scenarios"}
REQUIRED_METADATA_FIELDS = {"name", "testMode", "description"}


@pytest.mark.tier3
@pytest.mark.offline
@pytest.mark.parametrize("template_name", MULTI_TURN_TEMPLATES)
class TestTemplateSchema:
    """Schema-level validation for multi-turn YAML templates."""

    def _load(self, templates_dir, template_name):
        """Helper: load and return parsed YAML data."""
        path = templates_dir / template_name
        with open(path) as f:
            return yaml.safe_load(f)

    def test_required_top_level_fields(self, templates_dir, template_name):
        """Template must have: apiVersion, kind, metadata, scenarios."""
        data = self._load(templates_dir, template_name)
        missing = REQUIRED_TOP_LEVEL_FIELDS - set(data.keys())
        assert not missing, (
            f"Template {template_name} missing top-level fields: {missing}"
        )

    def test_metadata_structure(self, templates_dir, template_name):
        """metadata must have: name, testMode, description."""
        data = self._load(templates_dir, template_name)
        assert "metadata" in data, (
            f"Template {template_name} missing 'metadata' key"
        )
        metadata = data["metadata"]
        assert isinstance(metadata, dict), (
            f"Template {template_name}: 'metadata' is not a dict"
        )
        missing = REQUIRED_METADATA_FIELDS - set(metadata.keys())
        assert not missing, (
            f"Template {template_name} metadata missing fields: {missing}"
        )

    def test_turn_structure(self, templates_dir, template_name):
        """Each turn must have: user (str), expect (dict)."""
        data = self._load(templates_dir, template_name)
        for scenario in data["scenarios"]:
            sname = scenario.get("name", "?")
            for i, turn in enumerate(scenario["turns"]):
                assert "user" in turn, (
                    f"{template_name} > '{sname}' > turn {i}: missing 'user'"
                )
                assert isinstance(turn["user"], str), (
                    f"{template_name} > '{sname}' > turn {i}: 'user' must be a string"
                )
                assert "expect" in turn, (
                    f"{template_name} > '{sname}' > turn {i}: missing 'expect'"
                )
                assert isinstance(turn["expect"], dict), (
                    f"{template_name} > '{sname}' > turn {i}: 'expect' must be a dict"
                )

    def test_expect_keys_are_valid_check_types(self, templates_dir, template_name):
        """Every key in every turn's 'expect' dict must be a recognized check type."""
        data = self._load(templates_dir, template_name)
        for scenario in data["scenarios"]:
            sname = scenario.get("name", "?")
            for i, turn in enumerate(scenario["turns"]):
                expect = turn.get("expect", {})
                for key in expect:
                    assert key in VALID_CHECK_TYPES, (
                        f"{template_name} > '{sname}' > turn {i}: "
                        f"unrecognized check type '{key}'. "
                        f"Valid types: {sorted(VALID_CHECK_TYPES)}"
                    )
