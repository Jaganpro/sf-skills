#!/usr/bin/env python3
"""
Sync a local sf-docs corpus from a discovery manifest.

Features:
- create the recommended local corpus layout
- optionally verify/download official guide PDFs
- optionally download raw HTML guide roots
- normalize HTML/PDF sources into markdown with provenance frontmatter
- update a local manifest with fetch/normalize status

This script is intentionally conservative:
- it performs targeted guide fetches only
- it does not broad-crawl the Salesforce docs universe
- it keeps all downloaded content local to the user machine

Examples:
  python3 sync_sf_docs.py \
    --manifest skills/sf-docs/assets/discovery-manifest.seed.json \
    --corpus-root ~/.sf-docs \
    --download-pdf --normalize

  python3 sync_sf_docs.py \
    --manifest ~/.sf-docs/manifest/guides.json \
    --slug apexcode --slug api_rest \
    --download-pdf --download-html --normalize
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_CORPUS_ROOT = Path.home() / ".sf-docs"
USER_AGENT = "sf-docs-sync/0.1 (+https://github.com/Jaganpro/sf-skills)"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class TextExtractor(HTMLParser):
    """Very lightweight HTML → text extractor for fallback normalization."""

    BLOCK_TAGS = {
        "p", "div", "section", "article", "main", "header", "footer", "aside",
        "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol", "pre", "table",
        "tr", "td", "th", "br",
    }

    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1
            return
        if self.skip_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth > 0:
            return
        text = data.strip()
        if text:
            self.parts.append(text)
            self.parts.append("\n")

    def get_text(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def ensure_layout(corpus_root: Path) -> Dict[str, Path]:
    dirs = {
        "root": corpus_root,
        "manifest": corpus_root / "manifest",
        "raw_pdf": corpus_root / "raw" / "pdf",
        "raw_html": corpus_root / "raw" / "html",
        "normalized": corpus_root / "normalized" / "md",
        "logs": corpus_root / "logs",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def fetch_url(url: str, timeout: int = 30) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def run_browser_scraper(url: str, timeout: int = 45) -> Tuple[bool, Dict[str, Any]]:
    script = Path(__file__).resolve().parent / "salesforce_dom_scraper.mjs"
    if not shutil.which("node"):
        return False, {"error": "node not found for browser scraper"}
    if not script.exists():
        return False, {"error": f"scraper script not found: {script}"}

    try:
        result = subprocess.run(
            ["node", str(script), "--url", url, "--timeout", str(timeout * 1000)],
            capture_output=True,
            text=True,
            timeout=timeout + 15,
        )
    except subprocess.TimeoutExpired:
        return False, {"error": "browser scraper timed out"}
    except Exception as e:
        return False, {"error": str(e)}

    payload_text = (result.stdout or result.stderr or "").strip()
    if not payload_text:
        return False, {"error": "browser scraper returned no output"}

    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        return False, {"error": f"browser scraper returned invalid JSON: {payload_text[:300]}"}

    return bool(payload.get("ok")), payload


def verify_url(url: str, timeout: int = 15) -> Tuple[bool, Optional[int], Optional[str]]:
    for method in ("HEAD", "GET"):
        req = Request(url, headers={"User-Agent": USER_AGENT}, method=method)
        try:
            with urlopen(req, timeout=timeout) as resp:
                code = getattr(resp, "status", None) or resp.getcode()
                if 200 <= int(code) < 300:
                    return True, int(code), None
        except HTTPError as e:
            if method == "HEAD" and e.code == 405:
                continue
            return False, e.code, f"HTTP {e.code}: {e.reason}"
        except URLError as e:
            return False, None, str(e.reason)
        except Exception as e:  # pragma: no cover
            return False, None, str(e)
    return False, None, "No successful response"


def sanitize_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", text.lower()).strip("-")


def html_text(raw_html: str) -> str:
    parser = TextExtractor()
    parser.feed(raw_html)
    return parser.get_text()


def html_looks_useful(text: str) -> bool:
    if len(text) < 800:
        return False
    lowered = text.lower()
    bad_signals = [
        "enable javascript",
        "sorry to interrupt",
        "sign in",
        "cookie preferences",
        "skip to main content",
    ]
    return not any(signal in lowered for signal in bad_signals)


def detect_pdf_text_tool() -> Optional[str]:
    for candidate in ("pdftotext",):
        if shutil.which(candidate):
            return candidate
    return None


def extract_pdf_text(pdf_path: Path) -> Tuple[Optional[str], str]:
    tool = detect_pdf_text_tool()
    if tool:
        txt_path = pdf_path.with_suffix(".txt")
        try:
            subprocess.run([tool, str(pdf_path), str(txt_path)], check=True, capture_output=True, text=True)
            text = txt_path.read_text(errors="ignore")
            txt_path.unlink(missing_ok=True)
            if text.strip():
                return text.strip(), f"extracted with {tool}"
        except Exception as e:
            return None, f"{tool} failed: {e}"

    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(pdf_path))
        chunks = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                chunks.append(page_text)
        text = "\n\n".join(chunks).strip()
        if text:
            return text, "extracted with pypdf"
        return None, "pypdf produced no text"
    except Exception as e:
        return None, f"no PDF extractor available ({e})"


def frontmatter(meta: Dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in meta.items():
        if value is None:
            continue
        text = str(value).replace("\n", " ").strip()
        lines.append(f"{key}: {json.dumps(text)}")
    lines.append("---")
    return "\n".join(lines)


def write_markdown(path: Path, meta: Dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{frontmatter(meta)}\n\n{body.strip()}\n")


def load_manifest(path: Path) -> Dict[str, Any]:
    return read_json(path)


def filtered_guides(manifest: Dict[str, Any], slugs: List[str]) -> List[Dict[str, Any]]:
    guides = manifest.get("guides", [])
    if not slugs:
        return guides
    wanted = set(slugs)
    return [g for g in guides if g.get("slug") in wanted]


def update_local_manifest(manifest: Dict[str, Any], paths: Dict[str, Path]) -> Path:
    target = paths["manifest"] / "guides.json"
    write_json(target, manifest)
    return target


def normalize_from_html(guide: Dict[str, Any], html_path: Path, normalized_path: Path) -> Tuple[bool, str]:
    raw = html_path.read_text(errors="ignore")
    text = html_text(raw)
    if not html_looks_useful(text):
        return False, "HTML did not look useful enough to normalize"

    body = f"# {guide.get('title', guide.get('slug'))}\n\n{text}"
    meta = {
        "title": guide.get("title"),
        "source_url": guide.get("root_url"),
        "guide_slug": guide.get("slug"),
        "family": guide.get("family"),
        "book_id": guide.get("book_id"),
        "fetched_at": now_iso(),
        "source_type": "html",
    }
    write_markdown(normalized_path, meta, body)
    return True, "normalized from html"


def normalize_from_scrape_json(guide: Dict[str, Any], scrape_path: Path, normalized_path: Path) -> Tuple[bool, str]:
    payload = read_json(scrape_path)
    text = str(payload.get("text") or "").strip()
    if not text or payload.get("likelyShell"):
        return False, "browser scrape looked like shell/noise or returned too little text"
    if len(text) < 500:
        return False, "browser scrape did not return enough text to normalize"

    body = f"# {payload.get('title') or guide.get('title', guide.get('slug'))}\n\n{text}"
    meta = {
        "title": payload.get("title") or guide.get("title"),
        "source_url": payload.get("url") or guide.get("root_url"),
        "guide_slug": guide.get("slug"),
        "family": guide.get("family"),
        "book_id": guide.get("book_id"),
        "fetched_at": now_iso(),
        "source_type": f"browser:{payload.get('strategy', 'unknown')}",
    }
    write_markdown(normalized_path, meta, body)
    return True, f"normalized from browser scrape ({payload.get('strategy', 'unknown')})"


def normalize_from_pdf(guide: Dict[str, Any], pdf_path: Path, normalized_path: Path) -> Tuple[bool, str]:
    text, note = extract_pdf_text(pdf_path)
    if not text:
        return False, note

    body = f"# {guide.get('title', guide.get('slug'))}\n\n{text}"
    meta = {
        "title": guide.get("title"),
        "source_url": guide.get("pdf_verified") or (guide.get("pdf_candidates") or [None])[0],
        "guide_slug": guide.get("slug"),
        "family": guide.get("family") or "pdf",
        "book_id": guide.get("book_id"),
        "fetched_at": now_iso(),
        "source_type": "pdf",
    }
    write_markdown(normalized_path, meta, body)
    return True, note


def sync_guide(guide: Dict[str, Any], paths: Dict[str, Path], download_pdf: bool,
               download_html: bool, normalize: bool, verify_pdf: bool,
               dry_run: bool, browser_scrape: bool) -> Dict[str, Any]:
    slug = guide.get("slug") or sanitize_slug(guide.get("title", "guide"))
    guide.setdefault("slug", slug)
    guide.setdefault("status", {"discovered": True, "fetched": False, "normalized": False, "cached": False})
    guide["status"].setdefault("cached", False)
    notes = list(guide.get("notes", []))

    pdf_path = paths["raw_pdf"] / f"{slug}.pdf"
    html_path = paths["raw_html"] / f"{slug}.html"
    scrape_path = paths["raw_html"] / f"{slug}.scrape.json"
    normalized_dir = paths["normalized"] / slug
    normalized_path = normalized_dir / "index.md"

    candidates = list(guide.get("pdf_candidates") or [])
    if verify_pdf and candidates:
        checks = []
        verified = None
        for candidate in candidates:
            ok, status, error = verify_url(candidate)
            checks.append({"candidate": candidate, "verified": ok, "status": status, "error": error})
            if ok and verified is None:
                verified = candidate
        guide["pdf_checks"] = checks
        guide["pdf_verified"] = verified

    pdf_source = guide.get("pdf_verified") or (candidates[0] if candidates else None)

    if download_pdf and pdf_source and not pdf_path.exists():
        if dry_run:
            notes.append(f"Would download PDF: {pdf_source}")
        else:
            try:
                pdf_bytes = fetch_url(pdf_source)
                pdf_path.write_bytes(pdf_bytes)
                guide["status"]["fetched"] = True
                notes.append(f"Downloaded PDF from {pdf_source}")
            except Exception as e:
                notes.append(f"PDF download failed: {e}")

    if download_html and guide.get("root_url"):
        if dry_run:
            if browser_scrape:
                notes.append(f"Would browser-scrape HTML: {guide['root_url']}")
            else:
                notes.append(f"Would download HTML: {guide['root_url']}")
        else:
            try:
                if browser_scrape:
                    ok, payload = run_browser_scraper(guide["root_url"])
                    if ok:
                        scrape_path.write_text(json.dumps(payload, indent=2) + "\n")
                        guide["status"]["fetched"] = True
                        notes.append(f"Browser-scraped HTML from {guide['root_url']} via {payload.get('strategy', 'unknown')}")
                        if payload.get("likelyShell"):
                            notes.append("Browser scraper flagged likely shell/noise content")
                    else:
                        notes.append(f"Browser scrape failed: {payload.get('error', 'unknown error')}")
                elif not html_path.exists():
                    html_bytes = fetch_url(guide["root_url"])
                    html_path.write_bytes(html_bytes)
                    guide["status"]["fetched"] = True
                    notes.append(f"Downloaded HTML from {guide['root_url']}")
            except Exception as e:
                notes.append(f"HTML download failed: {e}")

    if normalize:
        if dry_run:
            notes.append(f"Would normalize to {normalized_path}")
        else:
            normalized = False
            if guide.get("html_preferred", True) and scrape_path.exists():
                normalized, reason = normalize_from_scrape_json(guide, scrape_path, normalized_path)
                notes.append(reason)
            if not normalized and guide.get("html_preferred", True) and html_path.exists():
                normalized, reason = normalize_from_html(guide, html_path, normalized_path)
                notes.append(reason)
            if not normalized and pdf_path.exists():
                normalized, reason = normalize_from_pdf(guide, pdf_path, normalized_path)
                notes.append(reason)
            if normalized:
                guide["status"]["normalized"] = True
                guide["status"]["cached"] = True

    guide["raw_pdf_path"] = str(pdf_path)
    guide["raw_html_path"] = str(html_path)
    guide["raw_scrape_path"] = str(scrape_path)
    guide["normalized_dir"] = str(normalized_dir)
    guide["notes"] = notes
    return guide


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync a local sf-docs corpus from a manifest")
    parser.add_argument("--manifest", required=True, help="Input manifest JSON")
    parser.add_argument("--corpus-root", default=str(DEFAULT_CORPUS_ROOT), help="Local sf-docs corpus root")
    parser.add_argument("--slug", action="append", default=[], help="Guide slug to sync (repeatable)")
    parser.add_argument("--download-pdf", action="store_true", help="Download PDF candidates when available")
    parser.add_argument("--download-html", action="store_true", help="Download guide root HTML")
    parser.add_argument("--browser-scrape", action="store_true", help="Use Salesforce-aware browser scraping for HTML retrieval")
    parser.add_argument("--normalize", action="store_true", help="Normalize downloaded sources into markdown")
    parser.add_argument("--verify-pdf", action="store_true", help="Verify PDF candidates before download")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without modifying local corpus")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).expanduser()
    corpus_root = Path(args.corpus_root).expanduser()
    manifest = load_manifest(manifest_path)
    paths = ensure_layout(corpus_root)

    guides = filtered_guides(manifest, args.slug)
    updated = []
    for guide in guides:
        updated.append(
            sync_guide(
                guide,
                paths,
                download_pdf=args.download_pdf,
                download_html=args.download_html,
                normalize=args.normalize,
                verify_pdf=args.verify_pdf,
                dry_run=args.dry_run,
                browser_scrape=args.browser_scrape,
            )
        )

    manifest["generated_at"] = now_iso()
    if args.slug:
        updated_by_slug = {g["slug"]: g for g in updated}
        manifest["guides"] = [updated_by_slug.get(g.get("slug"), g) for g in manifest.get("guides", [])]
    else:
        manifest["guides"] = updated

    if not args.dry_run:
        local_manifest = update_local_manifest(manifest, paths)
        print(f"Updated local manifest: {local_manifest}")
    else:
        print("Dry run complete - no files written")

    print(f"Guides processed: {len(updated)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
