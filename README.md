# Salesforce Skills for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue.svg)](https://claude.ai/code)
[![Salesforce](https://img.shields.io/badge/Salesforce-Apex%20%7C%20Flow%20%7C%20DevOps-00A1E0.svg)](https://www.salesforce.com/)

A collection of Claude Code skills for Salesforce development, specializing in Apex code generation, Flow automation, and DevOps workflows.

## Skills

| Skill | Description |
|-------|-------------|
| **[sf-apex](skills/sf-apex/)** | Apex code generation and review with 2025 best practices |
| **[sf-flow-builder](skills/sf-flow-builder/)** | Flow creation with validation and best practices |
| **[sf-deployment](skills/sf-deployment/)** | Salesforce DevOps automation for deployments and CI/CD |
| **[skill-builder](skills/skill-builder/)** | Wizard for creating Claude Code skills |

## Quick Install

```bash
git clone https://github.com/Jaganpro/claude-code-sfskills.git
cd claude-code-sfskills
./scripts/install.sh
```

**Restart Claude Code** after installation to load the skills.

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

## Scripts

All scripts are located in the `scripts/` folder:

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
