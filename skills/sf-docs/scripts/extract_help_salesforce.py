#!/usr/bin/env python3
"""
Extract article content from help.salesforce.com using a real browser, deep shadow DOM
traversal, and Salesforce Help-specific heuristics.

Why this exists:
- help.salesforce.com is heavily client-rendered
- the real article body often lives inside custom elements and shadow roots
- naive HTML fetching often returns shell text like "Loading", "Sorry to interrupt",
  or CSS/runtime error wrappers instead of the actual documentation

This script:
- renders the page with Playwright
- waits for the Help article app to hydrate
- traverses nested shadow roots
- prioritizes Salesforce Help article-body containers such as `.slds-text-longform`
- returns structured JSON with the extracted article text and official child links

Example:
  python3 skills/sf-docs/scripts/extract_help_salesforce.py \
    --url "https://help.salesforce.com/s/articleView?id=service.miaw_security.htm&type=5"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

SHELL_TOKENS = [
    "loading",
    "sorry to interrupt",
    "css error",
    "enable javascript",
    "sign in",
    "cookie preferences",
    "we looked high and low",
    "couldn't find that page",
    "404 error",
]

NOISE_LINES = {
    "table of contents",
    "close",
    "search",
}


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\r", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def cleanup_help_text(text: str, title: str = "") -> str:
    text = normalize_text(text)
    if not text:
        return text

    lines = [line.strip() for line in text.splitlines()]
    cleaned: List[str] = []
    for idx, line in enumerate(lines):
        if not line:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue

        lowered = line.lower().strip()
        if lowered in NOISE_LINES:
            continue
        if lowered.startswith("you are here:"):
            continue
        if lowered in {"salesforce help", "docs"}:
            continue

        if title and "|" in line:
            title_pos = lowered.find(title.lower())
            if title_pos >= 0:
                line = line[title_pos:].strip()
                lowered = line.lower()

        if idx == 0 and title and line.isupper() and len(line) < 120:
            continue

        cleaned.append(line)

    text = "\n".join(cleaned)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def looks_like_shell(title: str, text: str) -> bool:
    haystack = f"{title}\n{text}".lower()
    return any(token in haystack for token in SHELL_TOKENS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract article text from help.salesforce.com")
    parser.add_argument("--url", required=True, help="help.salesforce.com article URL")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds (default: 60)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser.parse_args()


def validate_url(url: str) -> None:
    host = (urlparse(url).hostname or "").lower()
    if not host.endswith("help.salesforce.com"):
        raise SystemExit(f"URL must be on help.salesforce.com: {url}")


def extract(url: str, timeout_seconds: int) -> Dict[str, Any]:
    timeout_ms = timeout_seconds * 1000

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT, viewport={"width": 1440, "height": 1400})

        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            http_status = response.status if response else None

            # Let the client app boot, then wait for the article shell to hydrate.
            page.wait_for_timeout(1500)
            try:
                page.wait_for_function(
                    r"""
                    () => {
                      const hosts = Array.from(document.querySelectorAll('c-hc-article-viewer, c-hc-documentation-article'));
                      return hosts.some(el => ((el.innerText || '').trim().length > 400));
                    }
                    """,
                    timeout=min(timeout_ms, 30000),
                )
            except PlaywrightTimeoutError:
                # Continue anyway — some pages still expose enough content after network idle.
                pass

            page.wait_for_load_state("networkidle", timeout=timeout_ms)
            page.wait_for_timeout(1000)

            payload = page.evaluate(
                r"""
                () => {
                  function normalize(text) {
                    return String(text || '')
                      .replace(/\u00a0/g, ' ')
                      .replace(/\r/g, '')
                      .replace(/\n{3,}/g, '\n\n')
                      .trim();
                  }

                  function isVisible(el) {
                    if (!el || !el.getBoundingClientRect) return false;
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
                  }

                  function allRoots() {
                    const roots = [document];
                    const queue = [document];
                    while (queue.length) {
                      const current = queue.shift();
                      if (!current || !current.querySelectorAll) continue;
                      const elements = current.querySelectorAll('*');
                      for (const el of elements) {
                        if (el.shadowRoot) {
                          roots.push(el.shadowRoot);
                          queue.push(el.shadowRoot);
                        }
                      }
                    }
                    return roots;
                  }

                  function deepQueryAll(selector) {
                    const results = [];
                    const seen = new Set();
                    for (const root of allRoots()) {
                      if (!root.querySelectorAll) continue;
                      for (const el of root.querySelectorAll(selector)) {
                        if (!seen.has(el)) {
                          seen.add(el);
                          results.push(el);
                        }
                      }
                    }
                    return results;
                  }

                  function collectLinks(scope) {
                    const urls = new Set();
                    const nodes = scope && scope.querySelectorAll ? scope.querySelectorAll('a[href]') : [];
                    for (const a of nodes) {
                      const href = a.href || a.getAttribute('href') || '';
                      if (!href) continue;
                      if (href.startsWith('javascript:') || href.startsWith('mailto:')) continue;
                      urls.add(href);
                    }
                    return Array.from(urls);
                  }

                  const title = document.title || normalize(document.querySelector('title')?.innerText || 'Untitled');
                  const helpArticleId = new URL(window.location.href).searchParams.get('id');
                  const childLinks = new Set();
                  for (const root of allRoots()) {
                    for (const link of collectLinks(root)) childLinks.add(link);
                  }

                  const selectorConfigs = [
                    { selector: '#content.slds-text-longform', strategy: 'help-longform-id', base: 300 },
                    { selector: '.slds-text-longform#content', strategy: 'help-longform-id', base: 300 },
                    { selector: '.slds-text-longform', strategy: 'help-longform', base: 260 },
                    { selector: 'c-hc-documentation-article', strategy: 'help-article-host', base: 160 },
                    { selector: 'article', strategy: 'article', base: 120 },
                    { selector: 'main', strategy: 'main', base: 100 },
                    { selector: 'doc-content-layout', strategy: 'legacy-doc-layout', base: 90 },
                    { selector: 'doc-xml-content', strategy: 'legacy-doc-xml', base: 90 },
                    { selector: 'doc-amf-reference .markdown-content', strategy: 'legacy-amf-markdown', base: 90 },
                  ];

                  const candidates = [];
                  for (const cfg of selectorConfigs) {
                    const nodes = deepQueryAll(cfg.selector);
                    for (const node of nodes) {
                      if (!isVisible(node)) continue;
                      const text = normalize(node.innerText || node.textContent || '');
                      if (text.length < 200) continue;
                      let score = cfg.base + Math.min(text.length, 5000) / 25;
                      const lowered = text.toLowerCase();
                      if (lowered.includes('table of contents')) score -= 80;
                      if (lowered.includes('sorry to interrupt')) score -= 500;
                      if (lowered.includes('css error')) score -= 500;
                      if (lowered.includes(title.toLowerCase())) score += 40;
                      candidates.push({
                        strategy: cfg.strategy,
                        selector: cfg.selector,
                        score,
                        text,
                        html: (node.innerHTML || '').slice(0, 4000),
                        links: collectLinks(node).slice(0, 200),
                      });
                    }
                  }

                  // Last-resort body fallback.
                  const bodyText = normalize(document.body?.innerText || '');
                  if (bodyText.length >= 200) {
                    candidates.push({
                      strategy: 'body',
                      selector: 'body',
                      score: Math.min(bodyText.length, 5000) / 50,
                      text: bodyText,
                      html: (document.body?.innerHTML || '').slice(0, 4000),
                      links: Array.from(childLinks).slice(0, 200),
                    });
                  }

                  candidates.sort((a, b) => b.score - a.score);
                  const best = candidates[0] || null;

                  return {
                    url: window.location.href,
                    title,
                    helpArticleId,
                    httpStatus: null,
                    strategy: best ? best.strategy : 'none',
                    selector: best ? best.selector : null,
                    text: best ? best.text : '',
                    htmlExcerpt: best ? best.html : '',
                    contentLinks: best ? best.links : [],
                    childLinks: Array.from(childLinks).slice(0, 200),
                    candidateCount: candidates.length,
                  };
                }
                """
            )
            payload["httpStatus"] = http_status

            cleaned_text = cleanup_help_text(payload.get("text", ""), payload.get("title", ""))
            likely_shell = looks_like_shell(payload.get("title", ""), cleaned_text)
            ok = bool(cleaned_text) and len(cleaned_text) >= 400 and not likely_shell

            return {
                "ok": ok,
                "url": payload.get("url", url),
                "httpStatus": payload.get("httpStatus"),
                "title": payload.get("title") or "Untitled",
                "helpArticleId": payload.get("helpArticleId"),
                "strategy": payload.get("strategy"),
                "selector": payload.get("selector"),
                "likelyShell": likely_shell,
                "text": cleaned_text,
                "contentLinks": payload.get("contentLinks", []),
                "childLinks": payload.get("childLinks", []),
                "candidateCount": payload.get("candidateCount", 0),
            }
        finally:
            page.close()
            browser.close()


def main() -> int:
    args = parse_args()
    validate_url(args.url)
    result = extract(args.url, args.timeout)
    dump = json.dumps(result, indent=2 if args.pretty else None)
    print(dump)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
