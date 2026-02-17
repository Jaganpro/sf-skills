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
    python3 install.py --diagnose    # Run diagnostic checks
    python3 install.py --restore-settings  # Restore settings.json from backup
    python3 install.py --dry-run      # Preview changes
    python3 install.py --force        # Skip confirmations

    # Profile management (personal/enterprise config switching):
    python3 install.py --profile list             # List saved profiles
    python3 install.py --profile save personal    # Save current config as profile
    python3 install.py --profile use enterprise   # Switch to enterprise config
    python3 install.py --profile show enterprise  # View profile (tokens redacted)
    python3 install.py --profile delete old       # Delete a profile

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
import re
import shutil
import ssl
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

VERSION = "1.2.0"  # Installer version

# Installation paths (Claude Code native layout)
CLAUDE_DIR = Path.home() / ".claude"
SKILLS_DIR = CLAUDE_DIR / "skills"
HOOKS_DIR = CLAUDE_DIR / "hooks"
LSP_DIR = CLAUDE_DIR / "lsp-engine"
META_FILE = CLAUDE_DIR / ".sf-skills.json"
INSTALLER_FILE = CLAUDE_DIR / "sf-skills-install.py"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
SETTINGS_BACKUP_DIR = CLAUDE_DIR / ".settings-backups"
MAX_SETTINGS_BACKUPS = 5

# Profile management
PROFILE_PREFIX = "settings."
PROFILE_SUFFIX = ".json"

# Keys preserved across profile switches (user preferences + sf-skills config)
PERSISTENT_KEYS = frozenset({
    "hooks", "permissions", "statusLine", "attribution",
    "cleanupPeriodDays", "outputStyle", "enabledPlugins",
})

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


# ============================================================================
# ENTERPRISE DETECTION
# ============================================================================

class Environment:
    """Claude Code environment types."""
    PERSONAL = "personal"
    ENTERPRISE = "enterprise"
    UNKNOWN = "unknown"


def _detect_env_from_dict(settings: Dict[str, Any]) -> str:
    """Detect environment type from a settings dict.

    Detection priority:
    1. CLAUDE_CODE_USE_BEDROCK=1 → enterprise (strongest signal)
    2. ANTHROPIC_BEDROCK_BASE_URL present → enterprise
    3. forceLoginMethod=console + ANTHROPIC_AUTH_TOKEN → enterprise
    4. forceLoginMethod=claudeai → personal
    5. forceLoginOrgUUID present → personal
    6. Otherwise → unknown
    """
    env = settings.get("env", {})
    if env.get("CLAUDE_CODE_USE_BEDROCK") == "1":
        return Environment.ENTERPRISE
    if env.get("ANTHROPIC_BEDROCK_BASE_URL"):
        return Environment.ENTERPRISE
    if settings.get("forceLoginMethod") == "console" and env.get("ANTHROPIC_AUTH_TOKEN"):
        return Environment.ENTERPRISE
    if settings.get("forceLoginMethod") == "claudeai":
        return Environment.PERSONAL
    if settings.get("forceLoginOrgUUID"):
        return Environment.PERSONAL
    return Environment.UNKNOWN


