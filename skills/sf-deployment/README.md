# Salesforce Deployment Skill

## Overview

The `sf-deployment` skill provides comprehensive Salesforce DevOps automation capabilities for Claude Code. It helps you deploy metadata, run tests, validate deployments, and set up CI/CD pipelines using the Salesforce CLI.

## Prerequisites

Before using this skill, ensure you have:

1. **Salesforce CLI** installed (sf or sfdx)
   ```bash
   npm install -g @salesforce/cli
   # or
   sf update
   ```

2. **Authenticated Salesforce Org(s)**
   ```bash
   sf org login web --alias myorg
   # or use JWT, auth URL, etc.
   ```

3. **Valid SFDX Project** (if deploying from a project)
   - Must have `sfdx-project.json` in the root directory

## Usage

### Basic Invocation

Simply ask Claude Code to help with Salesforce deployments:

```
"Deploy my Salesforce metadata to the sandbox"
```

```
"Validate this deployment before production"
```

```
"Set up a CI/CD pipeline for Salesforce"
```

### Common Tasks

#### 1. Deploy to Sandbox/Production

```
"Deploy the force-app directory to my production org with all tests"
```

The skill will:
- Verify org authentication
- Create a deployment task list
- Run validation if needed
- Execute deployment with appropriate test level
- Provide detailed results and code coverage

#### 2. Validate Before Deploying

```
"Run a check-only deployment to validate my changes"
```

#### 3. Deploy Specific Components

```
"Deploy only the AccountController and ContactTrigger classes"
```

#### 4. Troubleshoot Deployment Failures

```
"My deployment failed with error INVALID_CROSS_REFERENCE_KEY. Help me fix it."
```

#### 5. Set Up CI/CD Pipeline

```
"Create a GitHub Actions workflow for automated Salesforce deployments"
```

#### 6. Create Scratch Org and Deploy

```
"Create a scratch org and push my source code"
```

## Features

### Deployment Management
- Full metadata deployments
- Selective component deployments
- Manifest-based deployments (package.xml)
- Check-only validations
- Quick deploy after validation

### Testing & Validation
- Run test classes (local, all, or specific)
- Code coverage analysis
- Pre-deployment validation
- Post-deployment verification

### DevOps Automation
- CI/CD pipeline setup
- Automated testing workflows
- Deployment scripts generation
- Multi-environment management

### Error Handling
- Detailed error analysis
- Common error solutions
- Deployment troubleshooting
- Rollback strategies

## Examples

See the `examples/` directory for:
- `deployment-workflows.md` - Common deployment scenarios
- `ci-cd-setup.md` - CI/CD pipeline examples
- `troubleshooting.md` - Error handling examples

## Templates

The `templates/` directory contains:
- `package.xml` - Manifest file template
- `destructiveChanges.xml` - Destructive changes template
- `.github/workflows/deploy.yml` - GitHub Actions pipeline
- `auth-org.sh` - Org authentication script

## Scripts

Helper scripts in `scripts/` directory:
- `deploy.sh` - Main deployment script
- `validate.sh` - Validation-only script
- `run-tests.sh` - Test execution script
- `quick-deploy.sh` - Quick deploy after validation

## Best Practices

1. **Always validate before production** - Use check-only deployments
2. **Run appropriate tests** - RunLocalTests for most deployments
3. **Monitor code coverage** - Maintain >75% (aim for >90%)
4. **Use version control** - Commit before deploying
5. **Test in sandbox first** - Never deploy untested changes to production
6. **Incremental deployments** - Deploy small, frequent changes
7. **Document changes** - Maintain deployment logs

## Tips

- The skill automatically checks for Salesforce CLI installation
- It verifies org authentication before attempting deployments
- It creates task lists for complex multi-step deployments
- It provides detailed error messages with solutions
- It can generate CI/CD pipeline configurations

## Troubleshooting

If you encounter issues:

1. **CLI not found**: Install Salesforce CLI
   ```bash
   npm install -g @salesforce/cli
   ```

2. **Org not authenticated**: Authenticate your org
   ```bash
   sf org login web --alias myorg
   ```

3. **Not an SFDX project**: Initialize project structure
   ```bash
   sf project generate --name myproject
   ```

4. **Deployment failures**: The skill will analyze errors and suggest fixes

## Contributing

To customize this skill:

1. Edit `SKILL.md` to modify deployment workflows
2. Add new examples to `examples/` directory
3. Create additional templates in `templates/`
4. Add helper scripts to `scripts/`

## Resources

- [Salesforce CLI Documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/)
- [Salesforce DX Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/)
- [Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/)

## License

This skill is part of your Claude Code skills library.

---

**Version**: 1.0.0
**Author**: jvalaiyapathy
**Tags**: salesforce, devops, sfdx, deployment, ci-cd, automation, apex, metadata
