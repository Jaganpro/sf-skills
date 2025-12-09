#!/usr/bin/env python3
"""
Post-write validation hook for sf-agentforce skill.
Validates Agent Script files after they are written.
"""

import json
import sys
import os

# Add the scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_agentforce import AgentScriptValidator


def main():
    """Main entry point for the post-write hook."""
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())

        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})

        file_path = tool_input.get("file_path", "")

        # Only validate .agentscript files
        if not file_path.endswith(".agentscript"):
            print(json.dumps({"continue": True}))
            return

        # Check if the write was successful
        if "error" in tool_response:
            print(json.dumps({"continue": True}))
            return

        # Get the content that was written
        content = tool_input.get("content", "")

        if not content:
            print(json.dumps({"continue": True}))
            return

        # Validate the Agent Script
        validator = AgentScriptValidator()
        result = validator.validate(content, file_path)

        # Format output
        output_lines = []
        output_lines.append("")
        output_lines.append("═" * 60)
        output_lines.append("🤖 AGENTFORCE VALIDATION")
        output_lines.append("═" * 60)
        output_lines.append("")

        # Score display
        score = result["score"]
        max_score = result["max_score"]
        percentage = (score / max_score) * 100 if max_score > 0 else 0

        # Rating stars
        if percentage >= 90:
            stars = "⭐⭐⭐⭐⭐"
            rating = "Excellent"
        elif percentage >= 80:
            stars = "⭐⭐⭐⭐"
            rating = "Very Good"
        elif percentage >= 70:
            stars = "⭐⭐⭐"
            rating = "Good"
        elif percentage >= 60:
            stars = "⭐⭐"
            rating = "Needs Work"
        else:
            stars = "⭐"
            rating = "Critical Issues"

        output_lines.append(f"Score: {score}/{max_score} {stars} {rating}")
        output_lines.append("")

        # Category breakdown
        for category, details in result["categories"].items():
            cat_score = details["score"]
            cat_max = details["max"]
            cat_pct = (cat_score / cat_max) * 100 if cat_max > 0 else 0
            output_lines.append(f"├─ {category}: {cat_score}/{cat_max} ({cat_pct:.0f}%)")

        output_lines.append("")

        # Issues
        if result["issues"]:
            output_lines.append("Issues:")
            for issue in result["issues"]:
                severity = issue.get("severity", "warning")
                icon = "❌" if severity == "error" else "⚠️"
                category = issue.get("category", "General")
                message = issue.get("message", "")
                line = issue.get("line")
                line_info = f" (line {line})" if line else ""
                output_lines.append(f"{icon} [{category}]{line_info} {message}")
        else:
            output_lines.append("✅ No issues found!")

        output_lines.append("")
        output_lines.append("═" * 60)

        output_message = "\n".join(output_lines)

        # Determine if we should block (critical issues)
        should_block = percentage < 60 and any(
            issue.get("severity") == "error" for issue in result["issues"]
        )

        response = {
            "continue": not should_block,
            "output": output_message
        }

        if should_block:
            response["stopReason"] = "Agent Script validation failed with critical issues. Please fix errors before proceeding."

        print(json.dumps(response))

    except Exception as e:
        # On error, allow the write to proceed but log the error
        print(json.dumps({
            "continue": True,
            "output": f"⚠️ Validation error: {str(e)}"
        }))


if __name__ == "__main__":
    main()
