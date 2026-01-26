#!/usr/bin/env python3
"""
Session Init Hook (SessionStart - Synchronous)
===============================================

Initializes session directory and cleans up stale sessions.
This hook runs SYNCHRONOUSLY before async hooks to ensure the session
directory exists before org-preflight.py and lsp-prewarm.py write to it.

BEHAVIOR:
1. Gets Claude Code's PID (parent process)
2. Cleans up session directories for dead processes
3. Creates ~/.claude/sessions/{PID}/ directory
4. Writes session.json marker with timestamp

The PID-keyed session directory enables:
- Multi-session isolation (each Claude Code gets its own state)
- Automatic stale session detection (statusline checks if PID is alive)
- Clean exit behavior (dead PIDs get cleaned up on next start)

Input: JSON via stdin (SessionStart event data)
Output: Silent (no stdout to avoid JSON validation issues)

Installation:
  Add to SessionStart hooks in install-hooks.py (BEFORE async hooks)
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


# Session directory base
SESSIONS_DIR = Path.home() / ".claude" / "sessions"


def is_pid_alive(pid: int) -> bool:
    """
    Check if a process is still running.

    Uses signal 0 which doesn't actually send a signal but checks
    if the process exists and we have permission to signal it.
    """
    try:
        os.kill(pid, 0)  # Signal 0 = check existence
        return True
    except (OSError, ProcessLookupError):
        return False
    except PermissionError:
        # Process exists but we can't signal it (different user)
        return True


def cleanup_old_sessions():
    """
    Remove session directories for dead processes.

    Iterates through ~/.claude/sessions/ and removes any directory
    whose name is a PID that is no longer running.
    """
    if not SESSIONS_DIR.exists():
        return

    for session_dir in SESSIONS_DIR.iterdir():
        if not session_dir.is_dir():
            continue
        try:
            pid = int(session_dir.name)
            if not is_pid_alive(pid):
                # Process is dead, clean up its session directory
                shutil.rmtree(session_dir, ignore_errors=True)
        except ValueError:
            # Directory name is not a valid PID, skip it
            pass


def main():
    """
    Main entry point for the hook.

    This hook is SYNCHRONOUS and runs FIRST in the SessionStart sequence.
    It must complete before async hooks (org-preflight, lsp-prewarm) run
    so they have a session directory to write to.
    """
    # Read input from stdin (SessionStart event data)
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    # Get Claude Code's PID (our parent process)
    # Note: This hook runs as a child of Claude Code, so getppid() gives us
    # the Claude Code process ID
    pid = os.getppid()

    # Clean up old sessions first (dead PIDs)
    cleanup_old_sessions()

    # Create this session's directory
    session_dir = SESSIONS_DIR / str(pid)
    session_dir.mkdir(parents=True, exist_ok=True)

    # Write session marker with timestamp
    # This timestamp is used by statusline to determine if state files are "fresh"
    state = {
        "timestamp": datetime.now().isoformat(),
        "pid": pid
    }
    with open(session_dir / "session.json", 'w') as f:
        json.dump(state, f, indent=2)

    # SILENT: No stdout output to avoid JSON validation errors
    sys.exit(0)


if __name__ == "__main__":
    main()
