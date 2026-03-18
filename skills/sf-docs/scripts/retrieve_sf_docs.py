#!/usr/bin/env python3
"""
End-to-end sf-docs retrieval.

Modes:
- local_first: inspect local corpus artifacts first, then fall back to Salesforce-aware retrieval
- salesforce_aware: use Salesforce-aware retrieval flow directly
- auto: choose based on runtime status

Output is structured JSON for benchmarking and operator review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sf_docs_runtime import (  # type: ignore
    DEFAULT_CORPUS_ROOT,
    DEFAULT_MANIFEST,
    build_lookup_plan,
    build_query_signature,
    evaluate_text_evidence,
    normalize_query,
)
from sync_sf_docs import extract_pdf_text, fetch_url, read_json, run_browser_scraper  # type: ignore


HELP_ARTICLE_HINTS = {
    'agentforce': [
        'https://help.salesforce.com/s/articleView?id=ai.generative_ai.htm',
        'https://help.salesforce.com/s/articleView?id=sf.copilot_intro.htm&type=5',
    ],
    'generative ai': [
        'https://help.salesforce.com/s/articleView?id=ai.generative_ai.htm',
    ],
    'messaging': [
        'https://help.salesforce.com/s/articleView?id=service.miaw_intro_landing.htm',
    ],
    'enhanced web chat': [
        'https://help.salesforce.com/s/articleView?id=service.miaw_intro_landing.htm',
    ],
    'in-app and web': [
        'https://help.salesforce.com/s/articleView?id=service.miaw_intro_landing.htm',
    ],
}

HELP_DISCOVERY_SOURCES = {
    'agentforce': [
        'https://developer.salesforce.com/docs/ai/agentforce/guide/',
    ],
    'generative ai': [
        'https://developer.salesforce.com/docs/ai/agentforce/guide/',
    ],
    'messaging': [
        'https://developer.salesforce.com/docs/service/messaging-web/guide/',
    ],
    'enhanced web chat': [
        'https://developer.salesforce.com/docs/service/messaging-web/guide/',
    ],
    'in-app and web': [
        'https://developer.salesforce.com/docs/service/messaging-web/guide/',
    ],
}


def load_manifest(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def parse_frontmatter(md_text: str) -> Tuple[Dict[str, str], str]:
    if not md_text.startswith('---\n'):
        return {}, md_text
    parts = md_text.split('\n---\n', 1)
    if len(parts) != 2:
        return {}, md_text
    fm_text = parts[0].split('---\n', 1)[1]
    body = parts[1]
    meta: Dict[str, str] = {}
    for line in fm_text.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, body


def guide_by_slug(manifest: Dict[str, Any], slug: Optional[str]) -> Optional[Dict[str, Any]]:
    if not slug:
        return None
    for g in manifest.get('guides', []):
        if g.get('slug') == slug:
            return g
    return None


def build_excerpt(text: str, needles: List[str], limit: int = 800) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ''
    lowered = normalize_query(cleaned)
    for needle in needles:
        normalized = normalize_query(needle)
        if not normalized:
            continue
        idx = lowered.find(normalized)
        if idx >= 0:
            start = max(0, idx - 220)
            end = min(len(cleaned), idx + max(limit - 220, 280))
            return cleaned[start:end].strip()
    return cleaned[:limit].strip()


def enrich_result(base: Dict[str, Any], evidence: Dict[str, Any], text: str) -> Dict[str, Any]:
    needles = evidence.get('matched_evidence') or evidence.get('matched_terms') or []
    enriched = {
        **base,
        'confidence': evidence.get('confidence'),
        'evidence_score': evidence.get('score'),
        'evidence_reason': evidence.get('reason'),
        'matched_terms': evidence.get('matched_terms', []),
        'matched_phrases': evidence.get('matched_phrases', []),
        'matched_identifiers': evidence.get('matched_identifiers', []),
        'matched_evidence': evidence.get('matched_evidence', []),
        'excerpt': build_excerpt(text, list(needles)),
    }
    return enriched


def canonical_help_url(url: str) -> str:
    return re.sub(r'([?&])language=en_US&?', r'\1', url).rstrip('?&')


def help_article_id(url: str) -> str:
    match = re.search(r'[?&]id=([^&#]+)', url)
    if match:
        return match.group(1)
    return canonical_help_url(url).rstrip('/').rsplit('/', 1)[-1]


def help_article_missing(payload: Dict[str, Any]) -> bool:
    title = normalize_query(payload.get('title') or '')
    text = normalize_query(payload.get('text') or '')
    bad_signals = [
        'we looked high and low',
        "couldn't find that page",
        '404 error',
        'salesforce help | article',
    ]
    return any(signal in title or signal in text for signal in bad_signals)


def help_article_urls_from_payload(payload: Dict[str, Any]) -> List[str]:
    urls: List[str] = []
    for link in payload.get('childLinks', []) or []:
        if isinstance(link, str) and 'help.salesforce.com/s/articleView' in link:
            urls.append(canonical_help_url(link))
    deduped: List[str] = []
    seen = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped


def local_scrape_payloads(manifest: Dict[str, Any], guides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    seen_paths = set()
    for guide in guides + manifest.get('guides', []):
        raw_scrape_path = guide.get('raw_scrape_path')
        if not raw_scrape_path:
            continue
        path = str(Path(raw_scrape_path).expanduser())
        if path in seen_paths:
            continue
        seen_paths.add(path)
        scrape_path = Path(path)
        if scrape_path.is_file():
            try:
                payloads.append(read_json(scrape_path))
            except Exception:
                continue
    return payloads


def score_help_url(query: str, url: str) -> int:
    lowered = normalize_query(query)
    canonical = canonical_help_url(url).lower()
    score = 0
    for needle, urls in HELP_ARTICLE_HINTS.items():
        if needle in lowered and canonical_help_url(urls[0]).lower() == canonical:
            score += 12
    signature = build_query_signature(query)
    article_id = help_article_id(url).lower()
    for phrase in signature.get('phrases', []):
        if phrase.replace(' ', '_') in article_id or phrase.replace(' ', '.') in article_id:
            score += 8
    for term in signature.get('terms', []):
        if term in article_id:
            score += 2
    if 'miaw' in article_id and any(token in lowered for token in ('messaging', 'web chat', 'in-app and web', 'enhanced chat')):
        score += 12
    if any(token in article_id for token in ('setup', 'optimize', 'allowlist', 'cors')) and any(token in lowered for token in ('allowed domains', 'cors', 'allowed origins', 'origin')):
        score += 10
    if 'release-notes' in article_id or article_id.startswith('release-notes.'):
        score -= 12
    if 'copilot' in article_id and 'agentforce' in lowered:
        score += 8
    if 'generative_ai' in article_id and any(token in lowered for token in ('agentforce', 'generative ai')):
        score += 8
    return score


def build_help_guide(plan: Dict[str, Any], article_url: str) -> Dict[str, Any]:
    product = plan.get('classification', {}).get('product') or 'platform'
    return {
        'slug': help_article_id(article_url),
        'family': 'help',
        'product': product,
        'root_url': article_url,
    }


def scrape_help_article(query: str, plan: Dict[str, Any], article_url: str, crawl_children: bool = True) -> Optional[Dict[str, Any]]:
    ok, payload = run_browser_scraper(article_url, timeout=60)
    if not ok or help_article_missing(payload):
        return None

    guide = build_help_guide(plan, payload.get('url') or article_url)
    result = evaluate_artifact(
        query,
        guide,
        str(payload.get('text') or ''),
        f"help_article:{payload.get('strategy', 'unknown')}",
        payload.get('url') or article_url,
    )

    if not crawl_children:
        return result

    child_urls = help_article_urls_from_payload(payload)
    child_urls.sort(key=lambda item: score_help_url(query, item), reverse=True)
    best_result = result

    should_crawl = bool(child_urls) and (
        result.get('status') != 'pass'
        or result.get('evidence_score', 0) < 18
        or any(phrase in normalize_query(query) for phrase in ('allowed domains', 'allowed origins', 'cors allowlist', 'origin restrictions'))
    )
    if not should_crawl:
        return result

    for child_url in child_urls[:8]:
        child = scrape_help_article(query, plan, child_url, crawl_children=False)
        if not child:
            continue
        child['discovered_via'] = payload.get('url') or article_url
        child_rank = 2 if child.get('status') == 'pass' else (1 if child.get('status') == 'partial' else 0)
        best_rank = 2 if best_result.get('status') == 'pass' else (1 if best_result.get('status') == 'partial' else 0)
        if (child_rank, child.get('evidence_score', 0)) > (best_rank, best_result.get('evidence_score', 0)):
            best_result = child

    return best_result


def help_article_fallback(query: str, manifest: Dict[str, Any], plan: Dict[str, Any], use_local_hints: bool = True) -> Optional[Dict[str, Any]]:
    lowered = normalize_query(query)
    likely_guides = [guide_by_slug(manifest, g.get('slug')) or g for g in plan.get('fallback', {}).get('likely_guides', [])]
    urls: List[str] = []

    for needle, hinted_urls in HELP_ARTICLE_HINTS.items():
        if needle in lowered:
            urls.extend(hinted_urls)

    if use_local_hints:
        for payload in local_scrape_payloads(manifest, likely_guides):
            urls.extend(help_article_urls_from_payload(payload))

    for needle, source_urls in HELP_DISCOVERY_SOURCES.items():
        if needle not in lowered:
            continue
        for source_url in source_urls:
            ok, payload = run_browser_scraper(source_url, timeout=60)
            if ok:
                urls.extend(help_article_urls_from_payload(payload))

    deduped: List[str] = []
    seen = set()
    for url in urls:
        canonical = canonical_help_url(url)
        if canonical not in seen:
            seen.add(canonical)
            deduped.append(canonical)

    deduped.sort(key=lambda item: score_help_url(query, item), reverse=True)
    best_partial: Optional[Dict[str, Any]] = None
    for article_url in deduped[:10]:
        result = scrape_help_article(query, plan, article_url, crawl_children=True)
        if not result:
            continue
        if result.get('status') == 'pass':
            return result
        if result.get('status') == 'partial' and (
            best_partial is None or result.get('evidence_score', 0) > best_partial.get('evidence_score', 0)
        ):
            best_partial = result
    return best_partial


def evaluate_artifact(query: str, guide: Dict[str, Any], text: str, method: str, source_url: str) -> Dict[str, Any]:
    evidence = evaluate_text_evidence(query, text, guide)
    fail_reasons = {'wrong_family_match', 'external_term_missing', 'missing_identifier', 'partial_identifier_match'}
    if evidence.get('acceptable'):
        status = 'pass'
    elif evidence.get('reason') in fail_reasons:
        status = 'fail'
    else:
        status = 'partial' if evidence.get('score', 0) > 0 else 'fail'
    grounded = status in ('pass', 'partial')
    result = {
        'status': status,
        'guide': guide.get('slug'),
        'source_family': guide.get('family'),
        'source_product': guide.get('product'),
        'grounded': grounded,
        'method': method,
        'source_url': source_url,
    }
    return enrich_result(result, evidence, text)


def best_candidate(candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None
    rank = {'pass': 3, 'partial': 2, 'fail': 1}
    candidates.sort(key=lambda item: (rank.get(item['status'], 0), item.get('evidence_score', 0)), reverse=True)
    return candidates[0]


def retrieve_from_local_artifacts(query: str, guide: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    normalized_dir_value = guide.get('normalized_dir')
    normalized_dir = Path(normalized_dir_value).expanduser() if normalized_dir_value else None
    normalized_path = normalized_dir / 'index.md' if normalized_dir else None
    if normalized_path and normalized_path.is_file():
        md = normalized_path.read_text(errors='ignore')
        meta, body = parse_frontmatter(md)
        candidates.append(evaluate_artifact(
            query,
            guide,
            body,
            'normalized_markdown',
            meta.get('source_url') or guide.get('root_url'),
        ))

    raw_scrape_path = guide.get('raw_scrape_path')
    scrape_path = Path(raw_scrape_path).expanduser() if raw_scrape_path else None
    if scrape_path and scrape_path.is_file():
        payload = read_json(scrape_path)
        text = str(payload.get('text') or '').strip()
        if text and not payload.get('likelyShell'):
            candidates.append(evaluate_artifact(
                query,
                guide,
                text,
                f"browser_scrape:{payload.get('strategy', 'unknown')}",
                payload.get('url') or guide.get('root_url'),
            ))

    raw_pdf_path = guide.get('raw_pdf_path')
    pdf_path = Path(raw_pdf_path).expanduser() if raw_pdf_path else None
    if pdf_path and pdf_path.is_file():
        text, note = extract_pdf_text(pdf_path)
        if text:
            candidates.append(evaluate_artifact(
                query,
                guide,
                text,
                f'pdf:{note}',
                guide.get('pdf_verified') or (guide.get('pdf_candidates') or [guide.get('root_url')])[0],
            ))

    return best_candidate(candidates)


def retrieve_from_live_sources(query: str, guide: Dict[str, Any], live_scrape: bool = False) -> Optional[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    if live_scrape and guide.get('root_url'):
        ok, payload = run_browser_scraper(guide['root_url'])
        if ok:
            text = str(payload.get('text') or '').strip()
            if text and not payload.get('likelyShell'):
                candidates.append(evaluate_artifact(
                    query,
                    guide,
                    text,
                    f"live_browser_scrape:{payload.get('strategy', 'unknown')}",
                    payload.get('url') or guide.get('root_url'),
                ))

    pdf_url = guide.get('pdf_verified') or (guide.get('pdf_candidates') or [None])[0]
    if pdf_url:
        tmp_pdf_path: Optional[Path] = None
        try:
            pdf_bytes = fetch_url(str(pdf_url), timeout=45)
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_pdf_path = Path(tmp.name)
            text, note = extract_pdf_text(tmp_pdf_path)
            if text:
                candidates.append(evaluate_artifact(
                    query,
                    guide,
                    text,
                    f'remote_pdf:{note}',
                    str(pdf_url),
                ))
        except Exception:
            pass
        finally:
            if tmp_pdf_path:
                tmp_pdf_path.unlink(missing_ok=True)

    return best_candidate(candidates)


def fallback_retrieve(query: str, manifest: Dict[str, Any], plan: Dict[str, Any], live_scrape: bool = False,
                     allow_local_artifacts: bool = True) -> Dict[str, Any]:
    likely_guides = plan.get('fallback', {}).get('likely_guides', [])
    tried: List[str] = []
    best_partial: Optional[Dict[str, Any]] = None

    if plan.get('fallback', {}).get('family_hint') == 'help':
        help_result = help_article_fallback(query, manifest, plan, use_local_hints=allow_local_artifacts)
        if help_result:
            help_result['tried'] = ['help-article-discovery']
            if help_result.get('status') == 'pass':
                return help_result
            best_partial = help_result if help_result.get('status') == 'partial' else best_partial

    for candidate in likely_guides:
        slug = candidate.get('slug')
        guide = guide_by_slug(manifest, slug) or candidate
        tried.append(slug or guide.get('title', 'unknown'))

        if allow_local_artifacts:
            local_result = retrieve_from_local_artifacts(query, guide)
            if local_result:
                local_result['tried'] = tried.copy()
                if local_result.get('status') == 'pass':
                    return local_result
                if local_result.get('status') == 'partial' and (
                    best_partial is None or local_result.get('evidence_score', 0) > best_partial.get('evidence_score', 0)
                ):
                    best_partial = local_result

        live_result = retrieve_from_live_sources(query, guide, live_scrape=live_scrape)
        if not live_result:
            continue
        live_result['tried'] = tried.copy()
        if live_result.get('status') == 'pass':
            return live_result
        if live_result.get('status') == 'partial' and (
            best_partial is None or live_result.get('evidence_score', 0) > best_partial.get('evidence_score', 0)
        ):
            best_partial = live_result

    if best_partial:
        if 'tried' not in best_partial:
            best_partial['tried'] = tried
        return best_partial

    return {
        'status': 'fail',
        'guide': likely_guides[0].get('slug') if likely_guides else None,
        'source_family': plan.get('fallback', {}).get('family_hint'),
        'source_product': None,
        'grounded': False,
        'method': 'fallback_failed',
        'source_url': likely_guides[0].get('root_url') if likely_guides else None,
        'excerpt': '',
        'confidence': 'low',
        'evidence_score': 0,
        'evidence_reason': 'no_viable_artifact',
        'matched_terms': [],
        'matched_phrases': [],
        'matched_identifiers': [],
        'matched_evidence': [],
        'tried': tried,
    }


def retrieve(query: str, manifest_path: Path, corpus_root: Path, mode: str, live_scrape: bool) -> Dict[str, Any]:
    manifest = load_manifest(manifest_path)
    plan = build_lookup_plan(query, manifest_path, corpus_root)
    resolved_mode = mode
    if mode == 'auto':
        resolved_mode = plan.get('mode', 'salesforce_aware')

    allow_local_artifacts = resolved_mode == 'local_first'
    result = fallback_retrieve(
        query,
        manifest,
        plan,
        live_scrape=live_scrape,
        allow_local_artifacts=allow_local_artifacts,
    )
    result['resolved_mode'] = resolved_mode
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Retrieve Salesforce docs using sf-docs runtime flow')
    parser.add_argument('--query', required=True)
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--corpus-root', type=Path, default=DEFAULT_CORPUS_ROOT)
    parser.add_argument('--mode', choices=('auto', 'local_first', 'salesforce_aware'), default='auto')
    parser.add_argument('--live-scrape', action='store_true', help='Allow live browser scraping during fallback')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = retrieve(args.query, args.manifest.expanduser(), args.corpus_root.expanduser(), args.mode, args.live_scrape)
    print(json.dumps(result, indent=2))
    return 0 if result.get('status') == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
