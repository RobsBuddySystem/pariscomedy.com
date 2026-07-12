#!/usr/bin/env python3
"""
build_europe_pages.py — generate static per-event pages for the Europe hub.

Reads data/upcoming_events.json (currently ~100 events, ~11 already past)
and writes:
  - europe/<city-slug>/<event-slug>.html   one static page per event
  - data/ticket_links.json                 slug -> outbound ticket URL map,
                                            consumed by europe/go.html

Doctrine (per approved design spec, 2026-07-12):
  - Every ticket link on the site is routed through europe/go.html?e=<slug>
    rather than linking the ticket/source URL directly. This gives us
    click-count evidence (via the existing pageview beacon on go.html) for
    future ticket-partnership negotiations, and a single choke point where
    affiliate/partner params can be injected later.
  - data/ticket_links.json embeds a PARTNER_PARAMS map, empty today. When a
    partnership lands, populate PARTNER_PARAMS (either '*' for a global
    param appended to every outbound link, or a bare hostname key for a
    site-specific param) and re-run this script once — every event page's
    ticket link updates automatically because they all resolve through
    go.html at click time, not at generation time.
  - Static pages tolerate becoming stale between nightly regenerations: each
    page embeds the same isPast() logic used by whats-on.html / europe.html
    (event considered over at ends_at, or starts_at + 3h if ends_at is
    absent) and swaps the ticket button for a "this show has passed" banner
    client-side if so, instead of waiting for the next regenerate.

Data provenance: data/upcoming_events.json itself is NOT produced by this
script — it is exported nightly by the comedy-network-db project and synced
into this repo. See scripts/com.pariscomedy.europe-refresh.plist for the
nightly schedule this script is meant to run under, AFTER that export lands.

Images: scripts/fetch_event_images.py runs BEFORE this script in the nightly
refresh and writes data/event_images.json (event id -> og:image URL scraped
from canonical_event_url). When present, this script embeds that photo as
the event page's hero image and og:image meta tag; events with no entry (or
an image that later 404s / hotlink-dies) fall back to the plain text layout
client-side via onerror — the page never breaks.

Run:
  python3 scripts/build_europe_pages.py

stdlib only, no third-party deps.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

REPO = Path(__file__).resolve().parent.parent
BASE = "https://pariscomedy.com"
DATA_FILE = REPO / "data" / "upcoming_events.json"
IMAGES_FILE = REPO / "data" / "event_images.json"
OUT_DIR = REPO / "europe"
TICKET_LINKS_FILE = REPO / "data" / "ticket_links.json"


def slugify(s: str | None) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "event"


def city_slug(ev: dict) -> str:
    return slugify(ev.get("city_name") or "other")


def event_slug(ev: dict) -> str:
    return f"{slugify(ev.get('title'))}-{ev.get('id')}"


def event_url_path(ev: dict) -> str:
    return f"/europe/{city_slug(ev)}/{event_slug(ev)}.html"


def esc(s) -> str:
    return xml_escape("" if s is None else str(s))


def fmt_long_date(iso: str | None) -> str:
    if not iso:
        return "Date TBA"
    try:
        d = datetime.fromisoformat(iso)
    except ValueError:
        return iso
    return d.strftime("%A %-d %B %Y, %H:%M") if hasattr(d, "strftime") else iso


def fmt_price(ev: dict) -> str | None:
    pmin, pmax = ev.get("price_min"), ev.get("price_max")
    if pmin is None and pmax is None:
        return None
    cur = {"EUR": "€", "GBP": "£"}.get(ev.get("currency"), (ev.get("currency") + " ") if ev.get("currency") else "")

    def n(v):
        if v is None:
            return ""
        v = round(float(v), 2)
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s

    if pmin is not None and pmax is not None and pmin != pmax:
        return f"{cur}{n(pmin)}–{n(pmax)}"
    v = pmin if pmin is not None else pmax
    if float(v) == 0:
        return "Free"
    return f"{cur}{n(v)}"


def lang_tag(ev: dict) -> tuple[str, str]:
    lang = (ev.get("language") or "").lower()
    if "fr" in lang:
        return "FR", "tag-fr"
    return "EN", "tag-en"


CARD_CSS_SHARED = """
:root{--navy:#0a0e1a;--card-bg:#111827;--border:#1e2a3a;--purple:#7c3aed;--gold:#c9a84c;--gold-light:#e8c96a;--white:#f0f0f0;--muted:#8899aa;--tag-en-bg:#0f2744;--tag-en:#7ab3e0;--tag-fr-bg:#241033;--tag-fr:#c79bf0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--navy);color:var(--white);min-height:100vh}
a{color:inherit;text-decoration:none}
nav{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--navy);z-index:100;flex-wrap:wrap;gap:8px}
.nav-logo{font-size:18px;font-weight:700;letter-spacing:-0.5px}
.nav-logo span{color:var(--gold)}
.nav-active{color:var(--white)!important}
.nav-links{display:flex;gap:20px;font-size:14px;color:var(--muted);align-items:center;flex-wrap:wrap}
.nav-links a:hover{color:var(--white)}
@media(max-width:620px){nav{align-items:flex-start}.nav-links{gap:12px}}
.wrap{max-width:760px;margin:0 auto;padding:32px 24px 60px}
.crumb{font-size:13px;color:var(--muted);margin-bottom:18px}
.crumb a:hover{color:var(--white)}
.past-banner{background:#241033;border:1px solid #3a1f52;color:#c79bf0;border-radius:10px;padding:14px 16px;font-size:14px;margin-bottom:20px;display:none}
.past-banner.show{display:block}
.hero-img{width:100%;max-height:360px;object-fit:cover;border-radius:12px;margin-bottom:20px;display:block;border:1px solid var(--border)}
h1{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-0.5px;line-height:1.2;margin-bottom:10px}
.event-date{font-size:15px;color:var(--gold);font-weight:700;margin-bottom:6px}
.event-venue{font-size:15px;color:var(--muted);margin-bottom:16px}
.event-venue .name{color:var(--white);font-weight:600}
.tag-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:22px}
.tag{padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;letter-spacing:.3px}
.tag-en{background:var(--tag-en-bg);color:var(--tag-en)}
.tag-fr{background:var(--tag-fr-bg);color:var(--tag-fr)}
.tag-price{background:#141d14;color:#8fce8f}
.desc{font-size:15px;line-height:1.7;color:#ccc;margin-bottom:28px}
.btn-tickets{display:inline-block;padding:14px 26px;border-radius:10px;background:var(--gold);color:#221a08;font-size:15px;font-weight:800}
.btn-tickets:hover{background:var(--gold-light)}
.more-city{border-top:1px solid var(--border);margin-top:40px;padding-top:24px}
.more-city h2{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}
.sib-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
@media(max-width:560px){.sib-grid{grid-template-columns:1fr}}
.sib-card{background:var(--card-bg);border:1px solid var(--border);border-radius:10px;padding:14px;display:block;transition:border-color .2s,transform .2s}
.sib-card:hover{border-color:rgba(201,168,76,.4);transform:translateY(-2px)}
.sib-date{font-size:11px;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:.3px}
.sib-title{font-size:14px;font-weight:700;margin-top:4px}
.sib-where{font-size:12px;color:var(--muted);margin-top:2px}
footer{border-top:1px solid #222;padding:32px 24px;text-align:center;color:#666;font-size:13px;margin-top:32px}
footer .frow{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:12px}
footer a{color:#666}
"""

NAV_HTML = """<nav class="nav-shell nav-shell-marketing">
  <a href="/" class="nav-logo">Paris<span>Comedy</span></a>
  <div class="nav-links">
    <a href="/">Home</a>
    <a href="/shows.html">Shows</a>
    <a href="/europe.html" class="nav-active">Europe</a>
    <a href="/hiring.html">Stage Time</a>
    <a href="/venues.html">Venues</a>
    <a href="/comedians.html">Comedians</a>
    <a href="/bookers.html">Bookers</a>
    <a href="/pricing.html">Pricing</a>
    <a href="/login.html">Sign In</a>
    <a href="/connect.html">Book / Connect</a>
    <a href="/about.html">About</a>
    <a href="/feedback.html">Feedback</a>
  </div>
</nav>"""

FOOTER_HTML = """<footer>
  <div class="frow">
    <a href="/">Home</a>
    <a href="/shows.html">Shows</a>
    <a href="/europe.html">Europe</a>
    <a href="/venues.html">Venues</a>
    <a href="/connect.html">Book a Show</a>
    <a href="/comedians.html">For Comedians</a>
  </div>
  <div>payments@pariscomedy.com</div>
</footer>"""


def event_over(ev: dict) -> bool:
    """Build-time twin of the client isPast(): over at ends_at, else starts_at+3h."""
    s = ev.get("starts_at")
    if not s:
        return False
    try:
        start = datetime.fromisoformat(s)
    except Exception:
        return False
    end = None
    if ev.get("ends_at"):
        try:
            end = datetime.fromisoformat(ev["ends_at"])
        except Exception:
            end = None
    if end is None:
        end = start + timedelta(hours=3)
    return end < datetime.now(end.tzinfo)


def sibling_card_html(ev: dict) -> str:
    where = ev.get("venue_name") or ev.get("organization_name") or ""
    d = ev.get("starts_at") or ""
    day_label = ""
    try:
        dd = datetime.fromisoformat(d)
        day_label = dd.strftime("%a %-d %b")
    except Exception:
        day_label = d
    ends = ev.get("ends_at") or ""
    return (
        f'<a class="sib-card" href="{esc(event_url_path(ev))}"'
        f' data-starts="{esc(d)}" data-ends="{esc(ends)}">'
        f'<div class="sib-date">{esc(day_label)}</div>'
        f'<div class="sib-title">{esc(ev.get("title"))}</div>'
        f'<div class="sib-where">{esc(where)}</div>'
        f"</a>"
    )


def event_ld_json(ev: dict) -> dict:
    url = BASE + event_url_path(ev)
    ld: dict = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": ev.get("title"),
        "url": url,
        "startDate": ev.get("starts_at"),
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled",
    }
    if ev.get("ends_at"):
        ld["endDate"] = ev["ends_at"]
    loc = {"@type": "Place", "name": ev.get("venue_name") or ev.get("organization_name") or ev.get("city_name")}
    if ev.get("venue_address") or ev.get("city_name") or ev.get("country_iso2"):
        loc["address"] = {
            "@type": "PostalAddress",
            "streetAddress": ev.get("venue_address"),
            "addressLocality": ev.get("city_name"),
            "addressCountry": ev.get("country_iso2"),
        }
    ld["location"] = loc
    if ev.get("price_min") is not None or ev.get("price_max") is not None:
        price = ev.get("price_min") if ev.get("price_min") is not None else ev.get("price_max")
        ld["offers"] = {
            "@type": "Offer",
            "price": price,
            "priceCurrency": ev.get("currency") or "EUR",
            "url": BASE + f"/europe/go.html?e={event_slug(ev)}",
            "availability": "https://schema.org/InStock",
        }
    return ld


def breadcrumb_ld_json(ev: dict) -> dict:
    city = ev.get("city_name") or "Other"
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Europe", "item": BASE + "/europe.html"},
            {"@type": "ListItem", "position": 3, "name": city, "item": BASE + f"/europe.html#{city_slug(ev)}"},
            {"@type": "ListItem", "position": 4, "name": ev.get("title"), "item": BASE + event_url_path(ev)},
        ],
    }


def render_event_page(ev: dict, siblings: list[dict], image_url: str | None = None) -> str:
    url_path = event_url_path(ev)
    slug = event_slug(ev)
    canonical = BASE + url_path
    title = ev.get("title") or "Comedy Show"
    city = ev.get("city_name") or ""
    venue = ev.get("venue_name") or ev.get("organization_name") or ""
    long_date = fmt_long_date(ev.get("starts_at"))
    tag_label, tag_class = lang_tag(ev)
    price = fmt_price(ev)
    desc = ev.get("description") if isinstance(ev.get("description"), str) else None
    page_title = f"{title} — {city} — Paris Comedy" if city else f"{title} — Paris Comedy"
    meta_desc = (
        desc[:200] if desc else f"{title} — English-language stand-up comedy in {city or 'Europe'}, {long_date}."
    )
    og_image = image_url or "https://pariscomedy.com/assets/og-default.png"

    ld_event = json.dumps(event_ld_json(ev), ensure_ascii=False)
    ld_breadcrumb = json.dumps(breadcrumb_ld_json(ev), ensure_ascii=False)

    sib_html = "".join(sibling_card_html(s) for s in siblings[:4])
    more_city_block = ""
    if sib_html:
        more_city_block = f"""
  <div class="more-city">
    <h2>More in {esc(city)}</h2>
    <div class="sib-grid">{sib_html}</div>
  </div>"""

    address_line = ev.get("venue_address") or ""
    venue_line = " · ".join([v for v in [venue, address_line, city] if v])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<meta name="description" content="{esc(meta_desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Paris Comedy">
<meta property="og:title" content="{esc(page_title)}">
<meta property="og:description" content="{esc(meta_desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{esc(og_image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page_title)}">
<meta name="twitter:description" content="{esc(meta_desc)}">
<meta name="twitter:image" content="{esc(og_image)}">
<script type="application/ld+json">{ld_event}</script>
<script type="application/ld+json">{ld_breadcrumb}</script>
<style>{CARD_CSS_SHARED}</style>
</head>
<body>
{NAV_HTML}
<div class="wrap">
  <div class="crumb"><a href="/">Home</a> &nbsp;/&nbsp; <a href="/europe.html">Europe</a> &nbsp;/&nbsp; <a href="/europe.html#{esc(city_slug(ev))}">{esc(city)}</a> &nbsp;/&nbsp; {esc(title)}</div>
  <div class="past-banner" id="pastBanner">This show has passed — more in {esc(city)} below.</div>
  {f'<img class="hero-img" src="{esc(image_url)}" alt="{esc(title)}" loading="lazy">' if image_url else ''}
  <h1>{esc(title)}</h1>
  <div class="event-date">{esc(long_date)}</div>
  <div class="event-venue">{f'<span class="name">{esc(venue)}</span>' if venue else ''}{f' · {esc(address_line)}' if address_line else ''}{f' · {esc(city)}' if city else ''}</div>
  <div class="tag-row">
    <span class="tag {tag_class}">{tag_label}</span>
    {f'<span class="tag tag-price">{esc(price)}</span>' if price else ''}
  </div>
  {f'<div class="desc">{esc(desc)}</div>' if desc else ''}
  <a class="btn-tickets" id="ticketBtn" href="/europe/go.html?e={esc(slug)}">Tickets &amp; details →</a>
  {more_city_block}
</div>
{FOOTER_HTML}
<script>
(function(){{
  // Hide the hero image if its hotlinked CDN source is dead (capture-phase
  // listener; no inline on*= attributes — the deploy gate blocks those).
  document.addEventListener('error', function(e){{
    if(e.target && e.target.classList && e.target.classList.contains('hero-img')) e.target.style.display='none';
  }}, true);
  var startsAt = {json.dumps(ev.get("starts_at"))};
  var endsAt = {json.dumps(ev.get("ends_at"))};
  function isPast(){{
    if(!startsAt) return false;
    var start = new Date(startsAt);
    if(isNaN(start.getTime())) return false;
    var end = endsAt ? new Date(endsAt) : new Date(start.getTime() + 3*3600*1000);
    if(isNaN(end.getTime())) end = new Date(start.getTime() + 3*3600*1000);
    return end < new Date();
  }}
  if(isPast()){{
    document.getElementById('pastBanner').classList.add('show');
    var btn = document.getElementById('ticketBtn');
    if(btn) btn.style.display = 'none';
  }}
  // "More in {{city}}" sibling cards are baked at build time — hide any whose
  // event has since ended, and drop the whole section if none survive.
  function cardPast(el){{
    var s = el.getAttribute('data-starts');
    if(!s) return false;
    var start = new Date(s);
    if(isNaN(start.getTime())) return false;
    var e = el.getAttribute('data-ends');
    var end = e ? new Date(e) : new Date(start.getTime() + 3*3600*1000);
    if(isNaN(end.getTime())) end = new Date(start.getTime() + 3*3600*1000);
    return end < new Date();
  }}
  var sibs = document.querySelectorAll('.sib-card');
  var alive = 0;
  sibs.forEach(function(el){{ if(cardPast(el)){{ el.style.display='none'; }} else {{ alive++; }} }});
  if(sibs.length && !alive){{
    var mc = document.querySelector('.more-city');
    if(mc) mc.style.display = 'none';
  }}
}})();
</script>
<script src="/assets/track.js" defer></script>
</body>
</html>
"""


def git_lastmod(rel_path: str) -> str:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", rel_path],
            cwd=REPO, stderr=subprocess.DEVNULL,
        ).decode().strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main() -> None:
    if not DATA_FILE.exists():
        raise SystemExit(f"missing {DATA_FILE}")
    events = json.loads(DATA_FILE.read_text())
    if not isinstance(events, list):
        events = events.get("events", [])

    images: dict[str, str] = {}
    if IMAGES_FILE.exists():
        try:
            raw_images = json.loads(IMAGES_FILE.read_text())
            if isinstance(raw_images, dict):
                images = {str(k): v for k, v in raw_images.items() if isinstance(v, str)}
        except Exception:
            images = {}

    # Group by city for "More in {City}" sibling lookups, sorted by start time.
    by_city: dict[str, list[dict]] = {}
    for ev in events:
        by_city.setdefault(ev.get("city_name") or "Other", []).append(ev)
    for city, lst in by_city.items():
        lst.sort(key=lambda e: e.get("starts_at") or "")

    OUT_DIR.mkdir(exist_ok=True)

    ticket_links: dict[str, dict] = {}
    written = 0
    for ev in events:
        city = ev.get("city_name") or "Other"
        siblings = [
            s for s in by_city.get(city, [])
            if s.get("id") != ev.get("id") and not event_over(s)
        ]
        page_dir = OUT_DIR / city_slug(ev)
        page_dir.mkdir(parents=True, exist_ok=True)
        page_path = page_dir / f"{event_slug(ev)}.html"
        image_url = images.get(str(ev.get("id")))
        page_path.write_text(render_event_page(ev, siblings, image_url), encoding="utf-8")
        written += 1

        url = ev.get("canonical_event_url")
        if url:
            ticket_links[event_slug(ev)] = {
                "url": url,
                "title": ev.get("title"),
                "city": city,
            }

    ticket_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        # PARTNER_PARAMS: '*' applies to every outbound host; a bare hostname
        # key (e.g. "billetreduc.com") applies only to that host. Empty
        # today by design — populate when a ticket-sale partnership lands,
        # then re-run this script. No per-page regeneration needed for the
        # params to take effect since europe/go.html reads this file at
        # click time.
        "PARTNER_PARAMS": {},
        "links": ticket_links,
    }
    TICKET_LINKS_FILE.write_text(json.dumps(ticket_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {written} event pages under {OUT_DIR}")
    print(f"Wrote {len(ticket_links)} ticket links to {TICKET_LINKS_FILE}")


if __name__ == "__main__":
    main()