def detect_environment() -> Tuple[str, Dict[str, Any]]:
    """Auto-detect personal vs enterprise from settings.json.

    Returns:
        Tuple of (environment_type, details_dict)
    """
    if not SETTINGS_FILE.exists():
        return Environment.UNKNOWN, {}
    try:
        settings = json.loads(SETTINGS_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return Environment.UNKNOWN, {}
    env_type = _detect_env_from_dict(settings)
    details = {
        "login_method": settings.get("forceLoginMethod", "unknown"),
        "model": settings.get("model", "unknown"),
        "bedrock": settings.get("env", {}).get("CLAUDE_CODE_USE_BEDROCK", "0"),
    }
    return env_type, details


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
# SSL CERTIFICATE HANDLING
# ============================================================================

_SSL_CONTEXT_CACHE: Optional[ssl.SSLContext] = None
_SSL_ERROR_SHOWN = False


def _build_ssl_context() -> ssl.SSLContext:
    """
    Build the best available SSL context for urllib.

    Priority:
    1. SSL_CERT_FILE env var (explicit user/corporate override)
    2. certifi package (common on python.org installs where pip exists)
    3. Default ssl.create_default_context() (works on Homebrew Python / Linux)

    Never disables certificate verification — security must be preserved
    since this installer downloads executable code from GitHub.
    """
    # Priority 1: Explicit SSL_CERT_FILE environment variable
    cert_file = os.environ.get("SSL_CERT_FILE")
    if cert_file and os.path.isfile(cert_file):
        ctx = ssl.create_default_context(cafile=cert_file)
        return ctx

    # Priority 2: certifi package (auto-detect)
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
        return ctx
    except ImportError:
        pass

    # Priority 3: System default (works on Homebrew Python, Linux, etc.)
    return ssl.create_default_context()


def _get_ssl_context() -> ssl.SSLContext:
    """Lazy-cached wrapper that calls _build_ssl_context() once."""
    global _SSL_CONTEXT_CACHE
    if _SSL_CONTEXT_CACHE is None:
        _SSL_CONTEXT_CACHE = _build_ssl_context()
    return _SSL_CONTEXT_CACHE


def _print_ssl_troubleshooting():
    """Print SSL certificate troubleshooting steps."""
    print()
    print_error("SSL certificate verification failed")
    print_info("This is common with python.org installs on macOS.")
    print()
    print(c("  Fix options (try in order):", Colors.BOLD))
    print()
    print("  1. Run the macOS certificate installer:")
    print('     /Applications/Python\\ 3.*/Install\\ Certificates.command')
    print()
    print("  2. Install certifi and set SSL_CERT_FILE:")
    print("     pip3 install certifi")
    print('     export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")')
    print("     Then re-run this installer.")
    print()
    print("  3. Use Homebrew Python (includes proper CA certs):")
    print("     brew install python3")
    print()
    print("  4. Corporate proxy? Set SSL_CERT_FILE to your CA bundle:")
    print("     export SSL_CERT_FILE=/path/to/corporate-ca-bundle.pem")
    print()


def _handle_ssl_error(e: Exception) -> bool:
    """
    Detect if an exception is SSL-related and print troubleshooting once.

    Args:
        e: The caught exception (typically urllib.error.URLError)

    Returns:
        True if the error was SSL-related, False otherwise
    """
    global _SSL_ERROR_SHOWN

    is_ssl = False

    # Check URLError wrapping an SSL error
    if isinstance(e, urllib.error.URLError) and hasattr(e, 'reason'):
        if isinstance(e.reason, (ssl.SSLCertVerificationError, ssl.SSLError)):
            is_ssl = True
    # Direct SSL errors
    elif isinstance(e, (ssl.SSLCertVerificationError, ssl.SSLError)):
        is_ssl = True

    if is_ssl and not _SSL_ERROR_SHOWN:
        _SSL_ERROR_SHOWN = True
        _print_ssl_troubleshooting()

    return is_ssl


# ============================================================================
# GITHUB OPERATIONS
# ============================================================================

def fetch_latest_release() -> Optional[Dict[str, Any]]:
    """Fetch latest release info from GitHub API."""
    try:
        url = f"{GITHUB_API_URL}/releases/latest"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10, context=_get_ssl_context()) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        _handle_ssl_error(e)
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
        with urllib.request.urlopen(req, timeout=10, context=_get_ssl_context()) as response:
            return response.read().decode().strip()
    except (urllib.error.URLError, TimeoutError) as e:
        _handle_ssl_error(e)
        return None


def fetch_registry_version() -> Optional[str]:
    """Fetch version from skills-registry.json on main branch."""
    try:
        url = f"{GITHUB_RAW_URL}/{SKILLS_REGISTRY}"
        with urllib.request.urlopen(url, timeout=10, context=_get_ssl_context()) as response:
            data = json.loads(response.read().decode())
            return data.get("version")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        _handle_ssl_error(e)
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

            with urllib.request.urlopen(zip_url, timeout=60, context=_get_ssl_context()) as response:
                tmp_file.write(response.read())

        # Extract
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

        # Clean up
        tmp_path.unlink()

        return True

    except (urllib.error.URLError, zipfile.BadZipFile, IOError) as e:
        if not _handle_ssl_error(e):
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
    except json.JSONDecodeError:
        print_warning("settings.json is invalid JSON — skipping hook cleanup")
        print_info(f"Run: python3 {INSTALLER_FILE} --diagnose")
        return 0
    except IOError:
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
# SETTINGS BACKUP & RESTORE
# ============================================================================

def backup_settings(reason: str = "pre-install") -> Optional[Path]:
    """
    Create a timestamped backup of settings.json.

    Args:
        reason: Tag for the backup filename (e.g., "pre-install", "corrupt", "pre-modify")

    Returns:
        Path to the backup file, or None if settings.json doesn't exist
    """
    if not SETTINGS_FILE.exists():
        return None

    SETTINGS_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"settings.{reason}.{timestamp}.json"
    backup_path = SETTINGS_BACKUP_DIR / backup_name

    shutil.copy2(SETTINGS_FILE, backup_path)
    _prune_old_backups()

    return backup_path


def _prune_old_backups():
    """Remove oldest backups beyond MAX_SETTINGS_BACKUPS."""
    if not SETTINGS_BACKUP_DIR.exists():
        return

    backups = sorted(
        SETTINGS_BACKUP_DIR.glob("settings.*.json"),
        key=lambda p: p.stat().st_mtime
    )

    while len(backups) > MAX_SETTINGS_BACKUPS:
        oldest = backups.pop(0)
        oldest.unlink()


def get_latest_backup() -> Optional[Path]:
    """Return the newest settings backup file, or None if no backups exist."""
    if not SETTINGS_BACKUP_DIR.exists():
        return None

    backups = sorted(
        SETTINGS_BACKUP_DIR.glob("settings.*.json"),
        key=lambda p: p.stat().st_mtime
    )

    return backups[-1] if backups else None


