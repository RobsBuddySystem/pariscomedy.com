#!/usr/bin/env python3
"""
P4.SITEMAP.1 — generate sitemap.xml from real public pages + verified shows.

Doctrine:
- Public indexable pages only (no <meta name="robots" content="noindex">).
- Admin/portal/login pages are EXCLUDED even if they don't have noindex,
  because they're behind auth — they appear in robots.txt Disallow.
- <lastmod> comes from `git log -1 --format=%cs <file>` (ISO date).
- /show.html?slug={slug} entries are included ONLY when their
  verification_status is verified_24h or verified_72h, per
  data/freshness-audit.json.
- 6 legal pages get hreflang EN <-> FR pairs.

Run:
  python3 scripts/generate_sitemap.py
Writes:
  sitemap.xml at repo root.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parent.parent
BASE = "https://pariscomedy.com"

# Pages that are explicitly excluded from sitemap (admin/portal/auth/redirects).
# These overlap with robots.txt Disallow.
EXCLUDED_PAGES = {
    "admin-events.html",
    "admin-crm.html",
    "admin-messages.html",
    "admin-payments.html",
    "admin-submit.html",
    "performer-portal.html",
    "booker-portal.html",
    "booker-dashboard.html",
    "show-runner.html",
    "login.html",
    "checkout-pending.html",
    "404.html",
    "r.html",
    "show.html",  # listed individually with ?slug=... below
}

# Public, indexable URLs. (path_in_repo, loc_path, changefreq, priority)
# loc_path is what gets written into <loc> (so "/" for index, "/shows" for shows.html etc).
# We use clean URLs where the host serves them; here we use the .html paths
# that actually exist in the repo to match deployed paths.
PUBLIC_PAGES = [
    ("index.html",       "/",                 "daily",   "1.0"),
    ("shows.html",       "/shows.html",       "daily",   "0.9"),
    ("venues.html",      "/venues.html",      "weekly",  "0.7"),
    ("comedians.html",   "/comedians.html",   "daily",   "0.8"),
    ("pricing.html",     "/pricing.html",     "weekly",  "0.7"),
    ("bookers.html",     "/bookers.html",     "weekly",  "0.7"),
    ("book.html",        "/book.html",        "weekly",  "0.7"),
    ("about.html",       "/about.html",       "monthly", "0.6"),
    ("archive.html",     "/archive.html",     "monthly", "0.5"),
    ("terms.html",       "/terms.html",       "yearly",  "0.3"),
    ("privacy.html",     "/privacy.html",     "yearly",  "0.3"),
    ("disclosure.html",  "/disclosure.html",  "yearly",  "0.3"),
    ("fr/terms.html",      "/fr/terms.html",      "yearly", "0.3"),
    ("fr/privacy.html",    "/fr/privacy.html",    "yearly", "0.3"),
    ("fr/disclosure.html", "/fr/disclosure.html", "yearly", "0.3"),
]

# Legal pages with EN <-> FR hreflang alternates.
HREFLANG_PAIRS = {
    "/terms.html":         "/fr/terms.html",
    "/privacy.html":       "/fr/privacy.html",
    "/disclosure.html":    "/fr/disclosure.html",
    "/fr/terms.html":      "/terms.html",
    "/fr/privacy.html":    "/privacy.html",
    "/fr/disclosure.html": "/disclosure.html",
}
PAGE_LANG = {
    "/terms.html": "en", "/privacy.html": "en", "/disclosure.html": "en",
    "/fr/terms.html": "fr", "/fr/privacy.html": "fr", "/fr/disclosure.html": "fr",
}


def git_lastmod(rel_path: str) -> str:
    """Return ISO date (YYYY-MM-DD) of last commit touching the file, or today."""
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", rel_path],
            cwd=REPO, stderr=subprocess.DEVNULL,
        ).decode().strip()
        if out:
            return out
    except subprocess.CalledProcessError:
        pass
    # Fallback to today
    return subprocess.check_output(["date", "+%Y-%m-%d"]).decode().strip()


def verified_slugs() -> list[tuple[str, str]]:
    """Return list of (slug, lastmod) for shows with verified_24h / verified_72h."""
    path = REPO / "data" / "freshness-audit.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    listings = data.get("listings", []) if isinstance(data, dict) else []
    audit_lastmod = git_lastmod("data/freshness-audit.json")
    out = []
    seen = set()
    for item in listings:
        status = item.get("verification_status")
        slug = item.get("slug")
        if not slug or slug in seen:
            continue
        if status in ("verified_24h", "verified_72h"):
            # Prefer last_verified_at date if present, else freshness file mtime
            lv = item.get("last_verified_at") or ""
            lastmod = lv[:10] if lv else audit_lastmod
            out.append((slug, lastmod))
            seen.add(slug)
    return out


def url_entry(loc: str, lastmod: str, changefreq: str, priority: str,
              alternates: dict[str, str] | None = None) -> str:
    lines = ["  <url>"]
    lines.append(f"    <loc>{escape(BASE + loc)}</loc>")
    lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.append(f"    <changefreq>{changefreq}</changefreq>")
    lines.append(f"    <priority>{priority}</priority>")
    if alternates:
        for hreflang, href in alternates.items():
            lines.append(
                f'    <xhtml:link rel="alternate" hreflang="{hreflang}" '
                f'href="{escape(BASE + href)}"/>'
            )
    lines.append("  </url>")
    return "\n".join(lines)


def main() -> None:
    entries: list[str] = []

    for rel, loc, freq, pri in PUBLIC_PAGES:
        full = REPO / rel
        if not full.exists():
            continue
        if Path(rel).name in EXCLUDED_PAGES:
            continue
        lastmod = git_lastmod(rel)
        alts = None
        if loc in HREFLANG_PAIRS:
            other = HREFLANG_PAIRS[loc]
            self_lang = PAGE_LANG[loc]
            other_lang = PAGE_LANG[other]
            alts = {
                self_lang: loc,
                other_lang: other,
                "x-default": loc if self_lang == "en" else other,
            }
        entries.append(url_entry(loc, lastmod, freq, pri, alts))

    # Verified shows
    show_lastmod_default = git_lastmod("show.html")
    for slug, lastmod in verified_slugs():
        lm = lastmod or show_lastmod_default
        entries.append(url_entry(
            f"/show.html?slug={slug}", lm, "daily", "0.8",
        ))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )

    (REPO / "sitemap.xml").write_text(xml)
    print(f"Wrote sitemap.xml with {len(entries)} URLs")


if __name__ == "__main__":
    main()
