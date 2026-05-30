# 07_CHANGELOG

## 2026-05-30 | backend | BACKEND.EMAIL.1-PLAN-SCAFFOLD: email plan + dry-run mailer

ChatGPT-authorized. Plan + dry-run mailer scaffold. No real send. No provider key.

backend/mailer.py (NEW): dry-run-first abstraction.
  - send(OutgoingEmail) entry point; validates from/to/reply-to, captures
    payload in-process for tests, stderr log line in dry-run.
  - EMAIL_SEND_REAL defaults false; EMAIL_PROVIDER defaults "dryrun".
  - magic_link_email(to, token, base_url) template - text + HTML pair,
    link only, subject does NOT contain token.
  - Real-send path raises NotImplementedError - provider wiring deferred.

backend/tests/test_mailer.py (NEW): 7 tests.
  dry-run captures payload; template includes link; invalid to/from fail closed;
  status reports state; real-send with provider=dryrun stays dry-run;
  real-send with unconfigured provider raises NotImplementedError.

docs/BACKEND_EMAIL_1_PLAN.md (NEW): full email plan.
  Inbound: Cloudflare Email Routing (chuck/payments/support/no-reply).
  Outbound: Postmark recommended. SPF + DKIM + DMARC ramp p=none -> quarantine
  -> reject. Security: tokens never logged in production mode; rate limit
  reuses auth_v2 gate; audit events to audit_events_v2 (action email.send.*).

data/email-plan.json (NEW): machine-readable companion.

Tests: 39/39 PASS (15 service + 12 router + 5 main integration + 7 mailer).
Live frontend regression: 12/12 PASS unchanged. Auth V2 remains disabled.
No real email. No DNS change. No provider API key. No env.example change yet.

Rollback: git revert <this-sha>


## 2026-05-30 | backend | BACKEND.AUTH.1-ROUTER-INTEGRATION-DISABLED

ChatGPT-authorized. backend/main.py now imports auth_v2_router inside a
try/except guard - if the import fails the app falls back to legacy
behavior with a stderr log line. AUTH_V2_ENABLED stays false in production
so action endpoints return 503 disabled.

backend/tests/test_main_integration.py (NEW): 5 integration tests proving
the router is mounted; /status returns enabled=false; every action endpoint
returns 503 auth/disabled; no DB rows created in v2 tables when disabled
endpoints are hit; legacy /api/health still responds.

docs/BACKEND_AUTH_1_ROUTER_INTEGRATION_DISABLED.md (NEW): full design +
production behavior table + rollback.

Tests: 32/32 PASS (15 service + 12 router + 5 integration).
Live frontend regression: 12/12 PASS unchanged.

No real email. No DB auto-apply. No login.html change. No secrets.

Rollback: git revert <this-sha>


## 2026-05-30 | backend | BACKEND.AUTH.1-CUTOVER-PLAN: wire v2 endpoints behind disabled flag

ChatGPT-authorized 2026-05-30. Plan + inert wiring only, no production enablement.

