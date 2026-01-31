#!/usr/bin/env python3
"""
sf-skills Hook Installation Script
===================================

Automatically configures Claude Code hooks for the sf-skills plugin.
This script merges hook configurations into the user's ~/.claude/settings.json
without overwriting existing hooks.

Usage:
    python3 scripts/install-hooks.py [--uninstall] [--dry-run] [--verbose]
    python3 scripts/install-hooks.py --global --to-hooks-json  # For global installation

Options:
    --uninstall       Remove sf-skills hooks from settings
    --dry-run         Show what would be changed without making changes
    --verbose         Show detailed output
    --global          Install to ~/.claude/sf-skills-hooks/ with absolute paths

NOTE: Claude Code does NOT support a separate hooks.json file.
All hooks must be in settings.json under the "hooks" key.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import shutil
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = SCRIPT_DIR.parent
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"
GLOBAL_HOOKS_DIR = Path.home() / ".claude" / "sf-skills-hooks"
BACKUP_DIR = Path.home() / ".claude" / "backups"

# Hook configurations for sf-skills
SF_SKILLS_HOOKS: Dict[str, Any] = {
    "PreToolUse": [
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/guardrails.py",
                    "timeout": 5000
                },
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/api-version-check.py",
                    "timeout": 10000
                }
            ],
            "_sf_skills": True  # Marker for identification
        },
        {
            "matcher": "Write|Edit",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/skill-enforcement.py",
                    "timeout": 5000
                }
            ],
            "_sf_skills": True
        },
        {
            "matcher": "Skill",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/skill-enforcement.py",
                    "timeout": 5000
                }
            ],
            "_sf_skills": True
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Write|Edit",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/validator-dispatcher.py",
                    "timeout": 10000
                },
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/suggest-related-skills.py",
                    "timeout": 5000
                }
            ],
            "_sf_skills": True
        }
    ],
    "UserPromptSubmit": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/skill-activation-prompt.py",
                    "timeout": 5000
                }
            ],
            "_sf_skills": True
        }
    ],
    "PermissionRequest": [
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/auto-approve.py",
                    "timeout": 5000
                }
            ],
            "_sf_skills": True
        }
    ],
    "SubagentStop": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/chain-validator.py",
                    "timeout": 5000
                }
            ],
            "_sf_skills": True
        }
    ],
    "SessionStart": [
        {
            # MUST run first (synchronous) to create session directory
            # before async hooks write to it
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/session-init.py",
                    "timeout": 3000
                    # No async - runs synchronously to ensure session dir exists
                }
            ],
            "_sf_skills": True
        },
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/org-preflight.py",
                    "timeout": 30000,  # Longer timeout OK since async doesn't block
                    "async": True  # Fire-and-forget, writes to sessions/{PID}/org-state.json
                }
            ],
            "_sf_skills": True
        },
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {PLUGIN_ROOT}/shared/hooks/scripts/lsp-prewarm.py",
                    "timeout": 60000,  # Java LSP can be slow on cold start
                    "async": True  # Fire-and-forget, writes to sessions/{PID}/lsp-state.json
                }
            ],
            "_sf_skills": True
        }
    ]
}

# Human-readable descriptions for --status output
# Script filename → (short_description, emoji)
# Note: Descriptions should be ≤35 chars to fit in status table
HOOK_DESCRIPTIONS = {
    "session-update-check.py": ("Check for sf-skills updates", "🔄"),
    "guardrails.py": ("Block dangerous DML, fix SOQL", "🛡️"),
    "api-version-check.py": ("Validate API version on deploy", "📋"),
    "skill-enforcement.py": ("Require skill for SF file edits", "🔐"),
    "validator-dispatcher.py": ("Route to skill validators", "📨"),
    "suggest-related-skills.py": ("Suggest next workflow steps", "💡"),
    "skill-activation-prompt.py": ("Suggest skills from keywords", "🔍"),
    "auto-approve.py": ("Auto-approve safe, confirm risky", "✅"),
    "chain-validator.py": ("Validate chains, track progress", "🔗"),
    "session-init.py": ("Create PID-keyed session dir", "📁"),
    "org-preflight.py": ("Validate SF org connectivity", "☁️"),
    "lsp-prewarm.py": ("Pre-warm LSP (Apex, LWC)", "⚡"),
}

# Event type → (description, emoji)
EVENT_DESCRIPTIONS = {
    "PreToolUse": ("Runs BEFORE tool executes", "🔒"),
    "PostToolUse": ("Runs AFTER tool completes", "📤"),
    "UserPromptSubmit": ("Runs when user sends message", "💬"),
    "PermissionRequest": ("Runs when permission needed", "🔐"),
    "SubagentStop": ("Runs when subagent completes", "🔗"),
    "SessionStart": ("Runs when Claude Code starts", "🚀"),
    "Stop": ("Runs when session ends", "🛑"),
}


def get_global_hooks_config() -> Dict[str, Any]:
    """
    Generate hook configuration with absolute paths for global installation.

    Uses ~/.claude/sf-skills-hooks/ as the base path, which is a stable
    location that auto-updates from the marketplace clone.
    """
    hooks_path = str(GLOBAL_HOOKS_DIR)

    return {
        "SessionStart": [
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {hooks_path}/scripts/session-update-check.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {hooks_path}/scripts/session-init.py",
                    "timeout": 3000
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {hooks_path}/scripts/org-preflight.py",
                    "timeout": 30000,
                    "async": True
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {hooks_path}/scripts/lsp-prewarm.py",
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
                    "command": f"python3 {hooks_path}/skill-activation-prompt.py",
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
                        "command": f"python3 {hooks_path}/scripts/guardrails.py",
                        "timeout": 5000
                    },
                    {
                        "type": "command",
                        "command": f"python3 {hooks_path}/scripts/api-version-check.py",
                        "timeout": 10000
                    }
                ],
                "_sf_skills": True
            },
            {
                "matcher": "Write|Edit",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {hooks_path}/scripts/skill-enforcement.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            },
            {
                "matcher": "Skill",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {hooks_path}/scripts/skill-enforcement.py",
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
                        "command": f"python3 {hooks_path}/scripts/validator-dispatcher.py",
                        "timeout": 10000
                    },
                    {
                        "type": "command",
                        "command": f"python3 {hooks_path}/suggest-related-skills.py",
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
                    "command": f"python3 {hooks_path}/scripts/auto-approve.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ],
        "SubagentStop": [
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {hooks_path}/scripts/chain-validator.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ]
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_banner():
    """Print installation banner."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           sf-skills Hook Installation Script                  ║
