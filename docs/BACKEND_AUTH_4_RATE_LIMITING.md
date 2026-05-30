# BACKEND.AUTH.4-RATE-LIMITING

**Status: CLOSED_BY_CHATGPT (pending)**
**Auth V2 status: NOT production-enabled (AUTH_V2_ENABLED=false)**

## Overview

HTTP-level rate limiting for Auth V2 endpoints. Implemented as an independent
"belt" check in `auth_v2_router.py` (separate from the service-layer "suspenders"
check already in `auth_v2.py`). Uses separate DB buckets to avoid double-counting.

## Endpoints and Limits

| Endpoint | Limit | Bucket |
|---|---|---|
| POST /api/auth_v2/magic-link/request | 10 req / email / hour | `http.magic_link.email` |
| POST /api/auth_v2/magic-link/request | 30 req / IP / hour | `http.magic_link.ip` |
| GET /api/auth_v2/magic-link/consume (invalid token) | 20 failures / IP / hour | `http.consume.ip` |
| POST /api/auth_v2/logout | Not rate-limited (abuse surface negligible) | — |
| GET /api/auth_v2/me | Not rate-limited | — |
| GET /api/auth_v2/status, /session/expiry | Not rate-limited | — |

## Fail-Closed Behavior

If rate-limit storage (SQLite `rate_limits_v2` table) is unavailable due to
disk I/O error or any other DB exception, the endpoint returns **429** rather
than allowing the request through. Error code: `auth/rate_limit_unavailable`.

## Disabled Mode

When `AUTH_V2_ENABLED=false` (default), endpoints return 503 immediately before
any rate-limit check or DB write. No `rate_limits_v2` rows are created.

## Service Layer vs HTTP Layer

`auth_v2.py::_check_rate` — service-layer check, uses `auth.magic_link.email`
and `auth.magic_link.ip` buckets.

`auth_v2_router.py::_http_rate_check` — HTTP-layer check, uses
`http.magic_link.email` and `http.magic_link.ip` buckets (separate, no
double-counting). Wraps `_check_rate` with fail-closed error handling.

## Tests (18 total in test_auth_v2_router.py)

New BACKEND.AUTH.4 tests:
- `test_per_email_limit_blocks_11th_request` — email-level limit enforced
- `test_per_ip_limit_blocks_excess` — IP-level limit enforced
- `test_different_email_not_blocked_by_per_email_limit` — limits are per-key
- `test_consume_invalid_token_rate_limited_per_ip` — consume attempt limiting
- `test_disabled_mode_creates_no_rate_limit_rows` — disabled mode safety
- `test_fail_closed_when_storage_unavailable` — storage failure → 429

## Blockers Remaining Before Production Auth V2

This phase does NOT unblock production enablement. Remaining blockers:

1. DNS/SPF/DKIM/DMARC not verified live
2. Postmark not connected/live
3. Production DB migration not applied (`migrations/002_auth_v2.sql`)
4. `login.html` not switched to Auth V2
5. `AUTH_V2_ENABLED=true` not set in production

## Safety Rules

- `AUTH_V2_ENABLED=false` in production — unchanged
- No real email sending — `AUTH_V2_DRY_RUN_MAILER=true`
- No Postmark key committed
- No production DB migration applied
- No login.html switch
- No payment/messaging/submission/claim/ticket changes

## Rollback

`git revert <commit-sha>` — removes router rate-limit logic and tests.
The `rate_limits_v2` table schema is unchanged (already in `002_auth_v2.sql`).