def restore_settings_from_backup(backup_path: Optional[Path] = None) -> bool:
    """
    Restore settings.json from a backup file.

    Args:
        backup_path: Specific backup to restore. If None, uses the latest.

    Returns:
        True if restore succeeded, False otherwise
    """
    if backup_path is None:
        backup_path = get_latest_backup()

    if backup_path is None or not backup_path.exists():
        print_error("No backup file found")
        return False

    # Validate backup is valid JSON
    try:
        content = backup_path.read_text()
        json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print_error(f"Backup file is not valid JSON: {e}")
        return False

    # Write to settings.json
    SETTINGS_FILE.write_text(content)
    return True


# ============================================================================
# SETTINGS PROFILE MANAGEMENT
# ============================================================================

def _validate_profile_name(name: str) -> bool:
    """Validate a profile name.

    Rules: 1-30 chars, alphanumeric + hyphens, must start with letter/digit.
    Reserved names are rejected.
    """
    if not name or len(name) > 30:
        return False
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*$', name):
        return False
    reserved = {"json", "backup", "backups", "settings"}
    if name.lower() in reserved:
        return False
    return True


def _redact_auth_token(env_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of env dict with auth tokens redacted for display."""
    sensitive_keys = {"ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"}
    result = {}
    for k, v in env_dict.items():
        if k in sensitive_keys and isinstance(v, str) and len(v) > 6:
            result[k] = v[:6] + "..."
        else:
            result[k] = v
    return result


def list_profiles() -> List[Dict[str, Any]]:
    """List all saved settings profiles.

    Scans ~/.claude/settings.*.json (excludes main settings.json).

    Returns:
        List of {name, path, environment, model} dicts, sorted by name.
    """
    profiles = []
    for p in sorted(CLAUDE_DIR.glob(f"{PROFILE_PREFIX}*{PROFILE_SUFFIX}")):
        # Skip the main settings.json
        if p.name == "settings.json":
            continue
        # Extract profile name from settings.{name}.json
        name = p.name[len(PROFILE_PREFIX):-len(PROFILE_SUFFIX)]
        if not name:
            continue
        try:
            data = json.loads(p.read_text())
            env_type = _detect_env_from_dict(data)
            model = data.get("model", "default")
            profiles.append({
                "name": name,
                "path": p,
                "environment": env_type,
                "model": model,
            })
        except (json.JSONDecodeError, IOError):
            profiles.append({
                "name": name,
                "path": p,
                "environment": "invalid",
                "model": "?",
            })
    return profiles


def load_profile(name: str) -> Optional[Dict[str, Any]]:
    """Load a named profile from disk.

    Args:
        name: Profile name (e.g., "personal", "enterprise")

    Returns:
        Parsed settings dict, or None if not found/invalid.
    """
    profile_path = CLAUDE_DIR / f"{PROFILE_PREFIX}{name}{PROFILE_SUFFIX}"
    if not profile_path.exists():
        return None
    try:
        return json.loads(profile_path.read_text())
    except (json.JSONDecodeError, IOError):
        return None


def save_profile(name: str, force: bool = False) -> bool:
    """Save current auth-layer settings as a named profile.

    Strips PERSISTENT_KEYS (hooks, permissions, etc.) so the profile
    contains only the auth/environment layer.

    Args:
        name: Profile name
        force: Overwrite existing profile

    Returns:
        True on success
    """
    if not _validate_profile_name(name):
        print_error(f"Invalid profile name: '{name}'")
        print_info("Use 1-30 alphanumeric chars and hyphens (e.g., 'personal', 'enterprise')")
        return False

    profile_path = CLAUDE_DIR / f"{PROFILE_PREFIX}{name}{PROFILE_SUFFIX}"
    if profile_path.exists() and not force:
        print_error(f"Profile '{name}' already exists (use --force to overwrite)")
        return False

    if not SETTINGS_FILE.exists():
        print_error("settings.json not found — nothing to save")
        return False

    try:
        settings = json.loads(SETTINGS_FILE.read_text())
    except (json.JSONDecodeError, IOError) as e:
        print_error(f"Cannot read settings.json: {e}")
        return False

    # Strip persistent keys — profile should only contain auth layer
    profile_data = {k: v for k, v in settings.items() if k not in PERSISTENT_KEYS}

    profile_path.write_text(json.dumps(profile_data, indent=2))
    return True


def apply_profile(name: str, dry_run: bool = False) -> bool:
    """Switch to a named profile, preserving user preferences.

    Merge strategy: profile provides auth layer, current settings
    provide user preferences (hooks, permissions, statusLine, etc.).

    Args:
        name: Profile name to switch to
        dry_run: Preview changes without applying

    Returns:
        True on success
    """
    profile_data = load_profile(name)
    if profile_data is None:
        print_error(f"Profile '{name}' not found or invalid")
        available = list_profiles()
        if available:
            print_info(f"Available profiles: {', '.join(p['name'] for p in available)}")
        return False

    # Load current settings for persistent keys
    current = {}
    if SETTINGS_FILE.exists():
        try:
            current = json.loads(SETTINGS_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            print_warning("Current settings.json unreadable — proceeding with profile only")

    # Build merged settings: start with profile (auth layer only)
    merged = {k: v for k, v in profile_data.items() if k not in PERSISTENT_KEYS}

    # Overlay persistent keys from current settings
    for key in PERSISTENT_KEYS:
        if key in current:
            merged[key] = current[key]

    if dry_run:
        env_type = _detect_env_from_dict(merged)
        print_info(f"Would switch to profile '{name}' ({env_type})")
        print_info(f"Auth layer: {', '.join(k for k in merged if k not in PERSISTENT_KEYS)}")
        preserved = [k for k in PERSISTENT_KEYS if k in merged]
        if preserved:
            print_info(f"Preserved from current: {', '.join(preserved)}")
        return True

    # Backup current settings before switching
    backup_settings(reason="pre-profile-switch")

    # Write merged settings
    SETTINGS_FILE.write_text(json.dumps(merged, indent=2))

    # Validate the write
    original_keys = set(current.keys()) if current else set()
    _validate_settings_write(original_keys)

    return True


def delete_profile(name: str) -> bool:
    """Delete a saved profile.

    Args:
        name: Profile name to delete

    Returns:
        True if deleted, False if not found
    """
    profile_path = CLAUDE_DIR / f"{PROFILE_PREFIX}{name}{PROFILE_SUFFIX}"
    if not profile_path.exists():
        print_error(f"Profile '{name}' not found")
        return False
    profile_path.unlink()
    return True


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
        ],
        "PostToolUse": [
            {
                "matcher": "Write|Edit",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"python3 {scripts_path}/validator-dispatcher.py",
                        "timeout": 10000
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
            },
            {
                "matcher": "Read",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {scripts_path}/auto-approve.py",
                    "timeout": 5000
                }],
                "_sf_skills": True
            }
        ],
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
    Register hooks in settings.json with backup and validation.

    Creates a pre-modification backup before writing, validates the write
    afterward, and aborts on corrupt input rather than silently overwriting.

    Returns:
        Status dict mapping event_name -> "added" | "updated" | "unchanged"
    """
    # Load existing settings
    settings = {}
    original_keys: set = set()
    if SETTINGS_FILE.exists():
        try:
            settings = json.loads(SETTINGS_FILE.read_text())
            original_keys = set(settings.keys())
        except json.JSONDecodeError as e:
            print_error(f"settings.json contains invalid JSON (line {e.lineno}, col {e.colno})")
            corrupt_backup = backup_settings(reason="corrupt")
            if corrupt_backup:
                print_info(f"Corrupt file backed up to: {corrupt_backup}")
            print_error("Cannot safely modify settings.json — aborting")
            print_info(f"Fix: python3 {INSTALLER_FILE} --restore-settings")
            sys.exit(1)

    # Upsert hooks
    hooks_config = get_hooks_config()
    new_settings, status = upsert_hooks(settings, hooks_config)

    if not dry_run:
        # Pre-modification backup (before we touch the file)
        backup_settings(reason="pre-modify")

        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(new_settings, indent=2))

        # Post-write validation
        _validate_settings_write(original_keys)

    return status


