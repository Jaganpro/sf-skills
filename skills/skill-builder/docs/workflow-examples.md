# Skill Builder Workflow Examples

Detailed output examples for bulk validation, interactive editor, and dependency management.

## Bulk Validation Output

### All Skills Valid

```
✅ All skills validated successfully!

Summary:
  • 12 skills found
  • 12 valid (100%)
  • No errors or warnings
```

### Issues Found

```
📊 Validation Report:
  • Total: 15 skills
  • Valid: 12 (80%)
  • Warnings: 2 (13%)
  • Errors: 1 (7%)

🔴 Critical Issues:
  • code-analyzer: Invalid tool 'bash' → should be 'Bash'
    Fix: Use interactive editor or update manually

⚠️  Warnings:
  • doc-generator: Missing 'author' field (recommended)
  • api-helper: No examples provided

💡 Recommendations:
  • 3 skill(s) not at v2.0.0 - consider updating with interactive editor
  • Fix 1 critical issue in code-analyzer
  • Review 2 warnings for improvements
```

### Bulk Validation Commands

```bash
# Standard validation
python3 bulk_validate.py

# Errors only (hide warnings)
python3 bulk_validate.py --errors-only

# JSON output
python3 bulk_validate.py --format json > report.json

# Sequential (no parallel)
python3 bulk_validate.py --no-parallel
```

## Interactive Editor UI

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
  [s] Save          [q] Quit
```

### Editor Commands

| Key | Action | Description |
|-----|--------|-------------|
| `e` | Edit field | Edit name, description, version, author, license, tags |
| `t` | Manage tools | Add/remove tools from allowed-tools |
| `v` | Validate | Run comprehensive validation |
| `s` | Save | Preview changes (diff), confirm, backup, write |
| `r` | Reload | Discard changes, reload from file |
| `q` | Quit | Exit editor |

### Launch Editor

```bash
cd ~/.claude/skills/skill-builder/scripts
~/.claude/skills/skill-builder/.venv/bin/python3 interactive_editor.py /path/to/skill/
```

## Dependency Management

### Dependency Syntax

```yaml
dependencies:
  - name: skill-builder
    version: ">=1.2.0"
    required: true
  - name: python-analyzer
    version: "^2.0.0"
    required: false
```

### Version Constraints

| Syntax | Meaning | Example |
|--------|---------|---------|
| `^1.2.0` | Compatible | >=1.2.0 <2.0.0 |
| `~1.2.0` | Approximately | >=1.2.0 <1.3.0 |
| `>=1.2.0` | Greater/equal | Any 1.2.0+ |
| `1.2.0` | Exact | Only 1.2.0 |
| `*` | Any | Wildcard |

### Dependency Tree Output

```
my-skill (1.0.0)
├─ skill-builder (>=1.2.0) → 2.0.0 ✓
├─ python-analyzer (^2.0.0) → NOT INSTALLED ✗
└─ doc-helper (*) → 1.5.0 ✓ [optional]
```

### Dependency Commands

```bash
cd ~/.claude/skills/skill-builder/scripts

# Check specific skill
python3 dependency_manager.py check my-skill

# Visualize dependency tree
python3 dependency_manager.py tree my-skill

# Detect circular dependencies
python3 dependency_manager.py circular my-skill

# Validate all skills
python3 dependency_manager.py validate --all
```

## Skill Creation Completion Summary

```
✓ Skill 'my-skill' created successfully!

📍 Location: ~/.claude/skills/my-skill/

📄 Files created:
  ✓ SKILL.md (skill definition)
  ✓ README.md (documentation)
  ✓ examples/ (example invocations)

🎯 Next Steps:
  1. Customize SKILL.md with your logic
  2. Restart Claude Code to load skill
  3. Test: "Use the my-skill skill to [task]"

📚 Resources:
  - docs/skill-structure.md
  - docs/frontmatter-reference.md
  - docs/best-practices.md
```

## Template Customization Patterns

### Code Analysis Skills
```
Tools: Glob, Read, Grep
Pattern: Find files → Read contents → Search patterns → Report issues
```

### Documentation Skills
```
Tools: Read, Write
Pattern: Read code → Generate docs → Write files
```

### Interactive Workflows
```
Tools: AskUserQuestion, Read, Write
Pattern: Gather input → Validate → Process → Confirm → Execute
```

### Testing Skills
```
Tools: Bash, Read, Write
Pattern: Run tests → Analyze results → Generate report
```
