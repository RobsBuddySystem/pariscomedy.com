# BACKEND_IMPLEMENTATION_SEQUENCE — execution order for backend phases

**Status:** PLAN ONLY. Mandated sequence from ChatGPT BACKEND.PLAN.1 verdict.
**Companion:** `docs/BACKEND_PLAN_1.md`.

Each phase below ships independently; no phase may merge until its predecessor is `CLOSED_BY_CHATGPT`.

---

## 1. BACKEND.AUTH.1 — auth foundation

**Why first:** Every other backend phase requires an authenticated `user_id`. Building anything else first would force later rework.

**Deliverables:**
- Migration: users, sessions, magic_links, audit_events, rate_limits
- Endpoints: `/auth/magic-link/request`, `/auth/magic-link/consume`, `/auth/logout`, `/auth/me`, `/auth/session/expiry`, `/auth/password/login` (admin only)
- Cookie issuance + CSRF cookie pair
- Audit event emission on every auth action
- Resolves: R-01, R-02, R-03, R-15 (partial), R-16, R-17, R-18; OD-01, OD-02, OD-04, OD-08

**Exit criteria for ChatGPT closure:**
- Live magic-link round-trip from a fresh email
- Session persists across page reloads
- Logout actually revokes (regression test: protected endpoint returns 401 after logout)
- Audit events visible in admin endpoint
- Rate-limiter blocks 11th magic-link request from same email in 1h

**Estimated effort:** medium (1 week of focused work)

---

## 2. BACKEND.SUBMIT.1 — public show submissions + admin queue

**Why second:** Lets community + Robert grow listings without manual DB inserts. Depends on auth for `reviewed_by` field.

**Deliverables:**
- Migration: show_submissions
- Endpoints: `POST /submissions/show`, `GET /admin/submissions`, `POST /admin/submissions/{id}/{approve|reject}`
- Inline source-URL verifier call (reuse `scripts/freshness_verify.py` logic in-process)
- Honeypot + Cloudflare Turnstile
- Decision email via Postmark
- Resolves: R-04, R-05

**Exit criteria:** public submission flows through to listings table on admin approve; rejected submission triggers email; spam attempts hit Turnstile or honeypot.

**Estimated effort:** small-medium (3-5 days)

---

## 3. BACKEND.CLAIM.1 — claim flows (comic/show-runner/venue)

**Why third:** Unblocks comic + venue user identity. Depends on auth.

**Deliverables:**
- Migration: claims (single table covers all 3 types)
- Endpoints: `POST /claims/{comic|show-runner|venue}`, `GET /admin/claims`, `POST /admin/claims/{id}/{approve|reject}`, `GET /api/{comics|listings|venues}/{id}/claim-status`
- Two-of-three evidence gate auto-approval; admin override otherwise
- Write-back to target table on approval
- Public badge endpoint
- Resolves: R-06

**Exit criteria:** end-to-end claim with Instagram + recent-post + domain-email auto-approves; badge appears only on `verified`; rejected claim emails reason.

**Estimated effort:** small-medium

---

## 4. BACKEND.EMAIL.1 — transactional email + domain auth

**Why fourth:** Auth + submissions + claims all rely on email already (sent via Postmark from day 1 of those phases), but DNS + DMARC + inbound parsing is its own phase to avoid blocking the above. Schedule allows email to mature before payments hit it.

**Deliverables:**
- DNS: SPF, DKIM (Postmark selector), DMARC `p=quarantine` initially
- Postmark inbound webhook to parse thread-replies (`POST /webhooks/postmark/inbound`)
- Email template library (welcome, magic-link, submission decision, claim decision)
- Bounce + complaint webhook handler → user flag `users.bounced_at`
- Resolves: R-10, R-11

**Exit criteria:** mail-tester.com score ≥ 9/10; DMARC reports clean for 30 days; inbound reply-to-thread appends to messages table.

**Estimated effort:** small (2-3 days of mostly DNS + Postmark setup)

---

## 5. BACKEND.PAYMENTS.1 — Stripe subscriptions + webhooks

**Why fifth:** Email + auth must be solid before charging anyone. Powers messaging gate (next).

**Deliverables:**
- Migration: stripe_customers, subscriptions, invoices, webhook_events_idempotency
- Endpoints: `POST /billing/checkout-session`, `POST /billing/customer-portal`, `POST /api/stripe/webhook`, `GET /billing/subscriptions`, `GET /api/invoices`
- Stripe Tax enabled
- Refund policy + cancel-anytime in customer portal
- Updated `/pricing.html` + `/disclosure.html` + `/conditions-generales.html`
- Resolves: R-08, R-09, R-20; OD-06, OD-07

**Exit criteria:** test card subscribes to comic_plus → DB row + invoice + webhook idempotent on replay; customer portal cancellation reflects in DB within 5s; legal pages reviewed.

**Estimated effort:** medium (~1 week, dominated by Stripe Tax + legal review)

---

## 6. BACKEND.MESSAGING.1 — gated comic↔booker messaging

**Why sixth:** Depends on auth + payments (subscription gate) + email (notification rules).

**Deliverables:**
- Migration: message_threads, messages, message_blocks, message_reports
- Endpoints: `GET /messages/threads`, `GET /messages/threads/{id}`, `POST /messages/{new,threads/{id}/reply}`, `POST /messages/threads/{id}/{report,block}`
- Subscription gate: send-message requires `users.plan IN ('comic_plus','booker_plus')`
- Daily cap 20 distinct recipients
- Email-on-no-reply within 1h, one-click unsubscribe per thread
- 90-day soft-hide; 24-month hard-delete with RGPD export
- Resolves: R-07, R-19; OD-05

**Exit criteria:** unpaid user cannot send; paid user can; abuse report lands in admin queue; data-export returns full message body for current user only.

**Estimated effort:** medium

---

## 7. BACKEND.TICKETS.1 — multi-platform adapter review pipeline

**Why last:** Lowest user-facing risk (admin-gated). Existing read-only Eventbrite freshness covers the main use case; this adds discovery + import for the other 7+ platforms.

**Deliverables:**
- Migration: adapter_discoveries, adapter_affiliate_ids
- Admin endpoints: `GET /admin/adapters/discovered`, `POST /admin/adapters/discovered/{id}/{import,reject}`
- One per-platform scraper (BilletRéduc, FNAC, Fever, Weezevent first; others deferred to BACKEND.TICKETS.2)
- Per-adapter unit test against snapshot fixtures
- Static regression: `affiliate_id` may never be public-exported when `enabled=false`
- Resolves: R-12, R-13

**Exit criteria:** discover script populates adapter_discoveries; admin reviews + imports one row → listing appears + freshness verifier runs; affiliate disabled until ChatGPT + Robert approve.

**Estimated effort:** medium-large (each adapter is its own small project)

---

## Sequencing rationale recap

1. Auth → unblocks user_id everywhere
2. Submit → unblocks growth without manual DB
3. Claim → unblocks identity badges
4. Email → matures deliverability before payments
5. Payments → unblocks messaging gate + revenue
6. Messaging → unblocks comic↔booker, depends on all four above
7. Tickets → admin-gated, lowest user-facing risk, can run in parallel with messaging if capacity allows

## Cross-references

- [[BACKEND_PLAN_1]]
- [[API_CONTRACT_DRAFT]]
- [[DB_SCHEMA_DRAFT]]
- [[BACKEND_RISK_REGISTER]]
- [[PHASE_LEDGER]]
