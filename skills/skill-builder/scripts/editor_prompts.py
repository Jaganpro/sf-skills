#!/usr/bin/env python3
"""
editor_prompts.py - Terminal-based prompt system for interactive skill editor

Provides clean terminal UI with optional prompt_toolkit enhancement.
Falls back to standard input() if prompt_toolkit is not available.
"""

import sys
from typing import List, Optional, Dict, Any

# Try to import prompt_toolkit for enhanced UX
try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.validation import Validator, ValidationError
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def strip_colors() -> None:
        """Disable colors (for piped output or testing)."""
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''
        Colors.NC = ''


class EditorUI:
    """Terminal UI for skill editor."""

    @staticmethod
    def clear_screen():
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")

    @staticmethod
    def print_header(skill_name: str, version: str):
        """
        Print editor header.

        Args:
            skill_name: Name of skill being edited
            version: Current skill version
        """
        width = 60
        print(f"{Colors.CYAN}{'═' * width}{Colors.NC}")
        title = f"Skill Editor: {skill_name} (v{version})"
        padding = (width - len(title)) // 2
        print(f"{Colors.CYAN}{'║'}{Colors.NC}{' ' * padding}{Colors.BOLD}{title}{Colors.NC}{' ' * (width - len(title) - padding - 1)}{Colors.CYAN}{'║'}{Colors.NC}")
        print(f"{Colors.CYAN}{'═' * width}{Colors.NC}")
        print()

    @staticmethod
    def print_divider():
        """Print a simple divider line."""
        print(f"{Colors.CYAN}{'─' * 60}{Colors.NC}")

    @staticmethod
    def print_field_summary(data: Dict[str, Any], highlight_fields: Optional[List[str]] = None):
        """
        Print current frontmatter fields.

        Args:
            data: Frontmatter dictionary
            highlight_fields: List of field names to highlight
        """
        print(f"{Colors.BOLD}Current Fields:{Colors.NC}\n")

        # Define field display order
        field_order = ['name', 'description', 'version', 'author', 'allowed-tools', 'tags', 'license', 'keywords']

        for i, field in enumerate(field_order, 1):
            if field in data:
                value = data[field]

                # Format value for display
                if isinstance(value, list):
                    if len(value) > 3:
                        display_value = f"[{', '.join(str(v) for v in value[:3])}, ... ({len(value)} total)]"
                    else:
                        display_value = f"[{', '.join(str(v) for v in value)}]"
                else:
                    display_value = str(value)
                    if len(display_value) > 50:
                        display_value = display_value[:47] + "..."

                # Highlight if requested
                if highlight_fields and field in highlight_fields:
                    print(f"  {Colors.YELLOW}[{i}] {field}: {display_value}{Colors.NC}")
                else:
                    print(f"  [{i}] {field}: {Colors.CYAN}{display_value}{Colors.NC}")

        print()

    @staticmethod
    def print_menu():
        """Print main menu options."""
        print(f"{Colors.BOLD}Options:{Colors.NC}")
        print(f"  {Colors.GREEN}[e]{Colors.NC} Edit field      {Colors.GREEN}[t]{Colors.NC} Manage tools    {Colors.GREEN}[v]{Colors.NC} Validate")
        print(f"  {Colors.GREEN}[s]{Colors.NC} Save changes    {Colors.GREEN}[r]{Colors.NC} Reload          {Colors.GREEN}[q]{Colors.NC} Quit")
        print()

    @staticmethod
    def print_success(message: str):
        """Print success message."""
        print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

    @staticmethod
    def print_error(message: str):
        """Print error message."""
        print(f"{Colors.RED}✗ {message}{Colors.NC}")

    @staticmethod
    def print_warning(message: str):
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")

    @staticmethod
    def print_info(message: str):
        """Print info message."""
        print(f"{Colors.CYAN}ℹ {message}{Colors.NC}")

    @staticmethod
    def prompt_choice(prompt_text: str, valid_choices: Optional[List[str]] = None, default: Optional[str] = None) -> str:
        """
        Prompt user for input with optional validation.

        Args:
            prompt_text: Text to display as prompt
            valid_choices: List of valid choices (case-insensitive)
            default: Default value if user presses Enter

        Returns:
            User's choice (lowercase)
        """
        if default:
            prompt_display = f"{prompt_text} [{default}]: "
        else:
            prompt_display = f"{prompt_text}: "

        if PROMPT_TOOLKIT_AVAILABLE and valid_choices:
            # Use prompt_toolkit with completion
            completer = WordCompleter(valid_choices, ignore_case=True)

            class ChoiceValidator(Validator):
                def validate(self, document):
                    text = document.text.strip().lower()
                    if text and valid_choices and text not in [c.lower() for c in valid_choices]:
                        raise ValidationError(
                            message=f"Invalid choice. Valid options: {', '.join(valid_choices)}"
                        )

            try:
                result = pt_prompt(
                    prompt_display,
                    completer=completer,
                    validator=ChoiceValidator() if valid_choices else None,
                    validate_while_typing=False
                )
            except (KeyboardInterrupt, EOFError):
                return ''
        else:
            # Fallback to standard input
            try:
                result = input(prompt_display)
            except (KeyboardInterrupt, EOFError):
                return ''

        result = result.strip()

        # Apply default if empty
        if not result and default:
            return default.lower()

        # Validate choices
        if valid_choices:
            result_lower = result.lower()
            if result_lower not in [c.lower() for c in valid_choices]:
                EditorUI.print_error(f"Invalid choice. Valid options: {', '.join(valid_choices)}")
                return EditorUI.prompt_choice(prompt_text, valid_choices, default)

        return result.lower() if valid_choices else result

    @staticmethod
    def prompt_text(prompt_text: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
        """
        Prompt user for text input.

        Args:
            prompt_text: Text to display as prompt
            default: Default value if user presses Enter
            allow_empty: Whether to allow empty input

        Returns:
            User's input string
        """
        if default:
            prompt_display = f"{prompt_text} [{default}]: "
        else:
            prompt_display = f"{prompt_text}: "

        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                result = pt_prompt(prompt_display, default=default or "")
            except (KeyboardInterrupt, EOFError):
                return default or ""
        else:
            try:
                result = input(prompt_display)
            except (KeyboardInterrupt, EOFError):
                return default or ""

        result = result.strip()

        # Apply default if empty
        if not result:
            if default:
                return default
            elif not allow_empty:
                EditorUI.print_error("Input cannot be empty")
                return EditorUI.prompt_text(prompt_text, default, allow_empty)

        return result

    @staticmethod
    def prompt_multiline(prompt_text: str) -> List[str]:
        """
        Prompt user for multi-line input (for lists).

        Args:
            prompt_text: Text to display as prompt

        Returns:
            List of input lines
        """
        print(f"{prompt_text} (enter blank line to finish):")
        lines = []

        while True:
            try:
                line = input("  > ").strip()
                if not line:
                    break
                lines.append(line)
            except (KeyboardInterrupt, EOFError):
                break

        return lines

    @staticmethod
    def confirm(prompt_text: str, default: bool = False) -> bool:
        """
        Prompt user for yes/no confirmation.

        Args:
            prompt_text: Question to ask
            default: Default value if user presses Enter

        Returns:
            True if user confirms, False otherwise
        """
        default_str = "Y/n" if default else "y/N"
        full_prompt = f"{prompt_text} [{default_str}]"

        choice = EditorUI.prompt_choice(full_prompt, valid_choices=['y', 'n', 'yes', 'no'], default='y' if default else 'n')

        return choice in ['y', 'yes']

    @staticmethod
    def show_validation_results(results: List[Any]):
        """
        Display validation results with formatting.

        Args:
            results: List of ValidationResult objects
        """
        errors = [r for r in results if not r.is_valid]
        warnings = [r for r in results if r.is_valid and r.has_suggestions]

        if not errors and not warnings:
            EditorUI.print_success("All validations passed!")
            return

        if errors:
            print(f"\n{Colors.RED}{'═' * 50}{Colors.NC}")
            print(f"{Colors.RED}Validation Errors ({len(errors)}):{Colors.NC}")
            print(f"{Colors.RED}{'═' * 50}{Colors.NC}\n")

            for i, error in enumerate(errors, 1):
                print(f"{i}. {Colors.RED}✗ {error.message}{Colors.NC}")
                if error.has_suggestions:
                    for suggestion in error.suggestions:
                        print(f"   {Colors.YELLOW}→ {suggestion}{Colors.NC}")
                print()

        if warnings:
            print(f"\n{Colors.YELLOW}{'═' * 50}{Colors.NC}")
            print(f"{Colors.YELLOW}Suggestions ({len(warnings)}):{Colors.NC}")
            print(f"{Colors.YELLOW}{'═' * 50}{Colors.NC}\n")

            for i, warning in enumerate(warnings, 1):
                print(f"{i}. {Colors.CYAN}ℹ {warning.message}{Colors.NC}")
                if warning.has_suggestions:
                    for suggestion in warning.suggestions:
                        print(f"   → {suggestion}")
                print()

    @staticmethod
    def show_tools_menu(current_tools: List[str], all_tools: List[str]):
        """
        Display tools management menu.

        Args:
            current_tools: Currently selected tools
            all_tools: All available tools
        """
        print(f"\n{Colors.BOLD}Current Tools ({len(current_tools)}):{Colors.NC}")
        for i, tool in enumerate(current_tools, 1):
            print(f"  {i}. {Colors.GREEN}{tool}{Colors.NC}")

        print(f"\n{Colors.BOLD}Available Tools:{Colors.NC}")
        available = [t for t in all_tools if t not in current_tools]
        for tool in available:
            print(f"  • {tool}")

        print(f"\n{Colors.BOLD}Options:{Colors.NC}")
        print(f"  {Colors.GREEN}[a]{Colors.NC} Add tool    {Colors.RED}[r]{Colors.NC} Remove tool    {Colors.CYAN}[b]{Colors.NC} Back to main menu")

    @staticmethod
    def display_diff(original: Dict[str, Any], modified: Dict[str, Any]):
        """
        Display differences between original and modified frontmatter.

        Args:
            original: Original frontmatter
            modified: Modified frontmatter
        """
        print(f"\n{Colors.BOLD}Changes Preview:{Colors.NC}\n")

        all_keys = set(original.keys()) | set(modified.keys())

        for key in sorted(all_keys):
            orig_val = original.get(key)
            mod_val = modified.get(key)

            if orig_val != mod_val:
                if key not in original:
                    print(f"  {Colors.GREEN}+ {key}: {mod_val}{Colors.NC}")
                elif key not in modified:
                    print(f"  {Colors.RED}- {key}: {orig_val}{Colors.NC}")
                else:
                    print(f"  {Colors.YELLOW}~ {key}:{Colors.NC}")
                    print(f"    {Colors.RED}- {orig_val}{Colors.NC}")
                    print(f"    {Colors.GREEN}+ {mod_val}{Colors.NC}")

        print()


def main():
    """Test UI components."""
    print("Testing EditorUI components...\n")

    EditorUI.print_header("test-skill", "1.0.0")

    test_data = {
        'name': 'test-skill',
        'description': 'A test skill for demonstration',
        'version': '1.0.0',
        'allowed-tools': ['Bash', 'Read', 'Write', 'Edit'],
        'tags': ['test', 'demo', 'example']
    }

    EditorUI.print_field_summary(test_data, highlight_fields=['name'])
    EditorUI.print_menu()

    EditorUI.print_success("This is a success message")
    EditorUI.print_error("This is an error message")
    EditorUI.print_warning("This is a warning message")
    EditorUI.print_info("This is an info message")

    print(f"\nprompt_toolkit available: {PROMPT_TOOLKIT_AVAILABLE}")


if __name__ == "__main__":
    main()
