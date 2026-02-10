#!/usr/bin/env python3
"""
PermissionRequest Auto-Approval Hook for sf-skills (v4.0)

Implements smart auto-approval based on org type and operation safety.
This reduces user friction for common safe operations while maintaining
security for dangerous ones.

Auto-Approval Matrix:
┌────────────────────────────────────┬────────────┬─────────────────┐
│ Operation                          │ Org Type   │ Decision        │
├────────────────────────────────────┼────────────┼─────────────────┤
│ Read ~/.claude/**                  │ Any        │ AUTO-APPROVE    │
│ Read (other paths)                 │ Any        │ DEFER           │
│ SF read operations (Bash)          │ Any        │ AUTO-APPROVE    │
│ Deploy/test                        │ Scratch    │ AUTO-APPROVE    │
│ Deploy with --dry-run              │ Sandbox    │ AUTO-APPROVE    │
│ Deploy to production               │ Production │ REQUIRE CONFIRM │
│ DELETE, org delete                 │ Any        │ REQUIRE CONFIRM │
│ Force push, reset --hard           │ Any        │ REQUIRE CONFIRM │
└────────────────────────────────────┴────────────┴─────────────────┘

Output Format (PermissionRequest):
{
    "hookSpecificOutput": {
        "hookEventName": "PermissionRequest",
        "autoApprove": true | false,
        "reason": "..."
    }
}

Usage:
Add to .claude/hooks.json:
{
    "hooks": {
        "PermissionRequest": [{
            "matcher": "Bash",
            "hooks": [{
                "type": "command",
                "command": "python3 ./shared/hooks/scripts/auto-approve.py",
                "timeout": 5000
            }]
        }]
    }
}
"""

import json
import os
import re
import select
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


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
SCRIPT_DIR = Path(__file__).parent.parent
REGISTRY_FILE = SCRIPT_DIR / "skills-registry.json"

# Org type detection patterns
PRODUCTION_PATTERNS = [
    r"--target-org\s+(?:prod|production|prd)",
    r"-o\s+(?:prod|production|prd)",
    r"--target-org\s+['\"]?[^'\"]*prod[^'\"]*['\"]?",
]

SCRATCH_ORG_PATTERNS = [
    r"--target-org\s+(?:scratch|dev|test|feature)",
    r"-o\s+(?:scratch|dev|test|feature)",
    r"scratch\s*org",
]

SANDBOX_PATTERNS = [
    r"--target-org\s+(?:sandbox|sbx|uat|qa|staging)",
    r"-o\s+(?:sandbox|sbx|uat|qa|staging)",
]

# =============================================================================
# SAFE OPERATIONS (AUTO-APPROVE)
# =============================================================================

SAFE_READ_OPERATIONS = [
    # Org information
    r"sf\s+org\s+display",
    r"sf\s+org\s+list",
    r"sf\s+org\s+open",
    r"sf\s+config\s+(get|list)",

    # Data queries (read-only)
    r"sf\s+data\s+query",
    r"sf\s+data\s+get\s+record",
    r"sf\s+data\s+export",

    # Metadata retrieval
    r"sf\s+project\s+retrieve",
    r"sf\s+project\s+generate",
    r"sf\s+sobject\s+(describe|list)",

    # Package information
    r"sf\s+package\s+(list|installed\s+list|version\s+list)",

    # Limits and status
    r"sf\s+limits\s+api\s+display",
    r"sf\s+org\s+list\s+limits",

    # Code analysis (local)
    r"sf\s+apex\s+get\s+log",
    r"sf\s+lightning\s+lint",

    # Source status
    r"sf\s+project\s+list\s+ignored",
    r"sf\s+source\s+status",

    # Debug logs
    r"sf\s+apex\s+log\s+(get|list|tail)",

    # Help and version
    r"sf\s+--help",
    r"sf\s+--version",
    r"sf\s+\w+\s+--help",
]

