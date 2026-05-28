#!/usr/bin/env python3
"""Prebuild — substitute partial includes in HTML files.

Per P1.1A v2 Section G (Migration Doctrine, Phase 2.0):
This script lands plumbing ONLY. It does NOT modify any existing HTML
that lacks include directives. It is intentionally a no-op against the
current pariscomedy-push repo because no page yet contains an
`<!-- include: ... -->` directive. Subsequent phases (2.1+) will start
adding those directives page-by-page as partials are extracted.

Directive syntax (canonical):

    <!-- include: partials/<name>.html -->

When encountered, the line is replaced verbatim with the contents of
`partials/<name>.html` resolved against the repo root. If the file is
missing, the build FAILS hard (errors out non-zero). This prevents
silent drift.

Hard rules (per P1.1A §G + §I and P1.1B §F + §H):
- One filesystem location for partials: `<repo>/partials/`
- Backend FastAPI Jinja layout MUST resolve to the same path
- No "half-migrated" pages: a page either has no directives OR has only
  directives (no inline header HTML alongside an include directive
  pointing at the header). The lint step at the bottom catches this.

Usage:
    python3 scripts/prebuild_partials.py [--src .] [--out dist] [--check]
        --src      repo root (default: parent of this scripts/ dir)
        --out      output directory (default: <src>/dist)
        --check    do not write outputs; exit non-zero if any directive
                   resolves missing OR any half-migration is detected
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

INCLUDE_RE = re.compile(r'<!--\s*include:\s*(?P<path>partials/[A-Za-z0-9_.\-/]+\.html)\s*-->')


class BuildError(Exception):
    pass


def collect_html_files(src: Path) -> list[Path]:
    skip = {'node_modules', 'dist', '_backups', '.git', 'partials'}
    out: list[Path] = []
    for p in src.rglob('*.html'):
        if any(part in skip for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def resolve_partial(src: Path, rel: str) -> Path:
    p = (src / rel).resolve()
    src_resolved = src.resolve()
    if not str(p).startswith(str(src_resolved)):
        raise BuildError(f"partial path escapes repo root: {rel}")
    if not p.is_file():
        raise BuildError(f"partial missing: {rel} (looked at {p})")
    return p


def substitute(html: str, src: Path) -> str:
    def repl(m: re.Match) -> str:
        partial_path = m.group('path')
        partial_file = resolve_partial(src, partial_path)
        return partial_file.read_text(encoding='utf-8')

    return INCLUDE_RE.sub(repl, html)


def lint_half_migration(html: str, page_rel: str) -> list[str]:
    """Detect pages that ship both inline header AND an include directive
    pointing at a header. Per the migration doctrine this is forbidden —
    a page is either fully legacy OR fully migrated.
    Returns a list of issue strings; empty if clean.
    """
    issues: list[str] = []
    has_include_header = bool(re.search(r'<!--\s*include:\s*partials/header\.html\s*-->', html))
    has_inline_header = bool(re.search(r'<header\b', html, re.IGNORECASE))
    if has_include_header and has_inline_header:
        issues.append(f"{page_rel}: BOTH <!-- include partials/header.html --> AND inline <header> — half-migrated")
    has_include_footer = bool(re.search(r'<!--\s*include:\s*partials/footer[.\-/][^>]*-->', html))
    has_inline_footer = bool(re.search(r'<footer\b', html, re.IGNORECASE))
    if has_include_footer and has_inline_footer:
        issues.append(f"{page_rel}: BOTH <!-- include partials/footer --> AND inline <footer> — half-migrated")
    return issues


def main() -> int:
    here = Path(__file__).resolve().parent
    default_src = here.parent
    ap = argparse.ArgumentParser(description='Prebuild — substitute partial includes (Phase 2.0 plumbing).')
    ap.add_argument('--src', type=Path, default=default_src, help='repo root')
    ap.add_argument('--out', type=Path, default=None, help='output dir (default <src>/dist)')
    ap.add_argument('--check', action='store_true', help='dry run; exit non-zero on any error or half-migration')
    args = ap.parse_args()

    src: Path = args.src.resolve()
    out: Path = (args.out or (src / 'dist')).resolve()
    check_only: bool = args.check

    if not (src / 'partials').exists():
        print(f"[prebuild] WARN: {src/'partials'} does not exist — creating empty.", file=sys.stderr)
        (src / 'partials').mkdir(parents=True, exist_ok=True)

    if not check_only:
        out.mkdir(parents=True, exist_ok=True)

    files = collect_html_files(src)
    print(f"[prebuild] scanning {len(files)} HTML files under {src}", file=sys.stderr)
    errors: list[str] = []
    n_with_directives = 0
    n_no_directives = 0
    for f in files:
        rel = f.relative_to(src)
        html = f.read_text(encoding='utf-8')
        has_directive = bool(INCLUDE_RE.search(html))
        # Lint regardless
        for issue in lint_half_migration(html, str(rel)):
            errors.append(issue)
        if has_directive:
            n_with_directives += 1
            try:
                substituted = substitute(html, src)
            except BuildError as e:
                errors.append(f"{rel}: {e}")
                continue
            if not check_only:
                dest = out / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(substituted, encoding='utf-8')
        else:
            n_no_directives += 1
            if not check_only:
                dest = out / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(html, encoding='utf-8')

    print(f"[prebuild] pages with include directives: {n_with_directives}", file=sys.stderr)
    print(f"[prebuild] pages with no directives (passed through): {n_no_directives}", file=sys.stderr)
    if errors:
        print('[prebuild] ERRORS:', file=sys.stderr)
        for e in errors:
            print(f'  - {e}', file=sys.stderr)
        return 1
    if not check_only:
        print(f"[prebuild] wrote {n_with_directives + n_no_directives} files to {out}", file=sys.stderr)
    print('[prebuild] OK', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
