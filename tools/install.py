#!/usr/bin/env python3
"""
sf-skills Unified Installer for Claude Code

Usage:
    curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.py | python3

    # Or with options:
    python3 install.py                # Interactive install
    python3 install.py --update       # Check version + content changes
    python3 install.py --force-update # Force reinstall even if up-to-date
    python3 install.py --uninstall    # Remove sf-skills
    python3 install.py --status       # Show installation status
    python3 install.py --dry-run      # Preview changes
    python3 install.py --force        # Skip confirmations

Update Detection:
    The --update command detects both version bumps AND content changes:
    - Version bump: Remote version > local version
    - Content change: Same version but different Git commit SHA
    - Legacy upgrade: Enables content tracking on older installs

Requirements:
    - Python 3.8+ (standard library only)
    - Claude Code installed (~/.claude/ directory exists)
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request
import urllib.error
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION = "1.0.0"  # Installer version

# Installation paths (Claude Code native layout)
CLAUDE_DIR = Path.home() / ".claude"
SKILLS_DIR = CLAUDE_DIR / "skills"
HOOKS_DIR = CLAUDE_DIR / "hooks"
LSP_DIR = CLAUDE_DIR / "lsp-engine"
META_FILE = CLAUDE_DIR / ".sf-skills.json"
INSTALLER_FILE = CLAUDE_DIR / "sf-skills-install.py"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

# Legacy paths (for migration cleanup only)
LEGACY_INSTALL_DIR = CLAUDE_DIR / "sf-skills"
LEGACY_HOOKS_DIR = CLAUDE_DIR / "sf-skills-hooks"
MARKETPLACE_DIR = CLAUDE_DIR / "plugins" / "marketplaces" / "sf-skills"

# GitHub repository info
GITHUB_OWNER = "Jaganpro"
GITHUB_REPO = "sf-skills"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main"

# Files to install (source layout paths)
SKILLS_GLOB = "sf-*"  # All skill directories
HOOKS_SRC_DIR = "shared/hooks"
LSP_ENGINE_SRC_DIR = "shared/lsp-engine"
SKILLS_REGISTRY = "shared/hooks/skills-registry.json"
AGENTS_DIR = "agents"  # FDE + PS agent definitions
AGENT_PREFIXES = ("fde-", "ps-")  # Agent file prefixes managed by installer

# Temp file patterns to clean
TEMP_FILE_PATTERNS = [
    "/tmp/sf-skills-*.json",
    "/tmp/sfskills-*.json",
]


# ============================================================================
# STATE DETECTION
# ============================================================================

class InstallState:
    """Enumeration of installation states."""
    FRESH = "fresh"              # No installation found
    UNIFIED = "unified"          # Unified install (this script)
    MARKETPLACE = "marketplace"  # Old marketplace install
    LEGACY = "legacy"            # Old sf-skills-hooks install
    CORRUPTED = "corrupted"      # Exists but missing fingerprint


def safe_rmtree(path: Path) -> None:
    """Remove a directory tree, handling symlinks gracefully.

    Python 3.12+ shutil.rmtree() refuses to operate on symbolic links.
    This helper detects symlinks and unlinks them instead, preventing
    OSError("Cannot call rmtree on a symbolic link").
    """
    p = Path(path)
    if p.is_symlink():
        p.unlink()
    elif p.exists():
        shutil.rmtree(p)


def write_metadata(version: str, commit_sha: Optional[str] = None):
    """Write install metadata to ~/.claude/.sf-skills.json."""
    META_FILE.write_text(json.dumps({
        "method": "unified",
        "version": version,
        "commit_sha": commit_sha,
        "installed_at": datetime.now().isoformat(),
        "installer_version": VERSION
    }, indent=2))


def read_metadata() -> Optional[Dict[str, Any]]:
    """Read install metadata from .sf-skills.json, falling back to legacy fingerprint."""
    # Check new location first
    if META_FILE.exists():
        try:
            return json.loads(META_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return None

    # Fallback: check legacy .install-fingerprint
    legacy_fp = LEGACY_INSTALL_DIR / ".install-fingerprint"
    if legacy_fp.exists():
        try:
            fp = json.loads(legacy_fp.read_text())
            # Enrich with version from legacy VERSION file
            if "version" not in fp:
                version_file = LEGACY_INSTALL_DIR / "VERSION"
                if version_file.exists():
                    fp["version"] = version_file.read_text().strip()
            return fp
        except (json.JSONDecodeError, IOError):
            return None

    return None


def read_fingerprint() -> Optional[Dict[str, Any]]:
    """Read install metadata (compatibility alias for read_metadata)."""
    return read_metadata()


def get_installed_version() -> Optional[str]:
    """Read version from metadata file."""
    metadata = read_metadata()
    if metadata:
        return metadata.get("version")
    return None


def detect_state() -> Tuple[str, Optional[str]]:
    """
    Detect current installation state.

    Returns:
        Tuple of (state, version)
        - state: One of InstallState values
        - version: Installed version if found, None otherwise
    """
    # Check for marketplace installation
    if MARKETPLACE_DIR.exists():
        return InstallState.MARKETPLACE, None

    # Check for legacy hooks installation
    if LEGACY_HOOKS_DIR.exists():
        # Check if it has VERSION file
        legacy_version = None
        version_file = LEGACY_HOOKS_DIR / "VERSION"
        if version_file.exists():
            try:
                legacy_version = version_file.read_text().strip()
            except IOError:
                pass
        return InstallState.LEGACY, legacy_version

    # Check for new unified installation (native layout)
    metadata = read_metadata()
    if metadata and metadata.get("method") == "unified":
        version = metadata.get("version")
        return InstallState.UNIFIED, version

    # Check for old unified installation (legacy bundle dir)
    if LEGACY_INSTALL_DIR.exists():
        fp_file = LEGACY_INSTALL_DIR / ".install-fingerprint"
        if fp_file.exists():
            try:
                fp = json.loads(fp_file.read_text())
                if fp.get("method") == "unified":
                    version_file = LEGACY_INSTALL_DIR / "VERSION"
                    version = version_file.read_text().strip() if version_file.exists() else None
                    return InstallState.UNIFIED, version
            except (json.JSONDecodeError, IOError):
                pass
        # Directory exists but no fingerprint - corrupted
        if (LEGACY_INSTALL_DIR / "VERSION").exists() or (LEGACY_INSTALL_DIR / "skills").exists():
            return InstallState.CORRUPTED, None

    # No installation found
    return InstallState.FRESH, None


# ============================================================================
# OUTPUT HELPERS
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    BLUE = "\033[34m"


def supports_color() -> bool:
    """Check if terminal supports color."""
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


USE_COLOR = supports_color()


def c(text: str, color: str) -> str:
    """Apply color if supported."""
    if USE_COLOR:
        return f"{color}{text}{Colors.RESET}"
    return text


def print_banner():
    """Display installation banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                 sf-skills Installer for Claude Code              ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(c(banner, Colors.CYAN))