def _validate_settings_write(original_keys: set):
    """
    Validate that settings.json was written correctly.

    Re-reads the file, parses it, and verifies all original top-level keys
    are still present. If keys are missing, auto-restores from backup.

    Args:
        original_keys: Set of top-level key names from the pre-write settings
    """
    if not original_keys:
        return  # Nothing to validate (fresh install)

    try:
        written = json.loads(SETTINGS_FILE.read_text())
        written_keys = set(written.keys())
    except (json.JSONDecodeError, IOError) as e:
        print_error(f"Post-write validation failed: {e}")
        _attempt_auto_restore()
        return

    missing = original_keys - written_keys
    if missing:
        print_error(f"Settings key loss detected! Missing keys: {', '.join(sorted(missing))}")
        _attempt_auto_restore()


def _attempt_auto_restore():
    """Attempt automatic restore from the most recent backup."""
    latest = get_latest_backup()
    if latest and restore_settings_from_backup(latest):
        print_warning(f"Auto-restored settings.json from: {latest.name}")
        print_info("Hooks were NOT applied. Re-run the installer after checking settings.json")
    else:
        print_error("Auto-restore failed. Check ~/.claude/.settings-backups/ for manual recovery")
    sys.exit(1)


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

    # Remove settings backups
    if SETTINGS_BACKUP_DIR.exists():
        if not dry_run:
            safe_rmtree(SETTINGS_BACKUP_DIR)
        print_success("Removed settings backups")

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


