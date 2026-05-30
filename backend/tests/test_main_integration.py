"""Integration tests proving auth_v2_router is mounted in main.app
and that production-mode (AUTH_V2_ENABLED=false) returns 503 for every
action endpoint without creating any DB state.

Run: cd backend && python3 -m unittest tests.test_main_integration
"""
from __future__ import annotations

import importlib
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MIGRATION = (ROOT / "migrations" / "002_auth_v2.sql").read_text()


def _setup_db_and_env() -> str:
    """Create a fresh sqlite DB with v1 + v2 migrations applied. Return path."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    db_path = f.name
    init_sql = (ROOT / "migrations" / "001_init.sql").read_text()
    conn = sqlite3.connect(db_path)
    conn.executescript(init_sql)
    conn.executescript(MIGRATION)
    conn.commit()
    conn.close()
    os.environ["DB_PATH"] = db_path
    return db_path


class TestMainIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_path = _setup_db_and_env()
        os.environ["AUTH_V2_ENABLED"] = "false"
        os.environ.setdefault("AUTH_V2_DRY_RUN_MAILER", "true")
        # Force-reload to pick up env changes
        for mod in ("auth_v2", "auth_v2_router", "main"):
            if mod in sys.modules:
                importlib.reload(sys.modules[mod])
        from fastapi.testclient import TestClient
        import main
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(cls.db_path)
        except FileNotFoundError:
            pass

    def test_auth_v2_router_is_mounted(self):
        """/api/auth_v2/status should respond, proving the router was included."""
        r = self.client.get("/api/auth_v2/status")
        self.assertEqual(r.status_code, 200)
        self.assertIn("enabled", r.json())

    def test_status_reports_disabled_in_production_mode(self):
        r = self.client.get("/api/auth_v2/status")
        self.assertIs(r.json()["enabled"], False)

    def test_action_endpoints_return_503_when_disabled(self):
        cases = [
            ("POST", "/api/auth_v2/magic-link/request", {"email": "a@x.test", "role": "user"}),
            ("GET",  "/api/auth_v2/magic-link/consume?token=anything", None),
            ("POST", "/api/auth_v2/logout", None),
            ("GET",  "/api/auth_v2/me", None),
            ("GET",  "/api/auth_v2/session/expiry", None),
        ]
        for method, path, body in cases:
            with self.subTest(method=method, path=path):
                if method == "POST":
                    r = self.client.post(path, json=(body or {}))
                else:
                    r = self.client.get(path)
                self.assertEqual(r.status_code, 503, f"{method} {path} expected 503, got {r.status_code}")
                detail = r.json().get("detail") or {}
                self.assertEqual(detail.get("error", {}).get("code"), "auth/disabled")

    def test_no_v2_db_rows_created_when_endpoints_hit_while_disabled(self):
        # Hit a bunch of disabled endpoints and confirm no row is created in v2 tables
        self.client.post("/api/auth_v2/magic-link/request", json={"email": "ghost@x.test", "role": "user"})
        self.client.get("/api/auth_v2/magic-link/consume?token=fake")
        self.client.post("/api/auth_v2/logout")
        self.client.get("/api/auth_v2/me")
        conn = sqlite3.connect(self.db_path)
        try:
            for table in ("users_v2", "sessions_v2", "magic_links_v2", "audit_events_v2", "rate_limits_v2"):
                row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                self.assertEqual(row[0], 0, f"{table} should have 0 rows while disabled, got {row[0]}")
        finally:
            conn.close()

    def test_legacy_endpoints_still_present(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
