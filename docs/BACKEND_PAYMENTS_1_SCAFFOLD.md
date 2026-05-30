# BACKEND_PAYMENTS_1_SCAFFOLD

**Phase:** BACKEND.PAYMENTS.1-SCAFFOLD
**Authorized:** ChatGPT 2026-05-30
**Status:** scaffold + dry-run checkout + idempotent webhook recording + feature-unlock gate. No real provider call. No live checkout.

## Files

- `data/payment-products.json` — product catalog (5 SKUs)
- `backend/migrations/005_payments_v2.sql` (+ rollback) — 5 tables
- `backend/payments_v2.py` — service module
- `backend/tests/test_payments_v2.py` — 12 unit tests

## Product catalog

| id | kind | price | unlocks |
|---|---|---|---|
| `comic_plus`           | subscription €1/mo | messaging + profile_highlight |
| `booker_plus`          | subscription €1/mo | messaging + promoted_show_tools |
| `show_highlight`       | one-off €10       | highlight_show |
| `private_booking_lead` | one-off €25       | private_booking_lead |
| `admin_manual_credit`  | manual comp €0    | (none) |

## Service API

- `list_products()` / `get_product(id)`
- `create_checkout_session_dry_run(conn, user_id, product_id)` → `{id, mode:"dryrun", url}` (no provider call)
- `record_webhook_event(conn, event_id, event_type, payload, provider)` → `{recorded, duplicate}` (DB-level idempotency via UNIQUE on event_id)
- `apply_subscription_created(conn, ...)` → activates subscription row
- `apply_subscription_cancelled(conn, provider_subscription_id)` → returns bool
- `subscription_status_for_user(conn, user_id)` → list[dict]
- `is_feature_unlocked(conn, user_id, feature)` → bool. Only `status='active'` subs whose product `unlocks` contains the feature → True.
- `status()` → `{enabled, provider, webhooks_enabled, product_count}`

## Feature flags

| Var | Default |
|---|---|
| `PAYMENTS_ENABLED` | `false` |
| `PAYMENTS_PROVIDER` | `dryrun` |
| `PAYMENT_WEBHOOKS_ENABLED` | `false` |

## Tests (12/12 PASS)

- product catalog loads with all 5 SKUs
- unknown product rejected
- checkout dry-run creates session row only (no subscription)
- checkout unknown product rejected
- status() reports dryrun + disabled
- webhook idempotency: duplicate event_id rejected silently
- subscription created unlocks correct feature
- subscription cancelled removes unlock
- unpaid user has no unlocks
- comic_plus does NOT unlock booker-only feature
- booker_plus does NOT unlock comic-only feature
- no public feature gated live (always False for non-subscribers)

## What is still NOT live

- No Stripe/SumUp/Resend integration
- No `/billing/checkout-session` route
- No live webhook endpoint
- Production DB migration NOT auto-applied
- pricing.html unchanged
- No paid feature is publicly gated yet
- VAT/Stripe Tax not configured

## Rollback

`git revert <commit-sha>` + optional `sqlite3 data/paris.db < backend/migrations/005_payments_v2.rollback.sql`.

## Related

- [[PHASE_LEDGER]]
- [[BACKEND_PLAN_1]]
- [[BACKEND_RISK_REGISTER]] — R-08 webhook replay, R-09 VAT, R-20 chargebacks