def print_step(step: int, total: int, message: str, status: str = "..."):
    """Print a progress step."""
    if status == "done":
        icon = c("✓", Colors.GREEN)
    elif status == "skip":
        icon = c("○", Colors.DIM)
    elif status == "fail":
        icon = c("✗", Colors.RED)
    else:
        icon = c("→", Colors.BLUE)
    print(f"[{step}/{total}] {icon} {message}")


def print_substep(message: str, indent: int = 1):
    """Print a substep with indentation."""
    prefix = "    " * indent + "└── "
    print(f"{prefix}{message}")


def print_success(message: str):
    """Print success message."""
    print(f"  {c('✅', Colors.GREEN)} {message}")


def print_warning(message: str):
    """Print warning message."""
    print(f"  {c('⚠️', Colors.YELLOW)} {message}")


def print_error(message: str):
    """Print error message."""
    print(f"  {c('❌', Colors.RED)} {message}")


def print_info(message: str):
    """Print info message."""
    print(f"  {c('ℹ️', Colors.BLUE)} {message}")


def confirm(prompt: str, default: bool = True) -> bool:
    """Get user confirmation."""
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        response = input(f"{prompt} {suffix}: ").strip().lower()
        if not response:
            return default
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


# ============================================================================
# GITHUB OPERATIONS
# ============================================================================

def fetch_latest_release() -> Optional[Dict[str, Any]]:
    """Fetch latest release info from GitHub API."""
    try:
        url = f"{GITHUB_API_URL}/releases/latest"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def fetch_latest_commit_sha(ref: str = "main") -> Optional[str]:
    """
    Fetch latest commit SHA from GitHub API.

    Uses the special Accept header to get just the SHA string (40 bytes).

    Args:
        ref: Git ref (branch, tag, or commit). Defaults to "main".

    Returns:
        40-character SHA string, or None on error.
    """
    try:
        url = f"{GITHUB_API_URL}/commits/{ref}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github.sha"
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode().strip()
    except (urllib.error.URLError, TimeoutError):
        return None


def fetch_registry_version() -> Optional[str]:
    """Fetch version from skills-registry.json on main branch."""
    try:
        url = f"{GITHUB_RAW_URL}/{SKILLS_REGISTRY}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("version")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


# Update reason constants
UPDATE_REASON_VERSION_BUMP = "version_bump"
UPDATE_REASON_CONTENT_CHANGED = "content_changed"
UPDATE_REASON_ENABLE_SHA_TRACKING = "enable_sha_tracking"
UPDATE_REASON_UP_TO_DATE = "up_to_date"
UPDATE_REASON_ERROR = "error"


def needs_update() -> Tuple[bool, str, Dict[str, Any]]:
    """
    Check both version AND commit SHA to determine if update is needed.

    Detection Logic:
    - IF remote_version > local_version → UPDATE (version bump)
    - IF remote_version == local_version AND remote_sha != local_sha → UPDATE (content changed)
    - IF local has no commit_sha (legacy) → UPDATE (enable tracking)
    - ELSE → "Already up to date!"

    Returns:
        Tuple of (needs_update, reason, details)
        - needs_update: True if update should be applied
        - reason: One of UPDATE_REASON_* constants
        - details: Dict with version/sha info for display
    """
    fingerprint = read_fingerprint()
    current_version = get_installed_version()
    local_sha = fingerprint.get("commit_sha") if fingerprint else None

    # Fetch remote info
    remote_version = fetch_registry_version()
    remote_sha = fetch_latest_commit_sha()

    details = {
        "local_version": current_version,
        "remote_version": remote_version,
        "local_sha": local_sha,
        "remote_sha": remote_sha,
    }

    # Network error
    if not remote_version:
        return False, UPDATE_REASON_ERROR, details

    # Compare versions (strip 'v' prefix for comparison)
    local_v = (current_version or "0.0.0").lstrip('v')
    remote_v = remote_version.lstrip('v')

    # Case 1: Version bump
    if remote_v > local_v:
        return True, UPDATE_REASON_VERSION_BUMP, details

    # Case 2: Same version, check SHA
    if remote_v == local_v:
        # Legacy install without SHA tracking
        if local_sha is None:
            return True, UPDATE_REASON_ENABLE_SHA_TRACKING, details

        # SHA comparison (only if we could fetch remote SHA)
        if remote_sha and local_sha != remote_sha:
            return True, UPDATE_REASON_CONTENT_CHANGED, details

    # Up to date
    return False, UPDATE_REASON_UP_TO_DATE, details


def download_repo_zip(target_dir: Path, ref: str = "main") -> bool:
    """
    Download repository as zip and extract to target directory.

    Args:
        target_dir: Directory to extract files into
        ref: Git ref (branch, tag, or commit)

    Returns:
        True on success, False on failure
    """
    try:
        # Download zip
        zip_url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/refs/heads/{ref}.zip"

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

            with urllib.request.urlopen(zip_url, timeout=60) as response:
                tmp_file.write(response.read())

        # Extract
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

        # Clean up
        tmp_path.unlink()

        return True

    except (urllib.error.URLError, zipfile.BadZipFile, IOError) as e:
        print_error(f"Download failed: {e}")
        return False


# ============================================================================
# CLEANUP OPERATIONS
# ============================================================================

def cleanup_marketplace(dry_run: bool = False) -> bool:
    """Remove marketplace installation."""
    if not MARKETPLACE_DIR.exists():
        return True

    if dry_run:
        print_info(f"Would remove: {MARKETPLACE_DIR}")
        return True

    try:
        safe_rmtree(MARKETPLACE_DIR)
        print_substep(f"Removed marketplace install: {MARKETPLACE_DIR}")
        return True
    except (OSError, shutil.Error) as e:
        print_error(f"Failed to remove marketplace: {e}")
        return False


