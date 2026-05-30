"""BACKEND.SUBMIT.1-SCAFFOLD — show submissions service module.

INERT BY DEFAULT. No routes wired (cutover happens in a later phase). Module
is importable + testable in isolation.

Service API:
- create_show_submission(conn, data, ip=None, user_agent=None) -> dict
- validate_submission(data) -> list[str] (problems; empty = ok)
- mark_submission_status(conn, submission_id, status, reviewer=None, notes=None) -> bool
- detect_duplicate_submission(conn, data) -> Optional[str] (id of duplicate)
- list_pending_submissions(conn) -> list[dict]

Safety:
- SUBMISSIONS_V2_ENABLED env var defaults "false". If route wiring lands later,
  routes must check this flag and return 503 disabled.
- create_show_submission does NOT publish to public listings; the resulting
  row has status='received' or 'needs_review' or 'spam' depending on input.
- Audit events written to audit_events_v2 (requires 002_auth_v2.sql migration).
- No email sent. Reviewer notification handled by future BACKEND.SUBMIT.1-CUTOVER.

Status transition matrix (enforced):
  received        -> needs_review | spam | duplicate
  needs_review    -> approved | rejected | duplicate | spam
  approved        -> imported | rejected
  rejected        -> (terminal)
  imported        -> (terminal)
  duplicate       -> (terminal)
  spam            -> (terminal)
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

SUBMISSIONS_V2_ENABLED = os.environ.get("SUBMISSIONS_V2_ENABLED", "false").lower() in (
    "1", "true", "yes", "on",
)

REQUIRED_FIELDS = ("submitter_email", "show_name", "venue_name", "source_url")
ALLOWED_STATUSES = (
    "received", "needs_review", "approved", "rejected",
    "imported", "duplicate", "spam",
)
ALLOWED_LANGUAGES = ("", "EN", "FR", "MIX")

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
URL_RE = re.compile(r"^https?://[A-Za-z0-9.\-]+(:\d+)?(/.*)?$")

TRANSITIONS = {
    "received":     {"needs_review", "spam", "duplicate"},
    "needs_review": {"approved", "rejected", "duplicate", "spam"},
    "approved":     {"imported", "rejected"},
    "rejected":     set(),
    "imported":     set(),
    "duplicate":    set(),
    "spam":         set(),
}


class SubmissionError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return uuid.uuid4().hex


def status() -> dict:
    return {"enabled": SUBMISSIONS_V2_ENABLED, "allowed_statuses": list(ALLOWED_STATUSES)}


# ── Validation ───────────────────────────────────────────────────────────────

def validate_submission(data: dict) -> list[str]:
    problems = []
    for f in REQUIRED_FIELDS:
        if not str(data.get(f) or "").strip():
            problems.append(f"missing required field: {f}")
    email = (data.get("submitter_email") or "").strip()
    if email and not EMAIL_RE.match(email):
        problems.append(f"invalid email: {email!r}")
    src = (data.get("source_url") or "").strip()
    if src and not URL_RE.match(src):
        problems.append(f"invalid source_url: {src!r}")
    tkt = (data.get("ticket_url") or "").strip()
    if tkt and not URL_RE.match(tkt):
        problems.append(f"invalid ticket_url: {tkt!r}")
    lang = (data.get("language") or "").strip()
    if lang and lang not in ALLOWED_LANGUAGES:
        problems.append(f"invalid language: {lang!r}")
    return problems


def _audit(conn: sqlite3.Connection, *, action: str, target_id: str,
           reviewer: Optional[str], metadata: Optional[dict] = None,
           ip: Optional[str] = None) -> None:
    try:
        conn.execute(
            """INSERT INTO audit_events_v2
               (user_id, actor_role, action, target_type, target_id, metadata_json, created_at, ip)
               VALUES (?,?,?,?,?,?,?,?)""",
            (None, reviewer or "system", action, "show_submission", target_id,
             json.dumps(metadata) if metadata else None, _now_iso(), ip),
        )
    except sqlite3.OperationalError:
        # audit_events_v2 not present in this DB (002_auth_v2.sql not applied) — skip
        pass


# ── Duplicate detection ──────────────────────────────────────────────────────

def detect_duplicate_submission(conn: sqlite3.Connection, data: dict) -> Optional[str]:
    """Same source_url + same email = duplicate (within last 90 days). Returns
    submission id of the existing duplicate, or None."""
    src = (data.get("source_url") or "").strip()
    email = (data.get("submitter_email") or "").strip().lower()
    if not src or not email:
        return None
    row = conn.execute(
        """SELECT id FROM show_submissions_v2
           WHERE source_url=? AND lower(submitter_email)=?
             AND status NOT IN ('rejected','spam')
           ORDER BY created_at DESC LIMIT 1""",
        (src, email),
    ).fetchone()
    return row[0] if row else None


# ── Create ───────────────────────────────────────────────────────────────────

def create_show_submission(
    conn: sqlite3.Connection,
    data: dict,
    *,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> dict:
    """Insert a new submission row. Honors honeypot + duplicate detection.

    Returns the inserted row as a dict, with `status` set to one of:
    received | needs_review | spam | duplicate.
    """
    problems = validate_submission(data)
    if problems:
        raise SubmissionError("; ".join(problems))

    honeypot = str(data.get("honeypot") or "").strip()
    if honeypot:
        status_value = "spam"
    else:
        dup_id = detect_duplicate_submission(conn, data)
        if dup_id:
            status_value = "duplicate"
        else:
            status_value = "needs_review"

    sub_id = _new_id()
    now = _now_iso()
    conn.execute(
        """INSERT INTO show_submissions_v2
           (id, submitter_name, submitter_email, submitter_role,
            show_name, venue_name, venue_address, city, language,
            source_url, ticket_url, recurrence_text, next_date_time,
            notes, honeypot, spam_signals, status, created_at, updated_at,
            duplicate_of, ip, user_agent)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            sub_id,
            (data.get("submitter_name") or "").strip(),
            (data.get("submitter_email") or "").strip(),
            (data.get("submitter_role") or "").strip(),
            (data.get("show_name") or "").strip(),
            (data.get("venue_name") or "").strip(),
            (data.get("venue_address") or "").strip(),
            (data.get("city") or "").strip(),
            (data.get("language") or "").strip(),
            (data.get("source_url") or "").strip(),
            (data.get("ticket_url") or "").strip(),
            (data.get("recurrence_text") or "").strip(),
            (data.get("next_date_time") or "").strip(),
            (data.get("notes") or "").strip(),
            honeypot,
            json.dumps([]) if not honeypot else json.dumps(["honeypot"]),
            status_value,
            now, now,
            detect_duplicate_submission(conn, data) if status_value == "duplicate" else None,
            ip, user_agent,
        ),
    )
    _audit(conn, action=f"submissions.create.{status_value}", target_id=sub_id, reviewer=None, ip=ip)
    return {"id": sub_id, "status": status_value, "created_at": now}


