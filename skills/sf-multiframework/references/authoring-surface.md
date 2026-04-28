# Authoring Surfaces

Salesforce markets **Agentforce Vibes** as *an* authoring path for Multi-Framework. It is one option among several. This skill is designed to work in any of:

- **Any MCP-capable AI coding assistant** (IDE-integrated or CLI-based)
- **Agentforce Vibes** (VS Code extension)
- **Plain `sf` CLI + editor** (no AI assistant at all)

The platform pieces — CLI, plugin, project template, Data SDK, ACC — are the same regardless of authoring surface. This file captures what differs.

## Why this matters

If you work with an MCP-capable assistant, you don't need the Vibes extension to build UI bundles. Install the CLI + plugin and the rest is standard npm / Vite work with this skill layered in for Salesforce-specific guidance.

If you work in Vibes, it brings natural-language prompts that scaffold Data SDK GraphQL code (operations, types, error handling) and ACC integration. Use those prompts as a starting point; the rules in this skill still apply to the output.

## Surface comparison

| Capability | Generic MCP-capable assistant | Agentforce Vibes |
|---|---|---|
| Scaffold project with `sf template generate ui-bundle` | ✅ plain CLI | ✅ CLI; Vibes can also prompt |
| Generate GraphQL query + types + component | ✅ via this skill | ✅ built-in slash commands |
| Generate ACC widget mount | ✅ via [acc-integration.md](acc-integration.md) | ✅ built-in prompt |
| MCP servers for org context | ✅ install any MCP server | ✅ "Metadata Experts" + "API Context" MCP servers shipped |
| Operates on existing code | ✅ | ✅ |
| Works offline (no live org) | ✅ | ⚠️ some prompts require a connected org |
| LLM provider | Your choice | Salesforce's Einstein models |

Neither surface is "correct" — pick based on team preference and which LLM you want behind the generation.

## CLI + plugin requirements (all surfaces)

```bash
# Node + sf CLI
node --version   # ≥ 22
sf --version     # latest

# UI bundle plugin
sf plugins install @salesforce/plugin-ui-bundle-dev

# Verify
sf template generate ui-bundle --help
```

If `sf template generate ui-bundle` is not recognized, the plugin didn't install. Re-run install; if it still fails, `sf plugins uninstall @salesforce/plugin-ui-bundle-dev && sf plugins install @salesforce/plugin-ui-bundle-dev`.

## Vibes-specific: enabling MCP servers in-org

If (and only if) you use Vibes:

1. Setup → MCP Servers → enable **Metadata Experts** and **API Context**
2. In VS Code, open the Agentforce Vibes panel and confirm both connect
3. The MCP servers use your authenticated `sf` CLI session

Non-Vibes assistants don't need this — their MCP wiring is client-side (in whatever config file the assistant uses).

## Working without Vibes

A reasonable non-Vibes workflow:

```bash
# 1. Scaffold
cd my-dx-project
sf template generate ui-bundle --name myApp --template reactinternalapp
cd force-app/main/default/uiBundles/myApp
npm install

# 2. Generate the schema once against a connected org
npm run graphql:schema

# 3. Ask the assistant to
#    "add a recipe that lists the first 10 Accounts with aliased multi-object query"
#    — the assistant writes the .graphql file, runs codegen, and emits the component.
#    Apply this skill's rules (UI API `{ value }`, inline `gql` for recipes, etc.)

# 4. Build + deploy
npm run build
cd ../../../../..
sf project deploy start --source-dir force-app/main/default/uiBundles/myApp
```

## Prompt patterns that work in any assistant

When telling an assistant to generate a recipe, include:

1. **The target object + fields** (e.g. "Contact: Name, Title, Phone")
2. **The operation** (query first 10 / query by ID / mutation create)
3. **The error strategy** (strict / tolerant / permissive — see [error-handling.md](error-handling.md))
4. **The styling system** (SLDS / DSR / shadcn)
5. **Whether `gql` is inline or external `.graphql`** (recipes: inline; complex reusable: external + codegen)

Example:

> Build a recipe `src/recipes/read-data/SingleContact.tsx` that queries the first Contact by ID via inline `gql`, uses strict error handling, and renders an SLDS card. Mock the SDK in a sibling test file with `vitest-axe` assertions.

Any assistant that can read this skill's references will produce the right shape.

## When to switch surfaces

| You're in… | Consider switching when… |
|---|---|
| Vibes | You want a different LLM; you need MCP servers outside Vibes' bundled set; you want terminal-native workflows |
| Generic assistant | You want the in-org MCP context for metadata / API introspection; the team standardizes on Vibes |

## What *not* to do

- ❌ Don't mix generated files across assistants without review — each has quirks (import ordering, JSX syntax, test patterns). Apply [recipe-conventions.md](recipe-conventions.md) as the arbiter.
- ❌ Don't rely on any assistant's memory of Multi-Framework — the feature is Beta and changes frequently. Point the assistant at this skill + the official docs ([official-sources.md](official-sources.md)).
- ❌ Don't install Vibes on a project where the team uses a different assistant unless there's a reason — the surfaces can generate conflicting patterns (e.g. external `.graphql` vs inline `gql`).
