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

# Installation paths
CLAUDE_DIR = Path.home() / ".claude"
INSTALL_DIR = CLAUDE_DIR / "sf-skills"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

# Legacy paths to clean up
LEGACY_HOOKS_DIR = CLAUDE_DIR / "sf-skills-hooks"
MARKETPLACE_DIR = CLAUDE_DIR / "plugins" / "marketplaces" / "sf-skills"

# GitHub repository info
GITHUB_OWNER = "Jaganpro"
GITHUB_REPO = "sf-skills"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main"

# Files to install
SKILLS_GLOB = "sf-*"  # All skill directories
HOOKS_DIR = "shared/hooks"
LSP_ENGINE_DIR = "shared/lsp-engine"
SKILLS_REGISTRY = "shared/hooks/skills-registry.json"

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


def read_fingerprint() -> Optional[Dict[str, Any]]:
    """Read .install-fingerprint if it exists."""
    fingerprint_file = INSTALL_DIR / ".install-fingerprint"
    if fingerprint_file.exists():
        try:
            return json.loads(fingerprint_file.read_text())
        except (json.JSONDecodeError, IOError):
            return None
    return None


def get_installed_version() -> Optional[str]:
    """Read VERSION file from installation directory."""
    version_file = INSTALL_DIR / "VERSION"
    if version_file.exists():
        try:
            return version_file.read_text().strip()
        except IOError:
            return None
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

    # Check for unified installation
    if INSTALL_DIR.exists():
        fingerprint = read_fingerprint()
        if fingerprint and fingerprint.get("method") == "unified":
            version = get_installed_version()
            return InstallState.UNIFIED, version
        # Directory exists but no fingerprint - corrupted
        if (INSTALL_DIR / "VERSION").exists() or (INSTALL_DIR / "skills").exists():
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
    if "sf-skills" in command or "shared/hooks" in command:
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
    hooks_path = str(INSTALL_DIR / "hooks")
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


def write_fingerprint(version: str, source: str = "github", commit_sha: Optional[str] = None):
    """
    Write installation fingerprint file.

    Args:
        version: Version string from skills-registry.json
        source: Installation source (default: "github")
        commit_sha: Git commit SHA for content-aware update detection
    """
    fingerprint = {
        "method": "unified",
        "version": version,
        "source": source,
        "installed_at": datetime.now().isoformat(),
        "installer_version": VERSION
    }

    # Add commit SHA for content-aware update detection
    if commit_sha:
        fingerprint["commit_sha"] = commit_sha

    fingerprint_file = INSTALL_DIR / ".install-fingerprint"
    fingerprint_file.write_text(json.dumps(fingerprint, indent=2))


def write_version_file(version: str):
    """Write VERSION file."""
    version_file = INSTALL_DIR / "VERSION"
    version_file.write_text(f"{version}\n")


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

    # Check VERSION file
    if not (INSTALL_DIR / "VERSION").exists():
        issues.append("Missing VERSION file")

    # Check fingerprint
    if not (INSTALL_DIR / ".install-fingerprint").exists():
        issues.append("Missing .install-fingerprint")

    # Check skills directory
    skills_dir = INSTALL_DIR / "skills"
    if not skills_dir.exists():
        issues.append("Missing skills directory")
    else:
        skill_count = sum(1 for d in skills_dir.iterdir() if d.is_dir() and d.name.startswith("sf-"))
        if skill_count == 0:
            issues.append("No skills found")

    # Check hooks directory
    hooks_dir = INSTALL_DIR / "hooks"
    if not hooks_dir.exists():
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
            if not (hooks_dir / script).exists():
                issues.append(f"Missing: hooks/{script}")

    # Check lsp-engine directory
    lsp_dir = INSTALL_DIR / "lsp-engine"
    if not lsp_dir.exists():
        issues.append("Missing lsp-engine directory")
    else:
        # Check key wrapper scripts
        required_wrappers = [
            "apex_wrapper.sh",
            "lwc_wrapper.sh",
            "agentscript_wrapper.sh"
        ]
        for wrapper in required_wrappers:
            if not (lsp_dir / wrapper).exists():
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

  📍 INSTALL LOCATION:
     ~/.claude/sf-skills/

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
            if (INSTALL_DIR.exists() or INSTALL_DIR.is_symlink()) and not dry_run:
                safe_rmtree(INSTALL_DIR)
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
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)

            # Copy skills
            skills_target = INSTALL_DIR / "skills"
            skill_count = copy_skills(source_dir, skills_target)

            # Copy hooks
            hooks_source = source_dir / "shared" / "hooks"
            hooks_target = INSTALL_DIR / "hooks"
            hook_count = copy_hooks(hooks_source, hooks_target)

            # Copy LSP engine (wrapper scripts for Apex, LWC, AgentScript LSPs)
            lsp_source = source_dir / "shared" / "lsp-engine"
            lsp_target = INSTALL_DIR / "lsp-engine"
            lsp_count = copy_lsp_engine(lsp_source, lsp_target)

            # Copy tools (includes install.py for local updates)
            tools_source = source_dir / "tools"
            tools_target = INSTALL_DIR / "tools"
            copy_tools(tools_source, tools_target)

            # Write VERSION and fingerprint (with commit SHA for update detection)
            write_version_file(version)
            write_fingerprint(version, commit_sha=commit_sha)

            # Touch all files
            touch_all_files(INSTALL_DIR)

            print_step(3, 5, "Skills, hooks, and LSP engine installed", "done")
            print_substep(f"{skill_count} skills installed")
            print_substep(f"{hook_count} hook scripts installed")
            print_substep(f"{lsp_count} LSP engine files installed")
        else:
            print_step(3, 5, "Would install skills, hooks, and LSP engine", "skip")

        # Step 4: Configure Claude Code
        print_step(4, 5, "Configuring Claude Code...", "...")

        if not dry_run:
            # Register hooks in settings.json
            status = update_settings_json()
            added = sum(1 for s in status.values() if s == "added")
            updated = sum(1 for s in status.values() if s == "updated")

            # Register skills as commands (symlinks in ~/.claude/commands/)
            skills_dir = INSTALL_DIR / "skills"
            skills_registered = register_skills_as_commands(skills_dir)

            print_step(4, 5, "Claude Code configured", "done")
            if added > 0:
                print_substep(f"{added} hook events added")
            if updated > 0:
                print_substep(f"{updated} hook events updated")
            print_substep(f"{skills_registered} skills registered as commands")
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
   Location: ~/.claude/sf-skills/
