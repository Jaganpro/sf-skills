# Anatomy of a Claude Code Skill

Complete guide to understanding and creating Claude Code skills.

## Directory Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md              # Required: Core skill definition
├── README.md             # Recommended: Usage documentation
├── references/           # Optional: Examples & extended docs
│   ├── example-1.md
│   └── guide.md
├── assets/               # Optional: Reusable templates
│   └── template.txt
└── scripts/              # Optional: Helper scripts
    └── helper.py
```

## SKILL.md Structure

The SKILL.md file has two parts: **YAML frontmatter** and **skill content**.

### YAML Frontmatter

Metadata between `---` delimiters at the start of the file:

```yaml
---
name: skill-name
description: One-line summary of what this skill does
version: 1.0.0
author: Your Name
tags: [tag1, tag2, tag3]
allowed-tools:
  - Tool1
  - Tool2
dependencies:
  - other-skill
---
```

**Required fields:**
- `name` - Unique identifier (kebab-case)
- `description` - Concise one-sentence summary
- `version` - Semantic version (X.Y.Z)

**Optional fields:**
- `author` - Creator name or organization
- `tags` - Array of categorization keywords
- `allowed-tools` - Array of tool names this skill can use
- `dependencies` - Array of other skills this skill requires

### Skill Content

Instructions for Claude Code after the frontmatter:

```markdown
# Skill Name: Brief Description

You are an expert [role] specializing in [domain]. Your role is to [primary responsibility].

## Core Responsibilities

1. **Primary Function**: Main capability
2. **Secondary Functions**: Supporting capabilities
3. **Output**: What users receive

## Workflow

### Phase 1: [Name]
1. Step one
2. Step two
3. Step three

### Phase 2: [Name]
1. Step one
2. Step two

## Best Practices

- Practice 1
- Practice 2
- Practice 3

## Examples

[Concrete usage examples]

## Notes

[Edge cases, limitations, special considerations]
```

## Field Reference

### name (required)

**Format:** kebab-case (lowercase with hyphens)

**Purpose:** Unique identifier for the skill

**Valid:**
```yaml
name: code-analyzer
name: api-doc-generator
name: git-commit-helper
```

**Invalid:**
```yaml
name: CodeAnalyzer      # Not kebab-case
name: code_analyzer     # Underscores not allowed
name: code analyzer     # Spaces not allowed
```

### description (required)

**Format:** One clear sentence (no period at end)

**Purpose:** Concise summary of skill's function

**Good:**
```yaml
description: Analyzes Python code for common anti-patterns and security issues
description: Generates API documentation from source code comments
description: Creates conventional commit messages based on staged changes
```

**Bad:**
```yaml
description: Helps with code          # Too vague
description: Does analysis.           # Has period
description: Analyzes code. Also does testing and documentation.  # Multiple sentences
```

### version (required)

**Format:** Semantic versioning (MAJOR.MINOR.PATCH)

**Purpose:** Track changes to the skill

**Valid:**
```yaml
version: 1.0.0
version: 2.1.3
version: 0.1.0
```

**Invalid:**
```yaml
version: 1.0         # Missing patch number
version: v1.0.0      # 'v' prefix not allowed
version: 1.0.0-beta  # Pre-release tags not supported yet
```

**Versioning guidelines:**
- **Major (X.0.0)**: Breaking changes to skill behavior
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes, documentation updates

### author (optional)

**Format:** Free-form text

**Purpose:** Attribution

**Examples:**
```yaml
author: Jane Developer
author: Development Team
author: Jane Developer <jane@example.com>
author: Acme Corporation
```

### tags (optional)

**Format:** Array of lowercase keywords

**Purpose:** Categorization and discovery

**Common patterns:**
```yaml
# By type
tags: [code-analysis, documentation, testing, refactoring, generation]

# By domain
tags: [web-dev, data-science, devops, python, javascript, react]

# By purpose
tags: [automation, validation, security, performance]

# Combined
tags: [python, testing, automation]
```

### allowed-tools (optional but recommended)

**Format:** Array of exact tool names (case-sensitive)

**Purpose:** Declare which Claude Code tools the skill can use

**Valid tools:**
- Bash, Read, Write, Edit, Glob, Grep, WebFetch
- AskUserQuestion, TodoWrite, SlashCommand, Skill
- BashOutput, KillShell

**Examples:**
```yaml
# Code analysis skill
allowed-tools:
  - Read
  - Glob
  - Grep

# Documentation generator
allowed-tools:
  - Read
  - Write
  - Glob

# Interactive workflow
allowed-tools:
  - AskUserQuestion
  - Read
  - Write

# System automation
allowed-tools:
  - Bash
  - Read
```

**Important:** Only request tools you'll actually use. Too many tools = security concern.

### dependencies (optional)

**Format:** Array of skill names

**Purpose:** Declare dependencies on other skills

**Example:**
```yaml
dependencies:
  - code-analyzer
  - test-generator
