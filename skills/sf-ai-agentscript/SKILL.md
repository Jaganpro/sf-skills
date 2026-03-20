---
name: sf-ai-agentscript
description: >
  Agent Script DSL for deterministic Agentforce agents.
  TRIGGER when: user writes or edits .agent files, builds FSM-based agents,
  uses Agent Script CLI (sf agent generate/publish), or asks about deterministic
  agent patterns, slot filling, or instruction resolution.
  DO NOT TRIGGER when: Setup UI agent building (use sf-ai-agentforce), agent
  testing (use sf-ai-agentforce-testing), or persona design
  (use sf-ai-agentforce-persona).
license: MIT
compatibility: "Requires Agentforce license, API v66.0+, Einstein Agent User"
metadata:
  version: "2.9.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 6 categories"
  validated: "0-shot generation tested (Pet_Adoption_Advisor, TechCorp_IT_Agent, Quiz_Master, Expense_Calculator, Order_Processor). Agent user setup validated against ORM1, ORM2, AutomotiveSupport, SalesforceProductAssistant."
  last_validated: "2026-03-20"
  validation_status: "PASS"
  validation_agents: "24"
  validate_by: "2026-04-10"
---

# SF-AI-AgentScript Skill

Agent Script is the **code-first** path for deterministic Agentforce agents. Use this skill when the user is authoring `.agent` files, building finite-state topic flows, or needs repeatable control over routing, variables, actions, and publish behavior.

> Start with the shortest guide first: [references/activation-checklist.md](references/activation-checklist.md)

## When This Skill Owns the Task

Use `sf-ai-agentscript` when the work involves:
- creating or editing `.agent` files
- deterministic topic routing, guards, and transitions
- Agent Script CLI workflows (`sf agent generate`, `sf agent validate`, `sf agent publish`)
- slot filling, instruction resolution, post-action loops, or FSM design

Delegate elsewhere when the user is:
- maintaining legacy Setup UI / Agent Builder agents → [sf-ai-agentforce](../sf-ai-agentforce/SKILL.md)
- designing persona / tone / voice → [sf-ai-agentforce-persona](../sf-ai-agentforce-persona/SKILL.md)
- building formal test plans or coverage loops → [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)

---

## Required Context to Gather First

Ask for or infer:
- agent purpose and whether Agent Script is truly the right fit
- Service Agent vs Employee Agent
- target org and publish intent
- expected actions / targets (Flow, Apex, PromptTemplate, etc.)
- whether the request is authoring, validation, preview, or publish troubleshooting

---

## Activation Checklist

Before you author or fix any `.agent` file, verify these first:

1. **Exactly one `start_agent` block**
2. **No mixed tabs and spaces**
3. **Booleans are `True` / `False`**
4. **No `else if` and no nested `if`**
5. **No top-level `actions:` block**
6. **No `@inputs` in `set` expressions**
7. **`linked` variables have no defaults**
8. **`linked` variables do not use `object` / `list` types**
9. **Use explicit `agent_type`**
10. **Use `@actions.` prefixes consistently**
11. **Use `run @actions.X` only when `X` is a topic-level action definition with `target:`**
12. **Do not branch directly on raw `@system_variables.user_input contains/startswith/endswith` for intent routing**
13. **On prompt-template outputs, prefer `is_displayable: False` + `is_used_by_planner: True`**
14. **Do not assume `@outputs.X` is scalar — inspect the output schema before branching or assignment**

For the expanded version, use [references/activation-checklist.md](references/activation-checklist.md).

---

## Non-Negotiable Rules

### 1) Service Agent vs Employee Agent

| Agent type | Required | Forbidden / caution |
|---|---|---|
| `AgentforceServiceAgent` | Valid `default_agent_user`, correct permissions, target-org checks | Publishing without a real Einstein Agent User |
| `AgentforceEmployeeAgent` | Explicit `agent_type` | Supplying `default_agent_user` |

