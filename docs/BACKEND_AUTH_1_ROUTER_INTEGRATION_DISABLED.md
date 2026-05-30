# BACKEND_AUTH_1_ROUTER_INTEGRATION_DISABLED

**Phase:** BACKEND.AUTH.1-ROUTER-INTEGRATION-DISABLED
**Authorized:** ChatGPT 2026-05-30
**Status:** router mounted in `backend/main.py`; `AUTH_V2_ENABLED=false` default → action endpoints reachable but 503.

## What this ships

- `backend/main.py` — added `app.include_router(auth_v2_router.router)` inside a try/except guard. If the import ever fails, main.py logs and continues — never crashes.
- `backend/tests/test_main_integration.py` — 5 integration tests proving the router is mounted, status reports disabled, every action endpoint returns 503 with `auth/disabled`, no DB rows created when disabled endpoints are hit, and the legacy `/api/health` still responds.

## Test coverage (32/32 across the suite)

- `tests.test_auth_v2` — 15 service-module tests (from scaffold)
- `tests.test_auth_v2_router` — 12 router tests (from cutover plan)
- `tests.test_main_integration` — 5 NEW integration tests this phase

Run: `cd backend && python3 -m unittest tests.test_main_integration tests.test_auth_v2_router tests.test_auth_v2`

## Production-mode behavior (AUTH_V2_ENABLED unset → false)

| Endpoint | Status | Body |
|---|---|---|
| `GET /api/auth_v2/status` | 200 | `{enabled:false, dry_run_mailer:true, ...}` |
| `POST /api/auth_v2/magic-link/request` | 503 | `{error:{code:"auth/disabled", message:"..."}}` |
| `GET /api/auth_v2/magic-link/consume` | 503 | same |
| `POST /api/auth_v2/logout` | 503 | same |
| `GET /api/auth_v2/me` | 503 | same |
| `GET /api/auth_v2/session/expiry` | 503 | same |
| Legacy `/api/health`, `/api/booker/*`, `/api/admin/*` | unchanged | unchanged |

## What is still NOT live

- `AUTH_V2_ENABLED` is still false in production
- No real email (DRY_RUN_MAILER=true)
- Production DB migration NOT auto-applied
- `login.html` UNCHANGED
- Legacy `/api/booker/auth` is the active auth path

## Rollback

`git revert <commit-sha>` removes the import block + the integration test. No DB or frontend change to undo.

## Related

- [[BACKEND_AUTH_1_CUTOVER_PLAN]]
- [[BACKEND_AUTH_1_SCAFFOLD]]
- [[PHASE_LEDGER]]