SAFE_SCRATCH_OPERATIONS = [
    # Deploy to scratch org
    r"sf\s+project\s+deploy\s+start",
    r"sf\s+project\s+deploy\s+preview",

    # Run tests
    r"sf\s+apex\s+run\s+test",
    r"sf\s+apex\s+test\s+run",

    # Execute anonymous apex
    r"sf\s+apex\s+run",

    # Data operations
    r"sf\s+data\s+(create|update|upsert|delete)",

    # Package install (scratch only)
    r"sf\s+package\s+install",

    # Alias management
    r"sf\s+alias\s+(set|unset)",

    # Agent operations
    r"sf\s+agent\s+(?:generate|preview)",
]

SAFE_WITH_DRYRUN = [
    # Deploy with validation flag
    r"sf\s+project\s+deploy.*--(?:dry-run|check-only)",
    r"sf\s+project\s+deploy\s+preview",
]

# =============================================================================
# DANGEROUS OPERATIONS (REQUIRE CONFIRM)
# =============================================================================

DANGEROUS_OPERATIONS = [
    # Destructive operations
    (r"sf\s+org\s+delete", "Org deletion - permanent and irreversible"),
    (r"sf\s+data\s+delete.*--hard-delete", "Hard delete - bypasses recycle bin"),
    (r"sf\s+project\s+deploy.*--(?:purge-on-delete|destructive)", "Destructive deployment"),

    # Production deploys without safety flags
    # NOTE: Only matches if --target-org contains prod/production AND no dry-run
    # Scratch/sandbox/dev orgs are handled separately and auto-approved
    (r"sf\s+project\s+deploy\s+start(?=.*--target-org\s+(?:prod|production))(?!.*--(?:dry-run|check-only))", "Production deploy without validation"),

    # Agent publish (production)
    (r"sf\s+agent\s+publish", "Publishing agent to production"),

    # Git destructive operations
    (r"git\s+push\s+(?:--force|-f)", "Force push - can destroy remote history"),
    (r"git\s+reset\s+--hard", "Hard reset - discards uncommitted changes"),
    (r"git\s+clean\s+-f", "Force clean - removes untracked files"),
    (r"git\s+branch\s+-D", "Force delete branch"),

    # Mass data operations
    (r"sf\s+data\s+(?:delete|update).*(?:--bulk|--batch)", "Bulk data modification"),
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_registry() -> dict:
    """Load auto-approval policy from registry if available."""
    try:
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, 'r') as f:
                registry = json.load(f)
                return registry.get("auto_approve_policy", {})
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def detect_org_type(command: str) -> str:
    """Detect the org type from the command."""
    command_lower = command.lower()

    # Check for production indicators
    for pattern in PRODUCTION_PATTERNS:
        if re.search(pattern, command_lower):
            return "production"

    # Check for scratch org indicators
    for pattern in SCRATCH_ORG_PATTERNS:
        if re.search(pattern, command_lower):
            return "scratch"

    # Check for sandbox indicators
    for pattern in SANDBOX_PATTERNS:
        if re.search(pattern, command_lower):
            return "sandbox"

    # Default to unknown (treated as sandbox)
    return "unknown"


def is_safe_read_operation(command: str) -> bool:
    """Check if this is a safe read-only operation."""
    for pattern in SAFE_READ_OPERATIONS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def is_safe_scratch_operation(command: str) -> bool:
    """Check if this is safe for scratch org execution."""
    for pattern in SAFE_SCRATCH_OPERATIONS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def is_safe_with_dryrun(command: str) -> bool:
    """Check if this is safe because it has dry-run/check-only flag."""
    for pattern in SAFE_WITH_DRYRUN:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def is_dangerous_operation(command: str) -> Tuple[bool, str]:
    """Check if this is a dangerous operation that requires confirmation."""
    for pattern, reason in DANGEROUS_OPERATIONS:
        if re.search(pattern, command, re.IGNORECASE):
            return (True, reason)
    return (False, "")


