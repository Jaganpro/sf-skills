#!/usr/bin/env python3
"""
dependency_validator.py - Dependency validation and checking

Validates skill dependencies:
- Checks if dependencies are installed
- Verifies version constraints are satisfied
- Detects circular dependencies
- Builds dependency graphs
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml")
    import sys
    sys.exit(1)

from version_resolver import VersionResolver


@dataclass
class Dependency:
    """Represents a skill dependency."""
    name: str
    version_constraint: str
    required: bool = True

    def __str__(self) -> str:
        req_str = "" if self.required else " [optional]"
        return f"{self.name} ({self.version_constraint}){req_str}"


@dataclass
class DependencyCheckResult:
    """Result of checking a single dependency."""
    dependency: Dependency
    is_satisfied: bool
    installed: bool
    installed_version: Optional[str] = None
    message: str = ""

    def __str__(self) -> str:
        status = "✓" if self.is_satisfied else "✗"
        if not self.installed:
            return f"{status} {self.dependency.name} → NOT INSTALLED"
        else:
            return f"{status} {self.dependency.name} ({self.dependency.version_constraint}) → {self.installed_version} {self.message}"


@dataclass
class CircularDependencyError:
    """Represents a circular dependency."""
    cycle_path: List[str]

    def __str__(self) -> str:
        return f"Circular dependency: {' → '.join(self.cycle_path)} → {self.cycle_path[0]}"


class DependencyValidator:
    """Validates and checks skill dependencies."""

    def __init__(self, skills_dir: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            skills_dir: Path to skills directory (default: ~/.claude/skills/)
        """
        if skills_dir is None:
            self.skills_dir = Path.home() / ".claude/skills"
        else:
            self.skills_dir = skills_dir

    def load_skill_metadata(self, skill_name: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Load skill's SKILL.md frontmatter.

        Args:
            skill_name: Name of skill to load

        Returns:
            Tuple of (metadata_dict, error_message)
        """
        skill_path = self.skills_dir / skill_name / "SKILL.md"

        if not skill_path.exists():
            return None, f"Skill not found: {skill_name}"

        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find frontmatter delimiters
            delimiter_indices = []
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    delimiter_indices.append(i)
                    if len(delimiter_indices) == 2:
                        break

            if len(delimiter_indices) < 2:
                return None, f"No frontmatter found in {skill_name}/SKILL.md"

            # Extract and parse YAML
            yaml_lines = lines[delimiter_indices[0] + 1:delimiter_indices[1]]
            yaml_content = "".join(yaml_lines)
            data = yaml.safe_load(yaml_content)

            return data, None

        except Exception as e:
            return None, f"Error loading {skill_name}: {str(e)}"

    def parse_dependencies(self, data: Dict) -> List[Dependency]:
        """
        Parse dependencies from skill metadata.

        Args:
            data: Parsed YAML frontmatter

        Returns:
            List of Dependency objects
        """
        deps = []

        if 'dependencies' not in data or not data['dependencies']:
            return deps

        for dep_item in data['dependencies']:
            if isinstance(dep_item, str):
                # Simple format: "skill-name@^1.0.0"
                if '@' in dep_item:
                    name, version_constraint = dep_item.split('@', 1)
                else:
                    name = dep_item
                    version_constraint = '*'

                deps.append(Dependency(
                    name=name.strip(),
                    version_constraint=version_constraint.strip(),
                    required=True
                ))

            elif isinstance(dep_item, dict):
                # Detailed format with name, version, required fields
                name = dep_item.get('name', '')
                version_constraint = dep_item.get('version', '*')
                required = dep_item.get('required', True)

                if name:
                    deps.append(Dependency(
                        name=name,
                        version_constraint=version_constraint,
                        required=required
                    ))

        return deps

    def check_dependency(self, dependency: Dependency) -> DependencyCheckResult:
        """
        Check if a dependency is satisfied.

        Args:
            dependency: Dependency to check

        Returns:
            DependencyCheckResult with outcome
        """
        # Load dependency skill metadata
        dep_metadata, error = self.load_skill_metadata(dependency.name)

        if error or dep_metadata is None:
            return DependencyCheckResult(
                dependency=dependency,
                is_satisfied=False,
                installed=False,
                message="Not installed"
            )

        # Get installed version
        installed_version = dep_metadata.get('version', '0.0.0')

        # Parse constraint
        constraint = VersionResolver.parse_constraint(dependency.version_constraint)
        if not constraint:
            return DependencyCheckResult(
                dependency=dependency,
                is_satisfied=False,
                installed=True,
                installed_version=installed_version,
                message="Invalid version constraint"
            )

        # Check if version satisfies constraint
        satisfies, reason = VersionResolver.satisfies(constraint, installed_version)

        return DependencyCheckResult(
            dependency=dependency,
            is_satisfied=satisfies,
            installed=True,
            installed_version=installed_version,
            message=reason
        )

    def check_all_dependencies(self, skill_name: str) -> Tuple[List[DependencyCheckResult], Optional[str]]:
        """
        Check all dependencies for a skill.

        Args:
            skill_name: Name of skill to check

        Returns:
            Tuple of (list of results, error_message)
        """
        # Load skill metadata
        metadata, error = self.load_skill_metadata(skill_name)
        if error or metadata is None:
            return [], error

        # Parse dependencies
        dependencies = self.parse_dependencies(metadata)

        if not dependencies:
            return [], None

        # Check each dependency
        results = []
        for dep in dependencies:
            result = self.check_dependency(dep)
            results.append(result)

        return results, None

    def detect_circular_dependencies(self, skill_name: str, visited: Optional[Set[str]] = None, path: Optional[List[str]] = None) -> Optional[CircularDependencyError]:
        """
        Detect circular dependencies recursively.

        Args:
            skill_name: Name of skill to check
            visited: Set of visited skills
            path: Current dependency path

        Returns:
            CircularDependencyError if found, None otherwise
        """
        if visited is None:
            visited = set()
        if path is None:
            path = []

        # Check if we've seen this skill in current path
        if skill_name in path:
            # Found a cycle
            cycle_start = path.index(skill_name)
            cycle_path = path[cycle_start:] + [skill_name]
            return CircularDependencyError(cycle_path=cycle_path)

        # Skip if already fully explored
        if skill_name in visited:
            return None

        # Load skill metadata
        metadata, error = self.load_skill_metadata(skill_name)
        if error or metadata is None:
            # Can't load, skip
            return None

        # Parse dependencies
        dependencies = self.parse_dependencies(metadata)

        # Explore each dependency
        path.append(skill_name)

        for dep in dependencies:
            circular_error = self.detect_circular_dependencies(dep.name, visited, path[:])
            if circular_error:
                return circular_error

        visited.add(skill_name)
        return None

    def build_dependency_tree(self, skill_name: str, depth: int = 0, max_depth: int = 10, seen: Optional[Set[str]] = None) -> List[str]:
        """
        Build a dependency tree visualization.

        Args:
            skill_name: Root skill name
            depth: Current depth level
            max_depth: Maximum recursion depth
            seen: Set of seen skills (to avoid infinite loops)

        Returns:
            List of formatted tree lines
        """
        if seen is None:
            seen = set()

        if depth >= max_depth:
            return [f"{'  ' * depth}└─ [max depth reached]"]

        if skill_name in seen:
            return [f"{'  ' * depth}└─ {skill_name} [already shown]"]

        seen.add(skill_name)

        lines = []

        # Load skill metadata
        metadata, error = self.load_skill_metadata(skill_name)

        if error or metadata is None:
            if depth == 0:
                lines.append(f"{skill_name} → NOT FOUND")
            return lines

        version = metadata.get('version', 'unknown')

        # Root skill
        if depth == 0:
            lines.append(f"{skill_name} ({version})")

        # Parse dependencies
        dependencies = self.parse_dependencies(metadata)

        if not dependencies:
            return lines

        # Add each dependency
        for i, dep in enumerate(dependencies):
            is_last = (i == len(dependencies) - 1)
            prefix = "└─" if is_last else "├─"

            # Check dependency
            result = self.check_dependency(dep)

            if result.installed:
                status = "✓" if result.is_satisfied else "✗"
                optional_str = " [optional]" if not dep.required else ""
                line = f"{'  ' * (depth + 1)}{prefix} {dep.name} ({dep.version_constraint}) → {result.installed_version} {status}{optional_str}"
            else:
                line = f"{'  ' * (depth + 1)}{prefix} {dep.name} ({dep.version_constraint}) → NOT INSTALLED ✗"

            lines.append(line)

            # Recurse into dependency's dependencies
            if result.installed:
                subtree = self.build_dependency_tree(dep.name, depth + 1, max_depth, seen)
                lines.extend(subtree)

        return lines


if __name__ == "__main__":
    # Test dependency validation
    import sys

    print("Testing Dependency Validator...\n")

    validator = DependencyValidator()

    # Test with skill-builder (which should have no dependencies)
    print("Checking skill-builder dependencies:")
    results, error = validator.check_all_dependencies("skill-builder")

    if error:
        print(f"ERROR: {error}")
    elif not results:
        print("  No dependencies")
    else:
        for result in results:
            print(f"  {result}")

    print("\nDependency tree:")
    tree = validator.build_dependency_tree("skill-builder")
    for line in tree:
        print(line)
