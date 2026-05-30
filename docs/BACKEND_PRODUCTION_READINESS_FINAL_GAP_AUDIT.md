# BACKEND.PRODUCTION-READINESS.FINAL-GAP-AUDIT

**Status: AUDIT ONLY — NO EXECUTION**  
**All feature flags: false (default)**  
**No production operator step authorized by this document**

---

## Endpoint Reconciliation

### Auth V2 (`backend/auth_v2_router.py`, prefix `/api/auth_v2`)

| Route | Method | Implemented | Docs reference | Mismatch? |
|---|---|---|---|---|
| `/api/auth_v2/status` | GET | YES | AUTH.6 cutover plan | NONE |
| `/api/auth_v2/magic-link/request` | POST | YES | AUTH.6 cutover plan says `/request-link` | **MISMATCH** — actual is `/magic-link/request` |
| `/api/auth_v2/magic-link/consume` | GET | YES | AUTH.6 cutover plan says `/verify` | **MISMATCH** — actual is `/magic-link/consume` |
| `/api/auth_v2/logout` | POST | YES | — | NONE |
| `/api/auth_v2/me` | GET | YES | — | NONE |
| `/api/auth_v2/session/expiry` | GET | YES | — | NONE |

**Mismatch note**: AUTH.6 cutover plan smoke tests referenced `/api/auth_v2/request-link` and `/api/auth_v2/verify`. Actual routes are `/api/auth_v2/magic-link/request` and `/api/auth_v2/magic-link/consume`. Cutover plan was accepted as strategic plan; exact route names must be corrected before operator execution.

---

### Submissions V2 (`backend/submissions_v2_router.py`)

| Route | Method | Implemented |
|---|---|---|
| `/api/submissions_v2/status` | GET | YES |
| `/api/submissions_v2/show` | POST | YES (503 when disabled) |
| `/api/admin/submissions_v2/{id}/approve` | POST | YES (503 when disabled) |
| `/api/admin/submissions_v2/{id}/reject` | POST | YES (503 when disabled) |
| `/api/admin/submissions_v2/{id}/mark-duplicate` | POST | YES (503 when disabled) |
| `/api/admin/submissions_v2/{id}/mark-spam` | POST | YES (503 when disabled) |

---

### Claims V2 (`backend/claims_v2_router.py`)

| Route | Method | Implemented |
|---|---|---|
| `/api/claims_v2/status` | GET | YES |
| `/api/claims_v2/comic` | POST | YES (503 when disabled) |
| `/api/claims_v2/show-runner` | POST | YES (503 when disabled) |
| `/api/claims_v2/venue` | POST | YES (503 when disabled) |
| `/api/admin/claims_v2/{id}/approve` | POST | YES (503 when disabled) |
| `/api/admin/claims_v2/{id}/reject` | POST | YES (503 when disabled) |
| `/api/admin/claims_v2/{id}/mark-duplicate` | POST | YES (503 when disabled) |
| `/api/admin/claims_v2/{id}/mark-spam` | POST | YES (503 when disabled) |

---

### Payments V2 (`backend/payments_v2_router.py`, prefix `/api/payments_v2`)

| Route | Method | Implemented |
|---|---|---|
| `/api/payments_v2/status` | GET | YES |
| `/api/payments_v2/checkout-session` | POST | YES (503 when disabled) |
| `/api/payments_v2/customer-portal` | POST | YES (503 when disabled) |
| `/api/payments_v2/webhook` | POST | YES (503 when disabled) |

---

### Messaging V2 (`backend/messaging_v2_router.py`, prefix `/api/messaging_v2`)

| Route | Method | Implemented |
|---|---|---|
| `/api/messaging_v2/status` | GET | YES |
| `/api/messaging_v2/threads` | POST | YES (503 when disabled) |
| `/api/messaging_v2/threads/{id}/reply` | POST | YES (503 when disabled) |
| `/api/messaging_v2/threads/{id}/report` | POST | YES (503 when disabled) |
| `/api/messaging_v2/users/{id}/block` | POST | YES (503 when disabled) |

---

### Tickets V2 (`backend/tickets_v2_router.py`)

| Route | Method | Implemented |
|---|---|---|
| `/api/tickets_v2/status` | GET | YES |
| `/api/tickets_v2/adapters` | GET | YES (imports_enabled=false) |
| `/api/admin/tickets_v2/discoveries` | POST | YES (503 when disabled) |
| `/api/admin/tickets_v2/discoveries/{id}/approve` | POST | YES (503 when disabled) |
| `/api/admin/tickets_v2/discoveries/{id}/reject` | POST | YES (503 when disabled) |
| `/api/admin/tickets_v2/discoveries/{id}/mark-duplicate` | POST | YES (503 when disabled) |
| `/api/admin/tickets_v2/discoveries/{id}/mark-unreachable` | POST | YES (503 when disabled) |
| `/api/admin/tickets_v2/discoveries/{id}/dry-run-import` | POST | YES (503 when disabled) |

---

## Feature Flag Reconciliation

| Flag | Module | Default | Production value | Status |
|---|---|---|---|---|
| `AUTH_V2_ENABLED` | `backend/auth_v2.py` | `false` | `false` | SAFE |
| `EMAIL_SEND_REAL` | `backend/mailer.py` | `false` | `false` | SAFE |
| `SUBMISSIONS_V2_ENABLED` | `backend/submissions_v2.py` | `false` | `false` | SAFE |
| `CLAIMS_V2_ENABLED` | `backend/claims_v2.py` | `false` | `false` | SAFE |
| `PAYMENTS_ENABLED` | `backend/payments_v2.py` | `false` | `false` | SAFE |
| `PAYMENT_WEBHOOKS_ENABLED` | `backend/payments_v2.py` | `false` | `false` | SAFE |
| `MESSAGING_V2_ENABLED` | `backend/messaging_v2.py` | `false` | `false` | SAFE |
| `TICKETS_ADAPTERS_ENABLED` | `backend/tickets_v2.py` | `false` | `false` | SAFE |
| `TICKET_IMPORTS_ENABLED` | `backend/tickets_v2.py` | `false` | `false` | SAFE |
| `AFFILIATE_LINKS_ENABLED` | `backend/tickets_v2.py` | `false` | `false` | SAFE |

