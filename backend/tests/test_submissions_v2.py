"""Tests for backend/submissions_v2.py — BACKEND.SUBMIT.1-SCAFFOLD.

Covers every ChatGPT-mandated scenario.
"""
from __future__ import annotations

import os
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Don't depend on env enablement
os.environ.setdefault("SUBMISSIONS_V2_ENABLED", "false")

import submissions_v2 as sv2

SUBS_MIGRATION = (ROOT / "migrations" / "003_submissions_v2.sql").read_text()
AUTH_MIGRATION = (ROOT / "migrations" / "002_auth_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SUBS_MIGRATION)
    conn.executescript(AUTH_MIGRATION)  # for audit_events_v2
    conn.commit()
    return conn


VALID = {
    "submitter_name": "Robert",
    "submitter_email": "r@x.test",
    "submitter_role": "comic",
    "show_name": "Test Show",
    "venue_name": "Test Venue",
    "venue_address": "1 Test St",
    "city": "Paris",
    "language": "EN",
    "source_url": "https://example.com/show1",
    "ticket_url": "https://example.com/tickets1",
    "recurrence_text": "every Wed",
    "next_date_time": "2026-06-10 20:00",
    "notes": "fun show",
    "honeypot": "",
}


class TestSubmissionsV2(unittest.TestCase):

    def setUp(self):
        self.conn = _fresh_db()

    def tearDown(self):
        self.conn.close()

    # ── validation ──

    def test_valid_submission_accepted_needs_review(self):
        res = sv2.create_show_submission(self.conn, dict(VALID))
        self.assertEqual(res["status"], "needs_review")
        self.assertTrue(res["id"])

    def test_missing_required_field_rejected(self):
        bad = dict(VALID); bad["show_name"] = ""
        with self.assertRaises(sv2.SubmissionError):
            sv2.create_show_submission(self.conn, bad)

    def test_invalid_email_rejected(self):
        bad = dict(VALID); bad["submitter_email"] = "not-an-email"
        with self.assertRaises(sv2.SubmissionError):
            sv2.create_show_submission(self.conn, bad)

    def test_invalid_source_url_rejected(self):
        bad = dict(VALID); bad["source_url"] = "javascript:alert(1)"
        with self.assertRaises(sv2.SubmissionError):
            sv2.create_show_submission(self.conn, bad)

    def test_invalid_language_rejected(self):
        bad = dict(VALID); bad["language"] = "ZZ"
        with self.assertRaises(sv2.SubmissionError):
            sv2.create_show_submission(self.conn, bad)

    # ── honeypot / spam ──

    def test_honeypot_filled_marks_spam(self):
        bad = dict(VALID); bad["honeypot"] = "bot"
        res = sv2.create_show_submission(self.conn, bad)
        self.assertEqual(res["status"], "spam")

    # ── duplicate ──

    def test_duplicate_detection_marks_duplicate(self):
        sv2.create_show_submission(self.conn, dict(VALID))
        res2 = sv2.create_show_submission(self.conn, dict(VALID))
        self.assertEqual(res2["status"], "duplicate")

    def test_different_email_not_duplicate(self):
        sv2.create_show_submission(self.conn, dict(VALID))
        other = dict(VALID); other["submitter_email"] = "other@x.test"
        res = sv2.create_show_submission(self.conn, other)
        self.assertEqual(res["status"], "needs_review")

    # ── transitions ──

    def test_approve_transition_works(self):
        res = sv2.create_show_submission(self.conn, dict(VALID))
        ok = sv2.mark_submission_status(self.conn, res["id"], "approved", reviewer="chuck", notes="ok")
        self.assertTrue(ok)

    def test_reject_transition_works(self):
        res = sv2.create_show_submission(self.conn, dict(VALID))
        ok = sv2.mark_submission_status(self.conn, res["id"], "rejected", reviewer="chuck", notes="nope")
        self.assertTrue(ok)

    def test_imported_transition_only_from_approved(self):
        res = sv2.create_show_submission(self.conn, dict(VALID))
        # needs_review -> imported = invalid
        with self.assertRaises(sv2.SubmissionError):
            sv2.mark_submission_status(self.conn, res["id"], "imported")
        sv2.mark_submission_status(self.conn, res["id"], "approved")
        ok = sv2.mark_submission_status(self.conn, res["id"], "imported")
        self.assertTrue(ok)

    def test_invalid_transition_rejected(self):
        res = sv2.create_show_submission(self.conn, dict(VALID))
        sv2.mark_submission_status(self.conn, res["id"], "rejected")
        # rejected is terminal
        with self.assertRaises(sv2.SubmissionError):
            sv2.mark_submission_status(self.conn, res["id"], "approved")

    def test_unknown_submission_id_rejected(self):
        with self.assertRaises(sv2.SubmissionError):
            sv2.mark_submission_status(self.conn, "nope", "approved")

    # ── no public listing created ──

    def test_no_public_listing_created_automatically(self):
        # listings table is part of the legacy schema; the show_submissions_v2
        # row should be the ONLY new row anywhere.
        before = self.conn.execute("SELECT COUNT(*) FROM show_submissions_v2").fetchone()[0]
        sv2.create_show_submission(self.conn, dict(VALID))
        after = self.conn.execute("SELECT COUNT(*) FROM show_submissions_v2").fetchone()[0]
        self.assertEqual(after, before + 1)
        # No public listings table modified in this scaffold (none even exist in :memory:).
        with self.assertRaises(sqlite3.OperationalError):
            self.conn.execute("SELECT COUNT(*) FROM listings").fetchone()

    # ── audit ──

    def test_audit_events_recorded(self):
        res = sv2.create_show_submission(self.conn, dict(VALID))
        sv2.mark_submission_status(self.conn, res["id"], "approved", reviewer="admin")
        rows = self.conn.execute(
            "SELECT action FROM audit_events_v2 ORDER BY id ASC"
        ).fetchall()
        actions = [r[0] for r in rows]
        self.assertIn("submissions.create.needs_review", actions)
        self.assertIn("submissions.transition.approved", actions)

    # ── list ──

    def test_list_pending_returns_only_pending(self):
        a = sv2.create_show_submission(self.conn, dict(VALID))
        b_data = dict(VALID); b_data["submitter_email"] = "b@x.test"
        b = sv2.create_show_submission(self.conn, b_data)
        sv2.mark_submission_status(self.conn, b["id"], "rejected")
        pending = sv2.list_pending_submissions(self.conn)
        ids = [p["id"] for p in pending]
        self.assertIn(a["id"], ids)
        self.assertNotIn(b["id"], ids)

    # ── status helper ──

    def test_status_shape(self):
        s = sv2.status()
        self.assertIn("enabled", s)
        self.assertIn("allowed_statuses", s)


if __name__ == "__main__":
    unittest.main()