def cmd_diagnose() -> int:
    """
    Run diagnostic checks on the sf-skills installation.

    Checks 6 areas: settings.json health, hook scripts, Python environment,
    backup status, settings diff vs backup, and hook execution test.

    Returns:
        Exit code (0 = all checks pass, 1 = issues found)
    """
    import subprocess

    print_banner()
    print("sf-skills Diagnostics")
    print("════════════════════════════════════════\n")

    issues = 0

    # ── Check 1: settings.json ──
    print(c("1. settings.json", Colors.BOLD))
    if not SETTINGS_FILE.exists():
        print(f"   {c('❌', Colors.RED)} File not found: {SETTINGS_FILE}")
        issues += 1
    else:
        try:
            settings = json.loads(SETTINGS_FILE.read_text())
            key_count = len(settings)
            print(f"   {c('✅', Colors.GREEN)} Valid JSON ({key_count} top-level keys)")

            # Detect environment type
            env_type = _detect_env_from_dict(settings)
            env_icon = "🏢" if env_type == Environment.ENTERPRISE else "👤" if env_type == Environment.PERSONAL else "❓"
            print(f"   {c('ℹ️', Colors.BLUE)} Environment: {env_icon} {env_type}")

            if env_type == Environment.ENTERPRISE:
                # Enterprise auth checks
                env_vars = settings.get("env", {})
                enterprise_fields = {
                    "ANTHROPIC_AUTH_TOKEN": env_vars.get("ANTHROPIC_AUTH_TOKEN"),
                    "ANTHROPIC_BEDROCK_BASE_URL": env_vars.get("ANTHROPIC_BEDROCK_BASE_URL"),
                    "CLAUDE_CODE_USE_BEDROCK": env_vars.get("CLAUDE_CODE_USE_BEDROCK"),
                }
                for field, value in enterprise_fields.items():
                    if value:
                        display = value[:6] + "..." if "TOKEN" in field or "KEY" in field else value
                        print(f"   {c('✅', Colors.GREEN)} {field}: {display}")
                    else:
                        print(f"   {c('❌', Colors.RED)} {field}: missing (required for enterprise)")
                        issues += 1
                login = settings.get("forceLoginMethod")
                if login == "console":
                    print(f"   {c('✅', Colors.GREEN)} forceLoginMethod: console")
                else:
                    print(f"   {c('⚠️', Colors.YELLOW)} forceLoginMethod: {login or 'unset'} (expected 'console' for enterprise)")
            elif env_type == Environment.PERSONAL:
                # Personal auth checks
                auth_fields = ["forceLoginMethod", "env", "permissions", "model"]
                present = [f for f in auth_fields if f in settings]
                missing = [f for f in auth_fields if f not in settings]
                if present:
                    print(f"   {c('✅', Colors.GREEN)} Auth fields present: {', '.join(present)}")
                if missing:
                    print(f"   {c('⚠️', Colors.YELLOW)} Auth fields missing: {', '.join(missing)}")
                    print(f"      (Not all are required — depends on your Claude Code setup)")
            else:
                # Unknown environment — generic check
                auth_fields = ["forceLoginMethod", "env", "model"]
                present = [f for f in auth_fields if f in settings]
                if present:
                    print(f"   {c('✅', Colors.GREEN)} Config fields present: {', '.join(present)}")
                else:
                    print(f"   {c('⚠️', Colors.YELLOW)} No auth fields detected — run --profile save to create a profile")

            if "hooks" in settings:
                sf_count = sum(
                    1 for ev in settings["hooks"].values()
                    for h in ev if h.get("_sf_skills")
                )
                print(f"   {c('✅', Colors.GREEN)} sf-skills hooks registered: {sf_count}")
            else:
                print(f"   {c('❌', Colors.RED)} No hooks registered")
                issues += 1

        except json.JSONDecodeError as e:
            print(f"   {c('❌', Colors.RED)} Invalid JSON (line {e.lineno}, col {e.colno}): {e.msg}")
            print(f"      Fix: python3 {INSTALLER_FILE} --restore-settings")
            issues += 1

    # ── Check 2: Hook scripts ──
    print(f"\n{c('2. Hook Scripts', Colors.BOLD)}")
    hooks_config = get_hooks_config()
    hook_ok = 0
    hook_missing = 0
    for event_name, event_hooks in hooks_config.items():
        for hook_group in event_hooks:
            for hook in hook_group.get("hooks", []):
                cmd = hook.get("command", "")
                # Extract script path from "python3 /path/to/script.py"
                parts = cmd.split()
                if len(parts) >= 2:
                    script_path = Path(parts[-1])
                    if script_path.exists():
                        hook_ok += 1
                    else:
                        print(f"   {c('❌', Colors.RED)} Missing: {script_path}")
                        hook_missing += 1
                        issues += 1

    if hook_missing == 0:
        print(f"   {c('✅', Colors.GREEN)} All {hook_ok} hook scripts present")
    else:
        print(f"   {c('⚠️', Colors.YELLOW)} {hook_ok} present, {hook_missing} missing")

    # ── Check 3: Python environment ──
    print(f"\n{c('3. Python Environment', Colors.BOLD)}")
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"   {c('✅', Colors.GREEN)} Python {py_version}")

    # Check json module
    try:
        json.loads('{"test": true}')
        print(f"   {c('✅', Colors.GREEN)} json module OK")
    except Exception:
        print(f"   {c('❌', Colors.RED)} json module broken")
        issues += 1

    # Check ssl module
    try:
        _get_ssl_context()
        print(f"   {c('✅', Colors.GREEN)} ssl module OK")
    except Exception as e:
        print(f"   {c('⚠️', Colors.YELLOW)} ssl module issue: {e}")

    # ── Check 4: Backup status ──
    print(f"\n{c('4. Settings Backups', Colors.BOLD)}")
    if SETTINGS_BACKUP_DIR.exists():
        backups = sorted(
            SETTINGS_BACKUP_DIR.glob("settings.*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if backups:
            print(f"   {c('✅', Colors.GREEN)} {len(backups)} backup(s) available:")
            for bp in backups[:5]:
                size = bp.stat().st_size
                mtime = datetime.fromtimestamp(bp.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"      {bp.name} ({size:,} bytes, {mtime})")
        else:
            print(f"   {c('⚠️', Colors.YELLOW)} Backup directory exists but is empty")
    else:
        print(f"   {c('⚠️', Colors.YELLOW)} No backups yet (created on next install/update)")

    # ── Check 5: Settings diff vs latest backup ──
    print(f"\n{c('5. Settings vs Backup Diff', Colors.BOLD)}")
    latest_backup = get_latest_backup()
    if latest_backup and SETTINGS_FILE.exists():
        try:
            current = json.loads(SETTINGS_FILE.read_text())
            backed_up = json.loads(latest_backup.read_text())

            current_keys = set(current.keys())
            backup_keys = set(backed_up.keys())

            added = current_keys - backup_keys
            removed = backup_keys - current_keys

            if not added and not removed:
                print(f"   {c('✅', Colors.GREEN)} Top-level keys match latest backup")
            else:
                if removed:
                    print(f"   {c('❌', Colors.RED)} Keys in backup but MISSING from current: {', '.join(sorted(removed))}")
                    issues += 1
                if added:
                    print(f"   {c('ℹ️', Colors.BLUE)} Keys added since backup: {', '.join(sorted(added))}")
        except (json.JSONDecodeError, IOError):
            print(f"   {c('⚠️', Colors.YELLOW)} Could not compare (parse error)")
    elif not latest_backup:
        print(f"   {c('⚠️', Colors.YELLOW)} No backup to compare against")
    elif not SETTINGS_FILE.exists():
        print(f"   {c('❌', Colors.RED)} settings.json missing — cannot compare")
        issues += 1

    # ── Check 6: Hook execution test ──
    print(f"\n{c('6. Hook Execution Test', Colors.BOLD)}")
    session_init = HOOKS_DIR / "scripts" / "session-init.py"
    if session_init.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(session_init)],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "CLAUDE_TOOL_NAME": "", "CLAUDE_TOOL_INPUT": ""}
            )
            if result.returncode == 0 and not result.stdout.strip():
                print(f"   {c('✅', Colors.GREEN)} session-init.py runs cleanly (exit 0, no stdout)")
            elif result.returncode == 0:
                print(f"   {c('⚠️', Colors.YELLOW)} session-init.py exit 0 but produced output ({len(result.stdout)} chars)")
            else:
                print(f"   {c('❌', Colors.RED)} session-init.py exit code {result.returncode}")
                if result.stderr:
                    print(f"      stderr: {result.stderr[:200]}")
                issues += 1
        except subprocess.TimeoutExpired:
            print(f"   {c('⚠️', Colors.YELLOW)} session-init.py timed out (10s)")
        except Exception as e:
            print(f"   {c('❌', Colors.RED)} Could not run session-init.py: {e}")
            issues += 1
    else:
        print(f"   {c('⚠️', Colors.YELLOW)} session-init.py not found (hooks not installed?)")

    # ── Check 7: Settings Profiles ──
    print(f"\n{c('7. Settings Profiles', Colors.BOLD)}")
    profiles = list_profiles()
    if profiles:
        print(f"   {c('✅', Colors.GREEN)} {len(profiles)} profile(s) saved:")
        for p in profiles:
            p_icon = "🏢" if p["environment"] == Environment.ENTERPRISE else "👤" if p["environment"] == Environment.PERSONAL else "❓"
            print(f"      {p_icon} {p['name']} ({p['environment']}, model: {p['model']})")
    else:
        print(f"   {c('ℹ️', Colors.BLUE)} No profiles saved")
        print(f"      Tip: python3 {INSTALLER_FILE} --profile save personal")

    # ── Summary ──
    print("\n════════════════════════════════════════")
    if issues == 0:
        print(f"{c('✅ All checks passed', Colors.GREEN)}")
    else:
        print(f"{c(f'❌ {issues} issue(s) found', Colors.RED)}")
        print(f"\nRemediation:")
        print(f"  • Restore settings: python3 {INSTALLER_FILE} --restore-settings")
        print(f"  • Reinstall:        python3 {INSTALLER_FILE} --force-update")
    print()

    return 0 if issues == 0 else 1


