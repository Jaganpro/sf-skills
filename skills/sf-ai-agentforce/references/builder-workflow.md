# Agentforce Builder Workflow

This reference expands the Setup UI / Agent Builder workflow for `sf-ai-agentforce`.

## Recommended order

1. Confirm this is a **Setup UI / Builder** project, not Agent Script
2. Identify agent type: Service Agent vs Employee Agent
3. Define topics and topic scope
4. Prepare supporting actions (Flow, Apex, PromptTemplate)
5. Configure action inputs and outputs
6. Configure agent-level instructions and messages
7. Validate supporting metadata
8. Publish and activate

## Builder checklist

### Topics
- Topic descriptions must be concrete and routeable
- Scope should say what the topic can and cannot do
- Instructions should be procedural, not vague brand copy

### Actions
- Flow actions are the safest default for Builder-based agents
- Apex actions must expose `@InvocableMethod`
- PromptTemplate actions should be used when the goal is generated content, not deterministic business logic

### Inputs / Outputs
- Input names must match the target contract exactly
- Output names should be meaningful to the planner
- Displayable outputs should be user-facing and concise

### Agent-level settings
- System instructions should be stable and role-defining
- Welcome message should orient the user quickly
- Error message should explain fallback behavior
- Service Agents need a valid default running user

## Publish sequence

1. Deploy supporting metadata
2. Validate the agent bundle
3. Publish the authoring bundle
4. Activate the agent

Publishing does **not** activate the new version automatically.

## Deep references

- CLI lifecycle: [cli-commands.md](cli-commands.md)
- Metadata details: [metadata-reference.md](metadata-reference.md)
- Prompt templates: [prompt-templates.md](prompt-templates.md)
- Models API: [models-api.md](models-api.md)
- Custom Lightning types: [custom-lightning-types.md](custom-lightning-types.md)