def cleanup_legacy(dry_run: bool = False) -> bool:
    """Remove legacy sf-skills-hooks installation."""
    if not LEGACY_HOOKS_DIR.exists():
        return True

    if dry_run:
        print_info(f"Would remove: {LEGACY_HOOKS_DIR}")
        return True

    try:
        safe_rmtree(LEGACY_HOOKS_DIR)
        print_substep(f"Removed legacy hooks: {LEGACY_HOOKS_DIR}")
        return True
    except (OSError, shutil.Error) as e:
        print_error(f"Failed to remove legacy hooks: {e}")
        return False


def cleanup_settings_hooks(dry_run: bool = False) -> int:
    """
    Remove sf-skills hooks from settings.json.

    Returns:
        Number of hooks removed
    """
    if not SETTINGS_FILE.exists():
        return 0

    try:
        settings = json.loads(SETTINGS_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return 0

    if "hooks" not in settings:
        return 0

    removed_count = 0

    for event_name in list(settings["hooks"].keys()):
        original_len = len(settings["hooks"][event_name])
        settings["hooks"][event_name] = [
            hook for hook in settings["hooks"][event_name]
            if not is_sf_skills_hook(hook)
        ]
        removed_count += original_len - len(settings["hooks"][event_name])

        # Remove empty arrays
        if not settings["hooks"][event_name]:
            del settings["hooks"][event_name]

    # Remove empty hooks object
    if not settings["hooks"]:
        del settings["hooks"]

    if removed_count > 0 and not dry_run:
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2))

    return removed_count


def cleanup_temp_files(dry_run: bool = False) -> int:
    """
    Remove sf-skills temp files.

    Returns:
        Number of files removed
    """
    import glob as glob_module

    removed = 0
    for pattern in TEMP_FILE_PATTERNS:
        for filepath in glob_module.glob(pattern):
            if dry_run:
                print_info(f"Would remove: {filepath}")
            else:
                try:
                    Path(filepath).unlink()
                    removed += 1
                except IOError:
                    pass

    return removed


def is_sf_skills_hook(hook: Dict[str, Any]) -> bool:
    """Check if a hook was installed by sf-skills."""
    # Check for marker
    if hook.get("_sf_skills"):
        return True

    # Check command path contains sf-skills indicators
    command = hook.get("command", "")
    if "sf-skills" in command or "shared/hooks" in command or ".claude/hooks" in command:
        return True

    # Check nested hooks
    for nested in hook.get("hooks", []):
        if is_sf_skills_hook(nested):
            return True

    return False


# ============================================================================
# INSTALLATION OPERATIONS
# ============================================================================

