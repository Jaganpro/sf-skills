# Validation History: sf-ai-agentscript

This file tracks the validation history of the sf-ai-agentscript skill. Validation agents are deployed to a test org to verify that documented patterns still work with current Salesforce releases.

## Latest Validation

| Status | Date | Version | Agents Deployed | Test Org |
|--------|------|---------|-----------------|----------|
| ✅ PASS | 2026-02-14 | v1.9.0 | 16/16 | AgentforceTesting |

## Validation Agent Results

### Tier 1: Original Agents (13) — Re-validated

| Agent | Pattern Tested | Publish | Duration | Notes |
|-------|----------------|---------|----------|-------|
| Val_Minimal_Syntax | Core block structure | ✅ PASS | 16s | config, system, start_agent, topic blocks |
| Val_Arithmetic_Ops | +/- operators | ✅ PASS | 11s | Addition and subtraction working |
| Val_Comparison_Ops | Comparison operators | ✅ PASS | 12s | ==, !=, <, <=, >, >=, and, or, not |
| Val_Variable_Scopes | @variables namespace | ✅ PASS | 9s | mutable string/number/boolean |
| Val_Topic_Transitions | @utils.transition | ✅ PASS | 12s | Permanent handoffs between topics |
| Val_Latch_Pattern | Boolean re-entry | ✅ PASS | 14s | Latch variable for topic re-entry |
| Val_Loop_Guard | Iteration protection | ✅ PASS | 12s | Counter-based loop guard |
| Val_Interpolation | Variable injection | ✅ PASS | 9s | {!@variables.x} in strings |
| Val_Action_Properties | Action property validity | ✅ PASS | 13s | NEGATIVE: confirms invalid properties don't work |
| Val_Before_Reasoning | before_reasoning lifecycle | ✅ PASS | 9s | Direct content under block (no instructions: wrapper) |
| Val_After_Reasoning | after_reasoning lifecycle | ✅ PASS | 9s | Direct content under block (no instructions: wrapper) |
| Val_Label_Property | label: property | ✅ PASS | 9s | NEGATIVE: confirms label is NOT valid anywhere |
| Val_Always_Expect_Input | always_expect_input | ✅ PASS | 11s | NEGATIVE: confirms not implemented |

### Tier 2: New Agents (3) — v1.9.0 Patterns

| Agent | Pattern Tested | Publish | Duration | Notes |
|-------|----------------|---------|----------|-------|
| Val_Else_Nested_If | else: + nested if | ✅ PASS | 9s | NEGATIVE: else: with nested if does NOT compile (Approach 3 INVALID) |
| Val_Step_Guard | Step counter re-entry guard | ✅ PASS | 14s | Step variable guards topic selector re-routing |
| Val_Multiple_Available_When | Multiple available when clauses | ✅ PASS | 14s | POSITIVE: Multiple available when on same action IS valid |

**Total Duration**: ~183s (16 agents)

## TDD Findings (v1.9.0)

### Finding 1: `else:` + nested `if` does NOT compile ❌

- **Pattern**: `else:` block containing a nested `if` statement (SKILL.md Approach 3)
- **Error**: `Unexpected 'if'` at the nested if line, cascading `Unexpected '@utils'`, `Missing colon`, `Invalid syntax`
- **Impact**: SKILL.md Approach 3 must be removed or marked INVALID
- **Workaround**: Use compound conditions (`if A and B:`) or sequential ifs
- **Note**: Local LSP validator PASSES this pattern — only server-side compiler rejects it

### Finding 2: `<>` not-equal operator does NOT compile ❌

- **Pattern**: `if @variables.x <> "value":` using `<>` as not-equal
- **Error**: `Unexpected '>' 44:29` — parser does not recognize `<>` as a token
- **Impact**: Remove `<>` from SKILL.md operator table; only `!=` is valid
- **Workaround**: Use `!=` operator (already validated in Val_Comparison_Ops)

### Finding 3: Multiple `available when` clauses ARE valid ✅

- **Pattern**: Two `available when` clauses on the same action
- **Result**: Compiles and publishes successfully
- **Impact**: SKILL.md constraint "One `available when` per action" is WRONG — remove it
- **Impact**: Common Issues entry "Duplicate 'available when' clause" is WRONG — remove it
- **Impact**: multi-step-workflow template pattern is CORRECT as-is

## Patterns Validated

Each validation agent tests specific patterns documented in SKILL.md:

1. **Val_Minimal_Syntax** → Core Syntax
   - `config` block with agent_name, agent_label, default_agent_user
   - `system` block with messages and instructions
   - `start_agent` block with reasoning and actions
   - `topic` block with description and reasoning

2. **Val_Arithmetic_Ops** → Expression Operators
   - Addition: `@variables.counter + 1`
   - Subtraction: `@variables.counter - 1`
   - Note: `*`, `/`, `%` are NOT supported

3. **Val_Comparison_Ops** → Expression Operators
   - Equality: `==`, not-equal: `!=`
   - Comparisons: `<`, `<=`, `>`, `>=`
   - Logical: `and`, `or`, `not`
   - Note: `<>` is NOT valid (see Finding 2)

