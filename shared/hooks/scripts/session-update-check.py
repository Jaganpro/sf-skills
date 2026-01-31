#!/usr/bin/env python3
"""
Session Update Check Hook (SessionStart - First)
=================================================

Checks for sf-skills updates on session start with minimal latency impact.
Uses a 24-hour cache to avoid repeated network calls.

BEHAVIOR:
1. Check if cache is fresh (< 24 hours) → exit immediately (no network)
2. Fetch latest release from GitHub API (3-second timeout)
3. Compare with ~/.claude/sf-skills-hooks/VERSION
4. If outdated:
   a. git fetch --tags in marketplace directory
   b. git checkout <latest-tag>
   c. rsync shared/hooks/ → ~/.claude/sf-skills-hooks/
   d. Write new VERSION file
5. Verify hooks in ~/.claude/settings.json (update if needed)
6. Update .last-update-check timestamp

CONSTRAINTS:
- 5-second total timeout (non-blocking)
- Silent output (no stdout except update notifications)
- Graceful offline fallback
- Uses existing session-init.py patterns

Input: JSON via stdin (SessionStart event data)
Output: Silent on no updates, brief message on update success

Installation:
  This hook should run FIRST in SessionStart sequence, before session-init.py
"""

import json
import os
import select
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def read_stdin_safe(timeout_seconds: float = 0.1) -> dict:
    """
    Safely read JSON from stdin with timeout.

    Returns empty dict if:
    - stdin is a TTY (interactive terminal)
    - No data available within timeout
    - JSON parsing fails

    This prevents blocking when Claude Code doesn't pipe data.
    """
    # Skip if running interactively
    if sys.stdin.isatty():
        return {}

    try:
        # Use select to check if stdin has data (Unix only)
        readable, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
        if not readable:
            return {}

        # Read and parse
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, OSError, ValueError):
        return {}

# ============================================================================
# CONFIGURATION
# ============================================================================

# Where hooks are installed for global use
HOOKS_DIR = Path.home() / ".claude" / "sf-skills-hooks"
VERSION_FILE = HOOKS_DIR / "VERSION"
CACHE_FILE = HOOKS_DIR / ".last-update-check"

# GitHub API endpoint for latest release
GITHUB_OWNER = "Jaganpro"
GITHUB_REPO = "sf-skills"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

# Marketplace clone location (installed by Claude Code plugin system)
MARKETPLACE_DIR = Path.home() / ".claude" / "plugins" / "marketplaces" / "sf-skills"

# Timeouts
CACHE_DURATION_HOURS = 24
NETWORK_TIMEOUT_SECONDS = 3
TOTAL_TIMEOUT_SECONDS = 5

# Global hooks.json template (with absolute paths)
GLOBAL_HOOKS_TEMPLATE = {
    "hooks": {
        "SessionStart": [
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/session-update-check.py",
                    "timeout": 10000,
                    "async": True
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/session-init.py",
                    "timeout": 3000
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/org-preflight.py",
                    "timeout": 30000,
                    "async": True
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/lsp-prewarm.py",
                    "timeout": 60000,
                    "async": True
                }],
                "_sf_skills": True
            }
        ],
        "UserPromptSubmit": [
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/skill-activation-prompt.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ],
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"python3 {HOOKS_DIR}/scripts/guardrails.py",
                        "timeout": 5000
                    },
                    {
                        "type": "command",
                        "command": f"python3 {HOOKS_DIR}/scripts/api-version-check.py",
                        "timeout": 10000
                    }
                ],
                "_sf_skills": True
            },
            {
                "matcher": "Write|Edit",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/skill-enforcement.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            },
            {
                "matcher": "Skill",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/skill-enforcement.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ],
        "PostToolUse": [
            {
                "matcher": "Write|Edit",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"python3 {HOOKS_DIR}/scripts/validator-dispatcher.py",
                        "timeout": 10000
                    },
                    {
                        "type": "command",
                        "command": f"python3 {HOOKS_DIR}/suggest-related-skills.py",
                        "timeout": 5000
                    }
                ],
                "_sf_skills": True
            }
        ],
        "PermissionRequest": [
            {
                "matcher": "Bash",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/auto-approve.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ],
        "SubagentStop": [
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {HOOKS_DIR}/scripts/chain-validator.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ]
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_cache_fresh() -> bool:
    """Check if the update cache is still fresh (< 24 hours old)."""
    if not CACHE_FILE.exists():
        return False

    try:
        cache_time = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime)
        age = datetime.now() - cache_time
        return age < timedelta(hours=CACHE_DURATION_HOURS)
    except (OSError, ValueError):
        return False