```

## Tool Permissions

Skills must explicitly request tools they need. Claude Code enforces these permissions.

### Available Tools

**File Operations:**
- `Read` - Read file contents
- `Write` - Create new files
- `Edit` - Modify existing files in-place
- `Glob` - Find files by pattern (e.g., `**/*.js`)
- `Grep` - Search file contents with regex

**System:**
- `Bash` - Execute shell commands
- `BashOutput` - Read output from background processes
- `KillShell` - Terminate background processes

**Interactive:**
- `AskUserQuestion` - Prompt user for input
- `TodoWrite` - Manage task lists

**Advanced:**
- `WebFetch` - Fetch web content
- `SlashCommand` - Execute slash commands
- `Skill` - Invoke other skills

### Tool Selection Guidelines

**Principle:** Request minimum tools needed

✅ **Good:**
```yaml
# Code analysis - read-only
allowed-tools:
  - Read
  - Glob
  - Grep
```

❌ **Too many:**
```yaml
# Unnecessarily broad permissions
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
```

## Common Skill Patterns

### Pattern 1: Code Analysis
**Purpose:** Analyze code without modifications

**Tools:** Read, Glob, Grep

**Workflow:**
1. Use Glob to find files
2. Use Read to examine contents
3. Use Grep for pattern matching
4. Report findings

### Pattern 2: File Generation
**Purpose:** Create new files from templates

**Tools:** Read, Write, Glob

**Workflow:**
1. Use Read to load templates
2. Process and populate templates
3. Use Write to create new files

### Pattern 3: Code Transformation
**Purpose:** Modify existing code

**Tools:** Read, Edit, Glob

**Workflow:**
1. Use Glob to find files
2. Use Read to understand code
3. Use Edit to modify in-place

### Pattern 4: Interactive Workflow
**Purpose:** Gather requirements before acting

**Tools:** AskUserQuestion, Read, Write

**Workflow:**
1. Use AskUserQuestion to gather input
2. Process user's requirements
3. Use Read/Write to fulfill request

### Pattern 5: System Automation
**Purpose:** Automate command-line tasks

**Tools:** Bash, Read

**Workflow:**
1. Use Read to understand context
2. Use Bash to execute commands
3. Process and report results

## Best Practices

### 1. Single Responsibility
Each skill should have one clear purpose:

✅ Good:
- `python-test-generator` - Generates Python tests
- `api-doc-writer` - Writes API documentation
- `git-commit-helper` - Helps with commit messages

❌ Too broad:
- `python-helper` - What does it help with?
- `code-tool` - Too vague
- `developer-assistant` - Too many responsibilities

### 2. Clear Instructions
Skill content should be explicit and actionable:

✅ Good:
```markdown
## Workflow
1. Use Glob to find all Python files: "**/*.py"
2. Use Read to examine each file
3. Use Grep to search for "def test_": find existing tests
4. Generate new tests for functions without coverage
```

❌ Vague:
```markdown
## Workflow
1. Find the code
2. Look at it
3. Make tests
```

### 3. Include Examples
Concrete examples help Claude execute correctly:

```markdown
## Example

User: "Analyze the auth module"

You should:
1. Use Glob: "src/auth/**/*.py"
2. Use Read on each file found
3. Check for: SQL injection, XSS, weak passwords
4. Report:
   ```
   ## Security Analysis: auth module

   ### Files Analyzed: 5

   ### Issues Found:
   1. HIGH: SQL injection risk in auth/login.py:45
   2. MEDIUM: Weak password validation in auth/validators.py:12

   ### Recommendations:
   - Use parameterized queries
   - Strengthen password requirements
   ```
```

### 4. Organize with Phases
Break complex workflows into clear phases:

```markdown
### Phase 1: Discovery
- Gather information
- Understand requirements

### Phase 2: Analysis
- Process information
- Make decisions

### Phase 3: Execution
- Take actions
- Generate output

### Phase 4: Validation
- Check results
- Report completion
```

### 5. Handle Edge Cases
Document special situations:

```markdown
## Edge Cases

- **No files found**: Report "No Python files found in specified directory"
- **File too large**: Skip files > 1MB, note in report
- **Permission denied**: Skip file, continue with others
- **Invalid syntax**: Report syntax errors, continue analysis
```

## Skill Locations

Skills can be installed in two locations:

### Global Skills
**Location:** `~/.claude/skills/skill-name/`

**Purpose:** Available in all projects

**Use when:**
- Skill is general-purpose
- Needed across multiple projects
- Personal productivity tool

### Project-Specific Skills
**Location:** `.claude/skills/skill-name/`

**Purpose:** Only available in current project

**Use when:**
- Skill is project-specific
- Contains project conventions
- Part of team workflow

## Skill Loading

1. Claude Code loads skills at startup
2. Finds all SKILL.md files in skill directories
3. Parses YAML frontmatter
4. Makes skills available for invocation
5. **Changes require restart** to take effect

## Validation

Before using a skill, validate it:

```bash
python3 ~/.claude/skills/skill-builder/scripts/validate_yaml.py /path/to/SKILL.md
```

Validation checks:
- ✓ YAML syntax is valid
- ✓ Required fields present
- ✓ Name is kebab-case
- ✓ Version is semver
- ✓ Tools are valid
- ✓ Content exists

## Next Steps

- Review `frontmatter-reference.md` for complete field documentation
- Read `best-practices.md` for design patterns
- Examine `examples/simple-skill/` for working example
- Use `skill-builder` to create your first skill
