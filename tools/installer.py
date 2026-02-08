#!/usr/bin/env python3
"""
sf-skills Multi-CLI Installer

Install sf-skills to different agentic coding CLIs following the Agent Skills
open standard (agentskills.io).

Supported CLIs:
- OpenCode: .opencode/skill/{name}/ or .claude/skills/{name}/
- Codex CLI: .codex/skills/{name}/
- Gemini CLI: ~/.gemini/skills/{name}/

Usage:
    # Install all skills for OpenCode
    python tools/installer.py --cli opencode --all

    # Install specific skills for Gemini
    python tools/installer.py --cli gemini --skills sf-apex sf-flow

    # Auto-detect installed CLIs and install all skills
    python tools/installer.py --detect --all

    # Install to custom location
    python tools/installer.py --cli codex --target ./my-project/.codex/skills/ --all

    # List available skills
    python tools/installer.py --list
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Dict

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from cli_adapters import ADAPTERS, CLIAdapter


# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
    print("=" * len(text))


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.ENDC} {text}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.ENDC} {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.ENDC} {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.ENDC} {text}")


def get_available_skills() -> List[str]:
    """
    Get list of available skills in the repository.

    Returns:
        List of skill directory names
    """
    skills = []
    for item in REPO_ROOT.iterdir():
        if not item.is_dir():
            continue
        # Any top-level directory with SKILL.md is a skill
        if (item / "SKILL.md").exists():
            skills.append(item.name)
    return sorted(skills)


def detect_installed_clis() -> List[str]:
    """
    Auto-detect which CLIs are installed on the system.

    Returns:
        List of detected CLI names
    """
    detected = []

    # Check for OpenCode
    if shutil.which("opencode") or Path.home().joinpath(".opencode").exists():
        detected.append("opencode")

    # Check for Codex CLI
    if shutil.which("codex"):
        detected.append("codex")

    # Check for Gemini CLI
    if shutil.which("gemini") or Path.home().joinpath(".gemini").exists():
        detected.append("gemini")

    # Check for Droid CLI (Factory.ai)
    if shutil.which("droid") or Path.home().joinpath(".factory").exists():
        detected.append("droid")

    # Check for Cursor (IDE with CLI)
    if shutil.which("cursor") or Path.home().joinpath(".cursor").exists():
        detected.append("cursor")

    return detected


def install_skill(
    adapter: CLIAdapter,
    skill_name: str,
    target_base: Optional[Path] = None
) -> bool:
    """
    Install a single skill using the specified adapter.

    Args:
        adapter: CLI adapter to use
        skill_name: Name of skill to install
        target_base: Base directory for installation (uses adapter default if None)

    Returns:
        True if successful, False otherwise
    """
    source_dir = REPO_ROOT / skill_name

    if not source_dir.exists():
        print_error(f"Skill not found: {skill_name}")
        return False

    if not (source_dir / "SKILL.md").exists():
        print_error(f"Invalid skill (no SKILL.md): {skill_name}")
        return False

    try:
        # Transform skill for target CLI
        output = adapter.transform_skill(source_dir)

        # Determine target directory
        if target_base:
            target_dir = target_base / skill_name
        else:
            target_dir = adapter.default_install_path / skill_name

        # Write output
        adapter.write_output(output, target_dir)

        print_success(f"Installed {skill_name} to {target_dir}")
        return True

    except Exception as e:
        print_error(f"Failed to install {skill_name}: {e}")
        return False


def install_skills(
    cli: str,
    skills: List[str],
    target: Optional[Path] = None,
    force: bool = False
) -> int:
    """
    Install multiple skills for a CLI.

    Args:
        cli: Target CLI name
        skills: List of skills to install
        target: Custom target directory (optional)
        force: Overwrite existing installations

    Returns:
        Number of successfully installed skills
    """
    if cli not in ADAPTERS:
        print_error(f"Unknown CLI: {cli}")
        print_info(f"Supported CLIs: {', '.join(ADAPTERS.keys())}")
        return 0

    adapter_class = ADAPTERS[cli]
    adapter = adapter_class(REPO_ROOT)

    target_base = Path(target) if target else None

    print_header(f"Installing skills for {cli.upper()}")
    print_info(f"Target: {target_base or adapter.default_install_path}")
    print()

    success_count = 0
    for skill in skills:
        target_dir = (target_base or adapter.default_install_path) / skill

        if target_dir.exists() and not force:
            print_warning(f"Skipping {skill} (already exists, use --force to overwrite)")
            continue

        if target_dir.exists() and force:
            try:
                shutil.rmtree(target_dir)
            except Exception as e:
                print_warning(f"Could not remove {target_dir} ({e}); overwriting files in place")

        if install_skill(adapter, skill, target_base):
            success_count += 1

    return success_count


def list_skills() -> None:
    """List all available skills with descriptions."""
    print_header("Available Skills")

    skills = get_available_skills()

    if not skills:
        print_warning("No skills found in repository")
        return

    for skill in skills:
        skill_md = REPO_ROOT / skill / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            # Extract description from YAML frontmatter
            import re
            desc_match = re.search(r'description:\s*[>|]?\s*\n?\s*(.+?)(?:\n\w|\n---)', content, re.DOTALL)
            if desc_match:
                desc = desc_match.group(1).strip().replace('\n', ' ')[:60]
                print(f"  {Colors.CYAN}{skill:20}{Colors.ENDC} {desc}...")
            else:
                print(f"  {Colors.CYAN}{skill:20}{Colors.ENDC}")
        else:
            print(f"  {Colors.CYAN}{skill:20}{Colors.ENDC} (no description)")


def list_clis() -> None:
    """List supported CLIs and their install paths."""
    print_header("Supported CLIs")

    for name, adapter_class in ADAPTERS.items():
        adapter = adapter_class(REPO_ROOT)
        print(f"  {Colors.CYAN}{name:12}{Colors.ENDC} → {adapter.default_install_path}")

    print()
    detected = detect_installed_clis()
    if detected:
        print_info(f"Detected on this system: {', '.join(detected)}")
    else:
        print_warning("No supported CLIs detected on this system")


def main():
    parser = argparse.ArgumentParser(
        description="Install sf-skills to different agentic coding CLIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --cli opencode --all              Install all skills for OpenCode
  %(prog)s --cli gemini --skills sf-apex     Install specific skill for Gemini
  %(prog)s --detect --all                    Auto-detect CLIs and install all
  %(prog)s --list                            List available skills
  %(prog)s --list-clis                       List supported CLIs
        """
    )

    # CLI selection
    cli_group = parser.add_mutually_exclusive_group()
    cli_group.add_argument(
        "--cli",
        choices=list(ADAPTERS.keys()),
        help="Target CLI to install for"
    )
    cli_group.add_argument(
        "--detect",
        action="store_true",
        help="Auto-detect installed CLIs"
    )

    # Skill selection
    skill_group = parser.add_mutually_exclusive_group()
    skill_group.add_argument(
        "--skills",
        nargs="+",
        help="Specific skills to install"
    )
    skill_group.add_argument(
        "--all",
        action="store_true",
        help="Install all available skills"
    )

    # Options
    parser.add_argument(
        "--target",
        type=str,
        help="Custom target directory for installation"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing installations"
    )

    # Info commands
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available skills"
    )
    parser.add_argument(
        "--list-clis",
        action="store_true",
        help="List supported CLIs"
    )

    args = parser.parse_args()

    # Handle info commands
    if args.list:
        list_skills()
        return 0

    if args.list_clis:
        list_clis()
        return 0

    # Validate required arguments for installation
    if not args.cli and not args.detect:
        parser.error("Either --cli or --detect is required for installation")

    if not args.skills and not args.all:
        parser.error("Either --skills or --all is required")

    # Get skills to install
    if args.all:
        skills = get_available_skills()
    else:
        skills = args.skills

    if not skills:
        print_error("No skills to install")
        return 1

    # Get target CLIs
    if args.detect:
        target_clis = detect_installed_clis()
        if not target_clis:
            print_error("No supported CLIs detected on this system")
            print_info("Install one of: OpenCode, Codex CLI, or Gemini CLI")
            return 1
        print_info(f"Detected CLIs: {', '.join(target_clis)}")
    else:
        target_clis = [args.cli]

    # Install for each CLI
    total_success = 0
    total_skills = len(skills) * len(target_clis)

    for cli in target_clis:
        success = install_skills(
            cli=cli,
            skills=skills,
            target=args.target,
            force=args.force
        )
        total_success += success

    # Summary
    print()
    print_header("Installation Summary")
    print(f"  Skills installed: {total_success}/{total_skills}")

    if total_success == total_skills:
        print_success("All skills installed successfully!")
    elif total_success > 0:
        print_warning("Some skills failed to install")
    else:
        print_error("No skills were installed")

    return 0 if total_success > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
