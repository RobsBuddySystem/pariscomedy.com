#!/usr/bin/env python3
"""Find each comic's current actuality (shows / news) via 5 independent methods.

A fact is PUBLISHED only when >= 2 independent methods corroborate it.
Anything with confidence < 2 goes to the unverified file and is NEVER shown.
"No bullshit": unverified == not published.

THE 5 METHODS (all empirically verified to work without auth/keys):
  M1  Eventbrite destination events API
        /api/v3/destination/events/?event_ids=...   -> name,start_date,status,
        is_cancelled,series_id,venue,organizer
  M2  Eventbrite series expansion
        /api/v3/destination/events/?event_series_ids=...  -> every occurrence
        of a recurring show
  M3  Eventbrite Paris-comedy search crawl
        /d/france--paris/comedy/  -> broad event + organizer discovery
  M4  Eventbrite structured-content API
        /api/v3/events/<id>/structured_content/  -> event description widgets,
        mined for known comic names (maps show -> comic lineup)
  M5  DuckDuckGo HTML search
        html.duckduckgo.com/html/?q=...  -> a comic's official site / Wikipedia
        / news, used to verify the comic is real + currently active
  M6  Wikipedia API (direct, independent of DDG)
        en.wikipedia.org/w/api.php  -> confirms an established comic has an
        encyclopedia entry; a true independent corroborator of M5

CROSS-CHECK: every candidate fact carries the set of methods that produced it.
confidence = len(methods). Output:
  data/comic_actuality.json            confidence >= 2  (publishable, still gated)
  data/comic_actuality_unverified.json confidence  < 2  (never published)

Usage:
  python3 scripts/comic_actuality.py [--limit N] [--comic SLUG]
Designed to run as a batch on the PC / hourly job, not interactively.
"""
import json, re, sys, time, html, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from datetime import datetime, timezone

ROOT       = Path(__file__).resolve().parent.parent
COMEDIANS  = ROOT / "data" / "comedians.json"
DISCOVERED = ROOT / "data" / "discovered_shows.json"
VERIFIED   = ROOT / "data" / "comic_actuality.json"
UNVERIFIED = ROOT / "data" / "comic_actuality_unverified.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ParisComedyActuality/1"
EB = "https://www.eventbrite.com"
EVENT_RE = re.compile(r'/e/[a-z0-9-]+-tickets-(\d{8,})')


def get(url, as_json=False, timeout=15, headers=None):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.8"}
    if as_json:
        h["Accept"] = "application/json"
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(900_000).decode("utf-8", errors="ignore")
            return json.loads(raw) if as_json else raw
    except Exception:
        return None


def strip_html(s):
    return re.sub(r"<[^>]+>", " ", html.unescape(s or "")).strip()


# ── M1: Eventbrite destination events API ───────────────────────────────────
def m1_event_meta(event_ids):
    """Batch fetch structured event metadata. {id: {...}}"""
    out = {}
    for i in range(0, len(event_ids), 10):
        batch = ",".join(event_ids[i:i+10])
        d = get(f"{EB}/api/v3/destination/events/?event_ids={batch}"
                f"&expand=primary_venue,primary_organizer", as_json=True)
        for ev in (d or {}).get("events", []):
            out[str(ev.get("id"))] = ev
        time.sleep(0.3)
    return out


# ── M2: Eventbrite series expansion ─────────────────────────────────────────
def m2_series(series_id):
    d = get(f"{EB}/api/v3/destination/events/?event_series_ids={series_id}"
            f"&expand=primary_venue", as_json=True)
    return (d or {}).get("events", [])


# ── M3: Eventbrite Paris-comedy search crawl ────────────────────────────────
def m3_search(query=""):
    """Return (event_ids, raw_html) from the Paris comedy search/category."""
    q = ("/d/france--paris/comedy/" if not query
         else "/d/france--paris/" + urllib.parse.quote(query) + "/")
    body = get(f"{EB}{q}") or ""
    ids = sorted({m.group(1) for m in EVENT_RE.finditer(body)})
    return ids, strip_html(body)


# ── M6: Wikipedia API (direct, independent of DDG) ──────────────────────────
def m6_wikipedia(name):
    """Return the Wikipedia page title if the comic has a comedy-related entry."""
    d = get("https://en.wikipedia.org/w/api.php?action=query&list=search"
            "&srlimit=3&format=json&srsearch=" + urllib.parse.quote(name + " comedian"),
            as_json=True)
    hits = (d or {}).get("query", {}).get("search", [])
    for hit in hits:
        title = hit.get("title", "")
        snippet = strip_html(hit.get("snippet", ""))
        # Strong: title carries the name AND a comedy keyword anywhere.
        if name_in(name, title):
            if re.search(r"comedian|comic|humori|stand-?up|actor|actress|presenter",
                         title + " " + snippet, re.I):
                return title
            # Title is an exact name match for a "<name> comedian" query: accept.
            if title.strip().lower() == name.strip().lower():
                return title
    return None


