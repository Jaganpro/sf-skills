# React (Multi-Framework) vs LWC

Multi-Framework **broadens developer choice**; it does not replace LWC. They serve different purposes. Use this guide to decide which framework fits a given task on the Salesforce Platform.

## TL;DR decision tree

```
Will this be embedded inside Lightning Experience, an Experience Builder site,
or the Salesforce mobile app as a reusable component?
  ├─ yes → LWC
  └─ no
      Is this a self-contained SPA or a custom-branded portal?
      ├─ yes → React (Multi-Framework)
      └─ no
          Do you need a specific React library (charting, mapping, code editor, etc.)?
          ├─ yes → React
          └─ no  → LWC (default for platform integration)
```

## Side-by-side

| Concern | LWC | React (Multi-Framework Beta) |
|---|---|---|
| **Integration with the platform** | Deep & native — automatic data binding, Lightning Data Service, Apex, page editor placement | Hosted on the platform, but app-shaped — UI Bundle is one atomic unit |
| **Performance inside Salesforce UI** | Optimized for the platform; usually best inside Lightning Experience | High performance for complex UIs; depends on API design and data fetching |
| **Security & governance** | Platform-enforced; CRUD/FLS, Locker/Lightning Web Security, secure component model | App-level — you own security best practices and secure API calls |
| **Component reuse across orgs/contexts** | Excellent at component-level reuse inside Salesforce | Component reuse is great inside the React app; Micro-Frontend support for cross-context is Developer Preview |
| **Learning curve** | Low for modern JS/HTML developers; standards-based | Low–moderate, depending on familiarity with React + ecosystem |
| **Ecosystem** | Lightning base components, `@wire`, lwc-recipes | All of npm; React 19; Vite; React Router 7; shadcn; etc. |
| **Styling** | Auto-applied SLDS via base components | SLDS blueprints, `design-system-react`, or Tailwind/shadcn — you choose |
| **Data access** | LDS, `@wire`, Apex `@AuraEnabled` | `@salesforce/sdk-data` (GraphQL UI API + `fetch` allow-list) |
| **Build / deploy** | First-class metadata, `sf project deploy` | UIBundle metadata; build artifacts in `dist/` ship with the bundle |
| **Available surfaces** | Lightning Experience, Experience Cloud (LWR + Aura), Mobile app, Page templates, Flow Screens, App Builder | App Launcher (`AppLauncher`) or Experience Cloud site (`Experience`) |
| **Embedding inside another framework** | Native | Hosted alone (cross-framework via Micro-Frontends Developer Preview) |
| **Languages** | Standard JS/TS, HTML templates | TypeScript / JSX |
| **Dark mode / theming** | Built-in via SLDS 2 tokens | DIY via Tailwind tokens or SLDS 2 |
| **Org enablement** | GA, no toggle | Beta toggle in sandbox/scratch only; **cannot be disabled** once enabled |

## Pick LWC when…

- You're building a **reusable component** that will be placed in record pages, list views, app pages, or App Builder.
- You need automatic SLDS, automatic accessibility from base components, and the latest design system updates.
- You want first-class platform integrations: `@wire`, `lightning/uiRecordApi`, Apex `@AuraEnabled`, `lightning/navigation`.
- You're building for **Salesforce mobile** with native rendering.
- You want platform-managed security policies (Locker / LWS) without writing them yourself.
- The unit of work is a **component**, not an **app**.

## Pick React when…

- You're building a **self-contained SPA** that uses Salesforce as a host and data source.
- You want a **custom-branded portal** (B2B / B2C) with specific UX requirements that don't fit Lightning conventions.
- You want a specific React library (data grid, charts, code editor, video player, etc.).
- Your team already has deep React expertise and you want to minimize ramp-up.
- The unit of work is an **app**, not a component.
- You can accept Beta limitations (sandbox/scratch only, English orgs, can't disable).

## Specific scenarios

| Scenario | Choice | Reason |
|---|---|---|
| Custom record-page tile showing related contacts | **LWC** | Embeds in the record page; needs `@wire` and Lightning navigation |
| Customer self-service portal with login, profile, support cases | **React** (`Experience` target) | Self-contained SPA with custom branding |
| Internal sales productivity app with charts and complex tables | **React** (`AppLauncher` target) | Use a charting library + custom layout |
| Form embedded in a Flow screen | **LWC** | Flow screens take LWCs natively, not React |
| Mobile-first field service interface | **LWC** | Salesforce Mobile App native rendering |
| Custom dashboard with shadcn UI + Tailwind | **React** | Design system fits poorly inside SLDS |
| Embedding an Agentforce chat in a custom UI | **Either** — both can host ACC | Pick based on the rest of the surface |

## Frequently confused points

### "Can I use both in the same org?"
Yes. They coexist. A React app can sit alongside LWC apps and components. They don't share state or styling automatically — treat them as independent surfaces.

### "Can I embed an LWC inside a React app?"
Not directly today. Cross-framework embedding is Developer Preview via the Micro-Frontends path. The supported pattern is to **embed an LWCI** (like ACC) inside a React app, not arbitrary LWCs.

### "Can I embed a React app inside an LWC?"
Not in the supported way. The opposite direction (LWCI inside React) is the supported flow.

### "Will React replace LWC?"
No. Salesforce positions LWC as the primary framework for platform-integrated components and React (and future frameworks) for **self-contained SPAs and custom experiences**.

### "Is the Beta production-ready?"
Beta. Sandbox/scratch only, English-only, can't be disabled. Plan production rollout against GA timelines.

## Migration thinking

You generally shouldn't **migrate** from LWC to React for a working component. The cost rarely pays back. Use React for **new apps** where its strengths apply. Keep LWC for component-shaped surfaces in the platform UI.

If you're thinking about migrating because LWC is "limiting", first check whether the limitation is real: many "I need React for this" cases are solvable with LWC + a well-chosen npm dep (chart libraries, date pickers, etc.) loaded via Lightning Web Security.

## See also

- [overview.md](overview.md) — what Multi-Framework is and isn't
- [setup.md](setup.md) — Beta org configuration
- Official: [React vs LWC (Beta)](https://developer.salesforce.com/docs/platform/code-builder/guide/reactdev-lwc-diff.html)
