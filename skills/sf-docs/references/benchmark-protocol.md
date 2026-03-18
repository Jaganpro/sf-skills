# sf-docs Benchmark Protocol

This document defines how to validate `sf-docs`.

## Runtime Mode to Validate

Validate the default **local-first runtime**:

- inspect local artifacts when available
- fall back to Salesforce-aware retrieval on weak/missing evidence

## Benchmark Assets

Use the **core grounding benchmark** for normal retrieval quality:

- [assets/retrieval-benchmark.json](../assets/retrieval-benchmark.json)
- [assets/retrieval-benchmark.results-template.json](../assets/retrieval-benchmark.results-template.json)

Use the **robustness benchmark** for negative cases and wrong-guide rejection:

- [assets/retrieval-benchmark.robustness.json](../assets/retrieval-benchmark.robustness.json)
- [assets/retrieval-benchmark.robustness.results-template.json](../assets/retrieval-benchmark.robustness.results-template.json)

Score results with:

- [scripts/score_retrieval_benchmark.py](../scripts/score_retrieval_benchmark.py)

## What Counts as a Pass

A benchmark case passes when:

- the retrieval outcome is marked `pass`
- the answer is grounded on an official Salesforce source when the expected outcome is a grounded hit
- the source family matches the benchmark expectation
- the product matches when the benchmark specifies a product
- the guide matches the expected guide when a guide is specified
- required evidence terms or identifiers are actually present
- negative / reject cases avoid returning a confident grounded answer from the wrong official guide

## Suggested Status Values

- `pass`
- `fail`
- `partial`
- `pending`

## Validation Checklist

For each case, verify:

1. local artifacts were used when available and relevant
2. weak local hits were rejected instead of overtrusted
3. Salesforce-aware fallback was used when needed
4. help.salesforce.com shell/noise issues were avoided when possible
5. official PDF fallback was used when HTML was unstable
6. the final answer was grounded

## Fallback Threshold Refinement

Use benchmark failures to refine fallback rules.

Examples:

- If local artifacts keep matching the wrong guide, tighten acceptance rules
- If local artifacts miss exact references, bias more strongly toward identifier evidence
- If retrieval keeps landing on shell pages, increase preference for guide roots or PDF candidates
- If fallback is too slow, narrow guide targeting instead of broadening crawl behavior

## v1 Non-Goals

Do **not** block v1 on these advanced features:

- whole-site automatic crawling during routine lookup
- highly automated refresh of all public Salesforce docs
- reintroducing a new indexing dependency before benchmark evidence exists

## Recommendation

Get the pilot corpus and benchmark healthy first.

Only after the local-first benchmark performs well should `sf-docs` expand to broader documentation coverage.
