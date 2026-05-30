# BACKEND.PAYMENTS.2-ROUTER-DISABLED

**Status: IN_GIT_UNVERIFIED**
**Feature flags: PAYMENTS_ENABLED=false, PAYMENTS_PROVIDER=dryrun, PAYMENT_WEBHOOKS_ENABLED=false (all default)**
**Live checkout: NOT enabled**

## Overview

Payments V2 router wired to `main.py` in disabled mode, matching the pattern
used by Auth/Submissions/Claims V2 routers.

## Routes Wired

| Method | Path | Disabled response |
|---|---|---|
| GET | /api/payments_v2/status | always-on, reports enabled=false |
| GET | /api/payments_v2/products | always-on, returns catalog; checkout_live=false |
| POST | /api/payments_v2/checkout-session | 503 disabled |
| POST | /api/payments_v2/customer-portal | 503 disabled |
| GET | /api/payments_v2/subscriptions | 503 disabled |
| POST | /api/payments_v2/webhook | 503 (webhooks_disabled) |

## Product Catalog

`/api/payments_v2/products` is always available (does not require PAYMENTS_ENABLED).
Returns static catalog with `checkout_live: false`.
Products: `comic_plus`, `booker_plus`, `show_highlight`, `private_booking_lead`, `admin_manual_credit`

## Tests (17 total — test_payments_v2_router.py)

Disabled (7): status, products available, checkout/portal/subscriptions/webhook 503, no state on disabled checkout
Enabled (10): status, products, dry-run checkout creates session, invalid product 400, missing fields 400, webhook idempotency, subscription feature gate, cancellation, no external network call, pricing regression check

## Safety Rules

- PAYMENTS_ENABLED=false — unchanged
- PAYMENTS_PROVIDER=dryrun — no real provider
- PAYMENT_WEBHOOKS_ENABLED=false — webhooks blocked
- No Stripe/SumUp API key committed
- No live checkout link
- No paid feature activation
- pricing_copy_safety regression guard: PASS
