"""
Tier 2 — _infer_failure_category() and _suggest_fix() unit tests.

Verifies that every known check name maps to a failure category,
unknown checks return None, and all categories have fix suggestions.
"""

import pytest

from multi_turn_test_runner import _infer_failure_category, _suggest_fix


# The full mapping from the source code
KNOWN_CHECK_TO_CATEGORY = {
    "topic_contains": "TOPIC_RE_MATCHING_FAILURE",
    "response_contains": "CONTEXT_PRESERVATION_FAILURE",
    "response_contains_any": "CONTEXT_PRESERVATION_FAILURE",
    "response_not_contains": "GUARDRAIL_NOT_TRIGGERED",
    "context_retained": "CONTEXT_PRESERVATION_FAILURE",
    "context_uses": "CONTEXT_PRESERVATION_FAILURE",
    "no_re_ask_for": "CONTEXT_PRESERVATION_FAILURE",
    "response_references": "CONTEXT_PRESERVATION_FAILURE",
    "response_references_both": "CONTEXT_PRESERVATION_FAILURE",
    "escalation_triggered": "MULTI_TURN_ESCALATION_FAILURE",
    "guardrail_triggered": "GUARDRAIL_NOT_TRIGGERED",
    "action_invoked": "ACTION_NOT_INVOKED",
    "has_action_result": "ACTION_NOT_INVOKED",
    "action_uses_prior_output": "ACTION_CHAIN_FAILURE",
    "action_uses_variable": "ACTION_CHAIN_FAILURE",
    "response_not_empty": "RESPONSE_QUALITY_ISSUE",
    "response_acknowledges_change": "RESPONSE_QUALITY_ISSUE",
    "response_offers_help": "RESPONSE_QUALITY_ISSUE",
    "response_offers_alternative": "RESPONSE_QUALITY_ISSUE",
    "response_acknowledges_error": "RESPONSE_QUALITY_ISSUE",
    "conversation_resolved": "RESPONSE_QUALITY_ISSUE",
    "response_declines_gracefully": "GUARDRAIL_NOT_TRIGGERED",
    "resumes_normal": "GUARDRAIL_RECOVERY_FAILURE",
    "turn_elapsed_max": "RESPONSE_QUALITY_ISSUE",
    "response_matches_regex": "CONTEXT_PRESERVATION_FAILURE",
    "response_length_min": "RESPONSE_QUALITY_ISSUE",
    "response_length_max": "RESPONSE_QUALITY_ISSUE",
    "action_result_contains": "ACTION_CHAIN_FAILURE",
}

ALL_CATEGORIES = {
    "TOPIC_RE_MATCHING_FAILURE",
    "CONTEXT_PRESERVATION_FAILURE",
    "MULTI_TURN_ESCALATION_FAILURE",
    "GUARDRAIL_NOT_TRIGGERED",
    "ACTION_NOT_INVOKED",
    "ACTION_CHAIN_FAILURE",
    "RESPONSE_QUALITY_ISSUE",
    "GUARDRAIL_RECOVERY_FAILURE",
}


@pytest.mark.tier2
@pytest.mark.offline
def test_all_categories_mapped():
    """Every known check name returns the expected failure category."""
    dummy_turn = {"agent_text": "", "evaluation": {}}
    for check_name, expected_category in KNOWN_CHECK_TO_CATEGORY.items():
        category = _infer_failure_category(check_name, dummy_turn)
        assert category == expected_category, (
            f"Check '{check_name}' expected category '{expected_category}', "
            f"got '{category}'"
        )


@pytest.mark.tier2
@pytest.mark.offline
def test_unknown_check_returns_none():
    """_infer_failure_category for an unknown check returns None."""
    result = _infer_failure_category("unknown_check", {})
    assert result is None


@pytest.mark.tier2
@pytest.mark.offline
def test_all_categories_have_fixes():
    """All 8 failure categories have a non-empty fix suggestion from _suggest_fix()."""
    for category in ALL_CATEGORIES:
        fix = _suggest_fix(category)
        assert fix is not None, f"Category '{category}' returned None fix"
        assert len(fix) > 0, f"Category '{category}' returned empty fix"
        # Ensure it's not the fallback message (meaning the category IS mapped)
        assert fix != "Review agent configuration for this failure type", (
            f"Category '{category}' fell through to default fix"
        )
