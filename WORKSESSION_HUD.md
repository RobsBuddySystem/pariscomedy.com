# WORKSESSION HUD — show-list correctness 2026-05-24

## Phase: DONE
## GO/HOLD: GREEN ✅

## Bugs fixed (all verified on rendered live DOM via Playwright)
- FFCN now appears 4x on Wednesdays at 22:00
- Velvet Open Mic now appears 4x on Wednesdays at 19:00
- Velvet Showcase has explicit 20:30 time (no longer null)
- Velvet Showcase + Kiss correctly tagged ['en','fr'] (bilingual)
- "Source check stale" replaced with honest "Last checked"
- EN filter now includes bilingual; BI filter requires both langs
- Public API PII clean across /api/listings, /api/listings?featured=1, /api/shows

## Guardrails extended
- check_invariants now scans all 3 public API endpoints
- check_invariants now detects duplicate (name+venue+date+time) rows in SHOWS_DATA

## Commit pushed
- 645cbab (shows.html + check_invariants)
- (this commit will add docs/logs)

## Next session can return to: barbes_comedy date-extraction regex (originally paused)
