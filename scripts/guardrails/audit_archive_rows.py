#!/usr/bin/env python3
"""Archive-row audit.

For every show_listings row whose `source` starts with `archive-` or `plateaux-`,
probe its ticket_url and decide whether the live page proves the show is
currently running. Per PROJECT_CANON, proof requires ONE of:

  (a) JSON-LD `startDate` >= today (future ticketed instance), OR
  (b) recurrence text in the page body (e.g. "every Wednesday",
      "tous les mercredis", "chaque <weekday>"), OR
  (c) signed admin approval in data/show_approvals.json.

Any row that fails all three is QUARANTINED:
    status='stale_hidden', featured=0, public_visible=0,
    quarantine_reason=..., quarantined_at=today,
    quarantined_by='audit_archive_rows.py', previous_status saved.

Outputs:
    data/archive_audit_2026-05-24.md   (human-readable report)
    DB updates                          (in-place, idempotent)

Exit 0 = clean (no unproven archive rows remain public)
Exit 1 = HOLD (something is still public without proof)
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROBE_GAP_S = 0.5  # avoid rate-limits on Eventbrite/etc

DB_PATH    = Path.home() / ".openclaw/workspace/apps/paris-comedy/data/paris.db"
PUSH_ROOT  = Path(__file__).resolve().parents[2]
APPROVALS  = PUSH_ROOT / "data" / "show_approvals.json"
REPORT_OUT = PUSH_ROOT / "data" / "archive_audit_2026-05-24.md"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124.0"
TIMEOUT_S = 12

JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
RECURRENCE_RE = re.compile(
    r"\b(every\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    r"|tous\s+les\s+(?:lundis|mardis|mercredis|jeudis|vendredis|samedis|dimanches)"
    r"|chaque\s+(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)"
    r"|weekly|hebdomadaire)",
    re.I,
)
PAST_EVENT_RE = re.compile(r"(event ended|sales ended|past event|événement terminé)", re.I)


def fetch(url: str) -> tuple[int, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def parse_future_startdates(html: str, today: str) -> list[str]:
    """Return all JSON-LD Event.startDate values >= today found in the page."""
    found: list[str] = []
    for m in JSONLD_RE.finditer(html):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        nodes = d if isinstance(d, list) else [d]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            # Walk top-level + nested @graph
            stack = [node]
            if isinstance(node.get("@graph"), list):
                stack.extend(x for x in node["@graph"] if isinstance(x, dict))
            for x in stack:
                t = x.get("@type") or ""
                if (t == "Event" or (isinstance(t, list) and "Event" in t)
                        or "Event" in str(t)):
                    sd = (x.get("startDate") or "")[:10]
                    if sd and sd >= today:
                        found.append(sd)
    return found


def load_approvals() -> dict:
    if not APPROVALS.exists():
        return {}
    try:
        raw = json.loads(APPROVALS.read_text())
    except Exception:
        return {}
    return {e.get("slug_or_id", ""): e for e in raw.get("approvals", [])}


def ensure_columns(conn: sqlite3.Connection) -> None:
    cols = {c[1] for c in conn.execute("PRAGMA table_info(show_listings)").fetchall()}
    for col, ddl in [
        ("quarantine_reason",  "ALTER TABLE show_listings ADD COLUMN quarantine_reason TEXT"),
        ("quarantined_at",     "ALTER TABLE show_listings ADD COLUMN quarantined_at TEXT"),
        ("quarantined_by",     "ALTER TABLE show_listings ADD COLUMN quarantined_by TEXT"),
        ("previous_status",    "ALTER TABLE show_listings ADD COLUMN previous_status TEXT"),
    ]:
        if col not in cols:
            try:
                conn.execute(ddl)
            except Exception:
                pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = dt.date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_columns(conn)

    # Include stale_hidden rows too — they may rehabilitate when probed now.
    # canceled rows are NOT included (intentional permanent state).
    rows = conn.execute(
        """SELECT id, slug, name, status, featured, source, booking_url,
                  verified_at, COALESCE(public_visible, 1) AS public_visible,
                  previous_status
           FROM show_listings
           WHERE (source LIKE 'archive-%' OR source LIKE 'plateaux-%')
             AND status != 'canceled'"""
    ).fetchall()

    approvals = load_approvals()
    report_lines = [
        f"# Archive Row Audit — {today}",
        "",
        f"Total archive/import rows: **{len(rows)}**",
        "",
        "| id | slug | name | source | status | feat | verified_at | url HTTP | future_dates | recurrence | past_event | action | reason |",
        "|---:|------|------|--------|--------|-----:|-------------|---------:|--------------|-----------:|-----------:|--------|--------|",
    ]

    proven = quarantined = canceled_seen = manual_review = 0
    leaks_remaining = 0

    for r in rows:
        url = r["booking_url"] or ""
        prev_status = r["status"]
        action = "review"
        reason = ""

        # Already canceled rows: nothing to do, just confirm they stay hidden.
        if r["status"] == "canceled":
            canceled_seen += 1
            report_lines.append(
                f"| {r['id']} | {r['slug']} | {r['name'][:30]} | {r['source']} | canceled | {r['featured']} | "
                f"{r['verified_at'] or ''} | — | — | — | — | keep canceled | already quarantined |"
            )
            continue

        # Manual approval covers some rows
        approval = approvals.get(r["slug"]) or approvals.get(str(r["id"]))
        if approval and approval.get("valid_until", "") >= today:
            proven += 1
            report_lines.append(
                f"| {r['id']} | {r['slug']} | {r['name'][:30]} | {r['source']} | {r['status']} | {r['featured']} | "
                f"{r['verified_at'] or ''} | (skipped) | — | — | — | keep public | manual approval until {approval['valid_until']} |"
            )
            continue

        # Probe URL (with rate-limit gap)
        status, body = (0, "")
        if url:
            status, body = fetch(url)
            time.sleep(PROBE_GAP_S)
        future_dates = parse_future_startdates(body, today) if body else []
        has_recurrence = bool(RECURRENCE_RE.search(body)) if body else False
        is_past = bool(PAST_EVENT_RE.search(body)) if body else False

        # Check future-date / recurrence FIRST. Eventbrite recurring events
        # show "Event ended" on the earliest instance while still listing
        # future dates — those are valid live shows, not stale.
        if future_dates:
            action = "keep public"
            reason = f"JSON-LD startDate proves future date {sorted(future_dates)[0]}"
            proven += 1
        elif has_recurrence:
            action = "keep public"
            reason = "page contains explicit recurrence text"
            proven += 1
        elif is_past:
            action = "quarantine"
            reason = "page says event ended / sales ended (no future dates, no recurrence)"
        elif status >= 400 or status == 0:
            action = "quarantine"
            reason = f"URL HTTP {status} — page unreachable / error"
        elif not body:
            action = "quarantine"
            reason = "empty body returned"
        else:
            action = "quarantine"
            reason = "HTTP 200 but no future date and no recurrence text — insufficient proof"

        # Featured archive rows with no proof: must lose featured even before quarantine call
        if action == "quarantine" and not args.dry_run:
            conn.execute(
                """UPDATE show_listings
                   SET status='stale_hidden',
                       featured=0,
                       public_visible=0,
                       previous_status=COALESCE(previous_status, ?),
                       quarantine_reason=?,
                       quarantined_at=date('now'),
                       quarantined_by='audit_archive_rows.py',
                       updated_at=datetime('now')
                   WHERE id=?""",
                (prev_status, reason, r["id"]),
            )
            quarantined += 1

        # Proven rows: rehabilitate if previously quarantined, refresh verified_at
        if action == "keep public" and not args.dry_run:
            if r["status"] == "stale_hidden":
                # rehab — restore to previous_status (default 'active')
                restored = r["previous_status"] or "active"
                conn.execute(
                    """UPDATE show_listings
                       SET status=?, public_visible=1,
                           quarantine_reason=NULL,
                           quarantined_at=NULL, quarantined_by=NULL,
                           verified_at=date('now'),
                           updated_at=datetime('now')
                       WHERE id=?""",
                    (restored, r["id"]),
                )
            else:
                conn.execute(
                    "UPDATE show_listings SET verified_at=date('now'), updated_at=datetime('now') WHERE id=?",
                    (r["id"],),
                )

        report_lines.append(
            f"| {r['id']} | {r['slug']} | {r['name'][:30]} | {r['source']} | {r['status']} | "
            f"{r['featured']} | {r['verified_at'] or ''} | {status} | {len(future_dates)} | "
            f"{int(has_recurrence)} | {int(is_past)} | {action} | {reason} |"
        )

    if not args.dry_run:
        conn.commit()
    conn.close()

    # Write report
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text("\n".join(report_lines) + "\n")

    print(f"audited rows: {len(rows)}")
    print(f"  kept public (proven):       {proven}")
    print(f"  already canceled (kept):    {canceled_seen}")
    print(f"  quarantined this run:       {quarantined}")
    print(f"  manual-review/none:         {manual_review}")
    print(f"  report:                     {REPORT_OUT}")

    # Final check: any archive row still marked active+public_visible WITHOUT proof?
    conn = sqlite3.connect(DB_PATH)
    leaks = conn.execute(
        """SELECT id, slug FROM show_listings
           WHERE (source LIKE 'archive-%' OR source LIKE 'plateaux-%')
             AND status='active' AND COALESCE(public_visible,1)=1"""
    ).fetchall()
    conn.close()
    # Cross-check: every active row must have today's verified_at OR an approval.
    today_proven_ids = set()
    conn = sqlite3.connect(DB_PATH)
    for r in conn.execute(
        "SELECT id, slug, verified_at FROM show_listings WHERE source LIKE 'archive-%' AND status='active'"
    ).fetchall():
        if r[2] == today or approvals.get(r[1]) or approvals.get(str(r[0])):
            today_proven_ids.add(r[0])
    conn.close()
    leaks_remaining = sum(1 for r in leaks if r[0] not in today_proven_ids)

    if leaks_remaining > 0:
        print(f"❌ HOLD — {leaks_remaining} archive row(s) still active+public without today's proof")
        return 1
    print("✅ GREEN — no unproven archive rows remain public")
    return 0


if __name__ == "__main__":
    sys.exit(main())
