# Claude Code Skill Design Best Practices

Comprehensive guide to designing effective, maintainable, and secure skills.

## Design Philosophy

### Single Responsibility Principle

Each skill should do one thing well.

**✅ Good - Focused Skills:**
```
code-analyzer         → Analyzes code quality
test-generator        → Generates tests
doc-writer            → Writes documentation
commit-helper         → Helps with commits
```

**❌ Bad - Too Broad:**
```
code-helper          → What does it help with?
developer-tool       → Too vague
swiss-army-knife     → Does everything (poorly)
```

**Why?**
- Easier to maintain
- Clearer expectations
- Better reusability
- Simpler testing

### Composability Over Monoliths

Build small skills that work together:

**✅ Good - Composable:**
```yaml
# skill: code-analyzer
- Analyzes code, reports issues

# skill: code-fixer
- Takes analysis results, applies fixes
- Uses: Skill (invokes code-analyzer)

# skill: code-review
- Orchestrates full review workflow
- Uses: Skill (invokes code-analyzer and code-fixer)
```

**❌ Bad - Monolithic:**
```yaml
# skill: do-everything
- Analyzes, fixes, tests, documents, deploys...
- Impossible to maintain
```

## Naming Conventions

### Pattern: [domain]-[capability]

**Format:** kebab-case
**Structure:** `<domain>-<action>` or `<domain>-<noun>`

**Good Examples:**
```
python-test-generator
react-component-analyzer
api-doc-writer
git-commit-helper
sql-query-optimizer
dockerfile-validator
```

**Bad Examples:**
```
pytestgen              → Unclear abbreviation
helper                 → Too generic
codeAnalyzer           → Wrong case
my_tool                → Underscores, too generic
```

### Be Specific, Not Generic

**✅ Specific:**
```
react-hook-validator
typescript-interface-generator
kubernetes-manifest-validator
```

**❌ Generic:**
```
validator
generator
helper
tool
utility
```

### Avoid Acronyms

**✅ Spell Out:**
```
api-doc-generator
continuous-integration-helper
pull-request-reviewer
```

**❌ Acronyms:**
```
adg
ci-helper
prr
```

Exception: Well-known acronyms (api, sql, html, css)

## Tool Selection

### Principle: Least Privilege

Only request tools you'll actually use.

**✅ Minimal & Specific:**
```yaml
# Code analysis (read-only)
allowed-tools:
  - Read
  - Glob
  - Grep
```

**❌ Too Many:**
```yaml
# "Just in case" approach
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - AskUserQuestion
```

### Tool Patterns by Use Case

**1. Code Analysis (Read-Only):**
```yaml
allowed-tools:
  - Read      # Examine files
  - Glob      # Find files by pattern
  - Grep      # Search for patterns
```

**2. File Generation:**
```yaml
allowed-tools:
  - Read      # Load templates
  - Write     # Create new files
  - Glob      # Find templates
```

**3. Code Refactoring:**
```yaml
allowed-tools:
  - Read      # Understand code
  - Edit      # Modify in-place
  - Glob      # Find files to refactor
```

**4. Interactive Workflows:**
```yaml
allowed-tools:
  - AskUserQuestion    # Gather requirements
  - Read               # Process input
  - Write              # Generate output
```

**5. System Automation:**
```yaml
allowed-tools:
  - Bash      # Run commands
  - Read      # Check files
```

**6. Meta-Skills (Create Things):**
```yaml
allowed-tools:
  - AskUserQuestion    # Interactive wizard
  - Write              # Create files
  - Bash               # File operations
```

### Security Considerations

**Bash Tool - Use Carefully:**
- Can execute arbitrary commands
- Validate inputs
- Avoid user-controlled command strings
- Document what commands you'll run

**Write/Edit Tools - Validate Paths:**
- Check file paths before writing
- Avoid overwriting critical files
- Confirm destructive operations
- Use project-relative paths when possible

## Skill Content Structure

### Recommended Template

