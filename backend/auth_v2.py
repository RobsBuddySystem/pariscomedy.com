"""BACKEND.AUTH.1-SCAFFOLD — v2 auth service module.

INERT BY DEFAULT. Nothing in main.py wires these functions until
AUTH_V2_ENABLED=true AND the cutover lands in a separate phase.

Scope (per ChatGPT BACKEND.AUTH.1-SCAFFOLD spec):
- request_magic_link(email, role)
- consume_magic_link(token)
- invalidate_old_tokens_for_email(email)
- create_session(user_id, role)
- logout(session_id)
- get_current_user(session_token)
- audit log helper

Safety:
- AUTH_V2_ENABLED env var defaults to "false" — module read but no
  endpoints exposed unless main.py wires them behind the same flag.
- All magic-link tokens are hashed (SHA-256) before storage.
- Single-use enforcement: a consumed token is rejected on re-use.
- Token expiry default 15 minutes. Session default 14 days rolling.
- Rate limit defaults: 10 magic-link requests / email / hour.
- DRY_RUN_MAILER=true (default) means emails are written to stderr
  rather than sent. Production mailer wiring lands later.

This module DOES NOT mutate any v1 tables (users, booker_sessions, etc.).
Rollback: delete this file + migrations/002_auth_v2.{sql,rollback.sql}.
"""
from __future__ import annotations

import dataclasses
import hashlib
import os
import re
import secrets
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

AUTH_V2_ENABLED = os.environ.get("AUTH_V2_ENABLED", "false").lower() in (
    "1", "true", "yes", "on",
)
DRY_RUN_MAILER = os.environ.get("AUTH_V2_DRY_RUN_MAILER", "true").lower() in (
    "1", "true", "yes", "on",
)

MAGIC_LINK_TTL = timedelta(minutes=15)
SESSION_TTL = timedelta(days=14)
MAGIC_LINK_RATE_PER_HOUR = 10
ROLES = ("user", "comic", "booker", "admin")


# ── Errors ───────────────────────────────────────────────────────────────────

class AuthV2Error(Exception):
    code: str = "auth/error"
    http_status: int = 400


class RateLimitedError(AuthV2Error):
    code = "auth/rate_limited"
    http_status = 429


class InvalidTokenError(AuthV2Error):
    code = "auth/invalid_token"
    http_status = 401


class ExpiredTokenError(AuthV2Error):
    code = "auth/expired_token"
    http_status = 401


class ConsumedTokenError(AuthV2Error):
    code = "auth/consumed_token"
    http_status = 401


class InvalidRoleError(AuthV2Error):
    code = "auth/invalid_role"
    http_status = 400


# ── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _parse_iso(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def _normalize_email(email: str) -> tuple[str, str]:
    if not isinstance(email, str) or "@" not in email:
        raise AuthV2Error("invalid email")
    e = email.strip()
    return e, e.lower()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _new_id() -> str:
    # ULID would be nicer; uuid4 hex is fine for v1 scaffold.
    return uuid.uuid4().hex


def _new_token(length_bytes: int = 24) -> str:
    return secrets.token_urlsafe(length_bytes)


def _check_role(role: str) -> str:
    if role not in ROLES:
        raise InvalidRoleError(f"invalid role: {role}")
    return role


# ── Rate limiter (simple per-hour bucket) ────────────────────────────────────

def _check_rate(conn: sqlite3.Connection, bucket: str, key: str, limit: int) -> None:
    now = _now()
    window_start = _iso(now.replace(minute=0, second=0))
    row = conn.execute(
        "SELECT count FROM rate_limits_v2 WHERE bucket=? AND key=? AND window_start=?",
        (bucket, key, window_start),
    ).fetchone()
    count = (row[0] if row else 0)
    if count >= limit:
        raise RateLimitedError(f"limit {limit}/hour exceeded")
    if row:
        conn.execute(
            "UPDATE rate_limits_v2 SET count=count+1 WHERE bucket=? AND key=? AND window_start=?",
            (bucket, key, window_start),
        )
    else:
        conn.execute(
            "INSERT INTO rate_limits_v2(bucket, key, window_start, count) VALUES(?,?,?,1)",
            (bucket, key, window_start),
        )


