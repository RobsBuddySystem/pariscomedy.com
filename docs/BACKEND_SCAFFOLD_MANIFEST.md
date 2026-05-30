# BACKEND_SCAFFOLD_MANIFEST — system status as of 2026-05-30

All 7 backend marketplace systems have scaffolds. **Zero are live in production.**

## System status table

| System | Status | Feature flag | Tests | Routes live | Public UI | Auth dep | Payment dep | DB applied |
|---|---|---|---|---|---|---|---|---|
| auth_v2 | disabled_router | AUTH_V2_ENABLED=false | 27 | No | No | — | No | No |
| mailer | scaffold_only | EMAIL_SEND_REAL=false | 7 | No | No | No | No | No |
| submissions_v2 | scaffold_only | SUBMISSIONS_V2_ENABLED=false | 17 | No | No | Yes | No | No |
| claims_v2 | scaffold_only | CLAIMS_V2_ENABLED=false | 18 | No | No | Yes | No | No |
| payments_v2 | scaffold_only | PAYMENTS_ENABLED=false | 12 | No | No | Yes | — | No |
| messaging_v2 | scaffold_only | MESSAGING_V2_ENABLED=false | 15 | No | No | Yes | Yes | No |
| tickets_v2 | scaffold_only | TICKETS_ADAPTERS_ENABLED=false | 14 | No | No | Yes | No | No |

**Total: 115/115 tests PASS. 0 feature flags enabled. 0 production DB migrations applied.**

## Dependency matrix

```
auth_v2 ─────────────────────────> submissions, claims, messaging, tickets
mailer ──────────────────────────> auth (magic links), payments (receipts)
payments_v2 + legal/compliance ──> messaging (paid-gated), tickets (affiliate)
legal/compliance ────────────────> auth (GDPR), payments (VAT/checkout)
```

## Migration summary

| Migration | Applied | Rollback exists |
|---|---|---|
| 001_init.sql | Yes (production) | No |
| 002_auth_v2.sql | No | Yes |
| 003_submissions_v2.sql | No | Yes |
| 004_claims_v2.sql | No | Yes |
| 005_payments_v2.sql | No | Yes |
| 006_messaging_v2.sql | No | Yes |
| 007_tickets_v2.sql | No | Yes |

## Route summary

| Router | Wired in main.py | Returns 503 when disabled |
|---|---|---|
| auth_v2_router | Yes (try/except import) | Yes (AUTH_V2_ENABLED=false) |
| all others | No | N/A |

## Next recommended phase: BACKEND.AUTH.2-STAGING-ENABLE

Auth V2 has the most complete scaffold (27 tests, disabled router already wired in main.py).
It is the upstream dependency for submissions, claims, messaging, and tickets.

Recommended action: Apply 002_auth_v2.sql to **staging DB only**, enable AUTH_V2_ENABLED=true
in **staging environment only**, and run a live magic-link round-trip test.
Production remains disabled until staging test passes.

In parallel: select email provider + document DNS records (does not require any code change).

### Other options considered

| Option | Risk | Prerequisite |
|---|---|---|
| BACKEND.EMAIL.2-DNS-PROVIDER | Low — docs only | Provider selection |
| BACKEND.SUBMIT.2-ROUTER-DISABLED | Low — no new behavior | None |
| BACKEND.ADMIN.1-REVIEW-QUEUE-SCAFFOLD | Medium — new UI | Auth |
| FINAL.FRONTEND.COPY.GUARD.1 | Low — copy audit | None |

## Blockers before any production cutover

1. Email provider not selected (blocks auth magic links)
2. Email DNS SPF/DKIM not configured
3. VAT/payment compliance not reviewed
4. Legal GDPR consent flows not implemented (P1.COMPLIANCE.1 still DEFERRED)
5. No staging environment defined
