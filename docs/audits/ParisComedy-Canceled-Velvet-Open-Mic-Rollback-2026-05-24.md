# ParisComedy — Canceled Velvet Open Mic Rollback (Round 2) — 2026-05-24

## Status: GREEN ✅

## Why the previous GREEN report was wrong
Prior hard-block applied only to `/api/listings` and matched only on slug.
- `/api/shows` was unprotected (different table, no slug column → title was the public field).
- Slug-only match missed any name-only row.
- DB row id=1 was status=canceled but still had `featured=1` and `verified_at=NULL`, so the underlying record still claimed featured status.

A cached client response (or a request issued before the round-1 restart) would have returned the row.

## Root cause (this round)
- DB row `show_listings.id=1` was half-quarantined (status=canceled only; featured/verified_at unchanged).
- `/api/shows` had no canceled-show filter (only `/api/listings` did).
- Block matched on slug only, not title — so the `shows` table row (no slug column) was unblocked.

## Fixes applied
1. **DB**: row id=1 fully quarantined — `status=canceled, featured=0, public_visible=0, blocked_from_auto_regeneration=1, verified_at=2026-05-24, verified_by='Robert (manual admin)', cancellation_reason='Robert confirmed Velvet Bar Open Mic canceled 2026-05-04; quarantined 2026-05-24'`. New schema columns added: `cancellation_reason`, `public_visible`, `blocked_from_auto_regeneration`, `verified_by`.
2. **Backend**: `_PUBLIC_BLOCKED_TITLE_PATTERNS` matches title substrings case-insensitively; `_is_publicly_blocked(slug, title)` helper used in BOTH `/api/listings` and `/api/shows`.
3. **Cache**: `_NO_STORE_HEADERS` helper available (currently rely on Cloudflare `cf-cache-status: DYNAMIC` — never cached server-side).
4. **Other stale rows**: Theatre BO Julie (#18) and Green Mic Showcase (#24) both returned HTTP 200 today; verified_at refreshed. featured flags untouched (SCOPE_LOCK).
5. **Invariants**: `check_canceled_blocklist` now scans `/api/listings`, `/api/listings?featured=1`, `/api/shows` and matches both slug AND name.

## Live verification (four exact curls)
```
$ curl -s 'https://api.pariscomedy.com/api/listings?featured=1' | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'  → (empty) PASS
$ curl -s 'https://api.pariscomedy.com/api/listings'             | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'  → (empty) PASS
$ curl -s 'https://api.pariscomedy.com/api/shows'                | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'  → (empty) PASS
$ curl -s 'https://pariscomedy.com/shows.html'                   | grep -Ei 'velvet-openmic|Velvet Bar Comedy — Open Mic'  → (empty) PASS
```

## Other stale archive-2026-04-13 rows
- Theatre BO Julie #18, featured=1, URL HTTP 200 — verified_at refreshed to 2026-05-24.
- Green Mic Showcase #24, featured=1, URL HTTP 200 — verified_at refreshed to 2026-05-24.
- featured flags **not** modified (ranking is SCOPE_LOCK; Robert's call).

## Commits pushed
- Backend: backend repo (uvicorn restarted on PID running latest code)
- Push: this audit + extended invariants

## Final status: GREEN ✅
