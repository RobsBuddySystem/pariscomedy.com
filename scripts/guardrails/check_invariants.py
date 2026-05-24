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

# NOTE: @pariscomedy must be the standalone IG handle, NOT the email suffix.
# Use regex with a negative-lookbehind on email-local characters.
FORBIDDEN_REGEX = [
    (r"(?<![a-zA-Z0-9._%+\-])@pariscomedy\b", "@pariscomedy IG handle"),
    (r"instagram\.com/pariscomedy", "instagram.com/pariscomedy link"),
    (r"chucklericain@gmail\.com", "chucklericain@gmail.com PII"),
    (r"\bRobert Hoehn\b", "Robert Hoehn real name"),
    (r"First 100 Featured listings FREE", "stale launch banner"),
    (r"Every show listing is verified", "false-claim verified"),
    (r"Every Eventbrite link is live", "false-claim every link live"),
    (r"\b34\+ active shows\b", "false-count 34+ shows"),
    (r"\b27\+ venues\b", "false-count 27+ venues"),
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
LIVE_PUBLIC_APIS = [
    "https://api.pariscomedy.com/api/listings",
    "https://api.pariscomedy.com/api/listings?featured=1",
    "https://api.pariscomedy.com/api/shows",
]


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
    patterns = [(re.compile(p), label) for p, label in FORBIDDEN_REGEX]
    stripe_re = re.compile(r"\bstripe\b", re.IGNORECASE)
    for pat in PUBLIC_HTML_GLOBS:
        for f in ROOT.glob(pat):
            if any(part in EXCLUDE_FROM_HTML_SCAN for part in f.parts):
                continue
            text = f.read_text(errors="replace")
            for rx, label in patterns:
                if rx.search(text):
                    failures.add(
                        f"repo: {label} present in {f.relative_to(ROOT)}"
                    )
            if stripe_re.search(text):
                failures.add(
                    f"repo: 'stripe' (word) present in {f.relative_to(ROOT)}"
                )


def check_live_pages(failures: Failures) -> None:
    """Live-URL scan. Skipped if --offline."""
    bodies: dict[str, str] = {}
    for url in LIVE_PAGES:
        try:
            bodies[url] = http_get(url)
        except Exception as e:
            failures.add(f"live: cannot fetch {url}: {e!r}")
    patterns = [(re.compile(p), label) for p, label in FORBIDDEN_REGEX]
    stripe_re = re.compile(r"\bstripe\b", re.IGNORECASE)
    for url, body in bodies.items():
        for rx, label in patterns:
            if rx.search(body):
                failures.add(f"live {url}: {label} present")
        if stripe_re.search(body):
            failures.add(f"live {url}: 'stripe' (word) present")

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


def check_no_pii_any_public_api(failures: Failures) -> None:
    """Every public listings/shows endpoint must be free of PII."""
    pii_patterns = [
        re.compile(r"chucklericain", re.I),
        re.compile(r"\bRobert Hoehn\b"),
        re.compile(r'"runner_email"\s*:\s*"[^"]+"'),
    ]
    for url in LIVE_PUBLIC_APIS:
        try:
            body = http_get(url, timeout=10)
        except Exception as e:
            failures.add(f"PII check: cannot fetch {url}: {e!r}")
            continue
        for rx in pii_patterns:
            if rx.search(body):
                failures.add(f"PII leak on {url}: pattern {rx.pattern!r}")


def check_shows_list_correctness(failures: Failures) -> None:
    """SHOWS_DATA on /shows.html must be present, parse, and not be empty."""
    try:
        body = http_get("https://pariscomedy.com/shows.html")
    except Exception as e:
        failures.add(f"shows.html: cannot fetch: {e!r}")
        return
    import re as _re
    m = _re.search(r'const SHOWS_DATA\s*=\s*(\[.*?\]);', body, _re.S)
    if not m:
        failures.add("shows.html: SHOWS_DATA array not found")
        return
    try:
        data = json.loads(m.group(1))
    except Exception as e:
        failures.add(f"shows.html: SHOWS_DATA invalid JSON: {e!r}")
        return
    if not data:
        failures.add("shows.html: SHOWS_DATA is empty")
        return
    # Duplicate detection: (show_name, venue, date, start_time)
    seen = {}
    for r in data:
        key = (r.get("show_name", ""), r.get("venue", ""),
               r.get("date", ""), r.get("start_time") or "")
        if key in seen and key[2] and key[3]:
            failures.add(f"shows.html: duplicate show row: {key!r}")
        seen[key] = True


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
    # No single-org dominance: when the featured list is non-empty it must
    # span ≥2 distinct venues. An empty featured list is canonically allowed.
    if data:
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
    if state not in ("GREEN", "FAILED", "PARTIAL"):
        failures.add(
            f"scraper summary: run_state must be 'GREEN'|'FAILED'|'PARTIAL', "
            f"got {state!r} (in {summary_path})"
        )
    # If state=GREEN, classifier must have been reachable and we must have raw events
    if state == "GREEN" and s.get("raw_events", 0) == 0:
        failures.add(
            "scraper summary: run_state=GREEN but raw_events=0 — must be FAILED"
        )
    if state == "GREEN" and s.get("classifier_unreachable", 0) > 0:
        failures.add(
            "scraper summary: run_state=GREEN but classifier was unreachable — must be PARTIAL"
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
        check_no_pii_any_public_api(failures)
        check_shows_list_correctness(failures)
        check_canceled_blocklist(failures)
        check_show_provenance(failures)
    # Strict per-row proof audit runs in offline mode too — uses cached url_health.json
    check_audit_public_shows_strict(failures)
    check_provenance_block_test(failures)
    check_archive_rows_clean(failures)
    if not args.offline:
        check_listings_endpoint_consistency(failures)
        check_homepage_truthfulness(failures)
    return failures.report()


def check_homepage_truthfulness(failures: Failures) -> None:
    """The homepage must not contradict the featured API. Stale launch copy,
    hardcoded dates, and overclaims are all forbidden."""
    HOMEPAGE = "https://pariscomedy.com/"
    FEATURED = "https://api.pariscomedy.com/api/listings?featured=1"
    # Always-forbidden in served HTML — no token-array workarounds allowed.
    # Per the homepage truthfulness rules: "Featured" only applies to
    # paid/editorial rows from /api/listings?featured=1. Day-of-week sections
    # must use "Tonight in Paris" or similar — never "Featured Tonight".
    # Overclaims like "every English stand-up show" and "Every show in the
    # directory is treated equally" are forbidden.
    FORBIDDEN = [
        ("May 19–25",                       "hardcoded date range"),
        ("first 100 show runners",          "stale launch copy"),
        ("First 100 Featured listings",     "stale launch banner"),
        ("claim your free Featured listing","stale free-tier copy"),
        ("every show in Paris",             "overclaim"),
        ("every English stand-up show",     "overclaim"),
        ("Every show in the directory",     "overclaim"),
        ("Stand-up every night of the week","overclaim — DB not nightly verified"),
        ("something on every night of the week","overclaim"),
        ("best English-language acts in Paris","unsupported superlative"),
        ("best English-language acts",      "unsupported superlative"),
        ("Featured Tonight",                "day-of-week mislabeled as Featured"),
        ("Featured Shows This Week",        "section name forbidden — use Promoted"),
        ("Rotating weekly",                 "obsolete weekly-rotation copy"),
        ("Verified, highlighted comedy nights in Paris", "overclaim"),
        ("These shows are Featured",        "implies featured exist regardless of API"),
        ("archive-2026-04-13",              "internal provenance leak"),
        ("verification_source",             "internal provenance leak"),
        ("runner_email",                    "PII leak"),
        ("Robert Hoehn",                    "PII leak"),
        ("chucklericain",                   "PII leak"),
        ("velvet-openmic",                  "canceled slug"),
        ("Velvet Bar Comedy — Open Mic",    "canceled show name"),
    ]
    try:
        home = http_get(HOMEPAGE)
    except Exception as e:
        failures.add(f"homepage truthfulness: cannot fetch {HOMEPAGE}: {e!r}")
        return
    for needle, why in FORBIDDEN:
        if needle in home:
            failures.add(f"homepage contains forbidden copy ({why}): {needle!r}")
    # API ↔ homepage consistency: if featured API is empty, homepage must
    # NOT claim featured shows exist via the "Verified, highlighted comedy
    # nights in Paris" subtitle or the "These shows are Featured" CTA.
    try:
        feat = json.loads(http_get(FEATURED))
    except Exception:
        feat = None
    # Rendered-DOM check via Playwright — catches strings that JS injects.
    # Same patterns as the static FORBIDDEN list must also be absent from the
    # rendered DOM (no token-array workarounds tolerated).
    try:
        import importlib
        pw = importlib.import_module("playwright.sync_api")
        with pw.sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            page = b.new_context(user_agent="PC-Invariants/1").new_page()
            page.goto("https://pariscomedy.com/", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2500)
            body = page.inner_text("body")
            b.close()
        for rendered_forbidden in (
            "Featured Tonight", "Featured Shows This Week", "Rotating weekly",
            "Verified, highlighted comedy nights in Paris",
            "These shows are Featured",
            "every English stand-up show", "Every show in the directory",
            "claim your free Featured listing",
            "Stand-up every night of the week",
            "something on every night of the week",
            "best English-language acts in Paris",
        ):
            if rendered_forbidden in body:
                # If the featured API is non-empty, "Promoted"-style headings
                # are allowed — but the strings above are still forbidden.
                failures.add(
                    f"rendered DOM contains forbidden string: {rendered_forbidden!r}"
                )
    except Exception:
        pass  # Playwright optional — static guard above is the floor


def check_listings_endpoint_consistency(failures: Failures) -> None:
    """The featured-filtered endpoint must serve the same public fields as the
    unfiltered endpoint. Any divergence is a split-brain bug (different
    serializer, stale cache, stale process, or two backends)."""
    FORBIDDEN_KEYS = {
        "runner", "runner_email", "source", "verification_source",
        "cancellation_reason", "quarantine_reason", "quarantined_at",
        "quarantined_by", "previous_status", "verified_by",
        "public_visible", "blocked_from_auto_regeneration",
    }
    FORBIDDEN_VALUE_SUBSTRINGS = ["archive-2026-04-13", "Robert-editorial",
                                  "Robert Hoehn", "chucklericain"]
    try:
        full     = json.loads(http_get("https://api.pariscomedy.com/api/listings"))
        featured = json.loads(http_get("https://api.pariscomedy.com/api/listings?featured=1"))
    except Exception as e:
        failures.add(f"listings-consistency: live fetch failed: {e!r}")
        return

    # 1. No forbidden keys leaked in either endpoint
    for label, payload in (("/api/listings", full), ("/api/listings?featured=1", featured)):
        for row in payload:
            leaked = set(row.keys()) & FORBIDDEN_KEYS
            if leaked:
                failures.add(f"{label}: forbidden keys leaked: {sorted(leaked)}")

    # 2. No forbidden substrings anywhere in either response body
    for label, payload in (("/api/listings", full), ("/api/listings?featured=1", featured)):
        body_str = json.dumps(payload)
        for needle in FORBIDDEN_VALUE_SUBSTRINGS:
            if needle in body_str:
                failures.add(f"{label}: forbidden substring leaked: {needle!r}")

    # 3. For every slug present in both, public fields must match
    by_slug_full = {r["slug"]: r for r in full if r.get("slug")}
    by_slug_feat = {r["slug"]: r for r in featured if r.get("slug")}
    for slug in set(by_slug_full) & set(by_slug_feat):
        a, b = by_slug_full[slug], by_slug_feat[slug]
        for k in ("name", "status", "featured", "verified_at", "venue"):
            if a.get(k) != b.get(k):
                failures.add(
                    f"split-brain on slug={slug!r} field={k}: "
                    f"/api/listings={a.get(k)!r} vs "
                    f"/api/listings?featured=1={b.get(k)!r}"
                )

    # 4. Featured endpoint must not return rows whose featured flag is 0
    for r in featured:
        if r.get("featured") != 1:
            failures.add(
                f"/api/listings?featured=1 returned row featured={r.get('featured')} "
                f"(slug={r.get('slug')!r})"
            )

    # 5. canceled blocklist slugs must be absent in both
    blocklist = ROOT / "data" / "canceled_shows.json"
    if blocklist.exists():
        try:
            cancel = json.loads(blocklist.read_text())
            slugs = {e["slug"] for e in cancel.get("canceled", [])}
            for label, payload in (("/api/listings", full),
                                   ("/api/listings?featured=1", featured)):
                for row in payload:
                    if (row.get("slug") or "") in slugs:
                        failures.add(f"{label}: canceled slug present: {row['slug']!r}")
        except Exception:
            pass


def check_archive_rows_clean(failures: Failures) -> None:
    """Any active+public_visible archive row must have today's verified_at OR an approval.
    Cheap DB read — no network probe (audit_archive_rows.py does the probes)."""
    import sqlite3 as _sqlite3
    db_path = Path.home() / ".openclaw/workspace/apps/paris-comedy/data/paris.db"
    if not db_path.exists():
        return
    today = __import__("datetime").datetime.now().date().isoformat()
    try:
        conn = _sqlite3.connect(str(db_path))
        rows = conn.execute(
            """SELECT id, slug, name, verified_at FROM show_listings
               WHERE (source LIKE 'archive-%' OR source LIKE 'plateaux-%')
                 AND status='active'
                 AND COALESCE(public_visible, 1) = 1"""
        ).fetchall()
        conn.close()
    except Exception as e:
        failures.add(f"archive-rows check: DB read failed: {e!r}")
        return
    for rid, slug, name, lv in rows:
        if (lv or "") != today:
            failures.add(
                f"archive row {slug!r} (id={rid}) is publicly active but verified_at={lv!r} "
                f"is not today ({today}); run scripts/guardrails/audit_archive_rows.py"
            )


def check_provenance_block_test(failures: Failures) -> None:
    """Run the negative-test that proves a fabricated SHOWS_DATA row is rejected."""
    import subprocess
    script = ROOT / "scripts" / "guardrails" / "test_provenance_blocks.py"
    if not script.exists():
        failures.add("test_provenance_blocks.py missing — guardrail demo not enforced")
        return
    p = subprocess.run(
        ["python3", str(script)],
        capture_output=True, text=True, timeout=30,
    )
    if p.returncode != 0:
        failures.add("test_provenance_blocks.py FAILED — fabricated row was not rejected")


def check_audit_public_shows_strict(failures: Failures) -> None:
    """Invoke audit_public_shows.py in strict mode and fail on any row that
    lacks (a) recent live URL check, (b) signed manual approval, or (c)
    recurrence_source_url."""
    import subprocess
    script = ROOT / "scripts" / "guardrails" / "audit_public_shows.py"
    if not script.exists():
        failures.add("audit_public_shows.py missing — provenance gate not enforced")
        return
    p = subprocess.run(
        ["python3", str(script), "--offline", "--strict=true"],
        capture_output=True, text=True, timeout=30,
    )
    if p.returncode != 0:
        # Surface the first 6 failure lines from the audit output
        lines = [ln for ln in p.stdout.splitlines() if ln.strip().startswith("- ")][:6]
        for ln in lines:
            failures.add(f"audit_public_shows: {ln.strip().lstrip('- ')}")
        if not lines:
            failures.add(f"audit_public_shows exited {p.returncode}; see output")


def check_canceled_blocklist(failures: Failures) -> None:
    """Every slug/name in data/canceled_shows.json must be absent from public surface."""
    blocklist_path = ROOT / "data" / "canceled_shows.json"
    if not blocklist_path.exists():
        return
    try:
        blocklist = json.loads(blocklist_path.read_text())
    except Exception as e:
        failures.add(f"canceled_shows.json invalid JSON: {e!r}")
        return
    slugs = [e["slug"] for e in blocklist.get("canceled", [])]
    names = []
    for e in blocklist.get("canceled", []):
        names.extend(e.get("names", []))
    # 1. shows.html SHOWS_DATA + every mirror file
    files_to_scan = [
        ROOT / "shows.html",
        ROOT / "js" / "data.js",
        ROOT / "data" / "shows_generated.json",
        ROOT / "generate_instances.py",
        ROOT / "comedians.html",
    ]
    for path in files_to_scan:
        if not path.exists():
            continue
        text = path.read_text()
        for s in slugs:
            if s in text:
                failures.add(f"canceled blocklist: '{s}' in {path.relative_to(ROOT)}")
        for n in names:
            if n in text:
                failures.add(f"canceled blocklist: '{n}' in {path.relative_to(ROOT)}")
    # 2. Live public API — every endpoint, slug AND title match
    bodies: dict[str, str] = {}
    for url in (
        "https://api.pariscomedy.com/api/listings",
        "https://api.pariscomedy.com/api/listings?featured=1",
        "https://api.pariscomedy.com/api/shows",
    ):
        try:
            bodies[url] = http_get(url)
        except Exception as e:
            failures.add(f"canceled blocklist live check failed for {url}: {e!r}")
    for url, body in bodies.items():
        for s in slugs:
            if f'"slug":"{s}"' in body:
                failures.add(f"canceled blocklist: slug '{s}' present in {url}")
        for n in names:
            if n in body:
                failures.add(f"canceled blocklist: name {n!r} present in {url}")


def check_show_provenance(failures: Failures) -> None:
    """Every SHOWS_DATA row must have ticket_url, source_url, last_verified_at."""
    sh = ROOT / "shows.html"
    if not sh.exists():
        return
    m = re.search(r"const SHOWS_DATA\s*=\s*(\[.*?\]);", sh.read_text(), re.S)
    if not m:
        return
    try:
        data = json.loads(m.group(1))
    except Exception:
        return
    today = __import__("datetime").datetime.now().date().isoformat()
    for r in data:
        rid = r.get("id", "")
        if not r.get("ticket_url"):
            failures.add(f"provenance {rid!r}: missing ticket_url")
        if not r.get("source_url"):
            failures.add(f"provenance {rid!r}: missing source_url")
        if not (r.get("last_verified_at") or r.get("verified_at")):
            failures.add(f"provenance {rid!r}: missing verified_at")
        lv = r.get("last_verified_at") or ""
        if lv and lv > today:
            failures.add(f"provenance {rid!r}: last_verified_at in the future ({lv!r})")


if __name__ == "__main__":
    sys.exit(main())
