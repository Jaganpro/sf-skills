---
name: sf-ai-agentforce
description: >
  Agentforce platform agent building via Setup UI.
  TRIGGER when: user maintains or configures agents via the legacy Setup UI / Agent Builder path,
  creates topics/actions, writes PromptTemplates, or touches .genAiFunction/.genAiPlugin/.promptTemplate
  metadata XML files.
  DO NOT TRIGGER when: Agent Script DSL .agent files (use sf-ai-agentscript),
  agent testing (use sf-ai-agentforce-testing), or persona design
  (use sf-ai-agentforce-persona).
license: MIT
compatibility: "Requires API v66.0+ (Spring '26)"
metadata:
  version: "2.1.0"
  author: "Jag Valaiyapathy"
---

# sf-ai-agentforce: Standard Agentforce Platform Development

Use this skill for the **Setup UI / Agent Builder** path: declarative topics, Builder-managed actions, GenAiFunction / GenAiPlugin metadata, PromptTemplate integration, Models API usage from Apex, and custom Lightning types.

> For new code-first agent development, prefer [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md).

## When This Skill Owns the Task

Use `sf-ai-agentforce` when the user is:
- maintaining existing Builder-based agents
- working in Setup → Agentforce → Agents
- creating or fixing `GenAiFunction`, `GenAiPlugin`, or `PromptTemplate` metadata
- wiring Builder topics to Flow / Apex / Prompt Template actions
- using Models API or LightningTypeBundle in the context of Builder-based agents

Do **not** use it for:
- `.agent` files or deterministic FSM design → [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)
- agent test suites and coverage loops → [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)
- persona / voice design → [sf-ai-agentforce-persona](../sf-ai-agentforce-persona/SKILL.md)

---

## Two Agentforce Paths

| Path | Skill | Best fit |
|---|---|---|
| Setup UI / Agent Builder | `sf-ai-agentforce` | Declarative maintenance, existing Builder agents, metadata-driven action registration |
| Agent Script DSL | `sf-ai-agentscript` | Code-first `.agent` authoring, deterministic routing, version-controlled agent logic |

If the user is starting from scratch and wants strong control over flow/state, route to Agent Script.

---

## Builder Workflow Summary

1. Confirm this is a **Builder / Setup UI** project
2. Pick Service Agent vs Employee Agent
3. Define topics with strong descriptions, scope, and instructions
4. Prepare supporting actions (Flow, Apex, PromptTemplate)
5. Configure inputs / outputs carefully
6. Validate dependencies
7. Publish, then activate

Expanded workflow: [references/builder-workflow.md](references/builder-workflow.md)

---

## Key Platform Rules

### Topic quality matters
Topic descriptions are routing instructions for the planner. They must be:
- specific
- scenario-based
- non-overlapping with sibling topics

### Actions are wrappers around real targets
| Target type | Typical use | Registered via |
|---|---|---|
| Flow | safest default for Builder actions | `GenAiFunction` |
| Apex | complex business logic via `@InvocableMethod` | `GenAiFunction` |
| Prompt Template | generated summaries / drafts / recommendations | `GenAiFunction` |

### Supporting metadata deploys first
Before publishing the agent itself, deploy the supporting stack:
1. metadata / fields if needed
2. Apex if needed
3. Flows if needed
4. PromptTemplate / GenAiFunction / GenAiPlugin
5. then publish the agent

### Publish does not activate
After publish, run `sf agent activate` separately.

---

## Metadata Guidance

### GenAiFunction
Use when registering a single callable action. Validate:
- target exists
- target is active / deployable
- input names match the target contract
- output names match the target contract
- capability text clearly says when the action should be used

### GenAiPlugin
Use when grouping related functions into one logical package.

### PromptTemplate
Use for generated content, not deterministic business rules.

### Models API
Use when the solution belongs in Apex-driven AI orchestration rather than Builder-only actions.

### Custom Lightning Types
Use when the action needs richer structured input or output presentation.

Expanded reference: [references/metadata-reference.md](references/metadata-reference.md)

---

## Recommended Orchestration Order

```text
sf-metadata → sf-apex → sf-flow → sf-ai-agentforce → sf-deploy
```

### Required delegations
| Requirement | Delegate to | Why |
|---|---|---|
| Create / fix Flows | [sf-flow](../sf-flow/SKILL.md) | Action target creation and Flow validation |
| Create / fix Apex actions | [sf-apex](../sf-apex/SKILL.md) | `@InvocableMethod` and Apex correctness |
| Deploy / publish | [sf-deploy](../sf-deploy/SKILL.md) | Deployment orchestration |
| Test the agent | [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md) | Formal test execution and assertions |

---

## High-Signal Failure Patterns

| Symptom | Likely cause | Read next |
|---|---|---|
| Action not available in Builder | target metadata missing or not deployed | [references/metadata-reference.md](references/metadata-reference.md) |
| Prompt output is poor | PromptTemplate shape / bindings are weak | [references/prompt-templates.md](references/prompt-templates.md) |
| Apex AI logic times out | Models API work placed in the wrong context | [references/models-api.md](references/models-api.md) |
| Rich input/output UI not rendering | Lightning type config or prerequisites are incomplete | [references/custom-lightning-types.md](references/custom-lightning-types.md) |
| Agent publishes but is not usable | forgot explicit activation | [references/cli-commands.md](references/cli-commands.md) |

---

## Reference Map

### Start here
- [references/builder-workflow.md](references/builder-workflow.md)
- [references/metadata-reference.md](references/metadata-reference.md)
- [references/cli-commands.md](references/cli-commands.md)

### Deep technical docs
- [references/prompt-templates.md](references/prompt-templates.md)
- [references/models-api.md](references/models-api.md)
- [references/custom-lightning-types.md](references/custom-lightning-types.md)

### Rubric
- [references/scoring-rubric.md](references/scoring-rubric.md)

### Cross-skill reads
- [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)
- [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)
- [sf-flow](../sf-flow/SKILL.md)
- [sf-apex](../sf-apex/SKILL.md)
- [sf-deploy](../sf-deploy/SKILL.md)

---

## Score Guide

| Score | Meaning |
|---|---|
| 90+ | Ready to deploy |
| 80–89 | Strong, minor cleanup only |
| 70–79 | Review before deploy |
| 60–69 | Needs work |
| < 60 | Block deployment |

Full rubric: [references/scoring-rubric.md](references/scoring-rubric.md)
