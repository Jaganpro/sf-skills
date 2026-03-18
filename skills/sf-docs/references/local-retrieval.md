# sf-docs Local Retrieval Strategy

This document defines how `sf-docs` should use a local synced corpus **without any external index dependency**.

## First-Version Policy

Use the local corpus as a **cache of official Salesforce documentation artifacts**.

Recommended root:

```text
~/.sf-docs/
```

## Preferred Local Artifact Order

When local assets exist for a likely guide, evaluate them in this order:

1. normalized markdown (`normalized/md/<slug>/index.md`)
2. browser scrape payloads (`raw/html/<slug>.scrape.json`)
3. downloaded official PDFs (`raw/pdf/<slug>.pdf`)

This order keeps the first pass simple and deterministic:

- normalized markdown is easiest to scan and quote
- scrape payloads preserve page-specific text for JS-heavy docs
- PDFs remain a stable fallback when HTML is weak

## Acceptance Rules

Local artifacts are acceptable only when the evidence is real.

Accept a local artifact when:

- the requested identifier appears exactly, or
- the query-specific phrases/terms appear densely enough in the right guide family, and
- the artifact is clearly from the expected Salesforce product area

Reject or downgrade a local artifact when:

- it comes from the wrong guide family
- exact identifiers are missing
- the text is too fragmentary to support a grounded answer
- the content looks stale for a release-sensitive question

## Retrieval Expectations

When a local corpus is available, `sf-docs` should:

1. classify the query
2. rank likely guides from the manifest
3. inspect the best local artifacts first
4. answer from local artifacts only when confidence is good enough
5. fall back to Salesforce-aware retrieval when local evidence is weak

## Why This Design Works

The project intentionally avoids any extra local indexing layer.

The local corpus remains valuable because it still gives:

- repeatable local lookups
- a deterministic cache of previously synced official docs
- cheaper/faster follow-up retrieval after sync
- a clean separation between acquisition, normalization, and query-time reasoning

## Future Expansion

If local-first retrieval later needs more sophistication, improve the ranking and artifact-evidence checks first.

Avoid reintroducing a new indexing dependency unless benchmark evidence clearly justifies it.
