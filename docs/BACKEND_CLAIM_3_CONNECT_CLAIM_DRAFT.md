# BACKEND.CLAIM.3-CONNECT-CLAIM-DRAFT

**Status: IN_GIT_UNVERIFIED**
**Scope: Frontend status note only. No V2 POST. No ownership writeback. No flag change.**

## What This Phase Delivers

A Claims V2 status note added to the claim banner on `connect.html`. The existing
manual-review claim flow is unchanged. No ownership writeback. No verified badge
activation. No POST to `/api/claims_v2/*`.

## Changes to connect.html

Added inside the existing `#claim-banner` div:

```html
<div id="claim-v2-status">
  Automated claims backend is not live yet. Claims are reviewed manually.
</div>
```

JS fetches `/api/claims_v2/status`:

| Response | Status line |
|---|---|
| 503 / enabled=false | "Automated claims backend is not live yet. Claims are reviewed manually." |
| Error/unreachable | "Automated claims backend is not live yet. Claims are reviewed manually." |
| enabled=true | "Claims V2 backend reachable. Ownership changes require admin review." |

**No V2 claim button added. No POST to `/api/claims_v2/*`.**

## Manual Review Copy Preserved

- "Claim this show — manual review, not yet live" (header)
- "Claims are reviewed manually — automated claim backend is not yet live." (existing copy)
- "Automated claims backend is not live yet. Claims are reviewed manually." (new status note)

## CLAIMS_V2_ENABLED

Still `false` (default). No DB migration. No ownership writeback. No verified badge change.

## Regression Guard

`scripts/regression_guard.py` check `claim_v2_connect_draft` (check 20/20) fails if:

1. `connect.html` contains "claims are live", "claim verified automatically", "ownership updated", "verified badge active"
2. A POST to `/api/claims_v2/*` appears without an enabled guard

## Rollback

Remove `claim-v2-status` div and `checkClaimsV2Status` JS from `connect.html`.
