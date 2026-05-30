# BACKEND_PLAN_1 — pariscomedy.com backend implementation plan

**Status:** PLAN ONLY. No code change. No production behavior change.
**Authorized:** ChatGPT 2026-05-30 — BACKEND.PLAN.1
**Companion:** `data/backend-plan.json` (machine-readable mirror).
**Sequenced phases:** `docs/BACKEND_IMPLEMENTATION_SEQUENCE.md`.

## Scope

Plan the backend requirements for seven product areas: Auth, Show Submissions, Claim flows, Messaging, Payments, Ticket adapters, Email/domain. For each item: classify, identify blockers, name the eventual phase id that will implement it.

## Item classification key

- **frontend-only** — entirely client-side, no API or DB change required
- **backend-required** — API endpoint / handler work required
- **database-required** — schema change or new table required
- **email-required** — transactional or inbound email pathway required
- **payment-provider-required** — Stripe / SumUp / similar integration required
- **admin-review-required** — human moderation queue required before public effect
- **legal/compliance-required** — disclosure, ToS, RGPD, or consent change required
- **blocked** — depends on another item not yet built
- **ready-to-build** — design complete, implementation can begin now

## 1. Auth

| Item | Classification | Eventual phase | Notes |
|---|---|---|---|
| Magic-link login (comic + booker + admin) | backend-required, email-required, ready-to-build | BACKEND.AUTH.1 | Tokens single-use + ≤15 min TTL, signed JWT in HttpOnly cookie. |
| Password login (admin only) | backend-required, database-required | BACKEND.AUTH.1 | Argon2id, no recovery flow yet (use magic link). |
| Session persistence | backend-required | BACKEND.AUTH.1 | Cookie `pc_session` HttpOnly + Secure + SameSite=Lax, 14-day rolling TTL. |
| Old-token invalidation | backend-required, database-required | BACKEND.AUTH.1 | `sessions` table; logout deletes row; `sessions.revoked_at` flag. |
| Logout / clear cookies | backend-required | BACKEND.AUTH.1 | Single POST endpoint clears `pc_session` + revokes DB row. |
| Comic account | database-required, backend-required | BACKEND.AUTH.1 | `users` row + `comic_profiles` link. |
| Booker account | database-required, backend-required | BACKEND.AUTH.1 | `users` row + `booker_profiles` link. |
| Admin account | database-required, backend-required | BACKEND.AUTH.1 | `users.role = 'admin'`; provisioned via CLI, no public signup. |
| Token expiry visible to user | backend-required, frontend-only (display) | BACKEND.AUTH.1 | Header `x-pc-token-expires-at`; client re-issues warning ≤2 min. |
| Rate limits on auth endpoints | backend-required | BACKEND.AUTH.1 | 10 magic-link requests/email/hour; 30 logins/IP/hour. Cloudflare WAF first line. |
| Audit log for auth events | database-required, backend-required | BACKEND.AUTH.1 | `audit_events` table; record login/logout/magic-link-issue/revoke. |

## 2. Show submissions

| Item | Classification | Eventual phase | Notes |
|---|---|---|---|
| Public submit form | frontend-only (UI already at `/submit-show.html` partial scaffold) | n/a | Already exists as UI, not wired. |
| Anti-spam + honeypot | backend-required | BACKEND.SUBMIT.1 | Hidden field + `submitted_at`/server-time delta + Cloudflare Turnstile. |
| Moderation queue | database-required, backend-required, admin-review-required | BACKEND.SUBMIT.1 | `show_submissions` table with `status` enum: pending / approved / rejected / spam / duplicate. |
| Status states (per-submission) | database-required | BACKEND.SUBMIT.1 | Above enum + `reviewed_by_user_id`, `reviewed_at`, `reviewer_notes`. |
| Source-URL validation | backend-required | BACKEND.SUBMIT.1 | On submit, server fetches the URL, runs P1.DATA.2.FIX verifier inline; rejects if HTTP ≠ 200 or ended-badge detected. |
| Freshness verification hook | backend-required | BACKEND.SUBMIT.1 | On approval, server adds the submission to `listings` and triggers a one-off freshness_verify run for that slug. |
| Admin approve/reject flow | backend-required, admin-review-required, email-required | BACKEND.SUBMIT.1 | Endpoint `POST /admin/submissions/{id}/approve` / `…/reject`; sends decision email to submitter. |

## 3. Claim flows (comic / show-runner / venue-booker)

