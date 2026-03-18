#!/usr/bin/env python3
"""
sf-docs CLI

Unified wrapper around the sf-docs helper scripts.

Examples:
  python3 cli.py discover --output ~/.sf-docs/manifest/guides.json --pretty
  python3 cli.py sync --download-pdf --normalize
  python3 cli.py status
  python3 cli.py diagnose --query "Find official Salesforce REST API authentication docs"
  python3 cli.py retrieve --query "System.StubProvider" --mode salesforce_aware --live-scrape
  python3 cli.py score-benchmark --benchmark ../assets/retrieval-benchmark.json --results ../assets/retrieval-benchmark.results-template.json
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
DEFAULT_SEED = ASSETS_DIR / "discovery-manifest.seed.json"
DEFAULT_BENCHMARK = ASSETS_DIR / "retrieval-benchmark.json"
DEFAULT_RESULTS = ASSETS_DIR / "retrieval-benchmark.results-template.json"
DEFAULT_CORPUS_ROOT = Path.home() / ".sf-docs"
DEFAULT_MANIFEST = DEFAULT_CORPUS_ROOT / "manifest" / "guides.json"


def run(script_name: str, args: List[str]) -> int:
    script = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script), *args]
    return subprocess.call(cmd)


def cmd_discover(args: argparse.Namespace) -> int:
    argv = [
        "--seed", str(args.seed),
        "--output", str(args.output),
    ]
    if args.verify_pdf:
        argv.append("--verify-pdf")
    if args.pretty:
        argv.append("--pretty")
    return run("discover_salesforce_docs.py", argv)


def cmd_sync(args: argparse.Namespace) -> int:
    argv = [
        "--manifest", str(args.manifest),
        "--corpus-root", str(args.corpus_root),
    ]
    for slug in args.slug:
        argv.extend(["--slug", slug])
    if args.download_pdf:
        argv.append("--download-pdf")
    if args.download_html:
        argv.append("--download-html")
    if args.browser_scrape:
        argv.append("--browser-scrape")
    if args.normalize:
        argv.append("--normalize")
    if args.verify_pdf:
        argv.append("--verify-pdf")
    if args.dry_run:
        argv.append("--dry-run")
    return run("sync_sf_docs.py", argv)


def cmd_status(args: argparse.Namespace) -> int:
    argv = ["status", "--corpus-root", str(args.corpus_root)]
    return run("sf_docs_runtime.py", argv)


def cmd_diagnose(args: argparse.Namespace) -> int:
    argv = [
        "diagnose",
        "--query", args.query,
        "--manifest", str(args.manifest),
        "--corpus-root", str(args.corpus_root),
    ]
    return run("sf_docs_runtime.py", argv)


def cmd_score_benchmark(args: argparse.Namespace) -> int:
    argv = [
        "--benchmark", str(args.benchmark),
        "--results", str(args.results),
    ]
    return run("score_retrieval_benchmark.py", argv)


def cmd_retrieve(args: argparse.Namespace) -> int:
    argv = [
        "--query", args.query,
        "--manifest", str(args.manifest),
        "--corpus-root", str(args.corpus_root),
        "--mode", args.mode,
    ]
    if args.live_scrape:
        argv.append("--live-scrape")
    return run("retrieve_sf_docs.py", argv)


def cmd_run_benchmark(args: argparse.Namespace) -> int:
    argv = [
        "--benchmark", str(args.benchmark),
        "--results", str(args.results),
        "--manifest", str(args.manifest),
        "--corpus-root", str(args.corpus_root),
    ]
    if args.live_scrape:
        argv.append("--live-scrape")
    return run("run_retrieval_benchmark.py", argv)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="sf-docs CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_discover = sub.add_parser("discover", help="Build/enrich a Salesforce docs manifest")
    p_discover.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    p_discover.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    p_discover.add_argument("--verify-pdf", action="store_true")
    p_discover.add_argument("--pretty", action="store_true")
    p_discover.set_defaults(func=cmd_discover)

    p_sync = sub.add_parser("sync", help="Fetch/normalize a local sf-docs corpus")
    p_sync.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p_sync.add_argument("--corpus-root", type=Path, default=DEFAULT_CORPUS_ROOT)
    p_sync.add_argument("--slug", action="append", default=[])
    p_sync.add_argument("--download-pdf", action="store_true")
    p_sync.add_argument("--download-html", action="store_true")
    p_sync.add_argument("--browser-scrape", action="store_true")
    p_sync.add_argument("--normalize", action="store_true")
    p_sync.add_argument("--verify-pdf", action="store_true")
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.set_defaults(func=cmd_sync)

    p_status = sub.add_parser("status", help="Show local corpus/runtime status")
    p_status.add_argument("--corpus-root", type=Path, default=DEFAULT_CORPUS_ROOT)
    p_status.set_defaults(func=cmd_status)

    p_diag = sub.add_parser("diagnose", help="Build a sequential lookup plan for a query")
    p_diag.add_argument("--query", required=True)
    p_diag.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p_diag.add_argument("--corpus-root", type=Path, default=DEFAULT_CORPUS_ROOT)
    p_diag.set_defaults(func=cmd_diagnose)

    p_retrieve = sub.add_parser("retrieve", help="Run end-to-end sf-docs retrieval")
    p_retrieve.add_argument("--query", required=True)
    p_retrieve.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p_retrieve.add_argument("--corpus-root", type=Path, default=DEFAULT_CORPUS_ROOT)
    p_retrieve.add_argument("--mode", choices=("auto", "local_first", "salesforce_aware"), default="auto")
    p_retrieve.add_argument("--live-scrape", action="store_true")
    p_retrieve.set_defaults(func=cmd_retrieve)

    p_score = sub.add_parser("score-benchmark", help="Score benchmark results")
    p_score.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    p_score.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    p_score.set_defaults(func=cmd_score_benchmark)

    p_run = sub.add_parser("run-benchmark", help="Execute retrieval benchmark and write results")
    p_run.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    p_run.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    p_run.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p_run.add_argument("--corpus-root", type=Path, default=DEFAULT_CORPUS_ROOT)
    p_run.add_argument("--live-scrape", action="store_true")
    p_run.set_defaults(func=cmd_run_benchmark)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
