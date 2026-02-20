# Salesforce Skills for Agentic Coding Tools

> 💙 **Community-powered agentic coding knowledge, shared by a Salesforce Certified Technical Architect (CTA)**

[![Author](https://img.shields.io/badge/Author-Jag_Valaiyapathy-blue?logo=github)](https://github.com/Jaganpro)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A collection of reusable skills for **Agentic Salesforce Development**, enabling AI-powered code generation, validation, testing, debugging, and deployment. Compatible with any AI coding agent via the [Agent Skills open standard](https://agentskills.io).

---

## ✨ Available Skills

### 💻 Development

- **[sf-apex](skills/sf-apex/)** — Apex generation, TAF patterns, LSP validation
- **[sf-flow](skills/sf-flow/)** — Flow creation & bulk validation
- **[sf-lwc](skills/sf-lwc/)** — Lightning Web Components, Jest tests, LMS
- **[sf-soql](skills/sf-soql/)** — Natural language → SOQL, query optimization

### 🧪 Quality

- **[sf-testing](skills/sf-testing/)** — Apex test runner, coverage, bulk testing
- **[sf-debug](skills/sf-debug/)** — Debug log analysis, governor limit fixes

### 📦 Foundation

- **[sf-metadata](skills/sf-metadata/)** — Metadata gen & org queries
- **[sf-data](skills/sf-data/)** — SOQL & test data factories
- **[sf-permissions](skills/sf-permissions/)** — Permission Set analysis, "Who has X?"

### 🔌 Integration

- **[sf-connected-apps](skills/sf-connected-apps/)** — OAuth apps & ECAs
- **[sf-integration](skills/sf-integration/)** — Callouts, Events, CDC

### 🤖 AI & Automation

- **[sf-ai-agentscript](skills/sf-ai-agentscript/)** — Agent Script DSL, FSM patterns
- **[sf-ai-agentforce-conversationdesign](skills/sf-ai-agentforce-conversationdesign/)** — Persona docs, utterance libraries, guardrails
- **[sf-ai-agentforce-observability](skills/sf-ai-agentforce-observability/)** — Session tracing (Data Cloud)
- **[sf-ai-agentforce-testing](skills/sf-ai-agentforce-testing/)** — Agent test specs, agentic fix loops
- **[sf-ai-agentforce](skills/sf-ai-agentforce/)** — Agent Builder, PromptTemplate, Models API

### 🛠️ DevOps & Tooling

- **[sf-deploy](skills/sf-deploy/)** — CI/CD automation (sf CLI v2)
- **[sf-diagram-mermaid](skills/sf-diagram-mermaid/)** — Mermaid diagrams & ERD
- **[sf-diagram-nanobananapro](skills/sf-diagram-nanobananapro/)** — Visual ERD, LWC mockups

## 🤖 Agent Team

Seven specialized Claude Code agents for Salesforce implementations, installed to `~/.claude/agents/`.

### FDE Team (Agent-Focused)

| Agent | Role | Mode | Key Skills |
|-------|------|------|------------|
| **fde-strategist** | Orchestrator — plans, researches, delegates | `plan` | sf-ai-agentforce, sf-diagram-mermaid |
| **fde-engineer** | Agent config, metadata, Apex, Agent Scripts | `acceptEdits` | sf-ai-agentforce, sf-ai-agentscript |
| **fde-experience-specialist** | Conversation design, persona, UX, LWC | `acceptEdits` | sf-ai-agentforce-conversationdesign, sf-lwc |

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

## 🚀 Installation

### Any AI Coding Agent

> Requires [Node.js 18+](https://nodejs.org/) (provides the `npx` command)

```bash
npx skills add github:Jaganpro/sf-skills
```

Works with Claude Code, Codex, Gemini CLI, OpenCode, Amp, and [40+ agents](https://agentskills.io).

```bash
# Install a single skill
npx skills add github:Jaganpro/sf-skills --skill sf-apex

# List available skills before installing
npx skills add github:Jaganpro/sf-skills --list
```

### Claude Code (Full Experience)

> **Using Claude Code?** This path is recommended — npx installs skills only, while install.py adds hooks, agents, LSP, and guardrails.

```bash
curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.sh | bash
```

Adds 19 skills + 7 agents + 11 hook scripts + LSP engine. Includes guardrails, auto-validation on Write/Edit, and org preflight checks.

**Restart Claude Code** after installation.

### Updating

| Install Method | Check for Updates | Update |
|----------------|-------------------|--------|
| **npx** | `npx skills check` | `npx skills update` |
| **install.py** | `python3 ~/.claude/sf-skills-install.py --status` | `python3 ~/.claude/sf-skills-install.py --update` |

### Managing install.py

```bash
python3 ~/.claude/sf-skills-install.py --status       # Check version
python3 ~/.claude/sf-skills-install.py --update        # Update to latest
python3 ~/.claude/sf-skills-install.py --uninstall     # Remove everything
python3 ~/.claude/sf-skills-install.py --cleanup       # Clean legacy artifacts
python3 ~/.claude/sf-skills-install.py --dry-run       # Preview without applying
```

> **Upgrading from npx to install.py?** Just run the curl command above — it auto-detects and migrates.

### What Gets Installed (install.py only)

```
~/.claude/
├── skills/                    # 19 Salesforce skills
│   ├── sf-apex/SKILL.md
│   ├── sf-flow/SKILL.md
│   └── ... (17 more)
├── agents/                    # 7 FDE + PS agents
│   ├── fde-strategist.md
│   ├── fde-engineer.md
│   └── ... (5 more)
├── hooks/                     # 11 hook scripts
│   ├── scripts/
│   └── skills-registry.json
├── lsp-engine/                # LSP wrappers (Apex, LWC, AgentScript)
├── .sf-skills.json            # Version + metadata
└── sf-skills-install.py       # Installer for updates
```

**What hooks provide:**

| Hook | Function |
|------|----------|
| **SessionStart** | Initializes session, preflights org connection, warms LSP servers |
| **PreToolUse** | Guardrails — blocks dangerous DML, auto-fixes unbounded SOQL |
| **PostToolUse** | Validates Apex/Flow/LWC on save |
| **PermissionRequest** | Auto-approves safe operations (read queries, scratch deploys) |

## 🎬 Video Tutorials

| Video | Description |
|-------|-------------|
| [How to Add/Install Skills](https://youtu.be/a38MM8PBTe4) | Install the sf-skills marketplace and add skills to Claude Code |
| [Skills Demo & Walkthrough](https://www.youtube.com/watch?v=gW2RP96jdBc) | Live demo of Apex, Flow, Metadata, and Agentforce skills in action |

## 🔗 Skill Architecture

![Skill Architecture Diagram](https://github.com/user-attachments/assets/dc5ada83-6555-4b40-8b46-5dce5f8851ad)

<details>
<summary><b>🚀 Deployment Note</b></summary>

**Use the sf-deploy skill for all Salesforce deployments:**

```
Use the sf-deploy skill: "Deploy to [org]"
```

</details>

## 🔌 Plugin Features

### 💡 Auto-Activation

Skills are available as slash commands (e.g., `/sf-apex`, `/sf-flow`). Claude dynamically selects the appropriate skill based on your request context — keywords, intent, and file patterns in `shared/hooks/skills-registry.json` serve as documentation for skill capabilities.

---

### Automatic Validation Hooks

Each skill includes validation hooks that run automatically on **Write** and **Edit** operations:

| | Skill | File Type | Validation |
|--|-------|-----------|------------|
| ⚡ | sf-apex | `*.cls`, `*.trigger` | 150-pt scoring + Code Analyzer + LSP |
| 🔄 | sf-flow | `*.flow-meta.xml` | 110-pt scoring + Flow Scanner |
| ⚡ | sf-lwc | `*.js` (LWC) | 140-pt scoring + LSP syntax validation |
| ⚡ | sf-lwc | `*.html` (LWC) | Template validation (directives, expressions) |
| 🔍 | sf-soql | `*.soql` | 100-pt scoring + Live Query Plan API |
| 🧪 | sf-testing | `*Test.cls` | 100-pt scoring + coverage analysis |
| 🐛 | sf-debug | Debug logs | 90-pt scoring + governor analysis |
| 📋 | sf-metadata | `*.object-meta.xml`, `*.field-meta.xml`, `*.permissionset-meta.xml` | Metadata best practices |
| 💾 | sf-data | `*.apex`, `*.soql` | SOQL patterns + Live Query Plan |
| 🤖 | sf-ai-agentscript | `*.agent` | Agent Script syntax + LSP auto-fix |
| 🧪 | sf-ai-agentforce-testing | Test spec YAML | 100-pt scoring + fix loops |
| 🔐 | sf-connected-apps | `*.connectedApp-meta.xml` | OAuth security validation |
| 🔗 | sf-integration | `*.namedCredential-meta.xml` | 120-pt scoring + callout patterns |
| 📸 | sf-diagram-nanobananapro | Generated images | Prerequisites check |


<details>
<summary><b>Validator Dispatcher Architecture</b></summary>

All PostToolUse validations are routed through a central dispatcher (`shared/hooks/scripts/validator-dispatcher.py`) that receives file paths from Write/Edit hook context, matches file patterns to determine which validators to run, and returns combined validation output.

**Routing Table:**

| Pattern | Skill | Validators |
|---------|-------|------------|
| `*.agent` | sf-ai-agentscript | agentscript-syntax-validator.py |
| `*.cls`, `*.trigger` | sf-apex | apex-lsp-validate.py + post-tool-validate.py |
| `*.flow-meta.xml` | sf-flow | post-tool-validate.py |
| `/lwc/**/*.js` | sf-lwc | lwc-lsp-validate.py + post-tool-validate.py |
| `/lwc/**/*.html` | sf-lwc | template_validator.py |
| `*.object-meta.xml` | sf-metadata | validate_metadata.py |
| `*.field-meta.xml` | sf-metadata | validate_metadata.py |
| `*.permissionset-meta.xml` | sf-metadata | validate_metadata.py |
| `*.namedCredential-meta.xml` | sf-integration | validate_integration.py |
| `*.soql` | sf-soql | post-tool-validate.py |
| `SKILL.md` | (removed) | — |

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

**Custom Validation Coverage:**
| Validator | Total Checks | Categories |
|-----------|--------------|------------|
| **Apex** (150-pt) | PMD 55 rules + Python 8 checks | Security (100%), Bulkification, Testing, Architecture, Clean Code, Error Handling, Performance, Documentation |
| **Flow** (110-pt) | 32+ checks (21/24 LFS rules) | Design/Naming, Logic/Structure, Error Handling, Architecture, Security, Performance |
| **LWC** (140-pt) | ESLint + retire-js + SLDS Linter | SLDS 2 Compliance, Naming, Accessibility, Component Patterns, Lightning Message Service, Security |

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

#### 🔤 Language Server Protocol (LSP) Integration

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

**Prerequisites:** See LSP table in Prerequisites section. LWC uses standalone npm package; Apex and Agent Script require VS Code extensions.

Hooks provide **advisory feedback** — they inform but don't block operations.

## 🔧 Prerequisites

**Required:**
- **Claude Code** (latest version)
- **Salesforce CLI** v2.x (`sf` command) — `npm install -g @salesforce/cli`
- **Python 3.10+** (for validation hooks)
- **Authenticated Salesforce Org** — DevHub, Sandbox, or Scratch Org
- **sfdx-project.json** — Standard DX project structure

**API Version Requirements:**
| Skills | Minimum API | Notes |
|--------|-------------|-------|
| Most skills | **62.0** (Winter '25) | sf-apex, sf-flow, sf-lwc, sf-metadata |
| sf-connected-apps, sf-integration | **61.0** | External Client Apps |
| sf-ai-agentforce | **65.0** (Winter '26) | Full agent deployment, GenAiPlannerBundle |

**Optional** (enables additional features):

*Code Analyzer V5 engines:*
- **Java 11+** — Enables PMD, CPD, SFGE engines (`brew install openjdk@11`)
- **Node.js 18+** — Enables ESLint, RetireJS for LWC (`brew install node`)
- **Code Analyzer plugin** — `sf plugins install @salesforce/sfdx-code-analyzer`

*LWC Testing & Linting:*
- **@salesforce/sfdx-lwc-jest** — Jest testing for LWC (`npm install @salesforce/sfdx-lwc-jest --save-dev`)
- **@salesforce-ux/slds-linter** — SLDS validation (`npm install -g @salesforce-ux/slds-linter`)

*LSP real-time validation (auto-fix loops):*
- **LWC Language Server** — `npm install -g @salesforce/lwc-language-server` (standalone, no VS Code needed)
- **VS Code with Salesforce Extensions** — Required for Apex and Agent Script only (no npm packages available)
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

### 🛠️ Skill Creation
```
"Create a new Claude Code skill for code analysis"
```

</details>

<details>
<summary><h2>🗺️ Roadmap</h2></summary>

### Naming Convention
```
sf-{capability}           # Cross-cutting (apex, flow, admin)
sf-ai-{name}              # AI features (agentforce, copilot)
sf-product-{name}         # Products (datacloud, omnistudio)
sf-cloud-{name}           # Clouds (sales, service)
sf-industry-{name}        # Industries (healthcare, finserv)
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
| 🔐 | `sf-permissions` | Permission Set analysis, hierarchy viewer, "Who has X?" | ✅ Live |
| 🔒 | `sf-security` | Sharing rules, org-wide defaults, encryption | 📋 Planned |
| 📦 | `sf-migration` | Org-to-org, metadata comparison | 📋 Planned |

### 🤖 AI & Automation
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 🤖 | `sf-ai-agentforce` | Agent Builder, PromptTemplate, Models API, GenAi metadata | ✅ Live |
| 🧪 | `sf-ai-agentforce-testing` | Agent test specs, agentic fix loops | ✅ Live |
| 📈 | `sf-ai-agentforce-observability` | Session tracing extraction & analysis (Data Cloud) | ✅ Live |
| 📝 | `sf-ai-agentscript` | Agent Script DSL, FSM patterns, 100-pt scoring | ✅ Live |
| 💬 | `sf-ai-agentforce-conversationdesign` | Persona docs, utterance libraries, guardrails | ✅ Live |
| 🧠 | `sf-ai-copilot` | Einstein Copilot, Prompts | 📋 Planned |
| 🔮 | `sf-ai-einstein` | Prediction Builder, NBA | 📋 Planned |

### 📦 Products
| | Skill | Description | Status |
|--|-------|-------------|--------|
| ☁️ | `sf-product-datacloud` | Unified profiles, segments | 📋 Planned |
| 🎨 | `sf-product-omnistudio` | FlexCards, DataRaptors | 📋 Planned |

### ☁️ Clouds
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 💰 | `sf-cloud-sales` | Opportunities, Quotes, Forecasting | 📋 Planned |
| 🎧 | `sf-cloud-service` | Cases, Omni-Channel, Knowledge | 📋 Planned |
| 🌐 | `sf-cloud-experience` | Communities, Portals | 📋 Planned |

### 🏢 Industries
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 🏥 | `sf-industry-healthcare` | FHIR, Care Plans, Compliance | 📋 Planned |
| 🏦 | `sf-industry-finserv` | KYC, AML, Wealth Management | 📋 Planned |
| 💵 | `sf-industry-revenue` | CPQ, Billing, Revenue Lifecycle | 📋 Planned |

**Total: 29 skills** (19 skills ✅ live, 10 planned 📋)

</details>

<details>
<summary><h2>🤖 Supported Agentic Coding Tools</h2></summary>

### CLI Compatibility

All skills follow the [Agent Skills open standard](https://agentskills.io). Install with `npx skills add` for any supported agent:

```bash
npx skills add github:Jaganpro/sf-skills
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally: `python3 tools/install.py --dry-run`
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Issues & Support

- [GitHub Issues](https://github.com/Jaganpro/sf-skills/issues)

## License

MIT License - Copyright (c) 2024-2026 Jag Valaiyapathy
