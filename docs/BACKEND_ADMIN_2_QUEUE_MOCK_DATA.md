# BACKEND.ADMIN.2-QUEUE-MOCK-DATA

**Status: IN_GIT_UNVERIFIED**
**Scope: Frontend mock data only. No backend writes. No flag change.**

## What This Phase Delivers

Mock/read-only sample rows added to each tab of `admin-review.html` for operator
UX validation. All rows are clearly labelled "mock data". All action buttons remain
disabled.

## Mock Rows Added

### Show Submissions Tab
3 mock rows: Mock Comedy Night / Mock Open Mic / Mock Stand-Up Club
Banner: "Mock data only — backend review queue is not live."

### Claims Tab
3 mock rows: show_runner / comic / venue claim types
Banner: "Mock data only — ownership changes are not live."

### Ticket Discoveries Tab
3 mock rows: eventbrite / shotgun / dice platforms
Banner: "Mock data only — imports and affiliate links are disabled."

## Safety Properties

- All rows carry `<span class="mock-tag">mock data</span>` label
- All action buttons remain `disabled`
- No onclick calls any write endpoint
- No fetch POST to `/api/admin/*`
- `noindex,nofollow` unchanged
- Not linked from public nav

## Regression Guard Update

`admin_review_shell` check now also fails if:
- Any POST to `/api/admin/submissions_v2`, `/api/admin/claims_v2`, `/api/admin/tickets_v2` appears
- Table rows present without "mock data" label

## No Backend Writes

`safe_to_enable_any_production_feature: false`  
No DB migration. No flags enabled.
