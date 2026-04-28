# Permissions, Trusted Sites, and Resource Loading

Two separate gates control what a UIBundle app can do in an org:

1. **Permission sets** — who can run the app and what Salesforce data they can access
2. **CSP Trusted Sites** — which *external* URLs the browser is allowed to load (images, fonts, analytics, Lightning Out hosts for ACC)

Both fail silently in different ways. Plan them upfront.

## Permission sets for UI bundles

At minimum your end users need:

| Permission | Who needs it | Why |
|---|---|---|
| Object-level read/edit on data the app queries | every user | GraphQL queries enforce org FLS/CRUD |
| Field-level read/edit for every field in GraphQL queries | every user | Missing FLS returns `null` in UI API, not an error |
| `ViewSetup` (if app deep-links into Setup) | admins only | Rare |
| System permission to view the bundle itself (if restricted) | every user | Default is usually public within the org |
| For **ACC**: `Agentforce` permission + the agent's `<agentAccesses>` | every user using chat | Without `<agentAccesses>` in a permission set, the agent is invisible |

See [`sf-permissions`](../../sf-permissions/SKILL.md) for permission-set design, `<agentAccesses>` grants, and audit patterns.

### Starter permission set (`force-app/main/default/permissionsets/myApp.permissionset-meta.xml`)

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My React App User</label>
    <hasActivationRequired>false</hasActivationRequired>

    <!-- Object + field access for everything the React app queries -->
    <objectPermissions>
        <allowRead>true</allowRead>
        <allowCreate>true</allowCreate>
        <allowEdit>true</allowEdit>
        <object>Account</object>
    </objectPermissions>

    <fieldPermissions>
        <field>Account.Industry</field>
        <readable>true</readable>
        <editable>true</editable>
    </fieldPermissions>

    <!-- If the app has its own tab entry in App Launcher -->
    <tabSettings>
        <tab>MyReactApp</tab>
        <visibility>Visible</visibility>
    </tabSettings>
</PermissionSet>
```

### Assign at scratch-org setup

```bash
sf org create scratch --definition-file config/project-scratch-def.json --alias devorg --set-default
sf project deploy start --source-dir force-app
sf org assign permset --name myApp
```

### Silent FLS failures

UI API GraphQL does not throw on missing field access — it returns `null` in the `{ value }` wrapper. If a field is suddenly blank in production but works in dev, check FLS first. Symptom:

```js
account.Phone.value  // → null   (field not readable for this user)
account.Phone        // → { value: null }   (field readable, value is empty)
```

Same wire-level shape, different cause. Add FLS before blaming the query.

## CSP Trusted Sites

Salesforce's Content Security Policy blocks *all* cross-origin requests from the host frame by default. Every non-Salesforce URL — image CDNs, analytics, fonts from Google Fonts, Lightning Out hosts, etc. — needs a `CspTrustedSite` metadata record.

### When you need one

| Loading… | Needs `CspTrustedSite`? |
|---|---|
| Images from an S3 bucket | yes (`isApplicableToImgSrc`) |
| Google Fonts stylesheets | yes (`isApplicableToStyleSrc` + `isApplicableToFontSrc`) |
| Analytics script (Segment, Amplitude, Plausible) | yes (`isApplicableToScriptSrc` + `isApplicableToConnectSrc`) |
| Third-party API via `fetch()` from the React app | yes (`isApplicableToConnectSrc`) — **but prefer a Named Credential + Apex REST** |
| Embedded iframe (e.g. external auth) | yes (`isApplicableToFrameSrc`) — ACC is a special case: see below |

### Metadata example

```xml
<!-- force-app/main/default/cspTrustedSites/AmazonS3Media.cspTrustedSite-meta.xml -->
<?xml version="1.0" encoding="UTF-8" ?>
<CspTrustedSite xmlns="http://soap.sforce.com/2006/04/metadata">
    <context>All</context>
    <description>App media hosted in S3</description>
    <endpointUrl>https://my-bucket.s3.us-west-2.amazonaws.com</endpointUrl>
    <isActive>true</isActive>
    <isApplicableToImgSrc>true</isApplicableToImgSrc>
    <isApplicableToConnectSrc>false</isApplicableToConnectSrc>
    <isApplicableToFontSrc>false</isApplicableToFontSrc>
    <isApplicableToFrameSrc>false</isApplicableToFrameSrc>
    <isApplicableToMediaSrc>false</isApplicableToMediaSrc>
    <isApplicableToStyleSrc>false</isApplicableToStyleSrc>
    <canAccessCamera>false</canAccessCamera>
    <canAccessMicrophone>false</canAccessMicrophone>