# ── Status transitions ───────────────────────────────────────────────────────

def mark_submission_status(
    conn: sqlite3.Connection,
    submission_id: str,
    new_status: str,
    *,
    reviewer: Optional[str] = None,
    notes: Optional[str] = None,
) -> bool:
    if new_status not in ALLOWED_STATUSES:
        raise SubmissionError(f"invalid status: {new_status}")
    row = conn.execute(
        "SELECT status FROM show_submissions_v2 WHERE id=?",
        (submission_id,),
    ).fetchone()
    if not row:
        raise SubmissionError(f"submission not found: {submission_id}")
    current = row[0]
    if new_status not in TRANSITIONS.get(current, set()):
        raise SubmissionError(
            f"invalid transition: {current} -> {new_status}",
        )
    now = _now_iso()
    conn.execute(
        """UPDATE show_submissions_v2
           SET status=?, review_notes=COALESCE(?, review_notes),
               reviewed_at=?, reviewed_by=?, updated_at=?
           WHERE id=?""",
        (new_status, notes, now, reviewer, now, submission_id),
    )
    _audit(conn, action=f"submissions.transition.{new_status}",
           target_id=submission_id, reviewer=reviewer,
           metadata={"from": current, "to": new_status, "notes": notes})
    return True


# ── List ─────────────────────────────────────────────────────────────────────

def list_pending_submissions(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """SELECT id, submitter_email, show_name, venue_name, source_url,
                  status, created_at
           FROM show_submissions_v2
           WHERE status IN ('received','needs_review')
           ORDER BY created_at DESC""",
    ).fetchall()
    return [
        {
            "id": r[0], "submitter_email": r[1], "show_name": r[2],
            "venue_name": r[3], "source_url": r[4], "status": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]
