#!/usr/bin/env python3
"""
dependency_manager.py - Dependency management CLI for Claude Code skills

Commands:
  check <skill>     - Check dependencies for a specific skill
  tree <skill>      - Show dependency tree
  validate --all    - Validate dependencies for all skills
  circular <skill>  - Detect circular dependencies
"""

import sys
import argparse
from pathlib import Path
from typing import List

from dependency_validator import DependencyValidator, DependencyCheckResult
from version_resolver import VersionResolver


# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    NC = '\033[0m'


class DependencyManager:
    """CLI tool for managing skill dependencies."""

    def __init__(self, skills_dir: Path = None):
        """
        Initialize dependency manager.

        Args:
            skills_dir: Path to skills directory
        """
        self.validator = DependencyValidator(skills_dir)

    def cmd_check(self, skill_name: str) -> int:
        """
        Check dependencies for a skill.

        Args:
            skill_name: Name of skill to check

        Returns:
            Exit code (0 if all satisfied, 1 otherwise)
        """
        print(f"{Colors.BOLD}Checking dependencies for: {skill_name}{Colors.NC}\n")

        # Load skill metadata
        metadata, error = self.validator.load_skill_metadata(skill_name)
        if error or metadata is None:
            print(f"{Colors.RED}✗ {error}{Colors.NC}")
            return 1

        version = metadata.get('version', 'unknown')
        print(f"Skill: {Colors.CYAN}{skill_name}{Colors.NC} (v{version})")

        # Check dependencies
        results, error = self.validator.check_all_dependencies(skill_name)
        if error:
            print(f"{Colors.RED}✗ {error}{Colors.NC}")
            return 1

        if not results:
            print(f"{Colors.CYAN}No dependencies{Colors.NC}")
            return 0

        # Display results
        print(f"\n{Colors.BOLD}Dependencies ({len(results)}):{Colors.NC}\n")

        all_satisfied = True
        for result in results:
            if result.is_satisfied:
                status = f"{Colors.GREEN}✓{Colors.NC}"
            else:
                status = f"{Colors.RED}✗{Colors.NC}"
                all_satisfied = False

            optional_str = f" {Colors.YELLOW}[optional]{Colors.NC}" if not result.dependency.required else ""

            if result.installed:
                print(f"  {status} {result.dependency.name} ({result.dependency.version_constraint})")
                print(f"     → Installed: {Colors.CYAN}{result.installed_version}{Colors.NC} {result.message}{optional_str}")
            else:
                print(f"  {status} {result.dependency.name} ({result.dependency.version_constraint})")
                print(f"     → {Colors.RED}NOT INSTALLED{Colors.NC}{optional_str}")

        # Summary
        print()
        if all_satisfied:
            print(f"{Colors.GREEN}✓ All dependencies satisfied{Colors.NC}")
            return 0
        else:
            unsatisfied = [r for r in results if not r.is_satisfied and r.dependency.required]
            if unsatisfied:
                print(f"{Colors.RED}✗ {len(unsatisfied)} required dependenc{'y' if len(unsatisfied) == 1 else 'ies'} not satisfied{Colors.NC}")
                return 1
            else:
                print(f"{Colors.YELLOW}⚠ Optional dependencies not satisfied{Colors.NC}")
                return 0

    def cmd_tree(self, skill_name: str) -> int:
        """
        Show dependency tree for a skill.

        Args:
            skill_name: Name of skill

        Returns:
            Exit code
        """
        print(f"{Colors.BOLD}Dependency Tree:{Colors.NC}\n")

        tree_lines = self.validator.build_dependency_tree(skill_name)

        for line in tree_lines:
            # Color-code the status symbols
            line = line.replace('✓', f'{Colors.GREEN}✓{Colors.NC}')
            line = line.replace('✗', f'{Colors.RED}✗{Colors.NC}')
            line = line.replace('[optional]', f'{Colors.YELLOW}[optional]{Colors.NC}')
            print(line)

        return 0

    def cmd_circular(self, skill_name: str) -> int:
        """
        Detect circular dependencies.

        Args:
            skill_name: Name of skill to check

        Returns:
            Exit code (0 if no circular deps, 1 if found)
        """
        print(f"{Colors.BOLD}Checking for circular dependencies: {skill_name}{Colors.NC}\n")

        circular_error = self.validator.detect_circular_dependencies(skill_name)

        if circular_error:
            print(f"{Colors.RED}✗ Circular dependency detected!{Colors.NC}\n")
            print(f"Cycle: {Colors.YELLOW}{' → '.join(circular_error.cycle_path)}{Colors.NC}")
            return 1
        else:
            print(f"{Colors.GREEN}✓ No circular dependencies found{Colors.NC}")
            return 0

    def cmd_validate_all(self) -> int:
        """
        Validate dependencies for all installed skills.

        Returns:
            Exit code
        """
        print(f"{Colors.BOLD}Validating All Skills{Colors.NC}\n")

        # Find all skills
        skills_dir = self.validator.skills_dir
        if not skills_dir.exists():
            print(f"{Colors.RED}Skills directory not found: {skills_dir}{Colors.NC}")
            return 1

        skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

        if not skill_dirs:
            print(f"{Colors.YELLOW}No skills found in {skills_dir}{Colors.NC}")
            return 0

        print(f"Found {len(skill_dirs)} skills\n")

        # Check each skill
        total_skills = 0
        skills_with_deps = 0
        total_deps = 0
        satisfied_deps = 0
        unsatisfied_deps = 0

        issues = []

        for skill_dir in sorted(skill_dirs):
            skill_name = skill_dir.name
            total_skills += 1

            results, error = self.validator.check_all_dependencies(skill_name)

            if error:
                issues.append(f"{skill_name}: {error}")
                continue

            if not results:
                continue

            skills_with_deps += 1
            total_deps += len(results)

            for result in results:
                if result.is_satisfied:
                    satisfied_deps += 1
                else:
                    unsatisfied_deps += 1
                    if result.dependency.required:
                        issues.append(f"{skill_name}: {result.dependency.name} - {result.message}")

        # Print summary
        print(f"{Colors.CYAN}{'═' * 60}{Colors.NC}")
        print(f"{Colors.BOLD}Summary:{Colors.NC}\n")
        print(f"  Total Skills: {total_skills}")
        print(f"  Skills with Dependencies: {skills_with_deps}")
        print(f"  Total Dependencies: {total_deps}")
        print(f"  {Colors.GREEN}Satisfied: {satisfied_deps}{Colors.NC}")
        print(f"  {Colors.RED}Unsatisfied: {unsatisfied_deps}{Colors.NC}")

        if issues:
            print(f"\n{Colors.RED}Issues Found ({len(issues)}):{Colors.NC}\n")
            for issue in issues:
                print(f"  • {issue}")
            print()
            return 1
        else:
            print(f"\n{Colors.GREEN}✓ All dependencies validated successfully{Colors.NC}")
            return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Dependency manager for Claude Code skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  check <skill>     Check dependencies for a specific skill
  tree <skill>      Show dependency tree with status
  circular <skill>  Detect circular dependencies
  validate --all    Validate dependencies for all skills

