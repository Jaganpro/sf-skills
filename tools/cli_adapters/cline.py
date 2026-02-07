"""
Cline/Agentforce Vibes adapter for sf-skills.

Cline uses a .clinerules directory or file system:
- Single file: .clinerules (markdown)
- Directory: .clinerules/ with multiple .md files (auto-combined)

Agentforce Vibes is built on a Salesforce fork of Cline and uses
the same .clinerules format.

This adapter transforms SKILL.md into Cline-compatible markdown rules
with templates inlined for self-contained usage.
"""

from pathlib import Path
from typing import Dict, Optional
import re

from .base import CLIAdapter, SkillOutput


class ClineAdapter(CLIAdapter):
    """
    Adapter for Cline and Agentforce Vibes.

    Cline uses pure markdown files in .clinerules/ directory.
    Files are automatically combined in alphanumeric order.

    Key differences from other CLIs:
    - No YAML frontmatter (pure markdown)
    - Templates must be inlined (no external file references)
    - No hook/validation support (manual only)
    """

    # Skill ordering for numeric prefixes
    SKILL_ORDER = {
        'sf-apex': '01',
        'sf-flow': '02',
        'sf-lwc': '03',
        'sf-soql': '04',
        'sf-testing': '05',
        'sf-debug': '06',
        'sf-metadata': '07',
        'sf-data': '08',
        'sf-connected-apps': '09',
        'sf-integration': '10',
        'sf-ai-agentforce': '11',
        'sf-deploy': '12',
        'sf-diagram-mermaid': '13',
        'skill-builder': '14',
        'sf-diagram-nanobananapro': '15',
    }

    @property
    def cli_name(self) -> str:
        return "cline"

    @property
    def default_install_path(self) -> Path:
        """
        Default to project-level .clinerules/ directory.

        Cline checks:
        1. .clinerules (single file)
        2. .clinerules/ (directory with multiple .md files)
        """
        cwd = Path.cwd()
        return cwd / ".clinerules"

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md into Cline-compatible markdown.

        Cline format:
        - Pure markdown (no YAML frontmatter)
        - Clear section headers
        - Inlined code templates
        """
        # Apply common transformations first
        content = self._common_skill_md_transforms(content)

        # Strip YAML frontmatter
        content = self._strip_yaml_frontmatter(content)

        # Clean up any remaining Claude Code-specific syntax
        content = self._clean_claude_specific(content)

        # Add Cline-specific header
        display_name = self._get_display_name(skill_name)

        header = f"""# {display_name}

