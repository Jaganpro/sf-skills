#!/usr/bin/env python3
"""
LLM-Powered Evaluation Hook for sf-skills (v4.0)

Uses Claude Haiku for semantic evaluation of code quality, security,
and deployment risk. This hook is called by other hooks (like guardrails.py)
when pattern matching isn't sufficient and semantic analysis is needed.

Use Cases:
- Code quality scoring (best practices adherence)
- Security review (SOQL injection, FLS bypass, sensitive data exposure)
- Deployment risk assessment
- Intent classification for ambiguous patterns

Output Format:
{
    "evaluation": {
        "score": 0-100,
        "risk_level": "low" | "medium" | "high" | "critical",
        "issues": [...],
        "recommendations": [...],
        "should_block": true | false,
        "reason": "..."
    }
}

Usage (called programmatically):
    from llm_eval import evaluate_code, evaluate_command

    result = evaluate_code(code_content, evaluation_type="security")
    result = evaluate_command(command, evaluation_type="deployment_risk")

Note: Requires ANTHROPIC_API_KEY environment variable.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Try to import Anthropic SDK
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Configuration
MODEL = "claude-3-5-haiku-20241022"  # Fast, cost-effective model for hooks
MAX_TOKENS = 1024
TIMEOUT = 25  # seconds

# Evaluation prompts
EVALUATION_PROMPTS = {
    "security": """Analyze this Salesforce code for security vulnerabilities.

Check for:
1. SOQL/SOSL injection (string concatenation in queries)
2. FLS/CRUD bypass (missing WITH USER_MODE or Security.stripInaccessible)
3. Missing "with sharing" keyword
4. Hardcoded credentials or sensitive data
5. XSS vulnerabilities in Lightning components
6. Open redirects
7. Insufficient input validation

Code to analyze:
```
{content}
```

Respond in JSON format:
{{
    "score": <0-100 security score>,
    "risk_level": "<low|medium|high|critical>",
    "issues": [
        {{"type": "<issue_type>", "severity": "<low|medium|high|critical>", "line": <line_number>, "description": "<description>", "fix": "<suggested_fix>"}}
    ],
    "recommendations": ["<recommendation1>", "<recommendation2>"],
    "should_block": <true if critical issues found>,
    "reason": "<summary of findings>"
}}""",

    "code_quality": """Evaluate this Salesforce Apex code for best practices.

Check for:
1. Bulkification (SOQL/DML in loops)
2. Governor limit awareness
3. Proper exception handling
4. Code organization and readability
5. Test coverage indicators
6. Documentation quality
7. Naming conventions

Code to analyze:
```
{content}
```

Respond in JSON format:
{{
    "score": <0-100 quality score>,
    "risk_level": "<low|medium|high>",
    "issues": [
        {{"type": "<issue_type>", "severity": "<low|medium|high>", "line": <line_number>, "description": "<description>", "fix": "<suggested_fix>"}}
    ],
    "recommendations": ["<recommendation1>", "<recommendation2>"],
    "should_block": <true if score < 50>,
    "reason": "<summary of findings>"
}}""",

    "deployment_risk": """Assess the deployment risk of this Salesforce CLI command.

Consider:
1. Target environment (production vs sandbox vs scratch)
2. Operation type (read vs write vs delete)
3. Scope of impact (single record vs bulk vs metadata)
4. Reversibility
5. Presence of safety flags (--dry-run, --check-only)

Command to analyze:
```
{content}
```

Respond in JSON format:
{{
    "score": <0-100 safety score, higher = safer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": [
        {{"type": "<risk_type>", "severity": "<low|medium|high|critical>", "description": "<description>"}}
    ],
    "recommendations": ["<recommendation1>", "<recommendation2>"],
    "should_block": <true if critical risk to production>,
    "reason": "<summary of risk assessment>"
}}""",

    "agent_completion": """Evaluate if this agent task was completed successfully.

Check for:
1. All requested files were created/modified
2. No error messages in output
3. Validation passed (if applicable)
4. Next steps are clear

Task context and output:
```
{content}
```

