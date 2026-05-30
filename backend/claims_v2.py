"""BACKEND.CLAIM.1-SCAFFOLD — claim flow service module.

INERT BY DEFAULT. No routes wired. Importable + tested in isolation.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

CLAIMS_V2_ENABLED = os.environ.get("CLAIMS_V2_ENABLED", "false").lower() in ("1", "true", "yes", "on")

CLAIM_TYPES = ("comic", "show_runner", "venue")
ALLOWED_STATUSES = ("received", "needs_review", "approved", "rejected", "duplicate", "spam")
TRANSITIONS = {
    "received":     {"needs_review", "duplicate", "spam"},
    "needs_review": {"approved", "rejected", "duplicate", "spam"},
    "approved":     set(),
    "rejected":     set(),
    "duplicate":    set(),
    "spam":         set(),
}

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
URL_RE = re.compile(r"^https?://[A-Za-z0-9.\-]+(:\d+)?(/.*)?$")
EVIDENCE_FIELDS = ("instagram_url", "recent_post_url", "domain_email", "website_url", "notes")


class ClaimError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return uuid.uuid4().hex


def status() -> dict:
    return {"enabled": CLAIMS_V2_ENABLED, "claim_types": list(CLAIM_TYPES),
            "allowed_statuses": list(ALLOWED_STATUSES)}


def validate_claim(data: dict) -> list[str]:
    problems = []
    ct = (data.get("claim_type") or "").strip()
    if ct not in CLAIM_TYPES:
        problems.append(f"invalid claim_type: {ct!r}")
    email = (data.get("claimant_email") or "").strip()
    if not email:
        problems.append("missing claimant_email")
    elif not EMAIL_RE.match(email):
        problems.append(f"invalid claimant_email: {email!r}")
    if not (data.get("target_id") or data.get("target_slug")):
        problems.append("missing target_id or target_slug")
    # at least one evidence
    if not any((data.get(f) or "").strip() for f in EVIDENCE_FIELDS):
        problems.append("at least one evidence field required (instagram_url, recent_post_url, domain_email, website_url, notes)")
    # URL fields must be valid http(s) if present
    for f in ("instagram_url", "recent_post_url", "website_url"):
        v = (data.get(f) or "").strip()
        if v and not URL_RE.match(v):
            problems.append(f"invalid {f}: {v!r}")
    if data.get("domain_email"):
        v = data["domain_email"].strip()
        if v and not EMAIL_RE.match(v):
            problems.append(f"invalid domain_email: {v!r}")
    return problems


def _audit(conn, *, action: str, target_id: str, reviewer: Optional[str],
           metadata: Optional[dict] = None, ip: Optional[str] = None) -> None:
    try:
        conn.execute(
            """INSERT INTO audit_events_v2
               (user_id, actor_role, action, target_type, target_id, metadata_json, created_at, ip)
               VALUES (?,?,?,?,?,?,?,?)""",
            (None, reviewer or "system", action, "claim", target_id,
             json.dumps(metadata) if metadata else None, _now_iso(), ip),
        )
    except sqlite3.OperationalError:
        pass


def detect_duplicate_claim(conn: sqlite3.Connection, data: dict) -> Optional[str]:
    email = (data.get("claimant_email") or "").strip().lower()
    ct = (data.get("claim_type") or "").strip()
    tid = (data.get("target_id") or "").strip()
    ts = (data.get("target_slug") or "").strip()
    if not email or not ct or not (tid or ts):
        return None
    row = conn.execute(
        """SELECT id FROM claims_v2
           WHERE claim_type=? AND lower(claimant_email)=?
             AND (target_id=? OR target_slug=?)
             AND status NOT IN ('rejected','spam')
           ORDER BY created_at DESC LIMIT 1""",
        (ct, email, tid, ts),
    ).fetchone()
    return row[0] if row else None


def create_claim_request(conn: sqlite3.Connection, data: dict,
                         *, ip: Optional[str] = None, user_agent: Optional[str] = None) -> dict:
    problems = validate_claim(data)
    if problems:
        raise ClaimError("; ".join(problems))
    honeypot = str(data.get("honeypot") or "").strip()
    if honeypot:
        status_value = "spam"
    else:
        dup_id = detect_duplicate_claim(conn, data)
        if dup_id:
            status_value = "duplicate"
        else:
            status_value = "needs_review"
    cid = _new_id()
    now = _now_iso()
    conn.execute(
        """INSERT INTO claims_v2
           (id, claim_type, claimant_name, claimant_email,
            target_id, target_slug, target_name,
            instagram_url, recent_post_url, domain_email, website_url, notes,
            honeypot, spam_signals, status, created_at, updated_at,
            duplicate_of, ip, user_agent)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            cid, (data.get("claim_type") or "").strip(),
            (data.get("claimant_name") or "").strip(),
            (data.get("claimant_email") or "").strip(),
            (data.get("target_id") or "").strip(),
            (data.get("target_slug") or "").strip(),
            (data.get("target_name") or "").strip(),
            (data.get("instagram_url") or "").strip(),
            (data.get("recent_post_url") or "").strip(),
            (data.get("domain_email") or "").strip(),
            (data.get("website_url") or "").strip(),
            (data.get("notes") or "").strip(),
            honeypot,
            json.dumps([]) if not honeypot else json.dumps(["honeypot"]),
            status_value, now, now,
            detect_duplicate_claim(conn, data) if status_value == "duplicate" else None,
            ip, user_agent,
        ),
    )
    _audit(conn, action=f"claims.create.{status_value}", target_id=cid, reviewer=None, ip=ip)
    return {"id": cid, "status": status_value, "created_at": now}


