# BACKEND.DB.2B-PRODUCTION-COPY-DRY-RUN

**Status: IN_GIT_UNVERIFIED**
**Scope: Dry-run against a copied production DB. Production DB not touched.**

## What This Phase Delivers

Verified that migrations 002–007 apply cleanly to a **copy of the actual production
DB** (`/Users/chuck/.openclaw/workspace/apps/paris-comedy/data/paris.db`), preserve
all existing data, are idempotent, and roll back cleanly.

## Source DB

| Property | Value |
|---|---|
| Path | `/Users/chuck/.openclaw/workspace/apps/paris-comedy/data/paris.db` |
| Size | 1,011,712 bytes |
| MD5 checksum | `8ffcfe02d9ed073f2b181cc55a010658` |
| Original modified | **NO** — copy only |

## Pre-Migration Baseline (real production data)

| Table | Row count |
|---|---|
| shows | 119 |
| venues | 45 |
| comics | 275 |
| show_listings | 179 |
| booker_shows | 11 |
| booker_lineup | 8 |
| booker_sessions | 21 |
| messages_review_queue | 10 |

## Apply Result

All 6 migrations: **OK**

## V2 Tables Verified (17/17)

`users_v2`, `sessions_v2`, `magic_links_v2`, `audit_events_v2`, `rate_limits_v2`,
`show_submissions_v2`, `claims_v2`, `payment_customers_v2`, `payment_subscriptions_v2`,
`payment_invoices_v2`, `payment_checkout_sessions_v2`, `payment_webhook_idempotency_v2`,
`message_threads_v2`, `messages_v2`, `message_blocks_v2`, `message_reports_v2`,
`adapter_discoveries_v2`

## Existing Data Preserved

After apply: shows=119, venues=45, comics=275, show_listings=179 (unchanged).
All booker/session/messages tables unchanged.

## Idempotency

Re-run 002–007 on same copy: all **OK**, data unchanged.

## Rollback

Rollback scripts 007→002 on second copy: all **OK**.  
Post-rollback V2 tables: **0**. Original data: fully preserved.

## Backend Tests

232/232 PASS

## Regression Guard

22/22 PASS

## Production DB Migration Status

**NOT APPLIED.** Production migration still requires explicit operator approval.
