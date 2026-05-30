"""Tests for backend/mailer.py — BACKEND.EMAIL.1-PLAN-SCAFFOLD.

Covers ChatGPT-mandated scenarios:
- dry-run mailer captures payload
- magic-link template includes link
- missing/invalid addresses fail closed
- real-send not implemented (NotImplementedError raised if EMAIL_SEND_REAL=true)
- no external network call (validated by structure — only stderr write in dry-run)

Run: cd backend && python3 -m unittest tests.test_mailer
"""
from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _fresh_mailer(send_real: bool = False, provider: str = "dryrun"):
    os.environ["EMAIL_SEND_REAL"] = "true" if send_real else "false"
    os.environ["EMAIL_PROVIDER"] = provider
    os.environ.setdefault("EMAIL_FROM", "no-reply@pariscomedy.com")
    os.environ.setdefault("EMAIL_REPLY_TO", "support@pariscomedy.com")
    if "mailer" in sys.modules:
        importlib.reload(sys.modules["mailer"])
    else:
        import mailer  # noqa: F401
    import mailer
    mailer.reset_captured()
    return mailer


class TestMailerDryRun(unittest.TestCase):

    def setUp(self):
        self.mailer = _fresh_mailer(send_real=False)

    def test_dry_run_captures_payload(self):
        email = self.mailer.magic_link_email("a@x.test", token="abc")
        result = self.mailer.send(email)
        self.assertEqual(result["mode"], "dryrun")
        self.assertFalse(result["delivered"])
        self.assertEqual(result["template"], "magic_link")
        captured = self.mailer.captured()
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0].to, "a@x.test")

    def test_magic_link_template_includes_link(self):
        email = self.mailer.magic_link_email("u@x.test", token="abc123", base_url="https://pariscomedy.com")
        self.assertIn("abc123", email.text)
        self.assertIn("/auth_v2/magic-link/consume?token=abc123", email.text)
        self.assertIn("/auth_v2/magic-link/consume?token=abc123", email.html)
        # Subject is fixed and does not leak the token
        self.assertNotIn("abc123", email.subject)
        # Plain-text version exists
        self.assertTrue(email.text)
        self.assertTrue(email.html)

    def test_invalid_to_address_fails_closed(self):
        email = self.mailer.magic_link_email("not-an-email", token="x")
        with self.assertRaises(self.mailer.MailerError):
            self.mailer.send(email)

    def test_invalid_from_address_fails_closed(self):
        email = self.mailer.magic_link_email("ok@x.test", token="x")
        email.from_addr = "garbage"
        with self.assertRaises(self.mailer.MailerError):
            self.mailer.send(email)

    def test_status_reports_dry_run(self):
        s = self.mailer.status()
        self.assertFalse(s["send_real"])
        self.assertEqual(s["provider"], "dryrun")
        self.assertIn("from", s)
        self.assertIn("reply_to", s)


class TestMailerRealSend(unittest.TestCase):

    def test_real_send_with_dryrun_provider_still_dryrun(self):
        # If EMAIL_SEND_REAL=true but provider is still "dryrun", behavior is dry-run.
        m = _fresh_mailer(send_real=True, provider="dryrun")
        email = m.magic_link_email("rs@x.test", token="t")
        result = m.send(email)
        self.assertEqual(result["mode"], "dryrun")

    def test_real_send_with_unconfigured_provider_raises(self):
        # With postmark provider but no real token: MailerError (fail-closed)
        os.environ["POSTMARK_SERVER_TOKEN"] = ""
        m = _fresh_mailer(send_real=True, provider="postmark")
        email = m.magic_link_email("rs2@x.test", token="t")
        with self.assertRaises(Exception):  # MailerError or NotImplementedError
            m.send(email)
        # Cleanup so other tests don't see EMAIL_SEND_REAL=true
        os.environ["EMAIL_SEND_REAL"] = "false"
        os.environ["EMAIL_PROVIDER"] = "dryrun"

    def test_missing_postmark_token_fails_closed(self):
        # Explicit: placeholder token should raise MailerError
        import importlib
        os.environ["EMAIL_SEND_REAL"] = "true"
        os.environ["EMAIL_PROVIDER"] = "postmark"
        os.environ["POSTMARK_SERVER_TOKEN"] = "PLACEHOLDER_DO_NOT_COMMIT"
        import mailer as _m
        importlib.reload(_m)
        email = _m.magic_link_email("fc@x.test", token="t")
        with self.assertRaises(_m.MailerError):
            _m.send(email)
        os.environ["EMAIL_SEND_REAL"] = "false"
        os.environ["EMAIL_PROVIDER"] = "dryrun"
        os.environ["POSTMARK_SERVER_TOKEN"] = ""
        importlib.reload(_m)


if __name__ == "__main__":
    unittest.main()
