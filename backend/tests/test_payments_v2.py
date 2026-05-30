"""Tests for backend/payments_v2.py — BACKEND.PAYMENTS.1-SCAFFOLD."""
from __future__ import annotations

import os, sqlite3, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PAYMENTS_ENABLED", "false")
os.environ.setdefault("PAYMENTS_PROVIDER", "dryrun")
os.environ.setdefault("PAYMENT_WEBHOOKS_ENABLED", "false")
import payments_v2 as pv2

PAY_MIG = (ROOT / "migrations" / "005_payments_v2.sql").read_text()
AUTH_MIG = (ROOT / "migrations" / "002_auth_v2.sql").read_text()


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(PAY_MIG)
    conn.executescript(AUTH_MIG)
    conn.commit()
    return conn


class TestPaymentsV2(unittest.TestCase):

    def setUp(self):
        self.conn = _fresh_db()
        pv2._CATALOG = None  # force reload from disk

    def tearDown(self):
        self.conn.close()

    def test_product_catalog_loads(self):
        prods = pv2.list_products()
        ids = {p["id"] for p in prods}
        self.assertIn("comic_plus", ids)
        self.assertIn("booker_plus", ids)
        self.assertIn("show_highlight", ids)

    def test_get_unknown_product_raises(self):
        with self.assertRaises(pv2.PaymentsError):
            pv2.get_product("nope")

    def test_checkout_dry_run_creates_session_only(self):
        r = pv2.create_checkout_session_dry_run(self.conn, user_id="u1", product_id="comic_plus")
        self.assertEqual(r["mode"], "dryrun")
        self.assertIn("dryrun", r["url"])
        # Row in payment_checkout_sessions_v2; nothing in subscriptions
        ck = self.conn.execute("SELECT COUNT(*) FROM payment_checkout_sessions_v2").fetchone()[0]
        sub = self.conn.execute("SELECT COUNT(*) FROM payment_subscriptions_v2").fetchone()[0]
        self.assertEqual(ck, 1)
        self.assertEqual(sub, 0)

    def test_checkout_unknown_product_rejected(self):
        with self.assertRaises(pv2.PaymentsError):
            pv2.create_checkout_session_dry_run(self.conn, user_id="u1", product_id="ghost")

    def test_no_provider_call_in_tests(self):
        # Just verify the status reports dryrun + disabled
        s = pv2.status()
        self.assertFalse(s["enabled"])
        self.assertEqual(s["provider"], "dryrun")

    def test_webhook_idempotency(self):
        r1 = pv2.record_webhook_event(self.conn, event_id="evt_1", event_type="subscription.created", payload='{"x":1}')
        r2 = pv2.record_webhook_event(self.conn, event_id="evt_1", event_type="subscription.created", payload='{"x":1}')
        self.assertTrue(r1["recorded"])
        self.assertFalse(r1["duplicate"])
        self.assertFalse(r2["recorded"])
        self.assertTrue(r2["duplicate"])

    def test_subscription_created_unlocks_feature(self):
        pv2.apply_subscription_created(self.conn, user_id="u1", product_id="comic_plus",
                                       provider_subscription_id="sub_1")
        self.assertTrue(pv2.is_feature_unlocked(self.conn, user_id="u1", feature="messaging"))
        self.assertTrue(pv2.is_feature_unlocked(self.conn, user_id="u1", feature="profile_highlight"))

    def test_subscription_cancelled_removes_unlock(self):
        pv2.apply_subscription_created(self.conn, user_id="u1", product_id="comic_plus",
                                       provider_subscription_id="sub_2")
        self.assertTrue(pv2.is_feature_unlocked(self.conn, user_id="u1", feature="messaging"))
        ok = pv2.apply_subscription_cancelled(self.conn, provider_subscription_id="sub_2")
        self.assertTrue(ok)
        self.assertFalse(pv2.is_feature_unlocked(self.conn, user_id="u1", feature="messaging"))

    def test_unpaid_user_has_no_unlocks(self):
        self.assertFalse(pv2.is_feature_unlocked(self.conn, user_id="ghost", feature="messaging"))

    def test_comic_plus_does_not_unlock_booker_feature(self):
        pv2.apply_subscription_created(self.conn, user_id="u1", product_id="comic_plus",
                                       provider_subscription_id="sub_3")
        self.assertFalse(pv2.is_feature_unlocked(self.conn, user_id="u1", feature="promoted_show_tools"))

    def test_booker_plus_does_not_unlock_comic_feature(self):
        pv2.apply_subscription_created(self.conn, user_id="u2", product_id="booker_plus",
                                       provider_subscription_id="sub_4")
        self.assertFalse(pv2.is_feature_unlocked(self.conn, user_id="u2", feature="profile_highlight"))

    def test_no_public_feature_gated_live(self):
        # is_feature_unlocked() never raises and always returns False when no subs
        for f in ("messaging", "profile_highlight", "promoted_show_tools", "anything"):
            self.assertFalse(pv2.is_feature_unlocked(self.conn, user_id="anon", feature=f))


if __name__ == "__main__":
    unittest.main()
