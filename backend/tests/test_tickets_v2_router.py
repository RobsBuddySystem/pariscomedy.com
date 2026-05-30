"""Tests for backend/tickets_v2_router.py — BACKEND.TICKETS.2-ROUTER-DISABLED.

Disabled mode (default): all action/admin endpoints return 503.
Status + adapters: always-on (safe read-only).
Enabled mode (test-only): candidate create, duplicate detect, approve/reject/mark actions, dry-run import.

Run: cd backend && python3 -m unittest tests.test_tickets_v2_router
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

MIGRATION = (ROOT / "migrations" / "007_tickets_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript(MIGRATION)
    conn.commit()
    return conn


@contextmanager
def reload_router(enabled: bool = False):
    os.environ["TICKETS_ADAPTERS_ENABLED"] = "true" if enabled else "false"
    os.environ["TICKET_IMPORTS_ENABLED"] = "false"
    os.environ["AFFILIATE_LINKS_ENABLED"] = "false"
    for mod in ["tickets_v2", "tickets_v2_router"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    yield


def _make_app():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import tickets_v2_router
    app = FastAPI()
    app.include_router(tickets_v2_router.router)
    return TestClient(app), tickets_v2_router


def _inject_conn(router_mod, conn):
    class _CtxConn:
        def __enter__(self): return conn
        def __exit__(self, *a): conn.commit()
    router_mod._conn_factory = lambda: _CtxConn()


_CANDIDATE_PAYLOAD = {
    "source_platform": "eventbrite",
    "source_url": "https://www.eventbrite.com/e/test-show-123",
    "title": "Test Comedy Show",
    "venue_name": "Le Petit Théâtre",
    "city": "Paris",
    "starts_at": "2026-07-01T20:00:00Z",
    "language_guess": "fr",
    "confidence_score": 0.85,
}


class TestDisabledMode(unittest.TestCase):

    def setUp(self):
        self.ctx = reload_router(enabled=False)
        self.ctx.__enter__()
        self.client, _ = _make_app()

    def tearDown(self):
        self.ctx.__exit__(None, None, None)

    def test_status_always_on(self):
        r = self.client.get("/api/tickets_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["adapters_enabled"], False)

    def test_adapters_always_on(self):
        r = self.client.get("/api/tickets_v2/adapters")
        self.assertEqual(r.status_code, 200)
        self.assertIn("adapters", r.json())
        self.assertIs(r.json()["imports_enabled"], False)
        self.assertIs(r.json()["affiliate_links_enabled"], False)

    def test_list_discoveries_disabled(self):
        r = self.client.get("/api/admin/tickets_v2/discoveries")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"]["error"]["code"], "tickets/disabled")

    def test_create_discovery_disabled(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        self.assertEqual(r.status_code, 503)

    def test_approve_disabled(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries/fake-id/approve")
        self.assertEqual(r.status_code, 503)

    def test_reject_disabled(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries/fake-id/reject")
        self.assertEqual(r.status_code, 503)

    def test_mark_duplicate_disabled(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries/fake-id/mark-duplicate")
        self.assertEqual(r.status_code, 503)

    def test_mark_unreachable_disabled(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries/fake-id/mark-unreachable")
        self.assertEqual(r.status_code, 503)

    def test_dry_run_import_disabled(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries/fake-id/dry-run-import")
        self.assertEqual(r.status_code, 503)

    def test_disabled_create_no_state(self):
        conn = _fresh_db()
        with reload_router(enabled=False):
            client, router_mod = _make_app()
            _inject_conn(router_mod, conn)
            client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        count = conn.execute("SELECT COUNT(*) FROM adapter_discoveries_v2").fetchone()[0]
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
        r = self.client.get("/api/tickets_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["adapters_enabled"], True)

    def test_adapters_registry_loads(self):
        r = self.client.get("/api/tickets_v2/adapters")
        self.assertEqual(r.status_code, 200)
        platforms = [a["platform"] for a in r.json()["adapters"]]
        self.assertIn("eventbrite", platforms)
        self.assertIn("instagram", platforms)

    def test_create_candidate_success(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["saved"], True)
        self.assertIn("candidate_id", r.json())

    def test_list_discoveries_returns_created(self):
        self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        r = self.client.get("/api/admin/tickets_v2/discoveries")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["discoveries"]), 1)

    def test_duplicate_detection(self):
        r1 = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        r2 = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        self.assertIs(r2.json()["duplicate_check"]["is_duplicate"], True)

    def test_approve_discovery(self):
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        cid = cr.json()["candidate_id"]
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/approve")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "approved_for_import")

    def test_reject_discovery(self):
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        cid = cr.json()["candidate_id"]
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/reject")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "rejected")

    def test_mark_duplicate(self):
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        cid = cr.json()["candidate_id"]
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/mark-duplicate")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "duplicate_existing")

    def test_mark_unreachable(self):
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        cid = cr.json()["candidate_id"]
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/mark-unreachable")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "source_unreachable")

    def test_dry_run_import_requires_approved(self):
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        cid = cr.json()["candidate_id"]
        # Not yet approved — should fail
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/dry-run-import")
        self.assertEqual(r.status_code, 400)
        self.assertIn("import_blocked", r.json()["detail"]["error"]["code"])

    def test_dry_run_import_approved_returns_draft(self):
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        cid = cr.json()["candidate_id"]
        self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/approve")
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/dry-run-import")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["mode"], "dryrun")
        self.assertIs(body["public_listing_created"], False)

    def test_signal_only_platform_cannot_import(self):
        payload = {**_CANDIDATE_PAYLOAD, "source_platform": "instagram",
                   "source_url": "https://www.instagram.com/p/test123"}
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=payload)
        cid = cr.json()["candidate_id"]
        self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/approve")
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/dry-run-import")
        self.assertEqual(r.status_code, 400)
        self.assertIn("signal_only", r.json()["detail"]["error"]["message"])

    def test_invalid_platform_returns_400(self):
        r = self.client.post("/api/admin/tickets_v2/discoveries",
                             json={**_CANDIDATE_PAYLOAD, "source_platform": "fakebook"})
        self.assertEqual(r.status_code, 400)

    def test_no_public_listing_created(self):
        """Dry-run import must never set public_listing_created=True."""
        cr = self.client.post("/api/admin/tickets_v2/discoveries", json=_CANDIDATE_PAYLOAD)
        cid = cr.json()["candidate_id"]
        self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/approve")
        r = self.client.post(f"/api/admin/tickets_v2/discoveries/{cid}/dry-run-import")
        self.assertIs(r.json()["public_listing_created"], False)

    def test_no_external_network_call(self):
        src = (ROOT / "tickets_v2_router.py").read_text()
        for net_lib in ["requests", "httpx", "aiohttp", "urllib.request"]:
            self.assertNotIn(f"import {net_lib}", src)

    def test_affiliate_links_disabled_in_router(self):
        src = (ROOT / "tickets_v2_router.py").read_text()
        self.assertNotIn("AFFILIATE_LINKS_ENABLED=true", src)
        self.assertNotIn("affiliate_enabled=1", src)


if __name__ == "__main__":
    unittest.main()