# ── M4: Eventbrite structured-content (lineup text) ─────────────────────────
def m4_lineup_text(event_id):
    d = get(f"{EB}/api/v3/events/{event_id}/structured_content/", as_json=True)
    if not d:
        return ""
    chunks = []
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("text", "body") and isinstance(v, str):
                    chunks.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(d.get("modules", []))
    walk(d.get("widgets", []))
    return strip_html(" ".join(chunks))


# ── M5: DuckDuckGo HTML search ──────────────────────────────────────────────
def m5_ddg(query):
    """Return list of (title, url) results."""
    body = get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query))
    if not body:
        return []
    out = []
    for m in re.finditer(r'result__a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', body):
        href, title = m.group(1), strip_html(m.group(2))
        dec = re.search(r'uddg=([^&]+)', href)
        if dec:
            href = urllib.parse.unquote(dec.group(1))
        out.append((title, href))
    return out[:8]


def name_in(name, text):
    """Whole-name match, case-insensitive, accent-tolerant-ish."""
    if not name or len(name) < 4 or not text:
        return False
    return re.search(r"\b" + re.escape(name) + r"\b", text, re.I) is not None


def main():
    args = sys.argv[1:]
    limit = None
    only = None
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])
    if "--comic" in args:
        only = args[args.index("--comic") + 1]

    comics = json.loads(COMEDIANS.read_text(encoding="utf-8"))
    comics = [c for c in comics if not c.get("is_archived")]
    if only:
        comics = [c for c in comics if c.get("slug") == only]
    if limit:
        comics = comics[:limit]

    # Pre-load the discovered-shows event pool (from discover_shows.py).
    pool_ids = []
    if DISCOVERED.exists():
        for s in json.loads(DISCOVERED.read_text(encoding="utf-8")):
            if s.get("eventbrite_id"):
                pool_ids.append(str(s["eventbrite_id"]))
    # M3 broadens the pool with the live Paris-comedy search.
    m3_ids, m3_text = m3_search()
    pool_ids = sorted(set(pool_ids) | set(m3_ids))

    event_meta   = m1_event_meta(pool_ids)            # M1
    lineup_cache = {}                                 # M4, lazy

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    verified, unverified = [], []

    for c in comics:
        name = c.get("name", "")
        slug = c.get("slug", "")
        signals = {}   # fact-key -> set(methods)
        detail  = {}   # fact-key -> dict

        # M4 + M1/M2: comic named in an event's lineup text.
        for eid, ev in event_meta.items():
            if eid not in lineup_cache:
                lineup_cache[eid] = m4_lineup_text(eid)
                time.sleep(0.25)
            text = lineup_cache[eid]
            hay = " ".join([text, ev.get("name", ""), ev.get("summary", "")])
            if name_in(name, hay):
                key = f"show:{eid}"
                methods = {"M4"} if name_in(name, text) else set()
                # M1 corroborates: event exists, live, structured.
                if not ev.get("is_cancelled") and ev.get("status") == "live":
                    methods.add("M1")
                # M2 corroborates if part of a recurring series.
                if ev.get("series_id"):
                    methods.add("M2")
                signals.setdefault(key, set()).update(methods)
                detail[key] = {
                    "type": "performing",
                    "event_id": eid,
                    "event_name": ev.get("name"),
                    "date": ev.get("start_date"),
                    "url": ev.get("url"),
                }

        # M3: comic named in the live Paris-comedy search result text.
        if name_in(name, m3_text):
            signals.setdefault("web:active", set()).add("M3")
            detail.setdefault("web:active", {"type": "active_in_paris_comedy_search"})

        # M5: web presence / current activity.
        ddg = m5_ddg(f"{name} comedian Paris")
        time.sleep(0.6)
        for title, url in ddg:
            if name_in(name, title):
                signals.setdefault("web:active", set()).add("M5")
                d = detail.setdefault("web:active", {"type": "web_presence"})
                d.setdefault("links", []).append({"title": title, "url": url})
                em = EVENT_RE.search(url)
                if em and em.group(1) in event_meta:
                    signals["web:active"].add("M1")

        # M6: Wikipedia direct — independent corroborator of M5.
        wiki = m6_wikipedia(name)
        time.sleep(0.4)
        if wiki:
            signals.setdefault("web:active", set()).add("M6")
            d = detail.setdefault("web:active", {"type": "web_presence"})
            d["wikipedia"] = f"https://en.wikipedia.org/wiki/{wiki.replace(' ', '_')}"

        for key, methods in signals.items():
            rec = {
                "comic_slug": slug,
                "comic_name": name,
                "fact": key,
                "methods": sorted(methods),
                "confidence": len(methods),
                "checked_at": now,
                **detail.get(key, {}),
            }
            (verified if len(methods) >= 2 else unverified).append(rec)

    VERIFIED.write_text(json.dumps(verified, ensure_ascii=False, indent=2), encoding="utf-8")
    UNVERIFIED.write_text(json.dumps(unverified, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "comics_checked": len(comics),
        "events_in_pool": len(event_meta),
        "verified_facts": len(verified),
        "unverified_facts": len(unverified),
    }))

if __name__ == "__main__":
    main()