```markdown
# [Skill Name]: [Brief Purpose]

You are an expert [role] specializing in [domain]. Your role is to [primary task].

## Core Responsibilities

1. **Primary Function**: Main capability
2. **Supporting Functions**: Additional capabilities
3. **Output**: What users receive

## Workflow

### Phase 1: [Understanding/Discovery/Preparation]
1. Concrete step
2. Concrete step
3. Concrete step

### Phase 2: [Analysis/Processing/Execution]
1. Concrete step
2. Concrete step

### Phase 3: [Delivery/Reporting/Completion]
1. Concrete step
2. Concrete step

## Best Practices

When executing this skill:
- Specific guideline 1
- Specific guideline 2
- Specific guideline 3

## Examples

### Example 1: [Common Use Case]
\```
User: "[Realistic request]"

You should:
1. [Specific action with tool]
2. [Specific action with tool]
3. [Expected output]
\```

## Tool Usage

[Explain how you use each tool and why]

## Edge Cases

- **Situation 1**: How to handle
- **Situation 2**: How to handle

## Output Format

[Template or example of typical output]

## Notes

- Important considerations
- Limitations
- Prerequisites
```

### Be Explicit, Not Vague

**✅ Explicit:**
```markdown
## Workflow

### Phase 1: Find Python Files
1. Use Glob with pattern: "**/*.py"
2. Exclude: "**/test_*.py", "**/__pycache__/**"
3. Sort results alphabetically

### Phase 2: Analyze Each File
1. Use Read to load file contents
2. Use Grep to find functions: pattern "^def "
3. For each function:
   - Check docstring presence
   - Verify type hints
   - Count lines (complexity)

### Phase 3: Generate Report
1. Format as markdown table
2. Include: file, function, issues, severity
3. Sort by severity: high → medium → low
4. Add summary statistics
```

**❌ Vague:**
```markdown
## Workflow

1. Find the files
2. Look at them
3. Find problems
4. Tell the user
```

### Include Concrete Examples

**✅ Good Examples:**
```markdown
## Example: Analyzing Auth Module

User: "Analyze the auth module for security issues"

You should:

1. **Find auth files:**
   - Use Glob: "src/auth/**/*.py"
   - Expected: auth/login.py, auth/validators.py, auth/tokens.py

2. **Analyze each file:**
   - Use Read to load contents
   - Use Grep to find patterns:
     * SQL queries: "SELECT .* FROM"
     * Password handling: "password"
     * Token generation: "jwt|token"

3. **Check for issues:**
   - SQL injection: Raw SQL with string formatting
   - Weak passwords: Length < 8, no complexity
   - Token security: Weak secrets, no expiration

4. **Report findings:**
   \```
   ## Security Analysis: auth module

   ### Files Analyzed: 3
   - auth/login.py
   - auth/validators.py
   - auth/tokens.py

   ### Issues Found: 2

   1. **HIGH**: SQL Injection Risk
      - File: auth/login.py:45
      - Code: `f"SELECT * FROM users WHERE email='{email}'"`
      - Fix: Use parameterized queries

   2. **MEDIUM**: Weak Password Requirements
      - File: auth/validators.py:12
      - Issue: Minimum length is 6 characters
      - Recommendation: Increase to 12, require complexity

   ### Summary:
   - 1 high severity issue (immediate action required)
   - 1 medium severity issue (should address soon)
   \```
```

## Documentation

### README.md Essentials

Every skill should have a README.md:

```markdown
# [Skill Name]

[One paragraph description]

## What It Does

[2-3 sentences explaining capabilities]

## How to Use

\```
[Example invocations]
\```

## Examples

[Concrete examples with input/output]

## Requirements

[Prerequisites, dependencies]

## Tips

[Usage tips, gotchas, best practices]
```

### When to Add References Directory

Add `references/` when:
- Skill has multiple usage modes
- Output format needs demonstration
- Common patterns should be shown
- Skill is complex or novel
- Extended documentation needed

### When to Add Assets Directory

Add `assets/` when:
- Skill generates files from templates
- Multiple output formats supported
- Reusable boilerplate provided

