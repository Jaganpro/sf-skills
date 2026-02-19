# YAML Frontmatter Reference

Complete field-by-field reference for Claude Code SKILL.md frontmatter.

## Overview

YAML frontmatter is metadata at the start of SKILL.md files, delimited by `---`:

```yaml
---
name: skill-name
description: What this skill does
version: 1.0.0
# ... more fields ...
---

# Skill content starts here
```

## Required Fields

### name

**Type:** string
**Format:** kebab-case
**Required:** Yes

**Description:** Unique identifier for the skill. Used to reference and invoke the skill.

**Rules:**
- Must be unique across all installed skills
- Lowercase letters, numbers, hyphens only
- Must start with a letter
- No spaces, underscores, or special characters

**Valid:**
```yaml
name: code-analyzer
name: api-doc-generator
name: git-commit-helper
name: hello-world
name: python3-test-generator
```

**Invalid:**
```yaml
name: CodeAnalyzer       # Not lowercase
name: code_analyzer      # Underscores not allowed
name: code analyzer      # Spaces not allowed
name: codeAnalyzer       # camelCase not allowed
name: 123-analyzer       # Can't start with number
```

---

### description

**Type:** string
**Format:** One sentence, no trailing period
**Required:** Yes

**Description:** Concise summary of what the skill does. Shows in skill listings and helps Claude decide when to use the skill.

**Rules:**
- One sentence only
- Focus on WHAT the skill does, not HOW
- Be specific, avoid generic terms
- No period at end (convention)
- Keep under 100 characters
- Start with a verb when possible

**Good:**
```yaml
description: Analyzes Python code for common anti-patterns and security vulnerabilities
description: Generates comprehensive API documentation from source code comments
description: Creates conventional commit messages based on staged git changes
description: Refactors JavaScript code to use modern ES6+ syntax
```

**Bad:**
```yaml
description: Helps with code.                    # Too vague
description: Analyzes code. Also helps test it.  # Multiple sentences
description: A tool for analyzing Python code for anti-patterns, security issues, and more.  # Too long
description: Code analyzer                       # Too brief, not descriptive
```

---

### version

**Type:** string
**Format:** Semantic versioning (MAJOR.MINOR.PATCH)
**Required:** Yes

**Description:** Version number following semver conventions. Used to track changes and compatibility.

**Rules:**
- Must be three numbers separated by dots
- Format: `MAJOR.MINOR.PATCH`
- No 'v' prefix
- No pre-release tags (yet)
- Start new skills at `1.0.0`

**Versioning Guidelines:**
- **Major (X.0.0)**: Breaking changes to skill behavior or interface
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes, documentation updates, no new features

**Valid:**
```yaml
version: 1.0.0
version: 2.1.3
version: 0.1.0
version: 10.0.5
```

**Invalid:**
```yaml
version: 1.0           # Missing patch number
version: v1.0.0        # 'v' prefix not allowed
version: 1.0.0-beta    # Pre-release tags not supported
version: 1.0.0.1       # Too many numbers
version: "1.0.0"       # Quotes unnecessary (but not wrong)
```

---

## Optional Fields

### author

**Type:** string
**Format:** Free-form text
**Required:** No

**Description:** Person, team, or organization that created the skill. Used for attribution and contact.

**Examples:**
```yaml
author: Jane Developer
author: Platform Team
author: Jane Developer <jane@example.com>
author: Acme Corporation
author: @janedeveloper
```

**Tips:**
- Include email for contact
- Use consistent format across your skills
- Optional but recommended for shared skills

---

### tags

**Type:** array of strings
**Format:** Lowercase keywords
**Required:** No

**Description:** Keywords for categorization, search, and discovery. Helps users find relevant skills.

**Format Options:**
```yaml
# Inline array
tags: [python, testing, automation]

# Multiline array
tags:
  - python
  - testing
  - automation
```

**Category Patterns:**

**By Type:**
```yaml
tags: [code-analysis, documentation, testing, refactoring, generation, validation]
```

**By Domain:**
```yaml
tags: [web-dev, data-science, devops, mobile, backend, frontend]
```

**By Technology:**
```yaml
tags: [python, javascript, react, typescript, go, rust, java]
```

**By Purpose:**
```yaml
tags: [automation, security, performance, quality, productivity]
```

**Combined:**
```yaml
tags: [python, testing, automation, backend]
```

**Tips:**
- Use 3-7 tags
- Be specific: `react` not just `javascript`
- Include both type and domain tags
- Consistent lowercase
- No spaces in individual tags

---

### allowed-tools

**Type:** array of strings
**Format:** Exact tool names (case-sensitive)
**Required:** No (but highly recommended)

**Description:** Tools this skill is permitted to use. Claude Code enforces these permissions for security.

**Valid Tool Names:**

**File Operations:**
- `Read` - Reading file contents
- `Write` - Creating new files
- `Edit` - Modifying existing files
- `Glob` - Finding files by pattern
- `Grep` - Searching file contents with regex

**System:**
- `Bash` - Executing shell commands
- `BashOutput` - Reading background shell output
- `KillShell` - Terminating background shells

**Interactive:**
- `AskUserQuestion` - Prompting user for input
- `TodoWrite` - Managing task lists

**Advanced:**
- `WebFetch` - Fetching web content
- `SlashCommand` - Executing slash commands
- `Skill` - Invoking other skills

**Format Options:**
```yaml
# Inline (for 1-2 tools)
allowed-tools: [Read, Write]

# Multiline (preferred for 3+ tools)
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
```

**Examples by Use Case:**

**Code Analysis (read-only):**
```yaml
allowed-tools:
  - Read
  - Glob
  - Grep
```

