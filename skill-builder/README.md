# Skill-Builder: Claude Code Skill Creation Wizard

An interactive meta-skill for creating, scaffolding, validating, and migrating Claude Code skills with comprehensive guidance and deep validation.

**Version**: 2.0.0

## Overview

The skill-builder provides a guided wizard that walks you through creating well-structured Claude Code skills. It handles everything from gathering metadata to creating files, validating YAML frontmatter, checking tool permissions, and providing helpful documentation.

## Prerequisites

Before using skill-builder, ensure you have:

1. **Python 3** - Already installed on your system
2. **PyYAML** - Required for YAML validation
3. **packaging** - Required for dependency version resolution (v2.0+)

### Installing Dependencies

**Recommended: Using the included virtual environment:**
```bash
# Virtual environment is already set up at:
# ~/.claude/skills/skill-builder/.venv/

# Activate it to use the scripts:
source ~/.claude/skills/skill-builder/.venv/bin/activate

# Dependencies already installed:
# - PyYAML 6.0.3
# - packaging 25.0
```

**Alternative: Manual installation:**
```bash
python3 -m venv ~/.venv/skill-builder
source ~/.venv/skill-builder/bin/activate
pip install pyyaml packaging
```

The scripts will provide helpful error messages if dependencies are missing.

## Features

### Core Features (v1.0)
- ✨ **Interactive Wizard**: 5-7 simple questions guide you through skill creation
- 📝 **Template-Based**: Uses a clean minimal-starter template you can customize
- ✅ **Deep Validation**: Comprehensive checks for YAML syntax, required fields, and tool permissions
- 🛡️ **Error Prevention**: Catches common mistakes before they become runtime issues
- 📚 **Educational**: Teaches best practices throughout the creation process
- 🎯 **Flexible**: Create global or project-specific skills

### Advanced Features (v1.2)
- 📊 **Bulk Validation**: Validate all installed skills at once with comprehensive reporting
- ⚡ **Parallel Processing**: Fast validation of multiple skills simultaneously
- 📈 **Multiple Report Formats**: Console (colored), JSON, and more
- 🔍 **Format Detection**: Automatically detect skill format versions
- 🎨 **Enhanced Tooling**: Updated tool list with latest Claude Code tools

### New Features (v2.0) 🆕
- ✏️ **Interactive Editor**: Terminal-based skill editor for refining existing skills
  - Real-time validation with inline suggestions
  - Field-by-field editing with confirmation
  - Tool management (add/remove from allowed-tools)
  - Preview changes before saving
  - Automatic backup on save
- 🔗 **Dependency Management**: Complete dependency system with version constraints
  - Semver constraint parsing (^, ~, >=, exact, *)
  - Check dependencies for skills
  - Visualize dependency trees
  - Detect circular dependencies
  - Bulk validation of all skill dependencies
- 📦 **Version Resolution**: Smart version constraint satisfaction checking
  - Compatible releases (^1.2.0 means >=1.2.0 <2.0.0)
  - Approximate releases (~1.2.0 means >=1.2.0 <1.3.0)
  - Comparison operators (>=, >, <=, <, ==)
  - Wildcard support (*)

## Quick Start

### Creating Your First Skill

In any Claude Code session, simply say:

```
I need to create a new skill for [your purpose]
```

Or more directly:

```
Use the skill-builder skill to create a new skill
```

The wizard will guide you through:
1. **Skill name** - What to call your skill (kebab-case)
2. **Description** - One-line summary of what it does
3. **Author** - Your name (optional)
4. **Tools needed** - Which Claude Code tools your skill will use
5. **Optional components** - README, references, assets, scripts
6. **Tags** - Categorization keywords
7. **Location** - Global or project-specific

### Example Session

```
User: I want to create a skill that helps me write git commit messages

Skill-builder will ask:
  → Name? "commit-message-helper"
  → Description? "Generates conventional commit messages based on staged changes"
  → Author? "Your Name"
  → Tools? [Read, Bash, Grep]  (to read diffs and git status)
  → Optional components? [README.md]
  → Tags? [git, automation, version-control]
  → Location? Global

Result:
✓ Skill created at ~/.claude/skills/commit-message-helper/
✓ SKILL.md with proper YAML frontmatter
✓ README.md with usage documentation
✓ All validation passed
```

