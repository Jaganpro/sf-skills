# Official Sources

The authoritative documentation and reference implementations this skill is distilled from. Cite these when you need to back up a claim or check the current state of the Beta.

## Salesforce Developer Documentation (Beta)

### Overview & Setup
- [Build a React App with Salesforce Multi-Framework (Beta)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-overview.html)
- [Configure Your Org for React App Development (Beta)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-setup.html)

### Project Mechanics
- [Integrate Your React App with the Agentforce 360 Platform (Beta)](https://developer.salesforce.com/docs/platform/code-builder/guide/reactdev-integrate.html) — `UIBundle`, `ui-bundle.json`, `.uibundle-meta.xml`, templates
- [Develop a React App Manually (Beta)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-develop.html) — manual authoring path

### Data SDK & GraphQL
- [Data SDK and GraphQL (Beta)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-data-sdk.html)
- [Access Record Data with Data SDK (Beta)](https://developer.salesforce.com/docs/platform/code-builder/guide/reactdev-data-sdk-usage.html)
- [Error Handling in Data SDK (Beta)](https://developer.salesforce.com/docs/platform/code-builder/guide/reactdev-data-sdk-graphql-error.html)

### UI / Experience
- [Style Your React Apps (Beta)](https://developer.salesforce.com/docs/platform/code-builder/guide/reactdev-styling.html)
- [Integrate Agentforce Conversation Client in Your React App (Beta)](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/reactdev-acc.html)

### Decisions
- [React vs LWC (Beta)](https://developer.salesforce.com/docs/platform/code-builder/guide/reactdev-lwc-diff.html)

## Reference Implementations

### `multiframework-recipes`
- [GitHub: trailheadapps/multiframework-recipes](https://github.com/trailheadapps/multiframework-recipes) — canonical recipe set
- [`AGENT.md`](https://raw.githubusercontent.com/trailheadapps/multiframework-recipes/main/AGENT.md) — developer & agent guide for the recipe repo (the source of most recipe conventions in this skill)
- Key directories:
  - `force-app/main/react-recipes/uiBundles/reactRecipes/` — the React app
  - `force-app/main/default/` — shared metadata (objects, classes, permission sets)
  - `data/` — sample data tree plans

## Salesforce CLI Reference

- [Salesforce CLI Command Reference: ui-bundle Commands](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_ui-bundle.htm)
- [Salesforce CLI Command Reference: template generate ui-bundle](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_template_generate_ui-bundle.htm)
- [Salesforce CLI Command Reference: template generate project](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_template_generate_project.htm)

## Metadata API

- [Metadata API Developer Guide: UIBundle](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_uibundle.htm)
- [Salesforce DX Project Structure and Source Format](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_source_file_format.htm)

## Related Salesforce Docs

- [Lightning Types in Agent Action](https://developer.salesforce.com/docs/) — used by ACC for dynamic component rendering
- [Agentforce Conversation Client Developer Guide](https://developer.salesforce.com/docs/) — standalone (external apps)
- [Agentforce Vibes Setup](https://developer.salesforce.com/docs/platform/einstein-for-devs/guide/) — for AI-assisted authoring
- [Salesforce Multi-Framework Developer Guide](https://developer.salesforce.com/docs/) — landing page

## npm Packages

| Package | Purpose |
|---|---|
| [`@salesforce/sdk-data`](https://www.npmjs.com/package/@salesforce/sdk-data) | Data SDK (`createDataSDK`, `gql`, `NodeOfConnection`) |
| [`@salesforce/agentforce-conversation-client`](https://www.npmjs.com/package/@salesforce/agentforce-conversation-client) | ACC widget for embedding chat |
| [`@salesforce/vite-plugin-ui-bundle`](https://www.npmjs.com/package/@salesforce/vite-plugin-ui-bundle) | Vite dev server integration |
| [`@salesforce/ui-bundle`](https://www.npmjs.com/package/@salesforce/ui-bundle) | Helper functions for the SDK |
| [`@salesforce-ux/design-system`](https://www.npmjs.com/package/@salesforce-ux/design-system) | SLDS CSS blueprints |
| [`@salesforce/design-system-react`](https://www.npmjs.com/package/@salesforce/design-system-react) | SLDS React components |

## When to defer to official docs

This skill condenses the docs and adds opinionated patterns from the recipe repo. Defer to the linked official sources when:

- A new Beta release changes the API surface (versions of `@salesforce/sdk-data`, ACC, the Vite plugin)
- You hit a specific error message you can't find in [troubleshooting.md](troubleshooting.md)
- The exact SDK option shape (e.g. `createAccWidget` parameters) matters for the bug you're fixing
- You need to verify a Beta limitation hasn't changed (sandbox-only, English-only, can't disable, etc.)

The skill's posture is: **patterns and decision frameworks** are stable enough to encode here; **exact API shapes** of evolving SDKs should be verified against the installed package.
