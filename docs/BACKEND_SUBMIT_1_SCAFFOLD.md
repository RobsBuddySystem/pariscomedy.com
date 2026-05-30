# BACKEND_SUBMIT_1_SCAFFOLD

**Phase:** BACKEND.SUBMIT.1-SCAFFOLD
**Authorized:** ChatGPT 2026-05-30
**Status:** scaffold + tests. No public cutover. No real email. No auto-publish.

## Files

- `backend/migrations/003_submissions_v2.sql` (+ rollback) — `show_submissions_v2` table
- `backend/submissions_v2.py` — service module
- `backend/tests/test_submissions_v2.py` — 17 unit tests

## Service API

| Function | Returns | Notes |
|---|---|---|
| `create_show_submission(conn, data, ip=, user_agent=)` | `{id, status, created_at}` | Honors honeypot + duplicate detection; status ∈ {needs_review, spam, duplicate} |
| `validate_submission(data)` | `list[str]` problems (empty = ok) | required fields + email/url/language regex |
| `mark_submission_status(conn, id, new_status, reviewer=, notes=)` | bool | Enforces transition matrix |
| `detect_duplicate_submission(conn, data)` | submission id or None | same source_url + same email (non-terminal status) = duplicate |
| `list_pending_submissions(conn)` | list[dict] | status ∈ {received, needs_review} |
| `status()` | dict | `{enabled, allowed_statuses}` |

## Submission states

`received → needs_review → approved → imported`
`              ↘ rejected (terminal)`
`              ↘ duplicate (terminal)`
`              ↘ spam (terminal)`
`approved → rejected (still allowed)`

Invalid transitions raise `SubmissionError`.

## Required fields

`submitter_email`, `show_name`, `venue_name`, `source_url`. All others optional.

## Spam handling

If `honeypot` field is non-empty → `status='spam'` immediately, no review queue entry, `spam_signals = ["honeypot"]`.

## Duplicate detection

Same `source_url` + same `submitter_email` (case-insensitive, non-terminal status) → new submission gets `status='duplicate'` with `duplicate_of` pointing at the original id.

## Audit

Every create + transition writes an audit row to `audit_events_v2` (skipped silently if that table is not present in this DB).

## Public cutover status

NONE. No route wired. `book.html` is UNCHANGED. No submission appears publicly without explicit `imported` transition (which is admin-only and itself does NOT touch the public listings table — that integration lands in `BACKEND.SUBMIT.1-IMPORT-LIVE`).

## Feature flag

`SUBMISSIONS_V2_ENABLED` env var default `false`. Routes (if added later) must check this flag and return 503 when disabled.

## Tests (17/17 PASS)

- Valid submission → needs_review
- Missing required field rejected
- Invalid email rejected
- Invalid source_url rejected (e.g., `javascript:`)
- Invalid language rejected
- Honeypot filled marks spam
- Duplicate detection marks duplicate
- Different email is not duplicate
- Approve transition works
- Reject transition works
- Imported only from approved (needs_review → imported is invalid)
- Invalid transition rejected (rejected is terminal)
- Unknown submission id rejected
- No public listing table touched
- Audit events recorded (`submissions.create.needs_review`, `submissions.transition.approved`)
- list_pending returns only pending
- status() shape

## What is still NOT live

- No `/api/submissions/show` route wired
- No admin review UI
- No email to submitter or reviewer
- No production DB migration auto-applied
- `book.html` unchanged
- No public listings created from submissions

## Rollback

`git revert <commit-sha>` + optional `sqlite3 data/paris.db < backend/migrations/003_submissions_v2.rollback.sql`.

## Related

- [[PHASE_LEDGER]]
- [[BACKEND_PLAN_1]]
- [[BACKEND_AUTH_1_SCAFFOLD]] — audit_events_v2 reused
- [[BACKEND_EMAIL_1_PLAN]] — submission_decision email template deferred to cutover
- [[API_CONTRACT_DRAFT]] — `POST /submissions/show` route deferred to cutover
- [[DB_SCHEMA_DRAFT]] — `show_submissions_v2` matches DB_SCHEMA_DRAFT spec
