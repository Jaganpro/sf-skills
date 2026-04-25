# Project Structure

A Multi-Framework app is a **self-contained unit** under `force-app/main/default/uiBundles/<appName>/` containing both metadata and source. Application metadata and content live together — there is no separation between "Salesforce metadata" and "frontend source" the way there is for LWC.

## Canonical layout

```
multiframework-recipes/
  sfdx-project.json                 # Salesforce DX config (apiVersion v66.0)
  package.json                      # ROOT — SFDX metadata scripts only, NOT the React app
  data/                             # sf data import tree plans
  config/project-scratch-def.json   # MUST set "language": "en_US"
  force-app/main/default/
    uiBundles/
      myApp/                        # ← the entire React app + metadata
        myApp.uibundle-meta.xml     # UIBundle metadata definition
        ui-bundle.json              # Runtime configuration (routing, output dir)
        package.json                # React app dependencies (separate from root)
        vite.config.ts              # Vite + @salesforce/vite-plugin-ui-bundle
        tsconfig.json
        codegen.yml                 # GraphQL codegen config
        schema.graphql              # Generated from connected org (gitignored)
        scripts/
          get-graphql-schema.mjs    # Introspection helper
        src/
          app.tsx                   # Router + providers
          appLayout.tsx             # Shell (Navbar + <Outlet />)
          routes.tsx                # Route definitions
          api/
            graphqlClient.ts        # executeGraphQL wrapper
            graphql-operations-types.ts  # Generated types
            utils/
              query/                # .graphql read queries
              mutation/             # .graphql write mutations
          components/
            app/                    # Navbar, Layout, CodeBlock
            recipe/                 # Shared recipe UI (Skeleton, ContactTile)
            ui/                     # shadcn/ui primitives
          pages/                    # Route pages
          recipes/                  # Recipe components by category
          lib/                      # cn(), utilities
          styles/
            global.css              # Tailwind + design tokens
            slds.css                # SLDS imports
          assets/                   # Icons, images
        dist/                       # ← BUILD OUTPUT — what gets deployed
```

> Two `package.json` files are intentional. The root one is for SFDX scripts. The bundle one is for the React app. **Do not merge them.**

## Required files at the bundle root

### `<appName>.uibundle-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<UIBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <isActive>true</isActive>
    <masterLabel>My App</masterLabel>
    <target>AppLauncher</target>
    <version>1.0.0</version>
</UIBundle>
```

| Element | Notes |
|---|---|
| `isActive` | Set `true` to make the app available |
| `masterLabel` | User-facing label |
| `target` | `AppLauncher` (default) or `Experience` |
| `version` | App version string |

> External apps must use `<target>Experience</target>` and ship matching `digitalExperiences/`, `networks/`, and `sites/` metadata. See [templates.md](templates.md).

### `ui-bundle.json`

Runtime configuration consumed by the platform when serving the app.

```json
{
  "outputDir": "dist",
  "apiVersion": "v66.0",
  "routing": {
    "fileBasedRouting": true,
    "trailingSlash": "never",
    "fallback": "index.html",
    "rewrites": [
      { "route": "/api/*", "target": "/api/index.html" }
    ],
    "redirects": [
      { "route": "/old", "target": "/new", "statusCode": "301" }
    ]
  }
}
```

#### Property reference

| Property | Type | Required | Notes |
|---|---|---|---|
| `outputDir` | string | yes | Path relative to bundle root containing build artifacts. Vite default is `dist`. |
| `apiVersion` | string | recommended | Format `vXX.X`. Match the deploy target. Defaults to current org version. |
| `routing.fileBasedRouting` | boolean | no | When `true`, URLs map to folder structure inside `outputDir`. Default `true`. |
| `routing.trailingSlash` | enum | no | `never` removes (`/page/` → `/page`); `always` adds; `auto` no change. |
| `routing.fallback` | string | **yes for SPAs** | File served when nothing matches. Set `index.html` for client-side routing. |
| `routing.rewrites` | array | no | Internal rewrite rules — change file served without changing URL. Supports `:id` and `*`. |
| `routing.redirects` | array | no | HTTP redirects with status `301` / `302` / `307` / `308`. Evaluated in order. |
| `routing.rewrites.route` / `.target` | string | yes | Source pattern → internal file path |
| `routing.redirects.route` / `.target` / `.statusCode` | string | yes | Source pattern → destination URL → HTTP status |

#### SPA-minimal `ui-bundle.json`

```json
{
  "outputDir": "dist",
  "apiVersion": "v66.0",
  "routing": {
    "fallback": "index.html",
    "trailingSlash": "never"
  }
}
```

### `package.json` (bundle)

The bundle's `package.json` declares React app dependencies and scripts. Typical scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "graphql:schema": "node scripts/get-graphql-schema.mjs",
    "graphql:codegen": "graphql-codegen --config codegen.yml"
  }
}
```

Recommended Vite plugins for any non-template-scaffolded project:

- `@salesforce/vite-plugin-ui-bundle` — wires Vite dev server to the org for live data
- `@salesforce/ui-bundle` — helper functions (auth, base path) for working with the Data SDK

## File-count budget

A `UIBundle` can hold up to **2,500 files**. Source maps in `dist/` and large public asset folders are the usual culprits when you hit the ceiling. Configure Vite to emit fewer source maps in production if needed:

```ts
// vite.config.ts
build: {
  sourcemap: false   // or 'hidden' to keep them but not reference in output
}
```

## Path aliases (recommended)

Define matching aliases in **both** `vite.config.ts` and `tsconfig.json` to keep imports tidy:

```ts
// vite.config.ts
resolve: {
  alias: {
    "@": "/src",
    "@api": "/src/api",
    "@components": "/src/components",
    "@utils": "/src/utils",
    "@styles": "/src/styles",
    "@assets": "/src/assets"
  }
}
```

```json
// tsconfig.json (compilerOptions)
"baseUrl": ".",
"paths": {
  "@/*":          ["src/*"],
  "@api/*":       ["src/api/*"],
  "@components/*":["src/components/*"],
  "@utils/*":     ["src/utils/*"],
  "@styles/*":    ["src/styles/*"],
  "@assets/*":    ["src/assets/*"]
}
```

## Why the bundle is self-contained

The platform treats `uiBundles/<appName>/` as one atomic unit. Deploys ship the metadata + the contents of `outputDir` together. Sharing source between bundles is **not** supported — you can't import from a sibling bundle. Use npm packages for genuine code sharing.
