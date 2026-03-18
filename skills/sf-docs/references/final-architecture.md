# sf-docs Final Architectural Recommendation

## Mandatory vs Optional

- `sf-docs` is a **mandatory core skill** in `sf-skills`
- `sf-docs` has **no external retrieval-index dependency**

## Runtime Behavior

Use a **sequential retrieval model** in v1:

1. detect local corpus availability
2. inspect local artifacts first when present
3. evaluate evidence quality
4. fall back to Salesforce-aware retrieval when results are weak or missing
5. answer with grounded official sources

## Why This Architecture

This model gives the best balance of:

- correctness
- operational simplicity
- predictable local caching
- compatibility with both synced and non-synced environments

## Local Storage

All downloaded/scraped Salesforce documentation artifacts stay **local to the user machine**:

- manifests
- raw PDFs
- raw HTML captures
- browser scrape payloads
- normalized markdown

These artifacts should **not** be committed into the public Git repo.

## v1 Boundaries

Keep v1 intentionally limited:

- small pilot corpus
- local artifact inspection before live retrieval
- targeted fallback retrieval
- no broad automatic crawling during normal queries
- no new indexing dependency

## Expansion Rule

Expand beyond the pilot corpus only after benchmark evidence shows that:

- local-first retrieval is reliable
- wrong-guide rejection remains strong
- fallback thresholds are well tuned
- answer grounding remains strong