### When to Add Scripts Directory

Add `scripts/` when:
- Helper scripts simplify skill logic
- External validation needed
- Command-line utilities support skill

## Versioning Strategy

Follow semantic versioning (semver):

### Version Format: MAJOR.MINOR.PATCH

**MAJOR (X.0.0)** - Breaking changes:
- Changed skill behavior incompatibly
- Removed functionality
- Changed output format significantly
- Changed tool requirements substantially

**MINOR (1.X.0)** - New features (backward compatible):
- Added new capabilities
- Added optional parameters
- Enhanced existing features
- Added new tool permissions

**PATCH (1.0.X)** - Bug fixes:
- Fixed incorrect behavior
- Improved error messages
- Updated documentation
- Performance improvements

### Examples:

```
1.0.0 → 1.0.1   (Fixed bug in file parsing)
1.0.1 → 1.1.0   (Added support for TypeScript files)
1.1.0 → 2.0.0   (Changed output format from JSON to markdown)
```

### When to Bump Version:

```
Changed allowed-tools?              → MAJOR
Added new workflow phase?           → MINOR
Fixed typo in output?               → PATCH
Improved documentation?             → PATCH
Added new file type support?        → MINOR
Changed how results are formatted?  → MAJOR
Optimized performance?              → PATCH
Added optional feature?             → MINOR
```

## Testing Strategy

### Before Release:

1. **Unit Testing**: Does skill respond to direct invocation?
2. **Integration Testing**: Works with other skills?
3. **Edge Cases**: Handles errors gracefully?
4. **Performance**: Efficient with large inputs?

### Test Cases to Consider:

**Happy Path:**
- Normal, expected usage
- Typical input sizes
- Standard scenarios

**Edge Cases:**
- Empty input
- Very large input
- Missing files
- Permission denied
- Invalid syntax
- Network failures (for WebFetch)

**Error Handling:**
- Graceful failures
- Clear error messages
- Partial results when possible
- No silent failures

## Common Patterns

### Pattern: Progressive Disclosure

Start simple, add complexity as needed:

**Version 1.0.0 - Minimal:**
```yaml
name: code-analyzer
description: Analyzes Python code for issues
allowed-tools: [Read, Glob]
# Basic analysis only
```

**Version 1.1.0 - Enhanced:**
```yaml
name: code-analyzer
description: Analyzes Python code for issues
allowed-tools: [Read, Glob, Grep]
# Added pattern matching
```

**Version 2.0.0 - Comprehensive:**
```yaml
name: code-analyzer
description: Analyzes Python code for issues with auto-fix suggestions
allowed-tools: [Read, Glob, Grep, Edit]
# Added auto-fix capability (breaking change: new tool)
```

### Pattern: Configuration via AskUserQuestion

For flexible workflows:

```yaml
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
```

```markdown
## Workflow

### Phase 1: Gather Configuration
1. Use AskUserQuestion: "Which file types?" → user selects
2. Use AskUserQuestion: "Severity level?" → user chooses
3. Use AskUserQuestion: "Output format?" → user picks

### Phase 2: Execute Based on Configuration
[Use gathered config to customize behavior]
```

### Pattern: Skill Composition

Skills invoking other skills:

```yaml
name: comprehensive-review
description: Full code review with analysis, testing, and documentation
allowed-tools:
  - Skill
  - Write
dependencies:
  - code-analyzer
  - test-generator
  - doc-writer
```

```markdown
## Workflow

### Phase 1: Analysis
1. Use Skill to invoke: code-analyzer
2. Collect analysis results

### Phase 2: Testing
1. Use Skill to invoke: test-generator
2. Generate tests for uncovered code

### Phase 3: Documentation
1. Use Skill to invoke: doc-writer
2. Generate docs for undocumented code

### Phase 4: Summary Report
1. Compile all results
2. Use Write to create comprehensive report
```

## Performance Tips

### 1. Use Glob Efficiently

