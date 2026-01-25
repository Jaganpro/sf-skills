#!/usr/bin/env python3
"""
Skill Enforcement Hook (PreToolUse)
===================================

Enforcing guardrail that BLOCKS editing Salesforce files without
first activating a skill. This ensures sf-skills are used for:
- Real-time validation hooks
- Best practice scoring (150-point, 120-point, etc.)
- Context-specific guidance

BEHAVIOR:
- BLOCK when SF file edit detected without active skill
- Require Claude to invoke the appropriate skill first
- Allow silently if skill was invoked within 5 minutes
- Allow silently for non-SF files

This enforces skill-first workflow for all Salesforce file types.

Input: JSON via stdin with tool_name, tool_input (file_path for Write/Edit)
Output: JSON with decision (allow/block) and message

Installation:
  Add to PreToolUse hooks in install-hooks.py
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

# Configuration
SKILL_TIMEOUT_MINUTES = 5  # Grace period after skill invocation
STATE_FILE = Path("/tmp/sf-skills-active-skill.json")


def save_active_skill(skill_name: str) -> None:
    """Save the currently active skill to state file."""
    state = {
        "active_skill": skill_name,
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass  # Silently fail - don't block on state save errors

# Salesforce file patterns (from validator-dispatcher.py)
SF_FILE_PATTERNS = [
    (r"\.cls$", "sf-apex", "Apex class"),
    (r"\.trigger$", "sf-apex", "Apex trigger"),
    (r"\.flow-meta\.xml$", "sf-flow", "Flow"),
    (r"\.object-meta\.xml$", "sf-metadata", "Custom Object"),
    (r"\.field-meta\.xml$", "sf-metadata", "Custom Field"),
    (r"\.permissionset-meta\.xml$", "sf-metadata", "Permission Set"),
    (r"/lwc/[^/]+/[^/]+\.js$", "sf-lwc", "LWC JavaScript"),
    (r"/lwc/[^/]+/[^/]+\.html$", "sf-lwc", "LWC Template"),
    (r"\.agent$", "sf-ai-agentscript", "Agent Script"),
    (r"\.soql$", "sf-soql", "SOQL Query"),
    (r"\.(namedCredential|externalServiceRegistration)-meta\.xml$", "sf-integration", "Integration"),
]


def get_active_skill() -> Optional[Tuple[str, datetime]]:
    """
    Read the active skill and timestamp from state file.
    Returns (skill_name, timestamp) or None if no active skill.
    """
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                skill = state.get("active_skill")
                timestamp_str = state.get("timestamp")
                if skill and timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    return (skill, timestamp)
    except (json.JSONDecodeError, IOError, ValueError):
        pass
    return None


def is_skill_active() -> Tuple[bool, Optional[str]]:
    """
    Check if a skill was invoked within the timeout period.
    Returns (is_active, skill_name).
    """
    result = get_active_skill()
    if result is None:
        return (False, None)

    skill_name, timestamp = result
    cutoff = datetime.now() - timedelta(minutes=SKILL_TIMEOUT_MINUTES)

    # Ensure both datetimes are naive for comparison (strip timezone if present)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.replace(tzinfo=None)

    if timestamp >= cutoff:
        return (True, skill_name)
    return (False, None)


def match_sf_file(file_path: str) -> Optional[Tuple[str, str, str]]:
    """
    Check if file matches any Salesforce file pattern.
    Returns (pattern, suggested_skill, description) or None.
    """
    for pattern, skill, description in SF_FILE_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            return (pattern, skill, description)
    return None


def format_block_message(file_path: str, suggested_skill: str, file_type: str) -> str:
    """Format the blocking message requiring skill invocation."""
    filename = Path(file_path).name

    # Use ASCII-only characters to avoid JSON encoding issues
    return (
        f"[SF-SKILLS REQUIRED] Cannot edit Salesforce files without activating a skill. "
        f"File: {filename}, Type: {file_type}. "
        f"ACTION: Invoke /{suggested_skill} first, then retry."
    )


def main():
    """Main entry point for the PreToolUse hook."""
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # No input - allow silently
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        sys.exit(0)
    except Exception:
        # Any other error - allow silently
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        sys.exit(0)

    # Get tool information
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Handle case where tool_input might be a string or non-dict
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}
    elif not isinstance(tool_input, dict):
        tool_input = {}

    try:
        _process_hook(tool_name, tool_input)
    except Exception:
        # Catch-all: always output valid JSON
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        sys.exit(0)


def _process_hook(tool_name: str, tool_input: dict) -> None:
    """Process the hook logic. Separated for better error handling."""
    # Detect Skill tool invocation and save state
    if tool_name == "Skill":
        skill_name = tool_input.get("skill", "")
        # Only track sf-skills (skills starting with "sf-")
        if skill_name.startswith("sf-"):
            save_active_skill(skill_name)
        # Always allow Skill tool
        output = {"hookSpecificOutput": {"permissionDecision": "allow"}}
        print(json.dumps(output))
        sys.exit(0)

    # Only check for Write and Edit tools
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        sys.exit(0)

    # Get file path
    file_path = tool_input.get("file_path", "")
    if not file_path:
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        sys.exit(0)

    # Check if this is a Salesforce file
    sf_match = match_sf_file(file_path)
    if sf_match is None:
        # Not a Salesforce file - allow silently
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        sys.exit(0)

    pattern, suggested_skill, file_type = sf_match

    # Check if a skill is currently active
    is_active, active_skill = is_skill_active()

    if is_active:
        # Skill was invoked recently - allow silently
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        sys.exit(0)

    # No active skill - DENY and require skill invocation first
    block_message = format_block_message(file_path, suggested_skill, file_type)

    output = {
        "hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": block_message
        }
    }

    print(json.dumps(output, ensure_ascii=True))
    sys.exit(0)


if __name__ == "__main__":
    main()
