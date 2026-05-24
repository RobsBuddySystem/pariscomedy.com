# WORKSESSION HUD — Velvet Open Mic Rollback Round 2 — 2026-05-24

## Phase: DONE
## GO/HOLD: GREEN ✅

## Why round 1 was incomplete
- Slug-only block (didn't match `shows` table which has title only)
- `/api/shows` had no block
- DB row still had featured=1, verified_at=NULL

## This round
- Title-pattern + slug hard-block in BOTH /api/listings and /api/shows
- DB row id=1 fully quarantined (4 new columns: cancellation_reason, public_visible, blocked_from_auto_regeneration, verified_by)
- Other archive rows audited; Theatre BO + Green Mic verified_at refreshed (URLs HTTP 200)
- check_invariants now scans 3 API endpoints AND matches names

## Four live curls all empty:
- /api/listings?featured=1
- /api/listings
- /api/shows
- /shows.html

## Backend commit pushed: pariscomedy-backend HEAD
## Push repo: this update
