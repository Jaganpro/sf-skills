# sf-multiframework — Asset Reference

Reference files used by the skill. **Copy and adapt** — these are minimal starters, not full-featured templates.

## `templates/`

Drop-in metadata + config files for a Multi-Framework UI bundle.

| File | Use |
|---|---|
| `myApp.uibundle-meta.xml` | UIBundle metadata. Rename file to match your `--name`. Update `<masterLabel>` and `<target>`. |
| `ui-bundle.json` | Runtime configuration with SPA fallback. Keep top-level keys to `outputDir`, `routing`, and `headers`. |
| `external-content.json` | `digitalExperiences/sfdc_cms_site/content.json` for external (`Experience`-target) apps. Update `appSpace` to `c__<DeveloperName>` (or `<Namespace>__<DeveloperName>`). |
| `vite.config.ts` | Minimal Vite config with `@salesforce/vite-plugin-ui-bundle` and path aliases. |
| `codegen.yml` | GraphQL codegen config with full UIAPI scalar mappings. Drop into the bundle root. |

## `examples/`

Reference React + GraphQL code patterns.

| File | Demonstrates |
|---|---|
| `SingleRecord.tsx` | Recipe-style inline `gql` + `{ value }` UIAPI shape + Loading / Error / Loaded states |
| `graphqlClient.ts` | Production-style Strict / Tolerant / Permissive wrappers around `sdk.graphql?.()` |
| `listAccountsQuery.graphql` | External-file pattern with variables + connection pagination |
| `AccChatPanel.tsx` | Minimal Agentforce Conversation Client mount with `useRef` + cleanup |
| `global.css` | Tailwind / shadcn design-token entry point with Salesforce-blue focus ring + dark mode |

## What's intentionally not here

- A full LWR `digitalExperiences` bundle — too org-specific; use `sf template generate ui-bundle --template reactexternalapp`.
- Complete `package.json` for the bundle — versions move too fast; use the template scaffold.
- ESLint config — the templates ship a flat config that's well-tuned to React 19 + GraphQL ESLint plugin.

## How to use

1. Scaffold via `sf template generate ui-bundle` first (preferred).
2. Use these files when you need to **understand** what the scaffold did, or when you need to **add** something to a manually-built bundle.
3. Always cross-check against [`trailheadapps/multiframework-recipes`](https://github.com/trailheadapps/multiframework-recipes) for the current canonical pattern.
