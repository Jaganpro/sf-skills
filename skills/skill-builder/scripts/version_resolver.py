#!/usr/bin/env python3
"""
version_resolver.py - Semantic version parsing and constraint resolution

Supports common version constraint syntaxes:
- ^1.2.0 : Compatible (>=1.2.0 <2.0.0)
- ~1.2.0 : Approximately (>=1.2.0 <1.3.0)
- >=1.2.0 : Greater than or equal
- 1.2.0 : Exact version
- * : Any version
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass
from packaging import version


@dataclass
class VersionConstraint:
    """Represents a version constraint."""
    operator: str  # '^', '~', '>=', '==', '*'
    version_str: str  # Original version string
    parsed_version: Optional[version.Version] = None

    def __str__(self) -> str:
        """String representation."""
        if self.operator == '*':
            return '*'
        elif self.operator == '^':
            return f"^{self.version_str}"
        elif self.operator == '~':
            return f"~{self.version_str}"
        else:
            return f"{self.operator}{self.version_str}"


class VersionResolver:
    """Resolves version constraints for dependency management."""

    @staticmethod
    def parse_constraint(constraint_str: str) -> Optional[VersionConstraint]:
        """
        Parse a version constraint string.

        Args:
            constraint_str: Version constraint (e.g., "^1.2.0", ">=1.0.0")

        Returns:
            VersionConstraint object or None if invalid
        """
        constraint_str = constraint_str.strip()

        # Handle wildcard
        if constraint_str == '*':
            return VersionConstraint(operator='*', version_str='*')

        # Handle caret (^) - compatible with
        if constraint_str.startswith('^'):
            version_str = constraint_str[1:].strip()
            try:
                parsed = version.parse(version_str)
                return VersionConstraint(operator='^', version_str=version_str, parsed_version=parsed)
            except version.InvalidVersion:
                return None

        # Handle tilde (~) - approximately
        if constraint_str.startswith('~'):
            version_str = constraint_str[1:].strip()
            try:
                parsed = version.parse(version_str)
                return VersionConstraint(operator='~', version_str=version_str, parsed_version=parsed)
            except version.InvalidVersion:
                return None

        # Handle comparison operators (>=, >, <=, <, ==)
        match = re.match(r'^(>=|>|<=|<|==)?\s*(.+)$', constraint_str)
        if match:
            op = match.group(1) or '=='
            version_str = match.group(2).strip()

            try:
                parsed = version.parse(version_str)
                return VersionConstraint(operator=op, version_str=version_str, parsed_version=parsed)
            except version.InvalidVersion:
                return None

        return None

    @staticmethod
    def satisfies(constraint: VersionConstraint, check_version: str) -> Tuple[bool, str]:
        """
        Check if a version satisfies a constraint.

        Args:
            constraint: VersionConstraint to check against
            check_version: Version string to check

        Returns:
            Tuple of (satisfies, reason)
        """
        try:
            check_ver = version.parse(check_version)
        except version.InvalidVersion:
            return False, f"Invalid version: {check_version}"

        # Wildcard matches anything
        if constraint.operator == '*':
            return True, "Matches wildcard (*)"

        if constraint.parsed_version is None:
            return False, "Invalid constraint"

        # Caret (^) - compatible with (same major version for >=1.0.0)
        if constraint.operator == '^':
            base = constraint.parsed_version
            base_parts = VersionResolver._parse_version_parts(constraint.version_str)

            if base_parts[0] == 0:
                # ^0.x.y is more restrictive (0.x.y <= version < 0.x+1.0)
                if base_parts[1] == 0:
                    # ^0.0.y means exactly 0.0.y
                    if check_ver == base:
                        return True, f"Exactly {constraint.version_str}"
                    else:
                        return False, f"Must be exactly {constraint.version_str} for ^0.0.y"
                else:
                    # ^0.x.y means >= 0.x.y < 0.x+1.0
                    upper_minor = version.parse(f"0.{base_parts[1] + 1}.0")
                    if check_ver >= base and check_ver < upper_minor:
                        return True, f"Compatible with ^{constraint.version_str} (0.x range)"
                    else:
                        return False, f"Must be >=0.{base_parts[1]}.0 <0.{base_parts[1]+1}.0"
            else:
                # ^x.y.z means >= x.y.z < x+1.0.0
                upper_major = version.parse(f"{base_parts[0] + 1}.0.0")
                if check_ver >= base and check_ver < upper_major:
                    return True, f"Compatible with ^{constraint.version_str}"
                else:
                    return False, f"Must be >={base} <{upper_major}"

        # Tilde (~) - approximately (patch-level changes allowed)
        elif constraint.operator == '~':
            base = constraint.parsed_version
            base_parts = VersionResolver._parse_version_parts(constraint.version_str)

            # ~x.y.z means >= x.y.z < x.y+1.0
            upper_minor = version.parse(f"{base_parts[0]}.{base_parts[1] + 1}.0")
            if check_ver >= base and check_ver < upper_minor:
                return True, f"Approximately {constraint.version_str}"
            else:
                return False, f"Must be >={base} <{upper_minor}"

        # Standard comparison operators
        elif constraint.operator == '>=':
            if check_ver >= constraint.parsed_version:
                return True, f">= {constraint.version_str}"
            else:
                return False, f"Must be >= {constraint.version_str}"

        elif constraint.operator == '>':
            if check_ver > constraint.parsed_version:
                return True, f"> {constraint.version_str}"
            else:
                return False, f"Must be > {constraint.version_str}"

        elif constraint.operator == '<=':
            if check_ver <= constraint.parsed_version:
                return True, f"<= {constraint.version_str}"
            else:
                return False, f"Must be <= {constraint.version_str}"

        elif constraint.operator == '<':
            if check_ver < constraint.parsed_version:
                return True, f"< {constraint.version_str}"
            else:
                return False, f"Must be < {constraint.version_str}"

        elif constraint.operator == '==':
            if check_ver == constraint.parsed_version:
                return True, f"Exactly {constraint.version_str}"
            else:
                return False, f"Must be exactly {constraint.version_str}"

        return False, "Unknown constraint operator"

    @staticmethod
    def _parse_version_parts(version_str: str) -> Tuple[int, int, int]:
        """
        Parse version string into (major, minor, patch) tuple.

        Args:
            version_str: Version string (e.g., "1.2.3")

        Returns:
            Tuple of (major, minor, patch)
        """
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)

    @staticmethod
    def compare_versions(v1: str, v2: str) -> int:
        """
        Compare two version strings.

        Args:
            v1: First version
            v2: Second version

        Returns:
            -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
        """
        try:
            ver1 = version.parse(v1)
            ver2 = version.parse(v2)

            if ver1 < ver2:
                return -1
            elif ver1 > ver2:
                return 1
            else:
                return 0
        except version.InvalidVersion:
            return 0

    @staticmethod
    def is_valid_semver(version_str: str) -> bool:
        """
        Check if a string is valid semver.

        Args:
            version_str: Version string to validate

        Returns:
            True if valid semver
        """
        try:
            version.parse(version_str)
            return True
        except version.InvalidVersion:
            return False

    @staticmethod
    def get_constraint_range(constraint_str: str) -> str:
        """
        Get human-readable range description for a constraint.

        Args:
            constraint_str: Version constraint string

        Returns:
            Human-readable description
        """
        constraint = VersionResolver.parse_constraint(constraint_str)
        if not constraint:
            return "Invalid constraint"

        if constraint.operator == '*':
            return "Any version"

        if constraint.operator == '^':
            parts = VersionResolver._parse_version_parts(constraint.version_str)
            if parts[0] == 0:
                if parts[1] == 0:
                    return f"Exactly {constraint.version_str}"
                else:
                    return f">={constraint.version_str} <0.{parts[1]+1}.0"
            else:
                return f">={constraint.version_str} <{parts[0]+1}.0.0"

        elif constraint.operator == '~':
            parts = VersionResolver._parse_version_parts(constraint.version_str)
            return f">={constraint.version_str} <{parts[0]}.{parts[1]+1}.0"

        elif constraint.operator == '==':
            return f"Exactly {constraint.version_str}"

        else:
            return f"{constraint.operator} {constraint.version_str}"


if __name__ == "__main__":
    # Test version resolution
    print("Testing Version Resolver...\n")

    test_cases = [
        ("^1.2.0", "1.3.0", True),
        ("^1.2.0", "2.0.0", False),
        ("^1.2.0", "1.1.0", False),
        ("~1.2.0", "1.2.5", True),
        ("~1.2.0", "1.3.0", False),
        (">=1.0.0", "2.0.0", True),
        (">=1.0.0", "0.9.0", False),
        ("1.2.0", "1.2.0", True),
        ("1.2.0", "1.2.1", False),
        ("*", "99.99.99", True),
    ]

    for constraint_str, check_ver, expected in test_cases:
        constraint = VersionResolver.parse_constraint(constraint_str)
        satisfies, reason = VersionResolver.satisfies(constraint, check_ver)

        status = "✓" if satisfies == expected else "✗"
        print(f"{status} {constraint_str} vs {check_ver}: {satisfies} ({reason})")

    print("\nConstraint ranges:")
    for const in ["^1.2.0", "~1.2.0", ">=1.0.0", "*", "1.2.0"]:
        desc = VersionResolver.get_constraint_range(const)
        print(f"  {const:12s} → {desc}")
