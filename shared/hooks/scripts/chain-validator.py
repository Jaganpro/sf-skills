#!/usr/bin/env python3
"""
SubagentStop Chain Validator Hook for sf-skills (v4.0)

Validates that subagents follow orchestration chains and suggests next skills.
This hook fires when a subagent completes work and validates:

1. Did the subagent follow the expected chain sequence?
2. What is the next recommended skill in the chain?
3. Are there any prerequisites that were skipped?

Output Format (SubagentStop):
{
    "hookSpecificOutput": {
        "hookEventName": "SubagentStop",
        "additionalContext": "chain progress + next step suggestion"
    }
}

Usage:
Add to SKILL.md frontmatter:
hooks:
  SubagentStop:
    - type: command
      command: "${SHARED_HOOKS}/scripts/chain-validator.py sf-apex"
      timeout: 5000
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Configuration
SCRIPT_DIR = Path(__file__).parent.parent
REGISTRY_FILE = SCRIPT_DIR / "skills-registry.json"
CONTEXT_FILE = Path("/tmp/sf-skills-context.json")
CHAIN_STATE_FILE = Path("/tmp/sf-skills-chain-state.json")

# Cache
_registry_cache: Optional[dict] = None


def load_registry() -> dict:
    """Load the unified skills registry configuration."""
    global _registry_cache
    if _registry_cache is not None:
        return _registry_cache

    try:
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, 'r') as f:
                _registry_cache = json.load(f)
                return _registry_cache
    except (json.JSONDecodeError, IOError):
        pass
    return {"skills": {}, "chains": {}, "confidence_levels": {}}


def load_chain_state() -> dict:
    """Load current chain execution state."""
    try:
        if CHAIN_STATE_FILE.exists():
            with open(CHAIN_STATE_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {
        "active_chain": None,
        "completed_skills": [],
        "started_at": None
    }


def save_chain_state(state: dict):
    """Save chain execution state."""
    try:
        with open(CHAIN_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError:
        pass


def load_context() -> dict:
    """Load previous skill context."""
    try:
        if CONTEXT_FILE.exists():
            with open(CONTEXT_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def detect_active_chain(completed_skills: List[str], registry: dict) -> Optional[dict]:
    """Detect which chain we're in based on completed skills."""
    chains = registry.get("chains", {})

    best_match = None
    best_match_count = 0

    for chain_name, chain_config in chains.items():
        order = chain_config.get("order", [])
        if not order:
            continue

        # Check how many skills in order have been completed
        match_count = 0
        for skill in completed_skills:
            if skill in order:
                match_count += 1

        # Must have at least 2 matches to consider it a chain
        if match_count >= 2 and match_count > best_match_count:
            best_match = {
                "name": chain_name,
                "description": chain_config.get("description", ""),
                "order": order,
                "match_count": match_count
            }
            best_match_count = match_count

    return best_match


def get_chain_position(skill: str, chain_order: List[str]) -> int:
    """Get the position of a skill in a chain (1-indexed)."""
    try:
        return chain_order.index(skill) + 1
    except ValueError:
        return -1


def get_next_skills(current_skill: str, chain_order: List[str], completed: List[str]) -> List[str]:
    """Get the next skills in the chain after the current one."""
    try:
        current_idx = chain_order.index(current_skill)
        next_skills = []
        for skill in chain_order[current_idx + 1:]:
            if skill not in completed:
                next_skills.append(skill)
            if len(next_skills) >= 2:
                break
        return next_skills
    except ValueError:
        return []


def get_skipped_skills(current_skill: str, chain_order: List[str], completed: List[str]) -> List[str]:
    """Get skills that should have been done before this one."""
    try:
        current_idx = chain_order.index(current_skill)
        skipped = []
        for skill in chain_order[:current_idx]:
            if skill not in completed:
                skipped.append(skill)
        return skipped
    except ValueError:
        return []


