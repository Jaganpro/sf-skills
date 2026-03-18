# sf-docs Ingestion Workflow

This document describes the first-version local ingestion workflow for `sf-docs`.

## Scope

The workflow is intentionally **targeted**, not broad:

- fetch only the guides selected in the manifest or by explicit slug
- prefer guide-root HTML when it is clean enough to normalize
- use official PDFs as fallback or bulk-ingestion source
- keep everything local to the user machine

## Pipeline

1. **discover**
   - build/enrich the guide manifest
   - classify each guide family
   - derive and optionally verify PDF candidates

2. **fetch**
   - download raw HTML guide roots when requested
   - optionally use a Salesforce-aware browser scraper for JS-heavy pages
   - download raw official PDFs when requested

3. **normalize**
   - convert useful HTML into markdown with provenance frontmatter
   - if HTML is weak/unusable, prefer PDF text extraction when available
   - retain raw sources locally for reprocessing

4. **refresh**
   - re-run sync for changed, missing, or newly added guides

## Helper Scripts

### Discover / enrich manifest

```bash
python3 skills/sf-docs/scripts/discover_salesforce_docs.py           --seed skills/sf-docs/assets/discovery-manifest.seed.json           --output ~/.sf-docs/manifest/guides.json           --pretty
```

### Fetch / normalize selected guides

```bash
python3 skills/sf-docs/scripts/sync_sf_docs.py           --manifest ~/.sf-docs/manifest/guides.json           --corpus-root ~/.sf-docs           --slug apexcode           --slug api_rest           --download-pdf           --download-html           --browser-scrape           --normalize
```

## Normalization Preference

When browser-scraped JSON, raw HTML, and raw PDF are available:

1. try **browser-scraped extraction first** for JS-heavy Salesforce pages
2. then try **raw HTML normalization** if `html_preferred` is true
3. if HTML looks like shell/noise or is too thin, fall back to **PDF extraction**
4. always preserve provenance in frontmatter

## v1 Constraints

- no broad whole-site crawling during routine queries
- no external indexing dependency
- no public-repo storage of downloaded Salesforce docs
- no parallel live-retrieval fusion by default
