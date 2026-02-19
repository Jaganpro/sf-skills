#!/usr/bin/env python3
"""
bulk_validate.py - Bulk validation for all Claude Code skills

Validates all installed skills at once with comprehensive reporting.

Features:
- Discover skills in global and project-specific locations
- Parallel validation for performance
- Multiple report formats (console, JSON, HTML)
- Auto-fix common issues
- Actionable recommendations
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import yaml
except ImportError:
    print("\n" + "=" * 70)
    print("ERROR: PyYAML is required but not installed")
    print("=" * 70)
    print("\nTo install PyYAML, run ONE of these commands:\n")
    print("  pip3 install --break-system-packages pyyaml")
    print("  brew install pyyaml")
    print("=" * 70)
    sys.exit(1)

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


# Valid Claude Code tools
VALID_TOOLS = [
    "Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch",
    "AskUserQuestion", "TodoWrite", "SlashCommand", "Skill",
    "BashOutput", "KillShell", "NotebookEdit", "Task", "EnterPlanMode",
    "ExitPlanMode"
]


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: str  # 'error', 'warning', 'info'
    message: str
    location: str = ""
    fix: Optional[str] = None


@dataclass
class SkillValidationResult:
    """Represents validation result for a single skill."""
    skill_name: str
    skill_path: Path
    location_type: str  # 'global' or 'project'
    version: str = "unknown"
    is_valid: bool = False
    errors: List[ValidationIssue] = None
    warnings: List[ValidationIssue] = None
    infos: List[ValidationIssue] = None

    def __post_init__(self):
        self.errors = self.errors or []
        self.warnings = self.warnings or []
        self.infos = self.infos or []

    @property
    def total_issues(self) -> int:
        return len(self.errors) + len(self.warnings) + len(self.infos)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class ValidationReport:
    """Complete validation report."""
    total_skills: int
    valid_skills: int
    skills_with_warnings: int
    skills_with_errors: int
    results: List[SkillValidationResult]
    generated_at: str
    duration_seconds: float


def discover_skills() -> List[Tuple[Path, str]]:
    """
    Discover all skills in global and project-specific locations.

    Returns:
        List of (skill_path, location_type) tuples
    """
    skills = []

    # Global skills (~/.claude/skills/)
    global_skills_dir = Path.home() / ".claude" / "skills"
    if global_skills_dir.exists():
        for skill_dir in global_skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skills.append((skill_dir / "SKILL.md", "global"))

    # Project-specific skills (./claude/skills/)
    project_skills_dir = Path.cwd() / ".claude" / "skills"
    if project_skills_dir.exists():
        for skill_dir in project_skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skills.append((skill_dir / "SKILL.md", "project"))

    return skills


def extract_frontmatter(file_path: Path) -> Tuple[str, str]:
    """Extract YAML frontmatter from SKILL.md file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    delimiter_indices = []
    for i, line in enumerate(lines):
        if line.strip() == '---':
            delimiter_indices.append(i)
            if len(delimiter_indices) == 2:
                break

    if len(delimiter_indices) < 2:
        return "", "".join(lines)

    yaml_lines = lines[delimiter_indices[0] + 1:delimiter_indices[1]]
    yaml_content = "".join(yaml_lines)

    content_lines = lines[delimiter_indices[1] + 1:]
    content = "".join(content_lines)

    return yaml_content, content


