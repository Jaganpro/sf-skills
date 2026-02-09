#!/usr/bin/env python3
"""
LSP Prewarm Hook (SessionStart)
===============================

Spawns LSP servers in background immediately on session start to eliminate
cold start delays during first validation. Each server receives an initialize
handshake and stays running for quick first-use response.

BEHAVIOR:
- Spawns Apex, LWC, and AgentScript LSP servers in background
- Sends LSP initialize handshake to prime each server
- Stores PIDs in /tmp/sf-skills-lsp-pids.json for cleanup
- Servers auto-terminate after 10 minutes of inactivity
- Reports which servers were successfully prewarm'd

EXPECTED BENEFIT:
- First validation instant (<1s) instead of 5-10s cold start
- Particularly helps Apex LSP which needs JVM warmup

Input: JSON via stdin (SessionStart event data)
Output: JSON with message showing prewarm status

Installation:
  Registered automatically by tools/install.py (SessionStart, async)

Prerequisites:
- VS Code Salesforce Extension Pack (for Apex/LWC LSPs)
- Java 11+ (for Apex LSP)
- agentscript-langserver npm package (for AgentScript LSP)
"""

import json
import os
import select
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


def find_sfdx_project_root() -> Optional[Path]:
    """Walk up from CWD looking for sfdx-project.json."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "sfdx-project.json").exists():
            return current
        current = current.parent
    return None


# Configuration
PID_FILE = Path("/tmp/sf-skills-lsp-pids.json")
PREWARM_TIMEOUT = 10  # Max seconds to wait for each server init
MODULE_DIR = Path(__file__).parent.parent.parent / "lsp-engine"

# Session directory and state file (PID-keyed for multi-session support)
# The session directory is created by session-init.py which runs synchronously first
SESSION_PID = os.getppid()
SESSION_DIR = Path.home() / ".claude" / "sessions" / str(SESSION_PID)
STATE_FILE = SESSION_DIR / "lsp-state.json"


# LSP Server configurations
LSP_SERVERS = {
    "apex": {
        "name": "Apex Language Server",
        "wrapper": "apex_wrapper.sh",
        "requires_java": True,
        "warm_time": 5,  # Apex/Java needs more warmup time
    },
    "lwc": {
        "name": "LWC Language Server",
        "wrapper": "lwc_wrapper.sh",
        "requires_java": False,
        "warm_time": 2,
    },
    "agentscript": {
        "name": "Agent Script Language Server",
        "wrapper": "agentscript_wrapper.sh",
        "requires_java": False,
        "warm_time": 2,
    },
}


def find_wrapper(wrapper_name: str) -> Optional[Path]:
    """Find the LSP wrapper script."""
    wrapper_path = MODULE_DIR / wrapper_name
    if wrapper_path.exists() and os.access(wrapper_path, os.X_OK):
        return wrapper_path
    return None


def find_java_binary() -> Optional[str]:
    """Find Java binary, checking Homebrew paths first (same logic as apex_wrapper.sh)."""
    # Prioritize Homebrew OpenJDK over /usr/local/bin/java which may be a stub
    candidates = [
        "/opt/homebrew/opt/openjdk@21/bin/java",
        "/opt/homebrew/opt/openjdk@17/bin/java",
        "/opt/homebrew/opt/openjdk@11/bin/java",
        "/opt/homebrew/opt/openjdk/bin/java",
        str(Path.home() / ".sdkman/candidates/java/current/bin/java"),
        "/usr/bin/java",
        "/usr/local/bin/java",  # Last - may be Salesforce stub
    ]
    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def check_java_available() -> bool:
    """Check if Java 11+ is available."""
    java_bin = find_java_binary()
    if not java_bin:
        return False

    try:
        result = subprocess.run(
            [java_bin, "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Java outputs version to stderr
        version_output = result.stderr or result.stdout
        return "version" in version_output.lower()
    except Exception:
        return False


def spawn_lsp_server(server_id: str, config: Dict) -> Tuple[bool, str, Optional[int]]:
    """
    Spawn an LSP server in background with initialize handshake.

    Args:
        server_id: Server identifier (apex, lwc, agentscript)
        config: Server configuration dict

    Returns:
        Tuple of (success, message, pid)
    """
    wrapper_path = find_wrapper(config["wrapper"])
    if not wrapper_path:
        return (False, f"Wrapper not found: {config['wrapper']}", None)

    # Check Java requirement
    if config.get("requires_java") and not check_java_available():
        return (False, "Java 11+ not available", None)

    try:
        # Start the LSP server
        process = subprocess.Popen(
            [str(wrapper_path), "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            start_new_session=True,  # Detach from parent
        )

        # Send initialize request
        init_params = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "processId": os.getpid(),
                "rootUri": f"file://{os.getcwd()}",
                "capabilities": {
                    "textDocument": {"publishDiagnostics": {}},
                }
            }
        }
        content = json.dumps(init_params).encode("utf-8")
        header = f"Content-Length: {len(content)}\r\n\r\n".encode("utf-8")

        try:
            process.stdin.write(header + content)
            process.stdin.flush()
        except BrokenPipeError:
            return (False, "Server exited immediately", None)

        # Wait briefly for server to initialize
        time.sleep(config.get("warm_time", 2))

        # Check if still running
        if process.poll() is not None:
            # Process exited - read stderr for error
            stderr = process.stderr.read().decode("utf-8", errors="replace")[:200]
            return (False, f"Server exited: {stderr}", None)

        return (True, "Ready", process.pid)

    except Exception as e:
        return (False, str(e), None)


def save_pids(pids: Dict[str, int]):
    """Save PIDs to file for later cleanup."""
    try:
        with open(PID_FILE, "w") as f:
            json.dump({
                "pids": pids,
                "timestamp": time.time(),
            }, f)
    except Exception:
        pass


def save_lsp_state(results: Dict[str, Tuple[bool, str, Optional[int]]]):
    """Save LSP prewarm results for status visibility.

    Writes state to ~/.claude/.lsp-prewarm-state.json so the status line
    can display LSP server status without this hook producing stdout.
    """
    try:
        servers = {}
        for server_id, (success, message, pid) in results.items():
            servers[server_id] = {
                "success": success,
                "message": message,
                "pid": pid,
                "name": LSP_SERVERS.get(server_id, {}).get("name", server_id)
            }

        state = {
            "servers": servers,
            "total": len(results),
            "ready": sum(1 for s, _, _ in results.values() if s),
            "timestamp": datetime.now().isoformat()
        }
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass  # Silent failure - don't break startup


def cleanup_old_servers():
    """Kill any old prewarm'd servers from previous sessions."""
    try:
        if PID_FILE.exists():
            with open(PID_FILE, "r") as f:
                data = json.load(f)

            # Kill old processes
            for server_id, pid in data.get("pids", {}).items():
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass  # Already dead
                except PermissionError:
                    pass

            PID_FILE.unlink()
    except Exception:
        pass


