# sf-docs

Official Salesforce documentation retrieval guidance for `sf-skills`.

## What it is

`sf-docs` is now a **prompt-only skill**.

It gives a practical retrieval playbook for official Salesforce docs on the public web, especially when:
- `developer.salesforce.com` pages are JS-heavy
- `help.salesforce.com` pages return shell content
- the real answer is on a child page, not the guide homepage

## What it is not

This skill no longer includes:
- local corpus workflows
- indexing
- benchmark workflows
- any required helper CLI dependency
- PDF fallback guidance

## Use it for

- official Salesforce docs lookup
- hard-to-fetch Help articles
- Apex / API / LWC / Agentforce documentation grounding
- deciding when to follow child links from broad official guide pages
- rejecting weak results such as shells, landing pages, and third-party summaries

## Optional utility

A minimal helper script is available for hard `help.salesforce.com` pages:

```bash
python3 skills/sf-docs/scripts/extract_help_salesforce.py \
  --url "https://help.salesforce.com/s/articleView?id=service.miaw_security.htm&type=5" \
  --pretty
```

It uses Playwright, browser rendering, and deep shadow DOM traversal to extract the article body from Help pages.

## Key idea

Keep retrieval:
- **official-source-first**
- **HTML-only**
- **targeted**
- **child-link aware**
- **strict about exact concept matching**
