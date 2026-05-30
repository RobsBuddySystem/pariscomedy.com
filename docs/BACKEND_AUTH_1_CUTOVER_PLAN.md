# BACKEND_AUTH_1_CUTOVER_PLAN — wire v2 endpoints behind disabled flag

**Phase:** BACKEND.AUTH.1-CUTOVER-PLAN
**Authorized:** ChatGPT 2026-05-30
**Status:** wiring + disabled-mode + enabled-mode tests done. Router file is NOT yet imported into `backend/main.py` (per ChatGPT spec — "wire endpoints behind the flag" but "no production enablement").

## Files

- `backend/auth_v2_router.py` — FastAPI APIRouter at `/api/auth_v2/*`. When `AUTH_V2_ENABLED=false` (default) every endpoint returns **503 `{error: {code: "auth/disabled"}}`** and creates no DB state. When enabled (test env only) endpoints delegate to `auth_v2.py`.
- `backend/tests/test_auth_v2_router.py` — 12 router tests (5 disabled-mode + 7 enabled-mode round-trip).

## Endpoints registered

| Method | Path | Behavior when disabled | Behavior when enabled |
|---|---|---|---|
| GET | `/api/auth_v2/status` | 200 `{enabled:false,…}` | 200 `{enabled:true,…}` |
| POST | `/api/auth_v2/magic-link/request` | 503 | 204 + DB row in `magic_links_v2` |
| GET | `/api/auth_v2/magic-link/consume?token=…` | 503 | 200 + Set-Cookie `pc_session_v2` (HttpOnly+Secure+SameSite=Lax) + `pc_csrf_v2` |
| POST | `/api/auth_v2/logout` | 503 | 204 + clear cookies + DB row revoked |
| GET | `/api/auth_v2/me` | 503 | 200 `{user_id,email,role,expires_at}` or 401 |
| GET | `/api/auth_v2/session/expiry` | 503 | 200 `{expires_at}` or 401 |

## Cookie design

- `pc_session_v2`: HttpOnly + Secure + SameSite=Lax, max-age 14 days. Carries the session id (also the DB primary key). Server-side only.
- `pc_csrf_v2`: NOT HttpOnly (readable by frontend JS). Same Secure/SameSite. Frontend echoes value as `X-CSRF-Token` header on all non-GET writes. Server compares header to cookie; mismatch = reject. (CSRF enforcement is handled at the router edge in the cutover phase, not in this PR.)

## Frontend cutover plan (NOT THIS PHASE)

1. `/login.html` continues to use legacy `/api/booker/auth` for now.
2. When `AUTH_V2_ENABLED=true` lands in production AND BACKEND.EMAIL.1 ships real mailer, frontend gets a feature-flag switch (`window.PC_AUTH_V2`) to use the new endpoints.
3. Old `/api/booker/auth` retired after a 30-day deprecation window.

## Email cutover dependency

This phase keeps `AUTH_V2_DRY_RUN_MAILER=true` so any real wiring of `request_magic_link` writes the token to stderr only. Production cutover requires BACKEND.EMAIL.1 first (Postmark setup + SPF/DKIM/DMARC).

## Migration apply instructions (NOT auto-applied)

```sh
# DEV / staging:
sqlite3 data/paris.db < backend/migrations/002_auth_v2.sql

# Rollback:
sqlite3 data/paris.db < backend/migrations/002_auth_v2.rollback.sql
```

Production apply is gated behind explicit operator authorization + backup.

## Tests

`cd backend && python3 -m unittest tests.test_auth_v2 tests.test_auth_v2_router -v`
→ 27/27 OK (15 service-module tests + 12 router tests).

Disabled-mode coverage:
- /status reports enabled=false
- request/consume/logout/me/session-expiry each return 503 with `auth/disabled` error code
- No DB state created when endpoints are hit while disabled

Enabled-mode coverage (test-only):
- /status reports enabled=true
- request returns 204 + DB row appears
- Full round-trip: request → consume → /me → logout → /me-after-logout 401
- Reused token rejected with 401 on second consume
- /me without session returns 401

## Wiring into main.py (deferred)

Single line added in the cutover phase: `app.include_router(auth_v2_router.router)`. Until then, the router is importable and tested but unreachable in production.

## Rollback

`git revert <commit-sha>` removes the router file + tests + this doc. No DB or main.py change to undo.

## Related

- [[PHASE_LEDGER]]
- [[BACKEND_AUTH_1_SCAFFOLD]]
- [[BACKEND_PLAN_1]]
- [[API_CONTRACT_DRAFT]]
- [[BACKEND_RISK_REGISTER]] — R-01 (enumeration), R-02 (replay), R-18 (CSRF) addressed by this design
