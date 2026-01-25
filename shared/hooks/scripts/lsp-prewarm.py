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
  Add to SessionStart hooks in install-hooks.py

Prerequisites:
- VS Code Salesforce Extension Pack (for Apex/LWC LSPs)
- Java 11+ (for Apex LSP)
- agentscript-langserver npm package (for AgentScript LSP)
"""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Configuration
PID_FILE = Path("/tmp/sf-skills-lsp-pids.json")
PREWARM_TIMEOUT = 10  # Max seconds to wait for each server init
MODULE_DIR = Path(__file__).parent.parent / "lsp-engine"


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


def check_java_available() -> bool:
    """Check if Java 11+ is available."""
    try:
        result = subprocess.run(
            ["java", "-version"],
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


def main():
    """Main entry point for the hook."""
    # Read input from stdin (SessionStart event)
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    # Cleanup any old servers first
    cleanup_old_servers()

    # Prewarm each server
    results = {}
    pids = {}

    for server_id, config in LSP_SERVERS.items():
        success, message, pid = spawn_lsp_server(server_id, config)
        results[server_id] = (success, message, pid)
        if success and pid:
            pids[server_id] = pid

    # Save PIDs for cleanup
    if pids:
        save_pids(pids)

    # Format output
    output_message = format_prewarm_output(results)

    # Return hook output
    output = {
        "hookSpecificOutput": {
            "message": output_message
        }
    }

    print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    main()
