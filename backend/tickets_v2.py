"""
tickets_v2.py — multi-source ticket/listing adapter scaffold.
No live scraping. No public auto-import. All candidates default needs_review.
Feature flags: TICKETS_ADAPTERS_ENABLED=false, TICKET_IMPORTS_ENABLED=false, AFFILIATE_LINKS_ENABLED=false.
"""
import os
import uuid
import sqlite3
from datetime import datetime, timezone
from typing import Optional

TICKETS_ADAPTERS_ENABLED = os.environ.get("TICKETS_ADAPTERS_ENABLED", "false").lower() == "true"
TICKET_IMPORTS_ENABLED = os.environ.get("TICKET_IMPORTS_ENABLED", "false").lower() == "true"
AFFILIATE_LINKS_ENABLED = os.environ.get("AFFILIATE_LINKS_ENABLED", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Adapter registry
# ---------------------------------------------------------------------------

_ADAPTER_REGISTRY: dict = {}

# Platform metadata: robots compliance notes + whether signal-only (cannot import directly)
_PLATFORM_META = {
    "eventbrite":       {"signal_only": False, "robots_note": "Eventbrite ToS: no scraping; use API or manual verify"},
    "billetreduc":      {"signal_only": False, "robots_note": "BilletRéduc: check robots.txt before crawling"},
    "fnac":             {"signal_only": False, "robots_note": "FNAC/France Billet: check robots.txt before crawling"},
    "fever":            {"signal_only": False, "robots_note": "Fever: API terms apply"},
    "weezevent":        {"signal_only": False, "robots_note": "Weezevent: check ToS before scraping"},
    "ticketmaster_fr":  {"signal_only": False, "robots_note": "Ticketmaster FR: API required; no scraping"},
    "see_tickets":      {"signal_only": False, "robots_note": "See Tickets: check robots.txt"},
    "billetweb":        {"signal_only": False, "robots_note": "Billetweb: public event pages allowed"},
    "yurplan":          {"signal_only": False, "robots_note": "Yurplan: check ToS"},
    "helloasso":        {"signal_only": False, "robots_note": "HelloAsso: public API available"},
    "shotgun":          {"signal_only": False, "robots_note": "Shotgun: check ToS"},
    "dice":             {"signal_only": False, "robots_note": "Dice: API required"},
    "venue_direct":     {"signal_only": False, "robots_note": "Venue-direct: manual verification required"},
    "instagram":        {"signal_only": True,  "robots_note": "Instagram: signal-only; login-scraping forbidden"},
    "facebook":         {"signal_only": True,  "robots_note": "Facebook: signal-only; scraping ToS violation"},
}


class TicketsError(Exception):
    pass


def register_adapter(platform: str, config: dict) -> dict:
    if platform not in _PLATFORM_META:
        raise TicketsError(f"unknown_platform: {platform!r}")
    _ADAPTER_REGISTRY[platform] = {**config, "platform": platform, **_PLATFORM_META[platform]}
    return {"registered": True, "platform": platform}


def list_adapters() -> list:
    return [{"platform": p, **_ADAPTER_REGISTRY.get(p, {}), **_PLATFORM_META[p]}
            for p in _PLATFORM_META]


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def _apply_schema(conn: sqlite3.Connection) -> None:
    schema_path = os.path.join(os.path.dirname(__file__), "migrations", "007_tickets_v2.sql")
    with open(schema_path) as f:
        conn.executescript(f.read())


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _audit(conn: sqlite3.Connection, actor_id: str, action: str, target_id: str, meta: dict) -> None:
    try:
        import json
        conn.execute(
            "INSERT INTO audit_events_v2 (id, actor_user_id, action, target_id, meta, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4()), actor_id, action, target_id, json.dumps(meta), _now()),
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Candidate lifecycle
# ---------------------------------------------------------------------------

def normalize_candidate(raw: dict) -> dict:
    """Normalise raw adapter output to the canonical candidate shape."""
    platform = (raw.get("source_platform") or "").lower().strip()
    if platform not in _PLATFORM_META:
        raise TicketsError(f"unknown_platform: {platform!r}")
    meta = _PLATFORM_META[platform]
    return {
        "candidate_id":           raw.get("candidate_id") or str(uuid.uuid4()),
        "source_platform":        platform,
        "source_url":             raw.get("source_url") or "",
        "title":                  raw.get("title"),
        "venue_name":             raw.get("venue_name"),
        "venue_address":          raw.get("venue_address"),
        "city":                   raw.get("city") or "Paris",
        "starts_at":              raw.get("starts_at"),
        "recurrence_text":        raw.get("recurrence_text"),
        "language_guess":         raw.get("language_guess") or "fr",
        "ticket_url":             raw.get("ticket_url"),
        "confidence_score":       float(raw.get("confidence_score") or 0.0),
        "parser_status":          raw.get("parser_status") or "parsed",
        "duplicate_match_status": "unknown",
        "review_status":          "needs_review",
        "affiliate_enabled":      0,  # always false at normalize time
        "robots_note":            meta["robots_note"],
        "notes":                  raw.get("notes"),
    }


def save_candidate(conn: sqlite3.Connection, candidate: dict) -> dict:
    now = _now()
    conn.execute(
        "INSERT OR REPLACE INTO adapter_discoveries_v2 "
        "(candidate_id, source_platform, source_url, title, venue_name, venue_address, city, "
        " starts_at, recurrence_text, language_guess, ticket_url, confidence_score, "
        " parser_status, duplicate_match_status, review_status, affiliate_enabled, "
        " robots_note, notes, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            candidate["candidate_id"], candidate["source_platform"], candidate["source_url"],
            candidate.get("title"), candidate.get("venue_name"), candidate.get("venue_address"),
            candidate.get("city", "Paris"), candidate.get("starts_at"),
            candidate.get("recurrence_text"), candidate.get("language_guess", "fr"),
            candidate.get("ticket_url"), float(candidate.get("confidence_score", 0.0)),
            candidate.get("parser_status", "parsed"),
            candidate.get("duplicate_match_status", "unknown"),
            candidate.get("review_status", "needs_review"),
            int(candidate.get("affiliate_enabled", 0)),
            candidate.get("robots_note"), candidate.get("notes"),
            now, now,
        ),
    )
    return {"saved": True, "candidate_id": candidate["candidate_id"]}


def detect_candidate_duplicate(conn: sqlite3.Connection, candidate: dict) -> dict:
    """Returns duplicate match info by source_url and title+platform."""
    row = conn.execute(
        "SELECT candidate_id, review_status FROM adapter_discoveries_v2 "
        "WHERE source_url=? AND candidate_id != ?",
        (candidate["source_url"], candidate["candidate_id"]),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE adapter_discoveries_v2 SET duplicate_match_status='duplicate_existing', updated_at=? "
            "WHERE candidate_id=?",
            (_now(), candidate["candidate_id"]),
        )
        return {"is_duplicate": True, "matched_candidate_id": row[0], "matched_status": row[1]}
    conn.execute(
        "UPDATE adapter_discoveries_v2 SET duplicate_match_status='no_duplicate', updated_at=? "
        "WHERE candidate_id=?",
        (_now(), candidate["candidate_id"]),
    )
    return {"is_duplicate": False}


def mark_candidate_status(
    conn: sqlite3.Connection,
    candidate_id: str,
    status: str,
    reviewer: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    allowed = {"discovered", "needs_review", "duplicate_existing", "rejected",
               "approved_for_import", "imported", "source_unreachable"}
    if status not in allowed:
        raise TicketsError(f"invalid_status: {status!r}")
    now = _now()
    conn.execute(
        "UPDATE adapter_discoveries_v2 SET review_status=?, updated_at=?, reviewed_at=?, reviewed_by=?, notes=COALESCE(?,notes) "
        "WHERE candidate_id=?",
        (status, now, now if reviewer else None, reviewer, notes, candidate_id),
    )
    _audit(conn, reviewer or "system", "tickets/mark_status", candidate_id, {"status": status})
    return {"candidate_id": candidate_id, "status": status}


def list_review_queue(conn: sqlite3.Connection) -> list:
    rows = conn.execute(
        "SELECT candidate_id, source_platform, source_url, title, venue_name, starts_at, "
        "       review_status, confidence_score, created_at "
        "FROM adapter_discoveries_v2 WHERE review_status IN ('needs_review','discovered') "
        "ORDER BY created_at ASC",
    ).fetchall()
    return [
        {
            "candidate_id": r[0], "source_platform": r[1], "source_url": r[2],
            "title": r[3], "venue_name": r[4], "starts_at": r[5],
            "review_status": r[6], "confidence_score": r[7], "created_at": r[8],
        }
        for r in rows
    ]


def import_candidate_dry_run(conn: sqlite3.Connection, candidate_id: str) -> dict:
    """Returns a draft import payload without touching public listings."""
    row = conn.execute(
        "SELECT candidate_id, source_platform, source_url, title, venue_name, starts_at, "
        "       review_status, duplicate_match_status, affiliate_enabled "
        "FROM adapter_discoveries_v2 WHERE candidate_id=?",
        (candidate_id,),
    ).fetchone()
    if not row:
        raise TicketsError("candidate_not_found")
    c_id, platform, url, title, venue, starts_at, status, dup_status, affiliate = row
    if status != "approved_for_import":
        raise TicketsError(f"import_blocked: status is {status!r}, must be approved_for_import")
    if dup_status == "duplicate_existing":
        raise TicketsError("import_blocked: duplicate_existing")
    if affiliate and not AFFILIATE_LINKS_ENABLED:
        raise TicketsError("import_blocked: affiliate_links_disabled")
    meta = _PLATFORM_META.get(platform, {})
    if meta.get("signal_only"):
        raise TicketsError("import_blocked: signal_only platform cannot import")
    # Dry-run only — no public listing created
    return {
        "mode": "dryrun",
        "candidate_id": c_id,
        "draft_listing": {
            "source_platform": platform,
            "source_url": url,
            "title": title,
            "venue_name": venue,
            "starts_at": starts_at,
        },
        "would_create": True,
        "public_listing_created": False,
    }


def status() -> dict:
    return {
        "adapters_enabled": TICKETS_ADAPTERS_ENABLED,
        "imports_enabled": TICKET_IMPORTS_ENABLED,
        "affiliate_links_enabled": AFFILIATE_LINKS_ENABLED,
        "platform_count": len(_PLATFORM_META),
    }
