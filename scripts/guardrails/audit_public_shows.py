#!/usr/bin/env python3
"""Provenance audit for every public show on pariscomedy.com.

Per PROJECT_CANON: a public show must have provable provenance. This script
walks SHOWS_DATA in /shows.html (canonical source) and applies each rule
below. Exit 0 = GREEN; non-zero = HOLD with reasons.

Rules (each row must satisfy ALL):
    1. has ticket_url AND source_url
    2. has verified_at (any non-empty date string)
    3. slug is NOT on the canonical canceled blocklist (data/canceled_shows.json)
    4. show_name is NOT on any canceled `names` list
    5. status (if present) is not 'canceled' alongside being visible
    6. last_verified_at must not claim a future date

Usage:
    python3 scripts/guardrails/audit_public_shows.py [--offline]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOWS_HTML = ROOT / "shows.html"
BLOCKLIST  = ROOT / "data" / "canceled_shows.json"
LIVE_URL   = "https://pariscomedy.com/shows.html"


def load_blocklist() -> tuple[set[str], set[str]]:
    if not BLOCKLIST.exists():
        return set(), set()
    data = json.loads(BLOCKLIST.read_text())
    slugs = {entry["slug"] for entry in data.get("canceled", [])}
    names = set()
    for entry in data.get("canceled", []):
        for n in entry.get("names", []):
            names.add(n)
    return slugs, names


def extract_shows_data(html: str) -> list[dict]:
    m = re.search(r"const SHOWS_DATA\s*=\s*(\[.*?\]);", html, re.S)
    if not m:
        raise RuntimeError("SHOWS_DATA not found")
    return json.loads(m.group(1))


def audit(rows: list[dict]) -> list[str]:
    failures: list[str] = []
    blocked_slugs, blocked_names = load_blocklist()
    today = datetime.now().date().isoformat()
    for r in rows:
        slug = (r.get("id") or "").split("-")[0:2]
        slug = "-".join(slug) if slug else ""
        full_id = r.get("id", "")
        name = r.get("show_name", "")
        # Rule 1
        if not r.get("ticket_url"):
            failures.append(f"{full_id!r}: missing ticket_url")
        if not r.get("source_url"):
            failures.append(f"{full_id!r}: missing source_url")
        # Rule 2
        if not r.get("last_verified_at") and not r.get("verified_at"):
            failures.append(f"{full_id!r}: missing verified_at / last_verified_at")
        # Rule 3 + 4
        # slug heuristic — id often is "<slug>-<YYYYMMDD>"; also check exact stem
        stem = re.sub(r"-\d{8}$", "", full_id)
        if stem in blocked_slugs or full_id in blocked_slugs:
            failures.append(f"{full_id!r}: slug is on canceled blocklist ({stem!r})")
        if name in blocked_names:
            failures.append(f"{full_id!r}: name is on canceled blocklist ({name!r})")
        # Rule 5
        if (r.get("status") or "").lower() == "canceled":
            failures.append(f"{full_id!r}: status=canceled but row is in public SHOWS_DATA")
        # Rule 6
        lv = r.get("last_verified_at") or ""
        if lv and lv > today:
            failures.append(f"{full_id!r}: last_verified_at is in the future ({lv!r})")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="audit the repo file instead of live shows.html")
    args = ap.parse_args()
    if args.offline or not LIVE_URL:
        if not SHOWS_HTML.exists():
            print(f"shows.html not found at {SHOWS_HTML}")
            return 2
        html = SHOWS_HTML.read_text()
    else:
        try:
            req = urllib.request.Request(LIVE_URL, headers={"User-Agent": "PC-Audit/1"})
            with urllib.request.urlopen(req, timeout=15) as r:
                html = r.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"live fetch failed: {e!r}; falling back to repo file")
            html = SHOWS_HTML.read_text()
    rows = extract_shows_data(html)
    fails = audit(rows)
    print(f"audited rows: {len(rows)}")
    if not fails:
        print("✅ GREEN — every public show has provenance and is not on the blocklist.")
        return 0
    print(f"❌ HOLD — {len(fails)} provenance failure(s):")
    for f in fails:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
