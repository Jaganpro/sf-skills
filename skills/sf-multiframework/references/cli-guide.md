# CLI Guide

> Prefer **Salesforce DX MCP** for deployments when available (`mcp_Salesforce_DX_deploy_metadata`, `mcp_Salesforce_DX_get_username`). The CLI commands below are the documented fallback and what most people run locally.

## Required plugins

```bash
sf plugins install @salesforce/plugin-ui-bundle-dev
```

This plugin provides:

- `sf template generate ui-bundle` — scaffolding
- Runtime support used by `npm run dev` for the Vite plugin

## Scaffolding

### Add a UI bundle to an existing project

```bash
sf template generate ui-bundle \
  --name myApp \
  --template reactinternalapp     # or reactexternalapp
```

The `--name` becomes the bundle directory name and the metadata API name. Stick with a developer-name-friendly identifier (no spaces, no leading digits).

### Generate a new DX project + external app

```bash
sf template generate project --template reactexternalapp
```

Use this when starting from a clean directory.

## Local development

```bash
cd force-app/main/default/uiBundles/myApp
npm install
npm run graphql:schema     # Introspects the connected org → schema.graphql
npm run graphql:codegen    # Reads codegen.yml → src/api/graphql-operations-types.ts
npm run dev                # Vite dev server (default http://localhost:5173)
```

Notes:

- `graphql:schema` requires an **already-authorized org**. Make sure `sf org list` shows your target.
- The Vite plugin (`@salesforce/vite-plugin-ui-bundle`) proxies Salesforce API calls during dev so the SDK works against the real org.
- Add `http://localhost:<port>` to **Trusted Domains for Inline Frames** if you're testing ACC locally.

## Build

```bash
npm run build
```

Typically `tsc --noEmit && vite build`. Output lands in the directory referenced by `ui-bundle.json` `outputDir` (Vite default `dist/`). Avoid `tsc -b` unless project references are intentionally configured, because it can emit TypeScript build artifacts into the deployable bundle root.

`npm run lint` and `npm run build` should both pass before you deploy.

## Deploy (CLI)

```bash
# From the project root
sf project deploy start \
  --source-dir force-app/main/default/uiBundles/myApp \
  --target-org TARGET_ORG
```

For external apps, deploy the companion folders **in the same call**:

```bash
sf project deploy start \
  --source-dir force-app/main/default/uiBundles/myApp \
  --source-dir force-app/main/default/digitalExperiences \
  --source-dir force-app/main/default/digitalExperienceConfigs \
  --source-dir force-app/main/default/networks \
  --source-dir force-app/main/default/sites \
  --target-org TARGET_ORG
```

> **Only one UI bundle deploys per metadata push** is the safe pattern. If you have multiple bundles in your project, deploy them in separate `sf project deploy start` calls.

## Deploy (MCP — preferred)

```js
// 1. Get the org alias
mcp_Salesforce_DX_get_username({ defaultTargetOrg: true })

// 2. Deploy
mcp_Salesforce_DX_deploy_metadata({
  usernameOrAlias: "myorg",
  sourceDir: ["force-app/main/default/uiBundles/myApp"]
})
```

For external apps, include all four supporting folders in `sourceDir`.

## Open the org

```bash
sf org open
# Or via MCP:
mcp_Salesforce_DX_open_org({ usernameOrAlias: "myorg" })
```

## Sample data import

Most templates include a `data/` folder with a tree plan for sample records:

```bash
sf data import tree --plan ./data/data-plan.json --target-org TARGET_ORG
```

## Common CLI failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `sf template generate ui-bundle` not recognized | Plugin missing | `sf plugins install @salesforce/plugin-ui-bundle-dev` |
| `npm run graphql:schema` fails with auth error | No authorized org in this shell | `sf org login web -a alias` and re-run |
| Deploy fails with file-count error | UIBundle ≥ 2,500 files | Disable source maps, prune `dist/` |
| Deploy succeeds but app missing from App Launcher | `<isActive>` is `false` or `<target>` mismatch | Set `isActive` true; confirm target |
| External app deploys but site is empty | Forgot to deploy `digitalExperiences`, `networks`, or `sites` | Re-deploy with all four folders |
| Vite dev server data calls 401 | Org authorization expired | `sf org login web -a alias` |
| Build OK locally but deploy fails | `outputDir` in `ui-bundle.json` doesn't match where the build emits | Align `outputDir` with `vite.config.ts` `build.outDir` |

## Useful org-side commands

```bash
sf org assign permset -n recipes                     # Assign starter PSet
sf org list                                          # See all authorized orgs
sf org display --target-org alias --verbose          # Confirm API version, instance URL
sf org open --target-org alias                       # Open the org in browser
```
