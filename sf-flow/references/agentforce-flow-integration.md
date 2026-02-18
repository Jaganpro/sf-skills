<!-- Parent: sf-flow/SKILL.md -->

# Flows for Agentforce (sf-ai-agentscript)

## When sf-ai-agentscript Requests a Flow

- sf-ai-agentscript will invoke sf-flow (this skill) to create Flows
- sf-flow creates the validated Flow XML
- sf-deploy handles deployment to org
- **Action Definition registration required** (see below)
- Only THEN can sf-ai-agentscript use `flow://FlowName` targets

## Variable Name Matching

When creating Flows for Agentforce agents:
- Agent Script input/output names MUST match Flow variable API names exactly
- Use descriptive names (e.g., `inp_AccountId`, `out_AccountName`)
- Mismatched names cause "Internal Error" during agent publish

### Output Variable Naming for Agentforce

Use `out_` prefix for output variables to distinguish them in Action Definition schema:

```xml
<variables>
    <name>out_CaseSubject</name>
    <dataType>String</dataType>
    <isOutput>true</isOutput>
</variables>
<variables>
    <name>out_CaseStatus</name>
    <dataType>String</dataType>
    <isOutput>true</isOutput>
</variables>
```

## Formula Expression Limitations in Flows

| Function | Status | Alternative |
|----------|--------|-------------|
| `BLANKVALUE()` | Not in Flow | Use Decision element or `IF()` |
| `CASESAFEID()` | Not in Flow | ID variables handle this automatically |
| `ISNEW()` / `ISCHANGED()` | Not in Flow | Use `$Record__Prior` comparisons |

## Action Definition Registration (REQUIRED)

> **CRITICAL**: Creating a Flow is NOT sufficient for Agentforce. The Flow must be registered as an Action Definition.

**Registration Workflow:**
1. **Deploy Flow** to target org via sf-deploy
2. Navigate to **Setup > Agentforce > Action Definitions**
3. Click **"New Action"**, select **"Flow"** as target type
4. Choose your deployed Flow from the list
5. **Map input/output variables** — these become the action's schema
6. Configure planner flags:
   - `is_displayable`: Can LLM show output to user?
   - `is_used_by_planner`: Can LLM use output for decisions?
7. **Save** the Action Definition

```
Flow Created  →  Deployed to Org  →  Action Definition Created  →  Agent Can Use
     ↑               ↑                        ↑                         ↑
   sf-flow       sf-deploy           Setup > Agentforce         @actions.MyAction
```

**Why This Matters**: The Action Definition is what exposes the Flow to the agent runtime. Without it, `@actions.FlowName` will fail with `ValidationError: Tool target 'FlowName' is not an action definition`.
