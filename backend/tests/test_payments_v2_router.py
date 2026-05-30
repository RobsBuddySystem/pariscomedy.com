"""Tests for backend/payments_v2_router.py — BACKEND.PAYMENTS.2-ROUTER-DISABLED.

Disabled mode (default): action endpoints return 503; no state created.
Products endpoint: safe to call even when disabled.
Enabled mode (test-only): dry-run checkout, webhook idempotency, feature gate.

Run: cd backend && python3 -m unittest tests.test_payments_v2_router
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
MIGRATION_PAYMENTS = (ROOT / "migrations" / "005_payments_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript(MIGRATION_AUTH)
    conn.executescript(MIGRATION_PAYMENTS)
    conn.commit()
    return conn


@contextmanager
def reload_router(enabled: bool = False, webhooks: bool = False, provider: str = "dryrun"):
    os.environ["PAYMENTS_ENABLED"] = "true" if enabled else "false"
    os.environ["PAYMENT_WEBHOOKS_ENABLED"] = "true" if webhooks else "false"
    os.environ["PAYMENTS_PROVIDER"] = provider
    for mod in ["payments_v2", "payments_v2_router"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    yield


def _make_app():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import payments_v2_router
    app = FastAPI()
    app.include_router(payments_v2_router.router)
    return TestClient(app), payments_v2_router


def _inject_conn(router_mod, conn):
    class _CtxConn:
        def __enter__(self): return conn
        def __exit__(self, *a): conn.commit()
    router_mod._conn_factory = lambda: _CtxConn()


class TestDisabledMode(unittest.TestCase):

    def setUp(self):
        self.ctx = reload_router(enabled=False, webhooks=False)
        self.ctx.__enter__()
        self.client, _ = _make_app()

    def tearDown(self):
        self.ctx.__exit__(None, None, None)

    def test_status_reports_disabled(self):
        r = self.client.get("/api/payments_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], False)
        self.assertEqual(r.json()["provider"], "dryrun")
        self.assertIs(r.json()["webhooks_enabled"], False)

    def test_products_available_when_disabled(self):
        """Product catalog is safe to read regardless of PAYMENTS_ENABLED."""
        r = self.client.get("/api/payments_v2/products")
        self.assertEqual(r.status_code, 200)
        self.assertIn("products", r.json())
        self.assertIs(r.json()["checkout_live"], False)

    def test_checkout_returns_503(self):
        r = self.client.post("/api/payments_v2/checkout-session",
                             json={"user_id": "u1", "product_id": "comic_plus"})
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"]["error"]["code"], "payments/disabled")

    def test_customer_portal_returns_503(self):
        r = self.client.post("/api/payments_v2/customer-portal")
        self.assertEqual(r.status_code, 503)

    def test_subscriptions_returns_503(self):
        r = self.client.get("/api/payments_v2/subscriptions?user_id=u1")
        self.assertEqual(r.status_code, 503)

    def test_webhook_returns_503_when_webhooks_disabled(self):
        r = self.client.post("/api/payments_v2/webhook", content=b'{"type":"test"}',
                             headers={"x-webhook-event-id": "evt_123", "content-type": "application/json"})
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"]["error"]["code"], "payments/webhooks_disabled")

    def test_disabled_checkout_creates_no_state(self):
        conn = _fresh_db()
        with reload_router(enabled=False):
            client, router_mod = _make_app()
            _inject_conn(router_mod, conn)
            client.post("/api/payments_v2/checkout-session",
                        json={"user_id": "u1", "product_id": "comic_plus"})
        count = conn.execute("SELECT COUNT(*) FROM payment_checkout_sessions_v2").fetchone()[0]
        self.assertEqual(count, 0)


class TestEnabledMode(unittest.TestCase):

    def setUp(self):
        self.ctx = reload_router(enabled=True, webhooks=True, provider="dryrun")
        self.ctx.__enter__()
        self.client, self.router_mod = _make_app()
        self.conn = _fresh_db()
        _inject_conn(self.router_mod, self.conn)

    def tearDown(self):
        self.conn.close()
        self.ctx.__exit__(None, None, None)

    def test_status_reports_enabled(self):
        r = self.client.get("/api/payments_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], True)

    def test_products_returns_catalog(self):
        r = self.client.get("/api/payments_v2/products")
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.json()["products"]), 0)

    def test_dryrun_checkout_creates_session(self):
        r = self.client.post("/api/payments_v2/checkout-session",
                             json={"user_id": "u1", "product_id": "comic_plus"})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["mode"], "dryrun")
        self.assertIn("session_id", body["url"])
        row = self.conn.execute("SELECT id FROM payment_checkout_sessions_v2").fetchone()
        self.assertIsNotNone(row)

    def test_invalid_product_returns_400(self):
        r = self.client.post("/api/payments_v2/checkout-session",
                             json={"user_id": "u1", "product_id": "not_a_real_product"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("payments/invalid", r.json()["detail"]["error"]["code"])

    def test_missing_fields_returns_400(self):
        r = self.client.post("/api/payments_v2/checkout-session", json={})
        self.assertEqual(r.status_code, 400)

    def test_webhook_idempotency(self):
        headers = {"x-webhook-event-id": "evt_abc", "content-type": "application/json"}
        r1 = self.client.post("/api/payments_v2/webhook", content=b'{"type":"checkout.completed"}',
                              headers=headers)
        self.assertEqual(r1.status_code, 200)
        self.assertIs(r1.json()["recorded"], True)
        self.assertIs(r1.json()["duplicate"], False)
        # Same event again
        r2 = self.client.post("/api/payments_v2/webhook", content=b'{"type":"checkout.completed"}',
                              headers=headers)
        self.assertEqual(r2.status_code, 200)
        self.assertIs(r2.json()["duplicate"], True)

    def test_subscription_feature_gate(self):
        import payments_v2
        # Apply a subscription directly to test feature gate
        payments_v2.apply_subscription_created(
            self.conn, user_id="u1", product_id="comic_plus",
            provider_subscription_id="sub_test", provider="dryrun",
        )
        self.conn.commit()
        unlocked = payments_v2.is_feature_unlocked(self.conn, user_id="u1", feature="messaging")
        self.assertIsInstance(unlocked, bool)

    def test_subscription_cancelled_removes_unlock(self):
        import payments_v2
        payments_v2.apply_subscription_created(
            self.conn, user_id="u2", product_id="comic_plus",
            provider_subscription_id="sub_cancel", provider="dryrun",
        )
        self.conn.commit()
        payments_v2.apply_subscription_cancelled(self.conn, provider_subscription_id="sub_cancel")
        self.conn.commit()
        row = self.conn.execute(
            "SELECT status FROM payment_subscriptions_v2 WHERE provider_subscription_id='sub_cancel'"
        ).fetchone()
        self.assertEqual(row[0], "cancelled")

    def test_no_external_network_call(self):
        """payments_v2 must not import requests/httpx/urllib externally."""
        import payments_v2 as pv
        src = (ROOT / "payments_v2.py").read_text()
        for net_lib in ["requests", "httpx", "aiohttp", "urllib.request"]:
            self.assertNotIn(f"import {net_lib}", src,
                             f"payments_v2.py must not import {net_lib}")

    def test_no_public_feature_gating_live(self):
        """Pricing page must still have no live checkout CTAs."""
        import subprocess
        result = subprocess.run(
            ["python3", str(ROOT.parent / "scripts" / "regression_guard.py")],
            capture_output=True, text=True, cwd=str(ROOT.parent),
        )
        self.assertIn("pricing_copy_safety", result.stdout)
        # Guard output format: "[PASS] pricing_copy_safety ..."
        self.assertIn("[PASS] pricing_copy_safety", result.stdout)


if __name__ == "__main__":
    unittest.main()