## What Gets Created

When you create a skill, skill-builder generates:

```
~/.claude/skills/your-skill-name/
├── SKILL.md              # Required: Your skill definition
├── README.md             # Optional: Usage documentation
├── references/           # Optional: Examples & extended docs
├── assets/               # Optional: Reusable templates
└── scripts/              # Optional: Helper scripts
```

### SKILL.md Structure

The generated SKILL.md includes:

```yaml
---
name: your-skill-name
description: One-line summary
version: 1.0.0
author: Your Name
tags: [tag1, tag2]
allowed-tools:
  - Tool1
  - Tool2
---

# Your Skill Name: Description

[Template provides structure for:]
- Purpose section
- Workflow steps
- Best practices
- Notes and edge cases
```

## Validation

Skill-builder performs deep validation to ensure quality:

### ✅ YAML Syntax
- Parses frontmatter with Python PyYAML
- Catches indentation errors
- Verifies proper delimiters (`---`)
- Reports line numbers for errors

### ✅ Required Fields
- Checks: name, description, version present
- Validates: name is kebab-case, version is semver (X.Y.Z)
- Warns: if optional recommended fields missing

### ✅ Tool Permissions
- Cross-references against valid Claude Code tools
- Catches typos: suggests corrections (e.g., "bash" → "Bash")
- Validates: all tools are real and properly cased

### ✅ Structure
- Verifies: SKILL.md has content after frontmatter
- Checks: optional directories are populated
- Validates: file permissions are correct

## Valid Tool Names

When selecting tools, use these exact names (case-sensitive):

**File Operations:**
- `Read` - Reading files
- `Write` - Creating new files
- `Edit` - Modifying existing files
- `Glob` - Finding files by pattern
- `Grep` - Searching file contents

**System:**
- `Bash` - Shell commands and system operations

**Interactive:**
- `AskUserQuestion` - Prompting users for input
- `TodoWrite` - Task list management

**Advanced:**
- `WebFetch` - Fetching web content
- `SlashCommand` - Executing slash commands
- `Skill` - Invoking other skills
- `BashOutput` - Reading background shell output
- `KillShell` - Terminating background shells

**Quick Reference:**
```bash
~/.claude/skills/skill-builder/scripts/list-available-tools.sh
```

## Usage Tips

### 1. Keep Skills Focused
✅ Good: `python-test-generator` (one clear purpose)
❌ Bad: `python-helper` (too broad, unclear)

### 2. Choose Descriptive Names
Use pattern: `[domain]-[capability]`
- `react-component-analyzer`
- `api-doc-generator`
- `git-commit-helper`

### 3. Request Minimal Tools
Only tools you'll actually use:
```yaml
# ✅ Minimal and specific
allowed-tools:
  - Read
  - Glob
  - Grep

# ❌ Too many, some unused
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
```

### 4. Include Examples in Your Skill
The SKILL.md content should include concrete examples:
```markdown
## Example Usage

User: "Analyze the auth module"

Your skill should:
1. Use Glob to find auth files: "src/auth/**/*.js"
2. Use Read to examine each file
3. Use Grep to search for security patterns
4. Report findings with file locations
```

### 5. Test Thoroughly
After creating a skill:
1. Restart Claude Code to load it
2. Test with realistic scenarios
3. Refine instructions based on results
4. Update documentation with real examples

## Common Patterns

### Code Analysis Skill
**Tools needed:** Read, Glob, Grep
**Pattern:** Find files → Read content → Analyze → Report

### Documentation Generator
**Tools needed:** Read, Write, Glob
**Pattern:** Read code → Analyze structure → Generate docs → Write files

### Interactive Workflow
**Tools needed:** AskUserQuestion, Read, Write
**Pattern:** Ask questions → Gather input → Process → Deliver results

### Testing Skill
**Tools needed:** Read, Write, Bash
**Pattern:** Read code → Generate tests → Write files → Run tests

## Troubleshooting

### "Skill not found" after creation
**Solution:** Restart Claude Code to reload skills
- Skills are loaded at startup
- Changes require restart to take effect