| Item | Classification | Eventual phase | Notes |
|---|---|---|---|
| Comic claim | database-required, backend-required, admin-review-required | BACKEND.CLAIM.1 | `comic_claims` table; ties `comic_profiles.id` to `users.id` after approval. |
| Show-runner claim | database-required, backend-required, admin-review-required | BACKEND.CLAIM.1 | Same shape, `show_runner_claims`. |
| Venue / booker claim | database-required, backend-required, admin-review-required | BACKEND.CLAIM.1 | `venue_claims` with venue_id FK. |
| Evidence upload / URL proof | backend-required, frontend-only (UI exists) | BACKEND.CLAIM.1 | Allow either (a) Instagram handle + recent-post URL OR (b) domain email match OR (c) admin invite. Already collected on the frontend per P3.CLAIM.2 + P3.CLAIM.3; backend needs to persist + verify. |
| Pending review status | database-required | BACKEND.CLAIM.1 | Same enum as submissions (pending/approved/rejected) per claim type. |
| Approved / rejected states | database-required | BACKEND.CLAIM.1 | On approve: write `comic_profiles.claimed_by_user_id`. On reject: keep audit row. |
| Fail-closed badges | frontend-only (already present), backend-required (badge source-of-truth API) | BACKEND.CLAIM.1 | `/api/comics/{slug}/claim-status` returns `verified / pending / none`; UI renders only `verified`. |

## 4. Messaging (comic ↔ booker)

| Item | Classification | Eventual phase | Notes |
|---|---|---|---|
| comic → booker | database-required, backend-required | BACKEND.MESSAGING.1 | `messages` table (sender_user_id, recipient_user_id, thread_id, body, sent_at). |
| booker → comic | same | BACKEND.MESSAGING.1 | Same table; symmetrical. |
| Abuse prevention | backend-required | BACKEND.MESSAGING.1 | Per-sender daily cap (20 outbound to distinct recipients) + report/block buttons + admin shadow view. |
| Subscription gate | payment-provider-required, backend-required, blocked-on-payments | BACKEND.MESSAGING.1 | Send-message endpoint checks `users.plan == 'comic_plus' OR 'booker_plus'`. |
| Email notification rules | email-required, backend-required | BACKEND.MESSAGING.1 | Recipient gets email if no unread reply within 1 hour; one-click unsubscribe per thread. |
| Data retention | legal/compliance-required, database-required | BACKEND.MESSAGING.1 | Hard delete after 24 months; soft-delete after 90 days hidden from UI. RGPD export endpoint returns full thread on request. |

## 5. Payments

| Item | Classification | Eventual phase | Notes |
|---|---|---|---|
| €1/mo comic plan | payment-provider-required, backend-required, legal/compliance-required | BACKEND.PAYMENTS.1 | Recurring subscription; provider-recommended: **Stripe** (TVA-handled, EU SCA, robust webhook tooling). |
| €1/mo booker plan | same | BACKEND.PAYMENTS.1 | Same provider/product. |
| Show highlight / promo products | payment-provider-required, backend-required, admin-review-required | BACKEND.PAYMENTS.1 | One-off purchase tied to a listing_id; admin can revoke. |
| Private-booking products | payment-provider-required, backend-required | BACKEND.PAYMENTS.1 | Treated as a separate SKU; not auto-renewing. |
| Refund / cancel path | payment-provider-required, backend-required | BACKEND.PAYMENTS.1 | Cancel from `/account/billing`; refund via admin only. |
| Invoice / receipt | legal/compliance-required, email-required | BACKEND.PAYMENTS.1 | Stripe auto-emails; we mirror to `invoices` table for our own search. |
| Disclosure / legal | legal/compliance-required | BACKEND.PAYMENTS.1 | Update `/pricing.html` + `/disclosure.html` + `/conditions-generales.html`. |
| Provider choice recommendation | n/a | n/a | **Stripe over SumUp**: Stripe Checkout + Customer Portal lowers integration cost; SumUp Online lacks robust subscription tooling; both can co-exist for in-person at venues later. |
| Backend webhook needs | backend-required | BACKEND.PAYMENTS.1 | Verified Stripe webhook signature, idempotency table, single endpoint `/api/stripe/webhook`. |

## 6. Ticket adapters