def update_cache_timestamp():
    """Update the cache file timestamp to mark a successful check."""
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.touch()


def get_current_version() -> Optional[str]:
    """Read the current installed version from VERSION file."""
    if not VERSION_FILE.exists():
        return None

    try:
        return VERSION_FILE.read_text().strip()
    except (OSError, IOError):
        return None


def fetch_latest_release() -> Optional[str]:
    """
    Fetch the latest release tag from GitHub API.

    Returns the tag name (e.g., "v1.2.0") or None if unavailable.
    """
    try:
        request = Request(
            GITHUB_API_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "sf-skills-update-checker"
            }
        )

        with urlopen(request, timeout=NETWORK_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("tag_name")

    except (URLError, HTTPError, json.JSONDecodeError, KeyError, TimeoutError):
        # Network unavailable or API error - fail gracefully
        return None


def version_compare(v1: str, v2: str) -> int:
    """
    Compare two semantic version strings.

    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
    """
    def normalize(v: str) -> Tuple[int, ...]:
        # Remove 'v' prefix if present and split into parts
        v = v.lstrip('v')
        parts = v.split('.')
        # Pad with zeros and convert to integers
        return tuple(int(p) for p in parts[:3] + ['0'] * (3 - len(parts)))

    try:
        v1_parts = normalize(v1)
        v2_parts = normalize(v2)

        if v1_parts < v2_parts:
            return -1
        elif v1_parts > v2_parts:
            return 1
        return 0
    except (ValueError, AttributeError):
        return 0


def git_update_to_tag(tag: str) -> bool:
    """
    Update the marketplace git clone to a specific tag.

    Returns True on success, False on failure.
    """
    if not MARKETPLACE_DIR.exists():
        return False

    try:
        # Fetch tags from origin
        subprocess.run(
            ["git", "fetch", "--tags", "--quiet"],
            cwd=MARKETPLACE_DIR,
            capture_output=True,
            timeout=10,
            check=True
        )

        # Checkout the specific tag
        subprocess.run(
            ["git", "checkout", tag, "--quiet"],
            cwd=MARKETPLACE_DIR,
            capture_output=True,
            timeout=5,
            check=True
        )

        return True

    except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def sync_hooks_to_global() -> bool:
    """
    Rsync the shared/hooks/ directory to ~/.claude/sf-skills-hooks/.

    Returns True on success, False on failure.
    """
    source_dir = MARKETPLACE_DIR / "shared" / "hooks"

    if not source_dir.exists():
        return False

    try:
        HOOKS_DIR.mkdir(parents=True, exist_ok=True)

        # Use rsync for efficient sync (preserves timestamps, handles deletions)
        result = subprocess.run(
            [
                "rsync", "-a", "--delete",
                f"{source_dir}/",
                f"{HOOKS_DIR}/"
            ],
            capture_output=True,
            timeout=10
        )

        return result.returncode == 0

    except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback to shutil if rsync not available
        try:
            if HOOKS_DIR.exists():
                shutil.rmtree(HOOKS_DIR)
            shutil.copytree(source_dir, HOOKS_DIR)
            return True
        except (OSError, shutil.Error):
            return False


def write_version(version: str) -> bool:
    """Write the VERSION file with the current version."""
    try:
        HOOKS_DIR.mkdir(parents=True, exist_ok=True)
        VERSION_FILE.write_text(version + "\n")
        return True
    except (OSError, IOError):
        return False


def is_sf_skills_hook(hook: dict) -> bool:
    """Check if a hook was installed by sf-skills."""
    if hook.get("_sf_skills"):
        return True

    # Check command path
    for nested in hook.get("hooks", []):
        command = nested.get("command", "")
        if "sf-skills" in command or "sf-skills-hooks" in command:
            return True

    return False


def ensure_global_hooks_in_settings() -> bool:
    """
    Ensure ~/.claude/settings.json contains sf-skills hooks.

    NOTE: Claude Code does NOT support a separate hooks.json file.
    All hooks must be in settings.json under the "hooks" key.

    Merges with existing user hooks without overwriting them.
    Returns True if settings.json is valid, False on error.
    """
    settings_path = Path.home() / ".claude" / "settings.json"

    try:
        # Load existing settings.json if it exists
        existing = {}
        if settings_path.exists():
            try:
                existing = json.loads(settings_path.read_text())
            except json.JSONDecodeError:
                existing = {}

        if "hooks" not in existing:
            existing["hooks"] = {}

        # For each event type in our template, merge hooks
        for event_name, template_hooks in GLOBAL_HOOKS_TEMPLATE["hooks"].items():
            if event_name not in existing["hooks"]:
                existing["hooks"][event_name] = []

            # Filter out old sf-skills hooks
            non_sf_hooks = [
                h for h in existing["hooks"][event_name]
                if not is_sf_skills_hook(h)
            ]

            # Add new sf-skills hooks
            existing["hooks"][event_name] = non_sf_hooks + template_hooks

        # Write back
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(existing, indent=2) + "\n")

        return True

    except (OSError, IOError):
        return False