def get_hooks_config() -> Dict[str, Any]:
    """
    Generate hook configuration with absolute paths.

    Returns hooks configuration for settings.json.
    """
    hooks_path = str(HOOKS_DIR)
    scripts_path = f"{hooks_path}/scripts"

    return {
        "SessionStart": [
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {scripts_path}/session-init.py",
                    "timeout": 3000
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {scripts_path}/org-preflight.py",
                    "timeout": 30000,
                    "async": True
                }],
                "_sf_skills": True
            },
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {scripts_path}/lsp-prewarm.py",
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
                        "command": f"python3 {scripts_path}/guardrails.py",
                        "timeout": 5000
                    },
                    {
                        "type": "command",
                        "command": f"python3 {scripts_path}/api-version-check.py",
                        "timeout": 10000
                    }
                ],
                "_sf_skills": True
            },
            {
                "matcher": "Write|Edit",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {scripts_path}/skill-enforcement.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            },
            {
                "matcher": "Skill",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {scripts_path}/skill-enforcement.py",
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
                        "command": f"python3 {scripts_path}/validator-dispatcher.py",
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
                    "command": f"python3 {scripts_path}/auto-approve.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ],
        "SubagentStop": [
            {
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {scripts_path}/chain-validator.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ]
    }


def upsert_hooks(existing: Dict[str, Any], new_hooks: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Upsert (update or insert) hooks into existing configuration.

    Args:
        existing: Current settings dict
        new_hooks: Hooks to add/update

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
            # Fresh add
            result["hooks"][event_name] = new_event_hooks
            status[event_name] = "added"
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
            else:
                # Replace old sf-skills hooks with new
                result["hooks"][event_name] = non_sf_hooks + new_event_hooks
                # Check if actually different
                old_normalized = json.dumps(sorted([json.dumps(h, sort_keys=True) for h in old_sf_hooks]))
                new_normalized = json.dumps(sorted([json.dumps(h, sort_keys=True) for h in new_event_hooks]))
                if old_normalized == new_normalized:
                    status[event_name] = "unchanged"
                else:
                    status[event_name] = "updated"

    return result, status


def copy_skills(source_dir: Path, target_dir: Path) -> int:
    """
    Copy skill directories.

    Args:
        source_dir: Source directory containing sf-* folders
        target_dir: Target skills directory

    Returns:
        Number of skills copied
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for skill_dir in source_dir.glob("sf-*"):
        if skill_dir.is_dir():
            target_skill = target_dir / skill_dir.name
            if target_skill.exists() or target_skill.is_symlink():
                safe_rmtree(target_skill)
            shutil.copytree(skill_dir, target_skill)
            count += 1

    return count


def copy_agents(source_dir: Path, target_dir: Path) -> int:
    """
    Copy agent .md files from agents/ to target directory.

    Only copies files matching known prefixes (fde-*, ps-*) to avoid
    overwriting user's custom agents.

    Args:
        source_dir: Root source directory containing agents/ subfolder
        target_dir: Target directory (e.g., ~/.claude/agents/)

    Returns:
        Number of agent files copied
    """
    agents_source = source_dir / AGENTS_DIR
    if not agents_source.exists():
        return 0

    target_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for prefix in AGENT_PREFIXES:
        for agent_file in agents_source.glob(f"{prefix}*.md"):
            if agent_file.is_file():
                shutil.copy2(agent_file, target_dir / agent_file.name)
                count += 1

    return count


def cleanup_agents(target_dir: Path, dry_run: bool = False) -> int:
    """
    Remove managed agent files from target directory during uninstall.

    Only removes files matching known prefixes (fde-*, ps-*) to preserve
    user's custom agents.

    Args:
        target_dir: Directory containing agent files (e.g., ~/.claude/agents/)
        dry_run: If True, don't actually remove files

    Returns:
        Number of agent files removed
    """
    if not target_dir.exists():
        return 0

    count = 0
    for prefix in AGENT_PREFIXES:
        for agent_file in target_dir.glob(f"{prefix}*.md"):
            if agent_file.is_file():
                if not dry_run:
                    agent_file.unlink()
                count += 1

    return count


def cleanup_installed_files(dry_run: bool = False):
    """Remove all sf-skills installed files from ~/.claude/ native layout."""
    # Remove sf-* dirs from ~/.claude/skills/ (preserves user's custom skills)
    if SKILLS_DIR.exists():
        for d in SKILLS_DIR.iterdir():
            if d.is_dir() and d.name.startswith("sf-"):
                if not dry_run:
                    safe_rmtree(d)

    # Remove hooks directory entirely (all sf-skills content)
    if HOOKS_DIR.exists() and not dry_run:
        safe_rmtree(HOOKS_DIR)

    # Remove LSP engine
    if LSP_DIR.exists() and not dry_run:
        safe_rmtree(LSP_DIR)

    # Remove metadata and installer
    for f in [META_FILE, INSTALLER_FILE]:
        if f.exists() and not dry_run:
            f.unlink()


def migrate_legacy_layout(dry_run: bool = False) -> bool:
    """
    Migrate from legacy ~/.claude/sf-skills/ to native ~/.claude/ layout.

    Copies files from old locations to new, writes metadata, updates
    settings.json hooks, and removes legacy directory. No network required.

    Args:
        dry_run: If True, preview changes without applying

    Returns:
        True if migration was performed (or would be), False if not needed
    """
    if not LEGACY_INSTALL_DIR.exists():
        return False

    print_banner()
    print_info("Legacy layout detected — migrating to native ~/.claude/ layout...")

    if dry_run:
        print_info("(dry run — no changes will be made)")

    old_skills = LEGACY_INSTALL_DIR / "skills"
    old_hooks = LEGACY_INSTALL_DIR / "hooks"
    old_lsp = LEGACY_INSTALL_DIR / "lsp-engine"

    # Copy skills: ~/.claude/sf-skills/skills/sf-*/ → ~/.claude/skills/sf-*/
    if old_skills.exists() and not dry_run:
        skill_count = copy_skills(old_skills, SKILLS_DIR)
        print_substep(f"{skill_count} skills migrated")

    # Copy hooks: ~/.claude/sf-skills/hooks/ → ~/.claude/hooks/
    if old_hooks.exists() and not dry_run:
        hook_count = copy_hooks(old_hooks, HOOKS_DIR)
        print_substep(f"{hook_count} hook scripts migrated")

    # Copy LSP: ~/.claude/sf-skills/lsp-engine/ → ~/.claude/lsp-engine/
    if old_lsp.exists() and not dry_run:
        lsp_count = copy_lsp_engine(old_lsp, LSP_DIR)
        print_substep(f"{lsp_count} LSP engine files migrated")

    # Copy agents if present
    old_agents = LEGACY_INSTALL_DIR / "agents"
    if old_agents.exists() and not dry_run:
        agents_target = CLAUDE_DIR / "agents"
        agent_count = copy_agents(LEGACY_INSTALL_DIR, agents_target)
        if agent_count > 0:
            print_substep(f"{agent_count} agents migrated (FDE + PS)")

    # Copy installer to new location
    this_file = Path(__file__).resolve()
    if not dry_run:
        shutil.copy2(this_file, INSTALLER_FILE)
        print_substep(f"Installer → {INSTALLER_FILE}")

    # Write metadata from old fingerprint
    if not dry_run:
        old_fp_file = LEGACY_INSTALL_DIR / ".install-fingerprint"
        old_version_file = LEGACY_INSTALL_DIR / "VERSION"
        version = old_version_file.read_text().strip() if old_version_file.exists() else "unknown"
        commit_sha = None
        if old_fp_file.exists():
            try:
                fp = json.loads(old_fp_file.read_text())
                commit_sha = fp.get("commit_sha")
            except (json.JSONDecodeError, IOError):
                pass
        write_metadata(version, commit_sha=commit_sha)
        print_substep(f"Metadata → {META_FILE}")

    # Update settings.json hook paths (old → new)
    if not dry_run:
        update_settings_json()
        print_substep("settings.json hooks updated")

    # Remove legacy directory and symlinks
    if not dry_run:
        safe_rmtree(LEGACY_INSTALL_DIR)
        old_cmds = unregister_skills_from_commands()
        print_substep("Removed legacy ~/.claude/sf-skills/")
        if old_cmds > 0:
            print_substep(f"Removed {old_cmds} legacy command symlinks")

    print_success("Migration complete!")
    print_info(f"Future updates: python3 {INSTALLER_FILE} --update")
    return True


# Commands directory for skill registration
COMMANDS_DIR = CLAUDE_DIR / "commands"


def register_skills_as_commands(skills_dir: Path, dry_run: bool = False) -> int:
    """
    Register skills in ~/.claude/commands/ by creating symlinks to SKILL.md files.

    Claude Code discovers custom commands from ~/.claude/commands/*.md files.
    This function creates symlinks like:
        ~/.claude/commands/sf-apex.md -> ~/.claude/sf-skills/skills/sf-apex/SKILL.md

    Args:
        skills_dir: Directory containing skill subdirectories (each with SKILL.md)
        dry_run: If True, only report what would be done

    Returns:
        Number of skills registered
    """
    if not skills_dir.exists():
        return 0

    if not dry_run:
        COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir() or not skill_dir.name.startswith("sf-"):
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        # Create symlink: ~/.claude/commands/sf-apex.md -> SKILL.md
        link_path = COMMANDS_DIR / f"{skill_dir.name}.md"

        if dry_run:
            print_info(f"Would create: {link_path} -> {skill_md}")
        else:
            # Remove existing link or file
            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()

            # Create symlink
            link_path.symlink_to(skill_md)

        count += 1

    return count


def unregister_skills_from_commands(dry_run: bool = False) -> int:
    """
    Remove sf-skills symlinks from ~/.claude/commands/.

    Args:
        dry_run: If True, only report what would be done

    Returns:
        Number of links removed
    """
    if not COMMANDS_DIR.exists():
        return 0

    count = 0
    for link_path in COMMANDS_DIR.glob("sf-*.md"):
        if link_path.is_symlink():
            target = link_path.resolve()
            # Only remove if it points to our skills directory
            if "sf-skills" in str(target):
                if dry_run:
                    print_info(f"Would remove: {link_path}")
                else:
                    link_path.unlink()
                count += 1

    return count


def copy_hooks(source_dir: Path, target_dir: Path) -> int:
    """
    Copy hook scripts.

    Args:
        source_dir: Source hooks directory
        target_dir: Target hooks directory

    Returns:
        Number of hook files copied
    """
    if target_dir.exists() or target_dir.is_symlink():
        safe_rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)

    # Count Python files
    return sum(1 for _ in target_dir.rglob("*.py"))


def copy_tools(source_dir: Path, target_dir: Path) -> int:
    """
    Copy tools directory (includes install.py for local updates).

    Args:
        source_dir: Source tools directory
        target_dir: Target tools directory

    Returns:
        Number of files copied
    """
    if not source_dir.exists():
        return 0

    if target_dir.exists() or target_dir.is_symlink():
        safe_rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)

    # Count files
    return sum(1 for _ in target_dir.rglob("*") if _.is_file())


def copy_lsp_engine(source_dir: Path, target_dir: Path) -> int:
    """
    Copy LSP engine directory (wrapper scripts for Apex, LWC, AgentScript LSPs).

    The lsp-engine contains shell wrapper scripts that interface with VS Code's
    Salesforce extensions to provide real-time syntax validation.

    Args:
        source_dir: Source lsp-engine directory
        target_dir: Target lsp-engine directory

    Returns:
        Number of files copied
    """
    if not source_dir.exists():
        return 0

    if target_dir.exists() or target_dir.is_symlink():
        safe_rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)

    # Make wrapper scripts executable
    for script in target_dir.glob("*.sh"):
        script.chmod(script.stat().st_mode | 0o111)

    # Count files
    return sum(1 for _ in target_dir.rglob("*") if _.is_file())


def touch_all_files(directory: Path):
    """Update mtime on all files to force cache refresh."""
    now = time.time()
    for filepath in directory.rglob("*"):
        if filepath.is_file():
            try:
                os.utime(filepath, (now, now))
            except IOError:
                pass


def update_settings_json(dry_run: bool = False) -> Dict[str, str]:
    """
    Register hooks in settings.json.

    Returns:
        Status dict mapping event_name -> "added" | "updated" | "unchanged"
    """
    # Load existing settings
    settings = {}
    if SETTINGS_FILE.exists():
        try:
            settings = json.loads(SETTINGS_FILE.read_text())
        except json.JSONDecodeError:
            print_warning("Could not parse settings.json, creating new")

    # Upsert hooks
    hooks_config = get_hooks_config()
    new_settings, status = upsert_hooks(settings, hooks_config)

    if not dry_run:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(new_settings, indent=2))

    return status


def verify_installation() -> Tuple[bool, List[str]]:
    """
    Verify installation is complete and functional.

    Returns:
        Tuple of (success, list of issues)
    """
    issues = []

    # Check metadata file
    if not META_FILE.exists():
        issues.append("Missing .sf-skills.json metadata")

    # Check skills directory
    if not SKILLS_DIR.exists():
        issues.append("Missing skills directory")
    else:
        skill_count = sum(1 for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name.startswith("sf-"))
        if skill_count == 0:
            issues.append("No skills found")

    # Check hooks directory
    if not HOOKS_DIR.exists():
        issues.append("Missing hooks directory")
    else:
        # Check key hook scripts
        required_scripts = [
            "scripts/guardrails.py",
            "scripts/session-init.py",
            "skill-activation-prompt.py",
            "skills-registry.json"
        ]
        for script in required_scripts:
            if not (HOOKS_DIR / script).exists():
                issues.append(f"Missing: hooks/{script}")

    # Check lsp-engine directory
    if not LSP_DIR.exists():
        issues.append("Missing lsp-engine directory")
    else:
        # Check key wrapper scripts
        required_wrappers = [
            "apex_wrapper.sh",
            "lwc_wrapper.sh",
            "agentscript_wrapper.sh"
        ]
        for wrapper in required_wrappers:
            if not (LSP_DIR / wrapper).exists():
                issues.append(f"Missing: lsp-engine/{wrapper}")

    # Check settings.json has hooks
    if SETTINGS_FILE.exists():
        try:
            settings = json.loads(SETTINGS_FILE.read_text())
            if "hooks" not in settings:
                issues.append("No hooks in settings.json")
            else:
                # Check for _sf_skills marker
                has_sf_hooks = False
                for event_hooks in settings["hooks"].values():
                    for hook in event_hooks:
                        if hook.get("_sf_skills"):
                            has_sf_hooks = True
                            break
                if not has_sf_hooks:
                    issues.append("sf-skills hooks not registered")
        except json.JSONDecodeError:
            issues.append("Invalid settings.json")
    else:
        issues.append("settings.json not found")

    return len(issues) == 0, issues


# ============================================================================
# MAIN COMMANDS
# ============================================================================

def cmd_install(dry_run: bool = False, force: bool = False, called_from_bash: bool = False) -> int:
    """
    Install sf-skills.

    Args:
        dry_run: Preview changes without applying
        force: Skip confirmation prompts
        called_from_bash: Suppress redundant output (bash wrapper handles UX)

    Returns:
        Exit code (0 = success)
    """
    # When called from bash wrapper, skip banner and intro (bash handles it)
    if not called_from_bash:
        print_banner()

        # Show what will be installed
        print("""
  📦 WHAT WILL BE INSTALLED:
     • 18 Salesforce skills (sf-apex, sf-flow, sf-metadata, ...)
     • 14 hook scripts (guardrails, auto-approval, validation)
     • LSP engine (Apex, LWC, AgentScript language servers)
     • Automatic skill suggestions and workflow orchestration

  📍 INSTALL LOCATIONS:
     ~/.claude/skills/sf-*/     (skills — native Claude Code discovery)
     ~/.claude/hooks/           (hook scripts)
     ~/.claude/lsp-engine/      (LSP wrappers)
     ~/.claude/.sf-skills.json  (metadata)

  ⚙️  SETTINGS CHANGES:
     ~/.claude/settings.json - hooks will be registered
""")

    # Detect current state
    state, current_version = detect_state()

    if state == InstallState.UNIFIED and not force:
        print_info(f"sf-skills already installed (v{current_version})")
        print_info("Use --update to check for updates")
        return 0

    if state == InstallState.UNIFIED and force:
        print_info(f"Reinstalling sf-skills (current: v{current_version})")
    elif state == InstallState.MARKETPLACE:
        print_warning("Found marketplace installation (will be removed)")
    elif state == InstallState.LEGACY:
        print_warning(f"Found legacy installation (v{current_version}, will be removed)")
    elif state == InstallState.CORRUPTED:
        print_warning("Found corrupted installation (will be reinstalled)")

    # Confirm
    if not force and not dry_run:
        if not confirm("\nProceed with installation?"):
            print("\nInstallation cancelled.")
            return 1

    print()

    # Step 1: Download
    print_step(1, 5, "Downloading sf-skills...", "...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        if not download_repo_zip(tmp_path):
            print_step(1, 5, "Download failed", "fail")
            return 1

        # Find extracted directory
        extracted = list(tmp_path.glob(f"{GITHUB_REPO}-*"))
        if not extracted:
            print_error("Could not find extracted files")
            return 1

        source_dir = extracted[0]

        # Get version from skills-registry.json
        registry_file = source_dir / SKILLS_REGISTRY
        version = "1.0.0"
        if registry_file.exists():
            try:
                registry = json.loads(registry_file.read_text())
                version = registry.get("version", "1.0.0")
            except (json.JSONDecodeError, IOError):
                pass

        # Fetch commit SHA for content-aware update detection
        commit_sha = fetch_latest_commit_sha()

        print_step(1, 5, f"Downloaded sf-skills v{version}", "done")
        print_substep("Downloaded from GitHub")
        if commit_sha:
            print_substep(f"Commit: {commit_sha[:8]}...")

        # Step 2: Detect and cleanup existing installations
        print_step(2, 5, "Detecting existing installations...", "...")

        cleanups = []
        if state == InstallState.MARKETPLACE:
            cleanups.append(("Marketplace", lambda: cleanup_marketplace(dry_run)))
        if state == InstallState.LEGACY:
            cleanups.append(("Legacy hooks", lambda: cleanup_legacy(dry_run)))
        if state == InstallState.CORRUPTED:
            if (LEGACY_INSTALL_DIR.exists() or LEGACY_INSTALL_DIR.is_symlink()) and not dry_run:
                safe_rmtree(LEGACY_INSTALL_DIR)
            cleanups.append(("Corrupted install", lambda: True))

        # Remove old hooks from settings.json
        hooks_removed = cleanup_settings_hooks(dry_run)
        if hooks_removed > 0:
            cleanups.append((f"{hooks_removed} old hooks", lambda: True))

        if cleanups:
            for name, cleanup_fn in cleanups:
                cleanup_fn()
            print_step(2, 5, f"Found: {', '.join(c[0] for c in cleanups)} (cleaned)", "done")
        else:
            print_step(2, 5, "No existing installations found", "done")

        # Step 3: Install skills, hooks, and LSP engine
        print_step(3, 5, "Installing skills, hooks, and LSP engine...", "...")

        if not dry_run:
            # Copy skills to native discovery path
            skill_count = copy_skills(source_dir, SKILLS_DIR)

            # Copy hooks
            hooks_source = source_dir / "shared" / "hooks"
            hook_count = copy_hooks(hooks_source, HOOKS_DIR)

            # Copy LSP engine (wrapper scripts for Apex, LWC, AgentScript LSPs)
            lsp_source = source_dir / "shared" / "lsp-engine"
            lsp_count = copy_lsp_engine(lsp_source, LSP_DIR)

            # Copy FDE + PS agents to ~/.claude/agents/
            agents_target = CLAUDE_DIR / "agents"
            agent_count = copy_agents(source_dir, agents_target)

            # Copy installer for self-updates
            installer_source = source_dir / "tools" / "install.py"
            if installer_source.exists():
                shutil.copy2(installer_source, INSTALLER_FILE)

            # Write metadata (version + commit SHA for update detection)
            write_metadata(version, commit_sha=commit_sha)

            # Touch all files for cache refresh
            for d in [SKILLS_DIR, HOOKS_DIR, LSP_DIR]:
                if d.exists():
                    touch_all_files(d)

            print_step(3, 5, "Skills, hooks, and LSP engine installed", "done")
            print_substep(f"{skill_count} skills installed")
            print_substep(f"{hook_count} hook scripts installed")
            print_substep(f"{lsp_count} LSP engine files installed")
            if agent_count > 0:
                print_substep(f"{agent_count} agents installed (FDE + PS)")
        else:
            print_step(3, 5, "Would install skills, hooks, and LSP engine", "skip")

        # Step 4: Configure Claude Code
        print_step(4, 5, "Configuring Claude Code...", "...")

        if not dry_run:
            # Register hooks in settings.json
            status = update_settings_json()
            added = sum(1 for s in status.values() if s == "added")
            updated = sum(1 for s in status.values() if s == "updated")

            # Migrate: Remove legacy ~/.claude/sf-skills/ if present
            if LEGACY_INSTALL_DIR.exists():
                safe_rmtree(LEGACY_INSTALL_DIR)
                print_substep("Migrated: removed legacy ~/.claude/sf-skills/")

            # Migrate: Remove legacy command symlinks
            old_cmds = unregister_skills_from_commands()
            if old_cmds > 0:
                print_substep(f"Migrated: removed {old_cmds} legacy command symlinks")

            print_step(4, 5, "Claude Code configured", "done")
            if added > 0:
                print_substep(f"{added} hook events added")
            if updated > 0:
                print_substep(f"{updated} hook events updated")
        else:
            print_step(4, 5, "Would configure settings.json", "skip")

        # Step 5: Validate
        print_step(5, 5, "Validating installation...", "...")

        if not dry_run:
            success, issues = verify_installation()
            if success:
                print_step(5, 5, "All checks passed", "done")
            else:
                print_step(5, 5, "Validation issues found", "fail")
                for issue in issues:
                    print_substep(c(issue, Colors.YELLOW))
        else:
            print_step(5, 5, "Would validate installation", "skip")

        # Clean up temp files
        cleanup_temp_files(dry_run)

    # Success message
    if not dry_run:
        if called_from_bash:
            # Brief message when called from bash (bash wrapper shows detailed next steps)
            print(f"""
{c('✅ sf-skills installed successfully!', Colors.GREEN)}
   Version:  {version}
   Skills:   ~/.claude/skills/sf-*/
   Hooks:    ~/.claude/hooks/
""")
        else:
            # Full message when run directly
            print(f"""
═══════════════════════════════════════════════════════════════════
{c('✅ Installation complete!', Colors.GREEN)}

   Version:  {version}
   Skills:   ~/.claude/skills/sf-*/
   Hooks:    ~/.claude/hooks/
   LSP:      ~/.claude/lsp-engine/

   🚀 Next steps:
   1. Restart Claude Code (or start new session)
   2. Try: /sf-apex to start building!

   📖 Commands:
   • Update:    python3 ~/.claude/sf-skills-install.py --update
   • Uninstall: python3 ~/.claude/sf-skills-install.py --uninstall
   • Status:    python3 ~/.claude/sf-skills-install.py --status
═══════════════════════════════════════════════════════════════════
""")
    else:
        print(f"\n{c('DRY RUN complete - no changes made', Colors.YELLOW)}\n")

    return 0


def cmd_update(dry_run: bool = False, force: bool = False, force_update: bool = False) -> int:
    """
    Check for and apply updates.

    Compares both VERSION and commit SHA to detect updates:
    - Version bump: remote version > local version
    - Content change: same version but different commit SHA
    - Legacy upgrade: local install missing commit SHA tracking

    Args:
        dry_run: Preview changes without applying
        force: Skip confirmation prompts
        force_update: Force reinstall even if up-to-date

    Returns:
        Exit code (0 = success, 1 = error, 2 = no update available)
    """
    print_banner()

    state, current_version = detect_state()

    if state not in (InstallState.UNIFIED, InstallState.LEGACY):
        print_error("sf-skills is not installed")
        print_info("Run without --update to install")
        return 1

    # Read current fingerprint for SHA info
    fingerprint = read_fingerprint()
    local_sha = fingerprint.get("commit_sha") if fingerprint else None

    # Display current state
    print_info(f"Current version: {current_version or 'unknown'}")
    if local_sha:
        print_info(f"Current commit:  {local_sha[:8]}...")
    print_info("Checking for updates...")

    # Use centralized update detection logic
    update_needed, reason, details = needs_update()

    # Display remote state
    if details.get("remote_version"):
        print_info(f"Latest version:  {details['remote_version']}")
    if details.get("remote_sha"):
        print_info(f"Latest commit:   {details['remote_sha'][:8]}...")

    # Handle force-update flag
    if force_update:
        print_info("Force update requested")
        if not force and not dry_run:
            if not confirm("Reinstall sf-skills?"):
                print("\nUpdate cancelled.")
                return 1
        return cmd_install(dry_run=dry_run, force=True)

    # Handle network error
    if reason == UPDATE_REASON_ERROR:
        print_warning("Could not check for updates (network error)")
        return 1

    # Handle up-to-date
    if reason == UPDATE_REASON_UP_TO_DATE:
        print_success("Already up to date!")
        return 2

    # Display update reason
    if reason == UPDATE_REASON_VERSION_BUMP:
        print_info(f"Update available: {current_version} → {details['remote_version']}")
    elif reason == UPDATE_REASON_CONTENT_CHANGED:
        print_info(f"Content updated (same version {current_version}, new commit)")
        if local_sha and details.get("remote_sha"):
            print_info(f"Commit: {local_sha[:8]}... → {details['remote_sha'][:8]}...")
    elif reason == UPDATE_REASON_ENABLE_SHA_TRACKING:
        print_info("Update available: Enable content-aware update tracking")

    if not force and not dry_run:
        if not confirm("Apply update?"):
            print("\nUpdate cancelled.")
            return 1

    # Run full install (will handle cleanup of old version)
    return cmd_install(dry_run=dry_run, force=True)


def cmd_uninstall(dry_run: bool = False, force: bool = False) -> int:
    """
    Remove sf-skills installation.

    Returns:
        Exit code (0 = success)
    """
    print_banner()

    state, current_version = detect_state()

    if state == InstallState.FRESH:
        print_info("sf-skills is not installed")
        return 0

    print_warning("This will remove:")
    print(f"     • sf-* skills from {SKILLS_DIR}")
    print(f"     • {HOOKS_DIR}")
    print(f"     • {LSP_DIR}")
    print(f"     • sf-skills hooks from {SETTINGS_FILE}")
    print(f"     • FDE + PS agents from {CLAUDE_DIR / 'agents'}")
    print(f"     • {META_FILE}")
    print(f"     • {INSTALLER_FILE}")

    if not force and not dry_run:
        if not confirm("\nProceed with uninstallation?", default=False):
            print("\nUninstallation cancelled.")
            return 1

    print()

    # Remove hooks from settings.json
    hooks_removed = cleanup_settings_hooks(dry_run)
    if hooks_removed > 0:
        print_success(f"Removed {hooks_removed} hooks from settings.json")

    # Remove all installed files (skills, hooks, lsp, metadata, installer)
    if not dry_run:
        cleanup_installed_files()
        print_success("Removed sf-skills files from native layout")

    # Remove legacy command symlinks
    skills_removed = unregister_skills_from_commands(dry_run)
    if skills_removed > 0:
        print_success(f"Removed {skills_removed} legacy command symlinks")

    # Remove FDE + PS agent files from ~/.claude/agents/ (preserves user's custom agents)
    agents_removed = cleanup_agents(CLAUDE_DIR / "agents", dry_run)
    if agents_removed > 0:
        print_success(f"Removed {agents_removed} agents from {CLAUDE_DIR / 'agents'}")

    # Remove legacy installation directory if present
    if LEGACY_INSTALL_DIR.exists() or LEGACY_INSTALL_DIR.is_symlink():
        if not dry_run:
            safe_rmtree(LEGACY_INSTALL_DIR)
        print_success(f"Removed legacy: {LEGACY_INSTALL_DIR}")

    # Clean up legacy if present
    cleanup_legacy(dry_run)
    cleanup_marketplace(dry_run)

    # Clean temp files
    temp_removed = cleanup_temp_files(dry_run)
    if temp_removed > 0:
        print_success(f"Removed {temp_removed} temp files")

    if not dry_run:
        print(f"""
═══════════════════════════════════════════════════════════════════
{c('✅ Uninstallation complete!', Colors.GREEN)}

   Restart Claude Code to apply changes.

   To reinstall:
   curl -sSL https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/tools/install.py | python3
═══════════════════════════════════════════════════════════════════
""")

    return 0


def cmd_status() -> int:
    """
    Show installation status.

    Returns:
        Exit code (0 = installed, 1 = not installed)
    """
    print_banner()

    state, current_version = detect_state()

    print("sf-skills Status")
    print("════════════════════════════════════════")

    if state == InstallState.FRESH:
        print(f"Status:      {c('❌ NOT INSTALLED', Colors.RED)}")
        print(f"\nTo install:")
        print(f"  curl -sSL https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/tools/install.py | python3")
        return 1

    if state == InstallState.UNIFIED:
        print(f"Status:      {c('✅ INSTALLED', Colors.GREEN)}")
        print(f"Method:      Unified installer (native layout)")
    elif state == InstallState.LEGACY:
        print(f"Status:      {c('⚠️ LEGACY INSTALL', Colors.YELLOW)}")
        print(f"Method:      Old hooks-only install")
    elif state == InstallState.MARKETPLACE:
        print(f"Status:      {c('⚠️ MARKETPLACE INSTALL', Colors.YELLOW)}")
        print(f"Method:      Marketplace (deprecated)")
    elif state == InstallState.CORRUPTED:
        print(f"Status:      {c('❌ CORRUPTED', Colors.RED)}")
        print(f"Action:      Run installer to repair")

    print(f"Version:     {current_version or 'unknown'}")

    # Display commit SHA from metadata
    metadata = read_metadata()
    if metadata and metadata.get("commit_sha"):
        sha = metadata["commit_sha"]
        print(f"Commit:      {sha[:8]}... (full: {sha})")
    else:
        print(f"Commit:      {c('not tracked', Colors.DIM)} (run --update to enable)")

    # Show locations
    print(f"Skills:      {SKILLS_DIR}")
    print(f"Hooks:       {HOOKS_DIR}")
    print(f"LSP Engine:  {LSP_DIR}")
    print(f"Metadata:    {META_FILE}")

    # Count skills
    if SKILLS_DIR.exists():
        skill_count = sum(1 for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name.startswith("sf-"))
        print(f"Skill count: {skill_count} installed")

    # Count hooks
    if HOOKS_DIR.exists():
        hook_count = sum(1 for _ in HOOKS_DIR.rglob("*.py"))
        print(f"Hook count:  {hook_count} scripts")

    # Check LSP engine
    if LSP_DIR.exists():
        wrapper_count = sum(1 for _ in LSP_DIR.glob("*_wrapper.sh"))
        print(f"LSP count:   {wrapper_count} wrappers (Apex, LWC, AgentScript)")
    else:
        print(f"LSP count:   {c('⚠️ Not installed', Colors.YELLOW)}")

    # Check settings.json
    if SETTINGS_FILE.exists():
        try:
            settings = json.loads(SETTINGS_FILE.read_text())
            if "hooks" in settings:
                sf_hook_count = 0
                for event_hooks in settings["hooks"].values():
                    for hook in event_hooks:
                        if hook.get("_sf_skills"):
                            sf_hook_count += 1
                print(f"Settings:    {SETTINGS_FILE} {c('✓', Colors.GREEN)} ({sf_hook_count} hook configs)")
            else:
                print(f"Settings:    {c('⚠️ No hooks registered', Colors.YELLOW)}")
        except json.JSONDecodeError:
            print(f"Settings:    {c('⚠️ Invalid JSON', Colors.YELLOW)}")
    else:
        print(f"Settings:    {c('⚠️ Not found', Colors.YELLOW)}")

    # Read metadata for timestamps
    if metadata:
        installed_at = metadata.get("installed_at", "unknown")
        if installed_at != "unknown":
            # Parse and format date
            try:
                dt = datetime.fromisoformat(installed_at)
                installed_at = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        print(f"\nLast updated: {installed_at}")

    print("════════════════════════════════════════\n")

    # Check for updates using centralized detection
    print_info("Checking for updates...")
    update_needed, reason, details = needs_update()

    if reason == UPDATE_REASON_ERROR:
        print_warning("Could not check for updates (network error)")
    elif reason == UPDATE_REASON_UP_TO_DATE:
        print_success("Up to date!")
    elif reason == UPDATE_REASON_VERSION_BUMP:
        print_warning(f"Update available: v{current_version} → v{details['remote_version']}")
        print_info("Run with --update to apply")
    elif reason == UPDATE_REASON_CONTENT_CHANGED:
        print_warning(f"Content updated (same version, new commit)")
        if details.get("local_sha") and details.get("remote_sha"):
            print_info(f"Commit: {details['local_sha'][:8]}... → {details['remote_sha'][:8]}...")
        print_info("Run with --update to apply")
    elif reason == UPDATE_REASON_ENABLE_SHA_TRACKING:
        print_warning("Update available: Enable content-aware update tracking")
        print_info("Run with --update to apply")

    return 0


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="sf-skills Unified Installer for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 install.py               # Interactive install
  python3 install.py --update      # Check version + content changes
  python3 install.py --force-update  # Force reinstall even if up-to-date
  python3 install.py --uninstall   # Remove sf-skills
  python3 install.py --status      # Show installation status
  python3 install.py --dry-run     # Preview changes
  python3 install.py --force       # Skip confirmations

Curl one-liner:
  curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.py | python3
        """
    )

    parser.add_argument("--update", action="store_true",
                        help="Check and apply updates (version + content)")
    parser.add_argument("--force-update", action="store_true",
                        help="Force reinstall even if up-to-date")
    parser.add_argument("--uninstall", action="store_true",
                        help="Remove sf-skills installation")
    parser.add_argument("--status", action="store_true",
                        help="Show installation status")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without applying")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Skip confirmation prompts")
    parser.add_argument("--called-from-bash", action="store_true",
                        help="Called from bash wrapper (suppress redundant output)")
    parser.add_argument("--version", action="version",
                        version=f"sf-skills installer v{VERSION}")

    args = parser.parse_args()

    # Ensure ~/.claude exists
    if not CLAUDE_DIR.exists():
        print_error("Claude Code not found (~/.claude/ does not exist)")
        print_info("Please install Claude Code first: https://claude.ai/code")
        sys.exit(1)

    # Auto-migration: if running from legacy location, migrate to native layout
    if not args.uninstall:
        try:
            this_file = Path(__file__).resolve()
            if (LEGACY_INSTALL_DIR.exists()
                    and not META_FILE.exists()
                    and this_file.is_relative_to(LEGACY_INSTALL_DIR.resolve())):
                result = migrate_legacy_layout(dry_run=args.dry_run)
                if result and not args.dry_run:
                    # Re-exec from new location if user passed --update/--status
                    if args.update or args.force_update or args.status:
                        print_info(f"Re-running from {INSTALLER_FILE}...")
                        os.execv(sys.executable, [
                            sys.executable, str(INSTALLER_FILE)
                        ] + sys.argv[1:])
                    sys.exit(0)
        except (ValueError, OSError):
            pass  # is_relative_to may fail on some platforms

    # Route to appropriate command
    if args.status:
        sys.exit(cmd_status())
    elif args.uninstall:
        sys.exit(cmd_uninstall(dry_run=args.dry_run, force=args.force))
    elif args.update or args.force_update:
        sys.exit(cmd_update(
            dry_run=args.dry_run,
            force=args.force,
            force_update=args.force_update
        ))
    else:
        sys.exit(cmd_install(
            dry_run=args.dry_run,
            force=args.force,
            called_from_bash=args.called_from_bash
        ))


if __name__ == "__main__":
    main()
