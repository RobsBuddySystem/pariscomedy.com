#!/usr/bin/env python3
"""Validate every ticket_url in shows_generated.json.

Writes ticket_url_status + ticket_url_checked_at into each show.
Statuses: active | ended | sold_out | unavailable | unknown.
Unknown shows are also appended to review_queue.json.
"""
import json, sys, time, urllib.request, urllib.error, re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
SHOWS = ROOT / "data" / "shows_generated.json"
REVIEW = ROOT / "data" / "review_queue.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ParisComedyValidator/1"

STATUS_RE = re.compile(r'"eventStatus"\s*:\s*"([^"]+)"', re.I)
END_RE    = re.compile(r'"endDate"\s*:\s*"([^"]+)"', re.I)
START_RE  = re.compile(r'"startDate"\s*:\s*"([^"]+)"', re.I)
AVAIL_RE  = re.compile(r'"availability"\s*:\s*"([^"]+)"', re.I)

def classify(url: str) -> str:
    if not url:
        return "unknown"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept-Language": "en-US,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            if r.status >= 400:
                return "unavailable"
            body = r.read(600_000).decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        if e.code in (404, 410): return "unavailable"
        return "unknown"
    except Exception:
        return "unknown"

    status = (STATUS_RE.search(body) or [None, ""])[1].lower()
    avails = [m.group(1).lower() for m in AVAIL_RE.finditer(body)]
    end    = (END_RE.search(body)   or [None, ""])[1]
    start  = (START_RE.search(body) or [None, ""])[1]

    if "cancelled" in status or "postponed" in status:
        return "unavailable"

    now = datetime.now(timezone.utc)
    end_dt = None
    for v in (end, start):
        if not v: continue
        try:
            end_dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            break
        except Exception:
            pass
    if end_dt and end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    if end_dt and end_dt < now:
        return "ended"

    if avails:
        if all("soldout" in a or "sold_out" in a for a in avails):
            return "sold_out"
        if any("instock" in a or "limited" in a or "preorder" in a for a in avails):
            return "active"

    if "eventscheduled" in status and end_dt and end_dt >= now:
        return "active"

    return "unknown"

def main():
    shows = json.loads(SHOWS.read_text(encoding="utf-8"))
    cache: dict[str, str] = {}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    counts = {"active":0, "ended":0, "sold_out":0, "unavailable":0, "unknown":0}
    review: list[dict] = []

    for s in shows:
        url = s.get("ticket_url") or s.get("source_url") or ""
        if url in cache:
            status = cache[url]
        else:
            status = classify(url)
            cache[url] = status
            time.sleep(0.4)
        s["ticket_url_status"] = status
        s["ticket_url_checked_at"] = now
        counts[status] += 1
        if status == "unknown":
            review.append({"id": s.get("id"), "ticket_url": url, "reason": "validator returned unknown", "checked_at": now})

    SHOWS.write_text(json.dumps(shows, ensure_ascii=False, indent=2), encoding="utf-8")

    # review_queue.json was deprecated 2026-05-29 (now a {_status, items:[]} dict);
    # live review lands at the canonical API. Only maintain it if it's still a flat list.
    if REVIEW.exists():
        try:
            existing = json.loads(REVIEW.read_text(encoding="utf-8"))
        except Exception:
            existing = []
        if isinstance(existing, list):
            keep_ids = {(r.get("id"), r.get("ticket_url")) for r in review}
            existing = [r for r in existing
                        if (r.get("id"), r.get("ticket_url")) not in keep_ids]
            REVIEW.write_text(json.dumps(existing + review, ensure_ascii=False, indent=2),
                              encoding="utf-8")
        # else: deprecated dict shape — do not write (see file _note).

    print(json.dumps({"counts": counts, "total": len(shows), "checked_at": now}))

if __name__ == "__main__":
    main()