> Salesforce development rules for {skill_name.replace('sf-', '').replace('-', ' ').title()}
>
> Source: [sf-skills](https://github.com/Jaganpro/sf-skills)

---

"""

        # Add footer with usage notes
        footer = f"""

---

## Cline Usage Notes

This rule was converted from [sf-skills/{skill_name}](https://github.com/Jaganpro/sf-skills/tree/main/{skill_name}).

### File Patterns

When working with files matching these patterns, apply the rules above:
{self._get_file_patterns(skill_name)}

### Cross-Skill References

Other Salesforce skills you may want to enable:
- `sf-apex` - Apex code generation and review
- `sf-flow` - Flow automation
- `sf-deploy` - Deployment automation
- `sf-metadata` - Metadata operations

### Validation

Validation scripts from the original skill are not automatically executed
in Cline. For full validation, consider using the original sf-skills
with Claude Code or running validation scripts manually.
"""

        return header + content.strip() + footer

    def _strip_yaml_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content."""
        return re.sub(
            r'^---\s*\n.*?\n---\s*\n',
            '',
            content,
            flags=re.DOTALL
        )

    def _clean_claude_specific(self, content: str) -> str:
        """Remove or transform Claude Code-specific syntax."""
        # Remove @skill references (already handled by common transforms)
        # Clean up marketplace path references
        content = re.sub(
            r'~/.claude/plugins/marketplaces/sf-skills/[^/]+/',
            '',
            content
        )

        # Transform Skill() calls to just references
        content = re.sub(
            r'@([a-z-]+)\s*',
            r'See \1 rules for details. ',
            content
        )

        # Clean up double spaces
        content = re.sub(r'  +', ' ', content)

        return content

    def _get_display_name(self, skill_name: str) -> str:
        """Get human-readable display name for skill."""
        name_mapping = {
            'sf-apex': 'Salesforce Apex Development',
            'sf-flow': 'Salesforce Flow Automation',
            'sf-lwc': 'Lightning Web Components',
            'sf-soql': 'SOQL Query Patterns',
            'sf-testing': 'Apex Testing Standards',
            'sf-debug': 'Debug Log Analysis',
            'sf-metadata': 'Metadata Operations',
            'sf-data': 'Data Factory Patterns',
            'sf-connected-apps': 'Connected Apps & OAuth',
            'sf-integration': 'Integration Patterns',
            'sf-ai-agentforce': 'Agentforce AI Agents',
            'sf-deploy': 'Deployment Automation',
            'sf-diagram-mermaid': 'Mermaid Diagrams',
            'skill-builder': 'Skill Builder',
            'sf-diagram-nanobananapro': 'Nano Banana Pro Diagrams',
        }
        return name_mapping.get(skill_name, skill_name.replace('-', ' ').title())

    def _get_file_patterns(self, skill_name: str) -> str:
        """Get file patterns as markdown list."""
        pattern_mapping = {
            'sf-apex': '- `**/*.cls` - Apex classes\n- `**/*.trigger` - Apex triggers',
            'sf-flow': '- `**/*.flow-meta.xml` - Flow definitions',
            'sf-lwc': '- `**/lwc/**/*.js` - LWC JavaScript\n- `**/lwc/**/*.html` - LWC templates\n- `**/lwc/**/*.css` - LWC styles',
            'sf-soql': '- `**/*.soql` - SOQL query files\n- `**/*.apex` - Anonymous Apex scripts',
            'sf-testing': '- `**/*Test.cls` - Test classes',
            'sf-debug': '- `**/*.log` - Debug log files',
            'sf-metadata': '- `**/*-meta.xml` - Metadata files',
            'sf-data': '- `**/*.json` - Data files\n- `**/*.csv` - CSV data files',
            'sf-connected-apps': '- `**/*.connectedApp-meta.xml` - Connected Apps',
            'sf-integration': '- `**/*.namedCredential-meta.xml` - Named Credentials\n- `**/*.externalService-meta.xml` - External Services',
            'sf-ai-agentforce': '- `**/*.genAiFunction-meta.xml` - GenAI functions\n- `**/*.genAiPlugin-meta.xml` - GenAI plugins\n- `**/*.promptTemplate-meta.xml` - Prompt templates\n- `**/*.lightningTypeBundle-meta.xml` - Custom Lightning types',
            'sf-deploy': '- `**/sfdx-project.json` - Project config\n- `**/package.xml` - Package manifests',
            'sf-diagram-mermaid': '- `**/*.md` - Markdown with diagrams',
            'skill-builder': '- `**/SKILL.md` - Skill definitions',
            'sf-diagram-nanobananapro': '- `**/*.png` - Generated images\n- `**/*.jpg` - Generated images',
        }
        return pattern_mapping.get(skill_name, '- `**/*` - All files')

    def transform_skill(self, source_dir: Path) -> SkillOutput:
        """
        Transform skill for Cline.

        Creates a single markdown file with templates inlined.
        No scripts or supporting files (Cline doesn't support them).
        """
        skill_name = source_dir.name

        # Read and transform SKILL.md
        skill_md_path = source_dir / "SKILL.md"
        if skill_md_path.exists():
            skill_md = skill_md_path.read_text(encoding='utf-8')
            skill_md = self.transform_skill_md(skill_md, skill_name)
        else:
            skill_md = f"# {skill_name}\n\nNo SKILL.md found in source."

        # Inline templates into the skill content
        templates_dir = source_dir / "templates"
        if templates_dir.exists():
            templates_section = self._build_templates_section(templates_dir, skill_name)
            if templates_section:
                # Insert templates before the footer
                footer_marker = "---\n\n## Cline Usage Notes"
                if footer_marker in skill_md:
                    skill_md = skill_md.replace(
                        footer_marker,
                        templates_section + "\n\n" + footer_marker
                    )
                else:
                    skill_md += "\n\n" + templates_section

        # Determine output filename with numeric prefix
        prefix = self.SKILL_ORDER.get(skill_name, '99')
        output_filename = f"{prefix}-{skill_name}.md"

        return SkillOutput(
            skill_md=skill_md,
            scripts={},       # Not supported in Cline
            templates={},     # Inlined into skill_md
            docs={},          # Not needed for Cline
            examples={},      # Not needed for Cline
            cli_specific={output_filename: skill_md}
        )

    def _build_templates_section(self, templates_dir: Path, skill_name: str) -> str:
        """Build markdown section with inlined templates."""
        templates = []

        for template_path in sorted(templates_dir.rglob("*")):
            if template_path.is_file():
                rel_path = template_path.relative_to(templates_dir)
                try:
                    content = template_path.read_text(encoding='utf-8')
                    # Determine language for code block
                    lang = self._get_language(template_path)

                    templates.append(f"""### Template: {rel_path}

```{lang}
{content.strip()}
```
""")
                except UnicodeDecodeError:
                    # Skip binary files
                    pass

        if not templates:
            return ""

        return f"""---

## Code Templates

The following templates are production-ready patterns for {skill_name.replace('sf-', '').replace('-', ' ')}.
Copy and customize these for your implementation.

""" + "\n".join(templates)

    def _get_language(self, file_path: Path) -> str:
        """Determine code block language from file extension."""
        ext_mapping = {
            '.cls': 'apex',
            '.trigger': 'apex',
            '.apex': 'apex',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.py': 'python',
            '.sh': 'bash',
            '.soql': 'sql',
        }
        return ext_mapping.get(file_path.suffix.lower(), '')

    def write_output(self, output: SkillOutput, target_dir: Path) -> None:
        """
        Write transformed skill output to .clinerules/ directory.

        For Cline, we write a single markdown file per skill.
        All files go directly into .clinerules/ (flat structure).

        Note: The installer passes target_dir as .clinerules/skill-name/
        but we want to write to .clinerules/ directly.
        """
        # Get the parent directory (.clinerules/) since installer adds skill_name
        clinerules_dir = target_dir.parent

        # Ensure .clinerules/ directory exists
        clinerules_dir.mkdir(parents=True, exist_ok=True)

        # Write the rule file(s) directly to .clinerules/
        for rel_path, content in output.cli_specific.items():
            file_path = clinerules_dir / rel_path
            file_path.write_text(content, encoding='utf-8')


class AgentforceVibesAdapter(ClineAdapter):
    """
    Adapter for Agentforce Vibes (Salesforce's fork of Cline).

    Agentforce Vibes uses the same .clinerules format as Cline,
    but with some Salesforce-specific enhancements available via
    the /newrule command.

    This adapter is an alias for ClineAdapter since the file
    format is identical.
    """

    @property
    def cli_name(self) -> str:
        return "agentforce-vibes"

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md for Agentforce Vibes.

        Same as Cline but with Agentforce-specific notes.
        """
        # Use parent transformation
        content = super().transform_skill_md(content, skill_name)

        # Add Agentforce-specific tip
        agentforce_note = """
### Agentforce Vibes Tip

You can also create persistent rules using the `/newrule` command
directly in Agentforce Vibes. This rule was converted from sf-skills
for compatibility.

For the best Agentforce experience, consider using the native
Salesforce DX MCP Server which provides 20+ integrated tools.
"""

        # Insert before the closing footer
        if "---\n\n## Cline Usage Notes" in content:
            content = content.replace(
                "---\n\n## Cline Usage Notes",
                "---\n\n## Agentforce Vibes Usage Notes"
            )

        # Add the Agentforce tip at the end
        content += "\n" + agentforce_note

        return content
