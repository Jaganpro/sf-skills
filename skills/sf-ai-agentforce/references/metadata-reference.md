# Agentforce Metadata Reference

Use this document for the metadata-heavy parts of `sf-ai-agentforce` that do not need to live in the activation path.

## GenAiFunction

A `GenAiFunction` registers one callable agent action.

### Common target types
- `flow`
- `apex`
- `prompt`

### Validate before deploy
- target exists
- target is active / deployable
- input names match the target contract
- output names match the target contract
- capability text explains when the planner should use the action

## GenAiPlugin

A `GenAiPlugin` groups related `GenAiFunction` records.

Use it when:
- multiple functions belong to one business domain
- you want cleaner packaging for Builder-based actions

## PromptTemplate integration

Use PromptTemplate-backed actions when:
- the output is generated content
- the user needs a draft, summary, rewrite, or recommendation

Do not use PromptTemplate as a substitute for deterministic business logic.

## Models API

Use `aiplatform.ModelsAPI` when:
- the requirement is Apex-driven AI logic
- the work belongs in custom server-side orchestration
- Builder-only action patterns are insufficient

## Custom Lightning Types

Use `LightningTypeBundle` when actions need:
- structured input collection
- richer output rendering
- UI-driven agent interaction patterns

## Deployment rule of thumb

Supporting metadata first:
- objects / fields
- Apex
- Flows
- PromptTemplates / GenAiFunction / GenAiPlugin
- then publish the agent

## Deep references

- Prompt templates: [prompt-templates.md](prompt-templates.md)
- Models API: [models-api.md](models-api.md)
- Custom Lightning types: [custom-lightning-types.md](custom-lightning-types.md)
- CLI lifecycle: [cli-commands.md](cli-commands.md)
