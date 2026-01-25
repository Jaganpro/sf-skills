#!/usr/bin/env python3
"""
Org Preflight Check Hook (SessionStart)
=======================================

Validates Salesforce org connectivity immediately when starting Claude Code.
Runs `sf org display` to check default org status and auth token validity.

OUTPUT EXAMPLE:
═══════════════════════════════════════════════════════════════════════════
📦 SALESFORCE ORG PREFLIGHT
═══════════════════════════════════════════════════════════════════════════

✅ Default org: MyScratchOrg (user@example.com)
✅ Auth status: Valid (expires in 23h)
✅ Instance URL: https://na139.salesforce.com
✅ API version: 65.0

═══════════════════════════════════════════════════════════════════════════

Input: JSON via stdin (SessionStart event data)
Output: JSON with message for display

Installation:
  Add to SessionStart hooks in install-hooks.py
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple


def run_sf_command(args: list) -> Tuple[bool, str, str]:
    """
    Run an sf CLI command and return (success, stdout, stderr).

    Args:
        args: Command arguments (without 'sf' prefix)

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["sf"] + args,
            capture_output=True,
            text=True,
            timeout=15
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except FileNotFoundError:
        return (False, "", "sf CLI not found - install Salesforce CLI")
    except subprocess.TimeoutExpired:
        return (False, "", "Command timed out after 15 seconds")
    except Exception as e:
        return (False, "", str(e))


def get_org_display() -> Dict:
    """
    Get default org information using sf org display.

    Returns:
        Dict with org info or error details
    """
    success, stdout, stderr = run_sf_command(["org", "display", "--json"])

    if not success:
        # Check for common error patterns
        if "No default org" in stderr or "NoDefaultOrgFoundError" in stderr:
            return {"error": "no_default_org"}
        if "ExpiredAccessTokenError" in stderr or "expired" in stderr.lower():
            return {"error": "expired_token"}
        if "RefreshTokenAuthError" in stderr:
            return {"error": "refresh_failed"}
        return {"error": "unknown", "details": stderr}

    try:
        data = json.loads(stdout)
        result = data.get("result", {})
        return {
            "alias": result.get("alias", "N/A"),
            "username": result.get("username", "Unknown"),
            "instance_url": result.get("instanceUrl", "Unknown"),
            "api_version": result.get("apiVersion", "Unknown"),
            "org_id": result.get("id", "Unknown"),
            "access_token": result.get("accessToken"),
            "connected_status": result.get("connectedStatus", "Unknown"),
            "is_scratch": result.get("isScratchOrg", False),
            "is_sandbox": result.get("isSandbox", False),
            "is_dev_hub": result.get("isDevHub", False)
        }
    except json.JSONDecodeError:
        return {"error": "parse_error", "details": stdout}


def check_auth_expiry(org_info: Dict) -> Tuple[str, str]:
    """
    Check if auth token is expired or close to expiring.

    Args:
        org_info: Org display info dict

    Returns:
        Tuple of (status_icon, status_message)
    """
    status = org_info.get("connected_status", "Unknown")

    if status == "Connected":
        return ("✅", "Valid")
    elif status == "RefreshToken":
        return ("✅", "Valid (refresh token)")
    elif status == "Unknown":
        # Token exists but status unclear - probably OK
        if org_info.get("access_token"):
            return ("⚠️", "Token present (verify by running a command)")
        return ("❌", "Unknown status")
    else:
        return ("❌", f"Status: {status}")


def get_org_type_label(org_info: Dict) -> str:
    """Get a human-readable label for the org type."""
    if org_info.get("is_scratch"):
        return "Scratch Org"
    elif org_info.get("is_sandbox"):
        return "Sandbox"
    elif org_info.get("is_dev_hub"):
        return "Dev Hub"
    else:
        return "Production"


def format_preflight_output(org_info: Dict) -> str:
    """
    Format the preflight check output for display.

    Args:
        org_info: Org display info dict

    Returns:
        Formatted string for display
    """
    lines = []

    # Header
    lines.append("")
    lines.append("=" * 70)
    lines.append("SALESFORCE ORG PREFLIGHT")
    lines.append("=" * 70)
    lines.append("")

    # Handle errors
    if "error" in org_info:
        error = org_info["error"]

        if error == "no_default_org":
            lines.append("(!) No default org configured")
            lines.append("")
            lines.append("    To set a default org:")
            lines.append("    sf config set target-org <alias>")
            lines.append("")
            lines.append("    To authenticate a new org:")
            lines.append("    sf org login web --set-default --alias <alias>")

        elif error == "expired_token":
            lines.append("(!) Auth token expired")
            lines.append("")
            lines.append("    Re-authenticate with:")
            lines.append("    sf org login web --alias <alias>")

        elif error == "refresh_failed":
            lines.append("(!) Token refresh failed")
            lines.append("")
            lines.append("    Re-authenticate with:")
            lines.append("    sf org login web --alias <alias>")

        else:
            lines.append(f"(!) Error: {org_info.get('details', 'Unknown error')}")

        lines.append("")
        lines.append("=" * 70)
        lines.append("")
        return "\n".join(lines)

    # Success case - show org details
    alias = org_info.get("alias", "N/A")
    username = org_info.get("username", "Unknown")
    instance_url = org_info.get("instance_url", "Unknown")
    api_version = org_info.get("api_version", "Unknown")
    org_type = get_org_type_label(org_info)

    auth_icon, auth_status = check_auth_expiry(org_info)

    # API version warning
    api_icon = "✅"
    api_note = ""
    try:
        api_float = float(api_version)
        if api_float < 65.0:
            api_icon = "⚠️"
            api_note = " (consider upgrading to 65.0)"
    except (ValueError, TypeError):
        pass

    lines.append(f"✅ Default org: {alias} ({username})")
    lines.append(f"✅ Org type: {org_type}")
    lines.append(f"{auth_icon} Auth status: {auth_status}")
    lines.append(f"✅ Instance URL: {instance_url}")
    lines.append(f"{api_icon} API version: {api_version}{api_note}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point for the hook."""
    # Read input from stdin (SessionStart event)
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    # Perform preflight check
    org_info = get_org_display()

    # Format output
    output_message = format_preflight_output(org_info)

    # Return hook output
    # SessionStart hooks return a message to display
    output = {
        "hookSpecificOutput": {
            "message": output_message
        }
    }

    print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    main()
