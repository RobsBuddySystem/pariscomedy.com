# BACKEND.AUTH.2-STAGING-ENABLE

**Status:** IN_GIT_UNVERIFIED — pending ChatGPT closure  
**Authorized by:** ChatGPT 2026-05-30 (after BACKEND.SCAFFOLD.MANIFEST.1 closed)

## What this phase delivers

Auth V2 staging round-trip proof. 18 scenarios pass. Production remains AUTH_V2_ENABLED=false.

## Staging environment

- In-memory SQLite DB (002_auth_v2.sql applied to `:memory:`, not `data/paris.db`)
- AUTH_V2_ENABLED=true (staging env only — reset to false for production proof)
- AUTH_V2_DRY_RUN_MAILER=true (tokens written to stderr, not emailed)

## Staging round-trip results: 18/18 PASS

| # | Test | Result |
|---|---|---|
| 1 | request_magic_link returns token | PASS |
| 2 | consume_magic_link succeeds | PASS |
| 3 | session_id returned | PASS |
| 4 | role=comic returned | PASS |
| 5 | reused token rejected (ConsumedTokenError) | PASS |
| 6 | get_current_user returns user | PASS |
| 7 | email matches | PASS |
| 8 | role=comic on user | PASS |
| 9 | booker role created and returned | PASS |
| 10 | invalid role rejected | PASS |
| 11 | logout succeeds | PASS |
| 12 | get_current_user after logout returns None | PASS |
| 13 | expired token rejected (ExpiredTokenError) | PASS |
| 14 | old token rejected after invalidation | PASS |
| 15 | rate limit blocks excessive requests | PASS |
| 16 | audit events recorded | PASS |
| 17 | auth.magic_link.request audit present | PASS |
| 18 | production AUTH_V2_ENABLED=false confirmed | PASS |

## Token safety

- Single-use: ConsumedTokenError on reuse ✓
- TTL: ExpiredTokenError on expired token ✓
- Invalidation: old token rejected after `invalidate_old_tokens_for_email` ✓

## Production safety

- AUTH_V2_ENABLED=false in production (not changed by this phase)
- Production DB (data/paris.db) NOT touched
- login.html NOT changed
- Legacy auth NOT modified
- No real email sent

## Runbook (staging → production transition, future phase)

1. Provision real staging DB (separate SQLite file or Postgres)
2. Run: `sqlite3 staging.db < backend/migrations/002_auth_v2.sql`
3. Set AUTH_V2_ENABLED=true in staging env only
4. Smoke test magic-link round-trip with real email
5. After passing: apply 002_auth_v2.sql to production DB
6. Set AUTH_V2_ENABLED=true in production

## Rollback

Auth V2 router already returns 503 when AUTH_V2_ENABLED=false — no state to revert.
