# Skill Validation Error Reference

Detailed examples of validation errors and how to fix them.

## YAML Syntax Errors

```
❌ YAML syntax error in SKILL.md:

Line 5: mapping values are not allowed in this context

This usually means:
  - Missing quotes around strings with special characters (: or #)
  - Incorrect indentation (use spaces, not tabs)
  - Unclosed brackets or braces

💡 Fix: Review lines 4-6 in the YAML frontmatter
```

**Common causes:**
- Colons in unquoted strings: `description: Deploy to: production` → use quotes
- Tabs instead of spaces for indentation
- Missing closing brackets in arrays

## Missing Required Fields

```
❌ Validation failed: Missing required field 'description'

Required fields for SKILL.md frontmatter:
  ✓ name: skill-name
  ✗ description: [MISSING]
  ✓ version: 1.0.0

💡 Fix: Add a description field:
---
name: skill-name
description: One-line summary of what this skill does
version: 1.0.0
---
```

**Required fields:**
- `name` - kebab-case identifier
- `description` - one-line summary
- `version` - semver format (X.Y.Z)

## Invalid Tool Names

```
❌ Invalid tools in allowed-tools:

Invalid tools:
  - 'bash' ❌ → Did you mean 'Bash'? (tools are case-sensitive)
  - 'read' ❌ → Did you mean 'Read'?
  - 'FileReader' ❌ → No such tool. Available: Read

💡 Fix: Update allowed-tools with correct tool names (case-sensitive)
```

**Valid tool names (case-sensitive):**
- `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebFetch`
- `AskUserQuestion`, `TodoWrite`, `SlashCommand`, `Skill`
- `BashOutput`, `KillShell`

## Version Format Errors

```
❌ Version format error: 'v1.0' is not valid semver

Version must be: MAJOR.MINOR.PATCH
  - Correct: 1.0.0, 2.1.3, 0.1.0
  - Incorrect: v1.0, 1.0, 2.1

💡 Fix: Change version to '1.0.0'
```

## Name Format Errors

```
❌ Name format error: 'My Skill' is not valid

Name must be kebab-case:
  - Correct: my-skill, code-analyzer, doc-writer
  - Incorrect: My Skill, my_skill, MySkill

💡 Fix: Use lowercase letters, numbers, and hyphens only
```

## Empty Content Error

```
❌ SKILL.md has no content after frontmatter

The skill definition must include instructions after the YAML frontmatter.

💡 Fix: Add skill logic and workflows after the closing ---
```

## Quick Fix Reference

| Error | Common Cause | Quick Fix |
|-------|--------------|-----------|
| YAML syntax | Unquoted special chars | Wrap strings in quotes |
| Missing field | Incomplete frontmatter | Add required field |
| Invalid tool | Wrong case or typo | Use exact tool name |
| Bad version | Missing patch number | Use X.Y.Z format |
| Bad name | Spaces or uppercase | Use kebab-case |