def format_chain_validation(
    current_skill: str,
    chain: Optional[dict],
    next_skills: List[str],
    skipped_skills: List[str],
    completed_skills: List[str],
    registry: dict
) -> str:
    """Format chain validation output."""

    confidence_levels = registry.get("confidence_levels", {
        "3": {"icon": "***", "label": "REQUIRED"},
        "2": {"icon": "**", "label": "RECOMMENDED"},
        "1": {"icon": "*", "label": "OPTIONAL"}
    })

    lines = [f"\n{'═' * 54}"]
    lines.append(f"🔗 CHAIN VALIDATION ({current_skill} completed)")
    lines.append(f"{'═' * 54}")

    if chain:
        chain_name = chain["name"]
        chain_order = chain["order"]
        current_pos = get_chain_position(current_skill, chain_order)
        total = len(chain_order)

        lines.append("")
        lines.append(f"📋 WORKFLOW: {chain_name}")
        lines.append(f"   {chain['description']}")
        lines.append(f"   Step {current_pos} of {total} complete")

        # Show progress bar
        completed_count = len([s for s in completed_skills if s in chain_order])
        progress = "█" * completed_count + "░" * (total - completed_count)
        lines.append(f"   Progress: [{progress}]")

        # Show completed steps
        completed_str = " ✓ → ".join([s for s in chain_order if s in completed_skills])
        if completed_str:
            lines.append(f"   Completed: {completed_str} ✓")

    # Warn about skipped prerequisites
    if skipped_skills:
        lines.append("")
        lines.append("⚠️  SKIPPED PREREQUISITES:")
        for skill in skipped_skills[:3]:
            skill_config = registry.get("skills", {}).get(skill, {})
            desc = skill_config.get("description", "")[:50]
            lines.append(f"   ⏭️  /{skill} - {desc}")

    # Show next steps
    if next_skills:
        lines.append("")
        lines.append("➡️  NEXT STEPS:")
        for i, skill in enumerate(next_skills):
            skill_config = registry.get("skills", {}).get(skill, {})
            orchestration = skill_config.get("orchestration", {})
            next_steps = orchestration.get("next_steps", [])

            # Get the message from orchestration if available
            message = skill_config.get("description", "")[:50]
            for step in next_steps:
                if step.get("skill") == skill:
                    message = step.get("message", message)
                    break

            # First next step is REQUIRED, others are RECOMMENDED
            conf = 3 if i == 0 else 2
            conf_info = confidence_levels.get(str(conf), {"icon": "**", "label": "RECOMMENDED"})

            lines.append(f"   {conf_info['icon']} /{skill} - {conf_info['label']}")
            lines.append(f"      └─ {message}")
    else:
        lines.append("")
        lines.append("✅ CHAIN COMPLETE! All steps finished.")

    lines.append(f"{'─' * 54}")
    lines.append("💡 Invoke next skill with /skill-name")
    lines.append(f"{'═' * 54}\n")

    return "\n".join(lines)


def main():
    """Main entry point for SubagentStop hook."""

    # Get skill name from CLI argument
    current_skill = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    # Load registry and state
    registry = load_registry()
    chain_state = load_chain_state()
    context = load_context()

    # If no skill provided, try to detect from context
    if not current_skill:
        current_skill = context.get("last_skill")

    if not current_skill:
        # Can't validate without knowing the skill
        sys.exit(0)

    # Update completed skills
    completed_skills = chain_state.get("completed_skills", [])
    if current_skill not in completed_skills:
        completed_skills.append(current_skill)

    # Detect active chain
    active_chain = detect_active_chain(completed_skills, registry)

    # Update chain state
    chain_state["completed_skills"] = completed_skills
    chain_state["active_chain"] = active_chain["name"] if active_chain else None
    chain_state["last_skill"] = current_skill
    chain_state["timestamp"] = datetime.now().isoformat()
    save_chain_state(chain_state)

    # Calculate next and skipped skills
    next_skills = []
    skipped_skills = []

    if active_chain:
        chain_order = active_chain["order"]
        next_skills = get_next_skills(current_skill, chain_order, completed_skills)
        skipped_skills = get_skipped_skills(current_skill, chain_order, completed_skills)
    else:
        # No chain detected - use orchestration from skill config
        skill_config = registry.get("skills", {}).get(current_skill, {})
        orchestration = skill_config.get("orchestration", {})
        next_steps = orchestration.get("next_steps", [])
        next_skills = [step["skill"] for step in next_steps[:2]]

    # Format output
    formatted = format_chain_validation(
        current_skill,
        active_chain,
        next_skills,
        skipped_skills,
        completed_skills,
        registry
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStop",
            "additionalContext": formatted
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
