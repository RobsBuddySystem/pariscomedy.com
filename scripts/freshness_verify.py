#!/usr/bin/env python3
"""Actual source verification job.

For each active listing, hits the source_url ONCE with a polite UA + 10s timeout.
If reachable (HTTP 200) AND the response body contains the show name OR the venue name,
the listing is marked `verified_24h` with high confidence. Else routes to
`needs_human_review` or `source_unreachable`.

Writes refreshed data/freshness-audit.json. No paid APIs, no aggressive scraping,
one request per source per run.
"""
import json, re, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.pariscomedy.com/api/listings"
OUT = Path(__file__).parent.parent / "data" / "freshness-audit.json"
NOW = datetime.now(timezone.utc)
UA = "ParisComedyFreshnessVerify/1.0 (+https://pariscomedy.com/about.html)"
TIMEOUT = 10

PLATFORM_HOSTS = {
    "eventbrite": ["eventbrite.com", "eventbrite.fr", "eventbrite.ca"],
    "fnac_france_billet": ["fnacspectacles.com", "francebillet.com"],
    "billetreduc": ["billetreduc.com"],
    "fever": ["feverup.com"],
    "ticketmaster_fr": ["ticketmaster.fr"],
    "see_tickets": ["seetickets.com", "seetickets.fr"],
    "weezevent": ["weezevent.com"],
    "billetweb": ["billetweb.fr"],
    "yurplan": ["yurplan.com"],
    "helloasso": ["helloasso.com"],
    "shotgun": ["shotgun.live"],
    "dice": ["dice.fm"],
    "instagram": ["instagram.com"],
    "facebook": ["facebook.com", "fb.com"],
}

def platform_of(url):
    if not url: return "manual"
    m = re.match(r"https?://(?:www\.)?([^/]+)", url)
    if not m: return "manual"
    host = m.group(1).lower()
    for plat, hosts in PLATFORM_HOSTS.items():
        if any(host == h or host.endswith("." + h) for h in hosts):
            return plat
    return "venue_website"