**✅ Specific patterns:**
```
**/*.py           → All Python files
src/**/*.js       → JavaScript in src only
tests/**/test_*.py → Test files only
```

**❌ Too broad:**
```
**/*              → Everything (slow)
```

### 2. Batch Operations

**✅ Batch reads:**
```markdown
1. Use Glob to collect all file paths
2. Read files in logical groups
3. Process batch before moving to next
```

**❌ One at a time:**
```markdown
1. Find file
2. Read file
3. Process file
4. Repeat (inefficient)
```

### 3. Early Exit

**✅ Stop when done:**
```markdown
1. Search for critical issue
2. If found: report immediately, exit
3. Don't continue unnecessary work
```

### 4. Avoid Redundant Reads

**✅ Cache results:**
```markdown
1. Read file once
2. Store relevant data
3. Reuse for multiple checks
```

**❌ Re-read multiple times:**
```markdown
1. Read file for check 1
2. Read same file for check 2
3. Read same file for check 3
```

## Security Best Practices

### 1. Validate Inputs

When using Bash or Write:
```markdown
## Before executing:
1. Validate file paths (no ../../../etc/passwd)
2. Sanitize user inputs
3. Check file extensions
4. Verify permissions
```

### 2. Least Privilege

```yaml
# ✅ Only what's needed
allowed-tools:
  - Read
  - Glob

# ❌ "Just in case"
allowed-tools:
  - Bash  # Can execute anything!
  - Write # Can create files anywhere!
  - Edit  # Can modify anything!
```

### 3. Document Security Implications

```markdown
## Security Notes

This skill uses Bash to:
- Run `git status` (read-only, safe)
- Run `git diff` (read-only, safe)
- Does NOT run: git push, git commit, rm, etc.

This skill uses Write to:
- Create files in `.claude/generated/` only
- Does NOT write to: system directories, user files
```

## Maintenance

### Regular Reviews

**Quarterly:**
- Update documentation
- Review for outdated patterns
- Check tool usage is current
- Update examples

**On Claude Code Updates:**
- Check if new tools available
- Verify existing tools still work
- Update allowed-tools if beneficial

### Deprecation

If deprecating a skill:

1. **Mark in README:**
   ```markdown
   # ⚠️ DEPRECATED

   This skill is deprecated. Use `new-skill` instead.

   **Migration Guide:**
   - Old: `use old-skill for X`
   - New: `use new-skill for X`
   ```

2. **Update version:**
   ```yaml
   version: 2.1.0-deprecated
   ```

3. **Keep functional during transition**

4. **Remove after sufficient notice** (e.g., 3 months)

## Anti-Patterns to Avoid

### ❌ Swiss Army Knife
```yaml
name: developer-helper
description: Helps with everything
# TOO BROAD - split into focused skills
```

### ❌ Unclear Naming
```yaml
name: helper
description: Helps with stuff
# VAGUE - be specific
```

### ❌ Too Many Tools
```yaml
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - AskUserQuestion
  - TodoWrite
# EXCESSIVE - use only what you need
```

### ❌ Vague Instructions
```markdown
## Workflow
1. Look at the code
2. Find problems
3. Tell user
# NOT ACTIONABLE - be explicit
```

### ❌ No Examples
```markdown
# Just theory, no concrete examples
# ADD EXAMPLES - show don't tell
```

## Checklist for Quality Skills

Before releasing a skill:

- [ ] Name is descriptive kebab-case
- [ ] Description is one clear sentence
- [ ] Version follows semver
- [ ] Only necessary tools requested
- [ ] Workflow is explicit and detailed
- [ ] Concrete examples included
- [ ] Edge cases documented
- [ ] Error handling specified
- [ ] README.md explains usage
- [ ] Validated with validation script
- [ ] Tested with realistic scenarios
- [ ] Security implications documented

## Next Steps

- Review `skill-structure.md` for anatomy reference
- Read `frontmatter-reference.md` for field details
- Examine `examples/simple-skill/` for working code
- Use skill-builder to create validated skills
- Start simple, iterate based on usage
