# CI/CD and Deploy

Multi-Framework has deploy rules that don't exist for plain LWC. Get these wrong and either the metadata deploy fails or the app deploys but doesn't run.

## The non-negotiable rules

| Rule | Why |
|---|---|
| **Build first, then deploy** | `sf project deploy start` ships whatever is in `outputDir` (`dist/`). No build = empty deploy = blank app. |
| **One UI bundle per metadata push (safe default)** | Multi-bundle deploys can collide; scope to one bundle at a time unless you've validated the combo. |
| **2,500-file ceiling per `UIBundle`** | `dist/` must stay under this. Source maps and vendored binaries bust the limit fast. |
| **`tsc -b && vite build` must pass** | The build script is `tsc -b && vite build` — TypeScript errors block the build, they're not warnings. |
| **`npm run lint` must pass** | ESLint flat config; violations block CI. |
| **Deploy from project root** | `sf project deploy start` resolves `force-app` from the root, not the bundle dir. |

## Standard deploy sequence

```bash
# 1. Build (inside the bundle)
cd force-app/main/default/uiBundles/myApp
npm install
npm run graphql:schema   # first time / when schema drifted
npm run graphql:codegen
npm run build            # → dist/

# 2. Deploy (from project root)
cd -
sf project deploy start \
  --source-dir force-app/main/default/uiBundles/myApp \
  --target-org TARGET_ORG \
  --json
```

If the team uses the **Salesforce DX MCP server** (`mcp_Salesforce_DX_deploy_metadata`), prefer it — same result, structured output.

## The `dist/` 2,500-file budget

You will hit this faster than you think. Common offenders:

| Offender | Fix |
|---|---|
| Per-file source maps (one per chunk) | `build.sourcemap: false` in `vite.config.ts` for prod builds |
| SLDS sprite maps exploded per icon | Keep `@salesforce-ux/design-system` sprite SVGs; don't copy icons into `public/` |
| Vendored Lucide icons as individual files | `lucide-react` is fine as a dependency; don't copy its `dist/` into your `public/` |
| Duplicate font files (ttf/woff/woff2/eot) | Ship woff2 only |
| `node_modules/.cache` leaking into `dist/` | Add `.cache/` to `.gitignore` and `.forceignore` |

Audit before deploy:

```bash
find dist -type f | wc -l
find dist -type f -name "*.map" | wc -l    # source maps
du -sh dist/assets/* | sort -h              # biggest assets
```

### `.forceignore` for React bundles

Deploys from `force-app/` pick up *everything* by default. Add to `.forceignore`:

```
# React build artifacts that shouldn't deploy alongside their source
**/node_modules/
**/coverage/
**/playwright-report/
**/test-results/

# package.xml is SFDX legacy; the CLI generates its own
package.xml

# LWC boilerplate that lands in new DX projects
**/jsconfig.json
**/.eslintrc.json
**/__tests__/**

# macOS
.DS_Store
```

`dist/` itself *must* deploy — it's the bundle payload. Only exclude build caches and test output.

## Scratch org definition for Multi-Framework

The scratch definition needs **`UIBundleSettings.webAppOptIn: true`** and `en_US`:

```json
{
  "orgName": "Multi-Framework Dev Org",
  "edition": "developer",
  "language": "en_US",
  "features": ["EnableSetPasswordInApi"],
  "settings": {
    "lightningExperienceSettings": {
      "enableS1DesktopEnabled": true
    },
    "UIBundleSettings": {
      "webAppOptIn": true
    },
    "mobileSettings": {
      "enableS1EncryptedStoragePref2": false
    }
  }
}
```

Without `webAppOptIn`, the scratch org won't have Multi-Framework enabled and metadata deploys fail with feature-not-enabled errors.

### `sfdx-project.json`

```json
{
  "packageDirectories": [
    {
      "path": "force-app",
      "default": true,
      "package": "MyReactApp",
      "versionName": "v1",
      "versionNumber": "1.0.0.NEXT"
    }
  ],
  "name": "my-react-app",
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "66.0"
}
```

`sourceApiVersion` must match the `apiVersion` in `ui-bundle.json`. Mismatches cause "metadata type not found" errors.

## CI/CD reference workflow (GitHub Actions)

The trailheadapps reference repo uses Volta for node pinning, separate caches for root and bundle `node_modules`, coverage upload, and Playwright browser caching. Adapt to any CI system.

