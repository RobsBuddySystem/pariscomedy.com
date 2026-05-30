# BACKEND.TICKETS.3-ADMIN-DISCOVERY-DRAFT

**Status: IN_GIT_UNVERIFIED**
**Scope: Admin UI draft only. No imports. No affiliate links. No flag change.**

## What This Phase Delivers

An adapter registry section added to the Tickets tab of `admin-review.html`.
The existing read-only discovery queue panel is unchanged. All buttons remain
disabled. No scraping. No imports. No affiliate link activation.

## Changes to admin-review.html

Added an Adapter Registry card inside the Tickets panel:

```html
<div class="queue-card">
  <h3>Adapter Registry (read-only)</h3>
  <p>Known ticket adapters. Imports disabled=true and affiliate_links disabled=true ...</p>
  <div id="adapters-raw">GET /api/tickets_v2/adapters → loading…</div>
</div>
```

JS fetches `GET /api/tickets_v2/adapters` (always-on endpoint) and shows the raw
response. Footer note: "imports_enabled: false · affiliate_links_enabled: false ·
Ticket adapters are not live yet. Discoveries require manual review."

The existing status fetch `GET /api/tickets_v2/status` remains.
All 4 action buttons (Approve for import, Reject, Mark duplicate, Dry-run import)
remain `disabled` with `title="Disabled until backend enabled"`.

## TICKETS_ADAPTERS_ENABLED / TICKET_IMPORTS_ENABLED / AFFILIATE_LINKS_ENABLED

All still `false` (default). No DB migration. No public import. No scraping.

## Regression Guard

`scripts/regression_guard.py` check `tickets_admin_discovery_draft` (check 22/22) fails if:

1. `admin-review.html` contains "imports are live", "automatic import active", "affiliate links active"
2. Any approve/import button lacks the `disabled` attribute
3. POST to `/api/admin/tickets_v2/*` appears without enabled guard

## Rollback

Remove the adapter registry card and adapter fetch JS from `admin-review.html`.
