#!/usr/bin/env python3
"""
interactive_editor.py - Terminal-based interactive skill editor

Provides a user-friendly interface for editing Claude Code skills with:
- Real-time validation
- Tool management
- Version guidance
- Preview before save
"""

import sys
import argparse
import copy
from pathlib import Path
from typing import Dict, Optional

# Import local modules
from editor_validators import (
    SkillFieldValidator,
    SkillValidator,
    ValidationResult,
    load_skill_frontmatter,
    save_skill_frontmatter,
    VALID_TOOLS
)
from editor_prompts import EditorUI, Colors


class SkillEditor:
    """Interactive editor for Claude Code skills."""

    def __init__(self, skill_path: Path):
        """
        Initialize skill editor.

        Args:
            skill_path: Path to skill directory or SKILL.md file
        """
        # Resolve to SKILL.md file
        if skill_path.is_dir():
            self.skill_file = skill_path / "SKILL.md"
        else:
            self.skill_file = skill_path

        if not self.skill_file.exists():
            raise FileNotFoundError(f"SKILL.md not found: {self.skill_file}")

        # Load skill data
        self.original_data = None
        self.current_data = None
        self.load_skill()

    def load_skill(self) -> bool:
        """
        Load skill from file.

        Returns:
            True if loaded successfully
        """
        data, yaml_str, error = load_skill_frontmatter(self.skill_file)

        if error:
            EditorUI.print_error(f"Failed to load skill: {error}")
            return False

        if data is None:
            EditorUI.print_error("No frontmatter found in SKILL.md")
            return False

        self.original_data = copy.deepcopy(data)
        self.current_data = data

        return True

    def reload_skill(self) -> bool:
        """
        Reload skill from file (discard unsaved changes).

        Returns:
            True if reloaded successfully
        """
        confirm = EditorUI.confirm("Discard all unsaved changes?", default=False)

        if confirm:
            success = self.load_skill()
            if success:
                EditorUI.print_success("Skill reloaded from file")
            return success

        return False

    def has_unsaved_changes(self) -> bool:
        """
        Check if there are unsaved changes.

        Returns:
            True if changes exist
        """
        return self.current_data != self.original_data

    def save_skill(self) -> bool:
        """
        Save current skill data to file.

        Returns:
            True if saved successfully
        """
        if not self.has_unsaved_changes():
            EditorUI.print_info("No changes to save")
            return True

        # Show diff
        EditorUI.display_diff(self.original_data, self.current_data)

        # Confirm save
        if not EditorUI.confirm("Save these changes?", default=True):
            EditorUI.print_info("Save cancelled")
            return False

        # Validate before save
        results = SkillValidator.validate_frontmatter(self.current_data)
        if SkillValidator.has_critical_errors(results):
            EditorUI.print_error("Cannot save: critical validation errors")
            EditorUI.show_validation_results(results)
            return False

        # Save to file
        success, error = save_skill_frontmatter(self.skill_file, self.current_data)

        if success:
            EditorUI.print_success(f"Saved to {self.skill_file}")
            self.original_data = copy.deepcopy(self.current_data)
            return True
        else:
            EditorUI.print_error(f"Failed to save: {error}")
            return False

    def validate_skill(self):
        """Run validation on current skill data."""
        print(f"\n{Colors.BOLD}Running Validation...{Colors.NC}\n")

        results = SkillValidator.validate_frontmatter(self.current_data)

        EditorUI.show_validation_results(results)

        if SkillValidator.has_critical_errors(results):
            EditorUI.print_error("Critical errors found - skill may not work correctly")
        else:
            EditorUI.print_success("Validation passed! Skill is ready to use")

    def edit_field(self):
        """Edit a frontmatter field interactively."""
        # Show available fields
        editable_fields = {
            '1': ('name', 'Skill name (kebab-case)'),
            '2': ('description', 'One-line description'),
            '3': ('version', 'Version (semver: X.Y.Z)'),
            '4': ('author', 'Author name'),
            '5': ('license', 'License (e.g., MIT, Apache-2.0)'),
            '6': ('tags', 'Tags (comma-separated)'),
            '7': ('keywords', 'Keywords (comma-separated)')
        }

        print(f"\n{Colors.BOLD}Edit Field:{Colors.NC}\n")
        for key, (field, desc) in editable_fields.items():
            current = self.current_data.get(field, "[not set]")
            if isinstance(current, list):
                current = ', '.join(str(x) for x in current)
            print(f"  [{key}] {field}: {Colors.CYAN}{current}{Colors.NC}")
            print(f"      ({desc})")

        print(f"\n  [b] Back to main menu")

        choice = EditorUI.prompt_choice("\nSelect field to edit", valid_choices=list(editable_fields.keys()) + ['b'])

        if choice == 'b':
            return

        field, desc = editable_fields[choice]

        # Get current value
        current_value = self.current_data.get(field, "")
        if isinstance(current_value, list):
            current_value = ', '.join(str(x) for x in current_value)

        # Prompt for new value
        print(f"\n{Colors.BOLD}Editing: {field}{Colors.NC}")
        print(f"Current: {Colors.CYAN}{current_value}{Colors.NC}")

        new_value = EditorUI.prompt_text(f"New value for {field}", default=str(current_value) if current_value else None)

        # Handle list fields (tags, keywords)
        if field in ['tags', 'keywords']:
            # Convert comma-separated to list
            new_value = [x.strip() for x in new_value.split(',') if x.strip()]

        # Validate new value
        if field == 'name':
            result = SkillFieldValidator.validate_name(new_value)
        elif field == 'description':
            result = SkillFieldValidator.validate_description(new_value)
        elif field == 'version':
            result = SkillFieldValidator.validate_version(new_value)
        elif field == 'author':
            result = SkillFieldValidator.validate_author(new_value)
        elif field in ['tags', 'keywords']:
            result = SkillFieldValidator.validate_tags(new_value)
        else:
            # No specific validation
            result = ValidationResult(is_valid=True, message="Value updated")

        if result.is_valid:
            self.current_data[field] = new_value
            EditorUI.print_success(f"Updated {field}")
        else:
            EditorUI.print_error(result.message)
            if result.has_suggestions:
                for suggestion in result.suggestions:
                    print(f"  → {suggestion}")

            # Ask if they want to try again
            if EditorUI.confirm("Try again?", default=True):
                self.edit_field()

    def manage_tools(self):
        """Manage allowed-tools list."""
        while True:
            current_tools = self.current_data.get('allowed-tools', [])

            EditorUI.show_tools_menu(current_tools, VALID_TOOLS)

            choice = EditorUI.prompt_choice("\nSelect option", valid_choices=['a', 'r', 'b'])

            if choice == 'b':
                break
            elif choice == 'a':
                self._add_tool()
            elif choice == 'r':
                self._remove_tool()

    def _add_tool(self):
        """Add a tool to allowed-tools."""
        current_tools = self.current_data.get('allowed-tools', [])
        available = [t for t in VALID_TOOLS if t not in current_tools]

        if not available:
            EditorUI.print_info("All tools are already added")
            return

        print(f"\n{Colors.BOLD}Available Tools:{Colors.NC}")
        for i, tool in enumerate(available, 1):
            print(f"  {i}. {tool}")

        tool_name = EditorUI.prompt_text("\nEnter tool name to add")

        # Validate tool
        result = SkillFieldValidator.validate_tool(tool_name)

        if not result.is_valid:
            EditorUI.print_error(result.message)
            if result.has_suggestions:
                for suggestion in result.suggestions:
                    print(f"  → {suggestion}")
            return

        # Check if already added
        if tool_name in current_tools:
            EditorUI.print_warning(f"{tool_name} is already in allowed-tools")
            return

        # Add tool
        if 'allowed-tools' not in self.current_data:
            self.current_data['allowed-tools'] = []

        self.current_data['allowed-tools'].append(tool_name)
        EditorUI.print_success(f"Added {tool_name} to allowed-tools")

    def _remove_tool(self):
        """Remove a tool from allowed-tools."""
        current_tools = self.current_data.get('allowed-tools', [])

        if not current_tools:
            EditorUI.print_warning("No tools to remove")
            return

        print(f"\n{Colors.BOLD}Current Tools:{Colors.NC}")
        for i, tool in enumerate(current_tools, 1):
            print(f"  {i}. {tool}")

        choice = EditorUI.prompt_text("\nEnter tool name or number to remove")

        # Handle numeric choice
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(current_tools):
                tool_name = current_tools[idx]
            else:
                EditorUI.print_error("Invalid number")
                return
        else:
            tool_name = choice

        # Remove tool
        if tool_name in current_tools:
            self.current_data['allowed-tools'].remove(tool_name)
            EditorUI.print_success(f"Removed {tool_name} from allowed-tools")
        else:
            EditorUI.print_error(f"{tool_name} not found in allowed-tools")

    def show_main_screen(self):
        """Display main editor screen."""
        EditorUI.clear_screen()

        name = self.current_data.get('name', 'unknown')
        version = self.current_data.get('version', '0.0.0')

        EditorUI.print_header(name, version)

        # Show unsaved changes indicator
        if self.has_unsaved_changes():
            print(f"{Colors.YELLOW}● Unsaved changes{Colors.NC}\n")

        EditorUI.print_field_summary(self.current_data)
        EditorUI.print_menu()

    def run(self):
        """Run the interactive editor main loop."""
        print(f"\n{Colors.GREEN}═══════════════════════════════════════════════════════{Colors.NC}")
        print(f"{Colors.GREEN}  Interactive Skill Editor{Colors.NC}")
        print(f"{Colors.GREEN}═══════════════════════════════════════════════════════{Colors.NC}\n")

        print(f"Editing: {Colors.CYAN}{self.skill_file}{Colors.NC}\n")

        while True:
            self.show_main_screen()

            choice = EditorUI.prompt_choice("Select option", valid_choices=['e', 't', 'v', 's', 'r', 'q'])

            if choice == 'q':
                # Quit
                if self.has_unsaved_changes():
                    if not EditorUI.confirm("You have unsaved changes. Quit anyway?", default=False):
                        continue

                print(f"\n{Colors.CYAN}Goodbye!{Colors.NC}\n")
                break

            elif choice == 'e':
                # Edit field
                self.edit_field()

            elif choice == 't':
                # Manage tools
                self.manage_tools()

            elif choice == 'v':
                # Validate
                self.validate_skill()
                input("\nPress Enter to continue...")

            elif choice == 's':
                # Save
                self.save_skill()
                input("\nPress Enter to continue...")

            elif choice == 'r':
                # Reload
                self.reload_skill()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive editor for Claude Code skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Edit a skill by directory path
  python3 interactive_editor.py ~/.claude/skills/my-skill/

  # Edit a skill by SKILL.md file path
  python3 interactive_editor.py ~/.claude/skills/my-skill/SKILL.md

Features:
  - Edit frontmatter fields interactively
  - Add/remove tools with validation
  - Real-time validation feedback
  - Preview changes before saving
  - Version guidance for semver updates
        """
    )

    parser.add_argument(
        'skill_path',
        type=Path,
        help='Path to skill directory or SKILL.md file'
    )

    args = parser.parse_args()

    # Initialize editor
    try:
        editor = SkillEditor(args.skill_path)
        editor.run()
    except FileNotFoundError as e:
        print(f"{Colors.RED}Error: {e}{Colors.NC}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