Respond in JSON format:
{{
    "score": <0-100 completion score>,
    "risk_level": "<low|medium|high>",
    "issues": [
        {{"type": "<issue_type>", "severity": "<low|medium|high>", "description": "<description>"}}
    ],
    "recommendations": ["<next_step1>", "<next_step2>"],
    "should_block": false,
    "reason": "<summary of completion status>",
    "is_complete": <true|false>
}}"""
}


def get_client() -> Optional[Any]:
    """Get Anthropic client if available."""
    if not HAS_ANTHROPIC:
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception:
        return None


def evaluate(content: str, evaluation_type: str = "security") -> Dict[str, Any]:
    """
    Evaluate content using LLM.

    Args:
        content: The code or command to evaluate
        evaluation_type: One of "security", "code_quality", "deployment_risk", "agent_completion"

    Returns:
        Evaluation result dictionary
    """
    # Get the appropriate prompt
    prompt_template = EVALUATION_PROMPTS.get(evaluation_type)
    if not prompt_template:
        return {
            "error": f"Unknown evaluation type: {evaluation_type}",
            "score": 50,
            "risk_level": "medium",
            "issues": [],
            "recommendations": [],
            "should_block": False,
            "reason": "Evaluation type not found"
        }

    # Get client
    client = get_client()
    if not client:
        # Graceful degradation - return neutral result
        return {
            "error": "Anthropic client not available (missing SDK or API key)",
            "score": 50,
            "risk_level": "medium",
            "issues": [],
            "recommendations": ["Install anthropic SDK and set ANTHROPIC_API_KEY for LLM evaluation"],
            "should_block": False,
            "reason": "LLM evaluation unavailable - using default pass-through"
        }

    # Build the prompt
    prompt = prompt_template.format(content=content[:10000])  # Limit content size

    try:
        # Call the API
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and parse the response
        response_text = response.content[0].text

        # Try to extract JSON from the response
        try:
            # Handle case where response might have markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            result = json.loads(response_text)
            return result

        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured error
            return {
                "error": "Failed to parse LLM response as JSON",
                "raw_response": response_text[:500],
                "score": 50,
                "risk_level": "medium",
                "issues": [],
                "recommendations": [],
                "should_block": False,
                "reason": "LLM response parsing failed"
            }

    except anthropic.APIError as e:
        return {
            "error": f"Anthropic API error: {str(e)}",
            "score": 50,
            "risk_level": "medium",
            "issues": [],
            "recommendations": [],
            "should_block": False,
            "reason": "API call failed"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "score": 50,
            "risk_level": "medium",
            "issues": [],
            "recommendations": [],
            "should_block": False,
            "reason": "Evaluation failed"
        }


def evaluate_code(code: str, evaluation_type: str = "security") -> Dict[str, Any]:
    """Evaluate code for security or quality issues."""
    return evaluate(code, evaluation_type)


def evaluate_command(command: str) -> Dict[str, Any]:
    """Evaluate a CLI command for deployment risk."""
    return evaluate(command, "deployment_risk")


def evaluate_agent_output(context: str) -> Dict[str, Any]:
    """Evaluate if an agent task completed successfully."""
    return evaluate(context, "agent_completion")


def format_evaluation_output(result: Dict[str, Any]) -> str:
    """Format evaluation result for display."""
    lines = [f"\n{'═' * 54}"]

    # Header based on risk level
    risk_level = result.get("risk_level", "medium")
    if risk_level == "critical":
        icon = "🛑"
        header = "CRITICAL RISK DETECTED"
    elif risk_level == "high":
        icon = "⚠️"
        header = "HIGH RISK DETECTED"
    elif risk_level == "medium":
        icon = "⚡"
        header = "MEDIUM RISK"
    else:
        icon = "✅"
        header = "LOW RISK"

    lines.append(f"{icon} LLM EVALUATION: {header}")
    lines.append(f"{'═' * 54}")

    # Score
    score = result.get("score", 50)
    score_bar = "█" * (score // 10) + "░" * (10 - score // 10)
    lines.append(f"\n📊 Score: [{score_bar}] {score}/100")

    # Reason
    if result.get("reason"):
        lines.append(f"\n📝 Summary: {result['reason']}")

    # Issues
    issues = result.get("issues", [])
    if issues:
        lines.append(f"\n🔍 Issues Found ({len(issues)}):")
        for issue in issues[:5]:  # Limit to 5 issues
            severity = issue.get("severity", "medium")
            sev_icon = {"critical": "🛑", "high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
            lines.append(f"   {sev_icon} [{severity.upper()}] {issue.get('type', 'Unknown')}")
            if issue.get("description"):
                lines.append(f"      └─ {issue['description'][:60]}")
            if issue.get("fix"):
                lines.append(f"      💡 Fix: {issue['fix'][:60]}")

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append(f"\n💡 Recommendations:")
        for rec in recommendations[:3]:  # Limit to 3
            lines.append(f"   • {rec}")

    # Block decision
    if result.get("should_block"):
        lines.append(f"\n🚫 RECOMMENDATION: BLOCK this operation")
    elif result.get("error"):
        lines.append(f"\n⚠️  Note: {result['error']}")

    lines.append(f"\n{'═' * 54}")

    return "\n".join(lines)


# =============================================================================
# MAIN (for CLI usage)
# =============================================================================

def main():
    """Main entry point for CLI usage."""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # Check for command line arguments
        if len(sys.argv) < 3:
            print(json.dumps({
                "error": "Usage: llm-eval.py <evaluation_type> <content> OR pipe JSON via stdin",
                "score": 50,
                "risk_level": "medium",
                "should_block": False
            }))
            sys.exit(0)

        evaluation_type = sys.argv[1]
        content = sys.argv[2]
        input_data = {
            "evaluation_type": evaluation_type,
            "content": content
        }

    # Extract parameters
    evaluation_type = input_data.get("evaluation_type", "security")
    content = input_data.get("content", "")

    if not content:
        print(json.dumps({
            "error": "No content provided for evaluation",
            "score": 50,
            "risk_level": "medium",
            "should_block": False
        }))
        sys.exit(0)

    # Run evaluation
    result = evaluate(content, evaluation_type)

    # Format output for hooks
    output = {
        "hookSpecificOutput": {
            "hookEventName": "LLMEvaluation",
            "evaluation": result,
            "additionalContext": format_evaluation_output(result)
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
