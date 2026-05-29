#!/usr/bin/env python3
"""Dry-run freshness audit.

Reads api.pariscomedy.com/api/listings, derives per-listing freshness metadata,
and writes data/freshness-audit.json. Does NOT scrape sources.

Status policy:
  age ≤ 1 day    → verified_24h        (confidence 95+, promotable everywhere)
  age ≤ 3 days   → verified_72h        (confidence 75–94, show "last checked" warning)
  age ≤ 7 days   → stale               (confidence 40–74, suppress from Next-3-Days unless pinned)
  age > 7 days   → needs_human_review  (confidence ≤39, suppress)
  no verified_at → source_unreachable  (review queue)

Source platform is derived from booking_url / show_url hostname; defaults to "manual".
"""
import json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.pariscomedy.com/api/listings"
OUT = Path(__file__).parent.parent / "data" / "freshness-audit.json"
NOW = datetime.now(timezone.utc)

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

def parse_dt(s):
    if not s: return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try: return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except: pass
    return None

def status_and_confidence(verified_at_dt):
    if not verified_at_dt: return "source_unreachable", 0, "high"
    age_days = (NOW - verified_at_dt).total_seconds() / 86400
    if age_days <= 1:   return "verified_24h", 95 + min(int(5 * (1 - age_days)), 5), "low"
    if age_days <= 3:   return "verified_72h", int(95 - 20 * ((age_days - 1) / 2)), "low"
    if age_days <= 7:   return "stale", int(70 - 30 * ((age_days - 3) / 4)), "medium"
    return "needs_human_review", max(int(40 - 40 * min((age_days - 7) / 14, 1)), 0), "high"

def main(dry_run=True):
    req = urllib.request.Request(API, headers={"User-Agent": "ParisComedyFreshnessAudit/1.0 (+https://pariscomedy.com/about.html)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            listings = json.loads(r.read())
    except Exception as e:
        print(f"ERROR fetching {API}: {e}", file=sys.stderr); return 1

    audit_items = []
    for l in listings:
        if l.get("status") != "active": continue
        verified_at = parse_dt(l.get("verified_at") or l.get("updated_at"))
        last_activity = parse_dt(l.get("last_web_activity_at"))
        source_url = l.get("booking_url") or l.get("show_url") or ""
        plat = platform_of(source_url)
        st, conf, risk = status_and_confidence(verified_at)
        next_due = (verified_at.timestamp() + 86400) if verified_at else NOW.timestamp()
        audit_items.append({
            "id": l["id"],
            "slug": l["slug"],
            "name": l["name"],
            "source_url": source_url,
            "source_platform": plat,
            "source_type": "ticket" if plat in (
                "eventbrite", "fnac_france_billet", "billetreduc", "fever",
                "ticketmaster_fr", "see_tickets", "weezevent", "billetweb",
                "yurplan", "helloasso", "shotgun", "dice") else "directory",
            "last_checked_at": verified_at.strftime("%Y-%m-%dT%H:%M:%SZ") if verified_at else None,
            "last_verified_at": verified_at.strftime("%Y-%m-%dT%H:%M:%SZ") if verified_at else None,
            "confidence_score": conf,
            "stale_risk": risk,
            "verification_status": st,
            "next_check_due_at": datetime.fromtimestamp(next_due, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_notes": "automated dry-run audit; manual operator approval not yet applied",
        })

    audit_items.sort(key=lambda x: (
        {"source_unreachable": 0, "needs_human_review": 1, "stale": 2, "verified_72h": 3, "verified_24h": 4}.get(x["verification_status"], 9),
        x["confidence_score"]
    ))

    summary = {
        "generated_at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": API,
        "dry_run": dry_run,
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
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"wrote {OUT}: {len(audit_items)} active listings, status breakdown {summary['by_status']}")
    return 0

if __name__ == "__main__":
    sys.exit(main(dry_run="--write" not in sys.argv))