# ── Audit log ────────────────────────────────────────────────────────────────

def audit(
    conn: sqlite3.Connection,
    *,
    user_id: Optional[str],
    actor_role: str,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata_json: Optional[str] = None,
    ip: Optional[str] = None,
) -> None:
    conn.execute(
        """INSERT INTO audit_events_v2
           (user_id, actor_role, action, target_type, target_id, metadata_json, created_at, ip)
           VALUES (?,?,?,?,?,?,?,?)""",
        (user_id, actor_role, action, target_type, target_id, metadata_json, _iso(_now()), ip),
    )


# ── Magic link (request + consume) ───────────────────────────────────────────

def request_magic_link(
    conn: sqlite3.Connection,
    *,
    email: str,
    role: str,
    ip: Optional[str] = None,
) -> dict:
    """Issue a single-use magic-link token. Returns the raw token (only
    surfaced to the caller for email send; not stored in raw form).

    Caller is responsible for emailing the token to the user. If
    DRY_RUN_MAILER is true the caller may instead log it to stderr.
    """
    _check_role(role)
    _, email_lower = _normalize_email(email)
    _check_rate(conn, "auth.magic_link.email", email_lower, MAGIC_LINK_RATE_PER_HOUR)
    if ip:
        _check_rate(conn, "auth.magic_link.ip", ip, MAGIC_LINK_RATE_PER_HOUR * 3)

    token = _new_token()
    now = _now()
    expires_at = now + MAGIC_LINK_TTL
    conn.execute(
        """INSERT INTO magic_links_v2
           (token_hash, email_lower, role, created_at, expires_at, ip)
           VALUES (?,?,?,?,?,?)""",
        (_hash_token(token), email_lower, role, _iso(now), _iso(expires_at), ip),
    )
    audit(conn, user_id=None, actor_role="system", action="auth.magic_link.request",
          target_type="email", target_id=email_lower, ip=ip)

    if DRY_RUN_MAILER:
        sys.stderr.write(f"[auth_v2 DRY_RUN_MAILER] magic-link for {email_lower} role={role}: {token}\n")
    return {"token": token, "expires_at": _iso(expires_at)}


