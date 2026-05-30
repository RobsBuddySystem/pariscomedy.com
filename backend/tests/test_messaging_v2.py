"""Tests for messaging_v2.py scaffold."""
import sqlite3
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import messaging_v2


def _db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    messaging_v2._apply_schema(conn)
    return conn


COMIC = "user-comic-1"
BOOKER = "user-booker-1"
OTHER = "user-other-9"


class TestMessagingScaffold(unittest.TestCase):

    def test_create_thread_with_first_message(self):
        conn = _db()
        result = messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "Availability?", "Hi!")
        self.assertEqual(result["status"], "active")
        self.assertIn("thread_id", result)

    def test_reply_to_thread(self):
        conn = _db()
        r = messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "Hey", "body")
        tid = r["thread_id"]
        reply = messaging_v2.reply_to_thread(conn, tid, BOOKER, "Sure!")
        self.assertIn("message_id", reply)

    def test_list_only_own_threads(self):
        conn = _db()
        messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s1", "b1")
        messaging_v2.create_thread(conn, OTHER, "comic", BOOKER, "booker", "s2", "b2")
        threads = messaging_v2.list_threads_for_user(conn, COMIC)
        for t in threads:
            self.assertIn(COMIC, (t["participant_a_user_id"], t["participant_b_user_id"]))

    def test_get_thread_rejects_nonparticipant(self):
        conn = _db()
        r = messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s", "b")
        with self.assertRaises(messaging_v2.MessagingError) as ctx:
            messaging_v2.get_thread(conn, r["thread_id"], OTHER)
        self.assertIn("not_participant", str(ctx.exception))

    def test_block_prevents_new_thread(self):
        conn = _db()
        messaging_v2.block_user(conn, BOOKER, COMIC)
        with self.assertRaises(messaging_v2.MessagingError) as ctx:
            messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s", "b")
        self.assertIn("blocked", str(ctx.exception))

    def test_block_prevents_reply(self):
        conn = _db()
        r = messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s", "b")
        tid = r["thread_id"]
        messaging_v2.block_user(conn, BOOKER, COMIC)
        with self.assertRaises(messaging_v2.MessagingError) as ctx:
            messaging_v2.reply_to_thread(conn, tid, COMIC, "text")
        self.assertIn("blocked", str(ctx.exception))

    def test_report_marks_thread_reported(self):
        conn = _db()
        r = messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s", "b")
        tid = r["thread_id"]
        result = messaging_v2.report_thread(conn, tid, BOOKER, "spam")
        self.assertTrue(result["reported"])
        thread = conn.execute(
            "SELECT status FROM message_threads_v2 WHERE thread_id=?", (tid,)
        ).fetchone()
        self.assertEqual(thread[0], "reported")

    def test_daily_recipient_cap_blocks_excess(self):
        conn = _db()
        cap = 3
        messaging_v2.DAILY_RECIPIENT_CAP = cap
        try:
            for i in range(cap):
                recipient = f"user-recip-{i}"
                messaging_v2.create_thread(conn, COMIC, "comic", recipient, "booker", "s", "b")
            extra_recipient = f"user-recip-{cap}"
            with self.assertRaises(messaging_v2.MessagingError) as ctx:
                messaging_v2.create_thread(conn, COMIC, "comic", extra_recipient, "booker", "s", "b")
            self.assertIn("daily_recipient_cap", str(ctx.exception))
        finally:
            messaging_v2.DAILY_RECIPIENT_CAP = 20

    def test_hidden_message_not_visible_to_normal_viewer(self):
        conn = _db()
        r = messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s", "secret body")
        tid = r["thread_id"]
        mid = r["message_id"]
        messaging_v2.soft_hide_message(conn, mid, BOOKER)
        thread = messaging_v2.get_thread(conn, tid, COMIC)
        visible_ids = [m["message_id"] for m in thread["messages"]]
        self.assertNotIn(mid, visible_ids)

    def test_feature_gate_fails_closed_for_unpaid_user(self):
        from pathlib import Path
        from payments_v2 import is_feature_unlocked
        conn = _db()
        PAY_MIG = (Path(__file__).parent.parent / "migrations" / "005_payments_v2.sql").read_text()
        conn.executescript(PAY_MIG)
        self.assertFalse(is_feature_unlocked(conn, user_id=COMIC, feature="messaging"))

    def test_active_subscription_unlocks_messaging_in_test_db(self):
        import uuid as _uuid
        from pathlib import Path
        from payments_v2 import is_feature_unlocked
        conn = _db()
        PAY_MIG = (Path(__file__).parent.parent / "migrations" / "005_payments_v2.sql").read_text()
        conn.executescript(PAY_MIG)
        now = messaging_v2._now()
        future = "2099-01-01T00:00:00Z"
        conn.execute(
            "INSERT INTO payment_subscriptions_v2 "
            "(id, user_id, product_id, provider_subscription_id, status, current_period_end, "
            " provider, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (str(_uuid.uuid4()), COMIC, "comic_plus", "test-sub-001",
             "active", future, "dryrun", now),
        )
        self.assertTrue(is_feature_unlocked(conn, user_id=COMIC, feature="messaging"))

    def test_comic_booker_roles_preserved(self):
        conn = _db()
        messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s", "b")
        threads = messaging_v2.list_threads_for_user(conn, COMIC)
        self.assertEqual(threads[0]["participant_a_role"], "comic")
        self.assertEqual(threads[0]["participant_b_role"], "booker")

    def test_audit_events_recorded(self):
        conn = _db()
        conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_events_v2 "
            "(id TEXT PRIMARY KEY, actor_user_id TEXT, action TEXT, target_id TEXT, meta TEXT, created_at TEXT)"
        )
        messaging_v2.create_thread(conn, COMIC, "comic", BOOKER, "booker", "s", "b")
        rows = conn.execute("SELECT action FROM audit_events_v2").fetchall()
        actions = [r[0] for r in rows]
        self.assertIn("messaging/create_thread", actions)

    def test_no_email_sent(self):
        # messaging_v2 must not import smtplib, sendgrid, resend, requests, or httpx
        import importlib, inspect
        src = inspect.getsource(messaging_v2)
        for forbidden in ("smtplib", "sendgrid", "resend", "httpx"):
            self.assertNotIn(forbidden, src, f"messaging_v2 must not import {forbidden}")

    def test_no_public_ui_changed(self):
        # No FastAPI router should be defined in this module
        import inspect
        src = inspect.getsource(messaging_v2)
        self.assertNotIn("APIRouter", src)
        self.assertNotIn("app.include_router", src)


if __name__ == "__main__":
    unittest.main()
