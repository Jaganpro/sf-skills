#!/usr/bin/env python3
"""
editor_validators.py - Validation functions for interactive skill editor

Provides field-level validation with structured results for use in the
interactive editor. Wraps and extends validate_yaml.py validation logic.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Run: pip install pyyaml")
    import sys
    sys.exit(1)

# Import validation constants from validate_yaml
from validate_yaml import VALID_TOOLS, REQUIRED_FIELDS


@dataclass
class ValidationResult:
    """Structured validation result."""
    is_valid: bool
    message: str = ""
    suggestions: List[str] = field(default_factory=list)
    field_name: str = ""

    @property
    def has_suggestions(self) -> bool:
        """Check if result has suggestions."""
        return len(self.suggestions) > 0


class SkillFieldValidator:
    """Validates individual skill frontmatter fields."""

    @staticmethod
    def validate_name(name: str) -> ValidationResult:
        """
        Validate skill name is kebab-case.

        Args:
            name: Skill name to validate

        Returns:
            ValidationResult with outcome
        """
        if not name:
            return ValidationResult(
                is_valid=False,
                message="Name cannot be empty",
                field_name="name"
            )

        # Check kebab-case format
        if not re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', name):
            suggestions = []

            # Suggest converting to kebab-case
            if ' ' in name:
                suggestions.append(f"Try: {name.lower().replace(' ', '-')}")
            elif '_' in name:
                suggestions.append(f"Try: {name.replace('_', '-')}")
            elif name[0].isupper():
                suggestions.append(f"Try: {name.lower()}")

            return ValidationResult(
                is_valid=False,
                message="Name must be kebab-case (lowercase with hyphens)",
                suggestions=suggestions,
                field_name="name"
            )

        return ValidationResult(
            is_valid=True,
            message=f"Valid skill name: {name}",
            field_name="name"
        )

    @staticmethod
    def validate_description(description: str) -> ValidationResult:
        """
        Validate skill description.

        Args:
            description: Description to validate

        Returns:
            ValidationResult with outcome
        """
        if not description:
            return ValidationResult(
                is_valid=False,
                message="Description cannot be empty",
                field_name="description"
            )

        if len(description) > 200:
            return ValidationResult(
                is_valid=False,
                message="Description is too long (max 200 characters)",
                suggestions=["Keep it concise: focus on WHAT the skill does"],
                field_name="description"
            )

        if len(description) < 10:
            return ValidationResult(
                is_valid=False,
                message="Description is too short (min 10 characters)",
                suggestions=["Be more descriptive about what the skill does"],
                field_name="description"
            )

        return ValidationResult(
            is_valid=True,
            message="Valid description",
            field_name="description"
        )

    @staticmethod
    def validate_version(version: str) -> ValidationResult:
        """
        Validate version is semver format.

        Args:
            version: Version string to validate

        Returns:
            ValidationResult with outcome
        """
        if not version:
            return ValidationResult(
                is_valid=False,
                message="Version cannot be empty",
                suggestions=["Use semver format: 1.0.0"],
                field_name="version"
            )

        # Check semver format (MAJOR.MINOR.PATCH)
        if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
            suggestions = []

            # Try to fix common issues
            if re.match(r'^v?\d+\.\d+$', str(version)):
                # Missing patch version
                clean_version = str(version).lstrip('v')
                suggestions.append(f"Add patch version: {clean_version}.0")
            elif re.match(r'^v\d+\.\d+\.\d+$', str(version)):
                # Has 'v' prefix
                suggestions.append(f"Remove 'v' prefix: {version[1:]}")
            else:
                suggestions.append("Use semver format: MAJOR.MINOR.PATCH (e.g., 1.0.0)")

            return ValidationResult(
                is_valid=False,
                message="Version must be valid semver (e.g., 1.0.0, 2.1.3)",
                suggestions=suggestions,
                field_name="version"
            )

        return ValidationResult(
            is_valid=True,
            message=f"Valid version: {version}",
            field_name="version"
        )

    @staticmethod
    def validate_tool(tool: str) -> ValidationResult:
        """
        Validate a single tool name.

        Args:
            tool: Tool name to validate

        Returns:
            ValidationResult with outcome
        """
        if tool in VALID_TOOLS:
            return ValidationResult(
                is_valid=True,
                message=f"Valid tool: {tool}",
                field_name="allowed-tools"
            )

        # Find case-insensitive matches
        suggestions = []
        for valid_tool in VALID_TOOLS:
            if tool.lower() == valid_tool.lower():
                suggestions.append(f"Did you mean '{valid_tool}'? (case-sensitive)")
                break

        if not suggestions:
            suggestions.append("See available tools with: list_tools.py")

        return ValidationResult(
            is_valid=False,
            message=f"Invalid tool: {tool}",
            suggestions=suggestions,
            field_name="allowed-tools"
        )

    @staticmethod
    def validate_tools(tools: List[str]) -> ValidationResult:
        """
        Validate list of tools.

        Args:
            tools: List of tool names

        Returns:
            ValidationResult with outcome
        """
        if not tools:
            return ValidationResult(
                is_valid=False,
                message="No tools specified",
                suggestions=["Skills typically need at least one tool to be functional"],
                field_name="allowed-tools"
            )

        invalid_tools = []
        suggestions = []

        for tool in tools:
            result = SkillFieldValidator.validate_tool(tool)
            if not result.is_valid:
                invalid_tools.append(tool)
                suggestions.extend(result.suggestions)

        if invalid_tools:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid tools: {', '.join(invalid_tools)}",
                suggestions=suggestions,
                field_name="allowed-tools"
            )

        return ValidationResult(
            is_valid=True,
            message=f"{len(tools)} valid tools",
            field_name="allowed-tools"
        )

    @staticmethod
    def validate_tags(tags: List[str]) -> ValidationResult:
        """
        Validate tags list.

        Args:
            tags: List of tag strings

        Returns:
            ValidationResult with outcome
        """
        if not tags:
            return ValidationResult(
                is_valid=True,
                message="No tags (optional but recommended)",
                suggestions=["Add tags for categorization and discovery"],
                field_name="tags"
            )

        # Check for reasonable tag format
        invalid_tags = []
        for tag in tags:
            if not isinstance(tag, str) or not tag.strip():
                invalid_tags.append(tag)
            elif len(tag) > 50:
                invalid_tags.append(tag)

        if invalid_tags:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid tags: {invalid_tags}",
                suggestions=["Tags should be short, descriptive strings"],
                field_name="tags"
            )

        return ValidationResult(
            is_valid=True,
            message=f"{len(tags)} tags",
            field_name="tags"
        )

    @staticmethod
    def validate_author(author: str) -> ValidationResult:
        """
        Validate author field.

        Args:
            author: Author name

        Returns:
            ValidationResult with outcome
        """
        if not author:
            return ValidationResult(
                is_valid=True,
                message="No author (optional but recommended)",
                suggestions=["Add author for attribution"],
                field_name="author"
            )

        if len(author) > 100:
            return ValidationResult(
                is_valid=False,
                message="Author name too long",
                suggestions=["Keep author name under 100 characters"],
                field_name="author"
            )

        return ValidationResult(
            is_valid=True,
            message=f"Author: {author}",
            field_name="author"
        )


class SkillValidator:
    """Validates complete skill frontmatter."""

    @staticmethod
    def validate_frontmatter(data: Dict) -> List[ValidationResult]:
        """
        Validate complete frontmatter data.

        Args:
            data: Parsed YAML frontmatter dictionary

        Returns:
            List of ValidationResult objects
        """
        results = []

        # Validate required fields
        for field in REQUIRED_FIELDS:
            if field not in data or not data[field]:
                results.append(ValidationResult(
                    is_valid=False,
                    message=f"Missing required field: {field}",
                    suggestions=[f"Add {field}: {REQUIRED_FIELDS[field]}"],
                    field_name=field
                ))
            else:
                # Validate field value
                value = data[field]
                if field == 'name':
                    results.append(SkillFieldValidator.validate_name(value))
                elif field == 'description':
                    results.append(SkillFieldValidator.validate_description(value))
                elif field == 'version':
                    results.append(SkillFieldValidator.validate_version(value))

        # Validate optional fields if present
        if 'allowed-tools' in data:
            results.append(SkillFieldValidator.validate_tools(data['allowed-tools']))

        if 'tags' in data:
            results.append(SkillFieldValidator.validate_tags(data['tags']))

        if 'author' in data:
            results.append(SkillFieldValidator.validate_author(data['author']))

        return results

    @staticmethod
    def has_critical_errors(results: List[ValidationResult]) -> bool:
        """
        Check if validation results contain critical errors.

        Args:
            results: List of validation results

        Returns:
            True if any critical errors found
        """
        for result in results:
            if not result.is_valid and result.field_name in REQUIRED_FIELDS:
                return True
        return False

    @staticmethod
    def get_error_summary(results: List[ValidationResult]) -> str:
        """
        Get human-readable summary of validation errors.

        Args:
            results: List of validation results

        Returns:
            Formatted error summary string
        """
        errors = [r for r in results if not r.is_valid]

        if not errors:
            return "✓ All validations passed"

        lines = [f"Found {len(errors)} validation issue(s):"]
        for i, error in enumerate(errors, 1):
            lines.append(f"  {i}. {error.message}")
            if error.has_suggestions:
                for suggestion in error.suggestions:
                    lines.append(f"     → {suggestion}")

        return "\n".join(lines)


def load_skill_frontmatter(file_path: Path) -> Tuple[Optional[Dict], Optional[str], str]:
    """
    Load and parse skill frontmatter from SKILL.md file.

    Args:
        file_path: Path to SKILL.md file

    Returns:
        Tuple of (parsed_data, yaml_string, error_message)
    """
    try:
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
            return None, None, "No YAML frontmatter found"

        # Extract YAML between delimiters
        yaml_lines = lines[delimiter_indices[0] + 1:delimiter_indices[1]]
        yaml_content = "".join(yaml_lines)

        # Parse YAML
        data = yaml.safe_load(yaml_content)

        return data, yaml_content, ""

    except yaml.YAMLError as e:
        return None, None, f"YAML syntax error: {str(e)}"
    except Exception as e:
        return None, None, f"Error reading file: {str(e)}"


def save_skill_frontmatter(file_path: Path, data: Dict) -> Tuple[bool, str]:
    """
    Save updated frontmatter to SKILL.md file.

    Args:
        file_path: Path to SKILL.md file
        data: Updated frontmatter dictionary

    Returns:
        Tuple of (success, error_message)
    """
    try:
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
            return False, "No YAML frontmatter found"

        # Generate new YAML content
        yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

        # Reconstruct file
        new_lines = (
            lines[:delimiter_indices[0] + 1] +  # First delimiter and before
            [yaml_content] +                     # New YAML content
            lines[delimiter_indices[1]:]         # Second delimiter and after
        )

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        return True, ""

    except Exception as e:
        return False, f"Error saving file: {str(e)}"


if __name__ == "__main__":
    # Test validation functions
    print("Testing field validators...\n")

    # Test name validation
    print("Name validation:")
    print(SkillFieldValidator.validate_name("my-skill"))
    print(SkillFieldValidator.validate_name("My Skill"))
    print(SkillFieldValidator.validate_name("my_skill"))
    print()

    # Test version validation
    print("Version validation:")
    print(SkillFieldValidator.validate_version("1.0.0"))
    print(SkillFieldValidator.validate_version("v1.0.0"))
    print(SkillFieldValidator.validate_version("1.0"))
    print()

    # Test tool validation
    print("Tool validation:")
    print(SkillFieldValidator.validate_tool("Bash"))
    print(SkillFieldValidator.validate_tool("bash"))
    print(SkillFieldValidator.validate_tool("InvalidTool"))