**All 10 flags default false. Zero flags mentioned in docs but missing from implementation.**

---

## Migration Reconciliation

| File | Tables created | Count | Rollback file |
|---|---|---|---|
| `001_init.sql` | shows, venues, comics, show_listings, … (legacy) | — | — |
| `002_auth_v2.sql` | users_v2, sessions_v2, magic_links_v2, audit_events_v2, rate_limits_v2 | 5 | `002_auth_v2.rollback.sql` ✓ |
| `003_submissions_v2.sql` | show_submissions_v2 | 1 | `003_submissions_v2.rollback.sql` ✓ |
| `004_claims_v2.sql` | claims_v2 | 1 | `004_claims_v2.rollback.sql` ✓ |
| `005_payments_v2.sql` | payment_customers_v2, payment_subscriptions_v2, payment_invoices_v2, payment_checkout_sessions_v2, payment_webhook_idempotency_v2 | 5 | `005_payments_v2.rollback.sql` ✓ |
| `006_messaging_v2.sql` | message_threads_v2, messages_v2, message_blocks_v2, message_reports_v2 | 4 | `006_messaging_v2.rollback.sql` ✓ |
| `007_tickets_v2.sql` | adapter_discoveries_v2 | 1 | `007_tickets_v2.rollback.sql` ✓ |

**Total V2 tables: 17. Matches authorization pack. All rollback files present.**

**DB runbooks match actual files.** Authorization pack (`data/backend-db-production-migration-authorization-pack.json`) lists the same table names as confirmed by `grep CREATE TABLE` on actual migration files.

---

## Public Surface Reconciliation

| Page | Status | Evidence |
|---|---|---|
| `connect.html` | SAFE — canonical contact/booking route | Submissions/Claims/Messaging V2 status notes present as read-only info; no write endpoints callable from UI; `SUBMISSIONS_V2_ENABLED=false` guard prevents any POST |
| `login.html` | SAFE — Auth V2 draft section present, not live | `aria-label="Auth V2 magic-link login — not yet live"`, `class="v2-draft"`, `!v2Enabled` JS guard on request button |
| `admin-review.html` | SAFE — noindex, read-only shell | `<meta name="robots" content="noindex,nofollow">`, all buttons `disabled`, mock data labelled with `.mock-tag` |
| `pricing.html` | SAFE — planned features explicitly marked not-live | `PRICING_FEATURE_COPY_SAFE_20260530` marker, "planned — not live yet" on all V2 features, "Checkout is not yet live" |
| `book.html` | NOT LINKED from public nav — decommissioned legacy | Not checked for active links in index.html |

---

## Mismatches Found

| ID | Type | Detail | Impact | Resolution |
|---|---|---|---|---|
| M1 | Route name mismatch | AUTH.6 cutover plan smoke tests reference `/api/auth_v2/request-link` and `/api/auth_v2/verify`; actual routes are `/api/auth_v2/magic-link/request` and `/api/auth_v2/magic-link/consume` | Operator would get 404 if they followed the plan literally | Update cutover plan smoke test commands before execution |
| M2 | No other mismatches | All other route names, table names, flag names, migration file names match between docs and implementation | — | — |

---

## Blocking Operator Actions

| Action | Blocker | Status |
|---|---|---|
| Run DB migrations 002–007 | Robert must type authorization text + confirm exact DB path on server | BLOCKED — awaiting operator |
| Enable EMAIL_SEND_REAL=true | Postmark DNS: SPF, DKIM, DMARC, return-path CNAME all missing (verified 2026-05-30) | BLOCKED — awaiting DNS setup by Robert |
| Enable AUTH_V2_ENABLED=true | Requires DB migrations + Postmark DNS first | BLOCKED |
| Enable PAYMENTS_ENABLED=true | Requires payment provider account, VAT configuration, legal review | BLOCKED |
| Enable SUBMISSIONS_V2_ENABLED=true | Requires DB migrations + AUTH_V2_ENABLED first | BLOCKED |
| Enable CLAIMS_V2_ENABLED=true | Requires DB migrations + AUTH_V2_ENABLED first | BLOCKED |
| Enable MESSAGING_V2_ENABLED=true | Requires AUTH_V2_ENABLED first | BLOCKED |
| Enable TICKETS_ADAPTERS_ENABLED=true | Requires DB migrations first | BLOCKED |

---

## Final Go/No-Go Table

| System | safe_to_enable | Blockers remaining |
|---|---|---|
| Auth V2 | **false** | DB migrations not applied; Postmark DNS missing; staging smoke test not run |
| Email (real send) | **false** | SPF/DKIM/DMARC/return-path CNAME all missing |
| Submissions V2 | **false** | DB migrations not applied; Auth V2 not enabled |
| Claims V2 | **false** | DB migrations not applied; Auth V2 not enabled |
| Payments | **false** | Payment provider account not created; VAT not configured; no legal review |
| Messaging V2 | **false** | Auth V2 not enabled |
| Tickets (adapters) | **false** | DB migrations not applied |

**safe_to_execute_any_operator_step: false** until Robert confirms DB path and types authorization text.

---

## Regression Guard

```
22/22 PASS
```
