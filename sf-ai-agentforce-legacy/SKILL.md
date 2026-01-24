---
name: sf-ai-agentforce-legacy
description: >
  [DEPRECATED] Creates Agentforce agents using Agent Script syntax with 100-point scoring.
  For new agent development, use sf-ai-agentscript instead.
  This skill remains available for maintaining existing agents built with legacy patterns.
license: MIT
compatibility: "Requires API v65.0+ (Winter '26) for deployment"
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  scoring: "100 points across 6 categories"
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 ${SHARED_HOOKS}/scripts/guardrails.py"
          timeout: 5000
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python3 ${SKILL_HOOKS}/agentscript-lsp-validate.py"
          timeout: 10000
        - type: command
          command: "python3 ${SHARED_HOOKS}/suggest-related-skills.py sf-ai-agentforce-legacy"
          timeout: 5000
  SubagentStop:
    - type: command
      command: "python3 ${SHARED_HOOKS}/scripts/chain-validator.py sf-ai-agentforce-legacy"
      timeout: 5000
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document - read this FIRST -->
<!-- Progressive disclosure: SKILL.md → Resources → Quick Refs → Detailed Refs → Specialized Guides -->

> ⚠️ **DEPRECATED**: This skill has been superseded by **sf-ai-agentscript**.
>
> For new agent development, use: `Skill(skill="sf-ai-agentscript")`
>
> This skill remains available for maintaining existing agents built with the legacy patterns.

# sf-ai-agentforce-legacy: Agentforce Agent Creation with Agent Script (Legacy)

Expert Agentforce developer specializing in Agent Script syntax, topic design, and action integration. Generate production-ready agents that leverage LLM reasoning with deterministic business logic.

## Core Responsibilities

1. **Agent Creation**: Generate complete Agentforce agents using Agent Script
2. **Topic Management**: Create and configure agent topics with proper transitions
3. **Action Integration**: Connect actions to Flows (directly) or Apex (via Agent Actions)
4. **Validation & Scoring**: Score agents against best practices (0-100 points)
5. **Deployment**: Publish agents using `sf agent publish authoring-bundle`

## Document Map (Progressive Disclosure)

**Read documents in tier order based on what you need:**

### Tier 2: Resource Guides (NEW)
| Need | Document | Description |
|------|----------|-------------|
| **Complete syntax reference** | [agent-script-reference.md](resources/agent-script-reference.md) | Full Agent Script DSL, patterns, reserved words, new features |
| **Topic design & routing** | [topics-guide.md](resources/topics-guide.md) | Topic structure, transitions, delegation, multi-topic agents |
| **Action implementation** | [actions-guide.md](resources/actions-guide.md) | Flow/Apex actions, data types, advanced fields, slot filling |
| **Testing approaches** | [testing-guide.md](resources/testing-guide.md) | Preview modes, Agent Testing Center, agentic fix loops |
| **Deployment & CLI** | [deployment-guide.md](resources/deployment-guide.md) | Two deployment methods, CLI commands, troubleshooting |

### Tier 3: Quick References
| Need | Document | Description |
|------|----------|-------------|
| **CLI commands** | [cli-guide.md](docs/cli-guide.md) | sf agent commands, preview, publish |
| **Patterns & practices** | [patterns-and-practices.md](docs/patterns-and-practices.md) | Decision tree + best practices |

### Cross-Skill: Testing
| Need | Skill | Description |
|------|-------|-------------|
| **Agent Testing** | `sf-ai-agentforce-testing` | Test execution, coverage analysis, agentic fix loops |

