"""Tests for backend/messaging_v2_router.py — BACKEND.MESSAGING.2-ROUTER-DISABLED.

Disabled mode (default): all action endpoints return 503.
Status endpoint: always-on.
Enabled mode (test-only): thread creation, reply, report, block, abuse controls.

Run: cd backend && python3 -m unittest tests.test_messaging_v2_router
"""
from __future__ import annotations

import importlib
import os
import sqlite3
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MIGRATION_MESSAGING = (ROOT / "migrations" / "006_messaging_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript(MIGRATION_MESSAGING)
    conn.commit()
    return conn


@contextmanager
def reload_router(enabled: bool = False):
    os.environ["MESSAGING_V2_ENABLED"] = "true" if enabled else "false"
    for mod in ["messaging_v2", "messaging_v2_router"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    yield


def _make_app():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import messaging_v2_router
    app = FastAPI()
    app.include_router(messaging_v2_router.router)
    return TestClient(app), messaging_v2_router


def _inject_conn(router_mod, conn):
    class _CtxConn:
        def __enter__(self): return conn
        def __exit__(self, *a): conn.commit()
    router_mod._conn_factory = lambda: _CtxConn()


_THREAD_PAYLOAD = {
    "sender_user_id": "u1",
    "sender_role": "comic",
    "recipient_user_id": "u2",
    "recipient_role": "booker",
    "subject": "Booking inquiry",
    "body": "Hi, I'd love to perform at your venue.",
}


class TestDisabledMode(unittest.TestCase):

    def setUp(self):
        self.ctx = reload_router(enabled=False)
        self.ctx.__enter__()
        self.client, _ = _make_app()

    def tearDown(self):
        self.ctx.__exit__(None, None, None)

    def test_status_always_on(self):
        r = self.client.get("/api/messaging_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], False)

    def test_list_threads_disabled(self):
        r = self.client.get("/api/messaging_v2/threads?user_id=u1")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"]["error"]["code"], "messaging/disabled")

    def test_create_thread_disabled(self):
        r = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        self.assertEqual(r.status_code, 503)

    def test_get_thread_disabled(self):
        r = self.client.get("/api/messaging_v2/threads/fake-id?viewer_user_id=u1")
        self.assertEqual(r.status_code, 503)

    def test_reply_disabled(self):
        r = self.client.post("/api/messaging_v2/threads/fake-id/reply",
                             json={"sender_user_id": "u1", "body": "hello"})
        self.assertEqual(r.status_code, 503)

    def test_report_disabled(self):
        r = self.client.post("/api/messaging_v2/threads/fake-id/report",
                             json={"reporter_user_id": "u1", "reason": "spam"})
        self.assertEqual(r.status_code, 503)

    def test_block_disabled(self):
        r = self.client.post("/api/messaging_v2/users/u2/block",
                             json={"blocker_user_id": "u1"})
        self.assertEqual(r.status_code, 503)

    def test_disabled_creates_no_state(self):
        conn = _fresh_db()
        with reload_router(enabled=False):
            client, router_mod = _make_app()
            _inject_conn(router_mod, conn)
            client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        count = conn.execute("SELECT COUNT(*) FROM message_threads_v2").fetchone()[0]
        self.assertEqual(count, 0)


class TestEnabledMode(unittest.TestCase):

    def setUp(self):
        self.ctx = reload_router(enabled=True)
        self.ctx.__enter__()
        self.client, self.router_mod = _make_app()
        self.conn = _fresh_db()
        _inject_conn(self.router_mod, self.conn)

    def tearDown(self):
        self.conn.close()
        self.ctx.__exit__(None, None, None)

    def test_status_reports_enabled(self):
        r = self.client.get("/api/messaging_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], True)

    def test_create_thread_success(self):
        r = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("thread_id", body)
        self.assertIn("message_id", body)
        self.assertEqual(body["status"], "active")

    def test_list_threads_returns_created(self):
        self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        r = self.client.get("/api/messaging_v2/threads?user_id=u1")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["threads"]), 1)

    def test_get_thread_success(self):
        cr = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        thread_id = cr.json()["thread_id"]
        r = self.client.get(f"/api/messaging_v2/threads/{thread_id}?viewer_user_id=u1")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["thread_id"], thread_id)
        self.assertEqual(len(r.json()["messages"]), 1)

    def test_get_thread_nonparticipant_404(self):
        cr = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        thread_id = cr.json()["thread_id"]
        r = self.client.get(f"/api/messaging_v2/threads/{thread_id}?viewer_user_id=u99")
        self.assertEqual(r.status_code, 404)

    def test_reply_success(self):
        cr = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        thread_id = cr.json()["thread_id"]
        r = self.client.post(f"/api/messaging_v2/threads/{thread_id}/reply",
                             json={"sender_user_id": "u2", "body": "Sounds great!"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("message_id", r.json())

    def test_reply_to_nonexistent_thread_404(self):
        r = self.client.post("/api/messaging_v2/threads/no-such-id/reply",
                             json={"sender_user_id": "u1", "body": "hello"})
        self.assertEqual(r.status_code, 404)

    def test_report_thread(self):
        cr = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        thread_id = cr.json()["thread_id"]
        r = self.client.post(f"/api/messaging_v2/threads/{thread_id}/report",
                             json={"reporter_user_id": "u1", "reason": "spam"})
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["reported"], True)

    def test_block_prevents_new_thread(self):
        # u1 blocks u2
        self.client.post("/api/messaging_v2/users/u2/block",
                         json={"blocker_user_id": "u1", "reason": "unwanted contact"})
        # Now u1 tries to message u2 — should be blocked
        r = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        self.assertEqual(r.status_code, 403)
        self.assertIn("messaging/blocked", r.json()["detail"]["error"]["code"])

    def test_block_is_idempotent(self):
        r1 = self.client.post("/api/messaging_v2/users/u2/block", json={"blocker_user_id": "u1"})
        r2 = self.client.post("/api/messaging_v2/users/u2/block", json={"blocker_user_id": "u1"})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)

    def test_reply_blocked_after_block(self):
        cr = self.client.post("/api/messaging_v2/threads", json=_THREAD_PAYLOAD)
        thread_id = cr.json()["thread_id"]
        # u2 blocks u1
        self.client.post("/api/messaging_v2/users/u1/block", json={"blocker_user_id": "u2"})
        r = self.client.post(f"/api/messaging_v2/threads/{thread_id}/reply",
                             json={"sender_user_id": "u1", "body": "Still here"})
        self.assertEqual(r.status_code, 403)

    def test_missing_body_returns_400(self):
        r = self.client.post("/api/messaging_v2/threads",
                             json={**_THREAD_PAYLOAD, "body": ""})
        self.assertEqual(r.status_code, 400)

    def test_no_external_network_call(self):
        src = (ROOT / "messaging_v2_router.py").read_text()
        for net_lib in ["requests", "httpx", "aiohttp", "urllib.request"]:
            self.assertNotIn(f"import {net_lib}", src)

    def test_no_email_send(self):
        """Router must not invoke any email-sending function."""
        src = (ROOT / "messaging_v2_router.py").read_text()
        self.assertNotIn("send_email", src)
        self.assertNotIn("sendmail", src)
        self.assertNotIn("postmark", src.lower())

    def test_no_paid_feature_activation(self):
        """Router must not check or activate paid messaging features."""
        src = (ROOT / "messaging_v2_router.py").read_text()
        self.assertNotIn("is_feature_unlocked", src)
        self.assertNotIn("comic_plus", src)


if __name__ == "__main__":
    unittest.main()