def format_prewarm_output(results: Dict[str, Tuple[bool, str, Optional[int]]]) -> str:
    """Format the prewarm results for display."""
    lines = []
    lines.append("")
    lines.append("-" * 50)
    lines.append("LSP PREWARM STATUS")
    lines.append("-" * 50)

    success_count = 0
    for server_id, (success, message, pid) in results.items():
        config = LSP_SERVERS.get(server_id, {})
        name = config.get("name", server_id)

        if success:
            lines.append(f"[OK] {name}: {message}")
            success_count += 1
        else:
            lines.append(f"[--] {name}: {message}")

    lines.append("-" * 50)

    if success_count == len(results):
        lines.append("All LSP servers ready for instant validation")
    elif success_count > 0:
        lines.append(f"{success_count}/{len(results)} LSP servers ready")
    else:
        lines.append("No LSP servers available (validations will use fallback)")

    lines.append("")
    return "\n".join(lines)


def is_clear_event(input_data: dict) -> bool:
    """
    Detect if this is a /clear command (SessionStart:clear) vs fresh session.

    Claude Code passes event type info that we can use to detect /clear.
    The hook event name includes ':clear' suffix for context clears.
    """
    # Check hook_event_name if provided (e.g., "SessionStart:clear")
    hook_event = input_data.get("hook_event_name", "") or input_data.get("hook_event", "")
    if ":clear" in hook_event.lower():
        return True

    # Check session_id pattern if available
    session_id = input_data.get("session_id", "")
    if session_id and ":clear" in session_id.lower():
        return True

    return False


