"""Tests for backend/claims_v2.py — BACKEND.CLAIM.1-SCAFFOLD."""
from __future__ import annotations

import os, sqlite3, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("CLAIMS_V2_ENABLED", "false")
import claims_v2 as cv2

CLAIMS_MIG = (ROOT / "migrations" / "004_claims_v2.sql").read_text()
AUTH_MIG = (ROOT / "migrations" / "002_auth_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(CLAIMS_MIG)
    conn.executescript(AUTH_MIG)
    conn.commit()
    return conn


COMIC = {
    "claim_type": "comic",
    "claimant_name": "X",
    "claimant_email": "x@x.test",
    "target_id": "c-001",
    "target_slug": "robert-hoehn",
    "target_name": "Robert Hoehn",
    "instagram_url": "https://instagram.com/x",
    "recent_post_url": "https://instagram.com/x/p/1",
    "honeypot": "",
}
SHOW = dict(COMIC, claim_type="show_runner", target_slug="ffcn", target_id="s-3", target_name="FFCN")
VENUE = dict(COMIC, claim_type="venue", target_slug="velvet-bar", target_id="v-9", target_name="Velvet Bar")


class TestClaimsV2(unittest.TestCase):

    def setUp(self):
        self.conn = _fresh_db()

    def tearDown(self):
        self.conn.close()

    def test_valid_comic_claim(self):
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        self.assertEqual(r["status"], "needs_review")

    def test_valid_show_runner_claim(self):
        r = cv2.create_claim_request(self.conn, dict(SHOW))
        self.assertEqual(r["status"], "needs_review")

    def test_valid_venue_claim(self):
        r = cv2.create_claim_request(self.conn, dict(VENUE))
        self.assertEqual(r["status"], "needs_review")

    def test_missing_email_rejected(self):
        bad = dict(COMIC); bad["claimant_email"] = ""
        with self.assertRaises(cv2.ClaimError):
            cv2.create_claim_request(self.conn, bad)

    def test_invalid_email_rejected(self):
        bad = dict(COMIC); bad["claimant_email"] = "not-an-email"
        with self.assertRaises(cv2.ClaimError):
            cv2.create_claim_request(self.conn, bad)

    def test_invalid_claim_type_rejected(self):
        bad = dict(COMIC); bad["claim_type"] = "owner"
        with self.assertRaises(cv2.ClaimError):
            cv2.create_claim_request(self.conn, bad)

    def test_missing_target_rejected(self):
        bad = dict(COMIC); bad["target_id"] = ""; bad["target_slug"] = ""
        with self.assertRaises(cv2.ClaimError):
            cv2.create_claim_request(self.conn, bad)

    def test_no_evidence_rejected(self):
        bad = dict(COMIC)
        for f in cv2.EVIDENCE_FIELDS:
            bad[f] = ""
        with self.assertRaises(cv2.ClaimError):
            cv2.create_claim_request(self.conn, bad)

    def test_invalid_url_rejected(self):
        bad = dict(COMIC); bad["instagram_url"] = "javascript:alert(1)"
        with self.assertRaises(cv2.ClaimError):
            cv2.create_claim_request(self.conn, bad)

    def test_honeypot_marks_spam(self):
        bad = dict(COMIC); bad["honeypot"] = "bot"
        r = cv2.create_claim_request(self.conn, bad)
        self.assertEqual(r["status"], "spam")

    def test_duplicate_detection(self):
        cv2.create_claim_request(self.conn, dict(COMIC))
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        self.assertEqual(r["status"], "duplicate")

    def test_approve_transition(self):
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        self.assertTrue(cv2.mark_claim_status(self.conn, r["id"], "approved", reviewer="admin"))

    def test_reject_transition(self):
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        self.assertTrue(cv2.mark_claim_status(self.conn, r["id"], "rejected", reviewer="admin"))

    def test_terminal_cannot_transition(self):
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        cv2.mark_claim_status(self.conn, r["id"], "approved")
        with self.assertRaises(cv2.ClaimError):
            cv2.mark_claim_status(self.conn, r["id"], "rejected")

    def test_list_pending_only_reviewable(self):
        r1 = cv2.create_claim_request(self.conn, dict(COMIC))
        r2_data = dict(SHOW); r2_data["claimant_email"] = "b@x.test"
        r2 = cv2.create_claim_request(self.conn, r2_data)
        cv2.mark_claim_status(self.conn, r2["id"], "approved")
        pending = cv2.list_pending_claims(self.conn)
        ids = [p["id"] for p in pending]
        self.assertIn(r1["id"], ids)
        self.assertNotIn(r2["id"], ids)

    def test_claim_status_for_target_fail_closed(self):
        # No claim at all → none
        self.assertEqual(cv2.claim_status_for_target(self.conn, "comic", "unknown-slug")["status"], "none")
        # Pending claim → pending
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        self.assertEqual(cv2.claim_status_for_target(self.conn, "comic", "robert-hoehn")["status"], "pending")
        # Approved → verified
        cv2.mark_claim_status(self.conn, r["id"], "approved")
        self.assertEqual(cv2.claim_status_for_target(self.conn, "comic", "robert-hoehn")["status"], "verified")
        # Rejected only → none
        rejected_data = dict(COMIC); rejected_data["claimant_email"] = "rej@x.test"; rejected_data["target_slug"] = "other-slug"; rejected_data["target_id"] = "o-1"
        r2 = cv2.create_claim_request(self.conn, rejected_data)
        cv2.mark_claim_status(self.conn, r2["id"], "rejected")
        self.assertEqual(cv2.claim_status_for_target(self.conn, "comic", "other-slug")["status"], "none")

    def test_audit_events_recorded(self):
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        cv2.mark_claim_status(self.conn, r["id"], "approved", reviewer="admin")
        actions = [row[0] for row in self.conn.execute("SELECT action FROM audit_events_v2").fetchall()]
        self.assertIn("claims.create.needs_review", actions)
        self.assertIn("claims.transition.approved", actions)

    def test_no_public_ownership_changed(self):
        # Approving a claim does NOT modify any external table — only claims_v2 is touched.
        r = cv2.create_claim_request(self.conn, dict(COMIC))
        cv2.mark_claim_status(self.conn, r["id"], "approved")
        # Check no other table mutated (only audit_events_v2 + claims_v2 should be non-empty)
        for t in ("users_v2", "sessions_v2", "magic_links_v2"):
            self.assertEqual(self.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
