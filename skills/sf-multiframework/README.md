# sf-multiframework

⚛️ **Salesforce Multi-Framework (Beta) skill** — Build React apps that run on the Agentforce 360 Platform via the `UIBundle` metadata type.

> Part of **Jag Valaiyapathy's SF Skills** framework — same format, rubric, and cross-skill orchestration conventions as [`sf-ai-agentforce`](../sf-ai-agentforce/), [`sf-ai-agentscript`](../sf-ai-agentscript/), [`sf-lwc`](../sf-lwc/), [`sf-apex`](../sf-apex/). Built from official [Salesforce Developer documentation](references/official-sources.md) and [`trailheadapps/multiframework-recipes`](https://github.com/trailheadapps/multiframework-recipes). Works in any MCP-capable agent or IDE — Agentforce Vibes is optional, not required.

> Beta status: sandbox + scratch orgs only, default language must be `en_US`. Once enabled in an org, the feature **cannot be disabled**.

## Features

- ✅ End-to-end React app authoring on the Salesforce Platform
- ✅ `UIBundle` metadata, `ui-bundle.json`, and `.uibundle-meta.xml` reference
- ✅ Data SDK (`@salesforce/sdk-data`) + GraphQL UI API patterns
- ✅ Codegen workflow for type-safe GraphQL operations
- ✅ Strict / Tolerant / Permissive error-handling strategies
- ✅ Agentforce Conversation Client (ACC) embed patterns
- ✅ Three styling tracks: SLDS blueprints · `design-system-react` · Tailwind + shadcn
- ✅ Internal (App Launcher) vs External (Experience Cloud) app templates
- ✅ Cross-skill orchestration with `sf-apex`, `sf-ai-agentforce`, `sf-deploy`

## Requirements

| Requirement | Value |
|---|---|
| Org type | Sandbox or Scratch (Beta) |
| Default language | `en_US` |
| API version | v66.0+ |
| Node.js | v22+ |
| `sf` CLI | latest with `@salesforce/plugin-ui-bundle-dev` |
| License (external apps) | Customer / Partner Community user licenses |
| ACC license | Agentforce + Employee Agent configured |

## Quick Start

### 1. Enable Multi-Framework in your org
Setup → "Salesforce Multi-Framework" → **Enable Beta**.

### 2. Install the CLI plugin
```bash
sf plugins install @salesforce/plugin-ui-bundle-dev
```

### 3. Scaffold an app
```bash
# Internal employee app (App Launcher target)
sf template generate ui-bundle --name myApp --template reactinternalapp

# External B2B/B2C portal (Experience Cloud target)
sf template generate ui-bundle --name myApp --template reactexternalapp
```

### 4. Develop locally
```bash
cd force-app/main/default/uiBundles/myApp
npm install
npm run graphql:schema      # introspect connected org
npm run graphql:codegen     # generate types
npm run dev                 # Vite dev server
```

### 5. Deploy
```bash
npm run build
cd ../../../../..
sf project deploy start --source-dir force-app/main/default/uiBundles/myApp --target-org TARGET
```

## Scoring System

| Category | Points | Focus |
|---|---|---|
| Project Structure | 20 | `uiBundles/` layout, metadata files, output dir |
| Routing & Hosting | 15 | `ui-bundle.json` SPA fallback, target match |
| Data Access | 25 | Data SDK usage, GraphQL `{ value }` shape, error strategy |
| Styling Discipline | 10 | One system per component, SLDS focus tokens |
| ACC Integration | 15 | Cookies, Trusted Domains, mount lifecycle |
| Deployment Readiness | 15 | Build artifacts, file-count budget, target org sanity |

**Thresholds:** 90+ Excellent · 75–89 Good · 60–74 Needs Work · <60 Block deploy

Full rubric: [references/scoring-rubric.md](references/scoring-rubric.md)

## Key Rules

1. **Use `@salesforce/sdk-data`** — never raw `fetch()` / `axios` to Salesforce endpoints.
2. **GraphQL UI API wraps every field in `{ value }`** — comment this for React-first developers.
3. **`ui-bundle.json` needs `routing.fallback: "index.html"`** for SPA refresh on sub-routes.
4. **`.uibundle-meta.xml` `target` is binding** — `AppLauncher` vs `Experience` cannot be hot-swapped.
5. **ACC requires My Domain cookies + Trusted Domains for Inline Frames + Agentforce preference** — all three.
6. **One styling system per component** — mixing SLDS + Tailwind inside a single component is the most common review failure.
7. **Beta = sandbox + scratch only, `en_US` only**. DE orgs and Playgrounds are unsupported.
8. **Multi-Framework can't be disabled** once enabled in an org. Treat the toggle as one-way.
9. **UIBundle has a 2,500-file ceiling** — prune `dist/` source maps and unused assets.
10. **Inside a React UI bundle**, `lightning/*` modules, `@wire`, and most `@salesforce/*` packages are **not** supported (`@salesforce/sdk-data`, the ACC, and `@salesforce/ui-bundle` are exceptions).

## Documentation

| Document | Description |
|---|---|
| [SKILL.md](SKILL.md) | Main entry point with rules and workflow |
| [references/](references/) | Topic-specific deep guides |
| [assets/](assets/) | Reference `ui-bundle.json`, metadata, and code snippets |

## Cross-Skill Workflow

```
sf-apex (REST endpoints) ─┐
sf-ai-agentforce (Agent) ─┤→  sf-multiframework  →  sf-deploy
sf-permissions (PSets) ───┘                          (CI deploy)
```

## Official Resources

- [React App Overview (Beta)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-overview.html)
- [Org Configuration (Beta)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-setup.html)
- [Multi-Framework Recipes (GitHub)](https://github.com/trailheadapps/multiframework-recipes)

## License

MIT
