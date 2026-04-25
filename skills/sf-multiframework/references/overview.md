# Overview — Salesforce Multi-Framework (Beta)

> **Sources.** Skill built from Salesforce developer documentation (see [official-sources.md](official-sources.md)) and code patterns from [trailheadapps/multiframework-recipes](https://github.com/trailheadapps/multiframework-recipes). Skill framework adapted from **Jag Valaiyapathy's SF Skills repo** (same rubric, format, and governance conventions used across `sf-*` skills).

## What it is

Salesforce Multi-Framework lets you build apps in non-Lightning UI frameworks — currently **React** — that run on the **Agentforce 360 Platform**. Apps are packaged and deployed as a `UIBundle` metadata type and hosted by the platform alongside CMS content with versioning and publication lifecycle management.

When deployed, a `UIBundle` record:

- declares the app's identity on the platform
- declares which containers can host it (App Launcher, Experience Cloud)
- pulls runtime assets, images, and metadata from Salesforce CMS storage

A single `UIBundle` can contain up to **2,500 files**.

## Why it exists

Two audiences benefit:

| Audience | Benefit |
|---|---|
| React developers | Reach Salesforce data and authentication without learning the LWC framework |
| Salesforce developers | Use modern bundlers (Vite), npm packages, and rich UI libraries inside the platform |

The feature is positioned for **self-contained SPAs and highly customized experiences** that use Salesforce as the host and data source — *not* as a replacement for LWC for tightly-integrated platform components.

## How it ships

| Element | Location | Purpose |
|---|---|---|
| `UIBundle` metadata | `force-app/main/default/uiBundles/<app>/` | App identity & container declaration |
| `<app>.uibundle-meta.xml` | bundle root | Metadata definition (target, isActive, version) |
| `ui-bundle.json` | bundle root | Runtime configuration (output dir, routing, API version) |
| App source | `src/`, `package.json`, etc. | The React app itself |
| Build output | `dist/` (Vite default) | What actually gets served at runtime |

## What targets are supported

The `<target>` element in `.uibundle-meta.xml` accepts:

| Target | Effect | Use case |
|---|---|---|
| `AppLauncher` (default) | App appears in the App Launcher for authenticated users | Internal employee apps (B2E) |
| `Experience` | App is served by an Experience Cloud site | External B2B / B2C portals |

## What you can use inside the React app

| Allowed | Not allowed |
|---|---|
| Standard web APIs (`fetch` to *non-Salesforce* endpoints, `URL`, etc.) | `lightning/*` modules, Lightning base components |
| Any npm package | `@wire` decorators |
| `@salesforce/sdk-data` (Data SDK) | Most other `@salesforce/*` scoped modules |
| `@salesforce/agentforce-conversation-client` (ACC) | Direct `axios` / `fetch` to Salesforce endpoints |
| `@salesforce/ui-bundle` helpers | |
| `@salesforce/vite-plugin-ui-bundle` (dev only) | |

## Beta limitations

- **Sandbox and scratch orgs only** — no DE orgs, no Trailhead Playgrounds.
- **Default language must be `en_US`** — known issue with non-English orgs.
- **Once enabled, cannot be disabled** in an org.
- **One UI bundle per metadata push** is the safe pattern; multi-app deploys can collide.
- **No Experience Builder editing** for sites attached to React apps.
- **Currently React only** — additional frameworks planned over time.

## Related platform features

| Feature | Relationship |
|---|---|
| **Agentforce Vibes** | AI-assisted authoring inside VS Code; uses skills + rules to scaffold and edit React apps + GraphQL |
| **Agentforce Conversation Client (ACC)** | Lightning Out 2.0 LWCI you can embed inside the React app for chat with Employee Agents |
| **Salesforce CMS** | Storage layer for runtime assets and content used inside React apps |
| **Data 360 / Hybrid Search** | Powers the `search_electronic_media` ACC tool when configured |

## Decision trees

### "Should I use React (Multi-Framework) or LWC?"

Pick LWC when:
- You're building reusable platform components, especially for Lightning Experience or Salesforce mobile.
- You need automatic SLDS, Lightning Data Service, or `@wire` integrations.
- The component will be embedded in record pages, list views, or App Builder.

Pick React when:
- You're building a self-contained SPA or a custom-branded portal.
- You need a specific React library (charting, mapping, code editor, etc.).
- You want a non-Salesforce UI aesthetic (Tailwind, custom design system).

See [lwc-vs-react.md](lwc-vs-react.md) for a structured comparison.

### "Internal or external app?"

Pick `AppLauncher` (internal) when:
- Users are employees authenticated via Salesforce.
- The app appears alongside other Lightning apps in the App Launcher.
- You want the simplest deployment path.

Pick `Experience` (external) when:
- Users are partners or customers (B2B / B2C).
- You need a public-facing URL via an Experience Cloud site.
- You're prepared to maintain `digitalExperienceConfigs`, `digitalExperiences`, `networks`, and `sites` metadata alongside the bundle.

## Workflow at a glance

```
Setup org (one-time)
  ├─ Enable Multi-Framework (Beta)
  ├─ Configure My Domain / Trusted Domains (if using ACC)
  └─ Authorize org via sf CLI

Scaffold project
  └─ sf template generate ui-bundle --template reactinternalapp|reactexternalapp

Develop locally
  ├─ npm install
  ├─ npm run graphql:schema   (introspect org)
  ├─ npm run graphql:codegen  (generate types)
  └─ npm run dev              (Vite + @salesforce/vite-plugin-ui-bundle)

Build & deploy
  ├─ npm run build            (→ dist/)
  └─ sf project deploy start --source-dir <bundle>

Verify
  └─ App Launcher / Digital Experiences / hard-refresh deep links
```
