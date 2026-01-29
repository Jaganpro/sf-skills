#!/usr/bin/env python3
"""
UserPromptSubmit hook for sf-skills auto-activation (v3.0)

This hook analyzes user prompts BEFORE Claude sees them and suggests
relevant skills based on keyword and intent pattern matching.

Enhanced features:
- Reads from unified skills-registry.json
- Detects orchestration chains from prompt
- Shows confidence levels (REQUIRED/RECOMMENDED/OPTIONAL)
- Chain-aware suggestions

How it works:
1. User submits prompt: "I need to create an apex trigger for Account"
2. This hook fires (UserPromptSubmit event)
3. Matches "apex" + "trigger" keywords → sf-apex skill (score: 5)
4. Returns suggestion: "⭐ STRONGLY RECOMMEND: /sf-apex"
5. Claude sees the prompt WITH the skill suggestion

Installation:
Add to .claude/hooks.json in project root:
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 ./shared/hooks/skill-activation-prompt.py",
        "timeout": 5000
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

# Operations that should run in background due to long execution time
SLOW_OPERATIONS = {
    "sf-testing",      # sf apex run test (2-15 min)
    "sf-deploy",       # sf project deploy (1-10 min) - only when not dry-run
}

# Script directory for loading registry
SCRIPT_DIR = Path(__file__).parent
REGISTRY_FILE = SCRIPT_DIR / "skills-registry.json"

# FIX 3: State file for tracking active skill
ACTIVE_SKILL_FILE = Path("/tmp/sf-skills-active-skill.json")

# Cache for registry
_registry_cache: Optional[dict] = None


def save_active_skill(skill_name: str):
    """Save the currently active skill to state file (FIX 3)."""
    try:
        from datetime import datetime
        state = {
            "active_skill": skill_name,
            "timestamp": datetime.now().isoformat()
        }
        with open(ACTIVE_SKILL_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError:
        pass  # Silently fail - state tracking is optional


def detect_skill_invocation(prompt: str, registry: dict) -> Optional[str]:
    """Detect if the prompt is a direct skill invocation (/skill-name)."""
    prompt = prompt.strip()

    # Match /skill-name pattern
    match = re.match(r'^/([a-z][a-z0-9-]*)', prompt, re.IGNORECASE)
    if match:
        skill_name = match.group(1).lower()

        # Check if it's a valid skill in our registry
        skills = registry.get("skills", {})
        if skill_name in skills:
            return skill_name

        # Also check for sf- prefix variants
        if skill_name.startswith("sf-") and skill_name in skills:
            return skill_name

    return None


def load_registry() -> dict:
    """Load skills registry from JSON config with caching."""
    global _registry_cache
    if _registry_cache is not None:
        return _registry_cache

    try:
        with open(REGISTRY_FILE, "r") as f:
            _registry_cache = json.load(f)
            return _registry_cache
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Silent fail - don't break user experience
        return {"skills": {}, "chains": {}}


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


def match_file_pattern(active_files: list, file_patterns: list) -> bool:
    """Check if any active file matches the file patterns."""
    if not active_files or not file_patterns:
        return False

    for pattern in file_patterns:
        try:
            for f in active_files:
                if re.search(pattern, f, re.IGNORECASE):
                    return True
        except re.error:
            continue

    return False


def detect_chain(prompt: str, registry: dict) -> Optional[dict]:
    """Detect if the prompt matches an orchestration chain."""
    prompt_lower = prompt.lower()
    chains = registry.get("chains", {})

    for chain_name, chain_config in chains.items():
        trigger_phrases = chain_config.get("trigger_phrases", [])
        for phrase in trigger_phrases:
            if phrase.lower() in prompt_lower:
                return {
                    "name": chain_name,
                    "description": chain_config.get("description", ""),
                    "order": chain_config.get("order", []),
                    "first_skill": chain_config.get("order", [""])[0]
                }

    return None


def generate_task_directive(chain: dict, registry: dict) -> str:
    """
    Generate a TASK_ORCHESTRATION directive for Claude to execute.

    This function creates a structured instruction block that tells Claude
    to automatically create tasks with dependencies based on the detected chain.
    """
    chain_name = chain["name"]
    chain_order = chain["order"]
    skills_config = registry.get("skills", {})
    background_ops = registry.get("background_operations", {})

    # Build tasks with dependencies from orchestration rules
    tasks = []
    for i, skill in enumerate(chain_order):
        skill_config = skills_config.get(skill, {})
        orchestration = skill_config.get("orchestration", {})
        prerequisites = [p["skill"] for p in orchestration.get("prerequisites", [])]

        # Map prerequisite skills to task indices (only those earlier in chain)
        blocked_by = []
        for p in prerequisites:
            if p in chain_order[:i]:
                blocked_by.append(f"task-{chain_order.index(p) + 1}")

        # If no explicit prerequisites but not first, block on previous task
        if not blocked_by and i > 0:
            blocked_by.append(f"task-{i}")

        # Detect slow operations for background execution
        is_background = skill in SLOW_OPERATIONS
        # Also check background_operations config from registry
        if skill in background_ops:
            bg_config = background_ops[skill]
            if bg_config.get("always_background", False):
                is_background = True

        tasks.append({
            "id": f"task-{i + 1}",
            "skill": skill,
            "blocked_by": blocked_by,
            "background": is_background,
            "description": skill_config.get("description", "")[:60]
        })

    return format_task_directive(chain_name, chain.get("description", ""), tasks)


def format_task_directive(chain_name: str, chain_description: str, tasks: list) -> str:
    """Format the task directive as a Claude-interpretable instruction block."""
    lines = [
        "",
        "╔══════════════════════════════════════════════════════╗",
        "║  🎯 TASK_ORCHESTRATION DIRECTIVE                     ║",
        "╠══════════════════════════════════════════════════════╣",
        f"║  Chain: {chain_name:<44}║",
        "║  Action: AUTO-CREATE tasks with dependencies         ║",
        "╚══════════════════════════════════════════════════════╝",
        "",
        f"📋 {chain_description}",
        "",
        "Claude: Execute the following automatically:",
        ""
    ]

    for task in tasks:
        blocked = ""
        if task['blocked_by']:
            blocked = f", blockedBy: {task['blocked_by']}"
        bg_marker = " (BACKGROUND)" if task['background'] else ""
        desc_truncated = task['description'][:50] if task['description'] else "Execute skill"
        lines.append(f"  TaskCreate(\"{task['skill']}: {desc_truncated}\"{blocked}){bg_marker}")

    lines.extend([
        "",
        "┌──────────────────────────────────────────────────────┐",
        "│ ⚡ EXECUTION RULES:                                  │",
        "│ • Create ALL tasks above with TaskCreate             │",
        "│ • Set blockedBy relationships as specified           │",
        "│ • For (BACKGROUND) tasks, use run_in_background=true │",
        "│ • Invoke first skill (/{}) automatically       │".format(tasks[0]['skill'] if tasks else "skill"),
        "└──────────────────────────────────────────────────────┘",
    ])

    return "\n".join(lines)


def detect_diagram_intent(prompt: str) -> dict:
    """
    Detect diagram intent and determine routing.

    This function analyzes user prompts to identify diagram-related requests
    and determines whether to auto-invoke a specific diagram skill or ask
    for clarification when the intent is ambiguous.

    Returns: {
        "type": "mermaid" | "visual" | "ambiguous" | None,
        "confidence": "high" | "medium" | None,
        "auto_invoke": skill_name or None
    }
    """
    prompt_lower = prompt.lower()

    # High-confidence Mermaid indicators (specific to Mermaid syntax/output)
    mermaid_keywords = [
        "mermaid",
        "flowchart",
        "sequence diagram",
        "erd diagram",
        "erdiagram",
        "class diagram",
        "gantt",
        "pie chart",
        "statediagram",
        "state diagram",
        "flowchart tb",
        "flowchart lr",
        "hook lifecycle",
        "architecture diagram",
    ]

    # High-confidence visual/image indicators (explicit image output)
    visual_keywords = [
        "image",
        "png",
        "svg",
        "mockup",
        "wireframe",
        "visual erd",
        "screenshot",
        "nano banana",
        "nanobananapro",
        "visual image",
        "generate image",
    ]

    # Check for keyword matches
    has_mermaid = any(kw in prompt_lower for kw in mermaid_keywords)
    has_visual = any(kw in prompt_lower for kw in visual_keywords)
    has_diagram = "diagram" in prompt_lower or "erd" in prompt_lower

    # Decision logic
    if has_mermaid and not has_visual:
        # Clear Mermaid intent - auto-invoke
        return {
            "type": "mermaid",
            "confidence": "high",
            "auto_invoke": "sf-diagram-mermaid"
        }
    elif has_visual and not has_mermaid:
        # Clear visual/image intent - auto-invoke
        return {
            "type": "visual",
            "confidence": "high",
            "auto_invoke": "sf-diagram-nanobananapro"
        }
    elif has_diagram:
        # Ambiguous diagram request - need clarification
        return {
            "type": "ambiguous",
            "confidence": "medium",
            "auto_invoke": None
        }

    # No diagram intent detected
    return {
        "type": None,
        "confidence": None,
        "auto_invoke": None
    }


def find_matching_skills(prompt: str, active_files: list, registry: dict) -> list:
    """
    Find all skills that match the prompt or active files.
    Returns list of matches sorted by score.
    """
    matches = []
    skills = registry.get("skills", {})

    for skill_name, config in skills.items():
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
        file_patterns = config.get("filePatterns", [])
        if file_patterns and active_files:
            if match_file_pattern(active_files, file_patterns):
                score += FILE_PATTERN_SCORE
                match_reasons.append("file match")

        # Only include if score meets threshold
        if score >= MIN_SCORE_THRESHOLD:
            # Determine confidence based on score
            if score >= 7:
                confidence = 3  # REQUIRED
            elif score >= 4:
                confidence = 2  # RECOMMENDED
            else:
                confidence = 1  # OPTIONAL

            matches.append({
                "skill": skill_name,
                "score": score,
                "confidence": confidence,
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


def format_suggestions(matches: list, chain: Optional[dict], registry: dict,
                       include_task_directive: bool = False) -> str:
    """Format skill suggestions as a user-friendly message."""
    if not matches and not chain:
        return ""

    confidence_levels = registry.get("confidence_levels", {
        "3": {"icon": "***", "label": "REQUIRED"},
        "2": {"icon": "**", "label": "RECOMMENDED"},
        "1": {"icon": "*", "label": "OPTIONAL"}
    })

    lines = [f"{'═' * 54}"]
    lines.append("💡 SKILL SUGGESTIONS (based on your request)")
    lines.append(f"{'═' * 54}")

    # Show chain detection if found
    if chain:
        lines.append("")
        lines.append(f"📋 DETECTED WORKFLOW: {chain['name']}")
        lines.append(f"   {chain['description']}")
        order_str = " → ".join(chain['order'][:5])
        if len(chain['order']) > 5:
            order_str += " → ..."
        lines.append(f"   Order: {order_str}")
        lines.append(f"   ⭐ START WITH: /{chain['first_skill']}")
        lines.append("")

    # Show individual skill suggestions
    for m in matches:
        skill = m["skill"]
        description = m["description"]
        conf = m.get("confidence", 2)
        conf_info = confidence_levels.get(str(conf), {"icon": "**", "label": "RECOMMENDED"})

        # Icon based on confidence
        if conf == 3:
            icon = "⭐⭐⭐"
        elif conf == 2:
            icon = "⭐⭐"
        else:
            icon = "⭐"

        lines.append(f"{icon} /{skill} - {conf_info['label']}")
        if description:
            lines.append(f"   └─ {description}")

    lines.append(f"{'─' * 54}")
    lines.append("💡 Invoke with /skill-name or ask Claude to use it")
    lines.append(f"{'═' * 54}")

    # If chain detected, append the task orchestration directive
    if chain and include_task_directive:
        task_directive = generate_task_directive(chain, registry)
        lines.append(task_directive)

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

    # Load skills registry
    registry = load_registry()
    if not registry.get("skills"):
        sys.exit(0)

    # DIAGRAM AUTO-INVOCATION: Check for diagram intent first (before skill suggestions)
    diagram_intent = detect_diagram_intent(prompt)

    if diagram_intent["auto_invoke"]:
        # High-confidence match - auto-invoke the skill
        skill = diagram_intent["auto_invoke"]
        save_active_skill(skill)
        output = {
            "output_message": (
                f"{'═' * 54}\n"
                f"🎯 AUTO-INVOKING /{skill}\n"
                f"{'═' * 54}\n\n"
                f"Detected {diagram_intent['type']} diagram request.\n"
                f"Skill activated - proceeding with diagram generation.\n\n"
                f"💡 The /{skill} skill is now active with its validation\n"
                f"   hooks and best practices enabled.\n"
                f"{'═' * 54}"
            )
        }
        print(json.dumps(output))
        sys.exit(0)

    if diagram_intent["type"] == "ambiguous":
        # Ambiguous diagram request - ask clarification
        output = {
            "output_message": (
                f"{'═' * 54}\n"
                "🎨 DIAGRAM TYPE CLARIFICATION NEEDED\n"
                f"{'═' * 54}\n\n"
                "I detected a diagram request. Which format do you prefer?\n\n"
                "1️⃣  **Mermaid** (text-based, version-controllable)\n"
                "    → /sf-diagram-mermaid\n"
                "    Best for: ERDs, flowcharts, sequence diagrams, architecture\n\n"
                "2️⃣  **Visual Image** (PNG/SVG via Nano Banana Pro)\n"
                "    → /sf-diagram-nanobananapro\n"
                "    Best for: Mockups, wireframes, visual ERDs, presentations\n\n"
                "💡 Tip: Include 'mermaid' or 'image/png/svg' in your request\n"
                "   for automatic skill selection, or invoke directly with\n"
                "   /sf-diagram-mermaid or /sf-diagram-nanobananapro\n"
                f"{'═' * 54}"
            )
        }
        print(json.dumps(output))
        sys.exit(0)

    # FIX 3: Track skill invocation if this is a slash command
    if prompt.strip().startswith("/"):
        invoked_skill = detect_skill_invocation(prompt, registry)
        if invoked_skill:
            save_active_skill(invoked_skill)
        # Exit - don't suggest skills when user already invoked one
        sys.exit(0)

    # Detect if prompt matches a workflow chain
    chain = detect_chain(prompt, registry)

    # Find matching skills
    matches = find_matching_skills(prompt, active_files, registry)

    # If we detected a chain, ensure first skill is in suggestions
    if chain and chain["first_skill"]:
        first_skill = chain["first_skill"]
        if first_skill not in [m["skill"] for m in matches]:
            # Add the chain's first skill with high confidence
            skill_config = registry.get("skills", {}).get(first_skill, {})
            matches.insert(0, {
                "skill": first_skill,
                "score": 10,
                "confidence": 3,
                "priority": "high",
                "description": skill_config.get("description", ""),
                "reasons": ["chain first step"]
            })
            matches = matches[:MAX_SUGGESTIONS]

    if not matches and not chain:
        # No suggestions - exit silently
        sys.exit(0)

    # Format and output suggestions
    # Include task directive when a chain is detected for automatic orchestration
    message = format_suggestions(matches, chain, registry, include_task_directive=bool(chain))

    output = {
        "output_message": message
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
