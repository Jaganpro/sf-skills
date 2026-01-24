# Shared Hooks Architecture

This directory contains the centralized hook system for sf-skills, providing intelligent skill discovery, guardrails, and orchestration across all 18 Salesforce skills.

## Overview

```
shared/hooks/
├── skills-registry.json         # Single source of truth for all skill metadata
├── skill-activation-prompt.py   # UserPromptSubmit hook (pre-prompt suggestions)
├── suggest-related-skills.py    # PostToolUse hook (post-action suggestions)
├── scripts/
│   ├── guardrails.py            # PreToolUse hook (block/auto-fix dangerous operations)
│   ├── chain-validator.py       # SubagentStop hook (workflow chain validation)
│   ├── auto-approve.py          # PermissionRequest hook (smart auto-approval)
│   └── llm-eval.py              # LLM-powered semantic evaluation (Haiku)
└── README.md                    # This file
```

## Architecture v4.0.0

### Proactive vs Reactive Hooks

The modernized architecture shifts from **reactive** (catch issues after) to **proactive** (prevent before + auto-fix):

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PROACTIVE LAYER (NEW)                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  User Request → PreToolUse Hook → Block or Modify → Tool Executes       │
│                       ↓                                                 │
│                 guardrails.py                                           │
│                       ↓                                                 │
│        ┌─────────────────────────────────┐                              │
│        │ CRITICAL: Block dangerous DML   │                              │
│        │ HIGH: Auto-fix unbounded SOQL   │                              │
│        │ MEDIUM: Warn on hardcoded IDs   │                              │
│        └─────────────────────────────────┘                              │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ REACTIVE LAYER (ENHANCED)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tool Executes → PostToolUse Hook → Validate → Suggest Next Steps       │
│                        ↓                  ↓                             │
│              skill-specific      suggest-related-skills.py              │
│               validators                                                │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ ORCHESTRATION LAYER (NEW)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Subagent Completes → SubagentStop Hook → Chain Validation              │
│                              ↓                                          │
│                     chain-validator.py                                  │
│                              ↓                                          │
│             "Step 2 of 7 complete. Next: sf-flow"                       │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ PERMISSION LAYER (NEW)                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Permission Request → PermissionRequest Hook → Auto-approve or Confirm  │
│                              ↓                                          │
│                       auto-approve.py                                   │
│                              ↓                                          │
│        ┌─────────────────────────────────────────────────┐              │
│        │ Read operations → Auto-approve                  │              │
│        │ Scratch org deploys → Auto-approve              │              │
│        │ Production deploys → Require confirmation       │              │
│        └─────────────────────────────────────────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Hook Types

### 1. PreToolUse (Guardrails)

**Purpose:** Block dangerous operations before execution, or auto-fix common issues.

**Location:** `scripts/guardrails.py`

**Severity Levels:**

| Severity | Action | Examples |
|----------|--------|----------|
| CRITICAL | Block | DELETE without WHERE, UPDATE without WHERE, hardcoded credentials |
| HIGH | Auto-fix | Unbounded SOQL → add LIMIT, production deploy → add --dry-run |
| MEDIUM | Warn | Hardcoded Salesforce IDs, deprecated API usage |

**How it works:**
```python
# Returns JSON to block or modify tool input
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",        # or "allow"
    "permissionDecisionReason": "DELETE without WHERE detected",
    "updatedInput": {                    # For auto-fix (optional)
      "command": "sf data query --query 'SELECT Id FROM Account LIMIT 200'"
    }
  }
}
```

### 2. PostToolUse (Validation + Suggestions)

**Purpose:** Validate tool output and suggest next workflow steps.

**Components:**
- **Skill-specific validators:** Located in each skill's `hooks/scripts/` directory
- **suggest-related-skills.py:** Shared script for workflow suggestions

### 3. SubagentStop (Chain Validation)

**Purpose:** Validate subagents follow orchestration chains, track progress, suggest next skill.

**Location:** `scripts/chain-validator.py`

**Output Example:**
```
══════════════════════════════════════════════════════
🔗 CHAIN VALIDATION (sf-apex completed)
══════════════════════════════════════════════════════

📋 WORKFLOW: full_feature
   Step 2 of 7 complete
   Progress: sf-metadata ✓ → sf-apex ✓ → sf-flow (next)

➡️ NEXT: /sf-testing *** REQUIRED
   └─ Run tests to validate Apex code
══════════════════════════════════════════════════════
```

### 4. PermissionRequest (Auto-Approval)

