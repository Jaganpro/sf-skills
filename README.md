# Salesforce Skills for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue.svg)](https://claude.ai/code)
[![Salesforce](https://img.shields.io/badge/Salesforce-Apex%20%7C%20Flow%20%7C%20DevOps-00A1E0.svg)](https://www.salesforce.com/)

A collection of Claude Code skills for Salesforce development, specializing in Apex code generation, Flow automation, and DevOps workflows.

## ✨ Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| **[sf-apex](skills/sf-apex/)** | Apex code generation & review | ✅ Live |
| **[sf-flow-builder](skills/sf-flow-builder/)** | Flow creation & validation | ✅ Live |
| **[sf-deployment](skills/sf-deployment/)** | DevOps & CI/CD automation | ✅ Live |
| **[skill-builder](skills/skill-builder/)** | Claude Code skill wizard | ✅ Live |

## 🚀 Quick Install

### Option 1: Plugin Install (Recommended)

```bash
/plugin install github:Jaganpro/sf-skills
```

That's it! Skills are loaded automatically.

### Option 2: Manual Install

```bash
git clone https://github.com/Jaganpro/sf-skills.git
cd sf-skills
/plugin install .
```

### Option 3: Legacy Install (Deprecated)

```bash
git clone https://github.com/Jaganpro/sf-skills.git
cd sf-skills
./scripts/install.sh
```

**Restart Claude Code** after manual installation to load the skills.

## 🔌 Plugin Features

This plugin includes **automatic validation hooks** that run when you write Salesforce files:

| File Type | Validation |
|-----------|------------|
| `*.flow-meta.xml` | Flow best practices, 110-point scoring |
| `*.cls`, `*.trigger` | Apex anti-patterns, 150-point scoring |
| `SKILL.md` | YAML frontmatter validation |

Hooks provide advisory feedback after writes - they inform but don't block.

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

**Total: 22 skills** (4 live, 18 planned)

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

## Plugin Commands

| Command | Description |
|---------|-------------|
| `/plugin install github:Jaganpro/sf-skills` | Install from GitHub |
| `/plugin update sf-skills` | Update to latest version |
| `/plugin uninstall sf-skills` | Remove the plugin |
| `/plugin list` | List installed plugins |

### Legacy Scripts (Deprecated)

For manual installations, scripts are in the `scripts/` folder:

| Script | Description |
|--------|-------------|
| `./scripts/install.sh` | Install skills (use `--local` for project-only) |
| `./scripts/upgrade.sh` | Upgrade to latest version |
| `./scripts/uninstall.sh` | Remove all skills |

## Prerequisites

- **Claude Code** (latest version)
- **Salesforce CLI** v2.x (`sf` command)
- **Python 3.8+** (optional, for validators)

## What's Included

### sf-apex
- 15 best practice categories (bulkification, security, testing, SOLID, etc.)
- 8-category validation scoring system (0-150 points)
- Trigger Actions Framework integration
- 9 production-ready templates
- Code review checklist

### sf-flow-builder
- Flow XML generation with API 62.0
- Strict validation and scoring
- Multiple flow type support (Screen, Record-Triggered, Scheduled, etc.)
- Integration with sf-deployment

### sf-deployment
- Modern `sf` CLI v2 commands
- Dry-run validation before deployment
- Test execution and coverage reporting
- CI/CD pipeline support

### skill-builder
- Interactive wizard for skill creation
- YAML frontmatter validation
- Bulk skill validation
- Dependency management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a Pull Request

## Issues & Support

- [GitHub Issues](https://github.com/Jaganpro/claude-code-sfskills/issues)

## License

MIT License - Copyright (c) 2024-2025 Jag Valaiyapathy
