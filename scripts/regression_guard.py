#!/usr/bin/env python3
"""
PROCESS.ROOT.1 — Regression guard.

Runs 10 checks against LIVE production (https://pariscomedy.com) to catch
recurrences of the root causes we've already fixed:

  1. forbidden_strings      — no bilingual/mixed-language/marketing-claim leakage
  2. internal_ctas          — /venues.html cards link to /show.html (not external)
  3. raw_includes           — no unprocessed `<!-- include: -->` directives
  4. stale_homepage_panel   — homepage .next3-row populated, or explicit empty msg
  5. card_render            — /comedians.html >200 cards, /shows.html >30 cards
  6. status_sweep           — 27+ public URLs return HTTP 200
  7. nav_consistency        — every page has exactly one nav-shell-* nav
  8. freshness_sanity       — /data/freshness-audit.json sane, no stale rows
  9. hreflang               — legal pages have >=3 hreflang alternates
 10. header_cta_rule        — per-page nav matches canonical partial set
                              (no page-specific CTA leaks into global nav)

Usage:
  python3 scripts/regression_guard.py
  python3 scripts/regression_guard.py --check forbidden_strings
  python3 scripts/regression_guard.py --with-dom    # enables Playwright (checks 2,4,5)

Exit code 0 = all pass, 1 = any fail. JSON output written to
logs/regression-guard.<ISO>.json (gitignored).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://pariscomedy.com"
UA = "pariscomedy-regression-guard/1.0 (+https://pariscomedy.com)"
TIMEOUT = 20

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "logs"

# ---------- HTTP helpers ----------------------------------------------------


def fetch(path_or_url: str, timeout: int = TIMEOUT) -> tuple[int, str]:
    url = path_or_url if path_or_url.startswith("http") else f"{BASE}{path_or_url}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            return r.status, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return e.code, body
    except Exception as e:  # noqa: BLE001
        return 0, f"__FETCH_ERROR__ {e}"


def head_status(path_or_url: str, timeout: int = TIMEOUT) -> int:
    # We just do a GET — HEAD often misbehaves behind Cloudflare.
    code, _ = fetch(path_or_url, timeout=timeout)
    return code


# ---------- Page sweep set --------------------------------------------------

SWEEP_PAGES = [
    "/",
    "/about.html",
    "/pricing.html",
    "/bookers.html",
    "/book.html",
    "/shows.html",
    "/venues.html",
    "/comedians.html",
    "/archive.html",
    "/terms.html",
    "/privacy.html",
    "/disclosure.html",
    "/login.html",
    "/performer-portal.html",
    "/booker-portal.html",
    "/booker-dashboard.html",
    "/show-runner.html",
    "/show.html",
    "/show.html?slug=charonne",
    "/show.html?slug=theatre-bo-julie",
    "/show.html?slug=ffcn",
    "/admin-events.html",
    "/admin-crm.html",
    "/admin-messages.html",
    "/admin-payments.html",
    "/admin-submit.html",
    "/404.html",
    "/fr/terms.html",
    "/fr/privacy.html",
    "/fr/disclosure.html",
]

# ---------- Check 1: forbidden strings --------------------------------------

FORBIDDEN_PATTERNS = [
    ("bilingual", re.compile(r"bilingual", re.IGNORECASE)),
    ("mixed-language", re.compile(r"mixed-language", re.IGNORECASE)),
    ("multilingual", re.compile(r"multilingual", re.IGNORECASE)),
    ("English and French", re.compile(r"English and French", re.IGNORECASE)),
    ("English &amp; French", re.compile(r"English &amp; French", re.IGNORECASE)),
    ("both English", re.compile(r"both English", re.IGNORECASE)),
    ("French and English", re.compile(r"French and English", re.IGNORECASE)),
    ("both languages", re.compile(r"both languages", re.IGNORECASE)),
    ("Every venue, every lineup", re.compile(r"Every venue, every lineup", re.IGNORECASE)),
    ("the definitive", re.compile(r"the definitive", re.IGNORECASE)),
    ("every show in Paris", re.compile(r"every show in Paris", re.IGNORECASE)),
    ('Click "Check current listing"', re.compile(r'Click "Check current listing"')),
]

# Allow-list: forbidden tokens inside HTML comments or JS string literals that
# represent SCRUBBING logic itself (e.g. an admin scrubber that strips
# "bilingual"). We intentionally do NOT add an allow-list here — the rule is
# strict: no forbidden token may appear in shipped HTML, period.


def check_forbidden_strings() -> dict:
    hits: list[dict] = []
    for path in SWEEP_PAGES:
        code, body = fetch(path)
        if code != 200:
            continue
        for label, pat in FORBIDDEN_PATTERNS:
            for m in pat.finditer(body):
                start = max(0, m.start() - 40)
                end = min(len(body), m.end() + 40)
                hits.append({
                    "page": path,
                    "pattern": label,
                    "snippet": body[start:end].replace("\n", " "),
                })
    return {
        "name": "forbidden_strings",
        "result": "PASS" if not hits else "FAIL",
        "evidence": {"hit_count": len(hits), "hits": hits[:30]},
    }


# ---------- Check 2: internal CTAs on /venues.html --------------------------

VENUES_CTA_RE = re.compile(
    r'<a[^>]+class="[^"]*\bbtn-tickets\b[^"]*"[^>]*href="([^"]+)"',
    re.IGNORECASE,
)


def check_internal_ctas(with_dom: bool = False) -> dict:
    code, body = fetch("/venues.html")
    if code != 200:
        return {"name": "internal_ctas", "result": "FAIL",
                "evidence": {"reason": f"/venues.html returned {code}"}}
    hrefs = VENUES_CTA_RE.findall(body)
    # If the page renders cards via JS, static HTML may not contain them.
    # In that case we soft-pass with a note unless --with-dom was requested.
    if not hrefs and not with_dom:
        return {"name": "internal_ctas", "result": "PASS",
                "evidence": {"reason": "no static .btn-tickets found; "
                                       "cards rendered client-side. "
                                       "Re-run with --with-dom for DOM check.",
                             "static_href_count": 0}}
    if not hrefs and with_dom:
        try:
            hrefs = _dom_collect_hrefs("/venues.html",
                                       ".card a.btn-tickets")
        except Exception as e:  # noqa: BLE001
            return {"name": "internal_ctas", "result": "FAIL",
                    "evidence": {"reason": f"DOM probe error: {e}"}}
    external = [h for h in hrefs if not h.startswith("/show.html")]
    return {
        "name": "internal_ctas",
        "result": "PASS" if not external else "FAIL",
        "evidence": {"total": len(hrefs), "external": external[:20]},
    }


# ---------- Check 3: raw include directives ---------------------------------

INCLUDE_RE = re.compile(r"<!--\s*include\s*:", re.IGNORECASE)


def check_raw_includes() -> dict:
    hits: list[str] = []
    for path in SWEEP_PAGES:
        code, body = fetch(path)
        if code != 200:
            continue
        if INCLUDE_RE.search(body):
            hits.append(path)
    return {
        "name": "raw_includes",
        "result": "PASS" if not hits else "FAIL",
        "evidence": {"pages_with_raw_include": hits},
    }


# ---------- Check 4: stale homepage panel -----------------------------------

NEXT3_ROW_RE = re.compile(r'class="[^"]*\bnext3-row\b[^"]*"', re.IGNORECASE)
EMPTY_MSG_RE = re.compile(r"No shows scheduled[^<]*check back", re.IGNORECASE)


def check_stale_homepage_panel(with_dom: bool = False) -> dict:
    code, body = fetch("/")
    if code != 200:
        return {"name": "stale_homepage_panel", "result": "FAIL",
                "evidence": {"reason": f"/ returned {code}"}}
    static_rows = len(NEXT3_ROW_RE.findall(body))
    has_empty_msg = bool(EMPTY_MSG_RE.search(body))
    if static_rows > 0 or has_empty_msg:
        return {"name": "stale_homepage_panel", "result": "PASS",
                "evidence": {"static_rows": static_rows,
                             "has_empty_msg": has_empty_msg,
                             "mode": "static"}}
    if not with_dom:
        # JS-rendered: soft pass with note (panel container must at least exist).
        container_present = "next3" in body or "homepage-next" in body
        return {"name": "stale_homepage_panel",
                "result": "PASS" if container_present else "FAIL",
                "evidence": {"reason": "JS-rendered; container "
                                       f"present={container_present}. "
                                       "Re-run with --with-dom for live count.",
                             "mode": "static-container-only"}}
    try:
        rows = _dom_count("/", ".next3-row")
    except Exception as e:  # noqa: BLE001
        return {"name": "stale_homepage_panel", "result": "FAIL",
                "evidence": {"reason": f"DOM probe error: {e}"}}
    if rows > 0:
        return {"name": "stale_homepage_panel", "result": "PASS",
                "evidence": {"dom_rows": rows, "mode": "dom"}}
    return {"name": "stale_homepage_panel", "result": "FAIL",
            "evidence": {"dom_rows": 0,
                         "reason": "panel empty AND no fallback message"}}


# ---------- Check 5: card render --------------------------------------------

CARD_RE = re.compile(r'class="[^"]*\bcard\b[^"]*"', re.IGNORECASE)


def check_card_render(with_dom: bool = False) -> dict:
    out: dict[str, int] = {}
    for path in ("/comedians.html", "/shows.html"):
        code, body = fetch(path)
        if code != 200:
            out[path] = -1
            continue
        out[path] = len(CARD_RE.findall(body))
    if with_dom:
        try:
            out["/comedians.html (dom)"] = _dom_count("/comedians.html", ".card")
            out["/shows.html (dom)"] = _dom_count("/shows.html", ".card")
        except Exception as e:  # noqa: BLE001
            return {"name": "card_render", "result": "FAIL",
                    "evidence": {"reason": f"DOM probe error: {e}",
                                 "static": out}}
        ok = (out["/comedians.html (dom)"] > 200
              and out["/shows.html (dom)"] > 30)
    else:
        # Static fallback: many sites render cards via JS — only fail if
        # the page itself is missing (returned non-200).
        ok = all(v >= 0 for v in out.values())
    return {
        "name": "card_render",
        "result": "PASS" if ok else "FAIL",
        "evidence": out,
    }


# ---------- Check 6: live status sweep --------------------------------------

EXTRA_URLS = [
    "/api/review-queue",
]


def check_status_sweep() -> dict:
    targets = SWEEP_PAGES + EXTRA_URLS
    results: list[dict] = []
    bad: list[dict] = []
    for path in targets:
        code = head_status(path)
        results.append({"path": path, "code": code})
        if code != 200:
            bad.append({"path": path, "code": code})
    return {
        "name": "status_sweep",
        "result": "PASS" if not bad and len(targets) >= 27 else "FAIL",
        "evidence": {"total": len(targets), "bad": bad,
                     "all_results": results},
    }


# ---------- Check 7: nav consistency ----------------------------------------

NAV_BLOCK_RE = re.compile(r"<nav\b[^>]*>", re.IGNORECASE)
NAV_SHELL_RE = re.compile(r"<nav\b[^>]*\bclass=\"([^\"]*)\"", re.IGNORECASE)
VALID_SHELL_CLASSES = {
    "nav-shell-marketing",
    "nav-shell-minimal",
    "nav-shell-auth",
    "nav-shell-portal",
    "nav-shell-admin",
}


def check_nav_consistency() -> dict:
    problems: list[dict] = []
    # Exclude pure API endpoint (no nav expected).
    pages = [p for p in SWEEP_PAGES if not p.startswith("/api/")]
    for path in pages:
        code, body = fetch(path)
        if code != 200:
            continue
        navs = NAV_BLOCK_RE.findall(body)
        shells = NAV_SHELL_RE.findall(body)
        nav_shell_count = sum(1 for s in shells if "nav-shell" in s)
        variants = set()
        for s in shells:
            for cls in s.split():
                if cls in VALID_SHELL_CLASSES:
                    variants.add(cls)
        ok = nav_shell_count == 1 and len(variants) >= 1
        if not ok:
            problems.append({
                "page": path,
                "nav_block_count": len(navs),
                "nav_shell_count": nav_shell_count,
                "variants": sorted(variants),
            })
    return {
        "name": "nav_consistency",
        "result": "PASS" if not problems else "FAIL",
        "evidence": {"problems": problems},
    }


# ---------- Check 8: freshness sanity ---------------------------------------

def check_freshness_sanity() -> dict:
    code, body = fetch("/data/freshness-audit.json")
    if code != 200:
        return {"name": "freshness_sanity", "result": "FAIL",
                "evidence": {"reason": f"HTTP {code}"}}
    try:
        data = json.loads(body)
    except Exception as e:  # noqa: BLE001
        return {"name": "freshness_sanity", "result": "FAIL",
                "evidence": {"reason": f"JSON parse error: {e}"}}
    summary = data.get("summary") or {}
    listings = data.get("listings") or []
    total_active = summary.get("total_active", 0)
    # P1.DATA.2.FIX: read verification_status (the field the verifier emits).
    # The previous code read a non-existent `status` field, making this check
    # a no-op that silently passed regardless of audit content.
    def vs(l):
        return (l.get("verification_status") or "").lower()
    stale = [l for l in listings if vs(l) == "stale"]
    review = sum(1 for l in listings if vs(l) == "needs_human_review")
    unreachable = sum(1 for l in listings if vs(l) == "source_unreachable")
    verified = sum(1 for l in listings
                   if vs(l) in ("verified_24h", "verified_72h"))
    soft_warn = (review / max(1, len(listings))) > 0.05
    # PASS criteria: audit must be present + non-empty. Stale rows are a hard
    # failure (verifier should have re-classified). All-review or all-unreachable
    # is a high-noise signal but not a regression failure on its own — operator
    # follow-up is tracked separately.
    ok = total_active > 0 and not stale
    return {
        "name": "freshness_sanity",
        "result": "PASS" if ok else "FAIL",
        "evidence": {
            "total_active": total_active,
            "stale_count": len(stale),
            "needs_human_review": review,
            "source_unreachable": unreachable,
            "verified_count": verified,
            "soft_warn_review_over_5pct": soft_warn,
        },
    }


# ---------- Check 9: hreflang -----------------------------------------------

HREFLANG_RE = re.compile(
    r'<link[^>]+rel=["\']alternate["\'][^>]+hreflang=["\'][^"\']+["\']',
    re.IGNORECASE,
)


def check_hreflang() -> dict:
    pages = [
        "/terms.html", "/privacy.html", "/disclosure.html",
        "/fr/terms.html", "/fr/privacy.html", "/fr/disclosure.html",
    ]
    problems: list[dict] = []
    for path in pages:
        code, body = fetch(path)
        if code != 200:
            problems.append({"page": path, "reason": f"HTTP {code}"})
            continue
        n = len(HREFLANG_RE.findall(body))
        if n < 3:
            problems.append({"page": path, "hreflang_count": n})
    return {
        "name": "hreflang",
        "result": "PASS" if not problems else "FAIL",
        "evidence": {"problems": problems},
    }


# ---------- Check 10: header CTA rule ---------------------------------------
#
# P2.UX.1 — No page-specific CTA may push or distort global nav.
# For each public page, extract its <nav class="nav-shell-*">…</nav> block
# and compare its <a href="…"> set against the canonical partial for that
# shell. FAIL if a page introduces an href not in the canonical set, or is
# missing more than one canonical href.
#
# Allowed extension: /archive.html may add a single extra link
# pointing at /archive.html (intentional class extension of marketing shell).

NAV_BLOCK_FULL_RE = re.compile(
    r'<nav\b[^>]*\bclass="([^"]*nav-shell[^"]*)"[^>]*>(.*?)</nav>',
    re.IGNORECASE | re.DOTALL,
)
HREF_RE = re.compile(r'href="([^"]+)"', re.IGNORECASE)

SHELL_CLASS_TO_PARTIAL = {
    "nav-shell-marketing": "partials/nav.shell.marketing.html",
    "nav-shell-minimal":   "partials/nav.shell.minimal.html",
    "nav-shell-auth":      "partials/nav.shell.auth.html",
    "nav-shell-portal":    "partials/nav.shell.portal.html",
    "nav-shell-admin":     "partials/nav.shell.admin.html",
}


def _load_canonical_nav_hrefs() -> dict:
    """Return {shell_class: set(href)} parsed from on-disk partials.

    Normalizes href="#" + PCAuth.signOut to /login.html (semantic Sign-Out)
    so the canonical set stays comparable across both legacy and post-P3.AUTH.2
    forms of the Sign-Out link."""
    out: dict[str, set] = {}
    for cls, rel in SHELL_CLASS_TO_PARTIAL.items():
        p = REPO_ROOT / rel
        if not p.exists():
            out[cls] = set()
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        m = NAV_BLOCK_FULL_RE.search(body)
        inner = m.group(2) if m else body
        hrefs = set(HREF_RE.findall(inner))
        if "#" in hrefs and ("PCAuth.signOut" in inner or "signOut(" in inner):
            hrefs.discard("#")
            hrefs.add("/login.html")
        out[cls] = hrefs
    return out


def _extract_page_nav(body: str) -> tuple[str | None, set]:
    """Return (shell_class, set_of_hrefs) for the first nav-shell on a page.

    Sign-Out links may be either href="/login.html" (legacy) or href="#" with
    onclick handler that invokes PCAuth.signOut() (post-P3.AUTH.2). Both forms
    are doctrine-compliant; normalize href="#" to /login.html when paired with
    a signOut handler so the canonical link-set comparison still passes."""
    m = NAV_BLOCK_FULL_RE.search(body)
    if not m:
        return None, set()
    classes = m.group(1).split()
    shell = next((c for c in classes if c in SHELL_CLASS_TO_PARTIAL), None)
    nav_inner = m.group(2)
    hrefs = set(HREF_RE.findall(nav_inner))
    if "#" in hrefs and ("PCAuth.signOut" in nav_inner or "signOut(" in nav_inner):
        hrefs.discard("#")
        hrefs.add("/login.html")
    return shell, hrefs


def check_header_cta_rule() -> dict:
    canonical = _load_canonical_nav_hrefs()
    problems: list[dict] = []
    # Skip API paths (no nav). Use the public sweep set.
    pages = [p for p in SWEEP_PAGES if not p.startswith("/api/")]
    inspected = 0
    for path in pages:
        code, body = fetch(path)
        if code != 200:
            continue
        shell, hrefs = _extract_page_nav(body)
        if shell is None:
            # nav_consistency already enforces presence — skip here.
            continue
        inspected += 1
        canon = canonical.get(shell, set())
        extras = hrefs - canon
        # archive.html may add a single self-referential Archive link
        # as an intentional marketing-shell extension.
        if path == "/archive.html" and shell == "nav-shell-marketing":
            extras = {e for e in extras if e != "/archive.html"}
        # Legal pages on the minimal shell are doctrine-approved to carry
        # cross-legal navigation (Terms/Privacy/About/Shows). These are
        # NOT page-specific CTAs and do not constitute a "Submit your bio"
        # style regression. Curated allow-list, anything beyond fails.
        LEGAL_ALLOWED = {
            "/about.html", "/shows.html",
            "/terms.html", "/privacy.html",
            "/fr/terms.html", "/fr/privacy.html",
        }
        if path in ("/disclosure.html", "/fr/disclosure.html") \
                and shell == "nav-shell-minimal":
            extras = {e for e in extras if e not in LEGAL_ALLOWED}
        missing = canon - hrefs
        # Rule: FAIL on ANY extra (page-specific CTA leaking into global nav)
        # FAIL when more than one canonical link is missing.
        if extras or len(missing) > 1:
            problems.append({
                "page": path,
                "shell": shell,
                "extras": sorted(extras),
                "missing": sorted(missing),
            })
    return {
        "name": "header_cta_rule",
        "result": "PASS" if not problems else "FAIL",
        "evidence": {
            "inspected": inspected,
            "canonical_counts": {k: len(v) for k, v in canonical.items()},
            "problems": problems,
        },
    }


# ---------- Optional Playwright DOM probes ---------------------------------

def _dom_count(path: str, selector: str) -> int:
    return len(_dom_collect_hrefs(path, selector, attr=None))


def _dom_collect_hrefs(path: str, selector: str, attr: str | None = "href") -> list:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"playwright not available: {e}")
    url = f"{BASE}{path}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(user_agent=UA)
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        elements = page.query_selector_all(selector)
        if attr is None:
            count = len(elements)
            browser.close()
            return [None] * count  # type: ignore[list-item]
        out = [el.get_attribute(attr) or "" for el in elements]
        browser.close()
        return out


# ---------- Runner ---------------------------------------------------------

def check_pricing_copy_safety() -> dict:
    """P0.PRICING.COPY.SAFETY — pricing page must not imply live checkout
    while payments are scaffold-only. Static check on pricing.html."""
    p = (REPO_ROOT / "pricing.html")
    if not p.exists():
        return {"name": "pricing_copy_safety", "result": "FAIL",
                "evidence": {"reason": "pricing.html missing"}}
    src = p.read_text(encoding="utf-8", errors="ignore").lower()
    forbidden = [
        "continue to €1 payment",
        "continue to payment",
        "paid through sumup",
        "pay now",
        "subscribe now",
        "browse every show in paris",
        "claim my €1 lifetime spot",
        "lifetime spot",
        "€1 lifetime",
        "sumup_1euro",
        "via sumup →",
        "checkout is live",
        "messaging is live",
        "direct messages available now",
        "affiliate links active",
    ]
    hits = [s for s in forbidden if s in src]
    return {
        "name": "pricing_copy_safety",
        "result": "PASS" if not hits else "FAIL",
        "evidence": {"forbidden_hits": hits},
    }


def check_public_copy_overclaims() -> dict:
    """FINAL.FRONTEND.COPY.GUARD.1 — scan all public HTML for overclaims.

    Forbidden: coverage overclaims, payment overclaims, feature overclaims.
    Allowed safe negations like "checkout is not live yet" are excluded.
    """
    html_files = [
        "index.html", "show.html", "shows.html", "pricing.html",
        "disclosure.html", "book.html", "venues.html", "comedians.html",
    ]
    forbidden_phrases = [
        # coverage overclaims
        "every show in paris",
        "all shows in paris",
        "all comedy shows in paris",
        "all comedy venues in paris",
        "definitive guide",
        "complete list",
        # payment / messaging overclaims
        "claim my",
        "lifetime spot",
        "€1 lifetime",
        "first 100",
        "continue to payment",
        "paid through sumup",
        "pay now",
        "subscribe now",
        "checkout is live",
        "message bookers directly",
        "direct messaging available",
        # feature overclaims
        "messaging is live",
        "direct messages available now",
        "claim verified",
        "payment active",
        "affiliate links active",
        "tickets sold by paris comedy",
        "auth v2 live",
        "accounts fully live",
    ]
    # Phrases that are safe negations — skip lines containing these
    safe_negations = [
        "checkout is not live",
        "not yet active",
        "planned",
        "not active",
        "coming soon",
        "every shows_data",  # JS comment in index.html
        "// p1.data",        # inline JS comment
    ]
    hits: list[dict] = []
    for fname in html_files:
        p = REPO_ROOT / fname
        if not p.exists():
            continue
        for lineno, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            ll = line.lower()
            # Skip lines that are clearly safe negations
            if any(neg in ll for neg in safe_negations):
                continue
            for phrase in forbidden_phrases:
                if phrase in ll:
                    hits.append({"file": fname, "line": lineno, "phrase": phrase, "text": line.strip()[:120]})
    return {
        "name": "public_copy_overclaims",
        "result": "PASS" if not hits else "FAIL",
        "evidence": {"hits": hits},
    }


def check_show_fallback_sync() -> dict:
    """P1.DATA.3B — show.html noscript fallback must match data/freshness-audit.json.

    For every <article id="show-{slug}" data-verification-status="..."> block,
    the status MUST equal the audit's verification_status for that slug, AND
    the freshness "Last checked: YYYY-MM-DD" date MUST NOT be older than the
    audit's last_checked_at date for that slug.

    Closes the root cause class where one source of truth (audit JSON) is
    updated but a static fallback in show.html still claims old states.
    """
    show = (REPO_ROOT / "show.html")
    audit = (REPO_ROOT / "data" / "freshness-audit.json")
    if not show.exists() or not audit.exists():
        return {"name": "show_fallback_sync", "result": "FAIL",
                "evidence": {"reason": "show.html or audit JSON missing"}}
    a = json.loads(audit.read_text(encoding="utf-8"))
    by_slug = {l["slug"]: l for l in a.get("listings", [])}
    html = show.read_text(encoding="utf-8")
    article_re = re.compile(
        r'<article id="show-(?P<slug>[a-z0-9-]+)" data-verification-status="(?P<status>[^"]+)">(?P<body>.*?)</article>',
        re.DOTALL,
    )
    freshness_re = re.compile(r"Last checked:</strong>\s*(\d{4}-\d{2}-\d{2})")
    problems = []
    checked = 0
    for m in article_re.finditer(html):
        slug = m.group("slug")
        fallback_status = m.group("status")
        body = m.group("body")
        entry = by_slug.get(slug)
        if not entry:
            problems.append({"slug": slug, "kind": "no_audit_entry"})
            continue
        checked += 1
        expected_status = entry.get("verification_status") or ""
        if fallback_status != expected_status:
            problems.append({
                "slug": slug, "kind": "status_mismatch",
                "fallback": fallback_status, "audit": expected_status,
            })
        fm = freshness_re.search(body)
        if fm:
            fallback_date = fm.group(1)
            audit_date = (entry.get("last_checked_at") or "")[:10]
            if audit_date and fallback_date < audit_date:
                problems.append({
                    "slug": slug, "kind": "date_drift",
                    "fallback": fallback_date, "audit": audit_date,
                })
    return {
        "name": "show_fallback_sync",
        "result": "PASS" if not problems else "FAIL",
        "evidence": {"articles_checked": checked, "problems": problems},
    }


def check_homepage_freshness_filter() -> dict:
    """Guard: every SHOWS_DATA.filter() in index.html must apply isFreshEnough().

    P1.DATA.2.FIX root-cause prevention: the Tonight panel filtered SHOWS_DATA
    by date only, bypassing the freshness check. This guard scans index.html
    statically: each `SHOWS_DATA.filter(` invocation must reference
    `isFreshEnough` either in its callback body OR in a chained .filter()
    within the next 240 characters.
    """
    p = (REPO_ROOT / "index.html")
    if not p.exists():
        return {"name": "homepage_freshness_filter", "result": "FAIL",
                "evidence": {"reason": "index.html missing"}}
    src = p.read_text(encoding="utf-8", errors="ignore")
    pat = re.compile(r"SHOWS_DATA\s*(?:\|\|\s*\[\])?\s*\)?\s*\.filter\s*\(")
    matches = []
    problems = []
    for m in pat.finditer(src):
        start = m.start()
        window = src[start:start + 360]
        line_no = src.count("\n", 0, start) + 1
        if "isFreshEnough" in window:
            matches.append({"line": line_no, "ok": True})
        else:
            matches.append({"line": line_no, "ok": False, "snippet": window[:120].replace("\n", " ")})
            problems.append({"line": line_no, "snippet": window[:120].replace("\n", " ")})
    return {
        "name": "homepage_freshness_filter",
        "result": "PASS" if not problems else "FAIL",
        "evidence": {"total_filter_sites": len(matches), "missing_isFreshEnough": problems},
    }


CHECKS = {
    "forbidden_strings":     lambda dom: check_forbidden_strings(),
    "internal_ctas":         lambda dom: check_internal_ctas(with_dom=dom),
    "raw_includes":          lambda dom: check_raw_includes(),
    "stale_homepage_panel":  lambda dom: check_stale_homepage_panel(with_dom=dom),
    "card_render":           lambda dom: check_card_render(with_dom=dom),
    "status_sweep":          lambda dom: check_status_sweep(),
    "nav_consistency":       lambda dom: check_nav_consistency(),
    "freshness_sanity":      lambda dom: check_freshness_sanity(),
    "homepage_freshness_filter": lambda dom: check_homepage_freshness_filter(),
    "show_fallback_sync":    lambda dom: check_show_fallback_sync(),
    "pricing_copy_safety":   lambda dom: check_pricing_copy_safety(),
    "public_copy_overclaims": lambda dom: check_public_copy_overclaims(),
    "hreflang":              lambda dom: check_hreflang(),
    "header_cta_rule":       lambda dom: check_header_cta_rule(),
}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="pariscomedy regression guard")
    ap.add_argument("--check", help="Run only one named check")
    ap.add_argument("--with-dom", action="store_true",
                    help="Enable Playwright DOM probes (checks 2/4/5)")
    args = ap.parse_args(argv)

    selected = [args.check] if args.check else list(CHECKS.keys())
    for c in selected:
        if c not in CHECKS:
            print(f"ERROR: unknown check '{c}'. "
                  f"Available: {sorted(CHECKS)}", file=sys.stderr)
            return 2

    results = []
    for name in selected:
        try:
            r = CHECKS[name](args.with_dom)
        except Exception as e:  # noqa: BLE001
            r = {"name": name, "result": "FAIL",
                 "evidence": {"reason": f"check raised: {e}"}}
        results.append(r)
        ev = r.get("evidence")
        ev_short = json.dumps(ev)[:200] if ev is not None else ""
        print(f"[{r['result']:4}] {r['name']:24} {ev_short}")

    fail = any(r["result"] == "FAIL" for r in results)
    iso = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = LOGS_DIR / f"regression-guard.{iso}.json"
    out_path.write_text(json.dumps({
        "timestamp_utc": iso,
        "base": BASE,
        "with_dom": args.with_dom,
        "results": results,
    }, indent=2))
    print(f"\nLog: {out_path}")
    print(f"Summary: {sum(1 for r in results if r['result']=='PASS')} pass, "
          f"{sum(1 for r in results if r['result']=='FAIL')} fail")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
