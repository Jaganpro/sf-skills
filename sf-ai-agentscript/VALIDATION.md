# Validation History: sf-ai-agentscript

This file tracks the validation history of the sf-ai-agentscript skill. Validation agents are deployed to a test org to verify that documented patterns still work with current Salesforce releases.

## Latest Validation

| Status | Date | Version | Agents Deployed | Test Org |
|--------|------|---------|-----------------|----------|
| ✅ PASS | 2026-01-20 | v1.1.0 | 8/8 | R6-Agentforce-SandboxFull |

## Validation Agent Results

| Agent | Pattern Tested | Deploy | Duration | Notes |
|-------|----------------|--------|----------|-------|
| Val_Minimal_Syntax | Core block structure | ✅ PASS | 15.9s | config, system, start_agent, topic blocks |
| Val_Arithmetic_Ops | +/- operators | ✅ PASS | 17.9s | Addition and subtraction working |
| Val_Comparison_Ops | Comparison operators | ✅ PASS | 27.7s | ==, !=, <, <=, >, >=, and, or, not |
| Val_Variable_Scopes | @variables namespace | ✅ PASS | 21.8s | mutable string/number/boolean |
| Val_Topic_Transitions | @utils.transition | ✅ PASS | 30.6s | Permanent handoffs between topics |
| Val_Latch_Pattern | Boolean re-entry | ✅ PASS | 18.6s | Latch variable for topic re-entry |
| Val_Loop_Guard | Iteration protection | ✅ PASS | 16.6s | Counter-based loop guard |
| Val_Interpolation | Variable injection | ✅ PASS | 22.6s | {!@variables.x} in strings |

**Total Duration**: ~171.6s

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
   - Equality: `==`, not-equal (`<>` or not-equal-operator)
   - Comparisons: `<`, `<=`, `>`, `>=`
   - Logical: `and`, `or`, `not`

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

## Validation Command

```bash
# Navigate to validation directory
cd sf-ai-agentscript/validation

# Deploy metadata first
sf project deploy start \
  --source-dir validation-agents/force-app/main/default/aiAuthoringBundles \
  --target-org R6-Agentforce-SandboxFull

# Publish each agent
for agent in Val_Minimal_Syntax Val_Arithmetic_Ops Val_Comparison_Ops Val_Variable_Scopes Val_Topic_Transitions Val_Latch_Pattern Val_Loop_Guard Val_Interpolation; do
  sf agent publish authoring-bundle --api-name "$agent" --target-org R6-Agentforce-SandboxFull
done
```

## History

| Date | Version | Status | Passed | Failed | Notes |
|------|---------|--------|--------|--------|-------|
| 2026-01-20 | v1.1.0 | ✅ PASS | 8/8 | 0 | Initial validation framework implementation |

## Next Validation Due

**2026-02-19** (30 days from last validation)

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