**Quick Links:**
- [Key Insights Table](#-key-insights) - Common errors and fixes
- [Scoring System](#scoring-system-100-points) - 6-category validation
- [Required Files Checklist](#required-files-checklist) - Pre-deployment verification

**Official Reference:**
- [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) - Salesforce's official Agent Script examples

---

## Critical Warnings

### API Version Requirement

**Agent Script requires API v65.0+ (Winter '26 or later)**

Before creating agents, verify:
```bash
sf org display --target-org [alias] --json | jq '.result.apiVersion'
```

If API version < 65, Agent Script features won't be available.

### Orchestration Order

**sf-metadata → sf-apex → sf-flow → sf-deploy → sf-ai-agentforce** (you are here: sf-ai-agentforce)

**Why this order?**
1. **sf-metadata**: Custom objects/fields must exist before Apex or Flows reference them
2. **sf-apex**: InvocableMethod classes must be deployed before Flow wrappers call them
3. **sf-flow**: Flows must be created AND deployed before agents can reference them
4. **sf-deploy**: Deploy all metadata before publishing agent
5. **sf-ai-agentforce**: Agent is published LAST after all dependencies are in place

**MANDATORY Delegation:**
- **Flows**: ALWAYS use `Skill(skill="sf-flow")` - never manually write Flow XML
- **Deployments**: Use `Skill(skill="sf-deploy")` for all deployments
- **Apex**: ALWAYS use `Skill(skill="sf-apex")` for InvocableMethod classes

See `docs/orchestration.md` for complete workflow.

### File Structure

| Method | Path | Files | Deploy Command |
|--------|------|-------|----------------|
| **AiAuthoringBundle** | `aiAuthoringBundles/[Name]/` | `[Name].agent` + `.bundle-meta.xml` | `sf agent publish authoring-bundle --api-name [Name]` |
| **GenAiPlannerBundle** | `genAiPlannerBundles/[Name]/` | `[Name].genAiPlannerBundle` + `agentScript/[Name]_definition.agent` | `sf project deploy start --source-dir [path]` |

**XML templates**: See `templates/` for bundle-meta.xml and genAiPlannerBundle examples.

GenAiPlannerBundle agents do NOT appear in Agentforce Studio UI.

**Full deployment method comparison**: See [deployment-guide.md](resources/deployment-guide.md#deployment-methods)

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- **Agent purpose**: What job should this agent do?
- **Topics needed**: What categories of actions? (e.g., FAQ, Order Management, Support)
- **Actions required**: Flow-based? Apex-based? External API?
- **Variables**: What state needs to be tracked?
- **System persona**: What tone/behavior should the agent have?

**Then**:
1. Check existing agents: `Glob: **/aiAuthoringBundles/**/*.agent`
2. Check for sfdx-project.json to confirm Salesforce project structure
3. Create TodoWrite tasks

### Phase 2: Template Selection / Design

**Select appropriate pattern** based on requirements - see [agent-script-reference.md](resources/agent-script-reference.md#common-patterns) for full list:

| Pattern | Use When | Template |
|---------|----------|----------|
| Hello World | Learning / Minimal agent | `templates/agents/hello-world.agent` |
| Simple Q&A | Single topic, no actions | `templates/agents/simple-qa.agent` |
| Multi-Topic | Multiple conversation modes | `templates/agents/multi-topic.agent` |
| Action-Based | External integrations needed | `templates/components/flow-action.agent` |

**Pattern Decision Guide**: See [patterns-and-practices.md](docs/patterns-and-practices.md) for detailed decision tree.

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/templates/[path]`
2. **Project folder**: `[project-root]/sf-ai-agentforce/templates/[path]`

### Phase 3: Generation / Validation

**Create TWO files** at:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml
```

**Required bundle-meta.xml content**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

**Required .agent blocks**:
1. `system:` - Instructions and messages (MUST BE FIRST)
2. `config:` - Agent metadata (agent_name, agent_label, description, default_agent_user)
3. `variables:` - Linked and mutable variables
4. `language:` - Locale settings
5. `start_agent topic_selector:` - Entry point topic with label and description
6. `topic [name]:` - Additional topics (each with label and description)

**Complete syntax reference**: See [agent-script-reference.md](resources/agent-script-reference.md)

**Validation Report Format** (6-Category Scoring 0-100):
```
Score: 85/100 ⭐⭐⭐⭐ Very Good
├─ Structure & Syntax:     18/20 (90%)
├─ Topic Design:           16/20 (80%)
├─ Action Integration:     18/20 (90%)
├─ Variable Management:    13/15 (87%)
├─ Instructions Quality:   12/15 (80%)
└─ Security & Guardrails:   8/10 (80%)

Issues:
⚠️ [Syntax] Line 15: Inconsistent indentation (mixing tabs and spaces)
⚠️ [Topic] Missing label for topic 'checkout'
✓ All topic references valid
✓ All variable references valid
```

### Phase 4: Deployment

**Complete deployment workflow**: See [deployment-guide.md](resources/deployment-guide.md#deployment-workflow)

**Quick workflow:**

```bash
# 1. Deploy dependencies first (flows, apex)
sf project deploy start --metadata Flow --target-org [alias]

# 2. ⚠️ VALIDATE AGENT (MANDATORY)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# 3. Deploy agent (Option A: Metadata API - recommended)
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]

# 4. Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]
```

**NEW vs UPDATING agents**: See [deployment-guide.md](resources/deployment-guide.md#new-agents-vs-updating-existing-agents) for method selection.

### Phase 5: Verification

```
✓ Agent Complete: [AgentName]
  Type: Agentforce Agent | API: 65.0+
  Location: force-app/main/default/aiAuthoringBundles/[AgentName]/
  Files: [AgentName].agent, [AgentName].bundle-meta.xml
  Validation: PASSED (Score: XX/100)
  Topics: [N] | Actions: [M] | Variables: [P]
  Published: Yes | Activated: [Yes/No]

Next Steps:
  1. Open in Studio: sf org open agent --api-name [AgentName]
  2. Test in Agentforce Testing Center
  3. Activate when ready: sf agent activate
```

### Phase 6: Testing (via sf-ai-agentforce-testing)

**Complete testing guide**: See [testing-guide.md](resources/testing-guide.md)

After deploying your agent, use the **sf-ai-agentforce-testing** skill:

```bash
# Invoke the testing skill
Skill(skill="sf-ai-agentforce-testing", args="Test agent [AgentName] and fix any failures")
```

The testing skill provides:
- **Test spec generation** from agent metadata
- **100-point test scoring** across 5 categories
- **Agentic fix loops** - auto-fix failing tests (max 3 iterations)
- **Coverage analysis** for topics, actions, guardrails, escalation

---

## Quick Reference

### Minimal Working Example

```agentscript
system:
	instructions: "You are a helpful assistant. Be professional and friendly."
	messages:
		welcome: "Hello! How can I help you today?"
		error: "I apologize, but I encountered an issue."

config:
	agent_name: "My_Agent"
	default_agent_user: "user@example.com"
	agent_label: "My Agent"
	description: "A helpful assistant agent"

variables:
	EndUserId: linked string
		source: @MessagingSession.MessagingEndUserId
		description: "Messaging End User ID"
	RoutableId: linked string
		source: @MessagingSession.Id
		description: "Messaging Session ID"
	ContactId: linked string
		source: @MessagingEndUser.ContactId
		description: "Contact ID"

language:
	default_locale: "en_US"
	additional_locales: ""
	all_additional_locales: False

start_agent topic_selector:
	label: "Topic Selector"
	description: "Routes users to appropriate topics"
	reasoning:
		instructions: ->
			| Determine what the user needs.
		actions:
			go_help: @utils.transition to @topic.help

topic help:
	label: "Help"
	description: "Provides help to users"
	reasoning:
		instructions: ->
			| Answer the user's question helpfully.
```

**Complete syntax and patterns**: See [agent-script-reference.md](resources/agent-script-reference.md)

### Action Target Types (22+ Supported)

| Type | Target Syntax | Recommended |
|------|---------------|-------------|
| **Flow** (native) | `flow://FlowAPIName` | Best choice |
| **Apex** (via Flow) | `flow://ApexWrapperFlow` | Recommended |
| **Prompt Template** | `generatePromptResponse://TemplateName` | For LLM tasks |
| **Standard Action** | `standardInvocableAction://sendEmail` | Built-in actions |

**Complete action reference**: See [actions-guide.md](resources/actions-guide.md#complete-action-type-reference)

### Topic Design

**Hub-and-Spoke Pattern** (Recommended):
- `start_agent` = Hub (routes to topics)
- Topics = Spokes (feature areas)
- Each topic can transition back to hub

**Complete topic patterns**: See [topics-guide.md](resources/topics-guide.md#routing-patterns)

---

## Scoring System (100 Points)

### Categories

| Category | Points | Key Criteria |
|----------|--------|--------------|
| **Structure & Syntax** | 20 | Valid syntax, consistent indentation, required blocks |
| **Topic Design** | 20 | Labels/descriptions, logical transitions, naming |
| **Action Integration** | 20 | Valid targets, input descriptions, no reserved words |
| **Variable Management** | 15 | Descriptions, required linked vars, appropriate types |
| **Instructions Quality** | 15 | Clear reasoning, edge cases, valid templates |
| **Security & Guardrails** | 10 | System guardrails, validation, error handling |

### Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Deploy with confidence |
| 80-89 | ⭐⭐⭐⭐ Very Good | Minor improvements suggested |
| 70-79 | ⭐⭐⭐ Good | Review before deploy |
| 60-69 | ⭐⭐ Needs Work | Address issues before deploy |
| <60 | ⭐ Critical | **Block deployment** |

---

## Cross-Skill Integration

### MANDATORY Delegations

| Requirement | Skill/Agent | Why | Never Do |
|-------------|-------------|-----|----------|
| **Flow Creation** | `Skill(skill="sf-flow")` | 110-point validation, proper XML ordering, prevents errors | Manually write Flow XML |
| **ALL Deployments** | `Skill(skill="sf-deploy")` | Centralized deployment | Direct CLI |
| **Apex Creation** | `Skill(skill="sf-apex")` | @InvocableMethod generation | Manually write Apex |

### Integration Patterns

| Direction | Pattern | Supported |
|-----------|---------|-----------|
| sf-agentforce → sf-flow | Create Flow-based actions | Full |
| sf-agentforce → sf-apex | Create Apex via Flow wrapper | Via Flow |
| sf-agentforce → sf-deploy | Deploy agent metadata | Full |
| sf-agentforce → sf-metadata | Query object structure | Full |
| sf-agentforce → sf-integration | External API actions | Via Flow |

**Complete integration guide**: See [actions-guide.md](resources/actions-guide.md#apex-actions-via-flow-wrapper)

---

## Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| File Extension | `.agentscript` not recognized | Use `.agent` |
| Config Field | `developer_name` OR `agent_name` | Both work (aliases for same field) |
| Instructions Syntax | `instructions:->` fails | Use `instructions: ->` (space!) |
| Topic Fields | Missing `label` fails deploy | Add both `label` and `description` |
| Linked Variables | Missing context variables | Add EndUserId, RoutableId, ContactId |
| Language Block | Missing causes deploy failure | Add `language:` block |
| Bundle XML | Missing causes deploy failure | Create `.bundle-meta.xml` file |
| **Indentation Consistency** | **Mixing tabs/spaces causes parse errors** | **Use TABS consistently (recommended)** |
| `@variables` is plural | `@variable.x` fails | Use `@variables.x` |
| Boolean capitalization | `true/false` invalid | Use `True/False` |
| **⚠️ Validation Required** | **Skipping validation causes late-stage failures** | **ALWAYS run `sf agent validate authoring-bundle` BEFORE deploy** |
| **Flow Variable Names** | **Mismatched names cause "Internal Error"** | **Agent Script input/output names MUST match Flow variable API names exactly** |
| **Action Location** | Top-level actions fail | Define actions inside topics |
| **start_agent Actions** | Flow actions in `start_agent` fail in AiAuthoringBundle | Use `start_agent` only for `@utils.transition`, put flow actions in `topic` blocks |
| **System Instructions** | Pipe `\|` syntax fails in system: block | Use single quoted string only |
| **Escalate Description** | Inline description fails | Put `description:` on separate indented line |
| **Reserved Words** | `description` as input fails | Use alternative names (e.g., `case_description`) |
| **⚠️ Slot Filling Reliability** | **LLM sends empty JSON, wrong field names, or wrong values** | **Use deterministic collection: dedicated setter action + single-use (`available when @var == ""`) + null guards. See [actions-guide.md](resources/actions-guide.md#slot-filling-patterns)** |
| **Explicit Action References** | LLM doesn't consistently call correct actions | Reference actions in instructions: `{!@actions.capture_id}`. Improves LLM reliability. |

**Complete troubleshooting**: See [deployment-guide.md](resources/deployment-guide.md#troubleshooting)

---

## Required Files Checklist

Before deployment, ensure you have:

- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent`
- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml`
- [ ] `sfdx-project.json` in project root
- [ ] Valid `default_agent_user` in config block
- [ ] All linked variables (EndUserId, RoutableId, ContactId)
- [ ] Language block present
- [ ] **⚠️ Validation passed**: `sf agent validate authoring-bundle --api-name [AgentName]` returns 0 errors
- [ ] All topics have `label:` and `description:`
- [ ] No reserved words used as input/output names
- [ ] Flow/Apex dependencies deployed to org first

---

## LSP Integration (Real-Time Validation)

This skill includes **Language Server Protocol (LSP)** integration for real-time Agent Script validation.

### Prerequisites

1. **VS Code with Agent Script Extension** (Required)
   - Open VS Code → Extensions (Cmd+Shift+X)
   - Search: "Agent Script" by Salesforce
   - Install the extension

2. **Node.js 18+** (Required)
   - Check: `node --version`
   - Install: `brew install node` (macOS)

### Features

When you edit `.agent` files, the LSP automatically provides:

| Feature | Description |
|---------|-------------|
| Syntax Validation | Real-time error detection |
| Auto-Fix Loop | Claude automatically fixes errors (max 3 attempts) |
| Fast Feedback | ~50ms response time |

### Troubleshooting

**"LSP server not found"**
- Install VS Code Agent Script extension
- Verify: `ls ~/.vscode/extensions/salesforce.agent-script-*`

**"Node.js not found"**
- Install Node.js 18+: `brew install node`

**Validation not triggering**
- Ensure hooks are enabled in Claude Code settings
- Check: `ls ~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/hooks/`

---

## Validation

**Manual validation** (if hooks don't fire):
```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-agentforce/hooks/scripts/validate_agentforce.py <file_path>
```

**Scoring**: 100 points / 6 categories. Minimum 60 (60%) for deployment.

**Hooks not firing?** Check: `CLAUDE_PLUGIN_ROOT` set, hooks.json valid, Python 3 in PATH, file matches pattern `*.agent`.

---

## Reference & Dependencies

**Resource Guides** (NEW):
- [agent-script-reference.md](resources/agent-script-reference.md) - Complete Agent Script DSL
- [topics-guide.md](resources/topics-guide.md) - Topic design and routing
- [actions-guide.md](resources/actions-guide.md) - Action implementation patterns
- [testing-guide.md](resources/testing-guide.md) - Testing approaches
- [deployment-guide.md](resources/deployment-guide.md) - Deployment and CLI
- [models-api.md](docs/models-api.md) - **NEW**: Native AI API (aiplatform.ModelsAPI) usage in Queueable/Batch
- [custom-lightning-types.md](docs/custom-lightning-types.md) - **NEW**: LightningTypeBundle for custom agent action UIs

**Quick References**:
- [agent-script-reference.md](docs/agent-script-reference.md) - Full syntax + gotchas
- [cli-guide.md](docs/cli-guide.md) - sf agent commands, preview, publish
- [actions-reference.md](docs/actions-reference.md) - Flow, Apex, Prompt actions
- [patterns-and-practices.md](docs/patterns-and-practices.md) - Decision tree + best practices

**Dependencies**: sf-deploy (optional) for additional deployment options. Install: `/plugin install github:Jaganpro/sf-skills/sf-deploy`

**Notes**: API 65.0+ required | Agent Script is GA (2025) | Block if score < 60

---

## License

MIT License. See LICENSE file in sf-ai-agentforce folder.
Copyright (c) 2024-2025 Jag Valaiyapathy
