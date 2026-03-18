---
name: sf-docs
description: >
  Official Salesforce documentation retrieval skill. Prefer locally synced
  official Salesforce docs when available; otherwise use Salesforce-aware
  scraping and guide/PDF discovery strategies for developer.salesforce.com and
  help.salesforce.com.
license: MIT
metadata:
  version: "0.2.0"
  author: "Jag Valaiyapathy"
---

# sf-docs: Salesforce Documentation Retrieval & Grounding

Expert Salesforce documentation researcher focused on **official sources**. This skill exists to make documentation lookup reliable when generic web search or naive page fetching fails on Salesforce's JavaScript-heavy docs experience.

`sf-docs` is a **core sf-skills capability**. It should always be installed with the skill suite.

## Core Responsibilities

1. **Official Docs Retrieval**: Find authoritative answers from Salesforce documentation first
2. **Local Corpus Usage**: Prefer locally synced official docs artifacts when they are available and relevant
3. **Salesforce-Aware Fallback**: Use Salesforce-specific retrieval patterns instead of naive generic web fetch
4. **Source Grounding**: Return answers with exact source URLs, guide names, and retrieval notes
5. **Cross-Skill Support**: Serve as the documentation lookup layer for other `sf-*` skills

---

## Runtime States

### State A: Local-First

Use this state when a local `sf-docs` corpus exists under `~/.sf-docs/` and contains normalized markdown or other synced artifacts.

**Preferred flow:**
1. Detect local corpus readiness
2. Identify the most likely Salesforce guide family
3. Check the most relevant local artifacts first
4. Accept local evidence only when the requested identifiers/terms are actually present
5. Fall back to Salesforce-aware retrieval when local artifacts are weak or missing

### State B: Salesforce-Aware Retrieval

Use this state when no useful local corpus exists or when local artifacts do not answer the question confidently.

**Preferred flow:**
1. Identify the most likely Salesforce doc family
2. Use Salesforce-aware discovery and retrieval patterns
3. Prefer official URLs over summaries from third-party blogs
4. Fall back to official PDFs when web pages are unstable or shell-rendered
5. Return grounded findings with source links and any uncertainty called out

**Claude Code operator shortcut:**
When the local `sf-docs` helper scripts are installed, prefer the built-in retrieval command over ad-hoc search-engine probing:

```bash
python3 ~/.claude/skills/sf-docs/scripts/cli.py retrieve           --query "<user question>"           --mode salesforce_aware           --live-scrape
```

For hard `help.salesforce.com` questions, this command applies the local Salesforce-aware retrieval flow, including targeted Help article discovery and browser-based rendering.

### Runtime Detection

`sf-docs` should detect **local corpus readiness at runtime**, not rely on installer choices.

Use this detection order:
1. Check whether a local Salesforce docs corpus exists
2. Check whether normalized markdown artifacts exist under the corpus root
3. If the local corpus is populated, use **local-first state**
4. Otherwise, use **Salesforce-aware retrieval state**

> Reference: [references/local-corpus-layout.md](references/local-corpus-layout.md)

---

## Local Artifact Acceptance Rules

Treat local artifacts as **weak** and fall back when any of the following happen:

- No relevant local artifacts are available
- The likely guide is clearly from the wrong Salesforce family or product area
- The exact concept, API name, CLI command, or error term requested is missing
- The local content is too fragmentary to answer confidently
- The local corpus appears stale for an obviously release-sensitive question

> **Rule**: Prefer a reliable Salesforce-specific fallback over confidently answering from a poor local hit.

---

## Salesforce Documentation Retrieval Playbook

### 1. Identify the Doc Family First

Classify the request before searching:

| Family | Typical Sources | Use For |
|--------|------------------|---------|
| **Developer Docs** | `developer.salesforce.com/docs/...` | Apex, APIs, LWC, metadata, Agentforce developer docs |
| **Salesforce Help** | `help.salesforce.com/...` | Setup UI steps, admin guides, feature configuration |
| **Platform Guides** | `developer.salesforce.com/docs/platform/...` | Newer guide-style docs with cleaner URLs |
| **Atlas / Legacy Guides** | `developer.salesforce.com/docs/atlas.en-us.*` | Older but still official guide and reference material |
| **Official PDFs** | `resources.docs.salesforce.com/...pdf/...` | Large guide bundles, stable offline extraction |

