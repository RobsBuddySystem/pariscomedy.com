"""
messaging_v2.py — comic/booker messaging scaffold.
No routes wired. MESSAGING_V2_ENABLED=false by default.
"""
import os
import uuid
import sqlite3
from datetime import datetime, timezone
from typing import Optional

MESSAGING_V2_ENABLED = os.environ.get("MESSAGING_V2_ENABLED", "false").lower() == "true"
DAILY_RECIPIENT_CAP = int(os.environ.get("MESSAGING_DAILY_RECIPIENT_CAP", "20"))


class MessagingError(Exception):
    pass


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def _apply_schema(conn: sqlite3.Connection) -> None:
    schema_path = os.path.join(os.path.dirname(__file__), "migrations", "006_messaging_v2.sql")
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
        pass  # audit table may not exist in test DB; never block messaging on audit failure


# ---------------------------------------------------------------------------
# Abuse controls
# ---------------------------------------------------------------------------

def can_message(conn: sqlite3.Connection, sender_user_id: str, recipient_user_id: str) -> bool:
    """Returns False if sender is blocked by recipient or sender has blocked recipient."""
    row = conn.execute(
        "SELECT 1 FROM message_blocks_v2 WHERE "
        "(blocker_user_id=? AND blocked_user_id=?) OR (blocker_user_id=? AND blocked_user_id=?)",
        (recipient_user_id, sender_user_id, sender_user_id, recipient_user_id),
    ).fetchone()
    return row is None


def enforce_daily_recipient_limit(conn: sqlite3.Connection, sender_user_id: str) -> None:
    """Raises MessagingError if sender has already contacted DAILY_RECIPIENT_CAP distinct recipients today."""
    today = _now()[:10]  # YYYY-MM-DD
    row = conn.execute(
        "SELECT COUNT(DISTINCT recipient_user_id) FROM messages_v2 "
        "WHERE sender_user_id=? AND created_at >= ?",
        (sender_user_id, today + "T00:00:00Z"),
    ).fetchone()
    count = row[0] if row else 0
    if count >= DAILY_RECIPIENT_CAP:
        raise MessagingError(f"daily_recipient_cap: sender has reached {DAILY_RECIPIENT_CAP} distinct recipients today")


# ---------------------------------------------------------------------------
# Thread + message operations
# ---------------------------------------------------------------------------

def create_thread(
    conn: sqlite3.Connection,
    sender_user_id: str,
    sender_role: str,
    recipient_user_id: str,
    recipient_role: str,
    subject: str,
    body: str,
) -> dict:
    if not can_message(conn, sender_user_id, recipient_user_id):
        raise MessagingError("blocked: cannot send to this user")
    enforce_daily_recipient_limit(conn, sender_user_id)

    thread_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    now = _now()

    conn.execute(
        "INSERT INTO message_threads_v2 "
        "(thread_id, participant_a_user_id, participant_b_user_id, participant_a_role, participant_b_role, "
        " subject, status, created_at, updated_at, last_message_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (thread_id, sender_user_id, recipient_user_id, sender_role, recipient_role,
         subject, "active", now, now, now),
    )
    conn.execute(
        "INSERT INTO messages_v2 (message_id, thread_id, sender_user_id, recipient_user_id, body, status, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (message_id, thread_id, sender_user_id, recipient_user_id, body, "sent", now),
    )
    _audit(conn, sender_user_id, "messaging/create_thread", thread_id, {"subject": subject})
    return {"thread_id": thread_id, "message_id": message_id, "status": "active"}


def reply_to_thread(
    conn: sqlite3.Connection,
    thread_id: str,
    sender_user_id: str,
    body: str,
) -> dict:
    thread = conn.execute(
        "SELECT participant_a_user_id, participant_b_user_id, status FROM message_threads_v2 WHERE thread_id=?",
        (thread_id,),
    ).fetchone()
    if not thread:
        raise MessagingError("thread_not_found")
    pa, pb, status = thread
    if sender_user_id not in (pa, pb):
        raise MessagingError("not_participant")
    if status in ("blocked", "reported"):
        raise MessagingError(f"thread_{status}: cannot reply")
    recipient_user_id = pb if sender_user_id == pa else pa
    if not can_message(conn, sender_user_id, recipient_user_id):
        raise MessagingError("blocked: cannot reply")

    message_id = str(uuid.uuid4())
    now = _now()
    conn.execute(
        "INSERT INTO messages_v2 (message_id, thread_id, sender_user_id, recipient_user_id, body, status, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (message_id, thread_id, sender_user_id, recipient_user_id, body, "sent", now),
    )
    conn.execute(
        "UPDATE message_threads_v2 SET updated_at=?, last_message_at=? WHERE thread_id=?",
        (now, now, thread_id),
    )
    _audit(conn, sender_user_id, "messaging/reply", thread_id, {})
    return {"message_id": message_id, "thread_id": thread_id}


