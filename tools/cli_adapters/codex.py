"""
OpenAI Codex CLI adapter for sf-skills.

Codex CLI follows the Agent Skills standard:
- Skills location: .codex/skills/{name}/
- Uses spec directories: assets/, references/, scripts/

Codex CLI has built-in skill creator and installer support.
"""

from pathlib import Path
import re
from typing import Optional

from .base import CLIAdapter, SkillOutput


class CodexAdapter(CLIAdapter):
    """
    Adapter for OpenAI Codex CLI.

    Codex follows the Agent Skills standard with spec directories
    (assets/, references/, scripts/) — same as our source layout.
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

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md for Codex CLI compatibility.

        Changes:
        - Remove Claude Code-specific syntax
        - Replace Claude references and hook sections in body
        - Add Codex-specific usage section
        """
        # Apply common transformations
        content = self._common_skill_md_transforms(content)

        # Replace Claude Code references in body
        content = self._replace_claude_references(content)

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

Follows the Agent Skills spec:
- `assets/` - Code templates and static resources
- `references/` - Documentation and guides
- `scripts/` - Validation scripts

See `scripts/README.md` for validation script usage.
"""

        # Only add if not already present
        if "## Codex CLI Usage" not in content:
            content += codex_section

        return content

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
        output.assets = self._transform_text_files(output.assets)
        output.references = self._transform_text_files(output.references)

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