║                      Version 4.3.0                            ║
╚═══════════════════════════════════════════════════════════════╝
""")


def print_success(msg: str):
    print(f"  ✅ {msg}")


def print_info(msg: str):
    print(f"  ℹ️  {msg}")


def print_warning(msg: str):
    print(f"  ⚠️  {msg}")


def print_error(msg: str):
    print(f"  ❌ {msg}")


def extract_script_name(command: str) -> str:
    """Extract script filename from command path.

    Examples:
        "python3 /path/to/guardrails.py" → "guardrails.py"
        "python3 /path/to/skill-activation-prompt.py" → "skill-activation-prompt.py"
    """
    import re
    match = re.search(r'([^/]+\.py)$', command)
    return match.group(1) if match else command.split()[-1] if command else "unknown"


def get_hook_details(hook_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract details from a hook configuration for display.

    Args:
        hook_config: A single hook matcher config (e.g., {"matcher": "Bash", "hooks": [...]})

    Returns:
        List of dicts with keys: matcher, script, description, emoji, is_async, timeout
    """
    details = []
    matcher = hook_config.get("matcher", "(all)")

    for hook in hook_config.get("hooks", []):
        command = hook.get("command", "")
        script = extract_script_name(command)
        is_async = hook.get("async", False)
        timeout = hook.get("timeout", 5000)

        desc_info = HOOK_DESCRIPTIONS.get(script, ("", ""))
        description = desc_info[0] if desc_info[0] else "Custom hook"
        emoji = desc_info[1] if len(desc_info) > 1 and desc_info[1] else "⚙️"

        details.append({
            "matcher": matcher,
            "script": script,
            "description": description,
            "emoji": emoji,
            "is_async": is_async,
            "timeout": timeout,
            "command": command  # Full command for verbose mode
        })

    return details