def list_threads_for_user(conn: sqlite3.Connection, user_id: str) -> list:
    rows = conn.execute(
        "SELECT thread_id, participant_a_user_id, participant_b_user_id, participant_a_role, "
        "participant_b_role, subject, status, created_at, last_message_at "
        "FROM message_threads_v2 WHERE participant_a_user_id=? OR participant_b_user_id=? "
        "ORDER BY last_message_at DESC NULLS LAST",
        (user_id, user_id),
    ).fetchall()
    return [
        {
            "thread_id": r[0], "participant_a_user_id": r[1], "participant_b_user_id": r[2],
            "participant_a_role": r[3], "participant_b_role": r[4],
            "subject": r[5], "status": r[6], "created_at": r[7], "last_message_at": r[8],
        }
        for r in rows
    ]


def get_thread(conn: sqlite3.Connection, thread_id: str, viewer_user_id: str) -> dict:
    thread = conn.execute(
        "SELECT thread_id, participant_a_user_id, participant_b_user_id, participant_a_role, "
        "participant_b_role, subject, status, created_at, last_message_at "
        "FROM message_threads_v2 WHERE thread_id=?",
        (thread_id,),
    ).fetchone()
    if not thread:
        raise MessagingError("thread_not_found")
    pa, pb = thread[1], thread[2]
    if viewer_user_id not in (pa, pb):
        raise MessagingError("not_participant")
    messages = conn.execute(
        "SELECT message_id, sender_user_id, recipient_user_id, body, status, created_at, read_at "
        "FROM messages_v2 WHERE thread_id=? AND status NOT IN ('hidden','deleted') "
        "ORDER BY created_at ASC",
        (thread_id,),
    ).fetchall()
    return {
        "thread_id": thread[0], "participant_a_user_id": pa, "participant_b_user_id": pb,
        "participant_a_role": thread[3], "participant_b_role": thread[4],
        "subject": thread[5], "status": thread[6], "created_at": thread[7], "last_message_at": thread[8],
        "messages": [
            {
                "message_id": m[0], "sender_user_id": m[1], "recipient_user_id": m[2],
                "body": m[3], "status": m[4], "created_at": m[5], "read_at": m[6],
            }
            for m in messages
        ],
    }


def block_user(
    conn: sqlite3.Connection,
    blocker_user_id: str,
    blocked_user_id: str,
    reason: Optional[str] = None,
) -> dict:
    block_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO message_blocks_v2 (block_id, blocker_user_id, blocked_user_id, reason, created_at) "
            "VALUES (?,?,?,?,?)",
            (block_id, blocker_user_id, blocked_user_id, reason, _now()),
        )
    except sqlite3.IntegrityError:
        pass  # already blocked — idempotent
    # Mark active threads between these users as blocked
    conn.execute(
        "UPDATE message_threads_v2 SET status='blocked' WHERE status='active' AND "
        "((participant_a_user_id=? AND participant_b_user_id=?) OR "
        " (participant_a_user_id=? AND participant_b_user_id=?))",
        (blocker_user_id, blocked_user_id, blocked_user_id, blocker_user_id),
    )
    _audit(conn, blocker_user_id, "messaging/block", blocked_user_id, {"reason": reason})
    return {"blocked": True, "blocker": blocker_user_id, "blocked_user": blocked_user_id}


def report_thread(
    conn: sqlite3.Connection,
    thread_id: str,
    reporter_user_id: str,
    reason: str,
) -> dict:
    thread = conn.execute(
        "SELECT participant_a_user_id, participant_b_user_id FROM message_threads_v2 WHERE thread_id=?",
        (thread_id,),
    ).fetchone()
    if not thread:
        raise MessagingError("thread_not_found")
    if reporter_user_id not in (thread[0], thread[1]):
        raise MessagingError("not_participant")
    report_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO message_reports_v2 (report_id, thread_id, reporter_user_id, reason, created_at) "
        "VALUES (?,?,?,?,?)",
        (report_id, thread_id, reporter_user_id, reason, _now()),
    )
    conn.execute(
        "UPDATE message_threads_v2 SET status='reported', updated_at=? WHERE thread_id=?",
        (_now(), thread_id),
    )
    _audit(conn, reporter_user_id, "messaging/report", thread_id, {"reason": reason})
    return {"reported": True, "report_id": report_id, "thread_id": thread_id}


def soft_hide_message(conn: sqlite3.Connection, message_id: str, actor_user_id: str) -> dict:
    now = _now()
    conn.execute(
        "UPDATE messages_v2 SET status='hidden', hidden_at=? WHERE message_id=?",
        (now, message_id),
    )
    _audit(conn, actor_user_id, "messaging/hide_message", message_id, {})
    return {"hidden": True, "message_id": message_id}


def status() -> dict:
    return {
        "enabled": MESSAGING_V2_ENABLED,
        "daily_recipient_cap": DAILY_RECIPIENT_CAP,
    }
