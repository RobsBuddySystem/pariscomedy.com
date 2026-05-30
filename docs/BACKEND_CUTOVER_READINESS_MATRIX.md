# BACKEND_CUTOVER_READINESS_MATRIX — 2026-05-30

What must be true before each system can go live.

| System | DB migration | Email/DNS | Legal/GDPR | Auth live | Staging test | Payment provider | Status |
|---|---|---|---|---|---|---|---|
| auth_v2 | Apply 002 to staging | SPF/DKIM records set | GDPR consent UI | — | Magic-link round-trip | No | NOT READY |
| mailer | None | Provider selected + DNS | No | No | Dry-run verified | No | NOT READY |
| submissions_v2 | Apply 003 | No | No | Yes | Submission flow | No | NOT READY |
| claims_v2 | Apply 004 | No | No | Yes | Claim flow | No | NOT READY |
| payments_v2 | Apply 005 | Receipts | VAT/Stripe Tax | Yes | Checkout test | Yes | NOT READY |
| messaging_v2 | Apply 006 | Notifications (future) | No | Yes | Message round-trip | Paid gate | NOT READY |
| tickets_v2 | Apply 007 | No | Per-platform ToS | Yes | Admin import test | Affiliate gate | NOT READY |
