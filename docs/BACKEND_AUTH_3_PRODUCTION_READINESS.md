# BACKEND.AUTH.3-PRODUCTION-READINESS

**Status:** IN_GIT_UNVERIFIED — pending ChatGPT closure  
**Authorized by:** ChatGPT 2026-05-30 (after FINAL.FRONTEND.COPY.GUARD.1 closed)

## Scope

Readiness checklist only. No production enablement, no migration, no login.html switch, no real email.

## Production Backend Status

- API base URL: `https://api.pariscomedy.com`
- `/api/health`: `{"ok": true, "version": "0.1.0"}` ✓
- `/api/auth_v2/status`: `{"detail": "Not Found"}` → router not mounted (expected, AUTH_V2_ENABLED=false)
- `AUTH_V2_ENABLED`: `false` (in env.example and production env)

## DB Migration Readiness

**Migration file:** `backend/migrations/002_auth_v2.sql`  
**Rollback file:** `backend/migrations/002_auth_v2.rollback.sql`

**Before running in production:**
```bash
# 1. Backup production DB
cp /path/to/production/paris.db /path/to/backups/paris.db.$(date +%Y%m%d_%H%M%S)

# 2. Apply migration (dry-run first — read the SQL)
sqlite3 /path/to/production/paris.db < backend/migrations/002_auth_v2.sql

# 3. Verify tables exist
sqlite3 /path/to/production/paris.db ".tables" | grep auth_v2

# 4. Rollback if needed
sqlite3 /path/to/production/paris.db < backend/migrations/002_auth_v2.rollback.sql
```

**Staging evidence:** Auth V2 staging round-trip test passed (in-memory SQLite, 18/18 scenarios). See docs/BACKEND_AUTH_2_STAGING_ENABLE.md.

**Production owner approval:** Required before migration runs. Do not auto-apply.

## Email Readiness

- Provider: Postmark (selected, not yet configured)
- `EMAIL_SEND_REAL`: `false` (default — must remain false until DNS verified)
- `POSTMARK_SERVER_TOKEN`: `PLACEHOLDER_DO_NOT_COMMIT` (no real key)
- SPF/DKIM/DMARC: documented in docs/BACKEND_EMAIL_2_DNS_PROVIDER.md, NOT applied to Cloudflare DNS yet
- Magic-link template: tested (test_mailer.py — 8/8 pass)
- Fail-closed guard: MailerError raised if real token missing

**Before real email is possible:**
1. Postmark account created + domain verified
2. DNS records applied (SPF, DKIM, DMARC, bounce CNAME)
3. POSTMARK_SERVER_TOKEN set in production env (not committed)
4. EMAIL_SEND_REAL changed to true (requires separate authorization)

## Security Readiness

| Check | Status |
|---|---|
| Magic-link token TTL | 15 minutes (configurable via MAGIC_LINK_TTL_MINUTES) |
| Token hashing | SHA-256 (token never stored plaintext) |
| Single-use enforcement | consumed_at timestamp prevents reuse |
| Session TTL | 30 days (configurable via SESSION_TTL_DAYS) |
| Rate limiting | Not yet implemented — required before production enable |
| CSRF plan | Session cookie (HttpOnly, SameSite=Strict) — not yet wired |
| Audit logging | audit_events_v2 table logs all magic-link events |
| No secrets committed | ✓ |

**Blocker before production enable:** Rate limiting on /auth_v2/request-link endpoint.

## Frontend Readiness

- `login.html`: legacy form login (unchanged)
- Auth V2 login UI: not built
- Planned switch: login.html → magic-link flow (requires separate BACKEND.AUTH.4-FRONTEND authorization)
- Rollback plan: `AUTH_V2_ENABLED=false` in env, restart backend — legacy login immediately restored
- No public claim that Auth V2 is live

## Monitoring Readiness

After enablement (when authorized):
```bash
# Check audit events
sqlite3 production.db "SELECT event_type, COUNT(*) FROM audit_events_v2 GROUP BY event_type ORDER BY 2 DESC LIMIT 20;"

# Check for errors
sqlite3 production.db "SELECT * FROM audit_events_v2 WHERE event_type='magic_link_error' ORDER BY created_at DESC LIMIT 10;"

# Check active sessions
sqlite3 production.db "SELECT COUNT(*) FROM auth_sessions_v2 WHERE expires_at > datetime('now');"
```

Smoke test sequence (after enablement):
1. POST /api/auth_v2/request-link with valid email → 200
2. Check audit_events_v2 for magic_link_requested
3. (staging only) Check mailer captured() for token
4. POST /api/auth_v2/consume-link with token → 200 + session cookie
5. GET /api/auth_v2/me with session cookie → user object
6. POST /api/auth_v2/logout → 200

## Rollback Plan

```bash
# 1. Disable Auth V2 immediately
# Set AUTH_V2_ENABLED=false in production env, restart backend

# 2. Restore login.html legacy state (if it was switched)
git checkout HEAD~1 -- login.html
git push

# 3. Revoke all active sessions (if needed)
sqlite3 production.db "DELETE FROM auth_sessions_v2;"

# 4. DB rollback (only if migration caused issues)
sqlite3 /path/to/production/paris.db < backend/migrations/002_auth_v2.rollback.sql
```

## What Is Still NOT Live

- Auth V2 is NOT enabled in production (`AUTH_V2_ENABLED=false`)
- login.html is unchanged (legacy form login)
- No production DB migration applied
- No real email sending (EMAIL_SEND_REAL=false)
- No Postmark account configured
- No DNS records applied
- Rate limiting not implemented
- Magic-link frontend UI not built

## Required Before Production Enable (future authorization)

1. Rate limiting on request-link endpoint
2. Postmark DNS verified + real token in env
3. login.html magic-link UI built + tested
4. Production DB backup + migration applied
5. Smoke test in production environment
6. Operator approval + ChatGPT authorization of BACKEND.AUTH.4-PRODUCTION-ENABLE
