# sf-docs Local Corpus Layout

`sf-docs` stores retrieved Salesforce documentation **locally on the user's machine**. Nothing in this layout should be committed into the public `sf-skills` repository.

## Default Root

```text
~/.sf-docs/
```

## Recommended Layout

```text
~/.sf-docs/
├── manifest/
│   ├── guides.json            # discovered guide roots and metadata
│   └── fetch-status.json      # optional sync status
├── raw/
│   ├── pdf/                   # downloaded official PDFs
│   └── html/                  # raw HTML captures + browser scrape payloads
├── normalized/
│   └── md/                    # canonical markdown corpus for local-first retrieval
│       ├── apexcode/
│       ├── api_rest/
│       ├── lwc/
│       └── ...
└── logs/
    └── fetch.log              # optional operational logs
```

## Canonical Content Rules

- **Markdown is the canonical local retrieval format**
- PDFs may be retained in `raw/pdf/` for provenance and reprocessing
- Page-level markdown should be preferred when available and clean
- Each normalized markdown document should preserve:
  - title
  - source URL
  - guide/book id when known
  - doc family (`atlas`, `platform`, `help`, `pdf`)
  - fetch timestamp

## Runtime Detection Rules

When `sf-docs` runs, determine state in this order:

1. Does a local Salesforce docs corpus exist under `~/.sf-docs/` (or configured equivalent)?
2. Does `~/.sf-docs/normalized/md/` contain markdown artifacts?
3. If yes, use **local-first** retrieval
4. Otherwise, use **Salesforce-aware** retrieval

## Operational Guidance

- Use a **single local root** so future sync commands are predictable
- Keep official downloaded content **outside the git repo**
- Avoid storing transient browser shell output as canonical docs
- Prefer guide-organized paths so local artifact routing remains predictable