Full details: [references/agent-user-setup.md](references/agent-user-setup.md)

### 2) Required block order

```yaml
config:
variables:
system:
connection:
knowledge:
language:
start_agent:
topic:
```

### 3) Critical config fields

| Field | Rule |
|---|---|
| `developer_name` | Must match folder / bundle name |
| `agent_description` | Use instead of legacy `description` |
| `agent_type` | Set explicitly every time |
| `default_agent_user` | Service Agents only |

### 4) Syntax blockers you should treat as immediate failures

- `else if`
- nested `if`
- comment-only `if` bodies
- top-level `actions:`
- invocation-level `inputs:` / `outputs:` blocks
- reserved variable / field names like `description` and `label`

Canonical rule set: [references/syntax-reference.md](references/syntax-reference.md) and [references/validator-rule-catalog.md](references/validator-rule-catalog.md)

---

## Recommended Workflow

## Recommended Authoring Workflow

### Phase 1 — design the agent
- decide whether the problem is actually deterministic enough for Agent Script
- model topics as states and transitions as edges
- define only the variables you truly need

### Phase 2 — author the `.agent`
- create `config`, `system`, `start_agent`, and topics first
- add target-backed actions with full `inputs:` and `outputs:`
- use `available when` for deterministic tool visibility
- normalize raw intent/validation signals into booleans or enums before branching; avoid direct substring checks on raw user utterances for critical control flow
- keep post-action checks at the **top** of `instructions: ->`

### Phase 3 — validate continuously
Validation already runs automatically on write/edit. Use the CLI before publish:

```bash
sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
```

The validator covers structure, runtime gotchas, target readiness, and org-aware Service Agent checks. Rule IDs live in [references/validator-rule-catalog.md](references/validator-rule-catalog.md).

### Phase 4 — preview smoke test
Use the preview loop before publish:
- derive 3–5 smoke utterances
- start preview
- inspect topic routing / action invocation / safety / grounding
- fix and rerun up to 3 times

Full loop: [references/preview-test-loop.md](references/preview-test-loop.md)

### Phase 5 — publish and activate
```bash
sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG --json
sf agent activate --api-name MyAgent -o TARGET_ORG
```

Publishing does **not** activate the agent.

---

## Deterministic Building Blocks

These execute as code, not suggestions:
- conditionals
- `available when` guards
- variable checks
- direct `set` / `transition to`
- `run @actions.X` **only when `X` is a topic-level action definition with `target:`**
- variable injection into LLM-facing text

Important distinction:
- **Deterministic**: `set`, `transition to`, and `run @actions.X` for a target-backed topic action
- **LLM-directed**: `reasoning.actions:` utilities / delegations such as `@utils.setVariables`, `@utils.transition`, and `{!@actions.X}` instruction references

If you need deterministic behavior for something that is currently modeled as a reasoning-level utility, either:
- rewrite it as direct `set` / `transition to`, or
- promote it to a topic-level target-backed action and `run` that action

See [references/instruction-resolution.md](references/instruction-resolution.md) and [references/architecture-patterns.md](references/architecture-patterns.md).

---

## Cross-Skill Integration

## Cross-Skill Orchestration

| Task | Delegate to | Why |
|---|---|---|
| Build `flow://` targets | [sf-flow](../sf-flow/SKILL.md) | Flow creation / validation |
| Build Apex action targets | [sf-apex](../sf-apex/SKILL.md) | `@InvocableMethod` and business logic |
| Test topic routing / actions | [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md) | Formal test specs and fix loops |
| Deploy / publish | [sf-deploy](../sf-deploy/SKILL.md) | Deployment orchestration |

---

## High-Signal Failure Patterns