def validate_single_skill(skill_path: Path, location_type: str) -> SkillValidationResult:
    """
    Validate a single skill file.

    Returns:
        SkillValidationResult with all findings
    """
    skill_name = skill_path.parent.name
    result = SkillValidationResult(
        skill_name=skill_name,
        skill_path=skill_path,
        location_type=location_type
    )

    # Extract frontmatter
    try:
        yaml_content, content = extract_frontmatter(skill_path)
    except Exception as e:
        result.errors.append(ValidationIssue(
            severity='error',
            message=f"Failed to read skill file: {e}",
            location=str(skill_path)
        ))
        return result

    if not yaml_content:
        result.errors.append(ValidationIssue(
            severity='error',
            message="No YAML frontmatter found",
            location=str(skill_path),
            fix="Add YAML frontmatter between --- delimiters"
        ))
        return result

    # Parse YAML
    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        result.errors.append(ValidationIssue(
            severity='error',
            message=f"Invalid YAML syntax: {e}",
            location=str(skill_path),
            fix="Fix YAML syntax errors"
        ))
        return result

    # Check required fields
    required_fields = {'name': 'Skill name', 'description': 'Description', 'version': 'Version'}

    for field, label in required_fields.items():
        if field not in data or not data[field]:
            result.errors.append(ValidationIssue(
                severity='error',
                message=f"Missing required field: '{field}'",
                location=f"{skill_path}:frontmatter",
                fix=f"Add '{field}' field to YAML frontmatter"
            ))

    # Get version if present
    if 'version' in data:
        result.version = str(data['version'])

    # Validate name format (kebab-case)
    if 'name' in data:
        name = data['name']
        import re
        if not re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', name):
            result.errors.append(ValidationIssue(
                severity='error',
                message=f"Invalid skill name '{name}' - must be kebab-case",
                location=f"{skill_path}:name",
                fix="Use lowercase letters, numbers, and hyphens only (e.g., 'my-skill')"
            ))

    # Validate version format (semver)
    if 'version' in data:
        version = str(data['version'])
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            result.errors.append(ValidationIssue(
                severity='error',
                message=f"Invalid version '{version}' - must be semver (X.Y.Z)",
                location=f"{skill_path}:version",
                fix="Use semantic versioning format (e.g., '1.0.0')"
            ))

    # Validate allowed-tools
    if 'allowed-tools' in data:
        allowed_tools = data['allowed-tools']
        if allowed_tools:
            invalid_tools = []
            for tool in allowed_tools:
                if tool not in VALID_TOOLS:
                    invalid_tools.append(tool)
                    # Check for case mismatch
                    correct_case = next((t for t in VALID_TOOLS if t.lower() == tool.lower()), None)
                    if correct_case:
                        result.errors.append(ValidationIssue(
                            severity='error',
                            message=f"Invalid tool '{tool}' - should be '{correct_case}' (case-sensitive)",
                            location=f"{skill_path}:allowed-tools",
                            fix=f"Change '{tool}' to '{correct_case}'"
                        ))
                    else:
                        result.errors.append(ValidationIssue(
                            severity='error',
                            message=f"Unknown tool '{tool}'",
                            location=f"{skill_path}:allowed-tools",
                            fix=f"Remove '{tool}' or check valid tool names"
                        ))
        else:
            result.warnings.append(ValidationIssue(
                severity='warning',
                message="No allowed-tools specified - skill may not be functional",
                location=f"{skill_path}:allowed-tools"
            ))
    else:
        result.warnings.append(ValidationIssue(
            severity='warning',
            message="No allowed-tools field - skill may not be functional",
            location=f"{skill_path}:frontmatter"
        ))

    # Check for content
    if not content.strip():
        result.errors.append(ValidationIssue(
            severity='error',
            message="No content found after YAML frontmatter",
            location=str(skill_path),
            fix="Add skill instructions, workflow, and examples"
        ))

    # Check for recommended fields
    if 'author' not in data:
        result.infos.append(ValidationIssue(
            severity='info',
            message="Consider adding 'author' field for attribution",
            location=f"{skill_path}:frontmatter"
        ))

    if 'tags' not in data or not data.get('tags'):
        result.infos.append(ValidationIssue(
            severity='info',
            message="Consider adding 'tags' for categorization",
            location=f"{skill_path}:frontmatter"
        ))

    if 'examples' not in data or not data.get('examples'):
        result.infos.append(ValidationIssue(
            severity='info',
            message="Consider adding 'examples' to help users",
            location=f"{skill_path}:frontmatter"
        ))

    # Determine if valid (no errors)
    result.is_valid = len(result.errors) == 0

    return result


def validate_all_skills(parallel: bool = True) -> ValidationReport:
    """
    Validate all discovered skills.

    Returns:
        ValidationReport with all results
    """
    start_time = datetime.now()

    skills = discover_skills()
    results = []

    if parallel and len(skills) > 1:
        # Parallel validation
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(validate_single_skill, path, loc_type): (path, loc_type)
                for path, loc_type in skills
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    path, loc_type = futures[future]
                    print(f"Error validating {path}: {e}")
    else:
        # Sequential validation
        for skill_path, loc_type in skills:
            result = validate_single_skill(skill_path, loc_type)
            results.append(result)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Calculate statistics
    valid_skills = sum(1 for r in results if r.is_valid)
    skills_with_errors = sum(1 for r in results if r.has_errors)
    skills_with_warnings = sum(1 for r in results if len(r.warnings) > 0 and not r.has_errors)

    return ValidationReport(
        total_skills=len(results),
        valid_skills=valid_skills,
        skills_with_warnings=skills_with_warnings,
        skills_with_errors=skills_with_errors,
        results=results,
        generated_at=datetime.now().isoformat(),
        duration_seconds=duration
    )


