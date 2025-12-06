# Salesforce Skills for Agentic Coding Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue.svg)](https://claude.ai/code)
[![Salesforce](https://img.shields.io/badge/Salesforce-Apex%20%7C%20Flow%20%7C%20DevOps-00A1E0.svg)](https://www.salesforce.com/)

A collection of reusable skills for Salesforce development, specializing in Apex code generation, Flow automation, and DevOps workflows. Built for Claude Code with planned support for other agentic coding tools.

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
| **[sf-flow-builder](sf-flow-builder/)** | Flow creation & validation with 110-point scoring | ✅ Live |
| **[sf-deployment](sf-deployment/)** | DevOps & CI/CD automation using sf CLI v2 | ✅ Live |
| **[skill-builder](skill-builder/)** | Claude Code skill creation wizard | ✅ Live |

## 🚀 Installation

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add Jaganpro/sf-skills
```

Then install only the skills you need:

```bash
# Flow development
/plugin install sf-flow-builder@sf-skills-marketplace

# Apex development
/plugin install sf-apex@sf-skills-marketplace

# Deployment automation
/plugin install sf-deployment@sf-skills-marketplace

# Skill creation wizard
/plugin install skill-builder@sf-skills-marketplace
```

### Local Development Install

```bash
git clone https://github.com/Jaganpro/sf-skills.git
cd sf-skills

# Install all skills
/plugin install .

# Or add as local marketplace, then install individually
/plugin marketplace add .
/plugin install sf-flow-builder@sf-skills-marketplace
```

## 🔗 Skill Dependencies

Some skills work together for a complete workflow:

```
┌─────────────────┐     ┌─────────────────┐
│  sf-flow-builder │────▶│  sf-deployment  │
└─────────────────┘     └─────────────────┘
                              ▲
┌─────────────────┐           │
│     sf-apex     │───────────┘
└─────────────────┘
```

- **sf-flow-builder** and **sf-apex** optionally use **sf-deployment** for deploying to Salesforce orgs
- Each skill works standalone, but will prompt you to install dependencies if needed

## 🔌 Plugin Features

### Automatic Validation Hooks

Each skill includes validation hooks that run automatically when you write files:

| Skill | File Type | Validation |
|-------|-----------|------------|
| sf-flow-builder | `*.flow-meta.xml` | Flow best practices, 110-point scoring, bulk safety |
| sf-apex | `*.cls`, `*.trigger` | Apex anti-patterns, 150-point scoring, TAF compliance |
| skill-builder | `SKILL.md` | YAML frontmatter validation |

Hooks provide **advisory feedback** after writes - they inform but don't block.

### Validation Scoring

**Flow Validation (110 points)**:
- Design & Naming (20 pts)
- Logic & Structure (20 pts)
- Architecture (15 pts)
- Performance & Bulk Safety (20 pts)
- Error Handling (20 pts)
- Security (15 pts)

**Apex Validation (150 points)**:
- Bulkification (25 pts)
- Security (25 pts)
- Testing (25 pts)
- Architecture (20 pts)
- Clean Code (20 pts)
- Error Handling (15 pts)
- Performance (10 pts)
- Documentation (10 pts)

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

### Deployment
```
"Deploy my Apex classes to sandbox with tests"
"Validate my metadata changes before deploying to production"
```

### Skill Creation
```
"Create a new Claude Code skill for code analysis"
```

## What's Included

### sf-flow-builder
- Flow XML generation with API 62.0 (Winter '26)
- 7 flow type templates (Screen, Record-Triggered, Scheduled, etc.)
- 6 reusable subflow patterns
- Strict validation with 110-point scoring
- Auto-Layout support (locationX/Y = 0)
- Integration with sf-deployment

### sf-apex
- 150-point scoring across 8 categories
- Trigger Actions Framework (TAF) enforcement
- 9 production-ready templates
- SOLID principles validation
- Security best practices (WITH USER_MODE, FLS)
- Modern Apex features (null coalescing, safe navigation)

### sf-deployment
- Modern `sf` CLI v2 commands (not legacy sfdx)
- Dry-run validation (`--dry-run`) before deployment
- Test execution with coverage reporting
- Quick deploy for validated changesets
- CI/CD pipeline support

### skill-builder
- Interactive wizard for skill creation
- YAML frontmatter validation
- Bulk skill validation
- Dependency management
- Interactive terminal editor

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
| `sf-admin` | Objects, fields, layouts | 📋 Planned |
| `sf-security` | Profiles, permissions, sharing | 📋 Planned |
| `sf-integration` | REST, SOAP, Platform Events | 📋 Planned |
| `sf-testing` | Test strategy, mocking, coverage | 📋 Planned |
| `sf-debugging` | Debug logs, Apex replay | 📋 Planned |
| `sf-migration` | Org-to-org, metadata comparison | 📋 Planned |
| `sf-data` | Data migration, ETL, bulk ops | 📋 Planned |

### 🤖 AI & Automation
| Skill | Description | Status |
|-------|-------------|--------|
| `sf-ai-agentforce` | Agent Studio, Topics, Actions | 📋 Planned |
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

**Total: 22 skills** (4 live ✅, 18 planned 📋)

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
