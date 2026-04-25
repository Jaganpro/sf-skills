#!/usr/bin/env python3
# ABOUTME: Validates GraphQL codegen freshness in a Multi-Framework project.
# ABOUTME: Exits 0 if generated types are newer than schema.graphql; non-zero with hint otherwise.

"""
Multi-Framework codegen freshness check.

Usage:
    python3 check_codegen_freshness.py <project-root>

Exits 0 if schema.graphql exists and graphql-operations-types.ts is newer than it.
Exits 1 with a remediation hint otherwise.
Exits 2 on usage error.

The skill front-loads this footgun in its WARNING block: schema.graphql is
generated from the connected org and not committed; if `npm run graphql:schema`
is skipped before `npm run build`, the build still passes but generated types
are stale or missing, and field access against UIAPI's `{ value }` shape fails
silently at runtime in production.
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_first(root: Path, name: str) -> Path | None:
    """Return the first matching file under root (BFS, depth-limited)."""
    for path in root.rglob(name):
        if "node_modules" in path.parts or ".git" in path.parts:
            continue
        return path
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "usage: check_codegen_freshness.py <project-root>",
            file=sys.stderr,
        )
        return 2

    root = Path(argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    print(f"sf-react codegen freshness check: {root}")

    schema = find_first(root, "schema.graphql")
    generated = find_first(root, "graphql-operations-types.ts")

    if schema is None:
        print("  ✗ schema.graphql not found")
        print(
            "    → Run `npm run graphql:schema` first to introspect the "
            "connected org and write schema.graphql."
        )
        print(
            "    → Schema files are deliberately not committed; you must "
            "regenerate from a fresh scratch/sandbox login."
        )
        return 1

    print(f"  ✓ schema.graphql found at {schema.relative_to(root)}")

    if generated is None:
        print("  ✗ graphql-operations-types.ts not found")
        print(
            "    → Run `npm run graphql:codegen` to generate operation "
            "types against the schema."
        )
        return 1

    print(
        f"  ✓ graphql-operations-types.ts found at "
        f"{generated.relative_to(root)}"
    )

    schema_mtime = schema.stat().st_mtime
    generated_mtime = generated.stat().st_mtime

    if generated_mtime < schema_mtime:
        print("  ✗ generated types are STALE — schema is newer than codegen output")
        print(
            "    → Run `npm run graphql:codegen` to regenerate "
            "graphql-operations-types.ts against the current schema."
        )
        print(
            "    → Build will pass but UIAPI field access (`{ value }` shape) "
            "may fail silently in production."
        )
        return 1

    print("  ✓ generated types are fresh (newer than schema)")
    print("codegen freshness OK — safe to proceed to build / deploy")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
