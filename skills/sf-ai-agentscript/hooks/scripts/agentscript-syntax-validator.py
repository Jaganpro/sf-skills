#!/usr/bin/env python3
"""
Agent Script Syntax Validator
=============================

PostToolUse hook that validates .agent files for common syntax errors
based on Agent Script DSL documentation.

Checks for:
- Mixed tabs and spaces (compilation error)
- Lowercase booleans (must be True/False)
- Missing required blocks (system, config, topic, start_agent)
- Missing default_agent_user in config
- Variables declared as both mutable AND linked
- Undefined topic references in transitions
- Post-action checks not at top of instructions

Usage:
    Triggered automatically by hooks.json configuration
    Input: JSON from stdin with tool_name and tool_input
    Output: Diagnostic messages to stdout (or empty if valid)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


class AgentScriptValidator:
    """Validates Agent Script syntax for common errors."""

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.errors: List[Tuple[int, str, str]] = []  # (line_num, severity, message)
        self.warnings: List[Tuple[int, str, str]] = []

    def validate(self) -> dict:
        """Run all validations and return results."""
        self._check_mixed_indentation()
        self._check_boolean_case()
        self._check_required_blocks()
        self._check_default_agent_user()
        self._check_mutable_linked_conflict()
        self._check_undefined_topics()
        self._check_post_action_position()

        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "file_path": self.file_path,
        }

    def _check_mixed_indentation(self):
        """Check for mixed tabs and spaces."""
        has_tabs = False
        has_spaces = False
        tab_line = None
        space_line = None

        for i, line in enumerate(self.lines, 1):
            # Check leading whitespace
            leading = len(line) - len(line.lstrip())
            if leading > 0:
                leading_chars = line[:leading]
                if '\t' in leading_chars:
                    has_tabs = True
                    if tab_line is None:
                        tab_line = i
                if ' ' in leading_chars:
                    has_spaces = True
                    if space_line is None:
                        space_line = i

        if has_tabs and has_spaces:
            self.errors.append((
                tab_line or 1,
                "error",
                f"Mixed tabs and spaces detected. Tabs first seen on line {tab_line}, "
                f"spaces first seen on line {space_line}. Use consistent indentation "
                "(all tabs OR all spaces)."
            ))

    def _check_boolean_case(self):
        """Check for lowercase boolean values."""
        # Pattern to match boolean assignments
        bool_pattern = re.compile(r'=\s*(true|false)\s*(?:#|$)', re.IGNORECASE)

        for i, line in enumerate(self.lines, 1):
            match = bool_pattern.search(line)
            if match:
                value = match.group(1)
                if value.lower() == 'true' and value != 'True':
                    self.errors.append((
                        i,
                        "error",
                        f"Boolean must be capitalized: use 'True' instead of '{value}'"
                    ))
                elif value.lower() == 'false' and value != 'False':
                    self.errors.append((
                        i,
                        "error",
                        f"Boolean must be capitalized: use 'False' instead of '{value}'"
                    ))

    def _check_required_blocks(self):
        """Check for required blocks: system, config, topic, start_agent."""
        required = {
            'system:': False,
            'config:': False,
            'topic ': False,  # topic followed by name
            'start_agent ': False,  # start_agent followed by name
        }

        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('system:'):
                required['system:'] = True
            elif stripped.startswith('config:'):
                required['config:'] = True
            elif stripped.startswith('topic '):
                required['topic '] = True
            elif stripped.startswith('start_agent '):
                required['start_agent '] = True

        missing = [k.strip(':').strip() for k, v in required.items() if not v]
        if missing:
            self.errors.append((
                1,
                "error",
                f"Missing required blocks: {', '.join(missing)}. "
                "Every agent needs system, config, at least one topic, and start_agent."
            ))

    def _check_default_agent_user(self):
        """Check if default_agent_user is present in config."""
        in_config = False
        has_default_agent_user = False

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()

            if stripped.startswith('config:'):
                in_config = True
                continue

            # Check if we've left config block (another top-level block)
            if in_config and stripped and not stripped.startswith('#'):
                if re.match(r'^(system|variables|language|connections|topic|start_agent)\s*:', stripped):
                    in_config = False

            if in_config and 'default_agent_user' in stripped:
                has_default_agent_user = True

        if not has_default_agent_user:
            self.errors.append((
                1,
                "error",
                "Missing 'default_agent_user' in config block. This is REQUIRED. "
                "Set it to a valid Einstein Agent User, e.g., default_agent_user: \"agent@yourorg.com\""
            ))

    def _check_mutable_linked_conflict(self):
        """Check for variables declared as both mutable AND linked."""
        pattern = re.compile(r'mutable\s+linked|linked\s+mutable', re.IGNORECASE)

        for i, line in enumerate(self.lines, 1):
            if pattern.search(line):
                self.errors.append((
                    i,
                    "error",
                    "Variable cannot be both 'mutable' AND 'linked'. "
                    "Use 'mutable' for changeable state, 'linked' for external read-only data."
                ))

    def _check_undefined_topics(self):
        """Check for transitions to undefined topics."""
        # Collect all defined topics
        topic_pattern = re.compile(r'^(topic|start_agent)\s+(\w+):')
        defined_topics = set()

        for line in self.lines:
            match = topic_pattern.match(line.strip())
            if match:
                defined_topics.add(match.group(2))

        # Find all topic references
        ref_pattern = re.compile(r'@topic\.(\w+)')

        for i, line in enumerate(self.lines, 1):
            for match in ref_pattern.finditer(line):
                topic_name = match.group(1)
                if topic_name not in defined_topics:
                    self.warnings.append((
                        i,
                        "warning",
                        f"Reference to undefined topic '@topic.{topic_name}'. "
                        "Ensure this topic is defined in the agent script."
                    ))

    def _check_post_action_position(self):
        """Warn if post-action checks appear after LLM instructions."""
        # This is a heuristic check - look for patterns that suggest
        # post-action checks are at the bottom instead of the top
        in_instructions = False
        seen_pipe_text = False
        instruction_start_line = None

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()

            if 'instructions:' in stripped:
                in_instructions = True
                instruction_start_line = i
                seen_pipe_text = False
                continue

            if in_instructions:
                # Check if we've left instructions block
                if stripped.startswith('actions:') or stripped.startswith('topic ') or stripped.startswith('start_agent '):
                    in_instructions = False
                    continue

                # Look for pipe text (LLM instructions)
                if stripped.startswith('|'):
                    seen_pipe_text = True

                # If we've seen pipe text and now see a post-action check pattern
                if seen_pipe_text and '@variables.' in stripped:
                    if any(x in stripped for x in ['_status', '_done', '_complete', '_processed']):
                        if stripped.startswith('if '):
                            self.warnings.append((
                                i,
                                "warning",
                                "Post-action check appears AFTER LLM instructions. "
                                "Consider moving this check to the TOP of instructions "
                                "so it triggers on the topic loop after action completion."
                            ))


def format_output(result: dict) -> str:
    """Format validation results for Claude."""
    lines = []
    file_name = Path(result["file_path"]).name

    if result["success"] and not result["warnings"]:
        # Show success message
        lines.append(f"✅ Agent Script LSP Validation Passed: {file_name}")
        lines.append("   • Syntax check: OK")
        lines.append("   • Required blocks: OK")
        lines.append("   • Topic references: OK")
        return "\n".join(lines)

    if result["errors"]:
        lines.append(f"❌ Agent Script validation errors in {file_name}:")
        lines.append("")
        for line_num, severity, message in result["errors"]:
            lines.append(f"  Line {line_num}: {message}")
        lines.append("")
        lines.append("Fix these errors before deployment.")

    if result["warnings"]:
        if lines:
            lines.append("")
        lines.append(f"⚠️ Agent Script warnings in {file_name}:")
        lines.append("")
        for line_num, severity, message in result["warnings"]:
            lines.append(f"  Line {line_num}: {message}")

    return "\n".join(lines)


def main():
    """Main hook entry point."""
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Extract file path
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only validate .agent files
    if not file_path.endswith(".agent"):
        sys.exit(0)

    # Check if file exists
    if not os.path.exists(file_path):
        sys.exit(0)

    # Read file content
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️ Could not read {file_path}: {e}")
        sys.exit(0)

    # Validate
    validator = AgentScriptValidator(content, file_path)
    result = validator.validate()

    # Output results
    output = format_output(result)
    if output:
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
