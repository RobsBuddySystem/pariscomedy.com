# BACKEND.TICKETS.2-ROUTER-DISABLED

**Status: IN_GIT_UNVERIFIED**
**Feature flags: TICKETS_ADAPTERS_ENABLED=false, TICKET_IMPORTS_ENABLED=false, AFFILIATE_LINKS_ENABLED=false (all default)**
**Live scraping: NOT enabled. Public import: NOT enabled. Affiliate links: NOT enabled.**

## Overview

Tickets/Adapters V2 router wired to `main.py` in disabled mode, matching the pattern
used by Auth/Submissions/Claims/Payments/Messaging V2 routers.

## Routes Wired

| Method | Path | Disabled response |
|---|---|---|
| GET | /api/tickets_v2/status | always-on, reports all flags false |
| GET | /api/tickets_v2/adapters | always-on, returns registry with imports_enabled=false |
| GET | /api/admin/tickets_v2/discoveries | 503 disabled |
| POST | /api/admin/tickets_v2/discoveries | 503 disabled |
| POST | /api/admin/tickets_v2/discoveries/{id}/approve | 503 disabled |
| POST | /api/admin/tickets_v2/discoveries/{id}/reject | 503 disabled |
| POST | /api/admin/tickets_v2/discoveries/{id}/mark-duplicate | 503 disabled |
| POST | /api/admin/tickets_v2/discoveries/{id}/mark-unreachable | 503 disabled |
| POST | /api/admin/tickets_v2/discoveries/{id}/dry-run-import | 503 disabled |

## Adapter Registry

`/api/tickets_v2/adapters` is always-on (read-only). Returns all 15 platform entries
with `imports_enabled=false` and `affiliate_links_enabled=false`.

Signal-only platforms (instagram, facebook) are marked `signal_only=true` in registry
and are blocked from dry-run import even in enabled mode.

## Safety Rules

- TICKETS_ADAPTERS_ENABLED=false — all admin routes return 503
- TICKET_IMPORTS_ENABLED=false — no public import
- AFFILIATE_LINKS_ENABLED=false — no affiliate activation
- No live scraping or crawling
- No public listing changes
- No network calls
- Dry-run import returns draft payload only; public_listing_created always false
- Signal-only platforms (instagram, facebook) cannot import

## Tests (26 total — test_tickets_v2_router.py)

Disabled (10): status always-on, adapters always-on with safe defaults, all 7 admin routes 503, no state on disabled create
Enabled (16): status enabled, registry loads (eventbrite + instagram present), create candidate, list discoveries, duplicate detection, approve/reject/mark-duplicate/mark-unreachable, dry-run blocks unapproved, dry-run approved returns draft, signal-only cannot import, invalid platform 400, no public listing, no external network, no affiliate activation