def is_sf_command(command: str) -> bool:
    """Check if this is an SF CLI command."""
    return bool(re.match(r"^\s*(?:sf|sfdx)\s+", command, re.IGNORECASE))


def decide_approval(command: str) -> Tuple[bool, str]:
    """
    Decide whether to auto-approve or require confirmation.
    Returns (auto_approve: bool, reason: str)
    """
    # Only process SF/SFDX and git commands
    is_sf = is_sf_command(command)
    is_git = bool(re.match(r"^\s*git\s+", command, re.IGNORECASE))

    if not is_sf and not is_git:
        # Non-SF commands: don't auto-approve, let default behavior handle it
        return (False, "Not an SF/SFDX command - deferring to default permission handling")

    # Check dangerous operations first (always require confirmation)
    is_dangerous, danger_reason = is_dangerous_operation(command)
    if is_dangerous:
        return (False, f"⚠️  Requires confirmation: {danger_reason}")

    # Safe read operations - always auto-approve
    if is_safe_read_operation(command):
        return (True, "✅ Safe read-only operation")

    # Commands with dry-run/check-only - auto-approve
    if is_safe_with_dryrun(command):
        return (True, "✅ Validation mode (--dry-run/--check-only)")

    # Detect org type
    org_type = detect_org_type(command)

    # Scratch org operations - auto-approve safe operations
    if org_type == "scratch" and is_safe_scratch_operation(command):
        return (True, "✅ Safe scratch org operation")

    # Production - always require confirmation for write operations
    if org_type == "production":
        return (False, "⚠️  Production org - requires confirmation")

    # Sandbox with safe operations - auto-approve
    if org_type in ("sandbox", "unknown") and is_safe_scratch_operation(command):
        return (True, f"✅ Safe {org_type} org operation")

    # Default: don't auto-approve, require confirmation
    return (False, "Operation requires confirmation")


def format_decision(auto_approve: bool, reason: str, command: str) -> str:
    """Format the decision for logging/display."""
    status = "AUTO-APPROVED" if auto_approve else "REQUIRES CONFIRMATION"
    icon = "✅" if auto_approve else "⚠️"

    # Truncate command for display
    cmd_display = command[:60] + "..." if len(command) > 60 else command

    return f"""
{'─' * 50}
{icon} {status}
{'─' * 50}
Command: {cmd_display}
Reason:  {reason}
{'─' * 50}
"""


# =============================================================================
# MAIN HOOK LOGIC
# =============================================================================

def main():
    """Main entry point for PermissionRequest hook."""
    # Read hook input from stdin with timeout to prevent blocking
    input_data = read_stdin_safe(timeout_seconds=0.1)
    if not input_data:
        # No input - don't auto-approve
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "autoApprove": False,
                "reason": "No input received"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # Get tool info
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Handle Read tool — auto-approve reads to ~/.claude/
    if tool_name == "Read":
        file_path = tool_input.get("file_path", "")
        claude_dir = os.path.expanduser("~/.claude/")
        if file_path.startswith(claude_dir):
            auto_approve = True
            reason = "✅ Safe read of ~/.claude/ configuration"
        else:
            auto_approve = False
            reason = "Read outside ~/.claude/ — deferring to default permission handling"
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "autoApprove": auto_approve,
                "reason": reason
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # Only process Bash commands
    if tool_name != "Bash":
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "autoApprove": False,
                "reason": f"Not a Bash command (got: {tool_name})"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # Get the command
    command = tool_input.get("command", "")
    if not command:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "autoApprove": False,
                "reason": "Empty command"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # Make the decision
    auto_approve, reason = decide_approval(command)

    # Format additional context for logging
    additional_context = format_decision(auto_approve, reason, command)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "autoApprove": auto_approve,
            "reason": reason,
            "additionalContext": additional_context
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
