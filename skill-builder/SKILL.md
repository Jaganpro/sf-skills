---
name: skill-builder
description: >
  Interactive wizard for creating Claude Code skills. Use when scaffolding new
  skills, validating skill structure, managing dependencies, or editing skill
  configuration files.
license: MIT
metadata:
  version: "2.1.0"
  author: "Jag Valaiyapathy"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: Write
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/post-write-validate.py"
          timeout: 10000
---

# Skill-Builder: Claude Code Skill Creation Wizard

Expert skill architect for Claude Code. Help users create well-structured, validated skills through an interactive wizard process.

## Core Responsibilities

1. **Interactive Skill Creation**: Step-by-step wizard to create new skills
2. **Template Application**: Apply minimal-starter template with custom metadata
3. **Deep Validation**: Validate YAML frontmatter, tool permissions, structure
4. **Bulk Validation**: Validate all installed skills with comprehensive reporting
5. **Interactive Editor** (v2.0): Terminal-based editor for refining skills
6. **Dependency Management** (v2.0): Check, validate, visualize skill dependencies
7. **Testing Support**: Verify skills work after creation
8. **Best Practices**: Educate on skill design patterns

## Skill Creation Workflow

### Phase 1: Information Gathering

Use **AskUserQuestion** to collect (in sequence):

| # | Question | Format | Validation |
|---|----------|--------|------------|
| 1 | Skill name | Text | kebab-case required |
| 2 | Description | Text | One clear sentence |
| 3 | Author | Text | Optional |
| 4 | Tools needed | Multi-select | From valid tools list |
| 5 | Optional components | Multi-select | README, examples/, templates/, scripts/, docs/ |
| 6 | Tags | Text | Comma-separated |
| 7 | Location | Choice | Global (~/.claude/skills/) or Project (.claude/skills/) |

**Valid tools**: Bash, Read, Write, Edit, Glob, Grep, WebFetch, AskUserQuestion, TodoWrite, SlashCommand, Skill, BashOutput, KillShell

### Phase 2: Scaffolding

1. **Determine path**: Global → `~/.claude/skills/{name}/` | Project → `.claude/skills/{name}/`
2. **Check existing**: If exists, ask to overwrite
3. **Create structure**:
   ```bash
   mkdir -p {base_path}
   # Create optional dirs based on selection: examples/, templates/, scripts/, docs/
   ```
4. **Load template**:
   - Marketplace: `Read: ~/.claude/plugins/marketplaces/sf-skills/skill-builder/templates/minimal-starter.md`
   - Project: `Read: [project-root]/skill-builder/templates/minimal-starter.md`
5. **Replace placeholders**: {{SKILL_NAME}}, {{SKILL_DESCRIPTION}}, {{VERSION}}, {{AUTHOR}}, {{TAGS}}, {{ALLOWED_TOOLS}}
6. **Write files**: SKILL.md + optional README.md, examples/example-usage.md

### Phase 3: Deep Validation

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_yaml.py {base_path}/SKILL.md
```

**Validation checks**:
- YAML syntax valid
- Required fields: name, description, version
- Name is kebab-case
- Version is semver (X.Y.Z)
- All tools in allowed-tools are valid (case-sensitive)
- SKILL.md has content after frontmatter

If validation fails: Report errors with line numbers and fixes. See `docs/validation-errors.md` (in skill-builder folder) for detailed examples.

### Phase 4: Testing (Optional)

Ask: "Test this skill now?" → Explain restart required, provide invocation example.

### Phase 5: Completion Summary

```
✓ Skill '{name}' created successfully!
📍 Location: {full_path}
📄 Files: SKILL.md [+ README.md, examples/, ...]

Next Steps:
1. Customize SKILL.md with your logic
2. Restart Claude Code to load skill
3. Test: "Use the {name} skill to [task]"

Resources: `docs/skill-structure.md`, `docs/frontmatter-reference.md`, `docs/best-practices.md` (in skill-builder folder)
```

## Validation Errors

| Error | Fix |
|-------|-----|
| YAML syntax | Quote strings with `:` or `#` |
| Missing field | Add required field to frontmatter |
| Invalid tool | Use exact case: `Bash` not `bash` |
| Bad version | Use X.Y.Z format |
| Bad name | Use kebab-case |

See `docs/validation-errors.md` (in skill-builder folder) for details.

## Bulk Validation (v2.0)

When user asks to validate all skills:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/bulk_validate.py [--errors-only] [--format json]
```

**Interpret results**: Total skills, valid count, warnings, errors.
**Guide fixes**: Use interactive editor or manual edits.

See `docs/workflow-examples.md` (in skill-builder folder) for output examples.

## Interactive Editor (v2.0)

For editing existing skills:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/interactive_editor.py /path/to/skill/
```

**Features**: Real-time validation, field editing, tool management, preview changes, auto-backup.

**Commands**: `[e]` Edit field | `[t]` Manage tools | `[v]` Validate | `[s]` Save | `[r]` Reload | `[q]` Quit

See [docs/workflow-examples.md](docs/workflow-examples.md) for UI example.

## Dependency Management (v2.0)

**Dependency syntax** in SKILL.md:
```yaml
dependencies:
  - name: other-skill
    version: ">=1.2.0"  # or ^1.2.0, ~1.2.0, *, exact
    required: true
```

**Version constraints**: `^` (compatible) | `~` (approximate) | `>=` | exact | `*` (any)

**Commands**:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dependency_manager.py check my-skill      # Check deps
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dependency_manager.py tree my-skill       # Visualize tree
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dependency_manager.py circular my-skill   # Detect cycles
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dependency_manager.py validate --all      # Validate all
```

See `docs/workflow-examples.md` (in skill-builder folder) for output examples.

## Patterns & Best Practices

**Skill types**: Code analysis (Glob→Read→Grep→Report) | Documentation (Read→Write) | Interactive (AskUserQuestion→Validate→Execute) | Testing (Bash→Analyze→Report)

**Best practices**: Single responsibility | Clear kebab-case names | Minimal tools | Include examples | Proper semver

## Troubleshooting

| Issue | Check |
|-------|-------|
| Creation fails | Permissions on ~/.claude/skills/, Python 3, disk space |
| Validation fails | YAML syntax, tool case-sensitivity (`Bash` not `bash`) |
| Skill doesn't load | Restart Claude Code, verify path, check frontmatter |

## Notes

- Restart Claude Code after creating skills
- Test with real scenarios
- This meta-skill can create other meta-skills!

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