### YAML validation errors
**Solution:** Check the error message for specific line numbers
- Common issues: missing quotes, wrong indentation, typos
- Use `scripts/validate-yaml.sh` to re-validate
- Review `docs/frontmatter-reference.md` for field requirements

### Skill doesn't behave as expected
**Solution:** Refine the SKILL.md content
- Add more specific instructions
- Include concrete examples
- Break complex workflows into clear steps
- Test with edge cases

### Can't find valid tool names
**Solution:** Run the helper script
```bash
~/.claude/skills/skill-builder/scripts/list-available-tools.sh
```

## Documentation

Comprehensive guides are available:

- **`docs/skill-structure.md`** - Complete anatomy of a skill
- **`docs/frontmatter-reference.md`** - Detailed YAML field reference
- **`docs/best-practices.md`** - Design philosophy and patterns

## Examples

Working examples to learn from:

- **`examples/simple-skill/`** - Minimal hello-world style skill
- Shows basic structure and required elements
- Good starting point for understanding

## Advanced Usage

### Creating Project-Specific Skills
Choose "Project-specific" when asked about location:
- Skill only available in current project
- Stored in `.claude/skills/` (relative to project root)
- Useful for project-specific workflows

### Using the Skill-Builder to Create Meta-Skills
You can use skill-builder to create other skill-builders:
- Select tools: `AskUserQuestion`, `Write`, `Bash`
- Follow the meta-skill pattern
- Recursive bootstrapping!

### Validating Existing Skills
Even if you didn't use skill-builder to create a skill, you can validate it:
```bash
cd ~/.claude/skills/skill-builder/scripts
python3 validate_yaml.py /path/to/SKILL.md
```

### Bulk Validation

Validate all your installed skills at once:

```bash
cd ~/.claude/skills/skill-builder/scripts

# Validate all skills
python3 bulk_validate.py

# Show only errors (hide warnings)
python3 bulk_validate.py --errors-only

# Generate JSON report
python3 bulk_validate.py --format json > report.json
```

**Example output:**
```
╔══════════════════════════════════════════════════════════╗
║     Claude Code Skills - Bulk Validation Report         ║
╚══════════════════════════════════════════════════════════╝

📊 Summary:
   Total Skills: 15
   ✓ Valid: 12 (80%)
   ⚠️  Warnings: 2 (13%)
   ❌ Errors: 1 (7%)

🔴 Critical Issues (1):
   └─ code-analyzer (v1.0.0)
      ❌ Invalid tool: 'bash' should be 'Bash'
      Fix: Use interactive editor or update manually

💡 Recommendations:
   • 3 skill(s) not at v2.0.0 - consider updating with interactive editor
   • Fix 1 critical issue to ensure skill loads correctly
```

**When to use:**
- After installing new skills
- Regular maintenance (monthly check)
- Troubleshooting skill loading issues
- Before system updates
- Preparing skills for sharing

### Interactive Editor (v2.0) 🆕

Edit existing skills interactively with real-time validation:

```bash
cd ~/.claude/skills/skill-builder/scripts

# Edit a skill
~/.claude/skills/skill-builder/.venv/bin/python3 interactive_editor.py ~/.claude/skills/my-skill/
```

**Features:**
- **Edit fields**: name, description, version, author, license, tags, keywords
- **Manage tools**: Add/remove from allowed-tools with validation
- **Real-time validation**: Instant feedback with suggestions
- **Preview changes**: See diff before saving
- **Safe editing**: Automatic backup on save

**Example session:**
```
╔══════════════════════════════════════════════════════════╗
║        Skill Editor: my-skill (v1.2.0)                   ║
╚══════════════════════════════════════════════════════════╝

Current Fields:
  [1] name: my-skill
  [2] description: My skill description
  [3] version: 1.2.0
  [4] allowed-tools: [Bash, Read, Write]

Options:
  [e] Edit field    [t] Manage tools  [v] Validate
  [s] Save          [r] Reload        [q] Quit
```

**When to use:**
- Updating skill metadata or version
- Adding/removing tools
- Fixing validation errors interactively
- Refining existing skills

