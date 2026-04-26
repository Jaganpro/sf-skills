# Troubleshooting

Bucketed by where the failure happens. Each row is a real failure mode seen in Multi-Framework Beta projects with the **first** thing to check.

## Setup & enablement

| Symptom | Likely cause | First check |
|---|---|---|
| Beta toggle missing in Setup | Org is DE / Trailhead Playground (not supported) | Use a sandbox or scratch org |
| Beta toggle visible but greyed out | User missing **Customize Application** | Assign System Administrator profile or equivalent permission |
| App loads in English only / blank screens elsewhere | Org default language ≠ `en_US` | Scratch: set `"language": "en_US"`. Sandbox: change org language |
| `sf template generate ui-bundle` not recognized | `@salesforce/plugin-ui-bundle-dev` not installed | `sf plugins install @salesforce/plugin-ui-bundle-dev` |
| `npm install` fails with Vite peer conflict | Salesforce Vite plugin and latest `@vitejs/plugin-react` target different Vite majors | Pin compatible majors, e.g. Vite 7 + `@vitejs/plugin-react` 5 |

## Project & build

| Symptom | Likely cause | First check |
|---|---|---|
| Build succeeds, deploy fails | `outputDir` in `ui-bundle.json` doesn't match Vite `build.outDir` | Align both to `dist` |
| Deploy fails with file-count error | UIBundle exceeded 2,500 files | Disable source maps in production; prune `dist/` |
| Deploy succeeds but app missing from App Launcher | `<isActive>false</isActive>` or wrong `<target>` | Set `isActive: true`; confirm target is `AppLauncher` |
| Deploy fails: `ui-bundle.json contains unknown property: 'apiVersion'` | Current validator only allows `outputDir`, `routing`, `headers` | Remove `apiVersion` from `ui-bundle.json`; rely on `sfdx-project.json` / deploy API version |
| Deploy fails: `apiVersion invalid at this location in type UIBundle` | `.uibundle-meta.xml` includes unsupported `<apiVersion>` | Remove `<apiVersion>` from `.uibundle-meta.xml` |
| Deploy fails: `isEnabled invalid at this location in type UIBundle` | Metadata uses LWC-style or stale field name | Use `<isActive>true</isActive>` and include `<version>` |
| Deploy report includes `vite.config.js`, `.d.ts`, or `*.tsbuildinfo` | `tsc -b` emitted TypeScript build artifacts into the bundle root | Use `tsc --noEmit && vite build`, delete artifacts, redeploy |
| Deploy succeeds but external app site is empty | Forgot to deploy `digitalExperiences/`, `networks/`, or `sites/` | Re-deploy with all four metadata folders |
| Hard refresh on `/dashboard` returns 404 | `routing.fallback` not set to `index.html` | Add `"fallback": "index.html"` under `routing` |
| Trailing slash redirects loop | Conflicting `trailingSlash` and `redirects` rules | Set `trailingSlash: "never"`, remove redundant redirects |
| Browser console: 404 on `/assets/...` after deploy | Vite `base` not configured for the served path | Set Vite `base` to match Salesforce-served path; rebuild |

## Data SDK / GraphQL

| Symptom | Likely cause | First check |
|---|---|---|
| `Cannot read properties of undefined (reading 'value')` | Forgot the UI API `{ value }` field wrapper | Read fields as `record.Name.value` |
| `edges` is null / empty despite data existing | Filter excludes everything; permission issue | Drop the filter; confirm running user has access |
| Codegen produces empty or `any` types | `schema.graphql` missing or scalars not mapped | `npm run graphql:schema` then add scalar mappings to `codegen.yml` |
| `GraphQL surface unavailable` thrown | Running in a surface that doesn't expose `graphql` | Use `sdk.fetch?.()` with allow-listed REST endpoint |
| 401 on every call after deploy | Bypassing Data SDK | Refactor to `createDataSDK()` / `sdk.graphql?.()` / `sdk.fetch?.()` |
| Mutation succeeds but returned record has errors | Field can't be selected on mutation return | Switch call site to **Permissive** error strategy or remove offending fields |
| `gql` template provides no IntelliSense | GraphQL ESLint plugin / extension not configured | Install `@graphql-eslint/eslint-plugin`; configure `.eslintrc` |
| Local dev fetches succeed, deployed fetches 401/403 | `basePath` mismatch between dev and deployed surface | Don't hard-code paths; let SDK resolve |
| React app needs Apex logic from an LWC controller | LWC `@salesforce/apex` imports are unavailable in React UI bundles | Expose Apex as REST and call it through `sdk.fetch?.()` |
| Apex compile fails: `Invalid type: aiplatform.ModelsAPI...` | Models API / Generative AI settings not enabled for the org | Enable the required org settings; don't replace React Data SDK calls with raw Salesforce fetches |

