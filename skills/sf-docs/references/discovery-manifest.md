# sf-docs Discovery Manifest

The discovery manifest is the **source of truth** for what `sf-docs` knows about Salesforce documentation roots, guide families, PDF candidates, local storage paths, and sync state.

## Why a Manifest Exists

Salesforce documentation spans several delivery patterns:

- `developer.salesforce.com/docs/platform/...`
- `developer.salesforce.com/docs/atlas.en-us.<book>.meta/...`
- `help.salesforce.com/...`
- `resources.docs.salesforce.com/...pdf/...`

A manifest lets `sf-docs` work deterministically instead of guessing from scratch on every lookup.

## Rules

1. **Manifest first** — guide discovery should write to the manifest before bulk sync work begins.
2. **Manifest is the source of truth** — fetch, normalize, and retrieval routing should read from it.
3. **HTML page extraction is preferred** when it yields clean, page-level content.
4. **PDFs are secondary but valid** for bulk ingestion, fallback retrieval, and offline reuse.
5. **Every normalized document must preserve provenance** back to a manifest entry.

## Families

Each manifest entry should carry a `family` value:

- `platform` — modern platform-style docs under `developer.salesforce.com/docs/platform/...`
- `atlas` — legacy guide/reference docs under `developer.salesforce.com/docs/atlas.en-us.*`
- `help` — setup/admin/help content under `help.salesforce.com`
- `pdf` — direct guide PDF or PDF-first document
- `unknown` — unresolved; requires operator review

## Preferred Retrieval Order

For a guide with both HTML and PDF forms:

1. Prefer **HTML/page-level extraction** if the page body is clean and navigable
2. Use **PDF** when HTML is unstable, shell-rendered, or better suited for local reuse
3. Keep both in the manifest when both are useful

## Recommended Schema

```json
{
  "version": 1,
  "generated_at": "2026-03-14T10:00:00Z",
  "root": "https://developer.salesforce.com/docs#browse",
  "guides": [
    {
      "slug": "apexcode",
      "title": "Apex Developer Guide",
      "family": "atlas",
      "root_url": "https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/",
      "book_id": "apexcode",
      "product": "platform",
      "html_preferred": true,
      "pdf_candidates": [
        "https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/apexcode.pdf"
      ],
      "pdf_verified": null,
      "normalized_dir": "~/.sf-docs/normalized/md/apexcode",
      "raw_pdf_path": "~/.sf-docs/raw/pdf/apexcode.pdf",
      "status": {
        "discovered": true,
        "fetched": false,
        "normalized": false,
        "cached": false
      },
      "notes": []
    }
  ]
}
```

## Minimum Fields Per Entry

| Field | Purpose |
|------|---------|
| `slug` | Stable local identifier |
| `title` | Human-readable guide name |
| `family` | Retrieval strategy selector |
| `root_url` | Official entry point |
| `book_id` | Atlas/PDF correlation when available |
| `html_preferred` | Whether HTML should be tried before PDF |
| `pdf_candidates` | Candidate official PDF URLs |
| `pdf_verified` | Whether a candidate was successfully validated |
| `normalized_dir` | Local markdown output location |
| `raw_pdf_path` | Local retained PDF location |
| `status.*` | Pipeline progress tracking |

## PDF Discovery

For `atlas` guides, derive PDF candidates from `book_id` using the official CDN pattern:

```text
https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/<book_id>.pdf
```

Verification should be explicit — do not assume every candidate exists.

## Normalization Rules

All cached content should be normalized into markdown with provenance frontmatter such as:

```yaml
---
title: Apex Developer Guide
source_url: https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/
guide_slug: apexcode
family: atlas
book_id: apexcode
fetched_at: 2026-03-14T10:00:00Z
source_type: html
---
```

## v1 Recommendation

For v1, keep the manifest focused on the small pilot corpus and expand only after benchmark evidence supports it.
