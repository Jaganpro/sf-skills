# sf-docs CLI Workflow

Use the unified `cli.py` wrapper to operate `sf-docs` end-to-end.

## Main Commands

### 1. Discover / enrich the manifest

```bash
python3 skills/sf-docs/scripts/cli.py discover           --output ~/.sf-docs/manifest/guides.json           --pretty
```

### 2. Sync a local corpus

```bash
python3 skills/sf-docs/scripts/cli.py sync           --manifest ~/.sf-docs/manifest/guides.json           --download-pdf           --normalize
```

### 3. Check runtime status

```bash
python3 skills/sf-docs/scripts/cli.py status
```

### 4. Diagnose query-time routing

```bash
python3 skills/sf-docs/scripts/cli.py diagnose           --query "Find official Salesforce REST API authentication docs"
```

### 5. Run local-first retrieval

```bash
python3 skills/sf-docs/scripts/cli.py retrieve           --query "Find official Salesforce REST API authentication docs"           --mode local_first
```

### 6. Score benchmark results

```bash
python3 skills/sf-docs/scripts/cli.py score-benchmark           --results skills/sf-docs/assets/retrieval-benchmark.results-template.json           --benchmark skills/sf-docs/assets/retrieval-benchmark.json
```

## Recommended Operator Sequence

1. `discover`
2. `sync`
3. `status`
4. `diagnose`
5. `retrieve`
6. `score-benchmark`

## Notes

- `discover` can write directly into `~/.sf-docs/manifest/guides.json`
- `sync` is targeted by default and accepts repeated `--slug` filters
- `diagnose` explains whether a query should use local-first or Salesforce-aware retrieval
- `retrieve --mode salesforce_aware --live-scrape` is useful for JS-heavy pages when no local corpus is present
