# sf-ai-agentscript

🤖 **Agent Script DSL development for Salesforce Agentforce** - Write deterministic agents in a single `.agent` file with FSM architecture, instruction resolution, and hybrid reasoning.

## Features

- ✅ **100-point scoring system** across 6 categories for quality assurance
- ✅ **Complete syntax reference** for Agent Script DSL
- ✅ **FSM architecture patterns** - Hub-and-spoke, verification gates, escalation chains
- ✅ **Instruction resolution guidance** - Three-phase execution model
- ✅ **Debugging support** - Trace analysis and forensic debugging
- ✅ **CLI deployment** - Retrieve, validate, deploy via `sf agent` commands
- ✅ **Cross-skill integration** - Works with sf-flow, sf-ai-agentforce-testing, sf-deploy

## Requirements

| Requirement | Value |
|-------------|-------|
| API Version | 62.0+ |
| License | Agentforce |
| Einstein Agent User | Required in org |
| SF CLI | v2+ with agent commands |

## Installation

```bash
# Install as part of sf-skills marketplace
claude /plugin install github:Jaganpro/sf-skills

# Or standalone
claude /plugin install github:Jaganpro/sf-skills/sf-ai-agentscript
```

## Quick Start

### 1. Invoke the Skill
```
/sf-ai-agentscript
```

### 2. Describe Your Agent
Tell Claude what your agent should do, and it will generate a scored Agent Script.

### 3. Validate & Deploy
```bash
sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
sf agent publish authoring-bundle --api-name MyAgent --target-org prod --json
```

## Scoring System

| Category | Points | Focus |
|----------|--------|-------|
| Structure & Syntax | 20 | Block ordering, indentation, required fields |
| Deterministic Logic | 25 | Security guards, post-action checks |
| Instruction Resolution | 20 | Arrow syntax, template injection |
| FSM Architecture | 15 | Topic separation, transitions |
| Action Configuration | 10 | Protocols, I/O mapping |
| Deployment Readiness | 10 | Valid user, clean validation |

**Thresholds:** 90+ Excellent | 80-89 Very Good | 70-79 Good | 60-69 Needs Work | <60 Critical

## Key Rules

1. **`default_agent_user` MUST exist** - Query for valid Einstein Agent User
2. **No mixed tabs/spaces** - Use consistent indentation throughout
3. **Booleans are `True`/`False`** - Python-style, not JavaScript
4. **Exactly one `start_agent`** - Single entry point required
5. **Use `available when` for security** - Don't rely on prompts

## Quick Syntax Reference

```yaml
# Block structure
system:        # Required: Messages and instructions
config:        # Required: Agent metadata
variables:     # Optional: State management
topic:         # Required: Conversation handlers
start_agent:   # Required: Entry point

# Instruction patterns
instructions: ->           # Arrow syntax for expressions
  if @variables.verified:  # Conditional (resolves before LLM)
    | Welcome back!        # Literal text for LLM
  run @actions.load_data   # Execute action
  set @var = @outputs.val  # Capture output

# Action guards
actions:
  process: @actions.refund
    available when @variables.verified == True  # LLM can't see if False
```

## Documentation

| Document | Description |
|----------|-------------|
| [SKILL.md](SKILL.md) | Main entry point with scoring system |
| [resources/](resources/) | Comprehensive guides per topic |
| [docs/](docs/) | Quick reference guides |
| [templates/](templates/) | Example .agent files |

## Cross-Skill Workflow

```
/sf-flow → /sf-ai-agentscript → /sf-ai-agentforce-testing → /sf-deploy
   ↑              ↑                      ↑                      ↑
Create Flows   Write agent         Test routing           Deploy to org
```

## Official Resources

- [Agent Script Documentation](https://developer.salesforce.com/docs/einstein/genai/guide/agent-script.html)
- [Agentforce Builder Guide](https://help.salesforce.com/s/articleView?id=sf.copilot_builder_overview.htm)
- [Atlas Reasoning Engine](https://developer.salesforce.com/docs/einstein/genai/guide/atlas-reasoning-engine.html)

## License

MIT License - See [LICENSE](LICENSE)

---

Created by [Jag Valaiyapathy](https://github.com/Jaganpro)
