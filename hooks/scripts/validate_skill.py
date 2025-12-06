#!/usr/bin/env python3
"""
validate_yaml.py - Deep validation for Claude Code SKILL.md files

Validates:
- YAML syntax
- Required fields (name, description, version)
- Field formats (kebab-case names, semver versions)
- Tool permissions (valid Claude Code tools)
- Content structure
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    print("\n" + "=" * 70)
    print("ERROR: PyYAML is required but not installed")
    print("=" * 70)
    print("\nTo install PyYAML, run ONE of these commands:\n")
    print("  # Using pip with --break-system-packages (macOS/Linux):")
    print("  pip3 install --break-system-packages pyyaml\n")
    print("  # Or using Homebrew (macOS):")
    print("  brew install pyyaml\n")
    print("  # Or in a virtual environment:")
    print("  python3 -m venv venv")
    print("  source venv/bin/activate")
    print("  pip install pyyaml\n")
    print("=" * 70)
    sys.exit(1)

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

# Valid Claude Code tools (case-sensitive)
VALID_TOOLS = [
    "Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch",
    "AskUserQuestion", "TodoWrite", "SlashCommand", "Skill",
    "BashOutput", "KillShell", "NotebookEdit", "Task",
    "EnterPlanMode", "ExitPlanMode"
]

REQUIRED_FIELDS = {
    'name': 'Skill name (kebab-case)',
    'description': 'One-line description',
    'version': 'Version number (semver: X.Y.Z)'
}


def print_error(message: str):
    """Print error message in red."""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")


def print_success(message: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")


def print_info(message: str):
    """Print info message in cyan."""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.NC}")


def extract_frontmatter(file_path: Path) -> Tuple[str, str]:
    """
    Extract YAML frontmatter and content from SKILL.md file.

    Returns:
        Tuple of (yaml_content, remaining_content)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find frontmatter delimiters
    delimiter_indices = []
    for i, line in enumerate(lines):
        if line.strip() == '---':
            delimiter_indices.append(i)
            if len(delimiter_indices) == 2:
                break

    if len(delimiter_indices) < 2:
        return "", "".join(lines)

    # Extract YAML between delimiters
    yaml_lines = lines[delimiter_indices[0] + 1:delimiter_indices[1]]
    yaml_content = "".join(yaml_lines)

    # Extract content after second delimiter
    content_lines = lines[delimiter_indices[1] + 1:]
    content = "".join(content_lines)

    return yaml_content, content


def validate_yaml_syntax(yaml_content: str) -> Tuple[bool, Dict, str]:
    """
    Validate YAML syntax and parse content.

    Returns:
        Tuple of (success, parsed_data, error_message)
    """
    try:
        data = yaml.safe_load(yaml_content)
        return True, data, ""
    except yaml.YAMLError as e:
        return False, {}, str(e)


def validate_required_fields(data: Dict) -> List[str]:
    """
    Check for required fields in YAML frontmatter.

    Returns:
        List of missing fields
    """
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in data or not data[field]:
            missing.append(field)
    return missing


def validate_name_format(name: str) -> Tuple[bool, str]:
    """
    Validate skill name is kebab-case.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', name):
        return False, (
            f"Skill name '{name}' is not valid kebab-case\n"
            "   Expected: lowercase letters, numbers, hyphens only\n"
            "   Examples: 'code-analyzer', 'doc-writer', 'hello-world'"
        )
    return True, ""


def validate_version_format(version: str) -> Tuple[bool, str]:
    """
    Validate version is semver format.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
        return False, (
            f"Version '{version}' is not valid semver\n"
            "   Expected format: MAJOR.MINOR.PATCH (e.g., 1.0.0, 2.1.3)"
        )
    return True, ""


