---
name: sf-react
description: "React on the Salesforce Multi-Framework runtime (Headless 360 / Agentforce 360 Platform). TRIGGER when: user creates or edits Multi-Framework UI bundles, touches a uiBundles/ directory, edits ui-bundle.json, .uibundle-meta.xml, .tsx files inside force-app/, or a package.json with @salesforce/sdk-data or @salesforce/vite-plugin-ui-bundle, or asks about 'React on Salesforce', 'Multi-Framework', 'Headless 360 React', 'Agentforce React app', or trailheadapps/multiframework-recipes patterns. DO NOT TRIGGER when: generic React work outside Salesforce (Next.js, plain Vite, Create-React-App with no platform context), Aura, Visualforce, or Lightning Web Components — for LWC use sf-lwc instead."
license: MIT
metadata:
  version: "0.1.0"
  author: "weytani"
  scoring: "44 recipes across 8 categories — Multi-Framework open beta, sourceApiVersion 66.0"
---

# sf-react: React on Salesforce (Multi-Framework / Headless 360)

## ⚠ WARNING: Stale GraphQL Codegen Silently Breaks Production

Multi-Framework projects generate `schema.graphql` from the connected org and **deliberately do not commit it**. If `npm run graphql:schema` is skipped before `npm run build`, the build passes, lint passes, no warnings appear — but `graphql-operations-types.ts` is stale or missing, and field access against UIAPI's `{ value }` shape silently fails at runtime in production.

**ALWAYS** run `npm run graphql:schema` before any `npm run build` in a Multi-Framework project. The bundled `scripts/check_codegen_freshness.py` validates this — run it before deploy. See `references/footguns.md` for the full failure-mode breakdown.

---

## When This Skill Owns the Task

Scope: any work touching the Multi-Framework runtime — see "Variant Detection" below for the exact markers.

Multi-Framework launched at **TDX 2026 (April 15, 2026)** as part of Headless 360 / the Agentforce 360 Platform, and it post-dates the model's training cutoff. It introduces three platform primitives that did not previously exist: **`@salesforce/sdk-data`** (UIAPI GraphQL data layer with `{ value }` field shape and Relay connections), **`@salesforce/vite-plugin-ui-bundle`** (Salesforce-aware Vite plugin emitting `uiBundles/` + `.uibundle-meta.xml`), and **GraphQL codegen against UIAPI** (`schema.graphql` introspected live from the org, never committed). It is currently in **open beta**: scratch orgs and sandboxes only (no production), `en_US` default language only, and **Node.js v22+** required (v18 and v20 are unsupported). It has replaced — not supplemented — the older React-on-Salesforce blueprints (Visualforce-embedded React, bearer-token REST against `/services/data`, `lightning-react-app`) for greenfield work.

---

## Variant Detection — Confirm It's Multi-Framework First

Before writing any code, detect the variant. **If you see any of these markers**, you are in a Multi-Framework project:

- `force-app/main/<package>/uiBundles/` directory (note: `uiBundles`, not `lwc`)
- `ui-bundle.json` in the React app root (routing config: `outputDir`, `trailingSlash`, SPA fallback)
- `.uibundle-meta.xml` metadata files
- `package.json` deps include `@salesforce/sdk-data` or `@salesforce/vite-plugin-ui-bundle`
- `sfdx-project.json` with `"sourceApiVersion": "66.0"` (Spring '26) or later
- `codegen.yml` for GraphQL code generation
- `vite.config.ts` referencing the Salesforce plugin (NOT Webpack, NOT Create-React-App)
- Volta config pinning **Node.js v22+** (Multi-Framework requires v22; v18 and v20 are unsupported)

If **none** of these markers are present, this is not a Multi-Framework project — stop and route the user elsewhere (see "Not Covered" below).

---

## Knowledge / Capability Boundary

This skill **owns** as static reference:

- The 44-recipe routing table — which recipe fits which task (`references/recipes-routing.md`)
- UIAPI GraphQL shape: `{ value }` wrapping, Relay `edges → node` connections, `pageInfo` cursors
- Salesforce scalar mappings for `codegen.yml` (Currency, Picklist, Date, DateTime, EncryptedString, IdOrRef)
- Mutation input shapes (`RecordCreateInput`, `RecordUpdateInput`, `RecordDeleteInput`)
- The three coexisting styling systems (SLDS / shadcn-ui / `design-system-react`) and when to pick which
- `ui-bundle.json` schema and `.uibundle-meta.xml` shape
- Beta restrictions (English-default orgs only, scratch + sandbox only, no production)
- Authentication context (B2E only in beta; no client-side auth)

This skill **does not own** — defer to live tools:

- `sf project deploy start` — deployment (route to `sf-deploy`)
- `sf org create scratch` / `sf org login web` — org setup (defer to CLI)
- `npm run graphql:schema` — live org introspection (defer to CLI)
- `npm run graphql:codegen` — code generation against schema (defer to CLI)
- `npm run build` / `npm run lint` / `npm run test` / `npm run test:e2e` — build and test execution
- Apex backend logic — route to `sf-apex`
- LWC work — route to `sf-lwc`

---

## Footguns — Beta Platform, Sharp Edges

### 1. Stale codegen against uncommitted schema (the WARNING above)
**NEVER** assume types are fresh just because the build passed. **ALWAYS** run `scripts/check_codegen_freshness.py` before deploy.

### 2. Non-English org → silent UI break
Multi-Framework only works in orgs with `"language": "en_US"` as default. Other languages produce no runtime error — the UI simply fails to load. **ALWAYS** verify scratch org definitions include `"language": "en_US"`.

### 3. No automatic cache invalidation after mutations
LWC's `updateRecord()` notifies `@wire` adapters automatically; React has no equivalent. After a mutation you **MUST** manually patch local state — easy to forget when coming from LWC, and it leaves stale UI in the user's face. See the `Modify Data` recipes in `references/recipes-routing.md`.

### 4. Extracting GraphQL queries to `src/api/` utilities (in recipes)
The recipes repo's `AGENT.md` explicitly forbids this for recipe code — every recipe inlines its query/mutation so readers see the pattern. **NEVER** suggest DRY-extracting queries into shared utilities when authoring or modifying recipes. App code can extract; recipe code cannot.

### 5. Mixing styling systems in one component
SLDS, shadcn/ui, and `design-system-react` coexist in the same codebase. **NEVER** mix two systems in a single component. Pick one per component and document the choice. ESLint will not catch this.

### 6. Production deploy attempts
Multi-Framework is open beta. **NEVER** attempt `sf project deploy start --target-org <production>`. Redirect to scratch or sandbox.

---

## Routing — Which Recipe for Which Task

The official `trailheadapps/multiframework-recipes` repo ships **44 recipes across 8 categories**. The full table lives in `references/recipes-routing.md`. Quick router:

| If the user wants to... | Read recipe(s) | Category |
|---|---|---|
| Render a basic React component on the platform | `HelloWorld`, `BindingAccountName` | Hello (8) |
| Read a single record from UIAPI | `SingleRecord` | Read Data |
| List, filter, sort, paginate records | `ListOfRecords`, `FilteredList`, `SortedResults`, `PaginatedList` | Read Data |
| Traverse parent → child relationships | `RelatedRecords` | Read Data |
| Refetch data imperatively (button click) | `ImperativeRefetch` | Read Data |
| Create / update / delete records | `CreateRecord`, `UpdateRecord`, `DeleteRecord` | Modify Data |
| Handle GraphQL errors gracefully | `GraphqlErrors`, `LoadingErrorEmpty`, `ErrorBoundaryRecipe` | Error Handling |
| Get current user / session context | `DisplayCurrentUser` | SF APIs |
| Call REST UIAPI directly | `UiApiRest` | SF APIs |
| Call custom Apex REST | `ApexRest` | SF APIs |
| Add routing (links, params, navigation) | `LinkDemo`, `NavLinkDemo`, `RouteParameters`, `UseNavigate`, `NestedRoutes` | Routing (5) |
| Style a component (pick one system) | `Button*`, `AccountCard*`, `Icons*` | Styling (9) |
| Combine query + filter + UI in one screen | `SearchableAccountList`, `DashboardAliasedQueries` | Integration |

**For training-gap content** — UIAPI `{ value }` shape, Relay connection pattern, scalar mappings, mutation input shapes, `ui-bundle.json` schema — read the relevant `references/` file before writing code. These primitives all post-date the model's training cutoff: they were renamed, replaced, or freshly GA'd as of 2026 (specifically the April 2026 Headless 360 launch). Patterns from earlier React-on-Salesforce integration approaches (e.g., bearer-token REST against `/services/data`, embedding React via Visualforce, or the older `lightning-react-app` blueprint) are deprecated and should not be used.

---

## Verification — How You Know It Worked

Before declaring a Multi-Framework change done, **validate** all of:

1. **Run `scripts/check_codegen_freshness.py <project-root>`** — exits 0 only if `schema.graphql` exists and `graphql-operations-types.ts` is newer than it. Exits non-zero with a remediation hint otherwise.
2. **Run `npm run lint`** — Multi-Framework projects ship a strict ESLint config; passing lint validates recipe-style-guide compliance.
3. **Run `npm run build`** in the React app directory. Treat any of the following TypeScript errors as **stale-codegen detected** (not as a code bug to fix in place) — re-run `npm run graphql:schema && npm run graphql:codegen`, then rebuild:
   - `Property 'value' does not exist on type '...'` — UIAPI `{ value }` shape access against pre-codegen / mismatched types.
   - `Cannot find module './generated/graphql-operations-types'` (or `'@/generated/graphql-operations-types'`, or any path ending in `graphql-operations-types`) — codegen output missing entirely.
   - `Property '<FieldName>' does not exist on type 'Account' | 'Contact' | …` or `Type 'unknown' is not assignable to type '<ScalarName>Value'` — schema drift between the org and the generated types.
4. **Run `npm run test:e2e`** in a scratch org with `"language": "en_US"` — actual UIAPI shape validation.
5. **Confirm beta constraints** — scratch or sandbox target org, English-default language, Node.js v22+.

If any of the above fail, **do not declare the task complete**. Surface the failure to the user with the exact command output.

---

## Not Covered — Out of Scope, Defer Elsewhere

This skill explicitly **does not cover**:

- **Plain React work outside Salesforce** (Next.js, Vite-only, Create-React-App, plain SPAs) — out of scope; the agent's general React knowledge applies.
- **Lightning Web Components** — out of scope; route to `sf-lwc`.
- **Apex controllers, triggers, business logic** — out of scope; route to `sf-apex`.
- **Metadata deployment** — out of scope; route to `sf-deploy`.
- **OmniStudio / FlexCard / DataMapper** — out of scope; route to `sf-omniscript`, `sf-flexcard`, `sf-datamapper`.
- **Production-org deploys** — Multi-Framework is open beta; production is unsupported. Refuse and redirect.
- **Non-English orgs** — beta restriction (`en_US` default only). Refuse and redirect.
- **Aura components, Visualforce** — legacy frameworks; out of scope entirely.

---

## Handoff — What Comes Next

After this skill completes its work, hand off explicitly:

- For deployment → next step is `sf-deploy`
- For Apex backend (controllers powering the React app) → next step is `sf-apex`
- For test execution → user runs `npm test` or `npm run test:e2e` directly (skill defers, does not own test execution)
- For converting an existing LWC into a Multi-Framework React equivalent → stay in `sf-react` (in scope)

If the work crosses into deployment or backend logic, hand off cleanly — do not try to span the boundary.

---

## Output Format

When finishing, report in this order:

1. **Multi-Framework component(s) created or updated**
2. **Recipe(s) referenced** — by name, from `references/recipes-routing.md`
3. **Files changed** — paths
4. **Codegen freshness** — `scripts/check_codegen_freshness.py` exit code and output
5. **Beta-constraint verification** — language, org type, Node version
6. **Next handoff step** — `sf-deploy`, `sf-apex`, or stay-in-skill

Suggested shape:

```text
sf-react work: <summary>
Recipes used: <names>
Files: <paths>
Codegen: fresh (check_codegen_freshness exit 0) | stale (FIX REQUIRED)
Constraints: en_US ✓, scratch/sandbox ✓, Node v22 ✓
Next: <handoff>
```
