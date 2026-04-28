# Configure Your Org for React Development

> Beta availability: **sandbox and scratch orgs only**. Default language must be `en_US`. Developer Edition orgs and Trailhead Playgrounds are not supported.

## 1. Pre-flight

- Latest **Salesforce CLI**: `sf update`
- Latest **Salesforce Extension Pack** for VS Code (or equivalent IDE)
- **Node.js v22+** and **npm**
- For external apps: planned **Customer Community / Customer Community Plus** (B2C) or **Partner Community / Channel Account** (B2B) user licenses

## 2. Enable Multi-Framework (Beta)

> Required permission: **Customize Application**.

1. Setup → search **"Salesforce Multi-Framework"** → click **React Development with Salesforce Multi-Framework (Beta)**.
2. Click **Enable Beta** → confirm.
3. **Cannot be disabled** afterwards. Treat the toggle as one-way.

## 3. Authorize the org

```bash
# Sandbox or production hub
sf org login web -d -a myhuborg

# Sandbox-specific (skip -d)
sf org login web -a mysandbox

# Optional: scratch org from project def
sf org create scratch -d -f config/project-scratch-def.json -a recipes
```

For scratch orgs, **explicitly set `"language": "en_US"`** in the project def. Non-English orgs hit known issues.

## 4. Install the UI Bundle CLI plugin

```bash
sf plugins install @salesforce/plugin-ui-bundle-dev
```

This adds the `sf template generate ui-bundle` command and runtime helpers used by `npm run dev`.

## 5. (External apps only) Set up Digital Experiences

External React apps live inside an Experience Cloud site even though you don't author the site in Experience Builder.

1. Setup → confirm **Digital Experiences** is enabled.
2. Setup → Digital Experiences → All Sites → **New** (any template — you'll back out).
3. Click **Back to Setup** without picking a template — this just ensures the underlying dependencies exist.
4. Confirm Customer/Partner Community user licenses are available.

The metadata you ship later (`digitalExperienceConfigs`, `digitalExperiences/sfdc_cms_site`, `networks`, `sites`) wires the React app to the site.

## 6. (Agentforce Vibes users only) MCP server setup

If you'll use Agentforce Vibes' natural-language scaffolding:

1. Setup → MCP Servers → **metadata-experts** → **Activate**.
2. Setup → MCP Servers → **salesforce-api-context** → **Activate**.
3. In VS Code, open the Agentforce Vibes panel.
4. Connect to your authorized org.
5. Confirm these MCP servers are enabled and connected:
   - Salesforce DX MCP server
   - Salesforce Metadata Experts MCP server
   - Salesforce API Context MCP server
6. Confirm all Salesforce skills and rules are enabled in the Vibes panel.

If you're going to vibe-code CMS content into the app, also activate the **content-readonly** MCP server (DE / scratch only):

1. Setup → CMS → toggle **Access the Content Read-Only MCP Server and Tools (Beta)**.
2. Setup → MCP Servers → **content-readonly** → **Activate**.
3. Add `content-readonly` as a remote server in Vibes pointing at the Server URL from the MCP detail page.
4. Set `cmsAssetProviderOrg` to the alias of the org that holds your CMS content.

For `search_electronic_media`: deploy the **CMS Base (Beta)** data kit, then create a Hybrid Search index in Data Cloud over the `Electronic Media` source object with `Description` chunked via Passage Extraction.

## 7. (ACC users only) Org configuration

To embed the Agentforce Conversation Client in a React app:

### 7a. Enable Agentforce
Setup → Einstein → Einstein Generative AI → Agentforce Studio → Agentforce Agents → enable **Agentforce** preference. Configure at least one Employee Agent with topics + actions.

### 7b. Cookie policy
Setup → My Domain → Routing and Policies → **uncheck** *Require first-party use of Salesforce cookies* → **Save**.

This is required because the React app is on a non-Salesforce origin (including `localhost`) and the ACC iframe must persist session state across origins.

### 7c. Trusted Domains for Inline Frames
Setup → Session Settings → **Trusted Domains for Inline Frames** → **Add Domain**:

- Production / preview origin (e.g. `https://app.example.com`)
- Local dev origin (e.g. `http://localhost:5173`)

Set **iFrame type** to **Lightning Out** for each.

## 8. Optional — Permission Set

Most starter projects ship a `recipes` permission set granting access to the bundle and any custom objects. Assign it to the running user:

```bash
sf org assign permset -n recipes
```

## 9. Smoke-test the setup

```bash
sf org open
```

Expected: org opens, App Launcher contains your app (after deploy), or Digital Experiences shows the linked site (external apps).

## Common setup failures

| Symptom | Cause | Fix |
|---|---|---|
| Beta toggle missing in Setup | DE org or Playground | Use a sandbox or scratch org |
| Beta toggle visible but not clickable | User lacks **Customize Application** | Assign the System Admin profile or equivalent |
| `sf template generate ui-bundle` not recognized | `@salesforce/plugin-ui-bundle-dev` not installed | `sf plugins install @salesforce/plugin-ui-bundle-dev` |
| Vite dev server starts but data calls 401 | Org not authorized in current shell | `sf org login web -a <alias>` |
| ACC FAB never appears | Trusted Domains not added or cookies still restricted | Re-check steps 7b and 7c |
| Non-English org blocks app loading | Known issue | Set org language to `en_US` (scratch) or use a different org |
