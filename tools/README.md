# sf-skills Multi-CLI Installer

Install sf-skills to different agentic coding CLIs following the [Agent Skills open standard](https://agentskills.io).

## Supported CLIs

| CLI | Install Path | Format | Description |
|-----|--------------|--------|-------------|
| **OpenCode** | `.opencode/skill/{name}/` | SKILL.md | Open-source Claude Code alternative |
| **Codex CLI** | `.codex/skills/{name}/` | SKILL.md | OpenAI's coding CLI |
| **Gemini CLI** | `~/.gemini/skills/{name}/` | SKILL.md | Google's Gemini-powered CLI |
| **Droid CLI** | `.factory/skills/{name}/` | SKILL.md | Factory.ai's agentic CLI (Claude Code compatible) |
| **Cursor** | `.cursor/rules/{name}.mdc` | MDC | Cursor IDE rules (transformed format) |
| **Agentforce Vibes** | `.clinerules/{name}.md` | Markdown | Salesforce's enterprise vibe-coding tool |

> **Note:** Claude Code support remains via the native `.claude-plugin/` structure in each skill directory. This installer is for *other* CLIs.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Jaganpro/sf-skills
cd sf-skills

# Install all skills for OpenCode
python tools/installer.py --cli opencode --all

# Install specific skills for Gemini
python tools/installer.py --cli gemini --skills sf-apex sf-flow

# Auto-detect installed CLIs and install all skills
python tools/installer.py --detect --all
```

## Usage

```
usage: installer.py [-h] [--cli {opencode,codex,gemini,droid,cursor,agentforce-vibes}] [--detect]
                    [--skills SKILLS [SKILLS ...]] [--all]
                    [--target TARGET] [--force] [--list] [--list-clis]

Install sf-skills to different agentic coding CLIs

optional arguments:
  -h, --help            show this help message and exit
  --cli {opencode,codex,gemini,droid,cursor,agentforce-vibes}
                        Target CLI to install for
  --detect              Auto-detect installed CLIs
  --skills SKILLS [SKILLS ...]
                        Specific skills to install
  --all                 Install all available skills
  --target TARGET       Custom target directory for installation
  --force               Overwrite existing installations
  --list                List available skills
  --list-clis           List supported CLIs
```

## Examples

### List Available Skills

```bash
python tools/installer.py --list
```

Output:
```
Available Skills
================
  sf-apex              Salesforce Apex development with validation...
  sf-data              Salesforce data operations and SOQL queries...
  sf-deploy            Salesforce deployment automation...
  sf-flow              Salesforce Flow development...
  ...
```

### Install All Skills for OpenCode

```bash
python tools/installer.py --cli opencode --all
```

This installs to `.opencode/skill/` in your current directory.

### Install to Custom Location

```bash
python tools/installer.py --cli codex --target /path/to/project/.codex/skills/ --all
```

### Auto-Detect CLIs

```bash
python tools/installer.py --detect --all
```

Detects installed CLIs (OpenCode, Codex, Gemini, Droid, Cursor) and installs skills to each.

### Force Reinstall

```bash
python tools/installer.py --cli gemini --all --force
```

Overwrites existing skill installations.

## What Gets Installed

Each installed skill contains:

```
{skill-name}/
├── SKILL.md           # Skill definition (transformed for target CLI)
├── scripts/           # Validation scripts (standalone)
│   ├── README.md      # Manual run instructions
│   ├── validate_*.py  # Validation scripts
│   └── shared/        # Bundled shared modules
├── assets/            # Code templates and static resources (spec)
└── references/        # Documentation and guides (spec)
```

### Key Transformations

| Source | OpenCode | Codex | Gemini | Droid | Cursor | Agentforce Vibes |
|--------|----------|-------|--------|-------|--------|------------------|
| `SKILL.md` | `SKILL.md` | `SKILL.md` | `SKILL.md` | `SKILL.md` | `{name}.mdc` | `{nn}-{name}.md` |
| `.claude-plugin/*` | (skipped) | (skipped) | (skipped) | (skipped) | (skipped) | (skipped) |
| `hooks/scripts/*.py` | `scripts/*.py` | `scripts/*.py` | `scripts/*.py` | `scripts/*.py` | `scripts/*.py` | (skipped) |
| `assets/` | `assets/` | `assets/` | `assets/` | `assets/` | `assets/` | (inlined) |
| `references/` | `references/` | `references/` | `references/` | `references/` | `references/` | (skipped) |
| `shared/*` | `scripts/shared/` | `scripts/shared/` | `scripts/shared/` | `scripts/shared/` | `scripts/shared/` | (skipped) |

> **Note for Agentforce Vibes:** Assets are inlined into the markdown rules. Scripts and references are not included since automatic validation hooks are not supported.

## Running Validation Scripts

Unlike Claude Code (which runs hooks automatically), other CLIs require manual validation:

```bash
# Navigate to installed skill
cd .opencode/skill/sf-apex/scripts

# Run Apex validation
python validate_apex.py /path/to/MyClass.cls

# Run Flow validation
cd .opencode/skill/sf-flow/scripts
python validate_flow.py /path/to/MyFlow.flow-meta.xml
```

## CLI-Specific Notes

### OpenCode

- Looks for skills in `.opencode/skill/` (project) or `~/.opencode/skill/` (global)
- Also supports `.claude/skills/` for Claude Code compatibility
- Skills are auto-discovered on startup

### Codex CLI

- Follows the Agent Skills spec (assets/, references/, scripts/)
- Enable skills with `codex --enable skills`
- Looks in `.codex/skills/` (project) or `~/.codex/skills/` (global)

### Gemini CLI

- Installs to `~/.gemini/skills/` (user scope) by default
- Can symlink with Claude Code: `ln -s ~/.gemini/skills/sf-apex ~/.claude/skills/sf-apex`
- Benefits from Gemini's 1M+ token context window

### Droid CLI (Factory.ai)

- Claude Code compatible - uses same SKILL.md format
- Installs to `.factory/skills/` (project) or `~/.factory/skills/` (user)
- Can also auto-discover from `.claude/skills/` directory
- Requires Custom Droids enabled: `/settings → Experimental → Custom Droids`
- Docs: [docs.factory.ai/cli/configuration/skills](https://docs.factory.ai/cli/configuration/skills)

### Cursor

- Uses MDC (Markdown with metadata) format instead of SKILL.md
- Skills are transformed into `.mdc` rule files with YAML frontmatter
- Installs to `.cursor/rules/` directory
- For full Agent Skills support, consider [SkillPort](https://github.com/gotalab/skillport) MCP bridge
- Validation scripts available but must be run manually

**Cursor MDC Format:**
```yaml
---
description: Salesforce Apex development skill
globs: ["**/*.cls", "**/*.trigger"]
alwaysApply: false
---

# Skill content here...
```

### Agentforce Vibes

[Agentforce Vibes](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/einstein-overview.html) is Salesforce's enterprise vibe-coding tool, built on a fork of Cline with strong Model Context Protocol (MCP) support.

- Uses pure markdown files in `.clinerules/` directory
- Files are auto-combined in alphanumeric order (numbered prefixes: `01-sf-apex.md`, etc.)
- Templates are inlined directly into the markdown rules (self-contained)
- Includes Agentforce-specific tips (e.g., `/newrule` command reference)
- Integrates with Salesforce DX MCP Server for additional tools
- Available in VS Code and Open VSX marketplaces

**Installation:**
```bash
python tools/installer.py --cli agentforce-vibes --all
```

**Output structure:**
```
.clinerules/
├── 01-sf-apex.md
├── 02-sf-flow.md
├── 03-sf-lwc.md
└── ... (13 skills total)
```

**Learn More:**
- [Agentforce Vibes Blog](https://developer.salesforce.com/blogs/2025/10/unleash-your-innovation-with-agentforce-vibes-vibe-coding-for-the-enterprise)
- [Five Pro Tips](https://developer.salesforce.com/blogs/2025/12/five-pro-tips-for-using-agentforce-vibes)

## Troubleshooting

### "No skills found in repository"

Make sure you're running from the sf-skills repository root:

```bash
cd /path/to/sf-skills
python tools/installer.py --list
```

### "Skill already exists"

Use `--force` to overwrite:

```bash
python tools/installer.py --cli opencode --skills sf-apex --force
```

### Scripts fail with import errors

Ensure shared modules are bundled. Reinstall with `--force`:

```bash
python tools/installer.py --cli opencode --all --force
```

### CLI not detected

The auto-detect feature checks for:
- OpenCode: `opencode` command or `~/.opencode/` directory
- Codex: `codex` command
- Gemini: `gemini` command or `~/.gemini/` directory
- Droid: `droid` command or `~/.factory/` directory
- Cursor: `cursor` command or `~/.cursor/` directory
- Agentforce Vibes: Not auto-detected (use `--cli agentforce-vibes` explicitly)

If your CLI is installed but not detected, use `--cli` explicitly.

### SSL Certificate Errors

If installation fails with `[SSL: CERTIFICATE_VERIFY_FAILED]`, this is common on macOS when Python is installed from python.org (it bundles its own OpenSSL and doesn't use the macOS system keychain).

**Fix 1: Run the macOS certificate installer (recommended)**

```bash
# Find and run the Install Certificates command for your Python version
/Applications/Python\ 3.*/Install\ Certificates.command
```

**Fix 2: Install certifi + set SSL_CERT_FILE**

```bash
pip3 install certifi
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
# Then re-run the installer
```

> **Note:** If `certifi` is installed, the sf-skills installer auto-detects it — no env var needed.

**Fix 3: Use Homebrew Python (includes proper CA certs)**

```bash
brew install python3
# Homebrew Python uses system certificates — no SSL issues
```

**Fix 4: Corporate proxy / custom CA bundle**

```bash
export SSL_CERT_FILE=/path/to/corporate-ca-bundle.pem
# Then re-run the installer
```

## Troubleshooting: 401 Authentication Error

If Claude Code fails with a 401 error after installing sf-skills:

```
401 {"error":{"message":"Authentication Error, No api key passed in","type":"auth_error","code":"401"}}
```

This means `settings.json` lost its authentication configuration during installation.

### Quick Fix

```bash
# Restore settings.json from automatic backup
python3 ~/.claude/sf-skills-install.py --restore-settings
```

### Diagnose the Issue

```bash
# Run all diagnostic checks
python3 ~/.claude/sf-skills-install.py --diagnose
```

This checks: settings.json validity, auth fields, hook scripts, Python environment,
backup status, and hook execution.

### Manual Recovery

If no backups are available:

```bash
# List available backups
ls -la ~/.claude/.settings-backups/

# Manually copy a backup
cp ~/.claude/.settings-backups/settings.pre-modify.YYYYMMDD-HHMMSS.json ~/.claude/settings.json

# Validate the restored file
python3 -c "import json; d = json.load(open('$HOME/.claude/settings.json')); print(f'{len(d)} keys:', list(d.keys()))"

# Restart Claude Code
```

### CLI Reference

| Command | Description |
|---------|-------------|
| `--diagnose` | Run 7-point diagnostic check on installation health |
| `--restore-settings` | Interactively restore settings.json from latest backup |
| `--profile [action] [name]` | Profile management (see below) |
| `--status` | Show installation status and check for updates |
| `--update` | Check and apply updates (version + content) |
| `--force-update` | Force reinstall even if up-to-date |
| `--uninstall` | Remove sf-skills installation |
| `--dry-run` | Preview changes without applying |
| `--force` | Skip confirmation prompts |

## Enterprise Claude Code (Bedrock Gateway)

Salesforce provides Claude Code to internal engineers via a custom API gateway (LLM Gateway Express → AWS Bedrock). These "enterprise" installs differ structurally from personal Anthropic subscriptions.

### Detection Signals

| Signal | Personal | Enterprise |
|--------|----------|------------|
| `forceLoginMethod` | `"claudeai"` | `"console"` |
| `CLAUDE_CODE_USE_BEDROCK` | `"0"` | `"1"` |
| `ANTHROPIC_BEDROCK_BASE_URL` | absent | gateway URL |
| `ANTHROPIC_AUTH_TOKEN` | absent | gateway API key |
| Model ID format | `claude-opus-4-5-*` | `us.anthropic.claude-*` |
| Telemetry | enabled | disabled |

The installer auto-detects enterprise vs personal environments and adapts diagnostics accordingly.

### Profile Management

Profiles let you safely switch between personal and enterprise `settings.json` configurations without losing your hooks, permissions, or other preferences.

```bash
# Save your current config as a named profile
python3 ~/.claude/sf-skills-install.py --profile save personal
python3 ~/.claude/sf-skills-install.py --profile save enterprise

# List all saved profiles
python3 ~/.claude/sf-skills-install.py --profile list

# Switch to a different profile (hooks/permissions preserved)
python3 ~/.claude/sf-skills-install.py --profile use enterprise

# Preview a switch without making changes
python3 ~/.claude/sf-skills-install.py --profile use enterprise --dry-run

# View profile contents (auth tokens redacted)
python3 ~/.claude/sf-skills-install.py --profile show enterprise

# Delete a profile
python3 ~/.claude/sf-skills-install.py --profile delete old-config
```

### What Gets Preserved During Profile Switches

| Category | Behavior | Examples |
|----------|----------|---------|
| **Auth layer** | Replaced from profile | `forceLoginMethod`, `env`, `model`, `forceLoginOrgUUID` |
| **User preferences** | Preserved from current | `hooks`, `permissions`, `statusLine`, `outputStyle` |
| **sf-skills config** | Preserved from current | `hooks` (always), `enabledPlugins`, `attribution` |

### Enterprise Limitations

- **LLM-based evaluation**: Disabled for enterprise. The `llm-eval.py` hook uses the Anthropic SDK directly, which doesn't route through the Bedrock gateway. Pattern-based guardrails still provide equivalent protection.
- **Telemetry**: Disabled by enterprise configuration.

## Contributing

To add support for a new CLI:

1. Create `tools/cli_adapters/{cli_name}.py`
2. Inherit from `CLIAdapter` base class
3. Implement required methods:
   - `cli_name` property
   - `default_install_path` property
   - `transform_skill_md()` method
4. Register in `tools/cli_adapters/__init__.py`

See existing adapters for examples.

## License

Same as the main sf-skills repository.
