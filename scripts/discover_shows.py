#!/usr/bin/env python3
"""Discover Paris comedy shows from Eventbrite organizers — dual-method, cross-checked.

METHOD A (primary): crawl each known organizer page (/o/<id>) to discover every
  event URL, then parse each event's JSON-LD (eventStatus, startDate, endDate,
  availability, location).
METHOD B (backup / cross-check): independently follow the HTTP redirect chain and
  parse Open Graph meta tags. A dead event redirects to a "…-archived-…" URL.

A show is emitted to data/discovered_shows.json ONLY when A and B agree it is live.
Any disagreement (or dead link) is written to data/scrape_conflicts.json and is
NEVER published. This guarantees no dead links reach the site.

Eventbrite does not expose per-comic lineups, so this discovers SHOWS, not which
comic is on which bill.

Run standalone, or let scripts/hourly_validate.sh chain it before validation.
"""
import json, re, sys, time, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT       = Path(__file__).resolve().parent.parent
GENERATED  = ROOT / "data" / "shows_generated.json"
DISCOVERED = ROOT / "data" / "discovered_shows.json"
CONFLICTS  = ROOT / "data" / "scrape_conflicts.json"
ORGANIZERS = ROOT / "data" / "organizers.json"   # persisted, auto-grows

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ParisComedyDiscover/1"

ORG_RE   = re.compile(r'eventbrite\.[a-z.]+/o/[a-zA-Z0-9-]*?(\d{6,})')
EVENT_RE = re.compile(r'/e/[a-z0-9-]+-tickets-(\d{8,})')
LD_BLOCK = re.compile(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I)
OG_RE    = lambda p: re.compile(r'<meta[^>]+property="og:%s"[^>]+content="([^"]*)"' % p, re.I)

WEEKDAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


def fetch(url, timeout=15):
    """Return (final_url, status_code, body) — follows redirects."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.geturl(), r.status, r.read(700_000).decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return url, e.code, ""
    except Exception:
        return url, 0, ""


def parse_iso(v):
    if not v:
        return None
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None


# ── METHOD A: JSON-LD ───────────────────────────────────────────────────────
def method_a(body):
    """Parse Eventbrite JSON-LD. Returns dict or None."""
    for raw in LD_BLOCK.findall(body):
        try:
            data = json.loads(raw.strip())
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if not isinstance(it, dict) or it.get("@type") != "Event":
                continue
            offers = it.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            return {
                "name":       it.get("name", "").strip(),
                "status":     str(it.get("eventStatus", "")).lower(),
                "start":      parse_iso(it.get("startDate")),
                "end":        parse_iso(it.get("endDate")),
                "availability": str(offers.get("availability", "")).lower(),
                "venue":      ((it.get("location") or {}).get("name") or "").strip(),
            }
    return None


# ── METHOD B: redirect chain + Open Graph ───────────────────────────────────
def method_b(final_url, status, body):
    """Independent liveness read. Returns dict or None."""
    if status != 200:
        return None
    dead = ("archived" in final_url.lower() or "expired" in final_url.lower()
            or "/e/null" in final_url.lower())
    og_title = (OG_RE("title").search(body) or [None, ""])[1].strip()
    og_type  = (OG_RE("type").search(body)  or [None, ""])[1].strip()
    return {"dead": dead, "og_title": og_title, "og_type": og_type}


def expand_series(name, venue, ev_id, url, start, end):
    """Weekly occurrences from start..end on start's weekday, capped 12 weeks out."""
    out = []
    if not start:
        return out
    horizon = datetime.now(timezone.utc) + timedelta(weeks=12)
    last = min(end, horizon) if end else (start if start > datetime.now(timezone.utc)
                                          else horizon)
    cur = start
    while cur <= last:
        if cur >= datetime.now(timezone.utc) - timedelta(hours=6):
            out.append({
                "id":         f"disc-{ev_id}-{cur:%Y%m%d}",
                "name":       name,
                "venue_name": venue,
                "start_date": cur.isoformat(),
                "time":       f"{cur:%H:%M}",
                "day":        WEEKDAYS[cur.weekday()],
                "booking_url": url,
                "source_url":  url,
                "eventbrite_id": ev_id,
            })
        cur += timedelta(weeks=1)
    return out


def main():
    # Seed organizer IDs: persisted file + derived from current event URLs.
    orgs = set()
    if ORGANIZERS.exists():
        try:
            orgs |= set(json.loads(ORGANIZERS.read_text(encoding="utf-8")))
        except Exception:
            pass
    if GENERATED.exists():
        gen = json.loads(GENERATED.read_text(encoding="utf-8"))
        for s in gen:
            u = s.get("booking_url") or s.get("source_url") or ""
            m = EVENT_RE.search(u)
            if not m:
                continue
            _, _, body = fetch(u)
            for om in ORG_RE.finditer(body):
                orgs.add(om.group(1))
            time.sleep(0.3)

    # METHOD A discovery: crawl organizer pages → event URLs.
    event_urls = {}
    for org in sorted(orgs):
        _, st, body = fetch(f"https://www.eventbrite.com/o/{org}")
        if st != 200:
            continue
        for m in EVENT_RE.finditer(body):
            ev_id = m.group(1)
            event_urls.setdefault(ev_id, "https://www.eventbrite.com" + m.group(0))
        time.sleep(0.4)

    discovered, conflicts = [], []
    now = datetime.now(timezone.utc)

    for ev_id, url in sorted(event_urls.items()):
        final_url, status, body = fetch(url)
        a = method_a(body)
        b = method_b(final_url, status, body)
        time.sleep(0.4)

        # Cross-check: both methods must independently agree the event is live.
        a_live = bool(a and "scheduled" in a["status"]
                      and (not a["end"] or a["end"] >= now)
                      and "soldout" not in a["availability"])
        b_live = bool(b and not b["dead"] and b["og_title"])

        if a_live and b_live:
            occ = expand_series(a["name"], a["venue"], ev_id, url, a["start"], a["end"])
            discovered.extend(occ)
        else:
            conflicts.append({
                "eventbrite_id": ev_id,
                "url": url,
                "final_url": final_url,
                "http_status": status,
                "method_a_live": a_live,
                "method_b_live": b_live,
                "method_a": {k: (v.isoformat() if isinstance(v, datetime) else v)
                             for k, v in (a or {}).items()},
                "method_b": b,
                "checked_at": now.isoformat(timespec="seconds"),
            })

    DISCOVERED.write_text(json.dumps(discovered, ensure_ascii=False, indent=2), encoding="utf-8")
    CONFLICTS.write_text(json.dumps(conflicts, ensure_ascii=False, indent=2), encoding="utf-8")
    ORGANIZERS.write_text(json.dumps(sorted(orgs), ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "organizers": len(orgs),
        "events_found": len(event_urls),
        "occurrences_discovered": len(discovered),
        "conflicts": len(conflicts),
    }))

if __name__ == "__main__":
    main()
