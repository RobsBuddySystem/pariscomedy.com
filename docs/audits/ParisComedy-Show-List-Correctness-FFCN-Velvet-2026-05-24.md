# ParisComedy — Show-List Correctness (FFCN + Velvet + Source Labels + Language) — 2026-05-24

## Status: GREEN ✅

All five reported bugs root-caused, fixed, and verified via rendered DOM on the live site (Playwright).

## Root causes
1. **FFCN missing** — `/shows.html` is fed by a baked-in `SHOWS_DATA` array, not the `/api/listings` feed. FFCN existed in the API but had never been written into the static array.
2. **Velvet duplication appearance** — Velvet Showcase had two correct weekly instances (5/27, 6/3), but with `start_time: null`. The cards rendered without a time, making them look identical. Not a true duplicate.
3. **"Source check stale: 19 May 2026"** — copy bug. The date itself was an honest `last_verified_at`; the JS label said "stale" instead of "last checked," implying something was wrong rather than just dated.
4. **Kiss Comedy Club tagged FR** — bad data in the baked array. Description clearly says English/bilingual.
5. **Public API PII** — actually clean across `/api/listings`, `/api/listings?featured=1`, `/api/shows`. Guardrail extended to catch any future regression.

## Fixes
- 8 new SHOWS_DATA rows: 4 weeks of FFCN Wednesday 22:00 (lang `['en','fr']`) + 4 weeks of Velvet Open Mic Wednesday 19:00 (lang `['en']`).
- Velvet Showcase: language corrected to `['en','fr']`, time `20:30` added.
- Kiss Comedy Club: language corrected to `['en','fr']`.
- JS label: `Source check stale: <date>` → `Last checked: <date>` (or `Source not yet verified` if absent).
- JS language filter: default `[]` (UNKNOWN) instead of `['fr']`; EN filter now includes BI (English-accessible); FR filter excludes EN-tagged; BI filter requires both EN+FR or explicit `'bi'`.
- JS sort safe against null start_time.
- `check_invariants.py` scans all three public API endpoints for PII and detects duplicate (name+venue+date+time) rows.

## Rendered-DOM proof (Playwright on https://pariscomedy.com/shows.html)
```
FFCN visible:                 True
Velvet Open Mic visible:      True
Velvet Showcase visible:      True
'Source check stale' visible: False
'Last checked' visible:       True
FFCN card count (Wednesday):  4
EN filter — FFCN visible:           True   (bilingual → English-accessible)
EN filter — Kiss visible:           True
BI filter — FFCN visible:           True
BI filter — Comedy Lab not visible: True   (EN-only stays out of BI)
```

## Files changed
- `shows.html` — SHOWS_DATA additions/corrections + JS logic
- `scripts/guardrails/check_invariants.py` — extended PII + duplicate detection

## Commits
- `645cbab` — shows.html SHOWS_DATA + JS + guardrail extension

## Guardrails: GREEN before, GREEN after
## Daily cron: trustable

## Next safest step
Return to the originally-paused work: extract visible-text dates for `barbes_comedy` (task #44 closed; new follow-up).