</CspTrustedSite>
```

Each `isApplicableTo*` flag maps to a CSP directive:

| Flag | Browser directive | Example resource |
|---|---|---|
| `isApplicableToImgSrc` | `img-src` | `<img src>`, `background-image: url(...)` |
| `isApplicableToStyleSrc` | `style-src` | `<link rel="stylesheet">` |
| `isApplicableToFontSrc` | `font-src` | `@font-face { src: url(...) }` |
| `isApplicableToScriptSrc` | `script-src` | `<script src>` |
| `isApplicableToConnectSrc` | `connect-src` | `fetch()`, `XMLHttpRequest`, WebSocket |
| `isApplicableToFrameSrc` | `frame-src` | `<iframe src>` |
| `isApplicableToMediaSrc` | `media-src` | `<audio>`, `<video>` |

Only enable the flags you actually need — each widens the attack surface.

### Common combos

**Google Fonts**

```xml
<endpointUrl>https://fonts.googleapis.com</endpointUrl>
<isApplicableToStyleSrc>true</isApplicableToStyleSrc>
```

```xml
<endpointUrl>https://fonts.gstatic.com</endpointUrl>
<isApplicableToFontSrc>true</isApplicableToFontSrc>
```

Two sites because Google splits the CSS from the font files.

**Image CDN**

```xml
<endpointUrl>https://cdn.example.com</endpointUrl>
<isApplicableToImgSrc>true</isApplicableToImgSrc>
```

**Analytics that loads a script + sends data**

```xml
<endpointUrl>https://cdn.segment.com</endpointUrl>
<isApplicableToScriptSrc>true</isApplicableToScriptSrc>
```

```xml
<endpointUrl>https://api.segment.io</endpointUrl>
<isApplicableToConnectSrc>true</isApplicableToConnectSrc>
```

## ACC (iframe hosts) — the `frame-src` case

The Agentforce Conversation Client loads Lightning Out into an iframe. For local dev, that iframe's origin is the dev server URL (`http://localhost:5173`). Two configurations need to line up:

1. **Trusted Domains for Inline Frames** (Setup → Session Settings) — platform-level allowlist for what can be *host* of an iframe embedding Salesforce. Type **Lightning Out**.
2. **`CspTrustedSite`** with `isApplicableToFrameSrc: true` — allowlist for what the *React app* is allowed to iframe.

For ACC, **#1 is the one that matters** because the React app is embedding a Salesforce iframe, not the other way around. Full detail in [acc-integration.md](acc-integration.md). Only add a `frame-src` trusted site if the React app embeds a *third-party* iframe (embedded auth, third-party video, etc.).

## `tabSettings` — making the app launch from App Launcher

When the UIBundle target is `AppLauncher`, the platform auto-creates a tab. End users must have it visible in their permission set:

```xml
<tabSettings>
    <tab>MyReactApp</tab>          <!-- matches UIBundle developer name -->
    <visibility>Visible</visibility>
</tabSettings>
```

Without this, the bundle deploys and the tab exists in metadata, but users don't see it in App Launcher.

## Diagnosing CSP blocks

Browser DevTools → Console prints CSP violations in full:

```
Refused to load the image 'https://cdn.example.com/foo.png' because it violates
the following Content Security Policy directive: "img-src ...".
```

Key facts from the message:
- the **directive name** (`img-src`) → maps to `isApplicableToImg`
- the **URL origin** (`https://cdn.example.com`) → the `endpointUrl`

Add a matching `CspTrustedSite`, redeploy, hard-refresh. CSP is cached — sometimes a Ctrl+Shift+R or new incognito window is needed.

## What NOT to do

- ❌ Don't set `isApplicableToConnectSrc: true` as a shotgun fix — that grants `fetch()` permission to the origin, which is rarely what you want. Use a Named Credential + Apex REST for outbound data calls.
- ❌ Don't manage third-party API auth inside the React app. Named Credential + Apex REST keeps secrets server-side.
- ❌ Don't deploy a permission set with `objectPermissions` but no `fieldPermissions` — UI API queries will return `null` for every field and users will see empty data.
- ❌ Don't rely on profile-level permissions in new work. Permission sets are the supported path for UI bundle access.

## Cross-skill handoff

| Task | Skill |
|---|---|
| Permission-set design / audit / hierarchy | [sf-permissions](../../sf-permissions/SKILL.md) |
| Named Credentials for third-party APIs | [sf-integration](../../sf-integration/SKILL.md) |
| Apex REST endpoints for server-side calls | [sf-apex](../../sf-apex/SKILL.md) |
| ACC iframe + cookie configuration | [acc-integration.md](acc-integration.md) |
