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

| Without Skills | With Skills |
|----------------|-------------|
| ❌ Explain best practices every conversation | ✅ AI already knows the standards |
| ❌ Manually review code for anti-patterns | ✅ Auto-validation on every file save |
| ❌ Copy-paste boilerplate repeatedly | ✅ Production-ready templates built-in |
| ❌ Remember CLI commands and flags | ✅ Skill handles tool orchestration |
| ❌ Burn tokens on lengthy system prompts | ✅ Skills load on-demand, saving context |

---

## 🤖 Supported Agentic Coding Tools

| Tool | Status | |
|------|--------|--|
| **Claude Code CLI** | ✅ Full Support | ![Claude](https://img.shields.io/badge/Anthropic-Claude_Code-191919?logo=anthropic&logoColor=white) |
| **Agentforce Vibes CLI** | 🔜 Planned | ![Salesforce](https://img.shields.io/badge/Salesforce-Agentforce-00A1E0?logo=salesforce&logoColor=white) |
| **Google Gemini CLI** | 🔜 Planned | ![Google](https://img.shields.io/badge/Google-Gemini_CLI-4285F4?logo=google&logoColor=white) |
| **Droid CLI** | 🔜 Planned | ![Droid](https://img.shields.io/badge/Android-Droid-3DDC84?logo=android&logoColor=white) |
| **Codex CLI** | 🔜 Planned | ![OpenAI](https://img.shields.io/badge/OpenAI-Codex-412991?logo=openai&logoColor=white) |

## ✨ Available Skills

| | Skill | Description | Status |
|--|-------|-------------|--------|
| ⚡ | **[sf-apex](sf-apex/)** | Apex code generation & review with TAF pattern enforcement | ✅ Live |
| 🔄 | **[sf-flow](sf-flow/)** | Flow creation & validation with bulkification checks | ✅ Live |
| 📋 | **[sf-metadata](sf-metadata/)** | Metadata generation & org querying | ✅ Live |
| 💾 | **[sf-data](sf-data/)** | Data operations, SOQL expertise & test data factories | ✅ Live |
| 🚀 | **[sf-deploy](sf-deploy/)** | DevOps & CI/CD automation using sf CLI v2 | ✅ Live |
| 🤖 | **[sf-ai-agentforce](sf-ai-agentforce/)** | Agentforce agent creation with Agent Script syntax & Agent Actions | ✅ Live |
| 🔐 | **[sf-connected-apps](sf-connected-apps/)** | Connected Apps & External Client Apps with OAuth config | ✅ Live |
| 🔗 | **[sf-integration](sf-integration/)** | Named Credentials, External Services, REST/SOAP, Platform Events, CDC | ✅ Live |
| 📊 | **[sf-diagram](sf-diagram/)** | Mermaid diagrams for OAuth, ERD, integrations & architecture | ✅ Live |
| 🛠️ | **[skill-builder](skill-builder/)** | Claude Code skill creation wizard | ✅ Live |

## 🚀 Installation

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add Jaganpro/sf-skills
```

### 📺 Video 1: How to Add/Install Skills to ClaudeCode?

<a href="https://youtu.be/a38MM8PBTe4" target="_blank">
  <img src="https://img.youtube.com/vi/a38MM8PBTe4/maxresdefault.jpg" alt="How to Add/Install Skills to ClaudeCode" />
</a>

## 🔗 Skill Architecture

```mermaid
flowchart TB
    subgraph ai["🤖 AI & Agents"]
        agentforce["🤖 sf-ai-agentforce<br/><small>Agent Script, Topics<br/>GenAiFunction, PromptTemplate</small>"]
    end

    subgraph integration["🔌 Integration & Security"]
        connectedapps["🔐 sf-connected-apps<br/><small>OAuth, ECAs, Security</small>"]
        sfintegration["🔗 sf-integration<br/><small>Named Creds, REST/SOAP<br/>Platform Events, CDC</small>"]
        diagram["📊 sf-diagram<br/><small>OAuth, ERD, Architecture</small>"]
    end

    subgraph development["💻 Development"]
        apex["⚡ sf-apex<br/><small>Triggers, Services, Tests</small>"]
        flow["🔄 sf-flow<br/><small>Screen, Record, Scheduled<br/>HTTP Callout Flows</small>"]
    end

    subgraph foundation["📦 Foundation"]
        metadata["📋 sf-metadata<br/><small>Objects, Fields, Perms</small>"]
        data["💾 sf-data<br/><small>SOQL, CRUD, Test Data</small>"]
    end

    subgraph devops["🚀 DevOps"]
        deploy["🚀 sf-deploy<br/><small>CI/CD, Validation</small>"]
    end

    subgraph tooling["🔧 Tooling"]
        skillbuilder["🛠️ skill-builder<br/><small>Create New Skills</small>"]
    end

    %% AI & Agent relationships
    agentforce -->|"flow:// actions"| flow
    agentforce -->|"API actions"| sfintegration
    agentforce -->|"GenAiFunction"| apex

    %% Integration relationships
    sfintegration -->|"OAuth apps"| connectedapps
    sfintegration -->|"callout classes"| apex
    sfintegration -->|"HTTP Callout"| flow
    connectedapps -->|"Permission Sets"| metadata
    diagram -->|"queries schema"| metadata
    diagram -.->|"documents"| connectedapps
    diagram -.->|"documents"| sfintegration

    %% Development relationships
    apex -->|"queries schema"| metadata
    flow -->|"queries schema"| metadata
    apex -.->|"test data"| data
    flow -.->|"test data"| data

    %% Foundation relationships
    data -->|"queries structure"| metadata

    %% Deployment relationships
    apex -->|"deploys"| deploy
    flow -->|"deploys"| deploy
    metadata -->|"deploys"| deploy
    sfintegration -->|"deploys"| deploy
    connectedapps -->|"deploys"| deploy
    agentforce -->|"publishes"| deploy

    %% Styling - AI (pink)
    style agentforce fill:#ec4899,stroke:#db2777,color:#fff

    %% Styling - Integration (orange/teal)
    style connectedapps fill:#f97316,stroke:#ea580c,color:#fff
    style sfintegration fill:#14b8a6,stroke:#0d9488,color:#fff
    style diagram fill:#0ea5e9,stroke:#0284c7,color:#fff

    %% Styling - Development (purple/indigo)
    style apex fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style flow fill:#6366f1,stroke:#4f46e5,color:#fff

    %% Styling - Foundation (cyan/amber)
    style metadata fill:#06b6d4,stroke:#0891b2,color:#fff
    style data fill:#f59e0b,stroke:#d97706,color:#fff

    %% Styling - DevOps (green)
    style deploy fill:#10b981,stroke:#059669,color:#fff

    %% Styling - Tooling (gray)
    style skillbuilder fill:#64748b,stroke:#475569,color:#fff

    %% Subgraph styling
    style ai fill:transparent,stroke:#ec4899,stroke-dasharray:5
    style integration fill:transparent,stroke:#f97316,stroke-dasharray:5
    style development fill:transparent,stroke:#8b5cf6,stroke-dasharray:5
    style foundation fill:transparent,stroke:#06b6d4,stroke-dasharray:5
    style devops fill:transparent,stroke:#10b981,stroke-dasharray:5
    style tooling fill:transparent,stroke:#64748b,stroke-dasharray:5
```

## 🔌 Plugin Features

### Automatic Validation Hooks

Each skill includes validation hooks that run automatically when you write files:

| | Skill | File Type | Validation |
|--|-------|-----------|------------|
| ⚡ | sf-apex | `*.cls`, `*.trigger` | Apex anti-patterns, TAF compliance |
| 🔄 | sf-flow | `*.flow-meta.xml` | Flow best practices, bulk safety |
| 📋 | sf-metadata | `*.object-meta.xml`, `*.field-meta.xml`, etc. | Metadata best practices, FLS checks |
| 💾 | sf-data | `*.apex`, `*.soql` | SOQL patterns, governor limits |
| 🤖 | sf-ai-agentforce | `*.agent`, `*.genAiFunction-meta.xml` | Agent Script syntax, topic validation |
| 🔐 | sf-connected-apps | `*.connectedApp-meta.xml`, `*.eca-meta.xml` | OAuth security, PKCE validation |
| 🔗 | sf-integration | `*.namedCredential-meta.xml`, `*.cls` | Named Credential security, callout patterns |
| 🛠️ | skill-builder | `SKILL.md` | YAML frontmatter validation |

Hooks provide **advisory feedback** after writes - they inform but don't block.

## 🔧 Prerequisites

- **Claude Code** (latest version)
- **Salesforce CLI** v2.x (`sf` command, not legacy `sfdx`)
- **Python 3.8+** (optional, for validation hooks)

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

**Total: 24 skills** (10 live ✅, 14 planned 📋)

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
