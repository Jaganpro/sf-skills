# sf-deploy

Comprehensive Salesforce DevOps automation using sf CLI v2. Deploy metadata, manage orgs, and set up CI/CD pipelines.

## Features

- **Deployment Management**: Execute, validate, and monitor deployments
- **DevOps Automation**: CI/CD pipelines, automated testing workflows
- **Org Management**: Authentication, scratch orgs, environment management
- **Quality Assurance**: Tests, code coverage, pre-production validation
- **Troubleshooting**: Debug failures, analyze logs, provide solutions

## Installation

```bash
# Install as part of sf-skills
claude /plugin install github:Jaganpro/sf-skills

# Or install standalone
claude /plugin install github:Jaganpro/sf-skills/sf-deploy
```

## Quick Start

### 1. Invoke the skill

```
Skill: sf-deploy
Request: "Deploy all changes to org dev with validation"
```

### 2. Common operations

| Operation | Example Request |
|-----------|-----------------|
| Deploy | "Deploy force-app to org dev" |
| Validate | "Dry-run deploy to check for errors" |
| Quick deploy | "Quick deploy validated changes" |
| Cancel | "Cancel the current deployment" |
| Status | "Check deployment status" |

## Key Commands

```bash
# Validate before deploy (ALWAYS DO THIS)
sf project deploy start --dry-run --source-dir force-app --target-org [alias]

# Deploy with tests
sf project deploy start --source-dir force-app --test-level RunLocalTests --target-org [alias]

# Quick deploy (after validation)
sf project deploy quick --job-id [id] --target-org [alias]

# Check status
sf project deploy report --job-id [id] --target-org [alias]

# Cancel deployment
sf project deploy cancel --job-id [id] --target-org [alias]
```

## Orchestration Order

```
sf-metadata → sf-flow → sf-deploy → sf-data
```

**Within sf-deploy**:
1. Objects/Fields
2. Permission Sets
3. Flows (as Draft)
4. Apex
5. Activate Flows

## Best Practices

| Rule | Details |
|------|---------|
| Always --dry-run first | Validate before actual deployment |
| Deploy order matters | Objects → Permissions → Code |
| Test levels | Use RunLocalTests for production |
| Flow activation | Deploy as Draft, activate manually |

## Cross-Skill Integration

| Related Skill | When to Use |
|---------------|-------------|
| sf-metadata | Create objects/fields BEFORE deploy |
| sf-testing | Run tests AFTER deployment |
| sf-data | Insert test data AFTER deployment |

## Documentation

- [Deployment Patterns](references/deployment-patterns.md)
- [CI/CD Guide](references/cicd-guide.md)
- [Troubleshooting](references/troubleshooting.md)

## Requirements

- sf CLI v2
- Target Salesforce org
- Proper permissions for deployment

## License

MIT License. See LICENSE file.
Copyright (c) 2024-2025 Jag Valaiyapathy