def is_pid_alive(pid: int) -> bool:
    """Check if a process is still running."""
    try:
        os.kill(pid, 0)  # Signal 0 = check existence
        return True
    except (OSError, ProcessLookupError):
        return False
    except PermissionError:
        # Process exists but we can't signal it (different user)
        return True


def should_skip_on_clear(input_data: dict) -> bool:
    """
    Check if we should skip this hook on a /clear event.

    Returns True if:
    1. It's a clear event
    2. State file exists and is fresh (within last hour)
    3. State indicates success (LSP servers ready and still running)
    """
    if not is_clear_event(input_data):
        return False

    if not STATE_FILE.exists():
        return False

    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)

        # Check freshness (less than 1 hour old)
        timestamp_str = state.get("timestamp", "")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now() - timestamp
            if age.total_seconds() > 3600:  # Older than 1 hour
                return False

        # Check if we had at least one successful server
        if state.get("ready", 0) == 0:
            return False

        # Verify at least some servers are still running
        servers = state.get("servers", {})
        running_count = 0
        for server_id, server_info in servers.items():
            if server_info.get("success") and server_info.get("pid"):
                if is_pid_alive(server_info["pid"]):
                    running_count += 1

        # If no servers are running anymore, we should re-prewarm
        if running_count == 0:
            return False

        return True
    except (json.JSONDecodeError, ValueError, KeyError):
        return False


def main():
    """
    Main entry point for the hook.

    This hook is now SILENT - it prewarms LSP servers in the background
    without any stdout output. This avoids JSON validation errors from
    Claude Code's hook system. Graceful degradation if servers fail to start.

    Results are written to STATE_FILE for status line visibility.

    On /clear events, if valid LSP state exists and servers are still running,
    we skip re-prewarming to prevent status bar flicker.
    """
    # Read input from stdin (SessionStart event) with timeout to prevent blocking
    input_data = read_stdin_safe(timeout_seconds=0.1)

    # On /clear: skip if we have fresh, valid state with running servers
    # This prevents status bar from resetting to "Loading..." unnecessarily
    if should_skip_on_clear(input_data):
        sys.exit(0)

    # Guard: skip LSP prewarm if not in a Salesforce project
    if find_sfdx_project_root() is None:
        save_lsp_state({
            "apex": (False, "Not a Salesforce project", None),
            "lwc": (False, "Not a Salesforce project", None),
            "agentscript": (False, "Not a Salesforce project", None),
        })
        sys.exit(0)

    # Cleanup any old servers first
    cleanup_old_servers()

    # Prewarm each server (best effort - failures are silent)
    pids = {}
    results = {}

    for server_id, config in LSP_SERVERS.items():
        try:
            success, message, pid = spawn_lsp_server(server_id, config)
            results[server_id] = (success, message, pid)
            if success and pid:
                pids[server_id] = pid
        except Exception as e:
            # Track failure but don't break startup
            results[server_id] = (False, str(e), None)

    # Save PIDs for cleanup
    if pids:
        save_pids(pids)

    # Save state for status line visibility
    save_lsp_state(results)

    # SILENT: No output regardless of success/failure
    # Graceful degradation - validation will work without prewarm (just slower)
    sys.exit(0)


if __name__ == "__main__":
    main()
