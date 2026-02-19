# Hello World Skill

A minimal example skill for learning Claude Code skill structure.

## Purpose

This skill demonstrates the basic anatomy of a Claude Code skill:
- How YAML frontmatter is structured
- What sections belong in SKILL.md
- How tools are declared and used
- Basic workflow organization

## What It Does

When invoked, this skill:
1. Greets the user
2. Explains its own structure
3. Demonstrates tool usage (Bash)
4. Teaches skill fundamentals

## How to Use

```
Use the hello-world-skill
```

Or:

```
Show me how the hello-world-skill works
```

## What You'll Learn

- **YAML Frontmatter Format**: Required and optional fields
- **Skill Content Structure**: Sections and organization
- **Tool Permissions**: How to declare allowed-tools
- **Workflow Patterns**: Phase-based organization
- **Best Practices**: Documentation and clarity

## File Structure

```
simple-skill/
├── SKILL.md     # The skill definition
└── README.md    # This file
```

## Key Concepts Demonstrated

### 1. YAML Frontmatter
```yaml
---
name: hello-world-skill
description: A minimal example skill...
version: 1.0.0
author: Claude Code Team
tags: [example, tutorial, beginner]
allowed-tools:
  - Bash
---
```

### 2. Skill Content Organization
- Core Responsibilities
- Workflow (phases)
- Best Practices
- Examples
- Notes

### 3. Tool Declaration
```yaml
allowed-tools:
  - Bash
```

Only tools listed here can be used by the skill.

## Extending This Example

To create your own skill based on this:

1. **Copy the structure** from SKILL.md
2. **Update YAML frontmatter** with your skill's info
3. **Customize content** for your specific purpose
4. **Add your workflow** steps
5. **Declare needed tools** in allowed-tools
6. **Test thoroughly** with realistic scenarios

## Comparison: Simple vs. Complex Skills

**This skill (simple):**
- One tool (Bash)
- Basic workflow
- Educational purpose
- ~100 lines

**Complex skills might have:**
- Multiple tools (Read, Write, Glob, Grep, etc.)
- Multi-phase workflows
- Validation logic
- Error handling
- ~300-500 lines

Both follow the same basic structure!

## Next Steps

After understanding this example:

1. **Use skill-builder** to create your own skill
2. **Start simple** like this example
3. **Add complexity** as needed
4. **Test and refine** with real use cases

## Tips

- Keep skills focused on one main purpose
- Use clear, descriptive names
- Document workflows thoroughly
- Include concrete examples
- Only request tools you'll actually use

---

This example is part of the skill-builder toolkit. Use it as a reference when creating your own skills!
