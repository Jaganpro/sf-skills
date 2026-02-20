<!-- Parent: sf-ai-agentforce/SKILL.md -->
<!-- TIER: 2 | DETAILED REFERENCE -->
<!-- Read after: SKILL.md -->
<!-- Purpose: CLI command reference for agent lifecycle, generation, and publishing -->

# Agent CLI Commands Reference

> Complete `sf agent` command reference for lifecycle management, spec generation, and publishing

## Overview

This document covers all `sf agent` CLI commands relevant to the Agentforce platform skill. Commands are grouped by function: lifecycle management, agent generation, and validation/publishing.

---

## Agent Lifecycle Commands

### sf agent activate

Makes a published agent available to users.

```bash
sf agent activate --api-name <AgentApiName> --target-org <alias> --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `--api-name` | Yes | API name of the agent to activate |
| `--target-org` | Yes | Alias or username of the target org |
| `--api-version` | No | Override the API version used for the request |
| `--json` | No | Return output as JSON (recommended) |

**Prerequisites:** Agent must be published first via `sf agent publish authoring-bundle`.

### sf agent deactivate

Deactivates an active agent. Required before making changes to topics, actions, or system instructions.

```bash
sf agent deactivate --api-name <AgentApiName> --target-org <alias> --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `--api-name` | Yes | API name of the agent to deactivate |
| `--target-org` | Yes | Alias or username of the target org |
| `--api-version` | No | Override the API version used for the request |
| `--json` | No | Return output as JSON (recommended) |

### sf agent create

Creates a new agent from a spec file.

```bash
sf agent create --spec <path-to-spec.yaml> --target-org <alias> --json
```

> **Not recommended.** Agents created via `sf agent create` do not use Agent Script and are less flexible than the authoring-bundle workflow. Prefer `sf agent generate authoring-bundle` + `sf agent publish authoring-bundle` instead.

---

## Agent Generation Commands

### sf agent generate agent-spec

Generates an agent spec YAML file interactively or with flags. The spec defines the agent's identity, topics, and behavior.

```bash
# Interactive full interview
sf agent generate agent-spec --full-interview

# Non-interactive with key flags
sf agent generate agent-spec \
    --type customer \
    --role "Customer support specialist" \
    --company-name "Acme Corp" \
    --company-description "Enterprise SaaS provider" \
    --tone formal \
    --output-file ./agent-spec.yaml

# Iterative refinement of existing spec
sf agent generate agent-spec --spec ./agent-spec.yaml
```

| Flag | Required | Description |
|------|----------|-------------|
| `--type` | No | Agent type: `customer` or `internal` |
| `--role` | No | Agent's role description |
| `--company-name` | No | Company name for agent context |
| `--company-description` | No | Company description for grounding |
| `--company-website` | No | Company website URL for enrichment |
| `--tone` | No | Conversational tone: `formal`, `casual`, or `neutral` |
| `--full-interview` | No | Interactive prompt for all properties |
| `--spec` | No | Path to existing spec YAML for iterative refinement |
| `--prompt-template` | No | Custom prompt template for spec generation |
| `--grounding-context` | No | Additional context for grounding the agent |
| `--force-overwrite` | No | Overwrite existing output file without prompting |
| `--enrich-logs` | No | Include enrichment logs in output |
| `--max-topics` | No | Maximum number of topics to generate |
| `--agent-user` | No | Default agent user for the spec |
| `--output-file` | No | Path for the output spec YAML file |

### sf agent generate authoring-bundle

Generates an authoring bundle scaffolding from an existing agent in the org.

```bash
sf agent generate authoring-bundle --api-name <AgentApiName> --target-org <alias> --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `--api-name` | No | API name of the agent to generate from |
| `--name` | No | Name for the authoring bundle |
| `--no-spec` | No | Generate without a spec file |
| `--force-overwrite` | No | Overwrite existing files |
| `--authoring-bundle` | No | Path to authoring bundle directory |
| `--target-org` | No | Alias or username of the target org |
| `--json` | No | Return output as JSON |

### sf agent generate template

Generates a BotTemplate for ISV packaging via managed packages on AppExchange.

```bash
sf agent generate template \
    --agent-file force-app/main/default/bots/My_Agent/My_Agent.bot-meta.xml \
    --agent-version 1
```

| Flag | Required | Description |
|------|----------|-------------|
| `--agent-file` | Yes | Path to the `.bot-meta.xml` file |
| `--agent-version` | Yes | BotVersion number to template |

The generated BotTemplate wraps Bot, BotVersion, and GenAiPlannerBundle metadata for distribution. Package the template in a managed package for sharing between orgs or publishing on AppExchange.

> **Full ISV workflow**: See [../../sf-deploy/references/agent-deployment-guide.md](../../sf-deploy/references/agent-deployment-guide.md) for the complete packaging workflow.

---

## Validation & Publishing Commands

### sf agent validate authoring-bundle

Validates Agent Script syntax before publishing.

```bash
sf agent validate authoring-bundle --api-name <AgentApiName> --target-org <alias> --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `--api-name` | Yes | API name of the agent to validate |
| `--target-org` | Yes | Alias or username of the target org |
| `--json` | No | Return output as JSON (recommended) |

### sf agent publish authoring-bundle

Publishes an agent's authoring bundle to the org.

```bash
sf agent publish authoring-bundle --api-name <AgentApiName> --target-org <alias> --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `--api-name` | Yes | API name of the agent to publish |
| `--target-org` | Yes | Alias or username of the target org |
| `--skip-retrieve` | No | Skip metadata retrieval from org (faster for CI/CD, v2.122.6+) |
| `--json` | No | Return output as JSON (recommended) |

### sf agent preview

Previews agent behavior interactively. This command is interactive and does not support `--json`.

```bash
# Simulated mode (default — no real Apex/Flow execution)
sf agent preview --api-name <AgentApiName> --target-org <alias>

# Live mode (executes real Apex/Flows)
sf agent preview --api-name <AgentApiName> --use-live-actions --target-org <alias>

# With debug output
sf agent preview --api-name <AgentApiName> --output-dir ./logs --apex-debug --target-org <alias>

# From local authoring bundle
sf agent preview --authoring-bundle <path> --target-org <alias>
```

| Flag | Required | Description |
|------|----------|-------------|
| `--api-name` | Yes* | API name of the agent to preview |
| `--authoring-bundle` | Yes* | Path to local authoring bundle (alternative to `--api-name`) |
| `--target-org` | Yes | Alias or username of the target org |
| `--use-live-actions` | No | Execute real Apex/Flows instead of LLM simulation |
| `--output-dir` | No | Directory for preview output/logs |
| `--apex-debug` | No | Include Apex debug logs in output |

*One of `--api-name` or `--authoring-bundle` is required.

---

## Cross-Skill References

| Command Area | Skill | Notes |
|-------------|-------|-------|
| Agent Script `.agent` files, preview, authoring-bundle | [sf-ai-agentscript](../../sf-ai-agentscript/SKILL.md) | Code-first agent development |
| Deployment orchestration, CI/CD | [sf-deploy](../../sf-deploy/SKILL.md) | Agent deployment workflows |
| Test execution, coverage analysis | [sf-ai-agentforce-testing](../../sf-ai-agentforce-testing/SKILL.md) | `sf agent test run/list/results` |
