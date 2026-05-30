"""Tests for tickets_v2.py scaffold."""
import sqlite3
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tickets_v2


def _db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    tickets_v2._apply_schema(conn)
    return conn


def _candidate(platform="eventbrite", **kwargs):
    raw = {
        "source_platform": platform,
        "source_url": kwargs.get("source_url", "https://www.eventbrite.fr/e/test-123"),
        "title": kwargs.get("title", "Test Show"),
        "venue_name": "Le Test Club",
        "starts_at": "2026-06-15T20:00:00Z",
        "confidence_score": 0.9,
        **{k: v for k, v in kwargs.items() if k not in ("source_url", "title")},
    }
    return tickets_v2.normalize_candidate(raw)


class TestTicketsScaffold(unittest.TestCase):

    def test_adapter_registry_loads(self):
        result = tickets_v2.list_adapters()
        platforms = [a["platform"] for a in result]
        self.assertIn("eventbrite", platforms)
        self.assertIn("billetreduc", platforms)
        self.assertIn("instagram", platforms)
        self.assertIn("facebook", platforms)
        self.assertEqual(len(platforms), 15)

    def test_unknown_platform_rejected(self):
        with self.assertRaises(tickets_v2.TicketsError) as ctx:
            tickets_v2.normalize_candidate({"source_platform": "unknown_xyz", "source_url": "http://x.com"})
        self.assertIn("unknown_platform", str(ctx.exception))

    def test_candidate_normalized(self):
        c = _candidate()
        self.assertEqual(c["review_status"], "needs_review")
        self.assertEqual(c["affiliate_enabled"], 0)
        self.assertEqual(c["city"], "Paris")
        self.assertIn("candidate_id", c)

    def test_candidate_saved_as_needs_review(self):
        conn = _db()
        c = _candidate()
        tickets_v2.save_candidate(conn, c)
        row = conn.execute("SELECT review_status FROM adapter_discoveries_v2 WHERE candidate_id=?",
                           (c["candidate_id"],)).fetchone()
        self.assertEqual(row[0], "needs_review")

    def test_duplicate_detection_works(self):
        conn = _db()
        c1 = _candidate(source_url="https://www.eventbrite.fr/e/same-url")
        c2 = _candidate(source_url="https://www.eventbrite.fr/e/same-url")
        tickets_v2.save_candidate(conn, c1)
        tickets_v2.save_candidate(conn, c2)
        result = tickets_v2.detect_candidate_duplicate(conn, c2)
        self.assertTrue(result["is_duplicate"])

    def test_duplicate_cannot_auto_import(self):
        conn = _db()
        c = _candidate()
        tickets_v2.save_candidate(conn, c)
        conn.execute("UPDATE adapter_discoveries_v2 SET review_status='approved_for_import', "
                     "duplicate_match_status='duplicate_existing' WHERE candidate_id=?",
                     (c["candidate_id"],))
        with self.assertRaises(tickets_v2.TicketsError) as ctx:
            tickets_v2.import_candidate_dry_run(conn, c["candidate_id"])
        self.assertIn("duplicate_existing", str(ctx.exception))

    def test_rejected_cannot_import(self):
        conn = _db()
        c = _candidate()
        tickets_v2.save_candidate(conn, c)
        tickets_v2.mark_candidate_status(conn, c["candidate_id"], "rejected")
        with self.assertRaises(tickets_v2.TicketsError) as ctx:
            tickets_v2.import_candidate_dry_run(conn, c["candidate_id"])
        self.assertIn("import_blocked", str(ctx.exception))

    def test_approved_dry_run_returns_draft_only(self):
        conn = _db()
        c = _candidate()
        tickets_v2.save_candidate(conn, c)
        tickets_v2.mark_candidate_status(conn, c["candidate_id"], "approved_for_import")
        result = tickets_v2.import_candidate_dry_run(conn, c["candidate_id"])
        self.assertEqual(result["mode"], "dryrun")
        self.assertFalse(result["public_listing_created"])
        self.assertIn("draft_listing", result)

    def test_signal_only_platform_cannot_import(self):
        conn = _db()
        c = _candidate(platform="instagram", source_url="https://www.instagram.com/p/test")
        tickets_v2.save_candidate(conn, c)
        tickets_v2.mark_candidate_status(conn, c["candidate_id"], "approved_for_import")
        with self.assertRaises(tickets_v2.TicketsError) as ctx:
            tickets_v2.import_candidate_dry_run(conn, c["candidate_id"])
        self.assertIn("signal_only", str(ctx.exception))

    def test_affiliate_fields_default_disabled(self):
        c = _candidate()
        self.assertEqual(c["affiliate_enabled"], 0)

    def test_source_unreachable_status_works(self):
        conn = _db()
        c = _candidate()
        tickets_v2.save_candidate(conn, c)
        result = tickets_v2.mark_candidate_status(conn, c["candidate_id"], "source_unreachable")
        self.assertEqual(result["status"], "source_unreachable")

    def test_audit_events_recorded(self):
        conn = _db()
        conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_events_v2 "
            "(id TEXT PRIMARY KEY, actor_user_id TEXT, action TEXT, target_id TEXT, meta TEXT, created_at TEXT)"
        )
        c = _candidate()
        tickets_v2.save_candidate(conn, c)
        tickets_v2.mark_candidate_status(conn, c["candidate_id"], "rejected", reviewer="admin-1")
        rows = conn.execute("SELECT action FROM audit_events_v2").fetchall()
        self.assertTrue(any("tickets/" in r[0] for r in rows))

    def test_no_public_listing_created_automatically(self):
        conn = _db()
        c = _candidate()
        tickets_v2.save_candidate(conn, c)
        # Candidates in needs_review cannot import
        with self.assertRaises(tickets_v2.TicketsError):
            tickets_v2.import_candidate_dry_run(conn, c["candidate_id"])

    def test_no_network_call_in_module(self):
        import inspect
        src = inspect.getsource(tickets_v2)
        for forbidden in ("requests", "httpx", "urllib.request", "aiohttp"):
            self.assertNotIn(forbidden, src, f"tickets_v2 must not import {forbidden}")


if __name__ == "__main__":
    unittest.main()