def cmd_restore_settings() -> int:
    """
    Interactively restore settings.json from the latest backup.

    Shows backup info, compares with current settings, backs up the
    current (possibly corrupt) file, and restores.

    Returns:
        Exit code (0 = restored, 1 = no backup or cancelled)
    """
    print_banner()
    print("Restore settings.json")
    print("════════════════════════════════════════\n")

    # Find latest backup
    latest = get_latest_backup()
    if latest is None:
        print_error("No settings backups found")
        print_info(f"Backup directory: {SETTINGS_BACKUP_DIR}")
        print_info("Backups are created automatically during install/update")
        return 1

    # Show backup info
    try:
        backup_content = latest.read_text()
        backup_data = json.loads(backup_content)
        backup_keys = sorted(backup_data.keys())
    except (json.JSONDecodeError, IOError) as e:
        print_error(f"Latest backup is not valid JSON: {e}")
        return 1

    backup_size = latest.stat().st_size
    backup_time = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

    print(f"Latest backup: {c(latest.name, Colors.CYAN)}")
    print(f"  Date:  {backup_time}")
    print(f"  Size:  {backup_size:,} bytes")
    print(f"  Keys:  {len(backup_keys)} ({', '.join(backup_keys)})")

    # Compare with current
    print()
    if SETTINGS_FILE.exists():
        try:
            current_data = json.loads(SETTINGS_FILE.read_text())
            current_keys = set(current_data.keys())
            backup_key_set = set(backup_keys)

            missing_from_current = backup_key_set - current_keys
            extra_in_current = current_keys - backup_key_set

            if missing_from_current:
                print(f"{c('Keys that will be RESTORED:', Colors.YELLOW)}")
                for k in sorted(missing_from_current):
                    print(f"  + {k}")
            if extra_in_current:
                print(f"{c('Keys in current but NOT in backup (will be lost):', Colors.RED)}")
                for k in sorted(extra_in_current):
                    print(f"  - {k}")
            if not missing_from_current and not extra_in_current:
                print(f"{c('Current and backup have the same top-level keys', Colors.GREEN)}")
        except json.JSONDecodeError:
            print(f"{c('Current settings.json is invalid JSON — restore recommended', Colors.YELLOW)}")
    else:
        print(f"{c('settings.json does not exist — restore will create it', Colors.YELLOW)}")

    # Confirm
    print()
    if not confirm("Restore settings.json from this backup?"):
        print("\nRestore cancelled.")
        return 1

    # Back up current (possibly corrupt) file before overwriting
    if SETTINGS_FILE.exists():
        pre_restore_backup = backup_settings(reason="pre-restore")
        if pre_restore_backup:
            print_info(f"Current file backed up to: {pre_restore_backup.name}")

    # Restore
    if restore_settings_from_backup(latest):
        print_success(f"settings.json restored from {latest.name}")
        print_info("Restart Claude Code to apply changes")
        return 0
    else:
        print_error("Restore failed")
        return 1


