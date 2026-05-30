"""Tests for backend/auth_v2_router.py — disabled and enabled mode.

Disabled mode (default) — every endpoint returns 503 and creates no state.
Enabled mode (test-only) — endpoints round-trip through auth_v2.

Run: cd backend && python3 -m unittest tests.test_auth_v2_router
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

MIGRATION = (ROOT / "migrations" / "002_auth_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    # check_same_thread=False so FastAPI's threadpool can reuse the in-memory DB
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript(MIGRATION)
    conn.commit()
    return conn


@contextmanager
def reload_router(enabled: bool):
    """Reload auth_v2 + auth_v2_router with a given AUTH_V2_ENABLED flag."""
    os.environ["AUTH_V2_ENABLED"] = "true" if enabled else "false"
    os.environ.setdefault("AUTH_V2_DRY_RUN_MAILER", "true")
    if "auth_v2" in sys.modules:
        importlib.reload(sys.modules["auth_v2"])
    else:
        import auth_v2  # noqa: F401
    if "auth_v2_router" in sys.modules:
        importlib.reload(sys.modules["auth_v2_router"])
    else:
        import auth_v2_router  # noqa: F401
    yield


def _make_app():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import auth_v2_router
    app = FastAPI()
    app.include_router(auth_v2_router.router)
    return TestClient(app), auth_v2_router


class TestDisabledMode(unittest.TestCase):

    def setUp(self):
        self.enter = reload_router(enabled=False)
        self.enter.__enter__()
        self.client, self.router_mod = _make_app()

    def tearDown(self):
        self.enter.__exit__(None, None, None)

    def test_status_reports_disabled(self):
        r = self.client.get("/api/auth_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], False)

    def test_request_returns_503(self):
        r = self.client.post("/api/auth_v2/magic-link/request", json={"email": "a@x.test", "role": "user"})
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"]["error"]["code"], "auth/disabled")

    def test_consume_returns_503(self):
        r = self.client.get("/api/auth_v2/magic-link/consume?token=anything")
        self.assertEqual(r.status_code, 503)

    def test_logout_returns_503(self):
        r = self.client.post("/api/auth_v2/logout")
        self.assertEqual(r.status_code, 503)

    def test_me_returns_503(self):
        r = self.client.get("/api/auth_v2/me")
        self.assertEqual(r.status_code, 503)

    def test_session_expiry_returns_503(self):
        r = self.client.get("/api/auth_v2/session/expiry")
        self.assertEqual(r.status_code, 503)

    def test_no_state_created_when_disabled(self):
        # Even if router is hit, no DB write should occur. We can't check
        # the prod DB; instead verify the request was rejected before the
        # auth_v2 module would run.
        r = self.client.post("/api/auth_v2/magic-link/request", json={"email": "ghost@x.test", "role": "user"})
        self.assertEqual(r.status_code, 503)


class TestEnabledMode(unittest.TestCase):
    """Enabled-mode tests use an in-memory DB injected via _conn_factory monkey-patch."""

    def setUp(self):
        self.enter = reload_router(enabled=True)
        self.enter.__enter__()
        self.client, self.router_mod = _make_app()
        self.conn = _fresh_db()
        # Replace the router's connection factory so all endpoints share the in-memory DB.
        # Wrap to make it usable as a context manager.
        class _CtxConn:
            def __init__(self, c): self.c = c
            def __enter__(self): return self.c
            def __exit__(self, *a): self.c.commit()
        self._conn_holder = self.conn
        self.router_mod._conn_factory = lambda: _CtxConn(self._conn_holder)

    def tearDown(self):
        self.conn.close()
        self.enter.__exit__(None, None, None)

    def test_status_reports_enabled(self):
        r = self.client.get("/api/auth_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["enabled"], True)

    def test_request_returns_204(self):
        r = self.client.post("/api/auth_v2/magic-link/request", json={"email": "a@x.test", "role": "user"})
        self.assertEqual(r.status_code, 204)
        row = self.conn.execute("SELECT email_lower, role FROM magic_links_v2").fetchone()
        self.assertEqual(row[0], "a@x.test")
        self.assertEqual(row[1], "user")

    def test_full_round_trip_consume_me_logout(self):
        # 1) request
        self.client.post("/api/auth_v2/magic-link/request", json={"email": "rt@x.test", "role": "comic"})
        # Pull the raw token from the DB — emulates user clicking magic link.
        # The raw token was logged to stderr; for test we just create a fresh known one.
        # Use the service directly to mint a usable known token under the same in-memory DB.
        import auth_v2
        out = auth_v2.request_magic_link(self.conn, email="rt@x.test", role="comic")
        # 2) consume
        r = self.client.get(f"/api/auth_v2/magic-link/consume?token={out['token']}")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["role"], "comic")
        sess = r.cookies.get("pc_session_v2")
        self.assertTrue(sess)
        # 3) me
        r2 = self.client.get("/api/auth_v2/me", cookies={"pc_session_v2": sess})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["email"], "rt@x.test")
        # 4) logout
        r3 = self.client.post("/api/auth_v2/logout", cookies={"pc_session_v2": sess})
        self.assertEqual(r3.status_code, 204)
        # 5) me after logout → 401
        r4 = self.client.get("/api/auth_v2/me", cookies={"pc_session_v2": sess})
        self.assertEqual(r4.status_code, 401)

    def test_reused_token_rejected(self):
        import auth_v2
        out = auth_v2.request_magic_link(self.conn, email="reuse@x.test", role="user")
        ok = self.client.get(f"/api/auth_v2/magic-link/consume?token={out['token']}")
        self.assertEqual(ok.status_code, 200)
        again = self.client.get(f"/api/auth_v2/magic-link/consume?token={out['token']}")
        self.assertEqual(again.status_code, 401)

    def test_me_without_session_is_401(self):
        r = self.client.get("/api/auth_v2/me")
        self.assertEqual(r.status_code, 401)


class TestRateLimiting(unittest.TestCase):
    """BACKEND.AUTH.4-RATE-LIMITING — HTTP-level rate limit tests."""

    def setUp(self):
        self.enter = reload_router(enabled=True)
        self.enter.__enter__()
        self.client, self.router_mod = _make_app()
        self.conn = _fresh_db()

        class _CtxConn:
            def __init__(self, c): self.c = c
            def __enter__(self): return self.c
            def __exit__(self, *a): self.c.commit()

        self.router_mod._conn_factory = lambda: _CtxConn(self.conn)

    def tearDown(self):
        self.conn.close()
        self.enter.__exit__(None, None, None)

    def _override_limits(self, email=10, ip=30, consume_ip=20):
        """Patch the router's HTTP-level limit constants for testing."""
        self.router_mod._HTTP_RATE_MAGIC_EMAIL = email
        self.router_mod._HTTP_RATE_MAGIC_IP = ip
        self.router_mod._HTTP_RATE_CONSUME_IP = consume_ip

    def test_per_email_limit_blocks_11th_request(self):
        self._override_limits(email=3)
        for i in range(3):
            r = self.client.post("/api/auth_v2/magic-link/request",
                                 json={"email": "limited@x.test", "role": "user"})
            self.assertEqual(r.status_code, 204, f"request {i+1} should succeed")
        r = self.client.post("/api/auth_v2/magic-link/request",
                             json={"email": "limited@x.test", "role": "user"})
        self.assertEqual(r.status_code, 429, "4th request should be rate-limited")

    def test_per_ip_limit_blocks_excess(self):
        self._override_limits(ip=3)
        for i in range(3):
            r = self.client.post("/api/auth_v2/magic-link/request",
                                 json={"email": f"user{i}@x.test", "role": "user"})
            self.assertEqual(r.status_code, 204, f"request {i+1} should succeed")
        r = self.client.post("/api/auth_v2/magic-link/request",
                             json={"email": "user99@x.test", "role": "user"})
        self.assertEqual(r.status_code, 429, "4th request from same IP should be rate-limited")

    def test_different_email_not_blocked_by_per_email_limit(self):
        self._override_limits(email=2, ip=100)
        for i in range(2):
            self.client.post("/api/auth_v2/magic-link/request",
                             json={"email": "first@x.test", "role": "user"})
        # first@x.test is now rate-limited
        r1 = self.client.post("/api/auth_v2/magic-link/request",
                              json={"email": "first@x.test", "role": "user"})
        self.assertEqual(r1.status_code, 429)
        # second@x.test is on a different email bucket — must still succeed
        r2 = self.client.post("/api/auth_v2/magic-link/request",
                              json={"email": "second@x.test", "role": "user"})
        self.assertEqual(r2.status_code, 204, "different email must not be blocked")

    def test_consume_invalid_token_rate_limited_per_ip(self):
        self._override_limits(consume_ip=3)
        for i in range(3):
            r = self.client.get(f"/api/auth_v2/magic-link/consume?token=badtoken{i}")
            self.assertEqual(r.status_code, 401, f"attempt {i+1} should return 401 (invalid token)")
        r = self.client.get("/api/auth_v2/magic-link/consume?token=badtoken_final")
        self.assertEqual(r.status_code, 429, "4th failed consume attempt from same IP should be rate-limited")

    def test_disabled_mode_creates_no_rate_limit_rows(self):
        # Reload as disabled
        with reload_router(enabled=False):
            client, router_mod = _make_app()
            router_mod._conn_factory = lambda: type("_C", (), {
                "__enter__": lambda s: self.conn,
                "__exit__": lambda s, *a: self.conn.commit(),
            })()
            client.post("/api/auth_v2/magic-link/request",
                        json={"email": "ghost@x.test", "role": "user"})
        count = self.conn.execute("SELECT COUNT(*) FROM rate_limits_v2").fetchone()[0]
        self.assertEqual(count, 0, "disabled mode must not write rate-limit rows")

    def test_fail_closed_when_storage_unavailable(self):
        """Rate limiter raises 429 (not 500) when DB is unavailable."""
        import auth_v2

        def _broken_factory():
            class _BrokenConn:
                def __enter__(self): return self
                def __exit__(self, *a): pass
                def execute(self, *a, **kw):
                    raise sqlite3.OperationalError("disk I/O error")
                def commit(self): pass

            return _BrokenConn()

        self.router_mod._conn_factory = _broken_factory
        r = self.client.post("/api/auth_v2/magic-link/request",
                             json={"email": "a@x.test", "role": "user"})
        self.assertEqual(r.status_code, 429, "storage failure must fail closed with 429")
        self.assertEqual(r.json()["detail"]["error"]["code"], "auth/rate_limit_unavailable")


if __name__ == "__main__":
    unittest.main()
