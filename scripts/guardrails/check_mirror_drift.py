#!/usr/bin/env python3
"""Mirror-drift check.

Several historical paris-comedy directories exist outside the deployed
push repo (iCloud, _repo, .openclaw). They are NOT served publicly, but
they are footguns: a future session could accidentally `cp` from a stale
mirror and re-publish stale copy.

This guardrail scans every mirror copy of index.html/about.html/book.html
and fails if ANY of them contains a forbidden string. Exit 0 = clean.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

FORBIDDEN = [
    "Stand-up every night",
    "best English-language acts in Paris",
    "something on every night",
    "How do I get a Featured listing",
    "Want Featured placement while",
    "best comics in Paris",
    "every night of the week",
    "Featured Tonight",
    "Featured Shows This Week",
    "Rotating weekly",
    "Verified, highlighted comedy nights in Paris",
    "These shows are Featured",
    "every English stand-up show",
    "Every show in the directory",
    "claim your free Featured listing",
    "First 100 Featured listings",
    "first 100 show runners",
    "May 19–25",
    "every show in Paris",
]


def find_mirrors() -> list[Path]:
    """Walk a known set of mirror roots — avoids slow $HOME traversal."""
    home = Path.home()
    roots = [
        home / "pariscomedy-push-20260517-194848",
        home / "Desktop" / "pariscomedy_output" / "html",
        home / "Documents" / "Claude" / "Projects" / "pariscomedy.com" / "_repo",
        home / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
            / "Family" / "pariscomedy.com" / "_repo",
        home / ".openclaw" / "workspace" / "apps" / "paris-comedy",
    ]
    paths: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for name in ("index.html", "about.html", "book.html"):
            p = root / name
            if p.is_file():
                paths.append(p)
    return paths


def main() -> int:
    failures = []
    mirrors = find_mirrors()
    for path in mirrors:
        try:
            text = path.read_text(errors="replace")
        except Exception:
            continue
        for needle in FORBIDDEN:
            if needle in text:
                failures.append(f"{path}: contains {needle!r}")
    if not failures:
        print(f"✅ {len(mirrors)} mirror files scanned — all clean")
        return 0
    print(f"❌ {len(failures)} mirror drift failure(s):")
    for f in failures:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
