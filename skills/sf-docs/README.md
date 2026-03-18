# sf-docs

Official Salesforce documentation retrieval skill for `sf-skills`.

## Contract

`sf-docs` is a **core skill** in the suite.

- mandatory with `sf-skills`
- prefers a **local synced corpus** when available
- falls back to **Salesforce-aware retrieval** when local artifacts are missing or weak
- keeps downloaded/scraped docs **local-only**, not in the public repo
- has **no external indexing dependency**

## Runtime States

### local-first

- detect local corpus readiness
- inspect the most likely local artifacts first
- accept results only when the requested identifiers/terms are present
- otherwise fall back to targeted official HTML/PDF retrieval

### salesforce-aware

- classify likely doc family first
- target likely official guide/article roots
- prefer official URLs and PDFs over third-party summaries
- avoid broad crawling during normal question answering

## Quick Start

### Prerequisites

- Python 3.10+
- Optional local corpus under `~/.sf-docs/` if you want faster repeat lookups

### Try it now (no setup required)

Test sf-docs immediately without any corpus setup:

```bash
python3 skills/sf-docs/scripts/cli.py retrieve           --query "System.StubProvider"           --mode salesforce_aware           --live-scrape
```

### Full local corpus setup

The pilot corpus covers 7 guides: Apex Developer Guide, Apex Reference,
REST API, Metadata API, Object Reference, LWC, and Agentforce.
See [references/pilot-scope.md](./references/pilot-scope.md) for details.

#### 1. Discover guides

```bash
python3 skills/sf-docs/scripts/cli.py discover           --output ~/.sf-docs/manifest/guides.json           --pretty
```

Verify: `~/.sf-docs/manifest/guides.json` exists with 7 guides.

#### 2. Sync corpus

```bash
python3 skills/sf-docs/scripts/cli.py sync           --download-pdf           --normalize
```

Verify: `~/.sf-docs/normalized/md/` contains guide folders (for example `apexcode/`, `api_rest/`).

#### 3. Test retrieval

```bash
python3 skills/sf-docs/scripts/cli.py retrieve           --query "Find official Salesforce REST API authentication docs"           --mode local_first
```

## CLI Reference

### Check local corpus status

```bash
python3 skills/sf-docs/scripts/cli.py status
```

### Diagnose runtime lookup behavior

```bash
python3 skills/sf-docs/scripts/cli.py diagnose           --query "Find official Salesforce REST API authentication docs"
```

### Run end-to-end retrieval (local-first mode)

```bash
python3 skills/sf-docs/scripts/cli.py retrieve           --query "Find official Salesforce REST API authentication docs"           --mode local_first
```

### Run Salesforce-aware retrieval for Help article discovery

```bash
python3 skills/sf-docs/scripts/cli.py retrieve           --query "Find official Salesforce Help documentation about Messaging for In-App and Web allowed domains, CORS allowlist, and allowed origins."           --mode salesforce_aware           --live-scrape
```

### Execute the core benchmark and write results

```bash
python3 skills/sf-docs/scripts/cli.py run-benchmark           --benchmark skills/sf-docs/assets/retrieval-benchmark.json           --results skills/sf-docs/assets/retrieval-benchmark.results.json
```

### Execute the robustness benchmark

```bash
python3 skills/sf-docs/scripts/cli.py run-benchmark           --benchmark skills/sf-docs/assets/retrieval-benchmark.robustness.json           --results skills/sf-docs/assets/retrieval-benchmark.robustness.results.json
```

### Score retrieval benchmark results

```bash
python3 skills/sf-docs/scripts/cli.py score-benchmark           --benchmark skills/sf-docs/assets/retrieval-benchmark.json           --results skills/sf-docs/assets/retrieval-benchmark.results.json
```

> See [references/cli-workflow.md](./references/cli-workflow.md) for the recommended operator sequence.

## Key References

- [SKILL.md](./SKILL.md)
- [references/local-corpus-layout.md](./references/local-corpus-layout.md)
- [references/discovery-manifest.md](./references/discovery-manifest.md)
- [references/local-retrieval.md](./references/local-retrieval.md)
- [references/runtime-workflow.md](./references/runtime-workflow.md)
- [references/ingestion-workflow.md](./references/ingestion-workflow.md)
- [references/salesforce-scraper-techniques.md](./references/salesforce-scraper-techniques.md)
- [references/pilot-scope.md](./references/pilot-scope.md)
- [references/benchmark-protocol.md](./references/benchmark-protocol.md)
- [references/cli-workflow.md](./references/cli-workflow.md)
