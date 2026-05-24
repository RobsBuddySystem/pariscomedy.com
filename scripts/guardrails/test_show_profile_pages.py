#!/usr/bin/env python3
"""Every unique show in SHOWS_DATA must have a matching /shows/<slug>.html
profile page, and every profile page must:
  - link back to /shows.html
  - contain a Promote + Claim CTA
  - contain no forbidden copy
  - render upcoming dates OR "No upcoming dates currently verified"
  - never render Bilingual unless evidence exists (language=[] → no badge)
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOWS_HTML = ROOT / "shows.html"
SHOWS_DIR  = ROOT / "shows"

FORBIDDEN = [
    "best comics in Paris",
    "every night of the week",
    "Verified, highlighted comedy nights in Paris",
    "These shows are Featured",
    "claim your free Featured listing",
    "Featured Tonight",
    "Featured Shows This Week",
    "Rotating weekly",
    "first 100 show runners",
    "First 100 Featured listings",
    "undefined",
    ">None<",
]
ARTIFACT_PATTERNS = [
    "href=\"\"",  # empty href is broken
    "href=\"undefined\"",
]


def main() -> int:
    failures: list[str] = []

    m = re.search(r"const SHOWS_DATA\s*=\s*(\[.*?\]);", SHOWS_HTML.read_text(), re.S)
    if not m:
        print("SHOWS_DATA not found"); return 1
    rows = json.loads(m.group(1))

    # 1. Build expected slug set
    slugs: set[str] = set()
    by_slug: dict[str, list[dict]] = {}
    for r in rows:
        stem = re.sub(r"-\d{8}$", "", r.get("id", ""))
        if not stem:
            continue
        slugs.add(stem)
        by_slug.setdefault(stem, []).append(r)

    # 2. Every slug has a page
    for slug in sorted(slugs):
        f = SHOWS_DIR / f"{slug}.html"
        if not f.exists():
            failures.append(f"missing show profile page: /shows/{slug}.html")
            continue
        text = f.read_text()

        # 3. Forbidden copy
        for needle in FORBIDDEN:
            if needle in text:
                failures.append(f"/shows/{slug}.html: forbidden copy {needle!r}")
        for art in ARTIFACT_PATTERNS:
            if art in text:
                failures.append(f"/shows/{slug}.html: broken artifact {art!r}")
        # 3b. Claim link must carry show_slug
        if f"/book.html?claim={slug}" not in text:
            failures.append(f"/shows/{slug}.html: Claim link missing show_slug param")
        # 3c. JSON-LD EventSeries
        if '"@type": "EventSeries"' not in text and '"@type":"EventSeries"' not in text:
            failures.append(f"/shows/{slug}.html: missing JSON-LD EventSeries")
        # 3d. OG metadata
        if 'property="og:title"' not in text:
            failures.append(f"/shows/{slug}.html: missing OG metadata")
        # 3e. Canonical URL
        if f'rel="canonical" href="https://pariscomedy.com/shows/{slug}.html"' not in text:
            failures.append(f"/shows/{slug}.html: missing/wrong canonical URL")
        # 3f. Ownership UI placeholder present (loaded via JS)
        if 'ownership-badge' not in text:
            failures.append(f"/shows/{slug}.html: missing ownership badge placeholder")
        # 3g. Copy-link button present
        if 'copyShowLink' not in text:
            failures.append(f"/shows/{slug}.html: missing copy-link affordance")

        # 4. Required structural elements
        if "/shows.html" not in text:
            failures.append(f"/shows/{slug}.html: missing back-link to /shows.html")
        if "Promote this show" not in text:
            failures.append(f"/shows/{slug}.html: missing Promote CTA")
        if "Claim this show" not in text:
            failures.append(f"/shows/{slug}.html: missing Claim CTA")
        # 5. Upcoming-dates section present
        if "Upcoming dates" not in text:
            failures.append(f"/shows/{slug}.html: missing Upcoming-dates section")

        # 6. Language honesty — page must not render "Bilingual" badge when
        #    the row's language list lacks bilingual evidence
        sample = by_slug[slug][0]
        langs = sample.get("language") or []
        is_bi_tagged = ("bi" in langs) or ("en" in langs and "fr" in langs)
        if not is_bi_tagged:
            if 'badge-lang-bi">Bilingual' in text:
                failures.append(f"/shows/{slug}.html: renders Bilingual badge without evidence")

    # 7. Index.html in /shows/
    if not (SHOWS_DIR / "index.html").exists():
        failures.append("/shows/index.html missing")

    if failures:
        print(f"❌ {len(failures)} failure(s):")
        for f in failures: print(f"  - {f}")
        return 1
    print(f"✅ {len(slugs)} show profile pages — all present, clean, with required structure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