**Documentation Generation:**
```yaml
allowed-tools:
  - Read
  - Write
  - Glob
```

**Code Refactoring:**
```yaml
allowed-tools:
  - Read
  - Edit
  - Glob
```

**Interactive Workflow:**
```yaml
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
```

**System Automation:**
```yaml
allowed-tools:
  - Bash
  - Read
```

**Meta-Skill (skill that creates things):**
```yaml
allowed-tools:
  - AskUserQuestion
  - Write
  - Bash
```

**Common Mistakes:**
```yaml
# ❌ Wrong case
allowed-tools:
  - bash        # Should be "Bash"
  - read        # Should be "Read"

# ❌ Invalid tool names
allowed-tools:
  - FileRead    # Should be "Read"
  - Execute     # Should be "Bash"

# ❌ Too many tools
allowed-tools:  # Only request what you'll use
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - AskUserQuestion
  - TodoWrite
```

**Guidelines:**
- Only request tools you'll actually use
- Fewer tools = better security
- Case-sensitive: must match exactly
- Alphabetical order (optional but nice)

---

### dependencies

**Type:** array of strings
**Format:** Skill names (kebab-case)
**Required:** No

**Description:** Other skills that this skill requires or invokes. Declares dependencies for documentation and validation.

**Format:**
```yaml
# Single dependency
dependencies: [code-analyzer]

# Multiple dependencies
dependencies:
  - code-analyzer
  - test-generator
  - doc-writer
```

**Use Cases:**
- Skill invokes other skills using `Skill` tool
- Skill extends another skill's functionality
- Skill relies on output from another skill

**Example:**
```yaml
name: comprehensive-code-review
description: Performs analysis, generates tests, and creates documentation
version: 1.0.0
allowed-tools:
  - Skill
  - Write
dependencies:
  - code-analyzer      # For code analysis
  - test-generator     # For test creation
  - doc-writer         # For documentation
```

**Notes:**
- Dependencies must be installed
- Avoid circular dependencies
- List only direct dependencies

---

### examples

**Type:** array of strings
**Format:** Example invocation prompts
**Required:** No

**Description:** Example prompts showing how to invoke the skill. Helpful for documentation and discoverability.

**Format:**
```yaml
examples:
  - "Analyze the authentication module for security issues"
  - "Check all API endpoints for consistency"
  - "Review the database models for optimization opportunities"
```

**Guidelines:**
- Write as natural language prompts
- Show diverse use cases
- Include 2-5 examples
- Be specific, not generic
- Start with verbs

**Good:**
```yaml
examples:
  - "Generate API documentation for the user service"
  - "Create JSDoc comments for all public functions in utils.js"
  - "Document the REST endpoints in the api/ directory"
```

**Bad:**
```yaml
examples:
  - "Use this skill"               # Too vague
  - "api-doc-generator"            # Not a natural prompt
  - "This skill generates docs"    # Describes, doesn't demonstrate
```

---

## Complete Example

```yaml
---
name: python-security-analyzer
description: Analyzes Python code for security vulnerabilities and common anti-patterns
version: 1.2.0
author: Security Team <security@example.com>
tags: [python, security, code-analysis, automation]
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
dependencies:
  - code-analyzer
examples:
  - "Analyze the auth module for security vulnerabilities"
  - "Check all Python files for SQL injection risks"
  - "Review the API handlers for XSS vulnerabilities"
---
```

## Validation

All frontmatter fields are validated when skills are created using skill-builder.

### Validation Checks:

**Required Fields:**
- ✓ `name` is present and kebab-case
- ✓ `description` is present and concise
- ✓ `version` is present and valid semver

**Optional Fields:**
- ✓ `allowed-tools` contains only valid tool names (case-sensitive)
- ✓ `dependencies` reference existing skills
- ✓ `tags` are lowercase and reasonable

**Syntax:**
- ✓ YAML parses without errors
- ✓ Frontmatter delimited by `---`
- ✓ No typos in field names

### Validation Tool:

```bash
python3 ~/.claude/skills/skill-builder/scripts/validate_yaml.py /path/to/SKILL.md
```

## Common Mistakes

### 1. Field Name Typos
```yaml
---
name: my-skill
descripton: Wrong field name!     # ❌ "descripton"
version: 1.0.0
---
```

### 2. Wrong Case in Tools
```yaml
---
allowed-tools:
  - bash      # ❌ Should be "Bash"
  - Read      # ✓ Correct
---
```

### 3. Invalid Version Format
```yaml
---
version: 1.0       # ❌ Missing patch number
version: v1.0.0    # ❌ 'v' prefix
version: 1.0.0     # ✓ Correct
---
```

### 4. Non-kebab-case Name
```yaml
---
name: mySkill       # ❌ camelCase
name: my_skill      # ❌ underscores
name: my-skill      # ✓ Correct
---
```

### 5. Description Too Long or Multiple Sentences
```yaml
---
description: This skill analyzes code. It also generates tests.  # ❌ Multiple sentences
description: Analyzes code and generates tests                   # ✓ One sentence
---
```

## Tips

1. **Start Simple**: Begin with minimal frontmatter, add fields as needed
2. **Validate Early**: Use validation tool to catch errors
3. **Be Consistent**: Use same format across all your skills
4. **Document Well**: Include author, tags, examples for shared skills
5. **Minimal Tools**: Only request tools you'll actually use
6. **Version Properly**: Follow semver conventions for versioning

## Next Steps

- Read `skill-structure.md` for complete skill anatomy
- Review `best-practices.md` for design patterns
- Use skill-builder to create validated skills
- Examine `examples/simple-skill/` for working example
