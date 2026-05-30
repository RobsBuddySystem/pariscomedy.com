# BACKEND_AUTH_1_SCAFFOLD — v2 auth scaffold (INERT)

**Phase:** BACKEND.AUTH.1-SCAFFOLD
**Authorized:** ChatGPT 2026-05-30
**Status:** INERT BY DEFAULT — `AUTH_V2_ENABLED=false` and no main.py wiring. The current live login/booker auth is unchanged.

## What this ships

- `backend/migrations/002_auth_v2.sql` — five new tables: `users_v2`, `sessions_v2`, `magic_links_v2`, `audit_events_v2`, `rate_limits_v2`. Coexists with existing `booker_sessions`.
- `backend/migrations/002_auth_v2.rollback.sql` — drops the five v2 tables.
- `backend/auth_v2.py` — service module (request/consume magic link, invalidate old tokens, create/get/logout session, audit). Honors `AUTH_V2_ENABLED` + `AUTH_V2_DRY_RUN_MAILER` env vars (default false / true).
- `backend/tests/test_auth_v2.py` — 15 unit tests covering ChatGPT-mandated scenarios.

## What this does NOT do

- Does NOT wire any endpoint in `backend/main.py`.
- Does NOT auto-apply the migration (run manually: `sqlite3 data/paris.db < backend/migrations/002_auth_v2.sql`).
- Does NOT send real emails — `DRY_RUN_MAILER=true` default writes tokens to stderr.
- Does NOT touch any v1 table (`users`, `booker_sessions`, etc.).
- Does NOT change the current login.html or booker-portal flow.

## Safety boundary

1. `AUTH_V2_ENABLED` defaults to `false`. Any future main.py wiring must check this flag before exposing v2 endpoints.
2. Migration file is a separate `.sql` — must be applied deliberately.
3. Single-use magic-link enforcement: token consumed even if downstream session creation fails (DB transaction).
4. Token TTL ≤ 15 min, session TTL 14 days, rate limit 10/email/hour.
5. Role check: only `user`/`comic`/`booker`/`admin` accepted; other roles raise `InvalidRoleError`.

## Test coverage (15 tests, all pass)

- magic-link round-trip
- consumed token rejected on re-use
- invalidated token (via `invalidate_old_tokens_for_email`) rejected
- expired token rejected
- unknown token rejected
- rate limit blocks after 10 same-email requests in 1h
- rate limit isolated per email
- get_current_user returns role/email for valid session
- logout invalidates session (idempotent)
- empty / unknown session returns None
- expired session returns None
- role separation: comic/booker get distinct user_ids + sessions
- invalid role rejected
- audit events recorded on request + consume
- status() reports `enabled: false` by default

Run: `cd backend && python3 -m unittest tests.test_auth_v2 -v` → 15/15 OK.

## Cutover plan (NOT THIS PHASE — future BACKEND.AUTH.1-CUTOVER)

1. Wire `/api/auth_v2/magic-link/{request,consume}`, `/auth_v2/logout`, `/auth_v2/me`, `/auth_v2/session/expiry` in `main.py`, ALL gated by `AUTH_V2_ENABLED`.
2. Wire HttpOnly cookie issuance + CSRF cookie pair.
3. Real mailer via Postmark when BACKEND.EMAIL.1 lands.
4. Frontend swap of `/login.html` to v2 endpoints.
5. Migration applied to production DB.
6. Old `/api/booker/auth` retired after a deprecation window.

## Rollback

```sh
# delete files (working-tree only — does not touch DB)
git revert <this-commit-sha>

# optional: drop the v2 tables from DB
sqlite3 data/paris.db < backend/migrations/002_auth_v2.rollback.sql
```

## Related

- [[PHASE_LEDGER]] — BACKEND.AUTH.1-SCAFFOLD row IN_GIT_UNVERIFIED
- [[BACKEND_PLAN_1]] — parent plan
- [[API_CONTRACT_DRAFT]] — endpoints to wire in the future cutover phase
- [[DB_SCHEMA_DRAFT]] — schema source-of-truth
- [[BACKEND_RISK_REGISTER]] — risks R-01 to R-03, R-15 to R-18 owned by this phase