def mark_claim_status(conn: sqlite3.Connection, claim_id: str, new_status: str,
                     *, reviewer: Optional[str] = None, notes: Optional[str] = None) -> bool:
    if new_status not in ALLOWED_STATUSES:
        raise ClaimError(f"invalid status: {new_status}")
    row = conn.execute("SELECT status FROM claims_v2 WHERE id=?", (claim_id,)).fetchone()
    if not row:
        raise ClaimError(f"claim not found: {claim_id}")
    current = row[0]
    if new_status not in TRANSITIONS.get(current, set()):
        raise ClaimError(f"invalid transition: {current} -> {new_status}")
    now = _now_iso()
    conn.execute(
        """UPDATE claims_v2
           SET status=?, review_notes=COALESCE(?, review_notes),
               reviewed_at=?, reviewed_by=?, updated_at=?
           WHERE id=?""",
        (new_status, notes, now, reviewer, now, claim_id),
    )
    _audit(conn, action=f"claims.transition.{new_status}", target_id=claim_id,
           reviewer=reviewer, metadata={"from": current, "to": new_status, "notes": notes})
    return True


def list_pending_claims(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """SELECT id, claim_type, claimant_email, target_slug, target_name, status, created_at
           FROM claims_v2 WHERE status IN ('received','needs_review')
           ORDER BY created_at DESC""",
    ).fetchall()
    return [
        {"id": r[0], "claim_type": r[1], "claimant_email": r[2],
         "target_slug": r[3], "target_name": r[4], "status": r[5], "created_at": r[6]}
        for r in rows
    ]


def claim_status_for_target(conn: sqlite3.Connection, claim_type: str,
                           target_id_or_slug: str) -> dict:
    """Public fail-closed: returns {status: 'verified'|'pending'|'none'}.

    Only the most recent APPROVED claim for that target yields 'verified'.
    A pending claim yields 'pending'. Anything else (including rejected/
    spam/duplicate or missing input) yields 'none'.
    """
    if claim_type not in CLAIM_TYPES or not target_id_or_slug:
        return {"status": "none"}
    rows = conn.execute(
        """SELECT status FROM claims_v2
           WHERE claim_type=? AND (target_id=? OR target_slug=?)
           ORDER BY created_at DESC LIMIT 5""",
        (claim_type, target_id_or_slug, target_id_or_slug),
    ).fetchall()
    statuses = [r[0] for r in rows]
    if "approved" in statuses:
        return {"status": "verified"}
    if "needs_review" in statuses or "received" in statuses:
        return {"status": "pending"}
    return {"status": "none"}
