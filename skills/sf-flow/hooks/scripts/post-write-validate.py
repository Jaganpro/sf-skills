#!/usr/bin/env python3
"""
Post-Write Validation Hook for sf-flow plugin.

This hook runs AFTER the Write tool completes and provides validation feedback
for Salesforce Flow files (*.flow-meta.xml).

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


def validate_flow(file_path: str) -> dict:
    """
    Run Flow validation on a flow-meta.xml file.

    Returns:
        dict with validation results
    """
    try:
        from validate_flow import EnhancedFlowValidator

        validator = EnhancedFlowValidator(file_path)
        results = validator.validate()

        # Format output
        score = results.get('overall_score', 0)
        rating = results.get('rating', 'Unknown')
        issues = []

        for category, data in results.get('categories', {}).items():
            for issue in data.get('issues', []):
                issues.append(f"[{issue.get('severity', 'INFO')}] {issue.get('message', '')}")

        output = f"\n🔍 Flow Validation: {results.get('flow_name', 'Unknown')}\n"
        output += f"Score: {score}/110 {rating}\n"

        if issues:
            output += "\nIssues found:\n"
            for issue in issues[:10]:  # Limit to first 10 issues
                output += f"  • {issue}\n"
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
            "output": f"⚠️ Flow validator not available: {e}"
        }
    except Exception as e:
        return {
            "continue": True,
            "output": f"⚠️ Flow validation error: {e}"
        }


def main():
    """
    Main hook entry point.

    Reads hook input from stdin, validates Flow files.
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

        # Only validate Flow files
        result = {"continue": True}

        if file_path.endswith(".flow-meta.xml"):
            result = validate_flow(file_path)

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
