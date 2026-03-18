#!/usr/bin/env python3
"""
Run the sf-docs retrieval benchmark against the local_first mode.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from retrieve_sf_docs import retrieve  # type: ignore


DEFAULT_BENCHMARK = SCRIPT_DIR.parent / 'assets' / 'retrieval-benchmark.json'
DEFAULT_RESULTS = SCRIPT_DIR.parent / 'assets' / 'retrieval-benchmark.results-template.json'
DEFAULT_MANIFEST = Path.home() / '.sf-docs' / 'manifest' / 'guides.json'
DEFAULT_CORPUS_ROOT = Path.home() / '.sf-docs'


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def evaluate_case(case: Dict[str, Any], result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    expected_outcome = case.get('expected_outcome', 'grounded')

    if expected_outcome == 'reject':
        if result.get('status') == 'pass' and result.get('grounded') is True and result.get('confidence') in ('high', 'medium'):
            reasons.append('query should have been rejected but returned a grounded pass')
        forbidden = case.get('forbidden_guides') or []
        if forbidden and result.get('guide') in forbidden and result.get('grounded') is True:
            reasons.append(f"forbidden guide returned: {result.get('guide')}")
        return len(reasons) == 0, reasons

    if result.get('status') != 'pass':
        reasons.append(f"status is {result.get('status')}")
        return False, reasons

    if result.get('grounded') is not True:
        reasons.append('result not grounded')

    families = case.get('expected_families') or []
    if families and result.get('source_family') not in families:
        reasons.append(f"family {result.get('source_family')!r} not in expected families {families}")

    products = case.get('expected_products') or []
    if products and result.get('source_product') not in products:
        reasons.append(f"product {result.get('source_product')!r} not in expected products {products}")

    guides = case.get('expected_guides') or []
    if guides and result.get('guide') not in guides:
        reasons.append(f"guide {result.get('guide')!r} not in expected guides {guides}")

    forbidden = case.get('forbidden_guides') or []
    if forbidden and result.get('guide') in forbidden:
        reasons.append(f"forbidden guide returned: {result.get('guide')}")

    matched = set((result.get('matched_evidence') or []) + (result.get('matched_terms') or []) + (result.get('matched_phrases') or []) + (result.get('matched_identifiers') or []))
    evidence_any = [item.lower() for item in case.get('evidence_any', [])]
    if evidence_any and not any(item in matched for item in evidence_any):
        reasons.append(f"missing any-of evidence terms {evidence_any}")

    evidence_all = [item.lower() for item in case.get('evidence_all', [])]
    missing = [item for item in evidence_all if item not in matched]
    if missing:
        reasons.append(f"missing required evidence terms {missing}")

    min_confidence = case.get('min_confidence')
    confidence_order = {'low': 1, 'medium': 2, 'high': 3}
    if min_confidence and confidence_order.get(result.get('confidence', 'low'), 0) < confidence_order.get(min_confidence, 0):
        reasons.append(f"confidence {result.get('confidence')!r} below required {min_confidence!r}")

    return len(reasons) == 0, reasons


def benchmark_status(case: Dict[str, Any], result: Dict[str, Any]) -> str:
    passed, _ = evaluate_case(case, result)
    if passed:
        return 'pass'
    if result.get('status') in ('pass', 'partial'):
        return 'partial'
    return 'fail'


def adapt_result(case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    passed, reasons = evaluate_case(case, result)
    return {
        'status': 'pass' if passed else benchmark_status(case, result),
        'source_family': result.get('source_family'),
        'source_product': result.get('source_product'),
        'guide': result.get('guide'),
        'grounded': result.get('grounded'),
        'confidence': result.get('confidence'),
        'evidence_score': result.get('evidence_score'),
        'matched_terms': result.get('matched_terms', []),
        'matched_phrases': result.get('matched_phrases', []),
        'matched_identifiers': result.get('matched_identifiers', []),
        'matched_evidence': result.get('matched_evidence', []),
        'notes': result.get('method', ''),
        'source_url': result.get('source_url'),
        'reasons': reasons,
    }


def run_case(case: Dict[str, Any], manifest: Path, corpus_root: Path, live_scrape: bool) -> Dict[str, Any]:
    local_first_result = retrieve(case['query'], manifest, corpus_root, 'local_first', live_scrape=live_scrape)
    return {
        'id': case['id'],
        'local_first': adapt_result(case, local_first_result),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run sf-docs retrieval benchmark')
    parser.add_argument('--benchmark', type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument('--results', type=Path, default=DEFAULT_RESULTS)
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--corpus-root', type=Path, default=DEFAULT_CORPUS_ROOT)
    parser.add_argument('--live-scrape', action='store_true')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    benchmark = load_json(args.benchmark)
    out = {
        'version': 3,
        'benchmark': args.benchmark.name,
        'generated_at': benchmark.get('generated_at'),
        'modes': {
            'local_first': {'description': 'Local corpus artifacts when available, with Salesforce-aware fallback on weak/missing evidence'},
        },
        'results': [run_case(case, args.manifest.expanduser(), args.corpus_root.expanduser(), args.live_scrape) for case in benchmark.get('cases', [])],
    }
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(out, indent=2) + '\n')
    print(f'Wrote benchmark results: {args.results}')
    print(f"Cases: {len(out['results'])}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
