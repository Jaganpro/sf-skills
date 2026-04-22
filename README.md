# Salesforce Skills for Agentic Coding Tools

> 💙 **Community-powered agentic coding knowledge, shared by a Salesforce Certified Technical Architect (CTA)**

[![Author](https://img.shields.io/badge/Author-Jag_Valaiyapathy-blue?logo=github)](https://github.com/Jaganpro)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-36-4F46E5)](#available-skills)
[![Claude Code Agents](https://img.shields.io/badge/Claude_Code_Agents-7-059669)](#agent-team)
[![Standard](https://img.shields.io/badge/Agent_Skills-Compatible-0F766E)](https://agentskills.io)

A reusable skill library for **Salesforce-focused coding agents**—covering Apex, Flow, LWC, SOQL, metadata, Data Cloud, integration, testing, deployment, Agentforce workflows, and Flex Credit estimation.

**Included:** 36 Salesforce skills, 7 specialist Claude Code agents, a shared hook system for guardrails and auto-validation, and LSP-backed feedback for Apex, LWC, and Agent Script.

> Recommended workflow for this repository: agent-first development in Claude Code, Pi, and similar coding agents. VS Code is optional tooling, not the primary operating model.
>
> The primary value of this repo is the skill library itself, not a VS Code-first workflow.

**Start here:** [Available Skills](#available-skills) · [Installation](#installation) · [Claude Code Features](#claude-code-features) · [Skill Architecture](#skill-architecture)

---

<a id="available-skills"></a>

## ✨ Available Skills

The library is organized by capability area so you can scan quickly, pick the right entry point, and jump straight into the relevant skill folder.

| Area | Skills | Best for |
|---|---|---|
| 💻 **Development** | [sf-apex](skills/sf-apex/), [sf-flow](skills/sf-flow/), [sf-lwc](skills/sf-lwc/), [sf-soql](skills/sf-soql/) | Apex, Flow, LWC, and query development |
| 🧪 **Quality** | [sf-testing](skills/sf-testing/), [sf-debug](skills/sf-debug/) | Test execution, coverage analysis, and debug-log troubleshooting |
| 📦 **Foundation** | [sf-metadata](skills/sf-metadata/), [sf-data](skills/sf-data/), [sf-docs](skills/sf-docs/), [sf-permissions](skills/sf-permissions/) | Metadata generation, data operations, access analysis, and official Salesforce docs retrieval |
| 🔌 **Integration** | [sf-connected-apps](skills/sf-connected-apps/), [sf-integration](skills/sf-integration/) | OAuth, External Client Apps, Named Credentials, callouts, and events |
| 💰 **Planning & Estimation** | [sf-flex-estimator](skills/sf-flex-estimator/) | Public list-price Flex Credit estimation, scenario planning, and cost optimization for Agentforce and Data Cloud |
| ☁️ **Data Cloud** | [sf-datacloud](skills/sf-datacloud/), [sf-datacloud-connect](skills/sf-datacloud-connect/), [sf-datacloud-prepare](skills/sf-datacloud-prepare/), [sf-datacloud-harmonize](skills/sf-datacloud-harmonize/), [sf-datacloud-segment](skills/sf-datacloud-segment/), [sf-datacloud-act](skills/sf-datacloud-act/), [sf-datacloud-retrieve](skills/sf-datacloud-retrieve/) | Data Cloud connections, ingestion, harmonization, segmentation, activation, and retrieval.<br><sub>Beta / Community Preview · live execution uses the external community <code>sf data360</code> runtime</sub> |
| 🤖 **AI & Automation** | [sf-ai-agentscript](skills/sf-ai-agentscript/), [sf-ai-agentforce](skills/sf-ai-agentforce/), [sf-ai-agentforce-testing](skills/sf-ai-agentforce-testing/), [sf-ai-agentforce-observability](skills/sf-ai-agentforce-observability/), [sf-ai-agentforce-persona](skills/sf-ai-agentforce-persona/), [sf-ai-agentforce-grid](skills/sf-ai-agentforce-grid/) | Agent design, Agent Script, testing, observability, persona design, and Agentforce Grid workbooks |
| 🚀 **DevOps & Tooling** | [sf-deploy](skills/sf-deploy/), [sf-vlocity-build-deploy](skills/sf-vlocity-build-deploy/), [sf-diagram-mermaid](skills/sf-diagram-mermaid/), [sf-diagram-nanobananapro](skills/sf-diagram-nanobananapro/) | Salesforce + Vlocity DataPack deployment automation, Mermaid diagrams, and visual artifacts |
| 🏢 **Industries** | [sf-industry-commoncore-omnistudio-analyze](skills/sf-industry-commoncore-omnistudio-analyze/), [sf-industry-commoncore-datamapper](skills/sf-industry-commoncore-datamapper/), [sf-industry-commoncore-integration-procedure](skills/sf-industry-commoncore-integration-procedure/), [sf-industry-commoncore-callable-apex](skills/sf-industry-commoncore-callable-apex/), [sf-industry-commoncore-omniscript](skills/sf-industry-commoncore-omniscript/), [sf-industry-commoncore-flexcard](skills/sf-industry-commoncore-flexcard/), [sf-industry-cme-epc-model](skills/sf-industry-cme-epc-model/) | OmniStudio + EPC: dependency analysis, Data Mappers, Integration Procedures, callable Apex, OmniScripts, FlexCards, and CME product/offer catalog modeling |

<a id="installation"></a>

## 🚀 Installation

### Choose Your Path

| If you want... | Use this | Best for |
|---|---|---|
| Skills only, any supported coding agent | <code>npx skills add Jaganpro/sf-skills</code> | Codex, Gemini CLI, OpenCode, Amp, Claude Code without local hooks |
| Full Claude Code experience | <code>curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.sh &#124; bash</code> | Hooks, agents, LSP, guardrails |
| Manual / Windows / CI-friendly install | <code>curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.py &#124; python3</code> | Direct installer control without bash wrapper |

### Any AI Coding Agent

> Requires [Node.js 18+](https://nodejs.org/) (provides the `npx` command)

```bash
npx skills add Jaganpro/sf-skills
```

Works with Claude Code, Codex, Gemini CLI, OpenCode, Amp, and [40+ agents](https://agentskills.io).

> **Note for Data Cloud users:** the `sf-datacloud-*` family uses an external community `sf data360` CLI runtime. Install sf-skills normally, then follow `skills/sf-datacloud/references/plugin-setup.md` if you plan to use the Data Cloud family.

```bash
# Install a single skill
npx skills add Jaganpro/sf-skills --skill sf-apex

# List available skills before installing
npx skills add Jaganpro/sf-skills --list
```

### Claude Code (Full Experience)

> **Using Claude Code?** This path is recommended — `npx` installs skills only, while the installer adds the full local experience: skills + agents + hooks + LSP + guardrails.

```bash
curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.sh | bash
```

This installs 36 skills, 7 specialist agents, a shared hook system, and the local LSP engine. It also configures LLM-powered guardrails (Haiku prompt hook), SOQL schema validation, Prettier auto-formatting, Code Analyzer (PMD/ESLint), and debug log analysis (Haiku agent hook).

> **Data Cloud note:** the installer brings in the `sf-datacloud-*` skills, but the external community `sf data360` CLI runtime is still a separate prerequisite. On first-time install the installer can prompt for it, or you can request it explicitly with `--with-datacloud-runtime`.

**Restart Claude Code** after installation.

### Direct Python Installer (manual / Windows / CI)

```bash
curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.py | python3
```

Want the optional Data Cloud runtime too?

```bash
curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.py | python3 - --with-datacloud-runtime
```

Use this path when you want to:
- review installer output directly
- run on Windows without the bash wrapper
- script installs in CI or managed environments
- access advanced installer commands immediately

### Updating

| Install Method | Check for Updates | Update |
|----------------|-------------------|--------|
| **npx** | `npx skills check` | `npx skills update` |
| **install.py** | `python3 ~/.claude/sf-skills-install.py --status` | `python3 ~/.claude/sf-skills-install.py --update` |

### Managing install.py

> After sf-skills is installed, use the installed copy at `~/.claude/sf-skills-install.py` for normal updates. Use `tools/install.py` only when developing or testing from a cloned repo checkout.
>
> **Data Cloud:** the `sf-datacloud-*` family ships with sf-skills, but live Data Cloud execution also needs the optional community `sf data360` runtime. Install it during setup when prompted, or later with `python3 ~/.claude/sf-skills-install.py --with-datacloud-runtime`.
>
> **Troubleshooting:** if a Data Cloud runtime clone error mentions `gthoppae/sf-cli-plugin-data360`, your local installer copy is stale. First refresh it with `python3 ~/.claude/sf-skills-install.py --force-update`, then rerun `python3 ~/.claude/sf-skills-install.py --with-datacloud-runtime`.

```bash
python3 ~/.claude/sf-skills-install.py --status                  # Check version and install state
python3 ~/.claude/sf-skills-install.py --update                  # Update to latest
python3 ~/.claude/sf-skills-install.py --force-update            # Reinstall even if already current
python3 ~/.claude/sf-skills-install.py --with-datacloud-runtime  # Install optional Data Cloud runtime
python3 ~/.claude/sf-skills-install.py --diagnose                # Run installer diagnostics
python3 ~/.claude/sf-skills-install.py --restore-settings        # Restore settings.json from backup
python3 ~/.claude/sf-skills-install.py --cleanup                 # Clean legacy artifacts
python3 ~/.claude/sf-skills-install.py --uninstall               # Remove everything installed by sf-skills
python3 ~/.claude/sf-skills-install.py --dry-run                 # Preview without applying
```

### Installer Profiles

```bash
python3 ~/.claude/sf-skills-install.py --profile list
python3 ~/.claude/sf-skills-install.py --profile save personal
python3 ~/.claude/sf-skills-install.py --profile use enterprise
python3 ~/.claude/sf-skills-install.py --profile show enterprise
python3 ~/.claude/sf-skills-install.py --profile delete old
```

> **Upgrading from `npx` to install.py?** Just run the installer command above — it auto-detects and migrates.

### What Gets Installed (install.py only)

```
~/.claude/
├── skills/                    # 36 Salesforce skills
│   ├── sf-apex/SKILL.md
│   ├── sf-flow/SKILL.md
│   └── ... (33 more)
├── agents/                    # 7 FDE + PS agents
│   ├── fde-strategist.md
│   ├── fde-engineer.md
│   └── ... (5 more)
├── hooks/                     # Shared hook system and registry
│   ├── scripts/
│   └── skills-registry.json
├── lsp-engine/                # LSP wrappers (Apex, LWC, AgentScript)
├── .sf-skills.json            # Version + metadata
└── sf-skills-install.py       # Installer for updates
```

**Active hook lifecycle:**

| Event | Matcher | Hook Type | What it does |
|------|---------|-----------|----------|
| **SessionStart** | — | command | Session directory lifecycle (session-init.py) |
| **PreToolUse** | Bash\|MCP | prompt (Haiku) | Advisory guardrails: sfdx deprecation, old API versions |
| **PreToolUse** | Bash | command | SOQL schema validator: JIT sf sobject describe before queries |
| **PostToolUse** | Write\|Edit | command | Validator dispatcher → Prettier + LSP + Scorer + Code Analyzer |
| **PostToolUse** | Bash | agent (Haiku) | Debug log analysis: exceptions, governor limits, hotspots |

For deeper install and hook internals, see [tools/README.md](tools/README.md) and [shared/hooks/README.md](shared/hooks/README.md).

<a id="claude-code-features"></a>

## ⚙️ Claude Code Features

### 💡 Auto-Activation

Skills are available as slash commands (for example `/sf-apex`, `/sf-flow`, `/sf-ai-agentscript`). Claude can also select the appropriate skill dynamically from your request context — keywords, intent, and file patterns in `shared/hooks/skills-registry.json` document what each skill is best at.

---

### Automatic Validation Hooks

Each skill includes validation hooks that run automatically on **Write** and **Edit** operations:

| | Skill | File Type | Validation |
|--|-------|-----------|------------|
| ⚡ | sf-apex | `*.cls`, `*.trigger` | Prettier auto-format + LSP compilation + 90-pt scorer + Code Analyzer PMD |
| 🔄 | sf-flow | `*.flow-meta.xml` | 110-pt scoring + Code Analyzer Flow Scanner |
| ⚡ | sf-lwc | `*.js` (LWC) | LWC LSP + 165-pt SLDS scorer + Code Analyzer ESLint + retire-js |
| ⚡ | sf-lwc | `*.html` (LWC) | Template anti-pattern validation (directives, expressions, LLM mistakes) |
| 🔍 | sf-soql | `*.soql` | 100-pt scoring + Live Query Plan API |
| 📋 | sf-metadata | `*.object-meta.xml`, `*.field-meta.xml`, `*.permissionset-meta.xml` | Metadata best practices |
| 🤖 | sf-ai-agentscript | `*.agent` | Agent Script syntax + LSP auto-fix loop |
| 🔗 | sf-integration | `*.namedCredential-meta.xml` | Integration pattern validation |


<details>
<summary><b>Validator Dispatcher Architecture</b></summary>

All PostToolUse validations are routed through a central dispatcher (`shared/hooks/scripts/validator-dispatcher.py`) that receives file paths from Write/Edit hook context, matches file patterns to determine which validators to run, and returns combined validation output.

**Routing Table:**

| Pattern | Skill | Validators | Timeout |
|---------|-------|------------|---------|
| `*.cls`, `*.trigger` | sf-apex | prettier-format.py (auto-format) | 10s |
| `*.cls`, `*.trigger` | sf-apex | apex-lsp-validate.py (LSP compilation) | 30s |
| `*.cls`, `*.trigger` | sf-apex | post-tool-validate.py (90-pt scorer + PMD) | 30s |
| `*.agent` | sf-ai-agentscript | agentscript-syntax-validator.py | 10s |
| `*.soql` | sf-soql | post-tool-validate.py | 10s |
| `*.flow-meta.xml` | sf-flow | post-tool-validate.py (110-pt + Flow Scanner) | 10s |
| `/lwc/**/*.js` | sf-lwc | lwc-lsp-validate.py + post-tool-validate.py | 30s |
| `/lwc/**/*.html` | sf-lwc | template_validator.py | 10s |
| `*.object-meta.xml` | sf-metadata | validate_metadata.py | 10s |
| `*.field-meta.xml` | sf-metadata | validate_metadata.py | 10s |
| `*.permissionset-meta.xml` | sf-metadata | validate_metadata.py | 10s |
| `*.namedCredential-meta.xml` | sf-integration | validate_integration.py | 10s |

</details>

<details>
<summary><b>Code Analyzer V5 Integration</b></summary>

Hooks integrate [Salesforce Code Analyzer V5](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer) for OOTB linting alongside custom scoring:

| Engine | What It Checks | Dependency |
|--------|----------------|------------|
| **PMD** | 55 Apex rules (85% coverage) — security, bulkification, complexity, testing | Java 11+ |
| **SFGE** | Data flow analysis, path-based security | Java 11+ |
| **Regex** | Trailing whitespace, hardcoded patterns | None |
| **ESLint** | JavaScript/LWC linting | Node.js |
| **Flow Scanner** | Flow best practices | Python 3.10+ |

**Custom Validation Coverage (no overlap with Code Analyzer):**
| Validator | Score | Categories (what PMD/ESLint doesn't cover) |
|-----------|-------|---------------------------------------------|
| **Apex** (90-pt) | 5 categories | Testing (25), Architecture (20), Clean Code (20), Error Handling (15), Performance (10) |
| **Flow** (110-pt) | 6 categories | Design/Naming, Logic/Structure, Error Handling, Architecture, Security, Performance |
| **LWC** (165-pt) | 9 categories | SLDS 2 Class Usage, Accessibility, Dark Mode, SLDS Migration, Styling Hooks, Component Structure, Performance, GraphQL Patterns, Focus Management |

**Graceful Degradation:** If dependencies are missing, hooks run custom validation only and show which engines were skipped.

</details>

<details>
<summary><b>Live SOQL Query Plan Analysis</b></summary>

Skills integrate with Salesforce's **REST API explain endpoint** to provide real-time query plan analysis.

**Sample Output:**
```
🌐 Live Query Plan Analysis (Org: my-dev-org)
   L42: ✅ Cost 0.3 (Index)
   L78: ⚠️ Cost 2.1 (TableScan) ⚠️ IN LOOP
      📝 Field Status__c is not indexed
```

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **relativeCost** | Query selectivity score | ≤1.0 = selective ✅, >1.0 = non-selective ⚠️ |
| **leadingOperationType** | How Salesforce executes the query | Index, TableScan, Sharing |
| **cardinality** | Estimated rows returned | vs. total records in object |
| **notes[]** | WHY optimizations aren't being used | Index suggestions, filter issues |

**Skills with Live Query Plan:** sf-soql (`.soql` files), sf-apex (`.cls`, `.trigger` — inline SOQL), sf-data (`.soql` for data operations).

**Prerequisites:** Connected Salesforce org (`sf org login web`). Falls back to static analysis if no org connected.

</details>

### 🔤 Language Server Protocol (LSP) Integration

Skills leverage official Salesforce LSP servers for real-time syntax validation with auto-fix loops:

| | Skill | File Type | LSP Server | Runtime |
|--|-------|-----------|------------|---------|
| 🤖 | sf-ai-agentscript | `*.agent` | Agent Script Language Server | Node.js 18+ |
| ⚡ | sf-apex | `*.cls`, `*.trigger` | apex-jorje-lsp.jar | Java 11+ |
| ⚡ | sf-lwc | `*.js`, `*.html` | @salesforce/lwc-language-server | Node.js 18+ |

**How Auto-Fix Loops Work:**
1. Claude writes/edits a file
2. LSP hook validates syntax (~500ms)
3. If errors found → Claude receives diagnostics and auto-fixes
4. Repeat up to 3 attempts

**Prerequisites:** See LSP table in Prerequisites section. LWC uses a standalone npm package; Apex and Agent Script use official extension-bundled language-server artifacts.

Hooks provide **advisory feedback** — they inform but don't block operations.

<a id="agent-team"></a>

## 🤖 Agent Team

Seven specialized Claude Code agents for Salesforce implementations, installed to `~/.claude/agents/`.

### FDE Team (Agent-Focused)

| Agent | Role | Mode | Key Skills |
|-------|------|------|------------|
| **fde-strategist** | Orchestrator — plans, researches, delegates | `plan` | sf-ai-agentforce, sf-diagram-mermaid |
| **fde-engineer** | Agent config, metadata, Apex, Agent Scripts | `acceptEdits` | sf-ai-agentforce, sf-ai-agentscript |
| **fde-experience-specialist** | Conversation design, persona, UX, LWC | `acceptEdits` | sf-ai-agentforce-persona, sf-lwc |

### Cross-Cutting (Serve Both Teams)

| Agent | Role | Mode | Key Skills |
|-------|------|------|------------|
| **fde-qa-engineer** | Testing (agent + platform), debug, observability | `acceptEdits` | sf-testing, sf-ai-agentforce-testing |
| **fde-release-engineer** | Deployment, Connected Apps, CI/CD | `acceptEdits` | sf-deploy, sf-connected-apps |

### PS Team (Platform Infrastructure)

| Agent | Role | Mode | Key Skills |
|-------|------|------|------------|
| **ps-technical-architect** | Apex, integrations, data, LWC, performance | `acceptEdits` | sf-apex, sf-integration, sf-lwc + 5 more |
| **ps-solution-architect** | Metadata, Flows, permissions, diagrams | `acceptEdits` | sf-metadata, sf-flow, sf-permissions + 2 more |

### Hierarchy

```
fde-strategist (orchestrator — plans, researches, delegates)
├── FDE: fde-engineer, fde-experience-specialist
├── QA/Release: fde-qa-engineer, fde-release-engineer
└── PS: ps-technical-architect, ps-solution-architect
```

The strategist spawns up to 4 concurrent workers via `Task()`. PS agents have `WebSearch` and `WebFetch` for self-directed Salesforce docs lookup.

<a id="skill-architecture"></a>

## 🔗 Skill Architecture

This is the working mental model for the ecosystem: foundation and integration skills support build work, quality skills reinforce delivery, AI skills cluster around Agentforce workflows, and `sf-deploy` carries finished assets across environments.

<p align="center">
  <img src="docs/assets/skill-capability-map-v3.svg" width="100%" alt="SF Skills capability map showing AI & Automation at the top, Development and Integration in the middle, Quality before delivery, separate DevOps and Diagrams sections, and Foundation at the base" />
</p>

- **AI & Automation** sits at the top, centered on Agentforce workflows.
- **Development + Integration** occupy the middle of the map where most implementation work happens.
- **Quality** sits after build work and before delivery.
- **DevOps** is separated for release and deployment automation.
- **Diagrams** is separated for Mermaid and premium visual artifact generation.
- **Foundation** anchors the base with metadata, data, and permissions context.

> **Why SVG instead of Mermaid here?** GitHub renders larger Mermaid graphs very small. A custom SVG keeps labels crisp, gives us better spacing, and reads more like a clean capability map than a dense dependency graph.
>
> **Deployment path:** use [sf-deploy](skills/sf-deploy/) for Salesforce deployments across Apex, Flow, LWC, metadata, and Agentforce assets. For local browser viewing, a standalone companion lives at `docs/assets/skill-ecosystem-overview.html` and now uses the refreshed `skill-capability-map-v3.svg` asset.

## 🎬 Video Tutorials

| Video | Description |
|-------|-------------|
| [How to Add/Install Skills](https://youtu.be/a38MM8PBTe4) | Install the sf-skills marketplace and add skills to Claude Code |
| [Skills Demo & Walkthrough](https://www.youtube.com/watch?v=gW2RP96jdBc) | Live demo of Apex, Flow, Metadata, and Agentforce skills in action |

## 🔧 Prerequisites

### Cross-CLI minimum

- **Node.js 18+** — required for `npx skills add`

### Claude Code full install

- **Claude Code** (latest version)
- **Salesforce CLI** v2.x (`sf` command) — `npm install -g @salesforce/cli`
- **Python 3.10+** — for hooks, validation, and installer tooling
- **Authenticated Salesforce Org** — DevHub, Sandbox, or Scratch Org
- **sfdx-project.json** — standard DX project structure

### API Version Requirements

| Skills | Minimum API | Notes |
|--------|-------------|-------|
| Most skills | **62.0** (Winter '25) | sf-apex, sf-flow, sf-lwc, sf-metadata |
| sf-connected-apps, sf-integration | **61.0** | External Client Apps |
| sf-ai-agentforce | **66.0** (Spring '26) | Full agent deployment, GenAiPlannerBundle |

### Optional dependencies (enable richer validation / LSP features)

*Data Cloud family runtime (`sf-datacloud-*`):*
- **Community `sf data360` CLI plugin** — external runtime required for the Data Cloud family
- **Setup guide** — see `skills/sf-datacloud/references/plugin-setup.md`
- **Bootstrap helper** — `bash ~/.claude/skills/sf-datacloud/scripts/bootstrap-plugin.sh`


*Code Analyzer V5 engines:*
- **Java 11+** — Enables PMD, CPD, SFGE engines (`brew install openjdk@11`)
- **Node.js 18+** — Enables ESLint, RetireJS for LWC (`brew install node`)
- **Code Analyzer plugin** — `sf plugins install @salesforce/sfdx-code-analyzer`

*LWC Testing & Linting:*
- **@salesforce/sfdx-lwc-jest** — Jest testing for LWC (`npm install @salesforce/sfdx-lwc-jest --save-dev`)
- **@salesforce-ux/slds-linter** — SLDS validation (`npm install -g @salesforce-ux/slds-linter`)

*LSP real-time validation (auto-fix loops):*
- **LWC Language Server** — `npm install -g @salesforce/lwc-language-server` (standalone, no VS Code needed)
- **VS Code with Salesforce Extensions** — Official Salesforce extension artifacts are still the source of the Apex and Agent Script language servers. In this repository, VS Code Marketplace usage is optional from a workflow perspective; install those extensions only if you want the bundled language-server binaries locally.
  - Apex: Install "Salesforce Extension Pack" (Java JAR bundled in extension)
  - Agent Script: Install "Salesforce Agent Script" extension (server.js bundled in extension)
- **Java 11+** — Required for Apex LSP (same as Code Analyzer)
- **Node.js 18+** — Required for Agent Script and LWC LSP

| LSP | Standalone npm? | VS Code Required? |
|-----|-----------------|-------------------|
| LWC | ✅ `@salesforce/lwc-language-server` | ❌ No |
| Apex | ❌ No (Java JAR) | ✅ Yes |
| Agent Script | ❌ No | ✅ Yes |

*Apex Development:*
- **Trigger Actions Framework (TAF)** — Optional package for sf-apex trigger patterns
  - Package ID: `04tKZ000000gUEFYA2` or [GitHub repo](https://github.com/mitchspano/trigger-actions-framework)

<details>
<summary><h2>💬 Usage Examples</h2></summary>

### ⚡ Apex Development
```
"Generate an Apex trigger for Account using Trigger Actions Framework"
"Review my AccountService class for best practices"
"Create a batch job to process millions of records"
"Generate a test class with 90%+ coverage"
```

### 🔄 Flow Development
```
"Create a screen flow for account creation with validation"
"Build a record-triggered flow for opportunity stage changes"
"Generate a scheduled flow for data cleanup"
```

### 📋 Metadata Management
```
"Create a custom object called Invoice with auto-number name field"
"Add a lookup field from Contact to Account"
"Generate a permission set for invoice managers with full CRUD"
"Create a validation rule to require close date when status is Closed"
"Describe the Account object in my org and list all custom fields"
```

### 💾 Data Operations
```
"Query all Accounts with related Contacts and Opportunities"
"Create 251 test Account records for trigger bulk testing"
"Insert 500 records from accounts.csv using Bulk API"
"Generate test data hierarchy: 10 Accounts with 3 Contacts each"
"Clean up all test records created today"
```

### ⚡ LWC Development
```
"Create a datatable component to display Accounts with sorting"
"Build a form component for creating new Contacts"
"Generate a Jest test for my accountCard component"
"Create an Apex controller with @AuraEnabled methods for my LWC"
"Set up Lightning Message Service for cross-component communication"
```

### 🔍 SOQL Queries
```
"Query all Accounts with more than 5 Contacts"
"Get Opportunities by Stage with total Amount per Stage"
"Find Contacts without Email addresses"
"Optimize this query: SELECT * FROM Account WHERE Name LIKE '%Corp%'"
"Generate a SOQL query to find duplicate Leads by Email"
```

### 🧪 Testing
```
"Run all Apex tests in my org and show coverage"
"Generate a test class for my AccountTriggerHandler"
"Create a bulk test with 251 records for trigger testing"
"Generate mock classes for HTTP callouts"
"Run tests for a specific class and show failures"
```

### 🐛 Debugging
```
"Analyze this debug log for performance issues"
"Find governor limit violations in my log"
"What's causing this SOQL in loop error?"
"Show me how to fix this null pointer exception"
"Optimize my Apex for CPU time limits"
```

### 🔐 Connected Apps & OAuth
```
"Create a Connected App for API integration with JWT Bearer flow"
"Generate an External Client App for our mobile application with PKCE"
"Review my Connected Apps for security best practices"
"Migrate MyConnectedApp to an External Client App"
```

### 🔗 Integration & Callouts
```
"Create a Named Credential for Stripe API with OAuth client credentials"
"Generate a REST callout service with retry and error handling"
"Create a Platform Event for order synchronization"
"Build a CDC subscriber trigger for Account changes"
"Set up an External Service from an OpenAPI spec"
```

### 🤖 Agentforce Agents & Actions
```
"Create an Agentforce agent for customer support triage"
"Build a FAQ agent with topic-based routing"
"Generate an agent that calls my Apex service via Flow wrapper"
"Create a GenAiFunction for my @InvocableMethod Apex class"
"Build an agent action that calls the Stripe API"
"Generate a PromptTemplate for case summaries"
```

### 💰 Flex Credit Estimation
```
"Estimate Flex Credits for an Agentforce agent with 3 standard prompts and 5 actions"
"Compare low, medium, and enterprise monthly costs for this Agentforce + Data Cloud design"
"How much does Private Connect add to this Data Cloud estimate?"
"Show me the biggest cost drivers in this proposed agent architecture"
"Generate a public list-price Flex Credit estimate for this rollout"
```

### ☁️ Data Cloud
```
"Set up a Data Cloud pipeline from CRM ingestion to unified profiles"
"Show me which Data Cloud connections and streams already exist in my org"
"Map this DLO to ssot__Individual__dlm and create an identity resolution ruleset"
"Create and publish a high-value customer segment in Data Cloud"
"Run a Data Cloud SQL query and describe the table before I build segment logic"
"Help me bootstrap the external sf data360 plugin required for the sf-datacloud family"
```

### 📈 Agent Observability & Trace Analysis
```
"Capture Builder traces for this agent test run and summarize routing issues"
"Analyze this Agentforce session trace for topic/action drift"
"Run trace-test against my agent and suggest Agent Script fixes"
```

### 📊 Diagrams & Documentation
```
"Create a JWT Bearer OAuth flow diagram"
"Generate an ERD for Account, Contact, Opportunity, and Case"
"Diagram our Salesforce to SAP integration flow"
"Create a system landscape diagram for our Sales Cloud implementation"
"Generate a role hierarchy diagram for our sales org"
```

### 🚀 Deployment
```
"Deploy my Apex classes to sandbox with tests"
"Validate my metadata changes before deploying to production"
```

</details>

<details>
<summary><h2>🤖 Supported Agentic Coding Tools</h2></summary>

### CLI Compatibility

All skills follow the [Agent Skills open standard](https://agentskills.io). Install with `npx skills add` for any supported agent:

```bash
npx skills add Jaganpro/sf-skills
```

| Tool | Status | Install Method | |
|------|--------|----------------|--|
| **Claude Code CLI** | ✅ Full Support | `npx skills add` or bash installer | ![Claude](https://img.shields.io/badge/Anthropic-Claude_Code-191919?logo=anthropic&logoColor=white) |
| **OpenCode CLI** | ✅ Compatible | `npx skills add` | ![OpenCode](https://img.shields.io/badge/Open-Code-4B32C3?logo=github&logoColor=white) |
| **Codex CLI** | ✅ Compatible | `npx skills add` | ![OpenAI](https://img.shields.io/badge/OpenAI-Codex-412991?logo=openai&logoColor=white) |
| **Gemini CLI** | ✅ Compatible | `npx skills add` | ![Google](https://img.shields.io/badge/Google-Gemini_CLI-4285F4?logo=google&logoColor=white) |
| **Amp CLI** | ✅ Compatible | `npx skills add` or `.claude/skills/` | ![Amp](https://img.shields.io/badge/Sourcegraph-Amp-FF5543?logo=sourcegraph&logoColor=white) |
| **Droid CLI** | ✅ Compatible | `npx skills add` | ![Factory](https://img.shields.io/badge/Factory.ai-Droid-6366F1?logo=robot&logoColor=white) |

> 🤝 **Call for Volunteers!** This repo is community-driven. We need testers on different CLIs — [open an issue](https://github.com/Jaganpro/sf-skills/issues) to get started.

</details>

<details>
<summary><h2>🗺️ Roadmap</h2></summary>

### Naming Convention
```
sf-{capability}           # Cross-cutting (apex, flow, admin)
sf-ai-{name}              # AI features (agentforce, copilot)
sf-datacloud-{phase}      # Data Cloud family (connect, prepare, harmonize, segment, act, retrieve)
sf-cloud-{name}           # Clouds (sales, service)
sf-industry-{name}        # Industries (healthcare, finserv)
sf-industry-commoncore-{name}  # Industries Common Core (omnistudio)
```

### 🔧 Cross-Cutting Skills
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 🔐 | `sf-connected-apps` | Connected Apps, ECAs, OAuth configuration | ✅ Live |
| 🔗 | `sf-integration` | Named Credentials, External Services, REST/SOAP, Platform Events, CDC | ✅ Live |
| 📊 | `sf-diagram-mermaid` | Mermaid diagrams for OAuth, ERD, integrations, architecture | ✅ Live |
| ⚡ | `sf-lwc` | Lightning Web Components, Jest, LMS | ✅ Live |
| 🔍 | `sf-soql` | Natural language to SOQL, optimization | ✅ Live |
| 🧪 | `sf-testing` | Test execution, coverage, bulk testing | ✅ Live |
| 🐛 | `sf-debug` | Debug log analysis, governor fixes | ✅ Live |
| 📸 | `sf-diagram-nanobananapro` | Visual ERD, LWC mockups, Gemini sub-agent | ✅ Live |
| 📚 | `sf-docs` | Official Salesforce docs retrieval guidance for hard-to-fetch online Salesforce documentation | ✅ Live |
| 🔐 | `sf-permissions` | Permission Set analysis, hierarchy viewer, "Who has X?" | ✅ Live |
| 🔒 | `sf-security` | Sharing rules, org-wide defaults, encryption | 📋 Planned |
| 📦 | `sf-migration` | Org-to-org, metadata comparison | 📋 Planned |

### 💰 Planning & Estimation
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 💰 | `sf-flex-estimator` | Public list-price Flex Credit estimation, scenario planning, and cost optimization for Agentforce and Data Cloud | ✅ Live |

### 🤖 AI & Automation
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 🤖 | `sf-ai-agentforce` | Agent Builder, PromptTemplate, Models API, GenAi metadata | ✅ Live |
| 🧪 | `sf-ai-agentforce-testing` | Agent test specs, agentic fix loops | ✅ Live |
| 📈 | `sf-ai-agentforce-observability` | STDM + Builder trace capture, trace-test, and execution analysis | ✅ Live |
| 📝 | `sf-ai-agentscript` | Agent Script DSL, FSM patterns, 100-pt scoring | ✅ Live |
| 💬 | `sf-ai-agentforce-persona` | Deep persona design, identity framework, Agent Builder encoding | ✅ Live |
| 🔲 | `sf-ai-agentforce-grid` | Agentforce Grid (AI Workbench) workbooks, worksheets, column design, `apply_grid` YAML, and Grid MCP/REST workflows | ✅ Live |
| 🧠 | `sf-ai-copilot` | Einstein Copilot, Prompts | 📋 Planned |
| 🔮 | `sf-ai-einstein` | Prediction Builder, NBA | 📋 Planned |

### ☁️ Data Cloud
| | Skill | Description | Status |
|--|-------|-------------|--------|
| ☁️ | `sf-datacloud` | Cross-phase Data Cloud orchestration, data spaces, data kits, and plugin verification | ✅ Live |
| 🔌 | `sf-datacloud-connect` | Connections, connectors, and source discovery | ✅ Live |
| 🧰 | `sf-datacloud-prepare` | Data streams, DLOs, transforms, and DocAI ingestion workflows | ✅ Live |
| 🧬 | `sf-datacloud-harmonize` | DMOs, mappings, identity resolution, unified profiles, and data graphs | ✅ Live |
| 🎯 | `sf-datacloud-segment` | Segments, calculated insights, and audience troubleshooting | ✅ Live |
| 📤 | `sf-datacloud-act` | Activations, activation targets, and data actions | ✅ Live |
| 🔎 | `sf-datacloud-retrieve` | SQL, async query, vector search, and search indexes | ✅ Live |

### ☁️ Clouds
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 💰 | `sf-cloud-sales` | Opportunities, Quotes, Forecasting | 📋 Planned |
| 🎧 | `sf-cloud-service` | Cases, Omni-Channel, Knowledge | 📋 Planned |
| 🌐 | `sf-cloud-experience` | Communities, Portals | 📋 Planned |

### 🏢 Industries Common Core
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 🔍 | `sf-industry-commoncore-omnistudio-analyze` | Namespace detection, dependency mapping, impact analysis | ✅ Live |
| 📊 | `sf-industry-commoncore-datamapper` | Data Mapper (DataRaptor) creation, 100-pt scoring | ✅ Live |
| 🔗 | `sf-industry-commoncore-integration-procedure` | Integration Procedure orchestration, 110-pt scoring | ✅ Live |
| ⚙️ | `sf-industry-commoncore-callable-apex` | System.Callable generation/review and Open Interface migration patterns | ✅ Live |
| 📝 | `sf-industry-commoncore-omniscript` | OmniScript guided experiences, 120-pt scoring | ✅ Live |
| 🃏 | `sf-industry-commoncore-flexcard` | FlexCard UI components, 130-pt scoring | ✅ Live |
| 🧱 | `sf-industry-cme-epc-model` | CME EPC Product2 modeling for products, attributes, and offer bundles | ✅ Live |

### 🏢 Industries
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 🏥 | `sf-industry-healthcare` | FHIR, Care Plans, Compliance | 📋 Planned |
| 🏦 | `sf-industry-finserv` | KYC, AML, Wealth Management | 📋 Planned |
| 💵 | `sf-industry-revenue` | CPQ, Billing, Revenue Lifecycle | 📋 Planned |

**Current repo state:** 36 live skills today, with additional cloud, security, AI, and industry roadmap items still planned.

</details>

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally: `python3 tools/install.py --dry-run`
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Contributors

| Contributor | Area | Skills |
|---|---|---|
| [August Krys](https://github.com/not2technical) | Agentforce metadata modernization, metadata/FLS improvements, data/deploy workflow updates, and primary contribution for Flex Credit estimation ([repo](https://github.com/not2technical/sf-skills)) | sf-ai-agentforce, sf-ai-agentscript, sf-metadata, sf-data, sf-deploy, sf-flex-estimator |
| [Gnanasekaran Thoppae](https://github.com/gthoppae) | Data Cloud product family | sf-datacloud, sf-datacloud-connect, sf-datacloud-prepare, sf-datacloud-harmonize, sf-datacloud-segment, sf-datacloud-act, sf-datacloud-retrieve |
| [David Ryan (weytani)](https://github.com/weytani) | Industries Common Core | sf-industry-commoncore-omnistudio-analyze, sf-industry-commoncore-datamapper, sf-industry-commoncore-integration-procedure, sf-industry-commoncore-omniscript, sf-industry-commoncore-flexcard |
| [Shreyas Dhond, CTA (ShreyasD)](https://github.com/ShreyasD) | Primary contributor — Industries Common Core callable Apex | sf-industry-commoncore-callable-apex |
| [Shreyas Dhond, CTA (ShreyasD)](https://github.com/ShreyasD) | Primary contributor — Industries CME EPC modeling | sf-industry-cme-epc-model |

## Issues & Support

- [GitHub Issues](https://github.com/Jaganpro/sf-skills/issues)

## License

MIT License - Copyright (c) 2024-2026 Jag Valaiyapathy
