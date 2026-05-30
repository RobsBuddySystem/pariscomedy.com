"""Tests for backend/auth_v2.py — BACKEND.AUTH.1-SCAFFOLD.

Covers ChatGPT-mandated scenarios:
  - old token cannot be reused after new token issued (invalidate_old_tokens)
  - expired token rejected
  - consumed token rejected
  - logout invalidates session
  - role separation (comic vs booker vs admin)
  - unauthenticated request returns None from get_current_user
  - rate limit blocks abuse

Run: cd backend && python3 -m unittest tests.test_auth_v2
"""
from __future__ import annotations

import os
import sqlite3
import sys
import unittest
from datetime import timedelta
from pathlib import Path

# Ensure module under test is importable when run as `python3 -m unittest`
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Force DRY_RUN_MAILER so test output stays quiet/safe
os.environ.setdefault("AUTH_V2_DRY_RUN_MAILER", "true")

import auth_v2  # noqa: E402

MIGRATION = (ROOT / "migrations" / "002_auth_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(MIGRATION)
    conn.commit()
    return conn


class TestAuthV2(unittest.TestCase):

    def setUp(self):
        self.conn = _fresh_db()

    def tearDown(self):
        self.conn.close()

    # ── magic link ──

    def test_magic_link_round_trip(self):
        out = auth_v2.request_magic_link(self.conn, email="a@x.test", role="comic")
        self.assertIn("token", out)
        result = auth_v2.consume_magic_link(self.conn, token=out["token"])
        self.assertEqual(result["role"], "comic")
        self.assertIn("session_id", result)
        self.assertIn("user_id", result)

    def test_consumed_token_rejected(self):
        out = auth_v2.request_magic_link(self.conn, email="b@x.test", role="user")
        auth_v2.consume_magic_link(self.conn, token=out["token"])
        with self.assertRaises(auth_v2.ConsumedTokenError):
            auth_v2.consume_magic_link(self.conn, token=out["token"])

    def test_invalidated_token_cannot_be_consumed(self):
        a = auth_v2.request_magic_link(self.conn, email="c@x.test", role="user")
        # Issuing a "new" token equivalent: invalidate prior live tokens for that email
        n = auth_v2.invalidate_old_tokens_for_email(self.conn, email="c@x.test")
        self.assertEqual(n, 1)
        with self.assertRaises(auth_v2.ConsumedTokenError):
            auth_v2.consume_magic_link(self.conn, token=a["token"])

    def test_expired_token_rejected(self):
        # Force an expired token by directly inserting one
        token = "test-expired-token"
        th = auth_v2._hash_token(token)
        past = auth_v2._iso(auth_v2._now() - timedelta(hours=1))
        self.conn.execute(
            """INSERT INTO magic_links_v2(token_hash,email_lower,role,created_at,expires_at)
               VALUES(?,?,?,?,?)""",
            (th, "d@x.test", "user", past, past),
        )
        with self.assertRaises(auth_v2.ExpiredTokenError):
            auth_v2.consume_magic_link(self.conn, token=token)

    def test_unknown_token_rejected(self):
        with self.assertRaises(auth_v2.InvalidTokenError):
            auth_v2.consume_magic_link(self.conn, token="not-a-real-token")

    # ── rate limit ──

    def test_rate_limit_blocks_after_threshold(self):
        for _ in range(auth_v2.MAGIC_LINK_RATE_PER_HOUR):
            auth_v2.request_magic_link(self.conn, email="rl@x.test", role="user")
        with self.assertRaises(auth_v2.RateLimitedError):
            auth_v2.request_magic_link(self.conn, email="rl@x.test", role="user")

    def test_rate_limit_does_not_affect_other_emails(self):
        for _ in range(auth_v2.MAGIC_LINK_RATE_PER_HOUR):
            auth_v2.request_magic_link(self.conn, email="rl1@x.test", role="user")
        # Different email should still work
        out = auth_v2.request_magic_link(self.conn, email="rl2@x.test", role="user")
        self.assertIn("token", out)

    # ── session ──

    def test_get_current_user_for_valid_session(self):
        out = auth_v2.request_magic_link(self.conn, email="s@x.test", role="comic")
        consumed = auth_v2.consume_magic_link(self.conn, token=out["token"])
        cur = auth_v2.get_current_user(self.conn, session_token=consumed["session_id"])
        self.assertIsNotNone(cur)
        self.assertEqual(cur["role"], "comic")
        self.assertEqual(cur["email"], "s@x.test")

    def test_logout_invalidates_session(self):
        out = auth_v2.request_magic_link(self.conn, email="l@x.test", role="user")
        consumed = auth_v2.consume_magic_link(self.conn, token=out["token"])
        sid = consumed["session_id"]
        self.assertTrue(auth_v2.logout(self.conn, session_id=sid))
        # Idempotent: logging out again returns False
        self.assertFalse(auth_v2.logout(self.conn, session_id=sid))
        # Subsequent get_current_user returns None
        self.assertIsNone(auth_v2.get_current_user(self.conn, session_token=sid))

    def test_empty_or_unknown_session_returns_none(self):
        self.assertIsNone(auth_v2.get_current_user(self.conn, session_token=""))
        self.assertIsNone(auth_v2.get_current_user(self.conn, session_token="fake-session"))

    def test_expired_session_returns_none(self):
        # Insert a user + expired session manually
        self.conn.execute(
            "INSERT INTO users_v2(id,email,email_lower,role,plan,created_at) VALUES(?,?,?,?,?,?)",
            ("u1", "e@x.test", "e@x.test", "user", "free", auth_v2._iso(auth_v2._now())),
        )
        past = auth_v2._iso(auth_v2._now() - timedelta(hours=1))
        self.conn.execute(
            """INSERT INTO sessions_v2(id,user_id,created_at,last_seen_at,expires_at)
               VALUES(?,?,?,?,?)""",
            ("expired-sid", "u1", past, past, past),
        )
        self.assertIsNone(auth_v2.get_current_user(self.conn, session_token="expired-sid"))

    # ── role separation ──

    def test_role_separation_in_returned_session(self):
        out_c = auth_v2.request_magic_link(self.conn, email="c@x.test", role="comic")
        out_b = auth_v2.request_magic_link(self.conn, email="b@x.test", role="booker")
        sc = auth_v2.consume_magic_link(self.conn, token=out_c["token"])
        sb = auth_v2.consume_magic_link(self.conn, token=out_b["token"])
        self.assertEqual(sc["role"], "comic")
        self.assertEqual(sb["role"], "booker")
        # Different users, different sessions, different user_ids
        self.assertNotEqual(sc["user_id"], sb["user_id"])
        self.assertNotEqual(sc["session_id"], sb["session_id"])

    def test_invalid_role_rejected(self):
        with self.assertRaises(auth_v2.InvalidRoleError):
            auth_v2.request_magic_link(self.conn, email="x@x.test", role="superuser")

    # ── audit log ──

    def test_audit_event_recorded_on_consume(self):
        out = auth_v2.request_magic_link(self.conn, email="au@x.test", role="user")
        auth_v2.consume_magic_link(self.conn, token=out["token"])
        rows = self.conn.execute(
            "SELECT action FROM audit_events_v2 ORDER BY id ASC"
        ).fetchall()
        actions = [r[0] for r in rows]
        self.assertIn("auth.magic_link.request", actions)
        self.assertIn("auth.magic_link.consume", actions)

    # ── module status ──

    def test_status_returns_expected_shape(self):
        # Don't assert env-dependent enabled flag — other test modules may
        # set AUTH_V2_ENABLED=true. Assert shape + roles instead.
        s = auth_v2.status()
        self.assertIn("enabled", s)
        self.assertIn("dry_run_mailer", s)
        self.assertEqual(s["roles"], ["user", "comic", "booker", "admin"])


if __name__ == "__main__":
    unittest.main()
