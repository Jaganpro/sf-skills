# Salesforce Skills for Agentic Coding Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue.svg)](https://claude.ai/code)
[![Salesforce](https://img.shields.io/badge/Salesforce-Apex%20%7C%20Flow%20%7C%20Metadata%20%7C%20Data%20%7C%20DevOps-00A1E0.svg)](https://www.salesforce.com/)

A collection of reusable skills for Salesforce development, specializing in Apex code generation, Flow automation, Metadata management, and DevOps workflows. Built for Claude Code with planned support for other agentic coding tools.

---

## 💡 What is a Skill?

> **Skills are portable knowledge packs that supercharge AI coding agents with domain expertise.**

Think of skills as "installable superpowers" for your agentic coding tool. Instead of repeatedly explaining Salesforce best practices to your AI assistant, a skill pre-loads that knowledge so the AI becomes an instant expert.

```
sf-apex/
├── SKILL.md              # 🧠 The brain - prompts & instructions
├── templates/            # 📁 Code templates & patterns
├── hooks/                # ✅ Validation scripts
└── examples/             # 📖 Usage examples
```

> 💡 **Tip:** Skills are open-source and composable. You can fork, customize, or create your own!

### Why Use Skills?

> 🚀 **Stop explaining Salesforce patterns. Start building.**

**1. Instant Expertise** — AI knows Trigger Actions Framework, Flow bulkification, deployment best practices from the first message.

**2. Automatic Validation** — Every Apex class, Flow, and agent script is scored against 100-150 point rubrics. Catch anti-patterns before deployment.

**3. Built-in Templates** — 50+ production-ready templates across Apex, Flow, Metadata, Agentforce, and more.

**4. Tool Orchestration** — "Deploy to production" becomes a single command. Skills handle `sf` CLI complexity.

**5. Context Efficiency** — Skills load only when invoked, saving ~2000 tokens per conversation vs. pasting prompts.

| Before | After |
|--------|-------|
| ❌ Prompt engineering every conversation | ✅ `Skill(skill="sf-apex")` |
| ❌ 10+ messages to explain requirements | ✅ 1 message, skill fills the gaps |
| ❌ Review code manually for issues | ✅ Hooks validate on every save |

---

## 🤖 Supported Agentic Coding Tools

| Tool | Status | |
|------|--------|--|
| **Claude Code CLI** | ✅ Full Support | ![Claude](https://img.shields.io/badge/Anthropic-Claude_Code-191919?logo=anthropic&logoColor=white) |
| **Amp CLI** | ✅ Compatible | ![Amp](https://img.shields.io/badge/Sourcegraph-Amp-FF5543?logo=sourcegraph&logoColor=white) |
| **Droid CLI** | 🔧 Setup Required | ![Droid](https://img.shields.io/badge/Android-Droid-3DDC84?logo=android&logoColor=white) |
| **Codex CLI** | 🚧 Experimental | ![OpenAI](https://img.shields.io/badge/OpenAI-Codex-412991?logo=openai&logoColor=white) |
| **Cursor CLI** | 🔜 Planned | ![Cursor](https://img.shields.io/badge/Cursor-Agent_CLI-000000?logo=cursor&logoColor=white) |
| **Agentforce Vibes CLI** | 🔜 Planned | ![Salesforce](https://img.shields.io/badge/Salesforce-Agentforce-00A1E0?logo=salesforce&logoColor=white) |
| **Google Gemini CLI** | 🔜 Planned | ![Google](https://img.shields.io/badge/Google-Gemini_CLI-4285F4?logo=google&logoColor=white) |

## ✨ Available Skills

| | Skill | Description | Status |
|--|-------|-------------|--------|
| ⚡ | **[sf-apex](sf-apex/)** | Apex gen & TAF patterns | 🧪 Alpha |
| 🔄 | **[sf-flow](sf-flow/)** | Flow creation & bulk validation | 🧪 Alpha |
| 📋 | **[sf-metadata](sf-metadata/)** | Metadata gen & org queries | 🧪 Alpha |
| 💾 | **[sf-data](sf-data/)** | SOQL & test data factories | 🧪 Alpha |
| 🚀 | **[sf-deploy](sf-deploy/)** | CI/CD automation (sf CLI v2) | 🧪 Alpha |
| 🤖 | **[sf-ai-agentforce](sf-ai-agentforce/)** | Agent Script & Actions | 🧪 Alpha |
| 🔐 | **[sf-connected-apps](sf-connected-apps/)** | OAuth apps & ECAs | 🧪 Alpha |
| 🔗 | **[sf-integration](sf-integration/)** | Callouts, Events, CDC | 🧪 Alpha |
| 📊 | **[sf-diagram](sf-diagram/)** | Mermaid diagrams & ERD | ✅ Stable |
| 🛠️ | **[skill-builder](skill-builder/)** | Skill creation wizard | ✅ Stable |

## 🏗️ Available Sub-Agents

| | Sub-Agent | Description | Status |
|--|-----------|-------------|--------|
| 🚦 | **[sf-devops-architect](agents/)** | MANDATORY deployment gateway - orchestrates all Salesforce deployments | ✅ Live |

> **Skills vs Sub-Agents**: Skills are invoked with `Skill(skill="name")`. Sub-agents are invoked with `Task(subagent_type="name", ...)` and can run autonomously in the background.

## 🚀 Installation

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add Jaganpro/sf-skills
```

### 📺 Video 1: How to Add/Install Skills to ClaudeCode?

<a href="https://youtu.be/a38MM8PBTe4" target="_blank">
  <img src="https://img.youtube.com/vi/a38MM8PBTe4/maxresdefault.jpg" alt="How to Add/Install Skills to ClaudeCode" />
</a>

## 🔗 Skill & Sub-Agent Architecture

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
flowchart TB
    subgraph ai["🤖 AI & AGENTS"]
        agentforce["🤖 sf-ai-agentforce"]
    end

    subgraph integration["🔌 INTEGRATION & SECURITY"]
        connectedapps["🔐 sf-connected-apps"]
        sfintegration["🔗 sf-integration"]
        diagram["📊 sf-diagram"]
    end

    subgraph development["💻 DEVELOPMENT"]
        apex["⚡ sf-apex"]
        flow["🔄 sf-flow"]
    end

    subgraph foundation["📦 FOUNDATION"]
        metadata["📋 sf-metadata"]
        data["💾 sf-data"]
    end

    subgraph gateway["🚦 DEPLOYMENT GATEWAY (Sub-Agent)"]
        devopsarchitect["🏗️ sf-devops-architect"]
    end

    subgraph devops["🚀 DEVOPS"]
        deploy["🚀 sf-deploy"]
    end

    subgraph tooling["🔧 TOOLING"]
        skillbuilder["🛠️ skill-builder"]
    end

    %% AI & Agent relationships
    agentforce -->|"flow actions"| flow
    agentforce -->|"API actions"| sfintegration
    agentforce -->|"GenAiFunction"| apex

    %% Integration relationships
    sfintegration -->|"OAuth apps"| connectedapps
    sfintegration -->|"callouts"| apex
    sfintegration -->|"HTTP Callout"| flow
    connectedapps -->|"permissions"| metadata
    diagram -->|"schema"| metadata
    diagram -.->|"documents"| connectedapps
    diagram -.->|"documents"| sfintegration

    %% Development relationships
    apex -->|"schema"| metadata
    flow -->|"schema"| metadata
    apex -.->|"test data"| data
    flow -.->|"test data"| data

    %% Foundation relationships
    data -->|"structure"| metadata

    %% MANDATORY Deployment Gateway - ALL deployments go through sf-devops-architect
    apex ==>|"MANDATORY"| devopsarchitect
    flow ==>|"MANDATORY"| devopsarchitect
    metadata ==>|"MANDATORY"| devopsarchitect
    sfintegration ==>|"MANDATORY"| devopsarchitect
    connectedapps ==>|"MANDATORY"| devopsarchitect
    agentforce ==>|"MANDATORY"| devopsarchitect

    %% Gateway delegates to sf-deploy skill
    devopsarchitect -->|"delegates"| deploy

    %% Styling - AI (pink-200)
    style agentforce fill:#fbcfe8,stroke:#be185d,color:#1f2937

    %% Styling - Integration (orange-200/teal-200/sky-200)
    style connectedapps fill:#fed7aa,stroke:#c2410c,color:#1f2937
    style sfintegration fill:#99f6e4,stroke:#0f766e,color:#1f2937
    style diagram fill:#bae6fd,stroke:#0369a1,color:#1f2937

    %% Styling - Development (violet-200/indigo-200)
    style apex fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
    style flow fill:#c7d2fe,stroke:#4338ca,color:#1f2937

    %% Styling - Foundation (cyan-200/amber-200)
    style metadata fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style data fill:#fde68a,stroke:#b45309,color:#1f2937

    %% Styling - Gateway Sub-Agent (rose-300 with thick border)
    style devopsarchitect fill:#fda4af,stroke:#be123c,stroke-width:3px,color:#1f2937

    %% Styling - DevOps (emerald-200)
    style deploy fill:#a7f3d0,stroke:#047857,color:#1f2937

    %% Styling - Tooling (slate-200)
    style skillbuilder fill:#e2e8f0,stroke:#334155,color:#1f2937

    %% Subgraph styling
    style ai fill:#fdf2f8,stroke:#be185d,stroke-dasharray:5
    style integration fill:#fff7ed,stroke:#c2410c,stroke-dasharray:5
    style development fill:#f5f3ff,stroke:#6d28d9,stroke-dasharray:5
    style foundation fill:#ecfeff,stroke:#0e7490,stroke-dasharray:5
    style gateway fill:#ffe4e6,stroke:#be123c,stroke-width:2px
    style devops fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
    style tooling fill:#f8fafc,stroke:#334155,stroke-dasharray:5
```

### 🚦 Deployment Gateway

**ALL deployments MUST go through the `sf-devops-architect` sub-agent:**

```
Task(subagent_type="sf-devops-architect", prompt="Deploy to [org]")
```

| ❌ Wrong | ✅ Correct |
|----------|------------|
| `sf project deploy start ...` | `Task(subagent_type="sf-devops-architect", ...)` |
| `Skill(skill="sf-deploy")` | `Task(subagent_type="sf-devops-architect", ...)` |

The gateway ensures consistent validation, orchestration, and deployment workflows.

### ⚡ Async Deployment (Non-Blocking)

Run deployments in the background while continuing other work:

```python
# Launch deployment in background (returns immediately)
Task(
  subagent_type="sf-devops-architect",
  prompt="Deploy to Production",
  run_in_background=true    # ← Key parameter!
)

# Continue working while deployment runs...

# Check status (non-blocking)
TaskOutput(task_id="agent-id", block=false)

# Wait for results when ready
TaskOutput(task_id="agent-id", block=true)
```

**Parallel Deployments Example:**
```python
# Deploy to multiple orgs simultaneously
Task(..., prompt="Deploy to Dev", run_in_background=true)
Task(..., prompt="Deploy to QA", run_in_background=true)
Task(..., prompt="Deploy to UAT", run_in_background=true)

# Collect results later
TaskOutput(task_id="dev-id", block=true)
TaskOutput(task_id="qa-id", block=true)
TaskOutput(task_id="uat-id", block=true)
```

## 🔌 Plugin Features

### Automatic Validation Hooks

Each skill includes validation hooks that run automatically on **Write** and **Edit** operations:

| | Skill | File Type | Validation |
|--|-------|-----------|------------|
| ⚡ | sf-apex | `*.cls`, `*.trigger` | 150-pt scoring + Code Analyzer |
| 🔄 | sf-flow | `*.flow-meta.xml` | 110-pt scoring + Flow Scanner |
| 📋 | sf-metadata | `*.object-meta.xml`, `*.field-meta.xml` | Metadata best practices |
| 💾 | sf-data | `*.apex`, `*.soql` | SOQL patterns, governor limits |
| 🤖 | sf-ai-agentforce | `*.agent`, `*.genAiFunction-meta.xml` | Agent Script syntax |
| 🔐 | sf-connected-apps | `*.connectedApp-meta.xml` | OAuth security |
| 🔗 | sf-integration | `*.namedCredential-meta.xml` | Callout patterns |
| 🛠️ | skill-builder | `SKILL.md` | YAML frontmatter |

#### 🔬 Code Analyzer V5 Integration

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

**Graceful Degradation:** If dependencies are missing, hooks run custom validation only and show which engines were skipped.

**Sample Output:**
```
🔍 Apex Validation: AccountService.cls
════════════════════════════════════════════════════════════════════════════════
📊 Score: 138/150 ⭐⭐⭐⭐ Very Good
   (Custom: 145, CA deductions: -7)

📋 Category Breakdown:
   ✅ Security: 25/25
   ✅ Bulkification: 25/25
   ⚠️ Testing: 20/25 (-5)
   ✅ Architecture: 20/20

🔬 Code Analyzer: pmd, regex (2847ms)

❗ Issues Found (3):
   🟠 HIGH [CA:pmd] L30: Validate CRUD permission before DML
   🟠 HIGH [CA:pmd] L45: Avoid empty catch blocks
   🔵 INFO [CA:regex] L12: Trailing whitespace
════════════════════════════════════════════════════════════════════════════════
```

Hooks provide **advisory feedback** — they inform but don't block operations.

## 🔧 Prerequisites

**Required:**
- **Claude Code** (latest version)
- **Salesforce CLI** v2.x (`sf` command)
- **Python 3.10+** (for validation hooks)

**Optional** (enables additional Code Analyzer engines):
- **Java 11+** — Enables PMD, CPD, SFGE engines (`brew install openjdk@11`)
- **Node.js** — Enables ESLint, RetireJS for LWC (`brew install node`)
- **Code Analyzer plugin** — `sf plugins install @salesforce/sfdx-code-analyzer`

## Usage Examples

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

## Roadmap

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
| 📊 | `sf-diagram` | Mermaid diagrams for OAuth, ERD, integrations, architecture | ✅ Live |
| 🔒 | `sf-security` | Sharing rules, org-wide defaults, encryption | 📋 Planned |
| 🧪 | `sf-testing` | Test strategy, mocking, coverage | 📋 Planned |
| 🐛 | `sf-debugging` | Debug logs, Apex replay | 📋 Planned |
| 📦 | `sf-migration` | Org-to-org, metadata comparison | 📋 Planned |

### 🤖 AI & Automation
| | Skill | Description | Status |
|--|-------|-------------|--------|
| 🤖 | `sf-ai-agentforce` | Agent Script, Topics, Actions (API v64+) | ✅ Live |
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

**Total: 24 skills + 1 sub-agent** (10 skills ✅ + 1 sub-agent ✅ live, 14 planned 📋)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `/plugin install ./your-skill`
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Issues & Support

- [GitHub Issues](https://github.com/Jaganpro/sf-skills/issues)

## License

MIT License - Copyright (c) 2024-2025 Jag Valaiyapathy
