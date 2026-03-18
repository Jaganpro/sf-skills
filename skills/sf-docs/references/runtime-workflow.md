# sf-docs Runtime Workflow

This document defines the first-version runtime behavior for `sf-docs`.

## Query-Time Flow

Use this sequence in order:

1. **Detect local corpus readiness**
   - check whether `~/.sf-docs/normalized/md/` exists
   - check whether the local corpus contains usable markdown artifacts

2. **Inspect local artifacts when available**
   - rank likely guides from the manifest
   - check normalized markdown, scrape payloads, and PDFs in that order
   - prefer exact API names, CLI commands, error strings, and quoted terms

3. **Evaluate evidence quality**
   - if results are strong, answer from local artifacts
   - if results are weak, incomplete, or unrelated, fall back

4. **Salesforce-aware fallback retrieval**
   - identify likely doc family first (`platform`, `atlas`, `help`, `pdf`)
   - try the most likely official guide/article root
   - for JS-heavy pages, prefer Salesforce-aware browser scraping with Shadow DOM and legacy container heuristics
   - use targeted fallback, not broad crawling
   - prefer official PDFs when HTML retrieval is shell-rendered or unstable

5. **Answer with source grounding**
   - cite the exact official source URL
   - identify whether the source came from local markdown, local scrape payload, HTML retrieval, or PDF fallback
   - call out uncertainty when retrieval was partial or indirect

## Weak Result Rules

Fall back when:

- no relevant local artifacts are returned
- returned guides are clearly unrelated
- the exact requested concept/identifier does not appear
- snippets are too fragmentary to support a reliable answer
- the query is release-sensitive and the local corpus seems stale

## Salesforce-Aware Special Instructions

When no useful local corpus exists:

- do **not** rely on naive generic fetch expectations for Salesforce docs
- identify the likely official guide family first
- prefer official URLs over blog summaries
- try `help.salesforce.com` article views carefully because shell content is common
- try official PDFs when guide HTML is unstable

## Keep Fallback Targeted

During normal query-time retrieval:

- do **not** crawl the entire Salesforce docs universe
- do **not** launch a broad sync automatically
- target likely guide roots, exact official pages, and candidate PDFs first

Broad crawling belongs in explicit sync workflows, not in routine question answering.

## Separate Sync Workflow

Keep query-time retrieval separate from corpus maintenance.

Recommended operator workflow:

1. `discover` — build/update the guide manifest
2. `sync` — fetch targeted HTML/PDF sources
3. `normalize` — convert sources into markdown with provenance
4. `refresh` — re-run sync for changed or missing guides

## Persistence Policy

Useful fetched assets may be stored locally for future retrieval:

- official PDFs in `~/.sf-docs/raw/pdf/`
- browser scrape payloads and raw HTML in `~/.sf-docs/raw/html/`
- normalized markdown in `~/.sf-docs/normalized/md/`
- manifest/status files in `~/.sf-docs/manifest/`

However:

- query-time fallback should not trigger uncontrolled large-scale fetches
- persisted content stays local to the user machine
- fetched Salesforce docs content should not be committed into the public repo

## Repo Hygiene & Legal Constraints

Keep the public repo limited to:

- skill definitions
- installer logic
- helper scripts
- schemas, templates, and examples

Keep Salesforce documentation artifacts local-only:

- downloaded PDFs
- scraped HTML captures
- normalized markdown corpus
- browser scrape payloads
