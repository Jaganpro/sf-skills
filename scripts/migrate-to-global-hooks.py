#!/usr/bin/env python3
"""
sf-skills Migration Script: Migrate to Global Hooks
====================================================

Migrates sf-skills hooks to use a stable global hooks directory with
absolute paths in ~/.claude/settings.json.

NOTE: Claude Code does NOT support a separate hooks.json file.
All hooks must be in settings.json under the "hooks" key.

ACTIONS:
1. Detect current installation state
2. Backup existing configs to ~/.claude/backups/migration-{timestamp}/
3. Copy shared/hooks/ → ~/.claude/sf-skills-hooks/
4. Update ~/.claude/settings.json with hooks using absolute paths
5. Clean orphaned cache entries
6. Verify installation

Usage:
    python3 scripts/migrate-to-global-hooks.py [--dry-run] [--verbose]

Options:
    --dry-run    Show what would be changed without making changes
    --verbose    Show detailed output
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = SCRIPT_DIR.parent
SOURCE_HOOKS_DIR = PLUGIN_ROOT / "shared" / "hooks"

# Target locations
CLAUDE_DIR = Path.home() / ".claude"
HOOKS_DIR = CLAUDE_DIR / "sf-skills-hooks"
SETTINGS_JSON = CLAUDE_DIR / "settings.json"
BACKUP_DIR = CLAUDE_DIR / "backups"

# Version from skills-registry.json
REGISTRY_FILE = SOURCE_HOOKS_DIR / "skills-registry.json"


# ============================================================================
# PRINT HELPERS
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_banner():
    """Print migration banner."""
    print(f"""
{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗
║         sf-skills Migration to Global Hooks                   ║
╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}
""")


def print_success(msg: str):
    print(f"  {Colors.GREEN}✅{Colors.RESET} {msg}")


def print_info(msg: str):
    print(f"  {Colors.BLUE}ℹ️ {Colors.RESET} {msg}")


def print_warning(msg: str):
    print(f"  {Colors.YELLOW}⚠️ {Colors.RESET} {msg}")


def print_error(msg: str):
    print(f"  {Colors.RED}❌{Colors.RESET} {msg}")


def print_step(num: int, title: str):
    print(f"\n{Colors.BOLD}Step {num}: {title}{Colors.RESET}")
    print("─" * 50)


# ============================================================================
# GLOBAL HOOKS TEMPLATE
# ============================================================================

def get_global_hooks_template() -> Dict[str, Any]:
    """
    Generate the hooks template with absolute paths for settings.json.

    All paths point to ~/.claude/sf-skills-hooks/ which is a stable
    location that auto-updates from the marketplace clone.
    """
    hooks_path = str(HOOKS_DIR)

    return {
        "hooks": {
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
    }


# ============================================================================
# DETECTION FUNCTIONS
# ============================================================================

def is_sf_skills_hook(hook: Dict[str, Any]) -> bool:
    """Check if a hook was installed by sf-skills."""
    # Check for marker
    if hook.get("_sf_skills"):
        return True

    # Check command paths
    for nested in hook.get("hooks", []):
        command = nested.get("command", "")
        if any(marker in command for marker in [
            "sf-skills",
            "shared/hooks",
            "sf-skills-hooks"
        ]):
            return True

    return False


def detect_installation_state() -> Dict[str, Any]:
    """
    Detect the current installation state.

    Returns dict with:
        - has_settings_hooks: bool - sf-skills hooks in settings.json
        - has_hooks_dir: bool - ~/.claude/sf-skills-hooks/ exists
        - settings_hook_count: int - number of sf-skills events in settings.json
        - uses_absolute_paths: bool - hooks use absolute paths to sf-skills-hooks/
        - version: str - current version if known
    """
    state = {
        "has_settings_hooks": False,
        "has_hooks_dir": HOOKS_DIR.exists(),
        "settings_hook_count": 0,
        "uses_absolute_paths": False,
        "version": None
    }

    # Check settings.json for sf-skills hooks
    if SETTINGS_JSON.exists():
        try:
            settings = json.loads(SETTINGS_JSON.read_text())
            if "hooks" in settings:
                for event_name, hooks in settings["hooks"].items():
                    for hook in hooks:
                        if is_sf_skills_hook(hook):
                            state["has_settings_hooks"] = True
                            state["settings_hook_count"] += 1
                            # Check if using absolute paths to sf-skills-hooks
                            for nested in hook.get("hooks", []):
                                cmd = nested.get("command", "")
                                if "sf-skills-hooks" in cmd:
                                    state["uses_absolute_paths"] = True
                            break
        except (json.JSONDecodeError, KeyError):
            pass

    # Check for VERSION file
    version_file = HOOKS_DIR / "VERSION"
    if version_file.exists():
        try:
            state["version"] = version_file.read_text().strip()
        except (OSError, IOError):
            pass

    return state


def get_registry_version() -> Optional[str]:
    """Get version from skills-registry.json."""
    if not REGISTRY_FILE.exists():
        return None

    try:
        registry = json.loads(REGISTRY_FILE.read_text())
        return registry.get("version")
    except (json.JSONDecodeError, KeyError):
        return None


# ============================================================================
# BACKUP FUNCTIONS
# ============================================================================

def create_backup(dry_run: bool = False, verbose: bool = False) -> Optional[Path]:
    """
    Create backup of existing configs.

    Returns backup directory path or None if nothing to backup.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"migration-{timestamp}"

    files_to_backup = []

    if SETTINGS_JSON.exists():
        files_to_backup.append(SETTINGS_JSON)
    if HOOKS_DIR.exists():
        files_to_backup.append(HOOKS_DIR)

    if not files_to_backup:
        if verbose:
            print_info("No existing files to backup")
        return None

    if dry_run:
        print_info(f"Would create backup at: {backup_path}")
        for f in files_to_backup:
            print_info(f"  └─ {f.name}")
        return backup_path

    # Create backup directory
    backup_path.mkdir(parents=True, exist_ok=True)

    for f in files_to_backup:
        dest = backup_path / f.name
        if f.is_dir():
            shutil.copytree(f, dest)
        else:
            shutil.copy2(f, dest)
        if verbose:
            print_info(f"Backed up: {f.name}")

    print_success(f"Backup created: {backup_path}")
    return backup_path


# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def copy_hooks_to_global(dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Copy shared/hooks/ → ~/.claude/sf-skills-hooks/

    Returns True on success.
    """
    if not SOURCE_HOOKS_DIR.exists():
        print_error(f"Source hooks directory not found: {SOURCE_HOOKS_DIR}")
        return False

    if dry_run:
        print_info(f"Would copy {SOURCE_HOOKS_DIR} → {HOOKS_DIR}")
        return True

    try:
        # Remove existing directory if it exists
        if HOOKS_DIR.exists():
            shutil.rmtree(HOOKS_DIR)

        # Copy the entire hooks directory
        shutil.copytree(SOURCE_HOOKS_DIR, HOOKS_DIR)

        if verbose:
            # Count files copied
            file_count = sum(1 for _ in HOOKS_DIR.rglob("*") if _.is_file())
            print_info(f"Copied {file_count} files to {HOOKS_DIR}")

        print_success(f"Hooks installed to: {HOOKS_DIR}")
        return True

    except (OSError, shutil.Error) as e:
        print_error(f"Failed to copy hooks: {e}")
        return False


def write_version_file(version: str, dry_run: bool = False) -> bool:
    """Write the VERSION file."""
    version_file = HOOKS_DIR / "VERSION"

    if dry_run:
        print_info(f"Would write VERSION file: {version}")
        return True

    try:
        version_file.write_text(f"{version}\n")
        return True
    except (OSError, IOError) as e:
        print_error(f"Failed to write VERSION: {e}")
        return False


def update_settings_json_hooks(dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Update ~/.claude/settings.json with sf-skills hooks using absolute paths.

    NOTE: Claude Code does NOT support a separate hooks.json file.
    All hooks must be in settings.json under the "hooks" key.

    Merges with existing user hooks without overwriting them.
    """
    template = get_global_hooks_template()

    if dry_run:
        print_info(f"Would update hooks in: {SETTINGS_JSON}")
        if verbose:
            for event_name in template["hooks"]:
                print_info(f"  └─ {event_name}: {len(template['hooks'][event_name])} hook(s)")
        return True

    try:
        # Load existing settings if present
        existing = {}
        if SETTINGS_JSON.exists():
            try:
                existing = json.loads(SETTINGS_JSON.read_text())
            except json.JSONDecodeError:
                pass

        if "hooks" not in existing:
            existing["hooks"] = {}

        # Merge: keep non-sf-skills hooks, replace sf-skills hooks
        for event_name, new_hooks in template["hooks"].items():
            if event_name not in existing["hooks"]:
                existing["hooks"][event_name] = []

            # Filter out old sf-skills hooks
            non_sf_hooks = [
                h for h in existing["hooks"][event_name]
                if not is_sf_skills_hook(h)
            ]

            # Add new sf-skills hooks
            existing["hooks"][event_name] = non_sf_hooks + new_hooks

        # Write back
        SETTINGS_JSON.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_JSON.write_text(json.dumps(existing, indent=2) + "\n")

        if verbose:
            user_hook_count = sum(
                len([h for h in hooks if not is_sf_skills_hook(h)])
                for hooks in existing["hooks"].values()
            )
            if user_hook_count > 0:
                print_info(f"Preserved {user_hook_count} user-defined hooks")

        print_success(f"Updated hooks in: {SETTINGS_JSON}")
        return True

    except (OSError, IOError) as e:
        print_error(f"Failed to update settings.json: {e}")
        return False


