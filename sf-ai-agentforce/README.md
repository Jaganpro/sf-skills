# sf-ai-agentforce

Standard Agentforce platform skill for Setup UI-based agent building, PromptTemplate metadata, Einstein Models API, GenAiFunction/GenAiPlugin setup, and custom Lightning types.

> **For code-first Agent Script DSL development**, use [sf-ai-agentscript](../sf-ai-agentscript/) instead.

## What This Skill Covers

| Area | Description |
|------|-------------|
| **Agent Builder** | Creating and configuring agents via Setup UI / Agentforce Builder |
| **GenAiFunction** | Metadata XML for registering Flow, Apex, and Prompt Template actions |
| **GenAiPlugin** | Grouping multiple GenAiFunctions into reusable action sets |
| **PromptTemplate** | Einstein Prompt Builder templates for AI-generated content |
| **Models API** | Native LLM access in Apex via `aiplatform.ModelsAPI` |
| **Custom Lightning Types** | LightningTypeBundle for custom agent action UIs |

## What This Skill Does NOT Cover

| Area | Use Instead |
|------|-------------|
| Agent Script DSL (`.agent` files) | [sf-ai-agentscript](../sf-ai-agentscript/) |
| Agent testing & coverage | [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/) |
| Deployment & publishing | [sf-deploy](../sf-deploy/) |

## Requirements

| Requirement | Value |
|-------------|-------|
| API Version | **65.0+** (Winter '26 or later) |
| Licenses | Agentforce, Einstein Generative AI |
| sf CLI | v2.x with agent commands |

## Quick Start

```
Skill: sf-ai-agentforce
Request: "Set up a GenAiFunction for my Apex discount calculator"
```

## Documentation

| Document | Description |
|----------|-------------|
| [SKILL.md](SKILL.md) | Entry point — full skill reference |
| [docs/prompt-templates.md](docs/prompt-templates.md) | PromptTemplate metadata and Einstein Prompt Builder |
| [docs/models-api.md](docs/models-api.md) | Einstein Models API (`aiplatform.ModelsAPI`) |
| [docs/custom-lightning-types.md](docs/custom-lightning-types.md) | LightningTypeBundle for custom agent UIs |

## Orchestration

This skill fits into the Agentforce build chain:

```
sf-metadata → sf-apex → sf-flow → sf-ai-agentforce → sf-deploy
```

## License

MIT License — See [LICENSE](LICENSE)
