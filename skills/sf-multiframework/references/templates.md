# Templates: `reactinternalapp` vs `reactexternalapp`

The `sf template generate ui-bundle` command supports two React templates that pre-wire common patterns. Choose based on your **audience and authentication model**.

## `reactinternalapp` — internal employee apps

**Audience:** employees signing in with Salesforce credentials.
**Target:** `AppLauncher`.
**Includes:**

- Pre-wired Vite + TypeScript + Tailwind + shadcn/ui shell
- Object search using GraphQL UI API
- **Agentforce Conversation Client** integration (assumes ACC org config is complete)
- Recommended folder structure (`recipes/`, `pages/`, `components/`)

When to pick it:
- Single-page employee app inside Salesforce.
- Users are already authenticated.
- You plan to embed an Employee Agent.

```bash
sf template generate ui-bundle --name myEmployeeApp --template reactinternalapp
```

## `reactexternalapp` — external B2B / B2C portals

**Audience:** customers or partners signing in from outside the org.
**Target:** `Experience`.
**Includes:**

- Everything `reactinternalapp` provides, **plus**:
- A pre-wired **Experience Cloud site** with multiple pages
- Authentication entry points
- Object search

To use this template you also need:

- Digital Experiences enabled in the org
- Customer/Partner Community user licenses

```bash
sf template generate ui-bundle --name myPortal --template reactexternalapp

# Or scaffold a brand-new DX project + external app:
sf template generate project --template reactexternalapp
```

### Required companion metadata for external apps

External apps **cannot ship as just a `UIBundle`**. You must also deploy:

```
force-app/main/default/
  digitalExperienceConfigs/         # Workspace settings (label, URL prefix, type)
  digitalExperiences/
    sfdc_cms_site/
      content.json                  # MUST set appContainer + appSpace
  networks/                         # The Experience Cloud site
  sites/                            # Salesforce site config
  uiBundles/myPortal/
```

#### `digitalExperiences/sfdc_cms_site/content.json` — the critical wiring

```json
{
  "appContainer": true,
  "appSpace": "c__myPortal"
}
```

| Property | Rule |
|---|---|
| `appContainer` | **Must be `true`** to flag the site as a React app container |
| `appSpace` | **Must be `<NamespacePrefix>__<DeveloperName>`** — use `c__<DeveloperName>` if the org has no namespace |

> Unlike a standard LWR site, the React app's `digitalExperiences/` folder contains **only** `sfdc_cms_site/`. Do not try to author additional CMS content directories.

> The site **cannot be edited in Experience Builder**. Its only role is to host the React bundle.

## Picking the right target after the fact

Switching `<target>` from `AppLauncher` to `Experience` (or vice versa) is **not a hot swap**. You'll need:

- Going internal → external: add the four metadata folders above and a real Experience Cloud site, then redeploy.
- Going external → internal: remove the dependent site metadata or it will reference a non-existent app target.

Plan the target up front whenever possible.

## Manual setup (no template)

If you're not using a template and writing the bundle by hand, install these helpers:

```bash
npm install --save-dev @salesforce/vite-plugin-ui-bundle
npm install @salesforce/ui-bundle @salesforce/sdk-data
```

Minimum `vite.config.ts`:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { uiBundle } from "@salesforce/vite-plugin-ui-bundle";

export default defineConfig({
  plugins: [react(), uiBundle()],
  build: { outDir: "dist", sourcemap: false }
});
```

Minimum `package.json` scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  }
}
```

Add a starter `ui-bundle.json` (see [project-structure.md](project-structure.md)) and `<app>.uibundle-meta.xml`, and you have a deployable bundle.
