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

| Skill | Description | Status |
|-------|-------------|--------|
| **[sf-apex](sf-apex/)** | Apex code generation & review with 150-point scoring | ✅ Live |
| **[sf-flow](sf-flow/)** | Flow creation & validation with 110-point scoring | ✅ Live |
| **[sf-metadata](sf-metadata/)** | Metadata generation & org querying with 120-point scoring | ✅ Live |
| **[sf-data](sf-data/)** | Data operations, SOQL expertise & test data factories with 130-point scoring | ✅ Live |
| **[sf-deploy](sf-deploy/)** | DevOps & CI/CD automation using sf CLI v2 | ✅ Live |
| **[sf-ai-agentforce](sf-ai-agentforce/)** | Agentforce agent creation with Agent Script & 100-point scoring | ✅ Live |
| **[skill-builder](skill-builder/)** | Claude Code skill creation wizard | ✅ Live |

## 🚀 Installation

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add Jaganpro/sf-skills
```

### 📺 Video 1: How to Add/Install Skills to ClaudeCode?

<a href="https://youtu.be/a38MM8PBTe4" target="_blank">
  <img src="https://img.youtube.com/vi/a38MM8PBTe4/maxresdefault.jpg" alt="How to Add/Install Skills to ClaudeCode" />
</a>

## 🔗 Skill Dependencies

Some skills work together for a complete workflow:

```mermaid
flowchart TB
    subgraph consumers [" "]
        direction LR
        flow["🔄 sf-flow"]
        apex["⚡ sf-apex"]
    end

    subgraph core [" "]
        direction LR
        metadata["📋 sf-metadata"]
        data["💾 sf-data"]
    end

    deploy["🚀 sf-deploy"]

    flow -->|"queries objects/fields"| metadata
    apex -->|"queries objects/fields"| metadata
    data -->|"queries object structure"| metadata

    apex -.->|"test data generation"| data
    flow -.->|"test data generation"| data

    flow -->|"deploys"| deploy
    apex -->|"deploys"| deploy
    metadata -->|"deploys"| deploy

    style flow fill:#6366f1,stroke:#4f46e5,color:#fff
    style apex fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style metadata fill:#06b6d4,stroke:#0891b2,color:#fff
    style data fill:#f59e0b,stroke:#d97706,color:#fff
    style deploy fill:#10b981,stroke:#059669,color:#fff
    style consumers fill:transparent,stroke:#64748b,stroke-dasharray:5
    style core fill:transparent,stroke:#64748b,stroke-dasharray:5
```

- **sf-apex** and **sf-flow** can query **sf-metadata** to discover object/field information before generating code
- **sf-apex** and **sf-flow** can use **sf-data** to generate test data for trigger/flow testing
- **sf-data** can query **sf-metadata** for object structure before creating test records
- **sf-apex**, **sf-flow**, and **sf-metadata** use **sf-deploy** for deploying to Salesforce orgs
- Each skill works standalone, but will prompt you to install dependencies if needed

## 🔌 Plugin Features

### Automatic Validation Hooks

Each skill includes validation hooks that run automatically when you write files:

| Skill | File Type | Validation |
|-------|-----------|------------|
| sf-flow | `*.flow-meta.xml` | Flow best practices, 110-point scoring, bulk safety |
| sf-apex | `*.cls`, `*.trigger` | Apex anti-patterns, 150-point scoring, TAF compliance |
| sf-metadata | `*.object-meta.xml`, `*.field-meta.xml`, etc. | Metadata best practices, 120-point scoring, FLS checks |
| sf-data | `*.apex`, `*.soql` | SOQL patterns, 130-point scoring, governor limits |
| sf-ai-agentforce | `*.agentscript` | Agent Script syntax, 100-point scoring, topic validation |
| skill-builder | `SKILL.md` | YAML frontmatter validation |

Hooks provide **advisory feedback** after writes - they inform but don't block.

## 🔧 Prerequisites

- **Claude Code** (latest version)
- **Salesforce CLI** v2.x (`sf` command, not legacy `sfdx`)
- **Python 3.8+** (optional, for validation hooks)

## Usage Examples

### Apex Development
```
"Generate an Apex trigger for Account using Trigger Actions Framework"
"Review my AccountService class for best practices"
"Create a batch job to process millions of records"
"Generate a test class with 90%+ coverage"
```

### Flow Development
```
"Create a screen flow for account creation with validation"
"Build a record-triggered flow for opportunity stage changes"
"Generate a scheduled flow for data cleanup"
```

### Metadata Management
```
"Create a custom object called Invoice with auto-number name field"
"Add a lookup field from Contact to Account"
"Generate a permission set for invoice managers with full CRUD"
"Create a validation rule to require close date when status is Closed"
"Describe the Account object in my org and list all custom fields"
```

### Data Operations
```
"Query all Accounts with related Contacts and Opportunities"
"Create 251 test Account records for trigger bulk testing"
"Insert 500 records from accounts.csv using Bulk API"
"Generate test data hierarchy: 10 Accounts with 3 Contacts each"
"Clean up all test records created today"
```

### Deployment
```
"Deploy my Apex classes to sandbox with tests"
"Validate my metadata changes before deploying to production"
```

### Skill Creation
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
| Skill | Description | Status |
|-------|-------------|--------|
| `sf-security` | Sharing rules, org-wide defaults, encryption | 📋 Planned |
| `sf-integration` | REST, SOAP, Platform Events | 📋 Planned |
| `sf-testing` | Test strategy, mocking, coverage | 📋 Planned |
| `sf-debugging` | Debug logs, Apex replay | 📋 Planned |
| `sf-migration` | Org-to-org, metadata comparison | 📋 Planned |

### 🤖 AI & Automation
| Skill | Description | Status |
|-------|-------------|--------|
| `sf-ai-agentforce` | Agent Script, Topics, Actions (API v64+) | ✅ Live |
| `sf-ai-copilot` | Einstein Copilot, Prompts | 📋 Planned |
| `sf-ai-einstein` | Prediction Builder, NBA | 📋 Planned |

### 📦 Products
| Skill | Description | Status |
|-------|-------------|--------|
| `sf-product-datacloud` | Unified profiles, segments | 📋 Planned |
| `sf-product-omnistudio` | FlexCards, DataRaptors | 📋 Planned |

### ☁️ Clouds
| Skill | Description | Status |
|-------|-------------|--------|
| `sf-cloud-sales` | Opportunities, Quotes, Forecasting | 📋 Planned |
| `sf-cloud-service` | Cases, Omni-Channel, Knowledge | 📋 Planned |
| `sf-cloud-experience` | Communities, Portals | 📋 Planned |

### 🏢 Industries
| Skill | Description | Status |
|-------|-------------|--------|
| `sf-industry-healthcare` | FHIR, Care Plans, Compliance | 📋 Planned |
| `sf-industry-finserv` | KYC, AML, Wealth Management | 📋 Planned |
| `sf-industry-revenue` | CPQ, Billing, Revenue Lifecycle | 📋 Planned |

**Total: 22 skills** (7 live ✅, 15 planned 📋)

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