**Purpose:** Automatically approve safe operations, require confirmation for risky ones.

**Location:** `scripts/auto-approve.py`

**Policy Matrix:**

| Operation | Org Type | Decision |
|-----------|----------|----------|
| Read operations (query, display, retrieve) | Any | AUTO-APPROVE |
| Deploy/test | Scratch | AUTO-APPROVE |
| Deploy with --dry-run/--check-only | Sandbox | AUTO-APPROVE |
| Deploy to production | Production | REQUIRE CONFIRM |
| DELETE, org delete | Any | REQUIRE CONFIRM |

### 5. LLM-Powered Hooks (Haiku)

**Purpose:** Semantic evaluation for complex patterns that can't be detected by regex.

**Location:** `scripts/llm-eval.py`

**Use Cases:**
- Code quality scoring
- Security review (SOQL injection, FLS bypass detection)
- Deployment risk assessment

---

## Frontmatter Hooks (SKILL.md)

Skills now define their hooks directly in their `SKILL.md` YAML frontmatter instead of separate `hooks/hooks.json` files.

### Standard Hook Pattern

```yaml
---
name: sf-apex
description: >
  Generates and reviews Salesforce Apex code...
metadata:
  version: "1.1.0"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/apex-lsp-validate.py"
          timeout: 10000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-apex"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-apex"
      timeout: 5000
---
```

### Path Variables

| Variable | Resolves To |
|----------|-------------|
| `${SHARED_HOOKS}` | `shared/hooks/` directory |
| `${SKILL_HOOKS}` | Skill's own `hooks/scripts/` directory |
| `${CLAUDE_PLUGIN_ROOT}` | Root of the plugin/skill installation |

### Migrated Skills (18 total)

All skills have been migrated from `hooks/hooks.json` to frontmatter:

| Skill | Version | Special Hooks |
|-------|---------|---------------|
| sf-apex | 1.1.0 | apex-lsp-validate.py |
| sf-flow | 1.1.0 | flow-schema-validate.py |
| sf-lwc | 1.1.0 | lwc-lsp-validate.py |
| sf-metadata | 1.1.0 | post-write-validate.py |
| sf-data | 1.1.0 | post-write-validate.py |
| sf-testing | 1.1.0 | post-tool-validate.py |
| sf-debug | 1.1.0 | parse-debug-log.py (Bash) |
| sf-soql | 1.1.0 | post-tool-validate.py |
| sf-deploy | 1.1.0 | post-write-validate.py |
| sf-integration | 1.2.0 | suggest_credential_setup.py, validate_integration.py |
| sf-connected-apps | 1.1.0 | (standard) |
| sf-diagram-mermaid | 1.2.0 | (standard) |
| sf-diagram-nanobananapro | 1.5.0 | (Bash matcher) |
| sf-ai-agentscript | 1.4.0 | agentscript-syntax-validator.py |
| sf-ai-agentforce-legacy | 1.1.0 | agentscript-lsp-validate.py |
| sf-ai-agentforce-testing | 1.1.0 | parse-agent-test-results.py (Bash) |
| sf-permissions | 1.1.0 | (standard) |
| skill-builder | 2.1.0 | post-write-validate.py |

---

## Skills Registry Schema (v4.0.0)

```json
{
  "version": "4.0.0",
  "guardrails": {
    "dangerous_dml": {
      "patterns": ["DELETE FROM \\w+ (;|$)", "UPDATE \\w+ SET .* (?<!WHERE.*)$"],
      "severity": "CRITICAL",
      "action": "block",
      "message": "Destructive DML without WHERE clause detected"
    },
    "unbounded_soql": {
      "patterns": ["SELECT .* FROM \\w+ (?!.*LIMIT)"],
      "severity": "HIGH",
      "action": "auto_fix",
      "fix": "append LIMIT 200"
    }
  },
  "auto_approve_policy": {
    "read_operations": {
      "patterns": ["sf data query", "sf org display", "sf project retrieve"],
      "auto_approve": true,
      "reason": "Read-only operations are safe"
    },
    "scratch_org_operations": {
      "patterns": ["--target-org.*scratch", "-o.*scratch"],
      "auto_approve": true,
      "reason": "Scratch orgs are disposable"
    },
    "require_confirmation": {
      "patterns": ["--target-org.*prod", "DELETE", "org delete"],
      "auto_approve": false,
      "reason": "Production operations require confirmation"
    }
  },
  "skills": { ... },
  "chains": { ... },
  "confidence_levels": { ... }
}
```

---

## Global Hooks Configuration

