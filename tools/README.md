# sf-skills Installation Tools

Tools for installing sf-skills into Claude Code.

## Files

| File | Purpose |
|------|---------|
| `install.py` | Unified Python installer — downloads skills, hooks, LSP engine, and agents from GitHub |
| `install.sh` | Bash wrapper — checks prerequisites (Python, Homebrew, SF CLI, Java, Node) then runs `install.py` |

## Quick Start

### One-liner (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.sh | bash
```

The bash wrapper checks your environment (Python 3.12+, Homebrew, SSL certs, Claude Code directory) and offers to install missing dependencies before downloading and running the Python installer.

### Direct Python install

```bash
curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.py | python3
```

### From a local clone

```bash
git clone https://github.com/Jaganpro/sf-skills
cd sf-skills
python3 tools/install.py
```

## install.py — CLI Reference

```
python3 install.py                        # Interactive install
python3 install.py --update               # Check version + content changes
python3 install.py --force-update         # Force reinstall even if up-to-date
python3 install.py --uninstall            # Remove sf-skills
python3 install.py --status               # Show installation status
python3 install.py --diagnose             # Run 7-point diagnostic check
python3 install.py --restore-settings     # Restore settings.json from backup
python3 install.py --dry-run              # Preview changes without applying
python3 install.py --force                # Skip confirmation prompts
```

### Profile Management

Switch between personal (Anthropic) and enterprise (Bedrock gateway) configurations:

```
python3 install.py --profile list             # List saved profiles
python3 install.py --profile save personal    # Save current config as profile
python3 install.py --profile use enterprise   # Switch to enterprise config
python3 install.py --profile show enterprise  # View profile (tokens redacted)
python3 install.py --profile delete old       # Delete a profile
```

## What Gets Installed

| Component | Destination | Description |
|-----------|-------------|-------------|
| 19 sf-* skills | `~/.claude/skills/sf-*/` | Native Claude Code skill discovery |
| Hook scripts | `~/.claude/hooks/` | Guardrails, auto-approval, validation |
| LSP engine | `~/.claude/lsp-engine/` | Apex, LWC, AgentScript language servers |
| Agent definitions | `~/.claude/agents/` | FDE + PS agent definitions |

## install.sh — Environment Checks

The bash wrapper runs 5 phases before invoking `install.py`:

1. **Environment** — OS/arch detection, proxy detection, Rosetta check
2. **Required deps** — curl, Homebrew (macOS), Python 3.12+, SSL certs, Claude Code
3. **Optional deps** — Salesforce CLI, Java 11+ (Apex LSP), Node 18+ (LWC validation)
4. **Installation** — Downloads and runs `install.py --force --called-from-bash`
5. **Verification** — Health check and next-steps guidance

## Troubleshooting

### SSL Certificate Errors

Common on macOS when Python is installed from python.org:

```bash
# Option 1: Install certifi (installer auto-detects it)
pip3 install certifi

# Option 2: Run the macOS certificate installer
/Applications/Python\ 3.*/Install\ Certificates.command

# Option 3: Use Homebrew Python (includes proper CA certs)
brew install python3
```

### 401 Authentication Error After Install

```bash
# Restore settings.json from automatic backup
python3 ~/.claude/sf-skills-install.py --restore-settings

# Or run full diagnostics
python3 ~/.claude/sf-skills-install.py --diagnose
```

## Cross-CLI Distribution

For installing sf-skills into other agentic coding CLIs (OpenCode, Codex, Gemini, Cursor, etc.), use the `npx` method:

```bash
npx skills add github:Jaganpro/sf-skills
```

See the [main README](../README.md) for details.

## License

Same as the main sf-skills repository.
