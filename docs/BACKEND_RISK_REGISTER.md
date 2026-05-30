# BACKEND_RISK_REGISTER — pariscomedy.com backend plan risks + open decisions

**Status:** living document. Updated each time a BACKEND.* phase resolves or defers a risk.
**Companion:** `docs/BACKEND_PLAN_1.md`.

Risk severity key: **P0** (blocker — must resolve before launch), **P1** (resolve before public claim of feature), **P2** (operational risk — can ship behind a flag), **P3** (nice-to-have).

## Open decisions (resolve in the named phase)

| ID | Decision | Owner phase | Default if no decision | Risk |
|---|---|---|---|---|
| OD-01 | Hosting target for backend (Cloudflare Workers / Hetzner VM / Render) | BACKEND.AUTH.1 first sub-RFC | Cloudflare Workers + D1 (zero-ops, fits existing CF Pages stack) | P1 — wrong choice forces rewrite at scale |
| OD-02 | Database engine | BACKEND.AUTH.1 | Postgres (Neon free tier) — broader ecosystem | P2 — D1/SQLite-Turso also viable |
| OD-03 | Postmark vs SES vs Resend pricing | BACKEND.EMAIL.1 | Postmark (best deliverability, EU residency option) | P2 — provider swap is bounded |
| OD-04 | Admin password recovery flow (or magic-link only) | BACKEND.AUTH.1 | Magic-link only; no password reset | P3 — one admin user; bypass via DB if locked out |
| OD-05 | Message body retention (24mo hard delete vs only metadata) | BACKEND.MESSAGING.1 | Hard-delete body after 24mo, keep metadata for fraud audit 7y | P1 — RGPD compliance |
| OD-06 | Stripe vs SumUp for online subscriptions | BACKEND.PAYMENTS.1 | Stripe (already drafted in plan) | P2 — SumUp lacks subscription primitives |
| OD-07 | EU VAT registration threshold + invoicing | BACKEND.PAYMENTS.1 + legal | Stripe Tax (auto-collect) | P0 — illegal collection if mis-handled |
| OD-08 | RGPD lawful basis per data category | BACKEND.AUTH.1 + legal | Consent for messaging body; legitimate interest for audit logs | P0 |
| OD-09 | Whether to ship 2FA for admin in v1 | BACKEND.AUTH.1 | Defer; magic-link + IP allowlist for admin path | P2 |
| OD-10 | File uploads for claim evidence (S3-compatible) | BACKEND.CLAIM.2 | URL evidence only in v1 | P3 |

## Active risks

| ID | Risk | Severity | Mitigation | Owner phase |
|---|---|---|---|---|
| R-01 | Magic-link enumeration via timing/email-exists feedback | P1 | Always return 204; constant-time response | BACKEND.AUTH.1 |
| R-02 | Replay attack on consumed magic links | P0 | Token single-use; hash before storage; DB UNIQUE on token_hash | BACKEND.AUTH.1 |
| R-03 | Session fixation across logout | P1 | Logout revokes DB row AND rotates cookie | BACKEND.AUTH.1 |
| R-04 | Spam submissions overwhelming admin queue | P1 | Honeypot + Cloudflare Turnstile + per-email/per-IP throttle | BACKEND.SUBMIT.1 |
| R-05 | False-positive duplicate submissions blocking legitimate listings | P2 | "duplicate" status is reversible by admin | BACKEND.SUBMIT.1 |
| R-06 | Claim approval to wrong user (impersonation) | P0 | Require ≥ 2 of 3 evidence types (Instagram + recent-post URL + domain-email-match) for first-tier auto-approval; admin manual review otherwise | BACKEND.CLAIM.1 |
| R-07 | Messaging spam at scale | P1 | Daily cap 20 distinct recipients; rate-limit per-thread reply 60s; block list per user | BACKEND.MESSAGING.1 |
| R-08 | Stripe webhook replay → duplicate state change | P0 | `webhook_events_idempotency` table; reject if event.id seen | BACKEND.PAYMENTS.1 |
| R-09 | TVA/VAT mishandled on EU subscribers | P0 | Stripe Tax; legal review before first charge | BACKEND.PAYMENTS.1 |
| R-10 | Email deliverability collapse from DMARC misconfig | P0 | Start `p=quarantine` 30d, monitor rua reports, then `p=reject` | BACKEND.EMAIL.1 |
| R-11 | Cloudflare Email Routing forwarding loop / SPF break | P1 | Verify SPF includes both `_spf.mx.cloudflare.net` AND outbound provider | BACKEND.EMAIL.1 |
| R-12 | Adapter scrape breaks under platform UI changes | P1 | Per-adapter unit test against snapshot HTML in tests/fixtures/; alert on failure | BACKEND.TICKETS.1 |
| R-13 | Affiliate referral leak before network approval | P1 | `adapter_affiliate_ids.enabled` default FALSE; static check in regression_guard | BACKEND.TICKETS.1 |
| R-14 | Cloudflare cache serving stale show.html / freshness JSON to crawlers | P2 | Already mitigated by P1.DATA.3B + cache-bust convention; consider lower max-age for HTML | BACKEND.EMAIL.1 follow-up |
| R-15 | RGPD data export must return ALL user-linked rows | P0 | Generated via single source-of-truth function used by both export and delete | BACKEND.AUTH.1 + BACKEND.MESSAGING.1 |
| R-16 | Backup + point-in-time restore strategy | P1 | Neon PITR retention 7d on free tier; manual daily logical dump to encrypted offsite | BACKEND.AUTH.1 |
| R-17 | Secrets management (Stripe keys, Postmark token) | P0 | Cloudflare Workers env vars + secrets binding; never in repo; rotate quarterly | BACKEND.AUTH.1 |
| R-18 | CSRF on cookie auth endpoints | P0 | `pc_csrf` cookie + `X-CSRF-Token` header check | BACKEND.AUTH.1 |
| R-19 | Cross-tenant data leak in messaging | P0 | Every read scopes by `participant_a OR participant_b == current_user_id` | BACKEND.MESSAGING.1 |
| R-20 | Refund disputes (chargebacks) eroding margin | P2 | Clear refund policy on `/conditions-generales.html`; auto-refund within 14d window | BACKEND.PAYMENTS.1 |

## Resolved risks (archive — append on close)

(none yet)

## Cross-references

- [[BACKEND_PLAN_1]]
- [[API_CONTRACT_DRAFT]]
- [[DB_SCHEMA_DRAFT]]
- [[BACKEND_IMPLEMENTATION_SEQUENCE]]
- [[PHASE_LEDGER]]
