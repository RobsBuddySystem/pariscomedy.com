#!/usr/bin/env python3
"""Re-bake SHOWS_DATA in index.html + shows.html using only active shows."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOWS = ROOT / "data" / "shows_generated.json"
CANCELED = ROOT / "data" / "canceled_shows.json"


def _load_canceled_block():
    """Return (blocked_slugs, blocked_names_lower) from canceled_shows.json.

    Any show whose slug or name (case-insensitive) appears in this set MUST
    be excluded from public output, regardless of ticket_url_status.
    Root cause of recurring Velvet Open Mic regressions: generators did not
    consult this file. See vault: Open-Mic-Suspended-2026-05-04.
    """
    if not CANCELED.exists():
        return set(), set()
    data = json.loads(CANCELED.read_text(encoding="utf-8"))
    slugs, names = set(), set()
    for e in data.get("canceled", []):
        if e.get("public_visible") is True:
            continue
        if e.get("slug"):
            slugs.add(e["slug"].lower())
        for n in e.get("names", []) or []:
            names.add(n.strip().lower())
    return slugs, names


def main():
    shows = json.loads(SHOWS.read_text(encoding="utf-8"))
    blocked_slugs, blocked_names = _load_canceled_block()

    def _allowed(s):
        slug = (s.get("slug") or "").lower()
        name = (s.get("name") or s.get("show_name") or "").strip().lower()
        if slug and slug in blocked_slugs:
            return False
        if name and name in blocked_names:
            return False
        return True

    shows = [s for s in shows if _allowed(s)]
    active = [s for s in shows if s.get("ticket_url_status") == "active"]
    if len(active) < 10:
        print(f"REFUSE: only {len(active)} active shows (<10).", file=sys.stderr)
        sys.exit(2)
    blob = json.dumps(active, ensure_ascii=False, separators=(",", ":"))
    baked = []
    for fname in ("index.html", "shows.html"):
        p = ROOT / fname
        content = p.read_text(encoding="utf-8")
        new = re.sub(r"const SHOWS_DATA = \[.*?\];", f"const SHOWS_DATA = {blob};", content, flags=re.DOTALL)
        if new == content:
            # Page is live-wire (fetches /api/listings) — no static SHOWS_DATA to bake.
            print(f"SKIP: no SHOWS_DATA placeholder in {fname} (live-wire page)", file=sys.stderr)
            continue
        p.write_text(new, encoding="utf-8")
        baked.append(fname)
    print(json.dumps({"baked_active": len(active), "total": len(shows), "baked_files": baked}))

if __name__ == "__main__":
    main()
