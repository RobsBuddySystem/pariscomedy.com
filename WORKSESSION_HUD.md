# WORKSESSION HUD — venue-direct scrapers 2026-05-24

## Phase: 4 — DONE
## GO/HOLD: GREEN ✅

## Result
- 10 venue-direct modules added under scripts/discovery/
- 2 real extractors (blastoff_comedy, paname_art_cafe) → 8 raw candidates, 4 accepted by classifier
- 8 honest stubs documenting URL checked + reason + next action
- Registry: SOURCES = AGGREGATOR_SOURCES (7) + VENUE_DIRECT_SOURCES (10) = 17
- Group syntax: `--sources venue_direct` works
- No existing source touched; no privilege introduced

## Pipeline hardening
- daily_discover.py run_state now GREEN | PARTIAL | FAILED
- check_invariants.py accepts PARTIAL as honest

## Live re-check
- /, /shows, /comedians, /about, /featured API — all clean
- Guardrails: GREEN before, GREEN after

## Tomorrow's cron
- Trustable. PARTIAL or FAILED will surface honestly if PC Ollama is down.

## Open: task #43 (Playwright for fever_paris + barbes_comedy)