def load_settings(target_file: Path = None) -> Dict[str, Any]:
    """Load existing settings.json or return empty dict."""
    if target_file is None:
        target_file = SETTINGS_FILE

    if target_file.exists():
        try:
            with open(target_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in {target_file.name}: {e}")
            sys.exit(1)
    return {}


def save_settings(settings: Dict[str, Any], dry_run: bool = False, target_file: Path = None):
    """Save settings.json or hooks.json with backup."""
    if target_file is None:
        target_file = SETTINGS_FILE

    if dry_run:
        print_info("DRY RUN: Would save settings to:")
        print(f"         {target_file}")
        return

    # Create backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{target_file.stem}_{timestamp}.json"
    backup_file = BACKUP_DIR / backup_name

    if target_file.exists():
        shutil.copy(target_file, backup_file)
        print_info(f"Backup saved: {backup_file}")

    # Ensure .claude directory exists
    target_file.parent.mkdir(parents=True, exist_ok=True)

    # Save new settings
    with open(target_file, 'w') as f:
        json.dump(settings, f, indent=2)

    print_success(f"Settings saved: {target_file}")


def is_sf_skills_hook(hook: Dict[str, Any]) -> bool:
    """Check if a hook was installed by sf-skills."""
    # Check for marker
    if hook.get("_sf_skills"):
        return True

    # Check command path contains sf-skills indicators
    command = hook.get("command", "")
    if "sf-skills" in command or "shared/hooks" in command:
        return True

    # Check nested hooks
    for nested in hook.get("hooks", []):
        if is_sf_skills_hook(nested):
            return True

    return False


def hooks_equal(hooks1: List[Dict], hooks2: List[Dict]) -> bool:
    """
    Compare two hook lists for equality (ignoring order).

    Compares the full hook configuration including nested hooks, timeouts,
    async flags, etc. The _sf_skills marker is ignored in comparison since
    it's just for identification.
    """
    def normalize_hook(hook: Dict) -> str:
        """Normalize a hook to a comparable string (remove _sf_skills marker)."""
        cleaned = {k: v for k, v in hook.items() if k != "_sf_skills"}
        return json.dumps(cleaned, sort_keys=True)

    def normalize_list(hooks: List[Dict]) -> str:
        """Normalize a list of hooks to a comparable string."""
        normalized = sorted([normalize_hook(h) for h in hooks])
        return json.dumps(normalized)

    return normalize_list(hooks1) == normalize_list(hooks2)


def upsert_hooks(existing: Dict[str, Any], new_hooks: Dict[str, Any], verbose: bool = False) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Upsert (update or insert) hooks into existing configuration.

    This replaces the old merge_hooks() function with smarter behavior:
    - If event doesn't exist: add it (status: "added")
    - If sf-skills hooks exist but differ: replace them (status: "updated")
    - If sf-skills hooks exist and match: skip (status: "unchanged")
    - Non-sf-skills hooks are always preserved

    Returns:
        Tuple of:
        - Updated settings dict
        - Status dict mapping event_name -> "added" | "updated" | "unchanged"
    """
    result = existing.copy()
    status = {}

    if "hooks" not in result:
        result["hooks"] = {}

    for event_name, new_event_hooks in new_hooks.items():
        if event_name not in result["hooks"]:
            # Fresh add - no existing hooks for this event
            result["hooks"][event_name] = new_event_hooks
            status[event_name] = "added"
            if verbose:
                print_info(f"Adding new hook event: {event_name}")
        else:
            # Event exists - check if update needed
            existing_event_hooks = result["hooks"][event_name]

            # Separate sf-skills hooks from user's custom hooks
            non_sf_hooks = [h for h in existing_event_hooks if not is_sf_skills_hook(h)]
            old_sf_hooks = [h for h in existing_event_hooks if is_sf_skills_hook(h)]

            if not old_sf_hooks:
                # No sf-skills hooks existed, this is an add
                result["hooks"][event_name] = non_sf_hooks + new_event_hooks
                status[event_name] = "added"
                if verbose:
                    print_info(f"Adding sf-skills hooks to: {event_name}")
            elif hooks_equal(old_sf_hooks, new_event_hooks):
                # Configs match exactly - no change needed
                status[event_name] = "unchanged"
                if verbose:
                    print_info(f"Already up to date: {event_name}")
            else:
                # Configs differ - replace old sf-skills hooks with new
                result["hooks"][event_name] = non_sf_hooks + new_event_hooks
                status[event_name] = "updated"
                if verbose:
                    print_info(f"Updating sf-skills hooks: {event_name}")

    return result, status


def merge_hooks(existing: Dict[str, Any], new_hooks: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """Merge new hooks into existing configuration without duplicates."""
    result = existing.copy()

    if "hooks" not in result:
        result["hooks"] = {}

    for event_name, event_hooks in new_hooks.items():
        if event_name not in result["hooks"]:
            result["hooks"][event_name] = []
            if verbose:
                print_info(f"Adding new hook event: {event_name}")

        existing_hooks = result["hooks"][event_name]

        for new_hook in event_hooks:
            # Check if similar hook already exists
            # Must compare matchers AND commands when both are sf-skills hooks
            duplicate = False
            for existing_hook in existing_hooks:
                if is_sf_skills_hook(existing_hook) and is_sf_skills_hook(new_hook):
                    # Both are sf-skills hooks - compare matchers first
                    existing_matcher = existing_hook.get("matcher", "")
                    new_matcher = new_hook.get("matcher", "")
                    if existing_matcher == new_matcher:
                        # Same matcher - now compare commands to detect true duplicate
                        # Extract commands from nested hooks
                        existing_cmds = set()
                        new_cmds = set()
                        for h in existing_hook.get("hooks", []):
                            if cmd := h.get("command"):
                                existing_cmds.add(cmd)
                        for h in new_hook.get("hooks", []):
                            if cmd := h.get("command"):
                                new_cmds.add(cmd)
                        # Duplicate if same commands (or both have same single command)
                        if existing_cmds == new_cmds:
                            duplicate = True
                            if verbose:
                                print_info(f"Skipping duplicate: {event_name} (matcher: {new_matcher})")
                            break

            if not duplicate:
                existing_hooks.append(new_hook)
                if verbose:
                    matcher_info = new_hook.get("matcher", "all")
                    print_success(f"Added hook: {event_name} (matcher: {matcher_info})")

    return result


def remove_sf_skills_hooks(settings: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """Remove all sf-skills hooks from settings."""
    result = settings.copy()

    if "hooks" not in result:
        return result

    for event_name in list(result["hooks"].keys()):
        original_count = len(result["hooks"][event_name])
        result["hooks"][event_name] = [
            hook for hook in result["hooks"][event_name]
            if not is_sf_skills_hook(hook)
        ]
        removed_count = original_count - len(result["hooks"][event_name])

        if removed_count > 0 and verbose:
            print_info(f"Removed {removed_count} hook(s) from {event_name}")

        # Remove empty hook arrays
        if not result["hooks"][event_name]:
            del result["hooks"][event_name]

    # Remove empty hooks object
    if not result["hooks"]:
        del result["hooks"]

    return result


def verify_scripts_exist() -> bool:
    """Verify all hook scripts exist."""
    scripts = [
        PLUGIN_ROOT / "shared/hooks/scripts/session-update-check.py",
        PLUGIN_ROOT / "shared/hooks/scripts/guardrails.py",
        PLUGIN_ROOT / "shared/hooks/scripts/validator-dispatcher.py",
        PLUGIN_ROOT / "shared/hooks/scripts/auto-approve.py",
        PLUGIN_ROOT / "shared/hooks/scripts/chain-validator.py",
        PLUGIN_ROOT / "shared/hooks/scripts/skill-enforcement.py",
        PLUGIN_ROOT / "shared/hooks/scripts/session-init.py",
        PLUGIN_ROOT / "shared/hooks/scripts/org-preflight.py",
        PLUGIN_ROOT / "shared/hooks/scripts/lsp-prewarm.py",
        PLUGIN_ROOT / "shared/hooks/scripts/api-version-check.py",
        PLUGIN_ROOT / "shared/hooks/suggest-related-skills.py",
        PLUGIN_ROOT / "shared/hooks/skill-activation-prompt.py",
    ]

    all_exist = True
    for script in scripts:
        if not script.exists():
            print_error(f"Missing script: {script}")
            all_exist = False

    return all_exist


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def copy_hooks_to_global(dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Copy shared/hooks/ → ~/.claude/sf-skills-hooks/

    Returns True on success.
    """
    source_dir = PLUGIN_ROOT / "shared" / "hooks"

    if not source_dir.exists():
        print_error(f"Source hooks directory not found: {source_dir}")
        return False

    if dry_run:
        print_info(f"Would copy {source_dir} → {GLOBAL_HOOKS_DIR}")
        return True

    try:
        # Remove existing directory if it exists
        if GLOBAL_HOOKS_DIR.exists():
            shutil.rmtree(GLOBAL_HOOKS_DIR)

        # Copy the entire hooks directory
        shutil.copytree(source_dir, GLOBAL_HOOKS_DIR)

        if verbose:
            # Count files copied
            file_count = sum(1 for _ in GLOBAL_HOOKS_DIR.rglob("*") if _.is_file())
            print_info(f"Copied {file_count} files to {GLOBAL_HOOKS_DIR}")

        print_success(f"Hooks installed to: {GLOBAL_HOOKS_DIR}")
        return True

    except (OSError, shutil.Error) as e:
        print_error(f"Failed to copy hooks: {e}")
        return False


def write_version_file(version: str, dry_run: bool = False) -> bool:
    """Write the VERSION file in the global hooks directory."""
    version_file = GLOBAL_HOOKS_DIR / "VERSION"

    if dry_run:
        print_info(f"Would write VERSION file: {version}")
        return True

    try:
        GLOBAL_HOOKS_DIR.mkdir(parents=True, exist_ok=True)
        version_file.write_text(f"{version}\n")
        print_success(f"Version set: {version}")
        return True
    except (OSError, IOError) as e:
        print_error(f"Failed to write VERSION: {e}")
        return False


def get_registry_version() -> str:
    """Get version from skills-registry.json."""
    registry_file = PLUGIN_ROOT / "shared" / "hooks" / "skills-registry.json"
    if registry_file.exists():
        try:
            registry = json.loads(registry_file.read_text())
            return registry.get("version", "1.0.0")
        except (json.JSONDecodeError, KeyError):
            pass
    return "1.0.0"


def install_hooks_global(dry_run: bool = False, verbose: bool = False):
    """
    Install sf-skills hooks globally to ~/.claude/sf-skills-hooks/ with absolute paths.

    This creates a stable hooks directory and configures settings.json with absolute paths.
    NOTE: Claude Code does NOT support a separate hooks.json file.
    """
    print("\n📦 Installing sf-skills hooks (global mode)...\n")

    # Step 1: Verify source scripts exist
    if not verify_scripts_exist():
        print_error("Some hook scripts are missing. Please check your installation.")
        sys.exit(1)
    print_success("All hook scripts verified\n")

    # Step 2: Copy hooks to global location
    print_info("Step 1: Copying hooks to global location...")
    if not copy_hooks_to_global(dry_run=dry_run, verbose=verbose):
        if not dry_run:
            print_error("Failed to copy hooks to global location")
            sys.exit(1)

    # Step 3: Write VERSION file
    version = f"v{get_registry_version()}"
    write_version_file(version, dry_run=dry_run)

    # Step 4: Update settings.json with hooks using absolute paths
    print_info("\nStep 2: Configuring hooks in settings.json...")
    global_hooks = get_global_hooks_config()

    # Load existing settings to preserve user hooks
    existing = load_settings()
    if verbose:
        print_info(f"Loaded existing settings from: {SETTINGS_FILE}")

    # Upsert hooks (update or insert)
    new_settings, status = upsert_hooks(existing, global_hooks, verbose)

    # Count changes
    added = sum(1 for s in status.values() if s == "added")
    updated = sum(1 for s in status.values() if s == "updated")

    # Print status table
    print("\n  Hook Event         │ Status")
    print("  ───────────────────┼─────────────────")
    for event_name, event_status in status.items():
        hook_count = len(global_hooks.get(event_name, []))
        hook_label = f"{hook_count} hook{'s' if hook_count > 1 else ''}"
        if event_status == "added":
            print(f"  {event_name:18} │ ✅ Added ({hook_label})")
        elif event_status == "updated":
            print(f"  {event_name:18} │ 🔄 Updated ({hook_label})")
        else:
            print(f"  {event_name:18} │ ⚪ Up to date")

    # Save to settings.json
    print()
    save_settings(new_settings, dry_run=dry_run, target_file=SETTINGS_FILE)

    # Summary
    if not dry_run:
        print("\n" + "═" * 60)
        print("✅ Global installation complete!")
        print("═" * 60)
        print(f"""
  Hooks installed to: {GLOBAL_HOOKS_DIR}
  Config updated at:  {SETTINGS_FILE}
  Version: {version}

⚠️  Restart Claude Code to activate hooks
""")


def install_hooks(dry_run: bool = False, verbose: bool = False):
    """Install sf-skills hooks into settings.json."""
    print("\n📦 Installing sf-skills hooks...\n")

    # Verify scripts exist
    if not verify_scripts_exist():
        print_error("Some hook scripts are missing. Please check your installation.")
        sys.exit(1)
    print_success("All hook scripts verified\n")

    # Load existing settings
    settings = load_settings()
    if verbose:
        print_info(f"Loaded settings from: {SETTINGS_FILE}\n")

    # Upsert hooks (update or insert)
    new_settings, status = upsert_hooks(settings, SF_SKILLS_HOOKS, verbose)

    # Count changes
    added = sum(1 for s in status.values() if s == "added")
    updated = sum(1 for s in status.values() if s == "updated")
    unchanged = sum(1 for s in status.values() if s == "unchanged")

    # Count total hooks per event for display
    def count_hooks(event_name: str) -> int:
        return len(SF_SKILLS_HOOKS.get(event_name, []))

    # Print status table
    print("  Hook Event         │ Status")
    print("  ───────────────────┼─────────────────")
    for event_name, event_status in status.items():
        hook_count = count_hooks(event_name)
        hook_label = f"{hook_count} hook{'s' if hook_count > 1 else ''}"
        if event_status == "added":
            print(f"  {event_name:18} │ ✅ Added ({hook_label})")
        elif event_status == "updated":
            print(f"  {event_name:18} │ 🔄 Updated ({hook_label})")
        else:
            print(f"  {event_name:18} │ ⚪ Up to date")

    # Check if any changes
    if added == 0 and updated == 0:
        print("\n" + "═" * 55)
        print("✅ sf-skills hooks already installed and up to date!")
        print("═" * 55 + "\n")
        return

    # Save changes (only if there are changes)
    print()  # Blank line before backup/save messages
    save_settings(new_settings, dry_run)

    # Summary
    changes = []
    if added > 0:
        changes.append(f"{added} added")
    if updated > 0:
        changes.append(f"{updated} updated")

    if not dry_run:
        print("\n" + "═" * 55)
        print(f"✅ Installation complete! ({', '.join(changes)})")
        print("═" * 55)
        print("\n⚠️  Restart Claude Code to activate hooks\n")


def uninstall_hooks(dry_run: bool = False, verbose: bool = False):
    """Remove sf-skills hooks from settings.json."""
    print("\n🗑️  Uninstalling sf-skills hooks...\n")

    # Load existing settings
    settings = load_settings()
    if not settings:
        print_info("No settings.json found - nothing to uninstall")
        return

    if "hooks" not in settings:
        print_info("No hooks configured - nothing to uninstall")
        return

    # Remove sf-skills hooks
    new_settings = remove_sf_skills_hooks(settings, verbose)

    # Save
    save_settings(new_settings, dry_run)

    if not dry_run:
        print("\n" + "═" * 50)
        print("✅ Uninstall complete!")
        print("═" * 50)
        print("\n⚠️  Restart Claude Code to apply changes")
        print()


def show_status(verbose: bool = False):
    """Show current hook installation status with detailed hook information.

    Args:
        verbose: If True, show full command paths and timeouts
    """
    print("\n📊 sf-skills Hook Status")
    print("═" * 80)

    settings = load_settings()

    if not settings or "hooks" not in settings:
        print("\n   No hooks configured\n")
        print("═" * 80)
        print("\nStatus: ❌ sf-skills hooks NOT installed")
        print("═" * 80 + "\n")
        return

    sf_skills_found = False

    # Define event order by session lifecycle (start → prompt → tools → end)
    event_order = [
        "SessionStart",       # 1. Session begins
        "UserPromptSubmit",   # 2. User sends message
        "PreToolUse",         # 3. Before tool runs
        "PostToolUse",        # 4. After tool completes
        "PermissionRequest",  # 5. Permission needed
        "SubagentStop",       # 6. Subagent finishes
        "Stop",               # 7. Session ends
    ]

    # Add any events not in our predefined order
    all_events = set(settings["hooks"].keys())
    for event in all_events:
        if event not in event_order:
            event_order.append(event)

    for event_name in event_order:
        if event_name not in settings["hooks"]:
            continue

        event_hooks = settings["hooks"][event_name]
        sf_skills_hooks = [h for h in event_hooks if is_sf_skills_hook(h)]

        if not sf_skills_hooks:
            continue  # Skip events with no sf-skills hooks

        sf_skills_found = True

        # Get event description and emoji
        event_desc, event_emoji = EVENT_DESCRIPTIONS.get(event_name, ("", "⚙️"))
        hook_count = len(sf_skills_hooks)

        # Print event header
        print(f"\n{event_emoji} {event_name} ({hook_count} hook{'s' if hook_count > 1 else ''}) — {event_desc}")

        # Collect all hook details for this event
        all_details = []
        for hook_config in sf_skills_hooks:
            details = get_hook_details(hook_config)
            all_details.extend(details)

        # SessionStart has special formatting (sync/async mode column)
        is_session_start = event_name == "SessionStart"

        if is_session_start:
            # SessionStart format with Mode column
            # Column widths: Mode=7, Script=26, Description=40
            print("┌─────────┬────────────────────────────┬──────────────────────────────────────────┐")
            print("│ Mode    │ Script                     │ Description                              │")
            print("├─────────┼────────────────────────────┼──────────────────────────────────────────┤")
            for detail in all_details:
                mode = ("async" if detail["is_async"] else "sync").ljust(7)
                script = detail["script"][:26].ljust(26)
                desc = detail["description"][:40].ljust(40)
                print(f"│ {mode} │ {script} │ {desc} │")
                if verbose:
                    timeout_sec = detail["timeout"] / 1000
                    print(f"│         │   └─ timeout: {timeout_sec}s".ljust(79) + "│")
                    cmd_display = detail['command'][:55]
                    print(f"│         │   └─ {cmd_display}".ljust(79) + "│")
            print("└─────────┴────────────────────────────┴──────────────────────────────────────────┘")
        else:
            # Standard format with Matcher column
            # Column widths: Matcher=13, Script=26, Description=35
            print("┌───────────────┬────────────────────────────┬─────────────────────────────────────┐")
            print("│ Matcher       │ Script                     │ Description                         │")
            print("├───────────────┼────────────────────────────┼─────────────────────────────────────┤")
            for detail in all_details:
                matcher = detail["matcher"][:13].ljust(13)
                script = detail["script"][:26].ljust(26)
                desc = detail["description"][:35].ljust(35)
                print(f"│ {matcher} │ {script} │ {desc} │")
                if verbose:
                    timeout_sec = detail["timeout"] / 1000
                    async_marker = " [async]" if detail["is_async"] else ""
                    print(f"│               │   └─ timeout: {timeout_sec}s{async_marker}".ljust(79) + "│")
                    cmd_display = detail['command'][:55]
                    print(f"│               │   └─ {cmd_display}".ljust(79) + "│")
            print("└───────────────┴────────────────────────────┴─────────────────────────────────────┘")

    print("\n" + "═" * 80)

    if sf_skills_found:
        print("Status: ✅ sf-skills hooks INSTALLED")
    else:
        print("Status: ❌ sf-skills hooks NOT installed")

    print("═" * 80 + "\n")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Install or uninstall sf-skills hooks for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 install-hooks.py              # Install hooks to settings.json
  python3 install-hooks.py --dry-run    # Preview changes
  python3 install-hooks.py --uninstall  # Remove hooks
  python3 install-hooks.py --status     # Check status

Global installation (recommended for marketplace users):
  python3 install-hooks.py --global     # Install to ~/.claude/sf-skills-hooks/
                                        # with absolute paths in settings.json
        """
    )
    parser.add_argument("--uninstall", action="store_true", help="Remove sf-skills hooks")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--status", action="store_true", help="Show current installation status")
    parser.add_argument("--global", dest="use_global", action="store_true",
                        help="Install to ~/.claude/sf-skills-hooks/ with absolute paths in settings.json")

    args = parser.parse_args()

    print_banner()

    if args.status:
        show_status(verbose=args.verbose)
    elif args.uninstall:
        uninstall_hooks(dry_run=args.dry_run, verbose=args.verbose)
    elif args.use_global:
        # Global installation mode
        install_hooks_global(dry_run=args.dry_run, verbose=args.verbose)
    else:
        install_hooks(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