def validate_tools(allowed_tools: List[str]) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate tool names against valid Claude Code tools.

    Returns:
        Tuple of (all_valid, invalid_tools, suggestions)
    """
    invalid_tools = []
    suggestions = {}

    for tool in allowed_tools:
        if tool not in VALID_TOOLS:
            invalid_tools.append(tool)
            # Find case-insensitive matches
            for valid_tool in VALID_TOOLS:
                if tool.lower() == valid_tool.lower():
                    suggestions[tool] = valid_tool
                    break

    return len(invalid_tools) == 0, invalid_tools, suggestions


def detect_format_version(data: Dict) -> str:
    """
    Detect skill format version from frontmatter.

    Returns:
        Version string (e.g., "1.0.0", "1.1.0", "1.2.0")
    """
    # Check for explicit format_version in metadata
    if 'metadata' in data and 'format_version' in data['metadata']:
        return data['metadata']['format_version']

    # v1.2.0: has dependencies, license, keywords, test_config, repository, or homepage
    v12_fields = ['dependencies', 'license', 'keywords', 'test_config', 'repository', 'homepage']
    if any(field in data for field in v12_fields):
        return "1.2.0"

    # v1.1.0: has examples or metadata fields
    if 'examples' in data or 'metadata' in data:
        return "1.1.0"

    # Default to v1.0.0
    return "1.0.0"


def validate_skill_file(file_path: Path) -> bool:
    """
    Main validation function for SKILL.md file.

    Returns:
        True if validation passed, False otherwise
    """
    print(f"{Colors.BLUE}🔍 Validating: {file_path}{Colors.NC}\n")

    has_errors = False

    # Extract frontmatter
    yaml_content, content = extract_frontmatter(file_path)

    if not yaml_content:
        print_error("No YAML frontmatter found")
        print(f"{Colors.YELLOW}Expected format:{Colors.NC}")
        print("---")
        print("name: skill-name")
        print("description: Description of skill")
        print("version: 1.0.0")
        print("---")
        return False

    print_success("YAML frontmatter found")

    # Validate YAML syntax
    success, data, error_msg = validate_yaml_syntax(yaml_content)
    if not success:
        print_error(f"Invalid YAML syntax:\n   {error_msg}")
        return False

    print_success("YAML syntax is valid")

    # Check required fields
    missing_fields = validate_required_fields(data)
    if missing_fields:
        print_error("Missing required fields:")
        for field in REQUIRED_FIELDS:
            if field in missing_fields:
                print(f"   ✗ {field}: [MISSING] - {REQUIRED_FIELDS[field]}")
            else:
                print(f"   ✓ {field}: present")
        has_errors = True
        print(f"\n{Colors.YELLOW}💡 Fix: Add missing required fields to YAML frontmatter{Colors.NC}")
    else:
        for field in REQUIRED_FIELDS:
            print_success(f"Field '{field}' present")

    if has_errors:
        return False

    # Validate name format
    name = data.get('name', '')
    is_valid, error_msg = validate_name_format(name)
    if not is_valid:
        print_error(error_msg)
        has_errors = True
    else:
        print_success(f"Skill name '{name}' is valid kebab-case")

    # Validate version format
    version = data.get('version', '')
    is_valid, error_msg = validate_version_format(version)
    if not is_valid:
        print_error(error_msg)
        has_errors = True
    else:
        print_success(f"Version '{version}' is valid semver")

    # Validate allowed-tools if present
    if 'allowed-tools' in data:
        allowed_tools = data['allowed-tools']
        if allowed_tools:
            all_valid, invalid_tools, suggestions = validate_tools(allowed_tools)

            if not all_valid:
                print_error("Invalid tools in allowed-tools:")
                for tool in invalid_tools:
                    if tool in suggestions:
                        print(f"   - '{tool}' → Did you mean '{suggestions[tool]}'? (case-sensitive)")
                    else:
                        print(f"   - '{tool}' → Not a valid Claude Code tool")

                print(f"\n   {Colors.CYAN}Valid tools:{Colors.NC}")
                for tool in VALID_TOOLS:
                    print(f"     - {tool}")
                has_errors = True
            else:
                print_success(f"All {len(allowed_tools)} tools are valid")
        else:
            print_warning("allowed-tools is empty (skill may not be functional)")
    else:
        print_warning("No allowed-tools specified (skill may not be functional)")

    # Detect format version
    format_version = detect_format_version(data)
    print(f"\n{Colors.CYAN}📋 Format Version: {format_version}{Colors.NC}")

    if format_version != "2.0.0":
        print_info(f"Note: Skill is at v{format_version}. Current version is v2.0.0")
        print_info("Consider updating skill to v2.0.0 format manually or using the interactive editor")

    # Check for optional but recommended fields
    if 'author' not in data:
        print_info("Suggestion: Add 'author' field for attribution")

    if 'tags' not in data or not data['tags']:
        print_info("Suggestion: Add 'tags' for categorization and discovery")

    if 'examples' not in data or not data.get('examples'):
        print_info("Suggestion: Add 'examples' field to help users understand usage")

    # v1.2 field recommendations
    if format_version in ["1.0.0", "1.1.0"]:
        print_info("v1.2.0 enhancements available:")
        if 'license' not in data:
            print(f"   • Add 'license' field for legal clarity")
        if 'keywords' not in data:
            print(f"   • Add 'keywords' for better discoverability")
        if 'dependencies' not in data:
            print(f"   • Add 'dependencies' if skill depends on other skills")

    # Check for content after frontmatter
    if not content.strip():
        print_error("No content found after YAML frontmatter")
        print(f"{Colors.YELLOW}Skill content should include:{Colors.NC}")
        print("  - Purpose and responsibilities")
        print("  - Workflow or process steps")
        print("  - Examples and best practices")
        has_errors = True
    else:
        print_success("Content present after frontmatter")

    # Final result
    print()
    if has_errors:
        print(f"{Colors.RED}❌ Validation failed{Colors.NC}")
        return False
    else:
        print(f"{Colors.GREEN}✅ Validation passed!{Colors.NC}")
        print(f"{Colors.BLUE}Skill file is properly formatted and ready to use.{Colors.NC}")
        return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_yaml.py <path-to-SKILL.md>")
        print()
        print("Validates a Claude Code SKILL.md file:")
        print("  - YAML syntax")
        print("  - Required fields (name, description, version)")
        print("  - Field format (kebab-case name, semver version)")
        print("  - Tool permissions (valid tool names)")
        print("  - Content structure")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        sys.exit(1)

    success = validate_skill_file(file_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
