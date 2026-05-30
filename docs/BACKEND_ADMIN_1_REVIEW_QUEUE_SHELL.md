# BACKEND.ADMIN.1-REVIEW-QUEUE-SHELL

**Status: IN_GIT_UNVERIFIED**
**Scope: Read-only admin UI shell. No backend writes. No feature flags enabled.**

## What This Phase Delivers

A static admin page (`admin-review.html`) that shows the live status of three
backend review queues (Submissions V2, Claims V2, Ticket Discoveries V2) and
renders all review action controls in a permanently-disabled state until the
corresponding feature flags are enabled in a future phase.

## Safety Properties

- `<meta name="robots" content="noindex,nofollow">` — not indexed, not followed
- Not linked from any public nav partial (marketing, minimal, auth, portal)
- Safety banner on every load: "This admin shell is read-only. Approvals,
  ownership changes, and imports are not active. Production feature flags remain
  disabled. No public changes are made from this page."
- All approve/reject/import/dry-run buttons carry `disabled` attribute and
  `title="Disabled until backend enabled"`
- JS fetches `/api/{system}/status` for live flag state; handles 503 gracefully
  with "Backend route unavailable" chip — no write calls

## Tabs

| Tab | Backend system | Status endpoint |
|---|---|---|
| Show Submissions | SUBMISSIONS_V2_ENABLED=false | GET /api/submissions_v2/status |
| Claims | CLAIMS_V2_ENABLED=false | GET /api/claims_v2/status |
| Ticket Discoveries | TICKETS_ADAPTERS_ENABLED=false | GET /api/tickets_v2/status |

## Regression Guard

`scripts/regression_guard.py` check `admin_review_shell` (check 17/17) fails if:

1. `admin-review.html` is missing from repo root
2. Any approve/reject/import/dry-run button lacks the `disabled` attribute
3. Page copy contains live-action phrases (e.g. "approvals are live", "imports are active")
4. Any public nav partial links to `/admin-review.html`

## Next Phase

**BACKEND.AUTH.5-LOGIN-V2-DRAFT** or **BACKEND.DB.1-MIGRATION-RUNBOOK** (already
completed). Recommended: **BACKEND.EMAIL.4-OPERATOR-DNS-RUNBOOK** (already
completed). The blocker ledger lists all 7 systems with `safe_to_enable_production: false`.