def cmd_profile(args_list: List[str], dry_run: bool = False, force: bool = False) -> int:
    """Route --profile subcommands.

    Subcommands:
        list (default)  - List all profiles
        save <name>     - Save current auth-layer as profile
        use <name>      - Switch to profile (preserving hooks/permissions)
        show <name>     - Display profile contents (tokens redacted)
        delete <name>   - Delete a profile
    """
    if not args_list:
        args_list = ["list"]

    subcmd = args_list[0]
    subcmd_args = args_list[1:]

    handlers = {
        "list": _cmd_profile_list,
        "save": _cmd_profile_save,
        "use": _cmd_profile_use,
        "show": _cmd_profile_show,
        "delete": _cmd_profile_delete,
    }

    handler = handlers.get(subcmd)
    if handler is None:
        print_error(f"Unknown profile subcommand: '{subcmd}'")
        print_info("Usage: --profile [list|save|use|show|delete] [name]")
        return 1

    return handler(subcmd_args, dry_run=dry_run, force=force)


def _cmd_profile_list(args: List[str], **kwargs) -> int:
    """List all saved profiles."""
    profiles = list_profiles()

    # Detect current environment
    env_type, details = detect_environment()
    env_icon = "🏢" if env_type == Environment.ENTERPRISE else "👤" if env_type == Environment.PERSONAL else "❓"

    print(f"\n{c('Settings Profiles', Colors.BOLD)}")
    print("════════════════════════════════════════\n")
    print(f"  Current: {env_icon} {env_type} (model: {details.get('model', 'unknown')})")
    print()

    if not profiles:
        print(f"  {c('No saved profiles', Colors.DIM)}")
        print()
        print("  Save your current config:")
        print(f"    python3 {INSTALLER_FILE} --profile save personal")
        print(f"    python3 {INSTALLER_FILE} --profile save enterprise")
        return 0

    print(f"  {'Name':<20} {'Environment':<15} {'Model':<25}")
    print(f"  {'─' * 20} {'─' * 15} {'─' * 25}")

    for p in profiles:
        p_icon = "🏢" if p["environment"] == Environment.ENTERPRISE else "👤" if p["environment"] == Environment.PERSONAL else "❓"
        print(f"  {p['name']:<20} {p_icon} {p['environment']:<12} {p['model']:<25}")

    print(f"\n  Switch: python3 {INSTALLER_FILE} --profile use <name>")
    print()
    return 0


