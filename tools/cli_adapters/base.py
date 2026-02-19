"""
Base adapter interface for CLI-specific skill transformations.

All CLI adapters inherit from CLIAdapter and implement the transform_skill method
to convert sf-skills to their target CLI format.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re
import shutil


@dataclass
class SkillOutput:
    """Transformed skill output for a specific CLI."""

    skill_md: str                              # Transformed SKILL.md content
    scripts: Dict[str, str] = field(default_factory=dict)      # {filename: content}
    assets: Dict[str, str] = field(default_factory=dict)       # {filename: content}
    references: Dict[str, str] = field(default_factory=dict)   # {filename: content}
    cli_specific: Dict[str, str] = field(default_factory=dict) # CLI-specific files


class CLIAdapter(ABC):
    """
    Abstract base class for CLI-specific skill transformations.

    Each adapter handles:
    1. Path resolution for the target CLI
    2. SKILL.md transformation (removing Claude Code-specific syntax)
    3. Script bundling (including shared modules)
    4. Directory structure mapping (assets/, references/, scripts/ per spec)
    """

    def __init__(self, repo_root: Path):
        """
        Initialize adapter with repository root.

        Args:
            repo_root: Path to sf-skills repository root
        """
        self.repo_root = repo_root
        self.shared_dir = repo_root / "shared"

    @property
    @abstractmethod
    def cli_name(self) -> str:
        """CLI identifier (e.g., 'opencode', 'codex', 'gemini')."""
        pass

    @property
    @abstractmethod
    def default_install_path(self) -> Path:
        """Default installation directory for this CLI."""
        pass

    @property
    def assets_dir_name(self) -> str:
        """Name of assets directory in output (spec: assets/)."""
        return "assets"

    @property
    def references_dir_name(self) -> str:
        """Name of references directory in output (spec: references/)."""
        return "references"

    @abstractmethod
    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md content for this CLI.

        Args:
            content: Original SKILL.md content
            skill_name: Name of the skill being transformed

        Returns:
            Transformed SKILL.md content
        """
        pass

    def transform_skill(self, source_dir: Path) -> SkillOutput:
        """
        Transform a skill for this CLI.

        Args:
            source_dir: Path to skill directory (e.g., sf-apex/)

        Returns:
            SkillOutput with transformed files
        """
        skill_name = source_dir.name

        # Read and transform SKILL.md
        skill_md_path = source_dir / "SKILL.md"
        if skill_md_path.exists():
            skill_md = skill_md_path.read_text(encoding='utf-8')
            skill_md = self.transform_skill_md(skill_md, skill_name)
        else:
            skill_md = f"# {skill_name}\n\nNo SKILL.md found in source."

        # Copy scripts from hooks/scripts/
        scripts = self._copy_scripts(source_dir)

        # Generate scripts README
        scripts["README.md"] = self._generate_scripts_readme(source_dir)

        # Copy assets (spec directory)
        assets = self._copy_directory_contents(source_dir / "assets")

        # Copy references (spec directory)
        references = self._copy_directory_contents(source_dir / "references")

        return SkillOutput(
            skill_md=skill_md,
            scripts=scripts,
            assets=assets,
            references=references,
        )

    def _copy_scripts(self, source_dir: Path) -> Dict[str, str]:
        """
        Copy Python scripts from hooks/scripts/ directory.

        Args:
            source_dir: Skill source directory

        Returns:
            Dict mapping filename to content
        """
        scripts = {}
        scripts_dir = source_dir / "hooks" / "scripts"

        if not scripts_dir.exists():
            return scripts

        for script_path in scripts_dir.rglob("*.py"):
            # Preserve subdirectory structure
            rel_path = script_path.relative_to(scripts_dir)
            content = script_path.read_text(encoding='utf-8')

            # Transform script for standalone use
            content = self._transform_script(content)

            scripts[str(rel_path)] = content

        # Also copy any JSON data files
        for json_path in scripts_dir.rglob("*.json"):
            rel_path = json_path.relative_to(scripts_dir)
            scripts[str(rel_path)] = json_path.read_text(encoding='utf-8')

        return scripts

    def _transform_script(self, content: str) -> str:
        """
        Transform a Python script for standalone use.

        Modifies scripts to accept file path as argument in addition
        to reading from stdin (Claude Code hook mode).

        Args:
            content: Original script content

        Returns:
            Transformed script content
        """
        # Replace ${CLAUDE_PLUGIN_ROOT} with relative path marker
        content = content.replace('${CLAUDE_PLUGIN_ROOT}', '.')

        return content

    def _copy_directory_contents(self, dir_path: Path) -> Dict[str, str]:
        """
        Copy all files from a directory, preserving structure.

        Args:
            dir_path: Directory to copy from

        Returns:
            Dict mapping relative path to content
        """
        files = {}

        if not dir_path.exists():
            return files

        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(dir_path)
                try:
                    # Try to read as text
                    files[str(rel_path)] = file_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    # Skip binary files or handle differently
                    pass

        return files

    def _generate_scripts_readme(self, source_dir: Path) -> str:
        """
        Generate README for scripts directory explaining manual usage.

        Args:
            source_dir: Skill source directory

        Returns:
            README content
        """
        skill_name = source_dir.name
        scripts_dir = source_dir / "hooks" / "scripts"

        readme = f"""# {skill_name} Validation Scripts

These scripts provide validation for {skill_name} files. In Claude Code,
they run automatically via PostToolUse hooks. For other CLIs, run them manually.

## Usage

```bash
# Validate a file
python scripts/validate_*.py path/to/your/file

# Example for Apex
python scripts/validate_apex.py MyClass.cls
```

## Available Scripts

"""

        if scripts_dir.exists():
            for script in sorted(scripts_dir.glob("*.py")):
                readme += f"- `{script.name}` - "
                # Try to extract description from docstring
                content = script.read_text(encoding='utf-8')
                docstring_match = re.search(r'"""([^"]+)"""', content)
                if docstring_match:
                    desc = docstring_match.group(1).strip().split('\n')[0]
                    readme += desc
                else:
                    readme += "Validation script"
                readme += "\n"
        else:
            readme += "(No scripts found)\n"

        readme += """
## Requirements

- Python 3.8+
- Dependencies vary by script (check imports)

## Note

These scripts were originally designed as Claude Code hooks.
They accept file paths as command-line arguments for manual use.
"""

        return readme

    def _common_skill_md_transforms(self, content: str) -> str:
        """
        Apply common SKILL.md transformations for all CLIs.

        Args:
            content: Original SKILL.md content

        Returns:
            Transformed content
        """
        # Remove ${CLAUDE_PLUGIN_ROOT} references
        content = content.replace('${CLAUDE_PLUGIN_ROOT}', '.')

        # Update Skill() invocation syntax to generic form
        # Skill(skill="sf-apex", args="...") → @sf-apex ...
        content = re.sub(
            r'Skill\(skill="([^"]+)"(?:,\s*args="([^"]*)")?\)',
            r'@\1 \2',
            content
        )

        return content

    def write_output(self, output: SkillOutput, target_dir: Path) -> None:
        """
        Write transformed skill output to target directory.

        Args:
            output: SkillOutput with transformed files
            target_dir: Directory to write to
        """
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)

        # Write SKILL.md
        (target_dir / "SKILL.md").write_text(output.skill_md, encoding='utf-8')

        # Write scripts
        if output.scripts:
            scripts_dir = target_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            for rel_path, content in output.scripts.items():
                file_path = scripts_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')

        # Write assets
        if output.assets:
            assets_dir = target_dir / self.assets_dir_name
            assets_dir.mkdir(exist_ok=True)
            for rel_path, content in output.assets.items():
                file_path = assets_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')

        # Write references
        if output.references:
            references_dir = target_dir / self.references_dir_name
            references_dir.mkdir(exist_ok=True)
            for rel_path, content in output.references.items():
                file_path = references_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')

        # Write CLI-specific files
        for rel_path, content in output.cli_specific.items():
            file_path = target_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