def remove_from_settings_json(dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Remove sf-skills hooks from settings.json.

    This cleans up the old installation method.
    """
    if not SETTINGS_JSON.exists():
        if verbose:
            print_info("No settings.json to clean")
        return True

    try:
        settings = json.loads(SETTINGS_JSON.read_text())
    except json.JSONDecodeError:
        if verbose:
            print_info("settings.json invalid JSON, skipping")
        return True

    if "hooks" not in settings:
        if verbose:
            print_info("No hooks in settings.json")
        return True

    # Track what we're removing
    removed_count = 0
    events_modified = []

    for event_name in list(settings["hooks"].keys()):
        original_count = len(settings["hooks"][event_name])
        settings["hooks"][event_name] = [
            h for h in settings["hooks"][event_name]
            if not is_sf_skills_hook(h)
        ]
        new_count = len(settings["hooks"][event_name])

        if new_count < original_count:
            removed_count += original_count - new_count
            events_modified.append(event_name)

        # Remove empty arrays
        if not settings["hooks"][event_name]:
            del settings["hooks"][event_name]

    # Remove empty hooks object
    if not settings["hooks"]:
        del settings["hooks"]

    if removed_count == 0:
        if verbose:
            print_info("No sf-skills hooks found in settings.json")
        return True

    if dry_run:
        print_info(f"Would remove {removed_count} hook(s) from settings.json")
        for event in events_modified:
            print_info(f"  └─ {event}")
        return True

    # Write back
    SETTINGS_JSON.write_text(json.dumps(settings, indent=2) + "\n")
    print_success(f"Removed {removed_count} hook(s) from settings.json")

    return True


def clean_orphan_caches(dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Clean up orphaned cache files from old installations.
    """
    cache_files = [
        Path("/tmp/sf-skills-context.json"),
        Path("/tmp/sf-skills-chain-state.json"),
        Path("/tmp/sf-skills-active-skill.json"),
        Path("/tmp/sf-skills-org-api-version-cache.json"),
    ]

    cleaned = 0
    for cache_file in cache_files:
        if cache_file.exists():
            if dry_run:
                print_info(f"Would remove: {cache_file}")
            else:
                try:
                    cache_file.unlink()
                    cleaned += 1
                except OSError:
                    pass

    if cleaned > 0 and not dry_run:
        print_success(f"Cleaned {cleaned} orphan cache file(s)")
    elif verbose and cleaned == 0:
        print_info("No orphan caches found")

    return True


def verify_installation(verbose: bool = False) -> bool:
    """
    Verify the installation is complete and valid.
    """
    issues = []

    # Check hooks directory exists
    if not HOOKS_DIR.exists():
        issues.append("Hooks directory not found")
    else:
        # Check key scripts exist
        required_scripts = [
            "scripts/session-update-check.py",
            "scripts/session-init.py",
            "scripts/guardrails.py",
            "scripts/auto-approve.py",
            "skill-activation-prompt.py",
            "skills-registry.json"
        ]
        for script in required_scripts:
            if not (HOOKS_DIR / script).exists():
                issues.append(f"Missing: {script}")

    # Check settings.json has hooks configured
    if not SETTINGS_JSON.exists():
        issues.append("settings.json not found")
    else:
        try:
            settings = json.loads(SETTINGS_JSON.read_text())
            if "hooks" not in settings:
                issues.append("settings.json missing 'hooks' key")
            elif "SessionStart" not in settings.get("hooks", {}):
                issues.append("settings.json missing SessionStart hooks")
            else:
                # Verify hooks point to sf-skills-hooks directory
                has_correct_path = False
                for hook in settings["hooks"].get("SessionStart", []):
                    for nested in hook.get("hooks", []):
                        if "sf-skills-hooks" in nested.get("command", ""):
                            has_correct_path = True
                            break
                if not has_correct_path:
                    issues.append("Hooks not pointing to sf-skills-hooks directory")
        except json.JSONDecodeError:
            issues.append("settings.json is invalid JSON")

    # Check VERSION file
    version_file = HOOKS_DIR / "VERSION"
    if not version_file.exists():
        issues.append("VERSION file not found")

    if issues:
        print_error("Verification failed:")
        for issue in issues:
            print(f"    • {issue}")
        return False

    if verbose:
        print_info("All verification checks passed")
    return True


# ============================================================================
# MAIN
# ============================================================================

def run_migration(dry_run: bool = False, verbose: bool = False):
    """Run the full migration process."""

    print_banner()

    # Step 1: Detect current state
    print_step(1, "Detecting current installation")
    state = detect_installation_state()

    print(f"  Current state:")
    if state["has_settings_hooks"]:
        path_type = "(absolute paths)" if state["uses_absolute_paths"] else "(relative paths)"
        print(f"    • settings.json: {state['settings_hook_count']} sf-skills events {path_type}")
    else:
        print(f"    • settings.json: No sf-skills hooks")

    if state["has_hooks_dir"]:
        print(f"    • sf-skills-hooks/: Exists (v{state['version'] or 'unknown'})")
    else:
        print(f"    • sf-skills-hooks/: Not installed")

    # Get version for new installation
    version = get_registry_version() or "1.0.0"
    print(f"    • Source version: v{version}")

    # Step 2: Create backup
    print_step(2, "Creating backup")
    backup_path = create_backup(dry_run=dry_run, verbose=verbose)
    if not backup_path and not dry_run:
        print_info("No existing files to backup (fresh install)")

    # Step 3: Copy hooks to global location
    print_step(3, "Installing hooks to global location")
    if not copy_hooks_to_global(dry_run=dry_run, verbose=verbose):
        if not dry_run:
            print_error("Migration failed at step 3")
            return False

    # Step 4: Write VERSION file
    if not write_version_file(f"v{version}", dry_run=dry_run):
        if not dry_run:
            print_error("Migration failed at step 4")
            return False
    print_success(f"Version set: v{version}")

    # Step 5: Update settings.json with hooks using absolute paths
    print_step(4, "Updating settings.json hooks")
    if not update_settings_json_hooks(dry_run=dry_run, verbose=verbose):
        if not dry_run:
            print_error("Migration failed at step 5")
            return False

    # Step 6: Clean orphan caches
    print_step(5, "Cleaning up caches")
    clean_orphan_caches(dry_run=dry_run, verbose=verbose)

    # Step 7: Verify installation
    print_step(6, "Verifying installation")
    if dry_run:
        print_info("Skipping verification (dry run)")
    else:
        if verify_installation(verbose=verbose):
            print_success("Installation verified")
        else:
            print_warning("Verification found issues (see above)")

    # Summary
    print(f"""
{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}
""")

    if dry_run:
        print(f"{Colors.YELLOW}DRY RUN COMPLETE{Colors.RESET} - No changes were made")
        print(f"\nRun without --dry-run to apply changes")
    else:
        print(f"{Colors.GREEN}✅ MIGRATION COMPLETE!{Colors.RESET}")
        print(f"""
  Hooks installed to: {HOOKS_DIR}
  Config updated at:  {SETTINGS_JSON}
""")
        if backup_path:
            print(f"  Backup saved to:    {backup_path}")
        print(f"""
{Colors.YELLOW}⚠️  Restart Claude Code to activate the new hooks{Colors.RESET}
""")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate sf-skills hooks to global installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 migrate-to-global-hooks.py              # Run migration
    python3 migrate-to-global-hooks.py --dry-run    # Preview changes
    python3 migrate-to-global-hooks.py --verbose    # Detailed output
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()
    success = run_migration(dry_run=args.dry_run, verbose=args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