def perform_update(current_version: str, latest_version: str) -> bool:
    """
    Perform the full update sequence.

    Returns True on success, False on failure.
    """
    # Step 1: Git update to the new tag
    if not git_update_to_tag(latest_version):
        return False

    # Step 2: Sync hooks to global location
    if not sync_hooks_to_global():
        return False

    # Step 3: Write new VERSION file
    if not write_version(latest_version):
        return False

    # Step 4: Ensure settings.json hooks are up to date
    ensure_global_hooks_in_settings()

    return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    """
    Main entry point for the update check hook.

    This hook runs FIRST in the SessionStart sequence to check for updates
    before other hooks run. It must be fast and non-blocking.
    """
    start_time = time.time()

    # Read input from stdin (SessionStart event data) - with timeout to prevent blocking
    input_data = read_stdin_safe(timeout_seconds=0.1)

    # Check 1: Is cache fresh? If so, exit immediately (most common path)
    if is_cache_fresh():
        sys.exit(0)

    # Check 2: Enforce total timeout
    def check_timeout():
        if time.time() - start_time > TOTAL_TIMEOUT_SECONDS:
            update_cache_timestamp()  # Don't retry immediately
            sys.exit(0)

    # Check 3: Get current version
    current_version = get_current_version()
    check_timeout()

    # Check 4: Fetch latest release from GitHub
    latest_version = fetch_latest_release()
    check_timeout()

    if not latest_version:
        # Network unavailable - update cache to avoid retries and exit
        update_cache_timestamp()
        sys.exit(0)

    # Check 5: Compare versions
    if current_version:
        comparison = version_compare(current_version, latest_version)
        if comparison >= 0:
            # Current version is up to date or newer
            update_cache_timestamp()
            sys.exit(0)

    # Check 6: Perform update
    check_timeout()

    if perform_update(current_version or "unknown", latest_version):
        # Output brief success message (only time we output anything)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"✅ sf-skills updated {current_version or 'initial'} → {latest_version}"
            }
        }
        print(json.dumps(output))

    # Update cache regardless of success (to avoid repeated failed attempts)
    update_cache_timestamp()
    sys.exit(0)


if __name__ == "__main__":
    main()