def fetch_url(url):
    """Return (status_code, body_lowercase) or (None, None) on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(250000).decode("utf-8", errors="ignore").lower()
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return None, None

REPOINTS_PATH = Path(__file__).parent.parent / "data" / "manual-source-repoints.json"
_REPOINTS = None


def load_repoints():
    """P1.DATA.3.LITE: per-slug source_url override map. Loaded once per run."""
    global _REPOINTS
    if _REPOINTS is not None:
        return _REPOINTS
    try:
        d = json.loads(REPOINTS_PATH.read_text(encoding="utf-8"))
        _REPOINTS = (d or {}).get("repoints", {}) or {}
    except Exception:
        _REPOINTS = {}
    return _REPOINTS


def verify_listing(l):
    api_source_url = l.get("booking_url") or l.get("show_url") or ""
    slug = l["slug"]
    # P1.DATA.3.LITE: prefer manual repoint if present
    rep = load_repoints().get(slug)
    if rep and rep.get("new_url"):
        source_url = rep["new_url"]
        repointed = True
    else:
        source_url = api_source_url
        repointed = False
    plat = platform_of(source_url)
    name = (l.get("name") or "").lower()
    venue = ((l.get("venue") or {}).get("name") or "").lower()

    last_checked_at = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
    note = "source verification job"
    if not source_url:
        status, conf, risk = "source_unreachable", 0, "high"
        last_verified_at = None
    else:
        code, body = fetch_url(source_url)
        if code == 200 and body:
            # Detect "event ended" / past-event signals on ticket platform pages.
            # Use ONLY unambiguous "this event ended" phrases. Generic words like
            # "complet" or "sold out" alone are too noisy (Eventbrite shows them on
            # past dates of recurring events that still have future occurrences).
            past_signals = [
                "this event has ended", "event has ended",
                "this event has passed", "event has passed",
                "this event has already taken place",
                "tickets are no longer available",
                "event ended", "sales ended",
                "cet événement est terminé", "événement est terminé",
                "cet événement est passé", "événement terminé",
                "billetterie est fermée", "les ventes sont terminées",
                "ventes terminées", "vente terminée",
            ]
            # Match a phrase only when it is rendered HTML text, not an i18n
            # dictionary key. Eventbrite ships {"event ended":"..."} in every
            # page; the phrase is HTML status text only when it is NOT
            # immediately followed by a JSON value separator '"'.
            matched_sig = None
            for sig in past_signals:
                start = 0
                while True:
                    idx = body.find(sig, start)
                    if idx < 0:
                        break
                    after = body[idx + len(sig):idx + len(sig) + 1]
                    if after == '"':
                        start = idx + len(sig)
                        continue
                    matched_sig = sig
                    break
                if matched_sig:
                    break
            if matched_sig:
                status, conf, risk = "needs_human_review", 10, "high"
                last_verified_at = None
                note = f"past-event signal matched in source page: '{matched_sig}'"
            else:
                # Match if show name OR venue OR slug appears in body
                tokens = [t for t in [name, venue, slug.replace("-", " ")] if t]
                matched = any(t in body for t in tokens if len(t) >= 4)
                if matched:
                    status, conf, risk = "verified_24h", 98, "low"
                    last_verified_at = last_checked_at
                    note = f"source verified: HTTP 200 + name/venue/slug match + future-event"
                else:
                    status, conf, risk = "needs_human_review", 35, "high"
                    last_verified_at = None
                    note = f"source HTTP 200 but no name/venue/slug match — page may have changed"
        elif code in (404, 410):
            status, conf, risk = "source_unreachable", 0, "high"
            last_verified_at = None
            note = f"source HTTP {code} — link broken"
        elif code is None:
            status, conf, risk = "source_unreachable", 5, "high"
            last_verified_at = None
            note = "network error / timeout"
        else:
            status, conf, risk = "needs_human_review", 25, "medium"
            last_verified_at = None
            note = f"source HTTP {code}"

    next_due = NOW.timestamp() + 86400
    if repointed:
        note = f"[repointed via manual-source-repoints.json] {note}"
    return {
        "id": l["id"],
        "slug": slug,
        "name": l["name"],
        "source_url": source_url,
        "api_source_url": api_source_url if repointed else None,
        "source_repointed": repointed,
        "source_platform": plat,
        "source_type": "ticket" if plat in (
            "eventbrite", "fnac_france_billet", "billetreduc", "fever",
            "ticketmaster_fr", "see_tickets", "weezevent", "billetweb",
            "yurplan", "helloasso", "shotgun", "dice") else "directory",
        "last_checked_at": last_checked_at,
        "last_verified_at": last_verified_at,
        "confidence_score": conf,
        "stale_risk": risk,
        "verification_status": status,
        "next_check_due_at": datetime.fromtimestamp(next_due, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_notes": note,
    }

def main():
    req = urllib.request.Request(API, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        listings = json.loads(r.read())
    audit_items = []
    for l in listings:
        if l.get("status") != "active": continue
        sys.stderr.write(f"  checking {l['slug']:30s} ... "); sys.stderr.flush()
        item = verify_listing(l)
        sys.stderr.write(f"{item['verification_status']:22s} (conf {item['confidence_score']})\n")
        audit_items.append(item)
        time.sleep(0.5)  # polite pacing

    audit_items.sort(key=lambda x: (
        {"source_unreachable": 0, "needs_human_review": 1, "stale": 2,
         "verified_72h": 3, "verified_24h": 4}.get(x["verification_status"], 9),
        x["confidence_score"]
    ))

    summary = {
        "generated_at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": API,
        "verification_run": True,
        "total_active": len(audit_items),
        "by_status": {},
        "stale_or_review_count": 0,
    }
    for it in audit_items:
        summary["by_status"].setdefault(it["verification_status"], 0)
        summary["by_status"][it["verification_status"]] += 1
        if it["verification_status"] in ("stale", "needs_human_review", "source_unreachable"):
            summary["stale_or_review_count"] += 1

    out = {"summary": summary, "listings": audit_items}
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    sys.stderr.write(f"\nwrote {OUT}: by_status={summary['by_status']}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
