# Scoring Rubric

Total: **100 points** across 6 categories. Use this to grade an app or PR.

## Thresholds

| Score | Meaning |
|---|---|
| 90+ | Deploy with confidence |
| 75–89 | Good — review warnings before deploying |
| 60–74 | Needs focused revision |
| < 60 | Block deploy |

---

## Project Structure (20 points)

| Item | Points | What earns full credit |
|---|---|---|
| Bundle lives at `uiBundles/<appName>/` | 3 | Correct path, name matches metadata |
| `<appName>.uibundle-meta.xml` present and valid | 3 | `<isActive>`, `<masterLabel>`, `<target>`, `<version>` all set |
| `ui-bundle.json` present and valid | 3 | Required `outputDir`, matches build emit dir |
| API version managed at project/deploy layer | 2 | `sfdx-project.json` matches target org; no unsupported `apiVersion` in `ui-bundle.json` |
| Two distinct `package.json` files (root + bundle) | 2 | No accidental merge or duplicate dep declarations |
| Path aliases configured in **both** `vite.config.ts` and `tsconfig.json` | 2 | Aliases match between the two |
| External app: `digitalExperiences/sfdc_cms_site/content.json` correct | 3 | `appContainer: true`, valid `appSpace` |
| Build artifacts under `outputDir` count < 2,500 | 2 | Source maps disabled or filtered for production |

## Routing & Hosting (15 points)

| Item | Points | What earns full credit |
|---|---|---|
| SPA fallback set | 4 | `routing.fallback: "index.html"` |
| `trailingSlash` chosen and consistent | 2 | `never` / `always` / `auto` — matches in-app router |
| `target` matches deployment intent | 4 | `AppLauncher` for internal, `Experience` for external; companion metadata present for external |
| Rewrites / redirects (if any) are sane | 2 | Status codes correct; no redirect loops |
| Hard refresh on a deep route works | 3 | Manual smoke-test |

## Data Access (25 points)

| Item | Points | What earns full credit |
|---|---|---|
| Uses `@salesforce/sdk-data` exclusively for Salesforce calls | 5 | No raw `fetch` / `axios` to Salesforce endpoints |
| Optional chaining on SDK methods | 2 | `sdk.graphql?.()`, `sdk.fetch?.()` |
| GraphQL preferred over REST where possible | 3 | UI API GraphQL for record reads/writes |
| `{ value }` field shape respected | 3 | Fields read as `record.X.value` |
| `edges/node` connection pattern handled | 2 | `result.uiapi.query.X.edges?.map(e => e?.node)` |
| `schema.graphql` regenerated from connected org | 2 | `npm run graphql:schema` is committed in workflow |
| Codegen scalar mappings complete | 2 | UIAPI scalars mapped in `codegen.yml` |
| Error strategy chosen per call site | 4 | Strict / Tolerant / Permissive picked deliberately |
| 401 / 403 callbacks wired (Experience apps) | 2 | `on401` / `on403` registered in `createDataSDK` |

## Styling Discipline (10 points)

| Item | Points | What earns full credit |
|---|---|---|
| One styling system per component | 3 | No SLDS + Tailwind mixed inside one component |
| App-shell vs recipe styling boundary respected | 2 | Tailwind / shadcn for shell; SLDS or chosen system for data recipes |
| SLDS imports happen once globally | 1 | Single import in `global.css` (or equivalent) |
| Focus ring color is Salesforce blue if SLDS-feel desired | 1 | `--ring: #0176d3` for shadcn projects targeting native feel |
| `IconSettings` wraps `design-system-react` usage | 1 | Icons resolve correctly |
| Dark-mode tokens defined when supported | 1 | `.dark` overrides in `global.css` |
| No mixed SLDS versions | 1 | Don't combine `design-system-react` and `@salesforce-ux/design-system` |

## ACC Integration (15 points — only scored if ACC is in scope)

| Item | Points | What earns full credit |
|---|---|---|
| Agentforce preference enabled in target org | 2 | Setup confirms |
| Employee Agent with topics + actions exists | 2 | Required to render |
| My Domain cookie policy: first-party requirement OFF | 2 | Setup confirms |
| Trusted Domains for Inline Frames includes prod + dev | 3 | Both, with iFrame type Lightning Out |
| `@salesforce/agentforce-conversation-client` installed | 1 | Pinned in `package.json` |
| Mount uses `useRef` + `useEffect` with cleanup | 3 | `widgetRef.current?.destroy()` in cleanup |
| Display mode chosen deliberately | 2 | Floating / Docked / Inline matches UX intent |

> If ACC is not in scope, redistribute these 15 points: +10 to Data Access, +5 to Project Structure.

## Deployment Readiness (15 points)

| Item | Points | What earns full credit |
|---|---|---|
| `npm run lint` passes | 2 | Clean lint output |
| `npm run build` passes | 3 | Clean build, type-check passes |
| `dist/` size within budget | 2 | Under 2,500 files |
| Deploy via MCP first, CLI as fallback | 2 | Workflow uses `mcp_Salesforce_DX_deploy_metadata` when available |
| External app: all four metadata folders deployed together | 2 | `digitalExperienceConfigs/`, `digitalExperiences/`, `networks/`, `sites/` |
| Permission set assigned to running user | 1 | App is reachable for the test user |
| Sample data plan available if applicable | 1 | `sf data import tree --plan ...` works |
| Smoke-test pass: App Launcher / Digital Experiences | 1 | App appears and renders |
| Smoke-test pass: hard-refresh deep route | 1 | No 404 |

---

## Quick scoring template

```
Project Structure       : __ / 20
Routing & Hosting       : __ / 15
Data Access             : __ / 25
Styling Discipline      : __ / 10
ACC Integration         : __ / 15  (or N/A — redistribute)
Deployment Readiness    : __ / 15
                          --------
Total                   : __ / 100
```

## What disqualifies an app regardless of score

- Raw `fetch` / `axios` to Salesforce endpoints
- Multi-Framework enabled in a non-sandbox/scratch org with production data
- ACC integration without My Domain cookie policy + Trusted Domains both configured
- External app deployed without companion `digitalExperiences` / `networks` / `sites`
- Lightning base components (`lightning-card`, etc.) imported from a React UI bundle (won't work)
- `@wire` decorators inside the React app (not supported)
