#!/usr/bin/env python3
"""
Build or enrich an sf-docs discovery manifest.

This script is intentionally stdlib-only and focuses on manifest generation,
family classification, PDF candidate derivation, and optional PDF verification.
It does not scrape full document bodies.

Usage:
  python3 discover_salesforce_docs.py \
    --seed skills/sf-docs/assets/discovery-manifest.seed.json \
    --output /tmp/guides.json

  python3 discover_salesforce_docs.py \
    --seed skills/sf-docs/assets/discovery-manifest.seed.json \
    --output /tmp/guides.json \
    --verify-pdf
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PDF_PATTERN = "https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/{book_id}.pdf"
PDF_OVERRIDES = {
    "apexcode": [
        "https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_apex_developer_guide.pdf",
    ],
    "apexref": [
        "https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_apex_reference_guide.pdf",
    ],
}


@dataclass
class PdfCheckResult:
    verified: bool
    status: Optional[int]
    url: Optional[str]
    error: Optional[str] = None


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def classify_family(url: str) -> str:
    if "help.salesforce.com" in url:
        return "help"
    if "/docs/platform/" in url or "/docs/ai/" in url:
        return "platform"
    if "/docs/atlas.en-us." in url:
        return "atlas"
    if "resources.docs.salesforce.com" in url and url.lower().endswith(".pdf"):
        return "pdf"
    return "unknown"


def derive_book_id(url: str) -> Optional[str]:
    atlas_match = re.search(r"/docs/atlas\.en-us\.([^.]+)\.meta/", url)
    if atlas_match:
        return atlas_match.group(1)

    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if not parts:
        return None

    # Heuristic mappings for modern guides lacking atlas book ids.
    if parts[:3] == ["docs", "platform", "lwc"]:
        return "lwc"
    if parts[:3] == ["docs", "ai", "agentforce"]:
        return "agentforce-guide"

    return None


def derive_product(entry: Dict[str, Any]) -> str:
    title = (entry.get("title") or "").lower()
    url = entry.get("root_url") or ""
    if "agentforce" in title or "/docs/ai/agentforce/" in url:
        return "agentforce"
    if "apex" in title:
        return "apex"
    if "rest api" in title:
        return "api"
    if "metadata api" in title:
        return "metadata"
    if "object reference" in title:
        return "platform"
    if "lightning web components" in title or "/docs/platform/lwc/" in url:
        return "lwc"
    return "platform"


def default_normalized_dir(slug: str) -> str:
    return f"~/.sf-docs/normalized/md/{slug}"


def default_raw_pdf_path(slug: str) -> str:
    return f"~/.sf-docs/raw/pdf/{slug}.pdf"


def pdf_candidates(book_id: Optional[str]) -> List[str]:
    if not book_id:
        return []
    if book_id in PDF_OVERRIDES:
        return PDF_OVERRIDES[book_id]
    return [PDF_PATTERN.format(book_id=book_id)]


def verify_url(url: str, timeout: int = 15) -> PdfCheckResult:
    # Some CDNs are inconsistent with HEAD; try HEAD first, then GET.
    for method in ("HEAD", "GET"):
        request = Request(url, method=method)
        try:
            with urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", None) or response.getcode()
                if status and 200 <= status < 300:
                    return PdfCheckResult(True, status, url)
        except HTTPError as e:
            if e.code == 405 and method == "HEAD":
                continue
            return PdfCheckResult(False, e.code, None, f"HTTP {e.code}: {e.reason}")
        except URLError as e:
            return PdfCheckResult(False, None, None, str(e.reason))
        except Exception as e:  # pragma: no cover - defensive
            return PdfCheckResult(False, None, None, str(e))
    return PdfCheckResult(False, None, None, "No successful response")


def enrich_entry(entry: Dict[str, Any], verify_pdf: bool = False) -> Dict[str, Any]:
    root_url = entry["root_url"]
    slug = entry.get("slug") or derive_book_id(root_url) or re.sub(r"[^a-z0-9-]+", "-", (entry.get("title") or "guide").lower()).strip("-")
    family = entry.get("family") or classify_family(root_url)
    book_id = entry.get("book_id") or derive_book_id(root_url)
    product = entry.get("product") or derive_product({**entry, "root_url": root_url})
    candidates = entry.get("pdf_candidates") or pdf_candidates(book_id)
    html_preferred = entry.get("html_preferred")
    if html_preferred is None:
        html_preferred = family != "pdf"

    enriched: Dict[str, Any] = {
        "slug": slug,
        "title": entry.get("title", slug),
        "family": family,
        "root_url": root_url,
        "book_id": book_id,
        "product": product,
        "html_preferred": html_preferred,
        "pdf_candidates": candidates,
        "pdf_verified": entry.get("pdf_verified"),
        "normalized_dir": entry.get("normalized_dir") or default_normalized_dir(slug),
        "raw_pdf_path": entry.get("raw_pdf_path") or default_raw_pdf_path(slug),
        "status": {
            "discovered": True,
            "fetched": bool(entry.get("status", {}).get("fetched", False)),
            "normalized": bool(entry.get("status", {}).get("normalized", False)),
            "cached": bool(entry.get("status", {}).get("cached", False)),
        },
        "notes": list(entry.get("notes", [])),
    }

    if verify_pdf and candidates:
        checks: List[Dict[str, Any]] = []
        verified_url: Optional[str] = None
        for candidate in candidates:
            result = verify_url(candidate)
            checks.append({
                "candidate": candidate,
                "verified": result.verified,
                "status": result.status,
                "error": result.error,
            })
            if result.verified and verified_url is None:
                verified_url = result.url
        enriched["pdf_checks"] = checks
        enriched["pdf_verified"] = verified_url

    return enriched


def load_seed(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def build_manifest(seed: Dict[str, Any], verify_pdf: bool = False) -> Dict[str, Any]:
    guides = seed.get("guides", [])
    enriched = [enrich_entry(g, verify_pdf=verify_pdf) for g in guides]
    return {
        "version": seed.get("version", 1),
        "generated_at": now_iso(),
        "root": seed.get("root", "https://developer.salesforce.com/docs#browse"),
        "guides": enriched,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or enrich an sf-docs discovery manifest")
    parser.add_argument("--seed", type=Path, required=True, help="Seed manifest JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output manifest JSON")
    parser.add_argument("--verify-pdf", action="store_true", help="Verify candidate PDF URLs")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print output JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seed = load_seed(args.seed)
    manifest = build_manifest(seed, verify_pdf=args.verify_pdf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.pretty:
        args.output.write_text(json.dumps(manifest, indent=2) + "\n")
    else:
        args.output.write_text(json.dumps(manifest) + "\n")
    print(f"Wrote manifest: {args.output}")
    print(f"Guides: {len(manifest.get('guides', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