4. **Val_Variable_Scopes** → Variable Namespaces
   - `mutable string` with default value
   - `mutable number` with default value
   - `mutable boolean` with default value
   - `set @variables.x = value` assignment

5. **Val_Topic_Transitions** → Topic Transitions
   - `@utils.transition to @topic.X` (permanent handoff)
   - Multi-step topic chains

6. **Val_Latch_Pattern** → Production Gotchas
   - Boolean flag initialization
   - Setting latch on entry
   - Checking latch in topic selector
   - Clearing latch on completion

7. **Val_Loop_Guard** → Production Gotchas
   - Iteration counter pattern
   - `available when` guard clause
   - Exit condition on max iterations

8. **Val_Interpolation** → Instruction Syntax
   - Basic interpolation: `{!@variables.x}`
   - Multiple variables in string
   - Conditional interpolation: `{!value if condition else alt}`

9. **Val_Action_Properties** → Action Properties (NEGATIVE)
   - CONFIRMED NOT VALID: require_user_confirmation, include_in_progress_indicator, output_instructions, progress_indicator_message (on transitions)
   - CONFIRMED VALID: description only (on @utils.transition)

10. **Val_Before_Reasoning** → Lifecycle Hooks
    - Content directly under `before_reasoning:` block
    - NO `instructions:` wrapper required

11. **Val_After_Reasoning** → Lifecycle Hooks
    - Content directly under `after_reasoning:` block
    - NO `instructions:` wrapper required

12. **Val_Label_Property** → Reserved Properties (NEGATIVE)
    - CONFIRMED NOT VALID: `label:` property on topics and actions

13. **Val_Always_Expect_Input** → Unimplemented Features (NEGATIVE)
    - CONFIRMED NOT VALID: `always_expect_input:` property

14. **Val_Else_Nested_If** → if/else Nesting (NEGATIVE)
    - CONFIRMED NOT VALID: `else:` block with nested `if` statement
    - CONFIRMED VALID: Compound conditions and sequential ifs as alternatives

15. **Val_Step_Guard** → Topic Re-Entry Protection
    - Step counter in `start_agent` guards topic selector
    - `workflow_active` boolean flag pattern
    - `available when` on step completion

16. **Val_Multiple_Available_When** → Action Guards
    - CONFIRMED VALID: Multiple `available when` clauses on same action
    - DISPROVES: "One available when per action" constraint in SKILL.md

## Validation Command

```bash
# Navigate to validation directory
cd sf-ai-agentscript/validation

# Deploy metadata first
sf project deploy start \
  --source-dir validation-agents/force-app/main/default/aiAuthoringBundles \
  --target-org AgentforceTesting --json

# Publish each agent
for agent in Val_Minimal_Syntax Val_Arithmetic_Ops Val_Comparison_Ops Val_Variable_Scopes \
  Val_Topic_Transitions Val_Latch_Pattern Val_Loop_Guard Val_Interpolation \
  Val_Action_Properties Val_Before_Reasoning Val_After_Reasoning \
  Val_Label_Property Val_Always_Expect_Input Val_Else_Nested_If \
  Val_Step_Guard Val_Multiple_Available_When; do
  sf agent publish authoring-bundle --api-name "$agent" --target-org AgentforceTesting --json
done
```

## Test Org Configuration

| Property | Value |
|----------|-------|
| **Target Org Alias** | `AgentforceTesting` |
| **Einstein Agent User** | `multistepworkflows@00dak00000gdhgd1068670160.ext` |
| **API Version** | 65.0 |
| **Instance URL** | `dak00000gdhgdeay-dev-ed.develop.my.salesforce.com` |

## History

| Date | Version | Status | Passed | Failed | Notes |
|------|---------|--------|--------|--------|-------|
| 2026-02-14 | v1.9.0 | ✅ PASS | 16/16 | 0 | 3 new agents + re-validation against AgentforceTesting. Found: else+nested-if INVALID, <> INVALID, multiple available-when VALID |
| 2026-01-20 | v1.1.0 | ✅ PASS | 8/8 | 0 | Initial validation framework implementation (R6-Agentforce-SandboxFull) |

## Next Validation Due

**2026-03-16** (30 days from last validation)

---

## Troubleshooting

### If Validation Fails

1. **Check the error message** - Salesforce will indicate what syntax changed
2. **Update SKILL.md** - Document the new constraint or syntax requirement
3. **Fix the validation agent** - Update to use correct syntax
4. **Re-run validation** - Ensure all agents pass again
5. **Update this file** - Log the issue and resolution in History

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| `Nonexistent flag: --source-dir` | CLI version change | Use `sf agent publish authoring-bundle --api-name` instead |
| `Unknown error` on publish | Usually successful | Check full JSON output for actual status |
| `Default agent user not found` | Wrong org or user inactive | Query target org for Einstein Agent User |
| `AgentCompilationError` on deploy | Server-side compiler stricter than LSP | Fix agent, redeploy. Note: LSP may pass patterns the server rejects |
| `Unexpected 'if'` inside else: | else: + nested if not valid | Use compound conditions or sequential ifs |
| `Unexpected '>'` in condition | `<>` not-equal not valid | Use `!=` instead |
| jq parse errors on `--json` output | sf CLI emits control chars | Pipe through `tr -d '\000-\037'` before jq |