Examples:
  # Check dependencies for a skill
  python3 dependency_manager.py check my-skill

  # Show dependency tree
  python3 dependency_manager.py tree my-skill

  # Detect circular dependencies
  python3 dependency_manager.py circular my-skill

  # Validate all skills
  python3 dependency_manager.py validate --all

Dependency Format in SKILL.md:
  dependencies:
    - name: skill-builder
      version: ">=1.2.0"
      required: true
    - name: python-analyzer
      version: "^2.0.0"
      required: false

Version Constraints:
  ^1.2.0   Compatible (>=1.2.0 <2.0.0)
  ~1.2.0   Approximately (>=1.2.0 <1.3.0)
  >=1.2.0  Greater than or equal
  1.2.0    Exact version
  *        Any version
        """
    )

    parser.add_argument(
        'command',
        choices=['check', 'tree', 'circular', 'validate'],
        help='Command to execute'
    )

    parser.add_argument(
        'skill',
        nargs='?',
        help='Skill name (required for check, tree, circular)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Apply to all skills (for validate command)'
    )

    parser.add_argument(
        '--skills-dir',
        type=Path,
        help='Path to skills directory (default: ~/.claude/skills/)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.command in ['check', 'tree', 'circular'] and not args.skill:
        parser.error(f"'{args.command}' command requires a skill name")

    if args.command == 'validate' and not args.all:
        parser.error("'validate' command requires --all flag")

    # Initialize manager
    manager = DependencyManager(skills_dir=args.skills_dir)

    # Execute command
    try:
        if args.command == 'check':
            return manager.cmd_check(args.skill)

        elif args.command == 'tree':
            return manager.cmd_tree(args.skill)

        elif args.command == 'circular':
            return manager.cmd_circular(args.skill)

        elif args.command == 'validate':
            return manager.cmd_validate_all()

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.NC}")
        return 130

    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
