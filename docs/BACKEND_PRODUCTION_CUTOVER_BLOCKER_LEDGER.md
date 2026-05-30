# BACKEND.PRODUCTION-CUTOVER.BLOCKER-LEDGER

**Status: IN_GIT_UNVERIFIED**
**Scope: Audit/planning only. No flags enabled. No migration applied. No backend behavior changed.**

## System Status Table

| System | Phase | Flag (default) | Tests | DB Migration | Safe to enable? |
|---|---|---|---|---|---|
| Auth V2 | BACKEND.AUTH.4 | AUTH_V2_ENABLED=false | 122/122 | 002 — NOT applied | NO |
| Email/Postmark | BACKEND.EMAIL.3 | EMAIL_SEND_REAL=false | 8/8 | N/A | NO |
| Submissions V2 | BACKEND.SUBMIT.2 | SUBMISSIONS_V2_ENABLED=false | 19/19 | 004 — NOT applied | NO |
| Claims V2 | BACKEND.CLAIM.2 | CLAIMS_V2_ENABLED=false | 25/25 | 003 — NOT applied | NO |
| Payments V2 | BACKEND.PAYMENTS.2 | PAYMENTS_ENABLED=false | 17/17 | 005 — NOT applied | NO |
| Messaging V2 | BACKEND.MESSAGING.2 | MESSAGING_V2_ENABLED=false | 23/23 | 006 — NOT applied | NO |
| Tickets V2 | BACKEND.TICKETS.2 | TICKETS_ADAPTERS_ENABLED=false | 26/26 | 007 — NOT applied | NO |

**Total: 7 systems scaffolded, 0 production-live, 232/232 backend tests pass**

## Blockers by System

### Auth V2
- production DB migration 002 not applied
- login.html not switched to Auth V2 endpoints
- no production smoke test (magic link → real email → token consume)

### Email / Postmark (external operator blockers)
- Postmark account not created by Robert
- SPF missing: needs `include:spf.protection.postmark.com` at Porkbun
- DKIM missing: `pm._domainkey.pariscomedy.com` TXT record
- DMARC missing: `_dmarc.pariscomedy.com` TXT record
- return-path CNAME missing: `pm-bounces.pariscomedy.com → pm.mtasv.net`

### Submissions V2
- production DB migration 004 not applied
- public submission form not cut over to V2 endpoints
- admin review UI not live

### Claims V2
- production DB migration 003 not applied
- admin claim review UI not live

### Payments V2
- production DB migration 005 not applied
- no payment provider configured (no Stripe/SumUp key)
- no VAT/payment compliance review done
- Robert must choose provider + add API keys as env vars

### Messaging V2
- production DB migration 006 not applied
- no paid messaging gate (requires Payments V2 live first)

### Tickets / Adapters V2
- production DB migration 007 not applied
- no admin review UI
- no robots.txt/ToS compliance review per platform
- no affiliate network approval

## Recommended Next Phase

**BACKEND.EMAIL.4-OPERATOR-DNS-RUNBOOK**

Email/DNS is a pure operator-action dependency with zero code risk. A clear runbook
gives Robert the exact steps to configure Postmark and DNS at Porkbun. This unblocks
Auth V2 (which requires real magic link emails), which is the foundation for all
paid feature gates. DB migration runbook and admin review UI can follow in parallel.

## Machine-readable ledger

`data/backend-cutover-blocker-ledger.json`
