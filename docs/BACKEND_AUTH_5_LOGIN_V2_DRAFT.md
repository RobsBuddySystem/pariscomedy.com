# BACKEND.AUTH.5-LOGIN-V2-DRAFT

**Status: IN_GIT_UNVERIFIED**
**Scope: Frontend draft only. No production login cutover. No DB migration. No real email.**

## What This Phase Delivers

An Auth V2 draft section added to `login.html` that previews the upcoming
magic-link login flow while keeping the current legacy login completely
untouched and fully operational.

## Draft Section Properties

- Clearly labeled: "Magic-Link Login (Auth V2 — planned, not live yet)"
- Static notice: "This section previews the upcoming magic-link login flow. The backend is not yet live."
- Role selector: Comic / Booker
- Email input
- "Request magic link — not live yet" button — **starts disabled**
- Status line: "Magic-link login is not live yet. Backend status: checking…"

## Auth V2 Status Fetch

On page load, JS fetches `GET /api/auth_v2/status`:

| Response | Button state | Status line |
|---|---|---|
| HTTP 503 / enabled=false | disabled | "Magic-link login is not live yet. Auth V2 backend is disabled." |
| Unreachable / error | disabled | "Magic-link login is not live yet. Auth V2 backend unavailable." |
| enabled=true | **enabled** | "Auth V2 backend reachable. Magic-link login available." |

## Guard: Never Sends While Disabled

JS has an explicit early-return guard:

```js
if (!v2Enabled) return; // guard: never send while disabled
```

POST to `/api/auth_v2/magic-link/request` is only called when `v2Enabled=true`
(set only when status endpoint returns `enabled=true`).

## Legacy Login

The legacy Comic + Booker login form remains untouched. It continues to use
`/api/auth/request` and `/api/booker/auth`. No routes changed, no behavior changed.

## AUTH_V2_ENABLED

Still `false` (default). No production DB migration applied. No real email sent.
No Postmark token. No legacy auth retired.

## Regression Guard

`scripts/regression_guard.py` check `auth_v2_login_draft` (check 18/18) fails if:

1. `login.html` contains static copy claiming magic links are live
2. Static HTML (non-JS) contains "check your email" or "request sent" implying live flow
3. JS sends to `/magic-link/request` without `v2Enabled` guard

## Rollback

Set `AUTH_V2_ENABLED=false` (already default). Remove the Auth V2 draft section
from `login.html`. The legacy login is unaffected in either state.
