# BACKEND.AUTH.6 — Auth V2 Production Cutover Plan (Final)

**Status: PLAN ONLY — NO CUTOVER EXECUTED**  
**AUTH_V2_ENABLED: false (unchanged)**  
**EMAIL_SEND_REAL: false (unchanged)**

---

## Preconditions (all must be true before any cutover step)

1. **DB migrations applied** — Migrations 002–007 executed on production DB and verified (17 V2 tables present, existing data preserved).
2. **Postmark DNS verified** — All 4 DNS records present and propagated:
   - SPF `include:spf.protection.postmark.com` in existing SPF record
   - DKIM: `pm._domainkey.pariscomedy.com` CNAME
   - DMARC: `_dmarc.pariscomedy.com` TXT with `p=quarantine`
   - Return-path CNAME: `pm-bounces.pariscomedy.com`
3. **POSTMARK_SERVER_TOKEN in server env only** — Token set via server-side environment variable (Fly.io secret / `.env` on server). Never committed to repo, never in frontend code.
4. **EMAIL_SEND_REAL=false confirmed** — Verified false before beginning; only flipped to true in Phase A after real-send preflight passes.
5. **Regression guard 22/22 PASS** — Run `python3 scripts/regression_guard.py` locally.
6. **Backend tests 232/232 PASS** — Run `cd backend && python3 -m pytest`.
7. **Maintenance window scheduled** — Off-peak hours recommended (04:00–06:00 CET).

---

## Cutover Sequence

### Phase A — EMAIL.6 Real-Send Preflight

**Goal**: Verify Postmark delivers one real magic-link email before any auth flag is touched.

```bash
# On production server — set real-send flag temporarily for preflight only
export EMAIL_SEND_REAL=true
export POSTMARK_SERVER_TOKEN=<token-from-server-env>

# Send one test email to operator address
curl -X POST https://api.pariscomedy.com/api/auth_v2/magic-link/request \
  -H "Content-Type: application/json" \
  -d '{"email":"robert@pariscomedy.com","role":"admin"}'

# Verify: check inbox for magic link email
# Verify: check Postmark dashboard for delivered status
# If email NOT received within 5 minutes → STOP, do not proceed to Phase B
```

**Go gate**: Email received in inbox + Postmark dashboard shows `delivered`. If not: revert `EMAIL_SEND_REAL=false`, diagnose DNS/token, do not proceed.

---

### Phase B — AUTH.7 Staging Smoke Test

**Goal**: Enable Auth V2 in a staging/local environment and run full smoke test suite before production flag flip.

```bash
# Staging environment only
export AUTH_V2_ENABLED=true
export EMAIL_SEND_REAL=true

cd backend
python3 -m pytest tests/test_auth_v2.py -v

# Manual smoke tests (see Smoke Test Plan below)
```

**Go gate**: All 7 smoke tests pass on staging. If any fail → fix before Phase C.

---

### Phase C — AUTH.8 Admin-Only Enable (Production)

**Goal**: Enable Auth V2 in production for admin/operator account only. Legacy login unchanged and still primary.

```bash
# On production server
export AUTH_V2_ENABLED=true
export EMAIL_SEND_REAL=true
# Restart backend
fly app restart pariscomedy-api   # or equivalent restart command

# Verify backend health
curl https://api.pariscomedy.com/health
curl https://api.pariscomedy.com/api/auth_v2/status
# Expect: {"enabled": true, ...}

# Test admin magic link flow manually (robert@pariscomedy.com only)
```

**Go gate**: `/api/auth_v2/status` returns `{"enabled": true}`, magic link received, session created, `/api/auth_v2/verify` accepts token. Legacy login still works.

---

### Phase D — AUTH.9 login.html Switch

**Goal**: Update `login.html` to present Auth V2 as the primary login method. Legacy login remains available but secondary.

**Files changed**: `login.html`
- Remove `v2-draft` CSS class from Auth V2 section
- Remove "Coming soon" / draft notice text
- Make Auth V2 email input + role selector the primary visible form
- Retain legacy login as a fallback link ("Having trouble? Use legacy login →")

```bash
# After editing login.html
git add login.html
git commit -m "AUTH.9: promote Auth V2 to primary login, legacy as fallback"
git push origin main

# Verify on production
curl -s https://pariscomedy.com/login.html | grep 'auth_v2'
```

**Go gate**: Auth V2 form visible and functional on production. Legacy login still reachable via fallback. 0 JS console errors.

---

### Phase E — AUTH.10 Legacy Retirement

**Goal**: Remove legacy comic/booker auth routes after 30-day coexistence period and zero legacy-login reports.