### Dependency Management (v2.0) 🆕

Manage skill dependencies with version constraints:

```bash
cd ~/.claude/skills/skill-builder/scripts

# Check dependencies for a skill
~/.claude/skills/skill-builder/.venv/bin/python3 dependency_manager.py check my-skill

# Show dependency tree
~/.claude/skills/skill-builder/.venv/bin/python3 dependency_manager.py tree my-skill

# Detect circular dependencies
~/.claude/skills/skill-builder/.venv/bin/python3 dependency_manager.py circular my-skill

# Validate all skills' dependencies
~/.claude/skills/skill-builder/.venv/bin/python3 dependency_manager.py validate --all
```

**Dependency format in SKILL.md:**
```yaml
dependencies:
  - name: skill-builder
    version: ">=1.2.0"
    required: true
  - name: python-analyzer
    version: "^2.0.0"
    required: false
```

**Version constraints:**
- `^1.2.0` - Compatible (>=1.2.0 <2.0.0) - allows minor and patch updates
- `~1.2.0` - Approximately (>=1.2.0 <1.3.0) - allows only patch updates
- `>=1.2.0` - Greater than or equal
- `1.2.0` - Exact version
- `*` - Any version (wildcard)

**Example output:**
```
Dependency Tree:

my-skill (1.0.0)
├─ skill-builder (>=1.2.0) → 2.0.0 ✓
├─ python-analyzer (^2.0.0) → NOT INSTALLED ✗
└─ doc-helper (*) → 1.5.0 ✓ [optional]
```

**When to use:**
- Documenting skill dependencies
- Validating skill installation
- Troubleshooting loading issues
- Building dependency-aware workflows
- Before distributing skills

## Versioning

Skills follow semantic versioning (semver):

- **Major (X.0.0)**: Breaking changes to skill behavior
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes, no new features

When updating your skill:
1. Edit SKILL.md
2. Update version number appropriately
3. Document changes in README.md
4. Restart Claude Code to reload

## What's New in v2.0 🎉

**Interactive Editor:**
- Terminal-based skill editor for refining existing skills
- Real-time validation with inline suggestions
- Field-by-field editing with confirmation dialogs
- Tool management (add/remove from allowed-tools)
- Preview changes before saving with diff view
- Automatic backup on save for safety
- Colorful terminal UI with fallback to standard input

**Dependency Management System:**
- Complete dependency tracking with version constraints
- Semver constraint parsing (^, ~, >=, exact, wildcard)
- Check dependencies for individual skills
- Visualize hierarchical dependency trees
- Detect circular dependencies
- Bulk validation of all skill dependencies
- Smart version resolution with helpful error messages

**Enhanced Infrastructure:**
- Virtual environment with all dependencies pre-installed
- Version resolver with packaging module integration
- Structured validation results with suggestions
- Comprehensive CLI tools for all features

## What's New in v1.2

**Bulk Validation:**
- Validate all skills simultaneously
- Parallel processing for speed
- Multiple report formats (console, JSON)
- Comprehensive error reporting with fixes

**Enhanced Validation:**
- Format version detection
- Updated tool list with latest Claude Code tools
- Improved error messages and suggestions

## Future Enhancements

Planned for v2.1+:

- **Import/Export**: Package and share skills as .skillpkg files
- **GitHub Marketplace**: Discover and install community skills
- **Testing Framework**: Automated testing with assertions
- **Template Library**: Multiple templates for common patterns

## Contributing

Want to improve skill-builder? It's a skill itself:
- Location: `~/.claude/skills/skill-builder/`
- Edit SKILL.md to modify wizard logic
- Add templates to `assets/` directory
- Improve scripts in `scripts/` directory
- Enhance docs in `references/` directory

## Support

Having issues or questions?
- Check the docs/ directory for detailed guides
- Review examples/simple-skill/ for a working reference
- Examine your SKILL.md for common mistakes
- Run validation scripts to diagnose issues

## License

This skill is part of the Claude Code community toolkit.

---

**Ready to create your first skill?**

Just say: "Use the skill-builder skill to create a new skill for [your purpose]"

The wizard will guide you through the rest! ✨
