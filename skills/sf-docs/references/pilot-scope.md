# sf-docs Pilot Ingestion Scope

This document defines the **initial implementation scope** for `sf-docs`.

## Goal

Do **not** attempt to ingest the entirety of Salesforce public documentation in v1.

Instead, start with a compact, high-value corpus that:

- covers the most common developer workflows
- covers the failure modes already observed with generic web fetch
- provides a realistic benchmark for local-first retrieval

## Pilot Guide Set

The recommended v1 pilot scope is the guide set seeded in:

- [assets/discovery-manifest.seed.json](../assets/discovery-manifest.seed.json)

### Included Guides

| Slug | Title | Family | Why It Is In Scope |
|------|-------|--------|--------------------|
| `apexcode` | Apex Developer Guide | `atlas` | Core Apex development and server-side logic |
| `apexref` | Apex Reference Guide | `atlas` | Exact class/method/API lookups |
| `api_rest` | REST API Developer Guide | `atlas` | Integration, auth, and API endpoint work |
| `api_meta` | Metadata API Developer Guide | `atlas` | Deployment and metadata automation |
| `object_reference` | Object Reference for Salesforce Platform | `atlas` | Standard object and field reference lookups |
| `lwc` | Lightning Web Components Developer Guide | `platform` | UI and modern component development |
| `agentforce-guide` | Agentforce Developer Documentation | `platform` | High-value AI/Agentforce lookup failures |

## Why This Scope First

This pilot covers the highest-value developer queries while keeping the first corpus manageable.

It intentionally mixes:

- legacy Atlas guides
- modern platform guides
- AI/Agentforce docs
- API/reference-heavy material

That mix is enough to validate:

- mixed-family retrieval behavior
- HTML-vs-PDF decisions
- local artifact usefulness
- fallback logic when pages are unstable

## Explicitly Out of Scope for v1

These are **not** required for the first implementation milestone:

- all of Salesforce Help
- full product-cloud coverage
- exhaustive setup/admin docs
- every guide listed under `developer.salesforce.com/docs#browse`
- aggressive continuous crawling of the whole docs site
- introducing a new indexing dependency

## Expansion Order After Pilot

Once the pilot benchmark is healthy, expand in this order:

1. `help.salesforce.com` articles for common setup/admin lookups
2. additional API guides (`SOAP`, `Tooling`, `Bulk`, `SOQL/SOSL`)
3. deployment and CLI-related guides
4. broader Agentforce/AI guide coverage
5. wider platform/product families

## Success Gate for Expansion

Do not expand breadth until the pilot corpus demonstrates:

- high answer grounding quality
- reliable fallback behavior
- acceptable query latency
- clear source attribution
- materially better results than naive web lookup