""")
        else:
            # Full message when run directly
            print(f"""
═══════════════════════════════════════════════════════════════════
{c('✅ Installation complete!', Colors.GREEN)}

   Version:  {version}
   Location: ~/.claude/sf-skills/

   🚀 Next steps:
   1. Restart Claude Code (or start new session)
   2. Try: /sf-apex to start building!

   📖 Commands:
   • Update:    python3 ~/.claude/sf-skills/tools/install.py --update
   • Uninstall: python3 ~/.claude/sf-skills/tools/install.py --uninstall
   • Status:    python3 ~/.claude/sf-skills/tools/install.py --status
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
    print(f"     • {INSTALL_DIR}")
    print(f"     • sf-skills hooks from {SETTINGS_FILE}")
    print(f"     • sf-skills commands from {COMMANDS_DIR}")

    if not force and not dry_run:
        if not confirm("\nProceed with uninstallation?", default=False):
            print("\nUninstallation cancelled.")
            return 1

    print()

    # Remove hooks from settings.json
    hooks_removed = cleanup_settings_hooks(dry_run)
    if hooks_removed > 0:
        print_success(f"Removed {hooks_removed} hooks from settings.json")

    # Remove skill symlinks from ~/.claude/commands/
    skills_removed = unregister_skills_from_commands(dry_run)
    if skills_removed > 0:
        print_success(f"Removed {skills_removed} skill commands from {COMMANDS_DIR}")

    # Remove installation directory
    if INSTALL_DIR.exists() or INSTALL_DIR.is_symlink():
        if not dry_run:
            safe_rmtree(INSTALL_DIR)
        print_success(f"Removed: {INSTALL_DIR}")

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
        print(f"Method:      Unified installer")
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

    # Display commit SHA from fingerprint
    fingerprint = read_fingerprint()
    if fingerprint and fingerprint.get("commit_sha"):
        sha = fingerprint["commit_sha"]
        print(f"Commit:      {sha[:8]}... (full: {sha})")
    else:
        print(f"Commit:      {c('not tracked', Colors.DIM)} (run --update to enable)")

    print(f"Location:    {INSTALL_DIR}")

    # Count skills
    skills_dir = INSTALL_DIR / "skills"
    if skills_dir.exists():
        skill_count = sum(1 for d in skills_dir.iterdir() if d.is_dir() and d.name.startswith("sf-"))
        print(f"Skills:      {skill_count} installed")

    # Count hooks
    hooks_dir = INSTALL_DIR / "hooks"
    if hooks_dir.exists():
        hook_count = sum(1 for _ in hooks_dir.rglob("*.py"))
        print(f"Hooks:       {hook_count} scripts")

    # Check LSP engine
    lsp_dir = INSTALL_DIR / "lsp-engine"
    if lsp_dir.exists():
        wrapper_count = sum(1 for _ in lsp_dir.glob("*_wrapper.sh"))
        print(f"LSP Engine:  {wrapper_count} wrappers (Apex, LWC, AgentScript)")
    else:
        print(f"LSP Engine:  {c('⚠️ Not installed', Colors.YELLOW)}")

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

    # Read fingerprint for more details (use already-read fingerprint)
    if fingerprint:
        installed_at = fingerprint.get("installed_at", "unknown")
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