backend/auth_v2_router.py (NEW): FastAPI APIRouter at /api/auth_v2/*.
  - /status, /magic-link/request, /magic-link/consume, /logout, /me, /session/expiry
  - All gated by AUTH_V2_ENABLED. When false (default) every endpoint returns
    503 {error:{code:"auth/disabled"}} and creates no token/session/audit row.
  - When enabled (test env only) endpoints delegate to auth_v2.py service module.
  - Cookie design: pc_session_v2 HttpOnly+Secure+SameSite=Lax, pc_csrf_v2 readable
    by frontend JS for X-CSRF-Token echo on writes.

backend/tests/test_auth_v2_router.py (NEW): 12 tests
  Disabled-mode (5): /status reports false; request/consume/logout/me/expiry all 503;
    no DB state created when disabled.
  Enabled-mode (7): /status reports true; request 204 + DB row; full round-trip
    request->consume->/me->logout->/me-after-logout 401; reused token rejected;
    /me without session 401.

docs/BACKEND_AUTH_1_CUTOVER_PLAN.md: design + cookie plan + frontend cutover plan
  + email cutover dependency + migration apply instructions + rollback.

NOT YET in main.py - the line app.include_router(auth_v2_router.router) lands in
the cutover phase only. Until then the router is importable + tested but
unreachable in production.

Tests: 27/27 PASS (15 service + 12 router).
Live site regression: 12/12 PASS unchanged. Public site untouched.
No secrets. No real email. No DB migration auto-apply. No login.html change.

Rollback: git revert <this-sha>


## 2026-05-30 | backend | BACKEND.AUTH.1-SCAFFOLD: inert v2 auth scaffold

ChatGPT-authorized 2026-05-30. Scaffold + safety boundary, no production cutover.

Files (all under backend/):
- migrations/002_auth_v2.sql              5 new tables (users_v2, sessions_v2,
                                          magic_links_v2, audit_events_v2, rate_limits_v2)
- migrations/002_auth_v2.rollback.sql     drops the 5 v2 tables
- auth_v2.py                              service module: request_magic_link,
                                          consume_magic_link, invalidate_old_tokens_for_email,
                                          create_session, logout, get_current_user, audit
- tests/test_auth_v2.py + tests/__init__.py  15 unit tests, all PASS

docs/BACKEND_AUTH_1_SCAFFOLD.md - engineering note + cutover plan.

Safety boundary:
- AUTH_V2_ENABLED env var defaults false; nothing in main.py reads auth_v2
- AUTH_V2_DRY_RUN_MAILER defaults true; magic-link tokens written to stderr only
- Migration NOT auto-applied; run sqlite3 < migrations/002_auth_v2.sql to apply
- Coexists with existing booker_sessions; no v1 table touched
- Magic-link tokens hashed (SHA-256) before storage; single-use enforced;
  TTL 15 min; rate limit 10/email/hour
- Session TTL 14 days rolling; logout sets revoked_at and is idempotent
- Roles enum-checked: user/comic/booker/admin only

ChatGPT-mandated test coverage (15/15 OK):
- magic-link round-trip
- consumed token rejected on re-use
- invalidated token (via invalidate_old_tokens) rejected
- expired token rejected
- unknown token rejected
- rate limit blocks after threshold
- rate limit isolated per email
- get_current_user for valid session
- logout invalidates session (idempotent)
- empty / unknown session returns None
- expired session returns None
- role separation: comic/booker get distinct user_ids + sessions
- invalid role rejected
- audit events recorded on request + consume
- status() reports enabled=false by default

Live site impact: NONE. Cloudflare Pages serves static files only; backend/
directory is part of the repo for deployment elsewhere. Public site
regression unchanged (12/12 PASS).

No payments / messaging / claims / submissions / ticket adapter / frontend
redesign / nav / schema / secrets changed.

Rollback:
  git revert <this-sha>
  sqlite3 data/paris.db < backend/migrations/002_auth_v2.rollback.sql  # if applied


## 2026-05-30 | docs | BACKEND.PLAN.1: backend implementation plan (plan-only)

ChatGPT-authorized 2026-05-30 (BACKEND.PLAN.1 - plan only, do not implement).

Seven new plan files:
- docs/BACKEND_PLAN_1.md           - master plan, per-area classification
- data/backend-plan.json           - machine-readable companion
- docs/API_CONTRACT_DRAFT.md       - REST endpoints + CSRF + error catalog
- docs/DB_SCHEMA_DRAFT.md          - engine-portable schema (Postgres/SQLite)
- docs/BACKEND_RISK_REGISTER.md    - 20 risks + 10 open decisions
- docs/BACKEND_IMPLEMENTATION_SEQUENCE.md - ordered execution: AUTH > SUBMIT > CLAIM > EMAIL > PAYMENTS > MESSAGING > TICKETS
- chuck_vault/.../BACKEND_PLAN_1.md - vault mirror

Coverage: Auth, Show Submissions, Claim flows, Messaging, Payments, Ticket
adapters, Email/domain. Each item classified
(frontend-only / backend-required / database-required / email-required /
payment-provider-required / admin-review-required / legal-compliance-required /
blocked / ready-to-build).

No backend code changed. No production behavior change. No DB migration.
Public site unchanged.

Also filed: BUG-P1-COPY-002 - residual "All comedy shows/venues" browse-link
overclaim on show.html (non-blocking, deferred to a copy/guard pass).

Rollback: git revert <sha>


## 2026-05-30 | data | P1.DATA.3B: sync show.html noscript fallback with audit JSON

ChatGPT-authorized 2026-05-30 (P1.DATA.3B - synchronize show.html raw
fallback with data/freshness-audit.json).

Root cause: show.html had 14 hardcoded <article id="show-{slug}"> blocks
inside <noscript> with static data-verification-status, source URL, and
"Last checked: 2026-05-29" freshness lines. They were last hand-edited and
never regenerated, so they drifted away from data/freshness-audit.json. ChatGPT
caught millennial-meltdown showing verified_24h in show.html while the live
audit said needs_human_review.

scripts/sync_show_fallback.py (NEW):
  Reads data/freshness-audit.json, walks every <article id="show-{slug}">
  block in show.html, rewrites three things on each: the
  data-verification-status attribute, the Get-tickets <a href> (so repointed
  source URLs flow through to noscript), and the <p class="freshness">
  inner content (Last checked / Status label / confidence). Everything else
  in the article (h2 / venue / address / description / disclaimer) is
  preserved. Idempotent.

scripts/freshness_daily_wrapper.sh:
  After every freshness_verify run, if the audit JSON changed the wrapper
  now also runs sync_show_fallback.py and stages show.html in the same
  commit. Daily 06:30 LaunchAgent will keep noscript in sync going forward.

scripts/regression_guard.py - new check show_fallback_sync:
  For every <article id="show-{slug}"> block in show.html, FAILs if
  (a) the data-verification-status differs from data/freshness-audit.json's
  verification_status for that slug, or (b) the freshness Last-checked date
  is older than the audit's last_checked_at date for that slug.
  Closes the drift root cause: any future audit run that does not
  re-sync the fallback fails regression immediately.

show.html: regenerated noscript articles for all 14 listings - now reflect:
  verified_24h: charonne, comedy-crush, comedy-lab-chat-noir, cuba-compagnie,
                coucou-friday, ffcn, green-light, green-mic-showcase, rocket,
                smash, velvet-comedy (11 total)
  needs_human_review: millennial-meltdown, theatre-bo-julie, wednesday-night-comedy
  ffcn, charonne, velvet-comedy <a href> now uses the repointed Eventbrite URLs.

Regression: 12/12 PASS (was 11/11). show_fallback_sync PASS, 0 problems on
14 articles checked.

Rollback: git revert <sha>

Vault: chuck_vault/10-concepts/projects/pariscomedy-canonical/
  P1_DATA_3B_FALLBACK_SYNC.md (to be created) +
  PHASE_LEDGER.md (P1.DATA.3B row IN_GIT_UNVERIFIED).


## 2026-05-30 | data | P1.DATA.3.LITE: source repoints + remove "sales end" overmatch

ChatGPT-authorized 2026-05-30 (P1.DATA.3.LITE — manual source URL repoint
for ended recurring listings).

data/manual-source-repoints.json (new):
  Hand-verified per-slug source_url overrides. Each entry must satisfy:
  (a) HTTP 200, (b) no HTML `event ended`/`sales ended` badge, (c) title
  shares the listing's distinctive tokens. Loose matches (same organizer
  but different show, e.g. Cuba Compagnie -> LES CAVES) are NOT included
  and stay needs_human_review. Three confirmed repoints:
    - ffcn:          1989838522586 -> 1989838453379 (FRENCH FRIED June 3)
    - charonne:      1697805324429 -> 1697801202099 (Charonne May 30)
    - velvet-comedy: 1989840198599 -> 1989840111338 (Velvet Bar June 3)
  Eleven other listings documented in "not_repointed" with the reason.

scripts/freshness_verify.py:
  - load_repoints() reads data/manual-source-repoints.json once per run.
  - verify_listing() prefers the repoint new_url over the API-stored URL
    when present. Output records both source_url (the URL actually fetched)
    and api_source_url (the original) plus source_repointed: true.
  - REMOVED "sales end" from past_signals — it was a greedy over-match that
    flipped LIVE bookable events to needs_human_review whenever Eventbrite
    rendered text like "Sales end June 10" or "Sales end Tomorrow". The
    proper match remains "sales ended" (past tense) which is the actual
    ended-event badge.

Live audit delta:
  Before (with "sales end" + no repoints):  needs_human_review 14 / verified_24h 0
  After  (sans "sales end" + 3 repoints):   needs_human_review 3  / verified_24h 11

Genuinely ended (verified ended badge): millennial-meltdown, theatre-bo-julie,
wednesday-night-comedy. Their organizers have not yet posted future
instances Eventbrite exposes via MoreOrganizerEvents.

Regression: 11/11 PASS. Status sweep 31/31 HTTP 200.

Rollback: git revert <sha>


## 2026-05-30 | data | P1.DATA.2.FIX-DEPLOY-RECONCILE — close root cause + tonight panel guard

Closes the two latent issues disclosed in the previous P1.DATA.2.FIX proof:

1. index.html — every SHOWS_DATA filter chain on the homepage now applies
   `isFreshEnough(s.slug)`: `renderTonightInParis()`, `recomputeShowWindows()`
   (both `TONIGHT_SHOWS` and `WEEK_SHOWS`), and `allShows()`. Ended Eventbrite
   listings can no longer promote on the Tonight panel or any downstream feed.
2. scripts/regression_guard.py — `freshness_sanity` now reads `verification_status`
   (the actual field name); previously it read non-existent `status` and was a
   no-op that silently PASSed. Plus new check `homepage_freshness_filter` scans
   index.html for every `SHOWS_DATA.filter(` invocation and FAILs if any nearby
   callback omits `isFreshEnough`. Closes the root cause that made the
   Tonight-panel bypass possible.

Regression: 11/11 PASS (was 10/10).

Rollback: `git revert <sha>`


## 2026-05-30 | data | P1.DATA.2.FIX — Eventbrite past-event detection (BUG-P0-008)

scripts/freshness_verify.py — three changes, all confined to the past-event branch of `verify_listing()`:

1. Extended `past_signals` list with phrases Eventbrite actually renders:
   `event ended`, `sales ended`, `sales end`, `this event has already taken place`,
   `cet événement est passé`, `événement terminé`, `ventes terminées`, `vente terminée`.
2. Raised body read window from 80 000 → 250 000 bytes (Eventbrite event UI badge
   sits at ~82 KB on the failing case, just past the old cap).
3. Filter out i18n-dictionary false-positives: Eventbrite ships
   `{"event ended":"l'événement s'est terminé",…}` in every page; a phrase only
   counts as a real status marker when the next character is not `"` (the JSON
   value separator).
4. Past-event branch now sets `verification_status: needs_human_review`
   (conf 10, high risk) instead of `source_unreachable` (conf 0) — semantically
   the URL IS reachable; the listing simply needs a human to repoint
   `source_url` at a current Eventbrite instance.

Live impact (one local run): 14/14 active listings flipped from `verified_24h` to
`needs_human_review` because every stored `source_url` currently points to an
ended Eventbrite event instance (recurring series have rolled to new URLs).
This is the correct, trust-honest behavior per ChatGPT P1.DATA.2.FIX spec.

Regression: 10/10 regression_guard checks PASS. 31/31 public pages return 200.
No nav / schema / auth / payment / messaging changes.

Rollback: `git revert <sha>`


## 2026-05-29 | frontend | P3.CLAIM.2 + P3.CLAIM.3
- Closed P3.CLAIM.1 critical findings FIND-2 (comic claim sent `{slug}` only — any verified-email user could claim any comic) and FIND-3 (show claim collected no evidence beyond freeform `message`).
- **P3.CLAIM.2 (`performer-portal.html`):** Added optional evidence-collection fields to the comic-claim banner — Instagram handle (with "@" prefix), recent IG/socials post URL, headshot URL, and a "I'll send my headshot by reply email" checkbox. Fields appended to `POST /api/performer/claim` body as `{instagram, recent_post_url, headshot_url, headshot_via_email}`. Also replaced the previous auto-fire behavior: instead of submitting the claim the moment a signed-in user lands on `?claim=<slug>`, the page now reveals a "Submit claim" button so the user can attach evidence before the claim is filed. `focus` rehydration changed in lockstep — pending-claim slug now reveals the button instead of auto-replaying. Helper note: "These help us verify it's really you. We'll never publish your private email."
- **P3.CLAIM.3 (`book.html`):** Added optional evidence panel to the show-runner form (`#sr-claim-evidence`), shown only when `?claim=<slug>` is present. Three new inputs: Show Instagram handle, Recent show poster URL (Eventbrite/IG/website), and Domain-bound contact email with inline amber hint that fires when the address resolves to a free provider (gmail/yahoo/outlook/hotmail/live/icloud/me/aol/proton). Fields appended to `POST /api/show/claim` body as `{show_instagram, recent_poster_url, contact_email}`.
- Backend out of scope (operator-review path); none of the new fields are required (backend validates). Doctrine intact (0 bilingual / mixed-language).
- Files touched: `performer-portal.html`, `book.html`. Verified: Playwright snapshot confirms all 3 evidence inputs visible on each page in claim mode; regression_guard 10/10 PASS; 31 pages 200.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P3_CLAIM_3_EVIDENCE_COLLECTION.md`.

## 2026-05-29 | frontend | P3.SUBMIT.4
- Closed P3.SUBMIT.1 high-severity audit finding: orphaned localhost-only intake server + static review-queue UI advertising a non-existent workflow. Decision: **deprecate** (clean path; backend wiring out of scope).
- Moved `api/intake_server.py` → `api/_deprecated/intake_server.py` (preserved, not deleted). Added module-level docstring documenting deprecation date (2026-05-29), the canonical submit flow (`/book.html` → `POST https://api.pariscomedy.com/api/submissions`), the operator inspection path (`/status.html`), the machine-local dependencies (`send_email.py`, sqlite under `data/intake/`), and the explicit "do not re-enable without re-audit" warning.
- Added prominent amber deprecation banner to `api/review-queue.html` above the H1: `<strong>DEPRECATED (2026-05-29):</strong> This page is a static placeholder. Live submissions land at api.pariscomedy.com/api/submissions. To inspect them, use the operator HUD at /status.html. The table below is historical scaffolding and is not auto-updated.` Banner is `.deprecation-banner` (amber, left-border accent, role="alert"). Page still returns 200; static table preserved for historical reference but the page's purpose is now honest.
- Replaced `data/review_queue.json` `[]` placeholder with a status-marker object: `_status: "deprecated"`, `_replaced_by: "api.pariscomedy.com/api/submissions"`, `_deprecated_on: "2026-05-29"`, `_deprecated_by: "P3.SUBMIT.4"`, `_note`, and an empty `items: []` preserving shape for any future backend producer.
- Files touched: `api/intake_server.py` (mv → `api/_deprecated/`), `api/_deprecated/intake_server.py` (docstring header), `api/review-queue.html` (banner + CSS), `data/review_queue.json` (status marker). NOT touched: `book.html` submit handlers (per scope; commit 87b24c3 is canonical), no backend, no fetch calls.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P3_SUBMIT_4_DEPRECATE_INTAKE.md`.

## 2026-05-29 | audit | P3.SUBMIT.1 + P3.CLAIM.1
- **P3.SUBMIT.1 (AUDIT ONLY):** Audited show-submission + review workflow across `book.html`, `admin-submit.html`, `show-runner.html`, `api/intake_server.py`, `api/review-queue.html`, `js/leadcapture.js`, `data/review_queue.json`, `data/show_approvals.json`, `data/intake/`. Output: `data/p3-submit-audit.json`. 12 findings (1 critical / 2 high / 4 medium / 4 low / 1 info). **Critical:** `book.html` ships TWO `<script>` blocks defining `submitShowRunner`/`submitComedian`/`submitBooker`/`submitMessage`/`showPath`; the second declaration wins, killing the entire `LeadCapture` offline-fallback path (mailto + localStorage). **High:** `api/intake_server.py` is orphaned (localhost-only, no form targets it); `api/review-queue.html` is fully static — `data/review_queue.json` is `[]` with no producer/consumer/schema. **Medium:** 3 of 4 tabs lack the honeypot field; JSONL race in intake_server; `admin-submit.html` has TODO password gate at line 2. Vault doc: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P3_SUBMIT_1_AUDIT.md`. No HTML / scripts modified. No fetch calls.
- **P3.CLAIM.1 (AUDIT ONLY):** Audited comic + show-runner + booker claim mechanics across `book.html` (`?claim=`), `performer-portal.html` (`?claim=`), `booker-portal.html`, `booker-dashboard.html`, `show-runner.html`, `c/*.html`, `shows/*.html`, `data/schema.json`. Output: `data/p3-claim-audit.json`. 13 findings (2 critical / 2 high / 5 medium / 3 low / 1 info). **Critical:** show-runner claim collects zero evidence (no Instagram, photo, domain-bound email — only freeform `message` field); comic claim sends only `{slug}` to `/api/performer/claim` so any verified-email user can claim any comic slug. **High:** no claim-race visibility; `/shows/<slug>.html` "Report it" → `/book.html?report=<slug>` is dead UI (no `?report=` handler in book.html). **Medium:** venue-claim schema with no UI; ownership badge fails open (API outage looks like "unclaimed"); slug sanitizer silently mutates non-ASCII; three portals use three different auth schemes (Bearer / cookie / `X-Booker-Token`). Vault doc: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P3_CLAIM_1_AUDIT.md`. No HTML / scripts modified. No fetch calls.

## 2026-05-29 | audit | P3.AUTH.1
- Login + token-safety AUDIT (no patches, no HTML touched, no backend calls). Scope locked by master prompt "no auth changes" without explicit authorization. Output: `data/p3-auth-audit.json` + vault doc `P3_AUTH_1_LOGIN_AUDIT.md`.
- Files inspected: `login.html`, `auth/verify.html`, `performer-portal.html`, `booker-portal.html`, `booker-dashboard.html`, `show-runner.html`, `admin-crm.html`, `admin-events.html`, `admin-messages.html`, `admin-payments.html`, `partials/nav.shell.{portal,admin}.html`.
- Token inventory: 7 distinct token-shaped localStorage keys (`booker_token`, `booker_email`, `pc_session_token`, `pc_auth_email`, `pc_owner_token`, `admin_token`, `pc_admin_secret`); zero sessionStorage; zero frontend cookie writes; comic flow uses `credentials:'include'` so a backend HttpOnly cookie is presumed but not visible from frontend.
- 4 login flows mapped: comic magic-link, booker token, show-runner owner-token (with `?owner_token=` URL auto-login), admin paste tokens (with `?token=` URL auto-login on 3 admin pages).
- 10 findings (3 high, 5 medium, 2 low). Highest-impact: (H1) every "Sign Out" nav link is a plain `<a href="/login.html">` that does NOT clear any token — `booker-dashboard.html` even defines a real `logout()` at line 385 that is never wired to the nav. (H2) Zero `api()` helper inspects HTTP 401 → revoked tokens stay in localStorage and produce opaque error loops (root cause of ChatGPT's "old token reuse"). (H3) Persistent tokens travel as URL query strings on `show-runner`, `admin-crm`, `admin-events`, `admin-messages`, and `performer-portal` (offers endpoint) — Referer/history/log leak.
- Mediums: (M4) `auth/verify.html` has no special path for "already-used magic link" or "already signed in"; (M5) `login.html:129` auto-persists booker `dev_token` before user action — shared-device leak; (M6) auto-login query strings never scrubbed via `history.replaceState`; (M7) no frontend `exp` tracking — needs backend to return `expires_at`; (M10) three independent surfaces (login, booker-portal, booker-dashboard) each clobber `booker_token` last-writer-wins.
- Lows: (L8) `pc_auth_email` is set in `auth/verify.html:55` but never read; (L9) comic claim flow auto-fires `submitClaim` from `pending_claim_slug` on window focus with no user confirmation.
- Scaffold proposal parked for P3.AUTH.2: new `assets/auth-helpers.js` exporting `AUTH_KEYS`, `clearAllAuth()`, `signOut()`, `getToken/setToken`, `authFetch()` with 401 auto-clear, `stripTokenFromURL()`. Wire into both nav partials + 5 page files.
- Recommended next sub-phase: **P3.AUTH.2** — implement FIND-1, FIND-2, FIND-3 (frontend half), FIND-5, FIND-6, FIND-8, FIND-9 (no backend coordination). **P3.AUTH.3** — FIND-4, FIND-7, FIND-10 (requires backend to expose `expires_at` + stable verify error codes + token rotation semantics).
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P3_AUTH_1_LOGIN_AUDIT.md`.

## 2026-05-29 | scaffold | P3.MESSAGING.1 + P3.PAYMENTS.1
- **P3.MESSAGING.1 (SCAFFOLD ONLY):** Created `data/messaging-schema.json` — canonical schema for direct messaging. Three tables: `messages` (id, thread_id, from_user, to_user, body [NOT search-indexed], created_at, read_at, paid_at, flag_count), `dm_threads` (id, participants[2], created_at, last_message_at, is_closed), `dm_quota` (user_id+date_utc composite PK, sent_count, plan, plan_expires_at). Free join open to anyone; free outbound = 1/day to verified comics/bookers only; `dm_plus_monthly` (€1/mo) = unlimited + read receipts. Spam prevention: per-day quota, 60s per-thread cooldown, flag_count>=3 → review queue, 30-day block on closed threads. Privacy: body NOT full-text indexed, no exposure via `/api/search`. Transport (polling vs WebSocket vs SSE) deferred to BE phase — v1 recommendation is 15s polling. `_enabled: false`. No HTML touched. No backend code. Doctrine: no bilingual/mixed-language copy.
- **P3.PAYMENTS.1 (SCAFFOLD ONLY):** Created `data/payments-plans.json` — 5-plan catalog: `comic_plus_lifetime` (€1 one-time, first 100 only), `comic_plus_monthly` (€1/mo, after first 100), `booker_plus_monthly` (€1/mo intro 6 months → €5/mo), `dm_plus_monthly` (€1/mo, pairs with P3.MESSAGING.1), `show_highlight_weekly` (€5 / 7 days). Each plan has `name_en` + `name_fr` (separate keys, never combined), `price_eur`, `currency: "EUR"`, `period`, `processor: "sumup"`, `tax_inclusive: true`, `fr_vat_rate: 0.20`, `compliance_url: "/disclosure.html"`, `refund_window_days: 14`. Primary processor SumUp (Robert's existing account, EU-friendly), Stripe fallback. Merchant of record: Paris Comedy SAS (placeholder). FR VAT 20% inclusive; invoice HT/TVA/TTC line split required. Refund: EU 14-day distance-selling right with immediate-execution waiver at checkout. Onboarding requires VAT number, SIRET, IBAN, SumUp merchant verification. `_enabled: false`. No live processor wiring. No keys in repo. No HTML touched. Doctrine: no bilingual/mixed-language copy.
- Vault docs: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P3_MESSAGING_1_SCAFFOLD.md` + `P3_PAYMENTS_1_SCAFFOLD.md` document doctrine, plan tiers, processor strategy, activation gates, cross-links.

## 2026-05-29 | seo | P4.PAGES.1
- Programmatic per-show static pages audit + minimal scaffold. Doctrine: NO thin pages. Audit doc `data/programmatic-pages-audit.json` evaluates 5 candidates (`/tonight`, `/this-week`, `/venues/{slug}`, `/shows/{slug}.html`, `/c/{slug}.html`). Deferred 3 candidates with concrete data-density blockers; built 1 with sufficient density.
- Built 11 new static `/shows/{slug}.html` pages for verified_24h slugs not already on disk: charonne, comedy-crush, comedy-lab-chat-noir, cuba-compagnie, coucou-friday, green-light, millennial-meltdown, rocket, smash, velvet-comedy, wednesday-night-comedy. Each page: title `{show name} — {venue} — Paris Comedy`, 1-sentence meta description sourced from show editorial copy, canonical `https://pariscomedy.com/shows/{slug}.html`, `<link rel="alternate" href="https://pariscomedy.com/show.html?slug={slug}">` to disambiguate from query-string variant, `nav-shell-marketing` + marketing footer partials, single article with H1, venue, day/time, language, description, ticket CTA `rel="nofollow sponsored"`, source disclosure block, Event JSON-LD. Page sizes 6,312–6,998 bytes — far above thin-page threshold.
- Skipped 2 verified_24h slugs whose `/shows/{slug}.html` already existed (`ffcn`, `green-mic-showcase`) — task forbids touching existing HTML pages. Skipped 1 needs_human_review slug (`theatre-bo-julie`) per scope.
- Extended `scripts/generate_sitemap.py` to emit `/shows/{slug}.html` URLs in addition to `/show.html?slug={slug}` legacy URLs. Sitemap regenerated: 28 → 41 URLs (+13: 11 new pages + ffcn + green-mic-showcase static variants).
- Generator script `scripts/build_show_pages.py` is rerunnable and skips any target file that already exists, so future verified_24h additions can be filled in safely.
- Verified: 0 forbidden strings (bilingual/mixed-language/multilingual/etc.) across new pages. Each page has exactly one `nav-shell-marketing` nav. Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P4_PAGES_1_PROGRAMMATIC_PAGES.md`.

## 2026-05-29 | infra | P5.AGENTS.1
- Added `scripts/agent_write_lock.py` — stdlib-only file lock helper. Atomic create via `os.open(O_CREAT|O_EXCL)` on `.pc-write.lock` at repo root; JSON payload `{agent_name, scope, acquired_at, pid}`. Four commands: `acquire <agent> "<scope>"`, `release`, `read_status`, `enforce_for_commit`. Stale-timeout 15 min — a lock older than that is overridden with a stderr warning, so a crashed agent never locks out the next run.
- Added `.githooks/pre-commit` — calls `enforce_for_commit`. **Soft enforcement**: only blocks when `PC_AGENT_NAME` is set AND mismatches the lock holder. Humans + the main agent (no `PC_AGENT_NAME`) stay free. Activate per-clone with `git config core.hooksPath .githooks`.
- `.gitignore` — `.pc-write.lock` ignored (runtime artifact, never committed).
- `data/source-adapters.json` — added `_write_lock_policy` field documenting that adapter scripts must acquire/release before any write to `data/`.
- Anti-PROCESS-P1-001: codifies single-writer-at-a-time so batched out-of-order writes can't contaminate `data/*.json`, HTML, or partials mid-session.
- Verified locally: `acquire test_agent "demo"` → lock written; `read_status` → holder JSON; `release` → removed. No HTML touched. `regression_guard.py` still 10/10 PASS.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P5_AGENTS_1_WRITE_LOCK.md`.

## 2026-05-29 | ux | P2.UX.2
- Playwright audit at mobile 390x844, tablet 820x1180, desktop 1280x900 against production `https://pariscomedy.com` across 7 pages (`/`, `/shows.html`, `/venues.html`, `/comedians.html`, `/show.html?slug=charonne`, `/pricing.html`, `/book.html`) — 21 page-viewport runs total. Per-run probe: horizontal overflow (`scrollWidth > clientWidth`), elements wider than viewport, nav visibility/scroll, primary CTA widths (`.btn-primary/.btn-secondary/.btn-book/.btn-plan`), footer presence, `pageerror` count. Output: `data/ux-mobile-tablet-audit.json`; screenshots at `/tmp/p2-ux-2/{viewport}-{page}.png`.
- 1 issue found: mobile (390px) homepage horizontal overflow (`sw=558` vs `vw=390`). Root cause: `.hero-left h1` containing the unbreakable hyphenated word "English-Language" forced min-content width ~540px, expanding the single-column grid track past the viewport. Small CSS fix applied inline in `index.html`: `.hero-left{min-width:0}`, `.hero-left h1{...overflow-wrap:anywhere;word-break:break-word}`, plus a `@media(max-width:480px)` h1 size clamp override. Re-verified locally → `sw=390`, `h1.width=354`, no horizontal scroll. No external CSS, no nav/footer/script changes.
- 20 other runs GREEN: no nav overflow, no footer missing, no too-narrow / too-wide CTAs, no `pageerror`s. Zero deferred BUGs.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P2_UX_2_MOBILE_TABLET_AUDIT.md`.

## 2026-05-29 | infra | P2.UX.1
- Added `header_cta_rule` check to `scripts/regression_guard.py` (now 10 checks total). For each public page, extracts the first `<nav class="nav-shell-*">` block, collects every `href`, and diffs against the canonical href set parsed from the matching `partials/nav.shell.<variant>.html`. FAIL on any extra href (page-specific CTA leaking into the global nav) or more than one missing canonical href.
- Canonical sets parsed at runtime: marketing (9), minimal (1), auth (3), portal (6), admin (8). Documented exceptions: `/archive.html` may carry an extra `/archive.html` link; `/disclosure.html` + `/fr/disclosure.html` (minimal shell) may carry curated cross-legal links (`/about`, `/shows`, `/terms`, `/privacy`, `/fr/terms`, `/fr/privacy`).
- Wired into the default-run list. Verified: `python3 scripts/regression_guard.py` → 10/10 PASS; standalone `--check header_cta_rule` → PASS (30 pages inspected). Status sweep still 31/31. No HTML touched.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P2_UX_1_HEADER_CTA_RULE.md`.

## 2026-05-29 | infra | P5.AUTOMATION.1
- Added `scripts/daily_proof_package.py` — single aggregator that runs `freshness_verify.py` + `regression_guard.py` + `generate_sitemap.py`, captures each into a structured JSON, and writes `logs/daily-proof-{ISO}.json` with sections `freshness`, `regression`, `sitemap-size` plus a top-level `failures` array. Exit 0 if all PASS, 1 if any FAIL. stdlib only.
- Extended `scripts/freshness_daily_wrapper.sh` — after the existing freshness commit, invokes the aggregator (output appended to `logs/freshness-daily.log`) and commits/pushes `sitemap.xml` if it changed. `logs/daily-proof-*.json` stays local as the evidence trail.
- Verified: `bash scripts/freshness_daily_wrapper.sh` → exit 0; status sweep 31 pages, 0 bad (≥27 pages 200). No HTML touched.

## 2026-05-29 | infra | P4.SITEMAP.1
- Regenerated `sitemap.xml` from real public pages + verified shows. Now includes 15 public pages + 13 `/show.html?slug=...` entries (only `verified_24h`/`verified_72h` from `data/freshness-audit.json`) = 28 URLs. Each `<lastmod>` from `git log -1 --format=%cs`. Six legal pages (terms/privacy/disclosure × EN/FR) carry `xhtml:link rel="alternate" hreflang` pairs + `x-default`.
- Excluded (noindex or auth-only): `404.html`, `admin-{events,crm,messages,payments,submit}.html`, `booker-{portal,dashboard}.html`, `performer-portal.html`, `show-runner.html`, `login.html`, `checkout-pending.html`, `r.html`.
- `robots.txt` rewritten: `Disallow` for all admin/portal/login pages + `/api/`; `Sitemap: https://pariscomedy.com/sitemap.xml` retained.
- Generator: `scripts/generate_sitemap.py` (stdlib only). Reads `data/freshness-audit.json` so daily freshness wrapper can keep sitemap fresh.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P4_SITEMAP_1_SITEMAP_GENERATOR.md`.

## 2026-05-29 | infra | PROCESS.ROOT.1
- Added `scripts/regression_guard.py` — stdlib-only Python 3 guard that runs 9 live-production checks against pariscomedy.com: forbidden-strings (bilingual/mixed-language/marketing-claim leakage), internal-CTAs (/venues.html → /show.html, no external bypass), raw-includes (no unprocessed `<!-- include: -->`), stale-homepage-panel (next3-row populated or explicit empty msg), card-render (/comedians.html + /shows.html non-zero), status-sweep (31 named public URLs return 200), nav-consistency (one `nav-shell-*` per page), freshness-sanity (/data/freshness-audit.json parses, zero stale rows), hreflang (3 alternates per legal page × EN+FR).
- Single check via `--check <name>`; optional Playwright DOM probes via `--with-dom`. JSON evidence written to `logs/regression-guard.<ISO>.json` (gitignored).
- CI: `.github/workflows/regression-guard.yml` runs the guard on push + PR to `main`.
- Doc: `chuck_vault/10-concepts/projects/pariscomedy-canonical/PROCESS_ROOT_1_REGRESSION_GUARD.md` (check rationale + add-a-check procedure).
- First live run (2026-05-29): 8/9 PASS. `nav_consistency` legitimately flagged 3 legacy bare-`<nav>` pages (`/disclosure.html`, `/show.html`, `/show-runner.html`) that haven't been migrated to `nav-shell-*` partials — real drift, deferred fix.

## 2026-05-29 | data | P1.SOURCE.2
- Scaffolded FNAC Spectacles, Fever, and Weezevent adapters under `scripts/adapter_{fnac,fever,weezevent}.py` following the BilletRéduc pattern. All stubs raise `NotImplementedError("<Platform> adapter — pending operator authorization")`; no network, no parsing, no imports of listings. `data/source-adapters.json` updated: `fnac_spectacles`, `weezevent` flipped none→scaffolded; new `fever` entry added scaffolded; all `enabled: false`. Other platforms untouched. Gate-unlock procedure in `chuck_vault/10-concepts/projects/pariscomedy-canonical/P1_SOURCE_2_DRY_RUN_ADAPTERS.md`. Stub-raises proof captured in vault doc.

## 2026-05-29 | frontend | SHOWS.DEFAULT.1
- `/shows.html` now lands on today's shows first (Paris TZ) instead of "All". New "Today" chip prepended to filter row, default-active; "All" chip moved to end of row. Contextual banner above grid: "Showing tonight's shows — {day} {date}" with a "See all shows" link. Fallback: if today has no shows, walks forward up to 7 days to next available day with appropriate banner copy. `.checked-badge` (P1.DATA.4) preserved. shows.html: 20,321 → 22,661 bytes. Commit `2eedcda`. Verified: initial active chip = "Today" → Friday; 6 of 34 cards visible until "All" clicked.

## 2026-05-29 | frontend | P1.COMPLIANCE.3
- Added French-language mirrors of 3 legal pages: `fr/terms.html`, `fr/privacy.html`, `fr/disclosure.html`. Each fully French, `<html lang="fr">`, French title/meta/og, robots index+follow.
- Added `<link rel="alternate" hreflang="en|fr|x-default">` triplet to all 6 pages (3 EN + 3 FR) for proper SEO cross-linking.
- Added small "Français" / "English" toggle link at top of `<main>`/`<div class="wrap">` of each of the 6 pages. No language-toggle widget on any other page.
- Brand "Paris Comedy" preserved; `payments@pariscomedy.com` preserved; EN-only URLs (`/shows.html`, etc.) preserved. No bilingual/bilingue/mixed-language/multilingual wording in any of the 6 pages.

## 2026-05-29 | frontend | P1.COMPLIANCE.2
- Added `partials/consent.banner.html` — self-contained EN+FR minimal-storage consent banner (HTML + scoped CSS + IIFE JS, zero deps, zero network).
- Embedded inline into `index.html`, `shows.html`, `comedians.html` (49 lines each).
- localStorage key `pc-consent-v1` with `accepted` | `declined`. Verified via Playwright: appear → click OK → hide → reload persists.

## 2026-05-29 | doctrine | CSS-LANG-001
- Scrubbed dead `.badge-bilingual{...}` CSS selector from 227 static comedian pages under `c/`.
- Also removed residual "bilingual" body/meta text in 8 comedian bios (julie-coulon, julie-haddad-kan, lorene-cadeau, patti-mansbach, rey-mendes, robert-le-ricain, sebastian-marx, tania-dutel).
- Sitewide grep for `bilingual|mixed-language` under `c/` returns 0. `.badge-en` + `.badge-fr` preserved.

## 2026-05-29 | frontend | P5.HUD.1
- Added `/status.html` — single-page operator HUD. Robots noindex, admin nav shell, auto-refresh 60s. Renders: (1) freshness summary from `/data/freshness-audit.json` (total + by-status metrics + per-listing color-coded table); (2) source adapter status from `/data/source-adapters.json`; (3) live page-health probe of 27 public URLs with `{cache:'no-store'}` fetch; (4) doctrine forbidden-string scan over `/`, `/shows.html`, `/comedians.html`; (5) phase ledger summary. Zero deps, inline CSS+JS. Added `status.html` to `EXCLUDED_PAGES` in `scripts/generate_sitemap.py` and regenerated `sitemap.xml` (15 URLs, status.html absent). Operator-only — not linked from any public nav; bookmark to access.
