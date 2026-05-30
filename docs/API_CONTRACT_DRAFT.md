# API_CONTRACT_DRAFT — pariscomedy.com backend endpoints

**Status:** DRAFT. Plan-only. Companion to `docs/BACKEND_PLAN_1.md`.

Conventions:
- Base URL: `https://api.pariscomedy.com`
- All requests/responses JSON (`Content-Type: application/json`)
- Auth via `pc_session` HttpOnly cookie (set by `/auth/*` endpoints)
- Errors: HTTP 4xx/5xx with `{"error": {"code": "...", "message": "..."}}`
- Pagination: `?cursor=<opaque>&limit=<N>` → `{"items": [...], "next_cursor": "..."}`
- All write endpoints require `X-CSRF-Token` header matching the cookie issued on session create

## Existing endpoints (no change)

- `GET /api/listings` — public list (already live, returns active listings + venue join)
- `GET /api/listings?featured=1` — promoted listings
- `GET /api/listings/{id}` — single listing detail (TBD if present today)

## New endpoints by area

### 1. Auth (BACKEND.AUTH.1)

| Method + Path | Body | Returns | Notes |
|---|---|---|---|
| `POST /auth/magic-link/request` | `{email}` | `204` | Rate-limited 10/email/hour. Always returns 204 to avoid email enumeration. |
| `GET /auth/magic-link/consume?token=…` | — | `302 → /account` + Set-Cookie | Token single-use, ≤15 min TTL. |
| `POST /auth/password/login` | `{email, password}` | `200 {user}` + Set-Cookie | Admin only; gated by `users.role`. |
| `POST /auth/logout` | — | `204` + Set-Cookie clearing | Revokes session DB row. |
| `GET /auth/me` | — | `{user}` or `401` | Used by client to detect session. |
| `GET /auth/session/expiry` | — | `{expires_at}` | Surfaced to UI countdown. |

### 2. Submissions (BACKEND.SUBMIT.1)

| Method + Path | Body | Returns | Notes |
|---|---|---|---|
| `POST /submissions/show` | `{name, venue_name, day_of_week, start_time, language, source_url, submitter_email, hp_field}` | `201 {submission_id}` | Honeypot field must be empty. Runs source-URL verifier inline; rejects if HTTP ≠200 or ended-badge detected. |
| `GET /admin/submissions` | — | `{items: [...]}` | Auth-required (admin). Filter by status. |
| `POST /admin/submissions/{id}/approve` | `{notes?}` | `200 {listing_id}` | Inserts into `listings`; triggers freshness verify. Sends email to submitter. |
| `POST /admin/submissions/{id}/reject` | `{reason}` | `200` | Sends email. |

### 3. Claims (BACKEND.CLAIM.1)

| Method + Path | Body | Returns | Notes |
|---|---|---|---|
| `POST /claims/comic` | `{comic_slug, instagram, recent_post_url, domain_email?}` | `201 {claim_id}` | Logged-in user implicit. |
| `POST /claims/show-runner` | `{listing_id, instagram, recent_post_url, domain_email?}` | `201` | Same. |
| `POST /claims/venue` | `{venue_id, evidence_url, domain_email?}` | `201` | Same. |
| `GET /admin/claims?type=comic\|show_runner\|venue` | — | `{items}` | Admin queue. |
| `POST /admin/claims/{id}/approve` | `{notes?}` | `200` | Sets `claimed_by_user_id` on target. |
| `POST /admin/claims/{id}/reject` | `{reason}` | `200` | Sends email. |
| `GET /api/comics/{slug}/claim-status` | — | `{status: "verified"\|"pending"\|"none"}` | Public; UI shows badge only on `verified`. |
| `GET /api/listings/{id}/claim-status` | — | same | Same shape. |

### 4. Messaging (BACKEND.MESSAGING.1)

| Method + Path | Body | Returns | Notes |
|---|---|---|---|
| `GET /messages/threads` | — | `{items}` | List threads for current user. |
| `GET /messages/threads/{id}` | — | `{thread, messages}` | Full thread. |
| `POST /messages/threads/{id}/reply` | `{body}` | `201 {message}` | Gated on `users.plan IN ('comic_plus','booker_plus')`. |
| `POST /messages/new` | `{recipient_user_id, body}` | `201 {thread_id, message_id}` | Same gate. Daily cap 20 distinct recipients. |
| `POST /messages/threads/{id}/report` | `{reason}` | `204` | Adds to admin abuse queue. |
| `POST /messages/threads/{id}/block` | — | `204` | Per-user block list. |

### 5. Payments (BACKEND.PAYMENTS.1)

| Method + Path | Body | Returns | Notes |
|---|---|---|---|
| `POST /billing/checkout-session` | `{plan: "comic_plus"\|"booker_plus", success_url, cancel_url}` | `200 {url}` | Returns Stripe Checkout URL. |
| `POST /billing/customer-portal` | `{return_url}` | `200 {url}` | Stripe Customer Portal. |
| `POST /api/stripe/webhook` | Stripe payload | `200` | Verify signature; idempotent on `event.id`. |
| `GET /billing/subscriptions` | — | `{items}` | Current user's subs. |
| `GET /api/invoices` | — | `{items}` | Current user. |

### 6. Ticket adapters (BACKEND.TICKETS.1)

Read-only public endpoints — no new public APIs needed. Backend admin endpoints:

| Method + Path | Body | Returns | Notes |
|---|---|---|---|
| `GET /admin/adapters/discovered` | — | `{items}` | Output of `scripts/discover_shows.py` queued for review. |
| `POST /admin/adapters/discovered/{id}/import` | `{venue_mapping}` | `201 {listing_id}` | Manual one-by-one import. |
| `POST /admin/adapters/discovered/{id}/reject` | `{reason}` | `200` | Skip. |

### 7. Email + RGPD (cross-cutting)

| Method + Path | Body | Returns | Notes |
|---|---|---|---|
| `POST /webhooks/postmark/inbound` | Postmark inbound JSON | `200` | Parses thread-reply-by-email → appends `messages` row. |
| `GET /api/account/data-export` | — | `200 {json blob}` | RGPD export, user-scoped. |
| `POST /api/account/delete` | `{confirm_email}` | `202` | Hard-delete cascade scheduled. |

## CSRF model

- Session cookie also issues `pc_csrf` cookie (readable by JS).
- All non-GET endpoints require `X-CSRF-Token: <pc_csrf value>`.
- Reject when header missing or mismatch.

## Error codes (catalog)

`auth/expired_token`, `auth/invalid_credentials`, `auth/rate_limited`,
`submissions/invalid_source_url`, `submissions/duplicate`,
`claims/insufficient_evidence`, `claims/already_claimed`,
`messaging/plan_required`, `messaging/recipient_blocked`, `messaging/daily_cap`,
`payments/checkout_failed`, `payments/webhook_signature_invalid`,
`adapters/host_unsupported`, `adapters/already_imported`,
`rgpd/already_pending`.

## Out of scope

- WebSocket / SSE — not in v1; polling on threads page is acceptable.
- File uploads — claims accept URL evidence only in v1; defer S3-compatible upload to BACKEND.CLAIM.2.

## Related
- [[BACKEND_PLAN_1]] — full plan
- [[DB_SCHEMA_DRAFT]] — table shapes
- [[BACKEND_RISK_REGISTER]] — open decisions