The project's `.claude/hooks.json` wires global hooks:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "type": "command",
      "command": "python3 ./shared/hooks/skill-activation-prompt.py",
      "timeout": 5000
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python3 ./shared/hooks/scripts/guardrails.py",
        "timeout": 5000
      }]
    }],
    "PermissionRequest": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python3 ./shared/hooks/scripts/auto-approve.py",
        "timeout": 5000
      }]
    }]
  }
}
```

---

## Workflow Chains

### Defined Chains

| Chain | Order | Trigger Phrases |
|-------|-------|-----------------|
| `full_feature` | sf-metadata → sf-apex → sf-flow → sf-lwc → sf-deploy → sf-testing | "build feature", "complete feature" |
| `agentforce` | sf-metadata → sf-apex → sf-flow → sf-deploy → sf-ai-agentscript → sf-ai-agentforce-testing | "agentforce", "agent", "copilot" |
| `integration` | sf-connected-apps → sf-integration → sf-flow → sf-deploy | "integration", "external service" |
| `troubleshooting` | sf-testing → sf-debug → sf-apex → sf-deploy → sf-testing | "debug", "troubleshoot", "fix failing" |

### Context Persistence

Workflow context is persisted to `/tmp/sf-skills-context.json`:

```json
{
  "last_skill": "sf-apex",
  "detected_chain": "full_feature",
  "chain_position": 2,
  "files_modified": ["force-app/main/default/classes/AccountService.cls"],
  "detected_patterns": ["@InvocableMethod"],
  "timestamp": "2026-01-24T10:30:00Z"
}
```

---

## Adding a New Skill

### 1. Add to skills-registry.json

```json
"sf-newskill": {
  "keywords": ["keyword1", "keyword2"],
  "intentPatterns": ["create.*pattern", "build.*pattern"],
  "filePatterns": ["\\.ext$"],
  "priority": "medium",
  "description": "Description of the skill",
  "orchestration": {
    "prerequisites": [{ "skill": "sf-metadata", "confidence": 2 }],
    "next_steps": [{ "skill": "sf-deploy", "confidence": 3 }],
    "commonly_with": [{ "skill": "sf-testing", "trigger": "test" }]
  }
}
```

### 2. Add hooks to SKILL.md frontmatter

```yaml
---
name: sf-newskill
description: >
  Description here
metadata:
  version: "1.0.0"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-newskill"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-newskill"
      timeout: 5000
---
```

### 3. Update chains if applicable

Add the skill to relevant workflow chains in the `chains` section of `skills-registry.json`.

---

## Design Rationale

### Why Proactive + Reactive?

1. **Prevention is better than cure** - Block dangerous operations before damage
2. **User experience** - Auto-fix common issues without user intervention
3. **Safety net** - PostToolUse catches issues that slip through

### Why Frontmatter Hooks?

1. **Self-contained skills** - Each skill owns its complete configuration
2. **No file sprawl** - No separate `hooks/hooks.json` files
3. **Easier maintenance** - Update skill config in one place
4. **Better discoverability** - Hook config visible in skill documentation

### Why Advisory, Not Automatic?

1. **User agency** - Users stay in control of skill invocations
2. **Transparency** - Claude explains why it's suggesting skills
3. **Flexibility** - Users can override suggestions based on context
4. **Claude is smart** - The model follows well-structured suggestions

### Why Single Registry?

1. **DRY** - No duplicate configuration across 18+ skills
2. **Consistency** - All skills use the same schema
3. **Maintainability** - One place to update skill metadata
4. **Discoverability** - Easy to see all skill relationships

---

## Troubleshooting

### Hook Not Firing

1. Check path variables resolve correctly:
   ```bash
   echo $SHARED_HOOKS
   echo $SKILL_HOOKS
   ```

2. Verify YAML frontmatter syntax:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"
   ```

3. Check hook timeout (default 5000ms may be too short for some operations)

### Guardrail Too Aggressive

1. Check `skills-registry.json` guardrails section
2. Adjust severity from CRITICAL to HIGH or MEDIUM
3. Add pattern exception if needed

### Auto-Approve Not Working

1. Verify org type detection:
   ```bash
   sf org display --json | jq '.result.isScratch'
   ```

2. Check pattern matching in `auto_approve_policy`

### Chain Validation Issues

1. Check context file exists: `cat /tmp/sf-skills-context.json`
2. Verify skill name matches registry exactly
3. Clear context to reset: `rm /tmp/sf-skills-context.json`

---

## License

MIT License. See [LICENSE](../../LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
