#!/usr/bin/env python3
"""
list_tools.py - Display valid Claude Code tools

Shows the complete list of valid tools that can be used in skill frontmatter.
"""

import sys

# ANSI color codes
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'


# Valid Claude Code tools with descriptions
TOOLS = {
    "File Operations": {
        "Read": "Reading files from the filesystem",
        "Write": "Creating new files",
        "Edit": "Modifying existing files in-place",
        "Glob": "Finding files by pattern (e.g., '**/*.js')",
        "Grep": "Searching file contents with regex",
    },
    "System": {
        "Bash": "Executing shell commands and system operations",
        "BashOutput": "Reading output from background shell processes",
        "KillShell": "Terminating background shell processes",
    },
    "Interactive": {
        "AskUserQuestion": "Prompting users for input during execution",
        "TodoWrite": "Managing task lists and tracking progress",
    },
    "Advanced": {
        "WebFetch": "Fetching content from web URLs",
        "SlashCommand": "Executing Claude Code slash commands",
        "Skill": "Invoking other skills",
    }
}


def print_tools_by_category():
    """Print tools organized by category."""
    print(f"{Colors.BLUE}📋 Valid Claude Code Tools{Colors.NC}\n")

    for category, tools in TOOLS.items():
        print(f"{Colors.CYAN}━━━ {category} ━━━{Colors.NC}")
        for tool, description in tools.items():
            print(f"  {Colors.GREEN}{tool:20}{Colors.NC} {description}")
        print()


def print_yaml_example():
    """Print example YAML frontmatter."""
    print(f"{Colors.YELLOW}📝 YAML Frontmatter Example:{Colors.NC}\n")
    print("---")
    print("name: my-skill")
    print("description: Description of what this skill does")
    print("version: 1.0.0")
    print(f"{Colors.CYAN}allowed-tools:{Colors.NC}")
    print("  - Read")
    print("  - Write")
    print("  - Bash")
    print("---")
    print()


def print_usage_tips():
    """Print tips for tool selection."""
    print(f"{Colors.MAGENTA}💡 Tool Selection Tips:{Colors.NC}\n")
    tips = [
        "Only request tools you'll actually use",
        "Tool names are case-sensitive (e.g., 'Bash' not 'bash')",
        "More tools ≠ better - follow principle of least privilege",
        "Common combinations:",
        "  • Code analysis: Read, Glob, Grep",
        "  • Doc generation: Read, Write, Glob",
        "  • Interactive workflow: AskUserQuestion, Read, Write",
        "  • System operations: Bash, Read",
    ]
    for tip in tips:
        if tip.startswith("  •"):
            print(f"    {tip}")
        else:
            print(f"  • {tip}")
    print()


def print_all_tools_list():
    """Print flat list of all tools."""
    all_tools = []
    for category in TOOLS.values():
        all_tools.extend(category.keys())

    print(f"{Colors.BLUE}Complete list (for copy-paste):{Colors.NC}")
    print(", ".join(all_tools))
    print()


def main():
    """Main entry point."""
    show_example = "--example" in sys.argv or "-e" in sys.argv
    show_brief = "--brief" in sys.argv or "-b" in sys.argv

    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: list_tools.py [options]")
        print()
        print("Display valid Claude Code tools for use in skill frontmatter.")
        print()
        print("Options:")
        print("  --example, -e    Show YAML frontmatter example")
        print("  --brief, -b      Show brief list only")
        print("  --help, -h       Show this help message")
        print()
        print("Examples:")
        print("  list_tools.py              # Show all information")
        print("  list_tools.py --brief      # Show just the list")
        print("  list_tools.py --example    # Show YAML example")
        sys.exit(0)

    if show_brief:
        print_all_tools_list()
    else:
        print_tools_by_category()
        print_all_tools_list()
        print_usage_tips()

        if show_example:
            print_yaml_example()


if __name__ == "__main__":
    main()
