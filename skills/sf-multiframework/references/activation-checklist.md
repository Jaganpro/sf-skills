# Activation Checklist

Run through this list before authoring or fixing a Multi-Framework app. Each item maps to a common failure mode.

## Org & Environment

- [ ] Org is **Sandbox** or **Scratch** (DE / Playgrounds unsupported in Beta)
- [ ] Org default language is **`en_US`** (scratch org def explicitly sets `"language": "en_US"`)
- [ ] **Salesforce Multi-Framework (Beta)** enabled in Setup → cannot be disabled later
- [ ] User has **Customize Application** permission to enable the feature
- [ ] **Node.js v22+** installed (`node -v`)
- [ ] **Salesforce CLI** is current (`sf update`)
- [ ] **`@salesforce/plugin-ui-bundle-dev`** installed (`sf plugins`)
- [ ] **Salesforce Extension Pack** installed in VS Code (or equivalent IDE)

## Project Layout

- [ ] App lives at `force-app/main/default/uiBundles/<appName>/` (or matching package dir)
- [ ] `<appName>.uibundle-meta.xml` exists at the bundle root
- [ ] `ui-bundle.json` exists at the bundle root
- [ ] `outputDir` in `ui-bundle.json` matches what the build emits (Vite default: `dist`)
- [ ] `apiVersion` matches the target org (e.g. `"v66.0"`)
- [ ] For SPAs: `routing.fallback: "index.html"` is set
- [ ] `package.json` inside the bundle (separate from the project root `package.json`)

## External Apps Only (`target: Experience`)

- [ ] **Digital Experiences** is enabled in Setup
- [ ] At least one site exists (placeholder is fine — no template needed)
- [ ] Customer/Partner Community user licenses available
- [ ] `digitalExperienceConfigs/` deployed
- [ ] `digitalExperiences/sfdc_cms_site/` deployed with `content.json` having:
  - `appContainer: true`
  - `appSpace: "<NamespacePrefix>__<DeveloperName>"` (or `c__<DeveloperName>` if no namespace)
- [ ] `networks/` and `sites/` deployed
- [ ] You **don't** try to edit the React app site in Experience Builder (not supported)

## Agentforce Conversation Client (only if embedding ACC)

- [ ] An **Employee Agent** with topics + actions exists in the org
- [ ] Setup → Einstein → Agentforce Studio → **Agentforce preference** is enabled
- [ ] Setup → My Domain → **"Require first-party use of Salesforce cookies"** is **unchecked**
- [ ] Setup → Session Settings → **Trusted Domains for Inline Frames** includes the host origin (prod, preview, and `http://localhost:<port>` for dev), iFrame type **Lightning Out**
- [ ] `npm install @salesforce/agentforce-conversation-client` completed
- [ ] Mount lifecycle uses `useRef` + `useEffect` and unmount cleanup

## Data SDK & GraphQL

- [ ] All Salesforce calls go through `@salesforce/sdk-data` (`createDataSDK`, `gql`)
- [ ] **No raw `fetch()` or `axios`** to Salesforce endpoints
- [ ] `schema.graphql` generated from a connected org (`npm run graphql:schema`)
- [ ] `src/api/graphql-operations-types.ts` regenerated after every `.graphql` edit (`npm run graphql:codegen`)
- [ ] Optional chaining used: `sdk.graphql?.()`, `sdk.fetch?.()`
- [ ] Field reads use `{ value }` shape: `record.Name.value`
- [ ] Connection reads use `edges/node` pattern: `result.uiapi.query.X.edges?.map(e => e?.node)`
- [ ] Error strategy chosen per call site: Strict / Tolerant / Permissive
- [ ] 401 / 403 callbacks wired (`on401`, `on403`) where auth flows are user-initiated

## Styling

- [ ] One styling system per component (no SLDS + Tailwind inside the same JSX)
- [ ] SLDS-styled components either use the official blueprint classes or `@salesforce/design-system-react`, not both
- [ ] Focus ring color uses Salesforce blue `#0176d3` if you want native-feeling focus
- [ ] Dark mode handled via `.dark` token overrides in `global.css` (when using Tailwind/shadcn)

## Build & Deploy

- [ ] `npm run lint` passes
- [ ] `npm run build` passes (this is the artifact that ships)
- [ ] `dist/` size is sane and < 2,500 files (UIBundle ceiling)
- [ ] Deploy via `sf project deploy start --source-dir force-app/main/default/uiBundles/<appName>` (or MCP equivalent)
- [ ] Smoke-test: open the app in App Launcher (internal) or Digital Experiences (external)
- [ ] Smoke-test: hard-refresh on a deep route — should not 404

## Anti-Patterns (block before they ship)

- [ ] **No** Lightning base components (`lightning-card`, `lightning-button`) — not supported in React UI bundles
- [ ] **No** `@wire` decorators
- [ ] **No** `@salesforce/*` imports other than `sdk-data`, ACC, or `@salesforce/ui-bundle`
- [ ] **No** raw `fetch()` to `/services/data/...`
- [ ] **No** debug code (`console.log` of SDK objects, response dumps) in committed recipes