### 2. Prefer Exact Guide Paths Over Homepage Search

Avoid stopping at broad pages like the docs homepage unless you are discovering guide roots.

Instead, resolve toward:
- A specific guide root
- A specific article or page
- A guide PDF when page-level retrieval is unstable

### 3. Retrieval Patterns for `developer.salesforce.com`

Use these patterns deliberately:

- **Modern platform guide**: `developer.salesforce.com/docs/platform/...`
- **Legacy Atlas guide**: `developer.salesforce.com/docs/atlas.en-us.<book>.meta/...`
- **Guide PDF candidate**: derive `<book>` and try the matching official PDF URL

When an HTML page fails because of JavaScript rendering, shell content, or soft errors, try:
1. the guide root
2. the legacy Atlas variant if known
3. the official PDF

### 4. Retrieval Patterns for `help.salesforce.com`

Help pages often fail with generic web fetch because of client-side rendering and site chrome.

Use this approach:
- Prefer exact `help.salesforce.com/s/articleView?id=...` URLs or article identifiers when available
- If you only have a product/topic query, start from a targeted official hub and discover linked Help articles from there
  - Agentforce queries: start from the Agentforce developer guide and follow linked Help articles
  - Messaging / Enhanced Web Chat queries: start from the Enhanced Web Chat docs or landing Help article, then follow one hop to child setup/security articles
- Expect navigation shell noise and incomplete body extraction
- Focus on retrieving the actual article body, not the rendered header/footer shell
- Reject shell or soft-404 pages such as "We looked high and low but couldn't find that page"
- Cross-check titles, product area, and article body before trusting a result

### 5. PDFs Are a Valid Official Fallback

Use PDFs when:
- The guide has a stable official PDF
- HTML extraction is inconsistent
- A long-form developer guide is easier to search locally after normalization

PDFs may be stored **locally** for reuse, but should **not** be committed into the public repo.

---

## Answer Requirements

When using `sf-docs`, answers should include:

1. **Source type** — local normalized markdown, local scrape artifact, official HTML page, or official PDF
2. **Guide/article name**
3. **Exact official URL**
4. **Any retrieval caveat** — for example, if browser scraping was needed or if the content appeared partially rendered

If the evidence is weak, say so plainly.

---

## Cross-Skill Integration

| Skill | How `sf-docs` Helps |
|-------|----------------------|
| `sf-ai-agentforce` | Find Agentforce, PromptTemplate, Models API, and setup docs |
| `sf-ai-agentscript` | Find Agent Script syntax, CLI, and reasoning engine docs |
| `sf-apex` | Find Apex language and reference docs |
| `sf-lwc` | Find LWC guides, component references, and wire docs |
| `sf-integration` | Find REST, SOAP, Named Credential, and auth docs |
| `sf-deploy` | Find CLI, deployment, packaging, and metadata references |

**Delegation rule**: If another skill needs authoritative Salesforce documentation, it should use `sf-docs` as the retrieval layer rather than improvising generic web search.

---

## Local Storage Policy

- `sf-docs` is part of the core skill suite
- There is **no external local index dependency**
- Downloaded PDFs, scraped markdown, manifests, and diagnostics should live on the **user's machine**
- Official Salesforce docs content should **not** be stored in this public Git repository

### Default Local Corpus Layout

Use a stable local root such as:

```text
~/.sf-docs/
```

Recommended structure:
- `~/.sf-docs/manifest/` — discovery manifests and sync status
- `~/.sf-docs/raw/pdf/` — downloaded official PDFs
- `~/.sf-docs/raw/html/` — optional raw HTML captures and browser scrape payloads
- `~/.sf-docs/normalized/md/` — canonical markdown corpus used for local-first retrieval
- `~/.sf-docs/logs/` — optional diagnostics and fetch logs

> Full reference: [references/local-corpus-layout.md](references/local-corpus-layout.md)

---

## First-Version Behavior

The initial implementation should optimize for correctness and operational simplicity:

1. Local-first when a useful corpus exists
2. Sequential fallback to Salesforce-aware retrieval
3. Targeted retrieval, not broad crawling, during normal lookups
4. Grounded responses with official source links

### Query-Time Runtime Flow

