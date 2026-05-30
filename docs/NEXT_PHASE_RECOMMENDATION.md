# Next Phase Recommendation

**Date:** 2026-05-30  
**Following:** FINAL.SCAFFOLD-CLOSURE-MANIFEST.2

## Recommended: BACKEND.DB.2-PRODUCTION-MIGRATION-DRY-RUN

**Why this phase:**

- All scaffold/router/draft phases are closed (76 ChatGPT-verified phases)
- Email DNS requires Robert operator action (Postmark not set up) → blocked
- Payment provider requires Robert decision → blocked
- Migration dry-run is unblocked: it runs against a local copy of paris.db only
- Verifies 002–007 apply cleanly in sequence before any production run
- Pure validation: no flag changes, no production writes, no operator action needed

**What it involves:**

```bash
cp data/paris.db data/paris.db.backup-dryrun
sqlite3 data/paris.db < backend/migrations/002_auth_v2.sql
sqlite3 data/paris.db < backend/migrations/003_submissions_v2.sql
sqlite3 data/paris.db < backend/migrations/004_claims_v2.sql
sqlite3 data/paris.db < backend/migrations/005_payments_v2.sql
sqlite3 data/paris.db < backend/migrations/006_messaging_v2.sql
sqlite3 data/paris.db < backend/migrations/007_tickets_v2.sql
# verify tables exist
# run backend tests: 232/232 expected
# rollback: sqlite3 paris.db < 007_rollback.sql ... 002_rollback.sql
```

**Operator-blocked alternatives (cannot proceed without Robert):**

- BACKEND.EMAIL.5-DNS-LIVE-VERIFY — requires Robert to add Porkbun DNS records first
- BACKEND.AUTH.6-CUTOVER-PLAN-FINAL — safer after email is live
- Payments — requires Robert to choose provider and add API keys

## Current Phase Count

76 phases closed by ChatGPT. 22/22 regression guard checks pass.
Safe to enable production features: **NO**.
