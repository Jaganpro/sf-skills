"""
OpenAI Codex CLI adapter for sf-skills.

Codex CLI follows the Agent Skills standard with some naming conventions:
- Skills location: .codex/skills/{name}/
- templates/ → assets/ (Codex convention)
- docs/ → references/ (Codex convention)

Codex CLI has built-in skill creator and installer support.
"""

from pathlib import Path
import re
from typing import Optional

from .base import CLIAdapter, SkillOutput


class CodexAdapter(CLIAdapter):
    """
    Adapter for OpenAI Codex CLI.

    Codex follows Agent Skills standard but uses different directory names:
    - assets/ instead of templates/
    - references/ instead of docs/
    """

    @property
    def cli_name(self) -> str:
        return "codex"

    @property
    def default_install_path(self) -> Path:
        """
        Default to project-level .codex/skills/ directory.

        Codex CLI checks:
        1. .codex/skills/{name}/ (repository scope)
        2. ~/.codex/skills/{name}/ (user scope)
        3. Built-in skills (lowest precedence)
        """
        cwd = Path.cwd()
        return cwd / ".codex" / "skills"

    @property
    def templates_dir_name(self) -> str:
        """Codex uses 'assets' instead of 'templates'."""
        return "assets"

    @property
    def docs_dir_name(self) -> str:
        """Codex uses 'references' instead of 'docs'."""
        return "references"

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md for Codex CLI compatibility.

        Changes:
        - Remove Claude Code-specific syntax
        - Update directory references (templates → assets, docs → references)
        - Remove Claude-specific hooks from frontmatter
        - Replace Claude references and hook sections in body
        - Add Codex-specific usage section
        """
        # Apply common transformations
        content = self._common_skill_md_transforms(content)

        # Remove Claude hook configuration from frontmatter if present
        content = self._strip_hooks_from_frontmatter(content)

        # Replace Claude Code references in body
        content = self._replace_claude_references(content)

        # Update directory references
        content = content.replace("templates/", "assets/")
        content = content.replace("docs/", "references/")
        content = content.replace("`templates`", "`assets`")
        content = content.replace("`docs`", "`references`")

        # Normalize slash invocation to Codex @skill syntax
        content = re.sub(r'/(sf-[\w-]+)\b', r'@\1', content)
        # Normalize Skill(...) shorthand in prose
        content = re.sub(r'Skill\(\s*([a-zA-Z0-9_-]+)\s*\)\s*:?', r'@\1', content)

        # Add Codex-specific section
        codex_section = f"""

---

## Codex CLI Usage

This skill is compatible with OpenAI Codex CLI. To use:

```bash
# Enable skills in Codex
codex --enable skills

# The skill is automatically loaded from .codex/skills/{skill_name}/

# To run validation scripts manually:
cd .codex/skills/{skill_name}/scripts
python validate_*.py path/to/your/file
```

### Directory Structure

Codex CLI uses slightly different directory names:
- `assets/` - Code templates (called `templates/` in Claude Code)
- `references/` - Documentation (called `docs/` in Claude Code)
- `scripts/` - Validation scripts

