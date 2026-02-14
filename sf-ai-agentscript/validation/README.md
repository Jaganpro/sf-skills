# Validation Agents for sf-ai-agentscript

This directory contains **Validation Agents** - dedicated `.agent` files that serve as test cases for the sf-ai-agentscript skill. They validate that documented patterns still work with current Salesforce releases.

## Quick Start

```bash
# 1. Navigate to validation directory
cd /Users/jvalaiyapathy/Projects/claude-code-sfskills/sf-ai-agentscript/validation

# 2. Validate syntax (no org needed) - Tier 1
for dir in validation-agents/force-app/main/default/aiAuthoringBundles/*/; do
  echo "Validating $(basename "$dir")..."
  name=$(basename "$dir")
  sf agent validate authoring-bundle --api-name "$name" -o TARGET_ORG --json
done

# 3. Deploy all validation agents (requires auth to test org) - Tier 2
for dir in validation-agents/force-app/main/default/aiAuthoringBundles/*/; do
  name=$(basename "$dir")
  echo "Publishing $name..."
  sf agent publish authoring-bundle --api-name "$name" -o R6-Agentforce-SandboxFull --json
done
```

## What Each Agent Tests

| Agent Name | Tests Pattern | SKILL.md Section |
|------------|---------------|------------------|
| `Val_Minimal_Syntax` | Basic config, system, start_agent, topic blocks | Core Syntax |
| `Val_Arithmetic_Ops` | Addition (+) and subtraction (-) operators | Expression Operators |
| `Val_Comparison_Ops` | Comparison operators (>, <, >=, <=, ==, !=) | Expression Operators |
| `Val_Variable_Scopes` | @variables.* namespace | Variable Namespaces |
| `Val_Topic_Transitions` | @utils.transition (permanent handoff) | Topic Transitions |
| `Val_Latch_Pattern` | Boolean flag for topic re-entry | Production Gotchas |
| `Val_Loop_Guard` | Max 3-4 iteration protection | Production Gotchas |
| `Val_Interpolation` | Variable injection in strings | Interpolation |
| `Val_Action_Properties` | Action property validity (NEGATIVE) | Action Properties |
| `Val_Before_Reasoning` | before_reasoning lifecycle hook | Lifecycle Hooks |
| `Val_After_Reasoning` | after_reasoning lifecycle hook | Lifecycle Hooks |
| `Val_Label_Property` | label: property (NEGATIVE) | Reserved Properties |
| `Val_Always_Expect_Input` | always_expect_input (NEGATIVE) | Unimplemented Features |
| `Val_Else_Nested_If` | else: + nested if (NEGATIVE) | if/else Nesting Rules |
| `Val_Step_Guard` | Step counter re-entry guard | Topic Re-Entry |
| `Val_Multiple_Available_When` | Multiple available when (POSITIVE) | Action Guards |

## Validation Tiers

| Tier | Check | Method | Pass Criteria |
|------|-------|--------|---------------|
| 1 | Syntax | `sf agent validate authoring-bundle` | Exit code 0 |
| 2 | Deployment | `sf agent publish authoring-bundle` | Published successfully |
| 3 | URL Health | HTTP HEAD requests | Salesforce doc URLs return 200 |

## Test Org Configuration

- **Target Org Alias**: `AgentforceTesting`
- **Einstein Agent User**: `multistepworkflows@00dak00000gdhgd1068670160.ext`
- **API Version**: 65.0

## When Validation Fails

If a validation agent fails to deploy:

1. **Check the error message** - Salesforce will indicate what syntax changed
2. **Update SKILL.md** - Document the new constraint or syntax requirement
3. **Fix the validation agent** - Update to use correct syntax
4. **Re-run validation** - Ensure all agents pass again
5. **Update VALIDATION.md** - Log the issue and resolution

## Directory Structure

```
validation/
├── sfdx-project.json           # SFDX project config
├── README.md                   # This file
└── validation-agents/
    └── force-app/main/default/aiAuthoringBundles/
        ├── Val_Minimal_Syntax/
        │   ├── Val_Minimal_Syntax.agent
        │   └── Val_Minimal_Syntax.bundle-meta.xml
        ├── Val_Arithmetic_Ops/
        │   ├── Val_Arithmetic_Ops.agent
        │   └── Val_Arithmetic_Ops.bundle-meta.xml
        └── ... (6 more validation agents)
```

## Creating New Validation Agents

When adding new patterns to SKILL.md, create a corresponding validation agent:

1. Create directory: `validation-agents/force-app/main/default/aiAuthoringBundles/Val_NewPattern/`
2. Create `.agent` file with minimal code testing the pattern
3. Create `.bundle-meta.xml` with bundleType AGENT
4. Run validation to ensure it works
5. Document in this README

## Maintenance Schedule

- **Validation Interval**: 30 days
- **Check `validate_by` date in SKILL.md frontmatter**
- **Run validation** before major skill updates
