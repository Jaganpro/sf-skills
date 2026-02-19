#!/usr/bin/env python3
"""
Post-Write Validation Hook for sf-apex plugin.

This hook runs AFTER the Write tool completes and provides validation feedback
for Salesforce Apex files (*.cls, *.trigger).

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


def validate_apex(file_path: str) -> dict:
    """
    Run Apex validation on .cls or .trigger files.

    Returns:
        dict with validation results
    """
    try:
        from validate_apex import ApexValidator

        validator = ApexValidator(file_path)
        results = validator.validate()

        output = f"\n🔍 Apex Validation: {os.path.basename(file_path)}\n"
        output += f"Score: {results.get('score', 0)}/150\n"

        issues = results.get('issues', [])
        if issues:
            output += "Issues found:\n"
            for issue in issues[:10]:
                output += f"  • [{issue.get('severity', 'INFO')}] {issue.get('message', '')}\n"
            if len(issues) > 10:
                output += f"  ... and {len(issues) - 10} more issues\n"
        else:
            output += "✅ No issues found!\n"

        return {
            "continue": True,
            "output": output
        }

    except ImportError as e:
        return {
            "continue": True,
            "output": f"⚠️ Apex validator not available: {e}"
        }
    except Exception as e:
        return {
            "continue": True,
            "output": f"⚠️ Apex validation error: {e}"
        }


def main():
    """
    Main hook entry point.

    Reads hook input from stdin, validates Apex files.
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

        # Only validate Apex files
        result = {"continue": True}

        if file_path.endswith(".cls") or file_path.endswith(".trigger"):
            result = validate_apex(file_path)

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