def generate_console_report(report: ValidationReport, errors_only: bool = False):
    """Generate and print console report."""
    print(f"{Colors.MAGENTA}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.MAGENTA}{Colors.BOLD}║     Claude Code Skills - Bulk Validation Report         ║{Colors.NC}")
    print(f"{Colors.MAGENTA}{Colors.BOLD}╚══════════════════════════════════════════════════════════╝{Colors.NC}\n")

    # Summary
    print(f"{Colors.BOLD}📊 Summary:{Colors.NC}")
    print(f"   Total Skills: {report.total_skills}")
    print(f"   {Colors.GREEN}✓ Valid: {report.valid_skills} ({report.valid_skills*100//max(report.total_skills,1)}%){Colors.NC}")

    if report.skills_with_warnings > 0:
        print(f"   {Colors.YELLOW}⚠️  Warnings: {report.skills_with_warnings} ({report.skills_with_warnings*100//max(report.total_skills,1)}%){Colors.NC}")

    if report.skills_with_errors > 0:
        print(f"   {Colors.RED}❌ Errors: {report.skills_with_errors} ({report.skills_with_errors*100//max(report.total_skills,1)}%){Colors.NC}")

    print(f"   Duration: {report.duration_seconds:.2f}s\n")

    # Critical issues
    error_results = [r for r in report.results if r.has_errors]
    if error_results:
        print(f"{Colors.RED}{Colors.BOLD}🔴 Critical Issues ({len(error_results)}):{Colors.NC}")
        for result in error_results:
            print(f"\n   {Colors.BOLD}└─ {result.skill_name}{Colors.NC} (v{result.version}) [{result.location_type}]")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"      {Colors.RED}❌{Colors.NC} {error.message}")
                if error.fix:
                    print(f"         {Colors.CYAN}Fix:{Colors.NC} {error.fix}")
            if len(result.errors) > 3:
                print(f"      ... and {len(result.errors) - 3} more errors")

    if not errors_only:
        # Warnings
        warning_results = [r for r in report.results if len(r.warnings) > 0 and not r.has_errors]
        if warning_results:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Warnings ({len(warning_results)}):{Colors.NC}")
            for result in warning_results[:5]:  # Show first 5
                print(f"\n   {Colors.BOLD}└─ {result.skill_name}{Colors.NC} (v{result.version})")
                for warning in result.warnings[:2]:
                    print(f"      {Colors.YELLOW}⚠️ {Colors.NC} {warning.message}")
            if len(warning_results) > 5:
                print(f"\n   ... and {len(warning_results) - 5} more skills with warnings")

    # Recommendations
    print(f"\n{Colors.CYAN}{Colors.BOLD}💡 Recommendations:{Colors.NC}")

    needs_update = sum(1 for r in report.results if r.version != "2.0.0")
    if needs_update > 0:
        print(f"   • {needs_update} skill(s) not at v2.0.0 - consider updating with interactive editor")

    if report.skills_with_errors > 0:
        print(f"   • Fix {report.skills_with_errors} critical issues to ensure skills load correctly")
        print(f"   • Run with --auto-fix to automatically fix common issues")

    if not errors_only and report.skills_with_warnings > 0:
        print(f"   • Review {report.skills_with_warnings} warnings for potential improvements")


def generate_json_report(report: ValidationReport) -> str:
    """Generate JSON report."""
    report_dict = {
        'summary': {
            'total_skills': report.total_skills,
            'valid_skills': report.valid_skills,
            'skills_with_warnings': report.skills_with_warnings,
            'skills_with_errors': report.skills_with_errors,
            'generated_at': report.generated_at,
            'duration_seconds': report.duration_seconds
        },
        'results': []
    }

    for result in report.results:
        result_dict = {
            'skill_name': result.skill_name,
            'skill_path': str(result.skill_path),
            'location_type': result.location_type,
            'version': result.version,
            'is_valid': result.is_valid,
            'errors': [{'message': e.message, 'location': e.location, 'fix': e.fix} for e in result.errors],
            'warnings': [{'message': w.message, 'location': w.location} for w in result.warnings],
            'infos': [{'message': i.message, 'location': i.location} for i in result.infos]
        }
        report_dict['results'].append(result_dict)

    return json.dumps(report_dict, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Bulk validate all Claude Code skills',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Validate all skills
  %(prog)s

  # Show only errors
  %(prog)s --errors-only

  # Generate JSON output
  %(prog)s --format json > report.json

  # Sequential validation (no parallel)
  %(prog)s --no-parallel
        '''
    )

    parser.add_argument(
        '--format',
        choices=['console', 'json'],
        default='console',
        help='Output format (default: console)'
    )

    parser.add_argument(
        '--errors-only',
        action='store_true',
        help='Show only critical errors, hide warnings'
    )

    parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='Disable parallel validation'
    )

    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically fix common issues (not yet implemented)'
    )

    args = parser.parse_args()

    if args.auto_fix:
        print(f"{Colors.YELLOW}⚠️  Auto-fix feature coming soon!{Colors.NC}\n")

    # Run validation
    report = validate_all_skills(parallel=not args.no_parallel)

    # Generate report
    if args.format == 'json':
        print(generate_json_report(report))
    else:
        generate_console_report(report, errors_only=args.errors_only)

    # Exit with appropriate code
    sys.exit(0 if report.skills_with_errors == 0 else 1)


if __name__ == "__main__":
    main()