| Adapter | Status today | Phase | Notes |
|---|---|---|---|
| Eventbrite (current) | live freshness + repoint support (P1.DATA.2.FIX, P1.DATA.3.LITE) | n/a | Read-only verifier + repoint mapping. |
| Eventbrite (import) | scaffold only | BACKEND.TICKETS.1 | `scripts/discover_shows.py` already exists; backend adds admin "import discovered" endpoint with manual review queue. |
| BilletRéduc | scaffold only (`adapter_billetreduc.py`) | BACKEND.TICKETS.1 | Verify URL + parse next showtime; manual approval before public surface. |
| FNAC / France Billet | scaffold only (`adapter_fnac.py`) | BACKEND.TICKETS.1 | Same shape. |
| Fever | scaffold only (`adapter_fever.py`) | BACKEND.TICKETS.1 | Same. |
| Weezevent | scaffold only (`adapter_weezevent.py`) | BACKEND.TICKETS.1 | Same. |
| Others (Ticketmaster FR, See Tickets, Billetweb, Yurplan, HelloAsso, Shotgun, Dice) | not started | BACKEND.TICKETS.2 (deferred) | Add as needed, one PR per adapter, admin-review-required for first import. |
| Affiliate / referral IDs | data only — kept disabled per `feedback_strict_language_classification.md` standing rule | BACKEND.TICKETS.1 | Persist `affiliate_id` field per adapter but `enabled:false` until network confirms approval. |

## 7. Email + domain

| Item | Classification | Eventual phase | Notes |
|---|---|---|---|
| chuck@pariscomedy.com | already alias (per vault notes) | BACKEND.EMAIL.1 | Forwarding to Robert's inbox; keep as is. |
| payments@pariscomedy.com | aliased to Robert | BACKEND.EMAIL.1 | Becomes Stripe receipt reply-to. |
| support@pariscomedy.com | NEW | BACKEND.EMAIL.1 | Inbound to a shared mailbox + autoresponder. |
| Inbound provider | email-required | BACKEND.EMAIL.1 | Cloudflare Email Routing for forwarding; **Postmark** for inbound parsing if needed (e.g. reply-to-message threading). |
| Outbound transactional provider | email-required, legal/compliance-required | BACKEND.EMAIL.1 | **Postmark** recommended over SES (better deliverability, simpler templating, EU data residency option). Fallback: Resend. |
| SPF | DNS change | BACKEND.EMAIL.1 | `v=spf1 include:_spf.mx.cloudflare.net include:spf.mtasv.net -all` |
| DKIM | DNS change | BACKEND.EMAIL.1 | Postmark provides 2048-bit selector `pm._domainkey`. |
| DMARC | DNS change, legal/compliance-required | BACKEND.EMAIL.1 | Start `p=quarantine; rua=mailto:dmarc-reports@pariscomedy.com`; tighten to `p=reject` after 30 days clean. |
| Forwarding vs transactional sending | n/a | BACKEND.EMAIL.1 | Cloudflare Email Routing for HUMAN inbound; Postmark for outbound transactional + thread-reply parsing. |

## Cross-cutting concerns

- **RGPD / privacy**: every database-required item above carries an RGPD data-subject access path. Plan adds `/api/account/data-export` returning a single JSON blob per user. Hard-delete cascades respected.
- **Audit trail**: every admin write goes through `audit_events`.
- **Rate limiting**: Cloudflare WAF + per-endpoint Lua at the API layer; per-user caps in code.
- **Observability**: All API endpoints emit structured JSON logs; sample dashboards in `docs/OPERATIONAL_HUD_SPEC.md`.

## What this plan does NOT decide

- Concrete hosting provider for the backend (Cloudflare Workers vs Hetzner VM vs Render). Defer to BACKEND.AUTH.1 first sub-RFC.
- Database engine (Postgres vs Turso/SQLite). The schema in `docs/DB_SCHEMA_DRAFT.md` is engine-portable.
- The exact endpoint pricing for Postmark vs SES. Recorded as a TODO in `docs/BACKEND_RISK_REGISTER.md`.

## Related (bidirectional)

- [[data/backend-plan.json]] — machine-readable plan
- [[docs/API_CONTRACT_DRAFT.md]] — REST contract per area
- [[docs/DB_SCHEMA_DRAFT.md]] — engine-portable schema
- [[docs/BACKEND_RISK_REGISTER.md]] — known unknowns + decisions deferred
- [[docs/BACKEND_IMPLEMENTATION_SEQUENCE.md]] — execution order
- [[PHASE_LEDGER]] — phase tracking
