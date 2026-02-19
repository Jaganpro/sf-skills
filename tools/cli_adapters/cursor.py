"""
Cursor CLI adapter for sf-skills.

Cursor uses its own rules system with MDC (Markdown with metadata) format:
- Rules location: .cursor/rules/{name}.mdc
- Format: YAML frontmatter + markdown content
- Different from Agent Skills standard

This adapter transforms SKILL.md into Cursor's MDC rule format.
Note: For full Agent Skills support in Cursor, use SkillPort MCP bridge.
"""

from pathlib import Path
from typing import Optional
import re

from .base import CLIAdapter, SkillOutput


class CursorAdapter(CLIAdapter):
    """
    Adapter for Cursor CLI/IDE.

    Cursor uses MDC (Markdown with metadata) format for rules.
    This adapter transforms skills into Cursor-compatible rules.

    Note: This provides basic rule conversion. For full skill
    functionality, consider using SkillPort MCP server.
    """

    @property
    def cli_name(self) -> str:
        return "cursor"

    @property
    def default_install_path(self) -> Path:
        """
        Default to project-level .cursor/rules/ directory.

        Cursor checks:
        1. .cursor/rules/ (project rules - MDC format)
        2. Settings → Rules (global rules)
        """
        cwd = Path.cwd()
        return cwd / ".cursor" / "rules"

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md into Cursor MDC rule format.

        MDC format requires:
        - YAML frontmatter with description, globs, alwaysApply
        - Markdown body with rule content
        """
        # Extract description from YAML frontmatter or content
        description = self._extract_description(content)

        # Determine file globs based on skill type
        globs = self._get_skill_globs(skill_name)

        # Apply common transformations
        content = self._common_skill_md_transforms(content)

        # Remove original YAML frontmatter (we'll add MDC frontmatter)
        content = self._strip_yaml_frontmatter(content)

        # Build MDC format
        mdc_content = f"""---
description: {description}
globs: {globs}
alwaysApply: false
---

{content}

---

## Cursor Integration Notes

This rule was converted from an Agent Skill (SKILL.md format).

### Validation Scripts

Validation scripts are available in the `scripts/` directory.
Run them manually after editing files:

```bash
cd .cursor/rules/{skill_name}/scripts
python validate_*.py path/to/your/file
```

### Full Agent Skills Support

