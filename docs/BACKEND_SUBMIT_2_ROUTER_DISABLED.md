# BACKEND.SUBMIT.2-ROUTER-DISABLED

**Status: IN_GIT_UNVERIFIED**
**Feature flag: SUBMISSIONS_V2_ENABLED=false (default)**
**Public form: NOT cut over — connect.html unchanged**

## Overview

Submissions V2 router wired to `main.py` in disabled mode, following the same
pattern as Auth V2 (`BACKEND.AUTH.1-ROUTER-INTEGRATION-DISABLED`).

All routes return 503 by default. No public listing is created. No email sent.
No production DB migration applied.

## Routes Wired

| Method | Path | Auth | Disabled response |
|---|---|---|---|
| GET | /api/submissions_v2/status | none | always-on, reports enabled=false |
| POST | /api/submissions_v2/show | none | 503 disabled |
| GET | /api/admin/submissions_v2 | none (admin token TBD) | 503 disabled |
| POST | /api/admin/submissions_v2/{id}/approve | none | 503 disabled |
| POST | /api/admin/submissions_v2/{id}/reject | none | 503 disabled |
| POST | /api/admin/submissions_v2/{id}/mark-duplicate | none | 503 disabled |
| POST | /api/admin/submissions_v2/{id}/mark-spam | none | 503 disabled |

## Disabled Mode

When `SUBMISSIONS_V2_ENABLED=false`:
- `/status` returns `{"enabled": false, "allowed_statuses": [...]}`
- All action endpoints return 503 `{error: {code: "submissions/disabled", ...}}`
- No `show_submissions_v2` rows created
- No audit rows created
- No public listing created

## Enabled Test Mode Behaviors

When `SUBMISSIONS_V2_ENABLED=true` (test env only):
- Valid submission → `needs_review` row
- Honeypot filled → `spam` row
- Duplicate URL+email → `duplicate` row
- Admin approve/reject → status transitions via transition matrix
- Invalid transition → 404
- No public listing auto-created on approve

## Tests (19 total — test_submissions_v2_router.py)

- Disabled mode (8 tests): status disabled, submit 503, admin list/approve/reject/duplicate/spam all 503, no state created
- Enabled mode (11 tests): status enabled, valid submission, invalid submission 400, honeypot spam, duplicate, admin list, approve, reject, invalid transition 404, no public listing, no email

## Safety Rules

- SUBMISSIONS_V2_ENABLED=false — unchanged
- No public form cutover
- No real email sending
- No public listing created
- No production DB migration applied
- No auth/payment/messaging/claim/ticket changes
- No secrets committed

## Rollback

`git revert <commit-sha>` — removes router + tests. main.py reverts to previous
import block pattern.
