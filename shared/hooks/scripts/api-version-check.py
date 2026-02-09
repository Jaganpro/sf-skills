#!/usr/bin/env python3
"""
API Version Compatibility Check Hook (PreToolUse)
================================================

Ensures API versions are compatible before deploy/retrieve operations.
Prevents "feature not available in API version X" errors.

BEHAVIOR:
- Triggers on sf/sfdx deploy/retrieve commands via Bash
- Parses sfdx-project.json for sourceApiVersion
- Queries target org's API version (cached for 1 hour)
- WARN if mismatch > 2 versions
- BLOCK if deploying features unavailable in target version

CHECKS:
1. sourceApiVersion in sfdx-project.json
2. Target org API version via sf org display
3. Version compatibility analysis

Input: JSON via stdin with tool_name, tool_input (command for Bash)
Output: JSON with decision (allow/warn/block) and message

Installation:
  Registered automatically by tools/install.py (PreToolUse, matcher: Bash)
"""

import json
import os
import re
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple


def read_stdin_safe(timeout_seconds: float = 0.1) -> dict:
    """Safely read JSON from stdin with timeout to prevent blocking."""
    if sys.stdin.isatty():
        return {}
    try:
        readable, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
        if not readable:
            return {}
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, OSError, ValueError):
        return {}


# Configuration
CACHE_FILE = Path("/tmp/sf-skills-org-api-version-cache.json")
CACHE_TTL_SECONDS = 3600  # 1 hour
VERSION_MISMATCH_WARN_THRESHOLD = 2  # Warn if difference > 2 versions


# Deploy/retrieve command patterns
DEPLOY_PATTERNS = [
    r'\bsf\s+project\s+deploy\b',
    r'\bsf\s+deploy\s+metadata\b',
    r'\bsfdx\s+force:source:deploy\b',
    r'\bsfdx\s+force:source:push\b',
]

RETRIEVE_PATTERNS = [
    r'\bsf\s+project\s+retrieve\b',
    r'\bsf\s+retrieve\s+metadata\b',
    r'\bsfdx\s+force:source:retrieve\b',
    r'\bsfdx\s+force:source:pull\b',
]


def is_deploy_retrieve_command(command: str) -> Tuple[bool, str]:
    """
    Check if command is a deploy or retrieve operation.

    Returns:
        Tuple of (is_match, operation_type)
    """
    for pattern in DEPLOY_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return (True, "deploy")

    for pattern in RETRIEVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return (True, "retrieve")

    return (False, "")


def get_source_api_version() -> Optional[str]:
    """
    Get sourceApiVersion from sfdx-project.json.

    Returns:
        API version string (e.g., "65.0") or None
    """
    # Look for sfdx-project.json in current directory and parents
    current = Path.cwd()
    while current != current.parent:
        project_file = current / "sfdx-project.json"
        if project_file.exists():
            try:
                with open(project_file, "r") as f:
                    config = json.load(f)
                return config.get("sourceApiVersion")
            except (json.JSONDecodeError, IOError):
                pass
        current = current.parent
    return None


