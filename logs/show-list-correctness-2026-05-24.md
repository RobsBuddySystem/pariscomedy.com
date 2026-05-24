# Show-list correctness — 2026-05-24

## Pre-flight: ✅ GREEN

## Root causes
1. **FFCN missing** — /shows.html reads from baked-in `const SHOWS_DATA` (line 177), not /api/listings. FFCN was in the featured API but not in the baked array. Two separate systems.
2. **Velvet "duplicate"** — two SHOWS_DATA rows for "Velvet Bar Comedy Showcase" (5/27 + 6/3), both with `start_time: null`. Different weeks, but identical-looking cards because no time was shown. Not a true duplicate — a missing-time + recurring-instance display issue.
3. **"Source check stale: 19 May 2026"** — `last_verified_at` was an old field value from the prior bake; the JS label said "stale" rather than "last checked." The data was honest, the copy was harsh.
4. **Kiss Comedy Club tagged FR** — description clearly says English/bilingual; baked language tag was `['fr']`. Bad data.
5. **Public API PII** — already sealed; live re-check on `/api/listings?featured=1`, `/api/listings`, `/api/shows` returned empty matches.

## Fixes applied
- `shows.html` SHOWS_DATA: added 4 FFCN Wednesday 22:00 rows + 4 Velvet Open Mic Wednesday 19:00 rows (8 new rows; 37 → 45).
- `shows.html` SHOWS_DATA: corrected Velvet Bar Comedy Showcase language → `["en","fr"]` and added `start_time: "20:30"`.
- `shows.html` SHOWS_DATA: corrected Kiss Comedy Club language → `["en","fr"]`.
- `shows.html` JS: label changed from "Source check stale: <date>" to "Last checked: <date>" / "Source not yet verified". Honest, no false negativity.
- `shows.html` JS: language filter no longer defaults missing lang to `['fr']`; defaults to `[]` (UNKNOWN). Per PROJECT_CANON the EN filter now includes BI (English-accessible shows), FR filter excludes EN-tagged shows, BI filter requires both or explicit `'bi'`.
- `shows.html` JS: sort safe against null `start_time`.
- `scripts/guardrails/check_invariants.py`: scans `/api/listings`, `/api/listings?featured=1`, `/api/shows` for PII. Detects duplicate (name+venue+date+time) rows in live SHOWS_DATA.

## Rendered-DOM verification (Playwright on live site)
```
FFCN visible:                 True
Velvet Open Mic visible:      True
Velvet Showcase visible:      True
'Source check stale' visible: False
'Last checked' visible:       True
FFCN card count (Wednesday):  4
EN filter — FFCN (BI) visible:           True
EN filter — Kiss (BI) visible:           True
BI filter — FFCN visible:                True
BI filter — Comedy Lab (EN only) NOT vis: True
```

## Public API PII status
- `/api/listings?featured=1`: clean
- `/api/listings`: clean
- `/api/shows`: clean
- Guardrail extended so next regression fails the build.

## Guardrails
- Before: ✅ GREEN
- After: ✅ GREEN