1. Detect local corpus availability
2. Inspect the most likely local artifacts first
3. Evaluate evidence quality
4. On weak/missing evidence, use Salesforce-specific HTML/PDF fallback
5. Answer with source grounding and retrieval caveats when needed

> Full runtime guide: [references/runtime-workflow.md](references/runtime-workflow.md)

---

## Success Criteria

`sf-docs` is successful when it does the following better than generic web search:

- Finds the right Salesforce page or PDF more often
- Avoids failed fetches on `help.salesforce.com`
- Reduces hallucinations by grounding on official sources
- Improves the documentation quality available to the rest of the `sf-*` skills

---

## References

| Document | Purpose |
|----------|---------|
| [references/local-corpus-layout.md](references/local-corpus-layout.md) | Local-only corpus structure and runtime detection rules |
| [references/discovery-manifest.md](references/discovery-manifest.md) | Guide discovery manifest schema, mixed doc family handling, and HTML vs PDF policy |
| [references/local-retrieval.md](references/local-retrieval.md) | Local artifact retrieval strategy and acceptance rules |
| [references/runtime-workflow.md](references/runtime-workflow.md) | Query-time flow, fallback rules, sync separation, and local persistence policy |
| [references/ingestion-workflow.md](references/ingestion-workflow.md) | Targeted HTML/PDF fetch and normalization workflow |
| [references/salesforce-scraper-techniques.md](references/salesforce-scraper-techniques.md) | Salesforce-aware browser extraction techniques, Shadow DOM handling, and PDF fallback rationale |
| [references/pilot-scope.md](references/pilot-scope.md) | Initial guide scope for v1 ingestion |
| [references/benchmark-protocol.md](references/benchmark-protocol.md) | Local-first benchmark and wrong-guide rejection protocol |
| [references/cli-workflow.md](references/cli-workflow.md) | Unified CLI workflow for discover, sync, diagnose, retrieve, and benchmark scoring |
| [references/implementation-order.md](references/implementation-order.md) | Recommended v1 execution order |
| [references/final-architecture.md](references/final-architecture.md) | Final architectural recommendation |

## Assets & Scripts

| File | Purpose |
|------|---------|
| [assets/discovery-manifest.seed.json](assets/discovery-manifest.seed.json) | Starter guide manifest seed |
| [assets/retrieval-benchmark.json](assets/retrieval-benchmark.json) | Expanded core retrieval benchmark cases for exact identifiers, guide routing, and evidence grounding |
| [assets/retrieval-benchmark.results-template.json](assets/retrieval-benchmark.results-template.json) | Template for recording local-first benchmark outcomes |
| [assets/retrieval-benchmark.robustness.json](assets/retrieval-benchmark.robustness.json) | Negative / wrong-guide rejection benchmark for hardening fallback behavior |
| [assets/retrieval-benchmark.robustness.results-template.json](assets/retrieval-benchmark.robustness.results-template.json) | Template for recording robustness benchmark outcomes |
| [scripts/cli.py](scripts/cli.py) | Unified sf-docs CLI for discover, sync, status, diagnose, retrieve, and benchmarking |
| [scripts/discover_salesforce_docs.py](scripts/discover_salesforce_docs.py) | Enrich guide seeds into a discovery manifest and optionally verify PDF candidates |
| [scripts/salesforce_dom_scraper.mjs](scripts/salesforce_dom_scraper.mjs) | Salesforce-aware browser scraper with Shadow DOM, legacy doc container, iframe, and help-page heuristics |
| [scripts/sync_sf_docs.py](scripts/sync_sf_docs.py) | Fetch targeted HTML/PDF sources into the local corpus and normalize them into markdown |
| [scripts/sf_docs_runtime.py](scripts/sf_docs_runtime.py) | Detect corpus readiness, build sequential lookup plans, and evaluate evidence quality |
| [scripts/retrieve_sf_docs.py](scripts/retrieve_sf_docs.py) | End-to-end local-first retrieval execution with Salesforce-aware fallback |
| [scripts/run_retrieval_benchmark.py](scripts/run_retrieval_benchmark.py) | Execute the benchmark cases through the local-first retrieval mode |
| [scripts/score_retrieval_benchmark.py](scripts/score_retrieval_benchmark.py) | Score benchmark results |

---

## License

MIT License. See LICENSE file in the repo root.
Copyright (c) 2024–2026 Jag Valaiyapathy
