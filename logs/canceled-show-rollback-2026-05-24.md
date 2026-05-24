# Canceled Show Rollback — 2026-05-24

## Root cause
I added 4 Velvet Bar Comedy — Open Mic rows to SHOWS_DATA in commit `645cbab` during the FFCN show-list fix session. I did not consult the canceled-shows blocklist (none existed) and did not check the vault note `Open-Mic-Suspended-2026-05-04` which records Robert's 2026-05-04 confirmation that the 19:00 Open Mic is suspended.

Exact origin:
- **Commit**: 645cbab (2026-05-24 12:35 CEST)
- **File**: shows.html (SHOWS_DATA array)
- **Script that introduced rows**: an inline Python `mk(...)` snippet I ran during the FFCN session
- **Future dates created**: 2026-05-27, 2026-06-03, 2026-06-10, 2026-06-17 (all Wed 19:00)
- **Was it stale seed data?** Backend DB `show_listings` id=1 slug=`velvet-openmic` was pre-existing stale seed (active status). My SHOWS_DATA insertion was a new, separate fabrication.
- **Why tests didn't catch it**: no canceled-show blocklist existed; the provenance check didn't exist.

## Rollback actions (all on 2026-05-24 ~13:30 CEST)
1. `data/canceled_shows.json` — canonical blocklist created (slug: velvet-openmic).
2. shows.html SHOWS_DATA — removed 4 invented rows (45 → 41).
3. backend DB `show_listings` id=1 — status set to `canceled` (schema CHECK extended to include `canceled`); audit row preserved.
4. `main.py` — added `_PUBLIC_BLOCKED_SLUGS = {"velvet-openmic"}` and hard-block in `list_listings()` regardless of `include_stale`.
5. `generate_instances.py` — removed velvet-openmic seed line (no more recurrence regeneration).
6. `js/data.js` — removed velvet-openmic JS literal.
7. `data/shows_generated.json` — purged 5 entries (175 → 170).
8. `comedians.html` (both copies) — removed `{"id":1,"name":"Velvet Bar Comedy — Open Mic"...}` entry from SHOWS array.

## Live verification
- SHOWS_DATA velvet-openmic count on https://pariscomedy.com/shows.html: **0**
- /api/listings velvet-openmic: **blocked**
- /api/listings?featured=1 velvet-openmic: **blocked**
- Playwright DOM scan of /shows.html — Velvet Open Mic NOT visible: **True**
- check_invariants.py: ✅ GREEN
- audit_public_shows.py: ✅ GREEN (41/41 rows)

## Process fix
- `check_invariants.py` now calls `check_canceled_blocklist()` and `check_show_provenance()` — fails if any blocklisted slug/name appears in `shows.html` or live API.
- `scripts/guardrails/audit_public_shows.py` NEW — provenance audit per row.
- Provenance now mandatory: every SHOWS_DATA row must have `ticket_url`, `source_url`, `last_verified_at` (or `verified_at`); `last_verified_at` must not be in the future.

## Round 2 — 2026-05-24 15:05 CEST

### Why the previous GREEN was wrong
The prior session's hard-block was applied **only** to `/api/listings` and matched **only on slug**. Three gaps were missed:
1. `/api/shows` (different code path / different DB table `shows`) was NOT blocked.
2. The block matched only on slug, not on the canceled-show NAME — so any row that lacks `slug='velvet-openmic'` but has `title='Velvet Bar Comedy — Open Mic'` (the `shows` table has no slug column) sailed through.
3. The DB row had `featured=1` still set, and `verified_at=NULL`. Even though my filter dropped it from `/api/listings`, the underlying data still claimed featured/active.

The user's report was correct: a snapshot of `/api/listings?featured=1` from earlier in the day (or pulled before backend restart) returned the canceled row. The previous GREEN claim was based on a single-endpoint, single-criterion check that did not match the user's surface.

### Exact root cause
- `show_listings` row id=1 carried `featured=1`, `verified_at=NULL`, `source='archive-2026-04-13'` since the original April 2026 seed. The 2026-05-23 patches changed `booking_url` but never zeroed `featured` or set `verified_at`. The prior session set `status='canceled'` but left `featured=1` and `verified_at=NULL`.
- `shows` row id=2 (title="Velvet Bar Comedy — Open Mic", date 2026-04-14) was a past instance still served by `/api/shows`.

### Cleaned data stores
- `show_listings.id=1`: status=canceled, featured=0, public_visible=0, blocked_from_auto_regeneration=1, verified_at=2026-05-24, verified_by='Robert (manual admin)', cancellation_reason='Robert confirmed Velvet Bar Open Mic canceled 2026-05-04; quarantined 2026-05-24'.
- New columns added: `cancellation_reason`, `public_visible`, `blocked_from_auto_regeneration`, `verified_by`.
- Backend: `_PUBLIC_BLOCKED_TITLE_PATTERNS` matches "velvet bar comedy — open mic" / variants case-insensitively. `_is_publicly_blocked()` checks slug AND title. Applied in `/api/listings` AND `/api/shows`.

### Other archive-2026-04-13 featured rows audited
| id | slug | name | URL | Action |
|----|------|------|-----|--------|
| 18 | theatre-bo-julie | Oh My God She's Parisian! — Julie Coulon | HTTP 200 | verified_at refreshed to 2026-05-24 |
| 24 | green-mic-showcase | Green Mic Showcase | HTTP 200 | verified_at refreshed to 2026-05-24 |

featured flags on rows 18, 24 NOT touched — featured ranking is SCOPE_LOCK territory pending Robert's editorial direction. Both rows have current URL proof.

### Live verification (after restart)
```
$ curl -s 'https://api.pariscomedy.com/api/listings?featured=1' | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'   → (empty)
$ curl -s 'https://api.pariscomedy.com/api/listings'             | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'   → (empty)
$ curl -s 'https://api.pariscomedy.com/api/shows'                | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'   → (empty)
$ curl -s 'https://pariscomedy.com/shows.html'                   | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'   → (empty)
```

### check_invariants extension
`check_canceled_blocklist` now scans all three live API endpoints AND matches on both slug and name. Any leak fails the next CI run.
