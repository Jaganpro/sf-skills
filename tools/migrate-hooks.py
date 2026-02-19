#!/usr/bin/env python3
"""
Part A: Migrate claude-code-hooks from SKILL.md frontmatter → .claude/hooks.yaml

For each skill with `metadata.claude-code-hooks` in SKILL.md:
1. Parse frontmatter YAML
2. Extract the claude-code-hooks block
3. Write to <skill-dir>/.claude/hooks.yaml with header comment
4. Remove claude-code-hooks from metadata in SKILL.md
5. Write back the cleaned SKILL.md (preserving body exactly)

Usage: python3 tools/migrate-hooks.py [--dry-run]
"""

import re
import sys
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# All 20 skill dirs with claude-code-hooks
SKILL_DIRS = [
    "sf-ai-agentforce",
    "sf-ai-agentforce-conversationdesign",
    "sf-ai-agentforce-observability",
    "sf-ai-agentforce-testing",
    "sf-ai-agentscript",
    "sf-apex",
    "sf-connected-apps",
    "sf-data",
    "sf-debug",
    "sf-deploy",
    "sf-diagram-mermaid",
    "sf-diagram-nanobananapro",
    "sf-flow",
    "sf-integration",
    "sf-lwc",
    "sf-metadata",
    "sf-permissions",
    "sf-soql",
    "sf-testing",
]


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """
    Split SKILL.md into (raw_frontmatter, frontmatter_yaml_str, body).
    Returns the raw frontmatter text (between ---), and the body after closing ---.
    """
    content = skill_path.read_text(encoding="utf-8")
    # Match frontmatter block: --- ... ---
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        raise ValueError(f"No frontmatter found in {skill_path}")
    return match.group(0), match.group(1), match.group(2)


def extract_hooks_from_frontmatter(frontmatter_str: str) -> tuple[dict | None, str]:
    """
    Parse frontmatter YAML, extract claude-code-hooks from metadata,
    and return (hooks_dict, cleaned_frontmatter_str).

    Uses line-based removal to preserve YAML formatting exactly.
    """
    data = yaml.safe_load(frontmatter_str)
    if not data or "metadata" not in data:
        return None, frontmatter_str

    metadata = data.get("metadata", {})
    hooks = metadata.get("claude-code-hooks")
    if not hooks:
        return None, frontmatter_str

    # Line-based removal to preserve formatting
    lines = frontmatter_str.splitlines()
    cleaned_lines = []
    skipping = False
    hooks_indent = None

    for line in lines:
        stripped = line.lstrip()

        if not skipping:
            # Detect the claude-code-hooks key
            if stripped.startswith("claude-code-hooks:"):
                skipping = True
                hooks_indent = len(line) - len(stripped)
                continue
            cleaned_lines.append(line)
        else:
            # We're inside the hooks block - skip until we find a line
            # at the same or lesser indent level (that's not blank)
            if stripped == "":
                # Skip blank lines within the hooks block
                continue
            current_indent = len(line) - len(stripped)
            if current_indent <= hooks_indent:
                # We've exited the hooks block
                skipping = False
                cleaned_lines.append(line)
            # else: still inside hooks block, skip

    # Remove trailing blank lines from metadata section
    cleaned_str = "\n".join(cleaned_lines)
    # Clean up any double blank lines that might result
    cleaned_str = re.sub(r"\n{3,}", "\n\n", cleaned_str)
    # Ensure no trailing whitespace on the frontmatter
    cleaned_str = cleaned_str.rstrip()

    return hooks, cleaned_str


def generate_hooks_yaml(hooks: dict, skill_name: str) -> str:
    """Generate the .claude/hooks.yaml content with header comment."""
    header = f"""# Claude Code lifecycle hooks for {skill_name}
# These hooks are registered by the installer (tools/install.py)
# and are NOT part of the Agent Skills open specification.
"""

    # Custom YAML dumper to get clean output
    class CleanDumper(yaml.SafeDumper):
        pass

    # Represent strings without unnecessary quoting unless they contain special chars
    def str_representer(dumper, data):
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        # Use quotes for strings with special yaml chars
        if any(c in data for c in [":", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`"]):
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    CleanDumper.add_representer(str, str_representer)

    yaml_content = yaml.dump(
        hooks,
        Dumper=CleanDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    return header + "\n" + yaml_content


def migrate_skill(skill_dir_name: str, dry_run: bool = False) -> bool:
    """Migrate hooks for a single skill. Returns True if migration was performed."""
    skill_dir = PROJECT_ROOT / skill_dir_name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        print(f"  SKIP: {skill_md} does not exist")
        return False

    try:
        full_fm, frontmatter_str, body = parse_skill_md(skill_md)
    except ValueError as e:
        print(f"  ERROR: {e}")
        return False

    hooks, cleaned_frontmatter = extract_hooks_from_frontmatter(frontmatter_str)

    if not hooks:
        print(f"  SKIP: No claude-code-hooks found in {skill_dir_name}")
        return False

    # Generate hooks.yaml content
    hooks_yaml = generate_hooks_yaml(hooks, skill_dir_name)

    # Generate cleaned SKILL.md
    cleaned_skill_md = f"---\n{cleaned_frontmatter}\n---\n{body}"

    if dry_run:
        print(f"  DRY RUN: Would create {skill_dir_name}/.claude/hooks.yaml")
        print(f"  DRY RUN: Would clean {skill_dir_name}/SKILL.md frontmatter")
        print(f"  Hooks keys: {list(hooks.keys())}")
        return True

    # Create .claude/ directory
    claude_dir = skill_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)

    # Write hooks.yaml
    hooks_yaml_path = claude_dir / "hooks.yaml"
    hooks_yaml_path.write_text(hooks_yaml, encoding="utf-8")
    print(f"  CREATED: {skill_dir_name}/.claude/hooks.yaml")

    # Write cleaned SKILL.md
    skill_md.write_text(cleaned_skill_md, encoding="utf-8")
    print(f"  CLEANED: {skill_dir_name}/SKILL.md (removed claude-code-hooks)")

    return True


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN MODE ===\n")
    else:
        print("=== Migrating claude-code-hooks → .claude/hooks.yaml ===\n")

    success_count = 0
    skip_count = 0
    error_count = 0

    for skill_dir in SKILL_DIRS:
        print(f"\n[{skill_dir}]")
        try:
            if migrate_skill(skill_dir, dry_run):
                success_count += 1
            else:
                skip_count += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            error_count += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {success_count} migrated, {skip_count} skipped, {error_count} errors")
    print(f"Total skills processed: {len(SKILL_DIRS)}")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
