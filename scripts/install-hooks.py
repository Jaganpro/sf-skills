#!/usr/bin/env python3
"""
sf-skills Hook Installation Script
===================================

Automatically configures Claude Code hooks for the sf-skills plugin.
This script merges hook configurations into the user's ~/.claude/settings.json
without overwriting existing hooks.

Usage:
    python3 scripts/install-hooks.py [--uninstall] [--dry-run] [--verbose]

Options:
    --uninstall  Remove sf-skills hooks from settings
    --dry-run    Show what would be changed without making changes
    --verbose    Show detailed output
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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_banner():
    """Print installation banner."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           sf-skills Hook Installation Script                  ║
║                      Version 4.2.0                            ║
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


def load_settings() -> Dict[str, Any]:
    """Load existing settings.json or return empty dict."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in settings.json: {e}")
            sys.exit(1)
    return {}


def save_settings(settings: Dict[str, Any], dry_run: bool = False):
    """Save settings.json with backup."""
    if dry_run:
        print_info("DRY RUN: Would save settings to:")
        print(f"         {SETTINGS_FILE}")
        return

    # Create backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"settings_{timestamp}.json"

    if SETTINGS_FILE.exists():
        shutil.copy(SETTINGS_FILE, backup_file)
        print_info(f"Backup saved: {backup_file}")

    # Ensure .claude directory exists
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save new settings
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

    print_success(f"Settings saved: {SETTINGS_FILE}")


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


def show_status():
    """Show current hook installation status."""
    print("\n📊 sf-skills Hook Status\n")
    print("─" * 50)

    settings = load_settings()

    if not settings or "hooks" not in settings:
        print("   No hooks configured")
        print("─" * 50)
        return

    sf_skills_found = False
    for event_name, event_hooks in settings["hooks"].items():
        sf_skills_hooks = [h for h in event_hooks if is_sf_skills_hook(h)]
        if sf_skills_hooks:
            sf_skills_found = True
            print(f"   ✅ {event_name}: {len(sf_skills_hooks)} sf-skills hook(s)")
        else:
            print(f"   ⬜ {event_name}: no sf-skills hooks")

    print("─" * 50)

    if sf_skills_found:
        print("\n   Status: ✅ sf-skills hooks INSTALLED")
    else:
        print("\n   Status: ❌ sf-skills hooks NOT installed")
    print()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Install or uninstall sf-skills hooks for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 install-hooks.py              # Install hooks
  python3 install-hooks.py --dry-run    # Preview changes
  python3 install-hooks.py --uninstall  # Remove hooks
  python3 install-hooks.py --status     # Check status
        """
    )
    parser.add_argument("--uninstall", action="store_true", help="Remove sf-skills hooks")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--status", action="store_true", help="Show current installation status")

    args = parser.parse_args()

    print_banner()

    if args.status:
        show_status()
    elif args.uninstall:
        uninstall_hooks(dry_run=args.dry_run, verbose=args.verbose)
    else:
        install_hooks(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