| Symptom | Likely cause | Read next |
|---|---|---|
| `Internal Error` during publish | invalid Service Agent user or missing action I/O | [references/agent-user-setup.md](references/agent-user-setup.md), [references/actions-reference.md](references/actions-reference.md) |
| `invalid input/output parameters` on prompt template action | **Target template is in Draft status** — activate it first | [references/action-prompt-templates.md](references/action-prompt-templates.md#draft-template-publish-errors) |
| Parser rejects conditionals | `else if`, nested `if`, empty `if` body | [references/syntax-reference.md](references/syntax-reference.md) |
| Action target issues | missing Flow / Apex target, inactive Flow, bad schemas | [references/actions-reference.md](references/actions-reference.md) |
| Prompt template runs but user sees blank response | prompt output marked `is_displayable: True` | [references/production-gotchas.md](references/production-gotchas.md), [references/action-prompt-templates.md](references/action-prompt-templates.md) |
| Prompt action runs but planner behaves like output is missing | output hidden from direct display but not planner-visible | [references/production-gotchas.md](references/production-gotchas.md), [references/actions-reference.md](references/actions-reference.md) |
| `ACTION_NOT_IN_SCOPE` on `run @actions.X` | `run` points at a utility / delegation / unresolved action instead of a topic-level target-backed definition | [references/syntax-reference.md](references/syntax-reference.md), [references/instruction-resolution.md](references/instruction-resolution.md) |
| Deterministic cancel / revise / URL checks behave inconsistently | raw `@system_variables.user_input` matching or string-method guards are being used as control-flow-critical validation | [references/syntax-reference.md](references/syntax-reference.md), [references/production-gotchas.md](references/production-gotchas.md) |
| `@outputs.X` comparisons or assignments behave unexpectedly | the action output is structured/wrapped, not a plain scalar | [references/actions-reference.md](references/actions-reference.md), [references/syntax-reference.md](references/syntax-reference.md) |
| Preview and runtime disagree | linked vars / context / known platform issues | [references/known-issues.md](references/known-issues.md) |
| Validate passes but publish fails | org-specific user / permission / retrieve-back issue | [references/production-gotchas.md](references/production-gotchas.md), [references/cli-guide.md](references/cli-guide.md) |

---

## Reference Map

### Start here
- [references/activation-checklist.md](references/activation-checklist.md)
- [references/syntax-reference.md](references/syntax-reference.md)
- [references/actions-reference.md](references/actions-reference.md)

### Publish / runtime safety
- [references/agent-user-setup.md](references/agent-user-setup.md)
- [references/production-gotchas.md](references/production-gotchas.md)
- [references/customer-web-client.md](references/customer-web-client.md)
- [references/known-issues.md](references/known-issues.md)

### Architecture / reasoning
- [references/architecture-patterns.md](references/architecture-patterns.md)
- [references/instruction-resolution.md](references/instruction-resolution.md)
- [references/fsm-architecture.md](references/fsm-architecture.md)
- [references/patterns-quick-ref.md](references/patterns-quick-ref.md)

### Validation / testing / debugging
- [references/preview-test-loop.md](references/preview-test-loop.md)
- [references/testing-guide.md](references/testing-guide.md)
- [references/debugging-guide.md](references/debugging-guide.md)
- [references/validator-rule-catalog.md](references/validator-rule-catalog.md)

### Examples / templates
- [references/minimal-examples.md](references/minimal-examples.md)
- [assets/](assets/)
- [assets/agents/](assets/agents/)
- [assets/patterns/](assets/patterns/)

### Project documentation
- [references/version-history.md](references/version-history.md)
- [references/sources.md](references/sources.md)

---

## Score Guide

| Score | Meaning |
|---|---|
| 90+ | Deploy with confidence |
| 75–89 | Good, review warnings |
| 60–74 | Needs focused revision |
| < 60 | Block publish |

Full rubric: [references/scoring-rubric.md](references/scoring-rubric.md)

---

## Official Resources

- [Agent Script Documentation](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-script.html)
- [Agent Script Recipes](https://github.com/trailheadapps/agent-script-recipes)
- [Agentforce DX Guide](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx.html)
- [references/official-sources.md](references/official-sources.md)