```yaml
name: CI
on:
  workflow_dispatch:
  push: { branches: [main], paths-ignore: [README.md, sfdx-project.json] }
  pull_request: { branches: [main] }

jobs:
  react-app:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: force-app/main/default/uiBundles/myApp
    steps:
      - uses: actions/checkout@v4

      - uses: volta-cli/action@v4

      - name: Cache React app node_modules
        id: cache-react-npm
        uses: actions/cache@v4
        with:
          path: force-app/main/default/uiBundles/myApp/node_modules
          key: react-npm-${{ hashFiles('force-app/main/default/uiBundles/myApp/package-lock.json') }}

      - name: Install
        if: steps.cache-react-npm.outputs.cache-hit != 'true'
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Unit tests + coverage
        run: npm run test -- --run --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./force-app/main/default/uiBundles/myApp/coverage/lcov.info

      - name: Build
        run: npm run build

      - name: Cache Playwright browsers
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ hashFiles('**/package-lock.json') }}

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: E2E
        run: npm run test:e2e

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: force-app/main/default/uiBundles/myApp/playwright-report

  deploy-preview:
    needs: react-app
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: volta-cli/action@v4
      - run: npm ci --prefix force-app/main/default/uiBundles/myApp
      - run: npm run build --prefix force-app/main/default/uiBundles/myApp
      - name: Install sf CLI
        run: npm install -g @salesforce/cli
      - name: Install UI bundle plugin
        run: sf plugins install @salesforce/plugin-ui-bundle-dev
      - name: Authenticate
        run: echo "${{ secrets.SFDX_AUTH_URL }}" | sf org login sfdx-url --set-default
      - name: Deploy to sandbox
        run: sf project deploy start --source-dir force-app/main/default/uiBundles/myApp --json
```

### What to cache

| Target | Why |
|---|---|
| Root `node_modules/` | SFDX / Prettier / Husky stuff |
| Bundle `node_modules/` | React app deps — the big one; cache saves 30-60s |
| `~/.cache/ms-playwright` | Browser downloads are ~300 MB; always cache |
| `.vite/` (optional) | Vite build cache across runs |

## PR preview deploys

For PR preview orgs, use scratch orgs with `--duration-days 1`:

```bash
sf org create scratch \
  --definition-file config/project-scratch-def.json \
  --alias pr-${{ github.event.number }} \
  --duration-days 1 \
  --set-default

npm run build --prefix force-app/main/default/uiBundles/myApp
sf project deploy start --source-dir force-app/main/default/uiBundles/myApp
sf org assign permset --name MyAppUser
sf org open
```

## Pre-commit hook

The reference repo uses Husky + lint-staged:

```json
// package.json (root)
{
  "husky": { "hooks": { "pre-commit": "lint-staged" } },
  "lint-staged": {
    "force-app/main/default/uiBundles/myApp/**/*.{ts,tsx}": [
      "npm run lint --prefix force-app/main/default/uiBundles/myApp --",
      "prettier --write"
    ]
  }
}
```

## Deploy failure diagnostics

| Error | Cause | Fix |
|---|---|---|
| `UIBundle: The file count ... exceeds the maximum` | >2,500 files in `dist/` | Prune source maps, sprite copies, fonts |
| `Component type 'UIBundle' not found` | API version mismatch | Align `sourceApiVersion` (sfdx-project.json) and `apiVersion` (ui-bundle.json) and org version |
| `Metadata API response: Required field 'masterLabel' missing` | `.uibundle-meta.xml` missing fields | Ensure `<masterLabel>`, `<isActive>`, `<version>` |
| `Insufficient access rights on cross-reference id` | Running user lacks permset to deploy UIBundle | Grant the deploy user `ModifyAllData` or the right system permission |
| Deploy succeeds but app never appears | Wrong `target` in `.uibundle-meta.xml`; or Experience site missing `appContainer: true` | Confirm `AppLauncher` vs `Experience` and `digitalExperiences/.../content.json` |
| `sf template generate ui-bundle` not recognized | Plugin missing | `sf plugins install @salesforce/plugin-ui-bundle-dev` |
| `UIBundleSettings` feature not enabled on scratch org | `webAppOptIn` not set | Add `"UIBundleSettings": { "webAppOptIn": true }` to scratch def |

## Multi-bundle repos

If you deploy more than one UI bundle from the same project:

- Deploy them in separate `sf project deploy start` calls
- Build each one in its own bundle directory
- Keep bundle names unique across the org (they're first-class metadata records)
- Share code via a **private npm package** or workspace, not by importing across `uiBundles/`

Cross-bundle imports break in the built output even if they compile in dev — the plugin scopes each bundle.
