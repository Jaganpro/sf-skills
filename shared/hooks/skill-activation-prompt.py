#!/usr/bin/env python3
"""
UserPromptSubmit hook for sf-skills auto-activation.

This hook analyzes user prompts BEFORE Claude sees them and suggests
relevant skills based on keyword and intent pattern matching.

How it works:
1. User submits prompt: "I need to create an apex trigger for Account"
2. This hook fires (UserPromptSubmit event)
3. Matches "apex" + "trigger" keywords → sf-apex skill (score: 5)
4. Returns suggestion: "💡 Consider invoking /sf-apex"
5. Claude sees the prompt WITH the skill suggestion

Installation:
Add to your hooks configuration:
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 /path/to/skill-activation-prompt.py",
        "timeout": 3000
      }
    ]
  }
}

Input: JSON via stdin with { "prompt": "user message", "activeFiles": [...] }
Output: JSON with { "output_message": "..." } for skill suggestions
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


# Configuration
MAX_SUGGESTIONS = 3  # Maximum number of skills to suggest
MIN_SCORE_THRESHOLD = 2  # Minimum score needed to suggest a skill
KEYWORD_SCORE = 2  # Score for keyword match
INTENT_PATTERN_SCORE = 3  # Score for intent pattern match
FILE_PATTERN_SCORE = 2  # Score for file pattern match

# Script directory for loading rules
SCRIPT_DIR = Path(__file__).parent
RULES_FILE = SCRIPT_DIR / "skill-rules.json"

# Cache for rules
_rules_cache: Optional[dict] = None


def load_skill_rules() -> dict:
    """Load skill rules from JSON config with caching."""
    global _rules_cache
    if _rules_cache is not None:
        return _rules_cache

    try:
        with open(RULES_FILE, "r") as f:
            data = json.load(f)
            # Remove metadata keys
            _rules_cache = {k: v for k, v in data.items()
                          if k not in ("version", "description")}
            return _rules_cache
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Silent fail - don't break user experience
        return {}


def match_keywords(prompt: str, keywords: list) -> int:
    """
    Check if any keyword appears in prompt.
    Returns the number of unique keyword matches.
    """
    prompt_lower = prompt.lower()
    matches = 0
    for kw in keywords:
        # Match whole words to avoid false positives
        # e.g., "class" shouldn't match "classification"
        pattern = rf'\b{re.escape(kw.lower())}\b'
        if re.search(pattern, prompt_lower):
            matches += 1
    return matches


def match_intent_patterns(prompt: str, patterns: list) -> bool:
    """Check if any intent pattern matches prompt."""
    prompt_lower = prompt.lower()
    for pattern in patterns:
        try:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return True
        except re.error:
            # Skip invalid regex patterns
            continue
    return False


def match_file_pattern(active_files: list, path_pattern: str) -> bool:
    """Check if any active file matches the path pattern."""
    if not active_files or not path_pattern:
        return False

    # Handle pipe-separated patterns like "**/*.cls|**/*.trigger"
    patterns = path_pattern.split("|")

    for pattern in patterns:
        # Convert glob-style to regex
        # ** matches any path including slashes
        # * matches any characters except slashes
        regex = pattern.strip()
        regex = regex.replace("**", "<<<DOUBLESTAR>>>")
        regex = regex.replace("*", "[^/]*")
        regex = regex.replace("<<<DOUBLESTAR>>>", ".*")
        regex = regex.replace(".", r"\.")

        try:
            for f in active_files:
                if re.search(regex, f):
                    return True
        except re.error:
            continue

    return False


def find_matching_skills(prompt: str, active_files: list, rules: dict) -> list:
    """
    Find all skills that match the prompt or active files.
    Returns list of matches sorted by score.
    """
    matches = []

    for skill_name, config in rules.items():
        score = 0
        match_reasons = []

        # Keyword matching (multiple matches add to score)
        keywords = config.get("keywords", [])
        keyword_matches = match_keywords(prompt, keywords)
        if keyword_matches > 0:
            score += KEYWORD_SCORE * min(keyword_matches, 3)  # Cap at 3x
            match_reasons.append(f"{keyword_matches} keyword(s)")

        # Intent pattern matching (adds to score)
        intent_patterns = config.get("intentPatterns", [])
        if match_intent_patterns(prompt, intent_patterns):
            score += INTENT_PATTERN_SCORE
            match_reasons.append("intent match")

        # File pattern matching (adds to score)
        trigger = config.get("trigger", {})
        path_pattern = trigger.get("pathPattern", "")
        if path_pattern and active_files:
            if match_file_pattern(active_files, path_pattern):
                score += FILE_PATTERN_SCORE
                match_reasons.append("file match")

        # Only include if score meets threshold
        if score >= MIN_SCORE_THRESHOLD:
            matches.append({
                "skill": skill_name,
                "score": score,
                "priority": config.get("priority", "medium"),
                "description": config.get("description", ""),
                "reasons": match_reasons
            })

    # Sort by score (descending), then by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    matches.sort(key=lambda x: (
        -x["score"],
        priority_order.get(x["priority"], 1)
    ))

    return matches[:MAX_SUGGESTIONS]


def format_suggestions(matches: list) -> str:
    """Format skill suggestions as a user-friendly message."""
    if not matches:
        return ""

    lines = ["💡 **Relevant Skills Detected**"]
    lines.append("Based on your request, consider using:")
    lines.append("")

    for m in matches:
        skill = m["skill"]
        score = m["score"]
        description = m["description"]

        # Use icons based on priority
        icon = "⭐" if m["priority"] == "high" else "▸"

        lines.append(f"{icon} **/{skill}** (relevance: {score})")
        if description:
            lines.append(f"   {description}")

    lines.append("")
    lines.append("_Invoke with `/skill-name` or ask me to use it._")

    return "\n".join(lines)


def main():
    """Main entry point for the UserPromptSubmit hook."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # No input or invalid JSON - exit silently
        sys.exit(0)

    # Extract prompt and active files
    prompt = input_data.get("prompt", "")
    active_files = input_data.get("activeFiles", [])

    # Skip if prompt is too short
    if len(prompt.strip()) < 5:
        sys.exit(0)

    # Skip if this looks like a slash command already
    if prompt.strip().startswith("/"):
        sys.exit(0)

    # Load skill rules
    rules = load_skill_rules()
    if not rules:
        sys.exit(0)

    # Find matching skills
    matches = find_matching_skills(prompt, active_files, rules)

    if not matches:
        # No suggestions - exit silently
        sys.exit(0)

    # Format and output suggestions
    message = format_suggestions(matches)

    output = {
        "output_message": message
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
