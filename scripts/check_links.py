#!/usr/bin/env python3
"""Internal link checker for the pariscomedy.com static site.

Scans every *.html file for href/src/form-action targets and verifies each
internal target resolves to a real file. Reports broken links and exits
non-zero if any are found (so it can gate a deploy).

External links (http/https/mailto/tel/lightning) are listed but not fetched.

Usage:  python3 scripts/check_links.py
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ATTR_RE = re.compile(r'(?:href|src|action)\s*=\s*"([^"]*)"', re.I)
SCRIPT_RE = re.compile(r'<script\b.*?</script>', re.S | re.I)
TEMPLATE_RE = re.compile(r'\$\{|\' \+|\+ \'')  # JS template / concat fragments

def resolve(target: str) -> Path | None:
    """Map an internal URL to a file path, or None if it's external/in-page."""
    t = target.split("#")[0].split("?")[0]
    if not t:
        return None
    if re.match(r'^(https?:|mailto:|tel:|lightning:|data:|javascript:)', t, re.I):
        return None
    if t.startswith("//"):
        return None
    t = t.lstrip("/")
    if t == "" or t.endswith("/"):
        return ROOT / t / "index.html"
    return ROOT / t

def main():
    html_files = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("blog/*.html"))
    checked, broken, external = 0, [], 0
    for f in html_files:
        text = SCRIPT_RE.sub("", f.read_text(encoding="utf-8", errors="ignore"))
        for m in ATTR_RE.finditer(text):
            target = m.group(1).strip()
            if TEMPLATE_RE.search(target):
                continue
            if re.match(r'^(https?:|mailto:|tel:|lightning:|data:|//)', target, re.I):
                external += 1
                continue
            if target.startswith("#") or not target:
                continue
            path = resolve(target)
            if path is None:
                continue
            checked += 1
            if not path.exists():
                broken.append((f.name, target))

    print(f"internal links checked : {checked}")
    print(f"external links (skipped): {external}")
    print(f"broken internal links  : {len(broken)}")
    for src, tgt in broken:
        print(f"  BROKEN  {src} -> {tgt}")
    sys.exit(1 if broken else 0)

if __name__ == "__main__":
    main()
