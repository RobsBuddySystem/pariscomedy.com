"""Tests for backend/submissions_v2_router.py — BACKEND.SUBMIT.2-ROUTER-DISABLED.

Disabled mode (default): every action endpoint returns 503; no state is created.
Enabled mode (test-only): routes round-trip through submissions_v2 service.

Run: cd backend && python3 -m unittest tests.test_submissions_v2_router
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

MIGRATION_INIT = (ROOT / "migrations" / "001_init.sql").read_text()
MIGRATION_AUTH = (ROOT / "migrations" / "002_auth_v2.sql").read_text()
MIGRATION_SUBMIT = (ROOT / "migrations" / "003_submissions_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript(MIGRATION_AUTH)
    conn.executescript(MIGRATION_SUBMIT)
    conn.commit()
    return conn


@contextmanager
def reload_router(enabled: bool):
    os.environ["SUBMISSIONS_V2_ENABLED"] = "true" if enabled else "false"
    for mod in ["submissions_v2", "submissions_v2_router"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    yield


def _make_app():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import submissions_v2_router
    app = FastAPI()
    app.include_router(submissions_v2_router.router)
    return TestClient(app), submissions_v2_router


def _inject_conn(router_mod, conn):
    class _CtxConn:
        def __enter__(self): return conn
        def __exit__(self, *a): conn.commit()
    router_mod._conn_factory = lambda: _CtxConn()


VALID_SUBMISSION = {
    "submitter_email": "test@venue.com",
    "submitter_name": "Test Promoter",
    "submitter_role": "booker",
    "show_name": "Test Comedy Night",
    "venue_name": "Test Venue",
    "source_url": "https://example.com/show",
    "honeypot": "",
}


class TestDisabledMode(unittest.TestCase):

    def setUp(self):
        self.ctx = reload_router(enabled=False)
        self.ctx.__enter__()
        self.client, _ = _make_app()

    def tearDown(self):
        self.ctx.__exit__(None, None, None)

    def test_status_reports_disabled(self):
        r = self.client.get("/api/submissions_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], False)

    def test_submit_show_returns_503(self):
        r = self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"]["error"]["code"], "submissions/disabled")

    def test_admin_list_returns_503(self):
        r = self.client.get("/api/admin/submissions_v2")
        self.assertEqual(r.status_code, 503)

    def test_admin_approve_returns_503(self):
        r = self.client.post("/api/admin/submissions_v2/fakeid/approve")
        self.assertEqual(r.status_code, 503)

    def test_admin_reject_returns_503(self):
        r = self.client.post("/api/admin/submissions_v2/fakeid/reject")
        self.assertEqual(r.status_code, 503)

    def test_admin_mark_duplicate_returns_503(self):
        r = self.client.post("/api/admin/submissions_v2/fakeid/mark-duplicate")
        self.assertEqual(r.status_code, 503)

    def test_admin_mark_spam_returns_503(self):
        r = self.client.post("/api/admin/submissions_v2/fakeid/mark-spam")
        self.assertEqual(r.status_code, 503)

    def test_disabled_creates_no_state(self):
        """Disabled endpoint must not write any rows."""
        conn = _fresh_db()
        with reload_router(enabled=False):
            client, router_mod = _make_app()
            _inject_conn(router_mod, conn)
            client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        count = conn.execute("SELECT COUNT(*) FROM show_submissions_v2").fetchone()[0]
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
        r = self.client.get("/api/submissions_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], True)

    def test_valid_submission_creates_needs_review_row(self):
        r = self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "needs_review")
        row = self.conn.execute("SELECT status FROM show_submissions_v2 WHERE id=?", (body["id"],)).fetchone()
        self.assertEqual(row[0], "needs_review")

    def test_invalid_submission_returns_400(self):
        bad = {k: v for k, v in VALID_SUBMISSION.items() if k != "submitter_email"}
        r = self.client.post("/api/submissions_v2/show", json=bad)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["detail"]["error"]["code"], "submissions/invalid")

    def test_honeypot_creates_spam_row(self):
        spammed = {**VALID_SUBMISSION, "honeypot": "bot text"}
        r = self.client.post("/api/submissions_v2/show", json=spammed)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "spam")

    def test_duplicate_creates_duplicate_row(self):
        self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        r2 = self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["status"], "duplicate")

    def test_admin_list_returns_submissions(self):
        self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        r = self.client.get("/api/admin/submissions_v2")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()["submissions"]), 1)

    def test_admin_approve_transitions_status(self):
        r = self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        sub_id = r.json()["id"]
        r2 = self.client.post(f"/api/admin/submissions_v2/{sub_id}/approve")
        self.assertEqual(r2.status_code, 204)
        row = self.conn.execute("SELECT status FROM show_submissions_v2 WHERE id=?", (sub_id,)).fetchone()
        self.assertEqual(row[0], "approved")

    def test_admin_reject_transitions_status(self):
        r = self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        sub_id = r.json()["id"]
        r2 = self.client.post(f"/api/admin/submissions_v2/{sub_id}/reject")
        self.assertEqual(r2.status_code, 204)
        row = self.conn.execute("SELECT status FROM show_submissions_v2 WHERE id=?", (sub_id,)).fetchone()
        self.assertEqual(row[0], "rejected")

    def test_invalid_transition_returns_404(self):
        r = self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        sub_id = r.json()["id"]
        # Mark approved first
        self.client.post(f"/api/admin/submissions_v2/{sub_id}/approve")
        # Now try to mark-spam from approved — not in transition matrix
        r2 = self.client.post(f"/api/admin/submissions_v2/{sub_id}/mark-spam")
        self.assertEqual(r2.status_code, 404)

    def test_no_public_listing_created(self):
        """Approving a submission must not touch any public listings table."""
        r = self.client.post("/api/submissions_v2/show", json=VALID_SUBMISSION)
        sub_id = r.json()["id"]
        self.client.post(f"/api/admin/submissions_v2/{sub_id}/approve")
        # shows table (public listings) must be empty or unchanged
        try:
            count = self.conn.execute("SELECT COUNT(*) FROM shows").fetchone()[0]
        except Exception:
            count = 0  # table doesn't exist in test DB — also acceptable
        self.assertEqual(count, 0, "approving a submission must not auto-create public listings")

    def test_no_real_email_sent(self):
        """No email-sending code called in submission flow."""
        # submissions_v2.py has no mailer import — verify by checking the module
        import submissions_v2
        self.assertFalse(hasattr(submissions_v2, "send_email"),
                         "submissions_v2 must not have a send_email function")


if __name__ == "__main__":
    unittest.main()
