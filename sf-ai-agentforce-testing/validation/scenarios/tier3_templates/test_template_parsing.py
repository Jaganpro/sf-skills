"""
Tier 3 - Template Parsing Tests (5 points)

Validates that each multi-turn YAML template can be parsed and contains
the basic structural elements required for test execution: scenarios with
names and turns.

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


@pytest.mark.tier3
@pytest.mark.offline
@pytest.mark.parametrize("template_name", MULTI_TURN_TEMPLATES)
class TestTemplateParsing:
    """Basic parsing and structural checks for multi-turn YAML templates."""

    def test_yaml_parses(self, templates_dir, template_name):
        """Template can be parsed by yaml.safe_load without error."""
        path = templates_dir / template_name
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert isinstance(data, dict)

    def test_has_scenarios(self, templates_dir, template_name):
        """Template has a 'scenarios' key with at least one scenario."""
        path = templates_dir / template_name
        with open(path) as f:
            data = yaml.safe_load(f)
        assert "scenarios" in data, f"Template {template_name} missing 'scenarios' key"
        assert len(data["scenarios"]) >= 1, (
            f"Template {template_name} has zero scenarios"
        )

    def test_scenarios_have_names(self, templates_dir, template_name):
        """Every scenario has a 'name' key."""
        path = templates_dir / template_name
        with open(path) as f:
            data = yaml.safe_load(f)
        for i, scenario in enumerate(data["scenarios"]):
            assert "name" in scenario, (
                f"Scenario {i} in {template_name} missing 'name'"
            )

    def test_scenarios_have_turns(self, templates_dir, template_name):
        """Every scenario has a 'turns' key with at least one turn."""
        path = templates_dir / template_name
        with open(path) as f:
            data = yaml.safe_load(f)
        for scenario in data["scenarios"]:
            sname = scenario.get("name", "?")
            assert "turns" in scenario, (
                f"Scenario '{sname}' in {template_name} missing 'turns'"
            )
            assert len(scenario["turns"]) >= 1, (
                f"Scenario '{sname}' in {template_name} has zero turns"
            )
