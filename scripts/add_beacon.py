#!/usr/bin/env python3
"""
add_beacon.py — idempotently insert the analytics beacon tag into HTML pages
that are missing it.

The canonical pattern (copied verbatim from index.html, line ~951):

    <script src="/assets/track.js" defer></script>

Insertion rule: if the string "assets/track.js" is NOT already present anywhere
in the file, insert the tag on its own line immediately before the last
</body> in the file. If no </body> is found, the file is skipped and reported.

Safe to re-run: files that already contain the tag are left untouched.

Usage:
    python3 scripts/add_beacon.py [path ...]
    # with no args, scans the default target set (see TARGET_GLOBS below)
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BEACON_TAG = '<script src="/assets/track.js" defer></script>'

TARGET_GLOBS = [
    "shows.html",
    "whats-on.html",
    "show.html",
    "blog/index.html",
    "blog/whats-on-*.html",
    "c/*.html",
    "shows/*.html",
]


def collect_targets():
    files = []
    for pattern in TARGET_GLOBS:
        files.extend(sorted(REPO_ROOT.glob(pattern)))
    # de-dupe, keep only files (skip dirs like c/_archived_fr_only_20260706 if matched)
    seen = set()
    result = []
    for f in files:
        if f.is_file() and f not in seen:
            seen.add(f)
            result.append(f)
    return result


def process(path: Path):
    text = path.read_text(encoding="utf-8")
    if "assets/track.js" in text:
        return "skipped-present"
    idx = text.rfind("</body>")
    if idx == -1:
        return "skipped-no-body"
    new_text = text[:idx] + BEACON_TAG + "\n" + text[idx:]
    path.write_text(new_text, encoding="utf-8")
    return "inserted"


def main():
    args = sys.argv[1:]
    targets = [Path(a) for a in args] if args else collect_targets()

    counts = {"inserted": 0, "skipped-present": 0, "skipped-no-body": 0}
    no_body_files = []

    for f in targets:
        try:
            result = process(f)
        except Exception as e:
            print(f"ERROR {f}: {e}")
            continue
        counts[result] += 1
        if result == "skipped-no-body":
            no_body_files.append(str(f))

    print(f"Scanned: {len(targets)} files")
    print(f"Inserted beacon: {counts['inserted']}")
    print(f"Already had beacon: {counts['skipped-present']}")
    print(f"No </body> found: {counts['skipped-no-body']}")
    if no_body_files:
        print("Files missing </body> (skipped):")
        for f in no_body_files:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