See `scripts/README.md` for validation script usage.
"""

        # Only add if not already present
        if "## Codex CLI Usage" not in content:
            content += codex_section

        return content

    def _strip_hooks_from_frontmatter(self, content: str) -> str:
        """
        Remove Claude Code hooks from YAML frontmatter for Codex.

        Keeps the rest of the frontmatter intact.
        """
        if not content.startswith("---"):
            return content

        # Match frontmatter block
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            return content

        frontmatter = match.group(1)
        body = content[match.end():]

        # Remove hooks block at top-level, preserving other keys
        lines = frontmatter.splitlines()
        cleaned = []
        skipping = False
        for line in lines:
            if not skipping and re.match(r'^hooks:\s*$', line):
                skipping = True
                continue
            if skipping:
                # Stop skipping when we hit a new top-level key
                if line and not line.startswith((" ", "\t")):
                    skipping = False
                else:
                    continue
            if not skipping:
                cleaned.append(line)

        frontmatter = "\n".join(cleaned)

        # Clean up extra blank lines
        frontmatter = re.sub(r'\n{3,}', '\n\n', frontmatter).strip()

        return f"---\n{frontmatter}\n---\n{body}"

    def _replace_claude_references(self, content: str) -> str:
        """
        Replace Claude Code references and remove hook-specific sections.
        """
        # Remove hook-related sections in body (headings containing Hook/Hooks)
        content = re.sub(
            r'\n#{2,}\s*[^#\n]*(Hook|Hooks)[^\n]*\n(?:.*\n)*?(?=\n#{2,}\s|\Z)',
            '\n',
            content,
            flags=re.IGNORECASE
        )

        # Replace tool/platform mentions
        replacements = [
            (r'\bClaude Code\b', 'Codex CLI'),
            (r'\bClaude\b', 'Codex'),
            (r'\.claude/skills/', '.codex/skills/'),
            (r'~/.claude/skills/', '~/.codex/skills/'),
            (r'\.claude/', '.codex/'),
            (r'~/.claude/', '~/.codex/'),
        ]
        for pattern, repl in replacements:
            content = re.sub(pattern, repl, content)

        return content

    def _transform_text_files(self, files: dict) -> dict:
        """
        Apply Codex text transforms to any text file content in a dict.
        """
        transformed = {}
        for path, content in files.items():
            if not isinstance(content, str):
                transformed[path] = content
                continue

            text = content
            text = self._common_skill_md_transforms(text)
            text = self._replace_claude_references(text)
            text = text.replace("templates/", "assets/")
            text = text.replace("docs/", "references/")
            text = text.replace("`templates`", "`assets`")
            text = text.replace("`docs`", "`references`")
            text = re.sub(r'/(sf-[\w-]+)\b', r'@\1', text)
            # Replace Skill(...) invocations in examples/scripts (handles escaped quotes)
            text = re.sub(
                r'Skill\(\s*skill=\\?"([^"]+)"(?:,\s*args=\\?"([^"]*)")?\s*\)',
                r'@\1 \2',
                text
            )
            text = re.sub(r'Skill\(\s*([a-zA-Z0-9_-]+)\s*\)', r'@\1', text)

            transformed[path] = text

        return transformed

    def transform_skill(self, source_dir: Path) -> SkillOutput:
        """
        Transform skill for Codex CLI.

        Same as base implementation but bundling shared modules.
        """
        # Get base transformation
        output = super().transform_skill(source_dir)

        # Apply Codex transforms to bundled text files
        output.scripts = self._transform_text_files(output.scripts)
        output.templates = self._transform_text_files(output.templates)
        output.docs = self._transform_text_files(output.docs)
        output.examples = self._transform_text_files(output.examples)

        # Bundle shared modules if scripts reference them
        if self._needs_shared_modules(output.scripts):
            shared_modules = self._bundle_shared_modules()
            for path, content in shared_modules.items():
                output.scripts[f"shared/{path}"] = content

        return output

    def _needs_shared_modules(self, scripts: dict) -> bool:
        """Check if any scripts import from shared/ modules."""
        for content in scripts.values():
            if isinstance(content, str):
                if "from shared" in content or "import shared" in content:
                    return True
                if "lsp_client" in content or "code_analyzer" in content:
                    return True
        return False

    def _bundle_shared_modules(self) -> dict:
        """Bundle shared modules for self-contained installation."""
        modules = {}

        extra_exts = {".json", ".yml", ".yaml", ".txt", ".md", ".cfg", ".ini", ".xml"}

        # Bundle lsp-engine
        lsp_dir = self.shared_dir / "lsp-engine"
        if lsp_dir.exists():
            for file_path in lsp_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_path.suffix not in {".py", *extra_exts}:
                    continue
                rel_path = file_path.relative_to(self.shared_dir)
                content = file_path.read_text(encoding='utf-8')
                modules[str(rel_path)] = content

        # Bundle code_analyzer
        analyzer_dir = self.shared_dir / "code_analyzer"
        if analyzer_dir.exists():
            for file_path in analyzer_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_path.suffix not in {".py", *extra_exts}:
                    continue
                rel_path = file_path.relative_to(self.shared_dir)
                modules[str(rel_path)] = file_path.read_text(encoding='utf-8')

        return modules