**Timing**: Minimum 30 days after Phase D. Requires:
- Zero support tickets about login failures
- Audit log shows no legacy `/api/auth/request` calls in 7 days
- Robert explicit authorization for route removal

```bash
# backend/routes/auth.py — disable legacy routes
# Set legacy_auth_enabled=false or remove route handlers

# Regression guard update: add check for legacy route removal
python3 scripts/regression_guard.py

# Deploy
git add backend/routes/auth.py scripts/regression_guard.py
git commit -m "AUTH.10: retire legacy auth routes after 30-day coexistence"
git push origin main
```

**Go gate**: Robert explicit sign-off. Zero legacy auth calls in 7-day audit window.

---

## Exact Commands

```bash
# 1. Verify preconditions
python3 scripts/regression_guard.py           # expect 22/22 PASS
cd backend && python3 -m pytest               # expect 232/232 PASS
sqlite3 data/paris.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_v2';"  # expect 17 rows
dig TXT pariscomedy.com | grep spf            # expect include:spf.protection.postmark.com
dig CNAME pm._domainkey.pariscomedy.com       # expect postmark DKIM CNAME

# 2. Phase A — real-send preflight (server)
export EMAIL_SEND_REAL=true
curl -X POST https://api.pariscomedy.com/api/auth_v2/request-link \
  -H "Content-Type: application/json" -d '{"email":"robert@pariscomedy.com","role":"admin"}'

# 3. Phase C — production flag enable (server)
# (set via Fly secrets or server .env, never in repo)
fly secrets set AUTH_V2_ENABLED=true EMAIL_SEND_REAL=true
fly app restart pariscomedy-api

# 4. Verify
curl https://api.pariscomedy.com/api/auth_v2/status
curl https://api.pariscomedy.com/health
```

---

## Smoke Test Plan (7 tests)

| # | Test | Expected |
|---|---|---|
| 1 | `GET /api/auth_v2/status` | `{"enabled": true, "email_configured": true}` |
| 2 | `POST /api/auth_v2/magic-link/request` with valid email | HTTP 200, email delivered in inbox |
| 3 | `GET /api/auth_v2/magic-link/consume?token=<valid>` | HTTP 200, session cookie set |
| 4 | `GET /api/auth_v2/magic-link/consume?token=<expired>` | HTTP 401, `{"error": "token_expired"}` |
| 5 | `GET /api/auth_v2/magic-link/consume?token=<invalid>` | HTTP 401, `{"error": "invalid_token"}` |
| 6 | `POST /api/auth/request` (legacy comic) | HTTP 200 — legacy still works |
| 7 | `POST /api/booker/auth` (legacy booker) | HTTP 200 — legacy still works |

---

## Rollback Plan

```bash
# Immediate rollback — revert flag, restart
fly secrets set AUTH_V2_ENABLED=false EMAIL_SEND_REAL=false
fly app restart pariscomedy-api

# Verify rollback
curl https://api.pariscomedy.com/api/auth_v2/status
# Expect: {"enabled": false} or 503

# Verify legacy still works
curl -X POST https://api.pariscomedy.com/api/auth/request \
  -H "Content-Type: application/json" -d '{"email":"test@example.com"}'

# If login.html was already switched (Phase D), revert the file:
git revert HEAD --no-edit
git push origin main
```

---

## Go / No-Go Gates

| Gate | Condition | Action if NO |
|---|---|---|
| DB migrations verified | 17 V2 tables present, existing data unchanged | Apply migrations first; do not proceed |
| DNS verified | All 4 Postmark records propagated | Fix DNS, wait 24h propagation, re-verify |
| Real email delivered | Phase A preflight email received in inbox | Diagnose Postmark token/DNS; do not proceed |
| Staging smoke tests pass | All 7 tests GREEN on staging | Fix failures; do not proceed to production |
| Regression guard 22/22 | No regressions | Fix guard failures first |
| Backend tests 232/232 | No test failures | Fix test failures first |
| Robert authorization | Robert types cutover authorization text | Do not proceed without it |

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Postmark token missing/expired on server | Medium | High | Verify token in server env before Phase A; test with real preflight send |
| R2 | Magic link email lands in spam | Low | Medium | Check spam folder in Phase A; add `X-PM-Tag` header for easy filtering |
| R3 | Token expiry too short for user flow | Low | Medium | Default 15-min expiry; consider 30-min for initial rollout |
| R4 | Legacy login traffic during cutover | Low | High | Keep legacy routes live for 30 days minimum; monitor access logs |
| R5 | DB session table write failure | Low | High | Verify sessions_v2 table writable before Phase C; test with dry insert |
| R6 | login.html CDN cache serving old version | Medium | Medium | Append `?v=<timestamp>` to login.html URL or purge CDN after Phase D deploy |
