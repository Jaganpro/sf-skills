# Salesforce Scraper Techniques

`sf-docs` should borrow the **techniques** from Salesforce-specific scrapers, but keep storage and retrieval independent from any external indexing layer.

## Principles

1. **Do not couple scraping to storage**
   - scrape into local raw artifacts
   - normalize into markdown
   - reuse those artifacts directly during local-first retrieval

2. **Prefer robust browser rendering for JS-heavy docs**
   - render with a headless browser
   - then apply Salesforce-specific extraction heuristics

3. **Use targeted strategies, not generic body scraping**
   - modern article/main content
   - Shadow DOM traversal for help/docs shells
   - legacy Salesforce doc containers
   - iframe extraction for older embedded docs

## Reimplemented Techniques

### Deep Shadow DOM Traversal

Traverse through nested shadow roots and search for real content, not just surface DOM.

This is especially important for:
- `help.salesforce.com`
- legacy/modern developer docs rendered through custom web components

### Help Longform Content Detection

Look for content such as:
- `.slds-text-longform`

This is often a stronger signal than plain `document.body.innerText`.

### Legacy Salesforce Docs Containers

Check for legacy doc structures like:
- `doc-content-layout`
- `doc-xml-content`
- `doc-content`
- `doc-amf-reference .markdown-content`

### Iframe Fallback

Some older or embedded doc surfaces still expose meaningful content in iframes.

### PDF Fallback

If HTML retrieval is shell-rendered, unstable, or too thin:
- download the official PDF candidate
- extract text locally
- normalize into markdown with provenance

## About Aura / Help-Article Fast Paths

Some implementations experiment with direct Aura or internal article APIs for `help.salesforce.com`.

For `sf-docs`, treat this as **optional and experimental**:
- helpful in theory
- brittle in practice
- more likely to break over time than browser-rendered extraction

For v1, the preferred approach is:
1. browser render + Salesforce-aware DOM extraction
2. official PDF fallback when needed

If a stable help-article API path is later identified, it can be added as a targeted optimization.

## Why This Is Better for sf-docs

This keeps the architecture aligned with the goals of the project:

- no SQLite dependency
- no external indexing dependency
- scraping is an acquisition/normalization layer
- local artifacts can be reused directly during retrieval
- heuristics are reusable no matter which browser engine is used

## Browser Engine Choice

The heuristics should remain mostly browser-engine agnostic.

That means the project can choose between:
- Playwright
- Puppeteer

without changing the overall `sf-docs` architecture.
