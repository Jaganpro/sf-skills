---
name: simple-skill
description: A minimal example skill demonstrating Claude Code skill structure
license: MIT
metadata:
  version: "1.0.0"
  author: "Claude Code Team"
  tags: "example, tutorial, beginner"
allowed-tools: Bash
---

# Hello World Skill: A Minimal Example

You are demonstrating how Claude Code skills work through this simple example skill.

## Core Responsibilities

1. **Greet User**: Provide a friendly welcome message
2. **Explain Structure**: Show what makes up a skill
3. **Educate**: Help users understand skill components

## Workflow

When a user invokes this skill:

### Phase 1: Greeting
1. Welcome the user warmly
2. Introduce this skill's purpose
3. Set expectations for what they'll learn

### Phase 2: Explanation
1. Explain the SKILL.md structure
2. Describe the YAML frontmatter
3. Show how content is organized
4. Demonstrate tool usage (Bash in this case)

### Phase 3: Demonstration
1. Use the Bash tool to show system information
2. Display the output in a friendly format
3. Explain what just happened

## Best Practices

This example demonstrates:

- **Clear Structure**: Organized into logical sections
- **YAML Frontmatter**: Proper metadata format
- **Tool Declaration**: Explicitly listing allowed tools
- **Workflow Pattern**: Phase-based organization
- **Documentation**: Comments and explanations

## Example Invocation

```
User: "Use the simple-skill"

Response:
👋 Hello! I'm the simple-skill, a minimal example demonstrating Claude Code skill structure.

I'm here to show you how skills work:

1. **SKILL.md File**: Every skill has a SKILL.md file
   - YAML frontmatter (between ---) defines metadata
   - Content below provides instructions for Claude

2. **YAML Frontmatter**: Contains key information
   - name: Unique identifier (kebab-case)
   - description: One-line summary
   - version: Semantic version (X.Y.Z)
   - tags: Categorization keywords
   - allowed-tools: Tools this skill can use

3. **Skill Content**: Instructions for Claude
   - Core Responsibilities: What the skill does
   - Workflow: Step-by-step process
   - Best Practices: Guidelines for execution
   - Examples: Usage demonstrations

Let me demonstrate using the Bash tool I have access to:

[Runs: date]
Current time: [output]

That's the simple-skill! It's intentionally simple to show the basic structure.
Real skills are more sophisticated but follow the same pattern.
```

## Tool Usage

This skill demonstrates Bash tool usage:
- `Bash` allows running system commands
- Used here to show current date/time
- Real skills use tools for their specific purposes

## Notes

- This is a learning example, not a production skill
- Real skills would have more complex logic
- The pattern scales from simple to sophisticated
- Start simple, add complexity as needed

## What Makes This Skill Work

1. **Valid YAML frontmatter**: Properly formatted metadata
2. **Clear instructions**: Specific guidance for Claude
3. **Tool permissions**: Explicit allowed-tools list
4. **Organized structure**: Logical sections and flow

## Learning Points

**From this example, you can learn:**

- How to structure YAML frontmatter
- What sections to include in skill content
- How to declare tool permissions
- How to organize workflows
- Best practices for documentation

**To create your own skill:**
1. Use the skill-builder to scaffold the structure
2. Customize the template for your purpose
3. Test with realistic scenarios
4. Refine based on results

**Remember:** This simple-skill is intentionally minimal. Your skills can be much more sophisticated while following this same basic pattern!
