# BACKEND.SUBMIT.3-CONNECT-FORM-DRAFT

**Status: IN_GIT_UNVERIFIED**
**Scope: Frontend status note only. No V2 POST. No public cutover. No flag change.**

## What This Phase Delivers

A Submissions V2 status note added to the "List my show" form on `connect.html`.
The existing manual-review submission flow is unchanged. The note fetches
`GET /api/submissions_v2/status` on load and displays the disabled state clearly.

## Changes to connect.html

Added above the "List my show →" button:

```html
<div id="submit-v2-status" ...>
  Automated submissions are not live yet. We review requests manually.
</div>
```

JS fetches `/api/submissions_v2/status`:

| Response | Status line |
|---|---|
| 503 / enabled=false | "Automated submissions backend is not live yet. We review requests manually." |
| Error/unreachable | "Automated submissions are not live yet. We review requests manually." |
| enabled=true | "Automated submissions backend reachable. Manual review is still required." |

**No V2 submit button added. No POST to `/api/submissions_v2/show`.**
The existing "List my show →" button continues to use the legacy manual path.

## Manual Review Copy Preserved

- "Claims are reviewed manually — automated claim backend is not yet live."
- "Automated submissions are not live yet. We review requests manually."

## SUBMISSIONS_V2_ENABLED

Still `false` (default). No DB migration. No public listing creation. No admin approval.

## Regression Guard

`scripts/regression_guard.py` check `submit_v2_connect_form` (check 19/19) fails if:

1. `connect.html` claims automated submissions are live
2. Static HTML has "published automatically" or "show submitted" (non-JS) without manual-review qualifier
3. A POST to `/api/submissions_v2/show` appears without an enabled guard

## Rollback

Remove the `submit-v2-status` div and the `checkSubmissionsV2Status` JS block from `connect.html`.
