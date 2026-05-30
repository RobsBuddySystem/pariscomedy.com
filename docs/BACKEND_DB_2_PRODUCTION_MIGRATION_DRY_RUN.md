# BACKEND.DB.2-PRODUCTION-MIGRATION-DRY-RUN

**Status: IN_GIT_UNVERIFIED**
**Scope: Dry-run against a local copy only. Production DB not touched.**

## What This Phase Delivers

Verified that migrations 002–007 apply cleanly to a copied DB, create all
expected V2 tables, preserve existing data, are idempotent, and roll back cleanly.

## Dry-Run Setup

- **Source DB**: fresh DB created from `001_init.sql` (production `paris.db` is
  not committed to the repo — live production DB is on the server)
- **Dry-run copy**: `/tmp/paris_dryrun_20260530T103937Z.db`
- **Rollback copy**: `/tmp/paris_dryrun_rollback_20260530T104115Z.db`
- **Production DB touched**: NO

## Pre-Migration Baseline

Tables: `booker_lineup`, `booker_shows`, `booker_sessions`, `messages_review_queue`  
Pre-migration checksum: `38ba1415e93448f7a6a2bd878fbe7af6`

## Apply Result

| Migration | Result |
|---|---|
| 002_auth_v2.sql | OK |
| 003_submissions_v2.sql | OK |
| 004_claims_v2.sql | OK |
| 005_payments_v2.sql | OK |
| 006_messaging_v2.sql | OK |
| 007_tickets_v2.sql | OK |

## Expected Tables Verified (17/17)

`users_v2`, `sessions_v2`, `magic_links_v2`, `audit_events_v2`, `rate_limits_v2`,
`show_submissions_v2`, `claims_v2`, `payment_customers_v2`, `payment_subscriptions_v2`,
`payment_invoices_v2`, `payment_checkout_sessions_v2`, `payment_webhook_idempotency_v2`,
`message_threads_v2`, `messages_v2`, `message_blocks_v2`, `message_reports_v2`,
`adapter_discoveries_v2`

Total tables after migration: **22** (4 existing + 17 V2 + 1 original = 22)

## Existing Data Preserved

All 4 baseline tables present with row counts unchanged.

## Idempotency

Re-running all 6 migrations: all OK, no duplicate tables, no failures.

## Rollback

Rollback scripts in reverse (007→002): all OK.  
Post-rollback V2 tables remaining: **0**  
Original baseline tables preserved: **YES**

## Backend Tests

232/232 PASS (no backend behavior changed — dry-run is docs/data only)

## Regression Guard

22/22 PASS

## Production DB Migration Status

**NOT APPLIED.** Applying to production requires:
1. Robert's explicit approval
2. Production DB backup
3. Applying during maintenance window
4. Smoke test after each migration

## Rollback Command (production, if ever applied)

```bash
sqlite3 "${DB_PATH:-data/paris.db}" < backend/migrations/007_tickets_v2.rollback.sql
sqlite3 "${DB_PATH:-data/paris.db}" < backend/migrations/006_messaging_v2.rollback.sql
sqlite3 "${DB_PATH:-data/paris.db}" < backend/migrations/005_payments_v2.rollback.sql
sqlite3 "${DB_PATH:-data/paris.db}" < backend/migrations/004_claims_v2.rollback.sql
sqlite3 "${DB_PATH:-data/paris.db}" < backend/migrations/003_submissions_v2.rollback.sql
sqlite3 "${DB_PATH:-data/paris.db}" < backend/migrations/002_auth_v2.rollback.sql
```
