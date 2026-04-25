# sf-react

Salesforce skill for working with React on the **Multi-Framework** runtime — the new native-React layer of Headless 360 / the Agentforce 360 Platform, announced at TDX 2026 (April 15 2026).

Helps an LLM agent ground its work in the official `trailheadapps/multiframework-recipes` patterns rather than freelancing against beta APIs.

## What this skill does

- Detects Multi-Framework projects via `uiBundles/`, `ui-bundle.json`, `.uibundle-meta.xml`, and `package.json` markers
- Routes tasks to the right recipe across the 44-recipe catalogue (Hello, Read Data, Modify Data, SF APIs, Error Handling, Routing, Styling, Integration)
- Front-loads the highest-stakes footgun (stale GraphQL codegen against an uncommitted schema → silent prod failure)
- Defers cleanly to `sf-apex`, `sf-deploy`, and the `sf` / `npm` CLIs for live operations
- Refuses production deploys and non-English orgs (beta restrictions)

## When it triggers

See the `description` field in `SKILL.md`. Short version: anywhere a Multi-Framework UI bundle, recipe, or Multi-Framework-specific package marker appears. **Not** generic React work.

## Files

- `SKILL.md` — main skill file (front-loads the WARNING, owns the routing table)
- `references/recipes-routing.md` — full 44-recipe routing catalogue
- `references/footguns.md` — extended failure-mode breakdown
- `scripts/check_codegen_freshness.py` — pre-deploy validator that enforces fresh GraphQL codegen against the schema

## Beta constraints (April 2026)

- Open beta — scratch orgs and sandboxes only
- English-default orgs only (`"language": "en_US"`)
- Node.js v22+ required (v18 / v20 unsupported)
- `sourceApiVersion: "66.0"` (Spring '26) or later

## Source

Content grounded in the official `trailheadapps/multiframework-recipes` repo and the Salesforce Headless 360 / Multi-Framework launch documentation.
