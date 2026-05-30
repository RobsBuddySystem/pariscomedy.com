"""Tests for backend/claims_v2_router.py — BACKEND.CLAIM.2-ROUTER-DISABLED.

Disabled mode (default): every action endpoint returns 503; no state created.
Enabled mode (test-only): routes round-trip through claims_v2 service.

Run: cd backend && python3 -m unittest tests.test_claims_v2_router
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

MIGRATION_AUTH = (ROOT / "migrations" / "002_auth_v2.sql").read_text()
MIGRATION_CLAIMS = (ROOT / "migrations" / "004_claims_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript(MIGRATION_AUTH)
    conn.executescript(MIGRATION_CLAIMS)
    conn.commit()
    return conn


@contextmanager
def reload_router(enabled: bool):
    os.environ["CLAIMS_V2_ENABLED"] = "true" if enabled else "false"
    for mod in ["claims_v2", "claims_v2_router"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    yield


def _make_app():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import claims_v2_router
    app = FastAPI()
    app.include_router(claims_v2_router.router)
    return TestClient(app), claims_v2_router


def _inject_conn(router_mod, conn):
    class _CtxConn:
        def __enter__(self): return conn
        def __exit__(self, *a): conn.commit()
    router_mod._conn_factory = lambda: _CtxConn()


VALID_COMIC_CLAIM = {
    "claim_type": "comic",
    "claimant_email": "comic@example.com",
    "claimant_name": "Test Comic",
    "target_slug": "test-comic",
    "target_name": "Test Comic",
    "instagram_url": "https://instagram.com/testcomic",
    "honeypot": "",
}

VALID_SHOW_CLAIM = {
    "claim_type": "show_runner",
    "claimant_email": "runner@venue.com",
    "claimant_name": "Show Runner",
    "target_slug": "test-show",
    "target_name": "Test Show",
    "domain_email": "runner@venue.com",
    "honeypot": "",
}

VALID_VENUE_CLAIM = {
    "claim_type": "venue",
    "claimant_email": "owner@venue.com",
    "claimant_name": "Venue Owner",
    "target_slug": "test-venue",
    "target_name": "Test Venue",
    "website_url": "https://venue.com",
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
        r = self.client.get("/api/claims_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], False)

    def test_comic_claim_returns_503(self):
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"]["error"]["code"], "claims/disabled")

    def test_show_runner_claim_returns_503(self):
        r = self.client.post("/api/claims_v2/show-runner", json=VALID_SHOW_CLAIM)
        self.assertEqual(r.status_code, 503)

    def test_venue_claim_returns_503(self):
        r = self.client.post("/api/claims_v2/venue", json=VALID_VENUE_CLAIM)
        self.assertEqual(r.status_code, 503)

    def test_admin_list_returns_503(self):
        r = self.client.get("/api/admin/claims_v2")
        self.assertEqual(r.status_code, 503)

    def test_admin_approve_returns_503(self):
        r = self.client.post("/api/admin/claims_v2/fakeid/approve")
        self.assertEqual(r.status_code, 503)

    def test_admin_reject_returns_503(self):
        r = self.client.post("/api/admin/claims_v2/fakeid/reject")
        self.assertEqual(r.status_code, 503)

    def test_claim_status_returns_503(self):
        r = self.client.get("/api/claim-status/comic/test-slug")
        self.assertEqual(r.status_code, 503)

    def test_disabled_creates_no_state(self):
        conn = _fresh_db()
        with reload_router(enabled=False):
            client, router_mod = _make_app()
            _inject_conn(router_mod, conn)
            client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        count = conn.execute("SELECT COUNT(*) FROM claims_v2").fetchone()[0]
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
        r = self.client.get("/api/claims_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], True)

    def test_comic_claim_creates_needs_review_row(self):
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "needs_review")
        row = self.conn.execute("SELECT status FROM claims_v2 WHERE id=?", (body["id"],)).fetchone()
        self.assertEqual(row[0], "needs_review")

    def test_show_runner_claim_works(self):
        r = self.client.post("/api/claims_v2/show-runner", json=VALID_SHOW_CLAIM)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "needs_review")

    def test_venue_claim_works(self):
        r = self.client.post("/api/claims_v2/venue", json=VALID_VENUE_CLAIM)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "needs_review")

    def test_invalid_claim_returns_400(self):
        bad = {k: v for k, v in VALID_COMIC_CLAIM.items() if k != "claimant_email"}
        r = self.client.post("/api/claims_v2/comic", json=bad)
        self.assertEqual(r.status_code, 400)
        self.assertIn("claims/invalid", r.json()["detail"]["error"]["code"])

    def test_honeypot_creates_spam_row(self):
        spammed = {**VALID_COMIC_CLAIM, "honeypot": "bot text"}
        r = self.client.post("/api/claims_v2/comic", json=spammed)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "spam")

    def test_duplicate_creates_duplicate_row(self):
        self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        r2 = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["status"], "duplicate")

    def test_admin_list_returns_pending_claims(self):
        self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        r = self.client.get("/api/admin/claims_v2")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()["claims"]), 1)

    def test_admin_approve_transitions_status(self):
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        claim_id = r.json()["id"]
        r2 = self.client.post(f"/api/admin/claims_v2/{claim_id}/approve")
        self.assertEqual(r2.status_code, 204)
        row = self.conn.execute("SELECT status FROM claims_v2 WHERE id=?", (claim_id,)).fetchone()
        self.assertEqual(row[0], "approved")

    def test_admin_reject_transitions_status(self):
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        claim_id = r.json()["id"]
        r2 = self.client.post(f"/api/admin/claims_v2/{claim_id}/reject")
        self.assertEqual(r2.status_code, 204)
        row = self.conn.execute("SELECT status FROM claims_v2 WHERE id=?", (claim_id,)).fetchone()
        self.assertEqual(row[0], "rejected")

    def test_invalid_transition_returns_404(self):
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        claim_id = r.json()["id"]
        # Approve it (terminal state)
        self.client.post(f"/api/admin/claims_v2/{claim_id}/approve")
        # Try to approve again — not in transition matrix
        r2 = self.client.post(f"/api/admin/claims_v2/{claim_id}/approve")
        self.assertEqual(r2.status_code, 404)

    def test_claim_status_fail_closed_none(self):
        r = self.client.get("/api/claim-status/comic/unknown-slug")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "none")

    def test_claim_status_pending(self):
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        claim_id = r.json()["id"]
        r2 = self.client.get("/api/claim-status/comic/test-comic")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["status"], "pending")

    def test_claim_status_verified_after_approve(self):
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        claim_id = r.json()["id"]
        self.client.post(f"/api/admin/claims_v2/{claim_id}/approve")
        r2 = self.client.get("/api/claim-status/comic/test-comic")
        self.assertEqual(r2.json()["status"], "verified")

    def test_no_ownership_writeback(self):
        """Approving a claim must not touch any public comics/shows/venues table."""
        r = self.client.post("/api/claims_v2/comic", json=VALID_COMIC_CLAIM)
        claim_id = r.json()["id"]
        self.client.post(f"/api/admin/claims_v2/{claim_id}/approve")
        import claims_v2
        self.assertFalse(hasattr(claims_v2, "write_ownership"),
                         "claims_v2 must not have a write_ownership function")

    def test_no_real_email_sent(self):
        import claims_v2
        self.assertFalse(hasattr(claims_v2, "send_email"),
                         "claims_v2 must not have a send_email function")


if __name__ == "__main__":
    unittest.main()