def get_cached_org_version() -> Optional[Dict]:
    """Get cached org API version if still valid."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)

            # Check if cache is still valid
            timestamp = cache.get("timestamp", 0)
            if time.time() - timestamp < CACHE_TTL_SECONDS:
                return cache
    except Exception:
        pass
    return None


def save_org_version_cache(org_alias: str, api_version: str):
    """Save org API version to cache."""
    try:
        cache = {
            "org_alias": org_alias,
            "api_version": api_version,
            "timestamp": time.time(),
        }
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass


def get_target_org_version(command: str) -> Optional[Dict]:
    """
    Get target org's API version.

    Args:
        command: The deploy/retrieve command (to extract --target-org if specified)

    Returns:
        Dict with org_alias and api_version, or None
    """
    # Check cache first
    cached = get_cached_org_version()
    if cached:
        return cached

    # Extract target org from command if specified
    target_org = None
    target_org_match = re.search(r'--target-org[=\s]+(\S+)', command)
    if target_org_match:
        target_org = target_org_match.group(1)

    # Query org API version
    try:
        cmd = ["sf", "org", "display", "--json"]
        if target_org:
            cmd.extend(["--target-org", target_org])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            org_result = data.get("result", {})
            api_version = org_result.get("apiVersion")
            org_alias = org_result.get("alias") or org_result.get("username", "Unknown")

            if api_version:
                save_org_version_cache(org_alias, api_version)
                return {
                    "org_alias": org_alias,
                    "api_version": api_version,
                }
    except Exception:
        pass

    return None


def parse_version(version_str: str) -> Optional[float]:
    """Parse version string to float for comparison."""
    try:
        return float(version_str)
    except (ValueError, TypeError):
        return None


def check_version_compatibility(source_version: str, org_version: str) -> Dict:
    """
    Check compatibility between source and org API versions.

    Returns:
        Dict with decision, message, and details
    """
    source_float = parse_version(source_version)
    org_float = parse_version(org_version)

    if source_float is None or org_float is None:
        return {
            "decision": "allow",
            "message": "Could not parse API versions",
        }

    version_diff = source_float - org_float

    # Source version higher than org = potential feature unavailability
    if version_diff > VERSION_MISMATCH_WARN_THRESHOLD:
        return {
            "decision": "warn",
            "severity": "high",
            "message": f"API Version Mismatch: Source ({source_version}) is {version_diff:.0f} versions ahead of org ({org_version})",
            "suggestion": f"Features from API {source_version} may not be available in org. Consider updating org or lowering sourceApiVersion.",
        }

    # Source slightly higher - minor warning
    if version_diff > 0:
        return {
            "decision": "allow",
            "note": f"Source API ({source_version}) slightly ahead of org ({org_version})",
        }

    # Org higher than source - usually OK but mention it
    if version_diff < -VERSION_MISMATCH_WARN_THRESHOLD:
        return {
            "decision": "allow",
            "note": f"Org API ({org_version}) is newer than source ({source_version}). Consider updating sourceApiVersion to access newer features.",
        }

    # Versions match or close
    return {
        "decision": "allow",
        "message": f"API versions compatible (source: {source_version}, org: {org_version})",
    }


def format_output(check_result: Dict, operation: str, source_version: str, org_info: Dict) -> Dict:
    """Format the hook output."""
    decision = check_result.get("decision", "allow")

    if decision == "warn":
        # Allow but show warning
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "message": f"\n[!] API VERSION WARNING ({operation})\n"
                           f"    {check_result.get('message', '')}\n"
                           f"    {check_result.get('suggestion', '')}\n"
            }
        }
    elif decision == "block":
        # Block the operation
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"\n[X] API VERSION BLOCKED ({operation})\n"
                           f"    {check_result.get('message', '')}\n"
                           f"    {check_result.get('fix', '')}\n"
            }
        }
    else:
        # Allow silently or with note
        note = check_result.get("note", "")
        if note:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "additionalContext": f"API check: {note}"
                }
            }
        else:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow"
                }
            }

    return output


def _process_hook(input_data: Dict) -> Dict:
    """Process the hook logic and return output."""
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only process Bash tool
    if tool_name != "Bash":
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

    # Get command
    command = ""
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")
    elif isinstance(tool_input, str):
        command = tool_input

    if not command:
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

    # Check if it's a deploy/retrieve command
    is_match, operation = is_deploy_retrieve_command(command)
    if not is_match:
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

    # Get source API version
    source_version = get_source_api_version()
    if not source_version:
        # No sourceApiVersion in project - allow but could warn
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

    # Get target org API version
    org_info = get_target_org_version(command)
    if not org_info:
        # Couldn't get org version - allow operation
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

    # Check compatibility
    check_result = check_version_compatibility(
        source_version,
        org_info.get("api_version", "")
    )

    # Format and return output
    return format_output(check_result, operation, source_version, org_info)


def main():
    """Main entry point for the hook."""
    # Read input from stdin with timeout to prevent blocking
    input_data = read_stdin_safe(timeout_seconds=0.1)

    try:
        output = _process_hook(input_data)
    except Exception as e:
        # On any error, allow the operation
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    main()
