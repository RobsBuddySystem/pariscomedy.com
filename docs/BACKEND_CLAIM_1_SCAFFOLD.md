# BACKEND_CLAIM_1_SCAFFOLD

**Phase:** BACKEND.CLAIM.1-SCAFFOLD
**Authorized:** ChatGPT 2026-05-30
**Status:** scaffold + tests. No routes wired. No public ownership change. No email.

## Files

- `backend/migrations/004_claims_v2.sql` (+ rollback) — `claims_v2` table
- `backend/claims_v2.py` — service module
- `backend/tests/test_claims_v2.py` — 18 unit tests

## Claim types

`comic`, `show_runner`, `venue`

## States

`received → needs_review → approved (terminal) | rejected (terminal) | duplicate | spam`

## Service API

| Function | Returns | Notes |
|---|---|---|
| `create_claim_request(conn, data, ip=, user_agent=)` | `{id, status, created_at}` | Honeypot → spam; duplicate detect → duplicate; else needs_review |
| `validate_claim(data)` | `list[str]` problems | requires claim_type ∈ enum, email valid, target_id or target_slug, ≥1 evidence field, URL fields validate |
| `mark_claim_status(conn, id, new_status, reviewer=, notes=)` | bool | enforces transition matrix |
| `detect_duplicate_claim(conn, data)` | id or None | same type + target + email (non-terminal) |
| `list_pending_claims(conn)` | list[dict] | status ∈ {received, needs_review} |
| `claim_status_for_target(conn, claim_type, target_id_or_slug)` | `{status: "verified"\|"pending"\|"none"}` | **fail-closed**: only approved → verified |
| `status()` | dict | `{enabled, claim_types, allowed_statuses}` |

## Evidence model

At least ONE of these must be non-empty: `instagram_url`, `recent_post_url`, `domain_email`, `website_url`, `notes`. URL fields validated against `https?://…` regex. Rejects `javascript:` and other schemes.

## Public cutover status

NONE. No route added. `show.html` claim CTA still points at the existing `/book.html#show-runner` flow. No public ownership column on any other table is touched by this scaffold.

## Tests (18/18 PASS)

- Valid comic / show_runner / venue claim
- Missing email rejected
- Invalid email rejected
- Invalid claim_type rejected
- Missing target rejected
- No evidence rejected
- Invalid URL rejected (javascript:)
- Honeypot marks spam
- Duplicate detection
- Approve / reject transitions work
- Terminal cannot transition (approved → rejected blocked)
- list_pending returns only reviewable
- claim_status_for_target fail-closed (none → pending → verified → still none for rejected-only target)
- Audit events recorded
- No public ownership table touched

## What is still NOT live

- No `/api/claims/*` routes
- No admin claim review UI
- No email to claimant or reviewer
- Production DB migration NOT auto-applied
- `show.html` / `comedians.html` claim CTAs unchanged
- No ownership flag set on any other table

## Rollback

`git revert <commit-sha>` + optional `sqlite3 data/paris.db < backend/migrations/004_claims_v2.rollback.sql`.

## Related

- [[PHASE_LEDGER]]
- [[BACKEND_PLAN_1]]
- [[BACKEND_AUTH_1_SCAFFOLD]] — audit_events_v2 reused
- [[BACKEND_SUBMIT_1_SCAFFOLD]] — same scaffolding pattern
