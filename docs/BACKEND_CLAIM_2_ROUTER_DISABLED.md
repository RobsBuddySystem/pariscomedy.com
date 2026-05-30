# BACKEND.CLAIM.2-ROUTER-DISABLED

**Status: IN_GIT_UNVERIFIED**
**Feature flag: CLAIMS_V2_ENABLED=false (default)**
**Public claim CTAs: NOT cut over**

## Overview

Claims V2 router wired to `main.py` in disabled mode, matching the
Auth/Submissions disabled-router pattern.

## Routes Wired

| Method | Path | Disabled response |
|---|---|---|
| GET | /api/claims_v2/status | always-on, reports enabled=false |
| POST | /api/claims_v2/comic | 503 disabled |
| POST | /api/claims_v2/show-runner | 503 disabled |
| POST | /api/claims_v2/venue | 503 disabled |
| GET | /api/claim-status/{type}/{slug} | 503 disabled |
| GET | /api/admin/claims_v2 | 503 disabled |
| POST | /api/admin/claims_v2/{id}/approve | 503 disabled |
| POST | /api/admin/claims_v2/{id}/reject | 503 disabled |
| POST | /api/admin/claims_v2/{id}/mark-duplicate | 503 disabled |
| POST | /api/admin/claims_v2/{id}/mark-spam | 503 disabled |

## Tests (25 total — test_claims_v2_router.py)

Disabled (9): status, comic/show_runner/venue 503, admin list/approve/reject/claim-status 503, no state created
Enabled (16): status, comic/show_runner/venue claims, invalid 400, honeypot spam, duplicate, admin list, approve, reject, invalid transition 404, claim-status fail-closed/pending/verified, no ownership writeback, no email

## Safety Rules

- CLAIMS_V2_ENABLED=false — unchanged
- No public claim UI cutover
- No ownership writeback (no write_ownership function in claims_v2)
- No real email sending
- No production DB migration applied
- No secrets committed
