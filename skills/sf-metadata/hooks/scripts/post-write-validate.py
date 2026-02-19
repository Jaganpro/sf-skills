#!/usr/bin/env python3
"""
Post-Write Validation Hook for sf-metadata plugin.

This hook runs AFTER the Write tool completes and provides validation feedback
for Salesforce metadata files:
- Custom Objects (*.object-meta.xml)
- Custom Fields (*.field-meta.xml)
- Profiles (*.profile-meta.xml)
- Permission Sets (*.permissionset-meta.xml)
- Validation Rules (*.validationRule-meta.xml)
- Record Types (*.recordType-meta.xml)
- Page Layouts (*.layout-meta.xml)

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


def validate_metadata(file_path: str) -> dict:
    """
    Run metadata validation on a Salesforce metadata XML file.

    Returns:
        dict with validation results
    """
    try:
        from validate_metadata import MetadataValidator

        validator = MetadataValidator(file_path)
        results = validator.validate()

        # Format output
        score = results.get('overall_score', 0)
        max_score = results.get('max_score', 120)
        rating = results.get('rating', 'Unknown')
        metadata_type = results.get('metadata_type', 'Unknown')
        issues = []

        for category, data in results.get('categories', {}).items():
            for issue in data.get('issues', []):
                issues.append(f"[{issue.get('severity', 'INFO')}] {issue.get('message', '')}")

        output = f"\n🔍 Metadata Validation: {metadata_type}\n"
        output += f"File: {os.path.basename(file_path)}\n"
        output += f"Score: {score}/{max_score} {rating}\n"

        # Show category breakdown
        categories = results.get('categories', {})
        if categories:
            output += "\nCategory Scores:\n"
            for cat_name, cat_data in categories.items():
                cat_score = cat_data.get('score', 0)
                cat_max = cat_data.get('max_score', 20)
                output += f"  ├─ {cat_name}: {cat_score}/{cat_max}\n"

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
            "output": f"⚠️ Metadata validator not available: {e}"
        }
    except Exception as e:
        return {
            "continue": True,
            "output": f"⚠️ Metadata validation error: {e}"
        }


# Metadata file patterns to validate
METADATA_PATTERNS = [
    ".object-meta.xml",
    ".field-meta.xml",
    ".profile-meta.xml",
    ".permissionset-meta.xml",
    ".validationRule-meta.xml",
    ".recordType-meta.xml",
    ".layout-meta.xml"
]


def is_metadata_file(file_path: str) -> bool:
    """Check if file is a Salesforce metadata file."""
    return any(file_path.endswith(pattern) for pattern in METADATA_PATTERNS)


def main():
    """
    Main hook entry point.

    Reads hook input from stdin, validates metadata files.
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

        # Only validate metadata files
        result = {"continue": True}

        if is_metadata_file(file_path):
            result = validate_metadata(file_path)

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
