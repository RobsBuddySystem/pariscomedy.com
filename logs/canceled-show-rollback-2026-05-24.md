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
