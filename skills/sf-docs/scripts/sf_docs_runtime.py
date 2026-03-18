#!/usr/bin/env python3
"""
sf-docs runtime helper.

Provides lightweight, stdlib-only utilities for:
- detecting local corpus readiness
- classifying likely Salesforce doc families
- building a sequential local-first / Salesforce-aware lookup plan
- extracting evidence from candidate docs so broad wrong-guide matches are rejected

Examples:
  python3 sf_docs_runtime.py diagnose     --query "Find official REST API authentication docs"     --manifest skills/sf-docs/assets/discovery-manifest.seed.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_CORPUS_ROOT = Path.home() / ".sf-docs"
DEFAULT_MANIFEST = DEFAULT_CORPUS_ROOT / "manifest" / "guides.json"
DEFAULT_NORMALIZED_ROOT = DEFAULT_CORPUS_ROOT / "normalized" / "md"

HIGH_SIGNAL_KEYWORDS = {
    "agentforce": {"family": "platform", "product": "agentforce"},
    "agent script": {"family": "platform", "product": "agentforce"},
    "atlas reasoning": {"family": "platform", "product": "agentforce"},
    "prompt template": {"family": "platform", "product": "agentforce"},
    "models api": {"family": "platform", "product": "agentforce"},
    "lwc": {"family": "platform", "product": "lwc"},
    "lightning web components": {"family": "platform", "product": "lwc"},
    "wire service": {"family": "platform", "product": "lwc"},
    "wire adapters": {"family": "platform", "product": "lwc"},
    "lightning message service": {"family": "platform", "product": "lwc"},
    "apex": {"family": "atlas", "product": "apex"},
    "stubprovider": {"family": "atlas", "product": "apex"},
    "queueable": {"family": "atlas", "product": "apex"},
    "rest api": {"family": "atlas", "product": "api"},
    "oauth": {"family": "atlas", "product": "api"},
    "bearer token": {"family": "atlas", "product": "api"},
    "metadata api": {"family": "atlas", "product": "metadata"},
    "deploy": {"family": "atlas", "product": "metadata"},
    "retrieve": {"family": "atlas", "product": "metadata"},
    "object reference": {"family": "atlas", "product": "platform"},
    "standard object": {"family": "atlas", "product": "platform"},
    "help article": {"family": "help", "product": "platform"},
    "salesforce help": {"family": "help", "product": "platform"},
    "help.salesforce.com": {"family": "help", "product": "platform"},
    "setup": {"family": "help", "product": "platform"},
    "messaging": {"family": "help", "product": "platform"},
    "allowed domains": {"family": "help", "product": "platform"},
    "allowed origins": {"family": "help", "product": "platform"},
    "cors allowlist": {"family": "help", "product": "platform"},
    "cors": {"family": "help", "product": "platform"},
    "origin restrictions": {"family": "help", "product": "platform"},
}

COMMON_PHRASES = [
    "wire service",
    "wire adapters",
    "bearer token",
    "authorization header",
    "allowed domains",
    "allowed origins",
    "cors allowlist",
    "origin restrictions",
    "embedded deployment",
    "deployment security",
    "identity verification",
    "lightning message service",
    "standard object",
    "object reference",
    "agent script",
    "prompt template",
    "models api",
]

GENERIC_PRODUCT_PHRASES = {
    "agentforce",
    "lightning web components",
    "rest api",
    "metadata api",
    "object reference",
    "standard object",
    "apex",
}

STOP_WORDS = {
    "find", "official", "salesforce", "documentation", "docs", "about",
    "explain", "guide", "guidance", "lookup", "look", "using", "with",
    "when", "where", "what", "which", "their", "they", "them", "from",
    "that", "this", "into", "your", "how", "and", "for", "the", "use",
    "used", "should", "does", "developer", "developers",
}

EXTERNAL_VENDOR_TERMS = {
    "stripe", "sap", "bapi", "shopify", "slack", "zendesk", "servicenow",
    "jira", "confluence", "docusign", "hubspot",
}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def corpus_status(corpus_root: Path = DEFAULT_CORPUS_ROOT) -> Dict[str, Any]:
    normalized_root = corpus_root / "normalized" / "md"
    manifest_path = corpus_root / "manifest" / "guides.json"
    md_files = list(normalized_root.rglob("*.md")) if normalized_root.exists() else []
    return {
        "corpus_root": str(corpus_root),
        "normalized_root": str(normalized_root),
        "manifest_path": str(manifest_path),
        "corpus_exists": corpus_root.exists(),
        "normalized_exists": normalized_root.exists(),
        "manifest_exists": manifest_path.exists(),
        "markdown_files": len(md_files),
        "ready": normalized_root.exists() and len(md_files) > 0,
    }


def normalize_query(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def unique_preserve(values: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for value in values:
        if not value:
            continue
        normalized = value.strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


def extract_terms(query: str) -> List[str]:
    lowered = normalize_query(query)
    raw_terms = re.findall(r"[A-Za-z][A-Za-z0-9_.:-]{2,}", lowered)
    terms = [t for t in raw_terms if t not in STOP_WORDS]
    return unique_preserve(terms)[:12]


def extract_identifiers(query: str) -> List[str]:
    identifiers: List[str] = []
    identifiers.extend(re.findall(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+", query))
    identifiers.extend(re.findall(r"[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9_]*)+", query))
    return unique_preserve(identifiers)


def extract_phrases(query: str) -> List[str]:
    lowered = normalize_query(query)
    phrases: List[str] = []
    phrases.extend(re.findall(r'"([^"]+)"', query))
    phrases.extend([key for key in HIGH_SIGNAL_KEYWORDS if key in lowered and " " in key])
    phrases.extend([phrase for phrase in COMMON_PHRASES if phrase in lowered])
    return unique_preserve(phrases)


def classify_query(query: str) -> Dict[str, Optional[str]]:
    lowered = normalize_query(query)
    best: Dict[str, Optional[str]] = {"family": None, "product": None, "keyword": None}
    best_score = 0

    for key, meta in HIGH_SIGNAL_KEYWORDS.items():
        if key in lowered:
            score = max(1, len(key.split())) * 2 + len(key)
            if score > best_score:
                best_score = score
                best = {"family": meta["family"], "product": meta["product"], "keyword": key}

    if not best["family"] and any(term in lowered for term in ("system.", "database.", "schema.", "test.")):
        best = {"family": "atlas", "product": "apex", "keyword": "apex-identifier"}

    return best


def manifest_guides(manifest_path: Optional[Path]) -> List[Dict[str, Any]]:
    if not manifest_path or not manifest_path.exists():
        return []

    data = load_json(manifest_path)
    return data.get("guides", [])


def build_query_signature(query: str) -> Dict[str, Any]:
    return {
        "terms": extract_terms(query),
        "identifiers": extract_identifiers(query),
        "phrases": extract_phrases(query),
        "classification": classify_query(query),
    }


def score_guide(query: str, guide: Dict[str, Any], classification: Dict[str, Optional[str]]) -> int:
    score = 0
    lowered = normalize_query(query)
    title = normalize_query(guide.get("title", ""))
    slug = normalize_query(guide.get("slug", ""))
    product = normalize_query(guide.get("product", ""))
    family = normalize_query(guide.get("family", ""))
    root_url = normalize_query(guide.get("root_url", ""))

    for identifier in extract_identifiers(query):
        if identifier in title:
            score += 8
        if identifier in slug:
            score += 7

    for phrase in extract_phrases(query):
        if phrase in title:
            score += 6
        if phrase in slug:
            score += 5
        if phrase in root_url:
            score += 4

    for term in extract_terms(query):
        if term in title:
            score += 4
        if term in slug:
            score += 4
        if term in root_url:
            score += 2

    if classification.get("product") and classification["product"] == product:
        score += 6
    if classification.get("family") and classification["family"] == family:
        score += 4
    if classification.get("keyword") and classification["keyword"] in title:
        score += 5

    if "reference" in lowered and "reference" in title:
        score += 3
    if "developer guide" in title and "guide" in lowered:
        score += 2
    return score


def likely_guides(query: str, manifest_path: Optional[Path], limit: int = 5) -> List[Dict[str, Any]]:
    guides = manifest_guides(manifest_path)
    classification = classify_query(query)
    ranked = [
        {**guide, "_score": score_guide(query, guide, classification)}
        for guide in guides
    ]
    ranked.sort(key=lambda g: g["_score"], reverse=True)
    return [
        {k: v for k, v in guide.items() if k != "_score"}
        for guide in ranked[:limit]
        if guide.get("_score", 0) > 0
    ]


def _contains_evidence(searchable: str, needle: str) -> bool:
    normalized = normalize_query(needle)
    if not normalized:
        return False
    pattern = r"(?<![a-z0-9_])" + re.escape(normalized) + r"(?![a-z0-9_])"
    return re.search(pattern, searchable) is not None


def evaluate_text_evidence(query: str, text: str, guide: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    searchable = normalize_query(text)
    signature = build_query_signature(query)
    matched_identifiers = [identifier for identifier in signature["identifiers"] if _contains_evidence(searchable, identifier)]
    matched_phrases = [phrase for phrase in signature["phrases"] if _contains_evidence(searchable, phrase)]
    matched_terms = [term for term in signature["terms"] if _contains_evidence(searchable, term)]
    specific_phrases = [phrase for phrase in signature["phrases"] if phrase not in GENERIC_PRODUCT_PHRASES]
    matched_specific_phrases = [phrase for phrase in matched_phrases if phrase not in GENERIC_PRODUCT_PHRASES]
    external_terms = [term for term in signature["terms"] if term in EXTERNAL_VENDOR_TERMS]
    matched_external_terms = [term for term in external_terms if term in searchable]

    score = 0
    score += len(matched_identifiers) * 8
    score += len(matched_specific_phrases) * 6
    score += (len(matched_phrases) - len(matched_specific_phrases)) * 2
    score += len(matched_terms) * 1

    classification = signature["classification"]
    family_match = None
    product_match = None
    if guide:
        family = normalize_query(guide.get("family", ""))
        product = normalize_query(guide.get("product", ""))
        family_match = bool(classification.get("family") and classification["family"] == family)
        product_match = bool(classification.get("product") and classification["product"] == product)
        if family_match:
            score += 2
        if product_match:
            score += 3

    confidence = "low"
    acceptable = False
    reason = "no_evidence"

    identifier_count = len(signature["identifiers"])
    if matched_identifiers and (identifier_count <= 1 or len(matched_identifiers) == identifier_count):
        confidence = "high"
        acceptable = True
        reason = "identifier_match"
    elif matched_identifiers and identifier_count > 1:
        confidence = "low"
        acceptable = False
        reason = "partial_identifier_match"
    elif signature["identifiers"]:
        confidence = "low"
        acceptable = False
        reason = "missing_identifier"
    elif matched_specific_phrases and (
        product_match or (
            not classification.get("product") and (family_match or not classification.get("family"))
        )
    ):
        confidence = "high" if len(matched_specific_phrases) >= 2 else "medium"
        acceptable = True
        reason = "specific_phrase_match"
    elif specific_phrases and not matched_specific_phrases:
        confidence = "low"
        acceptable = False
        reason = "missing_specific_phrase"
    elif len(matched_terms) >= 4 and (
        product_match or (
            not classification.get("product") and (family_match or product_match)
        )
    ):
        confidence = "medium"
        acceptable = True
        reason = "dense_term_match"
    elif matched_terms:
        confidence = "low"
        reason = "weak_term_overlap"

    if external_terms and not matched_external_terms and not matched_identifiers:
        acceptable = False
        confidence = "low"
        reason = "external_term_missing"

    if guide and classification.get("family") and family_match is False and not matched_identifiers:
        acceptable = False
        confidence = "low"
        reason = "wrong_family_match"

    return {
        "acceptable": acceptable,
        "confidence": confidence,
        "reason": reason,
        "score": score,
        "matched_identifiers": matched_identifiers,
        "matched_phrases": matched_phrases,
        "matched_terms": matched_terms,
        "matched_evidence": unique_preserve(matched_identifiers + matched_phrases + matched_terms),
        "family_match": family_match,
        "product_match": product_match,
    }


def build_fallback_plan(query: str, manifest_path: Optional[Path]) -> Dict[str, Any]:
    classification = classify_query(query)
    guides = likely_guides(query, manifest_path)
    family = classification.get("family") or (guides[0].get("family") if guides else None) or "unknown"

    plan = {
        "family_hint": family,
        "likely_guides": guides,
        "fallback_order": [],
        "notes": [
            "Keep fallback targeted; do not broad-crawl during normal query-time retrieval.",
            "Reject broad official guide hits when query evidence is weak or from the wrong family.",
            "Prefer official sources and call out uncertainty when retrieval is partial.",
        ],
    }

    if family == "help":
        plan["fallback_order"] = [
            "target help.salesforce.com article URLs or article identifiers",
            "avoid trusting site shell/navigation content",
            "fall back to official PDFs only if guide-form help content exists",
        ]
    elif family == "atlas":
        plan["fallback_order"] = [
            "try exact atlas guide root/page first",
            "if HTML is unstable, use verified PDF candidate from manifest",
            "prefer exact reference/relevant guide over broad docs homepage search",
        ]
    elif family == "platform":
        plan["fallback_order"] = [
            "try modern platform guide root/page first",
            "if query is AI/Agentforce related, prioritize /docs/ai/agentforce/ guides",
            "if HTML is unstable and a PDF exists, use official PDF fallback",
        ]
    else:
        plan["fallback_order"] = [
            "classify likely family from terminology and guide names",
            "target most likely official guide root",
            "use official PDF fallback if HTML retrieval is unstable",
        ]

    return plan


def build_lookup_plan(query: str, manifest_path: Optional[Path], corpus_root: Path) -> Dict[str, Any]:
    corpus = corpus_status(corpus_root)

    return {
        "query": query,
        "local_corpus": {
            "ready": corpus["ready"],
            "preferred_sources": [
                "normalized_markdown",
                "browser_scrape_payload",
                "pdf_text",
            ],
            "weak_result_rules": [
                "no relevant local artifacts found",
                "results clearly unrelated",
                "exact API/CLI/error term missing",
                "snippets too fragmentary to support confident answer",
                "release-sensitive query with stale local corpus",
            ],
        },
        "corpus": corpus,
        "mode": "local_first" if corpus["ready"] else "salesforce_aware",
        "classification": classify_query(query),
        "query_signature": build_query_signature(query),
        "fallback": build_fallback_plan(query, manifest_path),
    }


def command_diagnose(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest) if args.manifest else None
    corpus_root = Path(args.corpus_root).expanduser()
    plan = build_lookup_plan(args.query, manifest_path, corpus_root)
    print(json.dumps(plan, indent=2))
    return 0


def command_status(args: argparse.Namespace) -> int:
    corpus = corpus_status(Path(args.corpus_root).expanduser())
    payload = {
        "local_corpus_ready": corpus["ready"],
        "corpus": corpus,
    }
    print(json.dumps(payload, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="sf-docs runtime helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show local corpus/runtime status")
    p_status.add_argument("--corpus-root", default=str(DEFAULT_CORPUS_ROOT))
    p_status.set_defaults(func=command_status)

    p_diag = sub.add_parser("diagnose", help="Build a sequential lookup plan for a query")
    p_diag.add_argument("--query", required=True)
    p_diag.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    p_diag.add_argument("--corpus-root", default=str(DEFAULT_CORPUS_ROOT))
    p_diag.set_defaults(func=command_diagnose)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
