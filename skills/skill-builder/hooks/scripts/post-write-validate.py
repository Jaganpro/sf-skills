#!/usr/bin/env python3
"""
Post-Write Validation Hook for skill-builder plugin.

This hook runs AFTER the Write tool completes and provides validation feedback
for SKILL.md files.

Hook Input (stdin): JSON with tool_input and tool_response
Hook Output (stdout): JSON with optional output message

This hook is ADVISORY - it provides feedback but does not block writes.
"""

import sys
import os
import json

# Add script directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def validate_skill_file(file_path: str) -> dict:
    """
    Run YAML frontmatter validation on a SKILL.md file.

    Returns:
        dict with validation results
    """
    try:
        from pathlib import Path
        from io import StringIO
        import sys as _sys

        # Capture stdout from validate_skill_file
        old_stdout = _sys.stdout
        _sys.stdout = captured = StringIO()

        try:
            from validate_skill import validate_skill_file as _validate
            is_valid = _validate(Path(file_path))
        finally:
            _sys.stdout = old_stdout

        output = captured.getvalue()

        # Summarize the output
        skill_name = os.path.basename(os.path.dirname(file_path))
        summary = f"\n🔍 SKILL.md Validation: {skill_name}\n"

        if is_valid:
            summary += "✅ Skill file is valid!\n"
        else:
            summary += "❌ Validation failed. Check output above for details.\n"

        return {
            "continue": True,
            "output": summary + output
        }

    except ImportError as e:
        return {
            "continue": True,
            "output": f"⚠️ Skill validator not available: {e}"
        }
    except Exception as e:
        return {
            "continue": True,
            "output": f"⚠️ Skill validation error: {e}"
        }


def main():
    """
    Main hook entry point.

    Reads hook input from stdin, validates SKILL.md files.
    """
    try:
        # Read hook input from stdin
        hook_input = json.load(sys.stdin)

        # Extract file path from tool input
        tool_input = hook_input.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        # Check if write was successful
        tool_response = hook_input.get("tool_response", {})
        if not tool_response.get("success", True):
            # Write failed, don't validate
            print(json.dumps({"continue": True}))
            return 0

        # Only validate SKILL.md files
        result = {"continue": True}

        if file_path.endswith("SKILL.md"):
            result = validate_skill_file(file_path)

        # Output result
        print(json.dumps(result))
        return 0

    except json.JSONDecodeError:
        # No valid JSON input, continue silently
        print(json.dumps({"continue": True}))
        return 0
    except Exception as e:
        # Unexpected error, log but don't block
        print(json.dumps({
            "continue": True,
            "output": f"⚠️ Hook error: {e}"
        }))
        return 0


if __name__ == "__main__":
    sys.exit(main())
