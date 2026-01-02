#!/usr/bin/env python3
"""
Cross-Skill Suggestion Hook for sf-ai-agentforce-testing

Analyzes file operations and suggests related skills based on:
- File type patterns (test specs, agent definitions)
- Content patterns (test assertions, failure types)
- Relationship matrix from skill-relationships.json

Usage: Called automatically via PostToolUse hook on Write|Edit operations.

Output: JSON with additionalContext containing skill suggestions.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Configuration
MAX_SUGGESTIONS = 3
SCRIPT_DIR = Path(__file__).parent
RELATIONSHIPS_FILE = SCRIPT_DIR / "skill-relationships.json"

# Cache for relationships config
_relationships_cache: Optional[dict] = None


def load_relationships() -> dict:
    """Load the skill relationships configuration."""
    global _relationships_cache
    if _relationships_cache is not None:
        return _relationships_cache

    try:
        with open(RELATIONSHIPS_FILE, 'r') as f:
            _relationships_cache = json.load(f)
            return _relationships_cache
    except (FileNotFoundError, json.JSONDecodeError):
        return {"file_patterns": {}, "relationships": {}}


def detect_skill_from_file(file_path: str, config: dict) -> Optional[str]:
    """Detect which skill owns this file based on patterns."""
    file_patterns = config.get("file_patterns", {})

    for pattern_group in file_patterns.values():
        patterns = pattern_group.get("patterns", [])
        for pattern in patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return pattern_group.get("skill")

    return None


def detect_content_triggers(file_path: str, content: str) -> list[str]:
    """Detect trigger patterns in file content."""
    triggers = []

    # Test spec patterns (YAML)
    if re.search(r"AiEvaluationDefinition|testCases:", content):
        triggers.append("test_spec")
    if re.search(r"expectedTopic:", content):
        triggers.append("topic_test")
    if re.search(r"expectedActions:", content):
        triggers.append("action_test")
    if re.search(r"expectedBehavior:\s*guardrail", content):
        triggers.append("guardrail_test")
    if re.search(r"expectedBehavior:\s*escalation", content):
        triggers.append("escalation_test")
    if re.search(r"conversationHistory:", content):
        triggers.append("multi_turn_test")

    # Agent definition patterns
    if re.search(r"\.agent$|agentDefinition", file_path):
        triggers.append("agent_definition")
    if re.search(r"topicDefinition|GenAiTopic", content):
        triggers.append("topic_definition")
    if re.search(r"plannerDefinition|GenAiPlanner", content):
        triggers.append("planner_definition")
    if re.search(r"flow://", content):
        triggers.append("flow_action")

    # Test result patterns
    if re.search(r"FAILED|failure|failed", content, re.IGNORECASE):
        triggers.append("failure")
    if re.search(r"TOPIC_NOT_MATCHED", content):
        triggers.append("topic_failure")
    if re.search(r"ACTION_NOT_INVOKED|ACTION_INVOCATION_FAILED", content):
        triggers.append("action_failure")
    if re.search(r"GUARDRAIL_NOT_TRIGGERED", content):
        triggers.append("guardrail_failure")
    if re.search(r"ESCALATION_NOT_TRIGGERED", content):
        triggers.append("escalation_failure")

    # Coverage patterns
    if re.search(r"coverage|uncovered", content, re.IGNORECASE):
        triggers.append("coverage")

    # Connected app patterns (for live preview)
    if re.search(r"connectedApp|OAuth|live.*preview", content, re.IGNORECASE):
        triggers.append("connected_app")

    return triggers


def get_suggestions(skill: str, triggers: list[str], config: dict) -> list[dict]:
    """Get skill suggestions based on detected skill and triggers."""
    suggestions = []
    relationships = config.get("relationships", {}).get(skill, {})

    # After creating suggestions
    after_creating = relationships.get("after_creating", [])
    for suggestion in after_creating:
        if suggestion.get("condition") == "always" or any(
            t in triggers for t in suggestion.get("condition", "").split("|")
        ):
            suggestions.append({
                "type": "after",
                "skill": suggestion["skill"],
                "message": suggestion["message"],
                "priority": suggestion.get("priority", 99)
            })

    # Commonly used with (based on triggers)
    commonly_with = relationships.get("commonly_with", [])
    for suggestion in commonly_with:
        trigger_pattern = suggestion.get("trigger", "")
        if trigger_pattern == "always" or any(
            re.search(trigger_pattern, t, re.IGNORECASE) for t in triggers
        ):
            suggestions.append({
                "type": "with",
                "skill": suggestion["skill"],
                "message": suggestion["message"],
                "priority": suggestion.get("priority", 99)
            })

    # Before this suggestions (prerequisites)
    before_this = relationships.get("before_this", [])
    for suggestion in before_this:
        condition = suggestion.get("condition", "")
        if condition == "always" or any(
            re.search(condition, t, re.IGNORECASE) for t in triggers
        ):
            suggestions.append({
                "type": "before",
                "skill": suggestion["skill"],
                "message": suggestion["message"],
                "priority": suggestion.get("priority", 0)
            })

    # Sort by priority and deduplicate
    seen_skills = set()
    unique_suggestions = []
    for s in sorted(suggestions, key=lambda x: x["priority"]):
        if s["skill"] not in seen_skills:
            seen_skills.add(s["skill"])
            unique_suggestions.append(s)

    return unique_suggestions[:MAX_SUGGESTIONS]


def format_suggestions(suggestions: list[dict], current_skill: str) -> str:
    """Format suggestions as readable text."""
    if not suggestions:
        return ""

    lines = [f"\n{'─' * 50}", f"Related Skills (working with {current_skill})", f"{'─' * 50}"]

    type_icons = {
        "before": "PREREQUISITE",
        "after": "NEXT STEP",
        "with": "RELATED"
    }

    for s in suggestions:
        icon = type_icons.get(s["type"], "TIP")
        lines.append(f"{icon}: {s['skill']}")
        lines.append(f"   {s['message']}")

    lines.append(f"{'─' * 50}\n")

    return "\n".join(lines)


def main():
    """Main entry point for the hook."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    # Get file path from tool input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    # For Edit operations, content might be in different fields
    if not content:
        content = tool_input.get("new_string", "")

    if not file_path:
        sys.exit(0)

    # Load relationships config
    config = load_relationships()

    # Detect the skill from file pattern
    current_skill = detect_skill_from_file(file_path, config)
    if not current_skill:
        sys.exit(0)

    # Read full file content if we only have partial content
    if not content or len(content) < 100:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except (FileNotFoundError, IOError):
            pass

    # Detect content triggers
    triggers = detect_content_triggers(file_path, content)

    # Get suggestions
    suggestions = get_suggestions(current_skill, triggers, config)

    if not suggestions:
        sys.exit(0)

    # Format output
    formatted = format_suggestions(suggestions, current_skill)

    # Output as JSON for Claude
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": formatted
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