For complete Agent Skills functionality (automatic validation,
templates, etc.), consider using the [SkillPort](https://github.com/gotalab/skillport)
MCP server which bridges Agent Skills to Cursor.

### References

- Original skill: [sf-skills/{skill_name}](https://github.com/Jaganpro/sf-skills/tree/main/{skill_name})
- Agent Skills standard: [agentskills.io](https://agentskills.io)
"""

        return mdc_content

    def _extract_description(self, content: str) -> str:
        """Extract description from YAML frontmatter or first paragraph."""
        # Try YAML frontmatter first
        yaml_match = re.search(
            r'^---\s*\n(.*?)\n---',
            content,
            re.DOTALL
        )
        if yaml_match:
            frontmatter = yaml_match.group(1)
            desc_match = re.search(
                r'description:\s*[>|]?\s*\n?\s*(.+?)(?:\n\w|\n---|\n\n)',
                frontmatter,
                re.DOTALL
            )
            if desc_match:
                desc = desc_match.group(1).strip()
                # Clean up multiline descriptions
                desc = ' '.join(desc.split())
                return desc[:200]  # Limit length

        # Fall back to first heading or paragraph
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()[:200]

        return "Salesforce development skill"

    def _get_skill_globs(self, skill_name: str) -> str:
        """Determine appropriate file globs based on skill type."""
        glob_mapping = {
            'sf-apex': '["**/*.cls", "**/*.trigger"]',
            'sf-flow': '["**/*.flow-meta.xml"]',
            'sf-lwc': '["**/lwc/**/*.js", "**/lwc/**/*.html", "**/lwc/**/*.css"]',
            'sf-metadata': '["**/*-meta.xml"]',
            'sf-data': '["**/*.soql", "**/*.apex"]',
            'sf-ai-agentforce': '["**/*.genAiFunction-meta.xml", "**/*.genAiPlugin-meta.xml", "**/*.promptTemplate-meta.xml", "**/*.lightningTypeBundle-meta.xml"]',
            'sf-connected-apps': '["**/*.connectedApp-meta.xml"]',
            'sf-integration': '["**/*.namedCredential-meta.xml", "**/*.externalService-meta.xml"]',
            'sf-deploy': '["**/sfdx-project.json", "**/package.xml"]',
            'sf-diagram-mermaid': '["**/*.md"]',
            'sf-diagram-nanobananapro': '["**/*.png", "**/*.jpg"]',
            'sf-soql': '["**/*.soql"]',
            'sf-testing': '["**/*Test.cls"]',
            'sf-debug': '["**/*.log"]',
        }
        return glob_mapping.get(skill_name, '["**/*"]')

    def _strip_yaml_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content."""
        return re.sub(
            r'^---\s*\n.*?\n---\s*\n',
            '',
            content,
            flags=re.DOTALL
        )

    def transform_skill(self, source_dir: Path) -> SkillOutput:
        """
        Transform skill for Cursor.

        Creates MDC rule file and bundles supporting files.
        """
        skill_name = source_dir.name

        # Get base transformation
        output = super().transform_skill(source_dir)

        # Rename SKILL.md to {skill_name}.mdc for Cursor
        # The main rule file should be named after the skill
        output.cli_specific[f"{skill_name}.mdc"] = output.skill_md

        # Bundle shared modules if scripts reference them
        if self._needs_shared_modules(output.scripts):
            shared_modules = self._bundle_shared_modules()
            for path, content in shared_modules.items():
                output.scripts[f"shared/{path}"] = content

        return output

    def write_output(self, output: SkillOutput, target_dir: Path) -> None:
        """
        Write transformed skill output to target directory.

        For Cursor, we write the MDC file directly to .cursor/rules/
        and supporting files to a subdirectory.
        """
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)

        # Write the MDC rule file (main skill definition)
        for rel_path, content in output.cli_specific.items():
            if rel_path.endswith('.mdc'):
                (target_dir / rel_path).write_text(content, encoding='utf-8')

        # Write supporting files to skill subdirectory
        skill_subdir = target_dir / target_dir.name.replace('.mdc', '')

        # Write scripts
        if output.scripts:
            scripts_dir = skill_subdir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            for rel_path, content in output.scripts.items():
                file_path = scripts_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')

        # Write assets
        if output.assets:
            assets_dir = skill_subdir / self.assets_dir_name
            assets_dir.mkdir(parents=True, exist_ok=True)
            for rel_path, content in output.assets.items():
                file_path = assets_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')

        # Write references
        if output.references:
            references_dir = skill_subdir / self.references_dir_name
            references_dir.mkdir(parents=True, exist_ok=True)
            for rel_path, content in output.references.items():
                file_path = references_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')

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

        # Bundle lsp-engine
        lsp_dir = self.shared_dir / "lsp-engine"
        if lsp_dir.exists():
            for file_path in lsp_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.shared_dir)
                content = file_path.read_text(encoding='utf-8')
                modules[str(rel_path)] = content

        # Bundle code_analyzer
        analyzer_dir = self.shared_dir / "code_analyzer"
        if analyzer_dir.exists():
            for file_path in analyzer_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.shared_dir)
                content = file_path.read_text(encoding='utf-8')
                modules[str(rel_path)] = content

            for file_path in analyzer_dir.rglob("*.yml"):
                rel_path = file_path.relative_to(self.shared_dir)
                modules[str(rel_path)] = file_path.read_text(encoding='utf-8')

            for file_path in analyzer_dir.rglob("*.xml"):
                rel_path = file_path.relative_to(self.shared_dir)
                modules[str(rel_path)] = file_path.read_text(encoding='utf-8')

        return modules