def consume_magic_link(
    conn: sqlite3.Connection,
    *,
    token: str,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> dict:
    """Single-use consumption: token may be consumed exactly once.

    Returns a freshly created session.
    """
    th = _hash_token(token)
    row = conn.execute(
        """SELECT email_lower, role, expires_at, consumed_at
           FROM magic_links_v2 WHERE token_hash=?""",
        (th,),
    ).fetchone()
    if not row:
        raise InvalidTokenError("token not found")
    email_lower, role, expires_at, consumed_at = row
    if consumed_at:
        raise ConsumedTokenError("token already consumed")
    if _parse_iso(expires_at) <= _now():
        raise ExpiredTokenError("token expired")

    # Mark consumed BEFORE creating session — single-use enforcement.
    conn.execute(
        "UPDATE magic_links_v2 SET consumed_at=? WHERE token_hash=?",
        (_iso(_now()), th),
    )

    user_id = _upsert_user(conn, email=email_lower, role=role)
    session = create_session(conn, user_id=user_id, ip=ip, user_agent=user_agent)
    audit(conn, user_id=user_id, actor_role=role, action="auth.magic_link.consume",
          target_type="session", target_id=session["session_id"], ip=ip)
    return {"user_id": user_id, **session, "role": role}


def invalidate_old_tokens_for_email(
    conn: sqlite3.Connection,
    *,
    email: str,
) -> int:
    """Mark every unconsumed, unexpired magic link for an email as consumed
    so issuing a new token invalidates any earlier one in flight.
    Returns count invalidated.
    """
    _, email_lower = _normalize_email(email)
    cur = conn.execute(
        """UPDATE magic_links_v2
           SET consumed_at=?
           WHERE email_lower=? AND consumed_at IS NULL AND expires_at > ?""",
        (_iso(_now()), email_lower, _iso(_now())),
    )
    return cur.rowcount


# ── User upsert ──────────────────────────────────────────────────────────────

def _upsert_user(conn: sqlite3.Connection, *, email: str, role: str) -> str:
    _check_role(role)
    _, email_lower = _normalize_email(email)
    row = conn.execute(
        "SELECT id FROM users_v2 WHERE email_lower=?",
        (email_lower,),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE users_v2 SET last_login_at=? WHERE id=?",
            (_iso(_now()), row[0]),
        )
        return row[0]
    user_id = _new_id()
    conn.execute(
        """INSERT INTO users_v2(id, email, email_lower, role, plan, created_at, last_login_at)
           VALUES (?,?,?,?,'free',?,?)""",
        (user_id, email_lower, email_lower, role, _iso(_now()), _iso(_now())),
    )
    return user_id


# ── Session lifecycle ────────────────────────────────────────────────────────

def create_session(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> dict:
    session_id = _new_token(32)
    now = _now()
    expires_at = now + SESSION_TTL
    conn.execute(
        """INSERT INTO sessions_v2(id, user_id, created_at, last_seen_at, expires_at, ip, user_agent)
           VALUES(?,?,?,?,?,?,?)""",
        (session_id, user_id, _iso(now), _iso(now), _iso(expires_at), ip, user_agent),
    )
    return {"session_id": session_id, "expires_at": _iso(expires_at)}


def logout(conn: sqlite3.Connection, *, session_id: str) -> bool:
    cur = conn.execute(
        "UPDATE sessions_v2 SET revoked_at=? WHERE id=? AND revoked_at IS NULL",
        (_iso(_now()), session_id),
    )
    if cur.rowcount:
        audit(conn, user_id=None, actor_role="user", action="auth.logout",
              target_type="session", target_id=session_id)
        return True
    return False


def get_current_user(conn: sqlite3.Connection, *, session_token: str) -> Optional[dict]:
    """Return {user_id, email, role, expires_at} for a valid session token, or
    None for any invalid/expired/revoked state."""
    if not session_token:
        return None
    row = conn.execute(
        """SELECT s.user_id, s.expires_at, s.revoked_at, u.email_lower, u.role
           FROM sessions_v2 s JOIN users_v2 u ON u.id = s.user_id
           WHERE s.id=?""",
        (session_token,),
    ).fetchone()
    if not row:
        return None
    user_id, expires_at, revoked_at, email_lower, role = row
    if revoked_at:
        return None
    if _parse_iso(expires_at) <= _now():
        return None
    # Touch last_seen_at — best-effort, no error if it fails.
    try:
        conn.execute("UPDATE sessions_v2 SET last_seen_at=? WHERE id=?",
                     (_iso(_now()), session_token))
    except Exception:
        pass
    return {
        "user_id": user_id,
        "email": email_lower,
        "role": role,
        "expires_at": expires_at,
    }


# ── Module-level introspection ───────────────────────────────────────────────

def status() -> dict:
    """Returned by /api/auth_v2/status (also disabled-by-default)."""
    return {
        "enabled": AUTH_V2_ENABLED,
        "dry_run_mailer": DRY_RUN_MAILER,
        "magic_link_ttl_minutes": int(MAGIC_LINK_TTL.total_seconds() / 60),
        "session_ttl_days": SESSION_TTL.days,
        "rate_per_hour": MAGIC_LINK_RATE_PER_HOUR,
        "roles": list(ROLES),
    }
