#!/usr/bin/env python3
"""ParisComedy.com — invariant checker.

Enforces PROJECT_CANON.md and ACCEPTANCE_TESTS.md.

Exit code 0 = GREEN (all MUST-PASS invariants hold).
Exit code 1 = HOLD (one or more MUST-PASS invariants failed).

Run before every push. Run inside CI (when CI exists).
Run with --offline to skip live-URL checks.

Usage:
    python3 scripts/guardrails/check_invariants.py [--offline]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
PUBLIC_HTML_GLOBS = ["*.html", "c/*.html"]
EXCLUDE_FROM_HTML_SCAN = {
    "PROJECT_CANON.md", "SCOPE_LOCK.md", "ACCEPTANCE_TESTS.md",
    "logs", "docs",
}

FORBIDDEN_STRINGS_HTML = [
    "@pariscomedy",
    "instagram.com/pariscomedy",
    "chucklericain@gmail.com",
    "Robert Hoehn",
    "First 100 Featured listings FREE",
    "Every show listing is verified",
    "Every Eventbrite link is live",
    "34+ active shows",
    "27+ venues",
]
FORBIDDEN_CASE_INSENSITIVE = ["stripe"]

LIVE_PAGES = [
    "https://pariscomedy.com/",
    "https://pariscomedy.com/?lang=en",
    "https://pariscomedy.com/shows.html",
    "https://pariscomedy.com/venues.html",
    "https://pariscomedy.com/comedians.html",
    "https://pariscomedy.com/bookers.html",
    "https://pariscomedy.com/pricing.html",
    "https://pariscomedy.com/book.html",
    "https://pariscomedy.com/about.html",
    "https://pariscomedy.com/r.html",
    "https://pariscomedy.com/admin-events.html",
]
LIVE_API = "https://api.pariscomedy.com/api/listings?featured=1"


class Failures:
    def __init__(self):
        self.items: list[str] = []

    def add(self, msg: str) -> None:
        self.items.append(msg)

    def report(self) -> int:
        if not self.items:
            print("✅ GREEN — all invariants hold.")
            return 0
        print(f"❌ HOLD — {len(self.items)} invariant(s) failed:\n")
        for i, msg in enumerate(self.items, 1):
            print(f"  {i:2d}. {msg}")
        return 1


def http_get(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "ParisComedy-Invariant-Checker/1.0"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


# ── checks ─────────────────────────────────────────────────────────────────

def check_repo_html_strings(failures: Failures) -> None:
    """Scan every .html in the repo for forbidden public copy."""
    for pat in PUBLIC_HTML_GLOBS:
        for f in ROOT.glob(pat):
            if any(part in EXCLUDE_FROM_HTML_SCAN for part in f.parts):
                continue
            text = f.read_text(errors="replace")
            for needle in FORBIDDEN_STRINGS_HTML:
                if needle in text:
                    failures.add(
                        f"repo: '{needle}' present in {f.relative_to(ROOT)}"
                    )
            low = text.lower()
            for needle in FORBIDDEN_CASE_INSENSITIVE:
                if needle in low:
                    failures.add(
                        f"repo: '{needle}' (case-insensitive) present in {f.relative_to(ROOT)}"
                    )


def check_live_pages(failures: Failures) -> None:
    """Live-URL scan. Skipped if --offline."""
    bodies: dict[str, str] = {}
    for url in LIVE_PAGES:
        try:
            bodies[url] = http_get(url)
        except Exception as e:
            failures.add(f"live: cannot fetch {url}: {e!r}")
    for url, body in bodies.items():
        for needle in FORBIDDEN_STRINGS_HTML:
            if needle in body:
                failures.add(f"live {url}: '{needle}' present")
        low = body.lower()
        for needle in FORBIDDEN_CASE_INSENSITIVE:
            if needle in low:
                # Stripe substring may appear inside CSS like 'stripe-pattern';
                # require word boundary in URLs/copy
                if re.search(r"\bstripe\b", low):
                    failures.add(f"live {url}: '{needle}' (word) present")
                    break

    # / vs /?lang=en banner copy must match
    home = bodies.get("https://pariscomedy.com/", "")
    lang = bodies.get("https://pariscomedy.com/?lang=en", "")
    if home and lang:
        # Compare visible banner block (first 4KB of body — gross but sufficient
        # to catch banner divergence which is what we care about).
        if home[:4096] != lang[:4096]:
            failures.add("live: / and /?lang=en differ in first 4KB (banner copy)")

    # Shows page must have crawlable show data
    shows = bodies.get("https://pariscomedy.com/shows.html", "")
    if shows and "SHOWS_DATA" not in shows and "show-card" not in shows:
        failures.add("live shows.html: no embedded SHOWS_DATA and no .show-card markup")

    # Comedians page must have crawlable comic data
    comedians = bodies.get("https://pariscomedy.com/comedians.html", "")
    if comedians and "COMICS" not in comedians and "comic-card" not in comedians:
        failures.add("live comedians.html: no embedded COMICS and no .comic-card markup")


def check_live_featured_api(failures: Failures) -> None:
    try:
        raw = http_get(LIVE_API)
        data = json.loads(raw)
    except Exception as e:
        failures.add(f"live API: cannot fetch/parse {LIVE_API}: {e!r}")
        return
    if not isinstance(data, list):
        failures.add(f"live API: expected list, got {type(data).__name__}")
        return
    # No runner_email leaks
    for row in data:
        if not isinstance(row, dict):
            continue
        if row.get("runner_email"):
            failures.add(
                f"live API: runner_email leaked for slug={row.get('slug')!r}"
            )
        runner = (row.get("runner") or "").strip()
        if runner and any(name.lower() in runner.lower()
                          for name in ("robert hoehn", "chuck", "chuckle ricain")):
            failures.add(f"live API: personal runner name leaked: {runner!r}")
    # No single-org dominance: featured list must have ≥2 distinct venues
    venues = {(r.get("venue") or {}).get("slug") for r in data
              if isinstance(r, dict) and isinstance(r.get("venue"), dict)}
    venues.discard(None)
    if len(venues) < 2:
        failures.add(
            f"live API: featured list has only {len(venues)} venue(s); "
            f"PROJECT_CANON requires ≥2 distinct venues / no single-org dominance"
        )


def check_scraper_run_state(failures: Failures) -> None:
    """Most-recent daily_discover_summary must have run_state set."""
    candidates = [
        Path.home() / "Documents/Claude/Projects/pariscomedy.com/daily_discover_summary.json",
        Path.home() / "Documents/Claude/Projects/pariscomedy.com/_repo/daily_discover_summary.json",
    ]
    summary_path = next((p for p in candidates if p.exists()), None)
    if summary_path is None:
        # No scraper run yet — warn but don't fail
        print("⚠  warning: no daily_discover_summary.json found yet (warning only)")
        return
    try:
        s = json.loads(summary_path.read_text())
    except Exception as e:
        failures.add(f"scraper summary: cannot parse {summary_path}: {e!r}")
        return
    state = s.get("run_state")
    if state not in ("GREEN", "FAILED"):
        failures.add(
            f"scraper summary: run_state must be 'GREEN' or 'FAILED', got {state!r} "
            f"(in {summary_path})"
        )
    # If zero new + zero raw_events but state=GREEN, that's a false success
    if state == "GREEN" and s.get("new_shows", 0) == 0 and s.get("raw_events", 0) == 0:
        failures.add(
            "scraper summary: run_state=GREEN but new_shows=0 AND raw_events=0 — "
            "must be FAILED when no sources produced anything"
        )


# ── main ──────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="skip network-dependent checks (live URLs + API)")
    args = ap.parse_args()

    failures = Failures()
    check_repo_html_strings(failures)
    check_scraper_run_state(failures)
    if not args.offline:
        check_live_pages(failures)
        check_live_featured_api(failures)
    return failures.report()


if __name__ == "__main__":
    sys.exit(main())