## Local dev (Vite)

| Symptom | Likely cause | First check |
|---|---|---|
| Vite dev server starts but data calls 401 | No authorized org in this shell | `sf org login web -a alias` |
| Vite proxy doesn't forward to org | `@salesforce/vite-plugin-ui-bundle` not in `vite.config.ts` | Add the plugin |
| ACC FAB doesn't appear locally | `localhost` origin not in Trusted Domains | Add `http://localhost:<port>` with iFrame type Lightning Out |
| HMR doesn't pick up `.graphql` changes | Codegen not re-run | `npm run graphql:codegen` after every `.graphql` edit (or add a watcher) |

## Agentforce Conversation Client (ACC)

| Symptom | Likely cause | First check |
|---|---|---|
| FAB never appears | Trusted Domains not added or cookies still restricted | Verify both: My Domain cookie policy off + Trusted Domains entry with iFrame type Lightning Out |
| Panel opens but disconnects on navigation | Origin mismatch (e.g. wrong port) | Add the **exact** origin including port |
| Welcome message missing | Agentforce preference disabled | Setup → Einstein → Agentforce Studio → enable Agentforce |
| Rich Lightning Types render as plain text | Agent action output schema not using a Lightning Type | Update GenAiFunction output schema (delegate to sf-ai-agentforce) |
| Streaming cuts off mid-response | Network keepalive issue or session expiry | Inspect devtools Network; refresh session; retry |
| Branding tokens don't apply | SDK option key names differ from docs read | Check installed `@salesforce/agentforce-conversation-client` version's TypeScript declarations |
| ACC works in prod but not local | `localhost` origin missing from Trusted Domains | Add `http://localhost:<port>` |

## Styling

| Symptom | Likely cause | First check |
|---|---|---|
| SLDS classes don't apply | `@salesforce-ux/design-system` CSS not imported globally | Import in `global.css` once at app entry |
| `design-system-react` icons missing | No `IconSettings` wrapper | Wrap app/component subtree in `<IconSettings iconPath="/assets/icons">` |
| Tailwind utilities don't override SLDS | Specificity / source order | Pick **one** system per component; don't mix |
| Dark mode variables don't switch | `.dark` class not applied to `<html>` | Add `class="dark"` toggle on root |
| Focus ring is grey instead of Salesforce blue | Default shadcn `--ring` token | Set `--ring: #0176d3` in `global.css` |

## External (Experience Cloud) apps

| Symptom | Likely cause | First check |
|---|---|---|
| Site shows but app doesn't render | `appContainer` or `appSpace` wrong in `content.json` | `appContainer: true`; `appSpace: "<NamespacePrefix>__<DeveloperName>"` (or `c__<DeveloperName>`) |
| Site URL 404s | `networks/` or `sites/` not deployed | Deploy all four metadata folders together |
| User can't log in | Missing Customer / Partner Community license | Provision the right license type |
| Trying to edit site in Experience Builder | Not supported for React-app sites | Skip Builder; edit via metadata |

## Generic recovery checklist

When something is broken and you're not sure where:

1. Did `npm run build` pass? If no, fix the build first.
2. Did `npm run lint` pass? Lint errors often mask runtime bugs.
3. Is `schema.graphql` fresh? Re-run `npm run graphql:schema` and `npm run graphql:codegen`.
4. Is the org authorized in this shell? `sf org list` then `sf org login web -a alias` if needed.
5. Is the running user assigned the bundle's permission set?
6. Did a second deploy report source-tracking conflicts immediately after a successful create? If yes, and the org changes are your just-created bundle, redeploy the local bundle with `--ignore-conflicts`.
7. For ACC: re-walk the [acc-integration.md](acc-integration.md) checklist top to bottom.
8. For external apps: confirm all four metadata folders deployed.
9. Compare against the [`multiframework-recipes`](https://github.com/trailheadapps/multiframework-recipes) reference repo for the exact pattern you're trying to use.

## Reporting bugs to Salesforce

This is a **Beta**. Real issues exist beyond what's listed here. When filing:

- Include org type (sandbox / scratch), org language, API version
- Include `sf --version` and `node -v`
- Include `package.json` of the bundle (versions of `@salesforce/sdk-data`, `@salesforce/agentforce-conversation-client`)
- Include exact `ui-bundle.json` and `<app>.uibundle-meta.xml`
- Reproduce against `multiframework-recipes` if possible to isolate