def _cmd_profile_save(args: List[str], dry_run: bool = False, force: bool = False, **kwargs) -> int:
    """Save current settings as a named profile."""
    if not args:
        print_error("Profile name required")
        print_info("Usage: --profile save <name>")
        return 1

    name = args[0]

    if dry_run:
        print_info(f"Would save current auth-layer as profile '{name}'")
        return 0

    if save_profile(name, force=force):
        try:
            settings = json.loads(SETTINGS_FILE.read_text())
            env_type = _detect_env_from_dict(settings)
        except (json.JSONDecodeError, IOError):
            env_type = Environment.UNKNOWN
        env_icon = "🏢" if env_type == Environment.ENTERPRISE else "👤" if env_type == Environment.PERSONAL else "❓"
        print_success(f"Profile '{name}' saved ({env_icon} {env_type})")
        profile_path = CLAUDE_DIR / f"{PROFILE_PREFIX}{name}{PROFILE_SUFFIX}"
        print_info(f"File: {profile_path}")
        return 0
    return 1


def _cmd_profile_use(args: List[str], dry_run: bool = False, **kwargs) -> int:
    """Switch to a named profile."""
    if not args:
        print_error("Profile name required")
        print_info("Usage: --profile use <name>")
        return 1

    name = args[0]

    if apply_profile(name, dry_run=dry_run):
        if not dry_run:
            env_type, _ = detect_environment()
            env_icon = "🏢" if env_type == Environment.ENTERPRISE else "👤" if env_type == Environment.PERSONAL else "❓"
            print_success(f"Switched to profile '{name}' ({env_icon} {env_type})")
            print_info("Restart Claude Code to apply changes")
        return 0
    return 1


def _cmd_profile_show(args: List[str], **kwargs) -> int:
    """Display profile contents with tokens redacted."""
    if not args:
        print_error("Profile name required")
        print_info("Usage: --profile show <name>")
        return 1

    name = args[0]
    data = load_profile(name)
    if data is None:
        print_error(f"Profile '{name}' not found or invalid")
        return 1

    env_type = _detect_env_from_dict(data)
    env_icon = "🏢" if env_type == Environment.ENTERPRISE else "👤" if env_type == Environment.PERSONAL else "❓"

    print(f"\n{c(f'Profile: {name}', Colors.BOLD)} ({env_icon} {env_type})")
    print("════════════════════════════════════════\n")

    # Redact tokens in env vars
    display_data = data.copy()
    if "env" in display_data and isinstance(display_data["env"], dict):
        display_data["env"] = _redact_auth_token(display_data["env"])

    print(json.dumps(display_data, indent=2))
    print()
    return 0


def _cmd_profile_delete(args: List[str], force: bool = False, **kwargs) -> int:
    """Delete a saved profile."""
    if not args:
        print_error("Profile name required")
        print_info("Usage: --profile delete <name>")
        return 1

    name = args[0]

    if not force:
        if not confirm(f"Delete profile '{name}'?", default=False):
            print("Cancelled.")
            return 1

    if delete_profile(name):
        print_success(f"Profile '{name}' deleted")
        return 0
    return 1


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
  python3 install.py --diagnose    # Run diagnostic checks
  python3 install.py --restore-settings  # Restore settings.json from backup
  python3 install.py --dry-run     # Preview changes
  python3 install.py --force       # Skip confirmations

Profile management:
  python3 install.py --profile                    # List saved profiles
  python3 install.py --profile list               # Same as above
  python3 install.py --profile save personal      # Save current config
  python3 install.py --profile use enterprise     # Switch profiles
  python3 install.py --profile show enterprise    # View profile (redacted)
  python3 install.py --profile delete old         # Delete a profile
  python3 install.py --profile use ent --dry-run  # Preview switch

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
    parser.add_argument("--diagnose", action="store_true",
                        help="Run diagnostic checks on installation health")
    parser.add_argument("--restore-settings", action="store_true",
                        help="Restore settings.json from latest backup")
    parser.add_argument("--profile", nargs='*', metavar="ACTION",
                        help="Profile management: list|save|use|show|delete [name]")
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
    if args.profile is not None:
        sys.exit(cmd_profile(args.profile, dry_run=args.dry_run, force=args.force))
    elif args.diagnose:
        sys.exit(cmd_diagnose())
    elif args.restore_settings:
        sys.exit(cmd_restore_settings())
    elif args.status:
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
