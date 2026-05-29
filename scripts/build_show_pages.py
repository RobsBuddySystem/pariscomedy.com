#!/usr/bin/env python3
"""
P4.PAGES.1 — Build static /shows/{slug}.html pages for verified_24h slugs.

Source of truth: the per-slug `<article id="show-{slug}">` blocks already
embedded in /show.html as a noscript fallback. We parse those, plus
freshness-audit.json for verification metadata, and emit one HTML file per
slug into /shows/.

Doctrine:
- Only verified_24h slugs are emitted. needs_human_review (theatre-bo-julie)
  is skipped on purpose.
- If a target file already exists, we SKIP it (this script does NOT touch
  existing HTML pages — it only fills gaps).
- nav: nav-shell-marketing partial. footer: marketing partial.
- canonical: https://pariscomedy.com/shows/{slug}.html
- ticket CTAs: rel="nofollow sponsored", target="_blank"
- alternate link to /show.html?slug={slug} so the query-string variant
  doesn't dupe-conflict with the static path.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHOW_HTML = REPO / "show.html"
SHOWS_DIR = REPO / "shows"
AUDIT_PATH = REPO / "data" / "freshness-audit.json"
NAV_PARTIAL = REPO / "partials" / "nav.shell.marketing.html"
FOOTER_PARTIAL = REPO / "partials" / "footer.marketing.html"


ARTICLE_RE = re.compile(
    r'<article id="show-(?P<slug>[a-z0-9-]+)" '
    r'data-verification-status="(?P<status>[^"]+)">'
    r'(?P<body>.*?)</article>',
    re.DOTALL,
)
H2_RE = re.compile(r"<h2>(?P<name>.*?)</h2>", re.DOTALL)
FIELD_RE = re.compile(
    r"<p><strong>(?P<key>[A-Za-z]+):</strong>\s*(?P<val>.*?)</p>",
    re.DOTALL,
)
DESC_RE = re.compile(
    r"</p>\s*<p>(?P<desc>(?!<a |<small)[^<].*?)</p>",
    re.DOTALL,
)
TICKET_RE = re.compile(
    r'<a href="(?P<url>https?://[^"]+)" rel="[^"]*"[^>]*>'
    r"Get tickets / source listing",
    re.DOTALL,
)
FRESHNESS_RE = re.compile(
    r'<p class="freshness"><small>(?P<inner>.*?)</small></p>',
    re.DOTALL,
)


def parse_articles() -> dict[str, dict]:
    src = SHOW_HTML.read_text()
    out: dict[str, dict] = {}
    for m in ARTICLE_RE.finditer(src):
        slug = m.group("slug")
        status = m.group("status")
        body = m.group("body")

        h2 = H2_RE.search(body)
        name = html.unescape(h2.group("name").strip()) if h2 else slug

        fields: dict[str, str] = {}
        for fm in FIELD_RE.finditer(body):
            fields[fm.group("key").lower()] = html.unescape(
                fm.group("val").strip()
            )

        # description = first <p> that isn't a strong-field, ticket link, or small note
        desc = ""
        # remove all field <p>...</p> blocks then look for plain <p>...</p>
        body_no_fields = FIELD_RE.sub("", body)
        for pm in re.finditer(r"<p>(.*?)</p>", body_no_fields, re.DOTALL):
            chunk = pm.group(1).strip()
            if (
                chunk
                and not chunk.lower().startswith("<a ")
                and "<small" not in chunk
                and not chunk.startswith("<strong>")
                and "Tickets are sold" not in chunk
            ):
                desc = html.unescape(chunk).strip()
                break

        ticket_m = TICKET_RE.search(body)
        ticket_url = ticket_m.group("url") if ticket_m else ""

        fresh_m = FRESHNESS_RE.search(body)
        freshness_html = fresh_m.group("inner").strip() if fresh_m else ""

        out[slug] = {
            "slug": slug,
            "status": status,
            "name": name,
            "venue": fields.get("venue", ""),
            "address": fields.get("address", ""),
            "when": fields.get("when", ""),
            "language": fields.get("language", "EN"),
            "description": desc,
            "ticket_url": ticket_url,
            "freshness_html": freshness_html,
        }
    return out


def load_partial(p: Path) -> str:
    return p.read_text().strip()


def render_page(s: dict, nav: str, footer: str) -> str:
    slug = s["slug"]
    name = s["name"]
    venue = s["venue"]
    address = s["address"]
    when = s["when"]
    language = s["language"]
    desc = s["description"] or f"{name} — verified Paris stand-up listing."
    ticket_url = s["ticket_url"]
    canonical = f"https://pariscomedy.com/shows/{slug}.html"
    alt = f"https://pariscomedy.com/show.html?slug={slug}"

    # 1-sentence meta description, capped.
    meta_desc = re.sub(r"\s+", " ", desc).strip()
    if len(meta_desc) > 160:
        meta_desc = meta_desc[:157].rstrip() + "..."

    title = f"{name} — {venue} — Paris Comedy" if venue else f"{name} — Paris Comedy"

    # JSON-LD Event schema
    ld = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": name,
        "url": canonical,
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {
            "@type": "Place",
            "name": venue or "Paris",
            "address": address or "Paris, France",
        },
        "description": desc,
        "inLanguage": "en" if language.upper() == "EN" else "fr",
    }
    if ticket_url:
        ld["offers"] = {
            "@type": "Offer",
            "url": ticket_url,
            "availability": "https://schema.org/InStock",
        }
    ld_json = json.dumps(ld, ensure_ascii=False)

    # build HTML — escape user values once
    e = html.escape
    name_e = e(name)
    venue_e = e(venue)
    address_e = e(address)
    when_e = e(when)
    desc_e = e(desc)
    meta_desc_e = e(meta_desc)
    title_e = e(title)
    ticket_html = (
        f'<a class="cta-btn cta-primary" href="{e(ticket_url)}" '
        f'target="_blank" rel="nofollow sponsored noopener">Get tickets</a>'
        if ticket_url
        else ""
    )
    freshness_block = s["freshness_html"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_e}</title>
<meta name="description" content="{meta_desc_e}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" href="{alt}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="event">
<meta property="og:title" content="{title_e}">
<meta property="og:description" content="{meta_desc_e}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://pariscomedy.com/assets/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld_json}</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#f0f0f0;min-height:100vh}}
a{{color:inherit;text-decoration:none}}
nav.nav-shell-marketing{{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-bottom:1px solid #222;position:sticky;top:0;background:#0a0a0a;z-index:100;flex-wrap:wrap;gap:8px}}
nav .nav-logo{{font-size:18px;font-weight:700;letter-spacing:-0.5px}}
nav .nav-logo span{{color:#f5c518}}
nav .nav-links{{display:flex;gap:20px;font-size:14px;color:#888;flex-wrap:wrap}}
nav .nav-links a:hover{{color:#f0f0f0}}
.wrap{{max-width:780px;margin:0 auto;padding:32px 24px}}
.crumb{{color:#666;font-size:13px;margin-bottom:18px}}
.crumb a{{color:#888}}
.crumb a:hover{{color:#f5c518}}
h1{{font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:-0.5px;margin-bottom:12px}}
.venue-line{{font-size:16px;color:#c9a84c;font-weight:600;margin-bottom:6px}}
.meta-line{{font-size:14px;color:#888;margin-bottom:18px}}
.lead{{color:#bbb;font-size:15px;line-height:1.7;margin-bottom:22px}}
.info-card{{background:#111;border:1px solid #1e1e1e;border-radius:10px;padding:14px 16px;margin-bottom:10px}}
.info-card h3{{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#888;margin-bottom:6px}}
.info-card p{{font-size:14px;color:#ddd;line-height:1.5}}
.cta-row{{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0 14px}}
.cta-btn{{padding:11px 18px;border-radius:10px;font-size:14px;font-weight:700;display:inline-block;border:1px solid #333;color:#ccc}}
.cta-btn:hover{{border-color:#666;color:#f0f0f0}}
.cta-primary{{background:#f5c518;color:#000;border-color:#f5c518}}
.cta-primary:hover{{opacity:0.9;color:#000}}
.disclosure{{font-size:13px;color:#888;line-height:1.6;margin-top:16px;padding:12px 14px;background:#0f0f0f;border:1px solid #1a1a1a;border-radius:8px}}
.muted{{font-size:13px;color:#666;margin-top:14px;line-height:1.6}}
.muted a{{color:#888;text-decoration:underline}}
footer{{border-top:1px solid #222;padding:32px 24px;text-align:center;color:#666;font-size:13px;margin-top:40px}}
footer a{{color:#666}}footer a:hover{{color:#f0f0f0}}
.footer-links{{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:12px}}
</style>
</head>
<body>
{nav}
<div class="wrap">
  <div class="crumb"><a href="/">Home</a> &middot; <a href="/shows.html">Shows</a> &middot; <span>{name_e}</span></div>

  <article>
    <h1>{name_e}</h1>
    <div class="venue-line">{venue_e}</div>
    <div class="meta-line">{when_e} &middot; {e(language)}{(' &middot; ' + address_e) if address_e and address_e != 'Paris' else ''}</div>

    <p class="lead">{desc_e}</p>

    <div class="info-card"><h3>Venue</h3><p>{venue_e}{(' — ' + address_e) if address_e else ''}</p></div>
    <div class="info-card"><h3>When</h3><p>{when_e}</p></div>
    <div class="info-card"><h3>Language</h3><p>{e(language)}</p></div>

    <div class="cta-row">{ticket_html}<a class="cta-btn" href="/shows.html">Back to all shows</a></div>

    <p class="freshness"><small>{freshness_block}</small></p>
    <p class="disclosure">Tickets are sold on the source platform linked above, not by Paris Comedy. Times and prices can change — always confirm on the source link before purchase. This page links to the show's official ticket source as the system of record.</p>
  </article>

  <p class="muted">← Back to <a href="/shows.html">all shows</a>.</p>
</div>
{footer}
</body>
</html>
"""


def main() -> None:
    parsed = parse_articles()
    nav = load_partial(NAV_PARTIAL)
    footer = load_partial(FOOTER_PARTIAL)
    audit = json.loads(AUDIT_PATH.read_text())
    target_slugs = [
        l["slug"]
        for l in audit.get("listings", [])
        if l.get("verification_status") == "verified_24h"
    ]

    SHOWS_DIR.mkdir(exist_ok=True)
    created: list[tuple[str, int]] = []
    skipped_existing: list[str] = []
    missing_source: list[str] = []

    for slug in target_slugs:
        if slug not in parsed:
            missing_source.append(slug)
            continue
        target = SHOWS_DIR / f"{slug}.html"
        if target.exists():
            skipped_existing.append(slug)
            continue
        html_out = render_page(parsed[slug], nav, footer)
        target.write_text(html_out)
        created.append((slug, target.stat().st_size))

    print("Created:")
    for slug, size in created:
        print(f"  /shows/{slug}.html ({size} bytes)")
    print(f"Skipped (already exist): {skipped_existing}")
    if missing_source:
        print(f"WARNING: no noscript source for: {missing_source}")
    print(f"\nSummary: {len(created)} new, {len(skipped_existing)} skipped")


if __name__ == "__main__":
    main()
